import pytest
from exam_fixtures import make_pack,approve_questions
from exam_check import completion_status
from exam_cli import record_repair
from exam_contract import ExamError

def test_explanation_failure_is_partial(repo):
 p=make_pack(repo);assert completion_status(p,None,dict(repairs_used=0))['status']=='unverified'
 approve_questions(p);assert completion_status(p,None,dict(repairs_used=0))['status']=='partial'
 fake=p.parent/'fake.html';fake.write_text('exists')
 assert completion_status(p,fake,dict(repairs_used=0))['status']=='partial'
def test_one_repair_budget_across_handoff(tmp_path):
 from exam_build import dump,load
 run=tmp_path/'run';run.mkdir();dump(run/'run.json',dict(repairs_used=0))
 record_repair(run,'question correction');assert load(run/'run.json')['repairs_used']==1
 record_repair(run,'explanation correction');assert load(run/'run.json')['repairs_used']==2
 with pytest.raises(ExamError):record_repair(run,'third correction')
 value=load(run/'run.json');value['repairs_used']=0;dump(run/'run.json',value)
 with pytest.raises(ExamError):record_repair(run,'reset attempt')
