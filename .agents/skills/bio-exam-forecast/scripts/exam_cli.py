"""Agent-directed authoring workflow; never fabricates semantic approvals."""
import argparse
import json
import sys
from pathlib import Path
from exam_contract import ExamError,parse_scope,Selection,digest
from exam_sources import inventory,assert_fresh,web_candidates,past_candidates,local
from exam_selection import select_candidates,selection_report
from exam_build import dump,load,init_version,write_pack,build_exam
from exam_check import check_set,completion_status
from exam_blind import write_blind

def _budget(run,workflow):
    path=Path(run)/'repair-history.json';history=load(path) if path.exists() else []
    if type(workflow.get('repairs_used')) is not int or workflow['repairs_used']!=len(history) or not 0<=len(history)<=2:raise ExamError('수정 횟수 초기화/예산 불일치')
    return history

def record_repair(run,reason):
    run=Path(run);w=load(run/'run.json');history=_budget(run,w)
    if len(history)>=2 or not reason.strip():raise ExamError('최대 2회 수정 예산 소진/사유 필요')
    history.append(dict(number=len(history)+1,reason=reason));dump(run/'repair-history.json',history)
    w['repairs_used']=len(history);dump(run/'run.json',w)
    return w

def _author_hash(run):
    return digest([(name,(run/name).read_text(encoding='utf-8')) for name in ('candidates.json','scope.json','policy-notes.md','policy-summary.json','source-manifest.json')])

def _read(run):
    run=Path(run).resolve();w=load(run/'run.json');_budget(run,w)
    repo=Path(w['repo'])
    if not repo.is_absolute() or not repo.is_dir():raise ExamError('repo 절대 경로 필요')
    assert_fresh(repo,load(run/'source-manifest.json'))
    if w.get('src'):
        src=Path(w['src']);root=local(repo,'시험예상/'+parse_scope(w['scope']).label)/'.pack'
        if src.resolve().parent!=root.resolve():raise ExamError('src 경로 불일치')
    return run,w,repo

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--repo',required=True);p.add_argument('--scope',required=True);p.add_argument('--run',required=True)
    for name in ('select','build','check','blind','status','repair'):
        p=sub.add_parser(name);p.add_argument('--run',required=True)
        if name=='check':p.add_argument('--final',action='store_true')
        if name=='blind':p.add_argument('--out',required=True)
        if name=='status':p.add_argument('--explanation')
        if name=='repair':p.add_argument('--reason',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='prepare':
            repo=Path(args.repo).resolve();scope=parse_scope(args.scope);run=Path(args.run).absolute()
            if run.is_symlink() or (run.exists() and (not run.is_dir() or any(run.iterdir()))):raise ExamError('RUN은 새 빈 폴더여야 합니다')
            manifest=inventory(repo,scope);web,excluded=web_candidates(repo,scope)
            run.mkdir(parents=True,exist_ok=True);dump(run/'source-manifest.json',manifest);dump(run/'candidates.json',web+past_candidates(repo,scope));dump(run/'exclusions.json',excluded)
            dump(run/'scope.json',dict(chapters=list(scope.chapters),topics=[]));dump(run/'policy-summary.json',dict(type_targets=[],difficulty_targets=[],reason=''))
            (run/'policy-notes.md').write_text('',encoding='utf-8')
            dump(run/'repair-history.json',[]);dump(run/'run.json',dict(repo=str(repo),scope=scope.label,repairs_used=0,src=None,question_html=None,state='prepared'))
            print(run);return 0
        run,w,repo=_read(args.run)
        if args.command=='repair':record_repair(run,args.reason);return 0
        scope=parse_scope(w['scope'])
        if args.command=='select':
            scope_data=load(run/'scope.json');policy=load(run/'policy-summary.json')
            if scope_data['chapters']!=list(scope.chapters) or not scope_data['topics'] or not (run/'policy-notes.md').read_text(encoding='utf-8').strip() or not policy.get('reason'):raise ExamError('scope/정책 읽기·적용 저작 필요')
            previous=[];folder=local(repo,'시험예상/'+scope.label)/'.pack'
            if folder.exists():
                owned={Path(p).resolve() for p in w.get('owned_versions',[])}
                if w.get('src'):owned.add(Path(w['src']).resolve())
                for f in sorted(folder.glob('v*/pack.json')):
                    if f.parent.resolve() not in owned:previous.extend(load(f)['problems'])
            result=select_candidates(load(run/'candidates.json'),scope,{t['id']:t for t in scope_data['topics']},previous=tuple(previous))
            (run/'selection-report.md').write_text(selection_report(result),encoding='utf-8')
            dump(run/'selection.json',dict(problems=result.problems,quotas=result.quotas,shortages=result.shortages,deviations=result.deviations))
            w['question_html']=None
            w['needs_new_version']=True
            if result.shortages:w['state']='shortage';dump(run/'run.json',w);raise ExamError(str(result.shortages))
            w['state']='selected';w['selection_input_hash']=_author_hash(run);dump(run/'run.json',w);return 0
        if args.command=='build':
            if w['state'] not in ('selected','built'):raise ExamError('먼저 적격 후보를 select 하세요')
            if w.get('selection_input_hash')!=_author_hash(run):raise ExamError('저작 입력 변경: select부터 다시 실행하세요')
            data=load(run/'selection.json');selection=Selection(tuple(data['problems']),data['quotas'],tuple(data['shortages']),tuple(data['deviations']))
            # Re-selection is required after any authoring input changes.
            if not w.get('src') or w.get('needs_new_version'):
                src=init_version(repo,scope);w['src']=str(src)
                w.setdefault('owned_versions',[]).append(str(src));dump(run/'run.json',w)
                write_pack(src,selection,load(run/'scope.json'),load(run/'source-manifest.json'),(run/'policy-notes.md').read_text(encoding='utf-8'),load(run/'policy-summary.json'))
            p=build_exam(repo,Path(w['src']));w.update(question_html=str(p),state='built',needs_new_version=False);dump(run/'run.json',w);print(p);return 0
        if not w.get('question_html'):raise ExamError('아직 build된 문제 없음')
        question=Path(w['question_html'])
        if args.command=='check':
            errors=check_set(question,require_reviews=args.final)
            if errors:raise ExamError('\n'.join(errors))
        elif args.command=='blind':print(write_blind(question,args.out))
        elif args.command=='status':print(json.dumps(completion_status(question,Path(args.explanation) if args.explanation else None,w),ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
