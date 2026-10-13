const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent } = require('./harness.cjs');
const { snapshot } = require('./fixtures/replication-snapshot.cjs');
const FLAT = require('./fixtures/replication-flat.json');

const at = (f, tw = 1) => { const { c } = loadComponent({ systemDark: false }); c.state.mode = 'replication'; c.sim.f = f; c.sim.tw = tw; return c; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

test('twist off reproduces the current flat scene', () => {
  for (const f of Object.keys(FLAT)) assert.deepEqual(snapshot(at(Number(f), 0), Number(f)), FLAT[f], 'f=' + f);
});

test('deep leading daughter is helical', () => {
  const c = at(40);
  assert.equal(c.twistW(10, 1), 1);
  assert.ok(Math.abs(dist(c.dpos(10, 1, 0), c.armPos(10, 1, -0.78)) - 0.78) < 1e-9);
  const zs = [];
  for (let i = 10; i <= 19; i++) zs.push(c.dpos(i, 1, 0)[2]);
  assert.ok(Math.max(...zs) - Math.min(...zs) > 1.0);
});

test('fork end stays flat', () => {
  const c = at(40);
  for (const sg of [1, -1]) for (const i of [39, 40, 45]) assert.equal(c.twistW(i, sg), 0, sg + ':' + i);
  assert.ok(c.twistW(38, 1) < 0.3);
});

test('lagging single-strand gap stays flat', () => {
  const c = at(40);
  const gaps = [];
  for (let i = 28; i <= 38; i++) if (!c.lagState(i, 40)) gaps.push(i);
  assert.ok(gaps.length > 0);
  for (const i of gaps) assert.equal(c.twistW(i, -1), 0, 'i=' + i);
});

test('right-handed like the parent helix', () => {
  const c = at(50);
  const ang = (i) => { const p = c.dhelix(i, 1, 0), C = c.armPos(i, 1, -0.78); return Math.atan2(p[2] - C[2], p[1] - C[1]); };
  const d = ((ang(21) - ang(20)) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
  assert.ok(Math.abs(d - c.K.TW) < 1e-9);
});

test('backbone stays continuous while twisting', () => {
  const fs = loadComponent().c.K.STEPS.map((s) => s.f);
  for (let f = 0; f <= 60; f += 0.5) fs.push(f);
  for (const f of fs) {
    const c = at(f), lo = Math.max(0, Math.floor(f) - 34), hi = Math.floor(f) - 3;
    for (const sg of [1, -1]) for (const yoff of [0, -1.56]) for (let i = lo; i < hi; i++)
      assert.ok(dist(c.dpos(i, sg, yoff), c.dpos(i + 1, sg, yoff)) < 1.3, [f, sg, yoff, i].join(','));
  }
});

test('twist depends only on f', () => {
  const c = at(50);
  c.dpos(20, -1, 0);
  c.sim.f = 30;
  const fresh = at(30);
  for (let i = 0; i < 30; i++) assert.equal(c.twistW(i, -1), fresh.twistW(i, -1));
});

const { makeCtx, markupPart } = require('./harness.cjs');

test('3D view starts on', () => {
  const { c } = loadComponent();
  assert.equal(c.state.view3d, true);
  assert.equal(c.sim.tw, 1);
  assert.equal(c.renderVals().view3dPressed, 'true');
});

test('toggle eases to flat in 0.4 s', () => {
  const { c } = loadComponent();
  c.renderVals().toggle3d();
  assert.equal(c.state.view3d, false);
  const seen = [];
  for (let k = 0; k < 4; k++) { c.easeTwist(0.1); seen.push(c.sim.tw); }
  for (let k = 1; k < 4; k++) assert.ok(seen[k] < seen[k - 1]);
  assert.ok(seen[2] > 0);
  assert.equal(seen[3], 0);
  c.renderVals().toggle3d();
  c.easeTwist(1);
  assert.equal(c.sim.tw, 1);
});

test('reduced motion snaps', () => {
  const { c } = loadComponent({ reduceMotion: true });
  c.renderVals().toggle3d();
  c.easeTwist(0.016);
  assert.equal(c.sim.tw, 0);
});

test('tick eases twist while paused', () => {
  const { c } = loadComponent();
  c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 };
  c.ctx = makeCtx().ctx;
  c.setMode('replication');
  c.renderVals().toggle3d();
  c.tick(1000); c.tick(1100);
  assert.equal(c.state.playing, false);
  assert.ok(c.sim.tw < 1);
});

test('mode switch keeps 3D state', () => {
  const { c } = loadComponent();
  c.renderVals().toggle3d();
  c.setMode('replication'); c.setMode('structure'); c.setMode('replication');
  assert.equal(c.state.view3d, false);
});

test('3D button leads the view buttons, replication only', () => {
  const m = markupPart();
  const box = m.indexOf('<div class="view-btns">'), btn = m.indexOf('onClick="{{toggle3d}}"'), zoom = m.indexOf('aria-label="확대"');
  assert.ok(box > 0 && box < btn && btn < zoom);
  const ifAt = m.lastIndexOf('<sc-if value="{{isReplication}}"', btn);
  assert.ok(ifAt > box);
  for (const s of ['aria-pressed="{{view3dPressed}}"', 'aria-label="3D 입체로 보기"', '>3D</button>', '.icon-btn[aria-pressed="true"]'])
    assert.ok(m.includes(s), s);
});

test('enzymes are shaded spheres only in 3D', () => {
  const grads = (tw) => {
    const { c } = loadComponent({ systemDark: false });
    const { ctx, calls } = makeCtx();
    c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 };
    c.ctx = ctx;
    c.setMode('replication');
    c.sim.f = 10; c.sim.tw = tw;
    c.draw(0.016, 0);
    return calls.filter((k) => k.op === 'createRadialGradient');
  };
  const concentric = (k) => k.args[0] === k.args[3] && k.args[1] === k.args[4];
  assert.ok(grads(0).some(concentric));
  assert.equal(grads(1).some(concentric), false);
});

test('wound atoms move smoothly during playback', () => {
  const c = at(0);
  const pts = (f, lo, hi) => {
    c.sim.f = f;
    const out = [];
    for (let i = lo; i <= hi; i++) for (const sg of [1, -1]) for (const yoff of [0, -1.56]) out.push(c.dpos(i, sg, yoff), c.dpos(i + 0.5, sg, yoff - 0.2));
    return out;
  };
  for (let f = 0; f < 60; f = Math.round((f + 0.025) * 1000) / 1000) {
    const lo = Math.max(0, Math.floor(f) - 34), hi = Math.ceil(f) + 1;
    const a = pts(f, lo, hi), b = pts(f + 0.025, lo, hi);
    for (let k = 0; k < a.length; k++) assert.ok(dist(a[k], b[k]) < 0.15, 'f=' + f + ' k=' + k);
  }
});

test('lagging pairing ramp starts exactly when lagState fills', () => {
  const c = at(0);
  for (let j = 0; j < 60; j++) for (let f = 0; f <= 60; f = Math.round((f + 0.01) * 100) / 100)
    assert.equal(f >= c.lagOn(j), !!c.lagState(j, f), j + '@' + f);
});

test('strand-name labels keep apart in 3D', () => {
  for (let f = 10; f <= 60; f += 0.5) {
    const c = at(f), I = [], O = [];
    c.buildReplication(I, O);
    const y = (t) => O.find((o) => o.text === t).p[1];
    assert.ok(y('옛 가닥 (주형)') - y('선도가닥 · 연속') > 1.5, 'f=' + f);
  }
});
