# 5장 웹과제 피드백 기반 스킬 개선 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 5장 실제 웹과제에서 확인한 명칭·비교 단위·분류 경계의 요구를 생성 스킬과 문항별 피드백에 연결한다.

**Architecture:** 기존 bio-review-pack의 webquiz-style/note-feedback을 공통 정책으로 사용한다. 등록 스킬은 검증된 bank에서 장별 피드백으로 연결하고 노트·예상문제·해설·커닝페이퍼·코칭 지침이 이를 소비한다. 실행 코드·저장 스키마·UI를 추가하지 않고 기존 검사와 실제 사례 재검토로 전달 경로를 확인한다.

**Tech Stack:** Markdown skill instructions, 기존 Python unittest/pytest 검사, JSON question-bank 검증, SHA256 및 원문·본문 대조.

**Spec:** `docs/superpowers/specs/2026-10-15-bio-ch5-feedback-skills-design.md` — 같은 채팅의 설계를 고정한 동반 명세이며 구현자는 두 문서를 읽는다.

## Global Constraints

- 이번 범위는 스킬·검증 지침·5장 피드백이며, 기존 학습 산출물 재생성은 제외한다.
- 공식 답은 전부 미확인이다. 선택과 분석 답의 차이를 공식 오답 수로 표현하지 않는다.
- 7번을 개인 취약점의 증거로 세지 않는다. 무선택과 원문 방향 생략을 따로 기록한다.
- 다른 장에 5장 용어를 강제하지 않는다. 본문 동의어는 확인된 원천에만 근거한다.
- 기존 발문 복제·실제 웹과제 발문 복사 금지는 유지한다.
- 예상 15문항, 기출 5·신규 10, 기존 기출 모드 예외, 정답 A~E 각 3개는 유지한다.
- 새 JSON 스키마·pack.json 필드·UI·자동 개인 진단기를 만들지 않는다.
- source_visual/content/independent/browser, 해시·수정 최대 2회·발행 보류 계약은 유지한다.
- `웹과제/5장/` 입력은 보존한다. 계획 작성 마지막 확인에서 원본은 별도 커밋 `b69a977`로 추적 중이다. 이번 작업에서 새로 만드는 note-feedback.md만 변경 범위에 포함하며 부모 폴더 전체를 stage하지 않는다.
- `.agents/skills/`가 수정 원본이다. `.claude/skills/` 심볼릭 링크를 별도로 복사·수정하지 않는다.
- 복습노트·기존 예상 v1~v4·풀이기록·bank/raw/SVG·기존 감사표는 바이트를 보존한다.
- 실행은 저장소 루트에서 한다. 구현 단계에서 using-git-worktrees로 격리할 경우 5장 등록 커밋을 포함한 기준점을 사용한다. 필요한 입력이 미추적 상태로 남아 있다면 파일명·바이트 그대로 격리 작업 경로에 준비하고 해시를 확인한다. 공유 체크아웃에서 입력을 이동·삭제하지 않는다.
- 계획의 Commit 단계는 사용자 실행 요청에 커밋이 포함될 때만 수행한다. 그렇지 않으면 변경 파일과 메시지를 제안한다. push는 별도 요청 없이는 하지 않는다.

## Review Focus

1. 제출 전 선택·공식 답 미확인·문항 모호성을 개인 오개념으로 바꾸는 오류 — Task 1 수치/ID 수용 검사 및 Task 5 사례 R1.
2. 영어 병기가 이미 있는 노트와 명칭이 없는 다른 장 — Task 2 사례 R2가 병기와 회상을 구분하고 다른 장에 nonsense를 강제하지 않는지 확인.
3. 한 요소만 바꾼 연습이 원문 복사/동일 발문 금지의 우회로가 되는 오류 — Task 3 사례 R3와 기존 stem-dup/webquiz-copy 검사.
4. 피드백이 없거나 근거·본문 문장이 부족한 경우, lite/augment에서 완료를 과장하는 오류 — Task 2 사례 R4 및 기존 test_note_feedback.py.
5. 정답이 보이는 해설이나 근거 없는 동의어로 회상·학습 효과를 주장하는 오류 — Task 4 사례 R5, 기존 원문 보존·provenance·발행 검사.

