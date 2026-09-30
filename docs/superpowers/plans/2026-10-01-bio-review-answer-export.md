# 복습문제 풀이 기록 JSON 내보내기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 문제 화면을 벗어날 때마다 풀이 기록 스냅샷을 갱신하고, 마지막 문제 화면의 "JSON 내보내기" 버튼으로 전체 기록을 폴더(Chrome 폴더 선택창)에 `.json`으로 저장한다.

**Architecture:** 순수 함수(스냅샷 갱신·내보내기 객체·파일명·저장)를 `review-interaction.js`에 추가해 Node로 단위 테스트한다. 페이저가 화면을 벗어날 때 `od:leave` 이벤트를 보내고, `mount()`가 이를 받아 `sessionStorage` 스냅샷을 갱신한다. 내보내기 버튼은 `.pager` 안에 넣고 `body.at-end`일 때만 CSS로 보이게 한다. 이미 만들어진 복습문제 HTML은 `install()`이 페이저 패치와 최신 JS를 다시 주입한다.

**Tech Stack:** 순수 JavaScript(브라우저·Node 겸용 IIFE), Python 3(`review_interaction.py`), `unittest`, `node --test`, Playwright(Chromium).

**Spec:** `docs/superpowers/specs/2026-09-30-bio-review-answer-export-design.md`

## Global Constraints

- 고른 답·푼 기록·스냅샷은 `sessionStorage`에만 둔다. 이 기능에서 `localStorage`를 쓰지 않는다(직전 결정: 탭을 닫고 다시 열면 초기화).
- 폴더 저장은 `window.showDirectoryPicker`(Chrome), 실패·미지원 시 `Blob` 다운로드. 선택창 취소(`AbortError`)면 아무것도 저장하지 않는다.
- JSON `schema: 1`. `cards`는 문서(DOM) 순서, 안 푼 문제는 `selected: null`·`updatedAt: null`.
- 파일 이름 `<복습문제 파일명(확장자 제외)>_풀이기록_<YYYYMMDD-HHmm(로컬)>.json`.
- 저장소 차단·복원 불가 상황에서도 풀이는 막히지 않고, 내보내기는 메모리 값으로 동작한다.
- 화면 문구는 한국어 존댓말 톤(`~했어요`)을 따른다.
- `복습노트/*/복습문제_*.html`은 손으로 고치지 않고 `review_interaction.py --write`로만 갱신한다.

## Review Focus

1. **저장소 차단:** `sessionStorage`가 막혀도 내보낸 JSON에 푼 답이 들어간다. Task 3의 브라우저 테스트.
2. **선택창 취소:** 파일도 다운로드도 만들지 않고 "취소했어요" 안내만 나온다. Task 1 단위 테스트 + Task 3 브라우저 테스트.
3. **폴더 API 거부·미지원(예: Downloads 폴더 선택 시 SecurityError):** 다운로드로 대체된다. Task 1 단위 테스트 + Task 3 브라우저 테스트.
4. **다시 풀기 후 내보내기:** 초기화한 문제는 `selected: null`이다. Task 3의 브라우저 테스트.
5. **문항 순서:** `model.cards`는 키 정렬(`p1, p10, p2`)로 저장되므로 내보내기는 DOM 순서(`p1, p2, … p10`)여야 한다. Task 1 단위 테스트.

---

## File map

- Modify `assets/review-interaction.js`: 순수 함수 6개 추가, `mount()`에 스냅샷·내보내기 연결.
- Modify `assets/review-interaction.css`: 내보내기 줄 스타일.
- Modify `assets/review-template.html`: 페이저 `render()`에서 `od:leave` 발생.
- Modify `scripts/review_interaction.py`: `patch_pager_shell()` 추가, `install()`에서 호출.
- Modify `tests/test_review_interaction.cjs`, `tests/test_review_interaction.py`, `tests/browser_check_review.py`.
- Modify `references/content-rules.md`, `references/browser-check.md`, `SKILL.md`.
- Regenerate `복습노트/*/복습문제_*.html` (12개, 자동).

경로는 별도 표기가 없으면 `.agents/skills/bio-review-pack/` 기준이다. 명령은 저장소 루트(`C:\Users\Hyunjun\Desktop\현준대학\26-2\생명과학`)에서 실행한다.

---

