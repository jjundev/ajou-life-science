import json
import re
import unicodedata
import pytest
from forecast_helpers import forecast_source_file
from helpers import source_file
from mpe_source import load_source, resolve_sources
from mpe_types import ExplainError


def test_forecast_extracts_fifteen_and_preserves_input(tmp_path):
    source = forecast_source_file(tmp_path)
    before = source.read_bytes()
    pack = load_source(source, tmp_path)
    assert (pack.profile, pack.range, pack.slug) == ('forecast', '4장', '웹과제예상_v5')
    assert [p.id for p in pack.problems] == [f'p{i}' for i in range(1, 16)]
    assert all(p.subparts == ('main',) for p in pack.problems)
    assert len(pack.context_hashes) == 2
    assert source.read_bytes() == before


@pytest.mark.parametrize('bad', ['o3', 'q1', 'p16', 'p1'])
def test_only_known_overviews_and_unique_questions(tmp_path, bad):
    source = forecast_source_file(tmp_path)
    source.write_text(source.read_text().replace('id="o2"', f'id="{bad}"'))
    with pytest.raises(ExplainError, match='카드'):
        load_source(source, tmp_path)


def test_missing_question_rejected(tmp_path):
    source = forecast_source_file(tmp_path)
    source.write_text(re.sub(r'<article class="card" id="p15".*?</article>', '', source.read_text()))
    with pytest.raises(ExplainError, match='카드'):
        load_source(source, tmp_path)


@pytest.mark.parametrize('field,value', [('chapter', 3), ('version', 6), ('chapter', True), ('version', '5'), ('problems', [{'id': 'p1'}]), ('answer_key', {'p1': 'A'})])
def test_manifest_identity_and_key_mismatch_rejected(tmp_path, field, value):
    source = forecast_source_file(tmp_path)
    path = source.parent / '.pack/v5/pack.json'
    manifest = json.loads(path.read_text())
    manifest[field] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ExplainError):
        load_source(source, tmp_path)


@pytest.mark.parametrize('old,new', [('data-correct="A"', 'data-correct="B"'), ('정답: A', '정답: B')])
def test_card_key_mismatch_rejected(tmp_path, old, new):
    source = forecast_source_file(tmp_path)
    source.write_text(source.read_text().replace(old, new, 1))
    with pytest.raises(ExplainError, match='정답'):
        load_source(source, tmp_path)


def test_forecast_nfd_path(tmp_path):
    source = forecast_source_file(tmp_path)
    target = unicodedata.normalize('NFD', str(source))
    assert load_source(resolve_sources(tmp_path, target)[0], tmp_path).profile == 'forecast'


def test_forecast_not_selected_by_all_or_default(tmp_path):
    forecast_source_file(tmp_path)
    review = source_file(tmp_path)
    assert resolve_sources(tmp_path, 'all') == (review,)
    assert resolve_sources(tmp_path, None) == (review,)


def test_forecast_preserves_choices_original_svg_and_table(tmp_path):
    source = forecast_source_file(tmp_path)
    extra = '<svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg><table><tr><td>조건</td></tr></table>'
    original = '<details class="original"><summary>원문</summary><blockquote>original wording</blockquote></details>'
    source.write_text(source.read_text().replace('<p>맞는 보기는?</p>', '<p>맞는 보기는?</p>'+extra, 1).replace('<details class="solution">', original+'<details class="solution">', 1))
    problem = load_source(source, tmp_path).problems[0]
    assert all(s in problem.conditions_html for s in ('viewBox=', '<table>', '합성 보기 E', '맞는 보기는?'))
    assert problem.original_html == '<blockquote>original wording</blockquote>'


@pytest.mark.parametrize('name', ['pack.json', 'blueprint.md'])
def test_missing_manifest_or_blueprint_rejected(tmp_path, name):
    source = forecast_source_file(tmp_path)
    (source.parent/'.pack/v5'/name).unlink()
    with pytest.raises(ExplainError):
        load_source(source, tmp_path)


def test_wrong_folder_rejected(tmp_path):
    source = forecast_source_file(tmp_path)
    misplaced = source.parent.parent / source.name
    misplaced.write_bytes(source.read_bytes())
    with pytest.raises(ExplainError):
        load_source(misplaced, tmp_path)


def test_actual_forecast_without_data_correct_is_supported(tmp_path):
    source = forecast_source_file(tmp_path)
    source.write_text(re.sub(r' data-correct="[A-E]"', '', source.read_text()))
    assert len(load_source(source, tmp_path).problems) == 15


@pytest.mark.parametrize('answer', ['정답: A 또는 B', '정답: A. 정답: B', '정답: A B', '정답: A (B도 정답)'])
def test_ambiguous_answer_is_rejected(tmp_path, answer):
    source = forecast_source_file(tmp_path)
    source.write_text(source.read_text().replace('정답: A', answer, 1))
    with pytest.raises(ExplainError, match='정답'):
        load_source(source, tmp_path)


def test_forecast_choice_model_letters(tmp_path):
    source = forecast_source_file(tmp_path)
    key = json.loads((source.parent / '.pack/v5/pack.json').read_text())['answer_key']
    choice = load_source(source, tmp_path).problems[0].choice
    assert choice.option_ids == ('A', 'B', 'C', 'D', 'E')
    assert choice.answer == key['p1']


def test_old_src_layout_rejected(tmp_path):
    source = forecast_source_file(tmp_path)
    old = source.parent / 'src'
    old.mkdir()
    (source.parent / '.pack' / 'v5').rename(old / 'v5')
    with pytest.raises(ExplainError):
        load_source(source, tmp_path)
