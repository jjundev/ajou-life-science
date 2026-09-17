"""Chapter-specific preservation checks, including deliberate corrupted copies."""
import copy
import hashlib
import struct
import unittest
import unicodedata
from pathlib import Path

from scripts.question_bank.model import load_bank, validate_bank

ROOT = Path(__file__).resolve().parents[1]
BASE = next(p for p in (ROOT / '웹과제').iterdir()
            if unicodedata.normalize('NFC', p.name) == '1장')


def assert_chapter_contract(test, bank):
    questions = bank['questions']
    test.assertEqual([q['number'] for q in questions], list(range(1, 18)))
    test.assertEqual(len(bank['sources']), 19)
    test.assertEqual(sum(len(q['original']['options']) for q in questions), 82)
    test.assertEqual([q['number'] for q in questions if len(q['original']['options']) == 4], [6, 12, 15])
    test.assertTrue(all(q['observations']['official_answer'] is None for q in questions))
    test.assertEqual(len(bank['assets']), 2)
    statements = [b for b in questions[5]['original']['content'] if b['type'] == 'statements']
    test.assertEqual(len(statements), 1)
    test.assertEqual([s['id'] for s in statements[0]['items']], list('abcd'))
    for number, sources in [(9, ['s09', 's10']), (14, ['s15', 's16'])]:
        q = questions[number - 1]
        test.assertEqual(q['source_ids'], sources)
        test.assertEqual([b['asset_id'] for b in q['original']['content'] if b['type'] == 'figure'], [f'q{number:02}'])


class ChapterOneTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((BASE / 'questions.json').is_file(), 'chapter one bank is missing')
        self.bank = load_bank(BASE / 'questions.json', complete=True)

    def test_all_original_questions_and_options(self):
        assert_chapter_contract(self, self.bank)
        for q in self.bank['questions']:
            self.assertEqual(q['points'], 1)
            self.assertEqual([o['id'] for o in q['original']['options']], list('ABCDE')[:len(q['original']['options'])])
            self.assertEqual(q['observations']['phase'], 'pre_submission')

    def test_manifest_matches_png_bytes_dimensions_and_filename_order(self):
        paths = sorted((BASE / 'raw').glob('*.png'))
        self.assertEqual([s['path'] for s in self.bank['sources']], ['raw/' + p.name for p in paths])
        self.assertEqual([s['id'] for s in self.bank['sources']], [f's{i:02}' for i in range(1, 20)])
        for source in self.bank['sources']:
            data = (BASE / source['path']).read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual((source['width'], source['height']), struct.unpack('>II', data[16:24]))
            self.assertEqual(source['sha256'], hashlib.sha256(data).hexdigest())

    def test_observed_selections_stay_separate_from_reasoned_answers(self):
        self.assertEqual([q['observations']['selected_option_id'] for q in self.bank['questions']], list('AABBEBBDDEECDBCBE'))
        self.assertEqual([q['analysis']['answer_option_id'] for q in self.bank['questions']], list('AE BCEBBDCEE CDBCBD'.replace(' ', '')))
        for number in [4, 16]:
            self.assertTrue(any(i['kind'] == 'wording' for i in self.bank['questions'][number - 1]['analysis']['issues']))

    def test_corrupted_chapter_copies_are_rejected(self):
        mutations = [
            lambda b: b['questions'].pop(),
            lambda b: b['questions'][8]['original']['content'].pop(),
            lambda b: b['questions'][5]['original']['content'][1]['items'].pop(),
            lambda b: b['questions'][0]['observations'].update(official_answer={'option_ids': ['A'], 'source_ids': ['s01']}),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                broken = copy.deepcopy(self.bank)
                mutate(broken)
                with self.assertRaises(AssertionError):
                    assert_chapter_contract(self, broken)
                self.assertTrue(validate_bank(broken, BASE, complete=True))

    def test_each_diagnostic_has_audited_evidence(self):
        for q in self.bank['questions']:
            requirements = {r['id']: r for r in q['analysis']['requirements']}
            self.assertEqual(set(q['analysis']['option_diagnostics']), {o['id'] for o in q['original']['options']})
            for diagnostic in q['analysis']['option_diagnostics'].values():
                self.assertTrue(diagnostic['requirement_ids'])
                for rid in diagnostic['requirement_ids']:
                    for evidence in requirements[rid]['evidence']:
                        path = ROOT / evidence['path']
                        if path.suffix == '.md':
                            self.assertIn(evidence['quote'], path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
