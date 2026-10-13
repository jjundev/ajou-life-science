# DNA 3D 캔버스 리디자인 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 게시된 DNA 3D 디자인 캔버스를 1001 정리노트 HTML의 디자인 시스템(토큰·Pretendard·구분선 레이어·상단 바·좌우 패널)으로 옮기고, 라이트/다크 토글과 3열 한 화면 레이아웃을 넣고, 군더더기 텍스트를 뺀다.

**Architecture:** 변경은 단일 Design Component `Main.dc.html`(마크업 + `<helmet>` CSS + `class Component extends DCLogic`)과 `canvas.json`에 한정된다. 테마는 `state.theme` → 루트 div의 CSS 변수(마크업)와 `PAL[theme]`(캔버스 렌더러) 두 갈래로 흐른다. 로직은 Node `vm`으로 `<script type="text/x-dc">`를 꺼내 `DCLogic` 스텁 위에서 실행하는 하네스로 `node --test` 한다.

**Tech Stack:** Design Component(.dc.html, x-dc 템플릿), Canvas 2D, Node 24 `node:test` + `vm`, Pretendard 1.3.9 woff2, Artifact 툴(publish / asset upload).

**Spec:** `docs/superpowers/specs/2026-10-13-dna-3d-redesign-design.md`

## Global Constraints

- 대상 파일: `복습노트/1001/DNA_3D/project/Main.dc.html`, `복습노트/1001/DNA_3D/project/canvas.json`. 캔버스 URL: `https://claude.ai/artifact/592nYy4Lwta2FDT8MMGDFZ`.
- 모든 UI는 `<x-dc>` 마크업. `innerHTML`·`appendChild`·`document.documentElement` 조작·전역 keydown 핸들러 금지. `{{hole}}`은 점 경로 조회만(식 금지).
- 3D 기하와 복제 모형(`lagState`, `lagBond`, `isNick`, `STEPS[].f`, `events`, `stats`)은 바꾸지 않는다.
- 네트워크: Task 5 이후 `<helmet>`에는 업로드된 `/_blob/…` url만. Google Fonts `<link>`·IBM Plex는 남기지 않는다.
- 테마 저장 키 `'od-theme'`, 값 `'light'|'dark'`. drawer 기준 `@media (max-width: 1023.98px)`.
- 노트 토큰(라이트): `bg #ffffff, surface #f7f8fa, ink #111111, ink2 #6b7280, line #d9dee7, accent #1677ff, accentInk #1b64da, btnBg #1b64da, onBtn #ffffff, warn #b54708, prof #6941c6, supp #067647, danger #d92d20`.
- 노트 토큰(다크): `bg #17171c, surface #212128, ink #f2f4f6, ink2 #a3abb8, line #34353d, accent #3182f6, accentInk #6ea4ff, btnBg #1b64da, onBtn #ffffff, warn #f5a15c, prof #b69cff, supp #5fd39a, danger #ff6b61`.
- 터치 타겟 ≥ 44px(버튼 높이 48 = 노트 `--tap`). 반경 8px.
- 커밋 메시지는 `feat(dna-3d): …` 형식, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

- `localStorage`가 막힌 환경(샌드박스 iframe·사생활 보호 창)에서 첫 로드와 테마 토글이 예외 없이 동작해야 한다 → Task 2 `storage throws` 테스트.
- 좁은 화면(<1024px)에서 첫 로드 시 drawer 두 개가 열린 채 3D를 덮으면 안 된다 → Task 4 `narrow starts closed` 테스트.
- 복제 재생 중 테마를 바꿔도 분기점 진행(`sim.f`)이 처음으로 돌아가면 안 된다 → Task 3 `theme switch keeps progress` 테스트.
- 라이트 테마에서 캔버스 라벨 글자가 옅은 가닥 색(예: `#8A94A3`)으로 그려져 흰 바탕에서 안 읽히면 안 된다 → Task 3 `label text uses ink` 테스트.
- 모드를 바꿔도 사용자가 연/닫은 패널 상태가 유지되고, 꼭 기억해요 카드는 모드에 맞게 바뀌어야 한다 → Task 4 `mode switch keeps panels` 테스트.

