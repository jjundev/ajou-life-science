# 생명과학 출제 기준 조정 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습·예상문제 생성 지침을 실제 웹과제의 짧은 적용 중심 난이도에 맞추고, 장별 증거와 생성 목표를 구분한다.

**Architecture:** 공통 정책은 기존 bio-review-pack/references/webquiz-style.md에 둔다. 두 스킬의 설계·작성·리뷰 문서와 기존 계약 테스트를 동기화한다. 유형 최소값은 기존 types_required 인터페이스를 사용하며 실행 코드와 저장 스키마는 바꾸지 않는다.

**Tech Stack:** Markdown skill instructions, Python unittest, 기존 HTML 생성·검사 CLI.

**Spec:** `docs/superpowers/specs/2026-10-09-bio-question-calibration-design.md` (이 계획과 함께 읽는다).

## Global Constraints

- 예상 기본 목표: 15문항 중 수준 1~2를 12개, 수준 3을 3개. 생성 정책이며 실제 출제 통계가 아니다.
- 복습 partC는 10~15개, 수준 1~2 약 75~80%, 나머지 수준 3을 목표로 한다.
- 기존 기출 5·새 문제 10, 기출 모드 2/2/1(기존 예외 포함), 정답 A~E 각 3개를 유지한다.
- 그림 유무·부정형·보기 개수는 난이도를 자동으로 높이지 않는다.
- 4장 관찰을 기존 확정 집계에 합산하지 않는다.
- 기존 복습팩, 예상 v1~v4, 풀이기록, question-bank 스키마와 추출 스킬은 수정하지 않는다.
- 새로운 pack.json 필드·자동 난이도 판정·배지·카드 재정렬은 추가하지 않는다.
- raw만 있는 장을 정본 bank처럼 사용하지 않는다. 생성 목표 미달은 근거와 함께 보고한다.
- 아래 경로·명령은 저장소 루트 기준이다. Python 테스트는 두 스킬별로 별도 프로세스에서 실행해 `_util` 모듈 충돌을 피한다.
- 구현 시 시작 상태와 변경 파일을 확인한다. 기존 `STT/1008 생명.md` 등 이번 작업 밖 변경은 보존하고 스테이징하지 않는다.
- 계획의 커밋 단계는 실행 요청이 커밋을 포함할 때 수행한다. 커밋 요청이 없으면 정확한 변경 목록과 커밋 메시지를 제안한다. 푸시는 별도 요청이 있을 때만 수행한다.

## Review Focus

1. raw만 있고 bank가 없는 장: 관찰 출처·미확인 상태를 공개하고 확정 집계에 합산하지 않는다 — Task 1 `test_ch4_observation_is_provisional`.
2. 그림이 있는 쉬운 문제: 그림 자체로 level 3이 되지 않는다 — Task 1 `test_level_definitions_are_consistent`.
3. 계산 거리가 없는 장: 범위를 벗어나 채우지 않고 목표 차이를 보고한다 — Task 2 `test_blueprint_handles_insufficient_material`.
4. lite·블라인드 리뷰: 정답뿐 아니라 풀이 단계와 수준을 독립 판정한다 — Tasks 1/2 `test_blind_reports_reasoning_level`.
5. 선택 유형을 빼는 세트와 과거 버전: 최소 0을 허용하고 과거 pack의 최소값도 계속 검사한다 — Task 2 `TestCheck.test_optional_types_zero` 및 기존 `test_types_required`.

테스트는 지침 전달과 기존 검사 호환성을 확인한다. 의미상의 난이도 판정은 이후 새 세트의 블라인드 리뷰 대상이다.

## File Structure

| 역할 | 수정 파일 |
|---|---|
| 공통 증거·유형 정책 | `.agents/skills/bio-review-pack/references/webquiz-style.md` |
| 복습 수준·설계 계약 | 같은 스킬 `references/problem-selection.md`, `references/manifest-guide.md` |
| 복습 작성·리뷰·보고 | 같은 스킬 `references/card-rules.md`, `references/review-prompt.md`, `SKILL.md` |
| 복습 정책 계약 검사 | 같은 스킬 `tests/test_webquiz_rules.py` |
| 예상 배합·개요·작성·리뷰·보고 | `.agents/skills/bio-webquiz-forecast/references/question-blueprint.md`, `forecast-rules.md`, `card-brief.md`, `blind-brief.md`, `SKILL.md` |
| 예상 계약·기존 인터페이스 검사 | 같은 스킬 `tests/test_skill_files.py`, `tests/test_check.py` |

신규 생산 파일·모듈은 없다. 본 설계와 계획만 신규 문서다.

### Task 1: 공통 정책과 복습 생성·리뷰 계약 조정

