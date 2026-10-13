# bio-interactive 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 날짜나 주제를 받아 「DNA 구조와 복제 3D」와 같은 디자인의 `인터렉티브_NN.html`을 만드는 프로젝트 스킬과, 그 스킬이 쓰는 템플릿·빌드·검사·대상 해석 스크립트를 만든다.

**Architecture:** 기준 결과물 `Main.dc.html`에서 주제와 무관한 셸(패널·테마·캔버스·재생 바·그리기 기본형)을 `assets/template.dc.html`로 떼어 내고, 주제는 `topic()`·`buildScene()`·`extraState()`·`extraVals()` 훅과 마크업 슬롯만 채운다. `scripts/`의 node 스크립트가 원본을 검사(`check.cjs`)하고 단독 HTML로 빌드(`build.cjs`)하며 날짜·주제를 저장 폴더와 번호로 푼다(`resolve.cjs`). 주제 선정·저작·검토 절차는 `SKILL.md`가 지휘한다.

**Tech Stack:** Node 20+ (`node:test`, `node:vm`, 의존성 없음), x-dc 컴포넌트 형식, Canvas 2D.

**Spec:** `docs/superpowers/specs/2026-10-13-bio-interactive-design.md`

## Global Constraints

- 작업 위치: `main`에서 새 브랜치 `feat/bio-interactive`를 딴 워크트리. 현재 `feat/bio-problem-explain`의 미추적 파일은 건드리지 않는다.
- 스킬 원본 경로: `.agents/skills/bio-interactive/` (아래 `SKILL`). `.claude/skills/bio-interactive` → `../../.agents/skills/bio-interactive` 심볼릭 링크.
- 기준 결과물(읽기 전용): `복습노트/1001/자료_3D모형_1001_DNA_Structure_and_Replication/` — 수정·이동·이름 변경 금지.
- 의존성 추가 금지. 스크립트는 CommonJS `.cjs`, 테스트는 `SKILL/tests/*.test.cjs`, 실행: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
- 파일 이름 표기는 사용자 지정 그대로 「인터렉티브」: `인터렉티브_NN.html`, `자료_인터렉티브_NN/`. NN은 두 자리.
- 글꼴 CDN: `https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css`
- 런타임이 아는 이벤트 속성만: `onClick`, `onKeyDown`, `onMouseEnter`, `onMouseLeave`, `onChange` (+ `ref`, `<sc-if value>`, `<sc-for list as>`).
- 테마 저장 키 `od-theme`(노트와 공유), 패널 너비 키 `interactive-panel-w`. localStorage 접근은 모두 try/catch.
- 날짜당 2–4개(기준 3점 이상 최대 4, 부족하면 2까지 채움), 주제 입력은 1개. 정리노트에 없는 주제는 `복습노트/주제별/`.
- 파일명은 macOS에서 NFD로 저장된다. 경로 비교·검색은 모두 NFC로 정규화한 뒤 한다.

## Review Focus

1. NFD로 저장된 `복습노트`·정리노트 파일명 — NFC 문자열로 찾아도 찾아져야 한다 (Task 4 `finds NFD-named folders`).
2. 번호 빈칸·불일치(`인터렉티브_03.html`과 `자료_인터렉티브_04/`만 있음) — 다음 번호는 05, 기존 것을 덮어쓰지 않는다 (Task 4 `next number skips past every existing NN`).
3. 범위 폴더 안의 날짜(`0923` → `0922-0924`) — 그 폴더를 써야 한다 (Task 4 `date inside a range folder`).
4. localStorage가 막힌 브라우저(사생활 보호 창) — 템플릿이 예외 없이 뜬다 (Task 2 `blocked storage still loads`).
5. 숨겨진 캔버스(서랍·첫 렌더에서 크기 0) — 그리기가 예외 없이 건너뛴다 (Task 2 `zero-size canvas draws nothing and does not throw`).

---

### Task 1: 하네스·런타임·빌드

