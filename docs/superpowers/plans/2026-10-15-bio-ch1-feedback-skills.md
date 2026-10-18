# 1장 웹과제 피드백 기반 생성 규칙 보완 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 설명과 생성 구조를 유지하면서 해설의 유보 보존, 표현 전환 설계 기록, 실제 관찰과 생성 정책의 구분을 명확히 한다.

**Architecture:** 기존 Markdown 참조 문서 5개를 보완한다. 복습팩의 변형 설계 규칙을 공통 근거로 사용하고 예상문제 문서는 이를 참조한다. 해설 스킬의 기존 지문 검사를 유지하기 위해 변경한 두 문서의 목적지 SHA256만 이식 기록에 동기화한다.

**Tech Stack:** Markdown, Python 3 표준 라이브러리, 기존 unittest/pytest 검사. 새 런타임 의존성·스키마·검사기는 추가하지 않는다.

**Spec:** 이 계획의 「설계 기준」은 같은 대화의 grill-yourself 설계를 구현에 필요한 범위로 보존한다. 증거 문서는 `웹과제/1장/feedback/20261015-191852-d960f195/report.md` 6절 제안 A·B·D다. 실행자는 두 문서를 모두 읽는다. 앞선 선택 #1은 사용자가 별도 값을 지정하지 않고 계획 작성을 요청했으므로 권고값인 ‘스킬 참조 문서 5개만 수정’으로 기본 확정했다. 이식 기록 1개는 기존 검증을 유지하기 위한 보조 변경이다.

## Global Constraints

- 기존 개념 설명은 유지한다. 기존 학습 자료·정본 bank·정답키·raw·피드백 보고서를 수정하지 않는다.
- 기존 팩 재생성·새 예상 세트 제작·1장 `note-feedback.md` 작성은 제외한다.
- 새 JSON 필드·자동 의미 판정기는 추가하지 않는다.
- 기존 통계와 목표 수는 유지한다. 다른 장에 1장 소재나 유형 개수를 의무화하지 않는다.
- 공식 정답은 미확인이다. 선택 표시는 공식 정답·개인 취약점·학습 효과로 취급하지 않는다.
- 기존 충돌·발행 보류·독립 검산 규칙은 유지한다. 공식 답이 없다는 이유만으로 알려진 답과 불일치한다고 판정하지 않는다.
- 출처의 고정 커밋·원천 해시·고정 자산은 변경하지 않는다. 이식 기록에서는 수정한 두 문서의 `destination_sha256`만 갱신한다.
- 문서 보완에 불필요한 문자열 테스트는 추가하지 않는다. 기존 계약 검사와 아래 사례별 의미 검토를 구별해 수행한다.
- 경로는 저장소 루트 기준이다. 한글 경로는 실제 파일 목록을 사용한다. 동명 테스트 모듈 충돌을 피하도록 각 스킬 검사는 별도 프로세스로 실행한다.
- 시작 시 존재한 5장 계획·설계 문서와 1장 feedback 폴더는 다른 작업이다. 통째로 stage하거나 변경하지 않는다.
- 이번 요청은 계획 작성이다. 실행 방식 선택 전에는 구현·커밋·푸시하지 않는다. 실행 시 작업 격리는 using-git-worktrees로 확인하고, 커밋은 사용자가 요청한 경우에만 작업 단위별로 수행한다.

## Review Focus

1. 본문에만 남은 모호성: 검산·요약도 같은 유보와 공식 답 미확인을 유지해야 한다 — Task 1 사례 A.
2. 정상 문항까지 모호하게 만드는 과잉 적용: 표현 결함이 없는 문항은 명확한 결론을 유지해야 한다 — Task 1 사례 B.
3. 명칭만 바꾸거나 원문을 반복한 경우: 새 표현과 불변 판별 기준을 설명할 수 있어야 하며 원문 반복을 새 연습으로 세면 안 된다 — Task 2 사례 C·D.
4. 장식·보조 그림 및 합답형 표지: 그림 포함 수와 필수 판독 수, 실제 4진술과 생성 3진술을 구별해야 한다 — Task 3 사례 E.
5. 원천 해시를 덮어 검사를 맞추는 경우: 목적지 문서 해시만 바뀌고 원천 정보와 다른 항목은 같아야 한다 — Task 1 지문 검토.

---

## 설계 기준

