# 2장 웹과제 자료 보완 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 2장 q14 해설 오류·유보 누락과 q16 노트 조건 누락을 고치고, 전체 16문항을 기존 본문 피드백 경로에 연결한다.

**Architecture:** 기존 review-pack full 조립과 problem-explain 추출·조립·검토·발행을 사용한다. 새 문제·스키마·검사기·스킬 규칙은 만들지 않는다. 현재 발행 자료를 보존 입력으로 복원해 최소 내용 변경만 수행하고, 현재 산출물에 결합된 실제 검토 결과로 발행한다.

**Tech Stack:** Python 3.10+, 기존 표준 라이브러리 CLI, HTML/Markdown/JSON, 원자료 PDF·STT, 실제 브라우저 검토.

**Spec:** 이 문서의 ‘확정 설계’는 직전 grill-yourself 설계의 동봉 사본이다. 근거 보고서는 `웹과제/2장/feedback/20261015-194506-a9518cad/report.md` §4·6·7과 같은 폴더 `sources.json`이다. 실행자는 이 계획과 보고서 모두 읽는다. 경로는 저장소 루트 기준이며 실제 Unicode 이름은 pathlib로 확인한다.

## Global Constraints

- 범위: **자료 수정＋16문항 피드백 연결, 스킬 변경 제외**. 이전 설계 #7은 후속 계획 요청에서 변경이 없어 기본값으로 확정한다.
- 공식 정답 미확인. 선택 표시는 제출 전 관찰이며 개인 오개념·최종 오답으로 확정하지 않는다.
- 원문 C와 분석 답 D, questions.json/raw/intake를 보존한다. 공식 답을 만들어 넣지 않는다.
- 카드 번호·지문·보기·정답 모델·풀이기록·기존 인터랙티브 링크를 보존한다. 새 문제·새 토픽·임의 동의어를 추가하지 않는다.
- 노트 본문 반영은 full 조립으로 수행한다. augment로 본문 수정 완료를 주장하지 않는다.
- 의미가 바뀐 자료의 이전 리뷰를 재사용하거나 새 해시에 과거 pass만 옮기지 않는다.
- 기존 충분한 본문은 유지한다. 예정·보류를 반영 완료로 세지 않는다.
- Git commit/push는 별도 요청 전 수행하지 않는다. 다른 작업의 untracked 파일과 1장 자료를 건드리지 않는다.
- 코드 변경이 없는 자료 보완이다. 구현을 따라 쓰는 새 자동 테스트를 만들지 않고 기존 검사·원천 대조·내용 검토·보존 비교를 수행한다.

## Review Focus

1. q14: 본문만 고치고 요약·검산에서 D를 공식 유일 답으로 단정하는 회귀 — Task 3에서 다섯 구역을 각각 판정한다.
2. q16: 전자전달 유지 조건이 사라지거나 H⁺ 누출과 같은 결과로 설명되는 회귀 — Task 2에서 원문·차단·누출을 대조한다.
3. full 복원: 카드·위젯 스크립트·그림·기존 링크·풀이기록이 사라지는 회귀 — Task 2의 수정 전 무변경 조립 비교와 Task 3의 최종 비교로 막는다.
4. q09/q10 무선택, q07/q14 모호함을 개인 약점으로 기록하는 오류 — Task 1에서 근거 유형과 미확인 가설을 분리한다.
5. 여러 회차 연결: ID를 누락·중복하거나 옛 장 마감 기록을 현재 사실로 덮는 오류 — Task 1·2에서 전체 ID 집합 및 날짜가 있는 추가 기록을 확인한다.

---

## 확정 설계

- q14/p33: “해당과정에서는 포도당에서 유래한 전자를 NAD⁺가 받아 NADH가 돼요.”로 전자 방향을 바로잡는다.
- q14 안내: “화학적으로 정확한 분석 답은 D예요. C는 전자를 받는 피루브산과 생성물인 젖산을 바꿔 표현했어요. 다만 출제자가 이를 줄여 표현했을 가능성은 있으며, 공식 정답은 확인되지 않았어요.”의 의미를 understand·solve·verify·pitfall·sum에 일관되게 유지한다. 다섯 구역에 긴 문장을 반복 복사할 필요는 없다.
- q16 노트: “전자전달에 의한 H⁺ 수송이 계속되는 조건에서 ATP 합성효소를 통한 귀환을 막으면, 막 사이 공간에 H⁺가 더 쌓여 pH 차이가 커져요.”로 조건을 명시한다. 실제 장기 정상상태까지 일반화하지 않는다.
- 나머지 14개는 실제 본문 판별 문장을 확인해 기존 설명 충분/이전 노트 연결로 기록한다. q14는 본문 개념 충분과 해설 수정 완료를 구별한다.
- 불확실한 재풀이 결과가 분석 답과 충돌하면 해당 해설 발행을 보류하고 이유를 남긴다. 공식 답 부재 자체는 답 불일치가 아니다.

