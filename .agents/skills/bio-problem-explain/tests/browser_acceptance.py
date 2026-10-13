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
# p4 stands in for a forecast problem without an original (review sources always carry one)
import re
art.html.write_text(re.sub(r'<details class="original" data-original-problem="p4">.*?</details>','',art.html.read_text(),count=1,flags=re.S))
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
    assert page.locator('#tab-original').is_visible()
    page.locator('#tab-original').click()
    orig=page.locator('#tabpanel-original details.original[data-original-problem="p3"][open]')
    assert orig.is_visible() and '합성 원문 3' in orig.inner_text()
    assert orig.locator('summary').is_hidden() and page.locator('#tabpanel-problem').is_hidden()
    assert page.locator('[data-problem-for="p3"] details.original').count()==0
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#p3 [data-problem-for="p3"] details.original:not([open])').count()==1
    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
    assert page.locator('details.original[data-original-problem="p3"]').count()==1 and orig.is_visible()
    page.goto(url+'#p4');page.wait_for_timeout(100)
    assert page.locator('#tab-original').is_hidden()
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true' and page.locator('[data-problem-for="p4"]').is_visible()
    page.goto(url+'#p3');page.wait_for_timeout(100)
    assert page.locator('#tab-original').get_attribute('aria-selected')=='true'
    page.locator('#tab-original').focus();page.keyboard.press('ArrowRight')
    assert page.locator('#tab-summary').get_attribute('aria-selected')=='true'
    page.keyboard.press('ArrowRight')
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true'
   else:
    toggle=page.locator('#p3 .problem-toggle')
    assert toggle.get_attribute('aria-expanded')=='false' and not page.locator('#p3 [data-problem-for="p3"]').is_visible()
    toggle.click();assert page.locator('#p3 [data-problem-for="p3"]').is_visible() and toggle.inner_text()=='문제 접기'
    assert page.locator('#p3 [data-problem-for="p3"] details.original:not([open])').count()==1
    assert page.locator('#tab-original').is_hidden()
   assert page.locator('#p3 [data-explanation="understand"]').is_visible()
   pane=page.locator('[data-problem-for="p3"]')
   assert pane.locator('.review-choice').count()==5
   assert pane.locator('.review-choice-label:visible').count()==0
   pane.evaluate("e=>{const l=e.querySelector('.choices');for(const w of ['before','after']){const d=document.createElement('div');d.className='test-spacer';d.style.height='1400px';l[w](d)}}")
   pane.locator('.review-choice[data-choice-id="5"]').click();page.wait_for_timeout(100)
   fb=page.locator('.review-feedback[data-result="incorrect"]')
   assert fb.is_visible() and fb.inner_text()=='다시 확인해요'
   assert pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='selected'
   assert pane.locator('[data-choice-id="3"]').get_attribute('data-result')=='correct'
   assert pane.locator('[data-choice-id="3"] .review-choice-label').inner_text()=='정답'
   assert pane.locator('[data-choice-id="1"] .review-choice-label').inner_text()=='정답 아님'
   assert pane.locator('[data-choice-id="5"] .review-choice-label').inner_text()=='내 선택 · 정답 아님'
   assert pane.locator('.review-status').inner_text()=='정답이 아니에요. 보기별 이유를 확인해 보세요.'
   assert pane.locator('.review-status ~ .choices').count()==1
   centered=pane.evaluate("""e=>{const s=e.closest('.panel-inner')||document.querySelector('.content');
     const a=e.querySelector('[data-choice-id="5"]').closest('li').getBoundingClientRect(),b=e.querySelector('[data-choice-id="3"]').closest('li').getBoundingClientRect(),v=s.getBoundingClientRect();
     return Math.abs((Math.min(a.top,b.top)+Math.max(a.bottom,b.bottom))/2-(v.top+v.bottom)/2)<24}""")
   assert centered
   pane.locator('.review-choice[data-choice-id="4"]').click();page.wait_for_timeout(50)
   assert pane.locator('[data-choice-id="4"]').get_attribute('data-result')=='' and pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='selected'
   target=page.locator('#p3 [data-explanation="solve"] p.is-target')
   if width>=1024:
    assert target.count()==1 and target.inner_text().startswith('(5)')
    assert target.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
   else: assert target.count()==0
   page.wait_for_timeout(1700);assert target.count()==0 and fb.count()==0
   page.set_viewport_size({'width':900 if width>=1024 else 1280,'height':height});page.wait_for_timeout(150)
   assert page.locator('[data-problem-for="p3"] [data-choice-id="5"]').get_attribute('data-result')=='selected'
   page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
   page.locator('[data-problem-for="p3"] .review-reset').click()
   assert page.locator('[data-problem-for="p3"] [data-result="correct"]').count()==0
   page.locator('[data-problem-for="p3"] .review-choice[data-choice-id="5"]').click()
   assert page.locator('[data-problem-for="p3"] .review-reset').inner_text()=='다시 풀기'
   page.locator('[data-problem-for="p3"] .review-reset').click()
   assert page.locator('.review-feedback').count()==0
   page.locator('[data-problem-for="p3"] .review-choice[data-choice-id="3"]').click();page.wait_for_timeout(50)
   assert page.locator('.review-feedback[data-result="correct"]').inner_text()=='정답이에요'
   assert page.locator('[data-problem-for="p3"] .review-status').inner_text()=='정답이에요.'
   page.locator('[data-problem-for="p3"] .review-reset').click()
   page.evaluate("document.querySelectorAll('.test-spacer').forEach(n=>n.remove())")
   page.goto(url+'#p4');page.wait_for_timeout(100)
   if width<1024:page.locator('#p4 .problem-toggle').click()
   p4=page.locator('[data-problem-for="p4"]');p4.locator('[data-choice-id="1"]').click();page.wait_for_timeout(100)
   assert p4.locator('[data-choice-id="2"] .review-choice-label').inner_text()=='출제 의도상 답'
   assert p4.locator('[data-choice-id="2"]').get_attribute('data-result')=='intended'
   assert p4.locator('[data-choice-id="1"]').get_attribute('data-result')=='uncertain'
   assert p4.locator('.review-status').inner_text()=='단일 정답 판정 주의'
   assert page.locator('.review-feedback').count()==0
   assert page.locator('#p4 [data-explanation="solve"] h4.is-target').count()==(1 if width>=1024 else 0)
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
   assert page.locator('#p3 > [data-problem-for="p3"] details.original[open]').is_visible()
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