- 해설: 보기 판정의 조건·유보를 `verify`와 `sum`에도 유지한다. 출제 의도상 분석 답과 엄밀한 유일 정답을 구별한다. 공식 답 미확인을 정답 확인으로 표현하지 않는다. 정상 문항에 불필요한 유보를 붙이지 않는다.
- 표현 전환: 기존 `variants.md`의 `형태` 칸에 ‘원래 표현 → 새 표현 / 불변 판별 기준’을 기록한다. 원문 재수록만으로 새 표현 연습을 완료했다고 세지 않는다. 기존 출처 기록도 같은 칸에 유지한다.
- 예상문제: 공통 `problem-selection.md` 6절을 참조한다. 기존 blueprint의 `겨냥 혼동`에 표현 변화·판별 기준을, `최소 풀이 단계`에 적용 과정을 기록한다. 새 열·필드는 추가하지 않는다. v1의 새 문제에도 적용하며 v2 이후 기존 차별화 규칙을 약화하지 않는다.
- 관찰: 1장 그림 포함 2(q09·q14), 필수 구조 판독 1(q09). q14는 그림으로 반례 확인도 가능하다. 실제 q06은 a~d 4진술, 문서의 ㄱㄴㄷ 3진술은 생성 형식이다.
- 교육적 예: 다른 배치·곁사슬의 아미노산 구조에서도 중앙 탄소에 연결된 아미노기·카복실기·H·R을 확인하여 아미노산 → 단백질로 연결한다. 새 아미노산 이름 암기를 요구하지 않는다. 이 예는 모든 장의 고정 문항이 아니다.

## 파일 구조와 책임

| 수정 파일 | 책임 |
|---|---|
| `.agents/skills/bio-problem-explain/references/authoring.md` | 결함 공개 조건·유보를 검산과 요약까지 보존 |
| `.agents/skills/bio-problem-explain/references/verification.md` | 기존 content 검토에서 유보·답의 지위 일치 확인 |
| `.agents/skills/bio-problem-explain/assets/port-provenance.json` | 위 두 문서의 목적지 지문 동기화만 수행 |
| `.agents/skills/bio-review-pack/references/problem-selection.md` | 표현 전환의 공통 설계 기록 규칙 |
| `.agents/skills/bio-webquiz-forecast/references/question-blueprint.md` | 기존 blueprint 칸으로 공통 규칙을 사용 |
| `.agents/skills/bio-review-pack/references/webquiz-style.md` | 1장 관찰 정의와 생성 형식 구별 |

검사 파일은 수정하지 않는다. 의미 검토 사례는 실행 보고에 결과·근거를 남기며, 기존 학습 자료에 시험용 내용을 쓰지 않는다.

## Task 1: 해설의 조건·유보 보존

**Files:** 위 파일표의 `authoring.md`, `verification.md`, `port-provenance.json`.
**Test:** `.agents/skills/bio-problem-explain/tests/test_skill_files.py`.

**Interfaces:**
- Consumes: `authoring.md` 원자료 충돌 (A)/(B)/(C), `verification.md` content·independent 정의, 보고서 제안 A.
- Produces: 기존 `verify`·`sum`에 적용되는 의미 일치 요구. HTML 계약·review.json·발행 상태 인터페이스는 동일하다.

