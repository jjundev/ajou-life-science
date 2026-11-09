from pathlib import Path
import json,threading,http.server,functools,hashlib
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
R=Path.cwd();run=Path('/tmp/bio-webquiz-8-v2');d=R/'웹과제예상/8장'
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/';url=lambda n:base+quote((d/n).relative_to(R).as_posix())
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch();p=b.new_page(viewport={'width':375,'height':812},color_scheme='dark');errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  p.goto(url('복습문제_8장_웹과제예상_v2.html')+'#p1',wait_until='networkidle');p.locator('#open-explanation').click();p.wait_for_url(url('문제해설_8장_웹과제예상_v2.html'));p.locator('#pager-next').click();expect(p.locator('#p1 [data-explanation="recall"]')).to_be_visible();assert '문제해설' in p.url or '%EB%AC%B8%EC%A0%9C%ED%95%B4%EC%84%A4' in p.url
  p.locator('#p1 .panel-meta a').filter(has_text='시험형 문제 보기').click();expect(p.locator('#p1 input')).to_have_count(5);assert p.locator('#open-explanation').is_hidden()
  p.evaluate("location.hash='p15'");expect(p.locator('#p15')).to_be_visible();p.locator('#submit-exam').click();expect(p.locator('#results-title')).to_be_visible();p.locator('#toggle-right').click();expect(p.locator('#exam-scorecard')).to_be_visible();p.wait_for_timeout(350);expect(p.locator('#exam-scorecard')).to_be_in_viewport();assert p.locator('#exam-scorecard tbody tr').count()==3;assert p.locator('#exam-scorecard tbody tr').first.locator('td').count()==5
  p.screenshot(path=str(run/'final-scorecard-375-dark.png'),full_page=True)
  p.locator('#panel-right [data-panel-close]').click();p.locator('#open-explanation').click();p.wait_for_url(url('문제해설_8장_웹과제예상_v2.html'));p.locator('#pager-next').click();expect(p.locator('#p1')).to_be_visible();p.wait_for_load_state('networkidle');assert p.locator('#p1 [data-explanation="recall"]').is_visible();assert not errors
  b.close()
 report={'published_links':'practice→explanation→exam→submitted→explanation pass','scorecard':'3 rows ×5 columns at375px','console_errors':errors,'files':{n:hashlib.sha256((d/n).read_bytes()).hexdigest() for n in ['복습문제_8장_웹과제예상_v2.html','복습문제_8장_웹과제예상_시험형_v2.html','문제해설_8장_웹과제예상_v2.html']}}
 (run/'final-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS published links and mobile scorecard')
finally:s.shutdown();s.server_close()
