"""Omit source locators in explanation prose; keep reviewed fragments unchanged."""
import difflib
import html
import re
from html.parser import HTMLParser

NUMBER = r'\d+(?:[.·~–—-]\d+)*'
PAGE = rf'(?:pp?\.?\s*{NUMBER}(?:[~–—-]p\.?\s*{NUMBER})?|{NUMBER}\s*쪽)'
SOURCE = r'(?:교재|교과서|강의노트)\s*(?:\d+장\s*)?'
FIGURE = rf'(?:그림|표)\s*{NUMBER}[a-z]?'
# Without a named source, require p./pp. so p53 and p21 remain biological names.
LOCATOR = re.compile(
    rf'STT\s+\d{{4}}(?:\s+(?:L\d+|\d+행))?'
    rf'|(?:\d+(?:\.\d+)+,\s*)?인쇄\s*{PAGE}'
    rf'|{SOURCE}(?:(?:PDF\s*)?{PAGE}(?:\s*[,·]\s*pp?\.\s*{NUMBER})*'
    rf'(?:\s*{FIGURE})?(?:\s+\d+(?:\.\d+){{2,}}(?=\s*[,;]|\s*$))?|{FIGURE}|\d+(?:\.\d+){{1,}})'
    rf'|(?:여기서는\s*)?(?:\d+장\s*)?(?:pp?\.\s*{NUMBER}(?:[~–—-]pp?\.\s*{NUMBER})?|PDF\s*{NUMBER}\s*쪽)(?:\s*{FIGURE})?'
    rf'|{FIGURE}', re.I)
MATH = re.compile(r'(\$\$[\s\S]*?\$\$|(?<!\\)\$[^$\n]*?(?<!\\)\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
PROTECTED = {'code', 'pre', 'script', 'style', 'svg', 'math'}
BLOCK = {'p', 'div', 'li', 'ul', 'ol', 'td', 'th', 'tr', 'figure', 'figcaption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br'}


def _parenthetical(original):
    content = original[1:-1]
    cleaned = LOCATOR.sub('', content)
    if cleaned == content:
        return original
    cleaned = re.sub(r'^[\s,;:·+]+|[\s,;:·+]+$', '', cleaned)
    cleaned = re.sub(r'^[은는의]\s+', '', cleaned)
    cleaned = re.sub(r'\s*[,;·]\s*(?=[,;·])', '', cleaned)
    cleaned = re.sub(r'([,;])[ \t]+', r'\1 ', cleaned)
    if cleaned in ('', '보충', '여기서는', '은', '는', '도 같은 내용'):
        return ''
    return original[0] + cleaned + original[-1]


def _parentheses(text):
    """Process balanced parentheses, including nested citations and line wraps."""
    pairs = {'(': ')', '（': '）'}
    result = []
    start = 0
    index = 0
    while index < len(text):
        if text[index] not in pairs:
            index += 1
            continue
        stack = [pairs[text[index]]]
        end = index + 1
        while end < len(text) and stack:
            if text[end] in pairs:
                stack.append(pairs[text[end]])
            elif text[end] == stack[-1]:
                stack.pop()
            end += 1
        if stack:
            break  # Incomplete parentheses stay intact.
        result.append(text[start:index])
        inside = _parentheses(text[index+1:end-1])
        result.append(_parenthetical(text[index] + inside + text[end-1]))
        start = index = end
    result.append(text[start:])
    return ''.join(result)


def clean_citation_text(text):
    """Clean source parentheses while leaving TeX spans and other prose alone."""
    pieces = MATH.split(text)
    for index in range(0, len(pieces), 2):
        before = pieces[index]
        after = _parentheses(before)
        if after != before:
            after = re.sub(r'[ \t]+(?=[.,;:!?])', '', after)
        pieces[index] = after
    return ''.join(pieces)


def clean_explanation_citations(markup):
    """Delete prose spans only; preserve tags, attributes, source panels and TeX.

    Text runs span inline tags and entities, but stop at block/protected boundaries.
    Mapping characters back to source offsets avoids reserializing the document.
    """
    class Cleaner(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.stack, self.run, self.deleted = [], [], set()
            self.labels = {}
            self.lines = [0, *(m.end() for m in re.finditer('\n', markup))]

        def flush(self):
            text = ''.join(c for c, _, _ in self.run)
            cleaned = clean_citation_text(text)
            prefix = 0
            while prefix < min(len(text), len(cleaned)) and text[prefix] == cleaned[prefix]:
                prefix += 1
            suffix = 0
            while (suffix < min(len(text), len(cleaned)) - prefix
                   and text[-suffix-1] == cleaned[-suffix-1]):
                suffix += 1
            original_mid = text[prefix:len(text)-suffix if suffix else len(text)]
            cleaned_mid = cleaned[prefix:len(cleaned)-suffix if suffix else len(cleaned)]
            matcher = difflib.SequenceMatcher(None, original_mid, cleaned_mid, autojunk=False)
            for kind, a, b, c, d in matcher.get_opcodes():
                if kind == 'equal':
                    continue
                # Cleanup is deletion-only; unfamiliar formatting is kept conservatively.
                if kind != 'delete':
                    self.run.clear()
                    return
            for kind, a, b, _, _ in matcher.get_opcodes():
                if kind == 'delete':
                    for _, start, end in self.run[prefix+a:prefix+b]:
                        self.deleted.update(range(start, end))
            self.run.clear()

        def handle_starttag(self, tag, attrs):
            if tag in BLOCK or tag in PROTECTED:
                self.flush()
            attrs = dict(attrs)
            active, protected = self.stack[-1][1:3] if self.stack else (False, False)
            anchor = self.stack[-1][3] if self.stack else None
            if tag == 'a':
                anchor = len(self.labels)
                self.labels[anchor] = []
            active = active or 'data-explanation' in attrs or 'sum' in (attrs.get('class') or '').split()
            protected = protected or tag in PROTECTED
            if tag not in VOID:
                self.stack.append((tag, active, protected, anchor))

        def handle_startendtag(self, tag, attrs):
            if tag in BLOCK or tag in PROTECTED:
                self.flush()

        def handle_endtag(self, tag):
            if tag in BLOCK or tag in PROTECTED:
                self.flush()
            for index in range(len(self.stack)-1, -1, -1):
                if self.stack[index][0] == tag:
                    del self.stack[index:]
                    break

        def data(self, raw, decoded):
            if not self.stack or not self.stack[-1][1] or self.stack[-1][2]:
                return
            line, column = self.getpos()
            start = self.lines[line-1] + column
            if raw == decoded:
                chars = [(c, start+i, start+i+1) for i, c in enumerate(raw)]
            else:
                chars = [(c, start, start+len(raw)) for c in decoded]
            self.run.extend(chars)
            anchor = self.stack[-1][3]
            if anchor is not None:
                self.labels[anchor].extend(chars)

        def handle_data(self, data):
            self.data(data, data)

        def handle_entityref(self, name):
            raw = '&' + name + ';'
            self.data(raw, html.unescape(raw))

        def handle_charref(self, name):
            raw = '&#' + name + ';'
            self.data(raw, html.unescape(raw))

    parser = Cleaner()
    parser.feed(markup)
    parser.close()
    parser.flush()
    for label in parser.labels.values():
        visible = [(c, start, end) for c, start, end in label if c.strip()]
        if visible and all(start in parser.deleted for _, start, _ in visible):
            for _, start, end in label:
                parser.deleted.difference_update(range(start, end))
    return ''.join(c for index, c in enumerate(markup) if index not in parser.deleted)
