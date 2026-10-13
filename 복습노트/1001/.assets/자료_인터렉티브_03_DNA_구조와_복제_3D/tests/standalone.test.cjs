const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { build, OUT_PATH } = require('../standalone/build.cjs');

test('standalone html is up to date with the canvas source', () => {
  assert.ok(fs.existsSync(OUT_PATH), 'run: node standalone/build.cjs');
  assert.equal(fs.readFileSync(OUT_PATH, 'utf8'), build());
});

test('standalone html needs no canvas runtime or uploaded assets', () => {
  const h = build();
  assert.equal(h.includes('/_blob/'), false);
  assert.equal(h.includes('support.js'), false);
  assert.equal(h.includes('<x-dc>'), false);
  assert.ok(h.includes('https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css'));
  assert.ok(h.includes('<template id="dc-template">'));
  assert.ok(h.includes('class Component extends DCLogic'));
  assert.ok(h.includes('mountDC(Component)'));
  assert.ok(h.includes('<meta name="viewport"'));
});
