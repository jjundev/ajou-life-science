# 웹과제예상 `.pack/` 정리 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `웹과제예상/<N>장/` 맨 위에는 HTML과 숨김 폴더 `.pack/`만 남긴다. 예상 세트 소스(`src/v<K>`)와 해설 부속 파일(MD·figures·자료)은 모두 `.pack/`으로 옮기고, 이 폴더를 쓰는 두 스킬과 기존 4·5장을 새 구조에 맞춘다.

**Architecture:** 복습노트 `.assets` 이전과 같은 경로 규칙 모듈 `assets_path.py`에 `side` 인자를 더해 `.pack`에도 쓴다. bio-webquiz-forecast는 버전 폴더를 `<장>/.pack/v<K>`로 만들고 읽는다. bio-problem-explain forecast 프로필은 review 프로필처럼 부속 파일을 숨김 폴더(`.pack`)에 둔다. 일회성 이전 스크립트가 기존 파일을 옮기고 HTML·MD 링크와 해설 기록(JSON)을 고친다.

**Tech Stack:** Python 3 표준 라이브러리(unittest; bio-problem-explain만 pytest). 새 의존성은 없다. Windows(Git Bash)에서는 `python`으로 실행한다.

**Spec:** `docs/superpowers/specs/2026-10-15-forecast-pack-folder-design.md`

## Global Constraints
- 부속 폴더 이름은 고정값 `.pack`이다. 하위 이름(`figures_문제해설_<N>장_웹과제예상_v<K>`, `자료_문제해설_…`, `문제해설_….md`)은 그대로 둔다. 버전 소스만 `src/v<K>`에서 `.pack/v<K>`로 바뀐다.
- 장 폴더(`웹과제예상/<N>장/`) 루트에 남는 것은 `*.html`과 `.pack/`뿐이다.
- 범위는 `웹과제예상/<숫자>장/`이다. `웹과제예상/커닝페이퍼/`, `복습노트/`, homework 프로필, `mpe_cli.py rerender`는 바꾸지 않는다.
- `assets_path`의 기본 동작(`side` 생략 = `.assets`)은 바이트 단위로 같아야 한다. review 쪽 호출부는 고치지 않는다.
- 파일명 비교는 NFC로 한다.
- 저장소는 `core.autocrlf=true`라 작업 트리 파일이 CRLF다. 이전 스크립트는 `read_bytes`/`write_bytes`로 읽고 써서 줄바꿈을 보존한다. `Path.read_text`/`write_text`는 쓰지 않는다.
- 문서에는 `.pack`을 글자 그대로 쓴 경로만 적는다. 숨김 폴더는 Glob/Grep(ripgrep)과 `glob.glob('*')`이 건너뛴다.
- 작업 트리에는 이번 작업과 무관한 수정(bio-interactive, 복습노트 HTML)이 있다. `git add`는 항상 파일 경로를 명시하고, `git add -A`는 `웹과제예상`처럼 범위를 지정할 때만 쓴다.
- 커밋 메시지는 Conventional Commits 형식이고, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`을 붙인다.
- 테스트 명령(저장소 루트 기준):
  - review-pack: `python -m unittest discover -s .agents/skills/bio-review-pack/tests`
  - webquiz-forecast: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests`
  - problem-explain: `python -m pytest -q .agents/skills/bio-problem-explain/tests`
  - 이전 스크립트: `python -m pytest -q tests/test_migrate_forecast_pack.py`
- **기준선 실패:** 작업 전에 이미 실패하는 테스트가 있다(Windows CRLF 해시·경로 문제). problem-explain 9개(`test_cli.py`의 rerender 5개, `test_render.py::test_vendor_files_and_hashes_present`, `test_render.py::test_missing_images_and_duplic…`, `test_render.py:122` 해시, `test_skill_files.py::test_claude_link_and_provenance`)와 `tests/test_migrate_review_assets.py::test_apply_layout_and_links` 1개다. 각 Task에서 "통과"는 **이 목록 밖에 새 실패가 없음**을 뜻한다. Task 시작 전에 `python -m pytest -q .agents/skills/bio-problem-explain/tests 2>&1 | grep ^FAILED > "$TEMP/baseline.txt"`로 기준선을 저장하고, 끝에 같은 명령의 결과를 `diff`로 비교한다.

## Review Focus
1. 해설 MD 안의 %-인코딩된 바깥 링크(`../../%EB%B3%B5…/1001/…html#s4`)는 `.pack/` 안으로 옮긴 뒤 `../../../`로 시작해야 하고 인코딩은 그대로여야 한다. 같이 옮겨지는 `figures_…/x.svg` 링크는 바뀌지 않아야 한다. → Task 1 `test_pack_rebase_outside_link`, Task 4 `test_md_links_rebased_and_crlf_kept`.
2. CRLF 파일을 이전한 뒤에도 줄바꿈이 CRLF로 남아야 하고, manifest·validation에 적힌 해시가 실제 파일 바이트의 해시와 같아야 한다. → Task 4 `test_records_rewritten`.
3. 이전을 두 번 돌리거나, `.pack/v1`이 이미 있는데 `src/v1`도 남아 있으면 앞의 경우는 아무것도 하지 않고 뒤의 경우는 아무것도 옮기지 않은 채 멈춰야 한다. → Task 4 `test_idempotent`, `test_clash_moves_nothing`.
4. `.pack/` 안에 `figures_…_v9`, `자료_…_v9`, `문제해설_…_v9.md`가 섞여 있어도 `--init`의 다음 버전은 `v<K>` 폴더와 루트 HTML만으로 정해져야 한다. → Task 2 `test_next_version_ignores_pack_side_files`.
5. 해설을 발행해도 장 폴더 루트에는 HTML과 `.pack/`만 생기고, 같은 `.pack/` 안의 예상 세트 소스(`.pack/v5/pack.json`)는 바이트까지 그대로여야 한다. → Task 3 `test_forecast_publish_keeps_root_clean_and_sources_intact`.

---

### Task 1: `assets_path`에 `side` 인자와 `PACK` 상수 추가

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/assets_path.py`
- Modify: `.agents/skills/bio-problem-explain/scripts/vendor/assets_path.py` (위 파일을 그대로 복사)
- Modify: `.agents/skills/bio-problem-explain/assets/port-provenance.json` (`scripts/vendor/assets_path.py` 항목의 `destination_sha256`)
- Test: `.agents/skills/bio-review-pack/tests/test_assets_path.py`

**Interfaces:**
- Produces:
  - `PACK: str = ".pack"`, `SIDE: str = ".assets"`(기존)
  - `moves(name: str, side: str = SIDE) -> bool`
  - `relocate(url: str, side: str = SIDE) -> str`
  - `rebase_md(text: str, side: str = SIDE) -> str`
  - `migrate_md(text: str, side: str = SIDE) -> str`

- [ ] **Step 0: 스펙·계획 커밋**

```bash
git add docs/superpowers/specs/2026-10-15-forecast-pack-folder-design.md docs/superpowers/plans/2026-10-15-forecast-pack-folder.md
git commit -m "docs: add forecast pack folder spec and plan" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 1: 실패하는 테스트 작성**

