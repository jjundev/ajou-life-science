"""Run explicitly: python .agents/skills/bio-review-pack/tests/browser_check_note_supplement.py"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import tempfile
import threading
import unittest
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from _util import MINI_RUN
import assemble


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class TestSupplementPanelBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.note, _ = assemble.assemble(MINI_RUN, Path(cls.tmp.name))
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=cls.tmp.name))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def test_panel_label_return_link_and_mobile_drawer(self):
        for width, height in ((1280, 900), (375, 812)):
            for theme in ('light', 'dark'):
                with self.subTest(width=width, theme=theme):
                    context = self.browser.new_context(viewport={'width': width, 'height': height}, color_scheme=theme)
                    try:
                        context.route('https://**/*', lambda route: route.abort())
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(f'http://127.0.0.1:{self.server.server_port}/' + quote(self.note.name) + '#s1-var')
                        expect(page.locator('#s1-var')).to_be_visible()
                        if width < 1024:
                            page.locator('#toggle-right').click()
                        label = page.locator('#panel-right .sum:not([hidden]) .sum-supp-label')
                        expect(label).to_have_text('보충 · 수업에서 다루지 않았어요')
                        expect(label).to_be_visible()
                        page.locator('#panel-right .sum-supp-link').click()
                        expect(page.locator('body')).not_to_have_class(re.compile(r'\bdrawer-open\b'))
                        target = page.locator('#s1-var-supp-1')
                        expect(target).to_be_visible()
                        expect(target).to_be_focused()
                        self.assertEqual(page.evaluate('location.hash'), '#s1-var-supp-1')
                        self.assertEqual(errors, [])
                    finally:
                        context.close()


if __name__ == '__main__':
    unittest.main()
