# 복습노트 `.assets/` 정리 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `복습노트/<range>/` 맨 위에는 `.pack/`과 HTML만 남기고 나머지는 `.assets/`로 옮긴다. 이 폴더를 쓰거나 읽는 모든 스킬과 기존 12개 날짜 폴더를 새 구조에 맞춘다.

**Architecture:** 경로 규칙은 순수 함수 두 개로 정한다. `relocate`는 날짜 폴더 기준 URL을 새 위치로 옮기고, `rebase_md`는 날짜 폴더 기준 MD 링크를 `.assets/` 기준으로 바꾼다. 두 함수는 `bio-review-pack/scripts/assets_path.py`에 두고 bio-problem-explain에는 vendor 사본을 둔다. 생성기(review-pack html2md, problem-explain)는 MD를 날짜 폴더 기준으로 만든 뒤 `rebase_md`를 한 번 적용한다. 이전 스크립트는 같은 함수로 기존 HTML·MD 링크를 고친다. 나머지 스킬은 경로 상수와 문서만 바꾼다.

**Tech Stack:** Python 3 표준 라이브러리(unittest; bio-problem-explain만 pytest, `uvx pytest`로 실행), Node 20+(CommonJS, `node:test`). 새 의존성은 없다.

**Spec:** `docs/superpowers/specs/2026-10-13-review-assets-folder-design.md`