`test_assets_path.py`의 import 줄을 바꾸고 `TestAssetsPath` 클래스 끝에 메서드를 추가한다.

```python
from assets_path import PACK, migrate_md, moves, rebase_md, relocate
```

```python
    def test_pack_constant(self):
        self.assertEqual(PACK, ".pack")

    def test_pack_moves(self):
        for n in ("문제해설_5장_웹과제예상_v1.md", "figures_문제해설_5장_웹과제예상_v1", "자료_문제해설_5장_웹과제예상_v1"):
            self.assertTrue(moves(n, PACK), n)
        for n in ("복습문제_5장_웹과제예상_v1.html", ".pack", ".assets", ".DS_Store", ""):
            self.assertFalse(moves(n, PACK), n)

    def test_pack_relocate(self):
        enc = quote("figures_문제해설_5장_웹과제예상_v1") + "/explain-fig-1.svg"
        self.assertEqual(relocate(enc, PACK), ".pack/" + enc)
        self.assertEqual(relocate("자료_문제해설_5장_웹과제예상_v1/vendor/katex/katex.min.css", PACK),
                         ".pack/자료_문제해설_5장_웹과제예상_v1/vendor/katex/katex.min.css")
        for u in ("../../복습노트/1001/정리노트_1001_X.html#s1", "#p1", ".pack/figures_x/a.svg", "복습문제_5장_웹과제예상_v1.html"):
            self.assertEqual(relocate(u, PACK), u)

    def test_pack_rebase_outside_link(self):
        t = "[a](../../%EB%B3%B5%EC%8A%B5/1001/x.html#s4) ![b](.pack/figures_x/a.svg) [c](#p1)"
        self.assertEqual(rebase_md(t, PACK), "[a](../../../%EB%B3%B5%EC%8A%B5/1001/x.html#s4) ![b](figures_x/a.svg) [c](#p1)")

    def test_pack_migrate_md(self):
        t = "![f](figures_x/a.svg)\r\n[n](../../%EB%B3%B5/1001/x.html#s1)\r\n"
        self.assertEqual(migrate_md(t, PACK), "![f](figures_x/a.svg)\r\n[n](../../../%EB%B3%B5/1001/x.html#s1)\r\n")

    def test_default_side_unchanged(self):
        self.assertEqual(relocate("figures_0922/p37.png"), relocate("figures_0922/p37.png", ".assets"))
        self.assertEqual(rebase_md("[b](정리노트_1001_X.html)"), "[b](../정리노트_1001_X.html)")
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_assets_path.py -v`
Expected: `ImportError: cannot import name 'PACK'`

- [ ] **Step 3: 구현**

`assets_path.py`에서 아래 부분을 바꾼다. 나머지(`_nfc`, `_is_external`, `_strip_dot_slash`, 정규식)는 그대로 둔다. 모듈 docstring 첫 단락 끝에 한 줄을 추가한다: `웹과제예상/<N>장/ 은 같은 규칙을 side=PACK(".pack")으로 쓴다.`

```python
SIDE = ".assets"
PACK = ".pack"

_STAY = {PACK, SIDE, ".DS_Store", ""}
```

```python
def moves(name: str, side: str = SIDE) -> bool:
    """폴더 바로 아래 항목 `name`이 부속 폴더 `side`로 가는가."""
    name = _nfc(name)
    if name in _STAY or name == side:
        return False
    return not name.lower().endswith((".html", ".htm"))


def _segment_moves(piece: str, side: str) -> bool:
    """URL 경로 조각(?query·#fragment 포함 가능, 인코딩 가능)이 `side`로 가는가."""
    return moves(unquote(re.split(r"[?#]", piece, maxsplit=1)[0]), side)
```

```python
def relocate(url: str, side: str = SIDE) -> str:
    """폴더 루트 HTML/MD 기준 상대 URL을 `side/` 이전 뒤 위치로 바꾼다."""
    if _is_external(url):
        return url
    path = _strip_dot_slash(url)
    parts = path.split("/")
    if parts[0] == "..":
        if (len(parts) >= 3 and _DATE.fullmatch(_nfc(unquote(parts[1])))
                and _segment_moves(parts[2], side)):
            return "/".join(parts[:2] + [side] + parts[2:])
        return url
    if _segment_moves(parts[0], side):
        return f"{side}/{path}"
    return url


def rebase_md(text: str, side: str = SIDE) -> str:
    """폴더 루트 기준으로 쓰인 MD의 `](target)`을 `side/` 안 MD 기준으로 바꾼다."""
    def fix(m: re.Match) -> str:
        target = m.group(2)
        if _is_external(target):
            return m.group(0)
        target = _strip_dot_slash(target)
        if target.startswith(side + "/"):
            target = target[len(side) + 1:]
        else:
            target = "../" + target
        return m.group(1) + target + m.group(3)

    return _MD_TARGET.sub(fix, text)


def migrate_md(text: str, side: str = SIDE) -> str:
    """폴더 루트에 있던 MD를 `side/` 안 위치에 맞게 고친다(이전 때 한 번만 적용)."""
    return rebase_md(_MD_TARGET.sub(lambda m: m.group(1) + relocate(m.group(2), side) + m.group(3), text), side)
```

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -v 2>&1 | tail -3`
Expected: `OK` (기존 `test_assets_path` 7개 + 새 6개 포함)

- [ ] **Step 5: vendor 사본과 provenance 갱신**

```bash
cp .agents/skills/bio-review-pack/scripts/assets_path.py .agents/skills/bio-problem-explain/scripts/vendor/assets_path.py
python -c "import hashlib;print(hashlib.sha256(open('.agents/skills/bio-problem-explain/scripts/vendor/assets_path.py','rb').read()).hexdigest())"
```

출력된 해시로 `port-provenance.json`에서 `"destination": "scripts/vendor/assets_path.py"` 항목의 `destination_sha256` 값(현재 `b01905545dc9…6f4f`)을 바꾼다.

Run: `cmp .agents/skills/bio-review-pack/scripts/assets_path.py .agents/skills/bio-problem-explain/scripts/vendor/assets_path.py && python -m pytest -q .agents/skills/bio-problem-explain/tests 2>&1 | grep ^FAILED | diff "$TEMP/baseline.txt" -`
Expected: `cmp`는 아무것도 출력하지 않고, diff도 출력이 없음(새 실패 없음)

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-review-pack/scripts/assets_path.py .agents/skills/bio-review-pack/tests/test_assets_path.py .agents/skills/bio-problem-explain/scripts/vendor/assets_path.py .agents/skills/bio-problem-explain/assets/port-provenance.json
git commit -m "feat(bio-review-pack): let assets_path take a side folder" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: bio-webquiz-forecast 소스를 `.pack/v<K>`로

**Files:**
- Modify: `.agents/skills/bio-webquiz-forecast/scripts/build.py:2-10,24,36,71-86`
- Modify: `.agents/skills/bio-webquiz-forecast/scripts/check.py:66,73`
- Modify: `.agents/skills/bio-webquiz-forecast/SKILL.md:21,27,32,35,42,63,64`
- Modify: `.agents/skills/bio-webquiz-forecast/references/explanation-handoff.md:9,17,25`
- Modify: `.agents/skills/bio-webquiz-forecast/references/question-blueprint.md:3`
- Test: `.agents/skills/bio-webquiz-forecast/tests/_util.py:51`, `tests/test_build.py`, `tests/test_check.py:44`, `tests/test_skill_files.py`

**Interfaces:**
- Consumes: 없음(이 스킬은 `assets_path`를 쓰지 않는다)
- Produces: `build.PACK = ".pack"`; `build.init_version(repo, chapter, version=None) -> Path`는 `<repo>/웹과제예상/<N>장/.pack/v<K>`를 돌려준다. `build.load_pack(src)`는 `src.parent.name == ".pack"`일 때만 받는다. Task 3의 테스트가 `bio-webquiz-forecast/scripts/build.py <장>/.pack/v5`를 subprocess로 부른다.

- [ ] **Step 1: 테스트 수정과 새 실패 테스트 작성**

`tests/_util.py:51`:

```python
    src = repo / "웹과제예상" / f"{chapter}장" / ".pack" / f"v{version}"
