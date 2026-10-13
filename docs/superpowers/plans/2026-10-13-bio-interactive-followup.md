# bio-interactive 후속 수정 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 단계 위치 오류를 `check.cjs`가 잡게 하고, 단계 출력(`steps.cjs`)과 덮어쓰지 않는 저장(`save.cjs`)을 스크립트로 제공한다.

**Architecture:** Step에 `phase` 필드를 더해 `topicChecks`에서 `playback.label(f)`와 비교한다. `steps.cjs`·`save.cjs`는 기존 `harness.cjs`·`resolve.cjs`·`build.cjs`의 함수를 재사용하는 얇은 CLI다. SKILL.md 절차가 이 스크립트들을 부른다.

**Tech Stack:** Node 20+ (CommonJS, `node:test`), 의존성 없음.

**Spec:** `docs/superpowers/specs/2026-10-13-bio-interactive-followup-design.md`

## Global Constraints
- SKILL = `.agents/skills/bio-interactive` (모든 경로는 이 기준). 테스트: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
- 의존성 추가 없음, CommonJS `.cjs`, 기존 파일의 주석 밀도·이름 관례를 따른다.
- 사용자에게 보이는 문구는 한국어 해요체.
- 오류 줄 형식은 `코드:대상 — 메시지`(기존 `check()`의 `add(code, e)`; `e`가 문자열이면 그대로 메시지).
- 기준 결과물 `복습노트/1001/자료_인터렉티브_03_DNA_구조와_복제_3D/`과 이미 저장한 `복습노트/1006/자료_인터렉티브_0{1,2,3}/`은 수정하지 않는다.
- 파일명 비교는 NFC(`resolve.cjs`의 `nfc`).

## Review Focus
1. `f`가 재생 범위 밖이거나 모드가 없는 Step — 이미 `TOPIC_INVALID:STEPS[n].f`/`.mode`가 나므로 phase 검사는 건너뛰어 중복·예외가 없어야 한다. → Task 1 테스트 `phase check skips a step whose f is already invalid`.
2. `playback.label`이 예외를 내는 주제 — 검사가 멈추지 않고 `STEP_OFF_PHASE:n — <예외 문장>`. → Task 1 테스트 `label that throws is reported as STEP_OFF_PHASE`.
3. 저장 대상에 `자료_인터렉티브_02/`만 남아 있고 html이 없는 경우(중단된 저장) — 그 번호를 건너뛴다. → Task 3 테스트 `skips a number whose data folder exists`.
4. 저장이 원본 폴더(RUN)에 `canvas.json`을 남기지 않아야 한다(시험 실행에서 작성자들이 혼란). → Task 3 테스트 `writes nothing next to the source`.
5. 단계가 없는 주제에 `steps.cjs`를 돌릴 때 — 빈 배열, CLI는 `단계 없음` 한 줄. → Task 2 테스트 `topic without steps gives an empty report`.

---

### Task 1: Step `phase` 검사

**Files:**
- Modify: `SKILL/scripts/check.cjs:63-77` (`topicChecks`)
- Modify: `SKILL/assets/template.dc.html:296` (예시 Step 2에 `phase: '진행'`)
- Modify: `SKILL/references/scene-api.md` (오류 표 12–22행, Mode `playback` 52행, Step 55–57행)
- Test: `SKILL/tests/check.test.cjs`

**Interfaces:**
- Produces: Step 필드 `phase: string` (f가 있으면 필수). 오류 코드 `TOPIC_INVALID:STEPS[<n>].phase`, `STEP_OFF_PHASE:<n>` (n은 1부터). 템플릿 예시 Step 2 = `{ mode: 'b', f: 6, phase: '진행', … }`.

- [ ] **Step 1: 실패하는 테스트 작성** (`check.test.cjs`, 기존 `mutate` 사용)

```js
test('step with f but no phase', () => {
  const r = check(mutate((s) => s.replace(", phase: '진행'", '')), A);
  assert.ok(r.errors.includes('TOPIC_INVALID:STEPS[2].phase'), r.details.join('\n'));
});
test('step whose phase is not in the playback label', () => {
  const r = check(mutate((s) => s.replace("phase: '진행'", "phase: '연장'")), A);
  assert.ok(r.errors.includes('STEP_OFF_PHASE:2'));
  assert.ok(r.details.some((d) => d.startsWith('STEP_OFF_PHASE:2 — ') && d.includes("'연장'") && d.includes('진행 · 6.0 / 10')));
});
test('label that throws is reported as STEP_OFF_PHASE', () => {
  const r = check(mutate((s) => s.replace("label: (f) => '진행 · '", "label: (f) => f > 5 ? null.x : '진행 · '")), A);
  assert.ok(r.details.some((d) => d.startsWith('STEP_OFF_PHASE:2 — ')), r.details.join('\n'));
});
test('phase check skips a step whose f is already invalid', () => {
  const r = check(mutate((s) => s.replace("f: 6,", "f: 60,")), A);
  assert.ok(r.errors.includes('TOPIC_INVALID:STEPS[2].f'));
  assert.ok(!r.errors.some((e) => e.startsWith('STEP_OFF_PHASE')));
});
```
(첫 테스트의 mutate는 Step 3 이후에야 대상 문자열이 생긴다. Step 2에서는 `mutation changed nothing`으로 실패하는 것이 정상.)

