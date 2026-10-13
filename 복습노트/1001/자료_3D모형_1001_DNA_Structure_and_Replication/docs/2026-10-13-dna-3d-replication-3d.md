# 복제 장면 입체화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복제 모드의 딸 DNA를 짝이 맞은 구간부터 오른나선으로 감고 효소를 음영 구로 그리며, 3D 보기 오른쪽 위 「3D」 토글로 지금의 평면 화면을 그대로 되돌린다.

**Architecture:** 평면 좌표 `armPos`(지금의 `arm()`)와 나선 좌표 `dhelix`를 감김 가중치 `twistW`(짝/분기점 거리 × `sim.tw`)로 보간한 `dpos`를 딸 가닥 좌표에 쓴다. `sim.tw`는 `state.view3d`를 0.4초에 걸쳐 따라가므로 `sim.tw = 0`이면 지금과 비트 단위로 같은 장면이 나온다. 효소는 `sim.tw ≥ 0.5`일 때만 음영 구로 그린다.

**Tech Stack:** Design Component(`.dc.html`, x-dc), Canvas 2D, Node `node:test` + `vm` 하네스(`tests/harness.cjs`), `node:crypto` sha256.

**Spec:** `docs/2026-10-13-dna-3d-replication-3d-design.md`

## Global Constraints

- 작업 위치: `복습노트/1001/자료_3D모형_1001_DNA_Structure_and_Replication/` (이하 상대 경로 기준). 고칠 소스는 `canvas/Main.dc.html` 하나.
- **커밋·푸시하지 않는다**(사용자가 따로 요청할 때까지). 각 Task의 체크포인트는 전체 테스트 통과로 대신한다.
- 테스트 명령: `node --test --test-reporter=tap tests/*.test.cjs` (현재 41/41 통과).
- 바꾸면 안 되는 것: `lagState`, `lagBond`, `isNick`, `K.STEPS[].f`, `events`, `stats`, `K.AR = 0.62`, `buildStructure`, 효소·라벨 위치(평면 `arm` 좌표).
- 3D 토글: 상태 `view3d` 기본 `true`, 저장하지 않음. 버튼은 `.view-btns` 맨 앞, 복제 모드에서만 보임, 보이는 글자 `3D`, `aria-label="입체로 보기"`, `aria-pressed`.
- 전환 속도: `sim.tw`가 초당 2.5씩(0.4초) 목표값으로 이동. 동작 줄이기(`prefers-reduced-motion: reduce`)면 즉시.
- 소스를 고친 뒤에는 `node standalone/build.cjs`로 `../3D모형_1001_DNA_Structure_and_Replication.html`을 다시 만든다(`tests/standalone.test.cjs`가 확인).
- dc-runtime은 click/keydown/mouseenter/mouseleave/input만 매핑한다. 새 버튼은 `onClick`만 쓴다.

## Review Focus

- 스크럽으로 f를 뒤로 돌리기 — 감김은 f만의 함수여야 하고, 앞서 본 f의 흔적이 남으면 안 된다 → Task 1 `twist depends only on f`.
- 일시정지 상태에서 3D 끄기 — `tick`은 재생과 무관하게 돌아야 화면이 풀린다 → Task 2 `tick eases twist while paused`.
- 단계 버튼 점프(f = 5, 11.8, 17, 23.5, 26.9, 28.3) 직후 화면 — 그 f에서도 가닥이 끊겨 튀면 안 된다 → Task 1 `backbone stays continuous` 스윕에 STEPS f 포함.
- 3D 끔 상태의 화면 — 지금 화면과 조금이라도 달라지면 "현재 구조 유지" 위반 → Task 1 `twist off reproduces the current flat scene`(스냅숏 해시).
- 좁은 화면(375px)에서 버튼 4개 묶음 — 가로 스크롤이나 상단 바 겹침 없이 보여야 한다 → Task 3 브라우저 확인 단계.

---

### Task 1: 딸 DNA 나선 좌표와 평면 스냅숏

**Files:**
- Create: `tests/fixtures/replication-snapshot.cjs`, `tests/fixtures/replication-flat.json`(생성물)
- Create: `tests/replication3d.test.cjs`
- Modify: `canvas/Main.dc.html:417` (`this.sim`), `:725-736` (`buildReplication` 앞부분의 `arm`·`tpl`·`tmid`·`newS`·`newP`), 새 메서드는 `buildReplication` 바로 위(`// ---------- replication model ----------` 구역)

