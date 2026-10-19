import json
import pytest
from exam_helpers import repo,approved_exam
from helpers import fragment,approved
from test_cli import call
from mpe_cli import load_run,load_fragments,load_artifacts
from mpe_render import names

def build_exam_run(tmp_path,repo,source,core_only=False):
 run=tmp_path/'run'
 result=call('extract','--repo',repo,'--target',source,'--run',run);assert result.returncode==0,result.stderr
 item=load_run(run)[0]
 for p in item['pack'].problems:(item['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p,core_only=core_only))
 result=call('build','--run',run);assert result.returncode==0,result.stderr
 return run,load_run(run)[0]
@pytest.mark.parametrize('core_only',[False,True])
def test_exam_output_layout(tmp_path,repo,approved_exam,core_only):
 run,item=build_exam_run(tmp_path,repo,approved_exam,core_only=core_only)
 assert names(item['pack'])==('문제해설_1장-6장_시험예상_v1','.pack/v1/figures_문제해설_1장-6장_시험예상_v1','.pack/v1/자료_문제해설_1장-6장_시험예상_v1')
 artifacts=load_artifacts(item)
 assert '시험 예상 v1 문제해설' not in artifacts.html.read_text()
 assert '"showOptionIds": true' in artifacts.html.read_text()
 import html
 for p in item['pack'].problems:
  title=html.escape(p.title)
  assert f'<h3>{title}</h3>' in artifacts.html.read_text()
  assert f'<a href="#{p.id}">{title}</a>' in artifacts.html.read_text()
  assert p.title in artifacts.md.read_text()
 for p in [artifacts.html,artifacts.md]:
  s=p.read_text();assert 'Aa' in s and '합성 답' in s
 assert call('check','--run',run).returncode==0
 assert call('publish','--run',run).returncode==1
 review=approved(item['pack'],load_fragments(item),artifacts);(item['folder']/'review.json').write_text(json.dumps(review))
 result=call('publish','--run',run);assert result.returncode==0,result.stderr
 assert (approved_exam.parent/'문제해설_1장-6장_시험예상_v1.html').exists()
 assert (approved_exam.parent/'.pack/v1/문제해설_1장-6장_시험예상_v1.md').exists()
 # Rebuild resets reviews.
 assert call('build','--run',run).returncode==0
 r=json.loads((item['folder']/'review.json').read_text());assert r['content']['status']=='not_run'
def test_exam_context_change_requires_extract(tmp_path,repo,approved_exam):
 run,item=build_exam_run(tmp_path,repo,approved_exam)
 path=repo/'.agents/skills/bio-review-pack/references/webquiz-style.md';path.write_text('updated')
 assert call('check','--run',run).returncode==1
 assert call('publish','--run',run).returncode==1
