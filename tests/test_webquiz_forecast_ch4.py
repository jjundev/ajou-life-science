import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "웹과제예상/4장_웹과제예상.html"
SECTION_IDS = ["format", "topics", "mock", "last"]


def raw() -> str:
    return HTML.read_text(encoding="utf-8")


def body() -> str:
    return re.sub(r"<!--.*?-->", "", raw().split("<body", 1)[1], flags=re.S)


def text(html: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", t).strip()


def section(sec_id: str) -> str:
    m = re.search(rf'<section class="sec" id="{sec_id}">(.*?)</section>', body(), re.S)
    if not m:
        raise AssertionError(f"구역 없음: {sec_id}")
    return m.group(1)


class Skeleton(unittest.TestCase):
    def test_title(self):
        self.assertIn("<title>4장 웹과제 예상</title>", raw())

    def test_sections_in_order(self):
        found = re.findall(r'<section class="sec" id="([a-z]+)">', body())
        self.assertEqual(found, SECTION_IDS)

    def test_no_script(self):
        self.assertNotIn("<script", raw())

    def test_theme_tokens(self):
        r = raw()
        self.assertIn("@media (prefers-color-scheme: dark)", r)
        self.assertRegex(r, r"body\s*\{[^}]*background:\s*var\(--bg\)")

    def test_font_fallback(self):
        r = raw()
        self.assertIn("'Malgun Gothic'", r)
        self.assertIn("system-ui", r)


TOPIC_TERMS = [
    "유전 용어", "양성잡종", "성연관", "구조 변형", "비분리", "ABO",
    "불완전우성", "다인자유전", "연관·재조합", "이수성", "2/3", "가계도",
    "X 불활성화", "성 결정", "장 섞기",
]


class Content(unittest.TestCase):
    def test_format_numbers(self):
        t = text(section("format"))
        for term in ["13~17", "5개", "30%", "70%", "부정형", "그림", "ㄱㄴㄷ", "46문항"]:
            self.assertIn(term, t)

    def test_topic_rows(self):
        sec = section("topics")
        rows = re.findall(r"<tr>(.*?)</tr>", sec, re.S)
        self.assertEqual(len(rows), 16)  # 머리줄 1 + 주제 15
        t = text(sec)
        for term in TOPIC_TERMS:
            self.assertIn(term, t, f"주제 '{term}' 없음")

    def test_tables_wrapped(self):
        b = body()
        self.assertEqual(b.count("<table"), b.count('<div class="table-wrap"><table'))

    def test_last_check(self):
        t = text(section("last"))
        for term in ["9:3:3:1", "2ⁿ", "보인자", "상동염색체", "자매염색분체",
                     "기출 4강 32", "기출 4강 39", "p9"]:
            self.assertIn(term, t)


if __name__ == "__main__":
    unittest.main()
