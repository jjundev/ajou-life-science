# 생명과학 시험 예상문제 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 입력 장 범위에서만 객관식 55문항·단답형 20문항과 검증된 해설을 만들고 최신 공통 출제 경향 MD를 매 실행에 반영하는 `bio-exam-forecast` 스킬을 추가한다.

**Architecture:** 스킬이 자료 읽기·의미 판정·문항 저작·독립 검토를 지휘하고 Python helper는 입력/출처/배정/조립/검증만 맡는다. 시험 전용 계약·화면을 추가하고 기존 문제은행 validator·review 스타일·해설 SourcePack/검토/발행을 재사용한다. 75문항과 해설 연결은 하나의 사용자 흐름이므로 별도 독립 프로젝트로 나누지 않는다.

**Tech Stack:** Python 3.10+, 표준 라이브러리, 기존 jsonschema>=4.18,<5, HTML/CSS/JavaScript, 로컬 KaTeX/Pretendard, pytest, Playwright.

**Spec:** `docs/superpowers/specs/2026-10-15-bio-exam-forecast-design.md`. 실행자는 이 문서와 명세를 모두 읽는다. 장별 균등·출처 배합은 제안된 기본 생성 정책이며 실제 출제 통계가 아니다.

## Global Constraints

- 객관식 55문항·단답형 20문항, 합계 75문항을 기본으로 한다.
- 문제와 모든 보기를 판단하는 데 필요한 지식은 사용자가 입력한 장 범위 안에 있어야 한다.
- 실행할 때마다 공통 출제 경향 MD와 선택 범위의 장별 피드백을 새로 읽는다.
- 출제 경향 본문을 새 스킬에 복제하지 않는다. 읽은 파일의 경로·SHA-256과 문항별 적용 근거를 남긴다.
- 원문 재사용은 발문·수치·조건·보기 순서·그림을 보존한다. 의미를 수정한 문항은 변형으로 표시한다.
- 화면의 사용자 선택을 공식 정답으로 취급하지 않는다. 공식 답과 분석 답의 상태를 구별한다.
- 범위 부족·조건 모호함·정답 충돌·원문 미확인으로 75문항을 채울 수 없으면 부족을 보고한다. 범위 확장·반복 채우기·빈 문항은 금지한다.
- 기존 버전·문제은행·STT·강의노트·고정 vendor 사본을 수정하지 않는다.
- Python 3.10 이상을 사용한다. 문제은행 검증은 기존 jsonschema 의존성을 재사용하고 새 LLM API·스케줄러·백엔드를 추가하지 않는다.
- 최초 검토 이후 수정·재검토는 최대 2회다. 문제·해설 단계를 오가더라도 같은 실행의 수정 횟수를 초기화하지 않는다.
- 문제와 해설이 모두 검증되어야 전체 완료다. 해설이 미해결이면 검증된 문제는 보존하고 부분 완료로 보고한다.
- 커밋·푸시·실제 수업 범위의 75문항 생성은 별도 요청 전에는 실행하지 않는다.

## Review Focus

1. bank 없는 장·부재 피드백이 실행 도중 생기는 경우: 장별 문항 수를 유지하고 새 파일 등장도 현재 근거 변경으로 감지한다(Task 2/3).
2. bank와 공통 MD의 상태 서술이 다르거나 MD만 갱신된 경우: 현재 자료를 읽고 불일치를 보고하며 오래된 검토를 사용하지 않는다(Task 2/5/6).
3. 서로 다른 출처에 복제된 문제·같은 가족의 객관식/단답형이 경쟁하는 경우: 중복 없이 슬롯을 재배정하고 진짜 부족만 보고한다(Task 3).
4. gene symbol 대소문자·단위·허용답 밖 표현·미제출 상태: 의미를 지우는 정규화와 조기 답 노출 없이 자기채점 대기를 유지한다(Task 1/4).
5. 범위가 좁거나 추출/해설 실패·기존 all/최신 입력이 있는 경우: 75개처럼 보이는 빈 결과·검토 자동 pass·기존 선택 범위 확장을 허용하지 않는다(Task 5/6/7/8).

---

## 실행 전 준비와 확인한 현행 계약

- 구현 시작 시 `using-git-worktrees`로 작업 위치를 정한다. 이 계획 작성 시 기존 untracked인 `docs/superpowers/plans/2026-10-15-bio-ch1-feedback-skills.md`, `2026-10-15-bio-ch3-feedback-input.md`, 웹과제 1·3장 feedback 폴더는 본 작업 소유가 아니다.
- 새 스킬은 `skill-creator` 지침을 읽고 저장소의 `.agents/skills/` 정본 + `.claude/skills/` 심볼릭 링크 관례를 따른다. 전역 스킬 설정을 바꾸지 않는다.
- `.agents/skills/bio-webquiz-forecast/scripts/exam_pool.py:20`의 collector는 answer_index가 있는 객관식 카드만 모은다. 기존 파일명/정답이 원문 검증 증거는 아니다.
- `scripts/question_bank/model.py:488`의 `load_bank(path, *, complete=False, repo_root=None)`를 `complete=True`로 사용한다. NFC/NFD 경로 해결 기능도 재사용한다.
- `.agents/skills/bio-review-pack/scripts/assemble.py:82`는 `build_review()` 끝에서 즉시 채점 interaction을 설치한다. 시험 조립기는 이 함수를 그대로 호출하지 않는다.
- `.agents/skills/bio-webquiz-forecast/scripts/blind.py`는 객관식만 뽑고 SVG를 텍스트로 바꾼다. 시험 독립 풀이 사본으로 재사용하지 않는다.
- `.agents/skills/bio-problem-explain/scripts/mpe_forecast.py:9`는 p1~p15/A~E만 받는다. 새 `exam` adapter를 추가하고 기존 forecast 계약은 유지한다.
- `mpe_cli.load_run()`은 원본을 다시 로드해 직렬화 값과 비교한다. `mpe_render.check_artifacts()`와 `mpe_publish.publish_explanation()`은 context_hashes를 재확인한다. 이 경로에 exam을 연결한다.

