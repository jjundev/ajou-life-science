---
name: bio-webquiz-forecast
description: 생명과학 장별 웹과제 예상문제를 연습형·시험형의 별도 HTML과 공통 상세 해설로 만들 때 사용한다. "4장 웹과제 예상해줘", "웹과제 예상문제 만들어줘", "예상문제 한 세트 더", /bio-webquiz-forecast N [lite]에 사용한다. 정리노트·복습팩·커닝페이퍼에는 사용하지 않는다.
---

# 생명과학 웹과제 예상 세트

장 하나의 다음 예상 세트를 `웹과제예상/<N>장/`에 만든다. 세트는 개요 2장(o1·o2), 기출 재출제 예상 5문항(p1–p5), 새 문제 예상 10문항(p6–p15)이고 정답은 A~E 각 3개다. 같은 원본에서 연습형·시험형 문제 HTML을 각각 생성하고, bio-problem-explain을 자동 사용해 공통 상세 해설 HTML·MD를 만든다. **HTML 3개가 모두 검증·발행되어야 완료**다. [두 풀이형 공통 계약](../bio-exam-forecast/references/dual-html.md)을 먼저 읽는다. 중간에 묻지 않고 끝날 때 한 번만 보고한다. 커밋은 제안만 한다.

**인자**: `<N> [lite]`. `lite`면 카드 작성자는 `sonnet or luna`를 사용한다. 블라인드 풀이는 lite여도 `opus or sol`을 사용한다.

**경로 약속**
- `SKILL`은 이 폴더 `.agents/skills/bio-webquiz-forecast`의 절대 경로, `REPO`는 저장소 루트, `RUN`은 `<scratchpad>/webquiz-forecast/<N>장-v<K>/`(작업 메모·블라인드 사본).
- 셸 상태는 호출 사이에 이어지지 않으므로 명령마다 절대 경로를 쓴다.

## 절차

### 1. 버전 잡기
> `.assets/`는 숨김 폴더라 Glob·Grep 도구가 건너뛴다(0건이어도 없는 게 아니다). 안의 파일은 `복습노트/*/.assets/…`처럼 경로를 글자 그대로 쓰고, 찾을 때는 Bash의 `ls`·`find`나 Python `pathlib`를 쓴다.

`python "$SKILL/scripts/build.py" --init "$REPO" <N>` → 새 `웹과제예상/<N>장/.pack/v<K>/`가 생긴다. 이 명령만 버전 폴더를 만든다. 기존 버전은 고치지 않는다(덮어쓰기 금지). `REPO`에 `복습노트/`가 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다. `복습노트/*/.assets/정리노트_*.md` 중 N장을 다룬 파일이 없으면 "N장 정리노트가 없어 예상할 근거가 없습니다"라고 알리고 멈춘다(만든 빈 폴더는 지운다).

### 2. 원천 모으기
- 출제 패턴: `.agents/skills/bio-review-pack/references/webquiz-style.md`, 이전 장 `웹과제/*/questions.json`.
- 이 장 범위는 `복습노트/*/.assets/장마감_*_<N>장.md`(있으면)와 해당 장 정리노트 MD에서 확인한다. 공지와 강의 전사의 출제 발언은 앞뒤 맥락을 읽고 대상 웹과제, 다른 평가(중간·기말 등), 평가 불명으로 판별한다. 다른 평가나 평가 불명의 발언은 웹과제 범위 확대 근거에서 제외한다. 다음 장 개념은 `references/question-blueprint.md`의 경계 주제 규칙을 따르고, 앞서 배운 개념과의 연결은 기존 장섞기 규칙을 따른다.
- 기출 풀: `python "$SKILL/scripts/exam_pool.py" "$REPO" <N> --out "$RUN/pool.json"`. `--out`이 `RUN` 폴더도 만든다. 셸 리디렉션(`>`)은 PowerShell에서 한글 인코딩을 바꿀 수 있어 쓰지 않는다.
- 이전 세트: `웹과제예상/<N>장/.pack/v*/blueprint.md`와 `pack.json`(쓴 기출 번호·주제). `.pack`은 숨김 폴더라 Glob/Grep이 건너뛰므로 이 경로를 직접 연다.
- 실제 웹과제가 이미 있으면(`웹과제/<N>장/questions.json`) 그 발문은 피하고, 실제 경향을 개요에 반영한다.
- raw/intake만 있으면 공통 출제 기준의 별도 원본 관찰을 참고할 수 있다. 정본 bank 미등록과 공식 답 미확인을 공개하고 확정 집계에 합산하지 않는다. raw를 정본 원문 bank로 사용하지 않고 발문을 복사하지 않는다.

