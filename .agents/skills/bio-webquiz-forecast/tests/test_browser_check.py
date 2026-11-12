import tempfile
import unittest
from pathlib import Path

from test_blind_ledger import full_set
from _util import make_repo
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


if __name__ == '__main__':
    unittest.main()