## 파일 구성과 실행 약속

기존 파일:
- `복습노트/0910/.pack/manifest.json`, `복습노트/0915/.pack/manifest.json`: 섹션·토픽·카드 순서의 보존 기준.
- `복습노트/0910/정리노트_0910_Cells_and_Cellular_Respiration.html`와 `.assets/`의 동명 MD: q16 조건 보완.
- `복습노트/0915/정리노트_0915_Cellular_Respiration_and_Photosynthesis.html`와 동명 MD: 내용 유지, 감사 입력을 포함한 full 재조립.
- 두 회차의 복습문제 HTML·MD: full 출력이지만 카드 의미 변경 금지.
- `복습노트/0915/.assets/자료_문제설명_0915_Cellular_Respiration_and_Photosynthesis/fragments/p33.html`: q14 수정 원천. 직접 발행본을 먼저 덮지 않고 새 RUN의 explanations/p33.html에서 수정해 publish로 교체.
- 두 회차의 문제설명 HTML·MD 및 `.assets/자료_문제설명_<range>_<slug>/`: 최종 노트를 참조하는 새 검토·발행 결과.
- `복습노트/0915/.assets/장마감_0915_2장.md`: 기존 §3의 역사적 상태를 유지하고 현재 감사 결과를 추가.

새 파일:
- `웹과제/2장/note-feedback.md`: 전체 16개 입력 기준·근거·불확실성.
- 각 회차 `.pack/note-feedback-audit.md`: 회차별 실제 본문 반영·연결 결과.

실행 기록은 고유 scratch 루트 `WORK`에 둔다. 그 아래 `baseline/`, `pack/0910`, `pack/0915`, `explain/0910`, `explain/0915`, `evidence/`를 사용한다. 각 CLI 호출의 REPO/PACK/EXPLAIN/WORK는 실제 절대 경로로 명시한다. 조립 RUN 계약은 `assemble.py:1–12`, 해설 계약은 `mpe_cli.py:extract/load_fragments`와 각 SKILL.md다. 아래 셸 변수는 실행 호출마다 다시 정의하며 빈 경로로 실행하지 않는다.

### Task 1: 전체 16문항의 피드백 입력 확정

**Files:** Create `웹과제/2장/note-feedback.md`; Test `WORK/evidence/input-audit.md`.

**Interfaces:** Consumes 보고서 §4·6, questions.json의 원본 ID·issues·관찰 단계, 해당 강의노트·교재·STT. Produces 전체 ID `web-20261001-ch02:q01`–`q16` 각각 한 행과 source/판별 기준/근거 위치/불확실성. Task 2가 읽는 단일 입력이다.

- [x] Step 1: 실행 시 Git 상태와 AGENTS.md를 확인하고 원자료·대상 파일 해시 및 두 날짜 폴더를 WORK/baseline에 백업한다. 현재 보고서 해시와 달라진 자료는 재확인한다. 관련 스킬은 실행 지침으로 읽되 수정하지 않는다.
- [x] Step 2: 실제 bank 절대 경로로 `.venv-question-bank/bin/python -B -m scripts.question_bank validate <bank> --complete`를 실행한다. Expected: exit 0, `Valid: 16 questions (complete)`; 다르면 입력 작업을 멈춘다.
- [x] Step 3: 보고서의 16개 판별 기준을 재확인해 note-feedback.md에 기록한다. 공통 ID 접두사와 q01–q16을 명시하고 출제 관찰/개인 미확인 가설을 분리한다. q07의 오타 해석, q14 C의 표현 문제, q09/q10 무선택을 개인 취약점으로 전환하지 않는다.
- [x] Step 4: Python으로 입력 표의 ID를 추출해 bank ID 집합과 동일하고 각각 한 행인지 검사한다. `expected == actual`, `len(rows) == len(set(rows)) == 16`이어야 한다. 이어 실제 근거 문장·위치를 읽어 16개 전부 확인하고 WORK/evidence/input-audit.md에 결과를 남긴다. 단어 존재만으로 의미 검증 pass를 쓰지 않는다.

### Task 2: 노트 조건 보완과 full 조립·감사 연결

**Files:** Modify 두 회차 노트 HTML·MD, full 출력 복습문제 HTML·MD와 `.pack/log.md`; Create 두 `.pack/note-feedback-audit.md`; Modify `복습노트/0915/.assets/장마감_0915_2장.md`; Test WORK/evidence/pack-preservation.md 및 note-feedback-review.md.

