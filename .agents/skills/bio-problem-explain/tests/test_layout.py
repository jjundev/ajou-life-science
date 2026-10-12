from helpers import source_file, fragment
from mpe_source import load_source
from mpe_render import build_explanation

def test_layout_fixture_retains_code_table_math_svg(tmp_path):
    source=source_file(tmp_path/'repo');pack=load_source(source,tmp_path/'repo');p=pack.problems[0]
    body=fragment(p)+'<table><tr><th>연산</th><th>상태</th></tr><tr><td>push(1)</td><td>[1]</td></tr></table><svg viewBox="0 0 20 20"><rect width="10" height="10"/></svg>'
    result=build_explanation(pack,{'p1':body},tmp_path/'stage',tmp_path/'repo')
    text=result.html.read_text()
    assert 'push(1)' in text and 'printf("$%d", n);' in text and 'viewBox' in text

def test_acceptance_fixture_has_full_content(tmp_path):
    from helpers import acceptance_pack
    pack, fragments=acceptance_pack(tmp_path/'repo')
    assert pack.problems[0].subparts==('a','b')
    assert '&amp;' in pack.problems[0].conditions_html
    text=fragments['p1']
    for token in ['<table','<svg','<img','data-subpart="a"','data-subpart="b"','summary-group']:
        assert token in text