**Files:** File Structure의 공통 정책·복습 항목 전체.

**Interfaces:**
- Consumes: 설계 문서, `웹과제/4장/intake.md`, 연결된 원본 화면.
- Produces: 공통 수준 정의, 증거 상태 규칙, 복습 변형 설계표 `기존 열 + 수준 + 최소 풀이 단계`. manifest의 `level: int` 범위 1~3 유지.

- [ ] **Step 1: 기존 계약 테스트를 새 요구에 맞춰 변경한다.**

`tests/test_webquiz_rules.py`에서 `test_quota`의 ㄱㄴㄷ·장 섞기·낯선 참 필수 수 assertions를 제거하고 선택 유형·근거 제한·배합 목표 assertions로 바꾼다. 기존 46문항 통계 assertions는 유지한다. 다음 테스트를 추가한다:

```python
# TestWebquizStyle.test_ch4_observation_is_provisional
part = section(self.text, "### 4장 원본 관찰")
for value in ("15문항", "부정형 4", "계산 5", "그림 3", "표 1", "ㄱㄴㄷ 0",
              "공식 답 미확인", "기출 재사용 미집계", "정본 bank 미등록", "합산하지 않는다"):
    self.assertIn(value, part)
self.assertIn("웹과제/4장/intake.md", part)
```

`TestSelectionRules.test_level_definitions_are_consistent`는 selection 5절과 manifest-guide의 level 설명 양쪽에 `직접 식별`, `한 가지 원리`, `여러 조건`, `그림 유무`가 있는지 검사한다. `test_variants_table_has_type_column`을 새 열에 맞추되 기존 유형·modifier assertions를 유지한다. `TestBlindBrief.test_blind_reports_reasoning_level`은 출력 표의 `최소 풀이 단계 | 수준`과 `예상 수준은 보여 주지 않는다` 지침을 검사한다. `TestReportRules`에 기본/심화 실개수·목표 차이 보고 지침을 검사한다.

- [ ] **Step 2: 변경 테스트의 실패를 확인한다.**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_webquiz_rules.py -v`

Expected: 새 관찰 절·수준 설명·리뷰 출력 계약이 없어 FAIL. import/환경 실패라면 먼저 환경을 해결한다.

- [ ] **Step 3: 공통 정책과 복습 지침을 구현한다.**

webquiz-style 2절 아래에 `### 4장 원본 관찰`을 추가하고 raw 원본 근거·문항번호·미확인 상태를 기록한다. 1~3장 표와 재사용 비율은 유지한다. 할당은 기존 총수·토픽 상한·근거 제한을 유지하면서 선택 유형과 배합 목표로 수정한다. 표 해석을 그림과 구별해 보고하고, 문제 없이도 읽히는 장식 그림은 판독 유형으로 세지 않는다.

selection 5절과 manifest-guide의 level 정의를 일치시킨다. selection 6절의 variants 열·card-rules 작성 계약을 수정한다. review-prompt의 블라인드 출력에는 풀이 단계·수준을 추가하되 설계 수준은 숨긴다. 메인이 비교 후 원문 분류 재검토/생성 문항 수정/미달 보고를 선택하며 최대 2회 제한을 유지한다. SKILL.md의 일반·보강 보고 모두 기본/심화·목표 차이를 포함한다. 난이도 구분은 세트 안내와 내부 기록으로 제공하며 기존 카드 순서·배지 금지는 유지한다.

- [ ] **Step 4: 복습 정책과 연관 검사를 실행한다.**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_webquiz_rules.py -v`

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_manifest.py -v`

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_skill_files.py -v`

Expected: 모두 OK. 새 문구를 넣으면서 기존 범위·유일 정답·원문 보존 계약이 약해지지 않았는지 diff를 검토한다.

- [ ] **Step 5: 요청 범위에 따라 커밋 또는 커밋 제안을 남긴다.**

정확히 이 Task의 수정 파일만 스테이징한다. 메시지: `docs(review): calibrate question difficulty policy`.

### Task 2: 예상 세트 배합과 독립 난이도 리뷰 적용

**Files:** File Structure의 예상 항목 전체.

**Interfaces:**
- Consumes: Task 1 공통 수준·증거 규칙.
- Produces: blueprint `기존 열 + 수준 + 최소 풀이 단계`; blind 출력 `카드 | 고른 답 | 근거(노트 토픽) | 이의 | 최소 풀이 단계 | 수준`; 기존 `types_required: dict[str, int]` 인터페이스 유지.

- [ ] **Step 1: 예상 계약 테스트를 추가한다.**

`tests/test_skill_files.py`에 다음 테스트를 추가한다:
- `test_blueprint_calibration_contract`: blueprint의 `기본 12`, `심화 3`, `생성 정책`, 새 열과 기출 우선 분류를 검사한다.
- `test_blueprint_handles_insufficient_material`: 계산 없는 장·근거 부족 시 `범위 밖`, `목표 차이`, `보고` 지침과 장별 결정 규칙을 검사한다.
- `test_blind_reports_reasoning_level`: 위 출력 열, 설계 수준 비공개, 기존 최대 2회와 lite 적용을 검사한다.
- `test_observation_does_not_require_bank`: forecast-rules가 공통 원본 관찰을 참고할 수 있지만 raw를 partA 원문 bank로 쓰지 않는다는 지침을 검사한다.

`tests/test_check.py`의 TestCheck에 기존 인터페이스 호환 검사를 추가한다:

```python
def test_optional_types_zero(self):
    out = self.built(extra={"types_required": {"ㄱㄴㄷ": 0, "장섞기": 0}})
    self.assertEqual(check.check(out), [])