## Global Constraints
- 부속 폴더 이름은 모든 날짜 폴더에서 고정값 `.assets`다. 하위 이름(`figures_<range>`, `자료_문제설명_…`, `자료_인터렉티브_NN_…`, `풀이기록`, `<원래 이름>.md`)은 바꾸지 않는다.
- 날짜 폴더 루트에 남는 것은 `*.html`, `.pack/`, `.assets/`, `.DS_Store`뿐이다.
- 범위는 `복습노트/`뿐이다. `예습노트/`, `웹과제예상/`(forecast), homework 프로필 출력은 바꾸지 않는다. html2md의 `Ctx`·`convert` 기본 동작도 그대로 둔다(preview-note가 쓴다).
- 파일명 비교는 NFC로 한다(macOS는 한글 이름을 NFD로 저장한다).
- 문서(SKILL.md, references)에는 `.assets`를 글자 그대로 쓴 경로만 적는다. `**/정리노트_*.md`처럼 숨김 폴더를 건너뛰는 패턴은 쓰지 않는다. Python에서 `glob.glob('*')`는 dot 항목을 빼므로 `.assets`를 명시하거나 `pathlib`을 쓴다.
- 커밋 메시지는 Conventional Commits 형식이고, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`을 붙인다.
- 테스트 명령은 다음과 같다(저장소 루트 기준).
  - review-pack: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
  - problem-explain: `uvx --quiet pytest -q .agents/skills/bio-problem-explain/tests`
  - interactive: `node --test .agents/skills/bio-interactive/tests/*.test.cjs`
  - cheatsheet, preview-note, webquiz-forecast, review-video: `python3 -m unittest discover -s .agents/skills/<skill>/tests`
  - 저장소: `python3 -m unittest discover tests`

## Review Focus
1. NFD로 저장된 이름과 %-인코딩된 링크(`%EB%B3%B5…html#p1`)가 있어도 `relocate`·`rebase_md`가 판정은 디코드·NFC로 하고, 원래 인코딩은 보존해야 한다. → Task 1 테스트 `test_relocate_encoded_nfd`, `test_rebase_keeps_encoding`.
2. 이미 이전한 날짜 폴더에 팩을 다시 만들 때 html2md가 `.assets/figures_<range>/`의 고아 SVG를 지우고, 루트에 `figures_*`·`.md`를 새로 만들지 않아야 한다. → Task 2 테스트 `test_convert_pack_rerun_stays_in_assets`.
3. 이전 스크립트를 두 번 돌리거나, `.assets/`가 일부만 있는 폴더에 돌려도 결과가 같아야 한다(`.assets/.assets`나 `.assets/.assets/x` 링크가 생기면 안 됨). → Task 7 테스트 `test_migrate_is_idempotent`, `test_relocate_skips_already_relocated`.
4. 다른 날짜 MD를 가리키는 링크(`../0922/장마감_0922_3장.md`, `../0917/figures_0917/x.svg`)는 상대 날짜 폴더의 `.assets/`로 가야 한다. 다른 날짜 HTML(`../0917/정리노트_….html`)은 그대로 둔다. → Task 1 테스트 `test_relocate_cross_day`.
5. 범위 폴더(`0922-0924`)에서도 interactive 번호 매기기와 풀이기록 수거가 `.assets/`를 써야 한다. → Task 5 테스트 `nextNumber counts .assets data folders in a range folder`, Task 3 테스트 `test_moves_json_into_range_folder_assets`.

---

### Task 1: 경로 규칙 모듈 `assets_path`

**Files:**
- Create: `.agents/skills/bio-review-pack/scripts/assets_path.py`
- Create: `.agents/skills/bio-problem-explain/scripts/vendor/assets_path.py` (위 파일과 바이트까지 같은 사본)
- Test: `.agents/skills/bio-review-pack/tests/test_assets_path.py`

**Interfaces:**
- Produces:
  - `SIDE: str = ".assets"`
  - `moves(name: str) -> bool`: 날짜 폴더 바로 아래 항목이 `.assets/`로 가는지 판정한다. 이름을 NFC로 바꾼 뒤 `.html`/`.htm`으로 끝나지 않고 `.pack`, `.assets`, `.DS_Store`, `""`이 아니면 True다.
  - `relocate(url: str) -> str`: 날짜 폴더 HTML/MD 기준 상대 URL을 이전 뒤 위치로 바꾼다.
  - `rebase_md(text: str) -> str`: 날짜 폴더 기준으로 쓰인 MD의 모든 `](target)`을 `.assets/` 안 MD 기준으로 바꾼다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```python
class TestAssetsPath(unittest.TestCase):
    def test_moves(self):
        for n in ("정리노트_1001_X.md", "figures_1001", "자료_문제설명_1001_X", "풀이기록", "장마감_1001_4장.md"):
            self.assertTrue(moves(n), n)
        for n in ("정리노트_1001_X.html", ".pack", ".assets", ".DS_Store", ""):
            self.assertFalse(moves(n), n)
        self.assertTrue(moves(unicodedata.normalize("NFD", "장마감_1001_4장.md")))

    def test_relocate_same_day(self):
        self.assertEqual(relocate("figures_0922/p37.png"), ".assets/figures_0922/p37.png")
        self.assertEqual(relocate("./자료_문제설명_0903_X/vendor/katex/katex.min.css"), ".assets/자료_문제설명_0903_X/vendor/katex/katex.min.css")
        self.assertEqual(relocate("정리노트_1001_X.html#s1"), "정리노트_1001_X.html#s1")
        self.assertEqual(relocate("복습문제_1001_X.md#p3"), ".assets/복습문제_1001_X.md#p3")
        for u in ("#s1", "https://a.b/c.png", "/abs/x.png", "data:image/png;base64,AA", "", "../../웹과제/4장/x.json"):
            self.assertEqual(relocate(u), u)

    def test_relocate_encoded_nfd(self):
        enc = quote(unicodedata.normalize("NFD", "figures_문제설명_0903_X") + "/a.png")
        self.assertEqual(relocate(enc), ".assets/" + enc)
        html = quote("복습문제_1001_X.html") + "#p1"
        self.assertEqual(relocate(html), html)

    def test_relocate_cross_day(self):
        self.assertEqual(relocate("../0922/장마감_0922_3장.md"), "../0922/.assets/장마감_0922_3장.md")
        self.assertEqual(relocate("../0917/figures_0917/x.svg"), "../0917/.assets/figures_0917/x.svg")
        self.assertEqual(relocate("../0922-0924/figures_0922-0924/x.svg"), "../0922-0924/.assets/figures_0922-0924/x.svg")
        self.assertEqual(relocate("../0917/정리노트_0917_X.html#s2"), "../0917/정리노트_0917_X.html#s2")

    def test_relocate_skips_already_relocated(self):
        for u in (".assets/figures_0922/p37.png", "../0917/.assets/figures_0917/x.svg"):
            self.assertEqual(relocate(u), u)

    def test_rebase(self):
        md = ("![a](.assets/figures_1001/x.svg) [b](정리노트_1001_X.html#s1) [c](../0917/정리노트_0917_X.html) "
              "[d](.assets/복습문제_1001_X.md#p2) [e](#top) [f](https://x.y) ![g](./.assets/figures_1001/p.png)")
        self.assertEqual(rebase_md(md),
              "![a](figures_1001/x.svg) [b](../정리노트_1001_X.html#s1) [c](../../0917/정리노트_0917_X.html) "
              "[d](복습문제_1001_X.md#p2) [e](#top) [f](https://x.y) ![g](figures_1001/p.png)")

    def test_rebase_keeps_encoding(self):
        t = "[원 문제 보기](%EB%B3%B5%EC%8A%B5.html#p1)"
        self.assertEqual(rebase_md(t), "[원 문제 보기](../%EB%B3%B5%EC%8A%B5.html#p1)")
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_assets_path.py -v`
Expected: `ModuleNotFoundError: No module named 'assets_path'`

- [ ] **Step 3: `assets_path.py`에 `SIDE`, `moves`, `relocate`, `rebase_md`를 구현한다**

`relocate`의 순서는 다음과 같다.
1. 빈 값, `#`으로 시작, `/`로 시작, scheme(`^[A-Za-z][A-Za-z0-9+.-]*:`)이면 그대로 둔다.
2. 앞의 `./`를 뗀다.
3. `../<날짜>/<이름>/…` 형태(`<날짜>`는 디코드·NFC 뒤 `\d{4}(-\d{4})?`)이고 `moves(<이름>)`이면 `../<날짜>/.assets/<이름>/…`로 바꾼다. 다른 `../…`는 그대로 둔다.
4. 그 밖에는 첫 조각을 `unquote`·NFC해서 `moves`이면 `.assets/`를 붙인다.

경로 조각은 원문 문자열을 그대로 이어 붙인다. 디코드한 값은 판정에만 쓴다.

`rebase_md`는 정규식 `(\]\()([^)\s]+)(\))`의 target에만 적용한다.
- 외부(scheme·`#`·`/`)는 그대로 둔다.
- 앞의 `./`를 뗀다.
- `.assets/`로 시작하면 그 접두를 뗀다.
- 나머지는 `../`를 붙인다.

`bio-review-pack/scripts/assets_path.py`를 `bio-problem-explain/scripts/vendor/assets_path.py`로 복사한다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_assets_path.py -v`
Expected: 7 tests OK

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-review-pack/scripts/assets_path.py .agents/skills/bio-review-pack/tests/test_assets_path.py .agents/skills/bio-problem-explain/scripts/vendor/assets_path.py
git commit -m "feat(bio-review-pack): add .assets path rules"
```

---

### Task 2: bio-review-pack 조립·MD를 `.assets/`로

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/manifest.py:167-168` (`fig_href` 추가)
- Modify: `.agents/skills/bio-review-pack/scripts/assemble.py:9,115-125` (`copy_figures`)
- Modify: `.agents/skills/bio-review-pack/scripts/html2md.py:1-12,632-675` (`convert_pack`, 모듈 docstring)
- Modify: `.agents/skills/bio-review-pack/references/card-rules.md:15,24`, 그 밖에 `figures_<range>/`나 산출물 위치를 적은 references(`grep -n "figures_\|복습노트/" references/*.md`로 찾는다)
- Modify: `.agents/skills/bio-review-pack/SKILL.md:11,32,42,65,107-119,139-148,175,178,191,210,276`
- Test: `.agents/skills/bio-review-pack/tests/test_assemble.py`, `tests/test_html2md.py`, `tests/test_manifest.py`, `tests/test_skill_files.py`, `tests/fixtures/mini-run/cards/p2.html`

**Interfaces:**
- Consumes: `assets_path.SIDE`, `assets_path.rebase_md` (Task 1)
- Produces:
  - `manifest.fig_href(range_: str) -> str` = `".assets/figures_<range>"`. 카드 `<img src>`의 접두로 쓴다.
  - `html2md.convert_pack(note_path, review_path, only=None) -> (list[str], int)`: 시그니처는 그대로다. 돌려주는 MD 경로가 `<html 폴더>/.assets/<이름>.md`로 바뀐다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`test_html2md.py`의 픽스처 HTML 그림 `src`를 `.assets/figures_<range>/…`로 바꾸고 다음 테스트를 더한다.

```python
def test_convert_pack_writes_into_assets(self):
    (note_md, review_md), figs = html2md.convert_pack(self.note, self.review)
    side = Path(self.note).parent / ".assets"
    self.assertEqual(Path(note_md).parent, side)
    self.assertTrue((side / f"figures_{RANGE}").is_dir())
    self.assertFalse((Path(self.note).parent / f"figures_{RANGE}").exists())
    text = Path(note_md).read_text(encoding="utf-8")
    self.assertNotIn("](.assets/", text)
    self.assertIn(f"](figures_{RANGE}/", text)            # SVG 내보내기
    self.assertIn("](복습문제_", text)                     # 형제 MD 링크
    self.assertEqual(html2md.check_md(self.note, note_md), [])

def test_convert_pack_rerun_stays_in_assets(self):
    html2md.convert_pack(self.note, self.review)
    orphan = Path(self.note).parent / ".assets" / f"figures_{RANGE}" / "old.svg"
    orphan.write_text("<svg/>")
    html2md.convert_pack(self.note, self.review)
    self.assertFalse(orphan.exists())
    self.assertEqual(sorted(p.name for p in Path(self.note).parent.iterdir() if not p.name.endswith(".html")), [".assets"])
```

`test_assemble.py`에서는 그림 복사 대상이 `out/.assets/figures_<range>/p2.png`이고 `out/figures_<range>`가 없음을 단언한다. `test_manifest.py`에는 `self.assertEqual(manifest.fig_href("0922"), ".assets/figures_0922")`를 더한다.

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -v`
Expected: 새 테스트들이 FAIL(MD가 HTML 폴더에 생김, `fig_href` 없음)

- [ ] **Step 3: 구현한다**

- `manifest.fig_href`를 더한다.
- `copy_figures`는 `out_dir / SIDE / fig_dir_name(range_)`에 쓴다.
- `convert_pack`은 다음처럼 바꾼다.
  - `md_dir = out_dir/.assets`를 만든다.
  - `fig_abs = md_dir/figures_<range>`로 둔다.
  - `Ctx`의 `fig_dir_name`은 `".assets/figures_<range>"`로 넘긴다. 날짜 폴더 기준이다.
  - `link_map`은 `(html, ".assets/<md>")`로 만든다.
  - 각 `convert` 뒤 MD 파일을 `rebase_md`로 다시 쓴다.
  - 안내문(intro)의 그림 폴더 표기는 MD 기준인 `figures_<range>/`로 쓴다.
- `fixtures/mini-run/cards/p2.html`과 card-rules.md의 `<img src>`를 `.assets/figures_<range>/pN.png`로 바꾼다.
- SKILL.md를 바꾼다.
  - 산출물 설명: 루트에는 HTML 3종과 `.pack/`, `.assets/`에는 MD·`figures_<range>/`·`장마감_*.md`·`자료_문제설명_*`·`figures_문제설명_*`·`풀이기록/`.
  - 직전 노트 경로: `복습노트/*/.assets/정리노트_*.md`.
  - 4단계 백업 스크립트: `srcs`에 `<날짜>/.assets`를 더한다. `want()`는 지금 이름 목록을 그대로 쓴다. `풀이기록`과 `자료_인터렉티브_*`는 백업하지 않는다.
  - 장마감 출력: `복습노트/<range>/.assets/장마감_<range>_<N>장.md`.
  - 9단계 보고 형식의 파일 줄과 표 `:276`.
  - 숨김 폴더라서 Glob/Grep 도구가 건너뛴다는 한 줄 주의를 넣는다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK` (`test_skill_files.py` 포함)

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-review-pack
git commit -m "feat(bio-review-pack): write md and figures into .assets"
```

---

### Task 3: 풀이기록을 `.assets/풀이기록`으로

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js:128-141` (`resolveExportDir`), `:143-144` 주석
- Modify: `.agents/skills/bio-review-pack/scripts/collect_solves.py:1,36`
- Modify: `.agents/skills/bio-review-pack/SKILL.md:263` (`git status 복습노트/<range>/.assets/풀이기록`)
- Modify: `.agents/skills/bio-review-coach/SKILL.md:12`
- Test: `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs`, `tests/test_collect_solves.py`

