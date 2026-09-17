import unittest
from pathlib import Path


class SummaryEntrypointTests(unittest.TestCase):
    def test_claude_delegates_to_canonical_skill(self):
        path = Path(".claude/skills/summary-note/SKILL.md")
        text = path.read_text(encoding="utf-8")
        target = "../../../.agents/skills/summary-note/SKILL.md"
        self.assertIn(target, text)
        self.assertTrue((path.parent / target).resolve().is_file())
        self.assertNotIn("§§ 3. 문항 감사", text)


if __name__ == "__main__":
    unittest.main()
