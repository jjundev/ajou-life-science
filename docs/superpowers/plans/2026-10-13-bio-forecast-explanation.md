# 웹과제 예상문제·해설 자동 생성 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 웹과제 예상 스킬 한 번의 호출로 같은 장·버전의 예상문제 HTML과 검증된 해설 HTML을 생성한다.

**Architecture:** 해설기에 forecast 전용 입력 어댑터를 추가하고 기존 저작·조립·검토·발행 흐름을 재사용한다. 예상 스킬의 실행 절차가 검증된 HTML의 명시 경로를 해설기에 넘긴다. Python 조립기에 LLM 호출이나 별도 스케줄러를 추가하지 않는다.

**Tech Stack:** Python 3.10+, 표준 라이브러리, pytest, HTML/Markdown, 로컬 KaTeX/Pretendard, Playwright 브라우저 검토.

**Spec:** `docs/superpowers/specs/2026-10-13-bio-forecast-explanation-design.md` (2026-10-13 대화의 확정 설계 및 수정·재검토 결정).

## Global Constraints

- 최초 검토 이후 수정·재검토는 최대 2회다(최초 1회 + 재검토 최대 2회).
- 두 HTML이 모두 검증·발행되어야 전체 완료로 보고한다.
- 해설 대상: `p1–p15` 전체. `o1·o2`는 개요이므로 제외한다.
- 기존 날짜형 입력, 최신 선택, `all`의 복습노트 범위를 유지한다. 예상문제는 명시 경로로만 선택한다.
- 해설: `문제해설_N장_웹과제예상_vK.html/.md`.
- `lite`도 해설을 생성하고 네 검토를 모두 수행한다.
- Python 3.10 이상, 실행기 표준 라이브러리 유지.
- 기존 버전·실제 수업 산출물·고정 vendor 사본을 수정하지 않는다. 임시 합성 저장소로 검증한다.
- 커밋·푸시는 별도 사용자 요청 때만 실행한다. 아래 각 작업의 커밋 단계는 그 요청이 있을 때만 수행한다.
- 현재 checkout에는 템플릿·provenance·테스트·수업 파일의 기존 변경이 있다. 실행 시작 시 using-git-worktrees로 격리하고 기존 변경이 필요한 경우 그 파일만 비교·보존하여 반영한다. 기존 변경을 덮거나 함께 stage하지 않는다.

## Review Focus

1. `o1·o2`와 알 수 없는 카드가 섞인 입력: 개요만 제외하고 잘못된 카드는 거부한다(Task 1).
2. 장·버전·정답키가 서로 다르거나 Unicode 경로가 다른 입력: NFC/NFD 경로는 동일하게 처리하고 실제 불일치는 거부한다(Task 1).
3. 해설 추출 후 pack.json/blueprint.md 또는 문제 원본이 바뀐 입력: 이전 검토로 발행하지 않고 재추출을 요구한다(Task 2).
4. 해설 수정 후 기존 pass/disputed 기록이 남는 경우: build는 검토를 초기화하고 새로운 승인 없이는 발행하지 않는다(Task 2).
5. 해설 단계에서 문제 오류를 찾은 경우: 문제 검증으로 돌아가며 수정 한도를 중첩 초기화하지 않는다(Task 3).

---

## 파일 구조와 책임

아래 경로는 저장소 루트 기준이다. `E=.agents/skills/bio-problem-explain`, `F=.agents/skills/bio-webquiz-forecast`는 읽기 편의를 위한 표기이며 명령에서는 실제 경로를 사용한다.