```

기존 `test_types_required`는 유지해 양수 최소값 부족 시 실패하는 동작을 확인한다. 이 호환 테스트는 현재부터 PASS여야 하며 checker를 바꾸기 위한 red test가 아니다.

- [ ] **Step 2: 새 지침 계약의 실패와 기존 인터페이스의 성공을 확인한다.**

Run: `python3 -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -p test_skill_files.py -v`

Expected: 새 정책 문구/리뷰 계약이 없어 FAIL.

Run: `python3 -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -p test_check.py -v`

Expected: OK. 실패하면 기존 상태와 테스트 입력을 먼저 진단한다.

- [ ] **Step 3: 예상 설계·작성·리뷰·보고 지침을 동기화한다.**

question-blueprint의 고정 types_required 예제를 장별 목표 예제로 바꾼다. 4장 예제는 `{"부정형":4,"계산":5,"그림":3,"표":1,"ㄱㄴㄷ":0,"장섞기":0}`이며 실제 통계가 아닌 참고 생성 목표임을 표시한다. 기존 2/2/1 기출 배치 예외와 답 분포는 유지한다. 목표는 최소 검사에 쓰이며 실개수·중복 유형과 차이는 blueprint와 보고에서 별도로 확인한다.

forecast-rules는 확정 bank 통계와 별도 원본 관찰을 구별한다. 카드 작성자는 짧은 적용과 인접 개념 오답을 우선하고 새 버전 차별화를 난이도 상승으로 처리하지 않는다. blind-brief는 정답/설계 수준 없는 사본으로 독립 수준을 출력한다. SKILL.md의 리뷰·보고에 배합 비교와 최대 2회 후 미해결 보고를 연결한다. check.py, build.py, blind.py는 수정하지 않는다.

- [ ] **Step 4: 예상 스킬 테스트 전체를 실행한다.**

Run: `python3 -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -v`

Expected: OK. 두 스킬의 같은 수준 정의·목표/관찰 구분·브리프 계약을 대조한다.

- [ ] **Step 5: 기존 산출물 호환성을 확인한다.**

각 K=1,2,3,4에 대해 별도 실행: `python3 .agents/skills/bio-webquiz-forecast/scripts/check.py 웹과제예상/4장/복습문제_4장_웹과제예상_v<K>.html`

Expected: OK. 시작부터 존재한 실패가 있으면 baseline과 구별해 보고하며 기존 파일을 수정하지 않는다. 문서만 변경했으므로 새 브라우저 렌더나 새 예상 세트 생성은 하지 않는다. 실제 난이도 검증은 이후 생성 요청 시 수행한다.

- [ ] **Step 6: 요청 범위에 따라 커밋 또는 커밋 제안을 남긴다.**

정확히 이 Task의 수정 파일만 스테이징한다. 메시지: `docs(forecast): favor direct application questions`.

## 최종 검토와 인계

- [ ] 두 Task의 검사 결과, 변경 파일, 미해결 사항을 보고한다.
- [ ] `git diff --check`와 `git status --short`로 정책 파일 밖 변경이 없는지 확인한다.
- [ ] 문서 계약 검사를 교육적 난이도 검증으로 표현하지 않는다.
- [ ] 정본 bank 미등록과 공식 답 미확인 상태가 유지되는지 확인한다.

계획 자체 검토: 설계의 증거·수준·배합·작성·리뷰·보고는 Task 1/2에 배정했다. 실행 코드와 스키마 변경이 없으므로 새 함수나 타입은 없다. Review Focus 5항목은 위 계약/호환 검사에 연결했다. 기존 산출물 보존과 목표 미달 보고를 검증 단계에 포함했다.
