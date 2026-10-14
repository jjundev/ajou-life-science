# 문제해설 패널: 원문 탭 분리 + 복습노트 보기 반응 이식

## Intent
`bio-problem-explain` 문제해설 페이지에서 오른쪽 패널을 **[문제 | 원문 | 요약]** 세 탭으로 바꾸고 "기출 원문 보기" 접힘을 원문 탭으로 옮긴다. 문제 탭의 보기 클릭 반응(상태 문구·배지·상단 알림·자동 스크롤)을 복습문제 페이지(`bio-review-pack/assets/review-interaction.{js,css}`)와 같게 맞춘다. 완료 기준: 템플릿만 바뀌고, 기존 12팩을 `rerender`로 재발행하며, 단위·브라우저 테스트가 통과한다.

Classification: bounded — 기존 `note-template.html`의 `setupExplain()` 탭·보기 흐름 변경.

## Behavior when done
- ≥1024px: 패널 탭 [문제 | 원문 | 요약]. 원문 탭은 현재 문항에 `details.original`이 있을 때만 보이고(forecast도 탭 이름 "원문"), 접힘 없이 펼친 원문을 보여 준다. 저장된 탭이 원문인데 현재 문항에 원문이 없으면 문제 탭을 보이되 선호는 유지한다.
- <1024px: 탭 없음. 원문은 "문제 보기" 안에 지금처럼 접힌 `details`로 남는다.
- 인쇄: 원문을 문제 영역 안에 펼쳐 넣는다.
- 보기 클릭(복습노트와 같은 문구):
  - 상단 알림 1.1초: "정답이에요" / "다시 확인해요" (ambiguous는 알림 없음).
  - 상태(보기 목록 위): `정답이에요.` / `정답이 아니에요. 보기별 이유를 확인해 보세요.` / `단일 정답 판정 주의`.
  - 배지: `내 선택`, `정답`, `정답 아님`(single의 나머지 보기), `출제 의도상 답`.
  - `data-result`: 정답 `correct`(ambiguous `intended`), 내 오답 `selected`(ambiguous `uncertain`).
  - 첫 선택에서 잠금, 다시 풀려면 `다시 풀기`. **[#8 confirmed by default]**
  - 자동 스크롤: 내 선택과 정답 보기를 묶어 보기가 들어 있는 스크롤러 가운데로(`scrollAnswerIntoView`). 넓은 화면은 패널, 좁은 화면은 본문.
  - 넓은 화면만 추가로 본문을 해설 판정 문단으로 이동·1.6초 강조. 좁은 화면은 이동하지 않는다. **[#7 confirmed by default]**
- 모델이 없거나 어긋나면 지금처럼 정적 문제.

## Not in this round
- 보기별 이유 펼침(diagnostics), 애매함 표시, 풀이 기록 저장, JSON 내보내기.
- 렌더러 출력 변경(원문은 지금 마크업 그대로, JS가 옮긴다).

## Decisions
| # | Decision | Answer |
|---|---|---|
| 1 | 원문 이동 방식 | 렌더러 유지, JS가 `details.original`을 `.orig-tab`으로 이동 |
| 2 | 좁은 화면 원문 | 문제 영역 안 접힘 유지 |
| 3 | 원문 없는 문항 | 원문 탭 숨김, 문제 탭 표시, 선호 유지 |
| 4 | 탭 순서·이름 | 문제 · 원문 · 요약, forecast도 "원문" |
| 5 | 코드 이식 | 템플릿에 복사 + 출처 주석 + 드리프트 테스트 |
| 6 | 문구 | review-interaction.js `paint()`와 동일, 버튼 `다시 풀기`, 상태는 목록 앞 |
| 7 | 해설 판정 문단 이동 | 넓은 화면만 유지 |
| 8 | 재선택 | 첫 선택 잠금, `다시 풀기`로만 |
| 9 | 스크롤러 | `pane.closest('.panel-inner') || .content` |
| 10 | 재발행 | rerender, 근거 파일 `*-rerender2-<range>` |