지침 수정에는 문구를 그대로 복제한 새 테스트를 만들지 않는다. 기존 자동 검사로 런타임 계약을 보호하고, 새 데이터에는 누락 검사를 적용한다. 의미 충족은 아래 R1~R5의 입력·예상 행동을 근거와 대조한다. 에이전트의 사례 검토 결과는 학생 숙달의 증거가 아니다.

---

## File Structure

경로는 저장소 루트 기준이며 아래 파일만 변경 후보이다. 새 생산 코드·템플릿·스키마는 없다.

| 작업 | 생성·수정 경로 | 책임 |
|---|---|---|
| 1 생성 | `웹과제/5장/note-feedback.md` | 17문항 판별 기준과 분리된 개인 가설 |
| 1 수정 | `.agents/skills/web-quiz-extract/SKILL.md` | bank 게시 후 피드백 작성·별도 상태 보고 |
| 1 수정 | `.agents/skills/bio-review-pack/references/webquiz-style.md` | 5장 관찰, 명칭 전환·단위·분류 유형, 근거 기반 배합 |
| 2 수정 | `.agents/skills/bio-review-pack/SKILL.md` | 공통 규칙을 계획·저작·검토에 전달 |
| 2 수정 | `.agents/skills/bio-review-pack/references/note-feedback.md` | 기존 감사표에 회상/비교 단위 검토 연결 |
| 2 수정 | `.agents/skills/bio-review-pack/references/content-rules.md` | formal/warn에 명칭·대상·조건 구분 |
| 2 수정 | `.agents/skills/bio-review-pack/references/review-prompt.md` | 용어 존재와 의미 충족 구분, lite 검토 |
| 2 수정 | `.agents/skills/bio-review-pack/references/problem-selection.md` | 기존 +용어 변형에 양방향 회상 연결 |
| 2 수정 | `.agents/skills/bio-review-coach/SKILL.md` | 분석과 코칭 구분, 경쟁 가설 진단 |
| 3 수정 | `.agents/skills/bio-webquiz-forecast/SKILL.md` | 피드백 수집, 배합·완료 보고 |
| 3 수정 | `.agents/skills/bio-webquiz-forecast/references/question-blueprint.md` | 회상 카드 기록, 한 요소 변경 예외, 배합 |
| 3 수정 | `.agents/skills/bio-webquiz-forecast/references/forecast-rules.md` | 사전·사후 및 관찰·정책·가설 구분 |
| 3 수정 | `.agents/skills/bio-webquiz-forecast/references/card-brief.md` | 문제에서 명칭 대응 누설 방지 |
| 3 수정 | `.agents/skills/bio-webquiz-forecast/references/blind-brief.md` | 명칭·단위에서 필요한 노트 근거 확인 |
| 4 수정 | `.agents/skills/bio-problem-explain/references/authoring.md` | recall/pitfall의 명칭·결정적 차이 |
| 4 수정 | `.agents/skills/bio-problem-explain/references/verification.md` | 원문/해설 경계와 의미 검토 |
| 4 수정 | `.agents/skills/bio-problem-explain/assets/port-provenance.json` | 위 두 문서의 현재 destination 해시 |
| 4 수정 | `.agents/skills/bio-cheatsheet/SKILL.md` | 공통 피드백 수집과 범위 제한 |
| 4 수정 | `.agents/skills/bio-cheatsheet/references/panic-patterns.md` | 5장 사실과 실전 판별 패턴 |
| 4 수정 | `.agents/skills/bio-cheatsheet/references/content-rules.md` | ② 근거 있는 용어 대응, 나머지 단위/경계 |
| 4 수정 | `.agents/skills/bio-cheatsheet/references/section-brief.md` | 작성자에게 피드백·근거 전달 |
| 4 수정 | `.agents/skills/bio-cheatsheet/references/review-brief.md` | 동의어 근거·개인 가설 일반화 검토 |
| 5 생성 | `docs/superpowers/reviews/2026-10-15-bio-ch5-feedback-skills.md` | 사례 재검토·검사 결과·보존 증거 |

## 실행 준비와 검사 환경

실행 시작 시 `git status --short`와 작업 경로를 기록한다. `웹과제/5장/` 및 기존 노트·예상 5장 산출물의 실제 파일명→SHA256 목록을 RUN에 보관한다. 생명과학 경로는 NFD이므로 실제 경로를 열거해 사용한다. `RUN`은 실행 방식에서 정한 작업 디렉터리이며 최종 산출물 디렉터리가 아니다.

