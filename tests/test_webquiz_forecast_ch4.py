import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "웹과제예상/src/4장"
OUT = ROOT / "웹과제예상/복습문제_4장_웹과제예상.html"
sys.path.insert(0, str(ROOT / ".agents/skills/bio-review-pack/scripts"))
import check_html  # noqa: E402
from scripts.build_webquiz_forecast import render  # noqa: E402


def source() -> str:
    return OUT.read_text(encoding="utf-8")


def model() -> dict:
    m = re.search(r'<script id="review-interaction-model" type="application/json">(.*?)</script>', source(), re.S)
    return json.loads(m.group(1))


def card(cid: str) -> str:
    m = re.search(rf'<article class="card" id="{cid}"[^>]*>(.*?)</article>', source(), re.S)
    if not m:
        raise AssertionError(f"카드 없음: {cid}")
    return m.group(1)


def text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class Build(unittest.TestCase):
    def test_output_is_fresh(self):
        name, html = render(SRC)
        self.assertEqual(name, OUT.name)
        self.assertEqual(html, source(), "카드 조각과 HTML이 다름: build_webquiz_forecast.py 다시 실행")

    def test_checker_clean(self):
        self.assertEqual([str(p) for p in check_html.check_file(OUT)], [])

    def test_note_link(self):
        self.assertIn('<a class="top-link" href="../복습노트/0929/정리노트_0929_Heredity.html">정리노트</a>', source())

    def test_range_isolated(self):
        self.assertIn('data-range="4장"', source())

    def test_old_page_removed(self):
        self.assertFalse((ROOT / "웹과제예상/4장_웹과제예상.html").exists())

    def test_overview_cards(self):
        o1, o2 = text(card("o1")), text(card("o2"))
        for term in ["13~17", "30%", "70%", "부정형", "ㄱㄴㄷ", "46문항", "유전 용어", "양성잡종",
                     "성연관", "구조 변형", "비분리", "ABO", "불완전우성", "다인자유전", "연관·재조합",
                     "이수성", "2/3", "가계도", "X 불활성화", "성 결정", "장 섞기"]:
            self.assertIn(term, o1, f"o1에 '{term}' 없음")
        for term in ["9:3:3:1", "2ⁿ", "보인자", "상동염색체", "자매염색분체", "기출 4강 32", "기출 4강 39", "p9"]:
            self.assertIn(term, o2, f"o2에 '{term}' 없음")
        self.assertTrue({"o1", "o2"} <= set(model()["skipped"]))

    def test_tables_wrapped(self):
        s = source()
        self.assertEqual(s.count("<table"), s.count('<div class="table-wrap"><table'))


EXPECTED = dict(zip([f"p{i}" for i in range(1, 16)], "DBCEBCACEADBEAD"))
REQUIRED_TYPES = {"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "쌍둥이": 1, "장섞기": 1}
FIG_CLASSES = {"fig-ink", "fig-accent", "fig-dot", "fig-text", "fig-muted"}


class Cards(unittest.TestCase):
    def test_answer_key(self):
        cards = model()["cards"]
        self.assertEqual({k: v["answer"] for k, v in cards.items()}, EXPECTED)
        for pid, c in cards.items():
            self.assertEqual([o["id"] for o in c["options"]], list("ABCDE"), pid)
            self.assertEqual(c["mode"], "single", pid)

    def test_card_structure(self):
        for i in range(1, 16):
            body = card(f"p{i}")
            order = [m.group(0) for m in re.finditer(
                r'<h3>|<div class="problem">|<details class="(?:original|hint|solution)">', body)]
            self.assertEqual(order, ['<h3>', '<div class="problem">', '<details class="original">',
                                     '<details class="hint">', '<details class="solution">'], f"p{i}")
            self.assertTrue(text(body).startswith(f"P{i}. [예상]"), f"p{i} 제목")
            self.assertIn("수업과의 연결", body, f"p{i}")
            self.assertRegex(body, r'href="\.\./복습노트/\d{4}/정리노트_[^"]+#s\d-[a-z-]+"', f"p{i} 노트 링크")

    def test_every_option_diagnosed(self):
        for i in range(1, 16):
            steps = re.search(r'<ol class="steps">(.*?)</ol>', card(f"p{i}"), re.S).group(1)
            labels = re.findall(r"<li>([A-E])\. (맞아요|틀려요)", steps)
            self.assertEqual([l for l, _ in labels], list("ABCDE"), f"p{i} 보기 진단")
            right = [l for l, v in labels if v == "맞아요"]
            types = re.search(rf'<article class="card" id="p{i}"[^>]*data-types="([^"]+)"', source()).group(1).split()
            if "부정형" in types:
                self.assertNotIn(EXPECTED[f"p{i}"], right, f"p{i} 부정형 정답은 틀려요")
            else:
                self.assertEqual(right, [EXPECTED[f"p{i}"]], f"p{i} 맞아요는 정답 하나")

    def test_type_counts(self):
        counts: dict[str, int] = {}
        for t in re.findall(r'<article class="card" id="p\d+"[^>]*data-types="([^"]+)"', source()):
            for k in t.split():
                counts[k] = counts.get(k, 0) + 1
        for k, n in REQUIRED_TYPES.items():
            self.assertGreaterEqual(counts.get(k, 0), n, k)

    def test_figures(self):
        for pid in ("p7", "p8"):
            svgs = re.findall(r"<svg.*?</svg>", card(pid), re.S)
            self.assertEqual(len(svgs), 1, pid)
            svg = svgs[0]
            self.assertIn('role="img"', svg)
            self.assertNotRegex(svg, r"#[0-9a-fA-F]{3,6}\b")
            self.assertNotRegex(svg, r'\s(fill|stroke)="')
            self.assertLessEqual(int(re.search(r'viewBox="0 0 (\d+) \d+"', svg).group(1)), 360)
            self.assertTrue(set(re.findall(r'class="([^"]+)"', svg)) <= FIG_CLASSES, pid)
            for i in re.findall(r'\sid="([^"]+)"', svg):
                self.assertTrue(i.startswith(pid + "-"), i)

    def test_ganada_statements(self):
        problem = re.search(r'<div class="problem">(.*?)</div>', card("p8"), re.S).group(1)
        for s in ("ㄱ.", "ㄴ.", "ㄷ."):
            self.assertIn(s, text(problem))

    def test_scope_and_wording(self):
        cards_text = " ".join(text(card(c)) for c in ["o1", "o2"] + list(EXPECTED))
        for banned in ["헬리케이스", "오카자키", "코돈", "전사", "번역", "유전상담", "답을 선택하면", "여기를 눌러"]:
            self.assertNotIn(banned, cards_text)
        self.assertIsNone(re.search(r"[①-⑳]", cards_text), "원문자 ①~⑳ 금지")

    def test_no_open_details(self):
        self.assertNotRegex(source(), r"<details[^>]*\sopen[\s>=]")


if __name__ == "__main__":
    unittest.main()
