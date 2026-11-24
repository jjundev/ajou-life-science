import tempfile
import unittest
from pathlib import Path

from test_blind_ledger import full_set
from _util import card_html, make_repo
import browser_check
import build


class TestBrowserCheck(unittest.TestCase):
    def test_both_presentations_pass_and_break_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = make_repo(Path(temp))
            practice = build.build(full_set(repo))
            report = browser_check.check(practice)
            self.assertEqual(report['failures'], [])
            self.assertEqual(len(report['runs']), 8)
            exam = practice.with_name(practice.name.replace('_v', '_시험형_v'))
            exam.write_text(exam.read_text(encoding='utf-8').replace('id="submit-exam"', 'id="submit-gone"'), encoding='utf-8')
            broken = browser_check.check(practice, viewports=[(375, 812)], themes=['dark'])
            self.assertEqual(broken['status'], 'fail')
            self.assertTrue(any('시험형: 제출' in f for f in broken['failures']))
            self.assertTrue(all('practice' not in f for f in broken['failures']), broken['failures'][:3])

    def test_cli_rejects_exam_input(self):
        self.assertEqual(browser_check.main(['/x/복습문제_9장_웹과제예상_시험형_v1.html', '--out', '/tmp/x.json']), 2)

    def test_runtime_missing_exam_toc_link_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            practice = build.build(full_set(make_repo(Path(temp))))
            exam = practice.with_name(practice.name.replace('_v', '_시험형_v'))
            source = exam.read_text(encoding='utf-8')
            script = """<script>document.querySelector('.toc-list a[href="#p2"]').parentElement.remove();</script>"""
            exam.write_text(source.replace('</body>', script + '</body>', 1), encoding='utf-8')
            report = browser_check.check(practice, viewports=[(375, 812)], themes=['dark'])
            self.assertEqual(report['status'], 'fail', report['failures'])
            self.assertTrue(any('목차' in error and 'p2' in error for error in report['failures']), report['failures'])


    def test_formatted_exam_choice_stays_in_one_text_container(self):
        with tempfile.TemporaryDirectory() as temp:
            src = full_set(make_repo(Path(temp)))
            option = 'GABA<sub>A</sub>와 Na<sup>+</sup> 및 <i>Canis lupus</i> 보기'
            (src / 'cards' / 'p8.html').write_text(
                card_html(8, 'C', options=[option, '농도 $x^2$ 보기', '보기 C', '보기 D', '보기 E']),
                encoding='utf-8',
            )
            practice = build.build(src)
            exam = practice.with_name(practice.name.replace('_v', '_시험형_v'))
            markup = exam.read_text(encoding='utf-8')
            radio = '<label><input type="radio" name="p8" value="A">'
            grouped = f'{radio} <span class="exam-choice-text">A. {option}</span></label>'
            self.assertTrue(grouped in markup, '인라인 서식이 있는 시험형 보기가 한 요소에 묶여야 한다')
            self.assertTrue('<label><input type="radio" name="p8" value="C"> C. 보기 C</label>' in markup,
                            '일반 텍스트 보기의 마크업은 유지해야 한다')
            report = browser_check.check(practice, viewports=[(375, 812)], themes=['dark'])
            self.assertEqual(report['failures'], [])

            exam.write_text(markup.replace(grouped, f'{radio} A. {option}</label>'), encoding='utf-8')
            broken = browser_check.check(practice, viewports=[(375, 812)], themes=['dark'])
            self.assertEqual(broken['status'], 'fail')
            self.assertTrue(any('p8' in failure and 'A 보기' in failure for failure in broken['failures']),
                            broken['failures'])


if __name__ == '__main__':
    unittest.main()
