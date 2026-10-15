# 5장 기존 복습팩 갱신 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 실제 5장 웹과제의 판별 기준을 1001·1006·1008 자료에 대조하고 부족한 설명·연습만 반영한다.

**Architecture:** 기존 full 조립과 문제설명 발행기를 사용한다. 현재 HTML에서 기존 조각을 복원해 필요한 조각만 고치고, 카드·풀이기록·위젯·보충 설명은 보존한다. 팩 단위로 검토·발행하거나 이전 팩 전체를 복구한다.

**Tech Stack:** 기존 Python 조립·검사 CLI, HTML/Markdown/JSON, 원자료 PDF, 브라우저 검증. 새로운 생산 코드·의존성은 추가하지 않는다.

**Spec:** `docs/superpowers/specs/2026-10-15-bio-ch5-existing-materials-design.md` (실행 전 함께 읽는다).

## Global Constraints

- 사용자 결정 #1: **복습팩 먼저, 커닝페이퍼 그다음**. 이 계획은 복습팩 단계다.
- Native 방식은 구현자 직접 실행 후 마지막 별도 리뷰어 1명으로 유지한다. 계획 검토 후 구현 시작 지시를 기다린다. 모델 선택은 실행 시 적용 스킬을 따른다.
- 기존 작업 브랜치를 재사용하며 main 병합·push·워크트리 정리를 수행하지 않는다. 이 요청만으로 추가 커밋을 하지 않는다.
- bank/raw/원자료/예상 v1~v4/스킬/템플릿/인터렉티브 HTML/풀이기록을 보존한다.
- 기존 카드의 ID·part·source·answer·문제·보기를 보존한다. 새 문제는 필요한 경우만 다음 ID로 추가한다.
- 본문 수정 팩은 full 경로를 사용하고 17개 피드백은 기존 8열 감사표로 추적한다. 기존 설명 충분은 실제 문장을 인용하며 수정하지 않는다.
- 공식 채점·확신도·개인 취약점·숙달은 미확인 상태를 유지한다. q07을 취약점으로 확정하지 않는다.
- 검토 실패는 최대 2회 수정 후 재검토한다. 계속 실패한 팩은 이전 팩 전체를 복구한다. 다른 팩은 계속 가능하나 시트 단계는 선행 완료까지 대기한다.

## Review Focus

1. 현재 본문은 충분하지만 회상 연습만 부족한 경우: 문단을 중복 추가하지 않고 연습만 보완한다(Task 1·2의 사례 대조).
2. 본문 밖 widget 스크립트·사용자 맞춤 보충·인터렉티브 링크: 복원 전후 토픽·script ID와 내용·링크를 비교한다(Task 2).
3. 기존 풀이기록과 카드 번호: 기존 카드 본문 및 ID 대응을 보존하고 새 문제만 추가한다(Task 2의 보호 검사).
4. 기계 검사 통과 뒤 입력 변경·검토 실패: 과거 리뷰로 발행하지 않고 이전 팩 전체를 복구한다(Task 3).
5. 한 팩만 충분하거나 1001이 변경 불필요한 경우: 불필요한 재생성을 생략하되 17개 전체의 최종 상태와 시트 선행 조건을 기록한다(Task 1·4).

## File Structure

실제 파일명은 Unicode NFC 비교로 열거한다. 아래는 현재 확인한 정본 경로다.

| 역할 | 수정/생성 경로 |
|---|---|
| 입력, 수정 금지 | `웹과제/5장/{questions.json,note-feedback.md}`, STT·강의노트·교과서 |
| 1006 노트/문제/설명 | `복습노트/1006/{정리노트,복습문제,문제설명}_1006_Transcription_Translation_and_Lac_Operon.html` 및 `.assets/`의 대응 MD·설명 소유 자료 |
| 1008 노트/문제/설명 | `복습노트/1008/{정리노트,복습문제,문제설명}_1008_Gene_Regulation_and_DNA_Cloning.html` 및 `.assets/`의 대응 MD·설명 소유 자료 |
| 조건부 1001 | `복습노트/1001/{정리노트,복습문제,문제설명}_1001_Chromosome_Changes_and_DNA_Replication.html` 및 대응 `.assets/` 파일. 부족한 경우만 갱신 |
| 팩별 감사/설계 | 각 날짜 `.pack/{manifest.json,note-feedback-audit.md,variants.md,log.md}` 및 기존 다른 감사 기록 보존 |
| 최종 검토 기록 | 생성 `docs/superpowers/reviews/2026-10-15-bio-ch5-review-pack-backfill.md` |
| 실행 전용 | 고유 RUN 아래 baseline·백업·조각·원자료 추출·보호 검사·브라우저 증거. 저장소에 새 도구/테스트 프레임워크를 만들지 않음 |

