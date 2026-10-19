import json
import re
from urllib.parse import unquote
from dataclasses import replace
import pytest
from forecast_helpers import forecast_source_file
from helpers import fragment, approved
from test_cli import call
from mpe_cli import load_run, load_artifacts, load_fragments
from mpe_source import load_source
from mpe_render import build_explanation, names, check_artifacts
from mpe_publish import publish_explanation
from mpe_contract import payload_hash
from mpe_types import ExplainError


def build_run(tmp_path, version=5, core_only=False):
    repo = tmp_path / 'repo'
    source = forecast_source_file(repo, version=version)
    run = tmp_path / f'run-v{version}'
    result = call('extract', '--repo', repo, '--target', source, '--run', run)
    assert result.returncode == 0, result.stderr
    item = load_run(run)[0]
    for p in item['pack'].problems:
        (item['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p, core_only=core_only))
    result = call('build', '--run', run)
    assert result.returncode == 0, result.stderr
    return source, run, load_run(run)[0]


def approve(item):
    review = approved(item['pack'], load_fragments(item), load_artifacts(item))
    (item['folder']/'review.json').write_text(json.dumps(review))
    return review


@pytest.mark.parametrize('core_only', [False, True])
def test_forecast_cli_round_trip(tmp_path, core_only):
    source, run, item = build_run(tmp_path, core_only=core_only)
    before = source.read_bytes()
    assert names(item['pack']) == ('문제해설_4장_웹과제예상_v5', '.pack/figures_문제해설_4장_웹과제예상_v5', '.pack/자료_문제해설_4장_웹과제예상_v5')
    artifacts = load_artifacts(item)
    text = artifacts.html.read_text()
    assert '생명과학 4장 웹과제 예상 v5 문제해설' in text
    assert 'bio-problem-explain-forecast-4장-웹과제예상_v5' in text
    assert call('check', '--run', run).returncode == 0
    assert call('publish', '--run', run).returncode == 1
    approve(item)
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    for name in ('문제해설_4장_웹과제예상_v5.html', '.pack/문제해설_4장_웹과제예상_v5.md', '.pack/자료_문제해설_4장_웹과제예상_v5/validation.json'):
        assert (source.parent/name).is_file()
    assert source.read_bytes() == before


@pytest.mark.parametrize('name', ['pack.json', 'blueprint.md'])
def test_changed_forecast_context_requires_reextract(tmp_path, name):
    source, run, item = build_run(tmp_path)
    approve(item)
    path = source.parent/'.pack/v5'/name
    path.write_text(path.read_text()+'\n')
    for command in ('check', 'publish'):
        result = call(command, '--run', run)
        assert result.returncode == 1 and '추출' in result.stderr


@pytest.mark.parametrize('name', ['pack.json', 'blueprint.md'])
def test_direct_publish_rejects_changed_context(tmp_path, name):
    source, run, item = build_run(tmp_path)
    artifacts, fragments = load_artifacts(item), load_fragments(item)
    reviews = approve(item)
    path = source.parent/'.pack/v5'/name
    path.write_text(path.read_text()+'\n')
    with pytest.raises(ExplainError, match='문맥'):
        publish_explanation(item['pack'], artifacts, fragments, reviews, source.parent, tmp_path/'backup')
    assert not (source.parent/'문제해설_4장_웹과제예상_v5.html').exists()


def test_rebuild_resets_reviews_and_blocks_stale_pass(tmp_path):
    source, run, item = build_run(tmp_path)
    stale = approve(item)
    part = item['folder']/'explanations/p1.html'
    part.write_text(part.read_text().replace('구할 것을 읽어요.', '고친 조건을 읽어요.'))
    assert call('build', '--run', run).returncode == 0
    current = json.loads((item['folder']/'review.json').read_text())
    assert all(current[k]['status'] == 'not_run' for k in ('source_visual', 'content', 'independent', 'browser'))
    (item['folder']/'review.json').write_text(json.dumps(stale))
    assert call('publish', '--run', run).returncode == 1
    assert not (source.parent/'문제해설_4장_웹과제예상_v5.html').exists()
    approve(load_run(run)[0])
    assert call('publish', '--run', run).returncode == 0


def test_disputed_cannot_publish(tmp_path):
    source, run, item = build_run(tmp_path)
    review = approve(item)
    review['independent']['items']['p1:main']['status'] = 'disputed'
    (item['folder']/'review.json').write_text(json.dumps(review))
    assert call('publish', '--run', run).returncode == 1


def test_new_versions_have_distinct_names_and_state_keys(tmp_path):
    source5, run5, item5 = build_run(tmp_path, 5)
    approve(item5)
    assert call('publish', '--run', run5).returncode == 0
    output = source5.parent/'문제해설_4장_웹과제예상_v5.html'
    before = output.read_bytes()
    source6, run6, item6 = build_run(tmp_path, 6)
    approve(item6)
    assert call('publish', '--run', run6).returncode == 0
    assert output.read_bytes() == before
    assert 'bio-problem-explain-forecast-4장-웹과제예상_v6' in (source6.parent/'문제해설_4장_웹과제예상_v6.html').read_text()


def test_context_bound_to_payload_and_manifest(tmp_path):
    source, run, item = build_run(tmp_path)
    pack, fragments, artifacts = item['pack'], load_fragments(item), load_artifacts(item)
    changed = replace(pack, context_hashes=((pack.context_hashes[0][0], '0'*64), *pack.context_hashes[1:]))
    assert payload_hash(pack, fragments) != payload_hash(changed, fragments)
    manifest = json.loads(artifacts.manifest.read_text())
    assert manifest['context_hashes'] == [list(pair) for pair in pack.context_hashes]
    assert any('문맥' in error for error in check_artifacts(changed, artifacts))


def test_real_forecast_build_check_repair_and_reextract(tmp_path):
    import subprocess
    import sys
    from pathlib import Path
    from forecast_helpers import forecast_acceptance_source
    source = forecast_acceptance_source(tmp_path/'repo')
    forecast = Path(__file__).resolve().parents[2]/'bio-webquiz-forecast/scripts'
    src = source.parent/'.pack/v5'
    for script, target in [('build.py', src), ('check.py', source)]:
        result = subprocess.run([sys.executable, str(forecast/script), str(target)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout+result.stderr
    repo = tmp_path/'repo'
    run = tmp_path/'explain-1'
    assert call('extract', '--repo', repo, '--target', source, '--run', run).returncode == 0
    item = load_run(run)[0]
    for p in item['pack'].problems:
        (item['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p))
    bad = item['folder']/'explanations/p1.html'
    good = bad.read_text()
    bad.write_text(good.replace('data-explanation="verify"', 'data-explanation="wrong"'))
    assert call('build', '--run', run).returncode == 1
    bad.write_text(good)
    assert call('build', '--run', run).returncode == 0
    assert call('check', '--run', run).returncode == 0
    approve(item)
    # Original question condition changes, consistent with source cards and blueprint.
    card = src/'cards/p1.html'
    card.write_text(card.read_text().replace('$1+1$', '$2+0$'))
    blueprint = src/'blueprint.md'
    blueprint.write_text(blueprint.read_text()+'\n조건 수리: p1 $2+0$\n')
    assert subprocess.run([sys.executable, str(forecast/'build.py'), str(src)], capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, str(forecast/'check.py'), str(source)], capture_output=True).returncode == 0
    assert call('publish', '--run', run).returncode == 1
    new_run = tmp_path/'explain-2'
    assert call('extract', '--repo', repo, '--target', source, '--run', new_run).returncode == 0
    fresh = load_run(new_run)[0]
    assert '$2+0$' in fresh['pack'].problems[0].conditions_html
    for p in fresh['pack'].problems:
        (fresh['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p))
    assert call('build', '--run', new_run).returncode == 0
    assert call('publish', '--run', new_run).returncode == 1
    approve(fresh)
    assert call('publish', '--run', new_run).returncode == 0
    assert (source.parent/'문제해설_4장_웹과제예상_v5.html').is_file()


def test_forecast_source_info_is_not_labelled_past_exam_original(tmp_path):
    source, run, item = build_run(tmp_path)
    source.write_text(source.read_text().replace('<details class="solution">', '<details class="original"><summary>원문 정보</summary>새 예상문제의 근거 안내예요.</details><details class="solution">', 1))
    pack = load_source(source, tmp_path/'repo')
    fragments = {p.id: fragment(p) for p in pack.problems}
    artifacts = build_explanation(pack, fragments, tmp_path/'info-stage', tmp_path/'repo')
    text = artifacts.html.read_text()
    assert '<summary>원문·출처 정보 보기</summary>' in text
    assert '기출 원문 보기' not in text


def test_forecast_side_files_live_in_pack(tmp_path):
    source, run, item = build_run(tmp_path)
    artifacts = load_artifacts(item)
    root = artifacts.html.parent
    assert artifacts.md.parent == root / '.pack'
    assert not (root / '.assets').exists()
    html = artifacts.html.read_text(encoding='utf-8')
    assert 'href=".pack/자료_문제해설_4장_웹과제예상_v5/vendor/katex/katex.min.css"' in html
    md = artifacts.md.read_text(encoding='utf-8')
    assert '](.pack/' not in md
    for target in re.findall(r'\]\((\.\./[^)]+)\)', md):
        if target.startswith('../../'):  # 장 폴더 밖 링크는 .pack 기준으로 한 단계 더 올라간다
            assert target.startswith('../../../'), target
        else:  # 같은 장 폴더의 HTML
            path = unquote(target.split('#')[0])
            assert '/' not in path[3:] and (source.parent / path[3:]).is_file(), target


def test_forecast_publish_keeps_root_clean_and_sources_intact(tmp_path):
    source, run, item = build_run(tmp_path)
    pack_json = source.parent / '.pack' / 'v5' / 'pack.json'
    before = pack_json.read_bytes()
    approve(item)
    result = call('publish', '--run', run)
    assert result.returncode == 0, result.stderr
    root = sorted(p.name for p in source.parent.iterdir())
    assert all(n == '.pack' or n.endswith('.html') for n in root), root
    assert pack_json.read_bytes() == before
