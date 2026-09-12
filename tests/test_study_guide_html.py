import tempfile
import unittest
from pathlib import Path

from study_guide_fixture import HTML, case
from guide_html import partial_delivery_errors, validate_html


class HtmlTests(unittest.TestCase):
    def test_valid_links(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(validate_html(HTML, case(Path(directory))), [])

    def test_fact_id_in_answer_is_not_teaching(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            html = HTML.replace('id="fact-barrier"', 'id="other"').replace('data-part="answer"', 'data-part="answer" id="fact-barrier"')
            self.assertIn("fact target is not visible teaching: f1/fact-barrier", validate_html(html, data))

    def test_empty_explanation_and_duplicate_question_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            self.assertTrue(validate_html(HTML.replace("효소는 활성화에너지를 낮춥니다.", ""), data))
            duplicate = HTML.replace("</body>", '<article data-question-id="2강:6"></article></body>')
            self.assertIn("duplicate question: 2강:6", validate_html(duplicate, data))

    def test_generated_recall_is_not_an_original_question(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(validate_html(HTML.replace('data-role="recall"', 'data-role="recall" data-question-id="2강:99"'), case(Path(directory))))

    def test_model_answer_must_be_inside_details(self):
        with tempfile.TemporaryDirectory() as directory:
            html = HTML.replace('<details><summary>설명 확인</summary><p data-part="model-answer">', '<p data-part="model-answer">').replace('</p></details></div>', '</p></div>')
            self.assertIn("model answer not hidden: enzyme", validate_html(html, case(Path(directory))))

    def test_v2_question_requires_answerability_from_teaching(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            question = data["inventory"]["questions"][0]
            question.update({
                "format": "multiple_choice",
                "requirements": ["f2"],
                "grading": "single",
                "answerability": {
                    "teaching_target_ids": [],
                    "option_diagnostics": {"1": "평형과 속도를 혼동"},
                },
            })
            errors = validate_html(HTML, data)
            self.assertIn("question not answerable from teaching: 2강:6/f2", errors)

    def test_short_answer_cannot_silently_become_multiple_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            question = data["inventory"]["questions"][0]
            question.update({
                "format": "short_answer",
                "requirements": ["f2"],
                "grading": "rubric",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "rubric": ["평형은 바뀌지 않는다"],
                },
            })
            changed = HTML.replace(
                'data-question-id="2강:6"',
                'data-question-id="2강:6" data-format="multiple_choice"',
            )
            self.assertIn("question format mismatch: 2강:6", validate_html(changed, data))

    def test_ambiguous_question_requires_visible_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "requirements": ["f2"],
                "grading": "ambiguous",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "인쇄 답", "2": "대안도 성립"},
                },
            })
            self.assertIn(
                "ambiguous question missing disclosed conflict: 2강:6",
                validate_html(HTML, data),
            )

    def test_diagram_question_requires_figure_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "requirements": ["f2"],
                "grading": "single", "diagram_required": True,
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "활성부위"},
                },
            })
            self.assertIn(
                "question missing figure evidence: 2강:6",
                validate_html(HTML, data),
            )

    def test_multiple_choice_diagnoses_every_original_option(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "option_count": 5,
                "requirements": ["f2"], "grading": "single",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "첫 보기만 진단"},
                },
            })
            errors = validate_html(HTML, data)
            self.assertIn("option diagnostics count mismatch: 2강:6", errors)
            data["inventory"]["questions"][0]["option_count"] = 2
            data["inventory"]["questions"][0]["answerability"]["option_diagnostics"] = {
                "1": "첫 보기", "9": "존재하지 않는 보기",
            }
            self.assertIn(
                "option diagnostic keys mismatch: 2강:6",
                validate_html(HTML, data),
            )

    def test_figure_evidence_must_be_visible_teaching_content(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["schema_version"] = 2
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "option_count": 1,
                "requirements": ["f2"], "grading": "single",
                "diagram_required": True,
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "활성부위"},
                    "figure_target_ids": ["solution-figure"],
                },
            })
            html = HTML.replace(
                '<details data-role="solution">',
                '<details data-role="solution"><p id="solution-figure">그림</p>',
            )
            self.assertIn(
                "figure evidence is not visible teaching: 2강:6/solution-figure",
                validate_html(html, data),
            )

    def test_partial_delivery_names_every_omitted_question_visibly(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            data["delivery_mode"] = "partial"
            scope = {
                "2강:6": {"id": "2강:6", "status": "included"},
                "2강:7": {"id": "2강:7", "status": "included"},
            }
            self.assertIn(
                "partial banner missing",
                partial_delivery_errors(HTML, data, scope),
            )
            marked = HTML.replace(
                "<body>",
                '<body><aside data-role="partial-banner">PARTIAL 시범본</aside>'
                '<p data-role="omitted-questions">누락: 2강:7</p>',
            )
            self.assertEqual(partial_delivery_errors(marked, data, scope), [])
