# 누적 웹과제 출제 지침 갱신 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 누적된 1~6장 웹과제의 근거 현황과 출제 사례를 공통 지침·직접 연결 문서·기존 검사에 일관되게 반영한다.

**Architecture:** 기존 Markdown 지침을 보완하며 `webquiz-style.md`를 공통 출제 경향의 기준으로 유지한다. 최신 형식 집계와 과거 기출 대조 집계를 분리하고 기존 `variants.md`의 열과 유형을 재사용한다. 새 스키마·생성기·자동 분류기는 만들지 않는다.

**Tech Stack:** Markdown, Python 3 표준 라이브러리, 기존 question-bank 검증기와 unittest/pytest. 새 프로젝트 의존성은 추가하지 않는다.

**Spec:** 같은 대화의 「웹과제 출제 지침 업데이트 설계」를 아래 「설계 기준」에 보존한다. 증거 문서는 `웹과제/6장/feedback/20261110-163101-8f5e4f94/report.md`다. 실행자는 이 계획과 보고서를 모두 읽는다. 사용자가 범위 선택 #1에 다른 값을 지정하지 않고 계획 작성을 요청했으므로 ‘공통 지침과 직접 연결된 지침·검사까지 정비’를 **[confirmed by default]**로 확정한다. 실행 방식은 아직 선택되지 않았다.

## Global Constraints

- “최신 집계와 과거 집계를 분리”한다. 현재 확인값은 1~6장 92문항·부정형 33문항(약 35.9%)이며 실행 때 재확인한다.
- “새 필드나 유형은 추가하지 않는다.” `variants.md`의 기존 `형태`, `오답 보기의 의도`, `최소 풀이 단계`를 사용한다.
- “공식 답·응시 완료·전체 재사용률로 확대하지 않음.” 선택·분석 답·공식 답·응시 상태는 별개다.
- “현재 참고 목표 유지”: partC 10~15개·토픽당 최대 3개, 근거 부족 시 부정형 약 1/3·기본 약 75~80%는 생성 정책이다.
- 기존 학습 자료 재생성, 정본 bank·raw·기존 피드백 수정, 개인 약점 진단, 4~6장 기출 재사용 전수 대조는 제외한다.
- `.claude/skills/bio-review-pack`는 `.agents/skills/bio-review-pack`로 연결된다. 실제 수정은 `.agents` 정본에서만 한다.
- 불필요한 문자열 테스트를 추가하지 않는다. 기존 계약 검사와 사례별 의미 검토를 구분한다.
- 계획 작성 중에는 아래 계획 파일만 신규 작성한다. 구현·커밋·푸시는 이번 턴에 수행하지 않는다.
- 실행 시 using-git-worktrees로 격리 상태를 확인한다. 시작 시의 1110 정리노트·인터렉티브 자료, 7·8장 예상문제 `.pack/v3/`, 6장 feedback 등 다른 작업은 수정·일괄 stage하지 않는다.
- 경로는 저장소 루트 기준이다. 한글 파일명은 실제 디렉터리 목록으로 찾고 `_util` 모듈 충돌 방지를 위해 스킬별 검사를 별도 프로세스로 실행한다.

## Review Focus

1. 과거의 새 문항 70%·재사용 약 30%가 92문항 전체 통계로 읽히지 않아야 한다. — Task 1 사례 A, Task 3 사례 A 재검토.
2. ‘구아닌’과 ‘교차가 일어나지 않는다고 가정’은 부정형 질문으로 세지 않아야 한다. — Task 1 사례 B.
3. 그림 자산으로 저장된 표와 그림 필수 판독 문제를 구별해야 한다. — Task 1 사례 C.
4. 정본 검증 실패·raw만 존재하는 장은 확정 집계에서 분리하고, 검증 통과도 공식 답·응시 완료로 취급하지 않아야 한다. — Task 1 사례 D, Task 3 사례 D 재검토.
5. 6장 사례가 다른 장의 의무 소재·배합이나 순서 문제의 시작점·계산 대상 생략으로 이어지지 않아야 한다. — Task 2 사례 E.

---

## 설계 기준