---

### Task 1: 테스트 하네스와 현재 동작 고정

**Files:**
- Create: `tests/dna_3d/harness.cjs`
- Create: `tests/dna_3d/model.test.cjs`
- Add (현재 미추적): `복습노트/1001/DNA_3D/project/Main.dc.html`, `복습노트/1001/DNA_3D/project/canvas.json`, `docs/superpowers/specs/2026-10-13-dna-3d-redesign-design.md`, 이 계획 파일

**Interfaces:**
- Produces: `loadComponent(opts?: { storage?: object|'throw', systemDark?: boolean, narrow?: boolean }) -> { c: Component instance, store: object, win: object }`, `readMain() -> string`(Main.dc.html 전문), `markupPart() -> string`(`data-dc-script` 이전 부분), `makeCtx() -> { ctx, calls: Array<{op, args, fillStyle, strokeStyle}> }`, `MAIN_PATH`, `CANVAS_JSON_PATH`.

- [ ] **Step 1: 하네스 작성** — `harness.cjs`. 스크립트 추출·실행은 다음 방식으로 고정한다(나머지는 자유):

```js
const src = html.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/)[1];
class DCLogic { constructor(props) { this.props = props || {}; this.state = {}; }
  setState(u) { this.state = Object.assign({}, this.state, typeof u === 'function' ? u(this.state) : u); } }
// win.matchMedia(q): q에 'prefers-color-scheme: dark' 포함 → systemDark, 'max-width: 1023.98px' 포함 → narrow
// win.localStorage: storage==='throw'면 getItem/setItem/removeItem 모두 throw, 아니면 store 객체 기반
// win.devicePixelRatio = 1 (draw()가 읽음)
const ctx = vm.createContext({ DCLogic, window: win, requestAnimationFrame: () => 0, cancelAnimationFrame() {}, console });
vm.runInContext(src + '\n;globalThis.__C = Component;', ctx);
```
`makeCtx()`는 메서드 호출을 `calls`에 기록하고(`fillRect`, `fillText`, `arc`, `stroke` 등은 호출 시점의 `fillStyle`/`strokeStyle` 함께 기록), `createRadialGradient`는 `{ addColorStop() {} }`, `measureText`는 `{ width: 10 }`를 돌려준다.

- [ ] **Step 2: 회귀 테스트 작성** — `model.test.cjs`:

```js
test('lagging fragment 1 replaces fragment 0 primer then seals', () => {
  const { c } = loadComponent();
  assert.deepEqual(c.lagState(9, 26.0), { kind: 'rna', owner: 0 });
  assert.equal(c.lagState(9, 26.3).owner, 1);
  assert.equal(c.isNick(6, 28.0), true);
  assert.equal(c.lagBond(6, 28.9), true);
});
test('steps jump targets unchanged', () => {
  const { c } = loadComponent();
  assert.deepEqual(c.K.STEPS.map((s) => s.f), [5, 11.8, 17, 23.5, 26.9, 28.3]);
});
test('events at f=26.9 mention DNA 중합효소 I', () => {
  const { c } = loadComponent();
  assert.ok(c.events(26.9).some((e) => e.text.includes('DNA 중합효소 I이 1번째 조각')));
});
```

- [ ] **Step 3: 실행** — Run: `node --test tests/dna_3d/` → Expected: 3 PASS(현재 파일 기준).
- [ ] **Step 4: 커밋**

```bash
git add tests/dna_3d 복습노트/1001/DNA_3D docs/superpowers/specs/2026-10-13-dna-3d-redesign-design.md docs/superpowers/plans/2026-10-13-dna-3d-redesign.md
git commit -m "feat(dna-3d): add DNA 3D canvas, redesign spec/plan, and dc test harness"
```

---

### Task 2: 테마 상태·토큰·저장

**Files:**
- Modify: `복습노트/1001/DNA_3D/project/Main.dc.html` (script: `constructor` 217–, `renderVals` 728–)
- Create: `tests/dna_3d/theme.test.cjs`

