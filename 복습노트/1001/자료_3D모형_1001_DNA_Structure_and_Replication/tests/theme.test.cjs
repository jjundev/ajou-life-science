const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent } = require('./harness.cjs');

test('stored value wins', () => {
  const { c } = loadComponent({ storage: { 'od-theme': 'dark' }, systemDark: false });
  assert.equal(c.state.theme, 'dark');
});

test('falls back to system', () => {
  assert.equal(loadComponent({ systemDark: true }).c.state.theme, 'dark');
  assert.equal(loadComponent({ systemDark: false }).c.state.theme, 'light');
});

test('ignores unknown stored value', () => {
  assert.equal(loadComponent({ storage: { 'od-theme': 'sepia' }, systemDark: true }).c.state.theme, 'dark');
});

test('toggle stores only when differing from system', () => {
  const { c, store } = loadComponent({ systemDark: false });
  c.renderVals().toggleTheme();
  assert.equal(c.state.theme, 'dark');
  assert.equal(store['od-theme'], 'dark');
  c.renderVals().toggleTheme();
  assert.equal(c.state.theme, 'light');
  assert.equal('od-theme' in store, false);
});

test('storage throws', () => {
  const { c } = loadComponent({ storage: 'throw', systemDark: true });
  assert.equal(c.state.theme, 'dark');
  assert.doesNotThrow(() => c.renderVals().toggleTheme());
  assert.equal(c.state.theme, 'light');
});

test('renderVals exposes tokens and label', () => {
  const l = loadComponent({ systemDark: false }).c.renderVals();
  assert.equal(l.th.bg, '#ffffff');
  assert.equal(l.th.accentInk, '#1b64da');
  assert.equal(l.isDark, false);
  assert.equal(l.themeLabel, '다크 모드로 전환');
  const d = loadComponent({ systemDark: true }).c.renderVals();
  assert.equal(d.th.bg, '#17171c');
  assert.equal(d.isDark, true);
  assert.equal(d.themeLabel, '라이트 모드로 전환');
});
