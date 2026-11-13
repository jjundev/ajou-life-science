"""Standard browser check for a built explanation stage: `mpe_cli.py browser --run RUN [--shots]`.

Writes `<target>/evidence/explain-browser.json` and syncs it into the stage (reviews kept).
The JSON is evidence for the `browser` review; the reviewing agent still looks at the screenshots
(spacing, overlap) and records the review with `review-merge --kind browser`.

Template behaviour this script relies on (instead of rediscovering it every run):
- Navigation uses `location.hash`, not TOC clicks: at 1024px `fit()` closes `#panel-left` when the
  summary panel opens, so `#panel-left a[href="#pN"]` is hidden and a click would time out.
- Wide screens (>=1024) show the problem in `#panel-prob [data-problem-for=pN]`; narrow screens put it
  inside `#pN` behind `.problem-toggle`.
- Concept/original links in the stage are relative to the final publish folder, not the stage, so they
  are resolved on disk against the publish folder (no `page.goto` on same-document hashes).
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import unicodedata
from urllib.parse import quote, unquote, urlsplit

VIEWPORTS = [(1280, 900), (1024, 768), (375, 812)]
THEMES = ['light', 'dark']
ACTION_TIMEOUT = 3000
NAV_TIMEOUT = 15000
SETTLE_MS = 600  # 문항 전환 애니메이션이 끝난 뒤 찍는다(바로 찍으면 본문이 비어 보인다)
HREF_RE = re.compile(r'<a\b[^>]*\bhref="([^"]+)"', re.I)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def preview_server(artifacts, repo, destination):
    """Expose the stage at its eventual URL, plus the pinned shared files."""
    stage = artifacts.html.parent.resolve()
    manifest = json.loads(artifacts.manifest.read_text(encoding='utf-8'))
    if 'shared_assets' not in manifest:
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(stage)))
        return server, quote(artifacts.html.name)

    publish_path = destination.resolve().relative_to(repo.resolve())
    prefix = Path(unicodedata.normalize('NFC', publish_path.as_posix()))
    shared_dir = Path(manifest['shared_assets']['directory'])
    shared = (repo / shared_dir).resolve()
    shared_files = manifest['shared_assets']['files']

    class Preview(Quiet):
        def translate_path(self, url):
            relative = Path(unquote(urlsplit(url).path).lstrip('/'))
            if '..' in relative.parts:
                return ''
            if relative.is_relative_to(shared_dir):
                root, tail = shared, relative.relative_to(shared_dir)
                if relative.as_posix() not in shared_files:
                    return ''
            elif relative.is_relative_to(prefix):
                root, tail = stage, relative.relative_to(prefix)
            else:
                return ''
            path = (root / tail).resolve()
            return str(path) if path.is_relative_to(root) and path.is_file() else ''

    server = ThreadingHTTPServer(('127.0.0.1', 0), Preview)
    return server, quote(unicodedata.normalize('NFC', (publish_path / artifacts.html.name).as_posix()))


def link_problems(html_text, publish_dir, stage_dir):
    """Every relative link must resolve from the publish folder (stage-local assets from the stage)."""
    out, seen = [], set()
    for href in HREF_RE.findall(html_text):
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path or href in seen:
            continue
        seen.add(href)
        rel = unquote(url.path)
        target = (publish_dir / rel).resolve()
        if not target.is_file() and (stage_dir / rel).is_file():
            target = (stage_dir / rel).resolve()
        if not target.is_file():
            out.append(f'링크 파일 없음: {rel}')
            continue
        anchor = unquote(url.fragment)
        if anchor and target.suffix == '.html':
            text = target.read_text(encoding='utf-8', errors='replace')
            if not re.search(r'\bid=["\']' + re.escape(anchor) + r'["\']', text):
                out.append(f'링크 앵커 없음: {rel}#{anchor}')
    return out, len(seen)


def run_browser(item, shots=False):
    """Return True when any check failed."""
    from playwright.sync_api import sync_playwright
    from mpe_cli import load_artifacts, load_fragments, sync_evidence, read_json
    from mpe_source import sha256
    from mpe_render import check_artifacts
    from mpe_types import ExplainError
    pack, folder = item['pack'], item['folder']
    artifacts = load_artifacts(item)
    errors = check_artifacts(pack, artifacts)
    if errors:
        raise ExplainError(' / '.join(errors))
    stage = artifacts.html.parent
    html_text = artifacts.html.read_text(encoding='utf-8')
    model_match = re.search(r'<script[^>]*id="explain-choice-model"[^>]*>(.*?)</script>', html_text, re.S)
    choices = json.loads(model_match.group(1)) if model_match else {}
    ids = [p.id for p in pack.problems]
    has_original = {p.id: bool(p.original_html.strip()) for p in pack.problems}
    failures, runs = [], []
    links, link_count = link_problems(html_text, pack.path.parent, stage)
    failures += links
    server, page_path = preview_server(artifacts, item['repo'], pack.path.parent)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}/'
    url = origin + page_path
    shot_dir = folder / 'browser-shots'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in VIEWPORTS:
                for theme in THEMES:
                    label = f'{width}x{height} {theme}'
                    ctx = browser.new_context(viewport={'width': width, 'height': height}, color_scheme=theme)
                    blocked, errors, local_fail = [], [], []
                    ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith((origin, 'data:', 'blob:'))
                              else (blocked.append(r.request.url), r.abort()))
                    page = ctx.new_page()
                    page.set_default_timeout(ACTION_TIMEOUT)
                    page.set_default_navigation_timeout(NAV_TIMEOUT)
                    page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
                    page.on('console', lambda m: errors.append(f'console: {m.text}') if m.type == 'error' else None)
                    page.on('response', lambda r: local_fail.append(f'{r.status}: {r.url}') if r.status >= 400 else None)
                    mine = []
                    expect = lambda ok, what: ok or mine.append(f'{label}: {what}')

                    def step(what, fn):
                        try:
                            return fn()
                        except Exception as e:
                            mine.append(f'{label}: {what}: {type(e).__name__}: {str(e).splitlines()[0]}')

                    def go(pid):
                        page.evaluate('(id) => { location.hash = id; }', pid)
                        page.locator(f'#{pid}').wait_for(state='visible')

                    wide = width >= 1024
                    step('열기', lambda: page.goto(url + '#' + ids[0], wait_until='load'))
                    for pid in ids:
                        def one(pid=pid):
                            go(pid)
                            if wide:
                                pane = page.locator(f'#panel-prob [data-problem-for="{pid}"]')
                                expect(pane.is_visible(), f'{pid}: 문제 패널에 문제 없음')
                                expect(page.locator(f'#{pid} > [data-problem-for]').count() == 0, f'{pid}: 넓은 화면인데 본문 안에 문제')
                                expect(page.locator('#tab-original').is_visible() == has_original[pid], f'{pid}: 원문 탭 표시 불일치')
                            else:
                                toggle = page.locator(f'#{pid} .problem-toggle')
                                expect(toggle.count() == 1, f'{pid}: 좁은 화면 문제 보기 토글 없음')
                                if toggle.count() and toggle.get_attribute('aria-expanded') != 'true':
                                    toggle.click()
                                pane = page.locator(f'#{pid} [data-problem-for="{pid}"]')
                                expect(pane.is_visible(), f'{pid}: 문제 보기를 열어도 문제가 안 보임')
                            model = choices.get(pid)
                            if model and model.get('mode') == 'single':
                                right = model['answer']
                                wrong = next(o for o in model['options'] if o != right)
                                pane.locator(f'.review-choice[data-choice-id="{wrong}"]').click()
                                expect(pane.locator(f'[data-choice-id="{wrong}"]').get_attribute('data-result') == 'selected', f'{pid}: 오답 판정 표시')
                                expect(bool(pane.locator('.review-status').inner_text().strip()), f'{pid}: 판정 문구 없음')
                                pane.locator('.review-reset').click()
                                pane.locator(f'.review-choice[data-choice-id="{right}"]').click()
                                expect(pane.locator(f'[data-choice-id="{right}"]').get_attribute('data-result') == 'correct', f'{pid}: 정답 표시')
                                pane.locator('.review-reset').click()
                            return True
                        step(f'{pid} 조작', one)
                    def summary():
                        go(ids[0])
                        page.locator('#toggle-right').click()
                        panel = page.locator('#panel-right')
                        panel.wait_for(state='visible')
                        expect(page.locator('#panel-right-title').inner_text().strip() == '페이지 요약', '요약 패널 제목')
                        for pid in (ids[0], ids[-1]):
                            go(pid)
                            heading = page.locator(f'#{pid} h2, #{pid} h3').first.inner_text().strip()
                            body = panel.inner_text().replace('페이지 요약', '', 1).strip()
                            expect(bool(body), f'{pid}: 요약 내용 없음')
                            expect(not heading or heading not in body, f'{pid}: 요약에 문항 제목 반복')
                    if shots:
                        shot_dir.mkdir(parents=True, exist_ok=True)
                        figure = next((p for p in ids if page.locator(f'[data-problem-for="{p}"] svg, #{p} svg').count()), ids[-1])
                        for pid in dict.fromkeys((ids[0], figure)):
                            shot = shot_dir / f'{width}x{height}-{theme}-{pid}.png'
                            step(f'스크린샷 {pid}', lambda: (go(pid), page.wait_for_timeout(SETTLE_MS), page.screenshot(path=str(shot), timeout=10000)))
                    step('요약 패널', summary)
                    expect(page.locator('.katex-error').count() == 0, 'KaTeX 오류')
                    expect(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), '가로 넘침')
                    mine += [f'{label}: {e}' for e in errors + local_fail]
                    mine += [f'{label}: 외부 요청 {u}' for u in blocked]
                    runs.append({'label': label, 'failures': mine, 'external_blocked': blocked})
                    failures += mine
                    ctx.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report = {'status': 'fail' if failures else 'pass', 'html': str(artifacts.html), 'sha256': sha256(artifacts.html),
              'viewports': [f'{w}x{h}' for w, h in VIEWPORTS], 'themes': THEMES, 'problems': ids,
              'links_checked': link_count, 'runs': runs, 'failures': failures,
              'screenshots': str(shot_dir) if shots else None,
              'note': '스크립트 PASS는 기계 확인이다. 간격·겹침·그림은 스크린샷을 직접 보고 browser 검토를 기록한다.'}
    evidence = folder / 'evidence'
    evidence.mkdir(exist_ok=True)
    (evidence / 'explain-browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'browser: {report["status"]} · {len(runs)}회 · 링크 {link_count}개 · 실패 {len(failures)}건 → {evidence / "explain-browser.json"}')
    for line in failures[:20]:
        print('  ' + line)
    if (folder / 'review.json').is_file():
        sync_evidence(item, load_fragments(item))
    return bool(failures)
