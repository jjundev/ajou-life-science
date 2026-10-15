"""TEST ONLY synthetic source and academic review fixtures."""
import json, hashlib, copy, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
POLICY='.agents/skills/bio-review-pack/references/'
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def make_repo(root):
 root.mkdir(parents=True)
 import base64
 (root/'pixel.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
 for name in ['webquiz-style.md','note-feedback.md']:
  p=root/POLICY/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# TEST ONLY\n새 유형과 판단 기준')
 topics=[]
 for ch in range(1,7):
  p=root/f'강의노트/{ch}장.md';p.parent.mkdir(exist_ok=True);p.write_text(f'TEST ONLY {ch}장 학습 근거')
  topics.append(dict(id=f't{ch}',chapter=ch,title=f'주제{ch}',scope_status='included',reason='TEST ONLY',evidence=[dict(path=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),locator='1',role='teaching')]))
 dump(root/'scope.json',dict(chapters=list(range(1,7)),topics=topics))
 return root

def make_candidates(repo,chapters=(1,2,3,4,5,6)):
 ref=dict(path=POLICY+'webquiz-style.md',sha256=hashlib.sha256((repo/POLICY/'webquiz-style.md').read_bytes()).hexdigest(),locator='TEST ONLY',role='policy',criterion='대상 구별',application='보기 대상 구별')
 out=[]
 for ch in chapters:
  for fmt in ['mcq','short']:
   for i in range(20):
    id_=f'c{ch}-{fmt}-{i}'
    options=[dict(id=x,text=f'{id_} 보기 {x}') for x in 'ABCD'] if fmt=='mcq' else []
    markup=f'<p>{id_}: $1+1$ 조건을 판단해요?</p>'
    if i==0 and fmt=='mcq':markup+='<svg viewBox="0 0 100 30" role="img" aria-label="합성 그림"><defs><clipPath id="clip"><rect width="100" height="30"/></clipPath></defs><path d="M1 1L99 29" stroke="currentColor" clip-path="url(#clip)"/></svg><table><tr><th>조건</th></tr><tr><td>합성 조건</td></tr></table><img src="pixel.png" alt="합성 픽셀">'
    if options: markup+='<ul class="choices">'+''.join(f'<li>{o["text"]}</li>' for o in options)+'</ul>'
    answer=dict(kind='choice',option_id='B') if fmt=='mcq' else dict(kind='short',canonical='Aa',accepted=['Aa','합성 답'],case_sensitive=True)
    origin=['web','past','new'][i%3] if ch<6 else ['past','new'][i%2]
    out.append(dict(id=id_,family_id=id_,format=fmt,origin=origin,mode='generated' if origin=='new' else 'variant',primary_chapter=ch,required_chapters=[ch],topic_ids=[f't{ch}'],level=1,priority=[False]*5,types=['새로운 유형'],selection_reason='TEST ONLY 적용',problem_html=markup,options=options,answer=answer,rejected_answers=[dict(text='aa',reason='대소문자 차이')],solution_steps=['조건을 확인해요.','대상을 구별해요.'],source_refs=[copy.deepcopy(ref)],style_basis=[copy.deepcopy(ref)],transformation='합성 변형',minimum_steps=2,original_payload_sha256=None,review={x:dict(status='pass',evidence='TEST ONLY') for x in ['scope','key','source','style','family']}))
 return out

def make_pack(repo):
 from exam_contract import parse_scope
 from exam_sources import inventory
 from exam_selection import select_candidates
 from exam_build import init_version,write_pack,build_exam
 scope=parse_scope('1~6');src=init_version(repo,scope)
 sel=select_candidates(make_candidates(repo),scope,{t['id']:t for t in json.loads((repo/'scope.json').read_text())['topics']})
 write_pack(src,sel,json.loads((repo/'scope.json').read_text()),inventory(repo,scope),'TEST ONLY sections and application',dict(type_targets=[],difficulty_targets=[],reason='TEST ONLY no target'))
 return build_exam(repo,src)

def approve_questions(html):
 from exam_check import initial_question_review
 src=html.parent/'.pack'/('v'+html.stem.rsplit('_v',1)[1])
 rev=initial_question_review(src,html)
 for value in rev['reviews'].values():
  value.update(status='pass',reviewer='TEST ONLY',evidence='TEST ONLY synthetic review',items={f'p{i}':'TEST ONLY' for i in range(1,76)})
 dump(src/'question-review.json',rev)