**Interfaces:**
- Produces: `resolveExportDir(root, documentId, range) -> Promise<DirHandle|null>`. 시그니처는 그대로다. 고른 폴더별 반환은 다음과 같다.
  - `풀이기록` → 그 폴더
  - `.assets` → `.assets/풀이기록`
  - `복습노트` → `<range>/.assets/풀이기록` (`<range>` 폴더가 없으면 null)
  - documentId가 있는 폴더 → `.assets/풀이기록`
  - 그 밖 → null
  - 중간 폴더는 `create:true`로 만든다.
- 이전 스크립트(Task 7)는 이 함수 블록(`async function resolveExportDir`부터 `const isCancel` 직전까지)을 asset에서 잘라 기존 HTML에 넣는다. 그러니 블록의 시작과 끝 표식을 바꾸지 않는다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```js
test('날짜 폴더를 고르면 .assets/풀이기록에 저장', async () => {
  const written = {};
  const root = fakeDir('0929', {files:['d.html']}, written);
  assert.equal(await api.saveExport(fakeWin(async () => root).win, '{}', 'f.json', {...META, store:fakeStore()}), 'saved');
  assert.ok(root.dirs['.assets'] && root.dirs['.assets'].dirs['풀이기록']);
  assert.equal(root.dirs['풀이기록'], undefined);
});
test('.assets·복습노트 폴더를 골라도 .assets/풀이기록', async () => {
  const side = fakeDir('.assets');
  assert.equal(await api.saveExport(fakeWin(async () => side).win, '{}', 'f.json', {...META, store:fakeStore()}), 'saved');
  assert.ok(side.dirs['풀이기록']);
  const notes = fakeDir('복습노트'); notes.dirs['0929'] = fakeDir('0929');
  assert.equal(await api.saveExport(fakeWin(async () => notes).win, '{}', 'f.json', {...META, store:fakeStore()}), 'saved');
  assert.ok(notes.dirs['0929'].dirs['.assets'].dirs['풀이기록']);
});
```

