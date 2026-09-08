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
# MULTI: True 면 퀴즈 항목마다 src:"N강" 이 있어야 하고 QUIZ 는 (src, n) 쌍 집합.
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


def _html_quiz_set(html):
    if MULTI:
        pairs = re.findall(r'\bn:\s*(\d+)\s*,\s*src:\s*"([^"]+)"', html)
        return {(s, int(n)) for n, s in pairs}
    return {int(n) for n in re.findall(r"\bn:\s*(\d+)", html)}


def _html_item_count(html):
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


def render(mmdd, multi, items, scope_terms, prior, supplement, recap=True):
    required = ["## ⏱ 30초 요약"]
    if recap:
        required.append("## ⏪ 지난 회차 복습")
    required.append("## ✂️")
    if supplement:
        required.append("## 📎 강의 밖 보충")
    required.append("## 부록. 문항 ↔ 개념 매핑")
    return TEMPLATE.substitute(
        MMDD=mmdd,
        MULTI=repr(bool(multi)),
        QUIZ=_quiz_literal(multi, items),
        SCOPE_TERMS=repr(list(scope_terms)),
        REQUIRED_SECTIONS=repr(required),
        PRIOR=repr(prior),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="회차 노트 검증 테스트 생성기")
    ap.add_argument("mmdd", help="회차 날짜 MMDD (예: 0910)")
    ap.add_argument("--quiz", action="append", required=True,
                    help="이번 회차 문항. '7,8,11' 또는 '1강:32,40' (반복 가능)")
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
    try:
        multi, items = parse_quiz_specs(a.quiz)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    scope = [t.strip() for t in a.scope_terms.split(",") if t.strip()]
    out = a.out or os.path.join(REPO_ROOT, "tests", "test_note_%s.py" % a.mmdd)
    if os.path.exists(out) and not a.force:
        print("이미 있습니다: %s  (--force 로 덮어쓰기)" % out, file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(a.mmdd, multi, items, scope, a.prior, a.supplement, recap=not a.no_recap))
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
