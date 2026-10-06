"""Run explicitly: python .agents/skills/bio-review-pack/tests/browser_check_review.py"""
from functools import partial
import json
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

    def open_current_assets(self, date='0929', card='p1'):
        path = next((REPO / '복습노트' / date).glob('복습문제*.html'))
        url = self.url(date, card).split('#', 1)[0]
        source = ri.install(path.read_text(encoding='utf-8'), path.name)
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

    PICKER_MOCK = """
      window.__saved = null;
      window.__pickerCalls = 0;
      const writer = (name) => ({ async createWritable() {
        let text = '';
        return { async write(t) { text += t; }, async close() { window.__saved = { name, text, dir: '풀이기록' }; } };
      } });
      const outDir = { name: '풀이기록', async getFileHandle(name) { return writer(name); } };
      window.showDirectoryPicker = async (opts) => {
        window.__pickerCalls++;
        window.__pickerOpts = opts;
        return { name: '0929',
          async getFileHandle(name, o) { if (o && o.create) throw new Error('unexpected'); return {}; },
          async getDirectoryHandle(name) { return outDir; } };
      };
    """
    SNAP_KEY = "Object.keys(sessionStorage).find(k => k.startsWith('od-review-export:v1:'))"

    def go_to_last(self):
        last = self.page.evaluate("Array.from(document.querySelectorAll('main article.card')).pop().id")
        self.page.evaluate("id => { location.hash = '#' + id; }", last)
        expect(self.page.locator('#' + last)).to_be_visible()
        return last

    def saved_json(self):
        return json.loads(self.page.evaluate('window.__saved.text'))

    def test_leaving_a_card_updates_snapshot(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        self.assertIsNone(self.page.evaluate(f"sessionStorage.getItem({self.SNAP_KEY})"))
        self.page.locator('#pager-next').click()
        snap = self.page.evaluate(f"JSON.parse(sessionStorage.getItem({self.SNAP_KEY}))")
        self.assertEqual(snap['schema'], 1)
        self.assertIsNotNone(snap['cards']['p1']['selected'])
        self.assertIsNotNone(snap['cards']['p1']['updatedAt'])

    def test_export_button_only_on_last_screen(self):
        self.open()
        expect(self.page.locator('.review-export')).to_be_hidden()
        self.go_to_last()
        expect(self.page.locator('.review-export')).to_be_visible()
        expect(self.page.locator('.review-export')).to_have_text('JSON 내보내기')

    def test_export_to_chosen_folder(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        saved = self.page.evaluate('window.__saved')
        self.assertRegex(saved['name'], r'^복습문제_0929_Heredity_풀이기록_\d{8}-\d{4}\.json$')
        data = self.saved_json()
        dom_ids = self.page.evaluate("Array.from(document.querySelectorAll('main article.card')).map(e => e.id)")
        exported = [c['id'] for c in data['cards']]
        self.assertEqual(exported, [i for i in dom_ids if i in set(exported)])
        self.assertEqual(data['summary']['total'], len(exported))
        self.assertEqual(data['summary']['answered'], 1)
        self.assertEqual(data['summary']['unanswered'], len(exported) - 1)
        first = next(c for c in data['cards'] if c['id'] == 'p1')  # partA가 앞에 붙으면 p1이 첫 카드가 아닐 수 있다
        self.assertIsNotNone(first['selected'])
        self.assertIsNotNone(first['updatedAt'])
        self.assertIsNone(data['cards'][-1]['selected'])

    def test_export_goes_to_fixed_folder_with_remembered_picker_id(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        self.assertEqual(self.page.evaluate('window.__saved.dir'), '풀이기록')
        self.assertEqual(self.page.evaluate('window.__pickerOpts'), {'mode': 'readwrite', 'id': 'od-review-export'})

    def test_export_wrong_folder_saves_nothing(self):
        self.context.add_init_script(self.PICKER_MOCK)
        self.context.add_init_script(
            "const real = () => window.showDirectoryPicker; "
            "window.__origPicker = null; "
            "window.addEventListener('DOMContentLoaded', () => { window.showDirectoryPicker = async () => ({ name: 'etc', "
            "async getFileHandle() { const e = new Error('nf'); e.name = 'NotFoundError'; throw e; } }); });")
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('[data-review-feedback]')).to_contain_text('폴더를 골라 주세요')
        self.assertIsNone(self.page.evaluate('window.__saved'))

    def test_handle_store_round_trip_in_real_indexeddb(self):
        self.open()
        result = self.page.evaluate("""async () => {
          const s = ReviewInteraction.handleStore(window);
          await s.clear();
          const empty = await s.get();
          await s.set({name: 'x'});
          const got = await s.get();
          await s.clear();
          return [empty, got, await s.get()];
        }""")
        self.assertEqual(result, [None, {'name': 'x'}, None])

    def test_export_reflects_reset(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        card.locator('.review-reset').click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        data = self.saved_json()
        self.assertEqual(data['summary']['answered'], 0)
        self.assertIsNone(data['cards'][0]['selected'])

    def test_export_cancel_saves_nothing(self):
        self.context.add_init_script(
            "window.showDirectoryPicker = async () => { const e = new Error('cancel'); e.name = 'AbortError'; throw e; };")
        self.open()
        self.go_to_last()
        downloads = []
        self.page.on('download', lambda d: downloads.append(d))
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('저장을 취소했어요.')
        self.assertEqual(downloads, [])

    def test_export_button_is_disabled_while_picker_is_open(self):
        self.context.add_init_script(
            "window.__calls = 0; window.showDirectoryPicker = () => { window.__calls++; return new Promise(() => {}); };")
        self.open()
        self.go_to_last()
        button = self.page.locator('.review-export')
        button.click()
        expect(button).to_be_disabled()
        self.page.wait_for_function('window.__calls === 1')
        button.click(force=True)
        self.page.wait_for_timeout(300)
        self.assertEqual(self.page.evaluate('window.__calls'), 1)

    def test_export_result_shows_top_toast(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        toast = self.page.locator('[data-review-feedback]')
        expect(toast).to_have_attribute('data-result', 'saved')
        expect(toast).to_contain_text('풀이기록 폴더에 저장했어요')
        self.assertLess(toast.bounding_box()['y'], 150)
        expect(toast).to_have_count(0, timeout=4000)

    def test_export_cancel_shows_neutral_toast(self):
        self.context.add_init_script(
            "window.showDirectoryPicker = async () => { const e = new Error('cancel'); e.name = 'AbortError'; throw e; };")
        self.open()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'cancelled')
        expect(self.page.locator('[data-review-feedback]')).to_contain_text('저장을 취소했어요')

    def test_export_help_popup(self):
        self.open()
        self.go_to_last()
        help_btn = self.page.locator('.review-export-help')
        popup = self.page.locator('.review-export-popup')
        expect(help_btn).to_be_visible()
        expect(help_btn).to_have_attribute('aria-expanded', 'false')
        expect(popup).to_be_hidden()
        help_btn.click()
        expect(help_btn).to_have_attribute('aria-expanded', 'true')
        expect(popup).to_be_visible()
        expect(popup).to_contain_text('풀이기록 폴더에 바로 저장')
        self.page.keyboard.press('Escape')
        expect(popup).to_be_hidden()
        help_btn.click()
        expect(popup).to_be_visible()
        self.page.locator('.review-export-popup-close').click()
        expect(popup).to_be_hidden()
        help_btn.click()
        self.page.locator('.hero, main').first.click(position={'x': 5, 'y': 5}, force=True)
        expect(popup).to_be_hidden()

    def test_export_falls_back_to_download(self):
        self.context.add_init_script(
            "window.showDirectoryPicker = async () => { const e = new Error('no'); e.name = 'SecurityError'; throw e; };")
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        with self.page.expect_download() as info:
            self.page.locator('.review-export').click()
        download = info.value
        self.assertRegex(download.suggested_filename, r'\.json$')
        data = json.loads(Path(download.path()).read_text(encoding='utf-8'))
        self.assertEqual(data['summary']['answered'], 1)
        expect(self.page.locator('.review-export-note')).to_have_text('다운로드 폴더에 저장했어요.')

    def test_export_with_storage_blocked(self):
        self.context.add_init_script(
            "for(const n of ['localStorage','sessionStorage']) Object.defineProperty(window,n,{get(){throw Error('blocked')}});")
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').first.click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        self.assertEqual(self.saved_json()['summary']['answered'], 1)

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

    def test_unsure_updates_snapshot_immediately_and_survives_navigation(self):
        card = self.open()
        card.locator('.review-choice').nth(1).click()
        self.unsure_button().click()
        snap = self.page.evaluate(f"JSON.parse(sessionStorage.getItem({self.SNAP_KEY}))")
        self.assertTrue(snap['cards']['p1']['unsure'])
        self.page.locator('#pager-next').click()
        self.page.locator('#pager-prev').click()
        expect(self.unsure_button()).to_have_attribute('aria-pressed', 'true')
        self.page.reload()
        expect(self.unsure_button()).to_have_attribute('aria-pressed', 'true')

    def test_unsure_is_exported_and_reset_clears_it(self):
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').nth(1).click()
        self.unsure_button().click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        data = self.saved_json()
        self.assertTrue(next(c for c in data['cards'] if c['id'] == 'p1')['unsure'])
        self.assertEqual(data['summary']['unsure'], 1)
        self.assertFalse(data['cards'][-1]['unsure'])
        self.page.evaluate("location.hash = '#p1'")
        card.locator('.review-reset').click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        data = self.saved_json()
        self.assertFalse(next(c for c in data['cards'] if c['id'] == 'p1')['unsure'])
        self.assertEqual(data['summary']['unsure'], 0)

    def test_unsure_export_with_storage_blocked(self):
        self.context.add_init_script(
            "for(const n of ['localStorage','sessionStorage']) Object.defineProperty(window,n,{get(){throw Error('blocked')}});")
        self.context.add_init_script(self.PICKER_MOCK)
        card = self.open()
        card.locator('.review-choice').nth(1).click()
        self.unsure_button().click()
        self.go_to_last()
        self.page.locator('.review-export').click()
        expect(self.page.locator('.review-export-note')).to_have_text('풀이기록 폴더에 저장했어요.')
        self.assertEqual(self.saved_json()['summary']['unsure'], 1)

    def test_snapshot_does_not_survive_a_new_tab(self):
        card = self.open()
        card.locator('.review-choice').first.click()
        self.page.locator('#pager-next').click()
        other = self.context.new_page()
        other.goto(self.url('0929'))
        self.assertEqual(other.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('od-review-export:'))"), [])
        other.close()

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
