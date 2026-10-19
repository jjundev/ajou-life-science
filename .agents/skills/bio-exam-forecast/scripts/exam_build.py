"""Versioned static exam assembly. Building never approves a review."""
import copy
from functools import lru_cache
import html
import json
import os
import re
import shutil
from pathlib import Path
from exam_contract import ExamError,Scope,digest,validate_pack
from exam_sources import ROOT,sha,local,snapshot,assert_fresh
from exam_selection import TARGETS,selection_report

ASSETS=Path(__file__).resolve().parents[1]/'assets'
BINDINGS=('pack.json','blueprint.md','scope.json','source-manifest.json','policy-notes.md','candidates.json','selection-report.md')
REVIEW_NAMES=('source_visual','content_scope_style','independent','browser')
@lru_cache(maxsize=1)
def casefold_map():
 return {chr(i):chr(i).casefold() for i in range(0x110000) if chr(i).casefold()!=chr(i).lower()}

def dump(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def init_version(repo,scope):
 folder=local(repo,'시험예상/'+scope.label);packdir=folder/'.pack';packdir.mkdir(parents=True,exist_ok=True)
 numbers=[int(p.name[1:]) for p in packdir.iterdir() if re.fullmatch(r'v[1-9]\d*',p.name)]
 numbers += [int(m[1]) for p in folder.glob('*.html') if (m:=re.search(r'_v(\d+)\.html$',p.name))]
 version=max(numbers,default=0)+1
 while True:
  src=packdir/f'v{version}'
  try:src.mkdir();return src
  except FileExistsError:version+=1

def blueprint(pack):
 return '| ID | 후보 | 장 | 형식 | 가족 | 정답 |\n|---|---|---|---|---|---|\n'+''.join(f'| {p["id"]} | {p["candidate_id"]} | {p["primary_chapter"]} | {p["format"]} | {p["family_id"]} | {json.dumps(p["answer"],ensure_ascii=False)} |\n' for p in pack['problems'])

def write_pack(src,selection,scope_data,manifest,policy_notes,policy_summary):
 src=Path(src)
 if selection.shortages:raise ExamError('문항 부족: '+str(selection.shortages))
 if not policy_notes.strip() or not policy_summary or not scope_data.get('topics'):raise ExamError('정책/범위 저작 필요')
 if (src/'pack.json').exists():raise ExamError('이미 작성된 버전')
 scope=Scope(tuple(scope_data['chapters']))
 if src.parent.name!='.pack' or src.parent.parent.name!=scope.label or not re.fullmatch(r'v[1-9]\d*',src.name):raise ExamError('범위/버전 경로 불일치')
 problems=[]
 for i,c in enumerate(selection.problems,1):
  p=copy.deepcopy(c);p['candidate_id']=p['id'];p['id']=f'p{i}'
  topics={t['id']:t['title'] for t in scope_data['topics']}
  p.setdefault('concept_summary', ' · '.join(dict.fromkeys(topics[t] for t in p['topic_ids'])))
  problems.append(p)
 pack=dict(schema_version=1,profile='exam',scope=list(scope.chapters),range=scope.label,version=int(src.name[1:]),counts=dict(mcq=55,short=20),targets=[dict(format=k[0],origin=k[1],mode=k[2],target=v) for k,v in TARGETS.items()],policy_summary=policy_summary,problems=problems,scope_data=scope_data,source_manifest='source-manifest.json')
 errors=validate_pack(pack)
 if errors:raise ExamError('\n'.join(errors))
 dump(src/'pack.json',pack);dump(src/'scope.json',scope_data);dump(src/'candidates.json',[dict({k:v for k,v in p.items() if k not in ('id','candidate_id')},id=p['candidate_id']) for p in problems]);dump(src/'source-manifest.json',manifest)
 (src/'policy-notes.md').write_text(policy_notes,encoding='utf-8');(src/'blueprint.md').write_text(blueprint(pack),encoding='utf-8');(src/'selection-report.md').write_text(selection_report(selection),encoding='utf-8')
 return pack

def question_input_hash(src,question):
 src=Path(src);files=[src/name for name in BINDINGS]+[Path(question)]
 for folder in ('cards','vendor','assets'):
  if (src/folder).exists():files+=sorted(p for p in (src/folder).rglob('*') if p.is_file())
 return digest([(os.path.relpath(p,src),sha(p)) for p in files])

def initial_question_review(src,question):
 return dict(input_hash=question_input_hash(src,question),reviews={k:dict(status='not_run',reviewer='',evidence='',items={}) for k in REVIEW_NAMES})

def _resources(repo,src,markup,id_,manifest,*,copy_assets=True):
 # Reuse the existing Node parser without altering global search paths.
 from exam_dom import parse,outer
 root=parse(markup)
 for node in root.find_all(lambda n:True):
  if node.tag=='img':
   value=node.attrs.get('src','')
   if re.match(r'^[a-z]+:|^/|^//',value,re.I):raise ExamError('원문 그림은 저장소 상대 경로 필요')
   path=local(repo,value)
   if not path.is_file():raise ExamError('그림 누락: '+value)
   rel='assets/'+sha(path)[:16]+path.suffix
   target=src/rel
   if copy_assets:
    target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
   node.attrs['src']=f'.pack/{src.name}/{rel}'
   row=snapshot(repo,value,'question_asset')
   if row['path'] not in {x['path'] for x in manifest['sources']}:manifest['sources'].append(row)
 # SVG identifiers are local to each question occurrence.
 mapping={n.attrs['id']:id_+'-'+n.attrs['id'] for n in root.find_all(lambda n:n.tag=='svg' or bool(n.attrs.get('id')) ) if n.attrs.get('id')}
 for node in root.find_all(lambda n:True):
  for k,v in list(node.attrs.items()):
   if k=='id':node.attrs[k]=mapping.get(v,v)
   elif k in ('href','xlink:href') and v.startswith('#'):node.attrs[k]='#'+mapping.get(v[1:],v[1:])
   else:node.attrs[k]=re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+mapping.get(m[1],m[1])+')',v)
 return ''.join(outer(c) if not isinstance(c,str) else c for c in root.children)

