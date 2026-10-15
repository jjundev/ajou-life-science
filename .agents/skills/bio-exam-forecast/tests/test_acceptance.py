"""Synthetic pipeline/UI acceptance; never claims academic question validity."""
import importlib.util,json,sys,subprocess
from pathlib import Path
from exam_fixtures import make_pack,approve_questions,ROOT
from exam_check import check_set,completion_status
from exam_blind import write_blind
from playwright.sync_api import sync_playwright

def test_visual_exam_to_published_explanation(repo,tmp_path):
 question=make_pack(repo);approve_questions(question);assert not check_set(question,require_reviews=True)
 blind=write_blind(question,tmp_path/'blind/index.html')
 assert '<svg' in blind.read_text() and '<table' in blind.read_text() and '<img' in blind.read_text()
 scripts=ROOT/'.agents/skills/bio-problem-explain/scripts';cli=scripts/'mpe_cli.py';run=tmp_path/'explain'
 def call(*args):
  r=subprocess.run([sys.executable,str(cli),*map(str,args)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 call('extract','--repo',repo,'--target',question,'--run',run)
 # Only testing pipeline plumbing. TEST ONLY reviews are produced by test fixtures.
 code='''import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2])
from mpe_cli import load_run,load_artifacts,load_fragments
from helpers import fragment,approved
item=load_run(Path(sys.argv[3]))[0]
for p in item['pack'].problems:(item['folder']/'explanations'/f'{p.id}.html').write_text(fragment(p))
'''
 r=subprocess.run([sys.executable,'-c',code,str(scripts),str(scripts.parent/'tests'),str(run)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 call('build','--run',run);call('check','--run',run)
 code2=code[:code.index("for p in item")] + "review=approved(item['pack'],load_fragments(item),load_artifacts(item));(item['folder']/'review.json').write_text(json.dumps(review))\n"
 r=subprocess.run([sys.executable,'-c',code2,str(scripts),str(scripts.parent/'tests'),str(run)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 call('publish','--run',run)
 explanation=question.parent/'문제해설_1장-6장_시험예상_v1.html'
 status=completion_status(question,explanation,dict(repairs_used=0));assert status['status']=='complete',status
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  for width,height in [(1280,900),(375,812)]:
   for scheme in ('light','dark'):
    page=browser.new_page(viewport=dict(width=width,height=height),color_scheme=scheme);errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for p in (question,explanation):
     page.goto(p.as_uri());assert page.locator('article').count()==75
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
     assert page.locator('.katex').count()>0
    assert not errors;page.close()
  browser.close()
 # Changing a source after publication must prevent complete, even with both files present.
 f=repo/'웹과제/6장/note-feedback.md';f.parent.mkdir(parents=True);f.write_text('new')
 assert completion_status(question,explanation,dict(repairs_used=0))['status']!='complete'
