"""Run browser checks on the preview or the actual local publication."""
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version as package_version
import json
from os.path import commonpath
from pathlib import Path
from threading import Thread
from urllib.parse import quote, unquote, urlsplit

from comic_browser_evidence import (
    LINK_RECORD, PREVIEW_RECORD, VIEWS, preserve_published_report, require_current_resources, save_link_status,
)
from comic_contract import CSS, TEMPLATE, assets_for, jobs_for, local, read, validate_storyboard, write_atomic
from comic_links import strip_links
from comic_render import render
from comic_source import digest, existing, nfc

TIMEOUT = 5000
CHECKER = Path(__file__).resolve()


@dataclass
class Inputs:
    repo: Path
    work: Path
    comic: Path
    note: Path
    pages: list
    files: dict
    images: dict
    source_status: str
    note_link_error: str | None

    def hashes(self):
        return {
            'files': {name: digest(path.read_bytes()) for name, path in self.files.items()},
            'images': {key: digest(path.read_bytes()) for key, path in self.images.items()},
        }


def inputs_for(run, stage):
    published = stage == 'published'
    publication = run / 'publication.json'
    record = read(publication) if published else None
    work = existing(record['version']) if published else run
    work, src, book = validate_storyboard(work, historical=published)
    repo, note = existing(src['repo']), existing(src['path'])
    comic = existing(record['html']) if published else run / 'preview.html'
    if not note.is_relative_to(repo) or (published and not comic.is_relative_to(repo)):
        raise ValueError('정리노트와 발행 HTML은 저장소 안에 있어야 합니다.')
    if not any(page['status'] == 'ready' for page in book['pages']):
        raise ValueError('브라우저에서 검사할 준비 완료 페이지가 없습니다.')
    files = {name: work / name for name in ('source.json', 'source.html', 'storyboard.json', 'images.json')}
    files.update(comic=comic, note=note, checker=CHECKER)
    if published:
        files['publication'] = publication
        files['archived_publication'] = work / 'publication.json'
        if read(files['archived_publication']) != record:
            raise ValueError('RUN과 발행 버전의 publication.json이 다릅니다.')
        if digest(comic.read_bytes()) != record['html_sha256']:
            raise ValueError('발행 HTML이 publication.json의 지문과 다릅니다.')
    else:
        files.update(template=TEMPLATE, css=CSS)
        if comic.read_bytes() != render(run, comic).encode('utf-8'):
            raise ValueError('preview.html이 현재 렌더링 결과와 다릅니다. build 후 다시 검사하세요.')
    note_link_error = None
    note_text = note.read_bytes().decode('utf-8')
    try:
        content_sha256 = digest(strip_links(note_text))
    except ValueError as exc:
        if not published:
            raise
        note_link_error = str(exc)
        status = 'invalid_managed_links'
    else:
        status = 'current' if content_sha256 == src['content_sha256'] else 'changed_since_publication'
    assets = assets_for(work, jobs_for(src, book))
    images = {key: local(work, item['file']) for key, item in assets.items()}
    return Inputs(repo, work, comic, note, book['pages'], files, images, status, note_link_error)


class CheckFailure(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        super().__init__(f'기대값 {expected!r}, 실제값 {actual!r}')


def equal(actual, expected):
    if actual != expected:
        raise CheckFailure(expected, actual)


@contextmanager
def serve(inputs):
    # Preview relative links also work when the RUN is a sibling of the repository.
    root = Path(commonpath((inputs.repo, inputs.work)))
    allowed = (inputs.repo, inputs.work)

    class Handler(SimpleHTTPRequestHandler):
        def send_head(self):
            path = Path(self.translate_path(self.path)).resolve()
            if not path.is_file() or not any(path.is_relative_to(folder) for folder in allowed):
                self.send_error(404)
                return None
            return super().send_head()

        def log_message(self, *_):
            pass

    with ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root))) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}', root
        finally:
            server.shutdown()
            thread.join()


def url_for(origin, root, path, topic=''):
    url = f"{origin}/{quote(path.relative_to(root).as_posix())}"
    return f'{url}#{quote(topic, safe="")}' if topic else url