**Interfaces:**
- Consumes: `loadComponent` (Task 1)
- Produces: `c.K.THEMES.{light,dark}`(Global Constraints의 13개 키, camelCase), `c.state.theme: 'light'|'dark'`, `c.systemDark(): boolean`, `c.setTheme(t: 'light'|'dark'): void`, renderVals 키 `th`(현재 THEMES 객체), `isDark: boolean`, `themeLabel: string`, `toggleTheme: () => void`.

- [ ] **Step 1: 실패 테스트 작성** — `theme.test.cjs`:

```js
test('stored value wins', () => { const { c } = loadComponent({ storage: { 'od-theme': 'dark' }, systemDark: false }); assert.equal(c.state.theme, 'dark'); });
test('falls back to system', () => {
  assert.equal(loadComponent({ systemDark: true }).c.state.theme, 'dark');
  assert.equal(loadComponent({ systemDark: false }).c.state.theme, 'light');
});
test('toggle stores only when differing from system', () => {
  const { c, store } = loadComponent({ systemDark: false });
  c.renderVals().toggleTheme(); assert.equal(c.state.theme, 'dark'); assert.equal(store['od-theme'], 'dark');
  c.renderVals().toggleTheme(); assert.equal(c.state.theme, 'light'); assert.equal('od-theme' in store, false);
});
test('storage throws', () => {
  const { c } = loadComponent({ storage: 'throw', systemDark: true });
  assert.equal(c.state.theme, 'dark');
  assert.doesNotThrow(() => c.renderVals().toggleTheme()); assert.equal(c.state.theme, 'light');
});
test('renderVals exposes tokens and label', () => {
  const l = loadComponent({ systemDark: false }).c.renderVals();
  assert.equal(l.th.bg, '#ffffff'); assert.equal(l.th.accentInk, '#1b64da'); assert.equal(l.themeLabel, '다크 모드로 전환');
  const d = loadComponent({ systemDark: true }).c.renderVals();
  assert.equal(d.th.bg, '#17171c'); assert.equal(d.themeLabel, '라이트 모드로 전환');
});
```

- [ ] **Step 2: 실행해 실패 확인** — Run: `node --test tests/dna_3d/theme.test.cjs` → Expected: FAIL(`state.theme` undefined).
- [ ] **Step 3: 구현** — constructor에서 `K.THEMES` 정의, `state.theme`를 저장값(`'light'|'dark'`만 인정) → `systemDark()` 순으로 결정. `setTheme(t)`: `setState({ theme: t })` 후 `(t === 'dark') === this.systemDark()`면 `removeItem('od-theme')`, 아니면 `setItem('od-theme', t)`; 저장 접근은 전부 try/catch. renderVals에 `th`, `isDark`, `themeLabel`, `toggleTheme` 추가.
- [ ] **Step 4: 실행** — Run: `node --test tests/dna_3d/` → Expected: 전부 PASS.
- [ ] **Step 5: 커밋** — `git commit -am "feat(dna-3d): add light/dark theme state with od-theme persistence"`

---

### Task 3: 캔버스 팔레트를 테마에 연결

**Files:**
- Modify: `Main.dc.html` script — `buildStructure` 345–, `buildReplication` 446–, `draw` 563–, `drawOverlay` 664–
- Create: `tests/dna_3d/palette.test.cjs`

**Interfaces:**
- Consumes: `state.theme`, `setTheme` (Task 2); `makeCtx` (Task 1)
- Produces: `c.K.PAL.{light,dark}`, `c.pal(): object`(= `K.PAL[state.theme]`), `c.baseColor(b: string): string`(G면 `pal().G`, 아니면 `K.BASE[b]`).

PAL 값(그대로 사용):

| 키 | light | dark |
|---|---|---|
| bg | `#ffffff` | `#17171c` |
| labelBg | `#f7f8fa` | `#212128` |
| labelLine | `#d9dee7` | `#34353d` |
| ink / hb / ring | `#111111` | `#f2f4f6` |
| parent / parentSugar | `#8A94A3` / `#6B7584` | `#AEB7C4` / `#7F8A99` |
| newDna / newSugar | `#1FA58A` / `#16806B` | `#6FD3C1` / `#3FA893` |
| rna / rnaSugar | `#FF5FA2` / `#C93F80` | `#FF5FA2` / `#C93F80` |
| G | `#D9A50F` | `#F6C945` |
| blobAlpha | `0.30` | `0.42` |

