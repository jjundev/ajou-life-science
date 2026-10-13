import json
import tempfile
import unittest
from pathlib import Path
from _util import REPO
import collect_solves as cs


def make(tmp, name, document_id='복습문제_0929_Heredity.html', range_='0929', schema=1):
    (tmp / name).write_text(json.dumps(dict(schema=schema, documentId=document_id, range=range_)), encoding='utf-8')


class TestCollect(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.down = self.tmp / 'Downloads'
        self.root = self.tmp / '복습노트'
        self.down.mkdir()
        (self.root / '0929').mkdir(parents=True)
        (self.root / '0929' / '복습문제_0929_Heredity.html').write_text('x', encoding='utf-8')

    def test_moves_json_into_date_folder(self):
        name = '복습문제_0929_Heredity_풀이기록_20261001-1200.json'
        make(self.down, name)
        result = cs.collect(self.down, self.root)
        self.assertEqual([r[2] for r in result], ['moved'])
        self.assertTrue((self.root / '0929' / '.assets' / '풀이기록' / name).exists())
        self.assertFalse((self.down / name).exists())

    def test_handles_browser_duplicate_suffix(self):
        name = '복습문제_0929_Heredity_풀이기록_20261001-1200 (1).json'
        make(self.down, name)
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root)], ['moved'])
        self.assertTrue((self.root / '0929' / '.assets' / '풀이기록' / name).exists())

    def test_ignores_unrelated_and_foreign_files(self):
        (self.down / 'notes.json').write_text('{}', encoding='utf-8')
        make(self.down, 'a_풀이기록_20261001-1200.json', schema=2)
        (self.down / 'b_풀이기록_20261001-1200.json').write_text('{', encoding='utf-8')
        result = cs.collect(self.down, self.root)
        self.assertEqual({r[2] for r in result}, {'skipped'})
        self.assertTrue((self.down / 'notes.json').exists())
        self.assertTrue((self.down / 'a_풀이기록_20261001-1200.json').exists())

    def test_unknown_document_is_left_alone(self):
        name = '복습문제_1231_None_풀이기록_20261001-1200.json'
        make(self.down, name, document_id='복습문제_1231_None.html', range_='1231')
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root)], ['skipped'])
        self.assertTrue((self.down / name).exists())

    def test_existing_target_is_not_overwritten(self):
        name = '복습문제_0929_Heredity_풀이기록_20261001-1200.json'
        make(self.down, name)
        out = self.root / '0929' / '.assets' / '풀이기록'
        out.mkdir(parents=True)
        (out / name).write_text('old', encoding='utf-8')
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root)], ['skipped'])
        self.assertEqual((out / name).read_text(encoding='utf-8'), 'old')
        self.assertTrue((self.down / name).exists())

    def test_ambiguous_document_prefers_matching_range_folder(self):
        extra = self.root / '2장_3장_모음'
        extra.mkdir()
        (extra / '복습문제_0929_Heredity.html').write_text('x', encoding='utf-8')
        name = '복습문제_0929_Heredity_풀이기록_20261001-1200.json'
        make(self.down, name)
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root)], ['moved'])
        self.assertTrue((self.root / '0929' / '.assets' / '풀이기록' / name).exists())

    def test_dry_run_moves_nothing(self):
        name = '복습문제_0929_Heredity_풀이기록_20261001-1200.json'
        make(self.down, name)
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root, dry_run=True)], ['would-move'])
        self.assertTrue((self.down / name).exists())
        self.assertFalse((self.root / '0929' / '.assets' / '풀이기록').exists())

    def test_moves_json_into_range_folder_assets(self):
        rng = self.root / '0922-0924'
        rng.mkdir()
        (rng / '복습문제_0922-0924_X.html').write_text('x', encoding='utf-8')
        name = '복습문제_0922-0924_X_풀이기록_20261001-1200.json'
        make(self.down, name, document_id='복습문제_0922-0924_X.html', range_='0922-0924')
        self.assertEqual([r[2] for r in cs.collect(self.down, self.root)], ['moved'])
        self.assertTrue((rng / '.assets' / '풀이기록' / name).is_file())
        self.assertFalse((rng / '풀이기록').exists())

    def test_missing_downloads_folder(self):
        self.assertEqual(cs.collect(self.tmp / 'nope', self.root), [])
