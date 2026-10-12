from pathlib import Path
import unicodedata
import pytest
from mpe_source import load_source, resolve_sources, subparts
from mpe_shared import parse
from mpe_types import ExplainError
from helpers import source_file

def test_legacy_problem_preserves_code(tmp_path):
    path = source_file(tmp_path)
    before = path.read_bytes()
    p = load_source(path, tmp_path).problems[0]
    assert p.ask_html == '' and p.subparts == ('main',)
    assert next(parse(p.conditions_html).find_all(lambda n: n.tag == 'code')).text() == 'printf("$%d", n);'
    assert path.read_bytes() == before
    assert p.figures_html == ()

def test_empty_latest_does_not_fallback(tmp_path):
    source_file(tmp_path, '0917')
    empty = source_file(tmp_path, '1008', empty=True)
    assert resolve_sources(tmp_path, None) == (empty,)
    with pytest.raises(ExplainError, match='문항 없음.*',): load_source(empty, tmp_path)

def test_question_vs_operation_lists():
    assert subparts('<ol><li>(a) 값을 구하라<ol><li>push</li><li>pop</li></ol></li><li>(b) 복잡도를 구하라</li></ol>', '') == ('a', 'b')
    assert subparts('<p>다음 연산을 수행한다.</p><ol><li>push</li><li>pop</li></ol><p>최종 상태는?</p>', '') == ('main',)

def test_ambiguous_subparts_block():
    with pytest.raises(ExplainError, match='소문항'): subparts('<ol><li>값을 구하라</li><li>복잡도를 구하라</li></ol>', '')

def test_duplicate_card_ids(tmp_path):
    path = source_file(tmp_path)
    text = path.read_text(); card = text[text.index('<article'):text.index('</article>')+10]
    path.write_text(text.replace('</section>', card+'</section>'))
    with pytest.raises(ExplainError, match='duplicate'): load_source(path,tmp_path)

def test_nfd_target(tmp_path):
    path=source_file(tmp_path)
    assert resolve_sources(tmp_path, unicodedata.normalize('NFD',str(path)))[0].samefile(path)

def test_multiple_slugs_require_path(tmp_path):
    source_file(tmp_path); source_file(tmp_path,slug='Other')
    with pytest.raises(ExplainError,match='여러 후보'): resolve_sources(tmp_path,'0917')

def test_range_conflict(tmp_path):
    for date in ('0914','0917','0914-0917'): source_file(tmp_path,date)
    with pytest.raises(ExplainError,match='여러 후보'): resolve_sources(tmp_path,'0914-0917')

@pytest.mark.parametrize('target',['hw1','과제1','1330','0930-0909'])
def test_invalid_target(tmp_path,target):
    with pytest.raises(ExplainError): resolve_sources(tmp_path,target)

def test_source_outside_repo(tmp_path):
    path=source_file(tmp_path/'outside')
    (tmp_path/'repo').mkdir()
    with pytest.raises(ExplainError,match='저장소'):load_source(path,tmp_path/'repo')


def test_distinct_cards_can_share_exam_source(tmp_path):
    path=source_file(tmp_path)
    text=path.read_text();card=text[text.index('<article'):text.index('</article>')+10]
    path.write_text(text.replace('</section>',card.replace('id="p1"','id="p2"')+'</section>'))
    assert [p.id for p in load_source(path,tmp_path).problems]==['p1','p2']

def test_original_subparts_cannot_be_silently_collapsed():
    with pytest.raises(ExplainError,match='소문항'):
        subparts('<p>두 값을 계산해요.</p>', '<div class="part">(a) 첫째</div><div class="part">(b) 둘째</div>')

def test_paragraph_question_labels():
    assert subparts('<p>(a) 결과를 구하라</p><p>(b) 복잡도를 구하라</p>', '') == ('a','b')

def test_lettered_operation_list_is_single_question():
    assert subparts('<p>다음 연산을 실행한다.</p><ol><li>(a) push(1)</li><li>(b) pop()</li></ol><p>최종 상태를 구하라.</p>', '') == ('main',)
