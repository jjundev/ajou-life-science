"""SKILL.md 형식과, 본문이 가리키는 파일이 모두 있는지, 스니펫이 실제로 도는지 확인한다."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _util import SKILL

SKILL_MD = SKILL / "SKILL.md"


def snippet(first_line: str) -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(r"```bash\n" + re.escape(first_line) + r"\n(.*?)\nEOF\n```", text, re.S)
    assert m, f"SKILL.md 스니펫을 찾지 못함: {first_line}"
    return m.group(1)


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_augment_mode_documented(self):
        self.assertIn("`[MMDD | MMDD-MMDD] [augment]`", self.text)
        body = self.text[self.text.index("## 보강 모드"):self.text.index("## 오류 처리")]
        for s in ("scripts/augment.py", "extract", "build", "--only review", "IDS=", ".pack/manifest.json",
                  "풀이기록", "금지어 미복원", "기존 카드 번호"):
            with self.subTest(s=s):
                self.assertIn(s, body)
        for step in ("A1", "A2", "A3", "A4", "A5", "A6"):
            with self.subTest(step=step):
                self.assertIn(f"**{step}.", body)

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "bio-review-pack")
        self.assertIn("정리노트", m.group(2))
        self.assertIn("복습문제", m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?<!problem-explain/)(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 12)
        for rel in sorted(refs):
            with self.subTest(rel=rel):
                self.assertTrue((SKILL / rel).exists(), rel)

    def test_every_reference_is_used(self):
        for path in sorted((SKILL / "references").glob("*.md")):
            with self.subTest(ref=path.name):
                self.assertIn(f"references/{path.name}", self.text)

    def test_steps_present(self):
        for n in range(10):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### {n}\. ")

    def test_no_ml_leftovers(self):
        pattern = re.compile(r"MML|머신러닝|정방철|머러기|Mathematics_for|answers\.py")
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            with self.subTest(file=path.name):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))

    def test_no_circled_numbers_in_rules(self):
        # 원문자는 "쓰지 않는다"를 설명하는 ①~⑳ 범위 표기에서만 허용한다.
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8").replace("①~⑳", "").replace("①~⑤", "")
            with self.subTest(file=path.name):
                self.assertIsNone(re.search(r"[①-⑳]", text))

    def test_problem_explain_step(self):
        i8, i8b, i9 = (self.text.index(s) for s in ("\n### 8. ", "\n### 8b. 문제설명", "\n### 9. "))
        self.assertTrue(i8 < i8b < i9)
        self.assertIn("references/problem-explain.md", self.text[i8b:i9])

    def test_sibling_check_in_prepare(self):
        body = self.text[self.text.index("### 0. 준비"):self.text.index("### 1. ")]
        self.assertIn("bio-problem-explain/SKILL.md", body)
        self.assertIn("scripts/mpe_cli.py", body)

    def test_stale_explanation_reported(self):
        i8b = self.text.index("### 8b.")
        self.assertIn("이전 카드 기준(stale)", self.text[i8b:self.text.index("## ", i8b + 5)])
        self.assertIn("이전 카드 기준(stale)", self.text[self.text.index("## 오류 처리"):])
        t = (SKILL / "references" / "problem-explain.md").read_text(encoding="utf-8")
        self.assertIn("이전 카드 기준(stale)", t)

    def test_augment_reexplains(self):
        body = self.text[self.text.index("## 보강 모드"):self.text.index("## 오류 처리")]
        self.assertIn("**A5b.", body)
        self.assertIn("references/problem-explain.md", body)

    def test_report_has_explain_line(self):
        body = self.text[self.text.index("### 9. 보고"):self.text.index("## 보강 모드")]
        self.assertIn("- 문제설명:", body)
        self.assertIn("복습팩 생성됨 / 문제설명 보류", body)

    def test_reference_exists_without_forbidden_words(self):
        t = (SKILL / "references" / "problem-explain.md").read_text(encoding="utf-8")
        self.assertNotRegex(t, r"자구알|자료구조|\bds\b|ds-")
        for s in ("ABS_REVIEW", "EXPLAIN_RUN", "bio-problem-explain", "복습팩 생성됨 / 문제설명 보류",
                  "source_visual", "content", "independent", "browser"):
            self.assertIn(s, t)


class TestRangeSnippet(unittest.TestCase):
    """SKILL.md 0단계 기간 판정 스니펫을 임시 저장소에서 실제로 실행한다."""

    @classmethod
    def setUpClass(cls):
        cls.code = snippet("REPO=… python3 - <<'EOF'")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "STT").mkdir()
        for name in ("0903_생명.md", "0917 생명.md", unicodedata.normalize("NFD", "0922 생명.md"), "0924 생명.md", "메모.md"):
            (self.repo / "STT" / name).write_text("x", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_snippet(self):
        env = dict(os.environ, REPO=str(self.repo))
        r = subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_nothing_done_yet(self):
        self.assertIn("다음: 0903 0917 0922 0924", self.run_snippet())

    def test_new_pack_range_end_counts_as_done(self):
        pack = self.repo / "복습노트" / unicodedata.normalize("NFD", "0922-0924")
        pack.mkdir(parents=True)
        (pack / unicodedata.normalize("NFD", "정리노트_0922-0924_Cell_Division.html")).write_text("x", encoding="utf-8")
        out = self.run_snippet()
        self.assertIn("마지막 정리: 0924", out)
        self.assertRegex(out, r"다음:\s*$")


class TestBackupSnippet(unittest.TestCase):
    """SKILL.md 4단계 백업 스니펫(python 부분)을 임시 폴더에서 실제로 실행한다."""

    @classmethod
    def setUpClass(cls):
        cls.code = snippet("RANGE=<range> REPO=… RUN=… python3 - <<'EOF'")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.notes = self.tmp / "repo" / "복습노트"
        self.notes.mkdir(parents=True)
        self.run_dir = self.tmp / "run"
        self.run_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def backup(self, range_):
        env = dict(os.environ, RANGE=range_, REPO=str(self.tmp / "repo"), RUN=str(self.run_dir))
        return subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)

    def backups(self):
        return sorted(p for p in self.run_dir.iterdir() if p.name.startswith("previous-"))

    def test_nothing_to_back_up(self):
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업할 기존 팩 없음", r.stdout)
        self.assertEqual(self.backups(), [])

    def test_backs_up_dated_folder_layout(self):
        pack = self.notes / "0922"
        (pack / "figures_0922").mkdir(parents=True)
        (pack / "figures_0922" / "p2.png").write_bytes(b"x")
        (pack / "정리노트_0922_A.html").write_text("n", encoding="utf-8")
        (pack / unicodedata.normalize("NFD", "복습문제_0922_A.md")).write_text("r", encoding="utf-8")
        (pack / "장마감_0922_3장.md").write_text("c", encoding="utf-8")
        (self.notes / "0924").mkdir()
        (self.notes / "0924" / "정리노트_0924_B.html").write_text("other", encoding="utf-8")
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 4항목(파일 4개)", r.stdout)
        (d,) = self.backups()
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
        self.assertEqual(names, ["figures_0922", "복습문제_0922_A.md", "장마감_0922_3장.md", "정리노트_0922_A.html"])

    def test_backs_up_assets_folder_layout(self):
        pack = self.notes / "0922"
        side = pack / ".assets"
        (side / "figures_0922").mkdir(parents=True)
        (side / "figures_0922" / "p2.png").write_bytes(b"x")
        (side / unicodedata.normalize("NFD", "정리노트_0922_A.md")).write_text("n", encoding="utf-8")
        (side / "장마감_0922_3장.md").write_text("c", encoding="utf-8")
        (side / "figures_문제설명_0922_A").mkdir()
        (side / "figures_문제설명_0922_A" / "a.png").write_bytes(b"x")
        (side / "자료_문제설명_0922_A").mkdir()
        (side / "자료_문제설명_0922_A" / "manifest.json").write_text("{}", encoding="utf-8")
        (side / "자료_인터렉티브_01_A").mkdir()
        (side / "자료_인터렉티브_01_A" / "x.json").write_text("{}", encoding="utf-8")
        (side / "풀이기록").mkdir()
        (side / "풀이기록" / "y.json").write_text("{}", encoding="utf-8")
        (pack / "정리노트_0922_A.html").write_text("n", encoding="utf-8")
        (pack / ".pack").mkdir()
        (pack / ".pack" / "manifest.json").write_text("{}", encoding="utf-8")
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 7항목(파일 7개)", r.stdout)
        (d,) = self.backups()
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
        self.assertEqual(names, [
            ".pack", "figures_0922", "figures_문제설명_0922_A", "자료_문제설명_0922_A", "장마감_0922_3장.md",
            "정리노트_0922_A.html", "정리노트_0922_A.md"])

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

    def test_backs_up_explanations(self):
        pack = self.notes / "0922"
        (pack / "figures_문제설명_0922_X").mkdir(parents=True)
        (pack / "figures_문제설명_0922_X" / "a.png").write_bytes(b"x")
        (pack / "자료_문제설명_0922_X").mkdir()
        (pack / "자료_문제설명_0922_X" / "manifest.json").write_text("{}", encoding="utf-8")
        (pack / "문제설명_0922_X.html").write_text("e", encoding="utf-8")
        (pack / "풀이기록").mkdir()
        (pack / "풀이기록" / "y.json").write_text("{}", encoding="utf-8")
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        (d,) = self.backups()
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
        self.assertEqual(names, ["figures_문제설명_0922_X", "문제설명_0922_X.html", "자료_문제설명_0922_X"])
        self.assertTrue((d / unicodedata.normalize("NFC", "자료_문제설명_0922_X") / "manifest.json").is_file())

    def test_bad_range_fails_loudly(self):
        (self.notes / "정리노트_0922_A.html").write_text("n", encoding="utf-8")
        for bad in ("", "<range>", "922"):
            with self.subTest(bad=bad):
                r = self.backup(bad)
                self.assertEqual(r.returncode, 1)
                self.assertIn("백업 중단", r.stderr)
        self.assertEqual(self.backups(), [])


class TestBlindCopySnippet(unittest.TestCase):
    """references/review-prompt.md 블라인드 사본 스니펫을 임시 복습문제 HTML로 실제로 실행한다."""

    REVIEW_HTML = """<main>
