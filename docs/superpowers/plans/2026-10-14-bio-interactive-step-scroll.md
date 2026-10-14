# Bio-interactive Step Scroll Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 왼쪽 「단계」 버튼을 누르면 왼쪽 패널이 자동으로 내려가 목록 아래 설명 상자가 보이게 하고, 스킬 템플릿과 기존 인터렉티브 43개에 모두 적용한다.

**Architecture:** 템플릿 `pickStep(i)`이 상태를 바꾼 뒤 `revealStepDetail()`을 부른다. 이 메서드는 다음 프레임(런타임이 microtask로 다시 그린 뒤)에 `.panel-left .panel-inner` 안의 `.detail`·눌린 버튼 위치를 재서 패널만 `scrollBy`한다. 기존 자료는 다시 빌드하지 않고 원본 `Main.dc.html`과 빌드된 `인터렉티브_*.html`에 같은 문자열 치환을 일회용 스크립트로 적용한다.

**Tech Stack:** Node.js >=20, CommonJS, node:test, vm 기반 `scripts/harness.cjs`, 브라우저 DOM API(`getBoundingClientRect`, `scrollBy`, `matchMedia`).

**Spec:** `docs/superpowers/specs/2026-10-14-bio-interactive-step-scroll-design.md`

## Global Constraints

- 스크롤 대상은 `.panel-left .panel-inner`뿐. `scrollIntoView` 금지(페이지까지 움직임).
- 여백 16px. 설명 하단이 보이도록 내리되, 눌린 버튼 상단이 패널 상단 여백 위로 올라가지 않는 만큼까지만.
- 이미 보이면 스크롤하지 않음. `prefers-reduced-motion: reduce`면 `behavior: 'auto'`, 아니면 `'smooth'`.
- `document`가 없는 환경(harness, check.cjs, steps.cjs)에서는 아무것도 하지 않음.
- 기존 자료: 재빌드 금지, 원본·빌드본 동일 치환, 파일마다 정확히 1회 매칭 아니면 건너뛰고 보고. 재실행은 변경 없음.
- `references/example-dna.dc.html`, 정리노트·MD·PDF는 수정하지 않음.
- 커밋·푸시는 실행하지 않음(사용자 요청 시에만). 각 Task 끝에서 `git status --short`로 변경 범위만 확인.

## Review Focus

- 다른 모드의 단계를 누름(모드 전환 + 단계 선택이 한 번에 일어남) → 스크롤은 한 번만 예약되고 새 목록 기준으로 계산되어야 함. Task 1에 테스트 추가.
- 375px 서랍에서 단계 누름 → 서랍의 같은 `.panel-inner`가 내려가고 페이지는 가로·세로로 움직이지 않아야 함. Task 2 브라우저 확인 항목.
- 빠르게 여러 단계를 연달아 누름 → 마지막으로 누른 단계의 설명이 보이는 위치에서 멈춰야 함(앞선 smooth 스크롤과 겹쳐 지나치지 않음). Task 2 브라우저 확인 항목.
- CRLF 줄바꿈 또는 NFD 파일명인 기존 자료 → 치환 스크립트가 줄바꿈을 보존하고 파일을 놓치지 않아야 함. Task 2 스크립트가 줄바꿈 감지·`normalize('NFC')`로 처리, dry-run 개수 86으로 확인.
- 이미 아래로 스크롤된 상태에서 위쪽 단계를 다시 누름(설명이 이미 보임) → 움직이지 않아야 함. Task 1 「visible step text does not scroll」 테스트.

---

### Task 1: 템플릿에 자동 스크롤 추가 + 테스트 + 스킬 문서

**Files:**
- Modify: `.agents/skills/bio-interactive/scripts/harness.cjs:27-49` (`loadComponent`에 `opts.document`, `opts.raf`)
- Modify: `.agents/skills/bio-interactive/assets/template.dc.html:705-711` (`pickStep` + 새 메서드)
- Modify: `.agents/skills/bio-interactive/references/scene-api.md:97`
- Modify: `.agents/skills/bio-interactive/SKILL.md:93` (6단계 「단계 누르기」 다음 줄)
- Test: `.agents/skills/bio-interactive/tests/template.test.cjs`, `.agents/skills/bio-interactive/tests/skill.test.cjs`