### Task 1: 순수 함수 (스냅샷·내보내기 객체·파일명·저장)

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js` (`storageKey` 뒤, `mount` 앞에 함수 추가; 파일 끝 `api`에 이름 추가)
- Test: `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs`

**Interfaces:**
- Produces (모두 `ReviewInteraction`/`module.exports`로 노출):
  - `exportKey(documentId: string): string`
  - `readSnapshot(storage, key): {schema:1, cards:{[id]: {selected: string|null, updatedAt: string|null}}}` — 저장소 오류·손상 시 `{schema:1, cards:{}}`
  - `writeSnapshot(storage, key, snapshot): void` — 오류는 삼킨다
  - `updateSnapshot(snapshot, selectedById: {[id]: string|null}, ids: string[], now: Date): snapshot` — 새 객체를 돌려준다. 이미 같은 `selected`면 `updatedAt`을 유지하고, 다르면 `selected===null ? null : now.toISOString()`
  - `buildExport(model, snapshot, meta: {ids: string[], titles: {[id]: string}, range: string, now: Date}): object` — 스키마는 spec 참고
  - `exportFilename(documentId: string, now: Date): string`
  - `saveExport(win, text: string, filename: string): Promise<'saved'|'downloaded'|'cancelled'>`
- Consumes: 기존 `grade(card, selected)`(review-interaction.js:19)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_review_interaction.cjs` 맨 끝에 추가:

