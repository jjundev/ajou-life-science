import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILL = ROOT / ".claude/skills/study-note-eli5/SKILL.md"
CANONICAL_SKILL = ROOT / ".agents/skills/study-note-eli5/SKILL.md"


class ClaudeStudyNoteEli5Tests(unittest.TestCase):
    def test_claude_entrypoint_uses_shared_canonical_skill(self):
        text = CLAUDE_SKILL.read_text(encoding="utf-8")
        self.assertTrue(CANONICAL_SKILL.is_file())
        self.assertIn(
            "../../../.agents/skills/study-note-eli5/SKILL.md",
            text,
        )
        self.assertIn(
            "../../../.agents/skills/study-note-eli5/references/coverage-contract.md",
            text,
        )

    def test_claude_frontmatter_is_discoverable(self):
        text = CLAUDE_SKILL.read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", text, re.S)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertIn("name: study-note-eli5", frontmatter)
        self.assertRegex(frontmatter, r'description:\s*["\']?Use when')
        canonical = CANONICAL_SKILL.read_text(encoding="utf-8")
        canonical_frontmatter = re.match(r"---\n(.*?)\n---", canonical, re.S)
        self.assertIsNotNone(canonical_frontmatter)
        self.assertRegex(
            canonical_frontmatter.group(1),
            r'description:\s*["\']?Use when',
        )


if __name__ == "__main__":
    unittest.main()
