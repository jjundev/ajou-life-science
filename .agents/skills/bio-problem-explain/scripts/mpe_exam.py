"""Explicit, review-bound 75-question exam adapter with short-answer models."""
import importlib.util
import json
import re
import sys
from pathlib import Path
from mpe_shared import parse,inner
from mpe_source import inside,existing_path,nfc,sha256
from mpe_types import ExplainError,Problem,SourcePack,ChoiceModel,ShortAnswerModel
FILENAME_RE=r'시험예상문제_([1-9]\d*장(?:-[1-9]\d*장)?)(?:_v([1-9]\d*))?\.html'

def exam_problem_title(problem):
    labels={('past','original'):'기출 원문',('past','variant'):'기출 변형',
            ('web','original'):'웹과제 원문',('web','variant'):'웹과제 변형',
            ('new','generated'):'새 예상문제'}
    label=labels.get((problem.get('origin'),problem.get('mode')))
    concept=problem.get('concept_summary')
    id_=problem.get('id','')
    if not label or not isinstance(concept,str) or not concept.strip() or not re.fullmatch(r'p[1-9]\d*',id_):
        raise ExplainError(f'{id_}: 시험 해설 제목 메타데이터 확인 필요')
    return f'[{label}] {id_.upper()}. {concept.strip()}'

def exam_api():
    scripts=Path(__file__).resolve().parents[2]/'bio-exam-forecast/scripts'
    # Globally unique exam_* modules; no mutation of sys.path and no generic helper imports.
    for name in ('exam_contract','exam_sources','exam_selection','exam_dom','exam_build','exam_check'):
        if name not in sys.modules:
            spec=importlib.util.spec_from_file_location(name,scripts/(name+'.py'))
            mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return sys.modules['exam_check'],sys.modules['exam_sources']

def assert_exam_fresh(pack):
    checker,sources=exam_api()
    try:
        repo,src=checker.locate(pack.path)
        sources.assert_fresh(repo,json.loads((src/'source-manifest.json').read_text(encoding='utf-8')))
        errors=checker.check_set(pack.path,require_reviews=True)
        if errors:raise ExplainError('시험 입력 재추출 필요: '+' / '.join(errors))
    except (OSError,ValueError,KeyError) as exc:raise ExplainError('시험 입력 재추출 필요: '+str(exc)) from exc

def load_exam_source(path,repo):
    path=inside(existing_path(Path(path)),Path(repo))
    if not re.fullmatch(FILENAME_RE,nfc(path.name)):raise ExplainError('시험 파일명 오류')
    checker,sources=exam_api()
    try:
        errors=checker.check_set(path,require_reviews=True)
        if errors:raise ExplainError('시험 입력 재추출 필요: '+' / '.join(errors))
        actual_repo,src=checker.locate(path)
        if actual_repo.resolve()!=Path(repo).resolve():raise ExplainError('시험 저장소 경로 불일치')
        pack=json.loads((src/'pack.json').read_text(encoding='utf-8'))
        root=parse(path.read_text(encoding='utf-8'));cards={n.attrs['id']:n for n in root.find_all(lambda n:n.tag=='article' and 'card' in n.classes)}
        problems=[]
        for p in pack['problems']:
            card=cards[p['id']];problem=next(card.find_all(lambda n:'problem' in n.classes))
            source=f'{p["origin"]}/{p["mode"]} · {p["candidate_id"]}'
            answer=p['answer']
            choice=ChoiceModel(answer['option_id'],'single',tuple(o['id'] for o in p['options'])) if p['format']=='mcq' else None
            short=ShortAnswerModel(answer['canonical'],tuple(answer['accepted']),answer['case_sensitive']) if p['format']=='short' else None
            ref=answer['option_id'] if choice else answer['canonical']
            problems.append(Problem(p['id'],int(p['id'][1:]),exam_problem_title(p),source,'',inner(problem),'',(),tuple(p['solution_steps']),ref,('main',),choice,short))
        files=[src/name for name in (*checker.BINDINGS,'question-review.json')]
        files += [sources.local(repo,row['path']) for row in json.loads((src/'source-manifest.json').read_text(encoding='utf-8'))['sources'] if row['status']=='present']
        # Bind authored cards and copied visual assets too.
        for folder in ('cards','assets','vendor'):
            if (src/folder).exists():files.extend(p for p in (src/folder).rglob('*') if p.is_file())
        contexts=tuple(sorted({(str(p),sha256(p)) for p in files}))
        return SourcePack('exam',pack['range'],f'시험예상_v{pack["version"]}',path,sha256(path),tuple(problems),contexts)
    except (OSError,ValueError,KeyError,TypeError,StopIteration) as exc:
        if isinstance(exc,ExplainError):raise
        raise ExplainError('시험 입력 오류: '+str(exc)) from exc

def published_errors(question,explanation,repo):
    from mpe_render import names,check_artifacts,artifact_hashes
    from mpe_contract import validate_reviews,validate_fragment,payload_hash
    from mpe_types import Artifacts
    try:
        pack=load_exam_source(question,repo);stem,fig,data=names(pack)
        explanation=inside(Path(explanation),Path(repo))
        if explanation!=pack.path.parent/(stem+'.html'):return ['해설 범위/버전/경로 불일치']
        data_path=explanation.parent/data;manifest_path=data_path/'manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        review=json.loads((data_path/'validation.json').read_text(encoding='utf-8'))
        files=tuple(inside(explanation.parent/name,Path(repo)) for name in manifest['files'])+(manifest_path,)
        artifacts=Artifacts(explanation,explanation.parent/Path(fig).parent/(stem+'.md'),manifest_path,files)
        fragments={p.id:(data_path/'fragments'/f'{p.id}.html').read_text(encoding='utf-8') for p in pack.problems}
        errors=check_artifacts(pack,artifacts)+validate_reviews(pack,fragments,review)
        errors += [e for p in pack.problems for e in validate_fragment(p,fragments[p.id])]
        if manifest['input_hash']!=payload_hash(pack,fragments):errors.append('해설 입력 해시 변경')
        if review.get('artifact_hashes')!=artifact_hashes(artifacts):errors.append('발행 후 해설 자산 변경')
        for ref in review.get('references',[]):
            path=inside(Path(ref['path']),Path(repo))
            if not path.is_file() or sha256(path)!=ref['sha256']:errors.append('해설 참조 자료 변경')
        return errors
    except (OSError,ValueError,KeyError,TypeError) as exc:return [str(exc)]

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--question',required=True);parser.add_argument('--explanation',required=True);parser.add_argument('--repo',required=True)
    args=parser.parse_args();errors=published_errors(args.question,args.explanation,args.repo)
    print(json.dumps(errors,ensure_ascii=False));raise SystemExit(bool(errors))
