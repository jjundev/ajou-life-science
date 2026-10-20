# 복기 프롬프트 내보내기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습문제·시험예상문제의 JSON 내보내기를 없애고, 풀이 결과와 코칭 지시문을 묶은 "복기 프롬프트"를 클립보드로 복사하는 버튼으로 바꾼다.

**Architecture:** 순수 함수 `buildReviewPrompt(record)`와 복사 및 대체 대화상자 도우미를 담은 공통 모듈 `review-prompt.js`를 하나 만든다. 이 모듈을 복습문제 런타임(`review_interaction.install`)과 시험 런타임(`exam_build`)에 인라인한다. 각 런타임은 DOM 강화나 수식 렌더 전에 카드 원문을 캡처하고, 클릭 시점의 정오 상태와 합쳐 정규화 record를 만든다. JSON 저장 경로(폴더 API, 다운로드, 스냅샷, 수집 스크립트, 약점노트 어댑터)는 모두 지운다.

**Tech Stack:** 바닐라 JS(UMD, `node:test`), Python 3 조립 스크립트(pytest/unittest), Playwright(Chromium) 브라우저 검사.

**Spec:** `docs/superpowers/specs/2026-10-20-review-prompt-export-design.md` (프롬프트 고정 문구와 화면 문구는 이 문서를 그대로 따른다)

## Global Constraints

