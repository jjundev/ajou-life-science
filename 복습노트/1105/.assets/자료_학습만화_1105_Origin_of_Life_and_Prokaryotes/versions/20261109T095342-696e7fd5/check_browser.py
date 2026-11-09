from pathlib import Path
import json,sys,threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import quote,unquote
from playwright.sync_api import sync_playwright,expect

r=Path(__file__).resolve().parent
repo=r.parents[2]
book=json.loads((r/'storyboard.json').read_text())
pages=book['pages'];ids=[p['id'] for p in pages]
source=Path(json.loads((r/'source.json').read_text())['path'])
final='--final' in sys.argv
html=Path(json.loads((r/'publication.json').read_text())['html']) if final else r/'preview.html'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(repo)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
def url(path,pid=''):
    return base+'/'.join(quote(p,safe='') for p in path.relative_to(repo).parts)+('#'+pid if pid else '')
out=[]
try:
  with sync_playwright() as pw:
    browser=pw.chromium.launch()
    for width,height in [(1440,900),(375,812)]:
      for theme in ['light','dark']:
        prefix=f'{"final-" if final else ""}{width}-{theme}'
        ctx=browser.new_context(viewport={'width':width,'height':height},color_scheme=theme,reduced_motion='reduce')
        ctx.route('https://**/*',lambda route:route.abort())
        page=ctx.new_page();errors=[];failed=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda res:failed.append(res.url) if res.status>=400 and '127.0.0.1' in res.url else None)
        page.goto(url(html,ids[0]));expect(page.locator('#'+ids[0])).to_be_visible()
        assert page.evaluate('document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")')==theme
        visited=[];panels_checked=0
        for spec in pages:
          pid=spec['id']
          page.evaluate('(id)=>location.hash=id',pid)
          topic=page.locator('#'+pid);expect(topic).to_be_visible()
          assert topic.locator('.comic-panel').count()==len(spec['panels'])
          for n in range(1,len(spec['panels'])+1):
            panel=topic.locator(f'.comic-panel[data-panel="{n}"]');panel.scroll_into_view_if_needed()
            img=panel.locator('img');expect(img).to_have_js_property('complete',True)
            img.evaluate('(im)=>im.decode()');assert img.evaluate('(im)=>im.naturalWidth>0')
            metrics=panel.evaluate('''el=>{
              const scene=el.querySelector('.comic-scene'),img=el.querySelector('img'),layer=el.querySelector('.comic-balloon-layer');
              const ib=img.getBoundingClientRect(),lb=layer.getBoundingClientRect();
              return {overflow:el.scrollWidth>el.clientWidth+1,balloons:Array.from(el.querySelectorAll('.comic-dialogue')).map(b=>({overflow:(()=>{const r=document.createRange();r.selectNodeContents(b);const t=r.getBoundingClientRect(),bb=b.getBoundingClientRect();return t.right>bb.right+1||t.left<bb.left-1||t.bottom>bb.bottom+1})(),font:parseFloat(getComputedStyle(b).fontSize)})),overlap:lb.bottom-(ib.top+ib.height*.36),inside:layer.parentElement===scene};
            }''')
            assert not metrics['overflow'],(prefix,pid,n,metrics)
            assert metrics['inside'] and all(not x['overflow'] and x['font']>=17 for x in metrics['balloons']),(prefix,pid,n,metrics)
            assert metrics['overlap']<=1.1,(prefix,pid,n,metrics)
            panels_checked+=1
            if not final:
              panel.screenshot(path=str(r/f'checks/panel-{prefix}-{pid}-{n:02}.png'),animations='disabled')
          assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
          assert page.locator('.content').evaluate('el=>el.scrollWidth<=el.clientWidth+1')
          if width<1024:page.locator('#toggle-right').click()
          expect(page.locator('#sum-for .sum:not([hidden])')).to_contain_text(spec['summary']['text'])
          if width<1024:page.keyboard.press('Escape')
          topic.locator('.comic-source a').click();expect(page.locator('#'+pid)).to_be_visible()
          assert '정리노트' in unquote(page.url)
          assert page.url.endswith('#'+pid)
          if final:
            links=page.locator(f'#{pid} [data-bio-comic] a')
            target=links.filter(has_text=spec['note_link']['label'])
            target=target.filter(has=page.locator('span')) if False else target
            # Existing sample and full comic links may coexist; select destination filename.
            chosen=page.locator(f'#{pid} [data-bio-comic] a').filter(has_text=spec['note_link']['label'])
            matching=[a for a in chosen.all() if unquote(a.get_attribute('href')).split('#')[0]==html.name]
            assert len(matching)==1,(pid,[a.get_attribute('href') for a in chosen.all()])
            assert matching[0].get_attribute('target')=='_self'
            matching[0].click();expect(page.locator('#'+pid)).to_be_visible()
            assert unquote(page.url).split('#')[0].endswith(html.name)
            page.locator(f'#{pid} .comic-source a').click();expect(page.locator('#'+pid)).to_be_visible()
            page.go_back();expect(page.locator('#'+pid)).to_be_visible()
          else:
            page.go_back();expect(page.locator('#'+pid)).to_be_visible()
          visited.append(pid)
        # Actual UI navigation at first, middle, last topics.
        for pid in [ids[0],ids[len(ids)//2],ids[-1]]:
          if width<1024:page.locator('#toggle-left').click()
          page.locator(f'#panel-left a[href="#{pid}"]').click();expect(page.locator('#'+pid)).to_be_visible()
        page.locator('#pager-next').click();expect(page.locator('.hero')).to_be_visible()
        page.keyboard.press('ArrowRight');expect(page.locator('#'+ids[0])).to_be_visible()
        page.locator('#pager-next').click();expect(page.locator('#'+ids[1])).to_be_visible()
        page.locator('#pager-prev').click();expect(page.locator('#'+ids[0])).to_be_visible()
        page.keyboard.press('ArrowRight');expect(page.locator('#'+ids[1])).to_be_visible()
        page.keyboard.press('ArrowLeft');expect(page.locator('#'+ids[0])).to_be_visible()
        if width>=1024:
          page.locator('#toggle-left').click();assert page.locator('.layout').get_attribute('data-left')=='closed'
          page.locator('#toggle-left').click()
          sep=page.locator('#panel-left .panel-resize');sep.focus();old=page.locator('#panel-left').bounding_box()['width']
          page.keyboard.press('ArrowRight');new=page.locator('#panel-left').bounding_box()['width'];assert new>old
          page.keyboard.press('Home')
          page.locator('#toggle-right').click();assert page.locator('.layout').get_attribute('data-right')=='closed'
          page.locator('#toggle-right').click()
        else:
          page.locator('#toggle-left').click();expect(page.locator('#panel-left')).to_have_attribute('aria-modal','true')
          page.keyboard.press('Escape');assert not page.locator('body').evaluate('e=>e.classList.contains("drawer-open")')
          page.locator('#toggle-right').click();page.locator('#panel-scrim').click(position={'x':4,'y':4})
          assert not page.locator('body').evaluate('e=>e.classList.contains("drawer-open")')
        page.locator('#theme-toggle').click();other='dark' if theme=='light' else 'light'
        assert page.evaluate('document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")')==other
        page.reload();assert page.evaluate('document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")')==other
        page.locator('#theme-toggle').click()
        keys=page.evaluate('Object.keys(localStorage)')
        assert any(k.startswith('od-comic-read:') for k in keys),keys
        assert any(k.startswith('od-note-read:') for k in keys),keys
        page.goto(url(html,ids[0]));page.locator('.content').evaluate('e=>e.scrollTo(0,0)')
        shot=f'checks/{prefix}.png';page.screenshot(path=str(r/shot),full_page=True,animations='disabled')
        assert not errors,errors
        assert not failed,failed
        result={'width':width,'height':height,'theme':theme,'screenshot':shot,'pages':visited,'panels':panels_checked,'errors':errors,'local_failed_requests':failed,'navigation':True,'same_tab_source_return':True,'note_to_comic':final}
        out.append(result);print(json.dumps({k:v for k,v in result.items() if k!='pages'}),flush=True)
        ctx.close()
    browser.close()
  (r/('final-browser-observations.json' if final else 'browser-observations.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
finally:
  server.shutdown();server.server_close()