def card_html(repo,src,p,manifest,*,copy_assets=True):
 body=_resources(repo,src,p['problem_html'],p['id'],manifest,copy_assets=copy_assets)
 id_=p['id'];answer=p['answer']
 title=html.escape(p.get('concept_summary') or '시험 예상문제')
 if p['format']=='mcq':
  inputs='<fieldset><legend>답 선택</legend>'+''.join(f'<label><input type="radio" name="{id_}" value="{html.escape(o["id"])}"> {html.escape(o["id"])}. {html.escape(o["text"])}</label>' for o in p['options'])+'</fieldset>'
  key=html.escape(answer['option_id'])
 else:
  inputs=f'<label for="answer-{id_}">단답형 답안</label><input type="text" id="answer-{id_}" autocomplete="off">'
  key=html.escape(answer['canonical'])+' · 허용답: '+html.escape(', '.join(answer['accepted']))
 steps=''.join('<li>'+x+'</li>' for x in p['solution_steps'])
 refs=html.escape(json.dumps(dict(origin=p['origin'],mode=p['mode'],refs=p['source_refs'],reason=p['selection_reason'],style_basis=p['style_basis']),ensure_ascii=False))
 return f'<article class="card" id="{id_}"><h3>{id_}. {title}</h3><div class="problem">{body}</div><div class="exam-input">{inputs}</div><p class="result" role="status"></p><div class="solution" hidden><ol class="steps">{steps}</ol><p class="answer">정답: {key}</p></div><div class="provenance" hidden>{refs}</div></article>'

