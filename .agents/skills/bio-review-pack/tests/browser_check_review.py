"""Run explicitly: python .agents/skills/bio-review-pack/tests/browser_check_review.py"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from _util import REPO


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class TestReviewBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(REPO)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':1280,'height':850})
        self.context.route('https://**/*', lambda route: route.abort())
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e:self.errors.append(str(e)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def url(self, date, card='p1'):
        path = next((REPO / '복습노트' / date).glob('복습문제*.html'))
        return f'http://127.0.0.1:{self.server.server_port}/' + quote(path.relative_to(REPO).as_posix()) + '#' + card

    def open(self, date='0929', card='p1'):
        self.page.goto(self.url(date, card))
        expect(self.page.locator('#'+card)).to_be_visible()
        return self.page.locator('#'+card)

    def test_wrong_reset_correct_restore(self):
        card = self.open()
        choices = card.locator('.review-choice')
        expect(choices).to_have_count(5)
        choices.nth(0).click()
        expect(card.locator('.review-status')).to_contain_text('정답이 아니에요')
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)
        # Submitted choices toggle explanations without changing the answer.
        choices.nth(1).evaluate('(b)=>b.click()')
        expect(choices.nth(0)).to_have_attribute('data-selected', 'true')
        card.locator('.review-reset').click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)
        expect(self.page.locator('#progress-n')).to_have_text('0')
        choices.nth(1).focus()
        self.page.keyboard.press('Enter')
        expect(card.locator('.review-status')).to_have_text('정답이에요.')
        expect(self.page.locator('#progress-n')).to_have_text('1')
        self.page.reload()
        expect(card.locator('.review-choice').nth(1)).to_have_attribute('data-selected','true')
        expect(card.locator('.review-diagnostic:visible')).to_have_count(1)

    def test_answer_scroll_shows_selected_and_answer(self):
        card = self.open('0910', 'p8')
        self.page.locator('.content').evaluate('(e) => { e.scrollTop = 0; }')
        card.locator('.review-choice').nth(0).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        state = self.page.evaluate('''() => {
          const sc = document.querySelector('.content');
          const card = document.querySelector('#p8');
          const buttons = [0, 1].map(i => card.querySelectorAll('.review-choice')[i].getBoundingClientRect());
          const viewport = sc.getBoundingClientRect();
          return {scroll:sc.scrollTop, visible:buttons.every(b =>
            b.top >= viewport.top && b.bottom <= viewport.bottom),
            text:card.querySelector('.review-diagnostic:not([hidden])').textContent.trim()};
        }''')
        self.assertGreater(state['scroll'], 0)
        self.assertTrue(state['visible'])
        self.assertFalse(state['text'].startswith('(1)'))

    def test_correct_answer_centers_expanded_card(self):
        card = self.open('0910', 'p8')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        center_gap = self.page.evaluate('''() => {
          const sc=document.querySelector('.content').getBoundingClientRect();
          const li=document.querySelector('#p8 .choices > li:nth-child(2)').getBoundingClientRect();
          return Math.abs((li.top+li.bottom-sc.top-sc.bottom)/2);
        }''')
        self.assertLess(center_gap, 24)
        self.page.locator('.content').evaluate('(e) => { e.scrollTop = 0; }')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        self.assertEqual(self.page.locator('.content').evaluate('(e) => e.scrollTop'), 0)

    def test_small_viewport_scroll_fallback(self):
        for height in (480, 240):
            with self.subTest(height=height):
                ctx = self.browser.new_context(viewport={'width': 375, 'height': height})
                page = ctx.new_page()
                try:
                    page.goto(self.url('0910', 'p8'))
                    page.locator('#p8 .review-choice').nth(4).evaluate('(e) => e.click()')
                    page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                    state = page.evaluate('''() => {
                      const sc=document.querySelector('.content').getBoundingClientRect();
                      const b=document.querySelectorAll('#p8 .review-choice');
                      const a=b[4].getBoundingClientRect(), z=b[1].getBoundingClientRect();
                      const fits=Math.max(a.bottom,z.bottom)-Math.min(a.top,z.top) <= sc.height-32;
                      const visible=r => r.top >= sc.top-2 && r.bottom <= sc.bottom+2;
                      return {fits, both:visible(a)&&visible(z),
                        selectedCenterGap:Math.abs((a.top+a.bottom-sc.top-sc.bottom)/2)};
                    }''')
                    if state['fits']:
                        self.assertTrue(state['both'], state)
                    else:
                        self.assertLess(state['selectedCenterGap'], 2, state)
                finally:
                    ctx.close()

    def test_restored_answer_does_not_scroll(self):
        card = self.open('0910', 'p8')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.reload()
        expect(card.locator('.review-choice').nth(1)).to_have_attribute('data-selected', 'true')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        self.assertEqual(self.page.locator('.content').evaluate('(e) => e.scrollTop'), 0)

    def test_disclosures_toggle_independently_without_regrading(self):
        card = self.open()
        buttons = card.locator('.review-choice')
        buttons.nth(0).click()
        expect(buttons.nth(0)).to_have_attribute('aria-expanded', 'true')
        expect(buttons.nth(1)).to_have_attribute('aria-expanded', 'true')
        expect(buttons.nth(2)).to_have_attribute('aria-expanded', 'false')
        buttons.nth(2).click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(3)
        buttons.nth(2).focus()
        self.page.keyboard.press('Space')
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)
        buttons.nth(0).click()
        buttons.nth(1).click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)
        expect(card.locator('.review-status')).to_contain_text('정답이 아니에요')
        expect(self.page.locator('#progress-n')).to_have_text('1')
        self.page.reload()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)
        card.locator('.review-reset').click()
        buttons.nth(1).click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(1)
        buttons.nth(1).click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)

    def test_letter_negative_and_ambiguity(self):
        card = self.open('0903','p1')
        card.locator('.review-choice').first.click()
        expect(card.locator('.review-status')).to_have_text('정답이에요.')
        card = self.open('0901','p3')
        card.locator('.review-choice').nth(1).click()
        expect(card.locator('.review-status')).to_have_text('정답이에요.')
        card = self.open('0929','p11')
        card.locator('.review-choice').first.click()
        expect(card.locator('.review-status')).to_contain_text('단일 정답 판정 주의')
        expect(card.locator('.review-choice-label').nth(2)).to_have_text('출제 의도상 답')
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)

    def test_every_pack_all_choices_have_diagnostics(self):
        for date in ['0901','0903','0908','0910','0915','0917','0922','0929']:
            with self.subTest(date=date):
                self.open(date, 'p2' if date == '0910' else 'p1')
                result = self.page.evaluate("""() => {
                  const m=JSON.parse(document.getElementById('review-interaction-model').textContent);
                  return Object.entries(m.cards).every(([id,c])=>{
                    const el=document.getElementById(id);
                    return el.classList.contains('review-ready') &&
                      el.querySelectorAll('.review-choice').length===c.options.length &&
                      el.querySelectorAll('.review-diagnostic').length===c.options.length;
                  }) && new Set([...document.querySelectorAll('[id]')].map(e=>e.id)).size===document.querySelectorAll('[id]').length;
                }""")
                self.assertTrue(result)

    def test_storage_blocked(self):
        self.context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('blocked')}});")
        card = self.open()
        card.locator('.review-choice').first.click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)
        card.locator('.review-reset').click()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)

    def test_manual_completion_override_survives_reload(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        expect(self.page.locator('#progress-n')).to_have_text('1')
        self.page.locator('#solved-btn').click()
        expect(self.page.locator('#progress-n')).to_have_text('0')
        self.page.reload()
        expect(card.locator('.review-choice').first).to_have_attribute('data-selected','true')
        expect(self.page.locator('#progress-n')).to_have_text('0')

    def test_alternative_answers_get_caution(self):
        for date, cid, choice in [('0910','p4',1), ('0915','p3',0)]:
            card = self.open(date,cid)
            card.locator('.review-choice').nth(choice).click()
            expect(card.locator('.review-status')).to_contain_text('단일 정답 판정 주의')
            self.assertNotIn('정답 아님',card.locator('.review-choice-label').nth(choice).inner_text())

    def test_additional_notice_only_in_right_panel(self):
        card = self.open('0910','p4')
        card.locator('.review-choice').first.click()
        expect(card.locator('.review-status')).to_have_text('단일 정답 판정 주의')
        notice = self.page.evaluate("JSON.parse(document.getElementById('review-interaction-model').textContent).cards.p4.notice")
        self.assertNotIn(notice, card.inner_text())
        solution = self.page.locator('.aid[data-card-id="p4"] .solution')
        expect(solution).to_contain_text(notice)
        self.assertEqual(solution.inner_text().count(notice), 1)

    def test_metadata_only_notice_is_kept_in_right_panel(self):
        self.context.add_init_script("""document.addEventListener('DOMContentLoaded', () => {
          const el=document.getElementById('review-interaction-model');
          const model=JSON.parse(el.textContent);
          model.cards.p4.notice='메타데이터에만 있는 추가 해설이에요.';
          el.textContent=JSON.stringify(model);
        });""")
        card = self.open('0910','p4')
        card.locator('.review-choice').first.click()
        expect(card.locator('.review-status')).to_have_text('단일 정답 판정 주의')
        notice = self.page.locator('.aid[data-card-id="p4"] .review-notice')
        expect(notice).to_have_count(1)
        expect(notice).to_have_text('메타데이터에만 있는 추가 해설이에요.')

    def test_stale_and_corrupt_storage(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        self.page.evaluate("""() => {
          for(let i=0;i<localStorage.length;i++){
            const key=localStorage.key(i);
            if(key.startsWith('od-review-attempt:')) localStorage.setItem(key,'{');
          }
        }""")
        self.page.reload()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)
        expect(self.page.locator('#progress-n')).to_have_text('0')
        card.locator('.review-choice').first.click()
        self.page.evaluate("""() => {
          for(let i=0;i<localStorage.length;i++){
            const key=localStorage.key(i);
            if(key.startsWith('od-review-attempt:')) localStorage.setItem(key,JSON.stringify({version:'old',selected:'1'}));
          }
        }""")
        self.page.reload()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)

    def test_mobile_theme_print_and_figures(self):
        self.page.set_viewport_size({'width':390,'height':844})
        card = self.open('0903','p4')
        count = self.page.locator('svg,img').count()
        card.locator('.review-choice').first.focus()
        self.page.keyboard.press('Space')
        expect(card.locator('.review-diagnostic:visible')).to_have_count(2)
        self.assertEqual(self.page.locator('svg,img').count(), count)
        self.page.locator('#theme-toggle').click()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        shots = REPO / '.superpowers/sdd/bio-review-interactive'
        self.page.screenshot(path=str(shots/'mobile.png'))
        self.page.set_viewport_size({'width':1280,'height':850})
        self.page.screenshot(path=str(shots/'desktop.png'))
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        self.page.emulate_media(media='print')
        self.assertGreater(self.page.locator('main article .review-extra').count(),0)
        self.assertEqual(self.page.locator('svg,img').count(), count)
        self.page.emulate_media(media='screen')
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.assertEqual(self.page.locator('main article .review-extra').count(),0)

    def test_static_and_no_javascript(self):
        card = self.open('0903','p21')
        expect(card.locator('.review-choice')).to_have_count(0)
        context = self.browser.new_context(java_script_enabled=False)
        context.route('https://**/*', lambda route:route.abort())
        page = context.new_page()
        page.goto(self.url('0929'))
        expect(page.locator('#p1 .choices > li')).to_have_count(5)
        page.locator('#p1 details.solution summary').click()
        expect(page.locator('#p1 .answer')).to_be_visible()
        context.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