- 모든 명령은 저장소 루트(`C:\Users\Hyunjun\Desktop\현준대학\26-2\생명과학`)에서 실행한다. 경로는 `.agents/skills/...`다(`.claude/skills/*`는 이 폴더의 심볼릭 링크).
- 화면 문구와 프롬프트 문구는 spec의 "프롬프트 문구(고정)"와 "화면 문구"에서 글자 그대로 가져온다.
- 상태 값 `'correct' | 'unsure' | 'incorrect' | 'unanswered' | 'ambiguous' | 'pending'`. 묶음 순서는 incorrect → unsure → pending → unanswered → ambiguous.
- CSS 클래스 `.review-export-bar`, `.review-export`(버튼), `.review-export-note`는 이름을 유지한다. `bio-problem-explain/tests/test_render.py`가 `.review-export-bar`를 CSS 절단 표지로 쓴다.
- 답·푼 기록은 계속 `sessionStorage`만 쓴다. 새 저장 키는 만들지 않는다.
- 기존 `복습노트/*/.assets/풀이기록/*.json` 파일은 지우지 않는다.
- 커밋 메시지 형식: `feat(review): ...`, `refactor(exam): ...` 같은 conventional commits 형식이고, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`를 붙인다.

## Review Focus

1. **시험 단답형에 `<script>different</script>` 같은 입력:** 복사된 프롬프트와 대화상자 textarea에 글자 그대로 들어가고 실행되거나 이스케이프되지 않아야 한다. Task 3 브라우저 테스트가 고정한다.
2. **sessionStorage가 막힌 브라우저(접근 시 throw):** 메모리 상태로 프롬프트가 만들어지고 오답 문항이 포함되어야 한다. Task 2 브라우저 테스트가 고정한다.
3. **복사 실패 후 버튼을 다시 누름:** 대화상자가 두 개 생기지 않고 기존 것을 내용만 갱신해 다시 연다. Task 2 브라우저 테스트(`test_prompt_fallback_dialog_reused`)가 고정한다.
4. **출제 모호 문항(0929 p11):** `출제 모호` 묶음에 들어가고, `notice`가 있으면 `출제 주의` 해설로 포함되며, 오답으로 세지 않는다. Task 2 단위 테스트가 고정한다.
5. **문제에 그림이 있는 카드:** stem에 `[그림: alt]`가 남고, 보기 텍스트에 `내 선택`/`정답` 배지 글자가 섞이지 않는다(배지가 붙기 전에 캡처). Task 2 브라우저 테스트가 고정한다.

---

### Task 1: 공통 모듈 `review-prompt.js`

**Files:**
- Create: `.agents/skills/bio-review-pack/assets/review-prompt.js`
- Test: `.agents/skills/bio-review-pack/tests/test_review_prompt.cjs`

**Interfaces:**
- Produces (UMD: `module.exports` 또는 `globalThis.ReviewPrompt`):
  - `buildReviewPrompt(record) -> string`. record는 다음 구조다.
    `{kind:'review'|'exam', documentId:string, range:string, items:Item[]}`
    `Item = {id, title, stem, format:'mcq'|'short', options:{id,text}[]|null, selected:string|null, answer:string, accepted:string[]|null, status, explanations:{label:string, text:string}[]}`
    `label`이 빈 문자열이면 `- {text}`, 아니면 `- {label}: {text}`로 출력한다. 요약 수치는 items의 status를 세어 만든다.
  - `problemText(problemEl) -> string`. `.problem`을 clone하고 `.choices`를 제거한 뒤 `img`를 `[그림: {alt}]`로 바꾼다. textContent의 공백을 한 칸으로 줄이고 trim한다.
  - `copyText(win, text) -> Promise<boolean>`. `win.navigator.clipboard.writeText`를 먼저 시도하고, 실패하거나 API가 없으면 숨긴 textarea에서 `win.document.execCommand('copy')`를 시도한다. 둘 다 실패하면 false를 반환한다.
  - `openPromptDialog(doc, text) -> HTMLDialogElement`. `dialog.review-prompt-dialog`가 이미 있으면 재사용하고 textarea 값만 바꾼다. 처음 호출할 때 `<style id="review-prompt-style">`를 한 번 넣는다. `showModal()`을 호출한 뒤 textarea 전체를 선택한다. 제목, 안내, 닫기 문구는 spec을 따른다.

- [ ] **Step 1: 실패하는 테스트 작성** (`test_review_prompt.cjs`, `const api = require('../assets/review-prompt.js')`)
  - `test('상태별 묶음 순서와 빈 묶음 생략')`: items가 incorrect 1, unsure 1, unanswered 1, correct 1, pending/ambiguous 0개다. 출력에서 `### 오답` < `### 애매함 표시(맞혔지만 확신 없음)` < `### 미응답` 순서로 나오는지(indexOf) 확인한다. `### 자기채점 대기`, `### 출제 모호`는 없어야 한다. correct 항목은 `## 확신 있게 맞힌 문항` 아래 `- p4. 제목4`로만 나오고 본문(`문제:`)은 없어야 한다.
  - `test('요약 줄')`: 위 items로 `문항 4개 · 응답 3 · 정답 2(그중 애매함 1) · 오답 1 · 미응답 1`이 포함되어야 한다. pending/ambiguous가 0이면 그 항목이 없어야 한다.
  - `test('객관식 문항 본문')`: `#### p1. 제목1`, `보기:\n- [1] 가\n- [2] 나`, `내 답: [1] / 정답: [2]`, `- 내 선택 [1]: 이유1`, `- 수업과의 연결: 연결` (label이 빈 extra)이 들어 있어야 한다.
  - `test('단답형과 미응답')`: short pending은 `내 답: "Aa" / 정답: 뉴클레오타이드 (허용: 뉴클레오티드, nucleotide)`로 출력되고 `보기:`가 없어야 한다. selected가 null이면 `내 답: 없음`.
  - `test('다시 볼 문항이 없으면 심화 모드')`: 전부 correct면 `## 다시 볼 문항`이 없고, spec의 심화 규칙 문장 `오답·애매함·미응답 문항이 없어.`가 들어 있어야 한다.
  - `test('입력 원문 보존')`: selected `'  <script>x</script>  '`가 출력에 그대로 들어 있어야 한다.
  - `test('kind와 범위 표기')`: exam이면 `시험 예상문제(1장-6장)`, review면 `복습문제(0929)`. 마지막 줄은 `준비됐으면 핵심 진단부터 공유하고 첫 질문을 내 줘.`이다.
  - `test('copyText: clipboard 성공, 실패 시 execCommand, 둘 다 실패면 false')`: 가짜 `win`(navigator.clipboard, document.createElement/body.append/execCommand)으로 세 경로를 모두 검증한다.