기존 테스트 '날짜 폴더를 고르면 풀이기록 안에 저장…'과 '풀이기록·복습노트 폴더를…'의 위치 단언도 새 구조로 고친다.

```python
def test_moves_json_into_date_folder(self):   # 기존 테스트의 기대 경로 변경
    ...
    self.assertTrue((self.root / "0929" / ".assets" / "풀이기록" / name).is_file())

def test_moves_json_into_range_folder_assets(self):
    # 복습노트/0922-0924/복습문제_0922-0924_X.html 이 있을 때
    ...
    self.assertTrue((self.root / "0922-0924" / ".assets" / "풀이기록" / name).is_file())
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs && python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_collect_solves.py`
Expected: 새 단언들이 FAIL

- [ ] **Step 3: 구현한다**

위 Interfaces대로 `resolveExportDir`를 고친다. 낡은 핸들은 기존 `catch → store.clear() → picker` 경로(`:159-168`)가 이미 처리하므로 손대지 않는다. `collect_solves.py`의 목적지는 `folder / ".assets" / "풀이기록" / src.name`이다. review-coach SKILL의 풀이기록 위치는 `복습노트/<날짜>/.assets/풀이기록/`로 적는다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs && python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: 모두 pass, `OK`

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-review-pack .agents/skills/bio-review-coach/SKILL.md
git commit -m "feat(bio-review-pack): save solve records under .assets/풀이기록"
```

---

### Task 4: bio-problem-explain review 프로필을 `.assets/`로

**Files:**
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_render.py:18-24` (`names`), `:133-180` (`build_explanation`: md 경로·Ctx·rebase)
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_shared.py:10` (`from assets_path import SIDE, rebase_md`)
- Modify: `.agents/skills/bio-problem-explain/SKILL.md:41-42,88`
- Modify: `.agents/skills/bio-problem-explain/assets/port-provenance.json` (스크립트로 다시 만든다)
- Test: `.agents/skills/bio-problem-explain/tests/test_render.py`, `tests/test_publish.py`, `tests/test_skill_files.py`, 공용 픽스처(`tests/helpers.py`에서 복습문제 그림 `src`를 쓰는 곳)

**Interfaces:**
- Consumes: vendor `assets_path.SIDE`, `assets_path.rebase_md` (Task 1)
- Produces: `names(pack) -> (stem, fig_name, data_name)`. review 프로필일 때 `fig_name = ".assets/figures_문제설명_<range>_<slug>"`, `data_name = ".assets/자료_문제설명_<range>_<slug>"`다. forecast·homework는 지금과 같다. `Artifacts.md`는 review일 때 `stage/.assets/<stem>.md`다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```python
def test_review_outputs_go_under_assets(tmp_path, ...):   # test_render.py, 기존 review 빌드 픽스처 재사용
    art = build_explanation(pack, fragments, tmp_path / "stage", repo)
    html = art.html.read_text(encoding="utf-8")
    assert 'href=".assets/자료_문제설명_' in html and '/vendor/katex/katex.min.css' in html
    assert art.md.parent == tmp_path / "stage" / ".assets"
    md = art.md.read_text(encoding="utf-8")
    assert "](.assets/" not in md
    assert "](../" in md                                  # 원 문제 보기 → ../복습문제_….html
    assert (tmp_path / "stage" / ".assets" / f"figures_문제설명_{pack.range}_{pack.slug}").is_dir()
    assert not any(p.name.startswith(("figures_", "자료_")) for p in (tmp_path / "stage").iterdir())

