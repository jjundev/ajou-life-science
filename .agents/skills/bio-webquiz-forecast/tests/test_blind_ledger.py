import json
import tempfile
import unittest
from pathlib import Path

from _util import card_html, overview_html, make_repo, make_set
import blind
import blind_ledger
import build


def full_set(repo):
    cards = {i: overview_html(i) for i in ('o1', 'o2')}
    cards.update({f'p{i}': card_html(i, 'ABCDE'[(i - 1) % 5]) for i in range(1, 16)})
    return make_set(repo, 9, 1, cards)


def table(src, ids, override=None):
    key = json.loads((src / 'pack.json').read_text(encoding='utf-8'))['answer_key']
    override = override or {}
    lines = ['| 카드 | 고른 답 | 근거(노트 토픽) | 이의 | 최소 풀이 단계 | 수준 |', '|---|---|---|---|---|---|']
    for cid in ids:
        ans, obj = override.get(cid, (key[cid], ''))
        lines.append(f'| {cid.upper()} | {ans} | 토픽 | {obj} | 1단계 | 1 |')
    return '\n'.join(lines) + '\n'


class TestBlindLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.src = full_set(make_repo(root))
        self.html = build.build(self.src)
        self.run = root / 'run'
        self.ledger = self.run / 'blind-ledger.json'

    def tearDown(self):
        self.tmp.cleanup()

    def solve(self, ids, round_no, override=None, only=None):
        copy = self.run / f'blind-r{round_no}.md'
        args = [str(self.html), str(copy)] + (['--only', ','.join(only)] if only else [])
        self.assertEqual(blind.main(args), 0)
        answers = self.run / f'blind-answers-r{round_no}.md'
        answers.write_text(table(self.src, ids, override), encoding='utf-8')
        blind_ledger.record(self.src, answers, self.ledger, copy, round_no)

    def test_full_round_passes(self):
        ids = [f'p{i}' for i in range(1, 16)]
        self.solve(ids, 1)
        data = blind_ledger.load(self.ledger)
        self.assertEqual(blind_ledger.problems(self.src, data), [])
        self.assertEqual(blind_ledger.changed(self.src, data), [])

    def test_delta_round_merges_only_changed_cards(self):
        ids = [f'p{i}' for i in range(1, 16)]
        self.solve(ids, 1, override={'p13': ('C', '다른 보기도 답이 될 수 있음')})
        data = blind_ledger.load(self.ledger)
        self.assertTrue(any('p13: 이의' in p for p in blind_ledger.problems(self.src, data)))
        card = self.src / 'cards' / 'p13.html'
        card.write_text(card.read_text(encoding='utf-8').replace('제목 13', '고친 제목 13'), encoding='utf-8')
        data = blind_ledger.load(self.ledger)
        self.assertEqual(blind_ledger.changed(self.src, data), ['p13'])
        self.html = build.build(self.src)
        copy = self.run / 'blind-r2.md'
        blind.main([str(self.html), str(copy), '--only', 'p13'])
        self.assertIn('고친 제목 13', copy.read_text(encoding='utf-8'))
        self.assertNotIn('제목 12', copy.read_text(encoding='utf-8'))
        self.solve(['p13'], 2, only=['p13'])
        data = blind_ledger.load(self.ledger)
        self.assertEqual(blind_ledger.problems(self.src, data), [])
        self.assertEqual(data['cards']['p13']['round'], 2)
        self.assertEqual(data['cards']['p1']['round'], 1)

    def test_wrong_answer_and_stale_card_reported(self):
        ids = [f'p{i}' for i in range(1, 16)]
        self.solve(ids, 1, override={'p2': ('E', '')})
        card = self.src / 'cards' / 'p5.html'
        card.write_text(card.read_text(encoding='utf-8') + ' ', encoding='utf-8')
        found = blind_ledger.problems(self.src, blind_ledger.load(self.ledger))
        self.assertTrue(any(p.startswith('p2: 블라인드 답 E') for p in found))
        self.assertTrue(any(p.startswith('p5: 블라인드 이후 카드 변경') for p in found))

    def test_table_must_match_copy(self):
        copy = self.run / 'blind-r1.md'
        blind.main([str(self.html), str(copy), '--only', 'p1,p2'])
        answers = self.run / 'a.md'
        answers.write_text(table(self.src, ['p1']), encoding='utf-8')
        with self.assertRaises(blind_ledger.LedgerError):
            blind_ledger.record(self.src, answers, self.ledger, copy, 1)

    def test_only_rejects_unknown_card(self):
        self.assertEqual(blind.main([str(self.html), str(self.run / 'x.md'), '--only', 'p99']), 2)


if __name__ == '__main__':
    unittest.main()