- [ ] **Step 2: 실패 확인**: `node --test .agents/skills/bio-review-pack/tests/test_review_prompt.cjs` → `Cannot find module '../assets/review-prompt.js'`
- [ ] **Step 3: `review-prompt.js` 구현**: `review-interaction.js:1-2`, `:536-540`과 같은 UMD 틀을 쓴다. 고정 문구는 spec에서 복사한다.
- [ ] **Step 4: 통과 확인**: 같은 명령 → 전부 PASS
- [ ] **Step 5: 커밋**: `git add .agents/skills/bio-review-pack/assets/review-prompt.js .agents/skills/bio-review-pack/tests/test_review_prompt.cjs` → `feat(review): add shared review prompt builder`

---

### Task 2: 복습문제 런타임에서 JSON을 프롬프트 복사로 교체

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js` (`:49-188` 제거·교체, `:230-243` 캡처 추가, `:385-405` od:mark 제거, `:437-512` 버튼 교체, `:536-537` export 목록)
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.css:40-44`, `:93-113`
- Modify: `.agents/skills/bio-review-pack/scripts/review_interaction.py:184-198` (`review-prompt.js` 인라인)
- Modify: `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs` (`:54-156` 스냅샷·내보내기 테스트와 `:176-335` saveExport 도우미·테스트 삭제)
- Modify: `.agents/skills/bio-review-pack/tests/browser_check_review.py` (`:282-568` 내보내기 관련 테스트 교체)
- Modify: `.agents/skills/bio-problem-explain/tests/test_render.py:205` (끝 표지 `saved` → `copied`)
- Modify (문서): `.agents/skills/bio-review-pack/references/content-rules.md:118`, `.agents/skills/bio-review-pack/references/browser-check.md:78`, `.agents/skills/bio-review-pack/SKILL.md:156`

**Interfaces:**
- Consumes: Task 1의 `ReviewPrompt.buildReviewPrompt`, `problemText`, `copyText`, `openPromptDialog`. 브라우저에서는 `win.ReviewPrompt`, node에서는 `require('./review-prompt.js')`로 가져오고 `mount` 안에서만 참조한다.
- Produces (`review-interaction.js` export에 추가):
  - `captureCardText(card, choices, diagnostics, options, solution) -> {title, stem, options:{id,text}[], diagnostics:{[optionId]:string}, extras:string[]}`. 보기와 진단 텍스트는 `stripDiagnosticPrefix(text.trim(), o.id)`로 정리한다. extras는 `ol.steps > li` 중 어떤 옵션의 diagnostic 인덱스에도 해당하지 않는 줄이다.
  - `buildPromptRecord(model, texts, ids, selectedById, unsureById, range) -> record` (Task 1 record 형식, `kind:'review'`). 상태는 `grade()`로 정한다. null이면 unanswered, correct이면서 unsure이면 unsure. explanations 규칙: 선택한 보기 `내 선택 [id]`, 정답 `정답 [id]`(ambiguous면 `출제 의도상 답 [id]`). 선택이 정답과 같으면 정답 하나만 넣고, 미응답이면 정답만 넣는다. 그 뒤 extras를 label `''`로, `data.notice`가 있으면 `출제 주의`로 넣는다.
- 제거: `exportKey, readSnapshot, writeSnapshot, updateSnapshot, buildExport, exportFilename, handleStore, resolveExportDir, saveExport, isCancel`, 도움말 팝업, `od:leave`/`od:mark` 리스너와 `od:mark` 디스패치.

- [ ] **Step 1: 실패하는 node 테스트 작성** (`test_review_interaction.cjs`에 추가, `:54-156`·`:176-335` 삭제)
  - `test('프롬프트 record: 상태·해설 규칙')`: 0929 형태의 model(p1 single 정답 '2', p11 ambiguous 정답 '3' notice '주의문', p2 미응답)에 `selectedById={p1:'1', p11:'1'}`, `unsureById={}`를 넣는다. 확인: p1 status `incorrect`, explanations label이 `['내 선택 [1]', '정답 [2]', '']` 순서다. p11 status `ambiguous`, label에 `출제 의도상 답 [3]`와 `출제 주의`가 있다. p2 status `unanswered`, 해설은 정답만 있다.
  - `test('프롬프트 record: 정답+애매함은 unsure, 같은 보기는 해설 하나')`: `selectedById={p1:'2'}`, `unsureById={p1:true}`이면 status `unsure`이고 `정답 [2]` 해설이 하나만 있다.
  - `test('API에 JSON 내보내기 함수가 없다')`: `['saveExport','buildExport','exportFilename','resolveExportDir','handleStore','updateSnapshot'].every(k => !(k in api))`.
