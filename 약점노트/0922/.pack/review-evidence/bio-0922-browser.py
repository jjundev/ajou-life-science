from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import threading,json,urllib.parse
r=Path(Path('/private/tmp/bio-0922-run-path').read_text());repo=Path.cwd();out=repo/'약점노트/0922'; m=json.loads((r/'manifest.json').read_text()); report={'layouts':[],'interactions':{},'errors':[],'console_errors':[],'failed_requests':[]}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(repo)));threading.Thread(target=s.serve_forever,daemon=True).start()
def url(p):return f'http://127.0.0.1:{s.server_port}/'+urllib.parse.quote(p.relative_to(repo).as_posix())
urls={k:url(next(out.glob(k+'*.html'))) for k in ['정리노트','복습문제']}
with sync_playwright() as pw:
 b=pw.chromium.launch();c=b.new_context(viewport={'width':1280,'height':900});p=c.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda x:report['console_errors'].append(x.text) if x.type=='error' else None);p.on('requestfailed',lambda x:report['failed_requests'].append(x.url))
 for role,u in urls.items():
  for width,height in [(1280,900),(375,812)]:
   p.set_viewport_size({'width':width,'height':height})
   for theme in ['light','dark']:
    p.goto(u,wait_until='networkidle');p.evaluate('(t)=>{localStorage.setItem("od-theme",t)}',theme);p.reload(wait_until='networkidle');p.emulate_media(color_scheme=theme)
    ids=p.locator('main .screen').evaluate_all('(es)=>es.map(e=>e.id)');over=[]
    for id in ids:
     p.evaluate('(id)=>location.hash="#"+id',id);p.wait_for_timeout(50)
     res=p.evaluate('''()=>{document.getAnimations().forEach(a=>a.finish());const s=document.querySelector('.content');return {w:s.clientWidth,sw:s.scrollWidth,doc:document.documentElement.scrollWidth,ww:innerWidth}}''')
     if res['sw']>res['w']+1 or res['doc']>res['ww']+1:over.append([id,res])
    report['layouts'].append(dict(role=role,width=width,theme=theme,screens=len(ids),overflow=over,katex_errors=p.locator('.katex-error').count(),broken_images=p.locator('img').evaluate_all('(es)=>es.filter(e=>!e.complete||!e.naturalWidth).map(e=>e.src)')))
    p.evaluate('location.hash="#s2-cross"' if role=='정리노트' else 'location.hash="#p7"');p.wait_for_timeout(200);p.screenshot(path=str(r/'work'/f'{role}-{width}-{theme}.png'))
 # Choice behavior on every new question
 p.set_viewport_size({'width':1280,'height':900});p.goto(urls['복습문제']+'#p1',wait_until='networkidle')
 for q in m['problems']:
  id=q['id'];a=int(q['answer'][1:-1])-1; wrong=(a+1)%4;p.evaluate('(id)=>location.hash="#"+id',id);card=p.locator('#'+id);expect(card).to_be_visible();bs=card.locator('.review-choice');bs.nth(wrong).click();assert bs.nth(wrong).get_attribute('data-result')=='selected';assert bs.nth(a).get_attribute('data-result')=='correct';assert card.locator('.review-diagnostic:visible').count()==2
  # keyboard toggles preserve selected choice
  bs.nth(wrong).focus();bs.nth(wrong).press('Enter');bs.nth(wrong).press('Space');assert bs.nth(wrong).get_attribute('aria-expanded')=='true'
  card.locator('.review-reset').click();bs.nth(a).click();assert bs.nth(a).get_attribute('data-result')=='correct';assert card.locator('.review-diagnostic:visible').count()==1
 report['interactions']['all_16_wrong_right_keyboard_reset']=True
 p.evaluate('location.hash="#p1"');p.reload(wait_until='networkidle');assert p.locator('#p1 .review-choice').nth(1).get_attribute('data-result')=='correct';report['interactions']['reload_restore']=True
 # Only correct answers expose unsure
 p.locator('.aid[data-card-id="p1"] .review-unsure').click();assert p.locator('.aid[data-card-id="p1"] .review-unsure').get_attribute('aria-pressed')=='true';report['interactions']['unsure']=True
 p.locator('#p1 .review-reset').click();p.locator('#p1 .review-choice').nth(1).click();p.locator('.aid[data-card-id="p1"] .review-unsure').click()
 p.evaluate('location.hash="#p2"');expect(p.locator('.review-export')).to_be_hidden();p.evaluate('location.hash="#p16"');expect(p.locator('.review-export')).to_be_visible()
 # Browser picker replaced only with an in-memory fake; no user solve records saved
 for root in ['0922','약점노트']:
  p.evaluate('''root=>{window.__saved=null; window.__path=[]; const dir=(name)=>({name,async getFileHandle(n){ if(n.endsWith('.html'))return {};return {async createWritable(){return {async write(t){window.__saved=t},async close(){}}}}},async getDirectoryHandle(n){window.__path.push(n);return dir(n)}});window.showDirectoryPicker=async()=>dir(root); }''',root)
  p.locator('.review-export').click();p.wait_for_function('window.__saved!==null');data=json.loads(p.evaluate('window.__saved'));assert len(data['cards'])==16;assert data['cards'][0]['unsure'];report['interactions']['export_'+root]={'path':p.evaluate('window.__path'),'total':len(data['cards'])}
 # new tabs start empty even same browser context
 other=c.new_page();other.goto(urls['복습문제']+'#p1',wait_until='networkidle');assert other.locator('#p1 .review-choice').nth(1).get_attribute('data-result') in (None,'');other.close();report['interactions']['new_tab_empty']=True
 # Print returns aids to right panel
 p.evaluate("dispatchEvent(new Event('beforeprint'))");p.emulate_media(media='print');assert p.locator('article.card details.solution').count()==16;p.emulate_media(media='screen');p.evaluate("dispatchEvent(new Event('afterprint'))");assert p.locator('#panel-right .aid').count()==16;report['interactions']['print_restore']=True
 # JavaScript disabled still has original solution markup
 nc=b.new_context(java_script_enabled=False);np=nc.new_page();np.goto(urls['복습문제']);assert np.locator('details.solution').count()==16;nc.close();report['interactions']['static_solutions']=True
 # Theme toggle reverses stored setting
 p.goto(urls['정리노트']+'#s0-tools',wait_until='networkidle');before=p.evaluate('getComputedStyle(document.body).backgroundColor');p.locator('#theme-toggle').click();after=p.evaluate('getComputedStyle(document.body).backgroundColor');assert before!=after;report['interactions']['theme_toggle']=True
 report['summary_count']=p.locator('#panel-right .sum').count();assert report['summary_count']==8;assert p.locator('main .sum').count()==0
 b.close()
s.shutdown();(r/'work/browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
