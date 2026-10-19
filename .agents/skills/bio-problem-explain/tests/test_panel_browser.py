"""Exercise desktop defaults, breakpoint transitions and saved panel intent."""
import functools
import http.server
import threading

import pytest
from playwright.sync_api import sync_playwright, expect
from helpers import acceptance_pack
from mpe_render import build_explanation
from mpe_shared import parse, outer


@pytest.fixture
def panel_page_url(tmp_path, request):
    pack, fragments = acceptance_pack(tmp_path / "repo")
    if getattr(request, 'param', False):
        for key, text in fragments.items():
            for node in parse(text).find_all(lambda n: n.attrs.get('data-explanation') in ('start', 'pitfall', 'retry')):
                text = text.replace(outer(node), '')
            fragments[key] = text
    artifacts = build_explanation(pack, fragments, tmp_path / "stage", tmp_path / "repo")
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(tmp_path)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/stage/{artifacts.html.name}#p3"
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.parametrize('panel_page_url', [True], indirect=True)
def test_core_only_explanation_keeps_choice_navigation_and_summary(panel_page_url, tmp_path):
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            for width, height in ((1280, 900), (375, 812)):
                for theme in ('light', 'dark'):
                    context = browser.new_context(viewport={'width': width, 'height': height}, color_scheme=theme)
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                    page.on('requestfailed', lambda request: errors.append(request.url))
                    page.goto(panel_page_url, wait_until='networkidle')
                    assert page.locator('[data-explanation="start"], [data-explanation="pitfall"], [data-explanation="retry"]').count() == 0
                    assert page.locator('#p3 [data-explanation]').count() == 4
                    assert page.locator('#p3 .verdict-card').count() == 5
                    if width < 1024:
                        page.locator('#p3 .problem-toggle').click()
                    pane = page.locator('[data-problem-for="p3"]')
                    choice = pane.locator('.review-choice[data-choice-id="1"]')
                    choice.click()
                    assert choice.get_attribute('data-result') == 'selected'
                    if width >= 1024:
                        assert page.locator('#p3 .verdict-card.is-target').inner_text().startswith('(1)')
                    page.locator('#toggle-right').click()
                    assert page.locator('#panel-right').is_visible()
                    assert page.locator('#panel-right .sum:not([hidden]) .summary-group').count() > 0
                    expect(page.locator('#panel-right .sum:not([hidden]) .summary-group')).to_be_in_viewport()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.screenshot(path=str(tmp_path / f'core-only-{width}-{theme}.png'), animations='disabled')
                    assert errors == []
                    context.close()
        finally:
            browser.close()


def test_desktop_toc_and_problem_default_open_without_overriding_saved_choice(panel_page_url):
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            for width in (1024, 1280):
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                page.goto(panel_page_url, wait_until="networkidle")
                assert page.locator("#panel-left").is_visible()
                assert page.locator("#panel-prob").is_visible()
                left, problem, content = [page.locator(s).bounding_box() for s in
                                          ("#panel-left", "#panel-prob", ".content")]
                assert left["x"] + left["width"] <= problem["x"] + 1
                assert problem["x"] + problem["width"] <= content["x"] + 1
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.locator("#toggle-left").click()
                page.reload(wait_until="networkidle")
                assert page.locator("#panel-left").is_hidden()
                assert page.locator("#panel-prob").is_visible()
                context.close()
            context = browser.new_context(viewport={"width": 1023, "height": 900})
            page = context.new_page()
            page.goto(panel_page_url, wait_until="networkidle")
            assert page.locator("#panel-prob").is_hidden()
            assert page.locator(".problem-toggle:visible").count() == 1
            page.set_viewport_size({"width": 1024, "height": 900})
            page.wait_for_timeout(100)
            assert page.locator("#panel-left").is_visible()
            assert page.locator("#panel-prob").is_visible()
            context.close()
        finally:
            browser.close()