## 파일 구조와 책임

아래 표와 작업별 경로는 저장소 루트 기준이다. 명령은 해당 checkout 루트에서 실행한다.

| 생성/수정 경로 | 책임 |
|---|---|
| `.agents/skills/bio-exam-forecast/SKILL.md` | 호출·자료 읽기·저작/검토·해설 인계·완료 보고 |
| `.agents/skills/bio-exam-forecast/references/{pack-contract,selection,authoring,verification,explanation-handoff}.md` | 문서 5개, 각각 데이터 계약/선정/단답 포함 저작/실제 검토/해설 연결 |
| `.agents/skills/bio-exam-forecast/scripts/exam_contract.py` | Scope·형식·후보·pack·단답 정규화 계약 |
| `.agents/skills/bio-exam-forecast/scripts/exam_sources.py` | 동적 자료 inventory·검증된 원문 후보·근거 신선도 |
| `.agents/skills/bio-exam-forecast/scripts/exam_selection.py` | 장/형식 슬롯 배정·가족 중복·출처 목표·선정 보고 |
| `.agents/skills/bio-exam-forecast/scripts/exam_build.py` | 버전 예약·pack/blueprint/card·문제 HTML 조립 |
| `.agents/skills/bio-exam-forecast/scripts/exam_check.py` | 기계 검사·문항 검토 계약·완료 판정 |
| `.agents/skills/bio-exam-forecast/scripts/exam_blind.py` | 답을 제외하고 그림/표를 보존한 독립 풀이 HTML |
| `.agents/skills/bio-exam-forecast/scripts/exam_cli.py` | prepare/select/build/check/blind/status 명령 |
| `.agents/skills/bio-exam-forecast/assets/exam-template.html`, `exam-runtime.js` | 시험용 shell·전체 제출·단답형 입력/채점 |
| `.agents/skills/bio-exam-forecast/tests/` | 아래 작업별 합성 fixture·검증·브라우저 테스트 |
| `.agents/skills/bio-problem-explain/scripts/mpe_exam.py` | 시험 입력을 SourcePack(profile='exam')으로 변환 |
| `.agents/skills/bio-problem-explain/scripts/mpe_types.py`, `mpe_source.py`, `mpe_render.py` | 단답형 모델·명시 경로 분기·시험 이름/제목/자료 경로 |
| `.agents/skills/bio-problem-explain/SKILL.md`, `references/verification.md` | 새 입력 지원과 검토 지침만 추가 |
| `.agents/skills/bio-problem-explain/tests/exam_helpers.py`, `test_exam_source.py`, `test_exam_pipeline.py` | 기존 입력과 격리된 시험 연동 회귀 |
| `.claude/skills/bio-exam-forecast` | `../../.agents/skills/bio-exam-forecast`를 가리키는 링크 |

기존 출제 경향 MD·다른 생성 스킬·고정 vendor는 이 작업에서 수정하지 않는다. 해설 `mpe_contract.py`·`mpe_publish.py`는 기존 context 검사로 해결하며 무조건적인 리팩터링을 하지 않는다.

## 공통 인터페이스

후보/pack JSON 필드는 명세 6~7절이 정본이다. Python에서는 `dict`로 전달하고 validator로 경계를 검사한다. `exam_contract.py`의 `ExamError(ValueError)`를 모든 helper의 사용자 오류로 통일한다. `Scope`는 frozen dataclass로 `chapters: tuple[int,...]`, 읽기 전용 `label: str` 속성을 제공한다. `Selection`은 frozen dataclass로 `problems: tuple[dict,...]`, `quotas: dict[int,dict[str,int]]`, `shortages: tuple[dict,...]`, `deviations: tuple[dict,...]`를 가진다.

테스트 helper `exam_fixtures.py`의 인터페이스도 고정한다: `make_repo(root: Path)->Path`(공통 MD·6장 학습 근거·로컬 자료가 있는 합성 repo), `make_candidates(repo: Path, chapters: tuple[int,...]=(1,2,3,4,5,6))->list[dict]`(적격·다양한 가족·출처의 150개 이상 후보, 6장 web 후보 없음), `make_pack(repo: Path)->Path`(75개 합성 시험 HTML과 `.pack/v1/`), `approve_questions(html: Path)->None`(TEST ONLY 표시로 검토 fixture 작성). 이후 작업의 기능이 필요하면 helper에 순차 구현하고 먼저 필요한 시점 전에는 호출하지 않는다. conftest에 `repo`(make_repo(tmp_path/'repo')), `topics`(repo의 scope.json topics를 id로 인덱싱한 dict), `six_chapter_candidates`(make_candidates(repo)) fixture를 정의한다. mock 근거로 실제 학술 검토 pass를 쓰지 않는다.