**Interfaces:** Consumes Task 1 note-feedback.md와 baseline. Produces 최종 두 노트, 보존된 복습문제, 전체 16개를 정확히 한 소유 회차에 배정한 감사표. Task 3는 이 최종 파일만 참조한다.

- [x] Step 1: 두 manifest를 각각 WORK/pack/<range>/manifest.json에 복사한다. baseline HTML의 manifest 섹션에서 직접 h2를 제외한 안쪽 HTML을 sections/<id>.html로, 카드 article 전체를 cards/<pN>.html로 복원한다. figure·variants·기존 감사 기록을 복사하고 분리된 토픽 위젯 스크립트도 섹션에 복원한다. 재작성·새 카드 선별은 하지 않는다. 복원 보조 코드는 WORK 안에만 둔다.
- [x] Step 2: 수정 전 각 RUN으로 임시 출력 디렉터리에 full assemble을 실행한다. 토픽/카드 ID 순서, 카드 지문·보기·해설·채점 모델, 위젯 실행 코드와 링크·그림 대상이 baseline과 동등한지 비교한다. 템플릿 공백·표현 차이는 개별 확인하고 내용 누락·실행 코드 손실은 0이어야 한다. 복원 실패를 임의 내용 재생성으로 덮지 않는다.
- [x] Step 3: 0910 `#s5-atp-synthase`의 차단 결과 문장을 확정 설계대로 수정한다. 0915의 정상 흐름/전자전달 차단/H⁺ 누출 설명과 대조해 조건·방향이 일관적인지 WORK/evidence/note-feedback-review.md에 기록한다.
- [x] Step 4: 8열 감사표를 각 RUN/note-feedback-audit.md에 작성한다. 0910 소유 q02,04,05,08,09,12,15,16; 0915 소유 q01,03,06,07,10,11,13,14. 다른 회차 근거는 링크로 연결한다. 실제 토픽 id와 판별 문장을 적고 기존 설명 충분/이전 노트 연결/본문 반영/보류를 구별한다. q14 해설은 Task 3 완료 전 미완료다.
- [x] Step 5: `python3 "$PACK/scripts/assemble.py" --run "$WORK/pack/<range>" --out "$REPO/복습노트/<range>"`를 두 회차 각각 실행한다. 이어 `python3 "$PACK/scripts/check_html.py" --manifest <RUN/manifest.json> --note <note.html> --review <review.html>` 및 `python3 "$PACK/scripts/html2md.py" <note.html> <review.html> --check`를 실행한다. Expected: 모두 exit 0, FAIL 없음. 실패는 해당 RUN 원천에서 해결한다.
- [x] Step 6: 실제 내용·본문 피드백 검토와 review-pack 필수 브라우저 검증을 수행한다. 변경 전후 모든 카드·그림·링크·풀이기록을 비교하고, 브라우저에서 기존 기록 복원·JSON 내보내기·위젯 동작을 확인한다. 브라우저 검증에는 baseline 사본의 테스트용 기록을 사용하고 사용자 기록을 덮지 않는다.
- [x] Step 7: 최종 감사표를 RUN에 저장하고 마지막 full 조립·기계 검사·MD 변환을 반복해 `.pack`에 동일한 표가 복사됐는지 확인한다. 장 마감 §3에는 기존 기록의 시점을 보존한다는 설명과 2026-10-15 현재 감사 위치를 추가한다. ‘웹과제 없음’을 현재 결론으로 사용하지 않는다. 두 감사표의 소유 ID 합집합=16, 교집합=0을 확인한다.

### Task 3: q14 해설 수정·두 팩 참조 갱신·최종 검증

**Files:** Modify 두 회차의 문제설명 HTML·MD 및 소유 자료 폴더; q14 수정 대상은 0915 fragments/p33.html; Test 각 새 RUN의 review.json/evidence와 WORK/evidence/final-scope.md.

**Interfaces:** Consumes Task 2 최종 노트·보존 복습문제와 기존 설명 조각. Produces 현재 입력·참조 해시에 묶여 네 실제 검토를 통과한 발행분. 카드 원본 변경은 허용하지 않는다.