- [ ] **Step 2: 실패 확인**: `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs` → `buildPromptRecord is not a function` 등 FAIL
- [ ] **Step 3: 런타임 구현**: 카드 루프(`:233-236` 직후, 검증 `continue` 전)에서 `texts[id] = captureCardText(...)`를 저장한다. 내보내기 바에는 버튼 `.review-export`(`복기 프롬프트 복사`)와 `.review-export-note`만 둔다. 클릭하면 `buildPromptRecord` → `buildReviewPrompt` → `copyText`를 거친다. false면 `openPromptDialog`를 연다. `showFeedback(outcome 'copied'|'manual', 'export', message, 2200)`을 호출하고 note에 `message + '.'`를 넣는다. 버튼 중복 클릭은 기존처럼 `disabled`로 막는다.
- [ ] **Step 4: CSS와 인라인**: `.review-feedback[data-result="saved"|"downloaded"]` 셀렉터를 `"copied"|"manual"`로 바꾸고 `.review-export-help*`, `.review-export-popup*` 규칙을 지운다. `review_interaction.install`은 `review-prompt.js` 내용을 `review-interaction.js` 앞, 같은 `<script>` 안에 넣는다. `test_render.py:205`의 끝 표지를 `.review-feedback[data-result="copied"]`로 바꾼다.
- [ ] **Step 5: node·pytest 통과 확인**: `node --test .agents/skills/bio-review-pack/tests/` 그리고 `python -m pytest .agents/skills/bio-review-pack/tests .agents/skills/bio-problem-explain/tests -q` → 전부 PASS
- [ ] **Step 6: 브라우저 테스트 교체** (`browser_check_review.py`): `PICKER_MOCK`, `SNAP_KEY`, `saved_json`과 export·snapshot·help popup 테스트를 지운다. `CLIPBOARD_MOCK` init script(`navigator.clipboard.writeText`가 `window.__copied`에 저장)를 추가한다. 새 테스트는 모두 `open_current_assets()`를 쓴다.
  - `test_prompt_button_only_on_last_screen`: 첫 화면에서는 hidden이고 마지막 화면에서 `복기 프롬프트 복사` 텍스트로 visible.
  - `test_prompt_copies_wrong_answer_with_full_text`: p1에서 첫 보기(오답)를 고르고 마지막 화면에서 클릭한다. `__copied`에 `### 오답`, `#### p1.`, `내 답: [1] / 정답: [2]`가 있고, `내 선택`이라는 배지 문자열이 보기 줄(`- [1] `로 시작하는 줄)에 없다. note 텍스트는 `복기 프롬프트를 복사했어요. AI 채팅에 붙여 넣으세요.`
  - `test_prompt_marks_unsure_and_reset_clears_it`: p1 정답 + 애매함 표시 → `### 애매함 표시(맞혔지만 확신 없음)` 안에 p1이 있다. 다시 풀기 후 재복사하면 p1이 `### 미응답`에 있다.
  - `test_prompt_with_storage_blocked`: sessionStorage/localStorage getter가 throw하는 상태에서 p1 오답 → `__copied`에 `#### p1.`이 있다.
  - `test_prompt_fallback_dialog_reused`: writeText를 reject하고 `document.execCommand = () => false`로 둔다. 클릭하면 `dialog.review-prompt-dialog[open]` 하나가 뜨고 textarea 값에 `# 생명과학 복기 요청`이 있다. 닫기 후 다시 클릭해도 `dialog.review-prompt-dialog` 개수가 1이다.
  - `test_prompt_stem_keeps_figure_alt`: `img`가 있는 `.problem`을 가진 카드를 찾아(`document.querySelector('.problem img')`의 카드, 0929에 없으면 `self.skipTest`) `[그림:`이 그 카드 본문에 들어가는지 확인한다.
  - 유지·수정: `test_unsure_updates_snapshot_immediately_and_survives_navigation`은 스냅샷 단언을 빼고 `test_unsure_survives_navigation_and_reload`로 이름을 바꾼다.