bank 검증은 `.venv-question-bank/bin/python`을 사용한다. 테스트는 우선 기존 `/tmp/bio-forecast-test-env/bin/python`에서 `-m pytest --version`을 확인한다. 없어졌다면 실행의 RUN 아래 격리 venv를 만들고 pytest와 jsonschema를 준비한다. 이후 셸의 `BIO_TEST_PY`를 그 실행 파일의 절대 경로로 지정한다. 각 독립 셸 호출에서 `BIO_TEST_PY`와 `RUN`을 다시 지정한다. 이 검증용 경로를 프로젝트 의존성으로 추가하지 않는다.

서로 다른 스킬의 pytest는 `_util` 등 모듈 이름이 충돌하므로 한 프로세스에서 합치지 않는다. 초기 기존 실패가 있으면 수정 전 재현과 작업에 따른 새 실패를 구별하고 교육 지침과 무관한 코드를 고치지 않는다.

### Task 1: 장별 근거와 등록 후 피드백 연결

**Files:** File Structure의 작업 1 세 파일. 참조 위치: web-quiz-extract 26~34행, webquiz-style 5~40행·72~107행.

**Interfaces:**
- Consumes: bank의 assessment/sources/questions/original/observations/analysis, intake, 해당 raw 및 실제 교재·강의/STT 근거.
- Produces: `note-feedback.md`의 `## 출제 관찰`, `## 문항별 학습 피드백`, `## 개인 학습 가설`; 문항별 제목은 `### q01 제목`부터 `### q17 제목`까지. 기존 audit의 피드백 ID/source 인터페이스를 유지한다.
- 등록 후 bank와 피드백의 완료 상태는 별개다. 피드백 작성 실패가 기존 bank 게시 트랜잭션을 되돌리거나 official_answer를 바꾸지 않는다.

- [x] **Step 1: 아래 코드를 `RUN/check_ch5_feedback.py`에 저장하고 저장소 루트에서 `.venv-question-bank/bin/python "$RUN/check_ch5_feedback.py"`로 실행한다.** 현재 피드백 파일 부재로 실패해야 한다. 예상과 달리 파일이 있으면 덮어쓰지 말고 기존 내용을 대조한 후 차이만 계획한다.

```python
import json, re
from pathlib import Path
root = Path.cwd()
bank = json.loads((root / '웹과제/5장/questions.json').read_text())
feedback = root / '웹과제/5장/note-feedback.md'
assert feedback.is_file(), '5장 note-feedback 누락'
text = feedback.read_text()
rows = re.findall(r'^### (q\d{2}) [^\n]*\n(.*?)(?=^### |^## |\Z)', text, re.M | re.S)
expected = {f"q{q['number']:02d}": q for q in bank['questions']}
assert len(rows) == len(expected) == 17
assert {qid for qid, _ in rows} == set(expected)
for qid, body in rows:
    for sid in expected[qid]['source_ids']:
        assert re.search(rf'\b{re.escape(sid)}\b', body), (qid, sid)
print('PASS: 17개 피드백 ID/source 대조')
```

- [x] **Step 2: 원본·근거를 재대조하고 5장 피드백을 작성한다.** 각 문항에 source, 판별 기준, 실제 자료 위치/인용, 대상 노트 토픽, 원문 주의점을 넣는다. 별도 출제 관찰에는 명세의 17/84·부정형 번호·수치/서열/표 구분을 넣는다. 서두에 사용한 근거 파일 path/SHA256을 기록한다. 개인 가설은 명세의 네 행을 출발점으로 하되 모두 미확인 상태를 유지한다. 분석 답을 공식 답이라 쓰지 않는다.

- [x] **Step 3: 공통 출제 기준과 등록 지침을 연결한다.** 5장 절을 기존 1~3장 통계와 구분해 추가한다. 새로운 유형도 기존 정의/실제 예/만드는 법/피할 것 구조를 따른다. 명칭 전환은 기존 용어 바꿔 쓰기에 포함하며 새 data-types를 추가하지 않는다. 4절의 partC 기본 75~80%는 장별 근거가 부족할 때의 참고 생성 정책으로 명시하고 장별 근거를 우선한다. 기출 재사용은 미집계로 남긴다. 추출 스킬 마지막에 피드백 작성·원본 재검토·별도 상태 보고를 연결한다.