이번 장의 `웹과제/<N>장/note-feedback.md`가 있으면 [공통 본문 피드백](../bio-review-pack/references/note-feedback.md)에 따라 출제 관찰·문항별 판별 기준을 읽고 실제 근거 파일을 대조한다. 개인 학습 가설은 미확인 상태를 유지하며 출제 사실로 쓰지 않는다. 피드백이 없으면 미작성, 근거가 부족하면 보류로 보고한다. bank 존재만으로 응시 완료를 단정하지 않는다.

### 3. 개요 카드 o1·o2
`references/forecast-rules.md`대로 메인 에이전트가 `.pack/v<K>/cards/o1.html`, `o2.html`을 쓴다. o2에는 재출제 유력 기출 10개(번호·핵심 한 줄·정답)를 넣는다.

### 4. 설계표
`references/question-blueprint.md`의 장별 근거를 우선한 유형·기본/심화 목표(근거 부족 시에만 기본 12/심화 3 참고 정책)와 최소 풀이 단계를 정하고 `.pack/v<K>/blueprint.md`와 `pack.json`(`answer_key`, `exam_sources`, `types_required`, `forbidden` 포함)을 쓴다.

설계표 뒤에 `question-blueprint.md`의 `## 회상·비교 연습` 목록을 두고 적용 가능한 새 문항 p6~p15의 명칭·단위 변형을 근거와 연결한다. 고정 의무 개수를 만들거나 기존 버전을 소급 수정하지 않는다.

### 5. 카드 작성
`references/card-brief.md`의 브리프로 작성자 3명을 **한 메시지에서 병렬로** 띄운다: p1–p5(기출, 원문 대조), p6–p10, p11–p15. 모델은 `opus or sol`(lite면 `sonnet or luna`). 작성자는 빌드·검사를 돌리지 않는다. 세 명이 모두 돌아온 뒤 메인 에이전트가 6단계를 한다.

### 6. 빌드와 검사
```bash
python "$SKILL/scripts/build.py" "$REPO/웹과제예상/<N>장/.pack/v<K>"
python "$SKILL/scripts/check.py" --strict "$REPO/웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html"
```
`OK`가 나와야 한다. `[title-leak]`은 정답 보기에만 있는 낱말이 제목에 드러난 것이다. 제목을 발문이 묻는 대상으로 바꾼다(블라인드 풀이 전에 잡아 재풀이를 줄인다). 문제 줄의 카드 id로 담당 작성자를 찾아 한 번에 모아 되돌린다(최대 2회). 남으면 "미해결"로 보고한다.

build는 같은 버전의 연습형과 `_시험형_v<K>.html`을 함께 만들고 `.pack/v<K>/presentations.json`에 두 산출물 해시를 기록한다. check는 어느 문제판을 입력해도 두 판과 원본의 일치를 검사하고, 시험형의 목차 링크·본문 섹션·섹션별 문항 순서를 `pack.json`의 채점 문항과 대조한다. `[exam-layout]`은 표시된 섹션·문항을 출제 명세와 대조해 수정한 뒤 재빌드한다. 일반 검사에서 `OK (구버전 호환)`으로 표시되는 시험형은 현재 생성기로 재빌드해야 발행 검사(`--strict`)를 통과한다. 문항 저작·정답·보기 순서는 공유한다.

