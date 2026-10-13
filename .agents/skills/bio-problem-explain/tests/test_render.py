from dataclasses import replace
import json, re, base64, hashlib
from pathlib import Path
import pytest
from urllib.parse import unquote
from helpers import fragment, source_file
from mpe_source import load_source, sha256
from mpe_shared import parse
from mpe_types import ExplainError
from mpe_render import build_explanation, check_artifacts, names

def make(tmp_path):
    source=source_file(tmp_path/'repo');pack=load_source(source,tmp_path/'repo')
    p=pack.problems[0]
    return pack,{p.id:fragment(p)}

def test_legacy_statement_rendered_once(tmp_path):
    pack,fragments=make(tmp_path)
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    text=result.html.read_text();md=result.md.read_text()
    assert text.count('printf("$%d", n);')==1
    assert '구할 것</h4>' not in text
    assert 'printf("$%d", n);' in md
    assert 'bio-problem-explain-review-0917-Recursion' in text
    assert '생명과학 복습 0917 문제설명' in text
    assert '자료구조' not in text
    assert result.html.name=='문제설명_0917_Recursion.html'
    assert '이 문제를 봤을 때 떠올릴 개념과 공식' in md
    assert not list(parse(text).find_all(lambda n:n.tag=='details'))
    assert 'https://cdn.' not in text

def test_template_bytes_match_provenance():
    template=Path(__file__).resolve().parents[1]/'assets/note-template.html'
    provenance=json.loads((template.parent/'port-provenance.json').read_text())
    entry=next(e for e in provenance['files'] if e['destination']=='assets/note-template.html')
    assert hashlib.sha256(template.read_bytes()).hexdigest()==entry['destination_sha256']
    assert entry['source_path']=='assets/note-template.html' and entry['change_reason']=='biology course adaptation'

def test_template_scrollbar_uses_theme_tokens():
    text=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    assert len(re.findall(r'--scroll: #[0-9a-f]{6}; --scroll-hover: #[0-9a-f]{6};',text))==3
    for s in ('--scroll: #c9d0db; --scroll-hover: #9aa3b2;','--scroll: #3f414b; --scroll-hover: #5b5e6a;',
              '.panel-inner::-webkit-scrollbar-thumb { background: var(--scroll);',
              '.panel-inner::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }',
              '.content, .panel-inner { scrollbar-width: thin; scrollbar-color: var(--scroll) transparent; }'):
        assert s in text,s

def test_repeated_svg_ids_scoped(tmp_path):
    pack,fragments=make(tmp_path)
    second=replace(pack.problems[0],id='p2',number=2)
    pack=replace(pack,problems=(*pack.problems,second))
    svg='<svg viewBox="0 0 10 10"><defs><clipPath id="clip"><rect width="5" height="5"/></clipPath></defs><rect clip-path="url(#clip)" width="10" height="10"/></svg>'
    fragments={p.id:fragment(p)+svg for p in pack.problems}
    # Original-card anchors must exist in source too.
    pack.path.write_text(pack.path.read_text().replace('</section>','<article id="p2"></article></section>'))
    pack=replace(pack,sha256=sha256(pack.path))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    text=result.html.read_text();assert 'url(#p1-explain-clip)' in text and 'url(#p2-explain-clip)' in text

def test_nfd_image_link_and_missing_anchor(tmp_path):
    pack,fragments=make(tmp_path)
    image=pack.path.parent/'.assets'/'figures_0917'/'그림.png'
    image.parent.mkdir(parents=True)
    image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
    fragments['p1']+='<figure><img src=".assets/figures_0917/%EA%B7%B8%EB%A6%BC.png" alt="그림"><figcaption>상태</figcaption></figure>'
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert re.search(r'!\[그림\]\(figures_문제설명_0917_Recursion/[^)]+\.png\)',unquote(result.md.read_text()))
    with pytest.raises(ExplainError,match='앵커'):
        build_explanation(pack,{'p1':fragments['p1']+'<a href="'+pack.path.name+'#missing">x</a>'},tmp_path/'bad',tmp_path/'repo')

def test_missing_images_and_duplicate_svg_ids_refused(tmp_path):
    pack,fragments=make(tmp_path)
    for extra,match in [('<img src="missing.png">','경로|그림'),('<svg><g id="a"></g><g id="a"></g></svg>','중복.*ID')]:
        with pytest.raises(ExplainError,match=match):build_explanation(pack,{'p1':fragments['p1']+extra},tmp_path/match.replace('|',''),tmp_path/'repo')

def test_tampered_output_detected(tmp_path):
    pack,fragments=make(tmp_path);result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    result.html.write_text(result.html.read_text()+'changed')
    assert check_artifacts(pack,result)

def test_vendor_files_and_hashes_present():
    vendor=Path(__file__).resolve().parents[1]/'assets/vendor'
    manifest=json.loads((vendor/'provenance.json').read_text())
    for name,digest in manifest['files'].items(): assert sha256(vendor/name)==digest
    for css in vendor.rglob('*.css'):
        for href in re.findall(r"url\(['\"]?([^)'\"\s]+)",css.read_text()):assert (css.parent/href).is_file()