**Interfaces:**
- Consumes: 기존 `this.lerp`, `this.sm`, `this.lagState(i, f)`, `this.K.{TW, OFF, AR}`, `this.sim.f`.
- Produces:
  - `this.sim.tw: number` (0–1, 초기값 1)
  - `armPos(h: number, sg: 1|-1, yoff: number): [x, y, z]` — 지금 `arm()`과 같은 식, `f = this.sim.f`
  - `twistW(h: number, sg: 1|-1): number` — 0–1, `this.sim.tw`를 곱한 값, 반쪽 위치는 양옆 정수 위치를 선형 보간
  - `dhelix(h: number, sg: 1|-1, yoff: number): [x, y, z]`
  - `dpos(h: number, sg: 1|-1, yoff: number): [x, y, z]` = `lerp(armPos(h,sg,yoff), dhelix(h,sg,yoff), twistW(h,sg))`
  - `dmid(i: number, sg: 1|-1): [x, y, z]` = `lerp(armPos(i,sg,-0.78), 중점(dhelix(i,sg,0), dhelix(i,sg,-1.56)), twistW(i,sg))`

- [ ] **Step 1: 지금 화면의 스냅숏 만들기 (소스를 고치기 전에)**

`tests/fixtures/replication-snapshot.cjs`에 `snapshot(c, f) → { n, sha }`를 만든다. 순서:
- `c.state.mode = 'replication'`, `c.sim.f = f`, `c.sim.tw = 0`
- `c.buildReplication(I, O)`
- `[...I, ...O]`의 각 항목에서 `k,p,q,r,w,c,a,rod,flat,focus,t,text,dx,dy,size,lead`만 뽑는다.
- `JSON.stringify`의 sha256을 구한다. `n`은 항목 수다.

`require.main === module`이면 다음 f마다 `loadComponent({ systemDark: false })`로 새 컴포넌트를 만든다.

```
[0, 3, 5, 11.8, 17, 23.5, 26.9, 28.3, 40, 60]
```

결과 `{ "<f>": { n, sha } }`를 `replication-flat.json`에 쓴다.

Run: `node tests/fixtures/replication-snapshot.cjs && head -c 200 tests/fixtures/replication-flat.json`
Expected: f 10개 키가 있는 JSON.

- [ ] **Step 2: 실패하는 테스트 쓰기** — `tests/replication3d.test.cjs`

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadComponent } = require('./harness.cjs');
const { snapshot } = require('./fixtures/replication-snapshot.cjs');
const FLAT = require('./fixtures/replication-flat.json');