### Task 1: 범위·후보·단답형 계약

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_contract.py`
- Create: `.agents/skills/bio-exam-forecast/references/pack-contract.md`
- Test/Create: `.agents/skills/bio-exam-forecast/tests/conftest.py`, `exam_fixtures.py`, `test_contract.py`

**Interfaces:**
- Consumes: 명세 2~3·6~7절의 입력과 필드.
- Produces: `parse_scope(text: str)->Scope`, `validate_candidate(candidate: dict, scope: Scope, topics: dict)->list[str]`, `validate_pack(pack: dict)->list[str]`, `normalize_short(value: str, *, case_sensitive: bool=True)->str`, `ExamError`, `Scope`, `Selection`.

- [x] **Step 1: Write failing contract tests**

```python
def test_scope_range_and_single():
    assert parse_scope(' 1장 ～ 6장 ').chapters == (1, 2, 3, 4, 5, 6)
    assert parse_scope('4장-5장').label == '4장-5장'
    assert parse_scope('3').label == '3장'

@pytest.mark.parametrize('value', ['6장~1장', '0', '-1', '1,3', '../1장', ''])
def test_scope_rejects_invalid(value):
    with pytest.raises(ExamError): parse_scope(value)

def test_short_normalization_preserves_meaning():
    assert normalize_short('  BRCA1  ') == 'BRCA1'
    assert normalize_short('A a') != normalize_short('Aa')
    assert normalize_short('Aa') != normalize_short('aa')
    assert normalize_short('ATP', case_sensitive=False) == 'atp'
```

추가 assertions: 1~6장 scope의 candidate required_chapters에 7이 끼거나 topic scope_status가 uncertain이면 오류; MCQ 정답이 option_ids 밖이면 오류; short canonical/accepted가 비면 오류; 문제 옵션 수와 options 모델이 다르면 오류; 최종 pack 54+21·중복 p1·가족 중복·알 수 없는 mode는 모두 오류. fixture ID만 바꾼 동일 problem을 적격으로 오인하지 않도록 원문 payload 계약도 테스트한다. types는 열린 문자열 목록이고 새 유형명도 허용하며 생성 문항의 style_basis/application 누락은 거부한다.

- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_contract.py -q`; 기대: 새 모듈 import 실패. pytest가 없으면 작업용 venv를 만들고 `pytest`, 기존 `requirements-question-bank.txt`, `playwright`를 설치한 뒤 그 Python을 이후 명령에 사용한다. 의존성 부재를 기능 RED로 보고하지 않는다.
- [x] **Step 3: Implement the contract interfaces** — 명세 필드·원문 4/5보기·생성 4/5보기·55+20·NFC+strip을 구현한다. 한국어/영어 동의어·단위는 accepted에 명시한 것만 허용한다. source/state 판단은 다음 작업에 둔다.
- [x] **Step 4: Run GREEN** — Step 2 명령, 기대: 모든 contract test PASS.
- [x] **Step 5: Commit checkpoint** — 요청받은 경우에만 위 Task 1 소유 파일을 명시적으로 stage하고 `git diff --cached --check` 후 `feat(bio-exam): define scope and mixed-question contract`로 커밋한다. 미요청이면 이 체크포인트를 기록하고 계속한다.

### Task 2: 최신 출제 경향·장별 자료 inventory와 원문 후보

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_sources.py`
- Test: `.agents/skills/bio-exam-forecast/tests/test_sources.py`, `exam_fixtures.py`
- Read/reuse: `scripts/question_bank/model.py:27-57,488-504`, `.agents/skills/bio-webquiz-forecast/scripts/exam_pool.py:20-29`

**Interfaces:**
- Consumes: `Scope`, `ExamError`; `load_bank(path, complete=True, repo_root=repo)`.
- Produces: `inventory(repo: Path, scope: Scope)->dict` (`sources`, `warnings`), `assert_fresh(repo: Path, manifest: dict)->None`, `web_candidates(repo: Path, scope: Scope)->tuple[list[dict],list[dict]]` (후보, 제외 이유), `past_candidates(repo: Path, scope: Scope)->list[dict]`.
- `sources`는 명세 4절 snapshot 배열이다. 후자의 두 collector는 의미 검토 전 `review.*.status='not_run'`인 초안만 반환한다. 기출 단답형은 이미지 대조 후 에이전트가 동일 계약으로 후보 목록에 추가한다.

- [x] **Step 1: Write failing source tests** — 다음 이름과 assertions를 구현한다.
  - `test_inventory_reads_live_policy`: policy MD를 '정책 A'→'정책 B'로 바꾸면 다음 inventory SHA가 달라지고 `assert_fresh`는 이전 manifest를 거부한다.
  - `test_missing_feedback_becomes_present`: feedback 부재를 null/missing으로 기록한 뒤 파일을 만들면 이전 manifest를 거부한다. 공통 MD 부재는 즉시 ExamError다.
  - `test_bank_discovery_ignores_historical_note`: MD에 bank 미등록이라고 쓰여 있어도 현재 bank snapshot은 present이고 검증된 후보를 발견한다. 스크립트는 자연어 서술을 파싱하지 않는다. 불일치 해석·공개는 에이전트가 policy-notes에 기록한다. 6장 bank 부재는 해당 장의 학습 근거 수집을 중단하지 않는다.
  - `test_nfc_nfd_and_bank_assets`: Unicode가 다른 경로도 한 자료로 해석한다. 원문 SVG만 problem으로 넣고 explained SVG는 solution 쪽 자료로 분리한다. 모든 source/asset/evidence 해시를 snapshot에 포함한다.
  - `test_selected_is_not_answer`: 선택 A·분석 B·공식 null인 합성 bank에서 답의 출처를 reasoned/B로 남긴다. validator 실패 bank는 오류 이유와 함께 원문 후보에서 제외한다.
  - `test_past_collector_is_unreviewed`: 기존 복습 카드로 발견해도 key/source pass를 자동 부여하지 않는다. 원문 fingerprint와 source 위치를 보존한다.
- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_sources.py -q`; 기대: exam_sources import/function 실패.
- [x] **Step 3: Implement the source interfaces** — 파일 상태는 현재 filesystem/complete validator가 우선이다. 정책 내용의 뜻은 에이전트가 `policy-notes.md`에 적고 script가 자연어를 자동 통계/규칙으로 컴파일하지 않는다. 외부 경로·모호한 Unicode 후보·저장소 밖 symlink는 거부한다. 기출 원자료 위치가 확정되지 않으면 초안에 보류 이유를 남긴다.
- [x] **Step 4: Run GREEN** — Task 1·2 test 파일을 같은 새 스킬 suite에서 실행, 기대: PASS. 실제 bank는 읽기만 하며 이 테스트에 실제 자료 상태를 고정하지 않는다.
- [x] **Step 5: Commit checkpoint** — 위 Task 2 소유 파일만, 요청 시 `feat(bio-exam): load current evidence and preserve source states`.