명령의 `REPO`는 현재 실행 worktree 절대 경로, `RP=$REPO/.agents/skills/bio-review-pack`, `PE=$REPO/.agents/skills/bio-problem-explain`, `RUN`은 이 작업 전용 새 scratch 절대 경로다. 각 셸 호출에서 이 네 변수를 다시 설정한다. `DAY`는 현재 처리하는 `1001|1006|1008`이다. Python 런타임과 브라우저 도구의 실제 가용성을 실행 시작 때 확인한다.

### Task 1: 17개 기준의 누락 지도와 보존 기준선

**Files:** 입력 17문항 피드백·3개 기존 팩, 생성 `RUN/{inputs.json,coverage.md,baseline.json,baseline-check.py}`, 팩별 `RUN/<DAY>/note-feedback-audit.md`.

**Interfaces:**
- Consumes: 5장 피드백 q01–q17, 기존 1001/1006/1008의 manifest·HTML·MD·연습·검토 기록.
- Produces: `coverage.md`는 ID / 대상 날짜·토픽 / 실제 본문 근거 / 기존 연습 ID / 부족 내용 / 처리 상태를 기록한다. 팩별 감사표는 스킬의 8열 형식을 그대로 사용한다. `inputs.json`은 실제 절대 경로·SHA256·정본 파일명과 실행 출발 커밋을 고정한다.
- `baseline-check.py snapshot --repo REPO --out RUN/baseline.json`: 보호 파일 해시, 각 기존 카드의 HTML 원문·ID·part·source·answer, 토픽 앵커·링크·script ID와 원문을 저장한다.
- `baseline-check.py verify --repo REPO --baseline RUN/baseline.json --changes RUN/changes.json`: 원문/풀이기록/인터렉티브 파일 불변, 기존 카드 동일, 기존 앵커·링크·위젯 보존, 허용 목록 밖 변경 0을 검사한다. `changes.json`은 이번 수정 토픽 ID·추가 카드 ID·재생성 소유 파일 경로만 열거한다. 삭제된 기존 설명은 별도 수동 대조도 한다.

- [ ] **Step 1:** `git status --short`, 현재 커밋·브랜치와 대상 정본을 기록하고 `.agents/skills/bio-review-pack/SKILL.md`, feedback/content/problem-selection/review/browser 규칙 및 PE 규칙을 읽는다. 기존 카드 수 1001=36, 1006=32, 1008=21은 재확인하며 다르면 현재 변경을 조사하고 기준선을 갱신한다.
- [ ] **Step 2:** 위 인터페이스의 실행 전용 보호 검사기를 작성한다. 임시 복사본에서 기존 카드 정답 변경, 풀이기록 삭제, 위젯 script 삭제가 각각 종료 코드 1인지 확인한다. 실제 원본을 고쳐 실패를 만들지 않는다. 정상 기준선 자체는 종료 코드 0이어야 한다.
- [ ] **Step 3:** 고유 백업 폴더에 대상 팩 전체를 복사해 파일 수·SHA256을 대조한다. `웹과제/5장/`, 예상 v1~v4, 인터렉티브 파일·풀이기록·스킬은 별도 보호 목록에 넣는다.
- [ ] **Step 4:** q01–q17을 실제 원자료와 노트·기존 문제로 대조한다. PDF는 쪽 번호로 읽고 표·그림이 필요한 쪽은 렌더링해 확인한다. q01/q06, q03/q04/q15, q09/q12는 연결해서 비교한다. 1001의 q10/q11/q13/q14/q15/q17은 충분하면 그대로 유지한다.
- [ ] **Step 5:** 충분/본문 부족/연습 부족/근거 불확실을 각각 기록한다. 일부러 학습 누락을 만들어 RED로 보고하지 않는다. 완료 전 감사표에는 예정 상태가 남을 수 있지만 최종 산출물에는 실제 문장 또는 보류 이유가 필요하다.
- [ ] **Step 6:** `coverage.md`의 ID 집합이 정확히 q01–q17이고 각 ID에 source·위치·실제 문장 또는 보류 이유가 존재하는지 검사한다. 누락 ID를 제거한 임시 감사표는 실패해야 한다. 이 시점에는 기존 팩을 수정하지 않는다.

### Task 2: 필요한 팩만 full 경로로 재조립

**Files:** Task 1에서 변경 필요로 정한 팩의 HTML·대응 MD·`.pack/`, `RUN/<DAY>/{manifest.json,sections/,cards/,variants.md,changes.json}`. 1001은 조건부다.