def test_forecast_names_unchanged(...):
    assert names(forecast_pack)[1].startswith("figures_문제해설_")
```

`test_publish.py`에서는 review 게시 뒤 목적지에 `.assets/문제설명_….md`와 `.assets/자료_문제설명_…/validation.json`이 있고, 루트에는 `문제설명_….html`만 생기는지 단언한다.

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `uvx --quiet pytest -q .agents/skills/bio-problem-explain/tests -k "assets or forecast_names or publish"`
Expected: FAIL

- [ ] **Step 3: 구현한다**

- `names()`의 review 분기에 `SIDE + "/"` 접두를 붙인다.
- `build_explanation`의 `data_dir.mkdir()`·`(stage / fig_name).mkdir()`는 `parents=True`로 바꾼다.
- review일 때 `md_path = stage / SIDE / f"{stem}.md"`로 두고, `Ctx` link_map은 `(html_path.name, f"{SIDE}/{md_path.name}")`, fig 이름은 날짜 폴더 기준 `fig_name`으로 넘긴다.
- `convert_markdown` 뒤 MD 파일을 `rebase_md`로 다시 쓴다. 이 단계는 review 프로필에서만 한다. forecast·homework MD는 HTML 옆이라 rebase하지 않는다.
- `resources()`의 그림 `src`(`target.relative_to(stage)`)와 VENDOR 슬롯은 `data_name`·`fig_name`을 따라가므로 손대지 않는다.
- SKILL.md `:88`의 출력 설명을 바꾼다.
- 마지막으로 `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py`를 돌려 provenance를 다시 만든다(source 체크아웃 `/Users/hyunjun_macbook_pro/Documents/Univ/자구알` 필요).

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `uvx --quiet pytest -q .agents/skills/bio-problem-explain/tests`
Expected: 모두 pass(기준선 136개 + 새 테스트)

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): put review explanation assets under .assets"
```

---

### Task 5: bio-interactive를 `.assets/`로

**Files:**
- Modify: `.agents/skills/bio-interactive/scripts/save.cjs:3-4,22-24`
- Modify: `.agents/skills/bio-interactive/scripts/resolve.cjs:38-40` (`notesIn`), `:49-56` (`nextNumber`)
- Modify: `.agents/skills/bio-interactive/SKILL.md:16,42,111`
- Test: `.agents/skills/bio-interactive/tests/save.test.cjs`, `tests/resolve.test.cjs`, `tests/build.test.cjs`, `tests/skill.test.cjs`