```js

const model = {
  documentId: 'd.html', skipped: ['s1'],
  cards: {
    p10: {version:'v', mode:'single', answer:'2', options:[{id:'1'}, {id:'2'}]},
    p2: {version:'v', mode:'single', answer:'1', options:[{id:'1'}, {id:'2'}]},
    p3: {version:'v', mode:'ambiguous', answer:'1', options:[{id:'1'}, {id:'2'}]},
    p4: {version:'v', mode:'single', answer:'1', options:[{id:'1'}, {id:'2'}]}
  }
};
const T0 = new Date('2026-09-30T05:00:00.000Z');
const T1 = new Date('2026-09-30T05:01:00.000Z');

test('내보내기 파일 이름은 로컬 시각 기준', () => {
  assert.equal(api.exportFilename('복습문제_0929_Heredity.html', new Date(2026, 8, 30, 14, 3)),
    '복습문제_0929_Heredity_풀이기록_20260930-1403.json');
  assert.equal(api.exportFilename('a.htm', new Date(2026, 0, 2, 3, 4)), 'a_풀이기록_20260102-0304.json');
});

test('문서별 스냅샷 키', () => {
  assert.notEqual(api.exportKey('a.html'), api.exportKey('b.html'));
  assert.ok(api.exportKey('a.html').startsWith('od-review-export:v1:'));
});

test('손상·차단된 스냅샷 저장소는 빈 스냅샷', () => {
  for (const raw of ['{', 'null', '[]', '{"schema":2,"cards":{}}', '{"schema":1,"cards":[]}']) {
    assert.deepEqual(api.readSnapshot({getItem:()=>raw}, 'k'), {schema:1, cards:{}});
  }
  const blocked = {getItem(){throw Error('blocked')}, setItem(){throw Error('blocked')}};
  assert.deepEqual(api.readSnapshot(blocked, 'k'), {schema:1, cards:{}});
  assert.deepEqual(api.readSnapshot(null, 'k'), {schema:1, cards:{}});
  assert.doesNotThrow(() => api.writeSnapshot(blocked, 'k', {schema:1, cards:{}}));
  assert.doesNotThrow(() => api.writeSnapshot(null, 'k', {schema:1, cards:{}}));
});

test('스냅샷 저장과 복원', () => {
  const data = new Map();
  const storage = {getItem:k=>data.get(k), setItem:(k,v)=>data.set(k,v)};
  const snap = api.updateSnapshot({schema:1, cards:{}}, {p2:'1'}, ['p2'], T0);
  api.writeSnapshot(storage, 'k', snap);
  assert.deepEqual(api.readSnapshot(storage, 'k'), snap);
});

test('스냅샷 갱신: 같은 답은 시각 유지, 바뀌면 새 시각, 초기화하면 null', () => {
  let snap = api.updateSnapshot({schema:1, cards:{}}, {p2:'1'}, ['p2'], T0);
  assert.deepEqual(snap.cards.p2, {selected:'1', updatedAt:T0.toISOString()});
  snap = api.updateSnapshot(snap, {p2:'1'}, ['p2'], T1);
  assert.equal(snap.cards.p2.updatedAt, T0.toISOString());
  snap = api.updateSnapshot(snap, {p2:'2'}, ['p2'], T1);
  assert.deepEqual(snap.cards.p2, {selected:'2', updatedAt:T1.toISOString()});
  snap = api.updateSnapshot(snap, {p2:null}, ['p2'], T1);
  assert.deepEqual(snap.cards.p2, {selected:null, updatedAt:null});
  const before = {schema:1, cards:{}};
  api.updateSnapshot(before, {p2:'1'}, ['p2'], T0);
  assert.deepEqual(before, {schema:1, cards:{}}, '입력 스냅샷은 바꾸지 않는다');
});

test('스냅샷 갱신: selectedById에 없는 문항은 안 푼 것', () => {
  const snap = api.updateSnapshot({schema:1, cards:{}}, {}, ['p2'], T0);
  assert.deepEqual(snap.cards.p2, {selected:null, updatedAt:null});
});

test('내보내기: DOM 순서·안 푼 문제 null·요약', () => {
  let snap = {schema:1, cards:{}};
  snap = api.updateSnapshot(snap, {p2:'1', p10:'1', p3:'2'}, ['p2', 'p10', 'p3', 'p4'], T0);
  const out = api.buildExport(model, snap, {
    ids:['p2', 'p3', 'p4', 'p10'],
    titles:{p2:'둘째', p3:'셋째', p4:'넷째', p10:'열째'},
    range:'0929', now:T1
  });
  assert.equal(out.schema, 1);
  assert.equal(out.documentId, 'd.html');
  assert.equal(out.range, '0929');
  assert.equal(out.exportedAt, T1.toISOString());
  assert.deepEqual(out.skipped, ['s1']);
  assert.deepEqual(out.cards.map(c => c.id), ['p2', 'p3', 'p4', 'p10']);
  assert.deepEqual(out.cards[0], {id:'p2', title:'둘째', selected:'1', answer:'1', result:'correct', updatedAt:T0.toISOString()});
  assert.equal(out.cards[1].result, 'ambiguous');
  assert.deepEqual(out.cards[2], {id:'p4', title:'넷째', selected:null, answer:'1', result:null, updatedAt:null});
  assert.equal(out.cards[3].result, 'incorrect');
  assert.deepEqual(out.summary, {total:4, answered:3, unanswered:1, correct:1, incorrect:1, ambiguous:1});
});

test('내보내기: 스냅샷의 없는 보기·누락 항목은 안 푼 것', () => {
  const snap = {schema:1, cards:{p2:{selected:'X', updatedAt:T0.toISOString()}}};
  const out = api.buildExport(model, snap, {ids:['p2', 'p4'], titles:{}, range:'', now:T1});
  assert.equal(out.cards[0].selected, null);
  assert.equal(out.cards[0].updatedAt, null);
  assert.equal(out.cards[0].title, '');
  assert.equal(out.summary.answered, 0);
  assert.equal(out.summary.unanswered, 2);
});

function fakeWin(picker) {
  const log = {clicks:0, appended:0};
  const anchor = {click(){log.clicks++}, remove(){}};
  const win = {
    URL:{createObjectURL:() => 'blob:x', revokeObjectURL(){}},
    Blob: class { constructor(parts){ this.parts = parts; } },
    setTimeout: () => 0,
    document:{createElement:() => anchor, body:{append(){log.appended++}}}
  };
  if (picker) win.showDirectoryPicker = picker;
  return {win, log, anchor};
}

test('폴더 선택창으로 저장', async () => {
  const written = {};
  const picker = async () => ({
    async getFileHandle(name, opts) {
      written.name = name; written.opts = opts;
      return {async createWritable() { return {async write(t){ written.text = t; }, async close(){ written.closed = true; }}; }};
    }
  });
  const {win, log} = fakeWin(picker);
  assert.equal(await api.saveExport(win, '{"a":1}', 'f.json'), 'saved');
  assert.deepEqual(written, {name:'f.json', opts:{create:true}, text:'{"a":1}', closed:true});
  assert.equal(log.clicks, 0);
});

test('선택창 취소는 아무것도 저장하지 않음', async () => {
  const picker = async () => { const e = new Error('cancel'); e.name = 'AbortError'; throw e; };
  const {win, log} = fakeWin(picker);
  assert.equal(await api.saveExport(win, '{}', 'f.json'), 'cancelled');
  assert.equal(log.clicks, 0);
});

test('폴더 API 거부·미지원이면 다운로드로 대체', async () => {
  const denied = async () => { const e = new Error('no'); e.name = 'SecurityError'; throw e; };
  for (const picker of [denied, undefined]) {
    const {win, log, anchor} = fakeWin(picker);
    assert.equal(await api.saveExport(win, '{}', 'f.json'), 'downloaded');
    assert.equal(log.clicks, 1);
    assert.equal(anchor.download, 'f.json');
  }
});
```

- [ ] **Step 2: 실패 확인**

