# bio-review-pack 보강 모드·설계 기록·후속 보완 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 이미 만든 복습팩에 카드 번호를 바꾸지 않고 웹과제 원문·새 변형을 덧붙이는 보강 모드(`/bio-review-pack <range> augment`)와 팩 설계 기록(`.pack/`)을 만들고, 정리노트 보충·당황 패턴·변형 규칙·카드 손질을 마친다.

**Architecture:** `scripts/augment.py`가 기계적인 두 끝(기존 카드·manifest 추출 / 보호 검사·정렬·문구 갱신·복습문제만 조립)을 맡고, 그 사이(문항 감사, 변형 설계, 카드 작성)는 기존 `problem-selection.md`·`card-rules.md` 절차를 그대로 쓴다. 조립 결과와 설계 기록은 `assemble.save_pack_records`가 `복습노트/<range>/.pack/`에 남기고, MD는 `html2md --only review`로 복습문제만 다시 변환한다.

**Tech Stack:** Python 3 표준 라이브러리(`unittest`, `re`, `json`, `html`, `shutil`), 기존 스킬 스크립트(`assemble.py`, `manifest.py`, `html2md.py`, `check_html.py`, `review_interaction.py`). pytest는 없다.

**Spec:** `docs/superpowers/specs/2026-10-01-bio-review-augment-design.md` (선행: `docs/superpowers/specs/2026-10-01-bio-review-webquiz-variants-design.md`)

## Global Constraints

- 작업은 `bio-review-webquiz-variants`에서 만든 **별도 워크트리**에서 한다. 원래 폴더(`/Users/hyunjun_macbook_pro/Documents/Univ/생명과학`)는 1001 세션이 쓰고 있으니 거기서 파일을 쓰거나 커밋하지 않는다.
- 기존 카드 번호(`pN`)는 절대 다시 매기지 않는다.
- `복습노트/*/풀이기록/`은 읽지도 쓰지도 않는다.
- 1001 팩(`복습노트/1001/`)은 이번 작업에서 수정하지 않는다(읽기 전용 테스트 대상은 허용).
- 학생용 HTML·MD에 STT 녹음 시각(`MM:SS`), 원문자(①~⑳), 이모지를 쓰지 않는다. 문장은 "~해요" 체.
- 보충 배지 글자: `보충 · 수업에서 다루지 않았어요`(교과서·외부에만 있음), `보충 · 노트에 빠졌던 수업 내용`(STT나 강의노트에 있는데 정리노트에 없던 것).
- 변형 표시 값: `+낯선참`(부정형 문제의 참인 오답 보기에만, 팩당 1~2개), `+장섞기`(앞선 팩 개념, 앞선 팩이 있으면 1개 이상).
- 9단계 보고 문항 줄: `포함 N (웹과제 w, 기출 x) · 변형 v (쌍둥이 t · 그림 g · 상황 s · ㄱㄴㄷ k · 부정형 n · 용어 r · 낯선참 u · 장섞기 c)`
- 테스트 실행: `cd <worktree>/.agents/skills/bio-review-pack/tests && python3 -m unittest discover -p "test_*.py"`, 브라우저 검사 `python3 browser_check_review.py`. bio-cheatsheet를 고치면 `cd <worktree>/.agents/skills/bio-cheatsheet/tests && python3 -m unittest discover -p "test_*.py"`.
- 커밋은 작업별로 나누고 메시지 마지막 줄은 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 각 bash 블록 맨 앞에서 `WT="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment"; S="$WT/.agents/skills/bio-review-pack"`(필요하면 `RUN=…`)을 다시 설정한다. 계획의 블록이 앞 블록 변수를 쓰면 이 줄을 붙여 실행한다.
- 한글 파일명은 NFC/NFD가 섞여 있다. 파일을 찾을 때는 `unicodedata.normalize("NFC", name)`으로 비교한다.

## Review Focus

1. **NFD 파일명 팩** — macOS가 만든 NFD 이름(`복습문제_…html`)의 팩도 extract·build가 같은 파일을 찾아 그 파일을 덮어써야 하고, NFC 이름의 복제 파일이 새로 생기면 안 된다. (Task 4 테스트 `test_nfd_file_names`)
2. **연속 보강** — 같은 팩을 두 번 보강하면 두 번째 extract가 첫 보강의 새 카드를 기존 카드로 보고 다음 번호를 이어 가야 하며, `log.md`에 줄이 하나씩 쌓여야 한다. (Task 5 `test_second_augment_continues_numbering`)
3. **문항 수 표현이 없는 안내 문구** — 안내에 "웹과제 N문항" 같은 표현이 없으면 안내를 건드리지 않고 경고만 내야 한다(문장 삭제 금지). (Task 5 `test_intro_without_counts_is_left_alone`)
4. **partA가 없던 팩에 partA가 생김(1001류)** — parts 목록 앞에 `A. 웹과제`가 들어가고, 안내 맨 앞에 "웹과제 …", 꼬리말 `기출(…)` 뒤에 ` · 웹과제(N장)`이 붙어야 한다. (Task 5 `test_refresh_inserts_new_part_phrases`)
5. **`.pack` manifest와 HTML 불일치** — 누가 HTML을 손으로 고쳐 카드 집합이 달라졌으면 extract가 차이를 나열하고 멈춰야 한다(조용히 HTML로 덮지 않음). (Task 4 `test_pack_manifest_mismatch_stops`)

---

### Task 0: 워크트리 준비와 문서 옮기기

**Files:**
- Move: `docs/superpowers/specs/2026-10-01-bio-review-augment-design.md`, `docs/superpowers/plans/2026-10-01-bio-review-augment.md` (원래 폴더의 미추적 파일 → 워크트리)

**Interfaces:**
- Consumes: 없음
- Produces: 워크트리 경로 `WT`(이후 모든 작업의 저장소 루트), 브랜치 `bio-review-augment`

- [ ] **Step 1: 워크트리 만들기** — `superpowers:using-git-worktrees` 스킬을 따른다. 기준은 `bio-review-webquiz-variants`, 새 브랜치 `bio-review-augment`.

```bash
git -C "/Users/hyunjun_macbook_pro/Documents/Univ/생명과학" worktree add -b bio-review-augment "/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment" bio-review-webquiz-variants
```

이후 `WT=/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment`.

- [ ] **Step 2: 설계·계획 문서를 워크트리로 옮기기**

```bash
SRC="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학"; WT="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment"
for f in docs/superpowers/specs/2026-10-01-bio-review-augment-design.md docs/superpowers/plans/2026-10-01-bio-review-augment.md; do cp "$SRC/$f" "$WT/$f" && rm "$SRC/$f"; done
git -C "$WT" status --short
```
Expected: 두 파일만 `??`로 보인다.

- [ ] **Step 3: 기준 테스트가 통과하는지 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK` (실패하면 멈추고 보고 — 이 작업 탓이 아니다)

- [ ] **Step 4: Commit**

```bash
git -C "$WT" add docs/superpowers/specs/2026-10-01-bio-review-augment-design.md docs/superpowers/plans/2026-10-01-bio-review-augment.md
git -C "$WT" commit -m "docs: add review-pack augment design and plan

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 1: `.pack` 소급 생성 (사라질 원천부터 옮기기)

**Files:**
- Create: `복습노트/{0910,0915,0917,0922,0929}/.pack/manifest.json`, `variants.md`, `log.md`
- Create (0929만): `복습노트/0929/.pack/{question-audit.md,key-check.md,problem-pages.txt}`

**Interfaces:**
- Consumes: 직전 세션 실행 폴더 `D=/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ-----/dd6813f5-c8e1-4522-9756-96fd174c400f/scratchpad/review-pack/<range>/{manifest.json,variants.md}`, 원래 0929 실행 `/tmp/bio-review-pack/0929/{manifest.json,question-audit.md,key-check.md,problem-pages.txt}`
- Produces: `.pack/manifest.json` — `manifest.py` 검증을 통과하고, 그 manifest와 현재 HTML의 카드로 `assemble.build_review`를 돌리면 현재 복습문제 HTML과 **바이트까지 같다**. Task 4·5·8이 이 파일을 읽는다.

- [ ] **Step 1: 원천이 남아 있는지 확인**

```bash
D=/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ-----/dd6813f5-c8e1-4522-9756-96fd174c400f/scratchpad/review-pack
for r in 0910 0915 0917 0922 0929; do ls "$D/$r/manifest.json" "$D/$r/variants.md"; done; ls /tmp/bio-review-pack/0929/
```
Expected: 모든 파일이 보인다. 없는 range는 Step 2에서 건너뛰고(그 팩은 나중에 HTML 복원으로 보강된다) 보고서에 적는다.

- [ ] **Step 2: `.pack` 쓰기와 왕복 검증** (원천 → `.pack`, 그리고 그 manifest로 다시 조립해 현재 HTML과 비교)

```bash
WT="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment" D=/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ-----/dd6813f5-c8e1-4522-9756-96fd174c400f/scratchpad/review-pack python3 - <<'EOF'
import json, os, re, shutil, sys, tempfile, unicodedata as u
from pathlib import Path
wt, d = Path(os.environ["WT"]), Path(os.environ["D"])
sys.path.insert(0, str(wt / ".agents/skills/bio-review-pack/scripts"))
import assemble, manifest as mm
orig0929 = Path("/tmp/bio-review-pack/0929")
CARD = re.compile(r'<article class="card" id="(p\d+)"[^>]*>.*?</article>', re.S)
for r in ("0910", "0915", "0917", "0922", "0929"):
    src = d / r / "manifest.json"
    if not src.is_file():
        print(r, "원천 없음 — 건너뜀"); continue
    m = json.loads(src.read_text(encoding="utf-8"))
    notes = []
    if r == "0929" and (orig0929 / "manifest.json").is_file():
        m["forbidden_outside_preview"] = json.loads((orig0929 / "manifest.json").read_text(encoding="utf-8"))["forbidden_outside_preview"]
        notes.append("금지어: 원래 0929 실행(/tmp/bio-review-pack/0929)에서 복원")
    else:
        notes.append("금지어 미복원(원천 없음) — 다음 보강 때 예고 토픽에서 다시 정한다")
    assert not mm.validate(m), mm.validate(m)
    pack_dir = wt / "복습노트" / r
    review = next(p for p in pack_dir.iterdir() if u.normalize("NFC", p.name).startswith(f"복습문제_{r}_") and p.suffix == ".html")
    html = review.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "cards").mkdir()
        for c in CARD.finditer(html):
            (Path(tmp) / "cards" / f"{c.group(1)}.html").write_text(c.group(0), encoding="utf-8")
        same = assemble.build_review(m, Path(tmp)) == html
    print(r, "왕복", "같음" if same else "다름")
    assert same, f"{r}: .pack manifest로 다시 조립한 결과가 현재 HTML과 다르다 — 멈추고 보고"
    out = pack_dir / ".pack"; out.mkdir(exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(d / r / "variants.md", out / "variants.md")
    if r == "0929":
        for name in ("question-audit.md", "key-check.md", "problem-pages.txt"):
            if (orig0929 / name).is_file():
                shutil.copyfile(orig0929 / name, out / name)
        notes.append("question-audit·key-check·problem-pages는 0929 첫 실행(p1–p34) 기준")
    notes.append("anchor는 직전 보강 manifest 값(기존 카드는 임시값일 수 있음)")
    (out / "log.md").write_text("# 팩 실행 기록\n\n- 2026-10-01 bootstrap: 직전 세션 실행 폴더에서 소급 생성. " + " / ".join(notes) + "\n", encoding="utf-8")
    print(r, "→", out)
EOF
```
Expected: 다섯 range 모두 `왕복 같음`과 경로 출력. `AssertionError`가 나면 멈추고 보고한다.

- [ ] **Step 3: check_html로 manifest 검사**

```bash
WT="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment"; S="$WT/.agents/skills/bio-review-pack"
for r in 0910 0915 0917 0922 0929; do P="$WT/복습노트/$r"; python3 "$S/scripts/check_html.py" --manifest "$P/.pack/manifest.json" --note "$(ls "$P"/정리노트_*.html)" --review "$(ls "$P"/복습문제_*.html)" | tail -3; done
```
Expected: 다섯 번 모두 `OK`. 0929에서 `forbidden-term`만 나오면 금지어가 이미 본문에 있다는 뜻이다. 이 경우 `0929/.pack/log.md` 첫 줄 끝에 ` / 주의: 복원한 금지어 중 <용어>가 본문에 있음`을 덧붙이고 계속한다(팩 본문은 고치지 않는다).

- [ ] **Step 4: Commit**

```bash
git -C "$WT" add 복습노트/0910/.pack 복습노트/0915/.pack 복습노트/0917/.pack 복습노트/0922/.pack 복습노트/0929/.pack
git -C "$WT" commit -m "chore(notes): bootstrap .pack design records for 0910-0929

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `.pack` 저장 계약 (`save_pack_records`) + 백업 스니펫

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/assemble.py` (상단 import, 새 함수, `assemble()` 끝)
- Modify: `.agents/skills/bio-review-pack/SKILL.md` (4단계 백업 스니펫 `want()`, 4단계 설명 한 줄)
- Test: `.agents/skills/bio-review-pack/tests/test_assemble.py`, `tests/test_skill_files.py`