| 경로 | 작업 | 책임 |
|---|---|---|
| E/scripts/mpe_forecast.py | 생성 | 예상문제 경로·manifest·카드 검증과 SourcePack 변환 |
| E/scripts/mpe_source.py | 수정 | 명시 forecast 경로 분기, 기존 선택 범위 유지 |
| E/scripts/mpe_types.py | 수정 | SourcePack에 context_hashes 기본값 추가 |
| E/scripts/mpe_render.py | 수정 | forecast 출력 이름·제목·context manifest 보존 |
| E/scripts/mpe_contract.py | 수정 | context_hashes를 검토 대상 해시에 반영 |
| E/scripts/mpe_publish.py | 수정 | 발행 직전 forecast 문맥 파일 해시 확인 |
| E/tests/forecast_helpers.py | 생성 | 합성 15문항·개요·manifest fixture |
| E/tests/test_forecast_source.py | 생성 | 입력 지원·보존·오류·선택 회귀 |
| E/tests/test_forecast_pipeline.py | 생성 | CLI round-trip·수정 후 검토 무효화·발행 |
| E/SKILL.md, E/references/authoring.md, E/references/verification.md | 수정 | forecast 범위·근거·검토 절차 |
| F/SKILL.md, F/references/explanation-handoff.md | 수정/생성 | 자동 호출·수정 루프·통합 보고 |
| E/tests/test_skill_files.py, F/tests/test_skill_files.py | 수정 | 문서 계약과 링크 검증 |
| E/assets/port-provenance.json | 수정 | 변경 파일의 현재 해시와 이식 사본 대비 변경 이유 |

## Task 1: 예상문제 입력 어댑터

**Files:** Create `E/scripts/mpe_forecast.py`, `E/tests/forecast_helpers.py`, `E/tests/test_forecast_source.py`; modify `E/scripts/mpe_source.py:171`, `E/scripts/mpe_types.py:23`.

**Interfaces:**
- Consumes: 기존 `Problem`, `SourcePack`, `inside(path, repo)`, `existing_path(path)`, `sha256(path)`, `parse(text)`, `subparts(ask, original)`.
- Produces: `load_forecast_source(path: Path, repo: Path) -> SourcePack` in mpe_forecast.py. `load_source(path: Path, repo: Path) -> SourcePack`는 지원 파일명에 따라 이를 호출한다.
- SourcePack에 `context_hashes: tuple[tuple[str, str], ...] = ()`를 마지막 필드로 추가한다. forecast는 pack.json과 blueprint.md의 절대 경로·SHA256을 경로순으로 기록한다. review는 빈 tuple을 유지한다.
- Fixture: `forecast_source_file(repo: Path, chapter: int = 4, version: int = 5) -> Path`. 15문항, o1/o2, pack.json, blueprint.md, 로컬 노트 링크를 만든다. 각 카드에 A–E 보기, data-correct, solution/steps/answer, source를 넣고 정답키와 일치시킨다. 정답 분포 A~E 각 3개.

- [ ] **Step 1: 실패 테스트 작성**

```python
def test_forecast_extracts_fifteen_and_preserves_input(tmp_path):
    source = forecast_source_file(tmp_path)
    before = source.read_bytes()
    pack = load_source(source, tmp_path)
    assert (pack.profile, pack.range, pack.slug) == ('forecast', '4장', '웹과제예상_v5')
    assert [p.id for p in pack.problems] == [f'p{i}' for i in range(1, 16)]
    assert all(p.subparts == ('main',) for p in pack.problems)
    assert len(pack.context_hashes) == 2
    assert source.read_bytes() == before
```