**Interfaces:**
- Consumes: 없음
- Produces: 컴포넌트 메서드 `revealStepDetail(): void` (인자 없음, 반환 없음). 정확히 이 문자열의 메서드 블록을 Task 2가 기존 자료에 붙여 넣는다(아래 Step 3의 코드 그대로).
- Produces: `loadComponent(file, { document?, raf? })` — `document`를 주면 sandbox 전역 `document`로, `raf`를 주면 `requestAnimationFrame`으로 쓴다.

- [ ] **Step 1: harness에 DOM 주입 옵션 추가**

먼저 기준선을 저장한다: `node .agents/skills/bio-interactive/scripts/check.cjs .agents/skills/bio-interactive/assets/template.dc.html > .scratch/tpl-check-before.txt`

`harness.cjs`의 `const ctx = vm.createContext(...)` 한 줄을 다음으로 바꾼다.

```js
  const globals = { DCLogic, window: win, requestAnimationFrame: opts.raf || (() => 0), cancelAnimationFrame() {}, console };
  if (opts.document) globals.document = opts.document;
  const ctx = vm.createContext(globals);
```

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/template.test.cjs` 맨 끝에 추가한다(sandbox에서 만든 객체라 `deepStrictEqual` 대신 필드별 비교).

```js
// Left-panel DOM stub: rects are { top, bottom }; detail/btn null means "not rendered".
function fakeDom({ box, detail, btn }) {
  const scrolls = [];
  const el = (r) => r && { getBoundingClientRect: () => r };
  const inner = {
    getBoundingClientRect: () => box,
    querySelector: (q) => (q === '.detail' ? el(detail) : q === '.steps [aria-pressed="true"]' ? el(btn) : null),
    scrollBy: (o) => scrolls.push({ top: o.top, behavior: o.behavior }),
  };
  return { document: { querySelector: (q) => (q === '.panel-left .panel-inner' ? inner : null) }, scrolls };
}
const runNow = (fn) => { fn(); return 1; };

test('picking a step scrolls the left panel to show its text', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: { top: 620, bottom: 760 }, btn: { top: 400, bottom: 460 } });
  const { c } = loadComponent(T, { document: dom.document, raf: runNow });
  c.pickStep(0);
  assert.equal(dom.scrolls.length, 1);
  assert.equal(dom.scrolls[0].top, 176);
  assert.equal(dom.scrolls[0].behavior, 'smooth');
});

test('visible step text does not scroll', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: { top: 300, bottom: 500 }, btn: { top: 100, bottom: 160 } });
  const { c } = loadComponent(T, { document: dom.document, raf: runNow });
  c.pickStep(0);
  assert.equal(dom.scrolls.length, 0);
});

test('long step text keeps the pressed button in view', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: { top: 620, bottom: 1400 }, btn: { top: 300, bottom: 360 } });
  const { c } = loadComponent(T, { document: dom.document, raf: runNow });
  c.pickStep(0);
  assert.equal(dom.scrolls.length, 1);
  assert.equal(dom.scrolls[0].top, 284);
});

test('reduced motion scrolls instantly', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: { top: 620, bottom: 760 }, btn: { top: 400, bottom: 460 } });
  const { c } = loadComponent(T, { document: dom.document, raf: runNow, reduceMotion: true });
  c.pickStep(0);
  assert.equal(dom.scrolls[0].behavior, 'auto');
});

test('no rendered step text means no scroll', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: null, btn: null });
  const { c } = loadComponent(T, { document: dom.document, raf: runNow });
  c.pickStep(0);
  assert.equal(dom.scrolls.length, 0);
});

test('picking a step in another mode schedules one scroll', () => {
  const dom = fakeDom({ box: { top: 0, bottom: 600 }, detail: { top: 620, bottom: 760 }, btn: { top: 400, bottom: 460 } });
  let frames = 0;
  const { c } = loadComponent(withSteps(MIXED), { document: dom.document, raf: (fn) => { frames++; fn(); return 1; } });
  c.setMode('a');
  c.pickStep(1);
  assert.equal(c.state.mode, 'b');
  assert.equal(frames, 1);
  assert.equal(dom.scrolls.length, 1);
});

