import os
import re
import unittest

# ─── 생성 파라미터 (scripts/new_note_test.py 가 채움. 손으로 고쳐도 됨) ───
MMDD = "0917"
MULTI = False
QUIZ = {1, 2, 3, 5, 7, 11, 14, 18, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 34, 36, 37, 38, 40}
SCOPE_TERMS = ['재조합', '교차', '중기II', '무작위적 염색체 분배']
REQUIRED_SECTIONS = ['## ⏱ 30초 요약', '## ✂️', '## 📎 강의 밖 보충', '## 부록. 문항 ↔ 개념 매핑']
PRIOR = None
# MULTI: True 면 퀴즈 항목마다 src:"N강" 이 있어야 하고 QUIZ 는 (src, n) 쌍 집합.
# ────────────────────────────────────────────────────────────────────────

REPO_ROOT = os.environ.get("NOTE_REPO_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."))
MD_PATH = os.path.join(REPO_ROOT, "정리노트", MMDD + ".md")
HTML_PATH = os.path.join(REPO_ROOT, "정리노트", MMDD + ".html")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestArtifactsExist(unittest.TestCase):
    def test_markdown_and_html_exist(self):
        self.assertTrue(os.path.isfile(MD_PATH), MD_PATH + " 가 없습니다.")
        self.assertTrue(os.path.isfile(HTML_PATH), HTML_PATH + " 가 없습니다.")


def _body(md):
    """본문 영역만. ✂️ · 📎 · 부록은 다음 회차 개념이 이름으로 나오는 게 정상이라 제외."""
    idxs = [md.find(m) for m in ("## ✂️", "## 📎", "## 부록") if md.find(m) >= 0]
    return md[:min(idxs)] if idxs else md


def _md_quiz_set(md):
    if MULTI:
        rows = re.findall(r"^\|\s*(\d+강)\s*\|\s*(\d+)\s*\|", md, re.M)
        return {(s, int(n)) for s, n in rows}
    return {int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|", md, re.M)}


def parse_question_data(html):
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


def _html_quiz_set(html):
    data = parse_question_data(html)
    if data is not None:
        if MULTI:
            return {(item["src"], item["n"]) for item in data[1] if "src" in item and "n" in item}
        return {item["n"] for item in data[1] if "n" in item}
    if MULTI:
        pairs = re.findall(r'\bn:\s*(\d+)\s*,\s*src:\s*"([^"]+)"', html)
        return {(s, int(n)) for n, s in pairs}
    return {int(n) for n in re.findall(r"\bn:\s*(\d+)", html)}


def _html_item_count(html):
    data = parse_question_data(html)
    if data is not None:
        return len(data[1])
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
        for bad in ["fetch(", "XMLHttpRequest", "<script src=", "<link rel=\"stylesheet\"",
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


if __name__ == "__main__":
    unittest.main()