- [x] **Step 4: Step 1을 다시 실행하고 기존 검사를 실행한다.**

Run: `.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/5장/questions.json' --complete`

Run: `"$BIO_TEST_PY" -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q`

Expected: ID/source 검사 PASS, bank `Valid: 17 questions (complete)`, 기존 테스트 종료 코드 0. R1의 의미 검토도 기록한다: q07을 취약점으로 확정하지 않으며 q03/q06/q09는 분석과 선택의 차이로만 표시한다.

- [x] **Step 5: 이 작업만 검토하고 조건부 커밋한다.** 세 파일을 정확히 stage하고 `git diff --cached --check` 후 `docs(bio): connect chapter 5 evidence to skill feedback`를 사용한다. bank/raw/preview/candidate를 포함하지 않는다.

### Task 2: 노트 저작과 코칭에서 회상·비교 단위 구분

**Files:** File Structure 작업 2 여섯 파일. 주요 기존 위치: content-rules 23~39·59~71·85~89행, note-feedback 9~31행, review-prompt 64~72행, coach 진행 방식 1~8항.

**Test:** `.agents/skills/bio-review-pack/tests/test_note_feedback.py`, `test_webquiz_rules.py`, `test_skill_files.py`.

**Interfaces:**
- Consumes: Task 1의 일반 피드백/개인 가설 구분 및 기존 8열 `note-feedback-audit.md`.
- Produces: 기존 audit의 `본문 문장 또는 보류 이유`에 명칭 연결·단위·최소 판별 과정의 실제 문장을 기록하는 저작/검토 계약. 새 열·manifest 필드·런타임 함수를 만들지 않는다.

- [x] **Step 1: 현재 지침과 기존 테스트의 기준 상태를 확인한다.** 위 세 테스트 파일을 스킬 하나의 프로세스에서 실행하고 R2/R4에서 미지정된 행동을 기록한다. 기준 상태가 이미 통과한 사례를 실패했다고 쓰지 않는다.

- [x] **Step 2: 공통 저작·검토 계약을 수정한다.** 본문 영어 병기와 양방향 회상을 구별하고, 단위 혼동은 대상·조건·결과·반대 사례로 설명한다. 전문용어를 eli5에 강제하거나 모든 토픽을 길게 늘리지 않는다. 생성 +용어 변형과 실제 노트 문장으로 검토하되, 원문 카드에는 힌트를 추가하지 않는다. 피드백 없음은 미작성 보고, 근거 부족은 보류, 기존 설명 충분은 중복 방지로 처리한다. lite의 의미 검토와 augment의 기존 감사표 보존을 유지한다.

- [x] **Step 3: 코칭 지침을 수정한다.** 분석 요청이면 가설만 보고한다. 코칭을 요청하면 명칭 없는 현상→다른 이름, 비교 단위만 변경, 질문 방향만 변경을 각각 한 번에 한 개념으로 확인한다. 경쟁 가설과 확신도를 구분하고 설명을 본 뒤 성공을 최초 회상으로 세지 않는다.

- [x] **Step 4: R2/R4를 대조하고 기존 테스트를 다시 실행한다.** R2 입력은 명세에 적힌 1006 노트의 영어 병기와 ‘다른 장에는 해당 용어 없음’이다. 기대: 기존 병기를 누락으로 재진단하지 않고 영어만 바꾼 새 생성 연습을 설계하며, 다른 장은 해당 범위의 용어를 사용한다. R4 입력은 피드백 파일 부재·근거 부족·augment 실행이다. 기대: 각각 미작성/보류/본문 미반영이며, 예정을 완료로 보고하지 않는다. 실제 근거 문장과 지침 위치를 리뷰 기록에 남긴다.

Run: `"$BIO_TEST_PY" -m pytest .agents/skills/bio-review-pack/tests/test_note_feedback.py .agents/skills/bio-review-pack/tests/test_webquiz_rules.py .agents/skills/bio-review-pack/tests/test_skill_files.py -q`

Expected: 종료 코드 0, R2/R4 각 입력의 기대 행동을 지침에서 추적 가능. 문구 존재만으로 의미 통과라 보고하지 않는다.

