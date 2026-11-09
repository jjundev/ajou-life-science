from pathlib import Path
import json,threading,http.server,functools,hashlib
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
R=Path.cwd();run=Path('/tmp/bio-webquiz-8-v2'); src=R/'웹과제예상/8장/.pack/v2';pack=json.loads((src/'pack.json').read_text());keys=pack['answer_key']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'; reports=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch()
  for mode,name in [('practice','복습문제_8장_웹과제예상_v2.html'),('exam','복습문제_8장_웹과제예상_시험형_v2.html')]:
   file=R/'웹과제예상/8장'/name;url=base+quote(file.relative_to(R).as_posix())
   for w,h in [(1280,900),(375,812)]:
    for theme in ['light','dark']:
     print(mode,w,theme,flush=True)
     page=b.new_page(viewport={'width':w,'height':h},color_scheme=theme)
     page.set_default_timeout(8000)
     errs=[];failed=[];external=[]
     page.on('pageerror',lambda e:errs.append(str(e)))
     page.on('console',lambda e:errs.append(e.text) if e.type=='error' else None)
     page.on('requestfailed',lambda r:failed.append(r.url))
     page.on('response',lambda r:failed.append(f'{r.status} {r.url}') if r.status>=400 else None)
     page.on('request',lambda r:external.append(r.url) if not r.url.startswith(base) else None)
     page.add_init_script("window.__copied=null;Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>{window.__copied=t}}})")
     page.goto(url,wait_until='networkidle')
     def visit(pid):
      page.evaluate('(id)=>location.hash=id',pid);page.locator('#'+pid).wait_for(state='visible');page.wait_for_timeout(80)
     def overflow():return page.evaluate('document.documentElement.scrollWidth>innerWidth')
     for pid in ['o1','o2'] if mode=='practice' else []:
      visit(pid);assert not overflow()
     if mode=='exam':
      assert page.locator('#o1,#o2').count()==0
      assert '출제 개요 보기' not in page.content()
      assert page.locator('.solution:visible,.hint:visible,.original:visible').count()==0
      assert page.locator('#open-explanation:visible').count()==0
     for i in range(1,16):
      pid=f'p{i}';visit(pid);assert not overflow(),(mode,w,theme,pid)
      if mode=='practice':
       choice=page.locator(f'#{pid} .review-choice').nth('ABCDE'.index(keys[pid]));choice.click()
       expect(page.locator(f'#{pid} .review-status')).to_have_text('정답이에요.')
       assert page.evaluate('location.hash')=='#'+pid
       assert page.locator(f'#{pid} .review-diagnostic:visible').count()==1
       other=next(c for c in 'ABCDE' if c!=keys[pid]);page.locator(f'#{pid} .review-choice').nth('ABCDE'.index(other)).click()
       assert page.locator(f'#{pid} .review-diagnostic:visible').count()==2
      else:
       page.locator(f'#{pid} input[value="{keys[pid]}"]').check()
       if i<15:expect(page.locator(f'#p{i+1}')).to_be_visible()
       assert page.locator('.solution:visible').count()==0
     if mode=='practice':
      visit('p1');page.locator('#p1 .review-reset').click();assert page.locator('#p1 .review-status').inner_text()==''
      page.locator('#p1 .review-choice').nth('ABCDE'.index(keys['p1'])).click()

      if page.locator('#toggle-right').get_attribute('aria-expanded')!='true':page.locator('#toggle-right').click()
      page.locator('.review-unsure:visible').wait_for(state='visible')
      btn=page.locator('.review-unsure:visible');assert btn.count()==1;btn.click();assert btn.get_attribute('data-unsure')=='true'
      if w<600:page.locator('#panel-right [data-panel-close]').click()
      visit('p15');page.locator('.review-export').click();page.wait_for_timeout(100);assert page.evaluate('window.__copied')
      assert page.locator('#exam-results').count()==0
     else:
      page.emulate_media(media='print');assert page.locator('.solution:visible').count()==0;page.emulate_media(media='screen')
      page.locator('#submit-exam').click();expect(page.locator('#results-title')).to_be_visible()
      assert page.locator('.exam-result-row').count()==15
      assert page.locator('#exam-scorecard tbody tr').count()==3
      assert page.locator('#exam-scorecard tbody tr').first.locator('td').count()==5
      page.locator('#copy-prompt').click();page.wait_for_timeout(100);assert page.evaluate('window.__copied')
      assert not overflow()
      page.locator('.exam-result-row a[href="#p1"]').click();expect(page.locator('#p1')).to_be_visible()
      assert page.locator('#p1 input').first.is_disabled()
     visit('p12');page.screenshot(path=str(run/f'{mode}-{w}-{theme}.png'),full_page=True)
     page.reload(wait_until='networkidle');assert page.locator('input:checked').count()==0
     if mode=='practice':assert page.locator('.review-choice[data-selected="true"]').count()==0
     else:assert page.locator('.solution:visible').count()==0
     assert page.locator('.katex-error').count()==0
     assert not errs and not failed,(errs,failed)
     reports.append({'mode':mode,'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'viewport':[w,h],'theme':theme,'all15':True,'interaction':'grade/reset/unsure/prompt/reload' if mode=='practice' else 'advance/hide-before-submit/submit/5-column/prompt/lock/reload','overflow':0,'console':errs,'failed':failed,'external':external})
     page.close()
   if mode=='exam':
    page=b.new_page(java_script_enabled=False);page.goto(url);assert page.locator('.solution:visible,.hint:visible,.original:visible').count()==0;page.close()
  b.close()
 (run/'questions-browser.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
 print('PASS',len(reports),'viewport/theme/mode cases; server',server.server_port)
finally:server.shutdown();server.server_close()
