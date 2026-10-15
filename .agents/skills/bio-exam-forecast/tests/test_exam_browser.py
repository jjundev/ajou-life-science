import pytest
from playwright.sync_api import sync_playwright
from exam_fixtures import make_pack
@pytest.mark.parametrize('width,height,scheme',[(1280,900,'light'),(1280,900,'dark'),(375,812,'light'),(375,812,'dark')])
def test_submit_is_only_reveal_boundary(repo,width,height,scheme):
 p=make_pack(repo)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport=dict(width=width,height=height),color_scheme=scheme)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  remote=[];page.on('request',lambda r:remote.append(r.url) if r.url.startswith(('http:','https:')) else None)
  page.goto(p.as_uri());page.locator('#p1 input[value="B"]').check();page.locator('#p55 input[value="B"]').check()
  page.locator('#p56 input').fill('aa');page.locator('#p57 input').fill('合成誤答');page.locator('#p75 input').fill('합성 답')
  assert page.locator('.solution:visible').count()==0
  page.emulate_media(media='print');assert page.locator('.solution:visible').count()==0;page.emulate_media(media='screen')
  page.locator('#submit-exam').click()
  assert page.locator('.solution:visible').count()==75
  assert page.locator('#p56 .result').inner_text()=='자기채점 대기'
  assert page.locator('#p75 .result').inner_text()=='자동 일치'
  assert '미응답' in page.locator('#summary').inner_text()
  page.locator('#reset-exam').click();assert page.locator('.solution:visible').count()==0
  assert page.locator('#p56 input').input_value()==''
  assert page.locator('input:checked').count()==0
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  assert not errors and not remote
  browser.close()
def test_no_js(repo):
 p=make_pack(repo)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True);page=browser.new_page(java_script_enabled=False);page.goto(p.as_uri())
  assert page.locator('.solution:visible').count()==0
  browser.close()

def test_casefold_matches_python_without_changing_sensitive_answers(repo):
 import json
 p=make_pack(repo);s=p.read_text()
 # Test-only model isolates browser Unicode grading, no academic artifact approval.
 start=s.index('<script type="application/json" id="exam-model">')+len('<script type="application/json" id="exam-model">');end=s.index('</script>',start)
 models=json.loads(s[start:end]);models['p56']['answer']=dict(kind='short',canonical='ﬃ',accepted=['ﬃ'],case_sensitive=False)
 p.write_text(s[:start]+json.dumps(models)+s[end:])
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True);page=browser.new_page();page.goto(p.as_uri());page.locator('#p56 input').fill('ffi');page.locator('#submit-exam').click()
  assert page.locator('#p56 .result').inner_text()=='자동 일치'
  browser.close()
