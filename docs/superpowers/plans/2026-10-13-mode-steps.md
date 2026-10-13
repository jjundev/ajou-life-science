# 모드별 단계 목록 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 인터렉티브 왼쪽 패널 「단계」에 현재 모드의 단계만 보이게 하고, 이미 만든 인터렉티브 14개에도 같은 동작을 적용한다.

**Architecture:** 템플릿 셸에 전체 `STEPS` 인덱스로 단계를 고르는 `pickStep(i)`를 두고, `renderVals().steps`는 `st.mode`로 거른 목록(번호는 모드 안에서 1부터)만 돌려준다. `state.step`은 계속 전체 인덱스다. 검사 스크립트는 `renderVals().steps[i]` 대신 `pickStep(i)`를 쓴다. 기존 자료는 갱신된 템플릿에서 두 구간을 잘라 정확 치환한 뒤 `build.cjs`로 다시 빌드한다.

**Tech Stack:** Node 20+, `node:test`, dc 템플릿(`*.dc.html`), 기존 `scripts/harness.cjs`

**Spec:** 이 대화의 `/grill-yourself` 설계 「모드별 단계 목록」(파일 없음). 결정 #7 번호는 모드마다 1부터 [confirmed], #8 단계 없는 모드는 칸 전체 숨김 [confirmed]. 핵심 값은 아래 Global Constraints에 옮겼다.

`SKILL` = `.agents/skills/bio-interactive` (저장소 루트 기준. `.claude/skills/bio-interactive`는 이 폴더로의 링크)

## Global Constraints

- 단계 번호(`num`)는 현재 모드의 목록 안에서 1부터 센다.
- 목록 순서는 `STEPS`에 적힌 순서를 그대로 따른다(모드로 거르기만 한다).
- 단계가 없는 모드에서는 `hasSteps === false` → 「단계」 칸 전체가 숨겨진다. 안내 문구 없음.
- `state.step`, `hasStep`, `stepDetail`, `check.cjs` 오류 번호(`DRAW_THROWS:stepN`, `STEP_OFF_PHASE:N`, `STEPS[N]`), `steps.cjs`의 `n`은 모두 전체 `STEPS` 순서 기준(1부터)으로 유지한다.
- 모드 전환 시 `step: -1`, `f: 0` 동작은 바꾸지 않는다(`setMode`).
- 대상 기존 자료: `복습노트/{0901,0903,0908,1001,1006}/자료_인터렉티브_*/Main.dc.html` 14개와 짝 `인터렉티브_*.html`. `3D모형_1001_DNA_Structure_and_Replication`은 제외.
- `canvas.json`은 건드리지 않는다. 파일명은 NFD이므로 경로를 손으로 짓지 말고 `find`/glob 결과를 쓴다.
- `복습노트/1001`의 인터렉티브 파일은 아직 커밋되지 않은 사용자 작업이다. 고치기는 하되 `git add` 하지 않는다.

## Review Focus

1. **모드 순서가 섞인 `STEPS`** (예: `[fold, aa, fold, denat]`) — 모드 안 번호가 1, 2…로 이어지고 순서는 `STEPS` 순서. → Task 2 테스트 `steps are filtered and renumbered per mode`
2. **단계가 없는 모드** (0901 `sort`, 1006 `trna`) — `hasSteps === false`, `hasStep === false`. → Task 2 테스트 `mode without steps hides the section`
3. **다른 모드의 같은 위치 단계가 눌린 것으로 보임** — 모드 b의 1번을 고른 뒤 모드 a로 바꾸면 a 목록에 `pressed: 'true'`가 없어야 한다. → Task 2 테스트 `pressed follows the global step index`
4. **현재 모드가 아닌 단계를 스크립트가 고름** — `pickStep(i)`는 필요하면 모드를 바꾸고 `f`로 옮긴다. `check.cjs`가 템플릿에서 `DRAW_THROWS` 없이 통과한다. → Task 1 테스트 `pickStep switches mode and moves f`, 기존 `template passes with allowTemplate`
5. **기존 파일 치환이 엉뚱한 곳에 맞거나 0번 맞음** — 구간이 정확히 한 번 맞지 않으면 그 파일은 쓰지 않고 이름을 출력한다. → Task 3 Step 2의 기대 출력

---

### Task 1: `pickStep(i)` 도입과 스크립트 전환 (동작 변화 없음)

**Files:**
- Modify: `SKILL/assets/template.dc.html:698-721` (`setMode` 뒤에 `pickStep`, `steps[].pick`이 이를 부름)
- Modify: `SKILL/scripts/check.cjs:166`, `SKILL/scripts/steps.cjs:23`
- Test: `SKILL/tests/template.test.cjs`