```

`tests/test_check.py:44`:

```python
        (out.parent / ".pack" / "v1" / "cards" / "p1.html").write_text(
```

`tests/test_build.py`의 `test_next_version`, `test_init_refuses_existing`을 아래로 바꾸고, 새 테스트 두 개를 추가한다.

```python
    def test_next_version(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "웹과제예상" / "9장"
            self.assertEqual(build.next_version(d), 1)
            (d / ".pack" / "v1").mkdir(parents=True)
            (d / "복습문제_9장_웹과제예상_v3.html").write_text("x", encoding="utf-8")
            self.assertEqual(build.next_version(d), 4)

    def test_next_version_ignores_pack_side_files(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "웹과제예상" / "9장"
            (d / ".pack" / "v2").mkdir(parents=True)
            (d / ".pack" / "figures_문제해설_9장_웹과제예상_v9").mkdir()
            (d / ".pack" / "자료_문제해설_9장_웹과제예상_v9").mkdir()
            (d / ".pack" / "문제해설_9장_웹과제예상_v9.md").write_text("x", encoding="utf-8")
            (d / "src" / "v7").mkdir(parents=True)  # 옛 위치는 보지 않는다
            self.assertEqual(build.next_version(d), 3)

    def test_init_refuses_existing(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            src = build.init_version(repo, 9)
            self.assertEqual(src, repo / "웹과제예상" / "9장" / ".pack" / "v1")
            self.assertTrue((src / "cards").is_dir())
            self.assertEqual(build.init_version(repo, 9).name, "v2")
            (repo / "웹과제예상" / "9장" / ".pack" / "v3").mkdir()
            with self.assertRaises(build.BuildError):
                build.init_version(repo, 9, version=3)

    def test_old_src_layout_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 1, five())
            old = src.parents[1] / "src" / "v1"
            old.parent.mkdir()
            src.rename(old)
            with self.assertRaises(build.BuildError):
                build.render(old)
```

`tests/test_skill_files.py`의 `TestSkillFiles`에 추가한다.

```python
    def test_docs_use_pack_layout(self):
        docs = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
        for p in docs:
            self.assertNotIn("src/v", p.read_text(encoding="utf-8"), p.name)
        for needle in ("웹과제예상/<N>장/.pack/v<K>", ".pack/v*/blueprint.md", "HTML과 `.pack/`만"):
            self.assertIn(needle, self.md, needle)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests 2>&1 | tail -3`
Expected: `FAILED` (`load_pack`이 `.pack` 부모를 거부해 대부분 BuildError, `test_docs_use_pack_layout` 실패)

- [ ] **Step 3: `build.py` 구현**

docstring 2–10행:

```python
"""웹과제 예상 세트(.pack/v<K>) → 복습문제 형식 HTML, 그리고 버전 관리.

조립은 bio-review-pack assemble.build_review를 그대로 쓴다. 치환 3개(정리노트 링크, data-range, 내보내기 숨김)는
각각 정확히 1회여야 한다. 장 폴더 루트에는 HTML만 두고 소스는 숨김 폴더 `.pack/v<K>/`에 둔다.
CLI:
  build.py <src>              .pack/v<K> → 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html
  build.py --next <repo> <N>  다음 버전 번호 출력
  build.py --init <repo> <N>  다음 버전 폴더(.pack/v<K>/cards) 생성 후 경로 출력
"""
```

24행 `VERSION_RE` 위에 상수를 추가한다.

```python
PACK = ".pack"  # 장 폴더의 숨김 소스 폴더(해설 부속 파일도 여기에 둔다)
```

36행:

```python
    if src.name != f"v{k}" or src.parent.name != PACK or src.parent.parent.name != f"{n}장":
```

`next_version`과 `init_version`:

```python
def next_version(chapter_dir: Path | str) -> int:
    d = Path(chapter_dir)
    nums = [0]
    if (d / PACK).is_dir():
        nums += [int(m.group(1)) for p in (d / PACK).iterdir()
                 if p.is_dir() and (m := VERSION_RE.fullmatch(p.name))]
    if d.is_dir():
        nums += [int(m.group(1)) for p in d.iterdir() if (m := HTML_VERSION_RE.search(p.name))]
    return max(nums) + 1


def init_version(repo: Path | str, chapter: int, version: int | None = None) -> Path:
    d = Path(repo) / "웹과제예상" / f"{chapter}장"
    k = version or next_version(d)
    src = d / PACK / f"v{k}"
    if src.exists():
        raise BuildError(f"이미 있는 버전: {src}")
    (src / "cards").mkdir(parents=True)
    return src
```

- [ ] **Step 4: `check.py` 구현**

66행과 73행:

```python
    src = html_path.parent / build.PACK / f"v{m.group(1)}"
```

```python
        probs.append(f"[stale] {html_path.name}: .pack/v{pack['version']}로 다시 빌드한 결과와 다름")
```

`_earlier`(47–49행)는 `re.fullmatch(r"v(\d+)", d.name)`과 `pack.json` 존재로 이미 거르므로 바꾸지 않는다.

- [ ] **Step 5: 문서 수정**

`SKILL.md`:
- 21행: `` 새 `웹과제예상/<N>장/src/v<K>/`가 생긴다 `` → `` 새 `웹과제예상/<N>장/.pack/v<K>/`가 생긴다 ``
- 27행: `` - 이전 세트: `웹과제예상/<N>장/.pack/v*/blueprint.md`와 `pack.json`(쓴 기출 번호·주제). `.pack`은 숨김 폴더라 Glob/Grep이 건너뛰므로 이 경로를 직접 연다. ``
- 32행: `` `src/v<K>/cards/o1.html` `` → `` `.pack/v<K>/cards/o1.html` ``
- 35행: `` `src/v<K>/blueprint.md` `` → `` `.pack/v<K>/blueprint.md` ``
- 42행: `python "$SKILL/scripts/build.py" "$REPO/웹과제예상/<N>장/.pack/v<K>"`
- 63–64행을 아래 세 줄로 바꾼다.

```
- 예상문제 파일: 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html (소스는 .pack/v<K>/)
- 해설 파일: 웹과제예상/<N>장/문제해설_<N>장_웹과제예상_v<K>.html (MD·그림·자료 폴더는 .pack/)
- 장 폴더 맨 위에는 HTML과 `.pack/`만 둔다.
```

`references/explanation-handoff.md`:
- 9행: `` 해당 `src/v<K>/pack.json` `` → `` 해당 `.pack/v<K>/pack.json` ``
- 17행: `해당 src/v<K>/ 전체` → `해당 .pack/v<K>/ 전체`
- 25행: `` `문제해설_<N>장_웹과제예상_v<K>.html`(+MD·figures·자료 폴더) `` → `` `문제해설_<N>장_웹과제예상_v<K>.html`(MD·figures·자료 폴더는 `.pack/`) ``

`references/question-blueprint.md:3`: `## blueprint.md (.pack/v<K>/blueprint.md)`

Run: `grep -rn "src/v" .agents/skills/bio-webquiz-forecast/SKILL.md .agents/skills/bio-webquiz-forecast/references`
Expected: 출력 없음

- [ ] **Step 6: 통과 확인**

Run: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests 2>&1 | tail -3`
Expected: `test_repo_v1.test_v1_passes_check`만 실패(실제 4장 v1이 아직 `src/v1`에 있어서다. Task 5에서 이전하면 통과한다). 나머지는 모두 통과한다. 출력에서 실패가 이 하나뿐인지 확인한다.

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast/scripts/build.py .agents/skills/bio-webquiz-forecast/scripts/check.py .agents/skills/bio-webquiz-forecast/SKILL.md .agents/skills/bio-webquiz-forecast/references/explanation-handoff.md .agents/skills/bio-webquiz-forecast/references/question-blueprint.md .agents/skills/bio-webquiz-forecast/tests/_util.py .agents/skills/bio-webquiz-forecast/tests/test_build.py .agents/skills/bio-webquiz-forecast/tests/test_check.py .agents/skills/bio-webquiz-forecast/tests/test_skill_files.py
git commit -m "feat(bio-webquiz-forecast): keep sources under .pack" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: bio-problem-explain forecast 부속 파일을 `.pack/`으로

**Files:**
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_shared.py:10`
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_render.py:12,18-27,144-146,195-199,235-237`
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_forecast.py:5,34`
- Modify: `.agents/skills/bio-problem-explain/SKILL.md:43,62,98`
- Test: `tests/forecast_helpers.py:8,47`, `tests/test_forecast_source.py:40,82`, `tests/test_forecast_pipeline.py:38,48,57,69,129,180-183`, `tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 1의 `PACK`, `rebase_md(text, side)`; Task 2의 `build.py <장>/.pack/v<K>` CLI
- Produces: `mpe_render.side_of(pack) -> str | None`(review는 `".assets"`, forecast는 `".pack"`, homework는 `None`); forecast의 `names(pack)`는 `(stem, ".pack/figures_<stem>", ".pack/자료_<stem>")`를 돌려준다.

- [ ] **Step 1: 테스트 수정과 새 실패 테스트 작성**

`tests/forecast_helpers.py` 8행과 47행:

```python
    src = folder / '.pack' / f'v{version}'
```

```python
    src = path.parent/'.pack'/f'v{version}'
```

`tests/test_forecast_source.py` 40행과 82행의 `'src/v5'`를 `'.pack/v5'`로 바꾸고, 파일 끝에 추가한다.

```python
def test_old_src_layout_rejected(tmp_path):
    source = forecast_source_file(tmp_path)
    old = source.parent / 'src'
    old.mkdir()
    (source.parent / '.pack' / 'v5').rename(old / 'v5')
    with pytest.raises(ExplainError):
        load_source(source, tmp_path)
```

`tests/test_forecast_pipeline.py`:
- 38행:

```python
    assert names(item['pack']) == ('문제해설_4장_웹과제예상_v5', '.pack/figures_문제해설_4장_웹과제예상_v5', '.pack/자료_문제해설_4장_웹과제예상_v5')
```

- 48행:

```python
    for name in ('문제해설_4장_웹과제예상_v5.html', '.pack/문제해설_4장_웹과제예상_v5.md', '.pack/자료_문제해설_4장_웹과제예상_v5/validation.json'):
```

- 57·69·129행의 `'src/v5'`를 `'.pack/v5'`로 바꾼다.
- 맨 위 import에 `import re`를 추가한다.
- 180–183행 `test_forecast_outputs_stay_beside_html`을 아래 두 테스트로 바꾼다.

```python
def test_forecast_side_files_live_in_pack(tmp_path):
    source, run, item = build_run(tmp_path)
    artifacts = load_artifacts(item)
    root = artifacts.html.parent
    assert artifacts.md.parent == root / '.pack'
    assert not (root / '.assets').exists()
    html = artifacts.html.read_text(encoding='utf-8')
    assert 'href=".pack/자료_문제해설_4장_웹과제예상_v5/vendor/katex/katex.min.css"' in html
    md = artifacts.md.read_text(encoding='utf-8')
    assert '](.pack/' not in md
    for target in re.findall(r'\]\((\.\./[^)]+)\)', md):  # 바깥 링크는 .pack 기준으로 한 단계 더 올라간다
        assert target.startswith('../../../'), target


def test_forecast_publish_keeps_root_clean_and_sources_intact(tmp_path):
    source, run, item = build_run(tmp_path)
    pack_json = source.parent / '.pack' / 'v5' / 'pack.json'
    before = pack_json.read_bytes()
    approve(item)
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    root = sorted(p.name for p in source.parent.iterdir())
    assert all(n == '.pack' or n.endswith('.html') for n in root), root
    assert pack_json.read_bytes() == before
```

`tests/test_skill_files.py` 끝에 추가한다.

```python
def test_skill_documents_forecast_pack_layout():
    text=(S/'SKILL.md').read_text(encoding='utf-8')
    assert 'src/v<K>' not in text
    for needle in ('웹과제예상/<N>장/.pack/v<K>/pack.json','.pack/문제해설_<N>장_웹과제예상_v<K>.md',
                   '.pack/figures_문제해설_<N>장_웹과제예상_v<K>/','.pack/자료_문제해설_<N>장_웹과제예상_v<K>/'):
        assert needle in text,needle
```

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest -q .agents/skills/bio-problem-explain/tests/test_forecast_source.py .agents/skills/bio-problem-explain/tests/test_forecast_pipeline.py .agents/skills/bio-problem-explain/tests/test_skill_files.py 2>&1 | tail -5`
Expected: FAIL (`mpe_forecast`이 아직 `src/v5`를 찾아 'pack.json' 누락 오류가 나고, names 단언과 문서 테스트가 실패)

- [ ] **Step 3: `mpe_shared.py`와 `mpe_forecast.py` 구현**

`mpe_shared.py:10`:

```python
from assets_path import PACK, SIDE, migrate_md, moves, rebase_md
```

`mpe_forecast.py:5`와 34행:

```python
from mpe_shared import Node, parse, inner, compact, math_delimiter_errors, prose_text, PACK
```

```python
        src = path.parent / PACK / f'v{version}'
```

- [ ] **Step 4: `mpe_render.py` 구현**

12행 import에 `PACK`을 추가한다.

```python
from mpe_shared import Node, parse, inner, outer, compact, Ctx, convert, check_md, SIDE, PACK, rebase_md
```

18–27행 `names`를 바꾼다.

```python
SIDES = {'review': SIDE, 'forecast': PACK}  # profile → hidden folder for side files (homework: none)

def side_of(pack):
    return SIDES.get(pack.profile)

def names(pack):
    if pack.profile == 'forecast':
        stem = f'문제해설_{pack.range}_{pack.slug}'
        fig, data = f'figures_{stem}', f'자료_{stem}'
    else:
        stem = f'과제{pack.range}_문제설명_{pack.slug}' if pack.profile == 'homework' else f'문제설명_{pack.range}_{pack.slug}'
        range_ = f'hw{pack.range}' if pack.profile == 'homework' else pack.range
        fig, data = f'figures_문제설명_{range_}_{pack.slug}', f'자료_문제설명_{range_}_{pack.slug}'
    side = side_of(pack)
    return (stem, f'{side}/{fig}', f'{side}/{data}') if side else (stem, fig, data)
```

144–146행:

```python
    side = side_of(pack)
    html_path = stage / f'{stem}.html'
    md_path = (stage / side if side else stage) / f'{stem}.md'
```

195–199행:

```python
    md_ref = f'{side}/{md_path.name}' if side else md_path.name
    ctx = Ctx([(html_path.name, md_ref)], str(stage / fig_name), fig_name, prefix='explain')
    convert_markdown(html_path, md_path, ctx)
    if side:  # MD was written relative to the HTML folder; it lives in the side folder, so rebase once
        md_path.write_text(rebase_md(md_path.read_text(encoding='utf-8'), side), encoding='utf-8')
```

235–237행:

```python
        # Side-folder MD (review .assets, forecast .pack) drops that prefix from image paths.
        side = side_of(pack)
        prefix = side + '/' if side else ''
        wanted_images = Counter(unquote(n.attrs.get('src', '')).removeprefix(prefix) for n in main.find_all(lambda n: n.tag == 'img'))
```

`build_explanation` 안에 `review` 변수를 쓰는 곳이 더 있는지 확인하고 모두 `side`로 바꾼다.

Run: `grep -n "review = \|if review\|else review\|SIDE" .agents/skills/bio-problem-explain/scripts/mpe_render.py`
Expected: `SIDES = {...}` 정의 한 줄과 import 줄만 나옴

`mpe_publish.py:41`의 `md_rel = (Path(fig_name).parent / (stem + '.md'))`는 `fig_name`이 `.pack/figures_…`면 `.pack/<stem>.md`가 되므로 바꾸지 않는다. 주석만 고친다.

```python
        md_rel = (Path(fig_name).parent / (stem + '.md')).as_posix()  # <side>/<stem>.md for review/forecast, <stem>.md for homework
```

- [ ] **Step 5: `SKILL.md` 수정**

- 43행: `` 해당 `웹과제예상/<N>장/src/v<K>/pack.json` `` → `` 해당 `웹과제예상/<N>장/.pack/v<K>/pack.json` ``
- 62행: `` forecast는 위 `.pack/` 대신 해당 버전 pack.json/blueprint.md를 읽고 `` → `` forecast는 복습노트 `.pack/`의 key-check·variants 대신 `웹과제예상/<N>장/.pack/v<K>/`의 pack.json/blueprint.md를 읽고 ``
- 98행 앞부분을 아래로 바꾼다(제목·읽음 키 문장은 그대로 둔다).

```
forecast 출력은 같은 `웹과제예상/<N>장/` 폴더의 `문제해설_<N>장_웹과제예상_v<K>.html`과, 숨김 폴더의 `.pack/문제해설_<N>장_웹과제예상_v<K>.md`, `.pack/figures_문제해설_<N>장_웹과제예상_v<K>/`, `.pack/자료_문제해설_<N>장_웹과제예상_v<K>/`다. 장 폴더 루트에는 HTML과 `.pack/`만 둔다.
```

- [ ] **Step 6: 통과 확인**

Run: `python -m pytest -q .agents/skills/bio-problem-explain/tests 2>&1 | grep ^FAILED | diff "$TEMP/baseline.txt" -`
Expected: 출력 없음(기준선 밖 새 실패 없음; 새 forecast 테스트 4개 통과)

Run: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests 2>&1 | tail -3`
Expected: Task 2와 같음(`test_v1_passes_check`만 실패)

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-problem-explain/scripts/mpe_shared.py .agents/skills/bio-problem-explain/scripts/mpe_render.py .agents/skills/bio-problem-explain/scripts/mpe_forecast.py .agents/skills/bio-problem-explain/scripts/mpe_publish.py .agents/skills/bio-problem-explain/SKILL.md .agents/skills/bio-problem-explain/tests/forecast_helpers.py .agents/skills/bio-problem-explain/tests/test_forecast_source.py .agents/skills/bio-problem-explain/tests/test_forecast_pipeline.py .agents/skills/bio-problem-explain/tests/test_skill_files.py
git commit -m "feat(bio-problem-explain): put forecast explanation assets under .pack" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: 이전 스크립트 `migrate_forecast_pack.py`

**Files:**
- Create: `scripts/migrate_forecast_pack.py`
- Create: `tests/test_migrate_forecast_pack.py`

**Interfaces:**
- Consumes: Task 1의 `PACK`, `moves(name, side)`, `relocate(url, side)`, `migrate_md(text, side)`
- Produces:
  - `rewrite_html(text: str) -> str`
  - `rewrite_record(text: str, digests: dict[str, str]) -> str`
  - `migrate_chapter(chapter: Path, apply: bool) -> list[str]`
  - `problems(chapter: Path) -> list[str]` (깨진 링크 `broken: …`와 루트에 남은 항목 `stray: …`)
  - `main(argv: list[str] | None = None) -> int` (CLI `[ROOT=웹과제예상] [--apply] [--check]`)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_migrate_forecast_pack.py`:

```python
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

from scripts.migrate_forecast_pack import main, migrate_chapter, problems

STEM = "문제해설_5장_웹과제예상_v1"
FIG = f"figures_{STEM}"
DATA = f"자료_{STEM}"
NOTE = "../../복습노트/1001/정리노트_1001_X.html"
ENC_NOTE = "../../" + quote("복습노트") + "/1001/" + quote("정리노트_1001_X.html") + "#s4"


def crlf(text):
    return text.replace("\n", "\r\n").encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(p, raw):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw)


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None)
            for p in sorted(Path(root).rglob("*"))}


class TestMigrateForecast(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "웹과제예상"
        self.ch = self.root / "5장"
        put(Path(self.tmp.name) / "복습노트/1001/정리노트_1001_X.html", b"<html></html>")
        put(self.ch / "복습문제_5장_웹과제예상_v1.html", crlf(f'<a href="{NOTE}">노트</a>\n'))
        put(self.ch / "src/v1/pack.json", b'{"chapter": 5, "version": 1}')
        put(self.ch / "src/v1/blueprint.md", crlf("| 카드 |\n"))
        put(self.ch / "src/v1/cards/p1.html", b"<article></article>")
        self.html = crlf(f'<link href="{DATA}/vendor/katex/katex.min.css">\n'
                         f'<img src="{quote(FIG)}/explain-fig-1.svg">\n')
        put(self.ch / f"{STEM}.html", self.html)
        self.md = crlf(f"![그림]({FIG}/explain-fig-1.svg)\n[노트]({ENC_NOTE})\n[p1](#p1)\n")
        put(self.ch / f"{STEM}.md", self.md)
        put(self.ch / FIG / "explain-fig-1.svg", b"<svg/>")
        put(self.ch / DATA / "vendor/katex/katex.min.css", b"x")
        put(self.ch / DATA / "evidence/e.md", b"e")
        ctx = str(self.ch / "src" / "v1" / "pack.json").replace("/", "\\")
        manifest = {"context_hashes": [[ctx, "c"]],
                    "files": {f"{FIG}/explain-fig-1.svg": sha(b"<svg/>"), f"{STEM}.html": sha(self.html),
                              f"{STEM}.md": sha(self.md), f"{DATA}/evidence/e.md": sha(b"e")}}
        put(self.ch / DATA / "manifest.json", crlf(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"))
        validation = {"references": [{"path": ctx, "sha256": "c"}],
                      "artifact_hashes": {f"{STEM}.html": sha(self.html), f"{STEM}.md": sha(self.md)}}
        put(self.ch / DATA / "validation.json", crlf(json.dumps(validation, ensure_ascii=False, indent=2) + "\n"))
        put(self.root / "커닝페이퍼/5장/spec.json", b"{}")

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_changes_nothing(self):
        before = snapshot(self.root)
        acts = migrate_chapter(self.ch, apply=False)
        self.assertIn("move src/v1 -> .pack/v1", acts)
        self.assertEqual(snapshot(self.root), before)

    def test_apply_layout(self):
        migrate_chapter(self.ch, apply=True)
        self.assertEqual(sorted(p.name for p in self.ch.iterdir()),
                         sorted([".pack", "복습문제_5장_웹과제예상_v1.html", f"{STEM}.html"]))
        self.assertEqual(sorted(p.name for p in (self.ch / ".pack").iterdir()),
                         sorted(["v1", FIG, DATA, f"{STEM}.md"]))
        self.assertTrue((self.ch / ".pack/v1/cards/p1.html").is_file())
        self.assertEqual(problems(self.ch), [])

    def test_html_links_relocated(self):
        migrate_chapter(self.ch, apply=True)
        text = (self.ch / f"{STEM}.html").read_bytes().decode("utf-8")
        self.assertIn(f'href=".pack/{DATA}/vendor/katex/katex.min.css"', text)
        self.assertIn(f'src=".pack/{quote(FIG)}/explain-fig-1.svg"', text)
        review = (self.ch / "복습문제_5장_웹과제예상_v1.html").read_bytes()
        self.assertEqual(review, crlf(f'<a href="{NOTE}">노트</a>\n'))

    def test_md_links_rebased_and_crlf_kept(self):
        migrate_chapter(self.ch, apply=True)
        raw = (self.ch / ".pack" / f"{STEM}.md").read_bytes()
        text = raw.decode("utf-8")
        self.assertIn(f"]({FIG}/explain-fig-1.svg)", text)
        self.assertIn("](../" + ENC_NOTE + ")", text)
        self.assertIn("](#p1)", text)
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))

    def test_records_rewritten(self):
        migrate_chapter(self.ch, apply=True)
        pack = self.ch / ".pack"
        raw = (pack / DATA / "manifest.json").read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        manifest = json.loads(raw)
        self.assertIn("\\.pack\\v1\\pack.json", manifest["context_hashes"][0][0])
        files = manifest["files"]
        self.assertEqual(sorted(files), sorted([f".pack/{FIG}/explain-fig-1.svg", f"{STEM}.html",
                                                f".pack/{STEM}.md", f".pack/{DATA}/evidence/e.md"]))
        for name, digest in files.items():
            self.assertEqual(digest, sha((self.ch / name).read_bytes()), name)
        validation = json.loads((pack / DATA / "validation.json").read_bytes())
        self.assertIn("\\.pack\\v1\\pack.json", validation["references"][0]["path"])
        self.assertEqual(validation["artifact_hashes"][f".pack/{STEM}.md"], sha((pack / f"{STEM}.md").read_bytes()))
        self.assertEqual(validation["artifact_hashes"][f"{STEM}.html"], sha((self.ch / f"{STEM}.html").read_bytes()))

    def test_idempotent(self):
        migrate_chapter(self.ch, apply=True)
        after = snapshot(self.root)
        self.assertEqual(migrate_chapter(self.ch, apply=True), [])
        self.assertEqual(snapshot(self.root), after)

    def test_clash_moves_nothing(self):
        put(self.ch / ".pack/v1/pack.json", b"{}")
        before = snapshot(self.root)
        with self.assertRaises(FileExistsError):
            migrate_chapter(self.ch, apply=True)
        self.assertEqual(snapshot(self.root), before)

    def test_main_skips_non_chapter_and_checks(self):
        cheat = snapshot(self.root / "커닝페이퍼")
        self.assertEqual(main([str(self.root), "--check"]), 1)  # 루트에 src·md·figures가 남아 있음
        self.assertEqual(main([str(self.root), "--apply"]), 0)
        self.assertEqual(main([str(self.root), "--check"]), 0)
        self.assertEqual(snapshot(self.root / "커닝페이퍼"), cheat)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest -q tests/test_migrate_forecast_pack.py 2>&1 | tail -3`
Expected: `ModuleNotFoundError: No module named 'scripts.migrate_forecast_pack'`

- [ ] **Step 3: 구현**

`scripts/migrate_forecast_pack.py`:

```python
"""웹과제예상/<N>장/ 부속 파일을 숨김 폴더 `.pack/`으로 옮기는 일회성 이전 스크립트.

장 폴더 루트에는 *.html 과 .pack/ 만 남긴다. `src/v<K>/`는 `.pack/v<K>/`로, 그 밖의 비 HTML
항목(문제해설 MD, figures_*, 자료_*)은 `.pack/<이름>`으로 간다. 루트 HTML의 상대 src/href는
`relocate`로, 옮긴 MD의 `](t)`는 `migrate_md`로, 자료 폴더의 manifest.json·validation.json은
`rewrite_record`로 고친다.

    python scripts/migrate_forecast_pack.py [ROOT=웹과제예상] [--apply] [--check]

기본은 dry-run(할 일만 출력)이다. 새 내용은 옮기기 전에 모두 계산하고, 충돌이 있으면 아무것도
옮기지 않는다. 파일은 바이트로 읽고 써서 CRLF를 지킨다. 두 번 돌려도 결과가 같다.
git 기록은 커밋 때 `git add -A 웹과제예상`의 rename 감지가 처리한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
REVIEW_SCRIPTS = REPO / ".agents" / "skills" / "bio-review-pack" / "scripts"
if str(REVIEW_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS))

from assets_path import PACK, migrate_md, moves, relocate  # noqa: E402

SRC = "src"
RECORDS = ("manifest.json", "validation.json")
HASHED = ("files", "artifact_hashes")

_ATTR = re.compile(r'(src|href)="([^"]*)"')
# 검사용: `](t)`, `](t "제목")`, `](<t>)` 모두에서 대상만 뽑는다.
_MD_CHECK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
_CHAPTER = re.compile(r"[1-9]\d*장")
_VERSION = re.compile(r"v\d+")
_SRC_PATH = re.compile(r"([\\/])src([\\/])(v\d+)(?=[\\/])")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _nfc(name: str) -> str:
    return unicodedata.normalize("NFC", name)


def _read(p: Path) -> str:
    return p.read_bytes().decode("utf-8")


def _write(p: Path, text: str) -> None:
    p.write_bytes(text.encode("utf-8"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_html(name: str) -> bool:
    return _nfc(name).lower().endswith((".html", ".htm"))


def rewrite_html(text: str) -> str:
    """장 폴더 루트 HTML의 상대 src/href를 `.pack/` 이전 뒤 위치로 고친다."""
    return _ATTR.sub(lambda m: f'{m.group(1)}="{relocate(m.group(2), PACK)}"', text)


def rewrite_record(text: str, digests: dict[str, str]) -> str:
    """해설 manifest.json·validation.json 본문을 이전 뒤 위치에 맞게 고친다.

    문자열 속 `src\\v<K>`·`src/v<K>` 경로는 `.pack`으로, `files`·`artifact_hashes`의 장 폴더 기준
    키는 `relocate`로 옮긴다. 키가 `digests`(옛 키 NFC → 새 내용 해시)에 있으면 해시도 바꾼다.
    """
    nl = "\r\n" if "\r\n" in text else "\n"

    def fix(o):
        if isinstance(o, dict):
            return {k: fix(v) for k, v in o.items()}
        if isinstance(o, list):
            return [fix(x) for x in o]
        if isinstance(o, str):
            return _SRC_PATH.sub(lambda m: m.group(1) + PACK + m.group(2) + m.group(3), o)
        return o

    data = fix(json.loads(text))
    for key in HASHED:
        if isinstance(data.get(key), dict):
            data[key] = {relocate(name, PACK): digests.get(_nfc(name), digest)
                         for name, digest in data[key].items()}
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").replace("\n", nl)


def _sorted(paths):
    return sorted(paths, key=lambda p: _nfc(p.name))


def migrate_chapter(chapter: Path, apply: bool) -> list[str]:
    """장 폴더 하나의 할 일(`move X -> Y`, `rewrite Z`)을 돌려주고, `apply`일 때만 실행한다."""
    chapter = Path(chapter)
    pack = chapter / PACK
    src = chapter / SRC
    versions = _sorted(p for p in src.iterdir() if p.is_dir()) if src.is_dir() else []
    if src.is_dir() and any(not (p.is_dir() and _VERSION.fullmatch(p.name)) for p in src.iterdir()):
        raise ValueError(f"{src}에 v<K> 폴더가 아닌 항목이 있음")
    movers = [p for p in _sorted(chapter.iterdir()) if _nfc(p.name) != SRC and moves(p.name, PACK)]
    plan = [(v, pack / v.name) for v in versions] + [(p, pack / p.name) for p in movers]
    clash = [str(dst.relative_to(chapter)) for _, dst in plan if dst.exists()]
    if clash:
        raise FileExistsError(f"{chapter}에 이미 있음: {', '.join(clash)}")

    # 옮기기 전에 새 내용을 모두 계산한다.
    digests: dict[str, str] = {}
    html = []
    for p in _sorted(q for q in chapter.iterdir() if q.is_file() and _is_html(q.name)):
        old = _read(p)
        new = rewrite_html(old)
        if new != old:
            html.append((p, new))
            digests[_nfc(p.name)] = _sha(new)
    mds = []
    for p in movers:
        if p.is_file() and _nfc(p.name).lower().endswith(".md"):
            old = _read(p)
            new = migrate_md(old, PACK)
            if new != old:
                mds.append((p.name, new))
                digests[_nfc(p.name)] = _sha(new)
    records = []
    for p in movers:
        for name in RECORDS:
            f = p / name
            if p.is_dir() and f.is_file():
                old = _read(f)
                new = rewrite_record(old, digests)
                if new != old:
                    records.append((Path(p.name) / name, new))

    actions = [f"move {SRC}/{v.name} -> {PACK}/{v.name}" for v in versions]
    actions += [f"move {_nfc(p.name)} -> {PACK}/{_nfc(p.name)}" for p in movers]
    actions += [f"rewrite {_nfc(p.name)}" for p, _ in html]
    actions += [f"rewrite {PACK}/{_nfc(name)}" for name, _ in mds]
    actions += [f"rewrite {PACK}/{_nfc(rel.as_posix())}" for rel, _ in records]
    if apply and actions:
        pack.mkdir(exist_ok=True)
        for old, dst in plan:
            os.rename(old, dst)
        if src.is_dir():
            src.rmdir()
        for p, new in html:
            _write(p, new)
        for name, new in mds:
            _write(pack / name, new)
        for rel, new in records:
            _write(pack / rel, new)
    return actions


def _relative(url: str) -> bool:
    return bool(url) and url[0] not in "#/" and not _SCHEME.match(url)


def _missing(base: Path, url: str) -> bool:
    path = unquote(re.split(r"[?#]", url, maxsplit=1)[0])
    return bool(path) and not os.path.exists(base / path)


def problems(chapter: Path) -> list[str]:
    """루트에 남은 비 HTML 항목(`stray: …`)과 대상이 없는 상대 링크(`broken: …`)."""
    chapter = Path(chapter)
    out = [f"stray: {_nfc(p.name)}" for p in _sorted(chapter.iterdir())
           if _nfc(p.name) not in (PACK, ".DS_Store") and not _is_html(p.name)]
    for p in _sorted(q for q in chapter.iterdir() if q.is_file() and _is_html(q.name)):
        for m in _ATTR.finditer(_read(p)):
            if _relative(m.group(2)) and _missing(chapter, m.group(2)):
                out.append(f"broken: {_nfc(p.name)}: {m.group(2)}")
    pack = chapter / PACK
    if pack.is_dir():
        for p in _sorted(q for q in pack.iterdir() if q.is_file() and _nfc(q.name).lower().endswith(".md")):
            for m in _MD_CHECK.finditer(_read(p)):
                if _relative(m.group(1)) and _missing(pack, m.group(1)):
                    out.append(f"broken: {PACK}/{_nfc(p.name)}: {m.group(1)}")
    return out


def _chapters(root: Path) -> list[Path]:
    return _sorted(p for p in root.iterdir() if p.is_dir() and _CHAPTER.fullmatch(_nfc(p.name)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="웹과제예상 장 폴더 부속 파일을 .pack/으로 옮긴다.")
    ap.add_argument("root", nargs="?", default="웹과제예상")
    ap.add_argument("--apply", action="store_true", help="실제로 옮기고 고친다(기본은 dry-run)")
    ap.add_argument("--check", action="store_true", help="남은 항목·깨진 링크를 출력하고 있으면 종료 코드 1")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Windows 콘솔에서 한글 이름 출력
        sys.stdout.reconfigure(encoding="utf-8")

    root = Path(args.root)
    if not root.is_dir():
        print(f"폴더 없음: {root}", file=sys.stderr)
        return 2
    chapters = _chapters(root)

    if args.apply or not args.check:
        total = 0
        for ch in chapters:
            acts = migrate_chapter(ch, apply=args.apply)
            total += len(acts)
            for a in acts:
                print(f"{_nfc(ch.name)}: {a}")
        verb = "applied" if args.apply else "planned (dry-run)"
        print(f"{total} actions {verb}" if total else "nothing to do")

    if args.check:
        found = [f"{_nfc(ch.name)}/{x}" for ch in chapters for x in problems(ch)]
        for x in found:
            print(x)
        print(f"{len(found)} problems")
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `python -m pytest -q tests/test_migrate_forecast_pack.py 2>&1 | tail -3`
Expected: `8 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/migrate_forecast_pack.py tests/test_migrate_forecast_pack.py
git commit -m "feat(scripts): add 웹과제예상 .pack migration" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 실제 4·5장 이전과 검증

