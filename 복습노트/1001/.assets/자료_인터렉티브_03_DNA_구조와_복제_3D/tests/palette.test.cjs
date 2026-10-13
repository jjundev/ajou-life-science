const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent, makeCtx } = require('./harness.cjs');

test('hbond dots use pal.hb', () => {
  for (const t of ['light', 'dark']) {
    const { c } = loadComponent();
    c.setTheme(t);
    const I = [];
    c.buildStructure(I, []);
    const dots = I.filter((it) => it.flat && it.r === 0.045);
    assert.ok(dots.length > 0);
    assert.ok(dots.every((d) => d.c === c.K.PAL[t].hb), t);
  }
});

test('light G darkened', () => {
  const { c } = loadComponent({ systemDark: false });
  const I = [];
  c.buildStructure(I, []);
  const rods = I.filter((it) => it.rod).map((it) => it.c);
  assert.ok(rods.includes('#D9A50F'));
  assert.ok(!rods.includes('#F6C945'));
});

test('replication parental uses pal.parent', () => {
  const { c } = loadComponent({ systemDark: false });
  c.state.mode = 'replication';
  c.sim.f = 30;
  const I = [];
  c.buildReplication(I, []);
  const cols = new Set(I.map((it) => it.c));
  assert.ok(cols.has('#8A94A3'));
  assert.ok(!cols.has('#AEB7C4'));
  assert.ok(cols.has('#1FA58A'));
});

test('dimension rulers use ink, not the old near-white', () => {
  const { c } = loadComponent({ systemDark: false });
  c.state.dims = true;
  const I = [], O = [];
  c.buildStructure(I, O);
  assert.ok(!I.some((it) => it.c === '#E6EBF2'));
  assert.ok(!O.some((o) => o.c === '#E6EBF2'));
});

test('draw paints flat pal.bg first', () => {
  for (const t of ['light', 'dark']) {
    const { c } = loadComponent();
    c.setTheme(t);
    const { ctx, calls } = makeCtx();
    c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 };
    c.ctx = ctx;
    c.draw(0.016, 0);
    const first = calls.find((k) => k.op === 'fillRect');
    assert.equal(first.fillStyle, c.K.PAL[t].bg);
    assert.equal(calls.some((k) => k.op === 'createRadialGradient' && k.args[2] === 0 && k.args[0] === 400), false);
  }
});

test('label text uses ink, pill uses labelBg', () => {
  const { c } = loadComponent({ systemDark: false });
  const { ctx, calls } = makeCtx();
  c.ctx = ctx;
  const V = { cx: 0, cy: 1, sy: 0, cp: 1, sp: 0, F: 300, D: 30, ox: 400, oy: 300 };
  c.drawOverlay({ t: 'label', p: [0, 0, 0], text: '부모 DNA', c: '#8A94A3' }, V, 0);
  assert.equal(calls.find((k) => k.op === 'fillText').fillStyle, '#111111');
  assert.equal(calls.find((k) => k.op === 'fill').fillStyle, '#f7f8fa');
});

test('nick ring uses pal.ring', () => {
  const { c } = loadComponent({ systemDark: false });
  const { ctx, calls } = makeCtx();
  c.ctx = ctx;
  const V = { cx: 0, cy: 1, sy: 0, cp: 1, sp: 0, F: 300, D: 30, ox: 400, oy: 300 };
  c.drawOverlay({ t: 'ring', p: [0, 0, 0], text: '닉' }, V, 0);
  assert.equal(calls.find((k) => k.op === 'stroke').strokeStyle, '#111111');
  assert.equal(calls.find((k) => k.op === 'fillText').fillStyle, '#111111');
});

test('theme switch keeps progress', () => {
  const { c } = loadComponent();
  c.sim.f = 27;
  c.state.f = 27;
  c.setTheme('dark');
  assert.equal(c.sim.f, 27);
  assert.equal(c.state.f, 27);
});