- [ ] **Step 1: 실패 테스트 작성** — `palette.test.cjs` (`I`, `O`는 빈 배열로 build 호출):

```js
test('hbond dots use pal.hb', () => { for (const t of ['light', 'dark']) {
  const { c } = loadComponent(); c.setTheme(t); const I = [], O = []; c.buildStructure(I, O);
  const dots = I.filter((it) => it.flat && it.r === 0.045);
  assert.ok(dots.length > 0); assert.ok(dots.every((d) => d.c === c.K.PAL[t].hb)); } });
test('light G darkened', () => {
  const { c } = loadComponent({ systemDark: false }); const I = []; c.buildStructure(I, []);
  const rods = I.filter((it) => it.rod).map((it) => it.c);
  assert.ok(rods.includes('#D9A50F')); assert.ok(!rods.includes('#F6C945')); });
test('replication parental uses pal.parent', () => {
  const { c } = loadComponent({ systemDark: false }); c.state.mode = 'replication'; c.sim.f = 30;
  const I = []; c.buildReplication(I, []); const cols = new Set(I.map((it) => it.c));
  assert.ok(cols.has('#8A94A3')); assert.ok(!cols.has('#AEB7C4')); assert.ok(cols.has('#1FA58A')); });
test('draw paints flat pal.bg first', () => { for (const t of ['light', 'dark']) {
  const { c } = loadComponent(); c.setTheme(t); const { ctx, calls } = makeCtx();
  c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 }; c.ctx = ctx; c.draw(0.016, 0);
  const first = calls.find((k) => k.op === 'fillRect'); assert.equal(first.fillStyle, c.K.PAL[t].bg);
  assert.equal(calls.some((k) => k.op === 'createRadialGradient' && k.args[2] === 0 && k.args[0] === 400), false); } });
test('label text uses ink, pill uses labelBg', () => {
  const { c } = loadComponent({ systemDark: false }); const { ctx, calls } = makeCtx(); c.ctx = ctx;
  const V = { cx: 0, cy: 1, sy: 0, cp: 1, sp: 0, F: 300, D: 30, ox: 400, oy: 300 };
  c.drawOverlay({ t: 'label', p: [0, 0, 0], text: '부모 DNA', c: '#8A94A3' }, V, 0);
  assert.equal(calls.find((k) => k.op === 'fillText').fillStyle, '#111111');
  assert.equal(calls.find((k) => k.op === 'fill').fillStyle, '#f7f8fa'); });
test('theme switch keeps progress', () => {
  const { c } = loadComponent(); c.sim.f = 27; c.state.f = 27; c.setTheme('dark');
  assert.equal(c.sim.f, 27); assert.equal(c.state.f, 27); });
```

- [ ] **Step 2: 실행해 실패 확인** — Run: `node --test tests/dna_3d/palette.test.cjs` → Expected: FAIL(`c.pal` / `K.PAL` 없음).
- [ ] **Step 3: 구현** — `K.PAL`, `pal()`, `baseColor()` 추가. 하드코딩 색 교체: 수소결합 점 `#EEF2F7` → `pal().hb`(4곳: 372, 482, 494, 507), `PAR/PARs/NEW/NEWs/RNA/RNAs`(460) → `pal()` 값, 염기 막대 색 `K.BASE[...]` → `baseColor(...)`(구조·복제 모두), `draw`의 방사 그라디언트(570–572) → `ctx.fillStyle = pal().bg; ctx.fillRect(0,0,W,H)`, 효소 blob 채움 알파 `0.42` → `pal().blobAlpha`, `drawOverlay` 닉 고리·글자 `#FFFFFF`(668, 671) → `pal().ring`, 라벨 pill 배경 `rgba(11,15,20,0.86)`(682) → `pal().labelBg`, pill 테두리는 `o.c`(색 구분 유지), 라벨 글자는 `pal().ink`. 구조 모드 가닥 색(`C1`, `C2` 등)은 그대로.
- [ ] **Step 4: 실행** — Run: `node --test tests/dna_3d/` → Expected: 전부 PASS.
- [ ] **Step 5: 커밋** — `git commit -am "feat(dna-3d): drive canvas palette from theme"`

