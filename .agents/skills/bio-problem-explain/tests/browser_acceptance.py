"""Run synthetic browser acceptance: python browser_acceptance.py EMPTY_SCRATCH."""
import sys,json,threading,http.server,functools
from pathlib import Path
SKILL=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(SKILL/'scripts'),str(SKILL/'tests')]
from helpers import acceptance_pack
from mpe_render import build_explanation,check_artifacts
from playwright.sync_api import sync_playwright
root=Path(sys.argv[1]).resolve();root.mkdir(parents=True,exist_ok=True)
if any(root.iterdir()): raise SystemExit('acceptance scratch must be empty')
pack,fragments=acceptance_pack(root/'repo')
import shutil
shutil.rmtree(root/'stage',ignore_errors=True)
art=build_explanation(pack,fragments,root/'stage',root/'repo')
assert check_artifacts(pack,art)==[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start();port=server.server_port
url=f'http://127.0.0.1:{port}/stage/{art.html.name}'
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 for width,height in [(1280,900),(375,812)]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme)
   logs=[];failed=[];external=[]
   page.on('pageerror',lambda e:logs.append(str(e)))
   page.on('console',lambda e:logs.append(e.text) if e.type=='error' else None)
   page.on('requestfailed',lambda r:failed.append(r.url))
   page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(f'http://127.0.0.1:{port}/') else None)
   page.goto(url,wait_until='networkidle')
   page.locator('#pager-next').click();page.wait_for_timeout(100)
   assert page.locator('#p1').is_visible()
   for token in ['pre code','table','svg[aria-label="상태 그림"]','img']:
    assert page.locator('#p1 '+token).count()>0,token
   assert page.locator('#p1 .katex').count()>0
   assert page.locator('#p1 [data-explanation="start"] .katex').first.evaluate('(e)=>getComputedStyle(e).overflowX')=='visible'
   if width<800 or not page.locator('#panel-right').is_visible(): page.locator('#toggle-right').click()
   page.wait_for_timeout(250)
   assert page.locator('#panel-right').is_visible()
   assert page.locator('#panel-right .summary-group').count()>0
   if width<800:page.locator('#panel-right [data-panel-close]').click()
   else:
    handle=page.locator('#panel-right .panel-resize');handle.focus();handle.press('ArrowLeft');handle.press('Home')
    page.locator('#toggle-right').click()
   page.locator('#pager-next').click();assert page.locator('#p2').is_visible()
   page.locator('#pager-prev').click();assert page.locator('#p1').is_visible()
   page.locator('#toggle-left').click();page.wait_for_timeout(250)
   if width>=800:page.locator('#toggle-left').click()
   page.locator('#panel-left a[href="#p2"]').click();page.wait_for_timeout(150)
   assert page.locator('#p2').is_visible()
   page.locator('#theme-toggle').click();page.wait_for_timeout(100)
   page.locator('#theme-toggle').click()
   page.set_viewport_size({'width':width+10,'height':height});page.set_viewport_size({'width':width,'height':height})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('.katex-error').count()==0
   assert page.locator('#p2 img').evaluate('(e)=>e.complete && e.naturalWidth>0')
   page.screenshot(path=str(root/f'{width}-{theme}.png'),full_page=True)
   assert not logs and not failed and not external,(logs,failed,external)
   results.append({'viewport':[width,height],'theme':theme,'console_errors':logs,'failed_resources':failed,'external_requests':external,'overflow':False,'interaction':'TOC, next/prev, summary, close, resize, theme pass'})
   page.close()
 browser.close()
server.shutdown()
(root/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