- [ ] **Step 1: 변경 전 사례 A·B를 판정한다.** A는 `복습노트/0908/.assets/문제설명_0908_Biomolecules_and_Cells.md` P2의 본문 L188과 소거 L204·요약 L229를 읽는다. 본문은 B를 유보하지만 요약은 C만 틀리다고 하므로 불일치다. B는 같은 파일 P1을 읽고 표현 결함이 실제로 없는지 확인한다. 없다면 단일 답 결론을 유지하는 대조 사례로 쓴다. 결함이 발견되면 보고서에서 ‘유지’로 분류한 다른 정상 문항을 선택하고 출처를 기록한다.
- [ ] **Step 2: 저작 규칙을 보완한다.** `authoring.md` L69~76의 결함 공개 (B)에 「설계 기준」의 유보 보존 요구와 정상 문항 적용 제외를 통합한다. 공식 답 부재를 답 불일치로 치환하거나 기존 (A)/(C) 기준을 변경하지 않는다.
- [ ] **Step 3: 내용 검토를 보완한다.** `verification.md` L8의 기존 요약-본문 일치 검토에 ‘보기의 조건·유보, 출제 의도상 분석 답/엄밀한 유일 답, 공식 답 확인 여부’를 함께 읽도록 적는다. 별도 검토 상태는 만들지 않는다.
- [ ] **Step 4: 이식 기록의 목적지 지문을 동기화한다.** JSON에서 `destination`이 `references/authoring.md`, `references/verification.md`인 두 항목의 `destination_sha256`을 각 파일 바이트의 `hashlib.sha256(...).hexdigest()`로 교체한다. 변경 전 JSON과 비교해 다른 값은 모두 동일해야 한다. 전체 `port_provenance.py` 재생성은 실행하지 않는다.
- [ ] **Step 5: 기존 계약 검사를 실행한다.** 저장소 루트에서 `uv run --no-project --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_skill_files.py -q`. 기대: 수집된 테스트가 1개 이상이고 실패 0, 종료 코드 0. 현재 기본 Python과 `.venv-question-bank`에는 pytest가 없고 `uv`는 확인되어 있다. 의존성 설치 문제가 나면 원인을 보고하며 저장소 환경 파일은 바꾸지 않는다.
- [ ] **Step 6: 의미 검토를 수행한다.** 사례 A의 목표 검산·요약은 ‘분석 답 C / B의 독립 표현 엄밀성 주의 / 공식 답 미확인’을 모두 보존해야 한다. 사례 B는 불필요한 모호성 문구를 요구받지 않아야 한다. 새 규칙으로 두 사례의 판정이 가능한지 확인한다. 실제 파일을 고쳤거나 독립 재풀이를 마쳤다고 보고하지 않는다.
- [ ] **Step 7: diff를 검토한다.** 수정 3파일만 확인하고 `git diff --check`를 실행한다. 커밋 요청이 있을 때만 이 3파일을 명시해 stage하고 staged diff 확인 후 `docs: preserve ambiguity through explanation summaries`로 커밋한다.

## Task 2: 복습팩·예상문제 표현 전환 기록 연결

**Files:** `problem-selection.md` L84~90, `question-blueprint.md` L3~12 및 L27~30.
**Test:** `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`, `.agents/skills/bio-webquiz-forecast/tests/test_skill_files.py`.

**Interfaces:**
- Consumes: 기존 `variants.md` 10열 표와 blueprint 9열 표, 원문/생성 문제 구분.
- Produces: `형태` 및 `겨냥 혼동`의 ‘원래 표현 → 새 표현 / 불변 판별 기준’, 기존 `최소 풀이 단계`. 열 이름·개수와 JSON 구조는 동일하다.

- [ ] **Step 1: 사례 C·D의 합격 기준을 기록한다.** C는 새 배치·곁사슬의 아미노산 그림에서 네 연결기를 식별 → 아미노산 → 단백질로 이어지며, 새 이름 암기가 없어야 한다. D는 기존 원문을 그대로 반복한 경우로 새 표현 연습으로 인정하면 실패다. 다른 이름을 사용한 경우도 달라진 이름과 동일 대상임을 판단하는 기준이 기록되어야 한다.
- [ ] **Step 2: 공통 규칙을 보완한다.** `problem-selection.md` 6절의 기존 형태·표 기록 안내에 「설계 기준」을 통합한다. `형태` 칸의 쌍둥이 원문 출처·낯선 참 진술 교재 출처를 대체하지 않으며, 기록은 표현 전환을 선택한 행에 적용한다. 모든 행에 억지로 표현 전환을 요구하지 않는다.
- [ ] **Step 3: 예상문제에서 공통 규칙을 참조한다.** `question-blueprint.md`의 일반 blueprint 안내에 `../../bio-review-pack/references/problem-selection.md` 6절 링크를 추가한다. `겨냥 혼동`·`최소 풀이 단계`에 넣을 정보를 지정한다. v2 전용 절에만 넣지 않으며 기존 ‘둘 이상 변경’·발문 중복 금지는 유지한다.
- [ ] **Step 4: 기존 검사를 별도 프로세스로 실행한다.** 각각 `uv run --no-project --with pytest python -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q` 및 `uv run --no-project --with pytest python -m pytest .agents/skills/bio-webquiz-forecast/tests/test_skill_files.py -q`. 각각 수집 수 1 이상·실패 0·종료 코드 0이 합격이다. 공통 링크 대상 파일이 실제로 존재하는지도 확인한다.
- [ ] **Step 5: 사례 C·D를 새 규칙에 대조한다.** 기존 표 칸만으로 변경 표현·불변 기준·풀이 과정을 기록할 수 있어야 한다. C는 통과, D는 새 표현 연습으로 불인정한다. 정답·해설을 읽은 이 검토를 블라인드 재풀이나 사용자 학습 효과 검증으로 부르지 않는다.
- [ ] **Step 6: diff를 검토한다.** 표 열·기존 유형 배합·범위·난이도 정책이 유지되는지 읽고 `git diff --check`를 실행한다. 커밋 요청 시에만 두 파일을 명시해 stage하고 `docs: record invariant criteria in representation variants`로 커밋한다.

