import copy
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote

from tests.question_bank_fixture import make_bank
from scripts.question_bank.render import figure_templates, render_preview


ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.elements = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs, self.stack.copy()))
        if tag not in {'meta', 'br', 'hr', 'img', 'input', 'link'}:
            self.stack.append((tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, dict(attrs), self.stack.copy()))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        self.text.append((text, self.stack.copy()))


def add_figure(base, bank):
    (base / 'image').mkdir(exist_ok=True)
    for variant in ('exam', 'explained'):
        path = base / 'image' / (variant + '.svg')
        path.write_text('<svg viewBox="0 0 10 10" aria-labelledby="title"><title id="title">'
                        + variant + '</title><text x="1" y="5">H</text></svg>')
    bank['assets'] = [{
        'id': 'q01', 'source_ids': ['s1'],
        'review': {'status': 'pending', 'payload_sha256': None, 'notes': None},
        **{variant: {'path': 'image/' + variant + '.svg', 'alt': variant + ' ALT',
                     'sha256': hashlib.sha256((base / 'image' / (variant + '.svg')).read_bytes()).hexdigest()}
           for variant in ('exam', 'explained')},
    }]
    bank['questions'][0]['original']['content'].insert(0, {'type': 'figure', 'asset_id': 'q01'})


class PreviewTests(unittest.TestCase):
    def test_original_order_and_closed_observation_solution_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            q = bank['questions'][0]
            q['original']['content'].append({'type': 'statements', 'items': [{'id': 'a', 'text': 'first'}, {'id': 'b', 'text': 'second'}]})
            html = render_preview(bank, base)
            doc = Document(html)
            self.assertIn('data-question-id="web-test-ch01:q01"', html)
            self.assertLess(html.index('first'), html.index('second'))
            self.assertLess(html.index('second'), html.index('data-option-id="A"'))
            self.assertLess(html.index('data-option-id="A"'), html.index('data-option-id="B"'))
            details = [a for t, a, _ in doc.elements if t == 'details']
            self.assertEqual([a.get('data-role') for a in details], ['observations', 'solution'])
            self.assertTrue(all('open' not in a for a in details))
            for needle, role in [('캡처 선택: B', 'observations'), ('DNA가 유전 정보를 저장한다.', 'solution'), ('유전 정보 저장에 해당한다.', 'solution')]:
                matched = [parents for text, parents in doc.text if needle in text]
                self.assertTrue(matched, needle)
                self.assertTrue(all(any(t == 'details' and a.get('data-role') == role for t, a in p) for p in matched))
            self.assertFalse(any(t in {'script', 'input', 'iframe'} for t, _, _ in doc.elements))
            self.assertNotIn('fetch(', html)
            self.assertNotIn('checked', html)
            self.assertIn('미검토', html)
            self.assertIn('복원', html)
            self.assertIn('공식 답: 확인되지 않음', html)
            self.assertIn('분석 기준', html)

    def test_all_dynamic_text_and_paths_are_safe_and_links_follow_output_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            attack = '<img src=x onerror=alert(1)> & "text"'
            q = bank['questions'][0]
            bank['assessment']['title'] = attack
            q['original']['content'][0]['text'] = attack
            q['original']['content'].append({'type': 'statements', 'items': [{'id': attack, 'text': attack}]})
            q['original']['options'][0]['text'] = attack
            q['analysis']['reason'] = attack
            q['analysis']['issues'] = [{'kind': 'wording', 'description': attack, 'source_ids': ['s1']}]
            q['analysis']['requirements'][0]['statement'] = attack
            q['analysis']['requirements'][0]['evidence'][0]['quote'] = attack
            q['review']['notes'] = attack
            source = base / 'raw' / 'a #"<사진>.txt'
            source.write_text('raw')
            bank['sources'][0]['path'] = 'raw/' + source.name
            output_dir = base / 'output'
            html = render_preview(bank, base, output_dir=output_dir, repo_root=base)
            doc = Document(html)
            self.assertFalse(any(t == 'img' or any(k.startswith('on') for k in a) for t, a, _ in doc.elements))
            self.assertIn('&lt;img', html)
            hrefs = [a['href'] for t, a, _ in doc.elements if t == 'a']
            self.assertTrue(any((output_dir / unquote(href)).resolve() == source.resolve() for href in hrefs))
            self.assertTrue(all(not href.startswith(('http:', 'https:', 'javascript:')) for href in hrefs))

    def test_figures_are_accessible_unique_and_explanations_only_inside_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            add_figure(base, bank)
            # A repeated asset must still have unique document IDs.
            bank['questions'][0]['original']['content'].append({'type': 'figure', 'asset_id': 'q01'})
            doc = Document(render_preview(bank, base))
            ids = [a['id'] for _, a, _ in doc.elements if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs, parents in doc.elements:
                if tag == 'svg':
                    inside_solution = any(t == 'details' and a.get('data-role') == 'solution' for t, a in parents)
                    self.assertEqual(inside_solution, attrs['aria-label'] == 'explained ALT')
            first = Document(figure_templates(bank, base))
            second_bank = copy.deepcopy(bank)
            second_bank['assessment']['id'] = 'web-other-ch01'
            second = Document(figure_templates(second_bank, base))
            first_ids = {a['id'] for _, a, _ in first.elements if 'id' in a}
            second_ids = {a['id'] for _, a, _ in second.elements if 'id' in a}
            self.assertFalse(first_ids & second_ids)
            self.assertIn('figure-web-test-ch01-q01-exam', first_ids)
            self.assertIn('figure-web-test-ch01-q01-explained', first_ids)
            self.assertEqual(len([1 for t, _, _ in first.elements if t == 'template']), 2)

    def test_unresolved_and_ambiguous_analysis_keep_their_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, bank = make_bank(Path(tmp))
            analysis = bank['questions'][0]['analysis']
            analysis.update(answer_option_id=None, answer_status='unresolved', grading='unresolved')
            html = render_preview(bank, Path(tmp))
            self.assertIn('미확정', html)
            analysis.update(answer_option_id='A', answer_status='reasoned', grading='ambiguous', also_accept=['B'])
            html = render_preview(bank, Path(tmp))
            self.assertIn('모호', html)
            self.assertIn('추가 허용: B', html)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.bank_path, self.bank = make_bank(self.base)
        self.bank['questions'][0]['analysis']['requirements'][0]['evidence'][0]['path'] = 'tests/question_bank_fixture.py'
        self.save()

    def save(self):
        self.bank_path.write_text(json.dumps(self.bank, ensure_ascii=False), encoding='utf-8')

    def cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'scripts.question_bank', *map(str, args)], cwd=ROOT, capture_output=True, text=True)

    def test_validate_draft_complete_and_cli_argument_exit_codes(self):
        self.assertEqual(self.cli('validate', self.bank_path).returncode, 0)
        result = self.cli('validate', self.bank_path, '--complete')
        self.assertEqual(result.returncode, 1)
        self.assertIn('verified', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.cli('preview', self.bank_path).returncode, 2)

    def test_preview_preserves_identical_file_and_requires_force_for_changes(self):
        output = self.base / 'preview.html'
        self.assertEqual(self.cli('preview', self.bank_path, '--output', output).returncode, 0)
        os.utime(output, ns=(1_000_000_000, 1_000_000_000))
        self.assertEqual(self.cli('preview', self.bank_path, '--output', output).returncode, 0)
        self.assertEqual(output.stat().st_mtime_ns, 1_000_000_000)
        output.write_text('user text')
        self.assertEqual(self.cli('preview', self.bank_path, '--output', output).returncode, 1)
        self.assertEqual(output.read_text(), 'user text')
        self.assertEqual(self.cli('preview', self.bank_path, '--output', output, '--force').returncode, 0)
        self.assertIn('data-question-id=', output.read_text())

    def test_input_and_referenced_sources_are_protected_even_with_force_and_aliases(self):
        alias = self.base / 'alias.html'
        alias.symlink_to(self.bank_path)
        hardlink = self.base / 'hardlink.html'
        os.link(self.bank_path, hardlink)
        for output in (self.bank_path, alias, hardlink, self.base / 'raw/fixture.txt'):
            with self.subTest(output=output):
                before = output.read_bytes()
                result = self.cli('preview', self.bank_path, '--output', output, '--force')
                self.assertEqual(result.returncode, 1)
                self.assertEqual(output.read_bytes(), before)

    def test_invalid_banks_never_create_output_or_print_traceback(self):
        output = self.base / 'preview.html'
        for content in (b'{', b'[]', b'\xff', b'{"schema_version":1}'):
            self.bank_path.write_bytes(content)
            result = self.cli('preview', self.bank_path, '--output', output)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn('Traceback', result.stderr)
            self.assertTrue(result.stderr)
            self.assertFalse(output.exists())
        self.bank['questions'][0]['source_ids'] = ['missing']
        self.save()
        self.assertEqual(self.cli('preview', self.bank_path, '--output', output).returncode, 1)
        self.assertFalse(output.exists())