**Interfaces:**
- Produces:
  - `save({src, dest, name}) -> {nn, html, dir}`: `dir`는 `<dest>/.assets/자료_인터렉티브_NN_<name>`이다. `.assets`는 `recursive:true`로 만들고, `dir`는 지금처럼 non-recursive로 만든다.
  - `nextNumber(folder) -> string`: `folder`의 `인터렉티브_NN*.html`과 `folder/.assets`의 `자료_인터렉티브_NN*`(그리고 하위 호환을 위해 루트의 `자료_인터렉티브_NN*`) 중 최대값에 1을 더한다.
  - `notesIn(folder)`: `folder/.assets/정리노트_*.md`.
- `build.cjs`는 바꾸지 않는다. 생성 주석의 `rel`이 `path.relative`로 계산되므로 자동으로 `.assets/자료_인터렉티브_…/Main.dc.html`이 된다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```js
test('save puts the data folder under .assets', () => {
  const r = save({ src, dest, name: '전사' });
  assert.equal(nfc(path.relative(dest, r.dir)), '.assets/자료_인터렉티브_01_전사');
  assert.match(fs.readFileSync(r.html, 'utf8'), /생성 파일: \.assets\/자료_인터렉티브_01_전사\/Main\.dc\.html/);
});
test('nextNumber counts .assets data folders in a range folder', () => {
  const repo = fixture({ '복습노트/0922-0924/.assets/자료_인터렉티브_03_x/Main.dc.html': '' });
  assert.equal(nextNumber(path.join(repo, '복습노트/0922-0924')), '04');
});
test('resolve reads notes from .assets', () => {
  const repo = fixture({ '복습노트/1006/.assets/정리노트_1006_X.md': '# 전사', '복습노트/1006/정리노트_1006_X.html': '', 'STT/1006 생명.md': '...' });
  const r = resolve({ repo, arg: '1006' });
  assert.ok(nfc(r.notes[0]).endsWith('1006/.assets/정리노트_1006_X.md'));
});
```

`resolve.test.cjs`의 기존 픽스처 `'복습노트/<d>/정리노트_….md'`는 `'복습노트/<d>/.assets/정리노트_….md'`로 옮긴다.

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `node --test .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: 새 테스트와 옮긴 픽스처 테스트가 FAIL

- [ ] **Step 3: 구현한다**

위 Interfaces대로 고친다. SKILL.md는 산출물 줄(`:16`)을 `.assets/자료_인터렉티브_NN_<이름>/`으로, `notes` 설명(`:42`)을 `.assets/` 경로로, 커밋 제안(`:111`)을 `"<DEST>/.assets/자료_인터렉티브_NN_<이름>"`으로 바꾼다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `node --test .agents/skills/bio-interactive/tests/*.test.cjs`
Expected: `ℹ fail 0`

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-interactive
git commit -m "feat(bio-interactive): save interactive sources under .assets"
```

---

### Task 6: 읽는 스킬(stt·cheatsheet·preview-note·webquiz-forecast·review-video)

**Files:**
- Modify: `.agents/skills/bio-stt/scripts/infer_context.py:105-112` (장마감 탐색)
- Modify: `.agents/skills/bio-cheatsheet/SKILL.md:37-39,89`, `references/content-rules.md`(경로가 있으면)
- Modify: `.agents/skills/bio-preview-note/SKILL.md:72,132`
- Modify: `.agents/skills/bio-webquiz-forecast/SKILL.md:23`
- Modify: `.agents/skills/bio-review-video/references/sources-and-coverage.md`(MD·장마감 위치를 적은 곳이 있으면)
- Test: `tests/test_bio_stt.py`(저장소 루트)

**Interfaces:**
- Consumes: 없음(경로 문자열만). 장마감 위치는 `복습노트/<날짜>/.assets/장마감_<날짜>_<N>장.md`, 정리노트 MD 위치는 `복습노트/<날짜>/.assets/정리노트_*.md`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```python
def test_infer_chapter_reads_chapter_close_from_assets(self):
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        (repo / "복습노트/1001/.assets").mkdir(parents=True)
        (repo / "복습노트/1001/.assets/장마감_1001_4장.md").write_text("x", encoding="utf-8")
        self.assertEqual(infer_chapter(repo, "1006"), 5)   # 예습노트가 없으니 1001 장마감(4장) + 1
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m unittest tests.test_bio_stt -v`
Expected: 새 테스트 FAIL(루트에서만 장마감을 찾음)

- [ ] **Step 3: 구현한다**

`infer_context.py`는 `f_dir / ".assets"`가 있으면 그 안에서 `장마감_\d{4}_(\d+)장\.md`를 찾는다. 정리노트 HTML 태그 탐색(`:115~`)은 루트 그대로 둔다. 각 SKILL.md의 정리노트 MD·장마감 경로를 Global Constraints의 숨김 폴더 규칙대로 `복습노트/*/.assets/…`로 바꾼다. 범위 폴더 표기가 있는 곳은 `<날짜 폴더>/.assets/…`로 적는다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 -m unittest tests.test_bio_stt && for s in bio-cheatsheet bio-preview-note bio-webquiz-forecast bio-review-video; do python3 -m unittest discover -s .agents/skills/$s/tests || break; done`
Expected: 모두 `OK`(SKILL 문서 검사 테스트 포함)

