"""Mechanical and explicit human-review gates, bound to current input bytes."""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote,urlsplit
from exam_contract import ExamError,Scope,validate_pack,payload
from exam_sources import assert_fresh,sha,local,web_candidates
from exam_build import load,blueprint,question_input_hash,initial_question_review,REVIEW_NAMES,BINDINGS,card_html,exam_shared_files
from exam_selection import allocate_quotas
from exam_dom import parse,inner,outer

def locate(question):
 question=Path(question).resolve()
 m=re.fullmatch(r'시험예상문제_([1-9]\d*장(?:-[1-9]\d*장)?)_v([1-9]\d*)\.html',question.name)
 if not m and re.fullmatch(r'시험예상문제_[1-9]\d*장(?:-[1-9]\d*장)?\.html',question.name):
  publication=load(question.parent/'.pack/publication.json')['question']
  version=publication['version']
  if publication['file']!=question.name or type(version) is not int or version<1:raise ExamError('공개 시험 파일 연결 오류')
  m=re.fullmatch(r'시험예상문제_([1-9]\d*장(?:-[1-9]\d*장)?)_v([1-9]\d*)\.html',question.stem+f'_v{version}.html')
 if not m or question.parent.name!=m[1] or question.parent.parent.name!='시험예상':raise ExamError('시험 파일명/폴더 불일치')
 src=question.parent/'.pack'/('v'+m[2]);repo=question.parent.parent.parent
 return repo,src

def _refs(root,base,repo):
 errors=[]
 for n in root.find_all(lambda n:True):
  for key in ('src','href'):
   value=n.attrs.get(key)
   if not value:continue
   url=urlsplit(value)
   if url.scheme or url.netloc:errors.append('외부 자원: '+value);continue
   if not url.path:continue
   path=(base/unquote(url.path)).resolve()
   if not path.is_relative_to(repo.resolve()) or not path.is_file():errors.append('자원 누락/외부 경로: '+value)
 return errors