### 7. 블라인드 풀이
`python "$SKILL/scripts/blind.py" <html> "$RUN/blind-r1.md"`로 사본을 만들고 `references/blind-brief.md`로 `opus or sol` 리뷰어 1명을 띄운다. 리뷰어가 `$RUN/blind-answers-r1.md`를 쓰면 결과를 카드 해시와 함께 기록하고 판정한다.

```bash
python "$SKILL/scripts/blind_ledger.py" record "$SRC" "$RUN/blind-answers-r1.md" "$RUN/blind-ledger.json" --blind "$RUN/blind-r1.md" --round 1
python "$SKILL/scripts/blind_ledger.py" status "$SRC" "$RUN/blind-ledger.json"
```
`SRC`는 `웹과제예상/<N>장/.pack/v<K>`의 절대 경로다. 리뷰어 답이 `answer_key`와 다르거나 "다른 보기도 답이 될 수 있음" 이의가 있으면 그 카드를 고치고 6단계부터 다시 한다(최대 2회, 매번 새 리뷰어). 다시 풀 때는 `blind_ledger.py changed`가 출력한 바뀐 카드만 `blind.py … --only <id,…>`로 사본을 만들어 새 리뷰어에게 준다(delta). 바뀐 카드가 5개를 넘으면 전체를 다시 푼다. 회차마다 `record --round <n>`으로 병합하고 `status`로 판정한다. 목표: `status`가 OK(15/15 일치, 이의 0, 카드 해시 일치). 2회 뒤에도 남으면 그 카드와 이의를 "미해결"로 보고한다. 8단계 이후 카드를 고치면 ledger의 그 카드는 자동으로 무효가 되어 다시 풀어야 한다. ledger는 9단계에서 해설의 independent 검토로 승계된다.

정답 일치와 별도로 리뷰어의 수준·최소 풀이 단계를 설계표와 대조한다. 원문은 분류를 재검토하고, 생성 문항은 수정/교체하거나 목표 차이를 보고한다. lite에서도 수행하고 기존 최대 2회 한도에 포함한다. 남은 차이·판정 불가를 미해결로 공개하고, 기본/심화 실개수를 `review_intro`와 o1에 반영해 다시 빌드한다. 난이도 검증은 소비 에이전트의 실제 풀이 검토이며 텍스트 검사만으로 검증했다고 쓰지 않는다.

### 8. 브라우저 확인
일회용 Playwright 스크립트를 새로 짜지 않고 표준 스크립트를 한 번 실행한다(약 40초). 저장소 루트를 임의 포트로 띄우고 끝나면 끄며, 문제판이 쓰는 CDN KaTeX·Pretendard는 같은 버전의 로컬 사본으로 대신 응답한다.

```bash
python "$SKILL/scripts/browser_check.py" "$REPO/웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html" --out "$RUN/browser.json" --shots "$RUN/browser-shots"
```
시험형은 브라우저가 만든 목차의 섹션별 문항 링크와 순서를 `pack.json`의 채점 문항과 대조한다.

제출 후 결과에서 문항의 해설을 열어 `A.`~`E.` 보기 라벨과 수업과의 연결이 보이는지 확인한다. 자동 목록 번호와 그 들여쓰기는 시험형 해설 패널에서 제거한다. 카드 원본은 `ol.steps`와 보기 라벨을 유지하고, 패널의 표시 스타일은 `scripts/build.py`가 적용한다.

