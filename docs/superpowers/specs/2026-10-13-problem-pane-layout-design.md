# 문제해설 레이아웃: 오른쪽 클릭형 문제 패널 + 해설 전용 본문

## Intent
`bio-problem-explain`이 만드는 문제설명·문제해설 HTML에서, 넓은 화면은 문제(질문·보기·그림·기출 원문)를 오른쪽 패널에 고정하고 가운데에는 일곱 해설 구역만 둔다. 패널의 보기는 복습문제와 같은 클릭형 카드이고, 누르면 정답/오답이 표시되며 가운데 해설이 그 보기의 판정 문단으로 이동한다. 완료 기준: 1280×900에서 첫 화면이 해설로 시작하고, 문제는 스크롤과 무관하게 보이며, 기존 12팩을 조각 재저작 없이 새 레이아웃으로 재발행한다.

Classification: bounded — 기존 `mpe_render.build_explanation` → `note-template.html` 흐름 변경과 `rerender` 명령 추가.

## Behavior when done
- ≥1024px: 오른쪽 패널 기본 열림, 상단 **[문제 | 요약]** 탭(기본 문제). 문제 탭은 질문, 클릭형 보기 카드, 그림·표, 접힌 "기출 원문 보기"(forecast는 "원문·출처 정보 보기"). 요약 탭은 기존 페이지 요약.
- 보기 클릭: 누른 카드 "내 선택", 정답 카드 "정답"(ambiguous는 "출제 의도상 답") 배지. 가운데가 solve 구역에서 보기 라벨(`(n)`, `A`, `ㄱ`)로 시작하는 문단으로 스크롤되고 1.6초 강조. 없으면 solve 제목으로. "다시 고르기"로 해제. 선택은 페이지를 연 동안 메모리에만 유지.
- 클릭 전에는 정답을 숨긴다.
- 패널 그림 클릭 → 큰 시트로 확대.
- <1024px: 문제는 해설 맨 위 "문제 보기" 버튼 아래 접힘(기본 접힘). 펼친 뒤 동작은 같다. 요약은 오른쪽 서랍.
- 모델이 없거나 어긋난 문항은 정적 문제. JS 꺼짐이면 문제 블록이 해설 위에 펼쳐진다.
- MD는 문제 → 해설 순서 유지, 기출 원문만 `<details>`.
- 기존 12팩은 `rerender`로 재발행: 입력 동일 시 content·independent 재사용, source_visual·browser 재검토.

## Not in this round
- 보기 선택 localStorage 저장, ㄱㄴㄷ 진술 단위 이동, 조각 `data-choice` 계약, bio-review-pack 템플릿 변경, 복습문제↔문제설명 자동 링크.

## Implementation spec
1. `mpe_types.Problem`에 `choice: ChoiceModel | None = None`. `ChoiceModel(answer: str, mode: str, option_ids: tuple[str, ...])`, `option_ids[i]` = i번째 `.choices > li`의 보기 id. 원본의 `<script id="review-interaction-model" type="application/json">`에서 읽고, 옵션 수 = li 수, answer ∈ ids, index가 0..n-1 순열일 때만 채운다. 아니면 None. review·forecast 모두 적용. extract는 `.choices`가 있는데 None인 문항마다 경고 한 줄.
2. `mpe_render`: 조건/구할 것/그림을 `div.problem-pane[data-problem-for]`로 감싸고 `주어진 조건` h4 제거. 기출 원문은 pane 안 `details.original[data-original-problem]`. `SCRIPTS` 슬롯에 `script#explain-choice-model`(JSON, `</` → `<\/`, None 제외). 부제 "왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요."
3. 템플릿: `data-panels="explain"` + `setupExplain()`. 탭(role=tablist, `.probs`/`.sums`, store 키 `bio-problem-explain-tab`), 토글 라벨 "문제". pane은 wide면 `.probs`, 아니면 article 메타 뒤 `button.problem-toggle[aria-expanded=false]` "문제 보기" 아래. 기본: 오른쪽 `pref.right ?? true`, 왼쪽 `pref.left ?? roomyMq.matches`, `--panel-r-min: 360px`. 보기 `.review-choice` 버튼화, `data-result`, `.review-badge`, `.review-status`(aria-live), "다시 고르기". 이동 정규식 `^\(?ID(\)|\.|\s)`(solve 안 p·li), 대상 1/4 지점, `is-target` 1.6초. 그림 확대는 `.sheet` dialog. CSS는 bio-review-pack `review-interaction.css`의 보기 부분 인라인 복사.
4. `mpe_cli rerender --repo --target --run`: extract → 발행 `자료_<stem>/fragments`·`evidence` 복사 → build → 발행 `validation.json`의 input_hash가 같으면 references·content·independent 이식, 다르면 "입력 변경: 네 검토 모두 다시 필요".
5. 문서: SKILL.md(레이아웃·rerender), authoring.md(판정 문단 라벨 시작), verification.md(browser 항목 추가). `port-provenance.json` 재생성.

## Decisions (모두 확정)
1 원본 `review-interaction-model` 사용 · 2 정적 HTML은 article 안, JS가 이동 · 3 라벨 정규식(실측 429/430) · 4 CSS만 복사, JS 신규 · 5 원문 details · 6 패널 기본값 · 7 그림 dialog · 8 rerender 검토 재사용 범위 · 9 모델 불일치는 정적 · 10 forecast 동일 · 11 12팩 전부 rerender · 12 클릭 전 정답 숨김 · 13 모바일 기본 접힘 · 14 [문제|요약] 탭.