**Interfaces:** Consumes Task 1 누락 지도·기준선. Produces 기존 카드 의미를 보존한 full 입력 조각과 갱신된 노트·문제·MD, 실제 본문 문장으로 채운 팩별 감사표. 카드 추가 이유·원천 토픽·변경 요소·질문 방향을 variants에 기록한다.

- [ ] **Step 1:** `augment.py extract "$REPO/복습노트/$DAY" "$RUN/$DAY"`로 기존 카드와 manifest를 복원한다. 이는 입력 추출에만 사용하며 augment build로 본문 갱신을 대신하지 않는다. 사전 작성 감사표와 충돌하지 않도록 추출은 빈 하위 디렉터리에서 하고 이후 감사표를 배치한다.
- [ ] **Step 2:** 현재 노트의 manifest section ID별 내부 HTML을 `sections/<id>.html`로 복원한다. 기존 `augment.SECTION_RE`를 활용하되 모든 section이 정확히 한 번씩 복원됐는지 확인한다. 첫 section h2만 조립기가 넣도록 제외한다. section 밖 `widget-*` 스크립트는 원문 그대로 해당 section 조각에 한 번만 포함한다. theme/panels/pager 같은 공통 스크립트는 템플릿이 넣으므로 중복 삽입하지 않는다.
- [ ] **Step 3:** 변경 전 조각을 별도 staging 디렉터리에 조립하고 기존 카드·토픽·보충·위젯이 보존되는지 대조한다. template 차이·원래 HTML의 수동 수정은 의도치 않게 덮지 말고 해당 manifest/조각에 복원한다. 실패하면 내용 저작 전에 복원 문제를 해결한다.
- [ ] **Step 4:** 부족한 토픽의 formal/warn/필요한 supp만 수정한다. 명칭 연결·비교 단위·단계 판별을 최소 설명으로 보완하고 현재 lac 동기/시작 조건 등 기존 보충을 유지한다. 기존 토픽 ID를 변경하지 않는다.
- [ ] **Step 5:** 연습 부족 항목만 생성한다. 새 ID는 기존 최댓값 다음부터, partC로 추가하며 원래 part 내부 순서를 유지한다. 기존 카드를 재저작하지 않는다. 무조건 17개 추가하거나 actual 원문을 모든 팩에 중복 수록하지 않는다. 정답·설명은 단서 없는 문제 화면에 보이지 않아야 한다.
- [ ] **Step 6:** 기존 manifest 형식으로 추가 문제·required_terms·정확한 제목/문항 수만 동기화한다. 실행 `python3 "$RP/scripts/manifest.py" "$RUN/$DAY/manifest.json"` → `OK`.
- [ ] **Step 7:** 백업이 검증된 팩에 `assemble.py --run "$RUN/$DAY" --out "$REPO/복습노트/$DAY"`를 실행한다. `check_html.py --manifest ... --note <정본 HTML> --review <정본 HTML>` → `OK`. `html2md.py <노트 HTML> <문제 HTML> --check`를 두 경로와 함께 실행한다. 이 변환은 파일을 쓰고 그림 폴더의 SVG를 정리하므로 보존 대상 그림 누락을 검사한다. RUN/figures에는 기존 SVG를 넣지 않는다(assemble의 금지 계약).
- [ ] **Step 8:** 최종 실제 문장·토픽 ID로 감사표를 채운 후 마지막 full 조립·검사를 반복해 `.pack/note-feedback-audit.md`에 보존한다. 보호 검사와 본문 수동 대조가 통과해야 한다. 기존 설명 충분인 팩은 full 재생성을 생략하고 감사 기록만 남긴다.

### Task 3: 문제설명·블라인드 풀이·브라우저 검증

**Files:** 변경 팩의 문제설명 HTML, `.assets/문제설명_*.md`, 설명 소유 그림·자료; 별도 `RUN/explain-<DAY>/`와 검토 증거.

**Interfaces:** Consumes Task 2의 현재 노트/문제/manifest. Produces 현재 입력 해시 기준 검토 통과한 문제설명 및 팩별 published/unchanged/restored 결과. 기존 풀이기록은 출력이 아니다.

