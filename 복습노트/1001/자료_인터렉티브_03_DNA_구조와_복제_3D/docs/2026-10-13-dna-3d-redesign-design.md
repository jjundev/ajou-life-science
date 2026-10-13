# DNA 3D 캔버스 리디자인 — 정리노트 스타일 · 라이트/다크 · 좌우 패널

대상: 디자인 캔버스 https://claude.ai/artifact/592nYy4Lwta2FDT8MMGDFZ
파일: `복습노트/1001/DNA_3D/project/Main.dc.html`, `복습노트/1001/DNA_3D/project/canvas.json`

## Intent
게시된 디자인 캔버스(`Main.dc.html` 한 장)를 1001 정리노트 HTML(`복습노트/1001/정리노트_1001_Chromosome_Changes_and_DNA_Replication.html`)의 디자인 시스템으로 옮긴다: 토큰·Pretendard·구분선 레이어·상단 바·좌우 패널. 라이트/다크 토글을 상단 바에 두고, 머리말·부제·안내문 같은 군더더기 텍스트를 빼고, 넓은 화면에서 「왼쪽 패널 | 3D | 오른쪽 패널」 3열로 한 화면(페이지 스크롤 없음)에 담는다. 좁은 화면은 노트처럼 양쪽 drawer.

Classification: bounded — 기존 아티팩트 한 파일의 외형·레이아웃 교체이며 3D 렌더러와 복제 모형 로직은 그대로 쓴다.

## Behavior when done
- 넓은 화면(≥1024px): 상단 바 `[조작 패널 토글] DNA 구조와 복제 [① 구조 | ② 복제] [해/달] [설명 패널 토글]`, 아래 3열. 3D는 남는 폭·높이 전부. 패널만 내부 스크롤.
- 좁은 화면(<1024px): 3D가 가득 차고, 상단 바 버튼으로 양쪽 패널이 가장자리에서 밀려 나옴(scrim 포함). 닫기 버튼·scrim 클릭으로 닫힘. 첫 로드 시 둘 다 닫힘.
- 테마: 해/달 버튼 → 즉시 전환, 페이지 UI와 3D 캔버스(배경·라벨·수소결합 점·닉 고리)가 함께 바뀜. 첫 로드: 저장값(`od-theme`) → 없으면 시스템 설정. 저장 불가 환경에서도 이번 방문엔 유지.
- 모드별 패널 내용
  - ① 구조 — 왼쪽: 보기 옵션 6개, 서열 / 오른쪽: 숫자로 보는 이중나선, 샤가프, 범례, 꼭 기억해요 3장
  - ② 복제 — 왼쪽: 6단계 버튼 + 선택 단계 설명 / 오른쪽: 지금 일어나는 일, 통계 3칸, 범례, 꼭 기억해요 3장
- 재생/슬라이더/속도 바는 지금처럼 3D 하단 오버레이.

## Not in this round
- 패널 너비 드래그 조절 — 고정 폭 `clamp`로 충분.
- 노트의 진행률·페이저 — 화면이 하나라 해당 없음.
- 독립 `.html` 사본 — 범위 밖.
- 3D 기하·복제 타이밍 변경 — 지난 라운드에서 검증 완료.

