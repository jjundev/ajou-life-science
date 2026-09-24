import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.question_bank_fixture import make_bank
from scripts.question_bank.model import canonical_digest, question_payload
from scripts import new_note_test
from scripts.question_bank.__main__ import main as bank_cli

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def fixture(root, complete=True):
    path, bank = make_bank(root / 'bank')
    (root / 'evidence.md').write_text('# DNA\nDNA는 유전 정보를 저장한다.\n')
    q = bank['questions'][0]
    if complete:
        q['review'] = {'status': 'verified', 'notes': 'fixture only',
                       'payload_sha256': canonical_digest(question_payload(bank, q, path.parent, repo_root=root))}
    write_json(path, bank)
    scope = root / 'meta/scope.json'
    manifest = {'schema_version': 1, 'banks': [{'path': '../bank/questions.json',
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'questions': [{'id': q['id'], 'status': 'included', 'reason': None,
            'prerequisite': None, 'refs': [{'path': 'evidence.md', 'section': 'DNA'}]}]}]}
    write_json(scope, manifest)
    return path, bank, scope, manifest


class WebScopeTests(unittest.TestCase):
    def load(self, scope, root):
        from scripts.question_bank.scope import load_web_scope
        return load_web_scope(scope, root)

    def test_manifest_cannot_drop_bank_question_before_complete_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, _, scope, manifest = fixture(root, False)
            manifest['banks'][0]['questions'] = []
            write_json(scope, manifest)
            with self.assertRaisesRegex(ValueError, 'question universe'):
                self.load(scope, root)

    def test_runtime_paths_and_complete_bank_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, bank, scope, manifest = fixture(root)
            entries, banks = self.load(scope, root)
            self.assertEqual(entries[0]['bank_path'], str(path.resolve()))
            self.assertEqual(entries[0]['bank_id'], 'web-test-ch01')
            self.assertEqual(banks, {'web-test-ch01': bank})
            self.assertEqual(json.loads(scope.read_text()), manifest)

    def test_rejects_duplicates_bad_status_deferred_missing_reason_or_prerequisite_and_bad_refs(self):
        mutations = [lambda e: e.append(copy.deepcopy(e[0])),
                     lambda e: e[0].update(status='unknown'),
                     lambda e: e[0].update(status='deferred', prerequisite='next'),
                     lambda e: e[0].update(status='deferred', reason='later'),
                     lambda e: e[0].update(refs=[]),
                     lambda e: e[0]['refs'][0].update(section='missing'),
                     lambda e: e[0]['refs'][0].update(section='유전 정보를'),
                     lambda e: e[0]['refs'][0].update(path='../outside.md')]
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _, _, scope, manifest = fixture(root)
                mutate(manifest['banks'][0]['questions'])
                write_json(scope, manifest)
                with self.assertRaises(ValueError):
                    self.load(scope, root)

    def test_bank_raw_and_manifest_hash_tampering(self):
        for target in ('bank', 'raw', 'hash'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path, _, scope, manifest = fixture(root)
                if target == 'bank':
                    path.write_bytes(path.read_bytes() + b' ')
                elif target == 'raw':
                    (path.parent / 'raw/fixture.txt').write_text('changed')
                else:
                    manifest['banks'][0]['sha256'] = '0' * 64
                    write_json(scope, manifest)
                with self.assertRaises(ValueError):
                    self.load(scope, root)

    def test_distinct_banks_same_number_and_duplicate_bank(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, bank, scope, manifest = fixture(root)
            second = copy.deepcopy(bank)
            second['assessment']['id'] = 'web-other-ch01'
            q = second['questions'][0]
            q['id'] = 'web-other-ch01:q01'
            q['review']['payload_sha256'] = canonical_digest(question_payload(second, q, path.parent, repo_root=root))
            p2 = path.with_name('other.json')
            write_json(p2, second)
            row = copy.deepcopy(manifest['banks'][0])
            row.update(path='../bank/other.json', sha256=hashlib.sha256(p2.read_bytes()).hexdigest())
            row['questions'][0]['id'] = q['id']
            manifest['banks'].append(row)
            write_json(scope, manifest)
            self.assertEqual([e['id'] for e in self.load(scope, root)[0]],
                             ['web-test-ch01:q01', 'web-other-ch01:q01'])
            manifest['banks'].append(copy.deepcopy(row))
            write_json(scope, manifest)
            with self.assertRaises(ValueError):
                self.load(scope, root)

    @staticmethod
    def rebase_fixture(root, scope):
        manifest = json.loads(scope.read_text())
        path = (scope.parent / manifest['banks'][0]['path']).resolve()
        bank = json.loads(path.read_text())
        ref = (root / 'evidence.md').relative_to(ROOT).as_posix()
        q = bank['questions'][0]
        q['analysis']['requirements'][0]['evidence'][0]['path'] = ref
        q['review']['payload_sha256'] = canonical_digest(question_payload(bank, q, path.parent, repo_root=ROOT))
        write_json(path, bank)
        manifest['banks'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest['banks'][0]['questions'][0]['refs'][0]['path'] = ref
        write_json(scope, manifest)

    def test_new_note_test_from_temp_cwd_accepts_absolute_web_scope(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp, tempfile.TemporaryDirectory() as cwd:
            root = Path(tmp)
            _, _, scope, _ = fixture(root)
            self.rebase_fixture(root, scope)
            generated = root / 'test_note_0999.py'
            p = subprocess.run([sys.executable, str(ROOT / 'scripts/new_note_test.py'), '0999',
                                '--web-scope', str(scope), '--out', str(generated)],
                               cwd=cwd, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn('WEB_SCOPE =', generated.read_text())


class NoteScopeCliTests(unittest.TestCase):
    def test_generated_test_output_protects_web_scope_inputs_and_aliases(self):
        for target_name in ('scope', 'bank', 'raw', 'evidence'):
            for alias_kind in ('direct', 'symlink', 'hardlink'):
                with self.subTest(target=target_name, alias=alias_kind), tempfile.TemporaryDirectory(
                        dir=ROOT / '.superpowers') as tmp:
                    root = Path(tmp)
                    bank_path, _, scope, _ = fixture(root)
                    WebScopeTests.rebase_fixture(root, scope)
                    targets = {
                        'scope': scope,
                        'bank': bank_path,
                        'raw': bank_path.parent / 'raw/fixture.txt',
                        'evidence': root / 'evidence.md',
                    }
                    target = targets[target_name]
                    output = target
                    if alias_kind != 'direct':
                        output = root / ('output-' + alias_kind)
                        if alias_kind == 'symlink':
                            output.symlink_to(target)
                        else:
                            os.link(target, output)
                    before = target.read_bytes()
                    try:
                        self.assertEqual(new_note_test.main([
                            '0999', '--web-scope', str(scope), '--out', str(output), '--force'
                        ]), 2)
                        self.assertEqual(target.read_bytes(), before)
                    finally:
                        if alias_kind != 'direct' and output.exists():
                            output.unlink()

        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp:
            root = Path(tmp)
            _, _, scope, _ = fixture(root)
            WebScopeTests.rebase_fixture(root, scope)
            output = root / 'generated/test_note_0999.py'
            self.assertEqual(new_note_test.main([
                '0999', '--web-scope', str(scope), '--out', str(output)
            ]), 0)
            first = output.read_bytes()
            self.assertEqual(new_note_test.main([
                '0999', '--web-scope', str(scope), '--out', str(output)
            ]), 2)
            self.assertEqual(new_note_test.main([
                '0999', '--web-scope', str(scope), '--out', str(output), '--force'
            ]), 0)
            self.assertEqual(output.read_bytes(), first)

    def test_note_meta_requires_mmdd_and_nonempty_title(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp:
            root = Path(tmp)
            _, _, scope, _ = fixture(root)
            WebScopeTests.rebase_fixture(root, scope)
            meta = root / 'meta.json'
            for value in ({'date': '999', 'title': 'DNA'},
                          {'date': '0999', 'title': '  '},
                          {'date': '0999', 'title': 'DNA', 'unknown': True}):
                with self.subTest(value=value):
                    write_json(meta, value)
                    self.assertEqual(bank_cli(['note', '--scope', str(scope), '--meta', str(meta),
                                               '--output', str(root / 'note.html')]), 1)

    def test_note_scope_cli_and_overwrite_input_alias_protection(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp:
            root = Path(tmp)
            bank_path, _, scope, _ = fixture(root)
            WebScopeTests.rebase_fixture(root, scope)
            meta = root / 'meta.json'
            write_json(meta, {'date': '0999', 'title': 'DNA 퀴즈'})
            template = root / 'template.html'
            template.write_bytes((ROOT / '정리노트/_template.html').read_bytes())
            output = root / 'note.html'
            args = ['note', '--scope', str(scope), '--meta', str(meta), '--template', str(template)]
            self.assertEqual(bank_cli(args + ['--output', str(output)]), 0)
            data = new_note_test.parse_question_data(output.read_text())
            self.assertEqual([q['qid'] for q in data[1]], ['web-test-ch01:q01'])
            self.assertEqual(data[0]['title'], 'DNA 퀴즈')
            self.assertEqual(data[0]['chapter'], 'N장 단원명')
            self.assertEqual(data[1][0]['refs'][0]['href'], 'evidence.md#dna')
            self.assertEqual(bank_cli(args + ['--output', str(output)]), 0)
            for target in [scope, meta, template, bank_path, root / 'evidence.md', bank_path.parent / 'raw/fixture.txt']:
                before = target.read_bytes()
                for alias in ['direct', 'symlink', 'hardlink']:
                    alias_path = root / ('alias-' + alias)
                    if alias == 'direct':
                        alias_path = target
                    elif alias == 'symlink':
                        alias_path.symlink_to(target)
                    else:
                        os.link(target, alias_path)
                    try:
                        self.assertEqual(bank_cli(args + ['--output', str(alias_path), '--force']), 1)
                        self.assertEqual(target.read_bytes(), before)
                    finally:
                        if alias != 'direct':
                            alias_path.unlink()

    def test_generated_web_note_tests_use_full_qids_and_real_resources(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp:
            root = Path(tmp)
            _, _, scope, _ = fixture(root)
            WebScopeTests.rebase_fixture(root, scope)
            note_dir = root / '정리노트'
            note_dir.mkdir()
            meta = root / 'meta.json'
            write_json(meta, {'date': '0999', 'title': 'DNA 퀴즈'})
            html_path = note_dir / '0999.html'
            self.assertEqual(bank_cli(['note', '--scope', str(scope), '--meta', str(meta),
                                       '--output', str(html_path)]), 0)
            html_path.write_text(html_path.read_text().replace(
                '</body>', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"></svg></body>'))
            (note_dir / '0999.md').write_text('''# 0999 테스트

## ⏱ 30초 요약

요약.

## ⏪ 지난 회차 복습

복습.

## ✂️ 여기서 강의가 끝났습니다

다음.

## 부록. 문항 ↔ 개념 매핑

[0999.html](0999.html)

| 출처 | 문항 ID | 질문 요약 | 절 | 상태 |
|---|---|---|---|---|
| web-test-ch01 | web-test-ch01:q01 | 유전 정보 | DNA | included |
''', encoding='utf-8')
            generated = root / 'test_note_0999.py'
            self.assertEqual(new_note_test.main(['0999', '--web-scope', str(scope),
                                                 '--out', str(generated)]), 0)
            spec = importlib.util.spec_from_file_location('generated_web_note_test', generated)
            module = importlib.util.module_from_spec(spec)
            old_root = os.environ.get('NOTE_REPO_ROOT')
            old_scope_root = os.environ.get('WEB_SCOPE_REPO_ROOT')
            os.environ['NOTE_REPO_ROOT'] = str(root)
            os.environ['WEB_SCOPE_REPO_ROOT'] = str(ROOT)
            try:
                spec.loader.exec_module(module)
                with open(os.devnull, 'w') as sink:
                    result = unittest.TextTestRunner(stream=sink).run(
                        unittest.defaultTestLoader.loadTestsFromModule(module))
                self.assertTrue(result.wasSuccessful(), result.failures + result.errors)

                check = module.TestNoteHtml('test_single_file_no_external_deps')
                for attack in ('<script src="evil.js"></script>', '<script>fetch ("evil")</script>',
                               '<style>@import "evil.css"</style>',
                               '<svg><image href="evil.svg"></image></svg>',
                               '<img srcset="https://example.invalid/a.png 1x">',
                               '<video poster="https://example.invalid/poster.png"></video>',
                               '<svg><feImage href="https://example.invalid/filter.svg"></feImage></svg>'):
                    with self.subTest(attack=attack):
                        check.html = html_path.read_text().replace('</body>', attack + '</body>')
                        with self.assertRaises(AssertionError):
                            check.test_single_file_no_external_deps()

                decoy = root / 'decoy.md'
                decoy.write_text('# DNA\n관계없는 근거.\n', encoding='utf-8')
                refs = module.TestWebQuestionScope('test_web_refs_are_local_files_with_real_sections')
                refs.html = html_path.read_text().replace('../evidence.md#dna', '../decoy.md#dna')
                with self.assertRaises(AssertionError):
                    refs.test_web_refs_are_local_files_with_real_sections()

                mapping = module.TestWebQuestionScope(
                    'test_markdown_web_table_classifies_every_original_qid')
                original_web_scope = module.WEB_SCOPE
                q1 = module.WEB_SCOPE['questions']['web-test-ch01:q01']
                module.WEB_SCOPE = {'active': ['web-test-ch01:q01'], 'questions': {
                    'web-test-ch01:q01': q1,
                    'web-test-ch01:q02': {'bank_id': 'web-test-ch01',
                                          'status': 'deferred', 'refs': []},
                }}
                mapping.md = (note_dir / '0999.md').read_text() + (
                    '| web-test-ch01 | web-test-ch01:q01 | duplicate | DNA | included |\n')
                with self.assertRaises(AssertionError):
                    mapping.test_markdown_web_table_classifies_every_original_qid()
                module.WEB_SCOPE = original_web_scope
                mapping.md = (note_dir / '0999.md').read_text() + (
                    '| web-test-ch01 | web-test-ch01:q99 | extra | DNA | included |\n')
                with self.assertRaises(AssertionError):
                    mapping.test_markdown_web_table_classifies_every_original_qid()
            finally:
                if old_root is None:
                    os.environ.pop('NOTE_REPO_ROOT', None)
                else:
                    os.environ['NOTE_REPO_ROOT'] = old_root
                if old_scope_root is None:
                    os.environ.pop('WEB_SCOPE_REPO_ROOT', None)
                else:
                    os.environ['WEB_SCOPE_REPO_ROOT'] = old_scope_root