test('without a DOM pickStep schedules nothing', () => {
  let frames = 0;
  const { c } = loadComponent(T, { raf: () => { frames++; return 1; } });
  c.pickStep(0);
  assert.equal(frames, 0);
  assert.equal(c.state.step, 0);
});
```

`tests/skill.test.cjs` 맨 끝에 추가한다.

```js
test('step scroll is documented', () => {
  assert.ok(read('references/scene-api.md').includes('revealStepDetail'));
  assert.ok(read('SKILL.md').includes('설명 상자가 패널 안에 보이고'));
});
```

- [ ] **Step 3: 테스트가 실패하는지 확인**

Run: `node --test .agents/skills/bio-interactive/tests/`
Expected: FAIL — `picking a step scrolls…`(scrolls.length 0), `long step text…`, `reduced motion…`(`dom.scrolls[0]` undefined), `another mode…`(frames 0), `step scroll is documented`. 나머지 기존 테스트와 `visible…`, `no rendered…`, `without a DOM…`는 PASS.

- [ ] **Step 4: 템플릿 구현**

`assets/template.dc.html`의 `pickStep`을 다음으로 바꾼다(첫 줄부터 두 번째 메서드 끝까지 그대로; Task 2가 이 메서드 블록을 복사해 쓴다).

```js
  pickStep(i) {
    const s = (this.T.STEPS || [])[i];
    if (!s) return;
    if (s.mode !== this.state.mode) this.setMode(s.mode);
    if (s.f != null) this.sim.f = s.f;
    this.setState({ f: this.sim.f, playing: false, step: i });
    this.revealStepDetail();
  }

  // Scroll the left panel so the step text under the list shows, keeping the pressed button in view.
  revealStepDetail() {
    if (typeof document === 'undefined') return;
    requestAnimationFrame(() => {
      const box = document.querySelector('.panel-left .panel-inner'), d = box && box.querySelector('.detail');
      if (!d) return;
      const pad = 16, b = box.getBoundingClientRect();
      let dy = d.getBoundingClientRect().bottom + pad - b.bottom;
      const btn = box.querySelector('.steps [aria-pressed="true"]');
      if (btn) dy = Math.min(dy, btn.getBoundingClientRect().top - pad - b.top);
      if (dy <= 0) return;
      const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      box.scrollBy({ top: dy, behavior: reduce ? 'auto' : 'smooth' });
    });
  }
```

- [ ] **Step 5: 스킬 문서 수정**

`references/scene-api.md:97` 문장 끝 `필요하면 모드를 바꾸고 \`f\`로 옮겨요.` 뒤에 이어서 쓴다:

```
고른 뒤 다음 프레임에 왼쪽 패널을 설명 상자가 보이게 스크롤해요(`revealStepDetail()`, 눌린 버튼이 위로 사라지지 않을 만큼만, reduced-motion이면 즉시). 이 셸 메서드는 고치지 않아요.
```

`SKILL.md:93` 「단계 누르기」 줄 바로 다음에 새 항목을 넣는다:

