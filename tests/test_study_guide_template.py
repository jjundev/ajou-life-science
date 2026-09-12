import tempfile
import unittest
from pathlib import Path

from study_guide_fixture import ROOT, case
from guide_html import validate_html

class TemplateTests(unittest.TestCase):
    def test_template_teaches_before_asking(self):
        html = (ROOT / ".agents/skills/study-note-eli5/assets/base-template.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(validate_html(html, case(Path(directory))), [])
        for marker in ('id="study-map"', 'id="study-routine"', 'id="scope-boundary"'):
            self.assertIn(marker, html)
        self.assertLess(html.index('id="fact-balance"'), html.index('data-question-id="2강:6"'))
        self.assertIn("beforeprint", html)
        self.assertIn("afterprint", html)

    def test_template_demonstrates_v2_answerability_contract(self):
        html = (ROOT / ".agents/skills/study-note-eli5/assets/base-template.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            for fact in data["inventory"]["facts"]:
                fact["kind"] = "definition"
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "option_count": 2,
                "requirements": ["f2"],
                "grading": "single",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {
                        "1": "평형과 속도를 혼동한 선택",
                        "2": "활성화에너지 감소",
                    },
                },
            })
            self.assertEqual(validate_html(html, data), [])
