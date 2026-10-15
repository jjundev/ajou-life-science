"""Live evidence snapshots and unreviewed source drafts; no policy interpretation."""
import hashlib
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path
from exam_contract import ExamError,payload

ROOT=Path(__file__).resolve().parents[4]
POLICY='.agents/skills/bio-review-pack/references/'

def _module(name,path,package=False):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def bank_model():
    # Private package alias preserves relative SVG imports, without global sys.path edits.
    _module('_exam_question_bank',ROOT/'scripts/question_bank/__init__.py',True)
    return _module('_exam_question_bank.model',ROOT/'scripts/question_bank/model.py')

def local(repo,relative):
    try:return bank_model().resolve_local(Path(repo),str(relative))
    except ValueError as exc:raise ExamError(str(exc)) from exc

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def snapshot(repo,relative,role):
    p=local(repo,relative)
    return dict(path=p.relative_to(Path(repo).resolve()).as_posix(),role=role,status='present' if p.is_file() else 'missing',sha256=sha(p) if p.is_file() else None)

def _bank_paths(repo,path,bank):
    paths=[]
    def add(relative,role,base):
        p=local(base,relative); paths.append((p.relative_to(Path(repo).resolve()).as_posix(),role))
    for s in bank.get('sources',[]):add(s['path'],'bank_raw',path.parent)
    for asset in bank.get('assets',[]):
        for kind in ('exam','explained'):add(asset[kind]['path'],'bank_asset_'+kind,path.parent)
    for q in bank.get('questions',[]):
        for req in q.get('analysis',{}).get('requirements',[]):
            for e in req.get('evidence',[]):
                # Actual banks use repo relative evidence; older fixtures use bank relative.
                base=repo if local(repo,e['path']).exists() else path.parent
                add(e['path'],'bank_evidence',base)
    return paths

def inventory(repo,scope):
    repo=Path(repo).resolve();rows={};warnings=[]
    def add(relative,role,required=False):
        row=snapshot(repo,relative,role)
        if required and row['status']!='present':raise ExamError('필수 공통 자료 누락: '+relative)
        rows[row['path']]=row
    for name in ('webquiz-style.md','note-feedback.md'):add(POLICY+name,'policy',True)
    for ch in scope.chapters:
        for name in ('note-feedback.md','questions.json','intake.md'):add(f'웹과제/{ch}장/{name}','chapter_'+name)
        path=local(repo,f'웹과제/{ch}장/questions.json')
        if path.is_file():
            try:
                bank=bank_model().load_bank(path,complete=True,repo_root=repo)
                for rel,role in _bank_paths(repo,path,bank):add(rel,role,True)
            except ValueError as exc:warnings.append(str(exc))
    # Discover teaching material; explicit used refs are added by write_pack.
    for folder in ('강의노트','STT','교과서','기출','복습노트','장마감'):
        base=local(repo,folder)
        if base.exists():
            for p in sorted(base.rglob('*')):
                if p.is_file() and p.suffix.lower() in ('.md','.pdf','.html'):
                    add(p.relative_to(repo).as_posix(),'teaching')
    return dict(sources=list(rows.values()),warnings=warnings)

def assert_fresh(repo,manifest):
    for old in manifest['sources']:
        current=snapshot(repo,old['path'],old['role'])
        if current!=old:raise ExamError('근거 변경: '+old['path'])

def draft(id_,chapter,origin,problem_html,options,answer,refs,steps):
    c=dict(id=id_,family_id=id_,format='mcq',origin=origin,mode='original',primary_chapter=chapter,required_chapters=[],topic_ids=[],level=1,priority=[False]*5,types=[],selection_reason='',problem_html=problem_html,options=options,answer=answer,source_refs=refs,style_basis=[],solution_steps=steps,rejected_answers=[],minimum_steps=max(1,len(steps)),transformation='',review={k:dict(status='not_run',evidence='') for k in ('scope','key','source','style','family')})
    c['original_payload_sha256']=payload(c);return c

def web_candidates(repo,scope):
    repo=Path(repo).resolve();out=[];exclusions=[]
    for ch in scope.chapters:
        path=local(repo,f'웹과제/{ch}장/questions.json')
        if not path.is_file():continue
        try:bank=bank_model().load_bank(path,complete=True,repo_root=repo)
        except ValueError as exc:
            exclusions.append(dict(path=str(path),reason=str(exc)));continue
        assets={a['id']:a for a in bank['assets']}
        for q in bank['questions']:
            analysis=q['analysis']; official=q['observations']['official_answer']
            if analysis['grading']!='single' or analysis.get('issues') or len(q['original']['options']) not in (4,5):
                exclusions.append(dict(id=q['id'],reason='모호한 정답/원문 문제 또는 보기 수'));continue
            body=[]
            for piece in q['original']['content']:
                if piece['type']=='text':body.append('<p>'+html.escape(piece['text'])+'</p>')
                elif piece['type']=='statements':
                    body.append('<ul>'+''.join('<li>'+html.escape(x['id']+'. '+x['text'])+'</li>' for x in piece['items'])+'</ul>')
                elif piece['type']=='figure':
                    asset=assets[piece['asset_id']]['exam'];p=local(path.parent,asset['path'])
                    body.append(f'<img src="{html.escape(p.relative_to(repo).as_posix())}" alt="{html.escape(asset["alt"])}">')
                else: raise ExamError('미지원 원문 content: '+piece['type'])
            options=q['original']['options']
            body.append('<ul class="choices">'+''.join('<li>'+html.escape(o['text'])+'</li>' for o in options)+'</ul>')
            refs=[dict(path=path.relative_to(repo).as_posix(),sha256=sha(path),locator=q['id'],role='bank')]
            c=draft(q['id'],ch,'web',''.join(body),options,dict(kind='choice',option_id=analysis['answer_option_id']),refs,[html.escape(analysis['reason'])])
            c['answer_status']=analysis['answer_status'];c['official_answer']=official
            c['source_concept_ids']=analysis['concept_ids'];out.append(c)
    return out,exclusions

def past_candidates(repo,scope):
    parser=_module('_exam_old_cards',ROOT/'.agents/skills/bio-webquiz-forecast/scripts/cards.py')
    out=[];seen=set()
    for p in sorted(Path(repo).glob('복습노트/*/복습문제_*.html')):
        for c in parser.parse_cards(p.read_text(encoding='utf-8')).values():
            m=re.fullmatch(r'기출 ([1-9]\d*)강 \d+',c['source'])
            if not m or int(m[1]) not in scope.chapters or c['source'] in seen:continue
            if c['answer_index'] is None or not 0<=c['answer_index']<len(c['options']) or len(c['options']) not in (4,5):continue
            body=re.search(r'<div class="problem">(.*?)</div>\s*(?:<details|$)',c['body'],re.S)
            if not body:continue
            seen.add(c['source']);opts=[dict(id='ABCDE'[i],text=t) for i,t in enumerate(c['options'])]
            row=draft(c['source'],int(m[1]),'past',body[1],opts,dict(kind='choice',option_id='ABCDE'[c['answer_index']]),[dict(path=p.relative_to(repo).as_posix(),sha256=sha(p),locator=c['id'],role='past_review_card')],[])
            row['hold_reason']='기출 원자료·정답·그림 대조 필요';out.append(row)
    return out