## Implementation spec
1. **토큰**: 노트 `:16-43`의 라이트/다크 값을 JS 객체 `THEMES.light/dark`로 옮긴다 (키: `bg, surface, ink, ink2, line, accent, accentInk, btnBg, onBtn, warn, prof, supp, danger`). 공용: `radius 8, tap 48, s1–s7 = 4/8/12/16/24/32/48`. 루트 `<div>` inline style에 `--bg: {{th.bg}}; …` 주입.
2. **글꼴**: Pretendard 400/600/700/800 woff2를 asset 업로드 → `<helmet>` `@font-face`. 캔버스 라벨 폰트도 `Pretendard`. 숫자는 `font-variant-numeric: tabular-nums`; IBM Plex 제거.
3. **레이아웃 CSS**(`<helmet><style>`): 노트 `:206-276`을 class 기반으로 이식 — `.app{height:100vh;display:grid;grid-template-rows:auto minmax(0,1fr)}`, `.layout{grid-template-columns:auto minmax(320px,1fr) auto}`, `.panel-left{width:clamp(260px,20vw,320px)}`, `.panel-right{width:clamp(320px,24vw,400px)}`, `@media (max-width:1023.98px)` 고정 drawer + `.is-open` + `.scrim`. 열림 상태 `state.leftOpen/rightOpen`.
4. **컴포넌트 매핑**: 카드 박스 → 노트 `.layer`처럼 `border-top:1px solid var(--line)` 구분, 섹션 제목 19px/700. "꼭 기억해요" → 노트 `.layer.warn`(surface 배경, `--warn` 제목, `:83-86`). 토글/단계 버튼: 높이 48, `1px solid var(--line)`, 배경 `--bg`; 눌림 = 테두리 `--accent`·글자 `--accent-ink`(`:248`). 모드 탭 = 세그먼트, 선택 = `--btn-bg`/`--on-btn`. 해/달·패널 아이콘은 노트 `:326-329` SVG path 그대로.
5. **캔버스 팔레트**: `PAL[theme]` — 배경 단색 `bg`(방사 그라디언트 제거), 라벨 pill `surface`/`line` 테두리, 수소결합 점 `ink`, 닉 고리 `ink`, 옛 가닥 라이트 `#8A94A3`/다크 `#AEB7C4`, 라이트에서 G `#D9A50F`, 새 DNA `#1FA58A`. 효소 반투명 알파 라이트 0.30(다크 0.42).
6. **텍스트 제거**: 머리말 "1001 복습 · 5장 p1–2 · 3D 모형", h1·부제 문단(상단 바 brand로 대체), 캔버스 좌상단 "끌어서 회전 …"(aria-label만 유지), 서열 아래 설명 문단, 단계 미선택 안내 문단(미선택 시 설명 영역 숨김), 카드 제목 축약("복제 6단계", "샤가프 규칙", "서열"), 범례 설명 문단은 1문장으로. 출처는 오른쪽 패널 맨 아래 13px 한 줄 유지.
7. **테마 저장**: `localStorage.getItem('od-theme')`(try/catch) → 없으면 `matchMedia('(prefers-color-scheme: dark)')`. 토글 시 노트 `:563-564` 규칙(시스템과 같아지면 저장값 삭제).
8. **확인**: 1440px 3열·페이지 스크롤 없음 / 390px drawer 열고 닫기·3D 가득 / 테마 전환 시 캔버스 동기 / 복제 6단계 동작.

## Decisions
### Confident
| # | Decision | Answer |
|---|---|---|
| 1 | 테마 적용 방식 | 루트 div CSS 변수 + state (DC 포맷은 document 조작 금지) |
| 2 | 초기 테마 | `od-theme` 저장값 → 시스템 설정 (노트 `:8`, `:552-564`) |
| 3 | 화면 골격 | 상단 바 + 3열 grid, <1024px drawer, 100vh |
| 4 | 패널 역할 | 왼쪽=조작, 오른쪽=설명·요약 |
| 5 | 카드 스타일 | 박스 제거, 구분선 레이어; warn은 surface 배경 |
| 6 | 선택 상태 | accent 테두리 + accent-ink 글자 |
| 7 | 캔버스 팔레트 | 테마별 PAL, 단색 배경 |
| 8 | 지울 텍스트 | spec 6 목록 |

### Confirmed by user
| # | Decision | Answer |
|---|---|---|
| 9 | 글꼴 | Pretendard woff2 업로드 [confirmed] |
| 10 | 넓은 화면 패널 기본 상태 | 양쪽 열림 [confirmed] |
| 11 | 헷갈리기 쉬운 점 | 오른쪽 패널 맨 아래, 모드별 3장 [confirmed] |
