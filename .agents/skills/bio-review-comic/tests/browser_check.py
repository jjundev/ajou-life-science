"""Run explicitly with the repository Playwright Python; uses test-only rasters."""
import argparse
import copy
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright
from test_comic import ComicPipeline


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    ComicPipeline.setUpClass()
    fixture = ComicPipeline('test_held_pages_stay_visible_and_are_not_complete')
    fixture.setUp()
    server = None
    try:
        book = fixture.ready()
        page = book['pages'][0]
        page['panels'] += [copy.deepcopy(page['panels'][0]) for _ in range(4)]
        page['panels'][3]['caption'] = '가정한 실험 조건에서 얻은 결과와 실제 과거의 사건을 구별해야 해요. ' * 9
        fixture.write('storyboard.json', book)
        fixture.images()
        preview = fixture.api.build(fixture.run)
        handler = partial(QuietHandler, directory=fixture.tmp.name)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/run/preview.html#s0-miller'
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            results = []
            try:
                for width, height in ((1440, 900), (375, 812)):
                    for theme in ('light', 'dark'):
                        context = browser.new_context(viewport={'width': width, 'height': height}, color_scheme=theme)
                        context.route('https://**/*', lambda route: route.abort())
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(url)
                        expect(page.locator('#s0-miller')).to_be_visible()
                        expect(page.locator('#s0-miller .comic-panel')).to_have_count(8)
                        # Check all topics and force lazy images into view before decoding checks.
                        for topic in ('s0-miller', 's0-recap', 's1-cheatsheet'):
                            page.goto(url.split('#')[0] + '#' + topic)
                            for img in page.locator(f'#{topic} img').all():
                                img.scroll_into_view_if_needed()
                                expect(img).to_have_js_property('complete', True)
                                assert img.evaluate('(img) => img.naturalWidth > 0'), 'Raster did not decode'
                            assert page.locator('.content').evaluate('(el) => el.scrollWidth <= el.clientWidth + 1')
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        page.goto(url)
                        # Read state must not create the original note's key.
                        assert page.evaluate("Object.keys(localStorage).some(k => k.startsWith('od-comic-read:'))")
                        assert not page.evaluate("Object.keys(localStorage).some(k => k.startsWith('od-note-read:'))")
                        page.locator('#pager-next').click()
                        expect(page.locator('#s0-recap')).to_be_visible()
                        page.keyboard.press('ArrowLeft')
                        expect(page.locator('#s0-miller')).to_be_visible()
                        if width < 1024:
                            page.locator('#toggle-left').click()
                        page.locator('#panel-left a[href="#s1-cheatsheet"]').click()
                        expect(page.locator('#s1-cheatsheet')).to_be_visible()
                        page.locator('#toggle-right').click()
                        expect(page.locator('#sum-for .sum:not([hidden])')).to_contain_text('재료와 살아 있는 세포')
                        if width < 1024:
                            page.keyboard.press('Escape')
                        else:
                            page.locator('#toggle-right').click()
                        page.locator('#theme-toggle').click()
                        expected_theme = 'dark' if theme == 'light' else 'light'
                        assert page.locator('html').get_attribute('data-theme') == expected_theme
                        page.reload()
                        assert page.locator('html').get_attribute('data-theme') == expected_theme
                        page.locator('#theme-toggle').click()
                        # Actual original-note same-tab navigation and return.
                        link = page.locator('#s1-cheatsheet .comic-source a')
                        assert link.get_attribute('target') == '_self'
                        link.scroll_into_view_if_needed()
                        link.click()
                        assert 'Test.html' in page.url and page.url.endswith('#s1-cheatsheet')
                        page.go_back()
                        expect(page.locator('#s1-cheatsheet')).to_be_visible()
                        page.goto(url)
                        page.screenshot(path=str(args.output / f'{width}-{theme}.png'), full_page=True, animations='disabled')
                        assert errors == [], errors
                        results.append({'width': width, 'theme': theme, 'pages': 3, 'images': 16, 'errors': errors})
                        context.close()
            finally:
                browser.close()
        import json
        (args.output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps({'status': 'passed', 'views': results, 'screenshots': str(args.output.resolve()), 'art': 'synthetic fixtures only'}, indent=2))
    finally:
        if server:
            server.shutdown()
            server.server_close()
        fixture.doCleanups()


if __name__ == '__main__':
    main()
