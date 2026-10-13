const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { stepsReport } = require('../scripts/steps.cjs');

const SKILL = path.join(__dirname, '..');
const T = path.join(SKILL, 'assets', 'template.dc.html');
const SCRIPT = path.join(SKILL, 'scripts', 'steps.cjs');

test('template steps are reported in order', () => {
  const r = stepsReport(T);
  assert.equal(r.length, 2);
  assert.deepEqual(r.map((x) => [x.n, x.mode, x.f]), [[1, 'a', null], [2, 'b', 6]]);
  assert.deepEqual(r.map((x) => x.title), ['고리 살펴보기', '여섯 번째 구']);
  assert.equal(r[1].phase, '진행');
  assert.ok(r[1].fLabel.includes('진행'), r[1].fLabel);
  assert.ok(r[1].canvasLabel.includes('6개'), r[1].canvasLabel);
  assert.equal(typeof r[1].panel, 'string');
});

test('topic without steps gives an empty report', () => {
  const src = fs.readFileSync(T, 'utf8');
  const out = src.replace(/STEPS: \[[\s\S]*?\n      \],/, 'STEPS: [],');
  assert.notEqual(out, src, 'mutation changed nothing');
  const noSteps = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'bi-steps-')), 'Main.dc.html');
  fs.writeFileSync(noSteps, out);
  assert.deepEqual(stepsReport(noSteps), []);
  const cli = spawnSync(process.execPath, [SCRIPT, noSteps], { encoding: 'utf8' });
  assert.equal(cli.status, 0, cli.stderr);
  assert.equal(cli.stdout.trim(), '단계 없음');
});

test('cli without a file exits 2', () => {
  assert.equal(spawnSync(process.execPath, [SCRIPT], { encoding: 'utf8' }).status, 2);
  assert.equal(spawnSync(process.execPath, [SCRIPT, '/no/such/Main.dc.html'], { encoding: 'utf8' }).status, 2);
});
