import pytest
from exam_contract import parse_scope,ExamError
from exam_sources import inventory,assert_fresh,web_candidates,past_candidates,local
from exam_fixtures import POLICY

def test_inventory_reads_live_policy(repo):
 m=inventory(repo,parse_scope('1~6'));p=repo/POLICY/'webquiz-style.md';p.write_text('정책 B')
 assert inventory(repo,parse_scope('1~6'))!=m
 with pytest.raises(ExamError):assert_fresh(repo,m)
def test_missing_feedback_becomes_present(repo):
 m=inventory(repo,parse_scope('1~6'))
 row=next(s for s in m['sources'] if s['path']=='웹과제/6장/note-feedback.md')
 assert row['status']=='missing' and row['sha256'] is None
 p=repo/row['path'];p.parent.mkdir(parents=True);p.write_text('new')
 with pytest.raises(ExamError):assert_fresh(repo,m)
 (repo/POLICY/'webquiz-style.md').unlink()
 with pytest.raises(ExamError):inventory(repo,parse_scope('1~6'))
def test_nfc_nfd_and_path_escape(repo,tmp_path):
 import unicodedata
 p=repo/unicodedata.normalize('NFD','자료');p.mkdir();(p/'note.md').write_text('x')
 assert local(repo,'자료/note.md').is_file()
 (repo/'escape').symlink_to(tmp_path)
 with pytest.raises(ExamError):local(repo,'escape/out')
 with pytest.raises(ExamError):local(repo,'../out')
def test_invalid_bank_excluded(repo):
 p=repo/'웹과제/1장/questions.json';p.parent.mkdir(parents=True);p.write_text('{}')
 cs,excluded=web_candidates(repo,parse_scope('1'))
 assert cs==[] and excluded and 'reason' in excluded[0]
def test_past_collector_is_unreviewed(repo):
 assert past_candidates(repo,parse_scope('1~6'))==[]

def test_selected_is_not_answer_and_bank_assets(repo):
 import sys,json,copy
 from pathlib import Path
 from exam_sources import ROOT,bank_model,sha
 sys.path.insert(0,str(ROOT/'tests'))
 from question_bank_fixture import make_bank
 path,bank=make_bank(repo/'웹과제/1장');q=bank['questions'][0]
 q['original']['options'] += [dict(id='C',text='단백질'),dict(id='D',text='물')]
 q['analysis']['option_diagnostics'].update({letter:dict(is_answer=False,explanation='틀림',requirement_ids=['r1']) for letter in 'CD'})
 q['original']['content'].append(dict(type='statements',items=[dict(id='a',text='조건 목록')]))
 q['analysis']['requirements'][0]['evidence'][0]['path']='웹과제/1장/evidence.md'
 model=bank_model();q['review']=dict(status='verified',payload_sha256=model.canonical_digest(model.question_payload(bank,q,path.parent,repo_root=repo)),notes='TEST ONLY')
 path.write_text(json.dumps(bank,ensure_ascii=False))
 cs,excluded=web_candidates(repo,parse_scope('1'))
 assert not excluded and len(cs)==1
 assert cs[0]['answer']==dict(kind='choice',option_id='A')
 assert cs[0]['official_answer'] is None and cs[0]['answer_status']=='reasoned'
 assert all(x['status']=='not_run' for x in cs[0]['review'].values())
 manifest=inventory(repo,parse_scope('1'));assert any(s['role']=='bank_raw' for s in manifest['sources'])
 assert any(s['role']=='bank_evidence' for s in manifest['sources'])