**Interfaces:**
- Consumes: 없음
- Produces: `assemble.save_pack_records(run_dir: Path | str, out_dir: Path | str, mode: str, added_ids: list[str], today: str | None = None, note: str = "") -> Path` — `out_dir/.pack` 경로를 돌려준다. `mode`는 `"full"` 또는 `"augment"`. `assemble.PACK_RECORDS` 튜플.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_assemble.py` 끝(`if __name__` 앞)에 추가

```python
class TestPackRecords(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = self.tmp / "run"
        shutil.copytree(MINI_RUN, self.run)
        self.out = self.tmp / "out"
        self.pack = self.out / ".pack"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_full_assemble_saves_manifest_records_and_log(self):
        (self.run / "variants.md").write_text("| id |\n", encoding="utf-8")
        assemble.assemble(self.run, self.out)
        self.assertEqual(json.loads((self.pack / "manifest.json").read_text(encoding="utf-8"))["range"], "0101-0102")
        self.assertEqual((self.pack / "variants.md").read_text(encoding="utf-8"), "| id |\n")
        log = (self.pack / "log.md").read_text(encoding="utf-8")
        self.assertTrue(log.startswith("# 팩 실행 기록\n\n"))
        self.assertRegex(log, r"- \d{4}-\d{2}-\d{2} full: 추가 p1, p2\n")

    def test_augment_appends_variants_and_log(self):
        self.pack.mkdir(parents=True)
        (self.pack / "variants.md").write_text("old\n", encoding="utf-8")
        (self.pack / "log.md").write_text("# 팩 실행 기록\n\n- 2026-10-01 full: 추가 p1, p2\n", encoding="utf-8")
        (self.run / "variants.md").write_text("new\n", encoding="utf-8")
        assemble.save_pack_records(self.run, self.out, "augment", ["p3", "p4"], today="2026-10-09", note="HTML에서 복원")
        v = (self.pack / "variants.md").read_text(encoding="utf-8")
        self.assertEqual(v, "old\n\n## 2026-10-09 보강\n\nnew\n")
        log = (self.pack / "log.md").read_text(encoding="utf-8")
        self.assertTrue(log.endswith("- 2026-10-09 augment: 추가 p3, p4 — HTML에서 복원\n"))
        self.assertEqual(log.count("\n- "), 2)

    def test_missing_records_keep_previous(self):
        self.pack.mkdir(parents=True)
        (self.pack / "key-check.md").write_text("keep\n", encoding="utf-8")
        assemble.save_pack_records(self.run, self.out, "augment", [], today="2026-10-09")
        self.assertEqual((self.pack / "key-check.md").read_text(encoding="utf-8"), "keep\n")
        self.assertIn("augment: 추가 없음", (self.pack / "log.md").read_text(encoding="utf-8"))

    def test_long_id_list_is_summarised(self):
        ids = [f"p{i}" for i in range(1, 57)]
        assemble.save_pack_records(self.run, self.out, "full", ids, today="2026-10-09")
        self.assertIn("full: 추가 p1–p56 (56개)", (self.pack / "log.md").read_text(encoding="utf-8"))
```

`tests/test_skill_files.py`의 `class TestBackupSnippet` 안(`test_bad_range_fails_loudly` 앞)에 추가:

```python
    def test_backs_up_pack_records(self):
        pack = self.notes / "0922"
        (pack / ".pack").mkdir(parents=True)
        (pack / ".pack" / "manifest.json").write_text("{}", encoding="utf-8")
        (pack / "복습문제_0922_A.html").write_text("r", encoding="utf-8")
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 2항목(파일 2개)", r.stdout)
        (d,) = self.backups()
        self.assertTrue((d / ".pack" / "manifest.json").is_file())
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_assemble.TestPackRecords test_skill_files.TestBackupSnippet -v`
Expected: FAIL — `AttributeError: module 'assemble' has no attribute 'save_pack_records'`, `.pack` 백업 테스트는 `백업 1항목`으로 실패.

- [ ] **Step 3: 구현** — `assemble.py`

상단 import에 `from datetime import date`를 더한다. `copy_figures` 다음에 추가:

```python
PACK_RECORDS = ("manifest.json", "question-audit.md", "key-check.md", "variants.md", "problem-pages.txt")
APPEND_ON_AUGMENT = ("question-audit.md", "key-check.md", "variants.md")


def _ids_text(ids: list[str]) -> str:
    if not ids:
        return "없음"
    if len(ids) <= 4:
        return ", ".join(ids)
    return f"{ids[0]}–{ids[-1]} ({len(ids)}개)"


def save_pack_records(run_dir: Path | str, out_dir: Path | str, mode: str, added_ids: list[str],
                      today: str | None = None, note: str = "") -> Path:
    """RUN의 설계 기록을 out/.pack/ 에 남긴다. 보강이면 감사·변형 기록은 이어 붙이고, 없는 파일은 이전 것을 둔다."""
    if mode not in ("full", "augment"):
        raise AssembleError(f"알 수 없는 mode: {mode}")
    run_dir, pack = Path(run_dir), Path(out_dir) / ".pack"
    pack.mkdir(parents=True, exist_ok=True)
    today = today or date.today().isoformat()
    for name in PACK_RECORDS:
        src, dst = run_dir / name, pack / name
        if not src.is_file():
            continue
        if mode == "augment" and name in APPEND_ON_AUGMENT and dst.is_file():
            old = dst.read_text(encoding="utf-8").rstrip("\n")
            dst.write_text(f"{old}\n\n## {today} 보강\n\n{src.read_text(encoding='utf-8')}", encoding="utf-8")
        else:
            shutil.copyfile(src, dst)
    log = pack / "log.md"
    head = "" if log.is_file() else "# 팩 실행 기록\n\n"
    line = f"- {today} {mode}: 추가 {_ids_text(added_ids)}" + (f" — {note}" if note else "") + "\n"
    with open(log, "a", encoding="utf-8") as f:
        f.write(head + line)
    return pack
```

`assemble()`의 `copy_figures(run_dir, out_dir, m["range"])` 다음 줄에 추가:

```python
    save_pack_records(run_dir, out_dir, "full", [q["id"] for q in m["problems"]])
```

`SKILL.md` 4단계 백업 스니펫의 `want()` 반환 줄을 바꾼다:

```python
    return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_", f"장마감_{r}_")) or n in (f"figures_{r}", ".pack")
```

같은 4단계의 "조립기는 `RUN/figures/`의 카드 그림을 … 복사한다." 문장 다음 줄에 추가:

```markdown
조립기는 `RUN`의 `manifest.json`·`question-audit.md`·`key-check.md`·`variants.md`·`problem-pages.txt`를 `복습노트/<range>/.pack/`에 복사하고 `.pack/log.md`에 실행 한 줄을 더한다. `.pack/`은 git으로 추적한다(금지어 목록과 감사표를 다음 보강에서 다시 쓴다). 내부 기록이라 STT 시각이 있어도 된다.
```

- [ ] **Step 4: 통과 확인 (전체)**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/scripts/assemble.py .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/tests/test_assemble.py .agents/skills/bio-review-pack/tests/test_skill_files.py
git -C "$WT" commit -m "feat(bio-review-pack): save pack design records to .pack on assemble

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `html2md --only review`

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/html2md.py` (`convert_pack` 624–654행, `main` 657–676행, 상단 상수)
- Test: `.agents/skills/bio-review-pack/tests/test_html2md.py`

**Interfaces:**
- Consumes: 없음
- Produces: `html2md.convert_pack(note_path, review_path, only: str | None = None) -> tuple[list[str], int]` — `only="review"`면 복습문제 MD 하나만 쓰고 그 경로 하나만 돌려준다. CLI `html2md.py NOTE REVIEW --only review [--check]`.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_html2md.py` 끝(`if __name__` 앞)에 추가. 파일 상단에 `import assemble`, `from _util import MINI_RUN`, `import shutil, tempfile`, `from pathlib import Path`가 없으면 더한다.

```python
class TestOnlyReview(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.note, self.review = assemble.assemble(MINI_RUN, self.tmp)
        html2md.convert_pack(self.note, self.review)
        self.note_md = self.note.with_suffix(".md")
        self.review_md = self.review.with_suffix(".md")
        self.figs = self.tmp / "figures_0101-0102"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.figs.iterdir()}

    def test_only_review_leaves_note_md_and_figures(self):
        before_review, before_figs = self.review_md.read_bytes(), self.snapshot()
        marked = self.note_md.read_bytes() + b"\n<!-- untouched -->\n"
        self.note_md.write_bytes(marked)
        outs, _ = html2md.convert_pack(self.note, self.review, only="review")
        self.assertEqual([Path(o).name for o in outs], [self.review_md.name])
        self.assertEqual(self.note_md.read_bytes(), marked)
        self.assertEqual(self.review_md.read_bytes(), before_review)
        self.assertEqual(self.snapshot(), before_figs)

    def test_only_rejects_other_values(self):
        with self.assertRaises(ValueError):
            html2md.convert_pack(self.note, self.review, only="note")

    def test_cli_only_review_check(self):
        rc = html2md.main([str(self.note), str(self.review), "--only", "review", "--check"])
        self.assertEqual(rc, 0)
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_html2md.TestOnlyReview -v`
Expected: FAIL — `TypeError: convert_pack() got an unexpected keyword argument 'only'`

- [ ] **Step 3: 구현** — `html2md.py`

`NAME_RE` 정의 아래에 추가:

```python
SVG_REF_RE = re.compile(r"\]\(figures_[^/)]+/([^)]+\.svg)\)")


def _md_svg_refs(md_path):
    """MD가 참조하는 figures_<range>/ SVG 파일명 집합."""
    if not os.path.isfile(md_path):
        return set()
    return set(SVG_REF_RE.findall(_read(md_path)))
```

`convert_pack`을 다음으로 바꾼다:

```python
def convert_pack(note_path, review_path, only=None):
    """두 HTML을 같은 폴더에 .md로 변환한다. (md 경로 목록, 그림 파일 수)를 돌려준다.
    only="review"면 복습문제 MD만 다시 쓰고, 정리노트 MD와 그 SVG는 건드리지 않는다."""
    if only not in (None, "review"):
        raise ValueError(f"only는 None 또는 'review': {only!r}")
    out_dir = os.path.dirname(os.path.abspath(note_path))
    srcs = [os.path.abspath(note_path), os.path.abspath(review_path)]
    names = [nfc(os.path.basename(p)) for p in srcs]
    matches = [NAME_RE.match(n) for n in names]
    if not all(matches) or matches[0].group(1) != "정리노트" or matches[1].group(1) != "복습문제":
        raise ValueError(f"파일명 규칙 위반: {names}")
    if os.path.dirname(os.path.abspath(review_path)) != out_dir:
        raise ValueError("두 HTML은 같은 폴더에 있어야 함")
    fig_name = f"figures_{matches[0].group(2)}"
    fig_abs = os.path.join(out_dir, fig_name)
    os.makedirs(fig_abs, exist_ok=True)
    mds = [os.path.join(out_dir, n[:-5] + ".md") for n in names]
    if only == "review":
        keep = _md_svg_refs(mds[0])
        drop = _md_svg_refs(mds[1]) - keep
        registry = set(keep)  # 전체 변환 때처럼 정리노트 그림 이름을 먼저 차지시켜 이름이 같게 나온다
    else:
        drop = {e for e in os.listdir(fig_abs) if e.lower().endswith(".svg")}
        registry = set()
    for entry in drop:  # 다시 변환할 때 이전 실행의 고아 SVG를 남기지 않는다(.svg만, 이 폴더만)
        old_svg = os.path.join(fig_abs, entry)
        if os.path.isfile(old_svg) and not os.path.islink(old_svg):
            os.remove(old_svg)
    link_map = [(n, n[:-5] + ".md") for n in names]  # fix_href가 NFC로 비교하므로 NFD 링크도 잡힌다
    intros = [
        [f"> `{names[0]}`를 마크다운으로 옮겼어요. 그림은 `{fig_name}/` 폴더의 SVG, "
         "위젯은 대표 설정의 정적 그림으로 바꿨어요. 수식은 `$…$` / `$$…$$`라서 GitHub, Obsidian, Typora에서 보여요."],
        [f"> `{names[1]}`를 마크다운으로 옮겼어요. "
         "원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요."],
    ]
    jobs = list(zip(srcs, mds, intros, ("note", "review")))
    if only == "review":
        jobs = jobs[1:]
    outs = []
    for src, out, intro, prefix in jobs:
        ctx = Ctx(link_map, fig_abs, fig_name, prefix=prefix, registry=registry)
        convert(src, out, ctx, intro)
        outs.append(out)
    return outs, len(registry)
```

`main`에 인자와 검사 짝을 바꾼다:

```python
    ap.add_argument("--only", choices=["review"])
    args = ap.parse_args(argv)
    outs, fig_count = convert_pack(args.note, args.review, only=args.only)
    for out in outs:
        print(out)
    print(f"figures: {fig_count}")
    if not args.check:
        return 0
    htmls = (args.review,) if args.only else (args.note, args.review)
    problems = []
    for html_path, md_path in zip(htmls, outs):
        problems += [f"{os.path.basename(md_path)}: {p}" for p in check_md(html_path, md_path)]
```

(나머지 출력·반환 줄은 그대로.)

- [ ] **Step 4: 통과 확인 (전체)**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK`

- [ ] **Step 5: 실제 팩으로 무변화 확인** (복습문제 MD가 바뀌지 않아야 한다)

```bash
P="$WT/복습노트/0929"; S="$WT/.agents/skills/bio-review-pack"
python3 "$S/scripts/html2md.py" "$(ls "$P"/정리노트_*.html)" "$(ls "$P"/복습문제_*.html)" --only review --check | tail -1
git -C "$WT" status --short 복습노트/0929
```
Expected: `OK`, 그리고 `git status`에 변경 없음. 변경이 있으면 `git -C "$WT" diff --stat 복습노트/0929`로 확인하고, 복습문제 MD만 바뀌었다면 이 변환기 차이를 보고서에 적은 뒤 `git -C "$WT" checkout -- 복습노트/0929`로 되돌린다.

- [ ] **Step 6: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/scripts/html2md.py .agents/skills/bio-review-pack/tests/test_html2md.py
git -C "$WT" commit -m "feat(bio-review-pack): convert only the review MD with --only review

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `augment.py extract` (기존 카드·manifest 꺼내기, HTML 복원)

**Files:**
- Create: `.agents/skills/bio-review-pack/scripts/augment.py`
- Test: `.agents/skills/bio-review-pack/tests/test_augment.py`

**Interfaces:**
- Consumes: `assemble.save_pack_records`(Task 2 — fixture 조립이 `.pack`을 만든다), `manifest.validate/load`, `manifest.LAYER_NAMES`, `check_html.SUPP_LABEL`
- Produces:
  - `augment.AugmentError(RuntimeError)`
  - `augment.CARD_RE` — `<article class="card" id="(p\d+)"…>…</article>`
  - `augment.find_pack_files(pack_dir: Path) -> tuple[Path, Path]` — (정리노트, 복습문제) 실제 경로(NFD 이름 그대로)
  - `augment.reconstruct(note_path: Path, review_path: Path) -> dict` — manifest dict
  - `augment.extract(pack_dir, run_dir) -> dict` — `{"next_id": "p57", "parts": {"partA": 9, …}, "reconstructed": bool}`. 부수 효과: `RUN/cards/pN.html`, `RUN/manifest.json`, `RUN/work/base-ids.json`(`{id: {"part", "source", "answer"}}`), 복원이면 `RUN/work/reconstructed.txt`

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_augment.py` 새 파일

```python
"""보강 모드(scripts/augment.py): 기존 카드·manifest 추출과 복습문제만 다시 조립."""

import json
from pathlib import Path
import shutil
import tempfile
import unicodedata
import unittest

from _util import MINI_RUN, REPO

import assemble
import augment


def fixture_pack(tmp: Path) -> Path:
    """mini-run을 조립한 팩 폴더(.pack 포함)."""
    pack = tmp / "pack"
    assemble.assemble(MINI_RUN, pack)
    return pack


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pack = fixture_pack(self.tmp)
        self.run = self.tmp / "run"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_extract_uses_pack_manifest(self):
        info = augment.extract(self.pack, self.run)
        self.assertFalse(info["reconstructed"])
        self.assertEqual(info["next_id"], "p3")
        self.assertEqual(info["parts"], {"partA": 1, "partB": 1})
        self.assertEqual(sorted(p.name for p in (self.run / "cards").iterdir()), ["p1.html", "p2.html"])
        card = (self.run / "cards" / "p2.html").read_text(encoding="utf-8")
        self.assertTrue(card.startswith('<article class="card" id="p2" data-source="기출 3강 7">'))
        self.assertTrue(card.endswith("</article>"))
        base = json.loads((self.run / "work" / "base-ids.json").read_text(encoding="utf-8"))
        self.assertEqual(base["p2"], {"part": "partB", "source": "기출 3강 7", "answer": "(2)"})
        self.assertEqual(json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))["forbidden_outside_preview"], ["d-separation"])

    def test_extract_reconstructs_without_pack(self):
        shutil.rmtree(self.pack / ".pack")
        info = augment.extract(self.pack, self.run)
        self.assertTrue(info["reconstructed"])
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["forbidden_outside_preview"], [])
        self.assertEqual(m["preview_topic"], "s2-next")
        self.assertEqual([s["id"] for s in m["sections"]], ["s1", "s2"])
        self.assertEqual(m["sections"][0]["short"], "1 기초")
        self.assertTrue(m["sections"][0]["topics"][1]["supp"])
        self.assertEqual([q["id"] for q in m["problems"]], ["p1", "p2"])
        self.assertEqual(m["problems"][1]["answer"], "(2)")
        self.assertIn("금지어 미복원", (self.run / "work" / "reconstructed.txt").read_text(encoding="utf-8"))

    def test_pack_manifest_mismatch_stops(self):
        m = json.loads((self.pack / ".pack" / "manifest.json").read_text(encoding="utf-8"))
        m["problems"] = [q for q in m["problems"] if q["id"] != "p2"]
        (self.pack / ".pack" / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.extract(self.pack, self.run)
        self.assertIn("p2", str(cm.exception))

    def test_nfd_file_names(self):
        for p in list(self.pack.iterdir()):
            if p.suffix == ".html":
                p.rename(self.pack / unicodedata.normalize("NFD", p.name))
        note, review = augment.find_pack_files(self.pack)
        self.assertEqual(unicodedata.normalize("NFC", review.name), "복습문제_0101-0102_Mini_Test.html")
        self.assertTrue(review.exists())
        self.assertEqual(augment.extract(self.pack, self.run)["next_id"], "p3")


class TestReconstructRealPacks(unittest.TestCase):
    """저장소의 실제 팩마다: HTML에서 복원한 manifest로 다시 조립하면 원본과 바이트까지 같다."""

    def test_round_trip_from_html(self):
        packs = sorted(p for p in (REPO / "복습노트").iterdir() if p.is_dir() and not p.name.startswith("."))
        checked = 0
        for pack in packs:
            try:
                note, review = augment.find_pack_files(pack)
            except augment.AugmentError:
                continue
            with self.subTest(pack=pack.name), tempfile.TemporaryDirectory() as tmp:
                m = augment.reconstruct(note, review)
                run = Path(tmp)
                (run / "cards").mkdir()
                html = review.read_text(encoding="utf-8")
                for c in augment.CARD_RE.finditer(html):
                    (run / "cards" / f"{c.group(1)}.html").write_text(c.group(0), encoding="utf-8")
                self.assertEqual(assemble.build_review(m, run), html)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_augment -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'augment'`

- [ ] **Step 3: 구현** — `scripts/augment.py`

```python
#!/usr/bin/env python3
"""
이미 만든 복습팩에 문항을 덧붙인다(보강 모드). 기존 카드 번호를 그대로 두고 복습문제만 다시 쓴다.

  augment.py extract <팩 폴더> <RUN>   기존 카드 → RUN/cards/, manifest → RUN/manifest.json
  augment.py build   <팩 폴더> <RUN>   보호 검사 → 정렬·문구 갱신 → 복습문제 HTML만 쓰기 → .pack 기록

manifest는 <팩 폴더>/.pack/manifest.json을 쓰고, 없으면 정리노트·복습문제 HTML에서 복원한다
(금지어 [], anchor=예고 토픽, level 2, required_terms []).
"""

from __future__ import annotations

import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assemble  # noqa: E402
import check_html  # noqa: E402
import manifest as manifest_mod  # noqa: E402

CARD_RE = re.compile(r'<article class="card" id="(p\d+)"[^>]*>.*?</article>', re.S)
PACK_NAME_RE = re.compile(r"^(정리노트|복습문제)_(\d{4}(?:-\d{4})?)_([A-Za-z0-9_]+)\.html$")
SECTION_RE = re.compile(r'<section id="(s\d+)"><h2>(.*?)</h2>(.*?)\n    </section>', re.S)
PART_RE = re.compile(r'<section id="(part[A-Z])"><h2>(.*?)</h2>(.*?)\n    </section>', re.S)
TOPIC_HEAD_RE = re.compile(r'<article class="topic" id="([\w-]+)"><h3>(.*?)</h3>', re.S)
DEFAULT_PARTS = {"partA": ("A. 웹과제", "A 웹과제"), "partB": ("B. 기출", "B 기출"), "partC": ("C. 변형 연습", "C 변형")}
RECONSTRUCTED_NOTE = "HTML에서 복원: 금지어 미복원, anchor·level·required_terms 임시값"


class AugmentError(RuntimeError):
    pass


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def find_pack_files(pack_dir: Path | str) -> tuple[Path, Path]:
    """(정리노트, 복습문제) HTML의 실제 경로. NFD 파일명도 NFC로 비교해 찾는다."""
    pack_dir = Path(pack_dir)
    found: dict[str, Path] = {}
    for p in pack_dir.iterdir() if pack_dir.is_dir() else []:
        m = PACK_NAME_RE.match(nfc(p.name))
        if m and p.is_file():
            found[m.group(1)] = p
    if "정리노트" not in found or "복습문제" not in found:
        raise AugmentError(f"{pack_dir}: 정리노트·복습문제 HTML이 둘 다 있어야 함")
    return found["정리노트"], found["복습문제"]


def _need(pattern: str | re.Pattern, text: str, what: str) -> re.Match:
    m = re.search(pattern, text, re.S)
    if not m:
        raise AugmentError(f"복원 실패: {what}")
    return m


def _toc(text: str) -> dict[str, str]:
    nav = _need(r'<nav class="toc" aria-label="목차">(.*?)</nav>', text, "목차").group(1)
    return {k: html.unescape(v) for k, v in re.findall(r'<a href="#([\w-]+)">(.*?)</a>', nav)}


def _answer(card: str) -> str:
    m = re.search(r'<p class="answer">정답:\s*(.*?)</p>', card, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def reconstruct(note_path: Path, review_path: Path) -> dict:
    """정리노트·복습문제 HTML에서 manifest를 복원한다. 복습문제 조립에 쓰는 값은 원문 그대로다."""
    note, review = note_path.read_text(encoding="utf-8"), review_path.read_text(encoding="utf-8")
    name = PACK_NAME_RE.match(nfc(review_path.name))
    range_, slug = name.group(2), name.group(3)
    hero_r = _need(r"<h1>(.*?)</h1>\s*<p>(.*?)</p>", review, "복습문제 제목·안내")
    hero_n = _need(r"<h1>(.*?)</h1>\s*<p>(.*?)</p>", note, "정리노트 제목·부제")
    toc_n, toc_r = _toc(note), _toc(review)
    sections, topic_ids, links = [], [], []
    for sm in SECTION_RE.finditer(note):
        topics = []
        for chunk in re.split(r'(?=<article class="topic" id=")', sm.group(3)):
            tm = TOPIC_HEAD_RE.match(chunk)
            if not tm:
                continue
            layers: list[str] = []
            for layer in re.findall(r'<div class="layer (\w+)', chunk):
                if layer in manifest_mod.LAYER_NAMES and layer not in layers:
                    layers.append(layer)
            tid = tm.group(1)
            topics.append({"id": tid, "title": html.unescape(tm.group(2)), "required_terms": [],
                           "layers": layers, "supp": check_html.SUPP_LABEL in chunk})
            topic_ids.append(tid)
            if tid.endswith("-links"):
                links += [{"topic": tid, "href": h} for h in re.findall(r'href="([^"#][^"]*)"', chunk)]
        sid = sm.group(1)
        sections.append({"id": sid, "title": html.unescape(sm.group(2)),
                         "short": toc_n.get(sid, html.unescape(sm.group(2))), "topics": topics})
    if not topic_ids:
        raise AugmentError("복원 실패: 정리노트 토픽 없음")
    preview = next((t for t in topic_ids if t.endswith("-next")), topic_ids[-1])
    parts, problems = [], []
    for pm in PART_RE.finditer(review):
        pid = pm.group(1)
        parts.append({"id": pid, "title": html.unescape(pm.group(2)),
                      "short": toc_r.get(pid, DEFAULT_PARTS.get(pid, (pid, pid))[1])})
        for c in CARD_RE.finditer(pm.group(3)):
            source = html.unescape(_need(r'data-source="([^"]*)"', c.group(0), f"{c.group(1)} data-source").group(1))
            answer = _answer(c.group(0))
            problems.append({"id": c.group(1), "part": pid, "source": source,
                             "variant": pid == "partC" or source.startswith("생성 변형"),
                             "anchor": preview, "level": 2, "date": range_[:4],
                             "terms": [f"정답: {answer}"] if answer else [], "answer": answer})
    return {
        "course": html.unescape(_need(r"<title>(.*?) 복습문제 ", review, "페이지 제목").group(1)),
        "range": range_, "slug": slug,
        "note_title": html.unescape(hero_n.group(1)), "note_subtitle": html.unescape(hero_n.group(2)),
        "review_title": html.unescape(hero_r.group(1)), "review_intro": hero_r.group(2),
        "footer_note": _need(r"<footer>(.*?)</footer>", note, "정리노트 꼬리말").group(1),
        "footer_review": _need(r"<footer>(.*?)</footer>", review, "복습문제 꼬리말").group(1),
        "sessions": [], "preview_topic": preview, "forbidden_outside_preview": [],
        "sections": sections, "parts": parts, "problems": problems, "links": links,
    }


def extract(pack_dir: Path | str, run_dir: Path | str) -> dict:
    pack_dir, run_dir = Path(pack_dir), Path(run_dir)
    note_path, review_path = find_pack_files(pack_dir)
    review = review_path.read_text(encoding="utf-8")
    cards = {m.group(1): m.group(0) for m in CARD_RE.finditer(review)}
    if not cards:
        raise AugmentError(f"{review_path.name}: 카드 없음")
    saved = pack_dir / ".pack" / "manifest.json"
    if saved.is_file():
        m = manifest_mod.load(saved)
        ids = {q["id"] for q in m["problems"]}
        if ids != set(cards):
            raise AugmentError(".pack manifest와 복습문제 HTML의 카드가 다름: "
                               f"manifest에만 {sorted(ids - set(cards))}, HTML에만 {sorted(set(cards) - ids)}")
        reconstructed = False
    else:
        m = reconstruct(note_path, review_path)
        errors = manifest_mod.validate(m)
        if errors:
            raise AugmentError("복원한 manifest 검증 실패:\n" + "\n".join(errors))
        reconstructed = True
    (run_dir / "cards").mkdir(parents=True, exist_ok=True)
    (run_dir / "work").mkdir(parents=True, exist_ok=True)
    for pid, text in cards.items():
        (run_dir / "cards" / f"{pid}.html").write_text(text, encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base = {q["id"]: {"part": q["part"], "source": q["source"], "answer": q["answer"]} for q in m["problems"]}
    (run_dir / "work" / "base-ids.json").write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note_file = run_dir / "work" / "reconstructed.txt"
    if reconstructed:
        note_file.write_text(RECONSTRUCTED_NOTE + "\n", encoding="utf-8")
    elif note_file.exists():
        note_file.unlink()
    return {"next_id": f"p{max(int(i[1:]) for i in base) + 1}",
            "parts": dict(Counter(q["part"] for q in m["problems"])), "reconstructed": reconstructed}
```

(`build`와 CLI는 Task 5에서 더한다.)

- [ ] **Step 4: 통과 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_augment -v`
Expected: 5개 PASS (`test_round_trip_from_html`은 0901~1001 팩 모두 subTest 통과)

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/scripts/augment.py .agents/skills/bio-review-pack/tests/test_augment.py
git -C "$WT" commit -m "feat(bio-review-pack): extract cards and manifest for augment mode

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: `augment.py build` + CLI (보호 검사·정렬·문구 갱신·복습문제만 조립)

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/augment.py`
- Test: `.agents/skills/bio-review-pack/tests/test_augment.py`

**Interfaces:**
- Consumes: Task 4의 `extract`, `find_pack_files`, `AugmentError`, `DEFAULT_PARTS`, `RECONSTRUCTED_NOTE`; Task 2의 `assemble.save_pack_records`; `assemble.build_review`, `assemble.check_figures`, `assemble.copy_figures`, `manifest_mod.validate`, `manifest_mod.review_name`
- Produces:
  - `augment.ensure_parts(m: dict) -> None` — 문제에 쓰인 part가 `parts`에 없으면 `DEFAULT_PARTS`로 넣고 A,B,C 순으로 정렬
  - `augment.refresh_texts(m: dict, base_parts: set[str]) -> list[str]` — 제목·안내·꼬리말 갱신, 경고 목록 반환
  - `augment.build(pack_dir, run_dir, today: str | None = None) -> dict` — `{"review": Path, "added": list[str], "warnings": list[str]}`
  - CLI `augment.py extract|build <팩 폴더> <RUN>` — 실패 시 종료 코드 1

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_augment.py`에 클래스 추가(`TestReconstructRealPacks` 앞)

```python
def new_card(run: Path, pid: str, source: str) -> None:
    """fixture p2 카드를 복제해 새 카드를 만든다."""
    text = (run / "cards" / "p2.html").read_text(encoding="utf-8")
    text = text.replace('id="p2"', f'id="{pid}"').replace('data-source="기출 3강 7"', f'data-source="{source}"')
    text = text.replace("<h3>P2.", f"<h3>{pid.upper()}.")
    assert f'id="{pid}"' in text and source in text
    (run / "cards" / f"{pid}.html").write_text(text, encoding="utf-8")


def add_problem(run: Path, pid: str, part: str, source: str) -> None:
    m = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    m["problems"].append({"id": pid, "part": part, "source": source, "variant": part == "partC",
                          "anchor": "s1-mean", "level": 2, "date": "0101", "terms": ["정답: (2)"], "answer": "(2)"})
    (run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    new_card(run, pid, source)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pack = fixture_pack(self.tmp)
        self.run = self.tmp / "run"
        self.note, self.review = augment.find_pack_files(self.pack)
        self.original = self.review.read_text(encoding="utf-8")
        self.note_before = self.note.read_bytes()
        augment.extract(self.pack, self.run)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_round_trip_without_additions(self):
        result = augment.build(self.pack, self.run, today="2026-10-09")
        self.assertEqual(result["added"], [])
        self.assertEqual(self.review.read_text(encoding="utf-8"), self.original)
        self.assertEqual(self.note.read_bytes(), self.note_before)
        self.assertIn("- 2026-10-09 augment: 추가 없음", (self.pack / ".pack" / "log.md").read_text(encoding="utf-8"))

    def test_appends_new_problems_by_part(self):
        add_problem(self.run, "p3", "partC", "생성 변형 s1-mean")
        add_problem(self.run, "p4", "partA", "웹과제 2장 q01")
        result = augment.build(self.pack, self.run, today="2026-10-09")
        self.assertEqual(result["added"], ["p3", "p4"])
        html = self.review.read_text(encoding="utf-8")
        order = [m.group(1) for m in augment.CARD_RE.finditer(html)]
        self.assertEqual(order, ["p1", "p4", "p2", "p3"])
        self.assertIn('<section id="partC"><h2>C. 변형 연습</h2>', html)
        self.assertIn("<h1>복습문제 4선 — 테스트</h1>", html)
        self.assertIn("<p>테스트용 문제 <b>1개</b>입니다.</p>", html)  # 문항 수 표현이 없어 그대로
        self.assertTrue(any("review_intro" in w for w in result["warnings"]))
        self.assertIn("변형 연습은 수업 내용으로 만든 생성 문제입니다.", html)
        self.assertEqual(self.note.read_bytes(), self.note_before)
        saved = json.loads((self.pack / ".pack" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([q["id"] for q in saved["problems"]], ["p1", "p4", "p2", "p3"])

    def test_guard_rejects_changed_old_card(self):
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        m["problems"][1]["answer"] = "(3)"
        (self.run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.build(self.pack, self.run)
        self.assertIn("p2.answer", str(cm.exception))
        self.assertEqual(self.review.read_text(encoding="utf-8"), self.original)

    def test_guard_rejects_missing_card_and_low_new_id(self):
        (self.run / "cards" / "p1.html").unlink()
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        m["problems"].append(dict(m["problems"][1], id="p0"))
        (self.run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.build(self.pack, self.run)
        self.assertIn("p1: 카드 파일 없음", str(cm.exception))
        self.assertIn("p0: 새 문항 id는 p3부터", str(cm.exception))

    def test_second_augment_continues_numbering(self):
        add_problem(self.run, "p3", "partC", "생성 변형 s1-mean")
        augment.build(self.pack, self.run, today="2026-10-09")
        run2 = self.tmp / "run2"
        self.assertEqual(augment.extract(self.pack, run2)["next_id"], "p4")
        add_problem(run2, "p4", "partC", "생성 변형 s1-var")
        self.assertEqual(augment.build(self.pack, run2, today="2026-10-10")["added"], ["p4"])
        log = (self.pack / ".pack" / "log.md").read_text(encoding="utf-8")
        self.assertIn("2026-10-09 augment: 추가 p3", log)
        self.assertIn("2026-10-10 augment: 추가 p4", log)

    def test_cli_reports_failure(self):
        (self.run / "work" / "base-ids.json").unlink()
        self.assertEqual(augment.main(["build", str(self.pack), str(self.run)]), 1)


class TestRefreshTexts(unittest.TestCase):
    def manifest(self, intro, footer, parts):
        problems = []
        for part, n in parts.items():
            for i in range(n):
                src = "웹과제 4장 q01" if part == "partA" else ("생성 변형 s1-a" if part == "partC" else "기출 4강 1")
                problems.append({"id": f"{part}{i}", "part": part, "source": src})
        return {"review_title": f"복습문제 1선 — 1001 수업 범위", "review_intro": intro,
                "footer_review": footer, "problems": problems}

    def test_counts_only_digits_change(self):
        m = self.manifest("웹과제 6문항, 기출 23문항, 생성 변형 15문항이에요. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.",
                          "출처: 기출(3강 합본) · 웹과제(3장). 변형 연습은 수업 내용으로 만든 생성 문제입니다.",
                          {"partA": 7, "partB": 23, "partC": 16})
        self.assertEqual(augment.refresh_texts(m, {"partA", "partB", "partC"}), [])
        self.assertEqual(m["review_title"], "복습문제 46선 — 1001 수업 범위")
        self.assertEqual(m["review_intro"], "웹과제 7문항, 기출 23문항, 생성 변형 16문항이에요. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.")
        self.assertEqual(m["footer_review"], "출처: 기출(3강 합본) · 웹과제(4장). 변형 연습은 수업 내용으로 만든 생성 문제입니다.")

    def test_refresh_inserts_new_part_phrases(self):
        m = self.manifest("기출 <b>20개</b>와 변형 연습 <b>6개</b>입니다. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.",
                          "출처: 2023·2024 생명과학 기출(4·5강 합본). 정답은 대조했습니다. 변형 연습은 수업 내용으로 만든 생성 문제입니다.",
                          {"partA": 3, "partB": 20, "partC": 8})
        self.assertEqual(augment.refresh_texts(m, {"partB", "partC"}), [])
        self.assertEqual(m["review_intro"], "웹과제 <b>3개</b>, 기출 <b>20개</b>와 변형 연습 <b>8개</b>입니다. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.")
        self.assertEqual(m["footer_review"], "출처: 2023·2024 생명과학 기출(4·5강 합본) · 웹과제(4장). 정답은 대조했습니다. 변형 연습은 수업 내용으로 만든 생성 문제입니다.")

    def test_intro_without_counts_is_left_alone(self):
        intro = "먼저 풀어 보고, 막히면 힌트를 열어 보세요. 원문이 모호한 문항은 풀이에서 구분해요."
        m = self.manifest(intro, "출처: 기출(4강 합본).", {"partB": 2, "partC": 1})
        warnings = augment.refresh_texts(m, {"partB"})
        self.assertEqual(m["review_intro"], intro)
        self.assertTrue(any("review_intro" in w for w in warnings))

    def test_ensure_parts_orders_defaults(self):
        m = {"parts": [{"id": "partB", "title": "B. 기출", "short": "B 기출"}],
             "problems": [{"part": "partC"}, {"part": "partA"}, {"part": "partB"}]}
        augment.ensure_parts(m)
        self.assertEqual([p["id"] for p in m["parts"]], ["partA", "partB", "partC"])
        self.assertEqual(m["parts"][0], {"id": "partA", "title": "A. 웹과제", "short": "A 웹과제"})
```

`TestReconstructRealPacks` 아래에 실제 팩 왕복을 하나 더 추가:

```python
class TestAugmentRealPacks(unittest.TestCase):
    """.pack이 있는 실제 팩: 복사본에서 extract → build(추가 없음)가 원본 복습문제와 같다."""

    def test_round_trip_with_pack_records(self):
        checked = 0
        for pack in sorted((REPO / "복습노트").iterdir()):
            if not (pack / ".pack" / "manifest.json").is_file():
                continue
            with self.subTest(pack=pack.name), tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / pack.name
                shutil.copytree(pack, copy, ignore=shutil.ignore_patterns("풀이기록"))
                _, review = augment.find_pack_files(copy)
                original = review.read_text(encoding="utf-8")
                augment.extract(copy, Path(tmp) / "run")
                augment.build(copy, Path(tmp) / "run", today="2026-10-09")
                self.assertEqual(review.read_text(encoding="utf-8"), original)
                checked += 1
        self.assertGreater(checked, 0)
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_augment -v`
Expected: 새 테스트 FAIL — `AttributeError: module 'augment' has no attribute 'build'` 등

- [ ] **Step 3: 구현** — `augment.py`의 `extract` 아래에 추가

```python
COUNT_LABELS = {"partA": r"웹과제", "partB": r"기출", "partC": r"(?:생성 )?변형(?: 연습)?"}
NEW_LABELS = {"partA": "웹과제", "partB": "기출", "partC": "생성 변형"}
STYLE_RE = re.compile(r"(?:웹과제|기출|(?:생성 )?변형(?: 연습)?) (<b>)?\d+(개|문항)")
PARTC_NOTE = "변형 연습은 수업 내용으로 만든 생성 문제"


def ensure_parts(m: dict) -> None:
    have = {p["id"] for p in m["parts"]}
    for pid in sorted({q["part"] for q in m["problems"]} - have):
        if pid not in DEFAULT_PARTS:
            raise AugmentError(f"알 수 없는 part: {pid}")
        title, short = DEFAULT_PARTS[pid]
        m["parts"].append({"id": pid, "title": title, "short": short})
    m["parts"].sort(key=lambda p: p["id"])


def _phrase(intro: str, part: str, count: int) -> str:
    style = STYLE_RE.search(intro)
    bold, unit = (bool(style.group(1)), style.group(2)) if style else (False, "문항")
    num = f"<b>{count}{unit}</b>" if bold else f"{count}{unit}"
    return f"{NEW_LABELS[part]} {num}"


def refresh_texts(m: dict, base_parts: set[str]) -> list[str]:
    """제목의 N선, 안내의 문항 수, 꼬리말의 웹과제(N장)을 맞춘다. 숫자만 바꾸고 문장은 자르지 않는다."""
    warnings: list[str] = []
    counts = Counter(q["part"] for q in m["problems"])
    title, n = re.subn(r"\d+선", f"{len(m['problems'])}선", m["review_title"], count=1)
    m["review_title"] = title
    if not n:
        warnings.append("review_title에 'N선'이 없어 그대로 둠")
    intro = m["review_intro"]
    for part, label in COUNT_LABELS.items():
        pat = re.compile(rf"({label} (?:<b>)?)(\d+)(?=(?:개|문항))")
        if pat.search(intro):
            intro = pat.sub(lambda mo: f"{mo.group(1)}{counts.get(part, 0)}", intro, count=1)
        elif counts.get(part) and part not in base_parts:
            if part == "partA" and STYLE_RE.search(intro):
                intro = f"{_phrase(intro, part, counts[part])}, {intro}"
            elif part == "partC" and (exam := re.search(r"기출 (?:<b>)?\d+(?:개|문항)(?:</b>)?", intro)):
                intro = intro[:exam.end()] + f", {_phrase(intro, part, counts[part])}" + intro[exam.end():]
            else:
                warnings.append(f"review_intro에 {NEW_LABELS[part]} 문항 수를 넣지 못함(직접 고칠 것)")
    m["review_intro"] = intro
    footer = m["footer_review"]
    chapters = sorted({int(mo.group(1)) for q in m["problems"] if q["part"] == "partA"
                       for mo in [re.match(r"웹과제 (\d+)장", q["source"])] if mo})
    if chapters:
        label = "웹과제(" + "·".join(f"{c}장" for c in chapters) + ")"
        if re.search(r"웹과제\([^)]*\)", footer):
            footer = re.sub(r"웹과제\([^)]*\)", label, footer, count=1)
        elif (exam := re.search(r"기출\([^)]*\)", footer)):
            footer = footer[:exam.end()] + f" · {label}" + footer[exam.end():]
        else:
            warnings.append(f"footer_review에 {label}을 넣지 못함(직접 고칠 것)")
    if counts.get("partC") and PARTC_NOTE not in footer:
        footer = footer.rstrip() + f" {PARTC_NOTE}입니다."
    m["footer_review"] = footer
    return warnings


def build(pack_dir: Path | str, run_dir: Path | str, today: str | None = None) -> dict:
    pack_dir, run_dir = Path(pack_dir), Path(run_dir)
    note_path, review_path = find_pack_files(pack_dir)
    base_file = run_dir / "work" / "base-ids.json"
    if not base_file.is_file():
        raise AugmentError("RUN/work/base-ids.json 없음 — extract를 먼저 실행")
    base = json.loads(base_file.read_text(encoding="utf-8"))
    try:
        m = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise AugmentError(f"RUN/manifest.json 읽기 실패: {e}") from e
    probs = {q.get("id"): q for q in m.get("problems", [])}
    top = max(int(i[1:]) for i in base)
    errors = []
    for pid, old in base.items():
        q = probs.get(pid)
        if q is None:
            errors.append(f"{pid}: manifest에서 사라짐")
            continue
        errors += [f"{pid}.{k}: {old[k]!r} → {q.get(k)!r}" for k in ("part", "source", "answer") if q.get(k) != old[k]]
    added = [q["id"] for q in m["problems"] if q["id"] not in base]
    for pid in added:
        if not re.fullmatch(r"p\d+", pid) or int(pid[1:]) <= top:
            errors.append(f"{pid}: 새 문항 id는 p{top + 1}부터")
    for pid in probs:
        card = run_dir / "cards" / f"{pid}.html"
        if not card.is_file():
            errors.append(f"{pid}: 카드 파일 없음")
        elif f'id="{pid}"' not in card.read_text(encoding="utf-8"):
            errors.append(f"{pid}: 카드 안 id가 파일 이름과 다름")
    if errors:
        raise AugmentError("기존 카드 보호 검사 실패:\n" + "\n".join(errors))
    ensure_parts(m)
    order = {p["id"]: i for i, p in enumerate(m["parts"])}
    m["problems"].sort(key=lambda q: order[q["part"]])  # 안정 정렬: part 안의 기존 순서 + 새 문항은 끝
    warnings = refresh_texts(m, {v["part"] for v in base.values()})
    problems = manifest_mod.validate(m)
    if problems:
        raise AugmentError("manifest 검증 실패:\n" + "\n".join(problems))
    if manifest_mod.review_name(m) != nfc(review_path.name):
        raise AugmentError(f"manifest 이름 {manifest_mod.review_name(m)} ≠ 팩 파일 {nfc(review_path.name)}")
    review_html = assemble.build_review(m, run_dir)
    assemble.check_figures(run_dir)
    (run_dir / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path.write_text(review_html, encoding="utf-8")
    assemble.copy_figures(run_dir, pack_dir, m["range"])
    note_file = run_dir / "work" / "reconstructed.txt"
    note = note_file.read_text(encoding="utf-8").strip() if note_file.is_file() else ""
    assemble.save_pack_records(run_dir, pack_dir, "augment", added, today=today, note=note)
    return {"review": review_path, "added": added, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["extract", "build"])
    ap.add_argument("pack")
    ap.add_argument("run")
    args = ap.parse_args(argv)
    try:
        if args.command == "extract":
            info = extract(args.pack, args.run)
            print(f"다음 id: {info['next_id']}")
            print("part별 카드:", ", ".join(f"{k} {v}" for k, v in sorted(info["parts"].items())))
            print("manifest:", "HTML에서 복원(금지어 미복원)" if info["reconstructed"] else ".pack/manifest.json")
        else:
            result = build(args.pack, args.run)
            print(result["review"])
            print("추가:", ", ".join(result["added"]) or "없음")
            for w in result["warnings"]:
                print("경고:", w)
    except (AugmentError, manifest_mod.ManifestError, assemble.AssembleError, OSError, ValueError) as e:
        print(f"augment 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인 (전체)**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK` (`TestAugmentRealPacks`는 Task 1의 0910~0929 다섯 팩을 subTest로 확인)

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/scripts/augment.py .agents/skills/bio-review-pack/tests/test_augment.py
git -C "$WT" commit -m "feat(bio-review-pack): build augmented review with card-id guard

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: SKILL.md 보강 모드 절차 + 블라인드 사본 `IDS`

**Files:**
- Modify: `.agents/skills/bio-review-pack/SKILL.md` (13–14행 인자, `## 오류 처리` 앞에 새 절, 오류 표 행 추가)
- Modify: `.agents/skills/bio-review-pack/references/review-prompt.md` (블라인드 사본 스니펫)
- Test: `.agents/skills/bio-review-pack/tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 3 CLI `html2md.py … --only review --check`, Task 4·5 CLI `augment.py extract|build`
- Produces: 문서 절차. 블라인드 스니펫이 환경변수 `IDS`(쉼표 목록, 비우면 전체)를 받는다.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_skill_files.py`

`class TestSkillFiles`에 추가:

```python
    def test_augment_mode_documented(self):
        self.assertIn("`[MMDD | MMDD-MMDD] [lite] [augment]`", self.text)
        body = self.text[self.text.index("## 보강 모드"):self.text.index("## 오류 처리")]
        for s in ("scripts/augment.py", "extract", "build", "--only review", "IDS=", ".pack/manifest.json",
                  "풀이기록", "금지어 미복원", "기존 카드 번호"):
            with self.subTest(s=s):
                self.assertIn(s, body)
        for step in ("A1", "A2", "A3", "A4", "A5", "A6"):
            with self.subTest(step=step):
                self.assertIn(f"**{step}.", body)
```

`class TestBlindCopySnippet`에 추가(기존 `setUp`이 `self.review`에 `REVIEW_HTML`을 쓰고, 기존 테스트가 스니펫을 실행하는 방식을 그대로 따른다 — 실행 도우미 이름은 그 클래스의 기존 테스트에서 확인해 같은 것을 쓴다):

```python
    def test_ids_filter_keeps_only_listed_cards(self):
        out = self.tmp / "work" / "blind.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, REVIEW=str(self.review), OUT=str(out), IDS="p2")
        r = subprocess.run([sys.executable, "-c", self.code], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        text = out.read_text(encoding="utf-8")
        self.assertIn("## p2.", text)
        self.assertNotIn("## p1.", text)
        self.assertIn("1 문항", r.stdout)
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_skill_files -v`
Expected: 두 새 테스트 FAIL

- [ ] **Step 3: 구현**

`SKILL.md` 13행을 `**인자**: \`[MMDD | MMDD-MMDD] [lite] [augment]\``로 바꾸고 14행 아래에 추가:

```markdown
- `augment`: 이미 만든 팩에 웹과제 원문(partA)과 새 변형(partC)을 덧붙인다. 0~9단계 대신 아래 **보강 모드**를 따른다. range가 꼭 있어야 한다.
```

`## 오류 처리` 바로 앞에 새 절을 넣는다:

````markdown
## 보강 모드

웹과제 bank는 그 장 응시 뒤에 생긴다. 이미 만든 팩을 다시 만들면 카드 번호가 바뀌어 `references/interactive-overrides.json`(카드 id 키)과 `복습노트/<range>/풀이기록/`이 엉뚱한 문항에 붙는다. 그래서 보강은 **기존 카드 번호를 그대로 두고** 복습문제만 다시 쓴다. 정리노트 HTML·MD와 `풀이기록/`은 건드리지 않는다. `RUN` 경로 약속은 위와 같다(`<scratchpad>/review-pack/<range>-augment/`).

**A1. 추출**
```bash
SKILL=…; REPO=…; RUN=…; python3 "$SKILL/scripts/augment.py" extract "$REPO/복습노트/<range>" "$RUN"
```
- 기존 카드를 `RUN/cards/pN.html`로, manifest를 `RUN/manifest.json`으로 꺼내고 다음 id를 출력한다.
- manifest는 `복습노트/<range>/.pack/manifest.json`을 쓴다. 없으면 HTML에서 복원한다(출력에 "금지어 미복원"). 복원했거나 `.pack/log.md`에 "금지어 미복원"이 있으면 A2에서 금지어를 다시 정한다.
- `.pack` manifest와 HTML 카드가 다르다고 멈추면, 누가 HTML을 손으로 고친 것이다. 차이를 보고하고 멈춘다.

**A2. 새 문항 정하기** (기존 절차 재사용)
- 장 bank를 `references/problem-selection.md` 2절로 검증하고 3절 감사표를 `RUN/question-audit.md`에 쓴다. "이전 팩" 판정에 **이 팩 자신의 기존 `data-source`도** 넣는다.
- 변형은 6절과 `references/webquiz-style.md`대로 `RUN/variants.md`에 설계한다. 쌍둥이 재료 판단의 "같은 팩 partA"는 기존 카드와 새 partA를 합친 집합이다.
- 금지어 미복원이면: 정리노트 예고 토픽(`preview_topic`) 본문의 용어 중 다른 토픽에 나오지 않는 것을 후보로 다시 정해 `RUN/manifest.json`에 넣고 보고서에 "금지어 재도출"이라고 적는다.
- 새 문항을 `RUN/manifest.json` `problems` 끝에 A1이 출력한 다음 id부터 붙이고, 카드 작성자(`references/card-rules.md` 브리프)가 `RUN/cards/<새 id>.html`을 쓴다. 기출 그림은 `RUN/figures/`.

**A3. 조립**
```bash
SKILL=…; REPO=…; RUN=…; python3 "$SKILL/scripts/augment.py" build "$REPO/복습노트/<range>" "$RUN"
```
- 기존 카드의 id·part·source·answer가 바뀌었거나 카드가 사라졌으면 아무것도 쓰지 않고 멈춘다. 카드 본문 수정은 허용한다.
- part 순서(A·B·C)로 정렬하고, 제목의 "N선"·안내의 문항 수·꼬리말의 `웹과제(N장)`을 맞춘다. `경고:` 줄이 나오면 그 문구를 `RUN/manifest.json`에서 직접 고치고 A3을 다시 한다.
- 복습문제 HTML만 쓰고 `.pack/`에 기록을 남긴다(`log.md`에 augment 한 줄).

**A4. 검사**
- `python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note … --review …` → `OK`. 복원 manifest라면 정리노트 쪽은 구조만 검사된다는 한계를 보고서에 적는다.
- 블라인드 검사: `references/review-prompt.md` 스니펫을 `IDS=<새 id 쉼표 목록>`과 함께 돌려 **새 카드만** 사본을 만들고 6단계 규칙대로 검사한다.
- 브라우저: `references/browser-check.md`대로, 새 카드 하나 이상과 기존 카드 하나를 연다.

**A5. MD 변환**
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --only review --check
```
- 복습문제 MD만 다시 쓴다. 정리노트 MD와 그 그림은 그대로다.

**A6. 보고**
- 9단계 형식에 `보강:`을 앞에 붙이고 `추가 pX–pY`를 더한다. `git status 복습노트/<range>/풀이기록`이 비어 있는지 확인해 적는다. 기존 카드 번호를 바꾸지 않았음을 확인하는 줄을 넣는다.
- 커밋 제안: `git add 복습노트/<range> && git commit -m "docs(notes): augment review pack <range> with <N>장 webquiz"`
````

`## 오류 처리` 표에 행 추가:

```markdown
| 보강: `.pack` manifest와 HTML 카드 불일치 | 차이를 보고하고 멈춤(HTML을 덮어쓰지 않음) |
| 보강: 기존 카드 보호 검사 실패 | 쓰지 않고 멈춤, 바뀐 카드와 필드를 보고 |
```

`references/review-prompt.md` 블라인드 스니펫: 첫 줄을 `REVIEW=… OUT="$RUN/work/blind-<range>.md" IDS="" python3 - <<'EOF'`로 바꾸고, `cards = re.findall(...)` 다음 줄에 추가:

```python
ids = {i for i in os.environ.get("IDS", "").split(",") if i}
if ids:  # 보강 모드: 새 카드만
    cards = [c for c in cards if c[0] in ids]
```

스니펫 아래 안내 문장 "출력 문항 수가 manifest 문제 수와 다르면…" 다음에 추가: `보강 모드에서는 \`IDS\`에 새 카드 id만 넣는다(출력 문항 수 = 새 카드 수).`

- [ ] **Step 4: 통과 확인 (전체)**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/references/review-prompt.md .agents/skills/bio-review-pack/tests/test_skill_files.py
git -C "$WT" commit -m "docs(bio-review-pack): document augment mode and blind copy for new cards

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 변형 규칙 문구 (#11 낯선 참 진술, #12 장 섞기, 보고 줄, 쌍둥이 문구)

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/webquiz-style.md` (3절 쌍둥이 31행, 3절 끝, 4절)
- Modify: `.agents/skills/bio-review-pack/references/problem-selection.md` (6절 `웹과제 유형` 값 문장)
- Modify: `.agents/skills/bio-review-pack/references/card-rules.md` (쌍둥이 규칙 다음)
- Modify: `.agents/skills/bio-review-pack/references/review-prompt.md` (블라인드 브리프 목록)
- Modify: `.agents/skills/bio-review-pack/SKILL.md` (9단계 문항 줄)
- Test: `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`

**Interfaces:**
- Consumes: 없음
- Produces: 문서 규칙. `variants.md` 표시 값 `+낯선참`, `+장섞기`.

- [ ] **Step 1: 테스트 먼저 바꾸기** — `tests/test_webquiz_rules.py`

상단 `TYPES` 아래에 추가:

```python
MODIFIERS = ("낯선 참 진술", "장 섞기")
```

`TestWebquizStyle`에서 `test_twin_guards`의 `self.assertIn("보기 5개는 새로 쓴다", twin)`을 다음으로 바꾼다:

```python
        self.assertIn("보기는 새로 쓴다(5개 기본, 안 되면 4개)", twin)
        self.assertNotIn("보기 5개는 새로 쓴다", twin)
```

`TestWebquizStyle`에 추가:

```python
    def test_modifiers_have_four_parts(self):
        body = section(self.text, "## 3. 유형")
        for t in MODIFIERS:
            with self.subTest(t=t):
                part = section(body, f"### {t}")
                for label in ("정의:", "실제 예:", "만드는 법:", "피할 것:"):
                    self.assertIn(label, part)

    def test_unfamiliar_true_statement_guards(self):
        part = section(section(self.text, "## 3. 유형"), "### 낯선 참 진술")
        for s in ("오답 보기", "부정형", "출처", "정답 보기에는 쓰지 않는다", "3장 q5"):
            with self.subTest(s=s):
                self.assertIn(s, part)

    def test_mix_chapters_guards(self):
        part = section(section(self.text, "## 3. 유형"), "### 장 섞기")
        self.assertIn("앞선 팩", part)
        self.assertIn("금지어", part)
```

`test_quota`의 문자열 목록 끝에 `"낯선 참 진술 1~2개", "장 섞기 1개 이상"`을 더한다.

`TestSelectionRules.test_variants_table_has_type_column`의 값 튜플에 `"`+낯선참`"`, `"`+장섞기`"`를 더한다.

`TestReportRules.test_report_counts_types`를 다음으로 바꾼다:

```python
    def test_report_counts_types(self):
        self.assertIn("포함 N (웹과제 w, 기출 x) · 변형 v (쌍둥이 t · 그림 g · 상황 s · ㄱㄴㄷ k · 부정형 n · 용어 r · 낯선참 u · 장섞기 c)", self.report)
        self.assertNotIn("웹과제 a, 기출 b", self.report)
        self.assertIn("0개인 유형은 사유", self.report)
```

새 클래스 추가:

```python
class TestBlindBrief(unittest.TestCase):
    def test_blind_reviewer_ignores_unfamiliar_true_option(self):
        text = read(REFS / "review-prompt.md")
        self.assertIn("`+낯선참`", text)
        self.assertIn("정답 보기의 근거만", text)
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_webquiz_rules -v`
Expected: 바꾼·새 테스트 FAIL

- [ ] **Step 3: 문서 고치기**

`webquiz-style.md` 31행 "발문은 글자 그대로 쓰고 보기 5개는 새로 쓴다." → "발문은 글자 그대로 쓰고 보기는 새로 쓴다(5개 기본, 안 되면 4개)."

`webquiz-style.md` 3절 끝(`### 용어 바꿔 쓰기` 블록 다음, `## 4. 할당` 앞)에 추가:

```markdown
### 낯선 참 진술

- 정의: 수업에서 다루지 않았지만 교과서에 있는 **참인** 진술을 부정형 문제의 오답 보기로 넣은 표시(`+낯선참`). 단독 유형이 아니라 다른 문제에 붙인다.
- 실제 예: 3장 q5 "옳지 않은 것"의 보기 E "히스톤 단백질에는 양전하를 띤 아미노산이 많다"(교과서 부록 용어풀이에만 있음, 정답은 수업에서 배운 D), 3장 q12 ㄷ "M기에 방추사 단백질 합성"의 세부(수업은 "G2기에 분열 준비"까지만).
- 만드는 법: 부정형("옳지 않은 것") 문제에서 오답 보기 하나를 그 장 교과서에서 확인한 참인 진술로 쓴다. 풀이에 "수업 밖이지만 맞는 진술이에요(출처: 교재 N장 p.x). 확실히 틀린 보기를 먼저 찾아요."를 쓴다. 정답은 수업에서 배운 사실로 정해진다.
- 피할 것: 이 진술을 정답 보기로 쓰는 것(정답 보기에는 쓰지 않는다). 출처를 확인하지 못한 진술. 금지어나 다음 장 개념.

### 장 섞기

- 정의: 이번 범위의 개념에 앞선 팩(이전 장·이전 회차)의 개념을 함께 엮은 표시(`+장섞기`). 단독 유형이 아니라 다른 문제에 붙인다.
- 실제 예: 2장 q7 시금치 잎(2장 광계·색소와 1장 셀룰로오스를 함께 물음). 3장 q7의 "연관"은 다음 장 개념이라 이 표시에 해당하지 않는다.
- 만드는 법: 이번 팩 토픽을 anchor로 두고, 앞선 팩 토픽의 개념 하나를 보기나 조건에 넣는다. 풀이의 "수업과의 연결"에 앞선 팩 정리노트 링크를 붙인다.
- 피할 것: 앞선 팩에 없는 개념, 다음 장 개념(금지어 규칙과 충돌), 앞선 팩 개념만으로 풀리는 문제.
```

`webquiz-style.md` 4절 "- 최소: …" 줄 다음에 추가:

```markdown
- 표시: 낯선 참 진술 1~2개(부정형 문제의 오답 보기에만), 장 섞기 1개 이상(앞선 팩이 있을 때). 다른 유형 문제와 겹쳐도 된다.
```

`problem-selection.md` 6절의 "부정형 발문이면 `+부정형`, 용어 바꿔 쓰기면 `+용어`를 붙인다(예: `그림+부정형`)." → "부정형 발문이면 `+부정형`, 용어 바꿔 쓰기면 `+용어`, 낯선 참 진술이면 `+낯선참`, 장 섞기면 `+장섞기`를 붙인다(예: `그림+부정형+낯선참`). 낯선 참 진술은 `형태` 칸에 교과서 출처(예: `교재 3장 p.68`)를 적는다."

`card-rules.md` 쌍둥이 규칙 줄 다음에 추가:

```markdown
- 낯선 참 진술(`variants.md` 표시 `+낯선참`): 그 보기 진단을 "맞아요. 수업 밖이지만 맞는 진술이에요(출처: 교재 N장 p.x). 확실히 틀린 보기를 먼저 찾아요."로 쓴다. 장 섞기(`+장섞기`): "수업과의 연결"에 앞선 팩 정리노트 토픽 링크(`../<range>/정리노트_<range>_<slug>.html#<토픽>`)를 붙인다.
```

`review-prompt.md` 블라인드 브리프의 "- 문항마다 답을 고르고, …" 줄 다음에 추가:

```markdown
- 보기 진단에 `+낯선참`으로 설계된 보기(교과서에만 있는 참인 진술)는 정리노트에 근거가 없어도 정상이다. 정답 보기의 근거만 판정하고, 그 보기 때문에 "근거 없음"으로 적지 않는다.
```

(이 줄은 리뷰어 지시문 안이므로 메인 에이전트가 블라인드 사본을 줄 때 어떤 카드가 `+낯선참`인지 `variants.md`에서 골라 함께 알려 준다 — 같은 줄 끝에 "(메인 에이전트가 해당 카드 id를 알려 준다)"를 붙인다.)

`SKILL.md` 9단계 문항 줄의 `- 문항: 포함 N (웹과제 a, 기출 b) · 변형 v (쌍둥이 a · 그림 b · 상황 c · ㄱㄴㄷ d · 부정형 e) · 이전 팩 N …`을 `- 문항: 포함 N (웹과제 w, 기출 x) · 변형 v (쌍둥이 t · 그림 g · 상황 s · ㄱㄴㄷ k · 부정형 n · 용어 r · 낯선참 u · 장섞기 c) · 이전 팩 N …`으로 바꾼다(줄의 나머지는 그대로).

- [ ] **Step 4: 통과 확인 (전체)**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .agents/skills/bio-review-pack/references .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/tests/test_webquiz_rules.py
git -C "$WT" commit -m "feat(bio-review-pack): add unfamiliar-true and chapter-mix variant markers

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: 카드 손질 (0910 p49·p50, 0929 p35·p36) — 보강 모드로 다시 조립

**Files:**
- Modify: `복습노트/0910/복습문제_0910_Cells_and_Cellular_Respiration.{html,md}`, `복습노트/0910/.pack/{manifest.json,log.md}`
- Modify: `복습노트/0929/복습문제_0929_Heredity.{html,md}`, `복습노트/0929/.pack/{manifest.json,log.md}`

**Interfaces:**
- Consumes: Task 4·5 `augment.py extract|build`, Task 3 `html2md --only review`
- Produces: 손질된 카드. 카드 id·정답 불변.

- [ ] **Step 1: 0910 추출과 p49·p50 손질**

```bash
WT="/Users/hyunjun_macbook_pro/Documents/Univ/생명과학-augment"; S="$WT/.agents/skills/bio-review-pack"; RUN="$WT/../augment-runs/0910"
python3 "$S/scripts/augment.py" extract "$WT/복습노트/0910" "$RUN"
RUN="$RUN" python3 - <<'EOF'
import os, re
from pathlib import Path
run = Path(os.environ["RUN"])
for pid in ("p49", "p50"):
    p = run / "cards" / f"{pid}.html"
    t = p.read_text(encoding="utf-8")
    m = re.search(r'(</ol>\s*<p class="answer">[^<]*</p>)((?:\s*<p>(?:원문 정답과 달라진 점|수업과의 연결):.*?</p>)+)', t, re.S)
    assert m, f"{pid}: 정답 줄 뒤 문단을 못 찾음"
    items = re.findall(r'<p>((?:원문 정답과 달라진 점|수업과의 연결):.*?)</p>', m.group(2), re.S)
    assert [i.split(":")[0] for i in items] == ["원문 정답과 달라진 점", "수업과의 연결"], items
    t = t[:m.start()] + "".join(f"<li>{i}</li>" for i in items) + m.group(1) + t[m.end():]
    p.write_text(t, encoding="utf-8")
    print(pid, "옮김")
EOF
```
Expected: `p49 옮김`, `p50 옮김`. (`augment-runs/`는 워크트리 밖 형제 폴더라 커밋되지 않는다.)

- [ ] **Step 2: 0910 조립·변환·검사**

```bash
python3 "$S/scripts/augment.py" build "$WT/복습노트/0910" "$RUN"
P="$WT/복습노트/0910"; N="$(ls "$P"/정리노트_*.html)"; R="$(ls "$P"/복습문제_*.html)"
python3 "$S/scripts/html2md.py" "$N" "$R" --only review --check | tail -1
python3 "$S/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$N" --review "$R" | tail -1
git -C "$WT" diff --stat 복습노트/0910
```
Expected: `추가: 없음`, `OK`, `OK`, 변경 파일은 복습문제 `.html`·`.md`와 `.pack/manifest.json`(정렬·문구 동일이면 변경 없음)·`.pack/log.md`뿐. 정리노트 파일이 보이면 멈춘다.

- [ ] **Step 3: 바뀐 카드가 p49·p50뿐인지 확인**

```bash
WT="$WT" python3 - <<'EOF'
import os, re, subprocess
wt = os.environ["WT"]
path = next(f for f in os.listdir(f"{wt}/복습노트/0910") if f.endswith(".html") and "복습문제" in __import__("unicodedata").normalize("NFC", f))
old = subprocess.run(["git", "-C", wt, "show", f"HEAD:복습노트/0910/{path}"], capture_output=True, text=True).stdout
new = open(f"{wt}/복습노트/0910/{path}", encoding="utf-8").read()
CARD = re.compile(r'<article class="card" id="(p\d+)"[^>]*>.*?</article>', re.S)
a, b = {m.group(1): m.group(0) for m in CARD.finditer(old)}, {m.group(1): m.group(0) for m in CARD.finditer(new)}
assert a.keys() == b.keys()
print(sorted(k for k in a if a[k] != b[k]))
EOF
```
Expected: `['p49', 'p50']`

- [ ] **Step 4: 0929 추출과 p35·p36 손질 → 조립·변환·검사**

```bash
RUN="$WT/../augment-runs/0929"
python3 "$S/scripts/augment.py" extract "$WT/복습노트/0929" "$RUN"
RUN="$RUN" python3 - <<'EOF'
import os
from pathlib import Path
run = Path(os.environ["RUN"])
for pid in ("p35", "p36"):
    p = run / "cards" / f"{pid}.html"
    t = p.read_text(encoding="utf-8")
    assert t.count("기출 4강 합본 ") == 1, pid
    p.write_text(t.replace("기출 4강 합본 ", "기출 4강 "), encoding="utf-8")
    print(pid, "고침")
EOF
python3 "$S/scripts/augment.py" build "$WT/복습노트/0929" "$RUN"
P="$WT/복습노트/0929"; N="$(ls "$P"/정리노트_*.html)"; R="$(ls "$P"/복습문제_*.html)"
python3 "$S/scripts/html2md.py" "$N" "$R" --only review --check | tail -1
python3 "$S/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$N" --review "$R" | tail -1
grep -c "기출 4강 합본 3[29]번 발문" "$R"
```
Expected: `p35 고침`, `p36 고침`, `OK`, `OK`, 마지막 `0`. Step 3의 확인 스크립트를 `0910`→`0929`로 바꿔 돌려 `['p35', 'p36']`인지 본다.

- [ ] **Step 5: 브라우저 검사**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 browser_check_review.py`
Expected: 모든 검사 통과

- [ ] **Step 6: Commit**

```bash
git -C "$WT" add 복습노트/0910 복습노트/0929
git -C "$WT" commit -m "docs(notes): align twin card endings and source labels (0910 p49-p50, 0929 p35-p36)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: 보충 배지 구분 + 정리노트 보충 5곳 (핸드오프 4번, 결정 #13)

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/check_html.py:36-38, 305-307`
- Modify: `.agents/skills/bio-review-pack/references/content-rules.md:25, 39`
- Modify: `복습노트/{0910,0915,0917,0922}/정리노트_*.{html,md}`, 각 `.pack/manifest.json`·`.pack/log.md`
- Test: `.agents/skills/bio-review-pack/tests/test_check_html.py`

**Interfaces:**
- Consumes: Task 1 `.pack/manifest.json`, Task 3 `html2md` 전체 변환
- Produces: `check_html.SUPP_LABEL_NOTE_GAP = "보충 · 노트에 빠졌던 수업 내용"`, `check_html.SUPP_LABELS` 튜플

- [ ] **Step 1: 실패하는 테스트** — `tests/test_check_html.py` 끝(`if __name__` 앞)에 추가(`import check_html`이 없으면 더한다)

```python
class TestSuppBadges(unittest.TestCase):
    def note(self, badge):
        src = ('<html lang="ko"><body><main><section id="s1"><h2>1</h2>'
               '<article class="topic" id="s1-a"><h3>A</h3>'
               f'<div class="layer supp"><span class="badge supp">{badge}</span><p>사실</p><p>출처: 0903 수업</p></div>'
               '</article></section></main></body></html>')
        m = {"sections": [{"id": "s1", "topics": [{"id": "s1-a", "required_terms": [], "layers": [], "supp": True}]}],
             "preview_topic": "s1-a", "forbidden_outside_preview": [], "links": []}
        return [p for p in check_html.check_note(check_html.parse_html(src), m) if p.code == "missing-supp"]

    def test_both_badges_accepted(self):
        self.assertEqual(self.note("보충 · 수업에서 다루지 않았어요"), [])
        self.assertEqual(self.note("보충 · 노트에 빠졌던 수업 내용"), [])

    def test_other_badge_rejected(self):
        self.assertEqual(len(self.note("보충")), 1)
```

- [ ] **Step 2: 실패 확인**

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest test_check_html.TestSuppBadges -v`
Expected: `test_both_badges_accepted` FAIL

- [ ] **Step 3: 구현** — `check_html.py` 36행 근처

```python
SUPP_LABEL = "보충 · 수업에서 다루지 않았어요"
SUPP_LABEL_NOTE_GAP = "보충 · 노트에 빠졌던 수업 내용"
SUPP_LABELS = (SUPP_LABEL, SUPP_LABEL_NOTE_GAP)
```

305–307행:

```python
            if t["supp"] and ("supp" not in con.child_classes
                              or not any(label in con.text for label in (*SUPP_LABELS, *LEGACY_SUPP_LABELS))):
                out.append(Problem("missing-supp", t["id"], f"layer supp + '{SUPP_LABEL}' 또는 '{SUPP_LABEL_NOTE_GAP}' 필요"))
```

`content-rules.md` 25행 끝에 덧붙인다: " 배지는 둘 중 하나다. 강의노트·STT 어디에도 없고 교재·외부에만 있으면 `보충 · 수업에서 다루지 않았어요`, STT나 강의노트에 있는데 정리노트 본문에서 빠졌으면 `보충 · 노트에 빠졌던 수업 내용`. 출처 줄로 어느 자료인지 밝힌다(`출처: 0903 수업, 강의노트 1장 p5`)."

39행 마크업 예시 아래 줄에 추가: `  <div class="layer supp"><span class="badge supp">보충 · 노트에 빠졌던 수업 내용</span><p>…</p><p>출처: 0922 수업, 강의노트 3장 p2</p></div>   ← 수업 자료에는 있는데 노트에서 빠진 사실`

Run: `cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py"` → `OK`. 커밋:

```bash
git -C "$WT" add .agents/skills/bio-review-pack/scripts/check_html.py .agents/skills/bio-review-pack/references/content-rules.md .agents/skills/bio-review-pack/tests/test_check_html.py
git -C "$WT" commit -m "feat(bio-review-pack): accept a note-gap supplement badge

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: 근거 재확인** (넣기 전에. 이 대화에서 찾은 근거 위치)

| 팩·토픽 | 넣을 문장(학생용, ~해요) | 배지 | 출처 줄 | 근거 확인 명령 |
|---|---|---|---|---|
| 0917 `s2-chromatin` | 염색체는 분열이 시작되는 전기에 응축되기 시작해서 막대 모양으로 보이게 돼요. | 노트에 빠졌던 수업 내용 | `출처: 0922 수업, 강의노트 3장 p2` | `grep -n "전기 때 염색체가 응축" "STT/0922 생명.md"` / 강의노트 3장 p2 "전기 : 염색체 응축" |
| 0917 `s2-chromatin` | 히스톤 단백질에는 양전하를 띤 아미노산이 많아서, 음전하를 띤 DNA가 히스톤에 잘 감겨요. | 수업에서 다루지 않았어요 | `출처: 교재 부록 용어풀이 p.12 (histone)` | `교과서/생명과학_기초와_응용_2판/부록_용어풀이.pdf` 12쪽에서 histone 항목 확인 |
| 0915 세포호흡·미토콘드리아 토픽(`grep -o 'id="s3-[a-z-]*"' 정리노트_0915*.html`로 찾고, 없으면 `s3-electron-flow`) | 식물 세포도 엽록체와 함께 미토콘드리아를 가지고 있어서, 동물처럼 세포호흡으로 ATP를 만들어요. | 노트에 빠졌던 수업 내용 | `출처: 0910 수업` | `grep -n "미토콘드리아는 동물, 식물 다" "STT/0910 생명.md"` |
| 0915 `s3-pigments` | 잎이 녹색으로 보이는 주된 색소는 엽록소예요. 카로티노이드 같은 다른 색소도 있지만 양이 더 적어요. | 노트에 빠졌던 수업 내용 | `출처: 0915 수업, 강의노트 2장` | `grep -n "엽록소가 녹색을" "STT/0915 생명.md"` |
| 0915 `s3-pigments` | 사람은 셀룰로오스를 분해하지 못해서 연료로 쓰지 못해요. 잎을 먹어도 셀룰로오스에서는 에너지를 얻지 못해요. | 노트에 빠졌던 수업 내용 | `출처: 0903 수업` | `grep -n "사람은 이걸 연료로 사용 못" "STT/0903 생명.md"` |
| 0910 `s5-atp-synthase` | H⁺는 ATP 합성효소를 통해서만 기질로 돌아올 수 있어요. 그래서 ATP 합성효소가 막히면 전자전달계가 퍼낸 H⁺가 쌓여 막 사이 공간과 기질의 H⁺ 농도 차(pH 차이)가 커져요. | 노트에 빠졌던 수업 내용 | `출처: 0910 수업, 강의노트 2장` | `grep -n "ATP 합성 효소만을 통해서만" "STT/0910 생명.md"` |
| 0922 `s1-phases` | 전기에는 두 중심체가 서로 떨어져 세포의 양쪽 극으로 이동해요. | 노트에 빠졌던 수업 내용 | `출처: 강의노트 3장 p2` | 강의노트 3장 p2 "전기 : 염색체 응축, 중심체 분리" |

토픽 id가 실제 정리노트에 있는지 먼저 확인한다: `grep -o 'id="s[0-9]-[a-z-]*"' "$WT/복습노트/<range>/정리노트_*.html" | sort -u`. 근거 확인 명령이 아무것도 찾지 못한 행은 넣지 않고 보고서 "미해결"에 적는다. 이 대화의 대조 결과 "중기에 가장 응축"은 STT·강의노트에서 찾지 못했으므로, 교과서 3장에서 확인될 때만 0917 첫 문장 끝에 "중기에 가장 많이 응축돼요."를 붙이고 출처 줄에 교과서 쪽을 더한다.

- [ ] **Step 5: 보충 넣기 스크립트** (팩·토픽·배지·문장 묶음마다 한 번씩 실행. 같은 토픽에 같은 배지 레이어가 이미 있으면 그 안에 문단을 이어 붙인다)

```bash
WT="$WT" RANGE=0917 TOPIC=s2-chromatin BADGE="보충 · 노트에 빠졌던 수업 내용" TEXT="염색체는 분열이 시작되는 전기에 응축되기 시작해서 막대 모양으로 보이게 돼요." SRC="출처: 0922 수업, 강의노트 3장 p2" python3 - <<'EOF'
import html, json, os, re, unicodedata as u
from pathlib import Path
e = os.environ
pack = Path(e["WT"]) / "복습노트" / e["RANGE"]
note = next(p for p in pack.iterdir() if u.normalize("NFC", p.name).startswith("정리노트_") and p.suffix == ".html")
t = note.read_text(encoding="utf-8")
start = t.index(f'<article class="topic" id="{e["TOPIC"]}">')
end = t.index("</article>", start)
topic = t[start:end]
para = f'<p>{html.escape(e["TEXT"], quote=False)}</p><p>{html.escape(e["SRC"], quote=False)}</p>'
badge = f'<span class="badge supp">{e["BADGE"]}</span>'
if badge in topic:  # 같은 배지 레이어 끝에 이어 붙인다
    layer_at = topic.index(badge)
    close = topic.index("</div>", layer_at)
    topic = topic[:close] + para + topic[close:]
else:  # 새 레이어는 페이지 요약(.sum) 앞, 없으면 토픽 끝
    layer = f'<div class="layer supp">{badge}{para}</div>\n'
    at = topic.find('<div class="sum"')
    topic = topic[:at] + layer + topic[at:] if at >= 0 else topic + layer
t = t[:start] + topic + t[end:]
note.write_text(t, encoding="utf-8")
mf = pack / ".pack" / "manifest.json"
m = json.loads(mf.read_text(encoding="utf-8"))
for s in m["sections"]:
    for tp in s["topics"]:
        if tp["id"] == e["TOPIC"]:
            tp["supp"] = True
mf.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
with open(pack / ".pack" / "log.md", "a", encoding="utf-8") as f:
    f.write(f"- 2026-10-0x 노트 보충: {e['TOPIC']} ({e['BADGE']})\n")
print(note.name, e["TOPIC"], "보충")
EOF
```

`.pack`이 없는 팩은 없다(0910~0922는 Task 1에서 만듦). `log.md` 줄의 날짜는 실행 날짜(`date +%F`)로 바꿔 쓴다. 보충 레이어 안의 `<p>` 텍스트에 이 문서의 `<`·`>`가 없으므로 escape는 안전장치다.

- [ ] **Step 6: 팩마다 MD 전체 변환과 검사** (정리노트가 바뀌었으니 `--only` 없이)

```bash
for r in 0910 0915 0917 0922; do P="$WT/복습노트/$r"; N="$(ls "$P"/정리노트_*.html)"; R="$(ls "$P"/복습문제_*.html)"
python3 "$S/scripts/html2md.py" "$N" "$R" --check | tail -1
python3 "$S/scripts/check_html.py" --manifest "$P/.pack/manifest.json" --note "$N" --review "$R" | tail -1; done
git -C "$WT" diff --stat 복습노트
```
Expected: 팩마다 `OK` 두 줄. `diff --stat`에서 복습문제 MD가 바뀌었다면 변환기 차이다 — 내용을 보고 의미 변화가 없으면 그대로 두고 보고서에 적는다.

- [ ] **Step 7: 브라우저로 보충 레이어 확인** — `references/browser-check.md`대로 서버를 띄워 0917 정리노트 `#s2-chromatin`을 열고 보충 배지 두 개가 보이는지, 375px 가로 스크롤이 없는지 확인한 뒤 서버를 끈다.

- [ ] **Step 8: Commit**

```bash
git -C "$WT" add 복습노트/0910 복습노트/0915 복습노트/0917 복습노트/0922
git -C "$WT" commit -m "docs(notes): fill note gaps found by blind checks of webquiz cards

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: 커닝페이퍼 당황 패턴 (2장 사실 + 패턴 3개)

**Files:**
- Modify: `.agents/skills/bio-cheatsheet/references/panic-patterns.md`

**Interfaces:**
- Consumes: 없음
- Produces: ① 구역 원천 12줄

- [ ] **Step 1: 숫자 가정 재확인**

Run: `grep -rn "9개\|9줄" "$WT/.agents/skills/bio-cheatsheet" --include=*.md --include=*.py`
Expected: `references/panic-patterns.md`의 20행·34행만. 다른 곳이 나오면 그 파일도 12로 고친다.

- [ ] **Step 2: 파일 고치기**

3행 출처 문장 끝에 덧붙인다: " 2장은 `웹과제/2장/questions.json`·`intake.md`(2026-10-01 응시)."

`## 3장 웹과제 사실` 절 앞에 새 절:

```markdown
## 2장 웹과제 사실 (① 안에서는 반드시 "2장:"을 붙인다)

- 16문항, 모두 보기 5개. 시간 제한은 화면에 없음.
- 3/16이 부정형("일어나지 않는 것" Q1, "옳지 않은 것" Q5·Q9).
- 그림 3개: Q4 자유에너지 그래프(구간 I~IV), Q9 세포호흡 개요 모식도((가)(나)(다) 빈 라벨), Q15 ATP 분자.
- 기출과 같은 문제는 3개(Q3·Q13·Q15), 기출 발문 그대로 정답만 바꾼 문제 3개(Q1·Q8·Q10).
```

20행 `## 패턴 9개 → 이 장 구역 번호로 잇기` → `## 패턴 12개 → 이 장 구역 번호로 잇기`

표 마지막 행(`ㄱ·ㄴ·ㄷ 조합형`) 아래에 3행 추가:

```markdown
| 같은 발문, 다른 정답 | 2장 Q1·Q8·Q10(기출 2강 9·39·32번 발문 그대로) | 발문이 익숙해도 보기마다 참·거짓 판정. 외운 답 번호로 고르지 않기 |
| 오타로 정답이 이상해 보임 | 2장 Q7 "관계"(=광계), Q1 "관합성", Q5 "마지막 관계" | 말이 안 되는 보기는 비슷한 용어로 바꿔 읽어 보기 |
| 다른 장 개념이 섞임 | 3장 Q7 정답 "연관"(4장 개념) | 아는 범위 밖 낱말이 정답일 수 있음. 응시일까지 배운 다음 장 개념도 후보 |
```

34행 `① 구역은 위 9줄을` → `① 구역은 위 12줄을`

- [ ] **Step 3: 테스트**

Run: `cd "$WT/.agents/skills/bio-cheatsheet/tests" && python3 -m unittest discover -p "test_*.py"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git -C "$WT" add .agents/skills/bio-cheatsheet/references/panic-patterns.md
git -C "$WT" commit -m "docs(bio-cheatsheet): add chapter 2 webquiz facts and three panic patterns

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: 기존 변형 29개 5지선다화 (N1)

**Files:**
- Modify: `복습노트/{0910,0915,0917,0929}/복습문제_*.{html,md}`, 각 `.pack/log.md`
- 대상: 0910 p31–p39, 0915 p16–p23, 0917 p24–p29, 0929 p29–p34 (1001 제외)

**Interfaces:**
- Consumes: Task 4·5 `augment.py`, Task 3 `html2md --only review`, Task 6 블라인드 `IDS`
- Produces: 대상 카드가 보기 5개. id·정답 번호 불변.

- [ ] **Step 1: 대상이 정말 4지인지 확인** (이미 5지인 카드는 건너뛴다)

```bash
WT="$WT" python3 - <<'EOF'
import os, re, unicodedata as u
targets = {"0910": range(31, 40), "0915": range(16, 24), "0917": range(24, 30), "0929": range(29, 35)}
for r, ids in targets.items():
    d = f"{os.environ['WT']}/복습노트/{r}"
    f = next(x for x in os.listdir(d) if u.normalize("NFC", x).startswith("복습문제_") and x.endswith(".html"))
    t = open(f"{d}/{f}", encoding="utf-8").read()
    for i in ids:
        card = re.search(rf'<article class="card" id="p{i}".*?</article>', t, re.S).group(0)
        n = len(re.findall(r"<li>\(\d\)", re.search(r'<ul class="choices">(.*?)</ul>', card, re.S).group(1)))
        print(r, f"p{i}", n)
EOF
```
Expected: 대부분 `4`. `5`인 카드는 대상에서 뺀다.

- [ ] **Step 2: 팩마다 추출** — `RUN="$WT/../augment-runs/<range>-5"; python3 "$S/scripts/augment.py" extract "$WT/복습노트/<range>" "$RUN"`

- [ ] **Step 3: 카드마다 보기 (5)와 진단 추가** (카드 작성자 일. 한 팩씩, 대상 카드 파일만 고친다)

규칙:
- `<ul class="choices">` 끝에 `<li>(5) …</li>`를 하나 더한다. 기존 보기 순서와 글자, 정답 번호는 바꾸지 않는다.
- 새 보기는 그 카드의 혼동 묶음(원문 정보의 "다루는 혼동")을 겨냥한 **오답**이다. 이번 팩과 이전 수업 범위 안의 개념만 쓴다. 금지어(`.pack/manifest.json`의 `forbidden_outside_preview`)를 쓰지 않는다.
- 부정형 발문("옳지 않은 것")이면 새 보기는 **맞는 진술**이어야 오답이 된다. 긍정형이면 틀린 진술이어야 한다.
- 풀이 `<ol class="steps">`에서 `(4)` 진단 `<li>` 바로 다음에 `<li>(5) 틀려요./맞아요. …이유 한 문장…</li>`를 넣는다("수업과의 연결"·"원문 정답과 달라진 점" `<li>`보다 앞).
- 보기·진단에 STT 시각·원문자·이모지를 쓰지 않는다.

카드마다 고친 뒤 확인:

```bash
RUN="$RUN" python3 - <<'EOF'
import os, re
from pathlib import Path
for p in sorted(Path(os.environ["RUN"], "cards").glob("p*.html")):
    t = p.read_text(encoding="utf-8")
    opts = re.findall(r"<li>\((\d)\)", re.search(r'<ul class="choices">(.*?)</ul>', t, re.S).group(1))
    diag = re.findall(r"<li>\((\d)\)", re.search(r'<ol class="steps">(.*?)</ol>', t, re.S).group(1)) if '<ol class="steps">' in t else []
    if opts == ["1", "2", "3", "4", "5"]:
        print(p.stem, "보기", opts, "진단", sorted(set(diag)))
EOF
```
Expected: 대상 카드마다 보기와 진단이 모두 `1`~`5`.

- [ ] **Step 4: 조립·변환·검사** (팩마다)

```bash
python3 "$S/scripts/augment.py" build "$WT/복습노트/<range>" "$RUN"
P="$WT/복습노트/<range>"; N="$(ls "$P"/정리노트_*.html)"; R="$(ls "$P"/복습문제_*.html)"
python3 "$S/scripts/html2md.py" "$N" "$R" --only review --check | tail -1
python3 "$S/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$N" --review "$R" | tail -1
```
Expected: `추가: 없음`, `OK`, `OK`. 보호 검사가 정답 불변을 보장한다(`answer`가 바뀌면 build가 멈춘다).

- [ ] **Step 5: 블라인드 검사 (고친 카드만)** — `references/review-prompt.md` 스니펫을 `IDS=<그 팩 대상 id 목록>`으로 돌려 사본을 만들고, 블라인드 리뷰어 1명에게 정리노트와 사본만 준다. 리뷰어 답이 정답과 다르거나 "근거 없음"이면 **새 보기 (5)**가 원인인지 먼저 보고, 그렇다면 그 보기를 고쳐 Step 4부터 다시 한다(정리노트는 고치지 않는다).

- [ ] **Step 6: 바뀐 카드 범위 확인** — Task 8 Step 3의 확인 스크립트를 range만 바꿔 돌려, 바뀐 카드가 대상 id와 같은지 본다.

- [ ] **Step 7: 브라우저** — `python3 browser_check_review.py` 통과, 그리고 `references/browser-check.md`대로 각 팩에서 고친 카드 하나를 열어 보기 5개·진단 펼침을 확인한다.

- [ ] **Step 8: Commit** (팩마다 하나씩)

```bash
git -C "$WT" add 복습노트/<range>
git -C "$WT" commit -m "docs(notes): extend <range> variants to five options without changing answers

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: 마무리 — 전체 검사, 기준 브랜치 반영, 보고

**Files:** 없음(검사만)

- [ ] **Step 1: 전체 테스트**

```bash
cd "$WT/.agents/skills/bio-review-pack/tests" && python3 -m unittest discover -p "test_*.py" && python3 browser_check_review.py
cd "$WT/.agents/skills/bio-cheatsheet/tests" && python3 -m unittest discover -p "test_*.py"
```
Expected: 모두 `OK`

- [ ] **Step 2: 풀이기록·1001 무변경 확인**

```bash
git -C "$WT" diff --stat bio-review-webquiz-variants -- '복습노트/*/풀이기록' 복습노트/1001
```
Expected: 출력 없음

- [ ] **Step 3: 기준 브랜치 최신 반영** (1001 세션 커밋이 먼저 들어갔을 수 있다)

```bash
git -C "$WT" merge --no-edit bio-review-webquiz-variants
```
충돌이 나면 해결하고 Step 1을 다시 한다. `TestReconstructRealPacks`가 새 1001 HTML도 왕복하는지 함께 확인된다.

- [ ] **Step 4: 보고** — 사용자에게 다음을 보고하고 병합 방식(기준 브랜치로 병합 / PR)을 묻는다.
  - 커밋 목록(`git -C "$WT" log --oneline bio-review-webquiz-variants..`)
  - `.pack` 소급 결과(금지어 복원: 0929만, 나머지 미복원)
  - 정리노트 보충: 넣은 줄과 넣지 못한 줄(근거 없음)
  - 5지화한 카드 수, 블라인드 검사 결과
  - 남은 일(사용자 몫): 0929·1001 팩을 풀고 풀이기록 JSON을 내보낸 뒤 4장 웹과제 결과와 비교 → `webquiz-style.md` 갱신 제안의 근거. 10/8 이후 `/bio-review-pack 0929 augment`, `/bio-review-pack 1001 augment`(1001은 그때 `.pack`이 없으니 HTML 복원 경로).
