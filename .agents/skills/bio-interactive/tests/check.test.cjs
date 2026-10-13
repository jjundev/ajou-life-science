const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { check } = require('../scripts/check.cjs');

const SKILL = path.join(__dirname, '..');
const T = path.join(SKILL, 'assets', 'template.dc.html');
const A = { allowTemplate: true };
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'bi-check-'));
let n = 0;

function mutate(fn) {
  const src = fs.readFileSync(T, 'utf8');
  const out = fn(src);
  assert.notEqual(out, src, 'mutation changed nothing');
  const p = path.join(TMP, 'm' + (n++) + '.dc.html');
  fs.writeFileSync(p, out);
  return p;
}

test('template passes with allowTemplate', () => assert.deepEqual(check(T, A), { ok: true, errors: [] }));

test('template left as-is is rejected', () => {
  const r = check(T);
  assert.equal(r.ok, false);
  for (const e of ['TEMPLATE_LEFT:__TITLE__', 'TEMPLATE_LEFT:__SOURCE__', 'TEMPLATE_LEFT:DEMO']) assert.ok(r.errors.includes(e), e);
});

test('missing shell piece', () => assert.ok(check(mutate((s) => s.replace('class="scrim', 'class="dim')), A).errors.includes('SHELL_MISSING:class="scrim')));

test('unknown hole', () => assert.ok(check(mutate((s) => s.replace('{{themeLabel}}"', '{{themLabel}}"')), A).errors.includes('HOLE_UNKNOWN:themLabel')));

test('loop variable outside its sc-for is unknown', () => {
  const r = check(mutate((s) => s.replace('<p class="source">', '<p class="source">{{md.label}}')), A);
  assert.ok(r.errors.includes('HOLE_UNKNOWN:md'));
});

test('unsupported event', () => assert.ok(check(mutate((s) => s.replace('onClick="{{zoomIn}}"', 'onDoubleClick="{{zoomIn}}"')), A).errors.includes('EVENT_UNSUPPORTED:onDoubleClick')));

test('raw hex in markup', () => assert.ok(check(mutate((s) => s.replace('<div class="scrim', '<div style="color:#123456" class="scrim')), A).errors.includes('HEX_IN_MARKUP:#123456')));

test('scene that throws', () => assert.ok(check(mutate((s) => s.replace(/buildScene\(mode, I, O\) \{/, '$& if (mode === "b") throw new Error("x");')), A).errors.includes('DRAW_THROWS:b')));

test('scene that throws late in playback', () => assert.ok(check(mutate((s) => s.replace(/buildScene\(mode, I, O\) \{/, '$& if (this.sim.f > 9) throw new Error("x");')), A).errors.includes('DRAW_THROWS:b')));

test('scene that throws in dark only', () => {
  const r = check(mutate((s) => s.replace("link: '#AEB7C4'", 'link: null')), A);
  assert.ok(r.errors.includes('DRAW_THROWS:a'), r.errors.join());
});

test('empty scene', () => assert.ok(check(mutate((s) => s.replace(/buildScene\(mode, I, O\) \{/, '$& return;')), A).errors.includes('SCENE_EMPTY:a')));

test('renderVals that throws', () => {
  const r = check(mutate((s) => s.replace(/extraVals\(st\) \{/, '$& if (st.narrow && st.theme === "dark") throw new Error("x");')), A);
  assert.ok(r.errors.includes('RENDER_THROWS:narrow-dark-a'), r.errors.join());
  assert.equal(r.errors.includes('RENDER_THROWS:wide-light-a'), false);
});

test('cli exit codes', () => {
  const cli = path.join(SKILL, 'scripts', 'check.cjs');
  const ok = spawnSync('node', [cli, T, '--allow-template'], { encoding: 'utf8' });
  assert.equal(ok.status, 0);
  assert.equal(ok.stdout.trim(), 'ok');
  const bad = spawnSync('node', [cli, T], { encoding: 'utf8' });
  assert.equal(bad.status, 1);
  assert.match(bad.stdout, /TEMPLATE_LEFT:DEMO/);
});

test('hole syntax the runtime cannot parse', () => {
  const r1 = check(mutate((s) => s.replace('<sc-if value="{{hasSteps}}"', '<sc-if value="{{!hasSteps}}"')), A);
  assert.ok(r1.errors.includes('HOLE_SYNTAX:!hasSteps'), r1.errors.join());
  const r2 = check(mutate((s) => s.replace('<p class="source">', '<p class="source">{{isPlaying ? 1 : 2}}')), A);
  assert.ok(r2.errors.includes('HOLE_SYNTAX:isPlaying ? 1 : 2'), r2.errors.join());
  const r3 = check(mutate((s) => s.replace('onClick="{{zoomIn}}"', 'onClick="x{{zoomIn}}"')), A);
  assert.ok(r3.errors.includes('HOLE_SYNTAX:onClick'), r3.errors.join());
});
