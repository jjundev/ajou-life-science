#!/usr/bin/env python3
"""회차 노트 검증 테스트 생성기.

    python3 scripts/new_note_test.py 0910 --quiz 7,8,11 --scope-terms 세포골격,확산 --prior 0908
    python3 scripts/new_note_test.py 0910 --quiz "1강:32,40" --quiz "2강:1,2" --prior 0908

--quiz 는 여러 번 줄 수 있다. 'N강:' 접두가 하나라도 있으면 다중 출처 모드이고,
그때는 모든 --quiz 에 접두가 있어야 한다.

산출 파일은 tests/test_note_MMDD.py. 이미 있으면 --force 없이는 거부한다.
생성된 테스트는 NOTE_REPO_ROOT 환경변수로 저장소 루트를 덮어쓸 수 있다
(자체 테스트가 임시 fixture 에 대해 돌리기 위함).
"""
import argparse
import os
import re
import string
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUIZ_SPEC_RE = re.compile(r"^(?:(\d+강):)?(\d+(?:,\d+)*)$")

# Shared source keeps generated tests standalone and free of bank dependencies.
PARSER_SOURCE = r'''def parse_question_data(html):
    """Read a marked JSON data block, or return None for legacy JS literals."""
    import json
    start, end = '/* QUESTION-DATA-START */', '/* QUESTION-DATA-END */'
    if start not in html and end not in html:
        return None
    if html.count(start) != 1 or html.count(end) != 1 or html.index(start) >= html.index(end):
        raise ValueError('expected exactly one ordered question data marker pair')
    rest = html[html.index(start) + len(start):html.index(end)].strip()
    values = []
    for name in ('META', 'QUIZ'):
        match = re.match(r'const\s+' + name + r'\s*=\s*', rest)
        if not match:
            raise ValueError('missing JSON declaration: ' + name)
        value, offset = json.JSONDecoder().raw_decode(rest[match.end():])
        rest = rest[match.end() + offset:].lstrip()
        if not rest.startswith(';'):
            raise ValueError('missing declaration terminator: ' + name)
        rest = rest[1:].lstrip()
        values.append(value)
    if rest or not isinstance(values[0], dict) or not isinstance(values[1], list):
        raise ValueError('invalid question data shape or trailing code')
    if any(not isinstance(item, dict) for item in values[1]):
        raise ValueError('QUIZ items must be objects')
    return tuple(values)


def html_quiz_qids(html):
    """Keep full source-qualified IDs and duplicates for exact scope checks."""
    data = parse_question_data(html)
    if data is None:
        return []
    qids = [item['qid'] for item in data[1] if 'qid' in item]
    if any(not isinstance(qid, str) or not qid for qid in qids):
        raise ValueError('qid must be a nonempty string')
    return qids
'''
exec(PARSER_SOURCE)