- [ ] **Step 5: 커밋한다**

```bash
git add .agents/skills/bio-stt .agents/skills/bio-cheatsheet .agents/skills/bio-preview-note .agents/skills/bio-webquiz-forecast .agents/skills/bio-review-video tests/test_bio_stt.py
git commit -m "docs(skills): read review notes from .assets"
```

---

### Task 7: 이전 스크립트 `migrate_review_assets.py`

**Files:**
- Create: `scripts/migrate_review_assets.py`
- Test: `tests/test_migrate_review_assets.py`

**Interfaces:**
- Consumes: `assets_path.SIDE`, `moves`, `relocate`, `rebase_md` (Task 1). `sys.path`에 `.agents/skills/bio-review-pack/scripts`를 넣어 import한다(`bio-preview-note/scripts/_review.py` 방식). `review-interaction.js`의 `resolveExportDir` 블록(Task 3).
- Produces:
  - `export_block(js: str) -> str`: `async function resolveExportDir`부터 `const isCancel` 직전까지를 잘라 낸다. 각 표식이 정확히 한 번씩 없으면 `ValueError`를 낸다.
  - `rewrite_html(text: str, block: str | None) -> str`: 상대 `src="…"`·`href="…"`를 `relocate`하고, `<!-- 생성 파일: X…` 주석의 X를 `relocate`하고, 문서에 `resolveExportDir` 블록이 있으면 `block`으로 바꾼다.
  - `rewrite_md(text: str) -> str` = `rebase_md`(모든 `](t)`를 `relocate` 한 결과).
  - `migrate_day(day: Path, block: str, apply: bool) -> list[str]`: 할 일 목록(`move X`, `rewrite Y`)을 돌려주고, `apply`일 때만 실행한다.
  - `broken_links(day: Path) -> list[str]`: 루트 `*.html`의 상대 `src`/`href`와 `.assets/*.md`의 상대 `](t)` 대상(`#` 앞, `unquote`)이 없는 것을 모은다.
  - CLI: `python3 scripts/migrate_review_assets.py [ROOT=복습노트] [--apply] [--check]`. 기본은 dry-run(할 일 출력)이다. `--check`는 깨진 링크를 출력하고 개수가 0이 아니면 종료 코드 1이다.

`migrate_day`의 처리 순서는 다음과 같다.
1. 루트 `.md`를 읽어 둔다.
2. `moves(name)`인 항목을 `os.rename`으로 `.assets/`에 옮긴다. `.assets/`에 같은 이름이 이미 있으면 `FileExistsError`로 멈춘다.
3. 루트 HTML을 다시 쓴다.
4. 옮긴 `.md`는 `.assets/` 안 파일을 `rewrite_md`로 다시 쓴다. 이미 `.assets/`에 있던 MD는 다시 쓰지 않는다. 그래서 두 번 돌려도 결과가 같다.

git 기록은 커밋 때 `git add -A`의 rename 감지가 처리한다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

