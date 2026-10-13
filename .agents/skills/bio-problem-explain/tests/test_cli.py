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


PNG = __import__('base64').b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII=')

def published_pack(tmp_path, reference=None, name='참조.html', figure=False):
    repo = tmp_path / 'repo'
    source = source_file(repo)
    if figure:
        source.write_text(source.read_text().replace('</p><pre>', '</p><img src="figures_0917/p1.png" alt="문제 그림"><pre>'))
        (source.parent / 'figures_0917').mkdir()
        (source.parent / 'figures_0917/p1.png').write_bytes(PNG)
    if reference:
        (repo / name).write_text(reference, encoding='utf-8')
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
    if reference:
        import hashlib
        ref = (repo / name).resolve()
        reviews['references'] = [{'path': str(ref), 'sha256': hashlib.sha256(ref.read_bytes()).hexdigest()}]
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


def rerendered_review(tmp_path, repo, source):
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    assert result.returncode == 0, result.stderr
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    return json.loads((folder / 'review.json').read_text()), result

def test_rerender_rebases_reference_paths_to_current_checkout(tmp_path):
    import shutil
    repo, source = published_pack(tmp_path, reference='<p>본문</p>')
    moved = tmp_path / 'moved'
    shutil.copytree(repo, moved)
    review, _ = rerendered_review(tmp_path, moved, moved / source.relative_to(repo))
    assert review['content']['status'] == 'pass'
    assert review['references'][0]['path'] == str((moved / '참조.html').resolve())

def test_rerender_reference_style_only_change_updates_hash(tmp_path):
    import hashlib
    repo, source = published_pack(tmp_path, reference='<style>a{color:red}</style><p>본문</p>')
    git_commit_all(repo)
    ref = repo / '참조.html'
    ref.write_text('<style>a{color:blue}</style><p>본문</p>', encoding='utf-8')
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'][0]['sha256'] == hashlib.sha256(ref.read_bytes()).hexdigest()
    assert '참조 자료는 스타일·스크립트·자산 경로만 바뀌었어요: 참조.html' in result.stdout

def test_rerender_reference_content_change_keeps_old_hash(tmp_path):
    repo, source = published_pack(tmp_path, reference='<style>a{color:red}</style><p>본문</p>')
    git_commit_all(repo)
    ref = repo / '참조.html'
    before = json.loads(next((repo / '복습노트/0917').glob('.assets/자료_*/validation.json')).read_text())['references'][0]['sha256']
    ref.write_text('<style>a{color:red}</style><p>바뀐 본문</p>', encoding='utf-8')
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'][0]['sha256'] == before
    assert '참조 자료 변경: 검토를 다시 하세요: 참조.html' in result.stdout


def test_rerender_review_keeps_side_files_under_assets(tmp_path):
    repo, source = published_pack(tmp_path)
    folder = source.parent
    run = tmp_path / 'run2'
    result = call('rerender', '--repo', repo, '--target', source, '--run', run)
    assert result.returncode == 0, result.stderr
    from mpe_cli import load_artifacts, load_fragments
    item = load_run(run)[0]
    artifacts = load_artifacts(item)
    stage = artifacts.html.parent
    assert artifacts.md.parent == stage / '.assets'
    assert sorted(p.name for p in stage.iterdir()) == ['.assets', artifacts.html.name]
    (item['folder'] / 'review.json').write_text(json.dumps(approved(item['pack'], load_fragments(item), artifacts), ensure_ascii=False), encoding='utf-8')
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    stem = artifacts.html.stem
    assert sorted(p.name for p in folder.iterdir()) == sorted(['.assets', source.name, f'{stem}.html'])
    side = folder / '.assets'
    assert (side / f'{stem}.md').read_bytes() == artifacts.md.read_bytes()
    assert '](.assets/' not in (side / f'{stem}.md').read_text(encoding='utf-8')
    data = side / '자료_문제설명_0917_Recursion'
    assert (data / 'validation.json').is_file() and (data / 'fragments' / 'p1.html').is_file()
    assert any((data / 'evidence').iterdir())


def assets_move(repo, figure=None, reference=None, text=None):
    """Replay the .assets migration for one side folder or file of 복습노트/0917."""
    day = repo / '복습노트/0917'
    (day / '.assets').mkdir(exist_ok=True)
    if figure:
        (day / figure).rename(day / '.assets' / figure)
    if reference:
        (day / reference).rename(day / '.assets' / reference)
        if text is not None:
            (day / '.assets' / reference).write_text(text, encoding='utf-8')
    return day

def approve_and_publish(tmp_path, run):
    from mpe_cli import load_artifacts, load_fragments
    item = load_run(run)[0]
    review = json.loads((item['folder'] / 'review.json').read_text())
    fresh = approved(item['pack'], load_fragments(item), load_artifacts(item))
    review.update(source_visual=fresh['source_visual'], browser=fresh['browser'])
    (item['folder'] / 'review.json').write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
    assert call('check', '--run', run).returncode == 0
    return call('publish', '--run', run)

@pytest.mark.parametrize('prefix', ['.assets/', './.assets/'])
def test_rerender_problem_figure_moved_to_assets_reuses_reviews(tmp_path, prefix):
    repo, source = published_pack(tmp_path, figure=True)
    git_commit_all(repo)
    assets_move(repo, figure='figures_0917')
    source.write_text(source.read_text().replace('src="figures_0917/', f'src="{prefix}figures_0917/'))
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['content']['status'] == 'pass' and review['independent']['status'] == 'pass'
    assert '문항 내용은 같아요' in result.stdout
    result = approve_and_publish(tmp_path, tmp_path / 'run2')
    assert result.returncode == 0, result.stderr