def render_exam(repo,src):
 src=Path(src);pack=load(src/'pack.json');manifest=load(src/'source-manifest.json');scope=Scope(tuple(pack['scope']))
 if src.name!=f'v{pack["version"]}' or src.parent.parent.name!=scope.label:raise ExamError('manifest 범위/버전 경로 불일치')
 errors=validate_pack(pack)
 if errors:raise ExamError('\n'.join(errors))
 assert_fresh(repo,manifest)
 # Include agent-added evidence, including topic evidence and source/style refs.
 refs=[r for p in pack['problems'] for field in ('source_refs','style_basis') for r in p[field]]
 refs += [r for t in pack['scope_data']['topics'] for r in t['evidence']]
 for ref in refs:
  row=snapshot(repo,ref['path'],ref.get('role','used_evidence'))
  if row['status']!='present' or row['sha256']!=ref['sha256']:raise ExamError('참조 근거 변경: '+ref['path'])
  if row['path'] not in {x['path'] for x in manifest['sources']}:manifest['sources'].append(row)
 content=[];(src/'cards').mkdir(exist_ok=True)
 for p in pack['problems']:
  card=card_html(repo,src,p,manifest);(src/'cards'/f'{p["id"]}.html').write_text(card,encoding='utf-8');content.append(card)
 dump(src/'source-manifest.json',manifest)
 vendor=ROOT/'.agents/skills/bio-problem-explain/assets/vendor'
 shutil.copytree(vendor,src/'vendor',dirs_exist_ok=True)
 template=(ROOT/'.agents/skills/bio-review-pack/assets/review-template.html').read_text(encoding='utf-8')
 vendor_url=f'.pack/{src.name}/vendor'
 template=re.sub(r'https://cdn.jsdelivr.net/npm/pretendard@[^" ]+/dist/web/static/pretendard.css',vendor_url+'/pretendard/pretendard.css',template)
 template=re.sub(r'https://cdn.jsdelivr.net/npm/katex@[^" ]+/dist/',vendor_url+'/katex/',template)
 template=template.replace('data-panels="review"','data-panels="exam"')
 template=template.replace('<strong class="brand">복습문제</strong>','<strong class="brand">시험예상문제</strong>')
 template=re.sub(r'      <a class="top-link"[^\n]+\n','',template)
 template=template.replace('<button class="text-btn theme-toggle"', '<button class="text-btn" id="reset-exam" type="button">다시 풀기</button>\n      <button class="text-btn theme-toggle"')
 template=template.replace('푼 문제 <b id="progress-n">','응답한 문제 <b id="progress-n">')
 template=template.replace('문제로 넘어가면 그 문제의 교과서 원문, 힌트, 풀이가 여기에 나옵니다. 먼저 스스로 풀어 본 뒤 여세요.','전체 제출 후 현재 문제의 정답과 풀이를 확인할 수 있습니다.')
 template=template.replace('<div class="aids"></div>','<div class="aids" id="exam-aid"></div>')
 template=template.replace('</main>',(ASSETS/'exam-results.html').read_text(encoding='utf-8')+'\n</main>')
 template=template.replace('</head>',(ASSETS/'exam-template.html').read_text(encoding='utf-8')+'\n</head>')
 controls='<div class="exam-actions"><button class="btn btn-primary" id="submit-exam" type="button" hidden>전체 제출</button><p id="summary" role="status" aria-live="polite"></p></div>'
 template=template.replace('<div class="pager-inner">',controls+'<div class="pager-inner">')
 fold=json.dumps(casefold_map(),ensure_ascii=True).replace('<','\\u003c')
 model=json.dumps({p['id']:dict(format=p['format'],answer=p['answer']) for p in pack['problems']},ensure_ascii=False).replace('<','\\u003c')
 meta=json.dumps(dict(documentId=f'시험예상문제_{scope.label}_v{pack["version"]}.html',range=scope.label,examVersion=pack['version'],questionSetHash=digest(pack['problems'])),ensure_ascii=False).replace('<','\\u003c')
 scripts='<script type="application/json" id="exam-meta">'+meta+'</script><script type="application/json" id="exam-casefold">'+fold+'</script><script type="application/json" id="exam-model">'+model+'</script><script>'+(ASSETS/'exam-runtime.js').read_text(encoding='utf-8')+'</script>'
 title=f'시험 예상문제 {scope.label}'
 intro='객관식 55문항 · 단답형 20문항. 전체 제출 후 정답과 출처가 공개됩니다.'
 replacements=dict(PAGE_TITLE=html.escape(title),DESCRIPTION=intro,RANGE='exam-'+scope.label+'-'+src.name,TITLE=html.escape(title),INTRO=intro+'<noscript> JavaScript를 켜면 이동·제출·채점을 사용할 수 있습니다. 정답은 숨겨져 있습니다.</noscript>',TOC='<a href="#exam-mcq">객관식 1–55</a><a href="#exam-short">단답형 56–75</a>',PARTS='<section id="exam-mcq"><h2>객관식</h2>'+''.join(content[:55])+'</section><section id="exam-short"><h2>단답형</h2>'+''.join(content[55:])+'</section>',FOOTER='55+20은 연습용 구성입니다.',SCRIPTS=scripts)
 text=re.sub(r'\{\{([A-Z_]+)\}\}',lambda m:replacements[m[1]],template)
 if re.search(r'\{\{[A-Z_]+\}\}',text):raise ExamError('미치환 template slot')
 return text

def build_exam(repo,src):
 src=Path(src)
 review=src/'question-review.json'
 if review.exists() and all(r.get('status')=='pass' for r in load(review)['reviews'].values()):raise ExamError('완료 버전은 새 버전으로 생성하세요')
 rendered=render_exam(repo,src);p=load(src/'pack.json');target=src.parent.parent/f'시험예상문제_{p["range"]}_v{p["version"]}.html'
 target.write_text(rendered,encoding='utf-8');dump(review,initial_question_review(src,target));return target