**Files:**
- Create: `SKILL/assets/dc-runtime.js` (기준 결과물 `standalone/dc-runtime.js` 그대로 복사)
- Create: `SKILL/references/example-dna.dc.html` (기준 결과물 `canvas/Main.dc.html` 그대로 복사, 품질 기준 예시)
- Create: `SKILL/scripts/harness.cjs`
- Create: `SKILL/scripts/build.cjs`
- Test: `SKILL/tests/build.test.cjs`

**Interfaces:**
- Produces (`harness.cjs`):
  - `readDc(file: string) -> string`
  - `markupPart(file: string) -> string` — `data-dc-script` 앞까지
  - `loadComponent(file: string, opts?: {narrow?, systemDark?, reduceMotion?, storage?: object|'throw', innerWidth?}) -> {c, store, win}` — 기준 결과물 `tests/harness.cjs`의 `loadComponent`를 파일 경로 인자로 일반화
  - `makeCtx() -> {ctx, calls}` — 기준 하네스와 같음
  - `makeCanvas(ctx, w = 800, h = 600) -> object` — `clientWidth/clientHeight/width/height/style`, `getContext() → ctx`, `addEventListener/removeEventListener/setPointerCapture` no-op, `getBoundingClientRect() → {left:0, top:0}`
- Produces (`build.cjs`):
  - `build(srcFile: string, outFile: string) -> string` — 기준 `standalone/build.cjs`의 `build()`와 같은 조립. `<title>`은 원본 `<title>` 텍스트, 생성 주석은 `<!-- 생성 파일: <outFile 기준 srcFile 상대 경로>을 고친 뒤 bio-interactive/scripts/build.cjs로 다시 만드세요. -->`, 런타임은 `../assets/dc-runtime.js`
  - `canvasJson(title: string) -> string` — 기준 `canvas/canvas.json`과 같은 구조, `title`과 `boards["Main.dc.html"].title`만 인자, `createdOnFiles.at`은 현재 시각 ISO
  - CLI: `node build.cjs <src Main.dc.html> <out.html>` → out을 쓰고 src 폴더에 `canvas.json`이 없으면 함께 쓴다. `wrote <out>` 출력.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/build.test.cjs`

```js
const EX = path.join(SKILL, 'references', 'example-dna.dc.html');
test('build makes a standalone page from a dc source', () => {
  const h = build(EX, path.join(os.tmpdir(), 'x', '인터렉티브_01.html'));
  for (const s of ['<!doctype html>', '<title>DNA 구조와 복제 3D</title>', PRETENDARD_CDN, '<template id="dc-template">', 'class Component extends DCLogic', 'mountDC(Component)', '<meta name="viewport"'])
    assert.ok(h.includes(s), s);
  for (const s of ['/_blob/', 'support.js', '<x-dc>']) assert.equal(h.includes(s), false, s);
});
test('canvasJson names the board and title', () => {
  const j = JSON.parse(canvasJson('세포 호흡'));
  assert.equal(j.title, '세포 호흡');
  assert.equal(j.boards['Main.dc.html'].title, '세포 호흡');
  assert.deepEqual(j.order, ['Main.dc.html']);
});
test('harness loads a dc component', () => {
  const { c } = loadComponent(EX, { narrow: false });
  assert.equal(c.renderVals().leftCls, 'is-open');
});
test('cli writes the page and canvas.json', () => { /* tmp dir에 example 복사 → execFileSync node build.cjs src out → out 존재, src 폴더 canvas.json 존재 */ });
```

- [ ] **Step 2: 실행해서 실패 확인** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/build.test.cjs` → FAIL (`Cannot find module '../scripts/build.cjs'`)
- [ ] **Step 3: 런타임·예시 복사, `harness.cjs`·`build.cjs` 구현**
- [ ] **Step 4: 다시 실행** → 4/4 PASS
- [ ] **Step 5: 커밋** — `git add .agents/skills/bio-interactive && git commit -m "feat(bio-interactive): add dc harness, runtime, and standalone build"`