- [ ] **Step 2: 실패 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/check.test.cjs`
Expected: 새 테스트 4개 중 3개 이상 FAIL(`phase`가 템플릿에 없음, 코드 미구현). 기존 테스트는 PASS.

- [ ] **Step 3: 구현**
- 템플릿 예시 Step 2에 `phase: '진행'`을 `f: 6` 뒤에 넣는다.
- `topicChecks`의 STEPS 반복에서, `mode`·`f` 검사를 통과했고 `s.f != null`인 단계에 대해: `phase`가 비었거나 문자열이 아니면 `add('TOPIC_INVALID:STEPS[n].phase')`; 아니면 `m.playback.label(s.f)`를 try로 불러, 예외면 `add('STEP_OFF_PHASE:n', e)`, 결과에 `s.phase`가 없으면 `add('STEP_OFF_PHASE:n', "기대 '" + s.phase + "', 실제 '" + label + "'")`.
- `scene-api.md`: Step 시그니처를 `{ mode, f?, phase?, c, title, who, text }`로, 설명에 「`f`가 있으면 `phase`도 써요. 그 `f`에서 재생 바 글자(`playback.label(f)`)에 들어 있는 과정 이름이에요. 단계는 그 과정이 화면에 다 보이는 지점에 둬요(다음 과정의 시작점에 두지 않아요).」 Mode `playback` 행에 `label(f)` 관례 `'<과정 이름> · ' + f.toFixed(1) + ' / ' + fmax`. 오류 표에 `| STEP_OFF_PHASE | 단계의 f에서 재생 바 글자에 phase가 없음(다음 과정에 들어가 있음) |`, `TOPIC_INVALID` 행에 `STEPS[n].phase` 추가.

- [ ] **Step 4: 통과 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: 전체 PASS (기존 59 + 4 = 63). `node .agents/skills/bio-interactive/scripts/check.cjs .agents/skills/bio-interactive/assets/template.dc.html --allow-template` → `ok`.

- [ ] **Step 5: 커밋**
```bash
git add .agents/skills/bio-interactive/scripts/check.cjs .agents/skills/bio-interactive/assets/template.dc.html .agents/skills/bio-interactive/references/scene-api.md .agents/skills/bio-interactive/tests/check.test.cjs
git commit -m "feat(bio-interactive): check that each step lands inside its own phase"
```

### Task 2: `steps.cjs` 단계 출력

**Files:**
- Create: `SKILL/scripts/steps.cjs`
- Test: `SKILL/tests/steps.test.cjs`

**Interfaces:**
- Consumes: `loadComponent(file, {narrow:false})`, `makeCtx()`, `makeCanvas(ctx, 800, 600)` from `harness.cjs`; 템플릿 Step 2의 `phase: '진행'`(Task 1).
- Produces: `stepsReport(file: string) → Array<{ n: number, title: string, mode: string, f: number|null, phase: string|null, fLabel: string, canvasLabel: string, panel: string }>`; CLI `node steps.cjs <Main.dc.html>` (인자 없거나 파일 없으면 usage를 stderr, exit 2).

- [ ] **Step 1: 실패하는 테스트 작성**

```js
const { stepsReport } = require('../scripts/steps.cjs');
test('template steps are reported in order', () => {
  const r = stepsReport(T);
  assert.equal(r.length, 2);
  assert.deepEqual(r.map((x) => [x.n, x.mode, x.f]), [[1, 'a', null], [2, 'b', 6]]);
  assert.equal(r[1].phase, '진행');
  assert.ok(r[1].fLabel.includes('진행'));
  assert.ok(r[1].canvasLabel.includes('6개'));
  assert.equal(typeof r[1].panel, 'string');
});
test('topic without steps gives an empty report', () => {
  // mutate: 템플릿의 STEPS: [ … ] 배열을 STEPS: [] 로 바꾼 사본
  assert.deepEqual(stepsReport(noSteps), []);
  const out = spawnSync(process.execPath, [SCRIPT, noSteps], { encoding: 'utf8' });
  assert.equal(out.stdout.trim(), '단계 없음');
});
test('cli without a file exits 2', () => assert.equal(spawnSync(process.execPath, [SCRIPT], { encoding: 'utf8' }).status, 2));
```

- [ ] **Step 2: 실패 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/steps.test.cjs`
Expected: FAIL — `Cannot find module '../scripts/steps.cjs'`.