- [ ] **Step 7: 브라우저 테스트 통과 확인**: `python .agents/skills/bio-review-pack/tests/browser_check_review.py` → OK, `pageerror` 없음
- [ ] **Step 8: 문서 수정**: `content-rules.md:118`의 "문제 화면을 벗어날 때마다 … 정적 HTML/Markdown에는" 사이 JSON·스냅샷·폴더 저장 설명을 "마지막 문제 화면에서만 보이는 **복기 프롬프트 복사** 버튼이 spec의 프롬프트를 클립보드에 복사하고, 막히면 직접 복사 대화상자를 연다"로 바꾼다. `unsure`는 "프롬프트의 애매함 묶음"으로 고친다. `browser-check.md:78`과 `SKILL.md:156`의 JSON 내보내기 확인 항목도 프롬프트 복사, 대체 대화상자, 애매함 반영으로 바꾼다.
- [ ] **Step 9: 커밋**: 위 파일 전부 → `feat(review): replace JSON export with review prompt copy`

---

### Task 3: 시험 런타임에서 JSON을 프롬프트 복사로 교체

**Files:**
- Modify: `.agents/skills/bio-exam-forecast/assets/exam-runtime.js` (`:11` 뒤 캡처, `:92-111` 교체, `:221`, `:228`)
- Modify: `.agents/skills/bio-exam-forecast/assets/exam-results.html:4-8`
- Modify: `.agents/skills/bio-exam-forecast/assets/exam-template.html:38`, `:50` (`#export-status` → `#prompt-status`)
- Modify: `.agents/skills/bio-exam-forecast/scripts/exam_build.py:143` (`review-prompt.js`를 `exam-runtime.js` 앞 `<script>`로 인라인)
- Modify: `.agents/skills/bio-exam-forecast/tests/test_exam_results.py:44-62`, `:79-98`
- Modify (문서): `.agents/skills/bio-exam-forecast/references/attempt-export.md`, `references/exam-ui.md:48-50`, `SKILL.md:16`

**Interfaces:**
- Consumes: `window.ReviewPrompt.buildReviewPrompt`, `problemText`, `copyText`, `openPromptDialog` (Task 1). `exam_build.py`는 `ROOT/'.agents/skills/bio-review-pack/assets/review-prompt.js'`를 읽는다(같은 파일 `:125`의 `ROOT` 사용 방식과 같다).
- Produces: 버튼 `#copy-prompt`(btn-primary, `복기 프롬프트 복사`), 상태 `#prompt-status`. `attempt` 객체 구조는 그대로 두되 `exportedAt`은 더 이상 만들지 않는다.

- [ ] **Step 1: 실패하는 테스트로 교체** (`test_exam_results.py`): 페이지 열기 전에 `page.add_init_script`로 clipboard 스텁(`window.__copied`)을 넣는다.
  - `test_results_export_and_review_roundtrip` → `test_results_prompt_and_review_roundtrip`: 다운로드 블록(`:44-62`)을 `#copy-prompt` 클릭으로 바꾼다. 확인: `#export-exam` 개수 0, `#prompt-status` 텍스트가 `복기 프롬프트를 복사했어요. AI 채팅에 붙여 넣으세요.`이다. `__copied`에 `시험 예상문제(`, `### 오답`(p2), `### 자기채점 대기`(p57), `### 미응답`이 있다. p57 줄에 `"  <script>different</script>  "`가 원문 그대로 있고, `(허용:`이 있다. p1은 `## 확신 있게 맞힌 문항` 아래에 있다. p56(matched)도 맞힌 문항에 있다.
  - `test_blank_submit_and_export_failure_retry` → `test_blank_submit_and_copy_fallback`: writeText reject와 `document.execCommand=()=>false` 상태에서 클릭하면 `dialog.review-prompt-dialog[open]`이 뜨고 textarea에 `### 미응답`이 있다. `#prompt-status`는 `자동 복사가 막혀 있어요. 열린 창에서 직접 복사해 주세요.`
  - 같은 테스트에서 첫 문항 stem에 KaTeX 마크업 텍스트(`katex`)가 들어 있지 않은지 확인한다(`'katex' not in copied`).