## Task 3: 1장 관찰 정의 정리와 전체 범위 확인

**Files:** `webquiz-style.md` L9~23 및 L65~70.
**Test:** `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`.

**Interfaces:**
- Consumes: 보고서 3절과 6절 제안 D, bank q06·q09·q14, 기존 유형 정의·역사적 집계.
- Produces: 그림 포함/필수 판독 구별 주석과 실제/생성 합답형 구별 문구. 유형 값·집계표·생성 목표는 동일하다.

- [ ] **Step 1: 사례 E의 근거를 확인한다.** 보고서에서 q06·q09·q14의 연결 raw ID를 읽고 `questions.json`의 해당 항목과 대조한다. q06은 a~d 4진술, q09·q14는 그림 포함, 필수 판독은 q09라는 보고서의 의미 분류가 맞는지 관련 원본도 확인한다. 불일치하면 통계를 임의 수정하지 말고 증거 차이를 보고한다.
- [ ] **Step 2: 관찰 주석을 추가한다.** 1~3장 집계표 아래에 그림 포함 2(q09·q14)/필수 구조 판독 1(q09), q14 반례 확인 가능을 적는다. 합답형 절은 실제 q06의 4진술과 아래 생성 형식의 3진술을 구별한다. 기존 17문항 분모·역사적 수치·생성 목표·기출 재사용률은 유지한다.
- [ ] **Step 3: 기존 규칙 검사를 실행한다.** `uv run --no-project --with pytest python -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q`. 기대: 수집 수 1 이상·실패 0·종료 코드 0. 실패 때문에 기존 수치나 테스트를 새 주장에 맞춰 바꾸지 않는다.
- [ ] **Step 4: 사례 E를 의미 검토한다.** 새 문구를 읽으면 ‘그림 포함 2 → 그림 판독 문제도 2’ 또는 ‘실제 q06도 ㄱㄴㄷ 3진술’로 해석되지 않아야 한다. 다른 장의 고정 그림 수나 4진술 의무로 확장되지 않는지도 확인한다.
- [ ] **Step 5: 전체 변경 범위를 확인한다.** `git diff --check`, `git diff --stat`, `git status --short`와 파일별 diff를 읽는다. 허용된 5개 문서와 보조 이식 기록만 수정되어야 하며, 현재 계획 파일 외의 새 산출물이 없어야 한다. 지문 검사는 Task 1의 최종 문서 바이트와 일치해야 한다. 이후 해설 문서를 다시 고쳤다면 지문 동기화·Task 1 검사를 다시 수행한다.
- [ ] **Step 6: 결과를 인계한다.** 사례 A~E의 판정·읽은 위치, 실행한 검사 결과와 한계를 보고한다. 기존 0908 해설은 이번에 고치지 않았음을 명시한다. 커밋 요청 시에만 이 문서를 명시해 stage하고 `docs: distinguish chapter one observations from generation policy`로 커밋한다. 푸시는 별도 요청 없이는 실행하지 않는다.

## 계획 자체 검토

- 설계 A/B/D는 각각 Task 1/2/3으로 연결했다. 후속 C와 기존 해설 갱신은 범위 밖이다.
- 기존 문서 5개와 지문 기록 1개만 수정하도록 제한했다. 실제 검증 때문에 필요한 지문 갱신을 명시했고 원천 정보는 보존한다.
- 런타임 함수·스키마 변경이 없어 새 시그니처가 없다. 두 설계표의 기존 칸을 사용한다.
- Review Focus 5개를 모두 사례 A~E 또는 지문 비교에 연결했다. 의미 검토를 자동 검사로 과장하지 않는다.
- 문서 변경이므로 새 구현 모사 테스트와 강제 RED 단계는 두지 않는다. 기존 계약 검사를 실행하되 현재 계획 작성 중에는 테스트를 실행하지 않았다.
- 실행 방식은 미선택이다. 범위가 작은 문서 변경이므로 Native를 권고한다. 실행은 사용자 검토·방식 선택 후 시작한다.