---

### Task 4: 노트식 레이아웃·패널·텍스트 정리

**Files:**
- Modify: `Main.dc.html` 마크업 10–212 전면 교체, script `constructor`·`setMode` 721–·`renderVals` 728–
- Create: `tests/dna_3d/layout.test.cjs`

**Interfaces:**
- Consumes: `th`, `themeLabel`, `toggleTheme`, `isDark` (Task 2); `pal()` (Task 3)
- Produces: `state.leftOpen`, `state.rightOpen`(초기값 = `!narrow`, narrow = `matchMedia('(max-width: 1023.98px)').matches`), `c.K.MISTAKES.{structure,replication}: Array<{title, text}>`(각 3개), renderVals 키 `leftCls`/`rightCls`(`'is-open'|''`), `leftExpanded`/`rightExpanded`(`'true'|'false'`), `scrimCls`(어느 쪽이든 열려 있으면 `'is-on'`), `toggleLeft`, `toggleRight`, `closePanels`, `mistakes`(현재 모드 배열), `hasStep: boolean`, `legend`(`{ parent, newDna, rna, ring }` = 현재 PAL 값, 범례 스와치용).

MISTAKES 제목(본문은 현재 카드 202–207의 문장 그대로):
- structure: `역평행 ≠ 오른나선`, `0.34 nm와 3.4 nm`, `새 뉴클레오타이드는 3′-OH에`
- replication: `지연가닥도 5′→3′`, `채우기 ≠ 잇기`, `원점은 자리, 분기점은 움직이는 경계`

마크업 골격(클래스·구멍 이름 고정, 나머지 스타일은 spec 3·4):

```
<div class="app" style="--bg: {{th.bg}}; --surface: {{th.surface}}; --ink: {{th.ink}}; --ink-2: {{th.ink2}}; --line: {{th.line}}; --accent: {{th.accent}}; --accent-ink: {{th.accentInk}}; --btn-bg: {{th.btnBg}}; --on-btn: {{th.onBtn}}; --warn: {{th.warn}}; …">
  <header class="topbar"> [패널 토글 aria-expanded="{{leftExpanded}}" "조작"] <strong class="brand">DNA 구조와 복제</strong> [① 구조 | ② 복제] [theme-toggle aria-label="{{themeLabel}}" 해/달 sc-if] [패널 토글 aria-expanded="{{rightExpanded}}" "설명"] </header>
  <div class="layout">
    <aside class="panel panel-left {{leftCls}}"> 패널 머리(제목 + "닫기" onClick={{closePanels}}) + 모드별 왼쪽 내용 </aside>
    <section class="stage"> canvas + 확대/축소/초기화 + hover 카드 + 재생 바 </section>
    <aside class="panel panel-right {{rightCls}}"> 모드별 오른쪽 내용 + 꼭 기억해요(sc-for mistakes) + 출처 한 줄 </aside>
  </div>
  <div class="scrim {{scrimCls}}" onClick="{{closePanels}}"></div>
</div>
```
`<helmet><style>`: `.app{height:100vh;display:grid;grid-template-rows:auto minmax(0,1fr);background:var(--bg);color:var(--ink);font-family:'Pretendard',system-ui,sans-serif}`, `.layout{display:grid;grid-template-columns:auto minmax(320px,1fr) auto;min-height:0}`, 넓은 화면 `.panel:not(.is-open){display:none}`, `@media (max-width: 1023.98px)`에서 `.panel` fixed drawer(왼쪽 `translateX(-100%)`, 오른쪽 `translateX(100%)`, `.is-open`이면 `none`), `.scrim`은 이 미디어 쿼리 안에서만 보이고 `.is-on`일 때 표시. 넓은 화면에서 `.scrim{display:none}`.

- [ ] **Step 1: 실패 테스트 작성** — `layout.test.cjs`:

```js
test('wide starts with both panels open', () => {
  const v = loadComponent({ narrow: false }).c.renderVals();
  assert.equal(v.leftCls, 'is-open'); assert.equal(v.rightCls, 'is-open'); assert.equal(v.leftExpanded, 'true'); });
test('narrow starts closed', () => {
  const { c } = loadComponent({ narrow: true }); const v = c.renderVals();
  assert.equal(v.leftCls, ''); assert.equal(v.rightCls, ''); assert.equal(v.scrimCls, '');
  v.toggleRight(); assert.equal(c.renderVals().scrimCls, 'is-on');
  c.renderVals().closePanels(); assert.equal(c.state.rightOpen, false); });
test('mode switch keeps panels, swaps mistakes', () => {
  const { c } = loadComponent({ narrow: false }); c.renderVals().toggleLeft();
  assert.deepEqual(c.renderVals().mistakes.map((m) => m.title), ['역평행 ≠ 오른나선', '0.34 nm와 3.4 nm', '새 뉴클레오타이드는 3′-OH에']);
  c.renderVals().toReplication();
  assert.equal(c.state.leftOpen, false); assert.equal(c.state.rightOpen, true);
  assert.equal(c.renderVals().mistakes[0].title, '지연가닥도 5′→3′'); });
test('stepDetail hidden until a step is picked', () => {
  const { c } = loadComponent(); c.setMode('replication'); assert.equal(c.renderVals().hasStep, false);
  c.renderVals().steps[2].pick(); assert.equal(c.renderVals().hasStep, true); });
test('removed copy is gone', () => {
  const m = markupPart();
  for (const s of ['1001 복습 · 5장 p1–2 · 3D 모형', '돌려 보며 이해하기', '끌어서 회전', '눌러서 그 장면으로', '이 20쌍 전체', '두 가닥은 마주 보고', '단계를 누르면 그 장면으로', '헷갈리기 쉬운 점 · 화면에서 직접 확인'])
    assert.equal(m.includes(s), false, s); });
test('note shell present, old dark hexes gone from markup', () => {
  const m = markupPart();
  for (const s of ['class="app"', 'class="topbar"', 'class="layout"', 'class="panel panel-left {{leftCls}}"', 'class="panel panel-right {{rightCls}}"', 'class="scrim {{scrimCls}}"', '@media (max-width: 1023.98px)', 'aria-label="{{themeLabel}}"', '--bg: {{th.bg}}', '--accent-ink: {{th.accentInk}}', '꼭 기억해요'])
    assert.ok(m.includes(s), s);
  for (const h of ['#0B0F14', '#121821', '#0F151D', '#1E2733', '#2A3443']) assert.equal(m.includes(h), false, h); });
```

- [ ] **Step 2: 실행해 실패 확인** — Run: `node --test tests/dna_3d/layout.test.cjs` → Expected: FAIL.
- [ ] **Step 3: 구현** — 위 골격으로 마크업 교체. 내용 배치는 spec "모드별 패널 내용" 표대로; 카드 박스 대신 `border-top: 1px solid var(--line)` 섹션, 섹션 제목 19px/700, "꼭 기억해요"는 `background: var(--surface)` + 제목 `color: var(--warn)`; 토글·단계 버튼 높이 48·`border: 1px solid var(--line)`·눌림 시 `var(--accent)` 테두리/`var(--accent-ink)` 글자(구멍 값은 renderVals에서 `'var(--accent)'` 등 문자열로); 모드 탭 선택 = `var(--btn-bg)`/`var(--on-btn)`; 해/달·패널 토글 SVG는 노트 `정리노트_1001…html:326-329` path 그대로; 범례 스와치 색은 `{{legend.*}}`. 제목 축약: "서열", "샤가프 규칙", "복제 6단계". 범례 설명은 1문장. 출처 한 줄(13px, `var(--ink-2)`)은 오른쪽 패널 맨 아래. 캔버스 `aria-label`은 유지, 좌상단 안내 div는 삭제.
- [ ] **Step 4: 실행** — Run: `node --test tests/dna_3d/` → Expected: 전부 PASS.
- [ ] **Step 5: 커밋** — `git commit -am "feat(dna-3d): note-style topbar, side panels, drawers, and trimmed copy"`

---

### Task 5: Pretendard 글꼴과 전체 화면 크기