- [ ] **Step 3: 구현** `SKILL/scripts/steps.cjs`
각 단계마다 새 컴포넌트가 아니라 하나를 쓰되 `renderVals().steps[i].pick()` → `draw(0.016, 0)` → `renderVals()`. `panel`은 `extraVals(this.state)` 결과에서 함수를 뺀 값을 `JSON.stringify` 후 400자로 자른다. CLI 출력은 단계마다 `n. 제목 [mode f=… phase=…]` 다음 줄들에 `재생 바: …`, `캔버스: …`, `패널: …`.

- [ ] **Step 4: 통과 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: 전체 PASS (66).

- [ ] **Step 5: 커밋**
```bash
git add .agents/skills/bio-interactive/scripts/steps.cjs .agents/skills/bio-interactive/tests/steps.test.cjs
git commit -m "feat(bio-interactive): add steps.cjs to print what each step shows"
```

### Task 3: `save.cjs` 저장

**Files:**
- Create: `SKILL/scripts/save.cjs`
- Modify: `SKILL/scripts/resolve.cjs:117` (`module.exports`에 `nextNumber`)
- Modify: `SKILL/scripts/build.cjs:76` (`module.exports`에 `titleOf`)
- Test: `SKILL/tests/save.test.cjs`

**Interfaces:**
- Consumes: `nextNumber(folder: string) → 'NN'` (resolve.cjs), `build(srcFile, outFile) → string`, `canvasJson(title) → string`, `titleOf(src) → string` (build.cjs).
- Produces: `save({ src: string, dest: string }) → { nn: string, html: string, dir: string }` (절대 경로). CLI `node save.cjs <src> <dest>` → 결과 JSON 출력, 인자·파일 문제면 stderr + exit 2.

- [ ] **Step 1: 실패하는 테스트 작성** (각 테스트는 새 `mkdtemp` 폴더, src는 템플릿을 `__TITLE__`→`테스트 주제`로 바꾼 사본을 별도 폴더 `run/1/Main.dc.html`에 둔다)

```js
test('first save gets 01', () => {
  const r = save({ src, dest });
  assert.equal(r.nn, '01');
  assert.ok(fs.existsSync(path.join(dest, '인터렉티브_01.html')));
  for (const f of ['Main.dc.html', 'canvas.json']) assert.ok(fs.existsSync(path.join(dest, '자료_인터렉티브_01', f)), f);
  assert.match(JSON.parse(fs.readFileSync(path.join(dest, '자료_인터렉티브_01', 'canvas.json'), 'utf8')).title, /테스트 주제/);
});
test('existing html moves to the next number', () => { fs.writeFileSync(path.join(dest, '인터렉티브_01.html'), 'x'); assert.equal(save({ src, dest }).nn, '02'); });
test('skips a number whose data folder exists', () => {
  fs.writeFileSync(path.join(dest, '인터렉티브_01.html'), 'x');
  fs.mkdirSync(path.join(dest, '자료_인터렉티브_02'));
  assert.equal(save({ src, dest }).nn, '03');
});
test('creates a missing dest', () => { const d = path.join(tmp, 'new', '1010'); assert.equal(save({ src, dest: d }).nn, '01'); });
test('writes nothing next to the source', () => {
  const before = fs.readdirSync(path.dirname(src)).sort();
  save({ src, dest });
  assert.deepEqual(fs.readdirSync(path.dirname(src)).sort(), before);
});
test('two saves in a row get 01 and 02', () => { assert.equal(save({ src, dest }).nn, '01'); assert.equal(save({ src, dest }).nn, '02'); });
```

