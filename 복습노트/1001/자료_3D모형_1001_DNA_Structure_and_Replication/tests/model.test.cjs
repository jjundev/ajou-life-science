const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent } = require('./harness.cjs');

test('lagging fragment 1 replaces fragment 0 primer then seals', () => {
  const { c } = loadComponent();
  assert.deepEqual({ ...c.lagState(9, 26.0) }, { kind: 'rna', owner: 0 });
  assert.equal(c.lagState(9, 26.3).owner, 1);
  assert.equal(c.isNick(6, 28.0), true);
  assert.equal(c.lagBond(6, 28.9), true);
});

test('steps jump targets unchanged', () => {
  const { c } = loadComponent();
  assert.deepEqual([...c.K.STEPS].map((s) => s.f), [5, 11.8, 17, 23.5, 26.9, 28.3]);
});

test('events at f=26.9 mention DNA 중합효소 I', () => {
  const { c } = loadComponent();
  assert.ok(c.events(26.9).some((e) => e.text.includes('DNA 중합효소 I이 1번째 조각')));
});