- 1절에 장별 정본 경로·문항 수·검증일·출제 관찰 반영 여부·기출 대조 범위를 나타내는 현황표를 둔다. 표의 ‘반영’은 공식 답이나 학습 효과를 뜻하지 않는다.
- 2절은 `### 1~3장 과거 집계` 아래에 기존 표·수치를 보존한다. 별도의 `### 1~6장 최신 형식 집계`에 장별 문항 수·부정형 수·해당 문항 번호와 전체 92/33을 기록한다. 4장 정본 미등록 서술을 현재 상태에 맞추고 5장 관찰은 유지하며 `### 6장 원본 관찰`을 추가한다.
- 부정형 문항 번호: 1장 2·3·4·7·11·12·14·16, 2장 1·5·9·10, 3장 5·6·7·9·10·11, 4장 1·2·7·10, 5장 3·4·6·8·14, 6장 3·6·7·8·12·14. 질문 방향을 직접 읽어 확인한다.
- 6장 관찰은 14문항·70보기·전부 5보기, 부정형 6개, 수치 계산 q13, 제공 그림 q14다. PCR q05/q12/q13의 순서/재료/총량, CRISPR q02/q14의 문장/그림, q09의 제공자별 DNA와 q11의 도구 역할을 기존 유형의 사례로 연결한다.
- 3절의 그림·상황 전이·비교 단위·분류 경계에 질문 방향 전환, 담당 주체/대상의 역할 교환, 계산 대상/초기량/단위/가정, 순서의 시작점 사례를 통합한다. 개념상 적합한 경우만 선택하며 원문을 복사한 새 문제나 모든 장의 PCR 의무 문항을 만들지 않는다.
- 5절과 진입점의 갱신 판단은 ‘현황표 누락, 검증된 문항 수·등록 상태 변경, 새 관찰 미반영’을 확인하도록 맞춘다. 재사용 미집계만으로 매 실행에 같은 미완료 제안을 반복하지 않는다. 기출 대조를 하지 않았으면 미집계로 공개한다. 통상적인 복습팩 실행 중 지침은 자동 수정하지 않고 기존 갱신 제안 경로를 유지한다.
- `forecast-rules.md`는 통계의 관찰 범위·확인일을 공통 파일에서 참조한다. 1~3장의 재사용 약 30%를 다른 장의 예상값으로 사용하지 않는다. 응시 후 자료를 사전 예상 성능으로 표현하지 않는다.

## 파일 구조

| 작업 | 파일 | 책임 |
|---|---|---|
| 신규 | `docs/superpowers/plans/2026-11-10-webquiz-style-refresh.md` | 이 계획과 설계 기준 보존 |
| 수정 | `.agents/skills/bio-review-pack/references/webquiz-style.md` | 현황·집계·6장 관찰·설계 사례·갱신 조건 |
| 수정 | `.agents/skills/bio-review-pack/SKILL.md` | 9단계의 갱신 판단을 공통 규칙과 연결 |
| 수정 | `.agents/skills/bio-webquiz-forecast/references/forecast-rules.md` | 개요 카드에서 통계 범위·상태를 올바르게 사용 |
| 수정 | `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py` | 기존 과거 수치 검사를 과거 집계 절에 한정 |
| 읽기·검사 | `problem-selection.md`, `review-prompt.md`, `test_note_feedback.py`, 예상문제 `tests/test_skill_files.py` | 기존 기록·내용 검토·연결 계약 재사용 |

