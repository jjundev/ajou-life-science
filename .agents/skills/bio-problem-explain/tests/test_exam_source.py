import pytest
from exam_helpers import repo,approved_exam
from mpe_exam import load_exam_source
from mpe_source import load_source,resolve_sources
from mpe_types import ExplainError

@pytest.mark.parametrize('origin,mode,label',[
 ('past','original','기출 원문'),('past','variant','기출 변형'),
 ('web','original','웹과제 원문'),('web','variant','웹과제 변형'),
 ('new','generated','새 예상문제'),
])
def test_exam_title_labels(origin,mode,label):
 from mpe_exam import exam_problem_title
 assert exam_problem_title(dict(id='p4',origin=origin,mode=mode,concept_summary='생체분자의 구조와 중합체'))==f'[{label}] P4. 생체분자의 구조와 중합체'

def test_exam_title_requires_explicit_metadata():
 from mpe_exam import exam_problem_title
 for data in [dict(id='p1',origin='web',mode='generated',concept_summary='개념'),
              dict(id='p1',origin='web',mode='original',concept_summary=' ')]:
  with pytest.raises(ExplainError):exam_problem_title(data)

def test_public_exam_filename_resolves_explicit_version(approved_exam,repo):
 import json
 from exam_check import locate,check_set
 # The public name mapping is the preserved single-presentation contract.
 from exam_build import render_exam
 from exam_helpers import fixtures
 src=approved_exam.parent/'.pack/v1'
 approved_exam.write_text(render_exam(repo,src))
 approved_exam.with_name(approved_exam.name.replace('_v','_연습형_v')).unlink()
 (src/'presentations.json').unlink()
 fixtures.approve_questions(approved_exam)
 public=approved_exam.with_name('시험예상문제_1장-6장.html')
 approved_exam.rename(public)
 mapping=public.parent/'.pack/publication.json'
 mapping.write_text(json.dumps({'question':{'file':public.name,'version':1}}))
 assert locate(public)==(repo,public.parent/'.pack/v1')
 assert check_set(public)==[]

def test_exam_has_all_formats(approved_exam,repo):
 pack=load_exam_source(approved_exam,repo)
 assert pack.profile=='exam' and len(pack.problems)==75
 assert sum(p.choice is not None for p in pack.problems)==55
 assert sum(p.short_answer is not None for p in pack.problems)==20
 assert [p.id for p in pack.problems]==[f'p{i}' for i in range(1,76)]
 assert pack.problems[55].short_answer.canonical=='Aa'
 import json
 from mpe_exam import exam_problem_title
 metadata=json.loads((approved_exam.parent/'.pack/v1/pack.json').read_text())
 assert [p.title for p in pack.problems]==[exam_problem_title(p) for p in metadata['problems']]
 assert load_source(approved_exam,repo)==pack
 from helpers import source_file
 review=source_file(repo)
 assert resolve_sources(repo,'all')==(review,)
def test_exam_mismatch_rejected(approved_exam,repo):
 approved_exam.write_text(approved_exam.read_text().replace('id="p75"','id="p76"'))
 with pytest.raises(ExplainError):load_exam_source(approved_exam,repo)
def test_missing_new_feedback_invalidates_adapter(approved_exam,repo):
 f=repo/'웹과제/6장/note-feedback.md';f.parent.mkdir(parents=True);f.write_text('new')
 with pytest.raises(ExplainError):load_exam_source(approved_exam,repo)