<article class="card" id="p1" data-source="기출 3강 12">
  <h3>P1. 그림 문항</h3>
  <div class="problem"><p>그림에서 옳은 것은?</p>
    <figure class="figure"><img src=".assets/figures_x/p1.png" alt="세포 그림"></figure>
    <ul class="choices"><li>(1) 가</li><li>(2) 나</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>기출 3강 합본 12번</details>
  <details class="hint" open><summary>힌트 보기</summary>HINT_ONE</details>
  <details class="solution"><summary>풀이 보기</summary><p class="answer">정답: (2)</p> SOLUTION_ONE</details>
</article>
<article class="card" id="p2" data-source="웹과제 3장 4">
  <h3>P2. SVG 문항</h3>
  <div class="problem"><p>다음 그림을 보고 답하시오.</p>
    <figure class="figure"><svg viewBox="0 0 10 10" aria-label="막 구조"><rect id="p2-r" width="5" height="5"/><text x="1" y="8">ATP</text></svg></figure>
    <ul class="choices"><li>A. 하나</li><li>B. 둘</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>웹과제 3장 4번</details>
  <details class="hint" open><summary>힌트 보기</summary>HINT_TWO</details>
  <details class="solution"><summary>풀이 보기</summary><p class="answer">정답: B</p> SOLUTION_TWO</details>