추가 테스트를 같은 파일에 작성한다: `test_only_known_overviews_are_skipped`(o1/o2 제외, o3/q1 거부), `test_missing_duplicate_and_extra_questions_rejected`(p15 누락/p1 중복/p16 추가), `test_manifest_identity_and_key_mismatch_rejected`(장/버전/정답키 불일치), `test_forecast_nfd_path`(명시 경로의 NFC/NFD 동일 선택), `test_forecast_not_selected_by_all_or_default`(기존 review만 선택), `test_forecast_preserves_choices_original_svg_and_table`(각 원문 필드 내용 보존), `test_missing_manifest_or_blueprint_rejected`(추측하거나 과거 버전으로 이동하지 않음).

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest .agents/skills/bio-problem-explain/tests/test_forecast_source.py -q`
Expected: forecast 입력 미지원으로 FAIL. 기존 review 회귀 테스트는 통과해야 한다.

- [ ] **Step 3: 입력 어댑터 구현**

파일명 정규식은 `복습문제_([1-9]\d*장)_(웹과제예상_v[1-9]\d*)\.html`. canonical 위치 `웹과제예상/N장/`와 `src/vK/pack.json`, `blueprint.md`를 확인한다. pack.json의 chapter/version은 양의 정수이고 filename과 일치해야 한다. problems 목록에서 o1/o2 및 p1–p15가 정확히 한 번씩 있어야 한다. answer_key는 정확히 p1–p15와 A–E 값이며 카드의 data-correct 및 answer와 일치해야 한다.

parse로 card를 읽고 o1/o2만 제외한다. 나머지는 기존 카드 구조 검증과 동일하게 필수 제목·problem·solution·steps·answer를 확인하고 Problem으로 변환한다. 지문/보기/그림은 .problem 전체를 conditions_html에 유지한다. original은 있으면 보존하며 새 예상문항에 없는 original/hint를 새로 요구하지 않는다. vendor/read_cards.py는 수정하지 않는다. 순환 import를 피하기 위해 load_source의 forecast 분기에서 loader를 지연 import한다.

- [ ] **Step 4: 통과 확인**

Run: `python3 -m pytest .agents/skills/bio-problem-explain/tests/test_forecast_source.py .agents/skills/bio-problem-explain/tests/test_source.py -q`
Expected: 모두 PASS, 입력 파일 바이트 변화 없음.

- [ ] **Step 5: 작업 단위 커밋(별도 요청 시)**

Task 1 파일만 stage하고 staged diff/check 확인 후 `feat(bio-problem-explain): support forecast sources`로 커밋한다.

## Task 2: 해설 출력과 검토 무효화·발행

**Files:** Modify `E/scripts/mpe_render.py:18,163,180,188`, `E/scripts/mpe_contract.py:11`, `E/scripts/mpe_publish.py:10`; create `E/tests/test_forecast_pipeline.py`.

**Interfaces:**
- Consumes: Task 1의 forecast SourcePack과 context_hashes, 기존 `build_explanation(pack, fragments, stage, repo) -> Artifacts`, `names(pack)`, `publish_explanation(...)` 및 CLI extract/build/check/publish.
- Produces: forecast용 names(pack) = (`문제해설_4장_웹과제예상_v5`, `figures_문제해설_4장_웹과제예상_v5`, `자료_문제해설_4장_웹과제예상_v5`). 기존 review 이름은 동일하다. `payload_hash(pack, fragments)`는 forecast의 context_hashes를 포함한다(빈 review 문맥은 기존 해시 형식을 유지).

- [ ] **Step 1: 실패 테스트 작성**

`test_forecast_cli_round_trip`는 기존 tests/test_cli.py의 call/fragment/approved 패턴으로 extract→15개 조각→build→check를 수행한다. `names(pack)`가 위 3개 이름인지, HTML 제목이 `생명과학 4장 웹과제 예상 v5 문제해설`인지, RANGE가 `bio-problem-explain-forecast-4장-웹과제예상_v5`인지 검사한다. 검토 전 publish는 실패하고 fixture 승인 후에는 같은 장 폴더에 HTML/MD와 자료 폴더가 생기며 원본 바이트는 동일해야 한다.

`test_changed_forecast_context_requires_reextract`는 pack.json과 blueprint.md를 각각 추출 후 수정하여 check/publish가 실패하는지 검사한다. `test_direct_publish_rejects_changed_context`는 CLI를 우회해 publish_explanation을 호출해도 실패해야 한다.

`test_rebuild_resets_reviews_and_blocks_stale_pass`는 승인한 해설 조각을 수정 후 build하여 네 status가 not_run인지, 예전 review를 다시 넣어도 해시 불일치로 publish가 실패하는지 검사한다. `test_disputed_cannot_publish`는 disputed에서 승인 없이 발행되지 않는지 검사한다. `test_new_versions_have_distinct_names_and_state_keys`는 v5/v6 산출명과 읽음 RANGE가 다르고 v5를 변경하지 않는지 검사한다.

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest .agents/skills/bio-problem-explain/tests/test_forecast_pipeline.py -q`
Expected: 기존 문제설명 파일명 또는 문맥 해시 미검증 때문에 FAIL.

- [ ] **Step 3: 출력·발행 구현**

names와 페이지 제목에 forecast 분기를 추가한다. manifest에 context_hashes를 JSON 배열로 기록하고 check_artifacts가 현재 pack과 대조하게 한다. payload_hash에 forecast 문맥을 반영한다. publish_explanation이 context_hashes의 파일을 inside로 검증한 뒤 존재·현재 SHA256을 확인하도록 한다. 기존 source/fragment/artifact/reference 해시 관문과 rollback을 재사용한다. 기존 build의 검토 초기화 동작은 유지한다.

