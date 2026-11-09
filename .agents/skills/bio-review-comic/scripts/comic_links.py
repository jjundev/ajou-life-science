"""Byte-preserving contextual note links and narrowly recognized managed blocks."""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import os
import re
from urllib.parse import quote, unquote, urlsplit
import uuid

from comic_source import digest

BLOCK = re.compile(r'\n<!-- bio-comic:v2:([a-f0-9]{64}) -->\n(.*?)\n<!-- /bio-comic -->\n', re.S)
PAYLOAD = re.compile(r'<p class="comic-note" data-bio-comic="([^"]+)">([^<]*)<a href="([^"]+)" target="_self">([^<]+)</a>([^<]*)</p>')


def managed_blocks(text):
    found = []
    for match in BLOCK.finditer(text):
        payload = match[2]
        p = PAYLOAD.fullmatch(payload)
        if digest(payload) != match[1] or not p or p[1] != p[3]:
            raise ValueError('만화 참조 블록 변경 또는 잘못된 형식')
        url = urlsplit(unescape(p[1]))
        if url.scheme or url.netloc or url.query or not url.path.endswith('.html') or not url.fragment:
            raise ValueError('만화 참조 목적지 형식 오류')
        found.append((match, unescape(p[1])))
    remainder = BLOCK.sub('', text)
    if '<!-- bio-comic:' in remainder or '<!-- /bio-comic' in remainder:
        raise ValueError('만화 참조 블록 손상')
    return found


def strip_links(text):
    managed_blocks(text)
    return BLOCK.sub('', text)


class Elements(HTMLParser):
    """Offsets only: never serialize surrounding note HTML."""
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.text, self.nodes, self.stack = text, [], []
        self.lines = [0] + [m.end() for m in re.finditer('\n', text)]
        self.feed(text)

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        from comic_source import VOID
        start = self.position()
        n = {'tag': tag, 'attrs': dict(attrs), 'start': start, 'open_end': start + len(self.get_starttag_text()), 'end': None, 'parent': self.stack[-1] if self.stack else None}
        self.nodes.append(n)
        if tag in VOID: n['end'] = n['open_end']
        else: self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] is self.nodes[-1]:
            self.stack.pop()['end'] = self.nodes[-1]['open_end']

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                self.stack[i]['end'] = self.text.find('>', self.position()) + 1
                del self.stack[i:]
                break


def within(node, parent):
    n = node['parent']
    while n is not None:
        if n is parent: return True
        n = n['parent']
    return False


def block_for(href, spec):
    e = lambda s: escape(s, quote=True)
    payload = f'<p class="comic-note" data-bio-comic="{e(href)}">{e(spec["before"])}<a href="{e(href)}" target="_self">{e(spec["label"])}</a>{e(spec["after"])}</p>'
    return f'\n<!-- bio-comic:v2:{digest(payload)} -->\n{payload}\n<!-- /bio-comic -->\n'


def link_notes(run, dry_run=False):
    from comic_contract import assets_for, check, jobs_for, load, local, raster, read, state, write
    run, src, book = load(run)
    check(run, 'browser')
    record = read(run / 'publication.json')
    target = Path(record['html'])
    if not target.is_file() or digest(target.read_bytes()) != record.get('html_sha256') or record.get('fingerprint') != state(run)['browser']:
        raise ValueError('발행한 만화가 없거나 변경됨. publish 후 연결하세요.')
    from comic_render import validate_output
    validate_output(target)
    for asset in assets_for(run, jobs_for(src, book)).values():
        if raster(local(Path(record['version']), asset['file']))['sha256'] != asset['sha256']:
            raise ValueError('발행 그림 변경: 다시 발행한 뒤 연결하세요.')
    note = Path(src['path'])
    original = note.read_bytes().decode('utf-8')
    text = original
    results = []
    for page in book['pages']:
        pid = page['id']
        result = {'page': pid, 'status': 'skipped'}
        results.append(result)
        if page['status'] != 'ready':
            result['reason'] = 'PAGE_HELD'; continue
        nodes = Elements(text).nodes
        hits = [n for n in nodes if n['attrs'].get('id') == pid]
        if len(hits) != 1 or hits[0]['tag'] != 'article' or not hits[0]['end']:
            result['reason'] = 'SECTION_MISSING_OR_AMBIGUOUS'; continue
        section = hits[0]
        from comic_source import parse
        targets = [n for n in parse(target.read_text(encoding='utf-8')).walk() if n.attrs.get('id') == pid]
        if len(targets) != 1:
            result['reason'] = 'TARGET_PAGE_MISSING_OR_AMBIGUOUS'; continue
        spec = page['note_link']
        children = [n for n in nodes if within(n, section)]
        if spec.get('anchor_id'):
            anchors = [n for n in children if n['attrs'].get('id') == spec['anchor_id']]
            if len(anchors) != 1:
                result['reason'] = 'ANCHOR_MISSING' if not anchors else 'ANCHOR_AMBIGUOUS'; continue
            anchor = anchors[0]
        else:
            def classes(n): return set((n['attrs'].get('class') or '').split())
            anchor = next((n for n in children if {'layer', 'formal'} <= classes(n)), None)
            anchor = anchor or next((n for n in children if {'layer', 'eli5'} <= classes(n)), None)
            anchor = anchor or next((n for n in children if n['tag'] in ('h2', 'h3')), None)
        if not anchor or not anchor['end'] or anchor['tag'] not in ('div', 'figure', 'section', 'h2', 'h3', 'table', 'ul', 'ol', 'blockquote') or any((p is anchor or within(anchor, p)) and (p['tag'] == 'svg' or 'hidden' in p['attrs'] or 'sum' in (p['attrs'].get('class') or '').split()) for p in [section] + children):
            result['reason'] = 'ANCHOR_INVALID'; continue
        href = '/'.join(quote(s, safe='') for s in Path(os.path.relpath(target, note.parent)).parts) + '#' + quote(pid, safe='')
        replacement = block_for(href, spec)
        matches = []
        for m, old_href in managed_blocks(text):
            url = urlsplit(old_href)
            old_path = (note.parent / unquote(url.path)).resolve()
            if section['start'] < m.start() < section['end'] and old_path == target.resolve() and unquote(url.fragment) == pid:
                matches.append(m)
        if matches:
            if len(matches) != 1:
                result['reason'] = 'REFERENCE_AMBIGUOUS'; continue
            m = matches[0]
            result['status'] = 'unchanged' if m[0] == replacement else 'updated'
            text = text[:m.start()] + replacement + text[m.end():]
        else:
            # User-authored links are outside this tool's managed region.
            # Keep their wording and attributes byte-for-byte; add the contextual
            # reference as an independently managed block.
            text = text[:anchor['end']] + replacement + text[anchor['end']:]
            result['status'] = 'added'
        result['href'] = href
    changed = text != original
    if changed and not dry_run:
        # Recheck both lesson content and exact bytes before replacing the note.
        load(run)
        if note.read_bytes() != original.encode('utf-8'):
            raise ValueError('연결 중 원본 변경: 다시 확인 후 실행하세요.')
        temporary = note.with_name('.' + note.name + '.' + uuid.uuid4().hex + '.tmp')
        try:
            temporary.write_bytes(text.encode('utf-8'))
            os.replace(temporary, note)
        finally:
            if temporary.exists(): temporary.unlink()
    result = {'status': 'partial' if any(r['status'] == 'skipped' and r.get('reason') != 'PAGE_HELD' for r in results) else 'complete', 'note': str(note), 'changed': changed, 'dry_run': dry_run, 'results': results}
    if not dry_run: write(run / 'note-links-result.json', result)
    return result
