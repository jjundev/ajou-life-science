# 문제·원문 패널 왼쪽 분리

## Intent
문제해설 페이지(`bio-problem-explain` 템플릿)에서 오른쪽 [문제 | 원문 | 요약] 탭 중 문제·원문을 새 패널로 떼어 목차 패널 오른쪽·본문 왼쪽에 둔다. 상단 바 목차 버튼 바로 오른쪽에 이 패널의 펼치기/닫기 버튼을 둔다. 목차와 문제 패널은 독립적으로 열리고, 둘 다 열면 `목차 | 문제 | 본문`. 오른쪽 패널은 요약만 남는다. 완료: 1280·1024에서 문제 패널이 본문 왼쪽에 기본으로 열리고, 목차와 동시에 열 수 있으며, 기존 보기 클릭·판정 카드 이동·너비 조절·375 접힘 동작이 그대로 동작한다.

Classification: bounded — 기존 패널 시스템(sync/toggle/리사이즈/mountPanes)에 패널 하나를 더하고 탭을 옮긴다.

## Behavior when done
- 상단 바: `[목차] [문제]  브랜드  테마  [요약]`. 새 `문제` 버튼은 목차 버튼과 같은 패널 아이콘 스타일(띠가 두 번째 칸), 열리면 강조색.
- 넓은 화면(≥1024): 문제 패널은 [문제 | 원문] 탭(원문 없는 문항은 원문 탭 숨김). 목차가 열려 있으면 그 바로 오른쪽. 오른쪽 경계 드래그·화살표 키로 너비 조절, 더블클릭/Home으로 자동 너비.
- 세 패널 열림 상태를 각각 localStorage에 기억. 첫 방문 기본: 문제 열림, 목차는 1280 이상에서만, 요약 닫힘.
- 보기 클릭: 판정 표시·상단 알림·문제 패널 안 보기 스크롤·본문 판정 카드 이동 그대로.
- 좁은 화면(<1024): 새 버튼 숨김, 각 문항 메타 줄 아래 '문제 보기' 접힘 그대로. 오른쪽 `요약` 버튼은 요약 drawer.
- 인쇄: 문제·원문을 각 문항 안으로 되돌려 찍음.

## Not in this round
- 좁은 화면 문제 drawer — 375는 인라인 접힘이 더 가깝다.
- bio-review-pack 레이아웃 — 범위 밖.
- 요약을 문제 패널 탭으로 합치기 — 요청과 반대.

## Implementation spec
- `assets/note-template.html`
  - 마크업: `#toggle-left` 바로 뒤 `#toggle-prob`(aria-controls="panel-prob", 라벨 `문제`). `#toggle-right` 라벨은 항상 `요약`. `#panel-left` 뒤·`.content` 앞에 `<aside class="panel panel-prob" id="panel-prob">`: 오른쪽 가장자리 `.panel-resize[data-side="prob"]`, `.panel-head` 안 탭 [`#tab-problem` | `#tab-original`], 그 아래 `.probs#tabpanel-problem`(`#prob-empty` 포함)·`.orig-tab#tabpanel-original`. `#panel-right`에는 보이는 `h2#panel-right-title`("페이지 요약")와 `.sum-tab` 내용만, `#tab-summary`·탭 리스트 제거. `.layout`에 `data-prob="open"`.
  - CSS: `.layout { grid-template-columns: auto auto minmax(320px,1fr) auto }`; `.panel-prob` grid-column 2 + border-right, `.content` 3, `.panel-right` 4. ≥1024: 문제 패널 너비 `var(--panel-p-user, clamp(360px, calc(100vw - var(--l) - var(--r) - var(--measure) - var(--scrollbar)), 720px))`, `--r` = 요약 패널 너비(닫힘 0px, 열림 `var(--panel-r-user, clamp(300px, 22vw, 380px))`). `.layout[data-prob="closed"] .panel-prob { display:none }`. <1024: `.panel-prob`, `#toggle-prob` 숨김(drawer 아님); no-JS에서도 숨김.
  - JS: `panels`/`toggles`에 `prob`; `sync`는 `['left','prob','right']`, `prob`는 넓은 화면에서만 docked 값, 좁은 화면은 항상 닫힘. explain 기본 `{left: roomy, prob: true, right: false}`. 저장 키 `od-panels:explain:v2`. `WIDTH.prob = {min: 320, max: 720, prop: '--panel-p-user'}`, `maxFor`는 열린 다른 패널 너비 합을 뺌, 핸들 방향 left·prob `+1`, right `-1`. `setupExplain`: `probs/origTab/tabList/tabs`는 `panels.prob`에서, 탭은 `['problem','original']`, 저장된 `'summary'`는 `'problem'`, 요약 분기 제거·`sumTab` 상시 표시, `mountPanes`의 넓은 화면 라벨·제목 전환 제거(제목 '페이지 요약', 라벨 '요약'), `od:screen`에서 두 패널 스크롤 맨 위. 보기 클릭·카드 이동은 선택자만 `panels.prob`로.
- 테스트: `tests/test_render.py::test_problem_panel_left_of_content`, `tests/browser_acceptance.py` 갱신.
- 문서: `SKILL.md:75`, `references/authoring.md:32`, `references/verification.md:10`.
- 발행: 12개 팩 `mpe_cli.py rerender` 재발행(source_visual·browser 재검토), port_provenance 재생성, 175·191 테스트·브라우저 테스트.

## Decisions
### Confident
| # | Decision | Answer |
|---|---|---|
| 1 | 구현 | 세 번째 docked 패널(`prob`) |
| 2 | 좁은 화면 | 새 버튼 숨김, 인라인 '문제 보기' 유지 |
| 3 | 너비 배분 | 문제 패널이 남는 폭 흡수(360–720) |
| 4 | 저장 키 | `od-panels:explain:v2` |
| 5 | 보기 클릭·카드 이동 | 선택자만 `prob`로 |
| 6 | 발행 | 12개 팩 rerender |
### Confirmed by user
| # | Decision | Answer |
|---|---|---|
| 7 | 오른쪽 패널 | 요약만 (버튼 `요약`) [confirmed] |
| 8 | 첫 방문 기본 | 문제 열림, 목차 1280↑, 요약 닫힘 [confirmed] |
