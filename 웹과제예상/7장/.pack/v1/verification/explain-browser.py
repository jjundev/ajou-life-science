from pathlib import Path
from urllib.parse import quote,unquote,urlparse
import json,http.server,threading
from playwright.sync_api import sync_playwright
repo=Path.cwd();run=Path('/tmp/webquiz-forecast/7장-v1');f=Path('/private/tmp/bio-problem-explain/forecast-ch7-v1-3/forecast-7장-웹과제예상_v1');st=json.loads((f/'stage.json').read_text());stage=f/st['stage'];prefix='/웹과제예상/7장/';name=st['html']; key=json.loads((repo/'웹과제예상/7장/.pack/v1/pack.json').read_text())['answer_key']
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):
  p=unquote(urlparse(path).path)
  if p.startswith(prefix):
   target=stage/p[len(prefix):]
   if target.is_file():return str(target)
  return str(repo/p.lstrip('/'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}';url=base+quote(prefix+name)
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for w,h in [(1280,900),(375,812)]:
  for theme in ['light','dark']:
   ctx=b.new_context(viewport=dict(width=w,height=h),color_scheme=theme,reduced_motion='reduce');page=ctx.new_page();errors=[];bad=[];external=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(base) and not r.url.startswith('data:') else None)
   page.goto(url+'#p1',wait_until='networkidle')
   page.evaluate('(t)=>{document.documentElement.dataset.theme=t;localStorage.setItem("od-theme",t)}',theme)
   if w>=1024:
    assert page.locator('#panel-left').is_visible() and page.locator('#panel-prob').is_visible()
    page.locator('#tab-original').click();assert page.locator('#tabpanel-original').is_visible();page.locator('#tab-problem').click()
    page.locator('[data-dock="right"]').click();assert page.locator('.layout').get_attribute('data-prob-dock')=='right'
    page.locator('#toggle-right').click();assert page.locator('#panel-prob').is_visible() and page.locator('#panel-right').is_visible()
    page.locator('[data-dock="float"]').click();assert page.locator('.layout').get_attribute('data-prob-dock')=='float'
    page.locator('.float-move').focus();page.keyboard.press('ArrowRight');page.keyboard.press('ArrowDown')
    page.locator('.float-resize').focus();page.keyboard.press('ArrowRight');page.keyboard.press('ArrowDown')
    rect=page.locator('#panel-prob').bounding_box();assert rect['x']>=0 and rect['y']>=0 and rect['x']+rect['width']<=w+1
    page.locator('[data-dock="left"]').click();page.locator('#toggle-right').click()
   for i in range(1,16):
    pid=f'p{i}';page.evaluate('(id)=>location.hash=id',pid);page.wait_for_timeout(30)
    assert page.locator('#'+pid).evaluate('(e)=>e.classList.contains("is-current")')
    if w<1024:
     toggle=page.locator(f'#{pid} .problem-toggle')
     if toggle.get_attribute('aria-expanded')!='true':toggle.click()
    pane=page.locator(f'[data-problem-for="{pid}"]'); wrong=chr(65+(ord(key[pid])-65+1)%5)
    pane.locator(f'.review-choice[data-choice-id="{wrong}"]').click()
    assert pane.locator('.review-status').get_attribute('data-result')=='incorrect'
    pane.locator('.review-reset').click();pane.locator(f'.review-choice[data-choice-id="{key[pid]}"]').click();assert pane.locator('.review-status').get_attribute('data-result')=='correct'
    assert page.locator('.katex-error').count()==0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    if w==1280 and theme=='light':
     for a in page.locator(f'#{pid} [data-explanation="recall"] a').all():
      href=a.get_attribute('href');check=ctx.new_page();check.goto(url+'#'+pid);link=check.locator(f'#{pid} [data-explanation="recall"] a[href="{href}"]');link.click();check.wait_for_load_state('networkidle');anchor=unquote(urlparse(check.url).fragment);assert check.locator('[id="'+anchor+'"]').count()==1;check.close()
    if i in [8,9]:
     pane.locator('svg').click();assert page.locator('dialog[open]').count()==1;page.locator('dialog[open] button').first.click()
   page.evaluate("location.hash='p13'");page.wait_for_timeout(50)
   if w<1024:
    page.locator('#p13 .problem-toggle').click() if page.locator('#p13 .problem-toggle').get_attribute('aria-expanded')!='true' else None
   page.screenshot(path=str(run/f'explain-{w}-{theme}.png'))
   assert not errors,errors;assert not bad,bad;assert not external,external
   results.append(dict(width=w,theme=theme,status='pass',questions=15,errors=errors,missing=bad,external=external,stage=str(stage)))
   (run/'explain-browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(w,theme,'PASS',flush=True);ctx.close()
 b.close()
server.shutdown();print('EXPLANATION BROWSER PASS')
