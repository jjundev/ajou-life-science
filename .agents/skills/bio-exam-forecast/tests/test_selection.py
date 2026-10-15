import copy
from collections import Counter
from exam_contract import parse_scope
from exam_selection import *
def test_six_chapter_quotas():
 q=allocate_quotas(parse_scope('1~6'))
 assert [q[n]['total'] for n in range(1,7)]==[13,13,13,12,12,12]
 assert [q[n]['mcq'] for n in range(1,7)]==[10,9,9,9,9,9]
 assert [q[n]['short'] for n in range(1,7)]==[3,4,4,3,3,3]
def test_missing_web_bank_does_not_erase_chapter(six_chapter_candidates,topics):
 r=select_candidates(six_chapter_candidates,parse_scope('1~6'),topics)
 assert len(r.problems)==75 and not r.shortages
 assert sum(p['primary_chapter']==6 for p in r.problems)==12
 assert len({p['family_id'] for p in r.problems})==75
 assert r==select_candidates(list(reversed(six_chapter_candidates)),parse_scope('1~6'),topics)
def test_narrow_scope_reports_shortage(six_chapter_candidates,topics):
 r=select_candidates(six_chapter_candidates[:8],parse_scope('1'),topics)
 assert len(r.problems)==8 and sum(s['missing'] for s in r.shortages)==67
def test_reassigns_family_for_scarce_short_slot(six_chapter_candidates,topics):
 rows=copy.deepcopy(six_chapter_candidates)
 # All short choices in chapter 1 must consume families initially preferred for MCQ.
 mcq=[c for c in rows if c['primary_chapter']==1 and c['format']=='mcq']
 shorts=[c for c in rows if c['primary_chapter']==1 and c['format']=='short']
 for a,b in zip(mcq,shorts):b['family_id']=a['family_id']
 r=select_candidates(rows,parse_scope('1~6'),topics)
 assert len(r.problems)==75 and len({p['family_id'] for p in r.problems})==75
def test_cross_source_duplicate_and_previous(six_chapter_candidates,topics):
 rows=copy.deepcopy(six_chapter_candidates);dup=copy.deepcopy(rows[0]);dup.update(id='duplicate',family_id='different',origin='past');rows.append(dup)
 prev=copy.deepcopy(rows[2]);prev['mode']='generated'
 r=select_candidates(rows,parse_scope('1~6'),topics,previous=(prev,))
 assert len(r.problems)==75
 assert sum(p['problem_html']==rows[0]['problem_html'] for p in r.problems)<=1
 assert not any(p['problem_html']==prev['problem_html'] and p['mode']=='generated' for p in r.problems)
def test_rich_pool_meets_source_targets(six_chapter_candidates,topics):
 rows=copy.deepcopy(six_chapter_candidates)
 for c in rows:
  i=int(c['id'].rsplit('-',1)[1]);c['origin']=['web','web','past','new'][i%4];c['mode']='original' if i%4 in (0,2) else ('generated' if i%4==3 else 'variant')
  if c['format']=='short' and c['origin']=='web':c['mode']='variant'
  from exam_contract import payload
  c['original_payload_sha256']=payload(c)
 r=select_candidates(rows,parse_scope('1~6'),topics)
 assert len(r.problems)==75
 counts=Counter((p['format'],p['origin'],p['mode']) for p in r.problems)
 assert counts['mcq','web','original']==20
 assert counts['mcq','web','variant']==10
 assert counts['mcq','past','original']==10
 assert counts['mcq','new','generated']==15
 assert not r.deviations

def test_generated_stem_reuse_with_new_options_rejected(six_chapter_candidates,topics):
 rows=copy.deepcopy(six_chapter_candidates);prev=copy.deepcopy(rows[2]);prev['mode']='generated'
 rows[2]['priority'][0]=True
 rows[2]['options'][0]['text']='수정한 보기';rows[2]['problem_html']=rows[2]['problem_html'].replace('보기 A','수정한 보기')
 r=select_candidates(rows,parse_scope('1~6'),topics,previous=(prev,))
 assert rows[2]['id'] not in {c['id'] for c in r.problems}

def test_exam_emphasis_beats_source_balance(six_chapter_candidates,topics):
 rows=copy.deepcopy(six_chapter_candidates)
 # High-emphasis candidates are all web; enough alternatives still fill every slot.
 for c in rows:
  if c['primary_chapter']==1 and c['format']=='mcq' and int(c['id'].rsplit('-',1)[1])<10:
   c['priority'][0]=True;c['origin']='web';c['mode']='variant'
 r=select_candidates(rows,parse_scope('1~6'),topics)
 assert sum(c['priority'][0] for c in r.problems)==10

def test_same_generated_stem_cannot_fill_two_slots(six_chapter_candidates,topics):
 rows=copy.deepcopy(list(select_candidates(six_chapter_candidates,parse_scope('1~6'),topics).problems))
 for c in rows[:2]:
  choices=c['problem_html'][c['problem_html'].index('<ul class="choices">'):]
  c.update(origin='new',mode='generated',problem_html='<p>Shared generated stem?</p>'+choices)
 r=select_candidates(rows,parse_scope('1~6'),topics)
 assert len(r.problems)==74 and sum(x['missing'] for x in r.shortages)==1