- [ ] **Step 2: 실패 확인**: `python -m pytest .agents/skills/bio-exam-forecast/tests/test_exam_results.py -q` → `#copy-prompt` 없음으로 FAIL
- [ ] **Step 3: 구현**: `:11` 직후 `const texts = {}`에 카드별 `{title: h3 텍스트, stem: problemText(.problem), options}`를 캡처한다. options는 mcq만 만들고 `.exam-input label`마다 `{id: input.value, text: label.textContent.trim().replace(/^[A-Z]\.\s*/, '')}`, short는 null이다. 클릭 핸들러는 `attempt.cards`를 record items로 매핑한다. status 매핑: correct→correct, matched→correct, incorrect→incorrect, pending→pending, unanswered→unanswered. answer는 mcq면 `option_id`, short면 `canonical`이고 accepted는 canonical을 뺀 `answer.accepted`다. explanations는 `.solution ol.steps > li`마다 `{label:'풀이', text}`다. 그다음 `copyText` → 실패 시 `openPromptDialog`. `exam-results.html` 안내문과 `:221` 확인창 문구는 spec 문구로 바꾸고 `:228`은 `#prompt-status`로 바꾼다.
- [ ] **Step 4: 통과 확인**: `python -m pytest .agents/skills/bio-exam-forecast/tests -q` → 전부 PASS
- [ ] **Step 5: 문서 수정**: `attempt-export.md`는 제목을 `# 시험 응시 기록과 복기 프롬프트`로 바꾼다. 응시 기록은 결과 화면·채점표용 내부 스냅샷이고 파일로 내보내지 않으며, 결과 화면의 복기 프롬프트 복사가 이 기록으로 spec 형식의 프롬프트를 만든다고 적는다. `exportedAt`·다운로드 문장은 삭제한다. `exam-ui.md:50`, `SKILL.md:16`의 "JSON 내보내기"는 "복기 프롬프트 복사"로 바꾼다.
- [ ] **Step 6: 커밋**: → `feat(exam): replace JSON export with review prompt copy`

---

### Task 4: JSON에 의존하던 도구 정리

**Files:**
- Delete: `.agents/skills/bio-review-pack/scripts/collect_solves.py`, `.agents/skills/bio-review-pack/tests/test_collect_solves.py`
- Modify: `.agents/skills/bio-weakness-pack/scripts/weakness_pack.py` (`adapt_export` `:233-256` 삭제, `:531` 호출 삭제, `:535` 풀이기록 mkdir 삭제. `:523-524` 기존 기록 보호는 유지)
- Modify: `.agents/skills/bio-weakness-pack/tests/test_weakness_pack.py:206-227` (`test_export_adapter_routes_versioned_root_and_rejects_wrong_folder` 삭제)
- Modify: `.agents/skills/bio-webquiz-forecast/scripts/build.py:4`, `:23`, `:58` (`OVERRIDE_STYLE` 제거, 독스트링 "치환 3개" → "치환 2개(정리노트 링크, data-range)")
- Modify: `.agents/skills/bio-webquiz-forecast/tests/test_build.py:24`
- Modify (문서): `.agents/skills/bio-review-coach/SKILL.md:3`, `:20-22`, `.agents/skills/bio-weakness-pack/references/generation.md:17`, `:37`, `.agents/skills/bio-weakness-pack/SKILL.md:19`

**Interfaces:**
- Consumes: Task 2의 런타임. 웹과제예상과 약점노트 HTML은 `assemble.build_review`를 거쳐 프롬프트 버튼을 그대로 갖는다.
- Produces: 없음(삭제·정리).