def url_parts(url):
    parts = urlsplit(url)
    return parts.scheme, parts.netloc, nfc(unquote(parts.path)), parts.query, unquote(parts.fragment)


def topic_selector(topic):
    return f'article.topic[id={json.dumps(topic, ensure_ascii=False)}]'


def destination(tab, url, topic, expect, *, comic=False):
    if url_parts(tab.url) != url_parts(url):
        raise CheckFailure(url, tab.url)
    equal(len(tab.context.pages), 1)
    selector = topic_selector(topic)
    active = f'{selector}.is-current'
    if not comic:
        active += f', {selector}:not(.screen)'
    expect(tab.locator(active)).to_be_visible()


def click_source(tab, note_url, topic, expect):
    link = tab.locator(f'{topic_selector(topic)} .comic-source a')
    expect(link).to_have_attribute('target', '_self')
    link.click()
    destination(tab, note_url, topic, expect)


def click_note(tab, comic_url, topic, expect):
    links = tab.locator(f'{topic_selector(topic)} [data-bio-comic] a').all()
    candidates = [(link, link.evaluate('el => el.href')) for link in links]
    # Select by publication path so a wrong topic fragment reaches the actual click.
    matches = [link for link, href in candidates if url_parts(href)[:-1] == url_parts(comic_url)[:-1]]
    if len(matches) != 1:
        raise CheckFailure(f'관리 링크 1개 → {comic_url}', [href for _, href in candidates])
    expect(matches[0]).to_have_attribute('target', '_self')
    matches[0].click()
    destination(tab, comic_url, topic, expect, comic=True)