**Files:**
- Modify (이동·링크 수정): `웹과제예상/4장/**`, `웹과제예상/5장/**`
- Test: `.agents/skills/bio-webquiz-forecast/tests/test_repo_v1.py`

**Interfaces:**
- Consumes: Task 4의 CLI. Task 2의 `check.check(html)`(이제 `.pack/v1`을 읽음)

- [ ] **Step 1: 실제 저장소 레이아웃 테스트 추가(실패)**

`test_repo_v1.py` 맨 위 import에 `import re`를 추가하고 `TestRepoV1`에 메서드를 추가한다.

```python
    def test_chapter_folders_hold_only_html_and_pack(self):
        chapters = [d for d in (REPO / "웹과제예상").iterdir() if re.fullmatch(r"[1-9]\d*장", d.name)]
        self.assertGreaterEqual(len(chapters), 2)
        for d in chapters:
            extra = sorted(p.name for p in d.iterdir() if p.name != ".pack" and not p.name.endswith(".html"))
            self.assertEqual(extra, [], d.name)
            self.assertTrue((d / ".pack" / "v1" / "pack.json").is_file(), d.name)
```

Run: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -p test_repo_v1.py 2>&1 | tail -3`
Expected: FAIL (`src`, `figures_…` 등이 남아 있음)

- [ ] **Step 2: dry-run 확인**

Run: `python scripts/migrate_forecast_pack.py 웹과제예상`
Expected: 4장은 `move src/v1..v4 -> .pack/v1..v4` 4줄. 5장은 `move src/v1·v2`, `move figures_…·자료_…·문제해설_….md` 6줄, `rewrite 문제해설_5장_웹과제예상_v1.html`·`v2.html`, `rewrite .pack/문제해설_….md` 2줄, `rewrite .pack/자료_…/manifest.json`·`validation.json` 4줄. 마지막 줄은 `N actions planned (dry-run)`. `커닝페이퍼`는 나오지 않아야 한다. 이와 다르면 멈추고 보고한다.

- [ ] **Step 3: 적용과 검사**

```bash
python scripts/migrate_forecast_pack.py 웹과제예상 --apply
python scripts/migrate_forecast_pack.py 웹과제예상 --check
```

Expected: 두 번째 명령은 `0 problems`를 출력하고 종료 코드 0. 다시 `--apply`를 돌리면 `nothing to do`가 나와야 한다.

Run: `ls -a 웹과제예상/4장 웹과제예상/5장 웹과제예상/5장/.pack`
Expected: 장 폴더에는 `.pack`과 HTML만 있다. `5장/.pack`에는 `v1 v2 figures_…_v1 figures_…_v2 자료_…_v1 자료_…_v2 문제해설_…_v1.md 문제해설_…_v2.md`가 있다.

- [ ] **Step 4: 전체 테스트**

```bash
python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests 2>&1 | tail -3
python -m unittest discover -s .agents/skills/bio-review-pack/tests 2>&1 | tail -3
python -m pytest -q .agents/skills/bio-problem-explain/tests 2>&1 | grep ^FAILED | diff "$TEMP/baseline.txt" -
python -m pytest -q tests/test_migrate_forecast_pack.py tests/test_migrate_review_assets.py 2>&1 | tail -3
```

Expected: webquiz-forecast `OK`(`test_v1_passes_check`와 새 레이아웃 테스트 포함), review-pack `OK`, problem-explain diff 출력 없음. 마지막 명령은 기준선 실패 `test_apply_layout_and_links` 1개만 실패한다.

- [ ] **Step 5: 브라우저 확인**

내장 브라우저(`mcp__Claude_Browser__preview_start`의 `url`)로 `file:///C:/Users/Hyunjun/Desktop/현준대학/26-2/생명과학/웹과제예상/5장/문제해설_5장_웹과제예상_v2.html`을 연다. 아래 JS 결과가 모두 참인지 본다.

```js
({katex: document.querySelectorAll('.katex').length > 0,
  images: [...document.images].every(i => i.complete && i.naturalWidth > 0),
  font: getComputedStyle(document.body).fontFamily.includes('Pretendard')})
```

`복습문제_5장_웹과제예상_v2.html`도 열어 "정리노트" 링크가 `복습노트/…` HTML로 열리는지 확인한다. 하나라도 거짓이면 멈추고 깨진 경로를 보고한다.

- [ ] **Step 6: 커밋**

```bash
git add -A 웹과제예상/4장 웹과제예상/5장
git add .agents/skills/bio-webquiz-forecast/tests/test_repo_v1.py
git status --short 웹과제예상 | head -20
git commit -m "docs(forecast): move side files into .pack" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`git status`에서 `R`(rename)으로 표시되는지 확인한다. HTML 2개, MD 2개, JSON 4개는 `RM`이나 `M`이어도 된다.