TEMPLATE = string.Template(r'''import os
import re
import unittest

# ─── 생성 파라미터 (scripts/new_note_test.py 가 채움. 손으로 고쳐도 됨) ───
MMDD = "$MMDD"
MULTI = $MULTI
QUIZ = $QUIZ
SCOPE_TERMS = $SCOPE_TERMS
REQUIRED_SECTIONS = $REQUIRED_SECTIONS
PRIOR = $PRIOR
$WEB_CONSTANTS# MULTI: True 면 퀴즈 항목마다 src:"N강" 이 있어야 하고 QUIZ 는 (src, n) 쌍 집합.
# ────────────────────────────────────────────────────────────────────────

REPO_ROOT = os.environ.get("NOTE_REPO_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."))
MD_PATH = os.path.join(REPO_ROOT, "정리노트", MMDD + ".md")
HTML_PATH = os.path.join(REPO_ROOT, "정리노트", MMDD + ".html")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _body(md):
    """본문 영역만. ✂️ · 📎 · 부록은 다음 회차 개념이 이름으로 나오는 게 정상이라 제외."""
    idxs = [md.find(m) for m in ("## ✂️", "## 📎", "## 부록") if md.find(m) >= 0]
    return md[:min(idxs)] if idxs else md


def _md_quiz_set(md):
    if MULTI:
        rows = re.findall(r"^\|\s*(\d+강)\s*\|\s*(\d+)\s*\|", md, re.M)
        return {(s, int(n)) for s, n in rows}
    return {int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|", md, re.M)}


$PARSER_SOURCE

def _html_quiz_set(html):
    data = parse_question_data(html)
    if data is not None:
$WEB_ITEM_FILTER        if MULTI:
            return {(item["src"], item["n"]) for item in data[1] if "src" in item and "n" in item}
        return {item["n"] for item in data[1] if "n" in item}
    if MULTI:
        pairs = re.findall(r'\bn:\s*(\d+)\s*,\s*src:\s*"([^"]+)"', html)
        return {(s, int(n)) for n, s in pairs}
    return {int(n) for n in re.findall(r"\bn:\s*(\d+)", html)}


def _html_item_count(html):
    data = parse_question_data(html)
    if data is not None:
$WEB_ITEM_FILTER        return len(data[1])
    return len(re.findall(r"\bn:\s*\d+", html))


class TestNoteMarkdown(unittest.TestCase):
    """MMDD.md 가 본문 SSOT 역할과 회차 경계 규칙을 지키는지"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(MD_PATH):
            raise unittest.SkipTest(MD_PATH + " 가 아직 없습니다.")
        cls.md = _read(MD_PATH)

    def test_mapping_table_matches_quiz_set(self):
        """부록 매핑표가 이번 회차 퀴즈 집합과 정확히 일치하는지"""
        self.assertEqual(_md_quiz_set(self.md), QUIZ)

    def test_no_answers_in_markdown(self):
        """답은 html 전용 — md에 보기 원문자가 나타나면 분업 규칙 위반"""
        leaks = re.findall(r"[➀-➄]|[①-⑤]", self.md)
        self.assertEqual(leaks, [], "md에 보기 기호가 있습니다: " + str(set(leaks)))

    def test_no_out_of_scope_content(self):
        """회차 경계 — 다음 회차 개념이 본문에 당겨져 오지 않았는지"""
        body = _body(self.md)
        for term in SCOPE_TERMS:
            self.assertNotIn(term, body, "본문에 다음 회차 개념 '" + term + "' 이 있습니다")

    def test_has_required_sections(self):
        """규칙이 요구하는 구조 블록이 모두 있는지"""
        for marker in REQUIRED_SECTIONS:
            self.assertIn(marker, self.md, "'" + marker + "' 섹션이 없습니다")

    def test_links_to_html_and_prior_notes(self):
        """md에서 html 및 직전 회차로 가는 동선이 있는지"""
        self.assertIn(MMDD + ".html", self.md)
        if PRIOR:
            self.assertIn(PRIOR + ".md", self.md)


class TestNoteHtml(unittest.TestCase):
    """MMDD.html 이 퀴즈 SSOT 역할과 단일 파일 제약을 지키는지"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(HTML_PATH):
            raise unittest.SkipTest(HTML_PATH + " 이 아직 없습니다.")
        cls.html = _read(HTML_PATH)

    def test_quiz_covers_exactly_this_lecture(self):
        """퀴즈 문항 집합이 이번 회차 집합과 정확히 일치하는지 (다중 모드는 src 누락도 잡음)"""
        got = _html_quiz_set(self.html)
        if MULTI:
            self.assertEqual(len(got), _html_item_count(self.html),
                             "src 가 빠진 퀴즈 항목이 있습니다")
        self.assertEqual(got, QUIZ)

    def test_single_file_no_external_deps(self):
        """file:// 에서 열리려면 외부 의존이 없어야 함"""
$RESOURCE_CHECK        for bad in ["fetch(", "XMLHttpRequest", "<script src=", "<link rel=\"stylesheet\"",
                    "cdn.", "http://", "https://", ".png", ".jpg", ".svg\""]:
            self.assertNotIn(bad, self.html, "외부 의존 '" + bad + "' 이 있습니다")

    def test_every_question_has_answer_and_reason(self):
        """근거 없는 정답표 금지 — 모든 문항에 answer·why·ref 가 붙어 있는지"""
        data = parse_question_data(self.html)
        if data is not None:
            for item in data[1]:
                for key in ("n", "answer", "why", "ref"):
                    self.assertIn(key, item)
            return
        n_items = _html_item_count(self.html)
        self.assertEqual(len(re.findall(r"\bwhy:", self.html)), n_items)
        self.assertEqual(len(re.findall(r"\bref:", self.html)), n_items)
        self.assertEqual(len(re.findall(r"\banswer:", self.html)), n_items)


class TestCrossReferences(unittest.TestCase):
    """두 파일 사이 참조 정합성"""

    @classmethod
    def setUpClass(cls):
        if not (os.path.isfile(MD_PATH) and os.path.isfile(HTML_PATH)):
            raise unittest.SkipTest("두 파일이 모두 있어야 검증할 수 있습니다.")
        cls.md = _read(MD_PATH)
        cls.html = _read(HTML_PATH)

    def test_html_refs_point_to_real_md_sections(self):
        """html의 ref 문자열이 md에 실제로 존재하는 절인지"""
        refs = set(re.findall(r'ref:\s*"([^"]+)"', self.html))
        data = parse_question_data(self.html)
        if data is not None:
            refs = {item["ref"] for item in data[1] if "ref" in item and not item.get("qid")}
        for ref in refs:
            if ref.startswith("📎") or (PRIOR and ref.startswith(PRIOR + ".md")):
                continue
            self.assertIn(ref, self.md, "html의 ref '" + ref + "' 가 md에 없습니다")

    def test_html_does_not_duplicate_body_text(self):
        """html이 본문을 복사하지 않았는지 — 본문 장문 문장이 html에 나타나면 위반"""
        body = _body(self.md)
        long_lines = [ln.strip() for ln in body.splitlines()
                      if len(ln.strip()) >= 40
                      and not ln.strip().startswith(("|", "#", ">", "-", "`"))]
        for line in long_lines:
            self.assertNotIn(line, self.html, "html이 md 본문을 복사했습니다: " + line[:40])


${WEB_TESTS}if __name__ == "__main__":
    unittest.main()
''')


