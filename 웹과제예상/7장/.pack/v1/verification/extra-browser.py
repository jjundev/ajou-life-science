from pathlib import Path
from urllib.parse import quote
import json
from playwright.sync_api import sync_playwright
r=Path.cwd();run=Path('/tmp/webquiz-forecast/7장-v1');base='http://127.0.0.1:63317/';rel='웹과제예상/7장/';paths=['복습문제_7장_웹과제예상_v1.html','복습문제_7장_웹과제예상_시험형_v1.html'];out=[]
with sync_playwright() as p:
 b=p.chromium.launch()
 for name in paths:
  page=b.new_page(viewport=dict(width=375,height=812));page.goto(base+quote(rel+name)+'#p1');page.wait_for_load_state('networkidle')
  rect=page.locator('.brand').bounding_box();link=page.locator('.topbar a').first.bounding_box();assert rect['x']+rect['width']<=link['x']+1
  if '시험형' in name:
   page.locator('#show-overview').click();assert page.locator('#forecast-overview').is_visible();page.locator('#close-overview').click()
   assert page.locator('.presentation-links').is_hidden(); page.screenshot(path=str(run/'exam-before-submit-375.png'))
   page.emulate_media(media='print');assert page.locator('#p1 .solution').is_hidden();assert page.locator('.presentation-links').is_hidden()
  else:
   page.screenshot(path=str(run/'practice-start-375.png'))
  out.append(dict(file=name,header_no_overlap=True,overview_or_print='pass'));page.close()
 ctx=b.new_context(java_script_enabled=False);page=ctx.new_page();page.goto(base+quote(rel+paths[1]));assert page.locator('.presentation-links').is_hidden();assert page.locator('#p1 .solution').is_hidden();out.append(dict(js_off='answers_and_tools_hidden'))
 b.close()
(run/'extra-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('extra checks PASS')
