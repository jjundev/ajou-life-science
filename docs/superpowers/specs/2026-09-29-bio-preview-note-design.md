# 생명과학 예습노트 스킬 (`bio-preview-note`) 설계

## Intent
생명과학 **다음 수업 날짜** 하나를 받아, 수업 중 옆에 띄워 둘 짧은 예습노트 HTML(+MD, 그림)을 `예습노트/<MMDD>/`에 만든다. 범위는 직전 복습노트가 끝난 쪽부터 강의노트를 따라간다. 양식은 `bio-review-pack` 정리노트와 같고, 규칙은 머신러닝기초 저장소의 `ml-preview-note` 예습 규칙(짧게, 문제 없음, 교수님 말씀 추측 금지)을 따른다.
완료 기준: `/bio-preview-note 0929`가 4장 p2 이후 범위의 예습노트를 만들고, 기계 검사·리뷰·브라우저 검사(720×900 반 화면)를 통과하며, 기존 `bio-review-pack` 테스트와 새 스킬 테스트가 모두 통과한다.
분류: architectural — 저장소에 예습 흐름이 없어서 새 스킬, 새 manifest 계약, 범위 선택 스크립트가 필요하다.

## Behavior when done
- `/bio-preview-note [MMDD] [lite]` → `예습노트/<MMDD>/예습노트_<MMDD>_<slug>.html`, `.md`, `figures_<MMDD>/`.
- 인자가 없으면 오늘 이후(오늘 포함) STT가 없는 가장 가까운 수업일(화·목). 그 날짜 예습노트가 이미 있으면 멈춘다.
- 대상 날짜의 STT가 이미 있으면 멈추고 `bio-review-pack`을 안내한다.
- 시작점은 가장 최근 정리노트의 마지막 쪽 태그(0922 노트 → `4장 p2`)이고, 절 경계에서 끊어 최대 4쪽까지 담는다.
- 토픽마다 쪽 태그 `4장 p3`, 쉽게 말하면(2문장), 정확히 말하면(정의·단계·비교표), 들을 때 포인트(2항목). 기출·웹과제에 나온 용어가 있는 토픽은 들을 때 포인트에 "기출" 배지가 붙는다.
- 강의노트나 교과서가 그림으로 설명하는 개념이면 그 토픽의 쉽게 말하면 레이어에 인라인 SVG 1개가 들어간다. 교과서 그림을 그대로 넣지 않고, 메인 에이전트가 렌더링한 참고 PNG(`RUN/work/textbook-figs/<토픽id>.png`, 저장소·산출물에 넣지 않음)를 보고 구조(단계 순서, 배치, 화살표 방향, 표지 이름)를 따라 단순하게 다시 그린다. figcaption에 "교과서 그림 4.3을 단순하게 다시 그렸어요"처럼 출처를 적는다. 그림이 있는 토픽도 720×900 한 화면에 들어가야 하고 글은 300자 안팎으로 줄인다.
- 중간 질문 없이 끝에 한 번 보고, 커밋은 제안만 한다. 추출 실패 시 Read 도구, 검사 2회 실패 시 "미해결".

## Not in this round
- 수업 전 동영상 입력 — 저장소에 영상·전사가 없다.
- 예습노트↔복습노트 자동 연결 — 예습노트 효용을 먼저 확인한다.
- 교과서 그림 이미지를 잘라 그대로 넣기 — 큰 래스터 그림은 720×900 한 화면 제약을 깨기 쉽고, 매 회차 PNG가 저장소에 쌓이며 교재 그림 복제라 저작권 부담이 있고, 흰 배경 이미지는 다크모드에서 튄다. 대신 보고 따라 그린 SVG(fig-* 클래스 색)를 쓴다.
- `ml-preview-note`와 공용 코드 통합 — 저장소가 분리돼 있고 사례가 둘뿐이다.

## Approach
| Option | 방식 | 선택 |
|---|---|---|
| A | 새 `bio-preview-note` 스킬이 `bio-review-pack/scripts`를 import해 재사용하고 ml 예습 로직을 옮긴다 | ✔ |
| B | `bio-review-pack`에 preview 모드 추가 | — |
| C | 전역 공용 preview 스킬 + 과목 어댑터 | — |

A: 머신러닝기초의 `ml-preview-note` ↔ `ml-review-pack` 구조를 그대로 따른다.

## Decisions (모두 확정)
| # | 결정 | 답 |
|---|---|---|
| 0 | 접근 | A |
| 1 | 위치 | `.agents/skills/bio-preview-note` + `.claude/skills/bio-preview-note` 심링크(`../../.agents/skills/bio-preview-note`) |
| 2 | 폴더·인자 기준 | 수업 날짜 `MMDD` (`예습노트/0929/`) |
| 3 | 쪽 태그 | `4장 p3`, `4장 p3–p4` (en dash) |
| 4 | 시작점 | 최신 정리노트(범위 끝 날짜 기준)의 최대 `(장, 쪽)`, 그 쪽 포함. 쪽 안의 이미 배운 절은 정리노트 MD `끊긴 지점:` 줄로 뺀다 |
| 5 | 토픽 단위 | 강의노트 소절(`4.1.2`, `n` 항목) 1~2개 |
| 6 | formal 레이어 | 정의 목록·과정 단계·비교표, TeX는 필요할 때만 |
| 7 | 분량 | 수업 1회분: 절 경계 기준 최대 4쪽 |
| 8 | 코드 재사용 | bio `check_common`, `check_note`, `manifest` 헬퍼, `assemble` 도우미, `html2md` import |
| 9 | 템플릿 | bio 템플릿에 `{{BRAND}}` 슬롯, `.layer.listen`·`.badge.exam` CSS 추가, 심링크 공유 |
| 10 | 이미 끝난 수업 | 멈추고 `bio-review-pack` 안내 |
| 11 | 모델 | opus / lite면 sonnet (GPT: sol / luna), 리뷰 생략 없음 |
| 12 | 기출 표시 | 넣음 — manifest `exam_terms`, 들을 때 포인트의 `<span class="badge exam">기출</span>`, 검사 `exam-mark` |
| 13 | 그림 | 강의노트·교과서가 그림으로 설명하는 개념이면 eli5에 인라인 SVG 1개(manifest 토픽 `figure_ref`, 예: `"그림 4.3"`). 참고 PNG는 `RUN/work/textbook-figs/<토픽id>.png`(PyMuPDF, dpi 150)로만 렌더링. figcaption에 `figure_ref`와 "다시 그렸어요". 노트에 `<img>` 금지(검사 `textbook-image`), `figure_ref` 토픽의 SVG 수·출처는 검사 `figure`·`figure-source` |