연습형만 넘기면 시험형을 찾아 **두 문제 HTML**을 1280×900·375×812 × light/dark로 모두 조작한다. 실패하면 문항·화면·이유가 `browser.json`의 `failures`에 남고 exit 1이다. PASS는 기계 확인이므로 `browser-shots/`의 스크린샷을 직접 열어 겹침·잘림·그림을 확인한다. 스크립트가 다루는 공통 계약의 데스크톱/375px·light/dark 검사는 다음과 같다. 연습형은 기존 복습문제의 선택 즉시 채점·현재 문항 유지·보기별 설명·다시 풀기·애매함 표시·복기 프롬프트·새로고침 초기화를 확인하고, 시험형은 p1~p15만 진행·선택 후 이동·제출 전 답 숨김·마지막 전체 제출·5열 채점표를 확인한다. 개요 o1·o2는 연습형에서만 제공한다. 시험형에는 문제 아래를 포함한 어느 위치에도 `출제 개요 보기` 버튼이나 개요 팝업을 만들지 않고, 시험형의 문항·진행·목차·채점에서 개요를 제외한다. 사용자가 기존 시험형의 표시 수정을 요청하면 문항·정답을 보존한 채 대상 장의 기존 시험형 버전 전체에도 적용하고, 해당 UI가 남아 있지 않은지 확인한다. 두 판의 경로·해시·실제 조작 증거(`browser.json`·스크린샷)를 RUN에 구별해 남긴다. 스크립트가 다루지 않는 표시 문제를 찾으면 그 화면만 추가로 확인한다.

### 9. 예상문제해설 생성
[해설 연결·수정 절차](references/explanation-handoff.md)를 읽고 필수 수행한다. `bio-problem-explain`에 방금 통과한 HTML의 명시 절대 경로와 `lite` 여부를 넘기고 새 RUN에서 1–7단계를 실행한다. 준비(`explanation-retry.json` attempt=0·검증 스냅샷·extract)는 `scripts/explain_handoff.py init` 한 번으로 하고, 7단계 ledger를 `mpe_cli.py import-blind`로 independent 검토에 승계한다(조건이 맞지 않으면 별도 독립 검산자). 해설 검토 실패는 원인을 고쳐 최대 2회 재검토하고, 현재 네 검토를 통과하면 발행한다. 미해결은 전체 부분 완료로 보고한다.

### 10. 보고
연습형·시험형·상세 해설 HTML 3개 모두 검증·발행되었을 때만 완료 제목을 쓴다. 하나라도 미해결이면 부분 완료와 각 상태를 보고한다.

```
## 웹과제 예상 <N>장 v<K> 완료
- 연습형 문제: 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html (소스는 .pack/v<K>/)
- 시험형 문제: 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_시험형_v<K>.html
- 해설 파일: 웹과제예상/<N>장/문제해설_<N>장_웹과제예상_v<K>.html (MD·그림·자료 폴더는 .pack/)
- 장 폴더 맨 위에는 HTML과 `.pack/`만 둔다.
- 해설 검토: source_visual/content/independent/browser · 수정 n/2 · 발행/보류 이유
- 문제판 검증: 연습형 … / 시험형 … · 동일 문제 집합 … · 브라우저 증거 경로 …
- 구성: 개요 2 · 기출 5 (그대로 2 · 쌍둥이 2 · 숫자 1: 기출 <N>강 …) · 새 문제 10
- 정답 분포: A3 B3 C3 D3 E3 · 유형: 부정형 n · 계산 n · 그림 n · 표 n · ㄱㄴㄷ n · 장섞기 n
- 난이도: 기본(수준 1~2) N · 심화(수준 3) N · 목표와 실제 유형 수·난이도 차이 및 이유
- 근거 상태: 확정 bank 통계 / 별도 원본 관찰 / 이전 장 참고를 구별, 공식 답·재사용 미확인 여부
- 이전 세트와 겹침: 기출 번호 0 · 발문 0
- 블라인드: 15/15 (고친 카드: …)
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 웹과제예상/<N>장 && git commit -m "feat(webquiz-forecast): add ch<N> forecast v<K>"
```
