"""Inventory original topic screens and stable, page-local evidence (stdlib only)."""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
import hashlib
import html
from pathlib import Path
import re
import unicodedata

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
BLOCKS = set('p li dt dd td th blockquote'.split())
SKIP = {'script', 'style', 'svg', 'button', 'noscript'}


def nfc(value):
    return unicodedata.normalize('NFC', str(value))


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def existing(path):
    path = Path(path).absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        matches = [p for p in current.iterdir() if nfc(p.name) == nfc(part)] if current.is_dir() else []
        if len(matches) != 1:
            raise ValueError(f'경로 없음 또는 모호함: {path}')
        current = matches[0]
    return current.resolve()


def resolve(repo, target):
    repo = existing(repo)
    target = nfc(target)
    if target.lower().endswith('.html'):
        path = Path(target)
        path = existing(path if path.is_absolute() else repo / path)
        if not path.is_relative_to(repo) or not path.is_file():
            raise ValueError('정리노트는 저장소 안 HTML이어야 합니다.')
        return path
    if not re.fullmatch(r'\d{4}(?:-\d{4})?', target):
        raise ValueError('날짜(MMDD), 기존 범위 폴더명 또는 정리노트 HTML 경로를 지정하세요.')
    root = existing(repo / '복습노트')
    candidates = []
    for folder in root.iterdir():
        if not folder.is_dir():
            continue
        bounds = folder.name.split('-')
        matches = folder.name == target or ('-' not in target and len(bounds) == 2 and bounds[0] <= target <= bounds[1])
        if matches:
            candidates.extend(p for p in folder.iterdir() if re.fullmatch(r'정리노트_.*\.html', nfc(p.name)))
    if not candidates:
        available = ', '.join(sorted(p.name for p in root.iterdir() if p.is_dir() and re.fullmatch(r'\d{4}(?:-\d{4})?', p.name)))
        raise ValueError(f'대상 정리노트 없음: {target}. 사용 가능한 폴더: {available}')
    if len(candidates) != 1:
        raise ValueError('여러 후보: HTML 경로를 지정하세요.\n' + '\n'.join(map(str, candidates)))
    return candidates[0].resolve()


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    parent: Node | None = None

    @property
    def classes(self):
        return set(self.attrs.get('class', '').split())

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.walk()

    def text(self):
        if self.tag in SKIP:
            return ''
        return ' '.join(c if isinstance(c, str) else c.text() for c in self.children)

    def ancestors(self):
        current = self.parent
        while current:
            yield current
            current = current.parent


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict((k, v or '') for k, v in attrs), parent=self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, dict((k, v or '') for k, v in attrs), parent=self.current))

    def handle_endtag(self, tag):
        current = self.current
        while current.parent and current.tag != tag:
            current = current.parent
        if current.parent:
            self.current = current.parent

    def handle_data(self, data):
        self.current.children.append(data)


def parse(text):
    parser = Parser()
    parser.feed(text)
    return parser.root


def compact(text):
    return re.sub(r'\s+', ' ', nfc(text)).strip()


def outer(node):
    if isinstance(node, str):
        return html.escape(node, quote=False)
    attrs = ''.join(f' {k}="{html.escape(v, quote=True)}"' for k, v in node.attrs.items())
    start = f'<{node.tag}{attrs}>'
    return start if node.tag in VOID else start + ''.join(outer(c) for c in node.children) + f'</{node.tag}>'


def inventory(path, repo, selection=None, raw=None, review_version=None):
    path, repo = (existing(path), existing(repo)) if raw is None else (Path(path), Path(repo))
    from comic_links import strip_links
    raw_bytes = path.read_bytes() if raw is None else raw
    raw = strip_links(raw_bytes.decode('utf-8'))
    root = parse(raw)
    body = next((n for n in root.walk() if n.tag == 'body'), None)
    main = next((n for n in root.walk() if n.tag == 'main'), None)
    if not body or not main:
        raise ValueError('정리노트 본문(main/body) 없음')
    topics, seen = [], set()
    for node in main.walk():
        if node.tag != 'article' or 'topic' not in node.classes:
            continue
        tid = node.attrs.get('id', '')
        if not re.fullmatch(r'[A-Za-z][\w:.-]*', tid) or tid in seen:
            raise ValueError(f'토픽 ID 누락·중복·잘못된 값: {tid}')
        seen.add(tid)
        heading = next((n for n in node.walk() if n.tag == 'h3'), None)
        title = compact(heading.text()) if heading else ''
        if not title:
            raise ValueError(f'토픽 제목 없음: {tid}')
        reason = ''
        if tid.endswith('-next') or re.fullmatch(r'다음 (?:시간|수업) 예고', title):
            reason = '미학습 범위 예고'
        elif tid.endswith('-links') or title == '함께 보면 좋은 자료':
            reason = '자료 링크 안내'
        if not reason and selection and tid not in selection:
            reason = '명시적 단일 페이지 제작 범위 밖'
        evidence = []
        for block in node.walk():
            ancestors = list(block.ancestors())
            if block.tag not in BLOCKS or any(n.tag in SKIP or 'sum' in n.classes or 'tags' in n.classes for n in ancestors):
                continue
            if any(n.tag in BLOCKS for n in block.walk()):
                continue
            text = compact(block.text())
            if not text:
                continue
            supplement = next((n for n in ancestors if 'layer' in n.classes and 'supp' in n.classes), None)
            label = next((compact(n.text()) for n in supplement.walk() if 'badge' in n.classes), '보충') if supplement else ''
            layer = next((sorted(n.classes - {'layer'}) for n in ancestors if 'layer' in n.classes), [])
            evidence.append({'id': f'{tid}:e{len(evidence) + 1:03}', 'text': text, 'scope': 'supplement' if supplement else 'lesson', 'label': label, 'layer': layer})
        if not reason and not evidence:
            raise ValueError(f'학습 본문 근거 없음: {tid}. 자동 제외하지 않습니다. 원본을 확인하세요.')
        section = next((n for n in node.ancestors() if n.tag == 'section'), None)
        sec_title = next((compact(n.text()) for n in section.children if isinstance(n, Node) and n.tag == 'h2'), '') if section else ''
        summary = next((n for n in node.children if isinstance(n, Node) and 'sum' in n.classes), None)
        topics.append({'id': tid, 'title': title, 'section': section.attrs.get('id', '') if section else 'topics', 'section_title': sec_title or '학습 내용', 'include': not bool(reason), 'reason': reason, 'sha256': digest(outer(node)), 'body_html': outer(node), 'summary_text': compact(summary.text()) if summary else '', 'evidence': evidence})
    if not topics or not any(t['include'] for t in topics):
        raise ValueError('만화로 만들 학습 토픽 없음')
    if selection and any(s not in seen for s in selection):
        raise ValueError('선택한 원본 페이지 없음')
    title = next((compact(n.text()) for n in main.walk() if n.tag == 'h1'), path.stem)
    result = {'schema_version': 2, 'selection': selection or [], 'content_sha256': digest(raw), 'repo': str(repo), 'path': str(path), 'sha256': digest(raw_bytes), 'title': title, 'range': body.attrs.get('data-range') or path.parent.name, 'topics': topics}
    if review_version is not None:
        result['review_version'] = review_version
    return result