- [x] **Step 5: 작업 2 여섯 파일만 조건부 커밋한다.** 메시지: `docs(bio): teach retrieval and comparison boundaries`.

### Task 3: 예상문제의 명칭 전환·반복·난이도 설계 연결

**Files:** File Structure 작업 3 다섯 파일. 주요 위치: SKILL 23~35·47~50행, question-blueprint 14~30행, forecast-rules 3~8행.

**Test:** `.agents/skills/bio-webquiz-forecast/tests/test_check.py`, `test_skill_files.py`.

**Interfaces:**
- Consumes: Task 1 피드백, Task 2 공통 저작 기준, 기존 blueprint 15행과 pack.json 계약.
- Produces: blueprint 표 뒤 `## 회상·비교 연습` 목록의 `카드 ID / 피드백 ID 또는 근거 토픽 / 바꾸는 요소 / 질문 방향 / 반복 이유`; 기존 15행 표·pack 필드·card data-types는 유지한다.

- [x] **Step 1: 기존 중복/원문 복사 검사를 기준 실행한다.** `test_check.py` 전체를 실행한다. 중복 방지를 완화하는 실행 코드 수정이 필요하지 않음을 확인한다. 여기서 허용할 것은 한 요소 변경이며, 동일 발문은 계속 금지다.

- [x] **Step 2: 원천 수집과 blueprint 규칙을 수정한다.** note-feedback을 입력으로 전달하고 회상·비교 연습을 기존 신규 문항 p6~p15에 배치한다. 적용 가능한 범위에만 연습을 계획하며 고정 의무 개수를 새로 만들지 않는다. 한 요소 변경은 이름/비교 단위 진단 목적·이전 카드·변경 요소를 적은 경우에만 허용한다. 기출 원문 수정·기출 재사용 제한은 기존 계약을 유지한다.

- [x] **Step 3: 난이도·개요·작성·블라인드 지침을 동기화한다.** 같은 장 근거가 있으면 근거 기반 목표를 정하고, 없으면 12/3은 명시된 참고 생성 정책으로만 쓴다. Task 1이 갱신한 공통 webquiz-style의 근거 우선 원칙을 사용한다. 그림/표가 많다고 수준을 높이지 않는다. bank 존재만으로 응시 완료를 단정하지 않으며, 이번 5장은 intake의 사용자 완료 확인을 근거로 사후 대비임을 표시한다. 이전 v1~v4는 고치지 않는다.

- [x] **Step 4: R3 재검토와 기존 검사를 실행한다.** RUN에 ‘정지→넌센스’ 한 요소 전환의 신규 문항과 명칭 전환 목적이 없는 단순 복제 사례를 작성해 새 지침으로 판별한다. 기대: 전자는 근거·변경 이유를 기록해 허용하고 후자는 거부한다. 문제 제목·aria-label·힌트 없이 보이는 영역에 답을 누설하지 않는다. 동일 발문/실제 웹과제 발문 복제는 기존 검사에서 계속 거부한다.

Run: `"$BIO_TEST_PY" -m pytest .agents/skills/bio-webquiz-forecast/tests/test_check.py .agents/skills/bio-webquiz-forecast/tests/test_skill_files.py -q`

Expected: 종료 코드 0. 기존 `test_stem_dup_across_versions`와 실제 웹과제 발문 복사 검사가 유지된다. 예상 v5나 전체 HTML은 발행하지 않는다.

- [x] **Step 5: 작업 3 다섯 파일만 조건부 커밋한다.** 메시지: `docs(bio): calibrate forecast retrieval practice`.

### Task 4: 해설·커닝페이퍼의 명칭 대응과 근거 검토

**Files:** File Structure 작업 4 여덟 파일.

**Test:** `.agents/skills/bio-problem-explain/tests/test_skill_files.py`, `test_source.py`, `test_forecast_source.py`, `test_publish.py`; `.agents/skills/bio-cheatsheet/tests/test_skill_files.py`, `test_stale.py`.

**Interfaces:**
- Consumes: Task 1의 5장 관찰과 Task 2의 명칭/대상/조건 구분.
- Produces: 기존 해설의 recall/pitfall/검증 절차 및 커닝페이퍼 ② 용어 구역·기존 근거 manifest에 반영하는 지침. 새 HTML 레이어·spec 필드는 만들지 않는다.