def parse_quiz_specs(specs):
    """['7,8'] -> (False, [(None,7),(None,8)]) / ['1강:32,40','2강:1'] -> (True, [('1강',32),…])"""
    items, prefixed = [], []
    for spec in specs:
        m = QUIZ_SPEC_RE.match(spec.strip())
        if not m:
            raise ValueError("--quiz 형식 오류: %r (예: 7,8,11 또는 1강:32,40)" % spec)
        src, nums = m.group(1), [int(x) for x in m.group(2).split(",")]
        prefixed.append(src is not None)
        items.extend((src, n) for n in nums)
    if any(prefixed) and not all(prefixed):
        raise ValueError("단일 출처(7,8)와 다중 출처(1강:7,8) 형식을 섞을 수 없습니다")
    return all(prefixed), items


def _quiz_literal(multi, items):
    if not items:
        return "set()"
    if multi:
        parts = ['("%s", %d)' % (s, n) for s, n in sorted(set(items))]
    else:
        parts = [str(n) for n in sorted({n for _, n in items})]
    return "{" + ", ".join(parts) + "}"


def _web_generated_parts(entries):
    if entries is None:
        return '', '', '', ''
    expected = {
        entry['id']: {
            'bank_id': entry['bank_id'],
            'status': entry['status'],
            'refs': entry['refs'],
        }
        for entry in entries
    }
    active = [entry['id'] for entry in entries if entry['status'] in ('included', 'review')]
    constants = 'WEB_SCOPE = ' + repr({'questions': expected, 'active': active}) + '\n'
    resource_check = r'''        from html.parser import HTMLParser
        class ResourceParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.resources = []
            def handle_starttag(self, tag, attrs):
                values = dict(attrs)
                resource_attrs = {
                    'script': ('src',), 'link': ('href',), 'base': ('href',),
                    'img': ('src', 'srcset'), 'source': ('src', 'srcset'),
                    'video': ('src', 'poster'), 'audio': ('src',), 'track': ('src',),
                    'iframe': ('src',), 'embed': ('src',), 'object': ('data',),
                    'input': ('src',), 'image': ('href', 'xlink:href'),
                    'use': ('href', 'xlink:href'), 'feimage': ('href', 'xlink:href'),
                }
                for attr in resource_attrs.get(tag, ()):
                    if values.get(attr):
                        self.resources.append((tag, attr, values[attr]))
                if values.get('background'):
                    self.resources.append((tag, 'background', values['background']))
                if (tag == 'meta' and values.get('http-equiv', '').lower() == 'refresh'
                        and values.get('content')):
                    self.resources.append((tag, 'content', values['content']))
        parser = ResourceParser()
        parser.feed(self.html)
        self.assertEqual(parser.resources, [], 'external resource elements: ' + repr(parser.resources))
        for pattern in (r'\bfetch\s*\(', r'\bXMLHttpRequest\s*\(', r'\bWebSocket\s*\(',
                        r'\bEventSource\s*\(', r'@import\b', r'url\s*\('):
            self.assertIsNone(re.search(pattern, self.html),
                              "external dependency pattern '" + pattern + "' exists")
        return
'''
    item_filter = "        data = (data[0], [item for item in data[1] if not item.get('qid')])\n"
    tests = r'''class TestWebQuestionScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.path.isfile(MD_PATH) and os.path.isfile(HTML_PATH)):
            raise unittest.SkipTest("both note files are required")
        cls.md = _read(MD_PATH)
        cls.html = _read(HTML_PATH)

    def test_html_uses_each_active_full_qid_once(self):
        qids = html_quiz_qids(self.html)
        self.assertEqual(qids, WEB_SCOPE['active'])
        self.assertEqual(len(qids), len(set(qids)), 'duplicate web qid in HTML')

    def test_markdown_web_table_classifies_every_original_qid(self):
        rows, in_table = [], False
        for line in self.md.splitlines():
            if not line.lstrip().startswith('|'):
                if in_table and rows:
                    break
                continue
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if cells == ['출처', '문항 ID', '질문 요약', '절', '상태']:
                in_table = True
                continue
            if not in_table or all(re.fullmatch(r':?-+:?', cell) for cell in cells):
                continue
            self.assertEqual(len(cells), 5, 'web mapping row must have five columns')
            rows.append(cells)
        qids = [row[1] for row in rows]
        self.assertEqual(set(qids), set(WEB_SCOPE['questions']), 'web mapping qid set mismatch')
        self.assertEqual(len(qids), len(set(qids)), 'duplicate web mapping qid')
        for source, qid, summary, section, status in rows:
            expected = WEB_SCOPE['questions'][qid]
            self.assertEqual(source, expected['bank_id'])
            self.assertTrue(summary, 'web mapping question summary is empty: ' + qid)
            self.assertEqual(status, expected['status'])
            expected_section = expected['refs'][0]['section'] if expected['refs'] else ''
            self.assertEqual(section, expected_section)

    def test_web_refs_are_local_files_with_real_sections(self):
        from pathlib import Path
        from urllib.parse import unquote, urlsplit
        data = parse_question_data(self.html)
        self.assertIsNotNone(data)
        items = {item['qid']: item for item in data[1] if item.get('qid')}
        self.assertEqual(set(items), set(WEB_SCOPE['active']))
        for qid in WEB_SCOPE['active']:
            expected_refs = WEB_SCOPE['questions'][qid]['refs']
            actual_refs = items[qid].get('refs', [])
            self.assertEqual(len(actual_refs), len(expected_refs))
            for actual, expected in zip(actual_refs, expected_refs):
                self.assertEqual({k: actual[k] for k in ('path', 'section')}, expected)
                parsed = urlsplit(actual.get('href', ''))
                self.assertFalse(parsed.scheme or parsed.netloc, 'web ref must be local: ' + actual.get('href', ''))
                target = (Path(HTML_PATH).parent / unquote(parsed.path)).resolve()
                scope_root = Path(os.environ.get('WEB_SCOPE_REPO_ROOT') or REPO_ROOT).resolve()
                declared = (scope_root / expected['path']).resolve()
                self.assertEqual(target, declared, 'web ref href points to a different local file')
                self.assertTrue(target.is_file(), 'web ref file missing: ' + str(target))
                headings = {m.group(1).strip() for m in re.finditer(
                    r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$', _read(str(target)), re.M)}
                self.assertIn(expected['section'], headings)
                anchor = re.sub(r'[^\w\- ]', '', expected['section'].lower()).replace(' ', '-')
                self.assertEqual(unquote(parsed.fragment), anchor)


'''
    return constants, resource_check, tests, item_filter