- [ ] **Step 2: 실패 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/save.test.cjs`
Expected: FAIL — `Cannot find module '../scripts/save.cjs'`.

- [ ] **Step 3: 구현**
- `resolve.cjs`, `build.cjs` exports에 `nextNumber`, `titleOf` 추가.
- `save`: `fs.mkdirSync(dest, {recursive:true})`; `nn = nextNumber(dest)`부터 `인터렉티브_NN.html` 또는 `자료_인터렉티브_NN`이 있는 동안 1씩 올림(NFC 비교, 두 자리 패딩); `fs.mkdirSync(dir)`(recursive 없음); `Main.dc.html` 복사; `fs.writeFileSync(html, build(copy, html))`; `canvas.json`은 `dir`에 `canvasJson(titleOf(src 내용))`.

- [ ] **Step 4: 통과 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: 전체 PASS (72).

- [ ] **Step 5: 커밋**
```bash
git add .agents/skills/bio-interactive/scripts/save.cjs .agents/skills/bio-interactive/scripts/resolve.cjs .agents/skills/bio-interactive/scripts/build.cjs .agents/skills/bio-interactive/tests/save.test.cjs
git commit -m "feat(bio-interactive): add save.cjs that numbers and builds without overwriting"
```

### Task 4: SKILL.md 절차 반영

**Files:**
- Modify: `SKILL/SKILL.md` (3단계 64행, 4단계 71행, 5단계 73–78행, 6단계 81–91행, 7단계 93–98행, 실패 처리 표 119행)
- Test: `SKILL/tests/skill.test.cjs`

**Interfaces:**
- Consumes: Task 1 코드 `STEP_OFF_PHASE`, Task 2 CLI `node "$SKILL/scripts/steps.cjs" <file>`, Task 3 CLI `node "$SKILL/scripts/save.cjs" <src> <dest>`.

- [ ] **Step 1: 실패하는 테스트 작성** (`skill.test.cjs`)

```js
test('follow-up rules are stated', () => {
  const md = read('SKILL.md');
  for (const s of ['scripts/steps.cjs', 'scripts/save.cjs', 'STEP_OFF_PHASE', 'phase']) assert.ok(md.includes(s), s);
  assert.ok(!/mkdir "\$DEST\/자료_인터렉티브/.test(md), 'old manual save snippet removed');
});
```

- [ ] **Step 2: 실패 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/skill.test.cjs`
Expected: FAIL on `scripts/steps.cjs`.

- [ ] **Step 3: SKILL.md 수정**
- 3단계 지시에 추가: 「단계에 `f`를 쓰면 그 단계 과정이 화면에 다 보이는 지점에 두고, `phase`에 재생 바 글자에 나오는 과정 이름을 적는다(다음 과정의 시작점에 두지 않는다).」
- 4단계 오류 코드 목록에 `STEP_OFF_PHASE` 추가.
- 5단계: 검토자에게 `node "$SKILL/scripts/steps.cjs" "$RUN/<n>/Main.dc.html"` 출력도 넘기고, 확인 항목에 「단계 문구가 그 지점의 재생 바·캔버스 설명·패널 값과 맞는지」.
- 6단계: 「단계 누르기」 항목에 steps.cjs 출력과 화면을 대조한다고 적는다.
- 7단계 코드 블록을 `SKILL=…; RUN=…; DEST=…; node "$SKILL/scripts/save.cjs" "$RUN/<n>/Main.dc.html" "$DEST"`(점수 순으로 주제마다 한 번, 셸 반복문 없이)로 바꾸고, 결과 JSON의 `html`을 브라우저로 연다고 적는다.
- 실패 처리 표 「번호 자리에 이미 파일이 있음」 → 「`save.cjs`가 다음 빈 번호로 넘긴다(덮어쓰지 않음)」.

- [ ] **Step 4: 통과 확인**
Run: `node --test --test-reporter=tap .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: 전체 PASS (73).

- [ ] **Step 5: 커밋**
```bash
git add .agents/skills/bio-interactive/SKILL.md .agents/skills/bio-interactive/tests/skill.test.cjs
git commit -m "docs(bio-interactive): use steps.cjs and save.cjs in the procedure"
```

### Task 5: 1006 결과물 커밋

**Files:**
- Add (변경 없이): `복습노트/1006/인터렉티브_0{1,2,3}.html`, `복습노트/1006/자료_인터렉티브_0{1,2,3}/`

- [ ] **Step 1: 내용 확인** — `git status --short 복습노트/1006`가 위 6개 경로만 untracked로 보여 주는지 확인. 다른 경로가 있으면 추가하지 않는다.
- [ ] **Step 2: 커밋**
```bash
git add 복습노트/1006/인터렉티브_01.html 복습노트/1006/인터렉티브_02.html 복습노트/1006/인터렉티브_03.html 복습노트/1006/자료_인터렉티브_01 복습노트/1006/자료_인터렉티브_02 복습노트/1006/자료_인터렉티브_03
git commit -m "docs(notes): add 1006 interactives"
```
