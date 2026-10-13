import re
import unittest

from _util import SKILL


class TestSkillFiles(unittest.TestCase):
    def setUp(self):
        self.md = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.md)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "bio-webquiz-forecast")
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"`((?:references|scripts)/[\w.-]+)`", self.md))
        refs |= set(re.findall(r"\$SKILL/((?:references|scripts)/[\w.-]+)", self.md))
        self.assertGreaterEqual(len(refs), 8)
        for r in sorted(refs):
            self.assertTrue((SKILL / r).exists(), r)

    def test_briefs_point_to_existing_files(self):
        for name in ("card-brief.md", "blind-brief.md"):
            text = (SKILL / "references" / name).read_text(encoding="utf-8")
            for r in re.findall(r"\{SKILL\}/((?:references|scripts)/[\w.-]+)", text):
                self.assertTrue((SKILL / r).exists(), f"{name}: {r}")

    def test_claude_symlink(self):
        link = SKILL.parents[2] / ".claude" / "skills" / "bio-webquiz-forecast"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), SKILL.resolve())


    def test_card_writers_do_not_build(self):
        brief = (SKILL / "references" / "card-brief.md").read_text(encoding="utf-8")
        self.assertNotIn("scripts/build.py", brief)
        self.assertNotIn("scripts/check.py", brief)

    def test_blind_loop_is_capped(self):
        step7 = self.md.split("### 7.")[1].split("### 8.")[0]
        self.assertIn("최대 2회", step7)

    def test_pool_saved_without_shell_redirect(self):
        step2 = self.md.split("### 2.")[1].split("### 3.")[0]
        self.assertIn("--out", step2)
        self.assertNotIn('> "$RUN', step2)

    def test_card_brief_overrides_review_pack_markup(self):
        brief = (SKILL / "references" / "card-brief.md").read_text(encoding="utf-8")
        self.assertIn("이 브리프가 우선", brief)

if __name__ == "__main__":
    unittest.main()


def test_explanation_handoff_is_required_before_report():
    text = (SKILL/'SKILL.md').read_text()
    assert '### 9. 예상문제해설 생성' in text
    step = text.split('### 9.')[1].split('### 10.')[0]
    assert 'bio-problem-explain' in step and '명시' in step and 'lite' in step
    assert (SKILL/'references/explanation-handoff.md').is_file()
    assert '문제해설_' in text.split('### 10.')[1]


def test_explanation_retry_contract():
    path = SKILL/'references/explanation-handoff.md'
    assert path.is_file()
    text = path.read_text()
    for phrase in ('최대 2회', '6–8단계', '새 RUN', '초기화하지', '부분 완료', 'attempt=0', 'source_visual', 'independent', 'references', 'lite'):
        assert phrase in text, phrase
