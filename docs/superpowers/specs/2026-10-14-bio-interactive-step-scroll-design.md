# 단계 버튼 → 설명까지 왼쪽 패널 자동 스크롤

## Intent
인터렉티브 HTML 왼쪽 「단계」 목록에서 버튼을 누르면 목록 아래 설명 상자(`.detail`)가 나타나지만, 단계가 많으면 패널 밖에 있어 직접 스크롤해야 한다. 버튼을 누르면 왼쪽 패널(`.panel-inner`)이 자동으로 내려가 설명이 보이게 한다. 범위: ① 스킬 템플릿, ② 스킬 문서·테스트, ③ 기존 `복습노트/**/인터렉티브_*` 43개(원본 `Main.dc.html` + 빌드된 `.html`).

Classification: bounded — 기존 `pickStep` 흐름(`template.dc.html:705`)에 후처리 한 단계만 붙인다.

## Behavior when done
- 단계 버튼을 누르면 왼쪽 패널이 부드럽게 내려가 설명 상자 하단이 보인다. `prefers-reduced-motion`이면 즉시 이동.
- 설명이 이미 다 보이면 스크롤하지 않는다.
- 설명 상자가 길어 다 보이게 하면 누른 버튼이 위로 사라지는 경우, 버튼이 패널 상단(16px 여백)에 걸리는 지점까지만 내린다.
- 패널만 스크롤되고 페이지·캔버스는 움직이지 않는다.
- 재생·스크럽·모드 전환(단계 선택 해제)은 스크롤하지 않는다.

## Not in this round
- 오른쪽 「설명」 패널 자동 열기·스크롤 — 요청 밖.
- 기존 자료를 `build.cjs`로 재빌드 — 런타임 변경이 섞이므로 원본·빌드본에 같은 문자열 치환.
- `references/example-dna.dc.html`(예전 형식 참고 예시) — 셸을 따라 하지 않는 참고 파일.

## Implementation spec
1. `assets/template.dc.html`: `pickStep(i)`의 `setState` 다음에 `this.revealStepDetail();`, 그 아래 `revealStepDetail()` 메서드 추가. 런타임은 setState 후 microtask에서 다시 그리므로(`dc-runtime.js:106-107`) rAF 안에서 `.panel-left .panel-inner`와 `.detail`, `.steps [aria-pressed="true"]`의 `getBoundingClientRect()`로 이동량을 계산해 `scrollBy`. `typeof document === 'undefined'`면 즉시 반환(harness 호환, `harness.cjs:45`).
2. `references/scene-api.md:97`, `SKILL.md` 6단계 「단계 누르기」에 동작·확인 항목 추가. `tests/template.test.cjs`에 가짜 DOM 테스트.
3. 기존 자료: 템플릿 형식 42쌍은 `pickStep` 블록 치환, 예전 형식 `1001/인터렉티브_03_DNA_구조와_복제_3D`는 `pick` 람다에 호출 추가 + `renderVals()` 앞에 메서드 추가. 각 파일 정확히 1회 매칭, 아니면 건너뛰고 보고. `check.cjs` ok, 브라우저 확인.

## Decisions
### Confident
| # | Decision | Answer | Rationale |
|---|---|---|---|
| 1 | 스크롤 대상 | `.panel-left .panel-inner`만 `scrollBy` | 패널 내부가 스크롤 컨테이너(`template.dc.html:38`); `scrollIntoView`는 페이지까지 움직일 수 있음 |
| 2 | 실행 시점 | `setState` 직후 `requestAnimationFrame` | 다시 그리기가 microtask(`dc-runtime.js:107`) |
| 3 | 훅 위치 | `pickStep` 한 곳 | 단계 선택 경로가 유일(`template.dc.html:705,724`) |
| 4 | harness 호환 | `typeof document` 가드 | harness에 document 없음(`harness.cjs:45`) |
| 5 | 기존 자료 수정 | 원본·빌드본 동일 문자열 치환, 재빌드 안 함 | 42개 `pickStep` 블록 해시 동일 |
| 6 | 움직임 | smooth, reduced-motion이면 즉시 | 템플릿이 이미 reduced-motion 존중(`template.dc.html:142`) |
| 7 | 이미 보일 때 | 스크롤 안 함 | 불필요한 흔들림 방지 |
| 8 | 설명이 너무 길 때 | 누른 버튼을 남기는 쪽 우선 **[confirmed by default]** | |
| 9 | 예전 형식 DNA 3D(1001/03) | 포함 **[confirmed by default]** | |
