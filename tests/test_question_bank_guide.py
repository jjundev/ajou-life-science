"""Source-bank guide integration: identity, teaching, scope and answer isolation."""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from study_guide_fixture import ROOT, SCRIPTS
from test_study_guide_build import GUIDE, NOTE
from question_bank_fixture import make_bank
from build_guide import build, qanchor, load_data, active_card
from make_blind_copy import strip_solutions
from verify_guide import run_coverage
from scripts.question_bank.model import canonical_digest, question_payload, load_bank, asset_payload
from scripts.question_bank.scope import file_hash
from test_question_bank_render import add_figure
from guide_html import parse_guide, answerability_errors
from coverage_model import validate_inventory


def adapter(*args):
    from scripts.question_bank.guide import bank_to_guide
    return bank_to_guide(*args)


class Cards(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.cards, self.figures = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-question-id' in attrs:
            self.cards.append((attrs['data-question-id'], attrs['data-status']))
        if attrs.get('data-figure-variant'):
            self.figures.append(attrs['data-figure-variant'])


def fixture(base, *, deferred=False):
    path, bank = make_bank(base)
    (base / 'evidence.md').write_text('# DNA\n\nDNA는 유전 정보를 저장한다.\n')
    q = bank['questions'][0]
    q['analysis']['requirements'][0]['evidence'][0]['path'] = os.path.relpath(base / 'evidence.md', ROOT)
    q['review'] = dict(status='verified', notes='synthetic fixture only',
                       payload_sha256=canonical_digest(question_payload(bank, q, base, repo_root=ROOT)))
    path.write_text(json.dumps(bank, ensure_ascii=False))
    entries = [dict(id=q['id'], status='deferred' if deferred else 'included', reason='DNA 연결',
                    prerequisite='DNA를 먼저 학습' if deferred else None,
                    refs=[dict(path=os.path.relpath(base / 'evidence.md', ROOT), section='DNA')])]
    scope = dict(schema_version=1, banks=[dict(path='questions.json', sha256=file_hash(path), questions=entries)])
    (base / 'scope.json').write_text(json.dumps(scope, ensure_ascii=False))
    (base / 'note.md').write_text(NOTE + '\n## DNA\n\nDNA는 유전 정보를 저장한다.\n')
    (base / 'quiz.txt').write_text('2강 6: 효소에 대한 설명 중 틀린 것은?\n')
    binding = {q['id']: dict(group='dna', status='included', requirement_facts={'r1': ['fact-dna']})}
    guide = GUIDE + '''
META.update(web_scope="scope.json", delivery_mode="draft", output_stem="mixed-draft")
META['groups'].append(('dna', 'DNA'))
CONCEPTS.append(('dna', 'DNA', []))
kit.TITLES['dna'] = 'DNA'
BLOCKS.extend([('dna-heading', 13, 13, 'metadata', 'DNA 제목', None),
               ('dna', 15, 15, 'teaching', 'DNA 본문', None)])
FACTS.append(F('fact-dna', 'dna', 'definition', 'dna', 'DNA는 유전 정보를 저장한다.', 'DNA는 유전 정보를 저장한다.'))
SECTIONS.append(section('dna', '개념', 'DNA', T('teach-dna', 'fact-dna', 'DNA는 유전 정보를 저장한다.') + R('유전 정보는?', 'DNA')))
'''
    guide += '\nWEB_BINDINGS = ' + repr({} if deferred else binding) + '\n'
    (base / 'guide.py').write_text(guide)
    return bank, entries, binding


def real_fixture(base):
    """Draft-only fixture with explicit classifications for the full real bank."""
    fixture(base)
    path = ROOT / '웹과제/1장/questions.json'
    bank = load_bank(path, complete=True)
    refs_path = base / 'scope-refs.md'
    refs_path.write_text('# 웹과제 자료 연결\n\n' + '\n'.join(
        r['statement'] for q in bank['questions'] for r in q['analysis']['requirements']))
    active = {4, 6, 9, 14}
    entries, bindings = [], {}
    extra = ["META['groups'].append(('web-study', '1장 자료 연결'))",
             "CONCEPTS.append(('web-study', '1장 자료 연결', []))",
             "kit.TITLES['web-study'] = '1장 자료 연결'", "web_teaching = ''"]
    for q in bank['questions']:
        refs = [dict(path=os.path.relpath(refs_path, ROOT), section='웹과제 자료 연결')]
        entries.append(dict(id=q['id'], status='included' if q['number'] in active else 'deferred',
                            reason='통합 테스트 범위' if q['number'] in active else '이번 테스트 범위 밖',
                            prerequisite=None if q['number'] in active else '해당 개념 학습', refs=refs))
        if q['number'] not in active:
            continue
        binding = dict(group='web-study', status='included', requirement_facts={})
        for index, r in enumerate(q['analysis']['requirements']):
            fid = f"real-{q['number']}-{index}"
            evidence = r['evidence'][0]
            src = fid + '-source'
            binding['requirement_facts'][r['id']] = [fid]
            extra += [
                'SOURCES.append(' + repr(dict(id=src, path=os.path.relpath(ROOT / evidence['path'], base), role='reference')) + ')',
                'BLOCKS.append(' + repr((fid, None, None, 'supplement', '웹과제 근거 자료 연결', [q['id']])) + ')',
                'FACTS.append(F(' + ', '.join(repr(x) for x in (fid, fid, 'definition', 'web-study', r['statement'], evidence['quote'])) + f', src={src!r}, loc={evidence["locator"]!r}))',
                f'web_teaching += T({fid + "-teaching"!r}, {fid!r}, {r["statement"]!r})',
            ]
        bindings[q['id']] = binding
    extra.append("SECTIONS.append(section('web-study', '자료 보충', '1장 자료 연결', web_teaching + R('근거를 말해 보세요.', '본문 참조')))" )
    (base / 'scope.json').write_text(json.dumps(dict(schema_version=1, banks=[dict(
        path=os.path.relpath(path, base), sha256=file_hash(path), questions=entries)]), ensure_ascii=False))
    guide = (base / 'guide.py').read_text()
    (base / 'guide.py').write_text(guide + '\n' + '\n'.join(extra) + '\nWEB_BINDINGS = ' + repr(bindings) + '\n')
    return bank, entries, bindings


class GuideBankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.superpowers')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_web_and_legacy_anchors_are_distinct(self):
        self.assertEqual(qanchor('1강:18'), 'q1-18')
        self.assertNotEqual(qanchor('web-20260917-ch01:q18'), qanchor('1강:18'))
        self.assertNotEqual(qanchor('web-20260917-ch01:q09'), qanchor('web-20260918-ch01:q09'))

    def test_adapter_preserves_source_and_maps_every_requirement(self):
        bank, entries, bindings = fixture(self.base)
        original = copy.deepcopy((bank, entries, bindings))
        questions, deferred, figures = adapter(bank, bindings, self.base, entries)
        q = questions[0]
        self.assertEqual((q['id'], q['ans'], q['key'], q['reqs']),
                         ('web-test-ch01:q01', 1, None, ['fact-dna']))
        self.assertEqual(q['option_labels'], ['A', 'B'])
        self.assertEqual(q['content'], bank['questions'][0]['original']['content'])
        self.assertIn('raw/fixture.txt', q['locator'])
        self.assertEqual((deferred, figures), ({}, ''))
        self.assertNotIn('observations', q)
        self.assertEqual((bank, entries, bindings), original)
        for bad in ({}, {**bindings, 'unknown:q01': bindings[q['id']]},
                    {q['id']: {**bindings[q['id']], 'requirement_facts': {}}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                adapter(bank, bad, self.base, entries)
        with self.assertRaises(ValueError):
            adapter(bank, bindings, self.base, [])

    def test_mixed_guide_passes_draft_with_actual_cards_hashes_and_locator(self):
        fixture(self.base)
        d = load_data(self.base / 'guide.py')
        original = copy.deepcopy((d.META, d.QUESTIONS, d.DEFERRED))
        with patch('build_guide.load_data', return_value=d):
            result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        self.assertEqual((d.META, d.QUESTIONS, d.DEFERRED), original)
        html = result['html'].read_text()
        self.assertEqual(Cards(html).cards, [('2강:6', 'included'), ('web-test-ch01:q01', 'included')])
        self.assertIn('A DNA', html)
        self.assertIn('raw/fixture.txt', html)
        self.assertNotIn('p스크린샷', html)
        self.assertNotIn('캡처 선택', html)
        self.assertIn('웹 범위 명세', html)
        data = json.loads(result['coverage'].read_text())
        paths = {(self.base / s['path']).resolve(): s['sha256'] for s in data['inventory']['sources']}
        for name in ('scope.json', 'questions.json', 'raw/fixture.txt', 'evidence.md'):
            self.assertEqual(paths[self.base / name], file_hash(self.base / name))
        self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])
        self.assertEqual(data['delivery_mode'], 'draft')
        self.assertTrue(run_coverage(result['html'], result['coverage'], 'complete', result['scope']))

    def test_invalid_binding_group_and_solution_only_fact_fail_without_output(self):
        fixture(self.base)
        path = self.base / 'guide.py'
        original = path.read_text()
        for source, want in ((original.replace("'fact-dna']}", "'missing-fact']}"), 'unknown'),
                             (original.replace("group': 'dna'", "group': 'absent'"), 'unknown question group'),
                             (original.replace("T('teach-dna', 'fact-dna', 'DNA는 유전 정보를 저장한다.')", "''"), 'fact not taught')):
            with self.subTest(want=want):
                path.write_text(source)
                _, errors = build(path, self.base)
                self.assertTrue(any(want in e for e in errors), errors)
                self.assertFalse((self.base / 'mixed-draft.html').exists())

    def test_overrides_use_final_status_and_deferred_requires_prerequisite(self):
        _, _, bindings = fixture(self.base, deferred=True)
        path = self.base / 'guide.py'
        original = path.read_text()
        path.write_text(original + '\nWEB_BINDINGS = ' + repr(bindings) + '\nMETA["overrides"] = "overrides.json"\n')
        override = dict(id='web-test-ch01:q01', **{'from':'deferred', 'to':'included'}, reason='본문에서 학습',
                        evidence=dict(source_path='note.md', page='15', quote='DNA는 유전 정보를 저장한다.'))
        (self.base / 'overrides.json').write_text(json.dumps([override]))
        result, errors = build(path, self.base)
        self.assertEqual(errors, [])
        self.assertIn(('web-test-ch01:q01', 'included'), Cards(result['html'].read_text()).cards)
        self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])
        fixture(self.base)
        path.write_text(path.read_text() + '\nWEB_BINDINGS["web-test-ch01:q01"]["status"] = "review"\nMETA["overrides"] = "overrides.json"\n')
        override.update({'from': 'included', 'to': 'review'})
        (self.base / 'overrides.json').write_text(json.dumps([override]))
        result, errors = build(path, self.base)
        self.assertEqual(errors, [])
        self.assertIn(('web-test-ch01:q01', 'review'), Cards(result['html'].read_text()).cards)
        override['to'] = 'deferred'
        (self.base / 'overrides.json').write_text(json.dumps([override]))
        _, errors = build(path, self.base)
        self.assertTrue(any('prerequisite' in e for e in errors), errors)

    def test_raw_mutation_rejected_and_cli_works_from_other_cwd(self):
        fixture(self.base)
        with tempfile.TemporaryDirectory() as cwd:
            output = Path(cwd) / 'output'
            proc = subprocess.run([sys.executable, str(SCRIPTS / 'build_guide.py'), str(self.base / 'guide.py'),
                                   '--out-dir', str(output)], cwd=cwd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(run_coverage(output / 'mixed-draft.html', output / 'mixed-draft.coverage.json',
                                          'draft', output / 'mixed-draft.question-scope.json'), [])
        (self.base / 'raw/fixture.txt').write_text('modified source')
        _, errors = build(self.base / 'guide.py', self.base)
        self.assertTrue(any('hash' in e or 'sha256' in e for e in errors), errors)

    def test_deferred_adapter_uses_override_reason_over_old_or_null_baseline(self):
        bank, entries, _ = fixture(self.base)
        from question_scope import apply_overrides
        override = dict(id='web-test-ch01:q01', **{'from': 'included', 'to': 'deferred'},
                        reason='후속 수업에서 DNA 구조를 배운 뒤 풉니다.',
                        evidence=dict(source_path='note.md', page='15', quote='DNA는 유전 정보를 저장한다.'))
        for baseline in ('이번 회차 DNA 연결 문항', None):
            with self.subTest(baseline=baseline):
                entry = {**entries[0], 'reason': baseline, 'prerequisite': 'DNA 구조 학습'}
                final, errors = apply_overrides({entry['id']: entry}, [override])
                self.assertEqual(errors, [])
                questions, deferred, _ = adapter(bank, {}, self.base, list(final.values()))
                self.assertEqual(questions, [])
                self.assertEqual(deferred[entry['id']], (override['reason'], 'DNA 구조 학습', []))
                self.assertEqual(entry['reason'], baseline)
                final[entry['id']]['prerequisite'] = None
                with self.assertRaisesRegex(ValueError, 'prerequisite'):
                    adapter(bank, {}, self.base, list(final.values()))

    def test_deferred_override_reason_reaches_card_and_inventory_for_old_or_null_baseline(self):
        for baseline in ('이번 회차 DNA 연결 문항', None):
            with self.subTest(baseline=baseline):
                fixture(self.base)
                scope_path = self.base / 'scope.json'
                scope = json.loads(scope_path.read_text())
                scope['banks'][0]['questions'][0].update(reason=baseline, prerequisite='DNA 구조 학습')
                scope_path.write_text(json.dumps(scope))
                path = self.base / 'guide.py'
                path.write_text(path.read_text() + '\nWEB_BINDINGS = {}\nMETA["overrides"] = "overrides.json"\n')
                override = dict(id='web-test-ch01:q01', **{'from': 'included', 'to': 'deferred'},
                                reason='후속 수업에서 DNA 구조를 배운 뒤 풉니다.',
                                evidence=dict(source_path='note.md', page='15', quote='DNA는 유전 정보를 저장한다.'))
                (self.base / 'overrides.json').write_text(json.dumps([override]))
                result, errors = build(path, self.base)
                self.assertEqual(errors, [])
                parsed = parse_guide(result['html'].read_text())
                from guide_html import text_of, descendants
                card = next(n for n in parsed.nodes if n.attrs.get('data-question-id') == override['id'])
                reason = next(n for n in descendants(card) if n.attrs.get('data-part') == 'deferred-reason')
                self.assertIn(override['reason'], text_of(reason))
                if baseline:
                    self.assertNotIn(baseline, text_of(reason))
                data = json.loads(result['coverage'].read_text())
                deferred = next(q for q in data['inventory']['questions'] if q['id'] == override['id'])
                self.assertEqual(deferred['reason'], override['reason'])
                self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])

    def test_figures_are_visible_in_prompt_and_only_explanations_are_removed(self):
        bank, entries, bindings = fixture(self.base)
        add_figure(self.base, bank)
        q = bank['questions'][0]
        q['original']['content'].append({'type': 'figure', 'asset_id': 'q01'})
        bank['assets'][0]['review'] = dict(status='verified', notes='synthetic fixture only',
            payload_sha256=canonical_digest(asset_payload(bank, bank['assets'][0], self.base)))
        q['review']['payload_sha256'] = canonical_digest(question_payload(bank, q, self.base, repo_root=ROOT))
        path = self.base / 'questions.json'
        path.write_text(json.dumps(bank))
        scope = json.loads((self.base / 'scope.json').read_text())
        scope['banks'][0]['sha256'] = file_hash(path)
        (self.base / 'scope.json').write_text(json.dumps(scope))
        questions, _, _ = adapter(bank, bindings, self.base, entries)
        self.assertEqual(len(questions[0]['fig']), 2)
        result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        html = result['html'].read_text()
        self.assertEqual(Cards(html).figures, ['exam', 'exam', 'explained', 'explained'])
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])
        blind, count, errors = strip_solutions(html)
        self.assertEqual((count, errors), (2, []))
        self.assertEqual(Cards(blind).figures, ['exam', 'exam'])
        for excluded in ('explained ALT', '<template', '보기별 진단', '캡처 선택', '정답(판단)'):
            self.assertNotIn(excluded, blind)
        (self.base / 'image/exam.svg').unlink()
        _, errors = build(self.base / 'guide.py', self.base)
        self.assertTrue(errors)

    def test_real_bank_full_scope_subset_preserves_ambiguity_statements_and_figures(self):
        bank, entries, bindings = real_fixture(self.base)
        questions, deferred, _ = adapter(bank, bindings, ROOT / '웹과제/1장', entries)
        q4 = next(q for q in questions if q['id'].endswith(':q04'))
        self.assertEqual((q4['ans'], q4['grading'], q4['also_accept'], q4['key']), (3, 'ambiguous', [], None))
        self.assertTrue(q4['conflict'])
        self.assertEqual(len(deferred), 13)
        result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        html = result['html'].read_text()
        cards = Cards(html).cards
        self.assertEqual(len(cards), 18)
        self.assertEqual(dict(cards), {'2강:6': 'included', **{e['id']: e['status'] for e in entries}})
        self.assertEqual(Cards(html).figures, ['exam', 'explained', 'exam', 'explained'])
        for text in bank['questions'][5]['original']['content']:
            if text['type'] == 'statements':
                for statement in text['items']:
                    self.assertIn(statement['text'], html)
        self.assertIn('출제 의도 정답: C', html)
        self.assertIn('공식 답은 확인되지 않았습니다.', html)
        self.assertNotIn('함께 인정할 수 있는 답:', html)
        self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])
        blind, _, errors = strip_solutions(html)
        self.assertEqual(errors, [])
        self.assertEqual(Cards(blind).figures, ['exam', 'exam'])

    def test_legacy_ambiguous_still_requires_alternate_and_jsonschema_is_lazy(self):
        fixture(self.base)
        (self.base / 'note.md').write_text(NOTE)
        legacy = GUIDE.replace('1, 1, "single"', '1, 1, "ambiguous"')
        (self.base / 'guide.py').write_text(legacy)
        _, errors = build(self.base / 'guide.py', self.base)
        self.assertTrue(any('also_accept' in e for e in errors), errors)
        (self.base / 'guide.py').write_text(GUIDE)
        (self.base / 'sitecustomize.py').write_text('''import sys
class Block:
    def find_spec(self, fullname, *args):
        if fullname == 'jsonschema' or fullname.startswith('jsonschema.'):
            raise ImportError('jsonschema blocked by legacy regression')
sys.meta_path.insert(0, Block())
''')
        with tempfile.TemporaryDirectory() as cwd:
            proc = subprocess.run([sys.executable, str(SCRIPTS / 'build_guide.py'), str(self.base / 'guide.py'),
                                   '--out-dir', str(self.base)], cwd=cwd, env={**os.environ, 'PYTHONPATH': str(self.base)},
                                  capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_bank_figure_target_must_belong_to_own_visible_prompt(self):
        real_fixture(self.base)
        result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        html = result['html'].read_text()
        data = json.loads(result['coverage'].read_text())
        q9 = next(q for q in data['inventory']['questions'] if q['id'].endswith(':q09'))
        q14 = next(q for q in data['inventory']['questions'] if q['id'].endswith(':q14'))
        original = q9['answerability']['figure_target_ids']
        self.assertEqual(answerability_errors(parse_guide(html), data), [])
        q9['answerability']['figure_target_ids'] = q14['answerability']['figure_target_ids']
        self.assertTrue(answerability_errors(parse_guide(html), data))
        q9['answerability']['figure_target_ids'] = original
        for modified in (html.replace('data-part="prompt"', 'data-part="other"'),
                         html.replace('data-figure-variant="exam"', 'hidden data-figure-variant="exam"'),
                         html.replace('data-part="prompt"', 'data-role="solution"')):
            self.assertTrue(answerability_errors(parse_guide(modified), data))

    def test_solution_fact_annotation_cannot_replace_actual_teaching(self):
        fixture(self.base)
        path = self.base / 'guide.py'
        source = path.read_text().replace("T('teach-dna', 'fact-dna', 'DNA는 유전 정보를 저장한다.')", "''")
        source += '\nQUESTIONS[0]["reason"] += kit.T("fake-teaching", "fact-dna", "DNA는 유전 정보를 저장한다.")\n'
        path.write_text(source)
        _, errors = build(path, self.base)
        self.assertTrue(any('not visible teaching' in e for e in errors), errors)

    def test_empty_deferred_web_facts_require_reason_and_prerequisite(self):
        fixture(self.base, deferred=True)
        result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        original = json.loads(result['coverage'].read_text())
        self.assertEqual(validate_inventory(original, self.base), [])
        for change in ({'reason': ''}, {'later_prerequisite': ''}, {'fact_ids': None},
                       {'status': 'included'}, {'origin': 'legacy'}):
            data = copy.deepcopy(original)
            data['inventory']['questions'][-1].update(change)
            data['inventory_sha256'] = canonical_digest(data['inventory'])
            with self.subTest(change=change):
                self.assertTrue(validate_inventory(data, self.base))

    def test_source_option_labels_and_official_answer_are_never_truncated(self):
        bank, entries, bindings = fixture(self.base)
        q = bank['questions'][0]
        q['original']['options'] = [dict(id=chr(65+i), text=f'보기 {i+1}') for i in range(12)]
        q['analysis'].update(answer_option_id='L', also_accept=['K'], grading='ambiguous',
            option_diagnostics={chr(65+i): dict(is_answer=i in (10, 11), explanation='진단', requirement_ids=['r1']) for i in range(12)},
            issues=[dict(description='범위 모호성', source_ids=['s1'])])
        q['observations']['official_answer'] = dict(option_ids=['A'], source_ids=['s1'])
        questions, _, _ = adapter(bank, bindings, self.base, entries)
        self.assertEqual((questions[0]['ans'], questions[0]['key'], questions[0]['also_accept']), (12, 1, [11]))
        html = active_card(questions[0], {'quiz_sources': {'web-test-ch01': {'label': 'fixture'}}},
                           {'fact-dna': {'concept': 'dna'}}, {'dna': 'DNA'})
        self.assertIn('L 보기 12', html)
        self.assertIn('함께 인정할 수 있는 답: K 보기 11', html)
        self.assertIn('확인된 공식 답: A 보기 1', html)
        single = {**questions[0], 'grading': 'single', 'also_accept': []}
        html = active_card(single, {'quiz_sources': {'web-test-ch01': {'label': 'fixture'}}},
                           {'fact-dna': {'concept': 'dna'}}, {'dna': 'DNA'})
        self.assertIn('분석 기준 답: L 보기 12', html)
        self.assertNotIn('오류로 판단', html)
        q['observations']['official_answer']['option_ids'].append('B')
        with self.assertRaisesRegex(ValueError, 'official option'):
            adapter(bank, bindings, self.base, entries)

    def test_deferred_scope_text_is_escaped_as_source_text(self):
        fixture(self.base, deferred=True)
        path = self.base / 'scope.json'
        scope = json.loads(path.read_text())
        scope['banks'][0]['questions'][0]['reason'] = '<script>throw "scope text"</script>'
        scope['banks'][0]['questions'][0]['prerequisite'] = '<b>source prerequisite</b>'
        path.write_text(json.dumps(scope))
        result, errors = build(self.base / 'guide.py', self.base)
        self.assertEqual(errors, [])
        html = result['html'].read_text()
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('&lt;b&gt;source prerequisite&lt;/b&gt;', html)
        self.assertNotIn('<script>throw', html)

    def test_override_cannot_activate_without_refs_or_binding(self):
        fixture(self.base, deferred=True)
        path = self.base / 'guide.py'
        path.write_text(path.read_text() + '\nMETA["overrides"] = "overrides.json"\n')
        override = dict(id='web-test-ch01:q01', **{'from': 'deferred', 'to': 'included'}, reason='학습',
                        evidence=dict(source_path='note.md', page='15', quote='DNA'))
        (self.base / 'overrides.json').write_text(json.dumps([override]))
        _, errors = build(path, self.base)
        self.assertTrue(any('WEB_BINDINGS' in e for e in errors), errors)
        path.write_text(path.read_text() + '\nWEB_BINDINGS = {"web-test-ch01:q01": dict(group="dna", status="included", requirement_facts={"r1":["fact-dna"]})}\n')
        scope_path = self.base / 'scope.json'
        scope = json.loads(scope_path.read_text())
        scope['banks'][0]['questions'][0]['refs'] = []
        scope_path.write_text(json.dumps(scope))
        _, errors = build(path, self.base)
        self.assertTrue(any('requires refs' in e for e in errors), errors)

    def test_source_identity_with_delimiters_is_escaped_and_preserved(self):
        bank, _, bindings = fixture(self.base)
        bank['assessment']['id'] = 'web-"<source>:extra'
        q = bank['questions'][0]
        old = q['id']
        q['id'] = bank['assessment']['id'] + ':q01'
        q['review']['payload_sha256'] = canonical_digest(question_payload(bank, q, self.base, repo_root=ROOT))
        bank_path = self.base / 'questions.json'
        bank_path.write_text(json.dumps(bank))
        path = self.base / 'scope.json'
        scope = json.loads(path.read_text())
        scope['banks'][0]['sha256'] = file_hash(bank_path)
        scope['banks'][0]['questions'][0]['id'] = q['id']
        path.write_text(json.dumps(scope))
        path = self.base / 'guide.py'
        path.write_text(path.read_text() + '\nWEB_BINDINGS = ' + repr({q['id']: bindings[old]}) + '\n')
        result, errors = build(path, self.base)
        self.assertEqual(errors, [])
        html = result['html'].read_text()
        self.assertIn((q['id'], 'included'), Cards(html).cards)
        self.assertNotIn('<source>', html)
        self.assertEqual(run_coverage(result['html'], result['coverage'], 'draft', result['scope']), [])


if __name__ == '__main__':
    unittest.main()