Run: `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Expected: 새 테스트가 `api.exportFilename is not a function` 등으로 FAIL(기존 테스트는 PASS).

- [ ] **Step 3: 최소 구현**

`assets/review-interaction.js`에서 `writeAttempt` 함수 끝(`}` 다음 줄), `function mount(` 앞에 삽입:

```js
  function exportKey(documentId) {
    return 'od-review-export:v1:' + encodeURIComponent(documentId);
  }
  function readSnapshot(storage, key) {
    const empty = () => ({schema:1, cards:{}});
    try {
      const value = JSON.parse(storage.getItem(key));
      return value && value.schema === 1 && value.cards && typeof value.cards === 'object' && !Array.isArray(value.cards)
        ? value : empty();
    } catch { return empty(); }
  }
  function writeSnapshot(storage, key, snapshot) {
    try { storage.setItem(key, JSON.stringify(snapshot)); } catch {}
  }
  function updateSnapshot(snapshot, selectedById, ids, now) {
    const cards = Object.assign({}, snapshot.cards);
    for (const id of ids) {
      const selected = selectedById[id] === undefined ? null : selectedById[id];
      const prev = cards[id];
      if (prev && prev.selected === selected) continue;
      cards[id] = {selected, updatedAt: selected === null ? null : now.toISOString()};
    }
    return {schema:1, cards};
  }
  function buildExport(model, snapshot, meta) {
    const counts = {correct:0, incorrect:0, ambiguous:0};
    const cards = meta.ids.map(id => {
      const data = model.cards[id];
      const entry = snapshot.cards[id] || {};
      const result = grade(data, entry.selected);
      if (result !== null) counts[result] += 1;
      return {
        id, title: meta.titles[id] || '',
        selected: result === null ? null : entry.selected,
        answer: data.answer, result,
        updatedAt: result === null ? null : (entry.updatedAt || null)
      };
    });
    const answered = counts.correct + counts.incorrect + counts.ambiguous;
    return {
      schema:1, documentId:model.documentId, range:meta.range, exportedAt:meta.now.toISOString(),
      summary:{total:cards.length, answered, unanswered:cards.length - answered,
        correct:counts.correct, incorrect:counts.incorrect, ambiguous:counts.ambiguous},
      skipped: model.skipped || [], cards
    };
  }
  function exportFilename(documentId, now) {
    const p = n => String(n).padStart(2, '0');
    const stamp = now.getFullYear() + p(now.getMonth() + 1) + p(now.getDate()) +
      '-' + p(now.getHours()) + p(now.getMinutes());
    return documentId.replace(/\.html?$/i, '') + '_풀이기록_' + stamp + '.json';
  }
  async function saveExport(win, text, filename) {
    if (typeof win.showDirectoryPicker === 'function') {
      try {
        const dir = await win.showDirectoryPicker({mode:'readwrite'});
        const file = await dir.getFileHandle(filename, {create:true});
        const out = await file.createWritable();
        await out.write(text);
        await out.close();
        return 'saved';
      } catch (error) {
        if (error && error.name === 'AbortError') return 'cancelled';
      }
    }
    const url = win.URL.createObjectURL(new win.Blob([text], {type:'application/json'}));
    const a = win.document.createElement('a');
    a.href = url;
    a.download = filename;
    win.document.body.append(a);
    a.click();
    a.remove();
    win.setTimeout(() => win.URL.revokeObjectURL(url), 1000);
    return 'downloaded';
  }
```

파일 끝의 `api` 줄을 교체:

```js
  const api = {stripDiagnosticPrefix, grade, storageKey, readAttempt, writeAttempt, mount,
    exportKey, readSnapshot, writeSnapshot, updateSnapshot, buildExport, exportFilename, saveExport};
```

- [ ] **Step 4: 통과 확인**

Run: `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Expected: 전부 PASS.

- [ ] **Step 5: 이미 만들어진 복습문제에 새 JS 반영**

Run:
```bash
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write
python -m pytest .agents/skills/bio-review-pack/tests -q
```
Expected: 12개 파일 각 줄에 `errors: []`, pytest 전부 PASS(특히 `test_existing_packs_embed_current_interaction_assets`).

- [ ] **Step 6: Commit**

먼저 앞선 세션의 `sessionStorage` 전환 작업이 미커밋 상태이므로 따로 커밋한다(이미 커밋돼 있으면 건너뜀).

```bash
git status --short
git add -u .agents/skills/bio-review-pack 복습노트
git reset .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/test_review_interaction.cjs
git commit -m "fix: keep review answers in sessionStorage so reopening starts fresh"
git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/test_review_interaction.cjs 복습노트
git commit -m "feat: add answer snapshot and export helpers for review packs"
```

주의: 두 번째 커밋에 담기는 `복습노트/*.html`은 위 첫 커밋 이후 재주입된 변경분이다. 이미 첫 커밋에 포함돼 남은 변경이 없으면 `복습노트`는 빼고 커밋한다.

---

### Task 2: 페이저가 화면을 벗어날 때 `od:leave` 발생

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-template.html:747` (`render()` 안)
- Modify: `.agents/skills/bio-review-pack/scripts/review_interaction.py` (`patch_review_shell` 다음에 `patch_pager_shell` 추가, `install()`에서 호출)
- Test: `.agents/skills/bio-review-pack/tests/test_review_interaction.py`

**Interfaces:**
- Produces: `document`에 `CustomEvent('od:leave', {detail:{index:number, screen:Element}})` — 카드·히어로 화면을 벗어날 때(이동 방식과 무관하게) 새 화면 전환 직전에 발생. 처음 렌더(`cur < 0`)에서는 발생하지 않는다.
- Produces: `review_interaction.patch_pager_shell(source: str) -> str` — 멱등. 페이저 스크립트(`<script id="pager-ui">`)가 없으면 그대로 반환.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_review_interaction.py`에서 `test_install_idempotent`(52행) 바로 뒤에 추가한다(`CARD`, `ri`, `REPO`는 파일 상단에 이미 있음):

```python
    def test_install_adds_pager_leave_event_once(self):
        pager = ('<script id="pager-ui">\n      function render(i, target) {\n        if (i !== cur) {\n'
                 "          if (cur >= 0) screens[cur].classList.remove('is-current', 'enter-next', 'enter-prev');\n"
                 '        }\n      }\n</script>')
        source = '<html><body>' + CARD + pager + '</body></html>'
        output = ri.install(source, 'test.html')
        marker = "detail: { index: cur, screen: screens[cur] }"
        self.assertEqual(output.count(marker), 1)
        self.assertLess(output.index(marker), output.index("screens[cur].classList.remove"))
        self.assertEqual(ri.install(output, 'test.html'), output)

    def test_pager_patch_leaves_pages_without_pager_alone(self):
        source = '<html><body>' + CARD + '</body></html>'
        self.assertEqual(ri.patch_pager_shell(source), source)

    def test_pager_patch_rejects_unknown_pager_structure(self):
        with self.assertRaises(ValueError):
            ri.patch_pager_shell('<script id="pager-ui">function render(){}</script>')

    def test_review_template_already_has_pager_leave_event(self):
        template = (SKILL / 'assets/review-template.html').read_text(encoding='utf-8')
        self.assertEqual(ri.patch_pager_shell(template), template)
        self.assertEqual(template.count("detail: { index: cur, screen: screens[cur] }"), 1)
```

파일 상단 import에 `SKILL`이 없으면 추가한다: `from _util import REPO, SKILL`(현재 `from _util import REPO`만 있다면 이 줄로 교체).

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest .agents/skills/bio-review-pack/tests/test_review_interaction.py -q`
Expected: 새 4개가 `AttributeError: ... patch_pager_shell` 등으로 FAIL.

- [ ] **Step 3: 구현**

`scripts/review_interaction.py`의 `ANSWER_EVENT = ...` 아래(`def patch_review_shell` 앞)에 추가:

```python
LEAVE_ANCHOR = "          if (cur >= 0) screens[cur].classList.remove('is-current', 'enter-next', 'enter-prev');\n"
LEAVE_LINE = ("          if (cur >= 0) document.dispatchEvent(new CustomEvent('od:leave', "
              "{ detail: { index: cur, screen: screens[cur] } }));\n")
```

`patch_review_shell` 함수 다음에 추가:

```python
def patch_pager_shell(source: str) -> str:
    if '<script id="pager-ui">' not in source or "detail: { index: cur, screen: screens[cur] }" in source:
        return source
    if source.count(LEAVE_ANCHOR) != 1:
        raise ValueError('pager 화면 전환 구조 불일치')
    return source.replace(LEAVE_ANCHOR, LEAVE_LINE + LEAVE_ANCHOR)
```

`install()`의 `source = patch_review_shell(source)` 줄 바로 아래에 추가:

```python
    source = patch_pager_shell(source)
```

`assets/review-template.html`의 747행 `if (cur >= 0) screens[cur].classList.remove(...)` 줄 **바로 위에** 같은 들여쓰기(10칸)로 삽입:

```html
          if (cur >= 0) document.dispatchEvent(new CustomEvent('od:leave', { detail: { index: cur, screen: screens[cur] } }));
```

- [ ] **Step 4: 통과 확인 + 기존 복습문제 재주입**

Run:
```bash
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write
python -m pytest .agents/skills/bio-review-pack/tests -q
```
Expected: 12개 파일 `errors: []`, pytest 전부 PASS. 재주입 뒤 `git diff --stat 복습노트`에서 파일마다 `od:leave` 한 줄이 늘어난 것이 보인다.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/bio-review-pack/assets/review-template.html .agents/skills/bio-review-pack/scripts/review_interaction.py .agents/skills/bio-review-pack/tests/test_review_interaction.py 복습노트
git commit -m "feat: emit od:leave when the review pager leaves a screen"
```

---

### Task 3: 스냅샷 갱신과 내보내기 버튼 연결

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js` (`mount()` 안)
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.css` (파일 끝의 `@media print` 앞)
- Test: `.agents/skills/bio-review-pack/tests/browser_check_review.py`

**Interfaces:**
- Consumes: Task 1의 `exportKey, readSnapshot, writeSnapshot, updateSnapshot, buildExport, exportFilename, saveExport`, Task 2의 `od:leave`(`detail.screen.id`).
- Produces (DOM): `.pager` 첫 자식 `div.review-export-bar` > `button.review-export`("JSON 내보내기") + `p.review-export-note[role=status]`. `body.at-end`가 아니면 CSS로 숨긴다.
- Produces (저장소): `sessionStorage['od-review-export:v1:<documentId>']` = 스냅샷 JSON.

- [ ] **Step 1: 실패하는 브라우저 테스트 작성**

`tests/browser_check_review.py`의 `TestReviewBrowser` 클래스 안, `test_storage_blocked`(280행) 바로 앞에 추가:

```python
    PICKER_MOCK = """
      window.__saved = null;
      window.showDirectoryPicker = async () => ({
        async getFileHandle(name) {
          return { async createWritable() {
            let text = '';
            return { async write(t) { text += t; }, async close() { window.__saved = { name, text }; } };
          } };
        }
      });
    """

    def last_card_id(self):
        return self.page.evaluate("Array.from(document.querySelectorAll('main article.card')).pop().id")

    def go_to_last(self):
        last = self.last_card_id()
        self.page.evaluate("id => { location.hash = '#' + id; }", last)
        expect(self.page.locator('#' + last)).to_be_visible()
        return last

    def test_leaving_a_card_updates_snapshot(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        self.assertIsNone(self.page.evaluate("sessionStorage.getItem(Object.keys(sessionStorage).find(k => k.startsWith('od-review-export:v1:')))"))
        self.page.locator('#pager-next').click()
        snap = self.page.evaluate("JSON.parse(sessionStorage.getItem(Object.keys(sessionStorage).find(k => k.startsWith('od-review-export:v1:'))))")
        self.assertEqual(snap['schema'], 1)
        self.assertIsNotNone(snap['cards']['p1']['selected'])
        self.assertIsNotNone(snap['cards']['p1']['updatedAt'])

    def test_export_button_only_on_last_screen(self):
        self.open()
        expect(self.page.locator('.review-export')).to_be_hidden()
        self.go_to_last()
        expect(self.page.locator('.review-export')).to_be_visible()
        expect(self.page.locator('.review-export')).to_have_text('JSON 내보내기')

    def test_export_to_chosen_folder(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('고른 폴더에 저장했어요.')
        saved = self.page.evaluate('window.__saved')
        self.assertRegex(saved['name'], r'^복습문제_0929_Heredity_풀이기록_\d{8}-\d{4}\.json$')
        data = __import__('json').loads(saved['text'])
        dom_ids = self.page.evaluate("Array.from(document.querySelectorAll('main article.card')).map(e => e.id)")
        self.assertEqual([c['id'] for c in data['cards']], [i for i in dom_ids if i in {c['id'] for c in data['cards']}])
        self.assertEqual(data['summary']['total'], len(data['cards']))
        self.assertEqual(data['summary']['answered'], 1)
        self.assertEqual(data['summary']['unanswered'], data['summary']['total'] - 1)
        first = data['cards'][0]
        self.assertEqual(first['id'], 'p1')
        self.assertIsNotNone(first['selected'])
        self.assertIsNotNone(first['updatedAt'])
        self.assertIsNone(data['cards'][-1]['selected'])

    def test_export_reflects_reset(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        card.locator('.review-reset').click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('고른 폴더에 저장했어요.')
        data = __import__('json').loads(self.page.evaluate('window.__saved.text'))
        self.assertEqual(data['summary']['answered'], 0)
        self.assertIsNone(data['cards'][0]['selected'])

    def test_export_cancel_saves_nothing(self):
        self.context.add_init_script("""
          window.showDirectoryPicker = async () => { const e = new Error('cancel'); e.name = 'AbortError'; throw e; };
        """)
        self.open()
        self.go_to_last()
        downloads = []
        self.page.on('download', lambda d: downloads.append(d))
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('저장을 취소했어요.')
        self.assertEqual(downloads, [])

    def test_export_falls_back_to_download(self):
        self.context.add_init_script("""
          window.showDirectoryPicker = async () => { const e = new Error('no'); e.name = 'SecurityError'; throw e; };
        """)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        with self.page.expect_download() as info:
            self.page.locator('.review-export').click()
        download = info.value
        self.assertRegex(download.suggested_filename, r'\.json$')
        data = __import__('json').loads(Path(download.path()).read_text(encoding='utf-8'))
        self.assertEqual(data['summary']['answered'], 1)
        expect(self.page.locator('.review-export-note')).to_have_text('다운로드 폴더에 저장했어요.')

    def test_export_with_storage_blocked(self):
        self.context.add_init_script(
            "for(const n of ['localStorage','sessionStorage']) Object.defineProperty(window,n,{get(){throw Error('blocked')}});")
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('고른 폴더에 저장했어요.')
        data = __import__('json').loads(self.page.evaluate('window.__saved.text'))
        self.assertEqual(data['summary']['answered'], 1)

    def test_snapshot_does_not_survive_a_new_tab(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        self.page.locator('#pager-next').click()
        other = self.context.new_page()
        other.goto(self.url('0929'))
        self.assertEqual(other.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('od-review-export:'))"), [])
        other.close()
```

- [ ] **Step 2: 실패 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py -k export`
Expected: `test_export_*`와 `test_leaving_a_card_updates_snapshot`이 FAIL(버튼·스냅샷이 아직 없음). `test_snapshot_does_not_survive_a_new_tab`은 이미 PASS일 수 있다.

- [ ] **Step 3: `mount()`에 연결**

`assets/review-interaction.js`에서:

(a) `mount()` 안 `let feedback = null;`(약 55행) 바로 위에 추가:

```js
    const selectedById = {};
```

(b) 카드 루프 안 `let selected = readAttempt(storage, key, data);` 다음 줄에 추가:

```js
        selectedById[id] = selected;
```

(c) 보기 클릭 핸들러에서 `selected = c.id;` 다음 줄에 추가:

```js
          selectedById[id] = selected;
```

(d) 다시 풀기 핸들러에서 `selected = null;` 다음 줄에 추가:

```js
          selectedById[id] = null;
```

(e) 카드 루프가 끝난 뒤, `// Existing page CSS hides side panels when printing.` 주석 바로 위에 추가:

```js
    const exportCards = Array.from(root.querySelectorAll('main article.card')).filter(el => model.cards[el.id]);
    const pager = root.querySelector('.pager');
    if (exportCards.length && pager && !pager.querySelector('.review-export-bar')) {
      const ids = exportCards.map(el => el.id);
      const titles = {};
      exportCards.forEach(el => { titles[el.id] = ((el.querySelector('h3') || {}).textContent || '').trim(); });
      const snapKey = exportKey(model.documentId);
      let snapshot = readSnapshot(storage, snapKey);
      root.addEventListener('od:leave', ({detail}) => {
        const id = detail && detail.screen && detail.screen.id;
        if (!model.cards[id]) return;
        snapshot = updateSnapshot(snapshot, selectedById, [id], new Date());
        writeSnapshot(storage, snapKey, snapshot);
      });
      const bar = element('div', 'review-export-bar');
      const button = element('button', 'btn btn-primary review-export', 'JSON 내보내기');
      button.type = 'button';
      const note = element('p', 'review-export-note');
      note.setAttribute('role', 'status');
      note.setAttribute('aria-live', 'polite');
      bar.append(button, note);
      pager.prepend(bar);
      root.addEventListener('od:screen', () => { note.textContent = ''; });
      button.addEventListener('click', async () => {
        const now = new Date();
        snapshot = updateSnapshot(snapshot, selectedById, ids, now);
        writeSnapshot(storage, snapKey, snapshot);
        const data = buildExport(model, snapshot, {ids, titles, range: root.body.dataset.range || '', now});
        const outcome = await saveExport(win, JSON.stringify(data, null, 2) + '\n', exportFilename(model.documentId, now));
        note.textContent = outcome === 'saved' ? '고른 폴더에 저장했어요.'
          : outcome === 'downloaded' ? '다운로드 폴더에 저장했어요.' : '저장을 취소했어요.';
      });
    }
```

- [ ] **Step 4: CSS**

`assets/review-interaction.css`의 마지막 `@media print {` 블록 바로 위에 추가하고, 그 블록 안 첫 줄로 `.review-export-bar { display:none !important; }`도 넣는다:

```css
.review-export-bar {
  display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:12px;
  max-width:var(--measure); margin:0 auto; padding:12px 16px 0;
}
body:not(.at-end) .review-export-bar { display:none; }
.review-export-note { margin:0; font-size:var(--fs-small); color:var(--ink-2); }
.review-export-note:empty { display:none; }
```

`@media print { ... }` 안 첫 줄:

```css
  .review-export-bar { display:none !important; }
```

- [ ] **Step 5: 재주입 후 전체 확인**

Run:
```bash
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write
python -m pytest .agents/skills/bio-review-pack/tests -q
node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs
python .agents/skills/bio-review-pack/tests/browser_check_review.py
```
Expected: 모두 PASS. 브라우저 테스트가 하나라도 FAIL이면 그 문제를 고친 뒤 이 단계를 다시 실행한다.

- [ ] **Step 6: 실제 Chrome에서 수동 확인**

브라우저로 `복습노트/0929/복습문제_0929_Heredity.html`을 열어 1) 문제 몇 개를 풀고 마지막 문제로 이동 2) "JSON 내보내기" → 폴더 선택 3) 저장된 파일을 열어 답·`unanswered` 확인 4) 탭을 닫고 다시 열어 기록이 없는지 확인한다. `Downloads`를 고르면 Chrome이 거부해 다운로드로 대체되는지도 본다. 결과를 최종 보고에 그대로 적는다.

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/bio-review-pack/assets .agents/skills/bio-review-pack/tests/browser_check_review.py 복습노트
git commit -m "feat: export review answers as JSON from the last screen"
```

---

### Task 4: 스킬 문서 갱신

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/content-rules.md:73`
- Modify: `.agents/skills/bio-review-pack/references/browser-check.md:72`
- Modify: `.agents/skills/bio-review-pack/SKILL.md:141`
- Test: `.agents/skills/bio-review-pack/tests/test_skill_files.py` (기존)

