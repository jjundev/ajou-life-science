const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const SKILL = path.join(__dirname, '..');
const REPO = path.join(SKILL, '..', '..', '..');
const read = (rel) => fs.readFileSync(path.join(SKILL, rel), 'utf8');

test('frontmatter names the skill', () => {
  const md = read('SKILL.md');
  const fm = md.match(/^---\n([\s\S]*?)\n---\n/);
  assert.ok(fm, 'frontmatter block');
  assert.match(fm[1], /^name: bio-interactive$/m);
  const d = fm[1].match(/^description: (.+)$/m);
  assert.ok(d && d[1].trim().length > 20, 'description');
});

test('every referenced skill file exists', () => {
  const md = read('SKILL.md');
  const refs = [...new Set([...md.matchAll(/\b((?:assets|scripts|references)\/[\w.-]+)/g)].map((m) => m[1]))];
  assert.ok(refs.length >= 8, 'references: ' + refs.join(', '));
  for (const r of refs) assert.ok(fs.existsSync(path.join(SKILL, r)), r);
});

test('rules from the spec are stated', () => {
  const md = read('SKILL.md');
  for (const s of ['2–4', '인터렉티브_NN_<이름>.html', '자료_인터렉티브_NN_<이름>/', '복습노트/주제별/', 'check.cjs', 'build.cjs', 'resolve.cjs', '1440×900', '375×812'])
    assert.ok(md.includes(s), s);
});

test('topic selection states the scoring', () => {
  const sel = read('references/topic-selection.md');
  for (const s of ['+2', '+1', '3점', '후보 없음']) assert.ok(sel.includes(s), s);
});

test('.claude link resolves to the skill', () => {
  const link = path.join(REPO, '.claude', 'skills', 'bio-interactive');
  assert.ok(fs.lstatSync(link).isSymbolicLink());
  assert.equal(fs.readlinkSync(link), '../../.agents/skills/bio-interactive');
  assert.equal(fs.realpathSync(link), fs.realpathSync(SKILL));
});

test('follow-up rules are stated', () => {
  const md = read('SKILL.md');
  for (const s of ['scripts/steps.cjs', 'scripts/save.cjs', 'STEP_OFF_PHASE', 'phase']) assert.ok(md.includes(s), s);
  assert.ok(!/mkdir "\$DEST\/자료_인터렉티브/.test(md), 'old manual save snippet removed');
  assert.ok(md.includes('save.cjs" "$RUN/<n>/Main.dc.html" "$DEST" "<이름>"'), 'save takes the name');
  assert.ok(md.includes('lac_오페론_스위치') && md.includes('고유명사'), 'names are Korean with English proper nouns');
  assert.ok(!/인터렉티브_NN\.html|자료_인터렉티브_NN[/"]/.test(md), 'no unnamed file pattern left');
});
