import json
import tempfile
import unittest
from pathlib import Path

from test_blind_ledger import full_set
from _util import make_repo
import build
import explain_handoff


class TestExplainHandoff(unittest.TestCase):
    def test_init_records_attempt_zero_and_extracts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = make_repo(root / 'repo')
            src = full_set(repo)
            (src / 'blueprint.md').write_text('| 카드 | 정답 |\n', encoding='utf-8')
            html = build.build(src)
            controller, explain = root / 'ctl', root / 'explain'
            self.assertEqual(explain_handoff.init(repo, html, controller, explain), 0)
            retry = json.loads((controller / 'explanation-retry.json').read_text(encoding='utf-8'))
            self.assertEqual(retry['attempt'], 0)
            self.assertEqual(retry['active_explain_run'], str(explain.resolve()))
            files = retry['verified_snapshot']['files']
            self.assertIn(str(html.resolve()), files)
            self.assertTrue(any(k.endswith('pack.json') for k in files))
            self.assertTrue(any(k.endswith('_시험형_v1.html') for k in files))
            folder = next(p for p in explain.iterdir() if p.is_dir())
            self.assertTrue((folder / 'source.json').is_file())
            self.assertTrue((folder / 'evidence' / 'explanation-retry.json').is_file())
            retry['attempt'] = 1
            (controller / 'explanation-retry.json').write_text(json.dumps(retry), encoding='utf-8')
            self.assertEqual(explain_handoff.init(repo, html, controller, root / 'explain-2'), 0)
            again = json.loads((controller / 'explanation-retry.json').read_text(encoding='utf-8'))
            self.assertEqual(again['attempt'], 1, '새 RUN에서도 attempt를 이어 써야 함')

    def test_rejects_exam_presentation(self):
        with self.assertRaises(SystemExit):
            explain_handoff.snapshot(Path('/x/복습문제_9장_웹과제예상_시험형_v1.html'))


if __name__ == '__main__':
    unittest.main()