- [x] **Step 1: 기존 원문/발행/출처/낡음 검사를 기준 실행한다.** 아래 두 프로세스로 실행한다. 이번 변경을 위해 기존 원문 보존 assertion이나 pinned source commit을 바꾸지 않는다.

- [x] **Step 2: 해설 저작·검토 지침을 수정한다.** recall에는 낯선 이름→개념 연결, pitfall에는 오답과의 결정적 차이를 적는다. 부정형은 내용상 참·거짓과 선택 적합성을 구분한다. solve와 긴 설명을 중복하지 않고 원문에 번역을 삽입하지 않는다. independent 리뷰어에게 답안·설계 정답·설명 조각을 제공하지 않는다.

- [x] **Step 3: provenance를 규정된 생성기로 갱신한다.**

Run: `"$BIO_TEST_PY" .agents/skills/bio-problem-explain/scripts/port_provenance.py --source /Users/hyunjun_macbook_pro/Documents/Univ/자구알`

Expected: 현재 destination 해시가 수정 문서와 일치한다. source_repository/source_commit/source_sha256을 새 출처로 조작하지 않는다. diff에 이번 수정과 무관한 기존 해시 불일치가 나타나면 그 원인을 구분하며, 생성기를 통과시키려고 unrelated 내용을 변경하지 않는다.

- [x] **Step 4: 커닝페이퍼 원천·저작·리뷰 지침을 수정한다.** 5장 사실 절·공통 피드백 링크·② 용어 대응과 구별 단서를 추가한다. source에 없는 동의어와 ‘개인 가설=출제 사실’을 거부한다. 7번은 코돈표 판독으로 기록하며 표·그림 분류 차이를 명시한다. 시간 제한은 미확인으로 유지한다. 기존 시트는 재생성하지 않고 panic-patterns 변경에 따른 stale 알림과 구분한다. refresh의 본문 불변 제한을 조용히 우회하지 않으며, ② 등 본문 재작성이 필요하면 전체 재생성이 필요하다고 보고한다.

- [x] **Step 5: R5와 검사를 실행한다.** R5 입력은 원문 용어를 그대로 둔 문제, 해설에서 공개되는 명칭 대응, 근거에 없는 동의어 후보, 해설 공개 뒤의 정답이다. 기대: 원문 유지/근거 있는 대응만 허용/미확인 후보 제외/독립 회상으로 판정하지 않음. 원문과 해설의 위치·실제 근거를 리뷰 기록에 남긴다.

Run: `"$BIO_TEST_PY" -m pytest .agents/skills/bio-problem-explain/tests/test_skill_files.py .agents/skills/bio-problem-explain/tests/test_source.py .agents/skills/bio-problem-explain/tests/test_forecast_source.py .agents/skills/bio-problem-explain/tests/test_publish.py -q`

Run: `"$BIO_TEST_PY" -m pytest .agents/skills/bio-cheatsheet/tests/test_skill_files.py .agents/skills/bio-cheatsheet/tests/test_stale.py -q`

Expected: 각각 종료 코드 0, provenance의 현재 해시 일치, 기존 raw/문항 원문과 발행 보호 유지. 소스 충돌·조건 부족은 해설 규칙에 따라 공개/보류한다.

- [x] **Step 6: 작업 4 여덟 파일만 조건부 커밋한다.** 메시지: `docs(bio): align explanations and lookup sheets with quiz feedback`.

### Task 5: 전체 규칙 재검토와 보존 증거 정리

**Files:** Create `docs/superpowers/reviews/2026-10-15-bio-ch5-feedback-skills.md`. 필요 수정은 해당 소유 Task로 되돌리고 관련 검사를 재실행한다.

**Interfaces:**
- Consumes: 명세, Task 1~4 변경, 기준 상태, R1~R5의 입력·기대·실제 행동, 초기 파일 SHA256 목록.
- Produces: 요구→수정 파일→실제 근거→PASS/보류/미해결의 검토 기록과 최종 변경 범위.

