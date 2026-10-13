import json
import subprocess
import sys
from pathlib import Path
import pytest
from helpers import fragment, approved, choice_source_file, source_file
from mpe_source import load_source
from mpe_cli import load_run

ROOT = Path(__file__).resolve().parents[4]
CLI = Path(__file__).resolve().parents[1] / 'scripts/mpe_cli.py'

def call(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True, encoding='utf-8')

def test_missing_target_returns_one(tmp_path):
    result = call('extract', '--repo', ROOT, '--target', '1011', '--run', tmp_path / 'run')
    assert result.returncode == 1
    assert '대상 없음' in result.stderr

def test_cli_round_trip_and_unreviewed_publish(tmp_path):
    repo = tmp_path / 'repo'
    source = repo / '복습노트/0917/복습문제_0917_Recursion.html'
    source.parent.mkdir(parents=True)
    source.write_bytes((ROOT / '복습노트/0917' / source.name).read_bytes())
    run = tmp_path / 'run'
    result = call('extract', '--repo', repo, '--target', '0917', '--run', run)
    assert result.returncode == 0, result.stderr
    item = load_run(run)[0]
    assert item['pack'] == load_source(source, repo)
    before = source.read_bytes()
    for p in item['pack'].problems:
        (item['folder'] / 'explanations' / f'{p.id}.html').write_text(fragment(p), encoding='utf-8')
    for command in ('build', 'check'):
        result = call(command, '--run', run)
        assert result.returncode == 0, result.stderr
    result = call('publish', '--run', run)
    assert result.returncode == 1 and '보류' in result.stderr
    assert source.read_bytes() == before
    assert not list(source.parent.glob('*문제설명*.html'))
    item = load_run(run)[0]
    from mpe_cli import load_artifacts, load_fragments
    artifacts = load_artifacts(item)
    reviews = approved(item['pack'], load_fragments(item), artifacts)
    (item['folder'] / 'review.json').write_text(json.dumps(reviews, ensure_ascii=False), encoding='utf-8')
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    assert list(source.parent.glob('*문제설명*.html'))
    assert source.read_bytes() == before

def test_extract_refuses_nonempty_run(tmp_path):
    run = tmp_path / 'run'
    run.mkdir()
    (run / 'keep.txt').write_text('keep')
    result = call('extract', '--repo', ROOT, '--target', '0917', '--run', run)
    assert result.returncode == 1
    assert (run / 'keep.txt').read_text() == 'keep'

def test_forged_serialized_problem_is_rejected(tmp_path):
    run = tmp_path / 'run'
    assert call('extract', '--repo', ROOT, '--target', '0917', '--run', run).returncode == 0
    source_json = next(run.rglob('source.json'))
    value = json.loads(source_json.read_text(encoding='utf-8'))
    value['problems'][0]['ask_html'] = '위조 조건'
    source_json.write_text(json.dumps(value), encoding='utf-8')
    result = call('check', '--run', run)
    assert result.returncode == 1
    assert '추출' in result.stderr

def test_one_stale_pack_does_not_block_other_pack(tmp_path):
    repo = tmp_path / 'repo'
    for date in ('0914', '0917'):
        source = repo / '복습노트' / date / f'복습문제_{date}_Recursion.html'
        source.parent.mkdir(parents=True)
        source.write_bytes((ROOT / '복습노트/0917/복습문제_0917_Recursion.html').read_bytes())
    run = tmp_path / 'run'
    assert call('extract', '--repo', repo, '--target', '0914-0917', '--run', run).returncode == 0
    for item in load_run(run):
        for p in item['pack'].problems:
            (item['folder'] / 'explanations' / f'{p.id}.html').write_text(fragment(p), encoding='utf-8')
    later = repo / '복습노트/0917/복습문제_0917_Recursion.html'
    later.write_bytes(later.read_bytes() + b'changed')
    result = call('build', '--run', run)
    assert result.returncode == 1
    assert (run / 'review-0914-Recursion/stage.json').is_file()
    assert not (run / 'review-0917-Recursion/stage.json').is_file()

def test_check_refuses_fragments_changed_after_build(tmp_path):
    run = tmp_path / 'run'
    assert call('extract', '--repo', ROOT, '--target', '0917', '--run', run).returncode == 0
    item = load_run(run)[0]
    for p in item['pack'].problems:
        (item['folder'] / 'explanations' / f'{p.id}.html').write_text(fragment(p), encoding='utf-8')
    assert call('build', '--run', run).returncode == 0
    (item['folder'] / 'explanations/p1.html').write_text('<p>풀이 누락</p>', encoding='utf-8')
    result = call('check', '--run', run)
    assert result.returncode == 1
    machine = json.loads((item['folder'] / 'machine.json').read_text(encoding='utf-8'))
    assert machine['status'] == 'fail'