def inspect_controls(tab, url, pages, mobile, theme, expect):
    first, middle, last = pages[0]['id'], pages[len(pages) // 2]['id'], pages[-1]['id']
    topic_url = lambda topic: f'{url}#{quote(topic, safe="")}'
    tab.goto(url, wait_until='domcontentloaded')
    expect(tab.locator('.hero.is-current')).to_be_visible()
    tab.locator('#pager-next').click()
    destination(tab, topic_url(first), first, expect, comic=True)
    if len(pages) > 1:
        second = pages[1]['id']
        tab.keyboard.press('ArrowRight')
        destination(tab, topic_url(second), second, expect, comic=True)
        tab.locator('#pager-prev').click()
        destination(tab, topic_url(first), first, expect, comic=True)
        tab.go_back(wait_until='domcontentloaded')
        destination(tab, topic_url(second), second, expect, comic=True)
    for index in dict.fromkeys((0, len(pages) // 2, len(pages) - 1)):
        if mobile:
            tab.locator('#toggle-left').click()
        tab.locator('#panel-left .toc-list a').nth(index).click()
        topic = pages[index]['id']
        destination(tab, topic_url(topic), topic, expect, comic=True)
        if mobile:
            expect(tab.locator('#toggle-left')).to_have_attribute('aria-expanded', 'false')
    expect(tab.locator('#pager-next')).to_have_text('처음으로')
    tab.locator('#pager-next').click()
    expect(tab.locator('.hero.is-current')).to_be_visible()

    tab.goto(topic_url(middle), wait_until='domcontentloaded')
    right = tab.locator('#toggle-right')
    if mobile:
        right.click()
        expect(tab.locator('#panel-right')).to_have_attribute('role', 'dialog')
        expect(tab.locator('#sum-for .sum:not([hidden])')).to_be_visible()
        tab.keyboard.press('Escape')
        expect(right).to_have_attribute('aria-expanded', 'false')
        tab.locator('#toggle-left').click()
        tab.locator('#panel-scrim').click(position={'x': tab.viewport_size['width'] - 4, 'y': 200})
        expect(tab.locator('#toggle-left')).to_have_attribute('aria-expanded', 'false')
    else:
        for expanded in ('false', 'true'):
            if right.get_attribute('aria-expanded') != expanded:
                right.click()
            expect(right).to_have_attribute('aria-expanded', expanded)
        separator = tab.locator('#panel-left [role="separator"]')
        left = tab.locator('#panel-left')
        before = left.bounding_box()['width']
        separator.press('ArrowRight')
        equal(left.bounding_box()['width'] > before, True)
        separator.press('Home')

    dark = theme == 'dark'
    equal(tab.evaluate("matchMedia('(prefers-color-scheme: dark)').matches"), dark)
    other = 'light' if dark else 'dark'
    toggle = tab.locator('#theme-toggle')
    toggle.click()
    expect(tab.locator('html')).to_have_attribute('data-theme', other)
    tab.reload(wait_until='domcontentloaded')
    expect(tab.locator('html')).to_have_attribute('data-theme', other)
    toggle.click()
    equal(tab.locator('html').get_attribute('data-theme'), None)
    keys = tab.evaluate('Object.keys(localStorage)')
    equal(any(k.startswith('od-comic-read:') for k in keys), True)
    equal(any(k.startswith('od-note-read:') for k in keys), False)


def inspect_page(tab, authored, expect):
    article = tab.locator(topic_selector(authored['id']))
    equal(tab.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), True)
    equal(tab.locator('.content').evaluate('(el) => el.scrollWidth <= el.clientWidth + 1'), True)
    panels = article.locator('.comic-panel')
    if authored['status'] == 'held':
        expect(article.locator('.layer.warn')).to_contain_text(authored['reason'])
        expect(panels).to_have_count(0)
        return
    summary = tab.locator('#sum-for .sum:not([hidden]) .sum-lead')
    expect(summary).to_have_text(authored['summary']['text'])
    expect(panels).to_have_count(len(authored['panels']))
    for index, (panel, data) in enumerate(zip(panels.all(), authored['panels']), 1):
        image = panel.locator('img')
        image.scroll_into_view_if_needed()
        expect(image, f'{index}컷 이미지 로딩').to_have_js_property('complete', True)
        equal(image.evaluate('async img => { await img.decode(); return img.naturalWidth > 0; }'), True)
        expect(panel.locator('figcaption .comic-caption'), f'{index}컷 설명').to_have_text(data['caption'])
        expect(panel.locator('figcaption .comic-dialogue')).to_have_count(0)
        bubbles = panel.locator('.comic-scene .comic-dialogue')
        expect(bubbles).to_have_count(len(data['dialogue']))
        for bubble, line in zip(bubbles.all(), data['dialogue']):
            expect(bubble).to_have_attribute('data-speaker', line['speaker'])
            expect(bubble).to_contain_text(line['text'])
            expect(bubble.locator('.comic-speaker')).to_be_visible()
            readable = bubble.evaluate('''el => {
                const box = el.getBoundingClientRect();
                const scene = el.closest('.comic-scene').getBoundingClientRect();
                const text = document.createRange();
                text.selectNodeContents(el);
                return parseFloat(getComputedStyle(el).fontSize) >= 17 &&
                    box.left >= scene.left - 1 && box.right <= scene.right + 1 &&
                    box.top >= scene.top - 1 && box.bottom <= scene.bottom + 1 &&
                    [...text.getClientRects()].every(r => r.left >= box.left - 1 &&
                        r.right <= box.right + 1 && r.top >= box.top - 1 && r.bottom <= box.bottom + 1);
            }''')
            if not readable:
                raise CheckFailure(f'{index}컷 말풍선 17px 이상, 장면 안에서 잘림 없음', line['text'])
        equal(panel.evaluate('el => el.scrollWidth <= el.clientWidth + 1'), True)


def check_view(tab, inputs, origin, root, view, mode, out, expect, error_type, resources, primary):
    width, height, theme = view
    report = {'width': width, 'height': height, 'theme': theme, 'pages': 0, 'panels': 0,
              'link_round_trips': 0, 'comic_to_source_returns': 0, 'failures': [],
              'panels_by_topic': {}, 'returned_topics': []}
    failures = report['failures']
    external = set()
    comic_base = url_for(origin, root, inputs.comic)
    topic = None

    def record(check, expected, actual):
        failures.append({'topic': topic, 'check': check, 'expected': expected, 'actual': actual, 'url': tab.url})

    def step(check, action, *args, **kwargs):
        try:
            action(*args, **kwargs)
            return True
        except CheckFailure as exc:
            record(check, exc.expected, exc.actual)
        except (AssertionError, error_type) as exc:
            record(check, '브라우저 검사 통과', str(exc))
        return False

    def route_request(route):
        url = route.request.url
        if url.startswith(origin + '/'):
            path = (root / unquote(urlsplit(url).path).lstrip('/')).resolve()
            if path.is_relative_to(inputs.repo) and path not in primary and path.is_file():
                name = path.relative_to(inputs.repo).as_posix()
                try:
                    sha = digest(path.read_bytes())
                    if resources.setdefault(name, sha) != sha:
                        record('local_resource_changed', resources[name], sha)
                except OSError as exc:
                    record('local_resource', '로컬 자원 읽기 성공', str(exc))
            route.continue_()
        else:
            external.add(url)
            route.abort()

    def local_failure(url, reason):
        if url.startswith(origin + '/'):
            record('local_request', '로컬 리소스 로딩 성공', f'{reason}: {url}')

    def console_message(message):
        url = message.location.get('url', '')
        if message.type == 'error' and (not url or url.startswith(origin + '/')) and not message.text.startswith('Failed to load resource:'):
            record('console_error', '콘솔 오류 없음', message.text)

    tab.context.route('**/*', route_request)
    tab.on('pageerror', lambda exc: record('page_error', '페이지 실행 오류 없음', str(exc)))
    tab.on('console', console_message)
    tab.on('requestfailed', lambda req: local_failure(req.url, req.failure) if req.failure != 'net::ERR_ABORTED' else None)
    tab.on('response', lambda response: local_failure(response.url, response.status) if response.status >= 400 else None)

    def go(url, *, comic):
        tab.goto(url, wait_until='domcontentloaded')
        destination(tab, url, topic, expect, comic=comic)

    def back(url):
        tab.go_back(wait_until='domcontentloaded')
        destination(tab, url, topic, expect, comic=True)

    def from_note(note_url, comic_url):
        go(note_url, comic=False)
        click_note(tab, comic_url, topic, expect)

    step('controls', inspect_controls, tab, comic_base, inputs.pages, width < 1024, theme, expect)
    for authored in inputs.pages:
        topic = authored['id']
        comic_url = url_for(origin, root, inputs.comic, topic)
        note_url = url_for(origin, root, inputs.note, topic)
        if not step('comic_page', go, comic_url, comic=True):
            continue
        shown = step('layout', inspect_page, tab, authored, expect)
        if authored['status'] == 'held':
            continue
        if shown:
            report['pages'] += 1
            report['panels'] += len(authored['panels'])
            report['panels_by_topic'][topic] = len(authored['panels'])
        if mode == 'required' and not step('note_to_comic', from_note, note_url, comic_url):
            continue
        if not step('comic_to_note', click_source, tab, note_url, topic, expect):
            continue
        if mode == 'required':
            report['link_round_trips'] += 1
            report['returned_topics'].append(topic)
        elif step('history_back', back, comic_url):
            report['comic_to_source_returns'] += 1
            report['returned_topics'].append(topic)
            if mode == 'history':
                report['link_round_trips'] += 1

    sample = next(page for page in inputs.pages if page['status'] == 'ready')
    topic = sample['id']
    shot = f'{width}x{height}-{theme}.png'

    def screenshot():
        go(url_for(origin, root, inputs.comic, topic), comic=True)
        image = tab.locator(f'{topic_selector(topic)} .comic-panel img').first
        image.scroll_into_view_if_needed()
        image.evaluate('img => img.decode()')
        tab.locator('.content').evaluate('el => el.scrollTo(0, 0)')
        tab.screenshot(path=str(out / shot), animations='disabled')

    report['screenshot'] = shot if step('screenshot', screenshot) else None
    if report['screenshot']:
        report['screenshot_sha256'] = digest((out / shot).read_bytes())
    report['external_requests_blocked'] = sorted(external)
    return report


def browser_check(run, stage, out, *, comic_only=False):
    run = run.resolve()
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError('브라우저 증거는 비어 있는 --out 폴더에 저장하세요.')
    if comic_only and stage != 'published':
        raise ValueError('--comic-only는 --stage published에서 사용하세요.')
    mode = 'comic-only' if comic_only else 'required' if stage == 'published' else 'history'
    report_path = out / 'report.json'
    report = {'schema_version': 2, 'stage': stage, 'link_mode': mode, 'run': str(run),
              'note_to_comic': 'required' if mode == 'required' else 'skipped',
              'views': [], 'failures': [], 'report': str(report_path)}
    resources = {}
    version = None
    publication = None
    try:
        if stage == 'published':
            publication = read(run / 'publication.json')
            candidate = existing(publication['version'])
            if read(candidate / 'publication.json') == publication:
                version = candidate
            if comic_only and version and (version / LINK_RECORD).is_file():
                if read(version / LINK_RECORD)['status'] != 'skipped':
                    raise ValueError('--comic-only는 원본 연결을 생략한 발행에 사용하세요.')
        inputs = inputs_for(run, stage)
        before = inputs.hashes()
        report['input_hashes'] = before
        primary = {inputs.comic, inputs.note, *inputs.images.values()}
        report['inputs'] = {
            'comic': {'path': str(inputs.comic), 'sha256': before['files']['comic']},
            'note': {'path': str(inputs.note), 'sha256': before['files']['note']},
            'images': before['images'],
        }
        report['source_status'] = inputs.source_status
        report['checker_sha256'] = before['files']['checker']
        if inputs.note_link_error:
            report['failures'].append({'check': 'note_link_integrity', 'expected': '유효한 원본 관리 링크 블록',
                                       'actual': inputs.note_link_error})
        report['held'] = [{'id': page['id'], 'reason': page['reason']}
                          for page in inputs.pages if page['status'] == 'held']
        try:
            from playwright.sync_api import Error, expect, sync_playwright
        except ImportError as exc:
            raise ValueError('Playwright가 필요합니다. python3 -m pip install playwright 실행 후 Chromium을 설치하세요.') from exc
        expect.set_options(timeout=TIMEOUT)
        try:
            with serve(inputs) as (origin, root), sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                report['browser'] = {'engine': 'chromium', 'version': browser.version,
                                     'playwright': package_version('playwright')}
                for view in VIEWS:
                    width, height, theme = view
                    context = browser.new_context(viewport={'width': width, 'height': height},
                                                  color_scheme=theme, reduced_motion='reduce',
                                                  service_workers='block')
                    try:
                        tab = context.new_page()
                        tab.set_default_timeout(TIMEOUT)
                        tab.set_default_navigation_timeout(TIMEOUT)
                        report['views'].append(check_view(tab, inputs, origin, root, view, mode, out,
                                                         expect, Error, resources, primary))
                    finally:
                        context.close()
                browser.close()
        except Error as exc:
            raise ValueError(f'Chromium 실행 오류. 설치 확인은 python3 -m playwright install chromium. {exc}') from exc
        if inputs.hashes() != before:
            raise ValueError('브라우저 검사 도중 입력 파일이 바뀌었습니다. 다시 실행하세요.')
        require_current_resources(inputs.repo, resources)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        report['failures'].append({'check': 'run', 'expected': '검사 입력과 환경 정상', 'actual': str(exc)})
    passed = len(report['views']) == len(VIEWS) and not report['failures'] and not any(
        view['failures'] for view in report['views']
    )
    report['status'] = 'passed' if passed else 'failed'
    report['local_resources'] = resources
    write_atomic(report_path, report)
    if stage == 'preview':
        write_atomic(run / PREVIEW_RECORD, {'report': str(report_path), 'sha256': digest(report_path.read_bytes())})
    elif version and not comic_only and read(version / 'publication.json') == publication:
        archived_report, report_sha = preserve_published_report(version, report_path, report)
        save_link_status(version, report['status'], stage='browser', report=archived_report,
                         report_sha256=report_sha, input_hashes=report.get('input_hashes'),
                         local_resources=resources)
    return report