## Task 1: 근거 현황과 집계 정정

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/webquiz-style.md:5-48`
- Modify: `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py:44-48`
- Read: `웹과제/*/questions.json`, 관련 `intake.md`, 6장 `note-feedback.md`, 증거 보고서.

**Interfaces:**
- Consumes: bank의 `assessment.chapter`, `questions[].number`, `questions[].original`, 원본/검토 근거. 보고서의 집계는 재확인용 후보 값이다.
- Produces: 위 설계 기준의 현황표·`### 1~3장 과거 집계`·`### 1~6장 최신 형식 집계`·6장 관찰. 다음 작업은 이 절들을 참조한다.

- [ ] **Step 1: 변경 전 검사를 기록한다.** `python3 -B -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_webquiz_rules.py -v`를 실행한다. 계획 작성 시 기준선은 17개 통과였다. 실행 때 다른 실패가 있으면 이번 변경과 구분해 기록한다.
- [ ] **Step 2: 현재 정본을 읽기 검증한다.** 실제 디렉터리 목록으로 찾은 각 bank에 `.venv-question-bank/bin/python -B -m scripts.question_bank validate '<실제 bank 경로>' --complete`를 실행한다. 성공은 종료 코드 0과 `Valid: N questions (complete)`다. 기대 문항 수는 17·16·13·15·17·14. 불일치/실패 장은 원본을 수리하지 말고 현황표에 보류 사유를 적고 확정 합계에서 분리한다.
- [ ] **Step 3: 사례 A~D를 대조한다.** A: 46문항의 새 문항 32개(약 70%)는 1~3장 한정이며 4~6장 재사용률은 미집계다. B: 3장 q02·5장 q11은 부정형에서 제외하고 위 번호 집합의 합계 33을 확인한다. C: 4장 q15·5장 q07은 표이며 자산 type만으로 그림 판독률을 계산하지 않는다. D: 검증 실패/raw-only를 확정 집계에 합산하지 않는 절차와, 검증 통과를 공식 답/응시 완료와 구별하는 절차가 각각 명시되어야 한다. 필요한 원본은 직접 열고 기존 보고서와 달라진 판독은 공개한다.
- [ ] **Step 4: 1~2절을 갱신한다.** 설계 기준의 현황표·분리된 집계·4장 상태·6장 관찰을 작성한다. 1~3장 기존 수치와 그림 포함/필수 판독 구별 주석은 보존한다. 미확인 재사용률·전체 그림 필수 판독률은 산출하지 않는다.
- [ ] **Step 5: 기존 수치 검사를 범위에 맞춘다.** `TestWebquizStyle.test_evidence_numbers`를 `test_historical_evidence_numbers`로 이름을 바꾸고 `section(self.text, '### 1~3장 과거 집계')`에서 기존 수치 assertions를 그대로 수행한다. 새 문자열 검사나 분류기는 추가하지 않는다.
- [ ] **Step 6: Step 1 명령을 다시 실행한다.** 기대: 검사 17개·실패 0. 이어 사례 A~D를 수정된 실제 문장에 다시 대조해 최신 합계와 과거 비율의 분모가 분명한지 확인한다.
- [ ] **Step 7: 변경 단위를 검토한다.** 두 파일의 diff와 `git diff --check -- .agents/skills/bio-review-pack/references/webquiz-style.md .agents/skills/bio-review-pack/tests/test_webquiz_rules.py`를 확인한다. 실행 범위에 커밋이 포함된 경우에만 이 두 파일을 명시해 stage하고 `docs: refresh webquiz evidence inventory`로 커밋한다.

## Task 2: 기존 유형에 새 설계 사례 연결

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/webquiz-style.md`의 3절(기준선 59~107행).
- Read: `.agents/skills/bio-review-pack/references/problem-selection.md:84-93`, 6장 q02·q05·q09·q11·q12·q13·q14 및 연결 근거.

**Interfaces:**
- Consumes: Task 1의 6장 관찰과 기존 `variants.md` 10열 형식.
- Produces: 기존 유형 값·표 열을 유지하는 설계 지침. 문장/그림 전환은 `그림`, 원리의 새 조건 적용은 `상황`, 역할·단위 구별만 필요하면 기존 `없음` 등을 의미에 맞게 사용한다. 새 유형 태그를 만들지 않는다.

- [ ] **Step 1: 사례 E의 판정 기준을 고정한다.** PCR 총량 예에서 초기 이중가닥 3분자·5주기·이상적 증폭·전체 분자 수를 명시하면 `3×2⁵=96`으로 판정 가능해야 한다. ‘정확한 길이의 표적 산물’ 질문으로 조용히 바꾸면 실패다. 순서 예는 변성에서 시작함을 밝혀야 한다. CRISPR 문장→그림 전환은 라벨 변경에도 인식/절단의 담당 주체를 구별해야 한다. 이 예들을 다른 장의 의무 소재로 지정하면 실패다.
- [ ] **Step 2: 기존 절에 통합한다.** 그림 절에는 문장↔도식의 동일 판별 기준, 상황 전이 절에는 질문 방향 변경과 단계의 선행 조건, 비교 단위·분류 경계 절에는 역할 교환 및 계산 대상·초기량·단위·가정을 짧게 추가한다. PCR의 순서·재료·계산 세 관찰은 서로 다른 판별 목적의 예시이며 한 원리의 동등한 표현이라고 묶지 않는다.
- [ ] **Step 3: 기록 방법을 확인한다.** 원래 표현→새 표현/불변 판별 기준은 `형태`, 잘못 바꾼 주체·대상은 `오답 보기의 의도`, 가정 적용 과정은 `최소 풀이 단계`로 전달할 수 있는지 사례 E를 표 한 행에 가상 대입해 확인한다. 별도 산출물이나 실제 카드는 만들지 않는다.
- [ ] **Step 4: 내용과 기존 계약을 검증한다.** Task 1 Step 1의 검사를 실행하고 사례 E를 새 문장에 대조한다. 기존 4절의 목표·범위·원문 구분·낯선 참 진술 제한이 유지되어야 한다. 검사 통과와 의미 검토를 별도로 보고한다.
- [ ] **Step 5: 변경 단위를 검토한다.** 해당 파일 diff와 `git diff --check`를 확인한다. 커밋 범위가 승인된 실행이면 파일을 명시해 `docs: extend webquiz variation examples`로 커밋한다.

## Task 3: 소비 지침과 갱신 판단 정합성 확인

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/webquiz-style.md` 5절(기준선 121~123행).
- Modify: `.agents/skills/bio-review-pack/SKILL.md:221`
- Modify: `.agents/skills/bio-webquiz-forecast/references/forecast-rules.md:3-9`
- Test: 기존 review-pack `test_webquiz_rules.py`, `test_note_feedback.py`와 forecast `test_skill_files.py`.

**Interfaces:**
- Consumes: Task 1 현황표의 장·문항 수·검증/관찰 상태와 Task 2의 공통 유형 지침.
- Produces: 복습팩 9단계의 갱신 제안 및 예상문제 개요 카드가 같은 근거 범위·상태를 사용한다. 자동 지침 수정·새 보고서 필드는 추가하지 않는다.

- [ ] **Step 1: 5절의 갱신 판단을 구체화한다.** 설계 기준의 누락·수/등록 상태 변경·새 관찰 미반영을 제안 조건으로 쓴다. 원본·근거가 바뀌면 재검토하며 기존 ‘이 파일은 고치지 않는다’는 통상 생성 실행의 규칙임을 유지한다. 재사용 미집계만으로 동일 제안을 반복하지 않도록 구별한다.
- [ ] **Step 2: 진입점을 연결한다.** `SKILL.md` 221행의 ‘1절에 없는 장’ 판단을 현황표와 5절 참조로 바꾼다. 같은 문단의 카드 번호·풀이기록 보존 지시는 그대로 둔다.
- [ ] **Step 3: 예상문제의 통계 사용을 정정한다.** `forecast-rules.md` 근거 절은 최신 형식 수치와 과거 재사용 수치의 관찰 범위·확인일을 구별하도록 작성한다. 근거 없는 해당 장 비율은 미집계로 쓰고 공통 유형은 설계 참고로 활용한다. 기존 응시 전후 구분과 원문 등록 규칙을 유지한다.
- [ ] **Step 4: 사례 A·D와 갱신 시나리오를 검토한다.** 4~6장 개요에서 ‘재사용 약 30%’를 해당 장 통계로 쓰면 실패다. 검증 실패 장의 문항 수를 최신 확정 합계에 넣거나 공식 답 확인으로 쓰면 실패다. 현황표에 반영된 4~6장은 미등록으로 재보고하지 않고, 새 장이 생기거나 bank 수가 달라지면 재검증·갱신 제안으로 이어져야 한다. 이는 절차의 문장 검토이며 자동 동작을 구현·시험한 결과가 아니다.
- [ ] **Step 5: 기존 검사를 별도 프로세스로 실행한다.** 아래 각각 수집 수 1 이상·실패 0·종료 코드 0이 합격이다. forecast 파일의 함수형 테스트까지 포함하기 위해 pytest를 사용한다. 기존 실패나 환경 문제는 원인·이번 변경과의 관련성을 기록하고 무관한 코드를 수정하지 않는다.

```bash
python3 -B -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_webquiz_rules.py -v
python3 -B -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_note_feedback.py -v
uv run --no-project --with pytest python -B -m pytest .agents/skills/bio-webquiz-forecast/tests/test_skill_files.py -q
```

- [ ] **Step 6: 최종 diff를 확인한다.** 허용된 구현 4파일의 diff·공백 오류·링크 대상 존재 여부를 확인한다. `problem-selection.md`와 `review-prompt.md`의 기존 전달·검토 규칙으로 새 사례를 검토할 수 있는지도 읽는다. 다른 작업의 신규 파일이나 수정은 이 작업의 결과에 포함하지 않는다.
- [ ] **Step 7: 결과를 인계한다.** 실제 변경 파일, 검증된 합계·보류 상태, 검사 결과, 사례 A~E의 판정과 한계를 보고한다. 커밋이 실행 범위에 포함되면 이 Task의 3파일만 명시해 `docs: align webquiz evidence consumers`로 커밋한다. 푸시는 이번 계획의 범위가 아니다.

## 계획 자체 검토

- 설계의 현황 정정·6장 관찰·과거 통계 보존은 Task 1, 설계 사례 보강은 Task 2, 소비 지침·갱신 조건 연결은 Task 3으로 연결했다.
- 별도 함수·형식·유형 없이 문서 절과 기존 표 열만 인터페이스로 사용한다. 파일 책임과 Task별 수정 범위가 일치한다.
- 다섯 Review Focus는 사례 A~E에 대응하며 각 소유 Task에 검사 단계와 판정 기준을 적었다. 문구 검사만으로 교육 효과나 자동 분류 정확도를 주장하지 않는다.
- 새 테스트·범용 도구를 늘리지 않고 기존 숫자 검사 범위만 정정한다. 변경 전/후의 기존 검사와 명시적 사례 대조를 수행한다.
- 이번 턴은 계획 저장으로 끝난다. 계획 검토와 실행 방식 선택 후에만 구현을 시작한다.
