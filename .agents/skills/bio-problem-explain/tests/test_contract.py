from copy import deepcopy
from itertools import combinations
import pytest
from helpers import problem, fragment, pack
from mpe_contract import validate_fragment, validate_reviews, payload_hash
from mpe_shared import parse, outer

OPTIONAL_SECTIONS = ('start', 'pitfall', 'retry')


def without_sections(text, *keys):
    for node in parse(text).find_all(lambda n: n.attrs.get('data-explanation') in keys):
        text = text.replace(outer(node), '')
    return text


@pytest.mark.parametrize('included', [subset for size in range(4)
                                    for subset in combinations(OPTIONAL_SECTIONS, size)])
def test_optional_sections_can_be_omitted_independently(included):
    text = without_sections(fragment(), *(key for key in OPTIONAL_SECTIONS if key not in included))
    assert validate_fragment(problem(), text) == []


@pytest.mark.parametrize('key', ('understand', 'recall', 'solve', 'verify'))
def test_core_sections_remain_required_without_optional_sections(key):
    text = without_sections(fragment(), *OPTIONAL_SECTIONS, key)
    assert validate_fragment(problem(), text)


@pytest.mark.parametrize('key', OPTIONAL_SECTIONS)
def test_optional_sections_still_reject_duplicates_empty_bodies_and_wrong_order(key):
    text = fragment()
    block = outer(next(parse(text).find_all(lambda n: n.attrs.get('data-explanation') == key)))
    assert validate_fragment(problem(), text + block)
    empty = f'<div class="layer warn formal" data-explanation="{key}"><h4>제목뿐인 구역</h4></div>'
    assert validate_fragment(problem(), text.replace(block, empty))
    misplaced = text.replace(block, '')
    assert any('순서' in error for error in validate_fragment(problem(), block + misplaced))


def test_unknown_section_refused_even_when_core_is_complete():
    text = without_sections(fragment(), *OPTIONAL_SECTIONS)
    text += '<div class="layer formal" data-explanation="background"><p>배경</p></div>'
    assert validate_fragment(problem(), text)


def test_warning_layer_required_only_for_present_pitfall():
    text = fragment().replace('class="layer warn" data-explanation="pitfall"',
                              'class="layer formal" data-explanation="pitfall"')
    assert validate_fragment(problem(), text)
    assert validate_fragment(problem(), without_sections(text, 'pitfall')) == []

RECALL = ('<div class="layer formal" data-explanation="recall">'
          '<h4>이 문제를 봤을 때 떠올릴 개념과 공식</h4>'
          '<p>제곱을 구하라는 단서에서 같은 수의 곱을 떠올려요. '
          '$A^2=A\\cdot A$이며 A는 주어진 스칼라예요.</p></div>')

def with_recall():
    text = fragment()
    if 'data-explanation="recall"' not in text:
        text = text.replace('<div class="layer formal" data-explanation="start">',
                            RECALL + '<div class="layer formal" data-explanation="start">')
    return text

def test_recall_required_and_legacy_fragment_refused():
    from mpe_shared import parse, outer
    text = with_recall()
    assert validate_fragment(problem(), text) == []
    node = next(parse(text).find_all(lambda n: n.attrs.get('data-explanation') == 'recall'))
    assert validate_fragment(problem(), text.replace(outer(node), ''))

def test_recall_duplicate_empty_and_wrong_order_refused():
    from mpe_shared import parse, outer
    text = with_recall()
    node = next(parse(text).find_all(lambda n: n.attrs.get('data-explanation') == 'recall'))
    block = outer(node)
    assert validate_fragment(problem(), text + block)
    empty = '<div class="layer formal" data-explanation="recall"><h4>개념</h4></div>'
    assert any('recall' in e for e in validate_fragment(problem(), text.replace(block, empty)))
    wrong = text.replace(block, '').replace('<div class="layer formal" data-explanation="solve">',
                                           block + '<div class="layer formal" data-explanation="solve">')
    assert any('순서' in e for e in validate_fragment(problem(), wrong))

def test_recall_edit_invalidates_approval():
    before = fragment()
    changed = before.replace('제곱을 구하라는 단서', '곱셈을 요구하는 단서')
    assert changed != before
    assert validate_reviews(pack(), {'p1': changed}, reviews())

def test_nested_heading_only_recall_refused():
    from mpe_shared import parse, outer
    text = with_recall()
    block = outer(next(parse(text).find_all(lambda n: n.attrs.get('data-explanation') == 'recall')))
    nested = ('<div class="layer formal" data-explanation="recall">'
              '<div><h4>제목뿐인 개념 구역</h4></div></div>')
    assert any('recall' in e for e in validate_fragment(problem(), text.replace(block, nested)))

def reviews():
    from helpers import approved
    return approved(pack(), {'p1': fragment()})

def test_all_subparts_must_be_solved_and_verified():
    assert validate_fragment(problem(), fragment()) == []
    broken = fragment().replace('data-subpart="b"', 'data-subpart="a"', 1)
    assert any('소문항' in e for e in validate_fragment(problem(), broken))

@pytest.mark.parametrize('markup', ['<details>답</details>', '<p hidden>답</p>', '<script>alert(1)</script>',
                                    '<img src="x" onerror="x">', '<a href="javascript:alert(1)">x</a>',
                                    '<p style="display:none">답</p>', '<iframe src="x"></iframe>'])
def test_hidden_or_active_explanation_refused(markup):
    assert validate_fragment(problem(), fragment() + markup)

def test_retry_and_missing_sections_refused():
    assert validate_fragment(problem(), fragment().replace('data-explanation="start"', 'data-explanation="solve"'))
    assert validate_fragment(problem(), fragment().replace('<li>다시 계산해요.</li>', ''))

def test_unreviewed_or_stale_or_incomplete_reports_refused():
    assert validate_reviews(pack(), {'p1': fragment()}, {})
    good = reviews()
    assert validate_reviews(pack(), {'p1': fragment()}, good) == []
    assert validate_reviews(pack(), {'p1': fragment() + '변경'}, good)
    for kind in ('source_visual', 'browser', 'content', 'independent'):
        bad = deepcopy(good)
        bad[kind]['status'] = 'not_run'
        assert validate_reviews(pack(), {'p1': fragment()}, bad)
    bad = deepcopy(good)
    del bad['independent']['items']['p1:b']
    assert validate_reviews(pack(), {'p1': fragment()}, bad)

def test_numerical_residual_requires_real_bounds():
    good = reviews()
    item = good['independent']['items']['p1:a']
    item.update(method='numerical', tolerance=1e-8, residual=1e-9)
    assert validate_reviews(pack(), {'p1': fragment()}, good) == []
    item['residual'] = 1
    assert validate_reviews(pack(), {'p1': fragment()}, good)
    item['residual'] = float('nan')
    assert validate_reviews(pack(), {'p1': fragment()}, good)

def test_code_dollar_is_not_math():
    text = fragment() + '<pre><code>printf("$%d", n);</code></pre>'
    assert validate_fragment(problem(), text) == []
    assert validate_fragment(problem(), text+'<p>$oops</p>')

def test_disputed_reviews_rejected():
    good=reviews(); good['content']['items']['p1:a']['status']='disputed'
    assert validate_reviews(pack(), {'p1':fragment()},good)