**Interfaces:**
- Produces: 컴포넌트 메서드 `pickStep(i: number): void` — `i`는 `STEPS` 전체 인덱스(0부터). `STEPS[i].mode !== state.mode`면 `setMode(STEPS[i].mode)`, `f`가 있으면 `sim.f = f`, 그 뒤 `setState({ f: sim.f, playing: false, step: i })`. 지금 `pick` 본문(717–719행)과 같다.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/template.test.cjs`에 추가

```js
test('pickStep switches mode and moves f', () => {
  const { c } = loadComponent(T);
  const S = c.topic().STEPS[1];
  c.setMode('a');
  c.setState({ playing: true });
  c.pickStep(1);
  assert.equal(c.state.mode, S.mode);
  assert.equal(c.state.f, S.f);
  assert.equal(c.state.playing, false);
  assert.equal(c.state.step, 1);
  assert.equal(c.renderVals().stepDetail, S.text);
});
```

- [ ] **Step 2: 실패 확인** — `node --test SKILL/tests/template.test.cjs` → FAIL `c.pickStep is not a function`

- [ ] **Step 3: 구현** — 템플릿 `setMode()` 바로 뒤에 `pickStep(i)` 추가, `steps[].pick`을 `() => this.pickStep(i)`로. `check.cjs:166`, `steps.cjs:23`의 `c.renderVals().steps[i].pick()`을 `c.pickStep(i)`로. `check.cjs:63` 주석을 `Steps are numbered from 1 in STEPS order.`로.

- [ ] **Step 4: 통과 확인** — `node --test SKILL/tests/*.test.cjs` → 전부 PASS

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-interactive/assets/template.dc.html .agents/skills/bio-interactive/scripts/check.cjs .agents/skills/bio-interactive/scripts/steps.cjs .agents/skills/bio-interactive/tests/template.test.cjs
git commit -m "refactor(bio-interactive): pick steps by global index"
```

---

### Task 2: 현재 모드 단계만 보이기

**Files:**
- Modify: `SKILL/assets/template.dc.html` (`renderVals()`의 `const steps = …`)
- Modify: `SKILL/references/scene-api.md:31`, `:58`, `:93` 근처 메서드 목록
- Test: `SKILL/tests/template.test.cjs` (기존 `scrub and step pick move f` 수정 + 새 테스트 3개)

**Interfaces:**
- Consumes: Task 1의 `pickStep(i)`
- Produces: `renderVals().steps: Array<{ num, title, who, c, pressed, pick }>` — `STEPS` 중 `mode === state.mode`인 것만, `num`은 1부터, `pressed`는 `state.step === <전체 인덱스>`일 때 `'true'`.

- [ ] **Step 1: 실패하는 테스트 작성**

기존 `scrub and step pick move f`(106행)에서 `c.renderVals().steps[1].pick()` → `c.pickStep(1)`, 마지막 단언 `v.steps[1].pressed` → `v.steps[0].pressed`.

모드 구성을 바꾼 주제는 `steps.test.cjs:24-30`처럼 `STEPS: [...]`를 치환한 임시 파일을 `fs.mkdtempSync`에 써서 `loadComponent`로 연다. 새 테스트:

```js
test('steps are filtered and renumbered per mode', () => {
  // STEPS = [a:'A1', b:'B1'(f 6), a:'A2', b:'B2'(f 8)]
  const { c } = loadComponent(withSteps(MIXED));
  assert.deepEqual(c.renderVals().steps.map((s) => [s.num, s.title]), [[1, 'A1'], [2, 'A2']]);
  c.setMode('b');
  assert.deepEqual(c.renderVals().steps.map((s) => [s.num, s.title]), [[1, 'B1'], [2, 'B2']]);
  c.renderVals().steps[1].pick();
  assert.equal(c.state.step, 3);
});

test('pressed follows the global step index', () => {
  const { c } = loadComponent(T);
  c.pickStep(1);
  assert.deepEqual(c.renderVals().steps.map((s) => s.pressed), ['true']);
  c.setMode('a');
  assert.deepEqual(c.renderVals().steps.map((s) => s.pressed), ['false']);
});

test('mode without steps hides the section', () => {
  // STEPS = [b 단계 1개]
  const { c } = loadComponent(withSteps(ONLY_B));
  c.setMode('a');
  const v = c.renderVals();
  assert.equal(v.hasSteps, false);
  assert.equal(v.hasStep, false);
  assert.deepEqual(v.steps, []);
});
```

`withSteps(src)`와 `MIXED`/`ONLY_B` 문자열은 이 테스트 파일 안에 둔다. `ONLY_B`의 단계는 템플릿 `STEPS[1]`과 같은 값을 쓴다.

- [ ] **Step 2: 실패 확인** — `node --test SKILL/tests/template.test.cjs` → 새 3개 FAIL(모드 a에서 목록 길이 2 등)

- [ ] **Step 3: 구현** — `renderVals()`의 `steps`를 `STEPS.map((s, i) => ({ s, i })).filter((x) => x.s.mode === st.mode).map((x, k) => …)`로. `num: k + 1`, `pressed`는 `x.i` 비교, `pick: () => this.pickStep(x.i)`. `hasSteps`, `hasStep`, `stepDetail` 줄은 그대로.

  `scene-api.md`:
  - 31행: `// 선택. 있으면 왼쪽 「단계」 목록이 생겨요` → `// 선택. 현재 모드의 단계만 왼쪽 「단계」 목록에 보여요(없으면 칸이 숨겨져요)`
  - Step 절(58행) 끝에 한 줄: `목록 번호는 모드 안에서 1부터 세요. 검사 오류의 단계 번호는 STEPS 전체 순서예요.`
  - 상태·메서드 설명에 `pickStep(i)`(전체 인덱스) 추가.

- [ ] **Step 4: 통과 확인** — `node --test SKILL/tests/*.test.cjs` → 전부 PASS. `node SKILL/scripts/check.cjs SKILL/assets/template.dc.html`은 템플릿 그대로라 `TEMPLATE_LEFT` 외 오류가 없어야 한다(테스트 `template passes with allowTemplate`가 이를 덮는다).

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-interactive/assets/template.dc.html .agents/skills/bio-interactive/references/scene-api.md .agents/skills/bio-interactive/tests/template.test.cjs
git commit -m "feat(bio-interactive): show only the current mode's steps"
```

---

### Task 3: 기존 인터렉티브 14개 적용과 다시 빌드

**Files:**
- Create (scratchpad, 커밋 안 함): `<scratchpad>/migrate-steps.cjs`
- Modify: `복습노트/{0901,0903,0908,1001,1006}/자료_인터렉티브_*/Main.dc.html` (14개)
- Modify: 같은 폴더의 `인터렉티브_NN_<이름>.html` (14개, 빌드 산출물)

**Interfaces:**
- Consumes: Task 2 이후의 `SKILL/assets/template.dc.html`, `SKILL/scripts/build.cjs`, `SKILL/scripts/check.cjs`

- [ ] **Step 1: 치환 스크립트 작성** — `node migrate-steps.cjs <template> <Main.dc.html>...`

  템플릿에서 두 구간을 잘라 각 대상 파일의 같은 구간을 바꾼다.
  - 구간 A: `  setMode(mode) {` 줄부터 `  renderVals() {` 바로 앞 줄까지(`pickStep` 포함)
  - 구간 B: `    const STEPS = T.STEPS || [];` 줄부터 그 뒤 첫 `    }));` 줄까지

  대상에서 각 구간의 시작 표지가 정확히 한 번 나오지 않으면 그 파일은 쓰지 않고 `SKIP <경로> <이유>`를 출력한다. 쓴 파일은 `OK <경로>`. 셸 변형 두 종류(`onKey` 한 줄 차이)는 두 구간 밖이라 영향 없다.

- [ ] **Step 2: 실행** — 대상은 `find 복습노트 -path '*자료_인터렉티브_*' -name Main.dc.html`

  기대: `OK` 14줄, `SKIP` 0줄.

- [ ] **Step 3: 검사** — 파일마다 `node SKILL/scripts/check.cjs "<Main.dc.html>"` → 14개 모두 `ok`

- [ ] **Step 4: 다시 빌드** — 파일마다 `node SKILL/scripts/build.cjs "<자료_…/Main.dc.html>" "<같은 날짜 폴더>/인터렉티브_NN_<이름>.html"` (출력 경로는 `자료_` 접두를 뗀 폴더명 + `.html`)

  `git diff --stat -- 복습노트/0901 복습노트/0903 복습노트/0908 복습노트/1006` → 파일 24개(0901 2쌍 + 0903 4쌍 + 0908 3쌍 + 1006 3쌍, Main 12 + html 12)만 바뀌고, html의 바뀐 줄은 `setMode`~`pickStep`과 `const steps` 구간뿐. 1001 2쌍은 미추적이라 diff에 안 나온다.

- [ ] **Step 5: 브라우저 확인** — 내장 브라우저로 `0901/인터렉티브_01_생명의_계층구조.html`, `1006/인터렉티브_01_lac_오페론_스위치.html` 열기(1440×900, 라이트·다크)
  - 콘솔 오류 0
  - lac: `off` 모드 단계 1–3, `on` 모드 단계 1–4. 단계 누르면 상세 칸 표시, 모드 바꾸면 사라짐
  - 생명의 계층구조: `sort` 모드에서 「단계」 칸 없음, `zoom` 모드에서 1–6

- [ ] **Step 6: 커밋** (1001 제외)

```bash
git add 복습노트/0901 복습노트/0903 복습노트/0908 복습노트/1006
git commit -m "docs(notes): show only current mode steps in interactives"
```

  `git add` 전에 `git status --short`로 이 네 폴더에서 인터렉티브 외 파일이 함께 올라가지 않는지 본다. 섞여 있으면 파일을 하나씩 지정한다.