def render(mmdd, multi, items, scope_terms, prior, supplement, recap=True, web_scope=None):
    required = ["## ⏱ 30초 요약"]
    if recap:
        required.append("## ⏪ 지난 회차 복습")
    required.append("## ✂️")
    if supplement:
        required.append("## 📎 강의 밖 보충")
    required.append("## 부록. 문항 ↔ 개념 매핑")
    web_constants, resource_check, web_tests, web_item_filter = _web_generated_parts(web_scope)
    return TEMPLATE.substitute(
        PARSER_SOURCE=PARSER_SOURCE,
        MMDD=mmdd,
        MULTI=repr(bool(multi)),
        QUIZ=_quiz_literal(multi, items),
        SCOPE_TERMS=repr(list(scope_terms)),
        REQUIRED_SECTIONS=repr(required),
        PRIOR=repr(prior),
        WEB_CONSTANTS=web_constants,
        RESOURCE_CHECK=resource_check,
        WEB_TESTS=web_tests,
        WEB_ITEM_FILTER=web_item_filter,
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="회차 노트 검증 테스트 생성기")
    ap.add_argument("mmdd", help="회차 날짜 MMDD (예: 0910)")
    ap.add_argument("--quiz", action="append", default=[],
                    help="이번 회차 문항. '7,8,11' 또는 '1강:32,40' (반복 가능)")
    ap.add_argument("--web-scope", help="원본 웹 문항 범위 명세 JSON")
    ap.add_argument("--scope-terms", default="",
                    help="본문에 있으면 안 되는 다음 회차 개념, 쉼표 구분")
    ap.add_argument("--prior", default=None, help="직전 회차 MMDD (⏪ 링크·ref 예외)")
    ap.add_argument("--supplement", action="store_true", help="📎 강의 밖 보충 섹션을 필수로")
    ap.add_argument("--no-recap", action="store_true", help="⏪ 지난 회차 복습을 요구하지 않음 (결석 회차)")
    ap.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    ap.add_argument("--out", default=None, help="출력 경로 (기본 tests/test_note_MMDD.py)")
    a = ap.parse_args(argv)

    if not re.fullmatch(r"\d{4}", a.mmdd):
        print("MMDD 는 숫자 4자리여야 합니다: %r" % a.mmdd, file=sys.stderr)
        return 2
    if not a.quiz and not a.web_scope:
        print("--quiz or --web-scope is required", file=sys.stderr)
        return 2
    try:
        multi, items = parse_quiz_specs(a.quiz)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    scope = [t.strip() for t in a.scope_terms.split(",") if t.strip()]
    web_entries, web_banks, web_scope_path = None, None, None
    if a.web_scope:
        try:
            from pathlib import Path
            if REPO_ROOT not in sys.path:
                sys.path.insert(0, REPO_ROOT)
            from scripts.question_bank.scope import load_web_scope
            web_scope_path = Path(a.web_scope).resolve()
            web_entries, web_banks = load_web_scope(web_scope_path, Path(REPO_ROOT))
        except (OSError, UnicodeError, ValueError) as error:
            print(error, file=sys.stderr)
            return 2
    out = a.out or os.path.join(REPO_ROOT, "tests", "test_note_%s.py" % a.mmdd)
    if web_entries is not None:
        try:
            from scripts.question_bank.__main__ import _protect_inputs
            from scripts.question_bank.model import resolve_local
            from scripts.question_bank.scope import protect_paths
            output = Path(out)
            bank_paths = {entry['bank_id']: Path(entry['bank_path']) for entry in web_entries}
            for bank_id, bank in web_banks.items():
                _protect_inputs(bank, bank_paths[bank_id], output)
            refs = [resolve_local(Path(REPO_ROOT), ref['path'])
                    for entry in web_entries for ref in entry['refs']]
            protect_paths(output, [web_scope_path, *refs])
        except (OSError, UnicodeError, ValueError) as error:
            print(error, file=sys.stderr)
            return 2
    if os.path.exists(out) and not a.force:
        print("이미 있습니다: %s  (--force 로 덮어쓰기)" % out, file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(a.mmdd, multi, items, scope, a.prior, a.supplement,
                       recap=not a.no_recap, web_scope=web_entries))
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