- [ ] **Step 1: 테스트 먼저 수정**: `test_build.py:24`를 `self.assertNotIn('forecast-overrides', html)`과 `self.assertIn('review-export-bar', html)`로 바꾼다. 약점노트 어댑터 테스트는 삭제한다.
- [ ] **Step 2: 실패 확인**: `python -m pytest .agents/skills/bio-webquiz-forecast/tests/test_build.py -q` → `forecast-overrides` 존재로 FAIL
- [ ] **Step 3: 코드 정리**: 위 Files대로 삭제하고 수정한다. `grep -rn "collect_solves\|adapt_export\|OVERRIDE_STYLE" .agents/skills --include=*.py --include=*.md` 결과가 비어야 한다.
- [ ] **Step 4: 통과 확인**: `python -m pytest .agents/skills/bio-review-pack/tests .agents/skills/bio-weakness-pack/tests .agents/skills/bio-webquiz-forecast/tests -q` → PASS
- [ ] **Step 5: 문서 수정**: bio-review-coach description은 `Use when a learner pastes a 생명과학 복기 프롬프트 or provides a legacy 풀이기록 JSON, ...`로 시작하게 바꾼다. 진행 방식 1–2단계는 "붙여 넣은 복기 프롬프트(문서명·범위·문항 묶음)를 읽거나, 이전 풀이기록 JSON이 주어지면 기존 방식대로 읽는다"로 바꾸고, 프롬프트의 `애매함 표시` 묶음은 `unsure`와 같은 신호로 다룬다고 적는다. 약점노트 generation.md에서는 `:17`의 "저장 안내·약점노트 루트 선택만 이 팩 위치에 맞게 조정한다" 문장을 지우고, `:37`의 `JSON 내보내기`와 저장 경로 확인 문장을 "복기 프롬프트 복사"로 바꾼다. SKILL.md `:19`의 `.assets/`에서는 `풀이기록`을 지운다.
- [ ] **Step 6: 커밋**: → `refactor(review): drop JSON export consumers`

---

### Task 5: 기존 HTML에 런타임 재주입(소급)

**Files:**
- Modify (데이터): `복습노트/*/복습문제_*.html`, `웹과제예상/*/복습문제_*.html`, `약점노트/*/복습문제_*.html`(버전 하위 폴더 포함)

**Interfaces:**
- Consumes: `review_interaction.py --root DIR --audit|--write` (`review_interaction.py:213-233`, 블록 교체는 멱등). 시험예상 HTML은 손대지 않는다(결정 #12).

- [ ] **Step 1: 백업**: 대상 HTML을 scratchpad의 `prompt-backfill-backup/`에 상대 경로를 유지해 복사한다.
- [ ] **Step 2: 감사**: 각 루트에 `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root <DIR> --audit`를 실행한다. 대상은 `복습노트`, `웹과제예상/4장`, `웹과제예상/5장`, `약점노트`, 그리고 `약점노트/*/v*`가 있으면 그 폴더들이다. 모든 줄에 `"errors": []`가 있고 종료 코드가 0이어야 한다. 오류가 나는 루트는 쓰지 말고 보고한다.
- [ ] **Step 3: 웹과제예상 숨김 스타일 제거**: 각 `웹과제예상/*/복습문제_*.html`에서 `<style id="forecast-overrides">…</style>\n`를 정확히 1회 지운다. 0회나 2회 이상이면 중단한다.
- [ ] **Step 4: 쓰기**: 같은 루트들에 `--write`를 실행한다.
- [ ] **Step 5: 검증**: 대상 파일마다 `review-prompt`(모듈 식별 문자열 `ReviewPrompt`)가 포함되고 `JSON 내보내기`·`showDirectoryPicker`·`forecast-overrides`가 0회여야 한다(grep 개수로 확인). 이어서 `python .agents/skills/bio-review-pack/tests/browser_check_review.py`가 OK여야 한다. 기존 테스트 중 저장소 파일을 직접 여는 것들이 재주입본을 검증한다.
- [ ] **Step 6: 수동 확인**: `복습노트/0929` 복습문제를 실제 Chrome에서 `file://`로 연다. 한 문제를 틀리고 마지막 화면에서 복사한 뒤, 붙여 넣은 텍스트가 spec 형식인지 눈으로 확인한다. 클립보드 권한 동작은 headless로 확인할 수 없어서 이 단계가 필요하다.
- [ ] **Step 7: 커밋**: → `chore(notes): reinject review runtime with prompt copy`

---

## 자체 검토 결과

- spec 대응: 결정 #1·#3·#6·#7 → Task 1·2·3, #2 → Task 2·3, #4 → Task 1(모듈)과 2·3(인라인), #9 → Task 2·3·4, #10·#13 → Task 1 고정 문구, #11 → Task 4·5, #12 → Task 5, coach 문서 → Task 4.
- 이름 일관성: `buildReviewPrompt`, `problemText`, `copyText`, `openPromptDialog`(Task 1), `captureCardText`, `buildPromptRecord`(Task 2), `#copy-prompt`, `#prompt-status`(Task 3), `.review-prompt-dialog`(Task 1·2·3).
