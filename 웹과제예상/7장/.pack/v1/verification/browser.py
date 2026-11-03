from pathlib import Path
from urllib.parse import quote
import json,hashlib
from playwright.sync_api import sync_playwright
repo=Path.cwd(); run=Path('/tmp/webquiz-forecast/7장-v1'); base='http://127.0.0.1:63317/'
pack=json.loads((repo/'웹과제예상/7장/.pack/v1/pack.json').read_text()); result=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 for mode,name in [('practice','복습문제_7장_웹과제예상_v1.html'),('exam','복습문제_7장_웹과제예상_시험형_v1.html')]:
  path=repo/'웹과제예상/7장'/name
  for w,h in [(1280,900),(375,812)]:
   for theme in ['light','dark']:
    ctx=browser.new_context(viewport=dict(width=w,height=h),color_scheme=theme,reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']); page=ctx.new_page(); errors=[]; failed=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failed.append(r.url) if r.status>=400 else None)
    page.goto(base+quote(str(path.relative_to(repo)))+'#p1',wait_until='networkidle')
    page.evaluate('(theme)=>{localStorage.setItem("od-theme",theme);document.documentElement.dataset.theme=theme}',theme)
    assert page.locator('a').filter(has_text='시험형 열기').count()==0
    if mode=='practice':
     assert page.locator('.presentation-links').count()==0
     for i in range(1,16):
      pid=f'p{i}'; page.evaluate('(id)=>location.hash=id',pid);page.wait_for_timeout(35)
      assert page.locator('#'+pid).evaluate('(e)=>e.classList.contains("is-current")')
      wrong=(list('ABCDE').index(pack['answer_key'][pid])+1)%5
      page.locator(f'#{pid} .review-choice').nth(wrong).click()
      assert page.url.endswith('#'+pid)
      assert page.locator(f'#{pid} .review-status').get_attribute('data-result')=='incorrect'
      assert page.locator(f'#{pid} .review-diagnostic:visible').count()==2
      page.locator(f'#{pid} .review-choice').nth((wrong+1)%5).click()
      page.locator(f'#{pid} .review-reset').click()
      page.locator(f'#{pid} .review-choice').nth(list('ABCDE').index(pack['answer_key'][pid])).click()
      assert page.locator(f'#{pid} .review-status').get_attribute('data-result')=='correct'
      if i==1:
       page.locator('#toggle-right').click() if page.locator('#toggle-right').get_attribute('aria-expanded')!='true' else None
       page.locator('.aid[data-card-id="p1"] .review-unsure').click()
       assert page.locator('.aid[data-card-id="p1"] .review-unsure').get_attribute('aria-pressed')=='true'
       if w<600: page.locator('#panel-right [data-panel-close]').click()
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
     page.locator('.review-export').click(); page.wait_for_timeout(120)
     clip=page.evaluate('navigator.clipboard.readText()'); assert 'p1' in clip and 'p15' in clip
     page.screenshot(path=str(run/f'{mode}-{w}-{theme}.png'))
     page.reload(wait_until='networkidle');assert page.locator('.review-choice[data-selected="true"]').count()==0
     assert page.locator('.review-status[data-result="correct"]').count()==0
    else:
     assert not page.locator('.presentation-links').is_visible()
     assert page.locator('.presentation-links').evaluate('(e)=>e.getBoundingClientRect().height')==0
     assert page.locator('.toc-list a[href="#o1"]').count()==0
     for i in range(1,16):
      pid=f'p{i}';page.evaluate('(id)=>location.hash=id',pid);page.wait_for_timeout(35)
      assert page.locator(f'#{pid} .solution').is_hidden()
      page.locator(f'#{pid} input[value="{pack["answer_key"][pid]}"]').check()
      page.wait_for_timeout(40)
      if i<15: assert page.url.endswith('#p'+str(i+1))
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
     page.locator('#submit-exam').click();page.wait_for_timeout(100)
     assert page.locator('.presentation-links').is_visible()
     assert page.locator('#exam-scorecard td').count()==15
     assert page.locator('#exam-scorecard tr').first.locator('td').count()==5
     assert page.locator('input[type=radio]:disabled').count()==75
     assert '15/15' in page.locator('#summary').inner_text()
     page.screenshot(path=str(run/f'{mode}-{w}-{theme}.png'))
     page.reload(wait_until='networkidle');assert page.url.endswith('#p1');assert not page.locator('.presentation-links').is_visible();assert page.locator('input:checked').count()==0
    assert not errors,errors;assert not failed,failed
    result.append(dict(mode=mode,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),width=w,height=h,theme=theme,status='pass',errors=errors,failed=failed))
    (run/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(mode,w,theme,'PASS',flush=True)
    ctx.close()
 browser.close()
(run/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS',len(result),'cases; 120 question interactions')