const at = (f, tw = 1) => { const { c } = loadComponent({ systemDark: false }); c.state.mode = 'replication'; c.sim.f = f; c.sim.tw = tw; return c; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

test('twist off reproduces the current flat scene', () => {
  for (const f of Object.keys(FLAT)) assert.deepEqual(snapshot(at(Number(f), 0), Number(f)), FLAT[f], 'f=' + f);
});

test('deep leading daughter is helical', () => {
  const c = at(40);
  assert.equal(c.twistW(10, 1), 1);
  assert.ok(Math.abs(dist(c.dpos(10, 1, 0), c.armPos(10, 1, -0.78)) - 0.78) < 1e-9);
  const zs = [];
  for (let i = 10; i <= 19; i++) zs.push(c.dpos(i, 1, 0)[2]);
  assert.ok(Math.max(...zs) - Math.min(...zs) > 1.0);
});

test('fork end stays flat', () => {
  const c = at(40);
  for (const sg of [1, -1]) for (const i of [39, 40, 45]) assert.equal(c.twistW(i, sg), 0, sg + ':' + i);
  assert.ok(c.twistW(38, 1) < 0.3);
});

test('lagging single-strand gap stays flat', () => {
  const c = at(40);
  const gaps = [];
  for (let i = 28; i <= 38; i++) if (!c.lagState(i, 40)) gaps.push(i);
  assert.ok(gaps.length > 0);
  for (const i of gaps) assert.equal(c.twistW(i, -1), 0, 'i=' + i);
});

test('right-handed like the parent helix', () => {
  const c = at(50);
  const ang = (i) => { const p = c.dhelix(i, 1, 0), C = c.armPos(i, 1, -0.78); return Math.atan2(p[2] - C[2], p[1] - C[1]); };
  const d = ((ang(21) - ang(20)) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
  assert.ok(Math.abs(d - c.K.TW) < 1e-9);
});

test('backbone stays continuous while twisting', () => {
  const fs = loadComponent().c.K.STEPS.map((s) => s.f);
  for (let f = 0; f <= 60; f += 0.5) fs.push(f);
  for (const f of fs) {
    const c = at(f), lo = Math.max(0, Math.floor(f) - 34), hi = Math.floor(f) - 3;
    for (const sg of [1, -1]) for (const yoff of [0, -1.56]) for (let i = lo; i < hi; i++)
      assert.ok(dist(c.dpos(i, sg, yoff), c.dpos(i + 1, sg, yoff)) < 1.3, [f, sg, yoff, i].join(','));
  }
});

test('twist depends only on f', () => {
  const c = at(50);
  c.dpos(20, -1, 0);
  c.sim.f = 30;
  const fresh = at(30);
  for (let i = 0; i < 30; i++) assert.equal(c.twistW(i, -1), fresh.twistW(i, -1));
});
```

- [ ] **Step 3: 실패 확인**

Run: `node --test --test-reporter=tap tests/replication3d.test.cjs`
Expected: `twist off reproduces…`는 PASS, 나머지 6개는 FAIL(`c.twistW is not a function`).

- [ ] **Step 4: 구현** — `canvas/Main.dc.html`
  - `this.sim`에 `tw: 1`을 추가한다.
  - `armPos(h, sg, yoff)`는 지금 `arm()` 식(`Yo(a) = 1.0 + 3.0·(1 − e^(−a/1.6))`, `a = max(0, f − h)·AR`)을 메서드로 옮긴 것이다.
  - `twistW(h, sg)`의 정수 위치 규칙:
    - `paired(i)`는 `sg = 1`이면 `i ≥ 0 && i ≤ f − 2`, `sg = −1`이면 `!!lagState(i, f)`다. 단, `i < 0` 또는 `i ≥ f − 1`이면 언제나 false다.
    - `d`는 `k = 0…3` 중 `i − k` 또는 `i + k`가 짝 없는 가장 작은 k다(없으면 3).
    - 값은 `sm(d / 3) · sim.tw`다.
  - `dhelix(h, sg, yoff)`:
    - `C = armPos(h, sg, -0.78)`, `δ = yoff + 0.78`, `r = |δ|`.
    - `θ = h·TW + sg·π/2`이고, δ < 0이면 여기에 `sg·OFF`를 더한다.
    - 반환값은 `[C0, C1 + r·cos θ, C2 + r·sin θ]`다.
  - `dpos`와 `dmid`는 Interfaces에 적은 대로 만든다.
  - `buildReplication`은 다음처럼 바꾼다.
    - 지역 `arm`을 `this.armPos`로 대신한다. 효소·라벨은 계속 이 평면 좌표를 쓴다.
    - `tpl`의 두 번째 lerp 끝점을 `this.dpos(h, sg, yoff)`로 바꾼다.
    - `tmid`의 끝점을 `this.dmid(i, sg)`로 바꾼다.
    - `newS = (i, sg) => this.dpos(i, sg, -1.56)`, `newP = (h, sg) => this.dpos(h, sg, -1.76)`로 바꾼다.

  `w = 0`이면 `lerp(a, b, 0)`이 `a`를 그대로 돌려주므로 스냅숏이 비트 단위로 같아야 한다. 다르면 식의 순서가 원래 `arm()`과 어긋난 것이다.

- [ ] **Step 5: 통과 확인**

Run: `node --test --test-reporter=tap tests/replication3d.test.cjs 2>&1 | grep -E '^# (pass|fail)'`
Expected: `# pass 7`, `# fail 0`. (미리 계산해 보니 연속성 스윕의 최댓값은 1.22예요. f=4, 원점 끝 i=0. 기준 1.3 안에 들어요.)

- [ ] **Step 6: standalone 다시 만들기**

Run: `node standalone/build.cjs && node --test --test-reporter=tap tests/*.test.cjs 2>&1 | grep -E '^# (pass|fail)'`
Expected: `# pass 48`, `# fail 0`.

---

### Task 2: 3D 토글 버튼과 전환

**Files:**
- Modify: `tests/harness.cjs` (`matchMedia`에 `prefers-reduced-motion` 분기)
- Modify: `canvas/Main.dc.html` — 아래 곳들을 고친다.
  - CSS: `:101` 근처 `.icon-btn` 규칙 뒤
  - 마크업: `:223` `.view-btns`
  - 생성자: `:346-360` (`reduce` 보관, `view3d`)
  - `tick`: `:586-597`
  - `renderVals`
- Test: `tests/replication3d.test.cjs`에 추가

**Interfaces:**
- Consumes: Task 1의 `this.sim.tw`.
- Produces:
  - `this.state.view3d: boolean` (초기 true)
  - `this.reduceMotion: boolean`
  - `easeTwist(dt: number): void` — `sim.tw`를 `view3d ? 1 : 0` 쪽으로 `dt·2.5`만큼 옮기고 0–1로 자른다. `reduceMotion`이면 바로 목표값이 된다.
  - `renderVals()`에 `view3dPressed: 'true'|'false'`, `toggle3d: () => void`를 더한다.

- [ ] **Step 1: 하네스 옵션 추가**

`loadComponent(opts)`의 `matchMedia`에서 질의에 `'prefers-reduced-motion'`이 있으면 `!!opts.reduceMotion`을 돌려주게 한다.

- [ ] **Step 2: 실패하는 테스트 추가** — `tests/replication3d.test.cjs` 끝

```js
const { makeCtx, markupPart } = require('./harness.cjs');

test('3D view starts on', () => {
  const { c } = loadComponent();
  assert.equal(c.state.view3d, true);
  assert.equal(c.sim.tw, 1);
  assert.equal(c.renderVals().view3dPressed, 'true');
});

test('toggle eases to flat in 0.4 s', () => {
  const { c } = loadComponent();
  c.renderVals().toggle3d();
  assert.equal(c.state.view3d, false);
  const seen = [];
  for (let k = 0; k < 4; k++) { c.easeTwist(0.1); seen.push(c.sim.tw); }
  for (let k = 1; k < 4; k++) assert.ok(seen[k] < seen[k - 1]);
  assert.ok(seen[2] > 0);
  assert.equal(seen[3], 0);
  c.renderVals().toggle3d();
  c.easeTwist(1);
  assert.equal(c.sim.tw, 1);
});

test('reduced motion snaps', () => {
  const { c } = loadComponent({ reduceMotion: true });
  c.renderVals().toggle3d();
  c.easeTwist(0.016);
  assert.equal(c.sim.tw, 0);
});

test('tick eases twist while paused', () => {
  const { c } = loadComponent();
  c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 };
  c.ctx = makeCtx().ctx;
  c.setMode('replication');
  c.renderVals().toggle3d();
  c.tick(1000); c.tick(1100);
  assert.equal(c.state.playing, false);
  assert.ok(c.sim.tw < 1);
});

test('mode switch keeps 3D state', () => {
  const { c } = loadComponent();
  c.renderVals().toggle3d();
  c.setMode('replication'); c.setMode('structure'); c.setMode('replication');
  assert.equal(c.state.view3d, false);
});

test('3D button leads the view buttons, replication only', () => {
  const m = markupPart();
  const box = m.indexOf('<div class="view-btns">'), btn = m.indexOf('onClick="{{toggle3d}}"'), zoom = m.indexOf('aria-label="확대"');
  assert.ok(box > 0 && box < btn && btn < zoom);
  const ifAt = m.lastIndexOf('<sc-if value="{{isReplication}}"', btn);
  assert.ok(ifAt > box);
  for (const s of ['aria-pressed="{{view3dPressed}}"', 'aria-label="입체로 보기"', '>3D</button>', '.icon-btn[aria-pressed="true"]'])
    assert.ok(m.includes(s), s);
});
```

- [ ] **Step 3: 실패 확인**

Run: `node --test --test-reporter=tap tests/replication3d.test.cjs 2>&1 | grep -E '^not ok'`
Expected: 새 6개가 `not ok`로 나온다.

- [ ] **Step 4: 구현**
  - **생성자**
    - `this.reduceMotion = reduce`
    - `state.view3d = true`
    - `easeTwist(dt)`는 Interfaces에 적은 대로 만든다.
  - **`tick`**: `this.draw` 호출 바로 앞에 `this.easeTwist(dt)`를 넣는다. 재생 여부나 모드와 상관없이 매번 부른다.
  - **`renderVals`**
    - `view3dPressed: st.view3d ? 'true' : 'false'`
    - `toggle3d: () => this.setState({ view3d: !st.view3d })`
  - **마크업**: `.view-btns` 첫 자식으로 아래를 넣는다.
    ```html
    <sc-if value="{{isReplication}}" hint-placeholder-val="{{ false }}"><button class="icon-btn icon-btn-text" type="button" aria-label="입체로 보기" aria-pressed="{{view3dPressed}}" onClick="{{toggle3d}}">3D</button></sc-if>
    ```
  - **CSS**
    - `.icon-btn-text{font:700 13px/1 inherit;letter-spacing:0.02em}`
    - `.icon-btn[aria-pressed="true"]{border-color:var(--accent);color:var(--accent-ink)}`

- [ ] **Step 5: 통과 확인**

Run: `node standalone/build.cjs && node --test --test-reporter=tap tests/*.test.cjs 2>&1 | grep -E '^# (pass|fail)'`
Expected: `# pass 54`, `# fail 0`.

---

### Task 3: 효소 음영 구, 브라우저 확인, 캔버스 게시

**Files:**
- Modify: `canvas/Main.dc.html:915-` (`draw`의 `it.k === 5` 분기)
- Test: `tests/replication3d.test.cjs`에 추가
- Regenerate: `../3D모형_1001_DNA_Structure_and_Replication.html`

**Interfaces:**
- Consumes: Task 1의 `this.sim.tw`, Task 2의 `toggle3d`.
- Produces: 없음.

- [ ] **Step 1: 실패하는 테스트 추가**

```js
test('enzymes are shaded spheres only in 3D', () => {
  const grads = (tw) => {
    const { c } = loadComponent({ systemDark: false });
    const { ctx, calls } = makeCtx();
    c.canvas = { clientWidth: 800, clientHeight: 600, width: 0, height: 0 };
    c.ctx = ctx;
    c.setMode('replication');
    c.sim.f = 10; c.sim.tw = tw;
    c.draw(0.016, 0);
    return calls.filter((k) => k.op === 'createRadialGradient');
  };
  const concentric = (k) => k.args[0] === k.args[3] && k.args[1] === k.args[4];
  assert.ok(grads(0).some(concentric));
  assert.equal(grads(1).some(concentric), false);
});
```

동심 그라디언트는 지금 효소(`k:5`)만 쓰는 모양이다. 음영 구(`k:0`)는 중심을 비켜 놓는다.

- [ ] **Step 2: 실패 확인**

Run: `node --test --test-reporter=tap tests/replication3d.test.cjs 2>&1 | grep -E '^not ok'`
Expected: `enzymes are shaded spheres only in 3D` 하나만 실패한다.

- [ ] **Step 3: 구현**

`k:5` 분기에서 `this.sim.tw >= 0.5`일 때만 그라디언트를 음영 구로 바꾼다.
- 중심: `createRadialGradient(x − R·0.35, y − R·0.4, R·0.1, x, y, R)`
- 색 정지점:
  - `0 → rgba(255,255,255,0.55)`
  - `0.3 → this.rgba(it.c, Math.min(1, pal.blobAlpha + 0.15))`
  - `1 → this.rgba(it.c, 0.18)`

테두리(`it.focus ? 3 : 1.5`)는 그대로 둔다. `sim.tw < 0.5`일 때는 지금 코드를 한 글자도 바꾸지 않는다.

- [ ] **Step 4: 통과 확인**

Run: `node standalone/build.cjs && node --test --test-reporter=tap tests/*.test.cjs 2>&1 | grep -E '^# (pass|fail)'`
Expected: `# pass 55`, `# fail 0`.

- [ ] **Step 5: 브라우저 확인**

인앱 브라우저로 `../3D모형_1001_DNA_Structure_and_Replication.html`을 열고(`data:` URL이라 localStorage는 꺼져 있음) 다음을 확인한다.

1440px:
- ② 복제를 누르면 오른쪽 위에 `3D | + | − | ↺`가 보이고, ① 구조에서는 `3D`가 사라진다.
- 6단계 4번(f = 23.5)을 고르고 캔버스를 오른쪽으로 끌어 yaw를 약 1.2 돌린다. 딸 DNA 두 개가 나선으로 보이고 효소에 하이라이트가 있으면 된다.
- `3D`를 끄면 0.4초 안에 평면 사다리와 납작한 효소로 돌아온다. `aria-pressed`는 `"false"`가 된다.
- 재생 중에 끄고 켜도 진행 위치가 그대로 유지된다.
- 콘솔 오류가 없다.

375px:
- 버튼 4개가 상단 바와 겹치지 않는다.
- `document.documentElement.scrollWidth === 375`

끝나면 viewport를 desktop으로 되돌린다.

- [ ] **Step 6: 캔버스 게시** (기존 방식)
  1. `canvas/Main.dc.html`과 `canvas/canvas.json`을 scratchpad의 `publish/project/`에 복사한다.
  2. Artifact publish를 아래 값으로 부른다.
     - `url`: `https://claude.ai/artifact/592nYy4Lwta2FDT8MMGDFZ`
     - `root`: 스테이징 디렉터리
     - `file_path`: `project/canvas.json`
     - `files`: `{"project/Main.dc.html": "project/Main.dc.html"}`

  Expected: Version 7이 같은 링크에 올라간다.