- [x] Step 1: 각 회차의 빈 새 RUN에 `python3 "$EXPLAIN/scripts/mpe_cli.py" extract --repo "$REPO" --target <review.html 절대 경로> --run "$WORK/explain/<range>"`를 실행한다. run.json targets의 각 bucket/explanations/에 발행된 fragments 전체를 복사하고 문항 ID 집합이 정확히 일치하는지 확인한다. source.json은 수동 수정하지 않는다. 노트 참조가 바뀌므로 0910도 검토 갱신 대상으로 포함한다.
- [x] Step 2: 0915 explanations/p33.html만 확정 설계대로 수정한다. 전자 방향을 바로잡고 understand·solve·verify·pitfall·sum 각각에서 분석 답/공식 미확인/C 표현 유보가 충돌하지 않게 한다. q07 등 다른 해설은 복사 보존하며 새 저작을 하지 않는다.
- [x] Step 3: 각 RUN에 `python3 "$EXPLAIN/scripts/mpe_cli.py" build --run <RUN>`와 `check --run <RUN>`를 실행한다. Expected: exit 0. build가 생성한 review.json의 not_run을 자동 승인으로 바꾸지 않는다.
- [x] Step 4: `references/verification.md`대로 source_visual·content·independent·browser를 실제 수행한다. 전체 items를 검토하고 independent는 정답·풀이·설명 조각을 받지 않은 별도 검산자가 담당한다. 그에게 문항·그림·최종 노트·원자료만 제공한다. 의미 판단을 required_terms 존재 검사로 대체하지 않는다. 검산 충돌은 disputed로 남기고 해당 팩 발행을 보류한다.
- [x] Step 5: 데스크톱 1280×900 및 모바일 375×812, light/dark에서 필수 UI 검증을 수행한다. 특히 p33 본문·요약 양쪽 안내와 원문 C 보존을 실제 화면에서 읽고, 콘솔 오류·누락 자원·문서 가로 넘침=0을 확인한다. 모든 review 항목 pass, 실제 reviewer/evidence, 현재 reference/input/artifact 해시를 확인한다.
- [x] Step 6: 모두 통과한 팩만 `python3 "$EXPLAIN/scripts/mpe_cli.py" publish --run <RUN>`로 발행한다. 실패하면 소유 파일을 백업에서 복구하고 미완료를 명시한다. q14 완료 상태는 실제 발행 후 기록한다.
- [x] Step 7: bank --complete 검증을 다시 실행한다. baseline과 bank/raw/intake·풀이기록 해시는 동일해야 한다. 카드 ID·정답 모델·지문·보기, 비대상 토픽의 내용 보존을 재확인한다. `git diff --check`, `git diff --stat`, `git status --short`로 허용 범위만 바뀌었는지 검사하고 결과를 WORK/evidence/final-scope.md에 기록한다. 스킬·1장·예상문제·커닝페이퍼 변경은 0이어야 한다.
- [x] Step 8: 두 수정 결과, 16개 연결 상태, 필수 검토 결과, 보류 항목과 파일 링크를 사용자에게 보고한다. commit/push는 요청하지 않았다면 수행하지 않는다. 이후 요청받으면 검토된 허용 파일만 stage하고 staged diff/check 후 커밋한다.

## 자체 검토

- 설계 요구: q14 Task 3, q16 Task 2, 전체 연결 Task 1–2, 보존·최종 검증 Task 2–3로 모두 배정했다.
- 단계와 인터페이스: note-feedback → 최종 노트 → 최종 노트 참조 해설 순서다. Task 3 이전 추출 결과를 재사용하지 않는다.
- 다섯 Review Focus는 각 소유 Task의 실제 확인 단계에 배정했다.
- 신규 프로덕션 코드·테스트 프레임워크·고정 문제 비율·일반 규칙을 추가하지 않는다.
- 현재 원천 임시 RUN이 없어 복원과 무변경 비교가 필요하다는 비용을 반영했다. 실제 보존 비교가 실패하면 완료를 주장하지 않는다.

## 실행 인계

권장 방식은 Native: 연결된 자료 보완 세 작업을 같은 실행자가 이어서 수행하고 마지막에 별도 검토자가 전체 변경을 검토한다. 해설의 정답 비공개 독립 검산은 Native에서도 별도 검산자로 수행하며 생략하지 않는다. 사용자가 계획 검토와 실행 방식을 선택하기 전에는 구현을 시작하지 않는다.


## 2026-10-15 승인된 추가 범위

사용자: “추가 오류까지 수정하고 발행 마무리”. 기존 보존 제한을 이 추가 범위에 한해 갱신한다. 0910 p17·p19·p43 및 0915 p6·p32 해설을 최소 수정하고, 문제설명 공통 템플릿의 1024px 기본 목차 동작과 해당 동작의 회귀 검사를 수정한다. 원문·정답 모델은 보존한다. 14번 초안을 포함해 최종 두 팩을 새로 build/check하고 내용·화면 검토를 다시 수행해 발행한다. 공식 정답 부재·개인 숙달은 계속 미확인이다.