</article>
</main>
"""

    @classmethod
    def setUpClass(cls):
        text = (SKILL / "references" / "review-prompt.md").read_text(encoding="utf-8")
        m = re.search(r"```bash\n(REVIEW=[^\n]*)\n(.*?)\nEOF\n```", text, re.S)
        assert m, "review-prompt.md 블라인드 사본 스니펫을 찾지 못함"
        cls.code = m.group(2)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.review = self.tmp / "pack" / "복습문제_x_A.html"
        self.review.parent.mkdir()
        self.review.write_text(self.REVIEW_HTML, encoding="utf-8")
        self.out = self.tmp / "work" / "blind-x.md"
        self.out.parent.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_ids_filter_keeps_only_listed_cards(self):
        env = dict(os.environ, REVIEW=str(self.review), OUT=str(self.out), IDS="p2")
        r = subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.out.read_text(encoding="utf-8")
        self.assertIn("## p2.", out)
        self.assertNotIn("## p1.", out)
        self.assertIn("1 문항", r.stdout)

    def test_blind_copy_keeps_png_and_svg_figures(self):
        env = dict(os.environ, REVIEW=str(self.review), OUT=str(self.out))
        r = subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 문항", r.stdout)
        out = self.out.read_text(encoding="utf-8")
        self.assertIn("## p1.", out)
        self.assertIn("## p2.", out)
        figs = re.findall(r"^\[그림: (.+)\]$", out, re.M)
        self.assertTrue(any(f.endswith(".assets/figures_x/p1.png") for f in figs), figs)
        svgs = [Path(f) for f in figs if f.endswith(".svg")]
        self.assertEqual(len(svgs), 1, figs)
        self.assertEqual(svgs[0].parent.name, "blind-figs")
        self.assertTrue(svgs[0].exists(), svgs[0])
        self.assertIn("<svg", svgs[0].read_text(encoding="utf-8"))
        for leaked in ("details", "풀이 보기", "힌트 보기", "HINT_", "SOLUTION_", "정답:"):
            with self.subTest(leaked=leaked):
                self.assertNotIn(leaked, out)


if __name__ == "__main__":
    unittest.main()
