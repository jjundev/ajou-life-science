"""Exercise desktop defaults, breakpoint transitions and saved panel intent."""
import functools
import http.server
import threading

import pytest
from playwright.sync_api import sync_playwright
from helpers import acceptance_pack
from mpe_render import build_explanation


@pytest.fixture
def panel_page_url(tmp_path):
    pack, fragments = acceptance_pack(tmp_path / "repo")
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