- [ ] **Step 4: 통과 확인**

Run: `python3 -m pytest .agents/skills/bio-problem-explain/tests/test_forecast_pipeline.py .agents/skills/bio-problem-explain/tests/test_cli.py .agents/skills/bio-problem-explain/tests/test_render.py .agents/skills/bio-problem-explain/tests/test_publish.py .agents/skills/bio-problem-explain/tests/test_contract.py -q`
Expected: 모두 PASS. 합성 승인 기록은 코드 관문 테스트용이며 실제 네 검토의 완료 증거로 쓰지 않는다.

- [ ] **Step 5: 작업 단위 커밋(별도 요청 시)**

Task 2 파일만 stage하고 staged diff/check 확인 후 `feat(bio-problem-explain): publish versioned forecast explanations`로 커밋한다.

## Task 3: 자동 호출·수정 루프·수락 검증

**Files:** Modify `E/SKILL.md`, `E/references/authoring.md`, `E/references/verification.md`, `E/tests/test_skill_files.py`, `F/SKILL.md`, `F/tests/test_skill_files.py`, `E/assets/port-provenance.json`; create `F/references/explanation-handoff.md`.

**Interfaces:**
- Consumes: Tasks 1–2의 명시 HTML 입력과 기존 mpe_cli.py extract/build/check/publish 명령.
- Produces: F의 브라우저 확인 이후 필수 `### 9. 예상문제해설 생성`과 `### 10. 보고`. 절차의 상세 계약은 explanation-handoff.md에 한 번 정의하고 SKILL.md에서 연결한다. 별도 자동 저작 CLI는 만들지 않는다.

- [ ] **Step 1: 실패 문서 계약 테스트 작성**

F/tests/test_skill_files.py에 `test_explanation_handoff_is_required_before_report`를 추가하여 9단계의 bio-problem-explain 호출·명시 HTML 경로·lite 전달·10단계 두 HTML 보고를 검사한다. `test_explanation_retry_contract`는 handoff에 최초+최대 2회, 문제 수정 시 6–8단계로 복귀, 새 RUN 재추출, 중첩 한도 초기화 금지, 미해결 시 부분 완료가 정의되어 있는지 검사한다.

E/tests/test_skill_files.py에는 `test_forecast_authoring_and_verification_contract`(pack.json/blueprint.md 근거, 원문/변형 구별, o1/o2 제외, 별도 정답 비공개 검산), `test_forecast_output_and_scope_contract`(정확한 해설 이름, all 범위 유지, 자동 백필 없음)을 추가한다. 문서 테스트는 실행·정답 검증의 대체가 아님을 유지한다.

- [ ] **Step 2: 실패 확인**

Run separately:
`python3 -m pytest .agents/skills/bio-webquiz-forecast/tests/test_skill_files.py -q`
`python3 -m pytest .agents/skills/bio-problem-explain/tests/test_skill_files.py -q`
Expected: 신규 문서 계약 부재로 FAIL. 기존 동일 basename 테스트는 별도 pytest 프로세스로 실행한다.

- [ ] **Step 3: 스킬 실행 계약 갱신**

F의 description과 목표에 두 HTML 생성을 반영한다. 9단계는 새 RUN을 사용해 방금 검증한 HTML 경로를 해설기에 넘기고 1–7단계를 수행한다. 저작/독립 검산 분담과 모델은 기존 스킬 규칙을 따르고 lite를 전달한다. 컨트롤러는 `attempt=0`부터 수정할 때만 증가하여 최대 2로 제한하고 검토 evidence에 원인·변경·재검토 결과를 남긴다. 해설만 수정하면 재조립과 네 검토를 다시 수행한다. 문제 오류이면 이번 호출에서 만든 카드/정답키/설계표를 함께 고치고 6–8단계를 다시 실행한 후 새 RUN으로 해설을 재추출한다. 기존 예상문제 블라인드 루프와 중첩하여 수정 예산을 새로 얻지 않는다.

