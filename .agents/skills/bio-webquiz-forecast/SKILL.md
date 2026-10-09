---
name: bio-webquiz-forecast
description: 생명과학 다음 웹과제(장별 퀴즈)를 예상해 복습문제 형식의 예상 세트 HTML을 만든다. "4장 웹과제 예상해줘", "웹과제 예상문제 만들어줘", "예상문제 한 세트 더", /bio-webquiz-forecast N [lite]처럼 장 번호와 함께 요청할 때 쓴다. 부를 때마다 웹과제예상/<N>장/에 v1, v2 … 새 세트가 쌓인다. 정리노트·복습문제(복습팩)·커닝페이퍼를 만드는 요청에는 쓰지 않는다.
---

# 생명과학 웹과제 예상 세트

장 하나의 다음 예상 세트를 `웹과제예상/<N>장/`에 만든다. 세트는 개요 2장(o1·o2), 기출 재출제 예상 5문항(p1–p5), 새 문제 예상 10문항(p6–p15)이고 정답은 A~E 각 3개다. 중간에 묻지 않고 끝날 때 한 번만 보고한다. 커밋은 제안만 한다.

**인자**: `<N> [lite]`. `lite`면 카드 작성자는 `sonnet or luna`를 사용한다. 블라인드 풀이는 lite여도 `opus or sol`을 사용한다.

**경로 약속**
- `SKILL`은 이 폴더 `.agents/skills/bio-webquiz-forecast`의 절대 경로, `REPO`는 저장소 루트, `RUN`은 `<scratchpad>/webquiz-forecast/<N>장-v<K>/`(작업 메모·블라인드 사본).
- 셸 상태는 호출 사이에 이어지지 않으므로 명령마다 절대 경로를 쓴다.

## 절차

### 1. 버전 잡기
`python "$SKILL/scripts/build.py" --init "$REPO" <N>` → 새 `웹과제예상/<N>장/src/v<K>/`가 생긴다. 이 명령만 버전 폴더를 만든다. 기존 버전은 고치지 않는다(덮어쓰기 금지). `REPO`에 `복습노트/`가 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다. `복습노트/*/정리노트_*.md` 중 N장을 다룬 파일이 없으면 "N장 정리노트가 없어 예상할 근거가 없습니다"라고 알리고 멈춘다(만든 빈 폴더는 지운다).

### 2. 원천 모으기
- 출제 패턴: `.agents/skills/bio-review-pack/references/webquiz-style.md`, 이전 장 `웹과제/*/questions.json`.
- 이 장 범위: `복습노트/*/장마감_*_<N>장.md`(있으면), 그 장을 다룬 정리노트 MD, STT(`STT/*.md`)의 "시험"·"중요" 발언.
- 기출 풀: `python "$SKILL/scripts/exam_pool.py" "$REPO" <N> --out "$RUN/pool.json"`. `--out`이 `RUN` 폴더도 만든다. 셸 리디렉션(`>`)은 PowerShell에서 한글 인코딩을 바꿀 수 있어 쓰지 않는다.
- 이전 세트: `웹과제예상/<N>장/src/v*/blueprint.md`와 `pack.json`(쓴 기출 번호·주제).
- 실제 웹과제가 이미 있으면(`웹과제/<N>장/questions.json`) 그 발문은 피하고, 실제 경향을 개요에 반영한다.
- raw/intake만 있으면 공통 출제 기준의 별도 원본 관찰을 참고할 수 있다. 정본 bank 미등록과 공식 답 미확인을 공개하고 확정 집계에 합산하지 않는다. raw를 정본 원문 bank로 사용하지 않고 발문을 복사하지 않는다.

### 3. 개요 카드 o1·o2
`references/forecast-rules.md`대로 메인 에이전트가 `src/v<K>/cards/o1.html`, `o2.html`을 쓴다. o2에는 재출제 유력 기출 10개(번호·핵심 한 줄·정답)를 넣는다.

### 4. 설계표
`references/question-blueprint.md`의 장별 유형 목표·기본 12/심화 3 목표와 최소 풀이 단계를 정하고 `src/v<K>/blueprint.md`와 `pack.json`(`answer_key`, `exam_sources`, `types_required`, `forbidden` 포함)을 쓴다.

### 5. 카드 작성
`references/card-brief.md`의 브리프로 작성자 3명을 **한 메시지에서 병렬로** 띄운다: p1–p5(기출, 원문 대조), p6–p10, p11–p15. 모델은 `opus or sol`(lite면 `sonnet or luna`). 작성자는 빌드·검사를 돌리지 않는다. 세 명이 모두 돌아온 뒤 메인 에이전트가 6단계를 한다.

### 6. 빌드와 검사
```bash
python "$SKILL/scripts/build.py" "$REPO/웹과제예상/<N>장/src/v<K>"
python "$SKILL/scripts/check.py" "$REPO/웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html"
```
`OK`가 나와야 한다. 문제 줄의 카드 id로 담당 작성자를 찾아 한 번에 모아 되돌린다(최대 2회). 남으면 "미해결"로 보고한다.

### 7. 블라인드 풀이
`python "$SKILL/scripts/blind.py" <html> "$RUN/blind.md"`로 사본을 만들고 `references/blind-brief.md`로 `opus or sol` 리뷰어 1명을 띄운다. 리뷰어 답이 `answer_key`와 다르거나 "다른 보기도 답이 될 수 있음" 이의가 있으면 그 카드를 고치고 6단계부터 다시 한다(최대 2회, 매번 새 리뷰어). 목표: 15/15 일치, 이의 0. 2회 뒤에도 남으면 그 카드와 이의를 "미해결"로 보고한다.

정답 일치와 별도로 리뷰어의 수준·최소 풀이 단계를 설계표와 대조한다. 원문은 분류를 재검토하고, 생성 문항은 수정/교체하거나 목표 차이를 보고한다. lite에서도 수행하고 기존 최대 2회 한도에 포함한다. 남은 차이·판정 불가를 미해결로 공개하고, 기본/심화 실개수를 `review_intro`와 o1에 반영해 다시 빌드한다. 난이도 검증은 소비 에이전트의 실제 풀이 검토이며 텍스트 검사만으로 검증했다고 쓰지 않는다.

### 8. 브라우저 확인
저장소 루트에서 `python -m http.server <빈 포트> --bind 127.0.0.1`을 띄우고 세트 HTML을 연다. 375px 가로 스크롤 없음, 콘솔 오류 0, 보기 클릭 채점, 다크 모드 그림을 확인한 뒤 서버를 끈다.

### 9. 보고
```
## 웹과제 예상 <N>장 v<K> 완료
- 파일: 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html (+ src/v<K>/)
- 구성: 개요 2 · 기출 5 (그대로 2 · 쌍둥이 2 · 숫자 1: 기출 <N>강 …) · 새 문제 10
- 정답 분포: A3 B3 C3 D3 E3 · 유형: 부정형 n · 계산 n · 그림 n · 표 n · ㄱㄴㄷ n · 장섞기 n
- 난이도: 기본(수준 1~2) N · 심화(수준 3) N · 목표와 실제 유형 수·난이도 차이 및 이유
- 근거 상태: 확정 bank 통계 / 별도 원본 관찰 / 이전 장 참고를 구별, 공식 답·재사용 미확인 여부
- 이전 세트와 겹침: 기출 번호 0 · 발문 0
- 블라인드: 15/15 (고친 카드: …)
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 웹과제예상/<N>장 && git commit -m "feat(webquiz-forecast): add ch<N> forecast v<K>"
```
