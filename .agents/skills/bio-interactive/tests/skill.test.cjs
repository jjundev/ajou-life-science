const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const SKILL = path.join(__dirname, '..');
const REPO = path.join(SKILL, '..', '..', '..');
const read = (rel) => fs.readFileSync(path.join(SKILL, rel), 'utf8').replace(/\r\n/g, '\n');

test('note-link workflow and contextual brief contract are stated', () => {
  const md = read('SKILL.md');
  for (const s of ['noteHtml', 'scripts/link-notes.cjs', 'references/note-links.md', '### 8. 정리노트 연결', '### 9. 보고'])
    assert.ok(md.includes(s), s);
  const refs = read('references/note-links.md');
  for (const s of ['target="_blank"', 'noopener noreferrer', 'sectionId', 'anchorId', '새 탭', '기존 자료', 'skipped'])
    assert.ok(refs.includes(s), s);
  assert.ok(read('references/topic-selection.md').includes('정리노트 연결'));
  assert.ok(md.includes('`(새 탭)` 같은 표시 문구는 붙이지 않는다'));
  assert.ok(!md.includes('**하지 않는 것**: 정리노트·복습문제 수정'));
});

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

test('.claude link resolves to the skill', (t) => {
  const link = path.join(REPO, '.claude', 'skills', 'bio-interactive');
  let installed = true;
  try { fs.lstatSync(link); } catch { installed = false; }
  if (!installed) return t.skip('no install link (standalone copy)');
  assert.ok(fs.lstatSync(link).isSymbolicLink());
  assert.equal(fs.readlinkSync(link).replace(/\\/g, '/'), '../../.agents/skills/bio-interactive');
  assert.equal(fs.realpathSync(link), fs.realpathSync(SKILL));
});

test('docs do not point outside the skill folder', () => {
  const docs = ['SKILL.md', ...fs.readdirSync(path.join(SKILL, 'references')).filter((f) => f.endsWith('.md')).map((f) => 'references/' + f)];
  for (const rel of docs) {
    const md = read(rel).normalize('NFC');
    for (const s of ['복습노트/1001', '.agents/skills/bio-interactive/']) assert.ok(!md.includes(s), `${rel}: ${s}`);
  }
});

test('follow-up rules are stated', () => {
  const md = read('SKILL.md');
  for (const s of ['scripts/steps.cjs', 'scripts/save.cjs', 'STEP_OFF_PHASE', 'phase']) assert.ok(md.includes(s), s);
  assert.ok(!/mkdir "\$DEST\/자료_인터렉티브/.test(md), 'old manual save snippet removed');
  assert.ok(md.includes('save.cjs" "$RUN/<n>/Main.dc.html" "$DEST" "<이름>"'), 'save takes the name');
  assert.ok(md.includes('lac_오페론_스위치') && md.includes('고유명사'), 'names are Korean with English proper nouns');
  assert.ok(!/인터렉티브_NN\.html|자료_인터렉티브_NN[/"]/.test(md), 'no unnamed file pattern left');
});

test('docs put the data folder and notes under .assets', () => {
  const md = read('SKILL.md').normalize('NFC');
  for (const s of ['.assets/자료_인터렉티브_NN_<이름>/', '"<DEST>/.assets/자료_인터렉티브_NN_<이름>"', '`.assets/`의 정리노트'])
    assert.ok(md.includes(s), s);
});