**Interfaces:** 없음. 문서만 수정한다.

- [ ] **Step 1: `content-rules.md`**

`(테마·패널 너비 같은 화면 설정만 `localStorage`).` 바로 뒤에 이어 붙인다:

```
 문제 화면을 벗어날 때마다(다음·이전·목차·방향키·스와이프) 그 문제의 고른 답·정오·시각을 `sessionStorage` 스냅샷(`od-review-export:v1:<문서>`)에 갱신하고, 마지막 문제 화면에서만 보이는 **JSON 내보내기** 버튼이 Chrome 폴더 선택창(`showDirectoryPicker`)으로 `<파일명>_풀이기록_<YYYYMMDD-HHmm>.json`을 저장한다. 폴더 API가 거부·미지원이면 다운로드로 대체하고, 선택창을 취소하면 저장하지 않는다. 안 푼 문제도 `selected: null`로 전체를 문서 순서대로 넣는다. 확인용 기록이라 불러오기 기능은 없다.
```

- [ ] **Step 2: `browser-check.md`**

`새 탭에서 다시 열면 푼 흔적이 없다(...)` 줄 바로 아래에 추가:

```
- 마지막 문제 화면에서만 **JSON 내보내기** 버튼이 보인다. 클릭하면 폴더 선택창으로 저장하고(취소하면 저장 없음, 폴더 API가 거부되면 다운로드), 파일에는 모든 문제가 문서 순서로 들어 있고 안 푼 문제는 `selected: null`이다. 저장소가 막혀도 내보내기가 된다.
```

