const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { readMain, CANVAS_JSON_PATH } = require('./harness.cjs');

test('Pretendard faces from uploads, no IBM Plex or Google Fonts', () => {
  const h = readMain();
  const faces = h.match(/@font-face\s*{[^}]*}/g) || [];
  assert.equal(faces.length, 4);
  for (const w of ['400', '600', '700', '800'])
    assert.ok(faces.some((f) => f.includes(`font-weight: ${w}`) && /url\('\/_blob\/[^']+'\)/.test(f) && f.includes("font-family: 'Pretendard'")), w);
  assert.equal(h.includes('IBM Plex'), false);
  assert.equal(h.includes('fonts.googleapis'), false);
});

test('page is one screen tall', () => {
  const cj = JSON.parse(fs.readFileSync(CANVAS_JSON_PATH, 'utf8'));
  assert.equal(cj.boards['Main.dc.html'].h, 900);
  assert.equal(cj.boards['Main.dc.html'].expand, 'fill');
  assert.ok(readMain().includes('"$preview":{"width":1440,"height":900}'));
});
