import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / ".agents/skills/bio-review-pack/SKILL.md"
ENTRY = ROOT / ".claude/skills/bio-review-pack"
LINK = "../../.agents/skills/bio-review-pack"


class BioReviewPackEntrypointTests(unittest.TestCase):
    def test_entry_is_symlink_to_canonical(self):
        self.assertTrue(ENTRY.is_symlink())
        self.assertEqual(os.readlink(ENTRY), LINK)
        self.assertEqual(ENTRY.resolve(), CANON.parent.resolve())

    def test_skill_file_reachable_through_entry(self):
        self.assertTrue((ENTRY / "SKILL.md").is_file())

    def test_problem_explain_entry(self):
        entry = ROOT / ".claude/skills/bio-problem-explain"
        self.assertEqual(os.readlink(entry), "../../.agents/skills/bio-problem-explain")
        self.assertTrue((entry / "SKILL.md").is_file())

    def test_old_skills_removed(self):
        for name in ("summary-note", "study-note-eli5"):
            for base in (".agents/skills", ".claude/skills"):
                with self.subTest(path=f"{base}/{name}"):
                    self.assertFalse((ROOT / base / name).exists())


if __name__ == "__main__":
    unittest.main()