def test_original_c_comparison_is_preserved(tmp_path):
    path=source_file(tmp_path/'repo')
    path.write_text(path.read_text().replace('원래 질문','<pre><code>for(i=0; i&lt;n &amp;&amp; p!=NULL; i++){}</code></pre>'))
    pack=load_source(path,tmp_path/'repo');p=pack.problems[0]
    result=build_explanation(pack,{'p1':fragment(p)},tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    original=next(parse(result.html.read_text()).find_all(lambda n:n.attrs.get('data-original-problem')=='p1'))
    assert next(original.find_all(lambda n:n.tag=='code')).text()=='for(i=0; i<n && p!=NULL; i++){}'

def test_source_and_explanation_svg_ids_do_not_collide(tmp_path):
    path=source_file(tmp_path/'repo')
    svg='<svg viewBox="0 0 10 10"><defs><clipPath id="clip"><rect width="5" height="5"/></clipPath></defs><rect clip-path="url(#clip)" width="10" height="10"/></svg>'
    path.write_text(path.read_text().replace('</div>',''+svg+'</div>',1))
    pack=load_source(path,tmp_path/'repo');p=pack.problems[0]
    result=build_explanation(pack,{'p1':fragment(p)+svg},tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    ids=[n.attrs['id'] for n in parse(result.html.read_text()).find_all(lambda n:'id' in n.attrs)]
    assert len(ids)==len(set(ids))

def test_existing_source_figure_presentation_preserved(tmp_path):
    pack,fragments=make(tmp_path)
    figure='<figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg viewBox="0 0 1000 200" style="background:white;width:1000px;max-width:none;height:auto"><text x="1" y="20">A B C D</text></svg></div></figure>'
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+figure)
    pack=replace(pack,problems=(p,))
    art=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,art)==[]
    assert figure in art.html.read_text()

@pytest.mark.parametrize('style',['background:url(https://example.com/x)','width:expression(alert(1))','position:fixed','color:red'])
def test_source_style_allowance_is_narrow(tmp_path,style):
    pack,fragments=make(tmp_path)
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+f'<figure style="{style}">x</figure>')
    with pytest.raises(ExplainError,match='마크업'):
        build_explanation(replace(pack,problems=(p,)),fragments,tmp_path/'stage',tmp_path/'repo')

def test_authored_style_still_refused(tmp_path):
    pack,fragments=make(tmp_path)
    with pytest.raises(ExplainError,match='style'):
        build_explanation(pack,{'p1':fragments['p1']+'<figure style="margin:16px 0">x</figure>'},tmp_path/'stage',tmp_path/'repo')

SVG_RECT='<svg viewBox="0 0 460 340"><rect class="fig-ink" x="20" y="20" width="420" height="300" rx="14" style="{s}"/>{extra}</svg>'

def test_source_svg_stroke_width_style_preserved(tmp_path):
    pack,fragments=make(tmp_path)
    svg=SVG_RECT.format(s='stroke-width:6',extra='<line x1="0" y1="0" x2="9" y2="9" style="stroke-width:2.5px;"/>')
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+svg)
    pack=replace(pack,problems=(p,))
    art=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,art)==[]
    out=art.html.read_text()
    assert 'style="stroke-width:6"' in out and 'style="stroke-width:2.5px;"' in out

@pytest.mark.parametrize('style',['fill:url(#x)','stroke-width:6;position:absolute','stroke-width:6 !important'])
def test_source_svg_style_allowance_is_narrow(tmp_path,style):
    pack,fragments=make(tmp_path)
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+SVG_RECT.format(s=style,extra=''))
    with pytest.raises(ExplainError,match='마크업'):
        build_explanation(replace(pack,problems=(p,)),fragments,tmp_path/'stage',tmp_path/'repo')

def test_source_stroke_width_outside_svg_refused(tmp_path):
    pack,fragments=make(tmp_path)
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+'<p style="stroke-width:6">x</p>')
    with pytest.raises(ExplainError,match='마크업'):
        build_explanation(replace(pack,problems=(p,)),fragments,tmp_path/'stage',tmp_path/'repo')

def test_authored_svg_stroke_width_style_refused(tmp_path):
    pack,fragments=make(tmp_path)
    with pytest.raises(ExplainError,match='style'):
        build_explanation(pack,{'p1':fragments['p1']+SVG_RECT.format(s='stroke-width:6',extra='')},tmp_path/'stage',tmp_path/'repo')


def test_review_outputs_go_under_assets(tmp_path):
    pack,fragments=make(tmp_path)
    stage=tmp_path/'stage'
    art=build_explanation(pack,fragments,stage,tmp_path/'repo')
    assert check_artifacts(pack,art)==[]
    html=art.html.read_text(encoding='utf-8')
    assert 'href=".assets/자료_문제설명_' in html and '/vendor/katex/katex.min.css' in html
    assert art.html.parent==stage and art.md.parent==stage/'.assets'
    md=unquote(art.md.read_text(encoding='utf-8'))
    assert '](.assets/' not in md
    assert f'](../{pack.path.name}#p1)' in md  # 원 문제 보기 -> ../복습문제_....html
    assert (stage/'.assets'/f'figures_문제설명_{pack.range}_{pack.slug}').is_dir()
    assert (stage/'.assets'/f'자료_문제설명_{pack.range}_{pack.slug}'/'manifest.json').is_file()
    assert not any(p.name.startswith(('figures_','자료_')) or p.suffix=='.md' for p in stage.iterdir())

def test_review_names_under_assets(tmp_path):
    pack,_=make(tmp_path)
    assert names(pack)==('문제설명_0917_Recursion','.assets/figures_문제설명_0917_Recursion','.assets/자료_문제설명_0917_Recursion')

def test_homework_names_unchanged(tmp_path):
    pack,_=make(tmp_path)
    hw=replace(pack,profile='homework',range='3')
    assert names(hw)==('과제3_문제설명_Recursion','figures_문제설명_hw3_Recursion','자료_문제설명_hw3_Recursion')
