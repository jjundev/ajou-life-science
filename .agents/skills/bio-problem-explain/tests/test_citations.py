"""Visible citations are omitted without changing the question or reviewed inputs."""
from dataclasses import replace
import pytest
from helpers import fragment, source_file
from mpe_source import load_source
from mpe_render import build_explanation, check_artifacts
from mpe_shared import parse

@pytest.mark.parametrize(('before', 'after'), [
    ('상동이에요(교재 7장 p.144).', '상동이에요.'),
    ('뷔퐁(교재 p.140 보충)이에요.', '뷔퐁이에요.'),
    ('확인해요 (강의노트 3장 p2, 교과서 3장 p.62).', '확인해요.'),
    ('관찰해요(p.145 그림 7.8).', '관찰해요.'),
    ('확인해요(강의노트 5장 PDF 7쪽).', '확인해요.'),
    ('확인해요(강의노트 3장 p4~p5).', '확인해요.'),
    ('같아요(강의노트 2장 p3도 같은 내용).', '같아요.'),
    ('그림(교재 4장 p.75, 그림 4.2b는 p.74)', '그림'),
    ('절(1.1.2, 인쇄 p.4–5)', '절'),
    ('보충(STT 1013·교재 p122 보충)', '보충'),
    ('단백질(p53)과 확률(0.5)은 유지해요.', '단백질(p53)과 확률(0.5)은 유지해요.'),
    ('단백질(교재 p.144, p53가 DNA 손상을 감지한다).', '단백질(p53가 DNA 손상을 감지한다).'),
    ('확률(교재 p.144, 0.5)', '확률(0.5)'),
    ('내용(교재 p.144 (그림 7.8))', '내용'),
    ('내용(교재 pp.144–145)', '내용'),
    ('수업 밖 내용이에요(교과서 4장 p.85, 수업 밖 보충).', '수업 밖 내용이에요(수업 밖 보충).'),
    ('ATP(산화적 인산화, 교과서 2장 p.42)', 'ATP(산화적 인산화)'),
    ('변화예요(교재 p.151, 변이가 없으면 적응하지 못할 수 있음).', '변화예요(변이가 없으면 적응하지 못할 수 있음).'),
    ('코돈(교과서 p.105: 코돈 5′-AGU-3′ ↔ 안티코돈 3′-UCA-5′)', '코돈(코돈 5′-AGU-3′ ↔ 안티코돈 3′-UCA-5′)'),
    ('비교해요(교재 그림 3.6의 사이클린 E, 사이클린 B).', '비교해요(사이클린 E, 사이클린 B).'),
    ('배열(강의노트 3장 p2 ‘중기: 염색체가 중간지점 배열’)', '배열(‘중기: 염색체가 중간지점 배열’)'),
    ('세포(원핵세포, prokaryotic cell), $p^2+2pq+q^2=1$', '세포(원핵세포, prokaryotic cell), $p^2+2pq+q^2=1$'),
])
def test_citations_omitted_from_html_and_md_only(tmp_path, before, after):
    repo = tmp_path / 'repo'
    path = source_file(repo)
    pack = load_source(path, repo)
    p = replace(pack.problems[0], conditions_html='<p>원문(교재 7장 p.144)</p>')
    pack = replace(pack, problems=(p,))
    raw = fragment(p).replace('</h4>', '</h4><p>' + before + '</p>', 1)
    result = build_explanation(pack, {'p1': raw}, tmp_path/'stage', repo)
    assert check_artifacts(pack, result) == []
    doc = parse(result.html.read_text())
    explanation = next(doc.find_all(lambda n: n.attrs.get('data-explanation') == 'recall'))
    assert after in explanation.text()
    assert after in result.md.read_text()
    assert '원문(교재 7장 p.144)' in result.html.read_text()
    assert (result.manifest.parent/'fragments/p1.html').read_text() == raw


def test_scoped_cleanup_preserves_markup_math_links_and_disclosures():
    from mpe_citations import clean_explanation_citations
    markup = '''<p>원문(교재 p.144)</p><div data-explanation="solve"><p>상동(교재 p.144).</p>
<a href="note.html#p144">개념(교재 p.144)</a><code>(교재 p.144)</code><p>$f(교재 p.144)$</p>
<p><strong>문항 결함:</strong> 수업 밖 보충(교과서 p.85).</p></div>
<div class="sum" hidden><ul><li>요약(교재 p.144).</li></ul></div>'''
    expected = markup.replace('상동(교재 p.144).', '상동.').replace('보충(교과서 p.85).', '보충.').replace('요약(교재 p.144).', '요약.').replace('개념(교재 p.144)</a>', '개념</a>')
    assert clean_explanation_citations(markup) == expected
    assert clean_explanation_citations(expected) == expected


def test_inline_tags_entities_and_wrapped_citations():
    from mpe_citations import clean_explanation_citations
    markup = '<div data-explanation="recall"><p>내용(교재&nbsp;p.144).</p><p>내용(교재 <em>p.144</em>).</p><p>내용(교재\np.144).</p><p>내용(교재 p.144, <a href="note.html#concept">정리노트</a>).</p></div>'
    cleaned = clean_explanation_citations(markup)
    assert parse(cleaned).text() == '내용.내용.내용.내용(정리노트).'
    assert '<em></em>' in cleaned
    assert '<a href="note.html#concept">정리노트</a>' in cleaned

@pytest.mark.parametrize(('before', 'after'), [
    ('확률(교재 p.144 0.5)', '확률(0.5)'),
    ('범위(p.4~p.5)', '범위'),
])
def test_numeric_conditions_and_unnamed_page_ranges(before, after):
    from mpe_citations import clean_citation_text
    assert clean_citation_text(before) == after


def test_citation_only_link_keeps_usable_label():
    from mpe_citations import clean_explanation_citations
    markup = '<div data-explanation="recall"><a href="note.html#concept">(교재 p.144)</a></div>'
    assert clean_explanation_citations(markup) == markup


def test_numeric_condition_without_separator_space():
    from mpe_citations import clean_citation_text
    assert clean_citation_text('확률(교재 p.144,0.5)') == '확률(0.5)'