### Task 3: 장/형식 배정·가족 중복 방지·출처 배합

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_selection.py`
- Create: `.agents/skills/bio-exam-forecast/references/selection.md`
- Test: `.agents/skills/bio-exam-forecast/tests/test_selection.py`, `exam_fixtures.py`

**Interfaces:**
- Consumes: `Scope`, `Selection`, 적격 candidate 배열, `scope.json` topics, 이전 버전의 family/생성 발문 목록.
- Produces: `allocate_quotas(scope: Scope)->dict[int,dict[str,int]]`, `select_candidates(candidates: list[dict], scope: Scope, topics: dict, *, previous: tuple[dict,...]=())->Selection`, `selection_report(selection: Selection)->str`.

- [x] **Step 1: Write failing selection tests**

```python
def test_six_chapter_quotas():
    q = allocate_quotas(parse_scope('1~6'))
    assert [q[n]['total'] for n in range(1, 7)] == [13, 13, 13, 12, 12, 12]
    assert [q[n]['mcq'] for n in range(1, 7)] == [10, 9, 9, 9, 9, 9]
    assert [q[n]['short'] for n in range(1, 7)] == [3, 4, 4, 3, 3, 3]

def test_missing_web_bank_does_not_erase_chapter(six_chapter_candidates, topics):
    result = select_candidates(six_chapter_candidates, parse_scope('1~6'), topics)
    assert len(result.problems) == 75
    assert not result.shortages
    assert sum(p['primary_chapter'] == 6 for p in result.problems) == 12
    assert len({p['family_id'] for p in result.problems}) == 75
```

추가 tests: `test_reassigns_family_for_scarce_short_slot`는 두 형식에 쓸 수 있는 가족을 재배정해 충족 가능한 55+20을 채운다. `test_cross_source_duplicates_share_family`는 web/past 원문 fingerprint 중복을 하나만 고른다. `test_narrow_scope_reports_shortage`는 후보 8개에서 75개처럼 만들지 않는다. `test_priorities_and_previous_versions`는 실제 시험 강조/빈 소주제/미사용 가족을 우선하되 소진 시 원문 재사용을 보고한다. `test_generated_duplicate_stem_rejected`는 이전 생성 발문 재사용을 거부한다. 풍부한 독립 가족 fixture에서는 MCQ 20/10/10/15 및 short 8/4/8을 달성한다.

- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_selection.py -q`; 기대: 인터페이스 미구현 실패.
- [x] **Step 3: Implement selection** — total quota 후 명세의 largest remainder를 쓴다. 장/형식 슬롯과 family 사이의 결정적 augmenting-path matching으로 단순 greedy의 가짜 부족을 피한다. 슬롯 후보 순서는 미충족 출처 목표→명세 우선순위→미사용 가족→안정적 candidate ID다. source 배합은 soft target이고 목표 차이는 deviations로 남긴다. 발문+보기 텍스트 집합+원문 그림의 정규화 fingerprint로 source 간 정확 중복을 묶되, 보기 순서를 포함한 original_payload_sha256은 별도로 보존한다. 의미상 가족 통합은 검토된 family_id를 따른다.
- [x] **Step 4: Run GREEN** — Task 1~3 suite, 기대: 합성 사례에서 필수 제약 충족·부족 수 정확·결정적 결과. 목표 미달을 임의 확률/통계로 표현하지 않는다.
- [x] **Step 5: Commit checkpoint** — Task 3 소유 파일만, 요청 시 `feat(bio-exam): allocate chapter quotas and select distinct families`.

