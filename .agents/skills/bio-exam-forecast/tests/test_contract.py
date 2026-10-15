import copy
import pytest
from exam_contract import *
def test_scope_range_and_single():
 assert parse_scope(' 1장 ～ 6장 ').chapters==(1,2,3,4,5,6)
 assert parse_scope('4장-5장').label=='4장-5장'
 assert parse_scope('3').label=='3장'
@pytest.mark.parametrize('value',['6장~1장','0','-1','1,3','../1장',''])
def test_scope_rejects_invalid(value):
 with pytest.raises(ExamError): parse_scope(value)
def test_short_normalization_preserves_meaning():
 assert normalize_short('  BRCA1  ')=='BRCA1'
 assert normalize_short('A a')!=normalize_short('Aa')
 assert normalize_short('Aa')!=normalize_short('aa')
 assert normalize_short('ATP',case_sensitive=False)=='atp'
def test_candidate_boundaries(six_chapter_candidates,topics):
 c=copy.deepcopy(six_chapter_candidates[0]);s=parse_scope('1~6')
 assert validate_candidate(c,s,topics)==[]
 for field,value in [('required_chapters',[7]),('answer',dict(kind='choice',option_id='E')),('options',[]),('mode','unknown'),('style_basis',[])]:
  bad=copy.deepcopy(c);bad[field]=value;assert validate_candidate(bad,s,topics),field
 badtopics=copy.deepcopy(topics);badtopics['t1']['scope_status']='uncertain'
 assert validate_candidate(c,s,badtopics)
 c=copy.deepcopy(six_chapter_candidates[20]);c['answer']['accepted']=[]
 assert validate_candidate(c,s,topics)
def test_original_requires_payload(six_chapter_candidates,topics):
 c=copy.deepcopy(six_chapter_candidates[0]);c['mode']='original'
 assert validate_candidate(c,parse_scope('1~6'),topics)

def test_option_text_and_active_markup_rejected(six_chapter_candidates,topics):
 c=copy.deepcopy(six_chapter_candidates[0]);c['options'][0]['text']='모델에만 있는 보기'
 assert validate_candidate(c,parse_scope('1~6'),topics)
 c=copy.deepcopy(six_chapter_candidates[0]);c['problem_html']+='<script>window.answer="B"</script>'
 assert validate_candidate(c,parse_scope('1~6'),topics)
