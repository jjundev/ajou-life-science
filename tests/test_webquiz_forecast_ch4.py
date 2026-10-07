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


if __name__ == "__main__":
    unittest.main()
