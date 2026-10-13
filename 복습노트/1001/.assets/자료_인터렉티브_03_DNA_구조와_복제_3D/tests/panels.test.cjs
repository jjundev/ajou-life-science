const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent, markupPart } = require('./harness.cjs');

test('default widths leave layout style empty', () => {
  const v = loadComponent().c.renderVals();
  assert.equal(v.layoutStyle, '');
  assert.equal(v.layoutCls, '');
  assert.equal(v.leftWNow, '');
});

test('setPanelWidth clamps to limits and saves', () => {
  const { c, store } = loadComponent({ innerWidth: 2560 });
  c.setPanelWidth('left', 1000, true);
  assert.equal(c.state.leftW, 480);
  assert.match(c.renderVals().layoutStyle, /--pl-user: ?480px/);
  assert.deepEqual({ ...JSON.parse(store['dna3d-panel-w']) }, { left: 480 });
  c.setPanelWidth('right', 100, false);
  assert.equal(c.state.rightW, 280);
  assert.deepEqual({ ...JSON.parse(store['dna3d-panel-w']) }, { left: 480 });
});

test('canvas keeps at least 400px', () => {
  const { c } = loadComponent({ innerWidth: 1100 });
  c.setPanelWidth('right', 720, false);
  // 1100 - left default (≤320) - 400 → right capped below 720
  assert.ok(c.state.rightW <= 1100 - 260 - 400, String(c.state.rightW));
});

test('reset clears width and storage', () => {
  const { c, store } = loadComponent({ innerWidth: 2560 });
  c.setPanelWidth('left', 300, true);
  c.resetPanelWidth('left');
  assert.equal(c.state.leftW, null);
  assert.equal(c.renderVals().layoutStyle, '');
  assert.deepEqual({ ...JSON.parse(store['dna3d-panel-w']) }, {});
});

test('saved widths restore, bad ones are ignored', () => {
  const ok = loadComponent({ storage: { 'dna3d-panel-w': '{"left":300,"right":500}' } }).c;
  assert.equal(ok.state.leftW, 300);
  assert.equal(ok.state.rightW, 500);
  assert.equal(loadComponent({ storage: { 'dna3d-panel-w': '{"left":9999,"right":"x"}' } }).c.state.leftW, null);
  assert.equal(loadComponent({ storage: { 'dna3d-panel-w': 'nope' } }).c.state.rightW, null);
  assert.equal(loadComponent({ storage: 'throw' }).c.state.leftW, null);
});

test('markup: resize handles and width transition, no display:none toggle', () => {
  const m = markupPart();
  assert.equal(m.split('class="panel-resize"').length - 1, 2);
  assert.ok(m.includes('ref="{{leftHandleRef}}"') && m.includes('ref="{{rightHandleRef}}"'));
  assert.ok(m.includes('style="{{layoutStyle}}"'));
  assert.ok(/transition:\s*width/.test(m));
  assert.equal(m.includes('.panel:not(.is-open){display:none}'), false);
});

test('docked panel-inner keeps flex sizing so it scrolls', () => {
  const m = markupPart();
  // flex:none would let .panel-inner grow to its content height inside the overflow:hidden panel
  assert.equal(/\.panel-(left|right) \.panel-inner\{[^}]*flex:none/.test(m), false);
  assert.ok(m.includes('.panel-inner{flex:1 1 auto;min-height:0;overflow-y:auto'));
});
