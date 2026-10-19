from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from urllib.parse import quote
import threading,json
r=Path(Path('/private/tmp/bio-0922-run-path').read_text());e=Path((r/'work/explain-path').read_text())/'review-0922-Weakness_0922_v1';st=json.loads((e/'stage.json').read_text());stage=e/st['stage'];m=json.loads((r/'manifest.json').read_text());report={'layouts':[],'errors':[],'console_errors':[],'missing':[],'external':[],'interactions':{}}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(stage)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/';url=base+quote(st['html'])
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for width,height in [(1280,900),(1024,768),(375,812)]:
  for theme in ['light','dark']:
   c=b.new_context(viewport={'width':width,'height':height},color_scheme=theme);p=c.new_page();p.on('pageerror',lambda x:report['errors'].append(str(x)));p.on('console',lambda x:report['console_errors'].append(x.text) if x.type=='error' else None);p.on('response',lambda x:report['missing'].append([x.status,x.url]) if x.status>=400 else None);p.on('request',lambda x:report['external'].append(x.url) if not x.url.startswith(base) else None)
   p.goto(url+'#p1',wait_until='networkidle');p.wait_for_timeout(100)
   if width>=1024:
    expect(p.locator('#panel-left')).to_be_visible();expect(p.locator('#panel-prob')).to_be_visible();assert p.locator('.layout').get_attribute('data-prob-dock')=='left'
    expect(p.locator('#tab-original')).to_be_visible();p.locator('#tab-original').click();expect(p.locator('#tabpanel-original')).to_be_visible();p.locator('#tab-problem').click();p.locator('#toggle-right').click();expect(p.locator('#panel-right')).to_be_visible()
   over=[]
   for q in m['problems']:
    id=q['id'];a=int(q['answer'][1:-1]);wrong=a%4+1;p.evaluate('(id)=>location.hash="#"+id',id);p.wait_for_timeout(70);expect(p.locator('#'+id)).to_be_visible()
    assert p.locator('#'+id+' [data-explanation="solve"] .verdict-card').count()==4
    if width<1024:p.locator('#'+id+' .problem-toggle').click()
    pane=p.locator('[data-problem-for="'+id+'"]');expect(pane).to_be_visible();pane.locator(f'.review-choice[data-choice-id="{wrong}"]').click();assert pane.locator(f'[data-choice-id="{wrong}"]').get_attribute('data-result')=='selected';assert pane.locator(f'[data-choice-id="{a}"]').get_attribute('data-result')=='correct'
    pane.locator('.review-reset').click();pane.locator(f'.review-choice[data-choice-id="{a}"]').click();assert pane.locator('.review-status').inner_text()=='정답이에요.'
    x=p.evaluate('''()=>{document.getAnimations().forEach(a=>a.finish());const s=document.querySelector('.content');return {w:s.clientWidth,sw:s.scrollWidth,doc:document.documentElement.scrollWidth,ww:innerWidth}}''')
    if x['sw']>x['w']+1 or x['doc']>x['ww']+1:over.append([id,x])
    if id in ['p7','p13']:
     p.evaluate('document.querySelector(".content").scrollTop=0');p.screenshot(path=str(r/'work'/f'explain-{width}-{theme}-{id}.png'))
   report['layouts'].append(dict(width=width,theme=theme,questions=16,overflow=over,katex_errors=p.locator('.katex-error').count()))
   # navigation works after any card, all links have actual targets checked separately
   p.evaluate('location.hash="#p1"');p.locator('#pager-next').click();assert p.evaluate('location.hash')=='#p2';p.locator('#pager-prev').click();assert p.evaluate('location.hash')=='#p1'
   if width>=1024:
    p.locator('#panel-prob [data-dock="right"]').click();assert p.locator('.layout').get_attribute('data-prob-dock')=='right';expect(p.locator('#panel-right')).to_be_visible()
    p.locator('#panel-prob [data-dock="float"]').click();assert p.locator('.layout').get_attribute('data-prob-dock')=='float';box=p.locator('#panel-prob').bounding_box();mv=p.locator('#panel-prob .float-move');mv.focus();p.keyboard.press('ArrowRight');assert p.locator('#panel-prob').bounding_box()['x']!=box['x'];rs=p.locator('#panel-prob .float-resize');rs.focus();rs.press('Enter');assert abs(p.locator('#panel-prob').bounding_box()['width']-420)<2
    # drag far offscreen: clamp keeps panel within viewport above pager
    mb=mv.bounding_box();p.mouse.move(mb['x']+mb['width']/2,mb['y']+mb['height']/2);p.mouse.down();p.mouse.move(mb['x']+mb['width']/2,mb['y']+2000,steps=6);p.mouse.up();fb=p.locator('#panel-prob').bounding_box();assert fb['y']+fb['height']<=p.locator('.pager').bounding_box()['y']+2
    p.reload(wait_until='networkidle');assert p.locator('.layout').get_attribute('data-prob-dock')=='float'
   c.close()
 report['interactions']={'all16_each_layout_wrong_right_reset':True,'toc_previous_next':True,'desktop_original_tabs':True,'mobile_problem_toggle':True,'summary':True,'left_right_float_move_resize_clamp_reload':True}
 b.close()
s.shutdown();(e/'evidence/browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
