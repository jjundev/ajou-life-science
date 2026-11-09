from pathlib import Path
import json,threading,http.server,functools,hashlib
from urllib.parse import quote,unquote,urlsplit
from playwright.sync_api import sync_playwright,expect
R=Path.cwd();run=Path('/tmp/bio-webquiz-8-v2');folder=Path('/tmp/bio-explain-8-v2/forecast-8장-웹과제예상_v2');meta=json.loads((folder/'stage.json').read_text());stage=folder/meta['stage'];name=meta['html'];key=json.loads((R/'웹과제예상/8장/.pack/v2/pack.json').read_text())['answer_key'];prefix='웹과제예상/8장/'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):
  rel=unquote(urlsplit(path).path).lstrip('/')
  if rel.startswith(prefix):
   alt=stage/rel[len(prefix):]
   if alt.is_file():return str(alt)
  return str(R/rel)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/';url=base+quote(prefix+name);reports=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch()
  for w,h in [(1280,900),(1024,768),(375,812)]:
   for theme in ['light','dark']:
    print(w,theme,flush=True)
    p=b.new_page(viewport={'width':w,'height':h},color_scheme=theme);p.set_default_timeout(10000);errors=[];failed=[];external=[]
    p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' else None)
    p.on('requestfailed',lambda r:failed.append(r.url));p.on('response',lambda r:failed.append(f'{r.status} {r.url}') if r.status>=400 else None);p.on('request',lambda r:external.append(r.url) if not r.url.startswith(base) else None)
    p.goto(url+'#p1',wait_until='networkidle')
    def visit(pid):
     p.evaluate('(id)=>location.hash=id',pid);p.locator('#'+pid).wait_for(state='visible');p.wait_for_timeout(60)
    if w>=1024:
     assert p.locator('#panel-prob').is_visible();assert p.locator('#panel-left').is_visible()
     p.locator('#tab-original').click();assert p.locator('#tabpanel-original').is_visible();p.locator('#tab-problem').click()
    for i in range(1,16):
     pid=f'p{i}';visit(pid)
     assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,theme,pid)
     assert p.locator(f'#{pid} [data-explanation="recall"]').is_visible()
     pane=p.locator(f'[data-problem-for="{pid}"]')
     if w<1024:p.locator(f'#{pid} .problem-toggle').click()
     assert pane.is_visible()
     wrong=next(c for c in 'ABCDE' if c!=key[pid]);pane.locator(f'.review-choice[data-choice-id="{wrong}"]').click()
     assert pane.locator('.review-status').inner_text().startswith('정답이 아니에요')
     if w>=1024:expect(p.locator(f'#{pid} [data-explanation="solve"] .is-target')).to_have_count(1)
     pane.locator('.review-reset').click();pane.locator(f'.review-choice[data-choice-id="{key[pid]}"]').click();assert pane.locator('.review-status').inner_text()=='정답이에요.'
     assert p.locator(f'#{pid} [data-explanation="solve"] .verdict-card').count()==5
     if w>=1024:
      if p.locator('#toggle-right').get_attribute('aria-expanded')!='true':p.locator('#toggle-right').click()
      assert p.locator('#panel-right-title').inner_text()=='페이지 요약'
      assert p.locator('#panel-right h3').count()==0
     else:
      # Inline summary is a disclosure; content and toggle are in the card.
      p.locator('#toggle-right').click();assert p.locator('#panel-right .sum:not([hidden])').is_visible();p.locator('#panel-right [data-panel-close]').click()
    visit('p12')
    pane=p.locator('[data-problem-for="p12"]')
    if w<1024 and not pane.is_visible():p.locator('#p12 .problem-toggle').click()
    pane.locator('svg').first.click();assert p.locator('dialog.figure-sheet[open]').is_visible();p.keyboard.press('Escape')
    p.screenshot(path=str(run/f'explanation-{w}-{theme}.png'),full_page=True)
    visit('p1');p.locator('#pager-next').click();expect(p.locator('#p2')).to_be_visible();p.locator('#pager-prev').click();expect(p.locator('#p1')).to_be_visible()
    if w>=1024:
     if p.locator('#toggle-right').get_attribute('aria-expanded')=='true':p.locator('#toggle-right').click()
     p.locator('#panel-prob [data-dock="right"]').click();assert p.locator('.layout').get_attribute('data-prob-dock')=='right'
     p.locator('#toggle-right').click();assert p.locator('#panel-prob').is_visible() and p.locator('#panel-right').is_visible()
     p.locator('#toggle-right').click();p.locator('#panel-prob [data-dock="float"]').click();assert p.locator('#panel-prob').evaluate('e=>getComputedStyle(e).position')=='fixed'
     grip=p.locator('#panel-prob .float-move');old=p.locator('#panel-prob').bounding_box();grip.focus();grip.press('ArrowRight');new=p.locator('#panel-prob').bounding_box();assert new['x']!=old['x']
     corner=p.locator('#panel-prob .float-resize');corner.focus();corner.press('Enter');assert p.locator('#panel-prob').bounding_box()['width']>=280
     box=grip.bounding_box();p.mouse.move(box['x']+5,box['y']+5);p.mouse.down();p.mouse.move(300,200,steps=5);p.mouse.up()
     p.locator('#panel-prob [data-dock="left"]').click()
    core_external=list(external)
    if w==1280 and theme=='light':
     for i in range(1,16):
      visit(f'p{i}');link=p.locator(f'#p{i} [data-explanation="recall"] a').first;href=link.get_attribute('href');target=link.get_attribute('target')
      if target=='_blank':
       with p.expect_popup() as pop:link.click()
       note=pop.value;note.wait_for_load_state('networkidle');assert note.locator('[id="'+unquote(urlsplit(note.url).fragment)+'"]').count()==1;note.close()
      else:
       link.click();p.wait_for_load_state('networkidle');frag=unquote(urlsplit(p.url).fragment);assert p.locator('[id="'+frag+'"]').count()==1;p.go_back(wait_until='networkidle')
    assert p.locator('.katex-error').count()==0;assert not errors and not failed and not core_external,(errors,failed,core_external)
    reports.append({'viewport':[w,h],'theme':theme,'all15':'wrong/reset/correct/verdict/recall/overflow','links':'15 actual clicks' if w==1280 and theme=='light' else 'reference anchors checked in main case','panels':'original/left/right/float/move/resize/summary' if w>=1024 else 'inline problem toggle/summary','overflow':0,'console':errors,'failed':failed,'external':core_external,'stage':str(stage),'sha256':hashlib.sha256((stage/name).read_bytes()).hexdigest()})
    p.close()
  b.close()
 (run/'explanation-browser.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('PASS',len(reports),'cases',flush=True)
finally:server.shutdown();server.server_close()