---

### Task 2: 공통 셸 템플릿

**Files:**
- Create: `SKILL/assets/template.dc.html`
- Create: `SKILL/references/scene-api.md` — 아래 계약을 주제 저작자용으로 적은 문서(한국어)
- Test: `SKILL/tests/template.test.cjs`

**Interfaces:**
- Consumes: Task 1 `loadComponent`, `makeCtx`, `makeCanvas`
- Produces — 템플릿 계약(Task 3 검사와 Task 5 문서가 이 이름을 쓴다):
  - 마크업 자리표시: `<title>__TITLE__</title>`, `<strong class="brand">__TITLE__</strong>`, `<p class="source">__SOURCE__</p>`. 슬롯 주석 `<!-- SLOT:left -->`(왼쪽 패널 「보기 옵션」·「단계」 사이), `<!-- SLOT:right -->`(오른쪽 패널 「꼭 기억해요」 앞).
  - 공통 마크업: 기준 결과물의 상단 바·`.layout`·좌우 `.panel`(+ `.panel-resize`)·`.scrim`·`.stage`(`canvas ref="{{canvasRef}}"`, `.view-btns`의 확대·축소·시점 처음으로)·`.playbar`(`<sc-if value="{{hasPlayback}}">`)를 그대로. 모드 선택은 `<sc-for list="{{modes}}" as="md">` 버튼(`aria-pressed="{{md.pressed}}" onClick="{{md.pick}}"`). 왼쪽 「보기 옵션」은 `toggles`, 「단계」는 `<sc-if value="{{hasSteps}}">` 안에 `steps`와 `stepDetail`. 오른쪽 「꼭 기억해요」는 `mistakes`. CSS는 기준 `<helmet>`에서 DNA 전용(`.seq*`, `.bars`, `.bar-row`, `.icon-btn-text`)만 빼고 그대로, `@font-face`는 뺀다(빌드가 CDN을 넣는다).
  - 주제 훅(템플릿 클래스의 메서드, 저작자가 바꾸는 유일한 스크립트 부분):
    - `topic() -> {DEMO?: true, MODES: Mode[], STEPS?: Step[], MISTAKES: {[modeKey]: {title, text}[]}, TOGGLES?: [stateKey, label][], PAL: {light: {bg, labelBg, ink, ring, ...}, dark: {...}}}`
    - `Mode = {key, label, cam: {yaw, pitch, zoom}, fit: [w, h], D: number, autoSpin: boolean, rotatable: boolean, playback: null | {fmax: number, rate: number, label: (f) => string}, canvasLabel: (f) => string}`
    - `Step = {mode, f?, c, title, who, text}`
    - `buildScene(mode: string, I: Item[], O: Overlay[]) -> void` — 그리기 항목 k: `0` 구 `{p, r, c, flat?, a?}`, `1` 막대 `{p, q, w, c, rod?, flat?, a?}`, `3` 글자 `{p, text, size, c}`, `4` 화살촉 `{p, q, c}`, `5` 반투명 구 `{p, r, c, focus?}`(항상 음영 구). `O`는 `{p, text, c, size?, dx?, dy?, lead?, a?}` 라벨 칩 또는 `{t: 'ring', p, text}`. 각 형태의 그리기는 기준 `draw`/`drawOverlay`(`example-dna.dc.html` 910–1045행)와 같다. 카메라 중심 `sim.cx`는 0으로 고정.
    - `extraState() -> object` — 초기 상태에 합침(토글 키 등)
    - `extraVals(st) -> object` — `renderVals()` 결과에 합침
  - 공통 상태: `mode`(= `MODES[0].key`), `f: 0`, `playing: false`, `speed: 1`, `step: -1`, `spin: !reduceMotion`, `theme`, `leftOpen`, `rightOpen`, `drawer`, `narrow`, `leftW`, `rightW`, `resizing`
  - 공통 `renderVals()` 키: `th, isDark, isLight, themeLabel, toggleTheme, canvasRef, modes[{label, pressed, pick}], leftCls, rightCls, leftExpanded, rightExpanded, scrimCls, toggleLeft, toggleRight, closePanels, layoutStyle, layoutCls, leftWNow, rightWNow, leftHandleRef, rightHandleRef, onKey, toggles[{label, pressed, toggle}], hasSteps, steps[{num, title, who, c, pressed, pick}], hasStep, stepDetail, mistakes, canvasLabel, zoomIn, zoomOut, resetView, hasPlayback, isPlaying, notPlaying, playLabel, togglePlay, fInt, fLabel, fMax10, onScrub, speeds[{label, pressed, pick}]`
  - 공통 동작: 패널·서랍·너비 조절·테마는 기준과 같음. `tick`은 `autoSpin && spin && !drag`일 때 yaw += dt·0.3, 재생 중이면 `f += dt·rate·speed`, `fmax`에서 멈춤. `rotatable: false`인 모드는 드래그가 카메라를 바꾸지 않음. 단계 `pick`은 그 단계 `mode`로 바꾸고 `f`가 있으면 `f`로 이동·재생 정지. 스크럽 범위 `0..fMax10`(= fmax·10).
  - 데모 주제(템플릿 그대로 동작용): `DEMO: true`, 모드 `a`(라벨 「구조」, 회전·자동 회전, 재생 없음: 고리 모양 구 8개 + 막대)와 `b`(라벨 「과정」, `rotatable: false`, `playback {fmax: 10, rate: 1.4}`: `f`만큼 구가 하나씩 나타남), 단계 2개, 모드마다 꼭 기억해요 1개.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/template.test.cjs` (`T = assets/template.dc.html`)

```js
test('modes render as buttons and switch', () => {
  const { c } = loadComponent(T); let v = c.renderVals();
  assert.deepEqual(v.modes.map((m) => m.label), ['구조', '과정']);
  v.modes[1].pick(); v = c.renderVals();
  assert.equal(c.state.mode, 'b'); assert.equal(v.modes[1].pressed, 'true'); assert.equal(v.hasPlayback, true);
});
test('wide opens both panels; narrow starts closed and Escape closes the drawer', () => { /* narrow:false → leftCls 'is-open'; narrow:true → '' ; toggleRight → scrimCls 'is-on'; onKey({key:'Escape'}) → scrimCls '' */ });
test('theme is saved to od-theme', () => { const { c, store } = loadComponent(T); c.setTheme('dark'); assert.equal(store['od-theme'], 'dark'); });
test('blocked storage still loads', () => { assert.doesNotThrow(() => loadComponent(T, { storage: 'throw' }).c.renderVals()); });
test('reduced motion turns auto spin off', () => { assert.equal(loadComponent(T, { reduceMotion: true }).c.state.spin, false); });
test('draw paints every mode', () => { /* 모드마다 setMode → attachCanvas(makeCanvas(ctx)) → draw(0.016, t) 10회 → calls에 'arc' 있음 */ });
test('zero-size canvas draws nothing and does not throw', () => { /* makeCanvas(ctx, 0, 0) → draw 예외 없음, calls에 'arc' 없음 */ });
test('playback advances to fmax and stops', () => { /* mode b, setState({playing:true}), tick(16·k) 2000회 → state.f === 10, playing false */ });
test('non-rotatable mode ignores drag', () => { /* mode b, attachCanvas, _pd({clientX:0,clientY:0,pointerId:1}), _pm({clientX:100,clientY:50}) → cam.yaw·pitch 그대로 */ });
test('scrub and step pick move f', () => { /* mode b, onScrub({target:{value:'50'}}) → f 5; steps[1].pick() → mode·f가 STEPS[1] 값, playing false */ });
test('placeholders and slots are present', () => { /* markupPart(T)에 '__TITLE__' 2회, '__SOURCE__', '<!-- SLOT:left -->', '<!-- SLOT:right -->' */ });
```

- [ ] **Step 2: 실행해서 실패 확인** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/template.test.cjs` → FAIL (`ENOENT … template.dc.html`)
- [ ] **Step 3: `template.dc.html` 작성** — 기준 `example-dna.dc.html`에서 공통 부분을 옮기고, DNA 전용(`buildStructure`, `lagState`…`buildReplication`, `easeTwist`, `events`, `stats`, 서열·샤가프·효소 마크업, 3D 토글)을 빼고 위 훅·데모로 바꾼다. `scene-api.md`에 훅·항목·상태·키 계약을 적는다.
- [ ] **Step 4: 다시 실행** → 11/11 PASS, 그리고 Task 1 테스트도 PASS
- [ ] **Step 5: 브라우저 확인** — `node SKILL/scripts/build.cjs SKILL/assets/template.dc.html <scratchpad>/template.html`로 빌드해 내장 브라우저로 열고, 1440×900·375×812에서 콘솔 오류 없음, 모드 전환·재생·패널 열고 닫기 동작 확인
- [ ] **Step 6: 커밋** — `git commit -m "feat(bio-interactive): extract shared shell template with demo topic"`

