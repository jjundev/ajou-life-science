# 최종 복습문제의 문제설명 연결

bio-problem-explain 스킬의 "실행" 1~7단계를 이 팩의 최종 복습문제에 적용한다. 절차를 여기서 다시 쓰지 않고 그 단계 번호를 가리킨다. 신규·보강·`lite` 모두 전체 절차를 실행한다.

**준비** (팩 생성 시작 전, 0단계에서 확인)
- EXPLAIN_SKILL = 이 스킬의 형제 `bio-problem-explain`의 원본 절대 경로(`.agents/skills/bio-problem-explain`; `.claude/skills/` 링크 경로가 아니다).
- `EXPLAIN_SKILL/SKILL.md`와 `EXPLAIN_SKILL/scripts/mpe_cli.py`가 있어야 한다. 없으면 경로와 오류를 보고하고 팩 생성을 시작하지 않는다.

**입력**
- ABS_REVIEW = 검증·발행·MD 변환이 끝난 최종 복습문제 HTML의 절대 경로.
- REPO = 저장소 절대 경로. ABS_CLI = `EXPLAIN_SKILL/scripts/mpe_cli.py`.
- EXPLAIN_RUN = `<scratchpad>/bio-problem-explain/<range>/`(scratchpad가 없으면 `/tmp/bio-problem-explain/<range>/`). 팩마다 비어 있는 새 폴더다. 같은 range를 다시 돌리면 `<range>-2/`처럼 새 폴더를 쓴다.
- 5~8단계에 미해결 기계·내용·브라우저 검사가 있거나 0문항 팩이면 실행하지 않고 보류로 보고한다.

**절차** (`EXPLAIN_SKILL/SKILL.md`를 읽고 그대로 따른다)
1. `EXPLAIN_SKILL/SKILL.md`와 `references/authoring.md`, `references/verification.md`를 읽는다.
2. 실행 1단계: `--target ABS_REVIEW`(최종 HTML 절대 경로)로 `extract`한다. 날짜나 최신 팩 선택에 맡기지 않는다. 모든 ABS 자리는 실제 절대 경로다.
3. 실행 2~3단계: `source.json`의 전체 문항·소문항을 읽고 기출 합본·웹과제·교과서·강의노트·정리노트·`.pack/`의 해당 쪽을 실제로 대조한 뒤 `explanations/pN.html`에 모든 문항의 일곱 구역과 요약을 쓴다. CLI는 설명을 자동 저작하지 않는다.
4. 실행 4단계: 정답을 보지 않은 별도 재풀이와 교과서 대조로 모든 소문항을 검산하고 `evidence/`에 둔다. 원문 오타·복수 정답·답안지 충돌은 disputed로 보류한다.
5. 실행 5단계: `build` 후 `check`. build는 검토를 `not_run`으로 되돌리며 기계 통과는 정답·실화면 승인이 아니다.
6. 실행 6단계: `source_visual`/`content`/`independent`/`browser`를 실제로 수행해 `review.json`에 기록한다. `lite`에서도 생략하지 않는다. 끝나면 서버를 종료한다.
7. 실행 7단계: 네 검토가 모두 `pass`일 때만 `publish`한다. 발행 뒤 최종 경로·원본 보존을 다시 확인한다. 원본이 바뀌면 extract부터, 조각이나 stage가 바뀌면 build와 전체 검토부터 다시 한다.

**보존과 산출**
- 산출은 `복습노트/<range>/문제설명_<range>_<slug>.html`과 `복습노트/<range>/.assets/`의 `문제설명_<range>_<slug>.md`, `figures_문제설명_<range>_<slug>/`, `자료_문제설명_<range>_<slug>/`다.
- 원 복습문제·정리노트·MD·그림·`.pack/`·`풀이기록/`을 수정하지 않는다. 정리노트·복습문제에 링크를 넣지 않는다. 설명 소유 파일만 백업·교체한다.
- 커밋·푸시는 별도 요청이 있을 때만 한다(커밋 제안은 `git add 복습노트/<range>`에 설명 파일이 포함된다).

**결과 보고**
- 발행(published) 또는 보류(withheld)와 이유, HTML/MD 경로, EXPLAIN_RUN, 백업 경로, 네 검토 결과를 적는다.
- 해설 저작·검산·검토·발행 중 하나라도 실패하면 검증된 복습팩과 이전 문제설명을 그대로 두고 "복습팩 생성됨 / 문제설명 보류"로 보고한다. 독립된 다른 팩은 계속 처리한다.
- 기존 range를 전체 재생성(augment 아님)했는데 문제설명이 보류·실패하면 보고서의 미해결에 "기존 문제설명 파일은 이전 카드 기준(stale)"이라고 적는다.