### Task 4: 버전별 시험 조립과 제출 후 채점 UI

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_build.py`
- Create: `.agents/skills/bio-exam-forecast/assets/exam-template.html`, `exam-runtime.js`
- Test: `.agents/skills/bio-exam-forecast/tests/test_build.py`, `test_exam_browser.py`, `exam_fixtures.py`
- Read/reuse: `.agents/skills/bio-review-pack/assets/review-template.html`, `.agents/skills/bio-problem-explain/assets/vendor/`

**Interfaces:**
- Consumes: 부족 없는 Selection, scope/topics, inventory/source-manifest, policy-notes, 실행별 policy_summary; `normalize_short`와 같은 규칙의 JS 비교.
- Produces: `init_version(repo: Path, scope: Scope)->Path`, `write_pack(src: Path, selection: Selection, scope_data: dict, manifest: dict, policy_notes: str, policy_summary: dict)->dict`, `render_exam(repo: Path, src: Path)->str`, `build_exam(repo: Path, src: Path)->Path`.
- init은 `시험예상/<scope.label>/.pack/v<K>/`를 mkdir(exist_ok=False)로 예약하고 기존 HTML과 version 폴더의 최대 K 다음을 선택한다. 부족 Selection은 write_pack에서 거부한다. 카드 ID는 p1~p75로 새로 매기고 candidate_id를 보존한다.

- [x] **Step 1: Write failing builder/browser tests**
  - `test_version_and_layout`: 두 번 init하면 v1/v2, 이전 파일 해시 불변; 폴더/manifest range 불일치 거부; root에는 HTML과 .pack만 존재.
  - `test_original_content_and_answers`: 보기 4개 원문·그림·수치·순서 보존, gene symbol·허용답 모델 보존, A~E를 11개씩 맞추려고 원문을 바꾸지 않음.
  - `test_submit_is_only_reveal_boundary`(Playwright): 첫/마지막 MCQ와 short 입력 후에도 submit 전 solution/provenance 숨김; Enter/키보드 접근·화면 375px에서 입력 가능; 제출하면 전 문항 채점/출처 공개.
  - `test_short_pending_and_reset`: 'Aa' 정답에 'aa' 입력 시 자기채점 대기, accepted 동의어는 자동 일치, 1/2↔0.5는 명시된 경우만 허용; 빈 답은 미응답으로 집계하고 오답/자기채점에 합치지 않는다. reset은 선택/입력/정답 공개를 모두 초기화.
  - `test_no_js_and_no_remote_resources`: JS 비활성 상태에도 정답 숨김, 인쇄 스타일에도 submit 전 정답 숨김, localhost 외 네트워크 요청 0. 수식·SVG·래스터 원문 모두 표시.
- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_build.py .agents/skills/bio-exam-forecast/tests/test_exam_browser.py -q`; 기대: 새 build/template 부재 실패. 브라우저 설치 부재면 먼저 환경 문제를 해결한다.
- [x] **Step 3: Implement versioning and rendering** — existing review-template의 style 블록을 읽어 스타일/토큰을 재사용하되 panels-ui/pager-ui/review interaction은 설치하지 않는다. 새 template에 styles/content/model/runtime 슬롯을 명시하고 slot 미치환을 오류로 처리한다. 로컬 vendor는 exam `.pack/v<K>/vendor/`로 필요한 사본만 복사한다. 외부 CDN 스크립트는 가져오지 않는다. SVG ID를 pN별로 재매핑하고 exam/해설 그림을 구별한다. 원문 자산을 변경하지 않는다.
- [x] **Step 4: Implement exam-runtime.js** — native radio/input과 전체 submit/reset만 사용한다. 답 모델은 application/json으로 안전하게 embed하고 `<`를 escape한다. 소스 열람 방지·영구 저장·타이머를 추가하지 않는다. 제출 전 답 숨김은 CSS/hidden의 초기 HTML 상태로 보장한다. 수식 입력 영역은 KaTeX 자동 변환에서 제외한다.
- [x] **Step 5: Run GREEN** — Step 2 명령; 1280x900·375x812 × light/dark에서 PASS, 가로 overflow/콘솔 오류/자원 실패 0. 빌드는 초안을 만들 뿐 실제 검토 pass를 기록하지 않는다.
- [x] **Step 6: Commit checkpoint** — Task 4 소유 파일만, 요청 시 `feat(bio-exam): render versioned mixed-format exam sessions`.