---

### Task 3: 계약 검사 `check.cjs`

**Files:**
- Create: `SKILL/scripts/check.cjs`
- Test: `SKILL/tests/check.test.cjs`

**Interfaces:**
- Consumes: Task 1 하네스, Task 2 템플릿 계약
- Produces: `check(file: string, opts?: {allowTemplate?: boolean}) -> {ok: boolean, errors: string[]}`; CLI `node check.cjs <Main.dc.html> [--allow-template]` → 통과 시 `ok` 출력·종료 0, 실패 시 오류를 한 줄씩 출력·종료 1.
- 오류 코드(`<CODE>:<detail>` 문자열):
  - `SHELL_MISSING:<s>` — 마크업에 `class="app"`, `class="topbar"`, `class="layout`, `panel panel-left`, `panel panel-right`, `class="scrim`, `class="stage"`, `ref="{{canvasRef}}"`, `class="view-btns"`, `@media (max-width: 1023.98px)`, `aria-label="{{themeLabel}}"`, `class="source"` 중 없는 것
  - `HOLE_UNKNOWN:<name>` — `</helmet>` 뒤 마크업의 `{{path}}` 첫 마디가 모든 모드의 `renderVals()` 키 합집합에도, 감싼 `<sc-for as>` 이름에도 없음(`hint-*` 속성 값은 제외)
  - `EVENT_UNSUPPORTED:<attr>` — `on[A-Z]\w*=` 속성 중 런타임 다섯 가지가 아닌 것
  - `HEX_IN_MARKUP:<hex>` — `</helmet>` 뒤 마크업의 `#rrggbb` (색은 토큰·구멍으로만)
  - `RENDER_THROWS:<narrow|wide>-<light|dark>-<mode>` — 그 조합에서 `renderVals()` 예외
  - `DRAW_THROWS:<mode>` / `SCENE_EMPTY:<mode>` — 800×600 가짜 캔버스에서 `draw()` 120프레임(재생 모드는 `playing: true`) 중 예외 / 마지막 프레임에 `arc`·`lineTo`·`fillText` 호출이 하나도 없음
  - `TEMPLATE_LEFT:<what>` — `allowTemplate`가 아닐 때 `__TITLE__`·`__SOURCE__`가 남았거나 `topic().DEMO === true`

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/check.test.cjs`. 변형은 템플릿을 읽어 문자열을 바꾼 뒤 tmp 파일로 쓴다(`mutate(fn) -> path`).

```js
test('template passes with allowTemplate', () => assert.deepEqual(check(T, { allowTemplate: true }), { ok: true, errors: [] }));
test('template left as-is is rejected', () => {
  const r = check(T);
  assert.ok(r.errors.includes('TEMPLATE_LEFT:__TITLE__')); assert.ok(r.errors.includes('TEMPLATE_LEFT:DEMO'));
});
test('missing shell piece', () => assert.ok(check(mutate((s) => s.replace('class="scrim', 'class="dim')), A).errors.includes('SHELL_MISSING:class="scrim')));
test('unknown hole', () => assert.ok(check(mutate((s) => s.replace('{{themeLabel}}"', '{{themLabel}}"')), A).errors.includes('HOLE_UNKNOWN:themLabel')));
test('unsupported event', () => assert.ok(check(mutate((s) => s.replace('onClick="{{zoomIn}}"', 'onDoubleClick="{{zoomIn}}"')), A).errors.includes('EVENT_UNSUPPORTED:onDoubleClick')));
test('raw hex in markup', () => assert.ok(check(mutate((s) => s.replace('<div class="scrim', '<div style="color:#123456" class="scrim')), A).errors.includes('HEX_IN_MARKUP:#123456')));
test('scene that throws', () => assert.ok(check(mutate((s) => s.replace(/buildScene\(mode, I, O\) \{/, '$& if (mode === "b") throw new Error("x");')), A).errors.includes('DRAW_THROWS:b')));
test('empty scene', () => assert.ok(check(mutate((s) => s.replace(/buildScene\(mode, I, O\) \{/, '$& return;')), A).errors.includes('SCENE_EMPTY:a')));
test('cli exit codes', () => { /* 템플릿 + --allow-template → 종료 0, stdout 'ok'; 템플릿 단독 → 종료 1 */ });
```
(`A = { allowTemplate: true }`)

- [ ] **Step 2: 실행해서 실패 확인** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/check.test.cjs` → FAIL (`Cannot find module '../scripts/check.cjs'`)
- [ ] **Step 3: `check.cjs` 구현** — `draw`는 `tick`의 try/catch를 거치지 않도록 직접 부른다.
- [ ] **Step 4: 다시 실행** → 9/9 PASS, 전체 스위트 PASS
- [ ] **Step 5: 커밋** — `git commit -m "feat(bio-interactive): add dc contract checker"`

---

### Task 4: 대상 해석 `resolve.cjs`

**Files:**
- Create: `SKILL/scripts/resolve.cjs`
- Test: `SKILL/tests/resolve.test.cjs`

**Interfaces:**
- Produces: `resolve({repo: string, arg: string}) -> {kind: 'date'|'topic', folder: string(절대 경로, 없을 수 있음), exists: boolean, date: string|null, notes: string[], stt: string|null, existing: {file: string, title: string}[], next: string}`; CLI `node resolve.cjs <repo> <arg>` → JSON 출력, 오류면 `{error: <code>}` 출력·종료 1.
- 규칙:
  - `arg`가 비면 `Error` code `NO_ARG`. `/^\d{4}$/`면 date, 아니면 topic.
  - date: `복습노트/` 아래 폴더 중 이름이 그 날짜이거나 `MMDD-MMDD` 범위가 그 날짜를 포함하는 것(여럿이면 정확히 같은 이름 우선). 없으면 `STT/<MMDD> 생명.md`가 있을 때 `복습노트/<MMDD>`(`exists: false`), 둘 다 없으면 `Error` code `NO_TARGET`.
  - topic: `복습노트/*/정리노트_*.md` 본문에서 NFC·소문자·공백 제거 후 포함 검색, 일치 폴더 중 끝 날짜(이름의 마지막 네 자리)가 가장 큰 것. 없으면 `복습노트/주제별`(`date: null`).
  - `notes`: 그 폴더의 `정리노트_*.md`. `stt`: 날짜가 있고 `STT/<MMDD> 생명.md`가 있으면 그 경로.
  - `existing`: 폴더의 `인터렉티브_*.html`·`3D모형_*.html`과 각 `<title>` 텍스트.
  - `next`: 폴더의 `인터렉티브_(\d{2}).html`과 `자료_인터렉티브_(\d{2})` 중 최댓값 + 1, 두 자리(없으면 `01`).
  - 모든 이름 비교는 NFC로 정규화한 뒤. 돌려주는 경로는 디스크의 실제 이름.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/resolve.test.cjs`. `fixture(tree) -> repo` 도우미가 tmp 폴더에 **NFD** 이름으로 파일을 만든다.

```js
test('date folder with notes and stt', () => { /* 복습노트/1006/정리노트_1006_X.md, STT/1006 생명.md → kind 'date', exists true, notes 1개, stt 경로, next '01' */ });
test('finds NFD-named folders', () => { /* 모든 이름 NFD → resolve({arg:'1006'}).notes.length === 1 */ });
test('date inside a range folder', () => { /* 복습노트/0922-0924/ → arg '0923' → folder 끝이 '0922-0924' */ });
test('stt only date points to a new folder', () => { /* STT/1013 생명.md만 → exists false, folder 끝 '복습노트/1013' */ });
test('no folder and no stt is NO_TARGET', () => assert.throws(() => resolve({ repo, arg: '1231' }), { code: 'NO_TARGET' }));
test('empty arg is NO_ARG', () => assert.throws(() => resolve({ repo, arg: '' }), { code: 'NO_ARG' }));
test('topic picks the latest note that mentions it', () => { /* 0929·1006 정리노트 둘 다 '오페론' → folder 1006 */ });
test('topic not in any note goes to 주제별', () => { /* folder 끝 '복습노트/주제별', date null */ });
test('existing interactives are listed with titles', () => { /* 3D모형_1001_x.html <title>DNA 구조와 복제 3D</title> → existing[0].title */ });
test('next number skips past every existing NN', () => { /* 인터렉티브_03.html + 자료_인터렉티브_04/ → next '05' */ });
```

- [ ] **Step 2: 실행해서 실패 확인** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/resolve.test.cjs` → FAIL (`Cannot find module '../scripts/resolve.cjs'`)
- [ ] **Step 3: `resolve.cjs` 구현**
- [ ] **Step 4: 다시 실행** → 10/10 PASS, 그리고 실제 저장소로 `node SKILL/scripts/resolve.cjs <repo> 1001` → `existing`에 `DNA 구조와 복제 3D`, `next` `01`
- [ ] **Step 5: 커밋** — `git commit -m "feat(bio-interactive): resolve date or topic to folder and next number"`

---

### Task 5: SKILL.md·참조 문서·링크

**Files:**
- Create: `SKILL/SKILL.md`
- Create: `SKILL/references/design.md`
- Create: `SKILL/references/topic-selection.md`
- Create: `.claude/skills/bio-interactive` → `../../.agents/skills/bio-interactive` (심볼릭 링크)
- Test: `SKILL/tests/skill.test.cjs`

**Interfaces:**
- Consumes: Task 1–4의 CLI(`build.cjs`, `check.cjs`, `resolve.cjs`), `assets/template.dc.html`, `references/scene-api.md`, `references/example-dna.dc.html`
- `SKILL.md` 내용(형제 `bio-problem-explain/SKILL.md`의 경로 약속·셸 규칙 문체를 따른다):
  - frontmatter `name: bio-interactive`, `description`: 「생명과학 복습노트 날짜(MMDD)나 주제로 DNA 3D 모형과 같은 디자인의 인터렉티브 HTML(인터렉티브_NN.html)을 만든다. "인터렉티브", "인터랙티브", "3D 모형", "움직이는 자료", /bio-interactive [MMDD|주제]에 사용한다. 정리노트·복습문제 생성(bio-review-pack)에는 사용하지 않는다.」
  - 인자 `[MMDD | 주제]`, 경로 약속(`SKILL`, `REPO`, `RUN = <scratchpad>/bio-interactive/<arg>/`)
  - 절차: 1) `resolve.cjs` → 2) 주제 고르기(`topic-selection.md`, 날짜면 2–4개, 주제면 1개, 브리프 작성) → 3) 주제당 opus 에이전트 병렬 저작(템플릿을 `RUN/<n>/Main.dc.html`로 복사, `scene-api.md`·`design.md`·`example-dna.dc.html`·정리노트·교과서·강의노트 제공, 수업 밖 보충 표시) → 4) `check.cjs` → 5) 별도 에이전트 내용 검토(패널 문구·장면 모델을 정리노트·교과서와 대조) → 6) 통과한 것만 `자료_인터렉티브_NN/`에 원본 복사 후 `build.cjs`로 `인터렉티브_NN.html`(번호는 `resolve`의 `next`부터 차례로) → 7) 내장 브라우저 1440×900·375×812 × 라이트·다크, 콘솔 오류 없음, 모드 전환·재생·패널·드래그 → 8) 보고(만든 파일·점수와 이유·보류와 이유·커밋 제안)
  - 실패 처리: `NO_TARGET` → 「대상 없음」 후 중단, 후보 0 → 「후보 없음」, 검사·검토·브라우저 실패 주제는 저장하지 않고 「보류」. 중간 질문 없음, 커밋은 제안만, 기준 결과물·정리노트 수정 금지, Design 캔버스 게시 안 함.
  - 서브에이전트가 없는 환경: 같은 브리프로 차례로 직접 쓰고, 내용 검토는 새 세션에서.