```python
class TestMigrate(unittest.TestCase):
    def setUp(self):  # tmp/복습노트/0922 에 실제 구조를 축소한 픽스처 (이름 일부는 NFD로 기록)
        ...  # 정리노트_0922_X.html(href="../0917/정리노트_0917_Y.html", <img src="figures_0922/p37.png">),
             # 복습문제_0922_X.html(asset 블록과 같은 resolveExportDir + "figures_0922/p37.png"),
             # 문제설명_0922_X.html(href="자료_문제설명_0922_X/vendor/katex/katex.min.css"),
             # 인터렉티브_01_a.html(<!-- 생성 파일: 자료_인터렉티브_01_a/Main.dc.html…),
             # 정리노트_0922_X.md([복습](복습문제_0922_X.md#p1), ![f](figures_0922/a.svg), [원](%EC%A0%95…html#s1)),
             # 장마감_0922_3장.md([n](../0917/정리노트_0917_Y.html)), figures_0922/{p37.png,a.svg},
             # 자료_문제설명_0922_X/vendor/katex/katex.min.css, 자료_인터렉티브_01_a/Main.dc.html,
             # 풀이기록/r.json, .pack/manifest.json, 그리고 tmp/복습노트/0917/정리노트_0917_Y.html

    def test_dry_run_changes_nothing(self):
        before = snapshot(self.root)
        acts = migrate_day(self.day, BLOCK, apply=False)
        self.assertTrue(any(a.startswith("move ") for a in acts))
        self.assertEqual(snapshot(self.root), before)

    def test_apply_layout_and_links(self):
        migrate_day(self.day, BLOCK, apply=True)
        self.assertEqual(sorted(nfc(p.name) for p in self.day.iterdir()),
                         [".assets", ".pack", "문제설명_0922_X.html", "복습문제_0922_X.html", "인터렉티브_01_a.html", "정리노트_0922_X.html"])
        self.assertIn('src=".assets/figures_0922/p37.png"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn('href="../0917/정리노트_0917_Y.html"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn("생성 파일: .assets/자료_인터렉티브_01_a/Main.dc.html", read(self.day / "인터렉티브_01_a.html"))
        self.assertIn("'.assets'", read(self.day / "복습문제_0922_X.html"))
        md = read(self.day / ".assets/정리노트_0922_X.md")
        self.assertIn("](복습문제_0922_X.md#p1)", md); self.assertIn("](figures_0922/a.svg)", md); self.assertIn("](../%EC%A0%95", md)
        self.assertIn("](../../0917/정리노트_0917_Y.html)", read(self.day / ".assets/장마감_0922_3장.md"))
        self.assertEqual(broken_links(self.day), [])

    def test_migrate_is_idempotent(self):
        migrate_day(self.day, BLOCK, apply=True)
        once = snapshot(self.root)
        self.assertEqual(migrate_day(self.day, BLOCK, apply=True), [])
        self.assertEqual(snapshot(self.root), once)

    def test_name_clash_stops(self):
        (self.day / ".assets/figures_0922").mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            migrate_day(self.day, BLOCK, apply=True)

    def test_export_block_requires_single_markers(self):
        with self.assertRaises(ValueError):
            export_block("no markers here")
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m unittest tests.test_migrate_review_assets -v`
Expected: `ModuleNotFoundError: No module named 'scripts.migrate_review_assets'`

- [ ] **Step 3: Interfaces대로 `scripts/migrate_review_assets.py`를 구현한다**

- HTML 속성은 정규식 `(src|href)="([^"]*)"`로 찾아 값에만 `relocate`를 적용한다.
- 날짜 폴더는 `\d{4}(-\d{4})?`(NFC)에 맞는 것만 처리한다.
- `.assets/` 안의 하위 폴더(`자료_*` 등)의 파일은 다시 쓰지 않는다.

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 -m unittest tests.test_migrate_review_assets -v`
Expected: 5 tests OK

- [ ] **Step 5: 커밋한다**

```bash
git add scripts/migrate_review_assets.py tests/test_migrate_review_assets.py
git commit -m "feat(scripts): add 복습노트 .assets migration"
```

---

### Task 8: 실제 12개 날짜 폴더를 이전하고 검증

**Files:**
- Modify: `복습노트/*/` (이전 결과)

**Interfaces:**
- Consumes: `scripts/migrate_review_assets.py` CLI (Task 7)

- [ ] **Step 1: 작업 트리를 확인한다**

Run: `git status --porcelain 복습노트`
Expected: 빈 출력. 출력이 있으면(예: 지금 수정 중인 `1001` 인터렉티브 HTML) 멈추고 사용자에게 커밋할지 보관할지 묻는다. 이전 스크립트가 같은 파일을 다시 쓰기 때문이다.

- [ ] **Step 2: dry-run으로 할 일을 확인한다**

Run: `python3 scripts/migrate_review_assets.py`
Expected: 0901–1013 12개 폴더의 `move …`·`rewrite …` 목록. `.pack`, `*.html`, `.DS_Store`의 move가 없어야 한다.

- [ ] **Step 3: 적용하고 링크를 검사한다**

Run: `python3 scripts/migrate_review_assets.py --apply && python3 scripts/migrate_review_assets.py --check`
Expected: `--check`가 깨진 링크 0, 종료 코드 0

- [ ] **Step 4: 구조와 회귀를 확인한다**

Run: `for d in 복습노트/*/; do ls -A "$d" | grep -vE '\.html$|^\.pack$|^\.assets$|^\.DS_Store$'; done; python3 -m unittest discover tests`
Expected: 첫 루프는 출력 없음. 저장소 테스트는 `OK`(`test_bio_stt`의 실제 1001 장 추론 포함).

- [ ] **Step 5: 브라우저에서 확인한다**

내장 브라우저(`mcp__Claude_Browser__navigate`)로 다음 세 파일을 연다.
- `file://…/복습노트/0903/문제설명_0903_Biomolecules_and_Cells.html`: KaTeX 수식이 렌더되고 그림이 뜨며, `read_console_messages`에 404가 없어야 한다.
- `…/0922/복습문제_0922_Cell_Division_and_Heredity.html`: p37 그림이 떠야 한다.
- `…/1001/인터렉티브_03_DNA_구조와_복제_3D.html`: 정상적으로 그려져야 한다.

- [ ] **Step 6: 커밋한다**

```bash
git add -A 복습노트
git commit -m "docs(notes): move review side files into .assets"
```
