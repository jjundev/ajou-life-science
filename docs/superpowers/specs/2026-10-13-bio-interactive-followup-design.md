# bio-interactive 시험 실행 후속 수정 — 설계

`/bio-interactive 1006` 시험 실행(2026-10-13)에서 드러난 문제를 스킬에 반영한다. 원 설계: `docs/superpowers/specs/2026-10-13-bio-interactive-design.md`.

## Intent
시험 실행에서 세 주제 중 둘의 단계 버튼이 다음 과정 시작점에 놓여 패널 설명이 화면과 어긋났고, `check.cjs`는 이를 잡지 못했다. 저장은 셸 반복문을 손으로 짜다 zsh 단어 나눔 문제로 잘못된 폴더가 생겼다. 고치면 단계 위치 오류가 4단계 검사에서 걸리고, 저장은 스크립트 한 줄로 끝나며 덮어쓰지 않는다.
Classification: bounded — 기존 검사·템플릿 계약·SKILL.md 절차를 고친다.

## Behavior when done
- `f`가 있는 Step은 `phase`(그 과정 이름)를 가진다. 없거나 빈 문자열이면 `TOPIC_INVALID:STEPS[n].phase`. 그 f에서 `playback.label(f)`에 `phase`가 들어 있지 않으면 `STEP_OFF_PHASE:n — 기대 '<phase>', 실제 '<label>'`. `label`이 예외를 내면 `STEP_OFF_PHASE:n — <예외 문장>`.
- `node scripts/steps.cjs <Main.dc.html>` → 단계마다 번호·제목·모드·f·phase·재생 바 글자·캔버스 설명·주제 패널 값. 5단계 내용 검토와 6단계 브라우저 확인에 쓴다.
- `node scripts/save.cjs <RUN/n/Main.dc.html> <DEST>` → 다음 빈 번호에 `자료_인터렉티브_NN/Main.dc.html`, `canvas.json`, `인터렉티브_NN.html`을 만들고 `{nn, html, dir}` JSON을 출력한다. 덮어쓰지 않고, 차 있으면 다음 번호. 원본 폴더(`RUN`)에는 아무것도 쓰지 않는다.

## Not in this round
- 슬래시 명령 등록 — 링크는 정상이고 세션 시작 때 목록을 읽기 때문이다(새 세션·병합 후 해결).
- 375px 라벨 겹침 — 주제별 디자인 문제.
- 재생 중간 시점 패널 검사 — 단계 지점은 stepChecks가 다룬다.
- `label(f)`와 `label(f−ε)` 경계 자동 판정 — `phase` 비교가 더 정확하다.
- 이미 저장한 1006 원본 3개에 `phase` 넣기 — 검토·브라우저 확인을 통과했으므로 그대로 둔다(#9).

## Implementation spec
- `references/scene-api.md`: Step에 `phase?`(f가 있으면 필수, `playback.label(f)`에 들어 있어야 하는 과정 이름). `playback.label(f)` 관례 `'<과정 이름> · ' + f.toFixed(1) + ' / ' + fmax`. 오류 표에 `STEP_OFF_PHASE`.
- `assets/template.dc.html`: 예시 Step `{mode:'b', f:6}`에 `phase: '진행'`.
- `scripts/check.cjs` `topicChecks`: 위 두 검사. `STEPS[n].mode`·`STEPS[n].f`가 이미 틀린 단계는 phase 검사를 건너뛴다.
- `scripts/steps.cjs`: `stepsReport(file)` + CLI.
- `scripts/save.cjs`: `save({src, dest})` + CLI. 번호는 `resolve.cjs`의 `nextNumber`, 빌드는 `build.cjs`의 `build`·`canvasJson`·`titleOf`.
- `SKILL.md`: 3단계 작성자 지시(phase), 4단계 코드 목록(STEP_OFF_PHASE), 5단계 검토자에게 steps.cjs 출력, 6단계 steps.cjs, 7단계 save.cjs, 실패 처리 표.
- 테스트: check(phase 빠짐·틀림·예외), steps(템플릿 2개, 단계 없는 주제), save(01, 02, 자료 폴더만 있을 때, dest 없음, RUN에 쓰지 않음), skill(문서 언급).

## Decisions
| # | 결정 | 답 |
|---|---|---|
| 1 | 단계 위치 검사 | Step `phase`가 `label(f)` 안에 있는지 |
| 2 | phase 필수 범위 | f가 있는 단계만 |
| 3 | 오류 코드 | 빠짐 `TOPIC_INVALID`, 어긋남·예외 `STEP_OFF_PHASE` |
| 4 | 단계 출력 | `scripts/steps.cjs` |
| 5 | 저장 | `scripts/save.cjs` |
| 6 | 번호 계산 | `resolve.cjs` `nextNumber` 재사용 |
| 7 | 재생 바 글자 관례 | `'<과정 이름> · f / fmax'` |
| 8 | 슬래시 명령 | 코드 변경 없음 |
| 9 | 1006 원본 | 그대로 둠 [confirmed by default] |
| 10 | 1006 결과물 커밋 | 이 브랜치에 별도 커밋 `docs(notes): add 1006 interactives` [confirmed by default] |
| 11 | 진행 | 계획 문서 먼저 [confirmed] |
