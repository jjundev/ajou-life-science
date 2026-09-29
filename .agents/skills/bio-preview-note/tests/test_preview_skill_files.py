"""SKILL.md 형식과, 본문이 가리키는 파일이 모두 있는지 확인한다."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _preview_util import REPO, SKILL

SKILL_MD = SKILL / "SKILL.md"


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "bio-preview-note")
        self.assertIn("예습노트", m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 9)
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

    def test_claude_entry_symlink(self):
        link = REPO / ".claude" / "skills" / "bio-preview-note"
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), "../../.agents/skills/bio-preview-note")
        self.assertEqual(link.resolve(), SKILL.resolve())


    def test_run_folder_guarded_before_rm(self):
        self.assertNotIn('rm -rf "$RUN/', self.text)
        self.assertIn('rm -rf "${RUN:?}/sections" "${RUN:?}/work"', self.text)

    def test_retry_dpi_same_in_skill_and_content_rules(self):
        rules = (SKILL / "references" / "content-rules.md").read_text(encoding="utf-8")
        skill_dpi = set(re.findall(r"dpi (\d+)(?:으로 다시| PNG를)", self.text))
        rules_dpi = set(re.findall(r"dpi (\d+)(?:으로 다시| PNG를)", rules))
        self.assertEqual(skill_dpi, {"140"})
        self.assertEqual(rules_dpi, {"140"})

    def test_manifest_guide_says_topics_stay_in_one_chapter(self):
        guide = (SKILL / "references" / "manifest-guide.md").read_text(encoding="utf-8")
        self.assertIn("장 경계", guide)

    def test_content_rules_height_budget(self):
        rules = (SKILL / "references" / "content-rules.md").read_text(encoding="utf-8")
        for needle in ("높이 예산", "650px", "130px", "560×140", "<p><b>"):
            with self.subTest(needle=needle):
                self.assertIn(needle, rules)

    def test_textbook_thumbnail_snippet_finds_nfd_file(self):
        try:
            import fitz  # noqa: F401
        except ImportError:
            self.skipTest("PyMuPDF 없음")
        import fitz
        m = re.search(r"6\. 교과서 쪽을 찾는다.*?```bash\n(.*?)\n   ```", self.text, re.S)
        self.assertIsNotNone(m, "1단계 6 스니펫 없음")
        script = "\n".join(line[3:] for line in m.group(1).splitlines())
        body = script.split("<<'EOF'\n", 1)[1].rsplit("\nEOF", 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / unicodedata.normalize("NFD", "교과서") / unicodedata.normalize("NFD", "생명과학_기초와_응용_2판")
            book.mkdir(parents=True)
            doc = fitz.open()
            doc.new_page()
            doc.new_page()
            doc.save(book / unicodedata.normalize("NFD", "04장_유전.pdf"))
            run = Path(tmp) / "run"
            env = dict(os.environ, REPO=tmp, RUN=str(run), CH="04")
            r = subprocess.run([sys.executable, "-c", body], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(sorted(os.listdir(run / "work" / "textbook-pages")), ["p01.png", "p02.png"])


if __name__ == "__main__":
    unittest.main()