- `design.md`: 노트 스타일 셸 규칙(토큰 이름·간격·버튼 최소 44px·`aria-pressed`/`aria-label`·해요체 짧은 문장·색은 토큰과 `PAL`로만·라벨은 겹치지 않게 평면 기준 고정·동작 줄이기·1024px 서랍), 패널 구성(왼쪽: 모드별 보기 옵션·단계 / 오른쪽: 숫자 타일·범례·꼭 기억해요 3개·출처 한 줄)
- `topic-selection.md`: 점수(과정 +2, 공간 구조 +2, 조건→결과 관계 +2, 「직접 해 보기」 +1), 기준 3점, 개수 규칙(최대 4, 부족하면 2까지 채움, 후보 0이면 「후보 없음」), `existing` 제목과 겹치면 제외, 정의·역사 위주 단원 제외, 브리프 항목(주제·모드 1–3개·단계·꼭 기억해요 3개·근거 쪽)

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/skill.test.cjs`

```js
test('frontmatter names the skill', () => { /* SKILL.md 첫 블록에 'name: bio-interactive', description 비어 있지 않음 */ });
test('every referenced skill file exists', () => { /* SKILL.md의 (assets|scripts|references)/[\w.-]+ 경로마다 fs.existsSync */ });
test('rules from the spec are stated', () => { for (const s of ['2–4', '인터렉티브_NN.html', '자료_인터렉티브_NN/', '복습노트/주제별/', 'check.cjs', 'build.cjs', 'resolve.cjs', '1440×900', '375×812']) assert.ok(md.includes(s), s); });
test('topic selection states the scoring', () => { for (const s of ['+2', '+1', '3점']) assert.ok(sel.includes(s), s); });
test('.claude link resolves to the skill', () => { /* fs.lstatSync(link).isSymbolicLink() && fs.realpathSync(link) === fs.realpathSync(SKILL) */ });
```

- [ ] **Step 2: 실행해서 실패 확인** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/skill.test.cjs` → FAIL (`ENOENT … SKILL.md`)
- [ ] **Step 3: 세 문서 작성, 링크 생성** (`ln -s ../../.agents/skills/bio-interactive .claude/skills/bio-interactive`)
- [ ] **Step 4: 전체 스위트 실행** — `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs` → 전부 PASS
- [ ] **Step 5: 커밋** — `git add .agents/skills/bio-interactive .claude/skills/bio-interactive && git commit -m "feat(bio-interactive): add skill instructions, design and topic references"`
