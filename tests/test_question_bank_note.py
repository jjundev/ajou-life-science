import copy
import json
from pathlib import Path
import tempfile
import unittest

from tests.question_bank_fixture import make_bank
from scripts.question_bank.model import canonical_digest, question_payload
from scripts.question_bank.note import export_note_items, render_note, script_json

ROOT = Path(__file__).resolve().parents[1]


class NoteExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        _, self.bank = make_bank(base)
        q = self.bank['questions'][0]
        q['review'] = {'status': 'verified', 'notes': 'synthetic fixture only',
                       'payload_sha256': canonical_digest(question_payload(self.bank, q, base, repo_root=base))}
        self.entries = [{'id': q['id'], 'status': 'included', 'reason': '이번 범위',
                         'prerequisite': None, 'refs': [{'path': 'evidence.md', 'section': 'DNA'}]}]

    def test_option_conversion_does_not_use_capture(self):
        original = copy.deepcopy(self.bank)
        item = export_note_items(self.bank, self.entries)[0]
        self.assertEqual(item['answer'], 0)
        self.assertEqual(item['qid'], self.entries[0]['id'])
        self.assertEqual(item['optionIds'], ['A', 'B'])
        self.assertEqual(len(item['diagnostics']), 2)
        self.assertNotIn('observations', item)
        self.assertNotIn('selected_option_id', json.dumps(item))
        self.assertIn('분석 기준', item['answerLabel'])
        self.assertEqual(self.bank, original)

    def test_active_subset_and_also_accept(self):
        q = self.bank['questions'][0]
        q['analysis']['also_accept'] = ['B']
        q['analysis']['grading'] = 'ambiguous'
        q['analysis']['issues'] = [{'description': '해석 주의'}]
        q['analysis']['option_diagnostics']['B']['is_answer'] = True
        item = export_note_items(self.bank, self.entries)[0]
        self.assertEqual(item['also_accept'], [1])
        self.assertEqual(item['trap'], {})
        self.assertIn('해석 주의', item['keyNote'])
        self.entries[0]['status'] = 'review'
        self.assertEqual(len(export_note_items(self.bank, self.entries)), 1)
        self.entries[0]['status'] = 'deferred'
        self.assertEqual(export_note_items(self.bank, self.entries), [])

    def test_rejects_pending_unresolved_duplicate_and_unknown(self):
        for field, value in [('review', {'status': 'pending'}),
                             ('analysis', {'answer_status': 'unresolved'})]:
            bank = copy.deepcopy(self.bank)
            bank['questions'][0][field] = value
            with self.assertRaises(ValueError):
                export_note_items(bank, self.entries)
        with self.assertRaises(ValueError):
            export_note_items(self.bank, self.entries * 2)
        self.entries[0]['id'] = 'unknown:q01'
        with self.assertRaises(ValueError):
            export_note_items(self.bank, self.entries)

    def test_preserves_content_order_and_canonical_figure_ids(self):
        self.bank['questions'][0]['original']['content'] = [
            {'type': 'figure', 'asset_id': 'q09'},
            {'type': 'text', 'text': 'Question'},
            {'type': 'statements', 'items': [{'id': 'a', 'text': 'Condition'}]}]
        item = export_note_items(self.bank, self.entries)[0]
        self.assertEqual([b['type'] for b in item['content']], ['figure', 'text', 'statements'])
        self.assertEqual(item['content'][0]['figureId'], 'figure-web-test-ch01-q09-exam')
        self.assertEqual(item['explainedFigureIds'], ['figure-web-test-ch01-q09-explained'])


class NoteRenderTests(unittest.TestCase):
    def test_script_safe_round_trip_and_templates_precede_engine(self):
        template = (ROOT / '정리노트/_template.html').read_text()
        value = {'q': '</script><script>&\u2028\u2029'}
        result = render_note(template, {'date': '0999'}, [value], figures='<template id="figure-test"></template>')
        self.assertEqual(json.loads(script_json(value)), value)
        self.assertNotIn(value['q'], result)
        self.assertLess(result.index('<template id="figure-test">'), result.rfind('<script>', 0, result.index('QUESTION-DATA-START')))
        self.assertIn('const META = {"date": "0999"};', result)
        self.assertEqual(result.count('QUESTION-DATA-START'), 1)

    def test_missing_or_duplicate_marker_fails(self):
        for template in ['<script></script>', '/* QUESTION-DATA-START */' * 2 + '/* QUESTION-DATA-END */']:
            with self.assertRaises(ValueError):
                render_note(template, {}, [])