```
- 마지막 단계를 눌렀을 때 설명 상자가 패널 안에 보이고 누른 버튼도 남아 있는지(1440×900 고정 패널, 375×812 서랍 모두)
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `node --test .agents/skills/bio-interactive/tests/`
Expected: 모두 PASS.

Run: `node .agents/skills/bio-interactive/scripts/check.cjs .agents/skills/bio-interactive/assets/template.dc.html`
Expected: `.scratch/tpl-check-before.txt`와 같은 결과(템플릿은 `TEMPLATE_LEFT` 같은 템플릿 고유 항목이 나올 수 있다. 새 오류만 늘지 않으면 된다).

- [ ] **Step 7: 변경 범위 확인**

Run: `git status --short .agents/skills/bio-interactive`
Expected: `harness.cjs`, `template.dc.html`, `scene-api.md`, `SKILL.md`, `template.test.cjs`, `skill.test.cjs`만 수정.

---

### Task 2: 기존 인터렉티브 43개에 적용 + 확인

**Files:**
- Create: `.scratch/patch-step-scroll.cjs` (일회용, 커밋 대상 아님)
- Modify: `복습노트/**/.assets/자료_인터렉티브_*/**/Main.dc.html` 43개
- Modify: `복습노트/**/인터렉티브_*.html` 43개

**Interfaces:**
- Consumes: Task 1 Step 4의 `revealStepDetail()` 메서드 블록(아래 `METHOD`에 같은 코드).
- Produces: 없음

- [ ] **Step 1: 예전 형식 파일의 check 기준선 기록**

Run: `node .agents/skills/bio-interactive/scripts/check.cjs "복습노트/1001/.assets/자료_인터렉티브_03_DNA_구조와_복제_3D/canvas/Main.dc.html" > .scratch/dna-check-before.txt; cat .scratch/dna-check-before.txt`
Expected: 결과 저장(예전 형식이라 `ok`가 아닐 수 있음 — Step 5에서 같은지 비교).

- [ ] **Step 2: 치환 스크립트 작성**

`.scratch/patch-step-scroll.cjs`:

```js
// One-off: add revealStepDetail() to existing interactives (sources and built pages).
// Usage: node .scratch/patch-step-scroll.cjs <복습노트 dir> [--dry-run]
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(process.argv[2]);
const dry = process.argv.includes('--dry-run');
const METHOD = [
  '  // Scroll the left panel so the step text under the list shows, keeping the pressed button in view.',
  '  revealStepDetail() {',
  "    if (typeof document === 'undefined') return;",
  '    requestAnimationFrame(() => {',
  "      const box = document.querySelector('.panel-left .panel-inner'), d = box && box.querySelector('.detail');",
  '      if (!d) return;',
  '      const pad = 16, b = box.getBoundingClientRect();',
  '      let dy = d.getBoundingClientRect().bottom + pad - b.bottom;',
  "      const btn = box.querySelector('.steps [aria-pressed=\"true\"]');",
  '      if (btn) dy = Math.min(dy, btn.getBoundingClientRect().top - pad - b.top);',
  '      if (dy <= 0) return;',
  "      const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;",
  "      box.scrollBy({ top: dy, behavior: reduce ? 'auto' : 'smooth' });",
  '    });',
  '  }',
];
const count = (s, x) => s.split(x).length - 1;

function patch(src) {
  if (src.includes('revealStepDetail(')) return { status: 'already' };
  const eol = src.includes('\r\n') ? '\r\n' : '\n';
  const method = METHOD.join(eol);
  // Template format: pickStep(i) ends with this setState.
  const A = '    this.setState({ f: this.sim.f, playing: false, step: i });' + eol + '  }';
  if (src.includes('  pickStep(i) {') && count(src, A) === 1) {
    const B = '    this.setState({ f: this.sim.f, playing: false, step: i });' + eol + '    this.revealStepDetail();' + eol + '  }' + eol + eol + method;
    return { status: 'template', out: src.replace(A, () => B) };
  }
  // Old format (1001 DNA 3D): steps pick inline, no pickStep.
  const P = 'pick: () => { this.sim.f = s.f; this.setState({ f: s.f, playing: false, step: i }); }';
  const R = eol + '  renderVals() {';
  if (count(src, P) === 1 && count(src, R) === 1) {
    const out = src
      .replace(P, () => 'pick: () => { this.sim.f = s.f; this.setState({ f: s.f, playing: false, step: i }); this.revealStepDetail(); }')
      .replace(R, () => eol + method + eol + R);
    return { status: 'old', out };
  }
  return { status: 'skipped' };
}

const files = fs.readdirSync(ROOT, { recursive: true }).map(String).filter((rel) => {
  const n = rel.normalize('NFC').split(path.sep).join('/'), b = path.posix.basename(n);
  return (b.startsWith('인터렉티브_') && b.endsWith('.html')) || (b === 'Main.dc.html' && n.includes('자료_인터렉티브_'));
}).map((rel) => path.join(ROOT, rel));

