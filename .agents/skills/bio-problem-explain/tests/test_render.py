from dataclasses import replace
import json, re, base64, hashlib
from pathlib import Path
import pytest
from helpers import fragment, source_file
from mpe_source import load_source, sha256
from mpe_shared import parse
from mpe_types import ExplainError
from mpe_render import build_explanation, check_artifacts

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

def test_template_bytes_match_pinned_source():
    template=Path(__file__).resolve().parents[1]/'assets/note-template.html'
    provenance=json.loads((template.parent/'port-provenance.json').read_text())
    entry=next(e for e in provenance['files'] if e['destination']=='assets/note-template.html')
    assert hashlib.sha256(template.read_bytes()).hexdigest()==entry['source_sha256']==entry['destination_sha256']

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
    image=pack.path.parent/'그림.png'
    image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
    fragments['p1']+='<figure><img src="%EA%B7%B8%EB%A6%BC.png" alt="그림"><figcaption>상태</figcaption></figure>'
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert re.search(r'!\[그림\]\(figures_[^)]+\.png\)',result.md.read_text())
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
