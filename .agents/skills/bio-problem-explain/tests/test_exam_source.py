import pytest
from exam_helpers import repo,approved_exam
from mpe_exam import load_exam_source
from mpe_source import load_source,resolve_sources
from mpe_types import ExplainError

def test_exam_has_all_formats(approved_exam,repo):
 pack=load_exam_source(approved_exam,repo)
 assert pack.profile=='exam' and len(pack.problems)==75
 assert sum(p.choice is not None for p in pack.problems)==55
 assert sum(p.short_answer is not None for p in pack.problems)==20
 assert [p.id for p in pack.problems]==[f'p{i}' for i in range(1,76)]
 assert pack.problems[55].short_answer.canonical=='Aa'
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