**Files:**
- Modify: `Main.dc.html` `<helmet>`, script의 `ctx.font` 문자열(626, 670, 675), `data-props` `$preview`
- Modify: `복습노트/1001/DNA_3D/project/canvas.json` (`boards["Main.dc.html"].h`)
- Create: `tests/dna_3d/fonts.test.cjs`

**Interfaces:**
- Consumes: 업로드 결과의 `/_blob/<id>` url 4개
- Produces: 없음

- [ ] **Step 1: 실패 테스트 작성** — `fonts.test.cjs`:

```js
test('Pretendard faces from uploads, no IBM Plex or Google Fonts', () => {
  const h = readMain(); const faces = h.match(/@font-face\s*{[^}]*}/g) || [];
  assert.equal(faces.length, 4);
  for (const w of ['400', '600', '700', '800']) assert.ok(faces.some((f) => f.includes(`font-weight: ${w}`) && /url\('\/_blob\/[^']+'\)/.test(f) && f.includes("font-family: 'Pretendard'")), w);
  assert.equal(h.includes('IBM Plex'), false); assert.equal(h.includes('fonts.googleapis'), false); });
test('page is one screen tall', () => {
  const cj = JSON.parse(fs.readFileSync(CANVAS_JSON_PATH, 'utf8'));
  assert.equal(cj.boards['Main.dc.html'].h, 900); assert.equal(cj.boards['Main.dc.html'].expand, 'fill');
  assert.ok(readMain().includes('"$preview":{"width":1440,"height":900}')); });
```

- [ ] **Step 2: 실행해 실패 확인** — Run: `node --test tests/dna_3d/fonts.test.cjs` → Expected: FAIL.
- [ ] **Step 3: 글꼴 받기** — 스크래치패드의 빈 폴더 `fonts-dl/`에 받는다(프로젝트 밖):
  `https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/woff2/Pretendard-{Regular,SemiBold,Bold,ExtraBold}.woff2`
  Run: `file fonts-dl/*.woff2` → Expected: 4개 모두 `Web Open Font Format (Version 2)`.
- [ ] **Step 4: 업로드** — Artifact `publish`, `url` = 캔버스 URL, `asset: true`, `file_paths` = 4개 파일. 결과의 url 4개를 굵기에 맞춰 기록.
- [ ] **Step 5: 구현** — `<helmet><style>`에 `@font-face { font-family: 'Pretendard'; font-weight: <w>; font-style: normal; font-display: swap; src: url('<결과 url 그대로>') format('woff2'); }` 4개. Google Fonts `<link>` 두 줄 삭제. 캔버스 폰트: 염기 글자 `'700 ' + fs + 'px "Pretendard", system-ui, sans-serif'`, 라벨·닉 `'600 … "Pretendard", system-ui, sans-serif'`. 마크업의 숫자 표시는 `font-variant-numeric: tabular-nums`. `canvas.json` `h` → 900, `$preview` → `{"width":1440,"height":900}`.
- [ ] **Step 6: 실행** — Run: `node --test tests/dna_3d/` → Expected: 전부 PASS.
- [ ] **Step 7: 커밋** — `git commit -am "feat(dna-3d): use uploaded Pretendard and full-screen page size"`

---

### Task 6: 캔버스에 게시

**Files:** 없음(게시만)

- [ ] **Step 1: 게시** — Artifact `publish`: `url` = 캔버스 URL, `root` = `복습노트/1001/DNA_3D`(절대경로), `file_path` = `<root>/project/canvas.json`, `files` = `{"project/Main.dc.html": "project/Main.dc.html"}`. Expected: "Updated the Artifact … Version N".
- [ ] **Step 2: 확인(사용자가 요청할 때만)** — 1440px: 3열·페이지 스크롤 없음 / 390px: 첫 로드 시 패널 닫힘, "조작"·"설명"으로 drawer 열고 scrim으로 닫힘 / 해·달 전환 시 패널과 3D 배경·라벨이 함께 바뀜 / 복제 6단계 버튼이 이전과 같은 장면으로 이동. Design 타입 규칙상 사용자가 요청하지 않으면 렌더·스크린샷 검증은 하지 않는다.
