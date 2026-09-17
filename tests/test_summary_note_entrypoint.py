import unittest
from pathlib import Path


class SummaryEntrypointTests(unittest.TestCase):
    def assert_thin_entrypoint(self, text):
        target = "../../../.agents/skills/summary-note/SKILL.md"
        self.assertIn(target, text)
        self.assertNotIn("## 3. 문항 감사", text)

    def test_claude_delegates_to_canonical_skill(self):
        path = Path(".claude/skills/summary-note/SKILL.md")
        text = path.read_text(encoding="utf-8")
        target = "../../../.agents/skills/summary-note/SKILL.md"
        self.assert_thin_entrypoint(text)
        self.assertTrue((path.parent / target).resolve().is_file())

    def test_old_procedure_cannot_be_appended_to_entrypoint(self):
        text = Path(".claude/skills/summary-note/SKILL.md").read_text(encoding="utf-8")
        restored_duplicate = text + "\n## 3. 문항 감사\n중복 절차\n"
        with self.assertRaises(AssertionError):
            self.assert_thin_entrypoint(restored_duplicate)

    def test_canonical_workflow_keeps_chapter_bank_session_scoped(self):
        text = Path(".agents/skills/summary-note/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("각 요청 MMDD", text)
        self.assertIn("assessment date", text)
        self.assertIn("## 3.", text)

    def test_explicit_legacy_update_uses_current_template_contract(self):
        skill = Path(".agents/skills/summary-note/SKILL.md").read_text(
            encoding="utf-8"
        )
        rules = Path("정리노트/CLAUDE.md").read_text(encoding="utf-8")

        for text in (skill, rules):
            self.assertIn("read compatibility", text)
            self.assertIn("current template", text)
            self.assertIn("strict JSON", text)


if __name__ == "__main__":
    unittest.main()