def test_rerender_problem_figure_retargeted_keeps_reviews_unrun(tmp_path):
    repo, source = published_pack(tmp_path, figure=True)
    git_commit_all(repo)
    (source.parent / 'figures_0917/p2.png').write_bytes(PNG)
    source.write_text(source.read_text().replace('src="figures_0917/p1.png"', 'src=".assets/figures_0917/p2.png"'))
    assets_move(repo, figure='figures_0917')
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    assert json.loads((folder / 'review.json').read_text())['content']['status'] == 'not_run'
    assert '입력 변경: 네 검토 모두 다시 필요' in result.stdout

def test_rerender_reference_assets_href_only_change_updates_hash(tmp_path):
    import hashlib
    name = '복습노트/0917/정리노트_0917_Recursion.html'
    repo, source = published_pack(tmp_path, reference='<a href="장마감_0917_1장.md">장마감</a><img src="./figures_0917/a.png">', name=name)
    git_commit_all(repo)
    ref = repo / name
    ref.write_text('<a href=".assets/장마감_0917_1장.md">장마감</a><img src="./.assets/figures_0917/a.png">', encoding='utf-8')
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'][0]['sha256'] == hashlib.sha256(ref.read_bytes()).hexdigest()
    assert '자산 경로만 바뀌었어요: 정리노트_0917_Recursion.html' in result.stdout
    assert approve_and_publish(tmp_path, tmp_path / 'run2').returncode == 0

def test_rerender_reference_assets_text_outside_url_is_a_change(tmp_path):
    name = '복습노트/0917/정리노트_0917_Recursion.html'
    repo, source = published_pack(tmp_path, reference='<p>그림은 figures_0917에 있어요</p>', name=name)
    git_commit_all(repo)
    (repo / name).write_text('<p>그림은 .assets/figures_0917에 있어요</p>', encoding='utf-8')
    _, result = rerendered_review(tmp_path, repo, source)
    assert '참조 자료 변경: 검토를 다시 하세요: 정리노트_0917_Recursion.html' in result.stdout

INTERACTION = ('<!-- review-interaction:start -->\n<style>.x{}</style>\n'
               '<script id="review-interaction-model" type="application/json">{"cards": {"p1": {"answer": "%s"}}}</script>\n'
               '<script>\nfunction resolveExportDir(root) { return child(root, %s); }\n</script>\n'
               '<script>start();</script>\n<!-- review-interaction:end -->\n')

def test_rerender_reference_interaction_script_only_change_updates_hash(tmp_path):
    import hashlib
    name = '복습노트/0917/복습문제_참조.html'
    repo, source = published_pack(tmp_path, reference='<p>본문</p>' + INTERACTION % ('2', "'풀이기록'"), name=name)
    git_commit_all(repo)
    ref = repo / name
    ref.write_text('<p>본문</p>' + INTERACTION % ('2', "'.assets', '풀이기록'"), encoding='utf-8')
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'][0]['sha256'] == hashlib.sha256(ref.read_bytes()).hexdigest()
    assert '스타일·스크립트·자산 경로만 바뀌었어요: 복습문제_참조.html' in result.stdout

def test_rerender_reference_answer_model_change_keeps_old_hash(tmp_path):
    name = '복습노트/0917/복습문제_참조.html'
    repo, source = published_pack(tmp_path, reference='<p>본문</p>' + INTERACTION % ('2', "'풀이기록'"), name=name)
    git_commit_all(repo)
    (repo / name).write_text('<p>본문</p>' + INTERACTION % ('3', "'풀이기록'"), encoding='utf-8')
    _, result = rerendered_review(tmp_path, repo, source)
    assert '참조 자료 변경: 검토를 다시 하세요: 복습문제_참조.html' in result.stdout

MD = '[정리노트](정리노트_0917_Recursion.html#s) ![그림](figures_0917/a.png) [다른 날](../0915/장마감_0915_2장.md)\n'

def moved_md_pack(tmp_path):
    name = '복습노트/0917/정리노트_0917_Recursion.md'
    repo, source = published_pack(tmp_path, reference=MD, name=name)
    git_commit_all(repo)
    return repo, source, name

def test_rerender_reference_md_moved_to_assets_follows_it(tmp_path):
    import hashlib
    from mpe_shared import migrate_md
    repo, source, name = moved_md_pack(tmp_path)
    moved = assets_move(repo, reference=Path(name).name, text=migrate_md(MD)) / '.assets' / Path(name).name
    assert moved.read_text(encoding='utf-8') != MD
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'] == [{'path': str(moved), 'sha256': hashlib.sha256(moved.read_bytes()).hexdigest()}]
    assert '참조 자료는 .assets/로 옮겨졌을 뿐이에요: 정리노트_0917_Recursion.md' in result.stdout
    result = approve_and_publish(tmp_path, tmp_path / 'run2')
    assert result.returncode == 0, result.stderr

def test_rerender_reference_md_moved_and_edited_needs_review(tmp_path):
    from mpe_shared import migrate_md
    repo, source, name = moved_md_pack(tmp_path)
    assets_move(repo, reference=Path(name).name, text=migrate_md(MD) + '추가 문단\n')
    review, result = rerendered_review(tmp_path, repo, source)
    assert review['references'][0]['path'] == str(repo / name)
    assert '참조 자료 변경: 검토를 다시 하세요: .assets/정리노트_0917_Recursion.md' in result.stdout

def test_rerender_reference_missing_is_reported(tmp_path):
    repo, source, name = moved_md_pack(tmp_path)
    (repo / name).unlink()
    _, result = rerendered_review(tmp_path, repo, source)
    assert '참조 자료 없음: 검토를 다시 하세요: 정리노트_0917_Recursion.md' in result.stdout
