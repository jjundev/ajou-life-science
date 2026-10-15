import json,hashlib,copy
import pytest
from exam_fixtures import make_pack
from exam_build import init_version,build_exam
from exam_contract import parse_scope,validate_pack,ExamError

def test_version_and_layout(repo):
 p=make_pack(repo);before=p.read_bytes();src=init_version(repo,parse_scope('1~6'))
 assert src.name=='v2' and p.read_bytes()==before
 assert {x.name for x in p.parent.iterdir()}=={p.name,'.pack'}
def test_original_content_and_answers(repo):
 p=make_pack(repo);s=p.read_text();pack=json.loads((p.parent/'.pack/v1/pack.json').read_text())
 assert len(pack['problems'])==75 and len(list((p.parent/'.pack/v1/cards').glob('*.html')))==75
 assert 'Aa' in s and '합성 답' in s and 'case_sensitive' in s
 assert validate_pack(pack)==[]
 for field,value in [('id','p2'),('family_id',pack['problems'][1]['family_id']),('mode','nope')]:
  bad=copy.deepcopy(pack);bad['problems'][0][field]=value;assert validate_pack(bad)
 bad=copy.deepcopy(pack);bad['problems'][54]['format']='short';assert validate_pack(bad)
 pack['version']=2;(p.parent/'.pack/v1/pack.json').write_text(json.dumps(pack))
 with pytest.raises(ExamError):build_exam(repo,p.parent/'.pack/v1')

def test_pack_rejects_duplicate_generated_stem(repo):
 p=make_pack(repo);pack=json.loads((p.parent/'.pack/v1/pack.json').read_text())
 for c in pack['problems'][:2]:
  choices=c['problem_html'][c['problem_html'].index('<ul class="choices">'):]
  c.update(origin='new',mode='generated',problem_html='<p>Shared generated stem?</p>'+choices)
 assert validate_pack(pack)
