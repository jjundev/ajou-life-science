const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent, markupPart } = require('./harness.cjs');

test('wide starts with both panels open', () => {
  const v = loadComponent({ narrow: false }).c.renderVals();
  assert.equal(v.leftCls, 'is-open');
  assert.equal(v.rightCls, 'is-open');
  assert.equal(v.leftExpanded, 'true');
  assert.equal(v.rightExpanded, 'true');
});

test('narrow starts closed', () => {
  const { c } = loadComponent({ narrow: true });
  const v = c.renderVals();
  assert.equal(v.leftCls, '');
  assert.equal(v.rightCls, '');
  assert.equal(v.scrimCls, '');
  v.toggleRight();
  assert.equal(c.renderVals().scrimCls, 'is-on');
  c.renderVals().closePanels();
  assert.equal(c.renderVals().rightCls, '');
  assert.equal(c.renderVals().scrimCls, '');
});

test('mode switch keeps panels, swaps mistakes', () => {
  const { c } = loadComponent({ narrow: false });
  c.renderVals().toggleLeft();
  assert.deepEqual([...c.renderVals().mistakes].map((m) => m.title), ['역평행 ≠ 오른나선', '0.34 nm와 3.4 nm', '새 뉴클레오타이드는 3′-OH에']);
  c.renderVals().toReplication();
  assert.equal(c.state.leftOpen, false);
  assert.equal(c.state.rightOpen, true);
  assert.deepEqual([...c.renderVals().mistakes].map((m) => m.title), ['지연가닥도 5′→3′', '채우기 ≠ 잇기', '원점은 자리, 분기점은 움직이는 경계']);
});

test('stepDetail hidden until a step is picked', () => {
  const { c } = loadComponent();
  c.setMode('replication');
  assert.equal(c.renderVals().hasStep, false);
  c.renderVals().steps[2].pick();
  assert.equal(c.renderVals().hasStep, true);
});

test('legend follows palette', () => {
  const { c } = loadComponent({ systemDark: false });
  assert.equal(c.renderVals().legend.parent, '#8A94A3');
  c.setTheme('dark');
  const lg = c.renderVals().legend;
  assert.equal(lg.parent, '#AEB7C4');
  assert.equal(lg.newDna, '#6FD3C1');
  assert.equal(lg.ring, '#f2f4f6');
});

test('removed copy is gone', () => {
  const m = markupPart();
  for (const s of ['1001 복습 · 5장 p1–2 · 3D 모형', '돌려 보며 이해하기', '끌어서 회전', '눌러서 그 장면으로', '이 20쌍 전체', '두 가닥은 마주 보고', '단계를 누르면 그 장면으로', '헷갈리기 쉬운 점 · 화면에서 직접 확인'])
    assert.equal(m.includes(s), false, s);
});

test('note shell present, old dark hexes gone from markup', () => {
  const m = markupPart();
  for (const s of ['class="app"', 'class="topbar"', 'class="layout {{layoutCls}}"', 'class="panel panel-left {{leftCls}}"', 'class="panel panel-right {{rightCls}}"', 'class="scrim {{scrimCls}}"', '@media (max-width: 1023.98px)', 'aria-label="{{themeLabel}}"', '--bg: {{th.bg}}', '--accent-ink: {{th.accentInk}}', '꼭 기억해요'])
    assert.ok(m.includes(s), s);
  for (const h of ['#0B0F14', '#121821', '#0F151D', '#1E2733', '#2A3443']) assert.equal(m.includes(h), false, h);
});
