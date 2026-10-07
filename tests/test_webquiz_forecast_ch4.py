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


EXPECTED_ANSWERS = "DBCEBCACEADBEAD"
REQUIRED_TYPES = {"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "쌍둥이": 1, "장섞기": 1}


def questions() -> list[re.Match]:
    return list(re.finditer(
        r'<article class="q" id="q(\d\d)" data-answer="([A-E])" data-types="([^"]+)">(.*?)</article>',
        section("mock"), re.S))


class Mock(unittest.TestCase):
    def test_fifteen_in_order(self):
        qs = questions()
        self.assertEqual([m.group(1) for m in qs], [f"{i:02d}" for i in range(1, 16)])

    def test_answer_key(self):
        self.assertEqual("".join(m.group(2) for m in questions()), EXPECTED_ANSWERS)

    def test_five_options(self):
        for m in questions():
            opts = re.findall(r'<li data-opt="([A-E])">', m.group(4))
            self.assertEqual(opts, list("ABCDE"), f"q{m.group(1)} 보기")

    def test_answer_text_matches(self):
        for m in questions():
            sol = re.search(r'<details class="sol">(.*?)</details>', m.group(4), re.S)
            self.assertIsNotNone(sol, f"q{m.group(1)} 풀이 없음")
            self.assertIn(f'<p class="ans">정답 {m.group(2)}</p>', sol.group(1))
            self.assertGreater(len(text(sol.group(1))), 25, f"q{m.group(1)} 풀이가 너무 짧음")

    def test_answers_hidden(self):
        b = body()
        self.assertNotRegex(b, r"<details[^>]*\bopen\b")
        outside = re.sub(r'<details class="sol">.*?</details>', "", b, flags=re.S)
        self.assertNotIn('class="ans"', outside)

    def test_type_counts(self):
        counts = {}
        for m in questions():
            for t in m.group(3).split():
                counts[t] = counts.get(t, 0) + 1
        for t, n in REQUIRED_TYPES.items():
            self.assertGreaterEqual(counts.get(t, 0), n, f"유형 {t}")

    def test_figures_and_stmts(self):
        for m in questions():
            types, inner = m.group(3).split(), m.group(4)
            if "그림" in types:
                self.assertIn("<svg", inner, f"q{m.group(1)} 그림 없음")
            if "ㄱㄴㄷ" in types:
                for s in ["ㄱ.", "ㄴ.", "ㄷ."]:
                    self.assertIn(s, text(inner), f"q{m.group(1)} {s}")

    def test_svg_rules(self):
        for svg in re.findall(r"<svg.*?</svg>", body(), re.S):
            self.assertNotRegex(svg, r"#[0-9a-fA-F]{3,6}\b")
            self.assertNotRegex(svg, r'\s(fill|stroke)="')
            self.assertNotIn("<marker", svg)
            width = int(re.search(r'viewBox="0 0 (\d+) \d+"', svg).group(1))
            self.assertLessEqual(width, 360)
            for cls in re.findall(r'class="([^"]+)"', svg):
                self.assertIn(cls, {"fig-ink", "fig-accent", "fig-dot", "fig-text", "fig-muted"})
            self.assertIn('role="img"', svg)

    def test_scope(self):
        t = text(section("mock"))
        for banned in ["헬리케이스", "오카자키", "코돈", "전사", "번역", "유전상담"]:
            self.assertNotIn(banned, t)


if __name__ == "__main__":
    unittest.main()