const tally = {};
let bad = 0;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8');
  const r = patch(src);
  tally[r.status] = (tally[r.status] || 0) + 1;
  if (r.status === 'skipped') { bad++; console.log('SKIPPED ' + path.relative(ROOT, f)); }
  if (r.out && !dry) fs.writeFileSync(f, r.out);
  if (r.out && count(r.out, 'revealStepDetail') !== 2) { bad++; console.log('BADCOUNT ' + path.relative(ROOT, f)); }
}
console.log(JSON.stringify({ files: files.length, dry, tally }));
process.exit(bad ? 1 : 0);
```

주의: `1001/.assets/자료_인터렉티브_03_DNA_구조와_복제_3D/standalone/` 같은 하위 폴더의 다른 파일은 이름 조건에 맞지 않아 대상이 아니다. `Main.dc.html`이 `canvas/` 아래에 있어도 경로에 `자료_인터렉티브_`가 있어 대상이다.

- [ ] **Step 3: dry-run**

Run: `node .scratch/patch-step-scroll.cjs 복습노트 --dry-run`
Expected: `{"files":86,"dry":true,"tally":{"template":84,"old":2}}`, exit 0, `SKIPPED`/`BADCOUNT` 줄 없음. 다르면 해당 파일을 열어 원인을 보고 하고 멈춘다(임의로 패턴을 넓히지 않는다).

- [ ] **Step 4: 적용 및 재실행 확인**

Run: `node .scratch/patch-step-scroll.cjs 복습노트`
Expected: `{"files":86,"dry":false,"tally":{"template":84,"old":2}}`

Run: `node .scratch/patch-step-scroll.cjs 복습노트 --dry-run`
Expected: `{"files":86,"dry":true,"tally":{"already":86}}`

Run: `git diff --stat -- 복습노트 | tail -1`
Expected: `86 files changed`, 각 파일 +17줄 안팎(템플릿 형식 +17, 예전 형식 +16, 삭제 0~1).

- [ ] **Step 5: check.cjs**

Run:
```bash
for f in $(find 복습노트 -name Main.dc.html -path "*자료_인터렉티브_*"); do echo "== $f"; node .agents/skills/bio-interactive/scripts/check.cjs "$f"; done
```
Expected: 템플릿 형식 42개 모두 `ok`. DNA 3D는 `diff <(node .agents/skills/bio-interactive/scripts/check.cjs "복습노트/1001/.assets/자료_인터렉티브_03_DNA_구조와_복제_3D/canvas/Main.dc.html") .scratch/dna-check-before.txt`가 출력 없음.

- [ ] **Step 6: 브라우저 확인**

`복습노트`를 `python -m http.server 8765 --directory 복습노트`로 띄우고 내장 브라우저로 다음 3개를 연다.
- `0917/인터렉티브_02_세포주기와_확인점.html`
- `0929/인터렉티브_03_염색체_구조_변화.html` (`.detail`에 aria-live 없음)
- `1001/인터렉티브_03_DNA_구조와_복제_3D.html` (예전 형식)

각각 1440×900과 375×812(왼쪽 서랍 열고)에서:
- 마지막 단계를 누르면 왼쪽 패널이 내려가 설명 상자 하단이 보이고 누른 버튼도 보임
- 이미 설명이 보이는 상태에서 위 단계를 누르면 움직이지 않음
- 단계 3개를 빠르게 연달아 누르면 마지막 단계 설명이 보이는 위치에서 멈춤
- `document.scrollingElement.scrollTop`과 `scrollLeft`가 0 그대로(페이지 자체는 안 움직임)
- 콘솔 오류 0

확인 후 서버를 끄고 viewport를 desktop으로 되돌린다.

- [ ] **Step 7: 변경 범위 확인**

Run: `git status --short`
Expected: Task 1 파일 6개 + `복습노트/**` 86개 + 새 spec·plan 문서 외 변경 없음(`.scratch/`는 이미 미추적). 정리노트·MD·PDF 변경 없음: `git status --short | grep -E '정리노트|\.md$|\.pdf$' | grep -vE 'docs/superpowers|\.agents/skills/bio-interactive'`가 출력 없음.