### Task 5: 검토 무효화·원문 보존 검사와 시각 자료를 유지한 블라인드 사본

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_check.py`, `exam_blind.py`
- Create: `.agents/skills/bio-exam-forecast/references/verification.md`
- Modify: `.agents/skills/bio-exam-forecast/scripts/exam_build.py` (build 후 검토 초기화)
- Test: `.agents/skills/bio-exam-forecast/tests/test_check.py`, `test_blind.py`, `exam_fixtures.py`

**Interfaces:**
- Consumes: exam_contract, assert_fresh, 75-card pack, question-review.json.
- Produces: `check_set(html: Path, *, require_reviews: bool=False)->list[str]`, `question_input_hash(src: Path, html: Path)->str`, `initial_question_review(src: Path, html: Path)->dict`, `write_blind(html: Path, output: Path)->Path`.
- question review는 명세 8절 네 항목에 `status/reviewer/evidence`, 각 항목 `items[p1..p75]`를 둔다. input_hash는 pack/blueprint/scope/policy/candidate/manifest/75카드/HTML/의존 자산을 포함하고 review 자신은 제외한다. 실제 근거의 freshness는 별도로 검사한다.

- [x] **Step 1: Write failing gate/blind tests**
  - `test_incomplete_or_unreviewed_rejected`: 74문항·short key 누락·빈 풀이·범위 밖 requirement·중복 family·blueprint 불일치는 기계 오류; not_run·일부 문항 pass 누락은 require_reviews=True에서 오류.
  - `test_policy_and_assets_invalidate_review`: policy MD·feedback·bank source PNG·카드 수치 각각 한 바이트 변경 시 이전 pass 거부. 부재 feedback 신규 등장도 거부.
  - `test_rebuild_resets_review`: 같은 버전의 미완료 초안을 수정/rebuild하면 모든 검토 not_run; 해시만 새 값으로 덮어 승인하지 않음. 기존 완료 버전은 수정하지 않고 새 버전 필요.
  - `test_blind_retains_visuals_and_short`: 75문항·20short·SVG path/텍스트·표·래스터 보존, answer/solution/hint/style_basis/source/provenance/model/data-correct/허용답·풀이전용그림 전부 제거; 그림 파일은 blind 전용 assets로 복사하고 링크 유효.
  - `test_empty_blind_is_failure`: 0문항/중복 ID/보기 모델 불일치는 오류다. 사람이 PDF/그림을 읽었다는 판정은 DOM 검사만으로 생성하지 않는다.
- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_check.py .agents/skills/bio-exam-forecast/tests/test_blind.py -q`; 기대: 새 checker/blind 미구현 실패.
- [x] **Step 3: Implement validation and blind export** — 기존 parser/해시 helper는 재사용하되 단답형을 제외하지 않는다. blind 문제 DOM은 보존하고 SVG를 설명 텍스트로 대체하지 않는다. 원문 mode의 payload와 current source를 대조하고 variant는 원문 동일성 검사를 강제하지 않는다. 의미상 범위·style 적용·답 노출은 실제 reviewer evidence를 요구한다.
- [x] **Step 4: Run GREEN** — 새 스킬 suite, 기대: 기계·문항검토·입력 변경·그림 보존 tests PASS. 문항 전체의 학술적 타당성을 합성 테스트로 확인했다고 보고하지 않는다.
- [x] **Step 5: Commit checkpoint** — Task 5 소유 파일만, 요청 시 `feat(bio-exam): gate reviews and export complete blind exams`.

### Task 6: 75문항·단답형을 기존 해설 파이프라인에 연결

**Files:**
- Create: `.agents/skills/bio-problem-explain/scripts/mpe_exam.py`
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_types.py:8-37`, `mpe_source.py:206-218`, `mpe_render.py:18-32,160-193`
- Test/Create: `.agents/skills/bio-problem-explain/tests/exam_helpers.py`, `test_exam_source.py`, `test_exam_pipeline.py`

**Interfaces:**
- Consumes: `check_set(html, require_reviews=True)`, `assert_fresh`, `Problem`, `SourcePack`, 기존 `mpe_cli.extract/load_run/build`, `publish_explanation`.
- Produces: `mpe_exam.load_exam_source(path: Path, repo: Path)->SourcePack`; `mpe_types.ShortAnswerModel(canonical: str, accepted: tuple[str,...], case_sensitive: bool)`와 `Problem.short_answer: ShortAnswerModel|None=None`(기존 positional 필드 뒤 default 추가).
- SourcePack: profile='exam', range='1장-6장', slug='시험예상_v1', problems p1~p75. MCQ만 choice를 가지며 short는 short_answer와 reference_answer/steps를 가진다. import는 전역 sys.path를 다른 skill로 바꾸지 않는 고유 module alias/필요 시 함수 내부 import를 사용한다.
- exam_helpers에 `repo`와 `approved_exam` fixture를 제공한다. repo는 새 스킬 exam_fixtures.make_repo로 만들고, approved_exam은 make_pack(repo) 후 approve_questions를 호출한 경로다. 모듈은 고유 alias로 로드해 기존 helpers와 충돌시키지 않는다. 해설 조각은 기존 `helpers.fragment(problem)` 합성 계약을 재사용한다.

- [x] **Step 1: Write failing adapter tests**

```python
def test_exam_has_all_formats(approved_exam, repo):
    pack = load_exam_source(approved_exam, repo)
    assert pack.profile == 'exam'
    assert len(pack.problems) == 75
    assert sum(p.choice is not None for p in pack.problems) == 55
    assert sum(p.short_answer is not None for p in pack.problems) == 20
    assert [p.id for p in pack.problems] == [f'p{i}' for i in range(1, 76)]
```

추가 tests: `test_exam_explicit_only`에서 all/최신은 기존 복습노트만 선택; `test_exam_mismatch_rejected`에서 range/version/path/key/75집합 불일치와 미검토 질문 거부; `test_exam_context_change_requires_extract`에서 policy/신규feedback/short 허용답 변경 후 load_run·publish 거부; `test_exam_output_layout`에서 두 HTML과 `.pack/v1/` 아래 해설 MD/figures/data, version 전용 reading key, 단답형 정답·허용답이 HTML/MD 해설에 모두 보존; `test_explanation_rebuild_resets_four_reviews`에서 기존 pass 재사용 차단.

- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-problem-explain/tests/test_exam_source.py .agents/skills/bio-problem-explain/tests/test_exam_pipeline.py -q`; 기대: mpe_exam/ShortAnswerModel 부재 실패.
- [x] **Step 3: Implement exam adapter and routing** — 명시 파일명 `시험예상문제_(<정규화 범위>)_v<K>.html`만 분기한다. manifest·카드·정답·검토 일치를 재확인한다. context_hashes에 pack/blueprint/scope/policy/candidates/manifest/question-review와 present source files를 포함한다. missing 새 등장은 adapter의 assert_fresh로 차단한다. 원본문·보기·그림은 그대로 Problem으로 전달한다.
- [x] **Step 4: Implement naming/render support** — `SIDES['exam']='.pack/v<K>'`는 상수값 대신 side_of(pack)의 exam 분기로 계산한다. stem=`문제해설_<range>_시험예상_v<K>`; title과 읽음 키도 exam/range/version 포함. short canonical/accepted는 해설 본문에 공개하고 명시적으로 보존 검사한다. 기존 choice 상호작용은 MCQ만 유지한다. 기존 contract/publish가 새 context와 side 경로를 검사하는지 tests로 확인하고 불필요한 변경은 하지 않는다.
- [x] **Step 5: Run GREEN and regressions** — `python3 -m pytest .agents/skills/bio-problem-explain/tests -q`; 기대: 기존 review/forecast와 새 exam 모두 PASS. 별도 프로세스로 `python3 -m pytest .agents/skills/bio-webquiz-forecast/tests -q` 실행, 기대: PASS. 동명 helpers/tests 충돌을 막기 위해 두 suite를 하나의 pytest 명령으로 합치지 않는다.
- [x] **Step 6: Commit checkpoint** — Task 6 소유 파일만, 요청 시 `feat(bio-explain): support version-bound mixed-format exam inputs`.

