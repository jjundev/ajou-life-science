"""Run explicitly: python .agents/skills/bio-review-pack/tests/browser_check_review.py"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from _util import REPO
import review_interaction as ri


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

    def open_current_assets(self, date='0929', card='p1', transform=None):
        path = next((REPO / '복습노트' / date).glob('복습문제*.html'))
        url = self.url(date, card).split('#', 1)[0]
        text = path.read_text(encoding='utf-8')
        source = ri.install(transform(text) if transform else text, path.name)
        self.page.route(url, lambda route: route.fulfill(body=source, content_type='text/html'))
        return self.open(date, card)

    def test_answer_borders_distinguish_correct_selected_and_ambiguous(self):
        card = self.open_current_assets('0929', 'p1')  # 정답 2번
        buttons = card.locator('.review-choice')
        buttons.nth(0).click()
        self.assertEqual(buttons.nth(0).get_attribute('data-result'), 'selected')
        self.assertEqual(buttons.nth(1).get_attribute('data-result'), 'correct')
        self.assertEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '3px')
        self.assertEqual(buttons.nth(1).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '3px')
        self.assertNotEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopColor'),
                            buttons.nth(1).evaluate('(e) => getComputedStyle(e).borderTopColor'))
        card.locator('.review-reset').click()
        self.assertEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '1px')
        card = self.open_current_assets('0929', 'p11')  # 모호 문항, 출제 의도상 답 3번
        buttons = card.locator('.review-choice')
        buttons.nth(0).click()
        self.assertEqual(buttons.nth(0).get_attribute('data-result'), 'uncertain')
        self.assertEqual(buttons.nth(2).get_attribute('data-result'), 'intended')
        self.assertNotEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopColor'),
                            buttons.nth(2).evaluate('(e) => getComputedStyle(e).borderTopColor'))

    def test_feedback_once_for_first_answer_only(self):
        card = self.open_current_assets('0929', 'p1')
        card.locator('.review-choice').nth(1).click()
        feedback = self.page.locator('[data-review-feedback]')
        expect(feedback).to_have_attribute('data-result', 'correct')
        expect(feedback).to_contain_text('정답이에요')
        self.assertEqual(feedback.get_attribute('aria-hidden'), 'true')
        card.locator('.review-choice').nth(0).click()  # 해설만 펼침
        expect(feedback).to_have_attribute('data-result', 'correct')
        expect(feedback).to_have_count(0, timeout=2500)
        card = self.open_current_assets('0929', 'p11')
        card.locator('.review-choice').first.click()
        expect(self.page.locator('[data-review-feedback]')).to_have_count(0)

    def test_feedback_replaces_previous_answer(self):
        card = self.open_current_assets('0929', 'p1')
        card.locator('.review-choice').first.click()
        expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'incorrect')
        self.page.wait_for_timeout(500)
        card = self.open_current_assets('0929', 'p2')
        card.locator('.review-choice').nth(4).click()  # p2의 정답 5번
        expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'correct')
        self.page.wait_for_timeout(650)
        expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'correct')
        expect(self.page.locator('[data-review-feedback]')).to_have_count(0, timeout=2500)

    def test_ambiguous_answer_clears_prior_feedback(self):
        self.open_current_assets('0929', 'p1')
        self.page.evaluate('''() => {
          document.querySelector('#p1 .review-choice').click();
          document.querySelector('#p11 .review-choice').click();
        }''')
        expect(self.page.locator('#p11 .review-status')).to_have_text('단일 정답 판정 주의')
        self.assertEqual(self.page.locator('[data-review-feedback]').count(), 0)

    def test_feedback_reset_and_restore(self):
        card = self.open_current_assets('0929', 'p1')
        card.locator('.review-choice').first.click()
        expect(self.page.locator('[data-review-feedback]')).to_have_count(1)
        card.locator('.review-reset').click()
        expect(self.page.locator('[data-review-feedback]')).to_have_count(0)
        card.locator('.review-choice').nth(1).click()
        self.page.reload()
        expect(card.locator('.review-choice').nth(1)).to_have_attribute('data-selected', 'true')
        expect(self.page.locator('[data-review-feedback]')).to_have_count(0)

    def test_feedback_reduced_motion_and_mobile(self):
        self.page.set_viewport_size({'width': 320, 'height': 568})
        self.page.emulate_media(reduced_motion='reduce')
        card = self.open_current_assets('0929', 'p1')
        card.locator('.review-choice').nth(1).click()
        box = self.page.locator('[data-review-feedback]').bounding_box()
        self.assertGreaterEqual(box['x'], 0)
        self.assertLessEqual(box['x'] + box['width'], 320)
        self.assertEqual(self.page.locator('.review-feedback-icon').evaluate('(e) => getComputedStyle(e).animationName'), 'none')
        self.page.emulate_media(media='print', reduced_motion='reduce')
        self.assertEqual(self.page.locator('[data-review-feedback]').evaluate('(e) => getComputedStyle(e).display'), 'none')

    def test_wrong_reset_correct_restore(self):
        card = self.open()
        choices = card.locator('.review-choice')
        expect(choices).to_have_count(5)
        expect(card.locator('.review-help')).to_have_count(0)
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

    CLIPBOARD_MOCK = """
      window.__copied = null;
      Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
        writeText: async (text) => { window.__copied = text; }
      }});
    """
    STORAGE_BLOCKED = ("for(const n of ['localStorage','sessionStorage']) "
                       "Object.defineProperty(window,n,{get(){throw Error('blocked')}});")

    def go_to_last(self):
        last = self.page.evaluate("Array.from(document.querySelectorAll('main article.card')).pop().id")
        self.page.evaluate("id => { location.hash = '#' + id; }", last)
        expect(self.page.locator('#' + last)).to_be_visible()
        return last

    def copy_prompt(self):
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text(
            '복기 프롬프트를 복사했어요. AI 채팅에 붙여 넣으세요.')
        return self.page.evaluate('window.__copied')

    @staticmethod
    def section(text, heading):
        start = text.index(heading)
        nxt = [i for i in (text.find('\n### ', start + 1), text.find('\n## ', start + 1)) if i != -1]
        return text[start:min(nxt) if nxt else len(text)]

    def test_prompt_button_only_on_last_screen(self):
        self.open_current_assets()
        expect(self.page.locator('.review-export')).to_be_hidden()
        self.go_to_last()
        expect(self.page.locator('.review-export')).to_be_visible()
        expect(self.page.locator('.review-export')).to_have_text('복기 프롬프트 복사')
        expect(self.page.locator('.review-export-help')).to_have_count(0)

    def test_prompt_copies_wrong_answer_with_full_text(self):
        self.context.add_init_script(self.CLIPBOARD_MOCK)
        card = self.open_current_assets()
        card.locator('.review-choice').first.click()
        text = self.copy_prompt()
        self.assertTrue(text.startswith('# 생명과학 복기 요청'))
        wrong = self.section(text, '### 오답')
        self.assertIn('#### p1.', wrong)
        self.assertNotIn('#### p1. P1.', wrong)
        self.assertIn('내 답: [1] / 정답: [2]', wrong)
        option_lines = [line for line in text.splitlines() if line.startswith('- [')]
        self.assertTrue(option_lines)
        self.assertFalse([line for line in option_lines if '내 선택' in line or '정답 아님' in line])
        self.assertNotIn('1번 선택', text)
        toast = self.page.locator('[data-review-feedback]')
        expect(toast).to_have_attribute('data-result', 'copied')

    def test_prompt_marks_unsure_and_reset_clears_it(self):
        self.context.add_init_script(self.CLIPBOARD_MOCK)
        card = self.open_current_assets()
        card.locator('.review-choice').nth(1).click()
        self.unsure_button().click()
        text = self.copy_prompt()
        self.assertIn('#### p1.', self.section(text, '### 애매함 표시(맞혔지만 확신 없음)'))
        self.page.evaluate("location.hash = '#p1'")
        card.locator('.review-reset').click()
        text = self.copy_prompt()
        self.assertNotIn('### 애매함 표시', text)
        self.assertIn('#### p1.', self.section(text, '### 미응답'))

    def test_prompt_with_storage_blocked(self):
        self.context.add_init_script(self.STORAGE_BLOCKED)
        self.context.add_init_script(self.CLIPBOARD_MOCK)
        card = self.open_current_assets()
        card.locator('.review-choice').first.click()
        self.assertIn('#### p1.', self.section(self.copy_prompt(), '### 오답'))

    def test_prompt_fallback_dialog_reused(self):
        self.context.add_init_script("""
          Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
            writeText: async () => { throw new Error('denied'); }
          }});
          document.execCommand = () => false;
        """)
        self.open_current_assets()
        self.go_to_last()
        self.page.locator('.review-export').click()
        dialog = self.page.locator('dialog.review-prompt-dialog[open]')
        expect(dialog).to_have_count(1)
        self.assertIn('# 생명과학 복기 요청', dialog.locator('textarea').input_value())
        expect(self.page.locator('.review-export-note')).to_have_text(
            '자동 복사가 막혀 있어요. 열린 창에서 직접 복사해 주세요.')
        expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'manual')
        dialog.get_by_role('button', name='닫기').click()
        expect(self.page.locator('dialog.review-prompt-dialog[open]')).to_have_count(0)
        self.page.locator('.review-export').click()
        expect(self.page.locator('dialog.review-prompt-dialog')).to_have_count(1)
        expect(self.page.locator('dialog.review-prompt-dialog[open]')).to_have_count(1)
        self.assertEqual(self.page.locator('style#review-prompt-style').count(), 1)

    def test_prompt_stem_keeps_figure_alt(self):
        self.context.add_init_script(self.CLIPBOARD_MOCK)
        self.open_current_assets('0917')
        found = self.page.evaluate("""() => {
          const img = document.querySelector('main article.card .problem img');
          return img ? {id: img.closest('article.card').id, alt: img.getAttribute('alt') || ''} : null;
        }""")
        if not found:
            self.skipTest('0917에 그림이 있는 문제가 없음')
        text = self.copy_prompt()
        block = text[text.index('#### ' + found['id'] + '.'):]
        block = block[:block.find('\n####', 1) if '\n####' in block[1:] else len(block)]
        self.assertIn('[그림: ' + found['alt'] + ']', block)

    def test_prompt_keeps_math_as_tex(self):
        from importlib.util import module_from_spec, spec_from_file_location

        helper = REPO / '.agents/skills/bio-problem-explain/scripts/bio_web_assets.py'
        spec = spec_from_file_location('bio_web_assets', helper)
        web_assets = module_from_spec(spec)
        spec.loader.exec_module(web_assets)
        vendor = REPO / web_assets.SHARED_DIR / 'katex'
        def serve(route):
            local = vendor / route.request.url.split('/dist/', 1)[1].split('?', 1)[0]
            if local.is_file():
                route.fulfill(path=str(local))
            else:
                route.abort()
        self.page.route('https://cdn.jsdelivr.net/npm/katex@*/dist/**', serve)
        self.context.add_init_script(self.CLIPBOARD_MOCK)
        card = self.open_current_assets(
            transform=lambda s: s.replace('귀에 털이 난 남성은', '귀에 털이 난 $x^2$ 남성은', 1))
        expect(card.locator('.problem .katex').first).to_be_attached()
        card.locator('.review-choice').first.click()
        text = self.copy_prompt()
        self.assertIn('귀에 털이 난 $x^2$ 남성은', text)
        self.assertNotIn('x2x^2', text)

    def unsure_button(self, cid='p1'):
        return self.page.locator(f'.aid[data-card-id="{cid}"] .review-unsure')

    def test_unsure_button_appears_only_after_correct_answer_and_toggles(self):
        card = self.open()  # 정답 2번
        expect(self.unsure_button()).to_be_hidden()
        card.locator('.review-choice').nth(0).click()
        expect(self.unsure_button()).to_be_hidden()
        card.locator('.review-reset').click()
        expect(self.unsure_button()).to_be_hidden()
        card.locator('.review-choice').nth(1).click()
        button = self.unsure_button()
        expect(button).to_be_visible()
        expect(button).to_have_text('애매함으로 표시')
        button.click()
        expect(button).to_have_text('애매함 표시 취소')
        expect(button).to_have_attribute('aria-pressed', 'true')
        expect(self.page.locator('[data-review-feedback]')).to_contain_text('애매함으로 표시했어요')
        button.click()
        expect(button).to_have_text('애매함으로 표시')
        expect(self.page.locator('[data-review-feedback]')).to_contain_text('애매함 표시를 취소했어요')

    def test_unsure_button_hidden_on_ambiguous_question(self):
        card = self.open('0929', 'p11')  # 모호 문항, 출제 의도상 답 3번
        card.locator('.review-choice').nth(0).click()
        expect(self.unsure_button('p11')).to_be_hidden()
        card.locator('.review-reset').click()
        card.locator('.review-choice').nth(2).click()
        expect(self.unsure_button('p11')).to_be_hidden()

    def test_unsure_survives_navigation_and_reload(self):
        card = self.open()
        card.locator('.review-choice').nth(1).click()
        self.unsure_button().click()
        self.page.locator('#pager-next').click()
        self.page.locator('#pager-prev').click()
        expect(self.unsure_button()).to_have_attribute('aria-pressed', 'true')
        self.page.reload()
        expect(self.unsure_button()).to_have_attribute('aria-pressed', 'true')

    def test_storage_blocked(self):
        self.context.add_init_script("for(const n of ['localStorage','sessionStorage']) Object.defineProperty(window,n,{get(){throw Error('blocked')}});")
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
          for(let i=0;i<sessionStorage.length;i++){
            const key=sessionStorage.key(i);
            if(key.startsWith('od-review-attempt:')) sessionStorage.setItem(key,'{');
          }
        }""")
        self.page.reload()
        expect(card.locator('.review-diagnostic:visible')).to_have_count(0)
        expect(self.page.locator('#progress-n')).to_have_text('0')
        card.locator('.review-choice').first.click()
        self.page.evaluate("""() => {
          for(let i=0;i<sessionStorage.length;i++){
            const key=sessionStorage.key(i);
            if(key.startsWith('od-review-attempt:')) sessionStorage.setItem(key,JSON.stringify({version:'old',selected:'1'}));
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
        shots = REPO / '.superpowers/sdd/bio-review-browser-check'
        shots.mkdir(parents=True, exist_ok=True)
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
