import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MD_PATH = os.path.join(REPO_ROOT, "정리노트", "0903.md")
HTML_PATH = os.path.join(REPO_ROOT, "정리노트", "0903.html")

# 이번 회차 노트로 풀 수 있는 문항 (본문 21 + 경계 2 + 보충 1)
QUIZ_NUMBERS = {
    1, 3, 4, 5, 6, 9, 10, 12, 13, 15, 18, 20, 23, 24, 25, 26, 27, 28, 29,
    31, 34, 36, 37, 38,
}


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _body(md):
    """본문 영역만 잘라낸다.

    ✂️ 이음매 · 📎 보충 · 부록 매핑표는 본문이 아니다. 이 세 섹션에는
    다음 회차 개념이 이름으로 등장하는 것이 정상이므로 경계 검사에서 제외한다.
    문서를 뒤에서부터 짓는 도중(매핑표만 있고 본문이 없는 상태)에도
    올바르게 빈 본문을 돌려준다.
    """
    idxs = [md.find(m) for m in ("## ✂️", "## 📎", "## 부록") if md.find(m) >= 0]
    return md[:min(idxs)] if idxs else md


class TestNoteMarkdown(unittest.TestCase):
    """0903.md 가 본문 SSOT 역할과 회차 경계 규칙을 지키는지 검증"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(MD_PATH):
            raise unittest.SkipTest("정리노트/0903.md 가 아직 없습니다.")
        cls.md = _read(MD_PATH)

    def test_mapping_table_has_40_rows(self):
        """부록 매핑표가 문항 1~40 전체를 빠짐없이 담는지"""
        nums = {int(m) for m in re.findall(r"^\|\s*(\d+)\s*\|", self.md, re.M)}
        self.assertEqual(nums, set(range(1, 41)))

    def test_no_answers_in_markdown(self):
        """답은 html 전용 — md에 보기 기호가 나타나면 분업 규칙 위반

        '답은 0903.html 에 있습니다' 같은 안내 문구는 필요하므로 '정답'이라는
        단어 자체는 막지 않는다. 대신 원문자를 md에서 전면 금지한다.
        답이 새는 형태는 반드시 보기 기호를 동반하므로 이것으로 충분히 잡힌다.
        일반 목록에도 원문자를 쓰지 말고 (1) (2) (3) 을 쓴다.
        """
        leaks = re.findall(r"[➀-➄]|[①-⑤]", self.md)
        self.assertEqual(leaks, [], f"md에 보기 기호가 있습니다: {set(leaks)}")

    def test_no_out_of_scope_content(self):
        """회차 경계 — 다음 회차 개념이 본문에 당겨져 오지 않았는지"""
        body = _body(self.md)
        for term in ["4차 구조", "뉴클레오타이드", "뉴클레오티드",
                     "미토콘드리아", "골지", "리소좀", "촉진확산", "능동수송"]:
            self.assertNotIn(term, body, f"본문에 다음 회차 개념 '{term}' 이 있습니다")

    def test_has_required_sections(self):
        """규칙이 요구하는 구조 블록이 모두 있는지"""
        for marker in ["## ⏱ 30초 요약", "## ⏪ 지난 회차 복습",
                       "## ✂️", "## 📎 강의 밖 보충", "## 부록. 문항 ↔ 개념 매핑"]:
            self.assertIn(marker, self.md, f"'{marker}' 섹션이 없습니다")

    def test_links_to_html(self):
        """md에서 html로 가는 동선이 있는지"""
        self.assertIn("0903.html", self.md)


class TestNoteHtml(unittest.TestCase):
    """0903.html 이 퀴즈 SSOT 역할과 단일 파일 제약을 지키는지 검증"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(HTML_PATH):
            raise unittest.SkipTest("정리노트/0903.html 이 아직 없습니다.")
        cls.html = _read(HTML_PATH)

    def test_quiz_covers_exactly_this_lecture(self):
        """퀴즈 문항 집합이 이번 회차로 풀 수 있는 24문항과 정확히 일치하는지"""
        nums = {int(m) for m in re.findall(r"\bn:\s*(\d+)", self.html)}
        self.assertEqual(nums, QUIZ_NUMBERS)

    def test_single_file_no_external_deps(self):
        """file:// 에서 열리려면 외부 의존이 없어야 함"""
        for bad in ["fetch(", "XMLHttpRequest", "<script src=", "<link rel=\"stylesheet\"",
                    "cdn.", "http://", "https://", ".png", ".jpg", ".svg\""]:
            self.assertNotIn(bad, self.html, f"외부 의존 '{bad}' 이 있습니다")

    def test_every_question_has_answer_and_reason(self):
        """근거 없는 정답표 금지 — 모든 문항에 why 와 ref 가 붙어 있는지"""
        n_items = len(re.findall(r"\bn:\s*\d+", self.html))
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
            if ref.startswith("📎"):
                continue
            self.assertIn(ref, self.md, f"html의 ref '{ref}' 가 md에 없습니다")

    def test_html_does_not_duplicate_body_text(self):
        """html이 본문을 복사하지 않았는지 — 본문 장문 문장이 html에 나타나면 위반"""
        body = _body(self.md)
        long_lines = [ln.strip() for ln in body.splitlines()
                      if len(ln.strip()) >= 40 and not ln.strip().startswith(("|", "#", ">", "-", "`"))]
        for line in long_lines:
            self.assertNotIn(line, self.html,
                             f"html이 md 본문을 복사했습니다: {line[:40]}...")


if __name__ == "__main__":
    unittest.main()
