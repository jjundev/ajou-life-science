import json
from exam_cli import main
from exam_fixtures import make_candidates,approve_questions,dump

def prepared(repo,tmp_path):
 run=tmp_path/'run'
 assert main(['prepare','--repo',str(repo),'--scope','1~6','--run',str(run)])==0
 return run

def authored(repo,run):
 dump(run/'scope.json',json.loads((repo/'scope.json').read_text()));dump(run/'candidates.json',make_candidates(repo))
 (run/'policy-notes.md').write_text('TEST ONLY actual sections and applications')
 dump(run/'policy-summary.json',dict(type_targets=[],difficulty_targets=[],reason='TEST ONLY no targets'))

def test_prepare_select_build_check_roundtrip(repo,tmp_path):
 run=prepared(repo,tmp_path)
 assert main(['select','--run',str(run)])==1
 authored(repo,run)
 assert main(['select','--run',str(run)])==0
 assert main(['build','--run',str(run)])==0
 assert main(['check','--run',str(run)])==0
 assert main(['check','--run',str(run),'--final'])==1
 path=json.loads((run/'run.json').read_text())['question_html'];approve_questions(__import__('pathlib').Path(path))
 assert main(['check','--run',str(run),'--final'])==0
 assert main(['status','--run',str(run)])==0
 assert main(['prepare','--repo',str(repo),'--scope','1~6','--run',str(run)])==1

def test_shortage_stops_before_build(repo,tmp_path):
 run=prepared(repo,tmp_path);authored(repo,run);dump(run/'candidates.json',make_candidates(repo)[:8])
 assert main(['select','--run',str(run)])==1
 assert main(['build','--run',str(run)])==1
 assert not list(repo.glob('시험예상/**/*.html'))

def test_source_change_blocks_commands(repo,tmp_path):
 run=prepared(repo,tmp_path);authored(repo,run)
 (repo/'.agents/skills/bio-review-pack/references/note-feedback.md').write_text('changed')
 assert main(['select','--run',str(run)])==1

def test_build_rejects_stale_selection(repo,tmp_path):
 run=prepared(repo,tmp_path);authored(repo,run)
 assert main(['select','--run',str(run)])==0
 cs=json.loads((run/'candidates.json').read_text());cs[0]['problem_html']+='<p>새 조건</p>';dump(run/'candidates.json',cs)
 assert main(['build','--run',str(run)])==1

def test_reselect_rebuild_uses_corrected_authoring(repo,tmp_path):
 from pathlib import Path
 from exam_cli import record_repair
 run=prepared(repo,tmp_path);authored(repo,run)
 assert main(['select','--run',str(run)])==0
 assert main(['build','--run',str(run)])==0
 old=json.loads((run/'run.json').read_text());oldpath=Path(old['question_html']);oldbytes=oldpath.read_bytes()
 record_repair(run,'TEST ONLY 풀이 수정')
 cs=json.loads((run/'candidates.json').read_text())
 for c in cs:c['solution_steps']=['CORRECTED SOLUTION']
 dump(run/'candidates.json',cs)
 assert main(['select','--run',str(run)])==0
 assert main(['build','--run',str(run)])==0
 current=json.loads((run/'run.json').read_text());p=Path(current['question_html'])
 assert 'CORRECTED SOLUTION' in p.read_text()
 assert p!=oldpath and oldpath.read_bytes()==oldbytes
 assert current['repairs_used']==1

def test_current_run_versions_do_not_make_false_shortages(repo,tmp_path):
 from pathlib import Path
 from exam_contract import parse_scope
 from exam_selection import select_candidates
 run=prepared(repo,tmp_path);authored(repo,run)
 scope=json.loads((repo/'scope.json').read_text())
 result=select_candidates(make_candidates(repo),parse_scope('1~6'),{t['id']:t for t in scope['topics']})
 dump(run/'candidates.json',list(result.problems))
 for i in range(3):
  assert main(['select','--run',str(run)])==0
  assert main(['build','--run',str(run)])==0
 assert json.loads((run/'run.json').read_text())['question_html'].endswith('_v3.html')