def check_set(html,*,require_reviews=False):
 errors=[]
 try:
  html=Path(html).resolve();repo,src=locate(html);pack=load(src/'pack.json');manifest=load(src/'source-manifest.json')
  errors.extend(validate_pack(pack));assert_fresh(repo,manifest)
  if pack['range']!=html.parent.name or src.name!=f'v{pack["version"]}':errors.append('pack 범위/버전 불일치')
  if load(src/'scope.json')!=pack['scope_data']:errors.append('scope/pack 불일치')
  if (src/'blueprint.md').read_text(encoding='utf-8')!=blueprint(pack):errors.append('blueprint 불일치')
  if not (src/'policy-notes.md').read_text(encoding='utf-8').strip():errors.append('정책 읽기 기록 누락')
  candidates=load(src/'candidates.json')
  if len(candidates)!=75 or len({c['id'] for c in candidates})!=75:errors.append('후보 집합 불일치')
  bycandidate={c['id']:c for c in candidates}
  source_rows={s['path']:s for s in manifest['sources']}
  for p in pack['problems']:
   c=dict(p);c['id']=c.pop('candidate_id')
   if bycandidate.get(c['id'])!=c:errors.append(p['id']+': 후보/pack 불일치')
   for ref in [*p['source_refs'],*p['style_basis']]:
    row=source_rows.get(ref['path'])
    if not row or row['status']!='present' or row['sha256']!=ref['sha256']:errors.append('근거 manifest 불일치: '+ref['path'])
  q=allocate_quotas(Scope(tuple(pack['scope'])))
  actual=Counter((p['primary_chapter'],p['format']) for p in pack['problems'])
  for ch,quota in q.items():
   for fmt in ('mcq','short'):
    if actual[ch,fmt]!=quota[fmt]:errors.append('장/형식 배정 불일치')
  text=html.read_text(encoding='utf-8');root=parse(text)
  from exam_presentations import check_pair
  errors.extend(check_pair(src))
  cards=list(root.find_all(lambda n:n.tag=='article' and 'card' in n.classes))
  if [c.attrs.get('id') for c in cards]!=[f'p{i}' for i in range(1,76)]:errors.append('HTML 75 카드 누락/중복')
  ids=[n.attrs['id'] for n in root.find_all(lambda n:'id' in n.attrs)]
  if len(ids)!=len(set(ids)):errors.append('HTML/SVG ID 중복')
  modelnodes=list(root.find_all(lambda n:n.attrs.get('id')=='exam-model'))
  model=json.loads(modelnodes[0].text()) if len(modelnodes)==1 else {}
  if model!={p['id']:dict(format=p['format'],answer=p['answer']) for p in pack['problems']}:errors.append('HTML 정답 모델 불일치')
  for c,p in zip(cards,pack['problems']):
   expected=next(parse(card_html(repo,src,p,manifest,copy_assets=False)).find_all(lambda n:n.tag=='article'))
   if outer(c)!=outer(expected):errors.append(p['id']+': pack/HTML 문항 불일치')
   cardpath=src/'cards'/f'{p["id"]}.html'
   if outer(c)!=outer(next(parse(cardpath.read_text(encoding='utf-8')).find_all(lambda n:n.tag=='article'))):errors.append(p['id']+': 카드/HTML 불일치')
   for cls in ('solution','provenance'):
    nodes=list(c.find_all(lambda n:cls in n.classes))
    if len(nodes)!=1 or 'hidden' not in nodes[0].attrs:errors.append('제출 전 답 노출')
  errors.extend(_refs(root,html.parent,repo))
  # Recheck original bank payload; reviewers must audit past PDF provenance.
  if any(p['origin']=='web' and p['mode']=='original' for p in pack['problems']):
   bankcs,_=web_candidates(repo,Scope(tuple(pack['scope'])));bankby={c['id']:c for c in bankcs}
   for p in pack['problems']:
    if p['origin']=='web' and p['mode']=='original' and payload(p)!=payload(bankby.get(p['candidate_id'],{})):errors.append('은행 원문 불일치: '+p['id'])
  if not require_reviews:
   exam_shared_files(repo, html)
  if require_reviews:
   review=load(src/'question-review.json')
   if review.get('input_hash')!=question_input_hash(src,html):errors.append('검토 입력 해시 변경')
   if set(review.get('reviews',{}))!=set(REVIEW_NAMES):errors.append('네 검토 필요')
   for name in REVIEW_NAMES:
    r=review.get('reviews',{}).get(name,{})
    if r.get('status')!='pass' or not r.get('reviewer') or not r.get('evidence') or set(r.get('items',{}))!={f'p{i}' for i in range(1,76)} or not all(isinstance(x,str) and x.strip() for x in r.get('items',{}).values()):errors.append('미완료 문항 검토: '+name)
   if (src/'presentations.json').exists():
    modes=review.get('reviews',{}).get('browser',{}).get('presentations',{})
    for mode in ('practice','exam'):
     r=modes.get(mode,{})
     if r.get('status')!='pass' or not r.get('reviewer') or not r.get('evidence'):errors.append('미완료 풀이형 브라우저 검토: '+mode)
 except (OSError,ValueError,KeyError,TypeError,IndexError,StopIteration) as exc:errors.append(str(exc))
 return errors

def completion_status(question_html,explanation_html,workflow):
    import subprocess,sys
    errors=check_set(question_html,require_reviews=True)
    if errors:return dict(status='unverified',question_errors=errors,explanation_errors=[])
    if type(workflow.get('repairs_used')) is not int or not 0<=workflow['repairs_used']<=2:return dict(status='partial',question_errors=[],explanation_errors=['수정 예산 오류'])
    if explanation_html is None:return dict(status='partial',question_errors=[],explanation_errors=['검증된 해설 없음'])
    repo,_=locate(question_html)
    from exam_sources import ROOT
    script=ROOT/'.agents/skills/bio-problem-explain/scripts/mpe_exam.py'
    result=subprocess.run([sys.executable,str(script),'--repo',str(repo),'--question',str(question_html),'--explanation',str(explanation_html)],capture_output=True,text=True)
    try:explanation_errors=json.loads(result.stdout)
    except ValueError:explanation_errors=[result.stderr or '해설 검증 실패']
    return dict(status='complete' if result.returncode==0 and not explanation_errors else 'partial',question_errors=[],explanation_errors=explanation_errors)