### Task 7: CLI 상태 흐름과 한 번의 수정 횟수·완료 판정

**Files:**
- Create: `.agents/skills/bio-exam-forecast/scripts/exam_cli.py`
- Create: `.agents/skills/bio-exam-forecast/references/explanation-handoff.md`
- Modify: `.agents/skills/bio-exam-forecast/scripts/exam_check.py`
- Test: `.agents/skills/bio-exam-forecast/tests/test_cli.py`, `test_handoff.py`

**Interfaces:**
- Consumes: Tasks 1~6의 helper와 명시 경로 해설 CLI.
- Produces: `exam_cli.main(argv: list[str]|None=None)->int`, `completion_status(question_html: Path, explanation_html: Path|None, workflow: dict)->dict`.
- Commands: `prepare --repo PATH --scope TEXT --run PATH`; `select --run PATH`; `build --run PATH`; `check --run PATH [--final]`; `blind --run PATH --out PATH`; `status --run PATH [--explanation PATH]`.
- RUN은 새 빈 폴더만 허용한다. `run.json`은 repo 절대 경로·scope·sources·후보 경로·예약 src·`repairs_used:0`·상태를 가진다. prepare는 `run.json`, `source-manifest.json`, 원문 초안 `candidates.json`, 작성 전 상태의 `scope.json`·`policy-notes.md`·`policy-summary.json`을 만든다. select는 에이전트가 검토·저작한 이 파일들을 소비하며 빈 정책/미검토 후보로 최종 선택하지 않는다. build 전 버전을 예약한다. 스크립트가 LLM 호출·자기 승인·외부 task 생성을 하지 않는다.

- [x] **Step 1: Write failing CLI/handoff tests**
  - `test_prepare_select_build_check_roundtrip`: 합성 6장 입력에서 파일 계약과 55+20이 이어지고 검토 전 --final 실패, fixture 검토 후 성공.
  - `test_shortage_stops_before_build`: 자료 부족의 상세 원인·장/형식 부족 수를 남기고 nonzero; 빈 HTML/이전버전 대신 성공 금지.
  - `test_one_repair_budget_across_handoff`: 문제 수정 1회+해설 수정 1회 후 세 번째 수정 요청은 보류; 새 explain RUN으로 카운터 초기화 금지.
  - `test_explanation_failure_is_partial`: 질문 검증 pass·해설 누락/fail이면 partial, 두 HTML에 현재 source와 묶인 실제 검토가 있을 때만 complete. 해설 단순 파일 존재만으로 성공 금지.
  - `test_no_real_coursework_mutation`: 모든 명령에서 임시 repo 밖·기존 버전·source MD/bank 해시는 불변; 실제 문제 생성은 설치 tests에 포함하지 않음.
- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_cli.py .agents/skills/bio-exam-forecast/tests/test_handoff.py -q`; 기대: CLI/status 미구현 실패.
- [x] **Step 3: Implement orchestration boundaries** — load/run마다 source freshness 확인; status는 question gate와 해설 manifest/context/validation 현재성을 검사한다. 수정 횟수는 workflow 주체 에이전트가 run.json에 기록하고 helper는 0~2·단조 증가를 검사한다. handoff 문서는 질문 오류→문제 재검토+새 해설 RUN, 해설 오류→build/check+네 검토를 정확히 명시한다. 파일 존재를 검토 pass 대신 쓰지 않는다.
- [x] **Step 4: Run GREEN** — 새 스킬 전체 suite, 기대: CLI·partial/complete·수정 예산·source 불변 tests PASS.
- [x] **Step 5: Commit checkpoint** — Task 7 소유 파일만, 요청 시 `feat(bio-exam): orchestrate evidence-bound exam and explanation runs`.

### Task 8: 스킬 등록·실제 경향 반영 절차와 전체 합성 수용 검증

**Files:**
- Create: `.agents/skills/bio-exam-forecast/SKILL.md`, `references/authoring.md`
- Create: `.claude/skills/bio-exam-forecast` (symlink)
- Modify: `.agents/skills/bio-problem-explain/SKILL.md`, `.agents/skills/bio-problem-explain/references/verification.md`
- Test/Create: `.agents/skills/bio-exam-forecast/tests/test_skill_files.py`, `test_acceptance.py`

**Interfaces:**
- Consumes: 모든 helper/CLI, 공통 MD의 live 경로, 기존 해설 1~7단계.
- Produces: 사용자 호출 가능한 skill + 검토 가능한 합성 75문항/해설 end-to-end 테스트.

- [x] **Step 1: Write failing skill/acceptance tests** — SKILL frontmatter name과 exam 전용 trigger, 공통 MD/장별feedback 읽기, policy-notes·문항 style_basis 연결, strict 범위·55+20·의미 검토·source/분석답 구별·handoff·partial 보고가 명시됐는지 검사한다. 테스트는 문서 키워드만으로 의미 검증 완료를 주장하지 않는다. `.claude` link target, 모든 reference/script 링크 존재도 확인한다.
- [x] **Step 2: Run RED** — `python3 -m pytest .agents/skills/bio-exam-forecast/tests/test_skill_files.py .agents/skills/bio-exam-forecast/tests/test_acceptance.py -q`; 기대: SKILL/등록/수용 흐름 부재 실패.
- [x] **Step 3: Write the skill workflow and register** — 다음 순서를 짧은 SKILL에 쓰고 상세는 해당 reference에 둔다: 범위→live 자료 읽기/기록→scope·후보 의미 감사→배정/저작→build/check→75문항 blind 실제 풀이→원문/범위/style/브라우저 검토→명시 HTML로 해설→최대 2회 수정·재검토→최종 보고. 정책 읽기 단계에서 최신 MD를 따라 policy_summary의 유형·난이도 목표를 정하고 불명확한 값은 null/이유로 남긴다. policy-notes와 문항 style_basis에 실제 절·판별 기준·적용을 연결하며, 경향 본문·난이도 비율·기존 15문항 배합을 코드에 복사하지 않는다. 해설기 문서에는 exam 명시 입력과 단답형 허용답 검토만 추가한다.
- [x] **Step 4: Run synthetic end-to-end acceptance** — 임시 repo에서 bank 없는 6장을 포함한 75개/원문4보기/수식/표/SVG/래스터/단답형을 조립하고 TEST ONLY 검토 fixture로 기존 해설 CLI extract/build/check/publish를 연결한다. Playwright로 문제·해설 각각 1280/375 × light/dark를 확인한다. 이 검증은 배관·UI 수용 검증이며 실제 학술 출제 검토가 아니다. 사용자가 실제 세트를 호출하면 별도 실제 source_visual/content/independent 검토를 수행해야 한다.
- [x] **Step 5: Run GREEN and final isolated suites** — 아래 명령을 각각 별도 프로세스로 실행한다. 기대: 모든 pytest PASS와 diff 오류 0. 브라우저 테스트가 skip되면 완료로 보고하지 않고 원인을 해결하거나 미검증으로 명시한다.

```bash
python3 -m pytest .agents/skills/bio-exam-forecast/tests -q
python3 -m pytest .agents/skills/bio-problem-explain/tests -q
python3 -m pytest .agents/skills/bio-webquiz-forecast/tests -q
python3 -m pytest tests/test_question_bank_model.py -q
git diff --check
git status --short
```

- [x] **Step 6: Commit checkpoint and delivery** — 요청 시 Task 8 소유 파일과 검증된 이 작업 범위만 명시적으로 stage, `git diff --cached --stat`·`git diff --cached --check` 후 `feat(bio-exam): register source-grounded exam forecast workflow`. 미요청이면 변경 파일·테스트 증거만 보고한다. 실제 1~6장 세트·커밋·푸시를 자동 추가하지 않는다.

## 자체 검토 기록

- 명세 1~3: Task 1/3/7; 4: Task 2/5/8; 5: Task 3; 6: Task 1/2/4/5; 7: Task 4/6; 8: Task 5/6/7/8; 9: Task 7/8에 연결했다.
- 다섯 Review Focus 각각에 해당 test를 배치했다. 기술 검사와 의미 검토를 구별하고 실제 출제 경향 MD 본문 복제·실제 문제 자동 생성을 제거했다.
- Scope/Selection/후보 JSON/p1~p75/exam profile/해설 이름·version 하위 경로가 작업 사이에서 일치한다. 선택형 기존 positional 생성자는 short_answer default 추가로 유지한다.
- 새 helper는 역할별로 분리하고 `select.py`처럼 표준 라이브러리 이름과 충돌할 파일명을 사용하지 않는다. 기존 동명 test helpers는 suite별 프로세스로 분리한다.
- 설치 수용 검증은 합성 자료로 수행하며 실제 시험 적중률·학습 효과·공식 채점 확인으로 표현하지 않는다.

## 실행 인계

계획과 명세 검토 후 실행 방식을 선택한다. 추천은 **Native(직접 구현)**다. 8개 작업이 동일 후보 계약·선정 결과·해설 context에 순차 의존하므로 같은 세션에서 인터페이스를 유지하기 쉽다. Native면 `executing-plans`로 구현하고 마지막에 독립 검토를 수행한다. Subagent-driven을 선택하면 `subagent-driven-development`에 따라 작업별 구현/검토를 분리한다. 실행 선택 전에는 코드 구현을 시작하지 않는다.

실행 기록(2026-10-16): 직접 구현 및 최종 독립 검토를 완료했다. 조건부 commit checkpoint는 변경 검증과 미커밋 보존으로 처리했으며 커밋/푸시는 실행하지 않았다. 실제 결과와 구현 판단은 `2026-10-15-bio-exam-forecast-verification.md`를 따른다.
