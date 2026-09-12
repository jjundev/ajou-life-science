import unittest

from study_guide_fixture import HTML
from make_blind_copy import strip_solutions


class BlindCopyTests(unittest.TestCase):
    def test_removes_answers_but_keeps_teaching_and_prompt(self):
        blind, removed, errors = strip_solutions(HTML)
        self.assertEqual((removed, errors), (1, []))
        self.assertNotIn('data-part="answer"', blind)
        self.assertNotIn('data-role="solution"', blind)
        self.assertIn('id="fact-balance"', blind)
        self.assertIn('data-part="prompt"', blind)
        self.assertIn('data-part="model-answer"', blind)  # generated recall stays for the learner

    def test_nested_details_inside_a_solution_are_removed_whole(self):
        html = ('<p data-part="prompt">문제</p><details data-role="solution"><summary>정답</summary>'
                '<details><summary>더 보기</summary>예시</details><p data-part="reason">근거</p></details>'
                '<p id="after">다음 설명</p>')
        blind, removed, errors = strip_solutions(html)
        self.assertEqual((removed, errors), (1, []))
        self.assertNotIn("근거", blind)
        self.assertIn('id="after"', blind)

    def test_answer_outside_a_solution_is_reported(self):
        _, _, errors = strip_solutions('<p data-part="answer">정답</p>')
        self.assertEqual(errors, ['answer content outside a solution block: data-part="answer"'])


if __name__ == "__main__":
    unittest.main()