- [x] **Step 1: 기존 4장 자료·5장 자료·자료 없는 다른 장을 대상으로 지침을 따라 재검토한다.** R1~R5마다 입력과 기대 행동이 앞 Tasks 정의와 같은지 확인한다. 기존 4장 provisional 상태는 유지하고, 5장만 보고 모든 장의 용어·배합을 확정하지 않는다. 작성자와 다른 최종 리뷰어는 실제 문장·출처를 확인하고 누락/충돌을 지적한다. 이 검토는 새로운 학생 풀이 실험이 아니다.

- [x] **Step 2: 기존 전체 자동 검사를 스킬별 별도 프로세스로 실행한다.**

```bash
"$BIO_TEST_PY" -m pytest .agents/skills/bio-review-pack/tests -q
"$BIO_TEST_PY" -m pytest .agents/skills/bio-webquiz-forecast/tests -q
"$BIO_TEST_PY" -m pytest .agents/skills/bio-problem-explain/tests -q
"$BIO_TEST_PY" -m pytest .agents/skills/bio-cheatsheet/tests -q
.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/5장/questions.json' --complete
git diff --check
```

Expected: 새 실패 0, bank complete 통과. 초기부터 있던 실패는 baseline과 함께 별도 보고한다. 검사 환경이나 브라우저 구성요소가 없으면 실행하지 못한 검사를 통과했다고 쓰지 않는다. 이번에 브라우저/UI 산출물을 바꾸지 않으므로 불필요하게 학습 자료를 재발행하지 않는다.

- [x] **Step 3: 보호 대상 SHA256·변경 파일·심볼릭 링크를 재확인한다.** 보호 목록은 초기와 동일해야 한다. 새 파일은 계획된 note-feedback과 리뷰 문서뿐이다. 필요한 증거가 없는 내용은 보류하고, 지침 누락은 소유 Task로 되돌린다. 기존 note-feedback 감사표나 v1~v4의 역사적 문장을 고치지 않는다.

- [x] **Step 4: 리뷰 문서에 실제 결과를 작성한다.** 실행한 명령·종료 코드, 테스트 요약, R1~R5의 근거, 미확인 개인 가설, 보류, 보호 파일 해시 대조를 기록한다. `스킬 개선 완료`와 `학생 숙달 확인`, `기존 산출물 반영 완료`를 구분한다.

- [x] **Step 5: 리뷰 문서만 조건부 커밋하고 사용자에게 전달한다.** 메시지: `docs(bio): record chapter 5 feedback verification`. 커밋한 경우 staged 범위와 commit ID를 보고하고, push는 별도 요청 없이는 하지 않는다.

## Self-Review 결과

- Spec coverage: 출제 관찰/가설 분리·17문항은 Task 1, 노트/코칭은 Task 2, 예상 반복/배합은 Task 3, 해설/커닝페이퍼는 Task 4, 의미 검토·보존은 Task 5가 맡는다.
- Step scan: 실행 코드 신규 구현은 없다. 데이터 누락 검사는 실제 missing→작성→PASS로 확인하고, 지침 변경은 불필요한 문구 복제 테스트 대신 기존 검사와 R1~R5를 사용한다.
- Interface consistency: 기존 JSON·blueprint 15행·audit 8열·해설 레이어를 유지한다. 신규 참조 파일은 5장 note-feedback 하나이며 등록 스킬과 소비 지침이 같은 경로를 사용한다.
- Review Focus: 다섯 항목을 R1~R5에 연결했다. 자료 부재는 없는 입력을 추론으로 채우지 않으며 모호한 문항은 학습자 오개념의 증거에서 제외한다.
- Proportion: 전체 프로그램·예시 문항을 계획 안에 구현하지 않았다. 생산 코드·템플릿·의존성을 늘리지 않는다.

## 실행 인계

사용자가 Native 직접 구현을 요청했다. 각 조건부 커밋 단계는 요청이 없어 생략했다. 공통 Markdown 계약을 여러 소비 스킬에 일관되게 전달하는 작업이어서 한 구현자가 다섯 작업을 이어 처리하고 마지막에 별도 리뷰어가 전체 변경을 검토하는 편이 효율적이다. Subagent-driven을 선택하면 각 Task별 구현·검토 게이트를 적용한다. 이 문서를 작성한 턴에서는 구현·커밋·push를 시작하지 않는다.

실행 결과: `../reviews/2026-10-15-bio-ch5-feedback-skills.md`. 독립 최종 리뷰 및 전달은 해당 기록으로 확인한다.