- [ ] **Step 3: `SKILL.md`**

`(`localStorage` 사용 금지).` 뒤에 이어 붙인다:

```
 마지막 문제 화면의 **JSON 내보내기** 버튼(폴더 선택창 저장, 취소·거부 처리)과 화면을 벗어날 때의 스냅샷 갱신도 함께 확인한다.
```

- [ ] **Step 4: 확인**

Run: `python -m pytest .agents/skills/bio-review-pack/tests -q`
Expected: 전부 PASS.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/bio-review-pack/references .agents/skills/bio-review-pack/SKILL.md docs/superpowers/specs/2026-09-30-bio-review-answer-export-design.md docs/superpowers/plans/2026-10-01-bio-review-answer-export.md
git commit -m "docs: document review answer JSON export"
```

---

## Self-Review 메모

- **Spec 범위:** 스냅샷 갱신(Task 2·3), 마지막 화면 버튼(Task 3), 폴더 선택창·다운로드 대체·취소(Task 1·3), 전체 포함·`null`(Task 1·3), 확인용·초기화(별도 코드 없음, Task 3 새 탭 테스트로 확인), 파일명(Task 1), 문서(Task 4)를 모두 다룬다.
- **이름 일관성:** `exportKey/readSnapshot/writeSnapshot/updateSnapshot/buildExport/exportFilename/saveExport`를 Task 1에서 정의하고 Task 3에서 그대로 쓴다. 이벤트 `od:leave`의 `detail.screen`도 Task 2·3이 같다.
- **알려진 한계:** Chrome은 `Downloads`·홈 같은 일부 폴더를 선택창에서 거부한다(이때 다운로드로 대체). 폴더 API의 실제 폴더 쓰기는 Playwright에서 자동화하기 어려워 모의 객체로 검증하고, Task 3 Step 6에서 실제 Chrome으로 확인한다.
