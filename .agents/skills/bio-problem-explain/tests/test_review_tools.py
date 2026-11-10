"""sync-evidence · review-merge · import-blind: post-build review bookkeeping without a second build."""
import hashlib
import json
from test_forecast_pipeline import build_run, approve
from test_cli import call
from mpe_cli import load_artifacts, load_fragments
from mpe_render import names


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review(item):
    return json.loads((item['folder'] / 'review.json').read_text())


def write_ledger(tmp_path, source, override=None):
    src = source.parent / '.pack' / 'v5'
    key = json.loads((src / 'pack.json').read_text())['answer_key']
    answers = tmp_path / 'blind-answers.md'
    answers.write_text('| 카드 | 고른 답 |\n')
    cards = {}
    for cid, answer in key.items():
        entry = {'answer': answer, 'basis': '토픽', 'objection': '', 'steps': '1단계', 'level': '1',
                 'sha256': sha(src / 'cards' / f'{cid}.html'), 'round': 1, 'answers_file': str(answers),
                 'blind_file': str(tmp_path / 'blind.md')}
        entry.update((override or {}).get(cid, {}))
        cards[cid] = entry
    ledger = tmp_path / 'blind-ledger.json'
    ledger.write_text(json.dumps({'version': 1, 'src': str(src.resolve()), 'cards': cards}, ensure_ascii=False))
    return ledger, src


def merge(run, kind, value, tmp_path):
    part = tmp_path / f'{kind}.json'
    part.write_text(json.dumps(value, ensure_ascii=False))
    return call('review-merge', '--run', run, '--kind', kind, '--from', part)


def test_sync_evidence_keeps_reviews_and_publishes_late_evidence(tmp_path):
    source, run, item = build_run(tmp_path)
    approve(item)
    (item['folder'] / 'evidence' / 'explain-browser.json').write_text('{"status": "pass"}')
    result = call('sync-evidence', '--run', run)
    assert result.returncode == 0, result.stderr
    after = review(item)
    assert after['browser']['status'] == 'pass'
    assert any(k.endswith('evidence/explain-browser.json') for k in after['artifact_hashes'])
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    data = source.parent / names(item['pack'])[2]
    assert (data / 'evidence' / 'explain-browser.json').is_file()


def test_sync_evidence_rejects_changed_render(tmp_path):
    source, run, item = build_run(tmp_path)
    approve(item)
    html = load_artifacts(item).html
    html.write_text(html.read_text() + '<!-- edited -->')
    result = call('sync-evidence', '--run', run)
    assert result.returncode == 1 and 'evidence 밖' in result.stderr


def test_review_merge_one_kind_and_references(tmp_path):
    source, run, item = build_run(tmp_path)
    base = {'status': 'pass', 'reviewer': '브라우저 검토', 'evidence': 'evidence/explain-browser.json'}
    assert merge(run, 'browser', base, tmp_path).returncode == 0
    assert review(item)['browser'] == base
    assert review(item)['content']['status'] == 'not_run'
    bad = merge(run, 'content', {**base, 'items': {'p1:main': base}}, tmp_path)
    assert bad.returncode == 1 and 'items 키' in bad.stderr
    pack_json = source.parent / '.pack' / 'v5' / 'pack.json'
    result = call('review-merge', '--run', run, '--add-reference', pack_json)
    assert result.returncode == 0, result.stderr
    assert review(item)['references'] == [{'path': str(pack_json.resolve()), 'sha256': sha(pack_json)}]


def test_import_blind_fills_independent_and_publishes(tmp_path):
    source, run, item = build_run(tmp_path)
    ledger, src = write_ledger(tmp_path, source)
    result = call('import-blind', '--run', run, '--ledger', ledger)
    assert result.returncode == 0, result.stderr
    independent = review(item)['independent']
    assert independent['status'] == 'pass' and set(independent['items']) == {f'p{i}:main' for i in range(1, 16)}
    assert independent['items']['p1:main']['method'] == 'qualitative'
    assert '블라인드' in independent['items']['p1:main']['reviewer']
    assert (item['folder'] / 'evidence' / 'independent-blind.md').is_file()
    current = review(item)
    keys = list(current['content']['items'])
    base = {'status': 'pass', 'reviewer': 'r', 'evidence': 'e'}
    for kind in ('source_visual', 'browser'):
        assert merge(run, kind, base, tmp_path).returncode == 0
    exceptions = {k: {**base, 'reason': v['reason']} for k, v in current['content']['note_link_exceptions'].items()}
    content = {**base, 'items': {k: base for k in keys}, 'note_link_exceptions': exceptions}
    assert merge(run, 'content', content, tmp_path).returncode == 0
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr


def test_import_blind_rejects_wrong_objection_or_changed_card(tmp_path):
    source, run, item = build_run(tmp_path)
    ledger, src = write_ledger(tmp_path, source, {'p2': {'answer': 'E'}, 'p3': {'objection': 'C도 답'}})
    result = call('import-blind', '--run', run, '--ledger', ledger)
    assert result.returncode == 1
    assert 'p2: 블라인드 답 E' in result.stderr and 'p3: 이의' in result.stderr
    ledger, src = write_ledger(tmp_path, source)
    card = src / 'cards' / 'p4.html'
    card.write_text(card.read_text() + ' ')
    result = call('import-blind', '--run', run, '--ledger', ledger)
    assert result.returncode == 1 and 'p4: 블라인드 이후 카드 변경' in result.stderr
    assert review(item)['independent']['status'] == 'not_run'
