const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent } = require('./harness.cjs');

const setNarrow = (win, narrow) => {
  const prev = win.matchMedia;
  win.matchMedia = (q) => (q.includes('max-width: 1023.98px') ? { matches: narrow } : prev(q));
};

test('crossing the breakpoint keeps docked panels and drops drawers', () => {
  const { c, win } = loadComponent({ narrow: false });
  setNarrow(win, true);
  c.syncBreakpoint();
  let v = c.renderVals();
  assert.equal(v.leftCls, ''); assert.equal(v.rightCls, ''); assert.equal(v.scrimCls, '');
  v.toggleRight();
  v = c.renderVals();
  assert.equal(v.rightCls, 'is-open'); assert.equal(v.scrimCls, 'is-on');
  v.toggleLeft();
  v = c.renderVals();
  assert.equal(v.leftCls, 'is-open'); assert.equal(v.rightCls, '', 'one drawer at a time');
  setNarrow(win, false);
  c.syncBreakpoint();
  v = c.renderVals();
  assert.equal(v.leftCls, 'is-open'); assert.equal(v.rightCls, 'is-open'); assert.equal(v.scrimCls, '');
});

test('narrow first load, then widening shows docked panels', () => {
  const { c, win } = loadComponent({ narrow: true });
  setNarrow(win, false);
  c.syncBreakpoint();
  const v = c.renderVals();
  assert.equal(v.leftCls, 'is-open'); assert.equal(v.rightCls, 'is-open');
});

const lum = (col) => {
  const m = col.startsWith('#') ? [1, 3, 5].map((i) => parseInt(col.slice(i, i + 2), 16)) : col.match(/\d+/g).slice(0, 3).map(Number);
  const [r, g, b] = m.map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

test('light panel text colors reach 4.5:1 on surface', () => {
  const { c } = loadComponent({ systemDark: false });
  c.state.hover = 3;
  const v = c.renderVals();
  const texts = [
    ...[...v.seqTop, ...v.seqBot].filter((b, i) => i % 20 !== 3).map((b) => b.fg),
    ...[...v.chargaff].map((r) => r.tc),
    v.strand.c1, v.strand.c2, v.hoverInfo.c1, v.hoverInfo.c2, v.statColor.done, v.statColor.rna,
  ];
  for (const t of texts) assert.ok(contrast(t, '#f7f8fa') >= 4.5, t + ' ' + contrast(t, '#f7f8fa').toFixed(2));
});

test('dark panel text keeps the bright base colors', () => {
  const { c } = loadComponent({ systemDark: true });
  const v = c.renderVals();
  assert.equal(v.seqTop[0].fg, c.K.BASE[c.K.SEQ[0]]);
});

test('step copy does not promise a white ring', () => {
  const { c } = loadComponent();
  assert.ok([...c.K.STEPS].every((s) => !s.text.includes('흰')));
});

test('light structure direction arrows reach 3:1 on white', () => {
  const { c } = loadComponent({ systemDark: false });
  const I = [];
  c.buildStructure(I, []);
  const arrows = I.filter((it) => it.k === 4);
  assert.ok(arrows.length > 0);
  for (const a of arrows) assert.ok(contrast(a.c, '#ffffff') >= 3, a.c);
});
