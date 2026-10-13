const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { loadComponent, makeCtx, makeCanvas, markupPart } = require('../scripts/harness.cjs');

const T = path.join(__dirname, '..', 'assets', 'template.dc.html');

function drawFrames(c, n, w, h) {
  const { ctx, calls } = makeCtx();
  c.attachCanvas(makeCanvas(ctx, w, h));
  for (let k = 1; k <= n; k++) c.draw(0.016, k * 16);
  return calls;
}

test('modes render as buttons and switch', () => {
  const { c } = loadComponent(T);
  let v = c.renderVals();
  assert.deepEqual(v.modes.map((m) => m.label), ['구조', '과정']);
  assert.equal(v.hasPlayback, false);
  v.modes[1].pick();
  v = c.renderVals();
  assert.equal(c.state.mode, 'b');
  assert.equal(v.modes[1].pressed, 'true');
  assert.equal(v.modes[0].pressed, 'false');
  assert.equal(v.hasPlayback, true);
});

test('wide opens both panels; narrow starts closed and Escape closes the drawer', () => {
  const wide = loadComponent(T, { narrow: false }).c.renderVals();
  assert.equal(wide.leftCls, 'is-open');
  assert.equal(wide.rightCls, 'is-open');
  const { c } = loadComponent(T, { narrow: true });
  let v = c.renderVals();
  assert.equal(v.leftCls, '');
  assert.equal(v.rightCls, '');
  v.toggleRight();
  v = c.renderVals();
  assert.equal(v.rightCls, 'is-open');
  assert.equal(v.scrimCls, 'is-on');
  v.onKey({ key: 'Escape' });
  assert.equal(c.renderVals().scrimCls, '');
});

test('theme is saved to od-theme', () => {
  const { c, store } = loadComponent(T);
  c.setTheme('dark');
  assert.equal(store['od-theme'], 'dark');
  assert.equal(c.renderVals().isDark, true);
});

test('blocked storage still loads', () => {
  assert.doesNotThrow(() => {
    const { c } = loadComponent(T, { storage: 'throw' });
    c.renderVals();
    c.setTheme('dark');
  });
});

test('reduced motion turns auto spin off', () => {
  assert.equal(loadComponent(T, { reduceMotion: true }).c.state.spin, false);
  assert.equal(loadComponent(T).c.state.spin, true);
});

test('draw paints every mode', () => {
  const { c } = loadComponent(T);
  for (const m of c.topic().MODES) {
    c.setMode(m.key);
    const calls = drawFrames(c, 10);
    assert.ok(calls.some((x) => x.op === 'arc'), m.key);
  }
});

test('zero-size canvas draws nothing and does not throw', () => {
  const { c } = loadComponent(T);
  let calls;
  assert.doesNotThrow(() => { calls = drawFrames(c, 3, 0, 0); });
  assert.equal(calls.some((x) => x.op === 'arc'), false);
});

test('playback advances to fmax and stops', () => {
  const { c } = loadComponent(T);
  c.setMode('b');
  const { ctx } = makeCtx();
  c.attachCanvas(makeCanvas(ctx));
  c.setState({ playing: true });
  for (let k = 1; k <= 2000; k++) c.tick(16 * k);
  assert.equal(c.state.f, 10);
  assert.equal(c.state.playing, false);
});

test('non-rotatable mode ignores drag', () => {
  const { c } = loadComponent(T);
  c.setMode('b');
  const { ctx } = makeCtx();
  c.attachCanvas(makeCanvas(ctx));
  const before = { yaw: c.cam.yaw, pitch: c.cam.pitch };
  c._pd({ clientX: 0, clientY: 0, pointerId: 1 });
  c._pm({ clientX: 100, clientY: 50 });
  assert.deepEqual({ yaw: c.cam.yaw, pitch: c.cam.pitch }, before);
  c.setMode('a');
  c._pd({ clientX: 0, clientY: 0, pointerId: 1 });
  c._pm({ clientX: 100, clientY: 50 });
  assert.notEqual(c.cam.yaw, c.topic().MODES[0].cam.yaw);
});

test('scrub and step pick move f', () => {
  const { c } = loadComponent(T);
  c.setMode('b');
  c.renderVals().onScrub({ target: { value: '50' } });
  assert.equal(c.state.f, 5);
  c.setMode('a');
  c.setState({ playing: true });
  const S = c.topic().STEPS[1];
  c.renderVals().steps[1].pick();
  assert.equal(c.state.mode, S.mode);
  assert.equal(c.state.f, S.f);
  assert.equal(c.state.playing, false);
  const v = c.renderVals();
  assert.equal(v.steps[1].pressed, 'true');
  assert.equal(v.stepDetail, S.text);
});

test('placeholders and slots are present', () => {
  const m = markupPart(T);
  assert.equal(m.split('__TITLE__').length - 1, 2);
  for (const s of ['<!-- SLOT:left -->', '<!-- SLOT:right -->']) assert.ok(m.includes(s), s);
  assert.equal(m.includes('@font-face'), false);
});

test('first section in each panel has no divider', () => {
  // A slot often wraps its sections in a bare <div>; that first section counts too.
  const rule = markupPart(T).match(/\.panel-head \+ \.sec,\.panel-head \+ div > \.sec:first-child\{([^}]*)\}/);
  assert.ok(rule, '.panel-head + .sec and wrapped first .sec rule');
  assert.ok(rule[1].includes('border-top:0'), rule[1]);
});

test('template has no source line', () => {
  const m = markupPart(T);
  assert.equal(m.includes('class="source"'), false);
  assert.equal(m.includes('__SOURCE__'), false);
});

test('flat scene is not fogged', () => {
  const { c } = loadComponent(T);
  c.setMode('b');
  c.renderVals().onScrub({ target: { value: '50' } });
  const calls = drawFrames(c, 1);
  const arcs = calls.filter((x) => x.op === 'arc');
  assert.ok(Math.max(...arcs.map((x) => x.alpha)) > 0.99);
});

test('a scene error is logged once, not swallowed', (t) => {
  const fs = require('node:fs'), os = require('node:os');
  const src = fs.readFileSync(T, 'utf8').replace(/buildScene\(mode, I, O\) \{/, '$& throw new Error("boom");');
  const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'bi-tpl-')), 'x.dc.html');
  fs.writeFileSync(f, src);
  const { c } = loadComponent(f);
  const { ctx } = makeCtx();
  c.attachCanvas(makeCanvas(ctx));
  const err = t.mock.method(console, 'error', () => {});
  for (let k = 1; k <= 3; k++) c.tick(16 * k);
  assert.equal(err.mock.callCount(), 1);
});

test('picking the active mode keeps progress', () => {
  const { c } = loadComponent(T);
  c.setMode('b');
  c.renderVals().onScrub({ target: { value: '50' } });
  c.renderVals().modes[1].pick();
  assert.equal(c.state.f, 5);
  c.renderVals().modes[0].pick();
  assert.equal(c.state.mode, 'a');
  assert.equal(c.state.f, 0);
});