E의 입력 범위·예상문제 경로·출력·저작·검토 지침을 추가한다. forecast에서는 key-check/variants의 부재를 오류로 보지 않고 해당 버전의 pack.json/blueprint.md로 대조한다. 원문 그대로 문항만 원문 답과 직접 대조하고, 변형은 바뀐 조건과 보기 순서를 실제로 재풀이한다. 설계표의 정답키를 블라인드 리뷰어에게 제공하지 않는다. 네 검토와 현재 해시가 통과할 때만 publish한다.

provenance의 source_commit과 기존 source_sha256은 유지한다. 이번에 변경한 기존 파일의 destination_sha256·change_reason만 갱신한다. 새 로컬 adapter/test/reference는 기존 files 배열에 source_path/source_sha256=null, destination=스킬 상대 경로, destination_sha256=현재 해시, change_reason="forecast explanation local addition"으로 추가한다. 기존 다른 작업의 provenance 변경을 재작성하거나 삭제하지 않는다.

- [ ] **Step 4: 두 스킬 전체 회귀 확인**

Run separately:
`python3 -m pytest .agents/skills/bio-problem-explain/tests -q`
`python3 -m pytest .agents/skills/bio-webquiz-forecast/tests -q`
Expected: 각각 모두 PASS. 실패가 기존 변경에서 비롯되면 기준 checkout과 비교하여 이 작업에 해당하는 원인만 수정한다.

- [ ] **Step 5: 임시 저장소에서 실제 연동 수락 검증**

forecast_source_file fixture로 임시 저장소를 만들고 build/check→해설 CLI round-trip을 수행한다. 문서의 handoff 절차대로 합성 해설 15개를 검토하여 최종 두 HTML을 확인한다. 의도적인 해설 오류 1개를 넣어 수정 후 재검토·발행되는지, 승인 뒤 문제 조건 변경 시 기존 RUN의 발행이 막히고 새 RUN에서 재검토해야 하는지 확인한다. 이 검증은 fixture의 소프트웨어 동작 확인이며 실제 수업 세트의 학술 검증으로 보고하지 않는다.

임시 저장소를 127.0.0.1에 serve하고 Playwright로 두 HTML을 1280×900/375×812, light/dark에서 검사한다. 문제의 보기 채점, 해설의 15개 목차·이전/다음·요약, 원문/노트 링크, 수식·SVG·표·이미지 로딩을 확인한다. 콘솔/KaTeX/누락 자원/외부 요청/문서 가로 넘침은 모두 0. 검토 결과·수정 기록·화면은 임시 RUN에 저장한다. 테스트를 위해 실제 v1–v4를 재생성하지 않는다.

- [ ] **Step 6: diff와 완료 조건 확인**

Run: `git diff --check` 및 이번 작업 파일의 `git diff --stat`.
Expected: whitespace 오류 0, 구현 범위 밖 파일 변경 0. 전체 성공 보고에는 테스트 결과와 실제 연동 검토 결과를 구별해서 적는다.

- [ ] **Step 7: 작업 단위 커밋(별도 요청 시)**

Task 3 파일만 stage하고 staged diff/check 확인 후 `feat(bio-webquiz-forecast): generate reviewed explanations automatically`로 커밋한다. push는 별도 요청 없이는 실행하지 않는다.

## 계획 자체 검토

- 설계 범위: 입력/개요 제외/근거/출력/자동 실행/lite/재검토/부분 완료/보존 조건을 Tasks 1–3에 배치했다.
- 인터페이스: SourcePack.context_hashes 및 load_forecast_source는 Task 1에서 정의하고 Task 2가 소비한다. 새 자동 저작 함수나 정의되지 않은 실행기가 없다.
- Review Focus 5개: 각 항목의 실패 입력 테스트 또는 문서 계약과 실제 수락 검증을 해당 작업에 배치했다.
- 과잉 범위: vendor 수정, 새 수업 세트, 기존 세트 백필, 실제 문제 링크 삽입, 자동 커밋·푸시를 제외했다.
- 구현 시작 전: 사용자 계획 검토 및 실행 방식 선택을 기다린다. 추천은 Native이며, 세 작업이 작은 입력 어댑터·기존 발행 계약을 순차적으로 공유하므로 직접 실행 후 최종 독립 검토가 적합하다.