def test_rebuild_resets_reviews(tmp_path):
    run=tmp_path/'run'
    assert call('extract','--repo',ROOT,'--target','0917','--run',run).returncode==0
    item=load_run(run)[0]
    for p in item['pack'].problems:(item['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p))
    assert call('build','--run',run).returncode==0
    from mpe_cli import load_artifacts, load_fragments
    item=load_run(run)[0]
    (item['folder']/'review.json').write_text(json.dumps(approved(item['pack'],load_fragments(item),load_artifacts(item))))
    assert call('build','--run',run).returncode==0
    review=json.loads((item['folder']/'review.json').read_text())
    assert review['browser']['status']=='not_run'
    assert all(v['status']=='not_run' for v in review['independent']['items'].values())


def test_port_provenance_requires_git_repo(tmp_path):
    import subprocess, sys
    script = Path(__file__).resolve().parents[1] / 'scripts/port_provenance.py'
    r = subprocess.run([sys.executable, str(script), '--source', str(tmp_path)], capture_output=True, text=True)
    assert r.returncode != 0 and 'git' in r.stderr


def test_extract_warns_static_choices(tmp_path):
    repo = tmp_path / 'repo'
    source = choice_source_file(repo)
    result = call('extract', '--repo', repo, '--target', source, '--run', tmp_path / 'run')
    assert result.returncode == 0, result.stderr
    assert 'p1: 보기 모델 없음/불일치 — 정적 표시' in result.stderr


def published_pack(tmp_path):
    repo = tmp_path / 'repo'
    source = source_file(repo)
    run = tmp_path / 'run'
    assert call('extract', '--repo', repo, '--target', source, '--run', run).returncode == 0
    item = load_run(run)[0]
    for p in item['pack'].problems:
        (item['folder'] / 'explanations' / f'{p.id}.html').write_text(fragment(p), encoding='utf-8')
    (item['folder'] / 'evidence' / 'note.txt').write_text('검산 근거', encoding='utf-8')
    assert call('build', '--run', run).returncode == 0
    from mpe_cli import load_artifacts, load_fragments
    item = load_run(run)[0]
    reviews = approved(item['pack'], load_fragments(item), load_artifacts(item))
    (item['folder'] / 'review.json').write_text(json.dumps(reviews, ensure_ascii=False), encoding='utf-8')
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    return repo, source

def test_rerender_reuses_content_reviews(tmp_path):
    repo, source = published_pack(tmp_path)
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    assert result.returncode == 0, result.stderr
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    review = json.loads((folder / 'review.json').read_text())
    assert review['content']['status'] == 'pass' and review['independent']['status'] == 'pass'
    assert review['source_visual']['status'] == 'not_run' and review['browser']['status'] == 'not_run'
    assert {p.name for p in (folder / 'explanations').glob('*.html')} == {'p1.html'}
    assert (folder / 'evidence').is_dir() and any((folder / 'evidence').iterdir())
    assert 'source_visual·browser 재검토 필요' in result.stdout

def test_rerender_changed_source_keeps_reviews_unrun(tmp_path):
    repo, source = published_pack(tmp_path)
    source.write_text(source.read_text().replace('함수 결과를 구해요.', '함수 결과를 다시 구해요.'))
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    review = json.loads((folder / 'review.json').read_text())
    assert review['content']['status'] == 'not_run'
    assert '입력 변경: 네 검토 모두 다시 필요' in result.stdout

def test_rerender_without_published_fragments_fails(tmp_path):
    repo = tmp_path / 'repo'
    source = source_file(repo)
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run')
    assert result.returncode == 1 and '발행된 조각 없음' in result.stderr


def git_commit_all(repo):
    for args in (['init', '-q'], ['add', '-A'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'published']):
        subprocess.run(['git', *args], cwd=repo, check=True)

def test_rerender_style_only_source_change_reuses_reviews(tmp_path):
    repo, source = published_pack(tmp_path)
    git_commit_all(repo)
    source.write_text('<style>:root{--scroll:#ccc}</style>' + source.read_text())
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    assert result.returncode == 0, result.stderr
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    review = json.loads((folder / 'review.json').read_text())
    assert review['content']['status'] == 'pass' and review['independent']['status'] == 'pass'
    assert review['source_visual']['status'] == 'not_run'
    assert 'content·independent 재사용' in result.stdout and '문항 내용은 같아요' in result.stdout

def test_rerender_content_change_with_history_keeps_reviews_unrun(tmp_path):
    repo, source = published_pack(tmp_path)
    git_commit_all(repo)
    source.write_text(source.read_text().replace('함수 결과를 구해요.', '함수 결과를 다시 구해요.'))
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    assert json.loads((folder / 'review.json').read_text())['content']['status'] == 'not_run'
    assert '입력 변경: 네 검토 모두 다시 필요' in result.stdout
