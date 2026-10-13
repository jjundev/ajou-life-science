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
 for width,height in [(1280,900),(1024,768),(375,812)]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme)
   logs=[];failed=[];external=[]
   page.on('pageerror',lambda e:logs.append(str(e)))
   page.on('console',lambda e:logs.append(e.text) if e.type=='error' else None)
   page.on('requestfailed',lambda r:failed.append(r.url))
   page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(f'http://127.0.0.1:{port}/') else None)
   page.goto(url+'#p3',wait_until='networkidle');page.wait_for_timeout(100)
   if width>=1024:
    assert page.locator('#panel-right .probs [data-problem-for="p3"]').is_visible()
    assert page.locator('#p3 > [data-problem-for]').count()==0
    assert page.locator('#panel-right [role=tab][data-tab="problem"]').get_attribute('aria-selected')=='true'
    page.locator('#panel-right [data-tab="summary"]').click()
    assert page.locator('#panel-right .sums .summary-group:visible').count()==1
    page.locator('#panel-right [data-tab="problem"]').click()
   else:
    toggle=page.locator('#p3 .problem-toggle')
    assert toggle.get_attribute('aria-expanded')=='false' and not page.locator('#p3 [data-problem-for="p3"]').is_visible()
    toggle.click();assert page.locator('#p3 [data-problem-for="p3"]').is_visible() and toggle.inner_text()=='문제 접기'
   assert page.locator('#p3 [data-explanation="understand"]').is_visible()
   pane=page.locator('[data-problem-for="p3"]')
   assert pane.locator('.review-choice').count()==5
   assert pane.locator('.review-badge:visible').count()==0
   pane.locator('.review-choice[data-choice-id="5"]').click();page.wait_for_timeout(100)
   assert pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='incorrect'
   assert pane.locator('[data-choice-id="3"]').get_attribute('data-result')=='correct'
   assert '정답' in pane.locator('[data-choice-id="3"] .review-badge').inner_text()
   assert '내 선택' in pane.locator('[data-choice-id="5"] .review-badge').inner_text()
   assert pane.locator('.review-status').inner_text()=='정답이 아니에요. 해설에서 판정 이유를 확인해요.'
   target=page.locator('#p3 [data-explanation="solve"] p.is-target')
   assert target.count()==1 and target.inner_text().startswith('(5)')
   assert target.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
   page.wait_for_timeout(1700);assert target.count()==0
   page.set_viewport_size({'width':900 if width>=1024 else 1280,'height':height});page.wait_for_timeout(150)
   assert page.locator('[data-problem-for="p3"] [data-choice-id="5"]').get_attribute('data-result')=='incorrect'
   page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
   page.locator('[data-problem-for="p3"] .review-reset').click()
   assert page.locator('[data-problem-for="p3"] [data-result="correct"]').count()==0
   page.goto(url+'#p4');page.wait_for_timeout(100)
   if width<1024:page.locator('#p4 .problem-toggle').click()
   p4=page.locator('[data-problem-for="p4"]');p4.locator('[data-choice-id="1"]').click();page.wait_for_timeout(100)
   assert '출제 의도상 답' in p4.locator('[data-choice-id="2"] .review-badge').inner_text()
   assert p4.locator('[data-choice-id="2"]').get_attribute('data-result')=='intended'
   assert p4.locator('.review-status').inner_text()=='출제 의도상 답을 표시했어요.'
   assert page.locator('#p4 [data-explanation="solve"] h4.is-target').count()==1
   page.goto(url+'#p1');page.wait_for_timeout(100)
   assert page.locator('[data-problem-for="p1"] .review-choice').count()==0
   if width>=1024:
    page.goto(url+'#p2');page.wait_for_timeout(100)
    page.locator('[data-problem-for="p2"] img').first.click()
    assert page.locator('dialog.figure-sheet[open] img').is_visible()
    page.keyboard.press('Escape');page.wait_for_timeout(100)
    assert page.locator('dialog.figure-sheet[open]').count()==0
    page.locator('[data-problem-for="p2"] svg[aria-label="문제 화살표"]').click()
    assert page.locator('dialog.figure-sheet[open] svg').is_visible()
    assert page.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(e=>e.id);return a.length===new Set(a).size})()')
    page.keyboard.press('Escape');page.wait_for_timeout(100)
   page.goto(url+'#p3');page.wait_for_timeout(100)
   page.emulate_media(media='print');page.wait_for_timeout(150)
   assert page.locator('#p3 > [data-problem-for="p3"] [data-source-problem="p3"]').is_visible()
   assert page.locator('#p1 > [data-problem-for="p1"]').is_visible() and page.locator('.problem-toggle:visible').count()==0
   page.emulate_media(media='screen');page.wait_for_timeout(150)
   if width>=1024:assert page.locator('#panel-right .probs [data-problem-for="p3"]').is_visible()
   else:assert page.locator('#p3 .problem-toggle').is_visible()
   page.goto(url,wait_until='networkidle')
   page.locator('#pager-next').click();page.wait_for_timeout(100)
   assert page.locator('#p1').is_visible()
   for token in ['pre code','table','svg[aria-label="상태 그림"]','img']:
    assert page.locator(f'#p1 {token}, [data-problem-for="p1"] {token}').count()>0,token
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
   if width>=1024 and page.locator('#toggle-left').get_attribute('aria-expanded')=='false':page.locator('#toggle-left').click()
   page.locator('#panel-left a[href="#p2"]').click();page.wait_for_timeout(150)
   assert page.locator('#p2').is_visible()
   page.locator('#theme-toggle').click();page.wait_for_timeout(100)
   page.locator('#theme-toggle').click()
   page.set_viewport_size({'width':width+10,'height':height});page.set_viewport_size({'width':width,'height':height})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('.katex-error').count()==0
   assert page.locator('#p2 img[alt="검증용 픽셀"]').evaluate('(e)=>e.complete && e.naturalWidth>0')
   page.screenshot(path=str(root/f'{width}-{theme}.png'),full_page=True)
   assert not logs and not failed and not external,(logs,failed,external)
   results.append({'viewport':[width,height],'theme':theme,'console_errors':logs,'failed_resources':failed,'external_requests':external,'overflow':False,'interaction':'TOC, next/prev, summary, close, resize, theme pass'})
   page.close()
 browser.close()
server.shutdown()
(root/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