- [ ] **Step 1:** `review-prompt.md` 방식으로 현재 문제의 정답·풀이를 제거한 블라인드 사본을 만든다. 작성자와 별도 검토자가 원자료와 노트만 보고 풀이하며, 컨트롤러가 카드 정답과 대조한다. 원본에 없는 전제는 확정 사실로 추가하지 않는다.
- [ ] **Step 2:** 팩이 변경됐다면 새 빈 EXPLAIN_RUN에 `python3 "$PE/scripts/mpe_cli.py" extract --repo "$REPO" --target <정본 복습문제 HTML 절대 경로> --run <EXPLAIN_RUN>`을 실행한다. 기존 설명이 충분한 조각은 재사용 가능하나 현재 입력에 대해 검토한다. 이번 변경은 레이아웃만의 rerender가 아니다.
- [ ] **Step 3:** authoring 규칙의 일곱 구역과 모든 문항/보기를 갖춘 설명을 작성한다. 명칭·비교 단위의 단서와 오판 이유를 필요한 문항에만 보완한다. 원 문제·정답을 몰래 고치지 않는다. 실제 문항 결함과 정답 충돌은 기존 PE 정책대로 구별한다.
- [ ] **Step 4:** `mpe_cli.py build --run <EXPLAIN_RUN>`, `check --run <EXPLAIN_RUN>` 실행. source_visual/content/independent/browser 네 검토를 현재 해시로 기록한다. 과거 pass 복사 금지. 검토 뒤 조각을 고치면 build와 검토를 다시 수행한다.
- [ ] **Step 5:** 1280×900·375×812, light/dark에서 변경 팩의 전체 페이지·목차·문제·보기 설명·이전/다음·링크·그림·위젯을 확인한다. 정답/오답/다시 풀기/새로고침 복원/새 탭 초기화/JSON 내보내기 취소도 검사한다. 콘솔 오류·자원 누락·가로 넘침 0. 풀이기록 JSON과 인터렉티브 파일 해시는 불변이어야 한다.
- [ ] **Step 6:** 현재 입력 해시·네 검토 pass 확인 후 `mpe_cli.py publish --run <EXPLAIN_RUN>`을 실행한다. baseline verify와 전체 audit를 재확인한다. 실패는 최대 2회 수정·재검토하며 미해결이면 이번 실행에서 단독으로 수정한 해당 팩 전체를 검증된 백업에서 복구한다. 동시 변경이 있으면 덮어쓰지 말고 차이를 보고한다.

### Task 4: 통합 판정과 커닝페이퍼 인계

**Files:** `docs/superpowers/reviews/2026-10-15-bio-ch5-review-pack-backfill.md`, 실행 증거. 원본 자료 변경 없음.

**Interfaces:** Consumes Task 1–3 감사/보호/발행 결과. Produces 날짜별 변경 이유·문제 수·추가 ID·해설 상태·보존 검사·보류 사유와 시트 단계 READY/NOT_READY. READY는 감사 완료, 필요한 갱신 팩 검증·발행 완료, 미해결 발행 실패 0을 뜻하며 학습 가설의 확인을 뜻하지 않는다.

- [ ] **Step 1:** q01–q17 전체의 최종 상태를 집계한다. 예정 상태 0, 각 반영 항목의 실제 문장과 위치 존재, 1001 변경 여부의 이유를 확인한다. 자료 불확실은 사유와 실제 문항 결함 공개 위치를 기록한다.
- [ ] **Step 2:** baseline verify, 각 변경 팩의 manifest/check_html/html2md 검사와 PE 현재 해시를 확인한다. `git diff --check`가 통과해야 한다. 원문·예상 v1~v4·풀이기록·인터렉티브 HTML·스킬은 보호 해시와 동일해야 한다. 테스트 코드는 바꾸지 않았으므로 이미 통과한 전체 스킬 pytest를 이유 없이 반복하지 않는다.
- [ ] **Step 3:** Native 실행의 별도 최종 리뷰어에게 설계/계획/현재 diff/원자료 위치/검토 결과를 전달해 의미 충족과 보존을 검토한다. 리뷰어가 검증하지 않은 항목을 검증 완료로 쓰지 않는다. 필요한 수정 뒤 영향 받은 검사·검토만 다시 수행한다.
- [ ] **Step 4:** 최종 보고서와 READY/NOT_READY를 작성한다. 다음 계획 `2026-10-15-bio-ch5-cheatsheet-rebuild.md`로 인계한다. 커밋·통합은 별도 지시가 있을 때만 한다.

## Plan Self-Review

- 설계의 보존/명칭·단위·단계/조건부 갱신/현재 해시 검토/순차 인계를 Task 1–4에 매핑했다.
- augment 추출과 full 조립의 역할을 구별했고, 카드 추출이 section 밖 위젯을 복원하지 않는 문제를 명시했다.
- 보호 검사의 RED는 임시 복사본에서만 수행한다. 실제 학습 누락이나 학생 오개념을 시험을 위해 조작하지 않는다.
- 새로운 생산 인터페이스는 없다. 실행 전용 보호 검사 CLI와 인계 상태만 이 계획에서 정의했다.
