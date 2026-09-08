import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MD_PATH = os.path.join(REPO_ROOT, "정리노트", "0908.md")
HTML_PATH = os.path.join(REPO_ROOT, "정리노트", "0908.html")

# 이번 회차(단백질 4차구조 ~ 세포소기관)로 새로 풀 수 있는 9문항
QUIZ_NUMBERS = {7, 8, 11, 14, 17, 22, 30, 33, 35}


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _body(md):
    """본문 영역만 잘라낸다. ✂️ 이음매 · 📎 보충 · 부록 매핑표는 본문이 아니다.

    이 세 섹션에는 다음 회차 개념이 이름으로 등장하는 것이 정상이므로
    경계 검사에서 제외한다. (0908 은 📎 섹션이 없어 ✂️ 에서 잘린다.)
    """
    idxs = [md.find(m) for m in ("## ✂️", "## 📎", "## 부록") if md.find(m) >= 0]
    return md[:min(idxs)] if idxs else md


class TestNoteMarkdown(unittest.TestCase):
    """0908.md 가 본문 SSOT 역할과 회차 경계 규칙을 지키는지 검증"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(MD_PATH):
            raise unittest.SkipTest("정리노트/0908.md 가 아직 없습니다.")
        cls.md = _read(MD_PATH)

    def test_mapping_table_matches_quiz_set(self):
        """부록 매핑표가 이번 회차로 새로 풀리는 9문항과 정확히 일치하는지"""
        nums = {int(m) for m in re.findall(r"^\|\s*(\d+)\s*\|", self.md, re.M)}
        self.assertEqual(nums, QUIZ_NUMBERS)

    def test_no_answers_in_markdown(self):
        """답은 html 전용 — md에 보기 원문자가 나타나면 분업 규칙 위반"""
        leaks = re.findall(r"[➀-➄]|[①-⑤]", self.md)
        self.assertEqual(leaks, [], f"md에 보기 기호가 있습니다: {set(leaks)}")

    def test_no_out_of_scope_content(self):
        """회차 경계 — 다음 회차(엽록체·세포골격·막수송) 개념이 본문에 없는지.

        엽록체는 세포내공생설 맥락에서 강의에 나왔으므로 본문에 있어도 정상이다.
        여기서 막는 것은 아직 강의하지 않은 세포골격·막수송 개념이다.
        """
        body = _body(self.md)
        for term in ["세포골격", "미세소관", "중간섬유",
                     "확산", "삼투", "능동수송", "촉진확산"]:
            self.assertNotIn(term, body, f"본문에 다음 회차 개념 '{term}' 이 있습니다")

    def test_has_required_sections(self):
        """규칙이 요구하는 구조 블록 (0908 은 강의 밖 내용이 없어 📎 없음)"""
        for marker in ["## ⏱ 30초 요약", "## ⏪ 지난 회차 복습",
                       "## ✂️", "## 부록. 문항 ↔ 개념 매핑"]:
            self.assertIn(marker, self.md, f"'{marker}' 섹션이 없습니다")

    def test_links_to_html_and_prior_notes(self):
        """md에서 html 및 앞선 회차로 가는 동선이 있는지"""
        self.assertIn("0908.html", self.md)
        self.assertIn("0903.md", self.md)  # 이어지는 회차 참조


class TestNoteHtml(unittest.TestCase):
    """0908.html 이 퀴즈 SSOT 역할과 단일 파일 제약을 지키는지 검증"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(HTML_PATH):
            raise unittest.SkipTest("정리노트/0908.html 이 아직 없습니다.")
        cls.html = _read(HTML_PATH)

    def test_quiz_covers_exactly_this_lecture(self):
        """퀴즈 문항 집합이 이번 회차 9문항과 정확히 일치하는지"""
        nums = {int(m) for m in re.findall(r"\bn:\s*(\d+)", self.html)}
        self.assertEqual(nums, QUIZ_NUMBERS)

    def test_single_file_no_external_deps(self):
        """file:// 에서 열리려면 외부 의존이 없어야 함"""
        for bad in ["fetch(", "XMLHttpRequest", "<script src=", "<link rel=\"stylesheet\"",
                    "cdn.", "http://", "https://", ".png", ".jpg", ".svg\""]:
            self.assertNotIn(bad, self.html, f"외부 의존 '{bad}' 이 있습니다")

    def test_every_question_has_answer_and_reason(self):
        """근거 없는 정답표 금지 — 모든 문항에 answer·why·ref 가 붙어 있는지"""
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
            if ref.startswith("📎") or ref.startswith("0903.md"):
                continue  # 보충 및 앞선 회차 참조는 예외
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
