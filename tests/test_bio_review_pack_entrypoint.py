import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / ".agents/skills/bio-review-pack/SKILL.md"
ENTRY = ROOT / ".claude/skills/bio-review-pack/SKILL.md"
TARGET = "../../../.agents/skills/bio-review-pack/SKILL.md"


def frontmatter(text):
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
    return m.groups() if m else None


class BioReviewPackEntrypointTests(unittest.TestCase):
    def test_entry_has_same_frontmatter_as_canonical(self):
        entry = frontmatter(ENTRY.read_text(encoding="utf-8"))
        self.assertIsNotNone(entry)
        self.assertEqual(entry, frontmatter(CANON.read_text(encoding="utf-8")))

    def test_entry_points_to_canonical(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertIn(TARGET, text)
        self.assertEqual((ENTRY.parent / TARGET).resolve(), CANON.resolve())

    def test_entry_does_not_duplicate_procedure(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 20)
        self.assertNotRegex(text, r"\n### \d\. ")

    def test_rules_point_to_new_skill_only(self):
        rules = (ROOT / "정리노트/CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/bio-review-pack/SKILL.md", rules)
        self.assertNotIn(".agents/skills/summary-note/SKILL.md", rules)
        self.assertNotIn(".agents/skills/study-note-eli5/SKILL.md", rules)

    def test_old_skills_removed(self):
        for name in ("summary-note", "study-note-eli5"):
            for base in (".agents/skills", ".claude/skills"):
                with self.subTest(path=f"{base}/{name}"):
                    self.assertFalse((ROOT / base / name).exists())


if __name__ == "__main__":
    unittest.main()
