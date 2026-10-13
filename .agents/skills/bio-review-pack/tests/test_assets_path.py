import unicodedata
import unittest
from urllib.parse import quote

import _util  # noqa: F401  (scripts/ 를 sys.path에 올린다)

from assets_path import moves, rebase_md, relocate


class TestAssetsPath(unittest.TestCase):
    def test_moves(self):
        for n in ("정리노트_1001_X.md", "figures_1001", "자료_문제설명_1001_X", "풀이기록", "장마감_1001_4장.md"):
            self.assertTrue(moves(n), n)
        for n in ("정리노트_1001_X.html", ".pack", ".assets", ".DS_Store", ""):
            self.assertFalse(moves(n), n)
        self.assertTrue(moves(unicodedata.normalize("NFD", "장마감_1001_4장.md")))
        self.assertFalse(moves(unicodedata.normalize("NFD", "정리노트_1001_X.html")))

    def test_relocate_same_day(self):
        self.assertEqual(relocate("figures_0922/p37.png"), ".assets/figures_0922/p37.png")
        self.assertEqual(relocate("./자료_문제설명_0903_X/vendor/katex/katex.min.css"), ".assets/자료_문제설명_0903_X/vendor/katex/katex.min.css")
        self.assertEqual(relocate("정리노트_1001_X.html#s1"), "정리노트_1001_X.html#s1")
        self.assertEqual(relocate("복습문제_1001_X.md#p3"), ".assets/복습문제_1001_X.md#p3")
        for u in ("#s1", "https://a.b/c.png", "/abs/x.png", "data:image/png;base64,AA", "", "../../웹과제/4장/x.json"):
            self.assertEqual(relocate(u), u)

    def test_relocate_encoded_nfd(self):
        enc = quote(unicodedata.normalize("NFD", "figures_문제설명_0903_X") + "/a.png")
        self.assertEqual(relocate(enc), ".assets/" + enc)
        html = quote("복습문제_1001_X.html") + "#p1"
        self.assertEqual(relocate(html), html)

    def test_relocate_cross_day(self):
        self.assertEqual(relocate("../0922/장마감_0922_3장.md"), "../0922/.assets/장마감_0922_3장.md")
        self.assertEqual(relocate("../0917/figures_0917/x.svg"), "../0917/.assets/figures_0917/x.svg")
        self.assertEqual(relocate("../0922-0924/figures_0922-0924/x.svg"), "../0922-0924/.assets/figures_0922-0924/x.svg")
        self.assertEqual(relocate("../0917/정리노트_0917_X.html#s2"), "../0917/정리노트_0917_X.html#s2")

    def test_relocate_skips_already_relocated(self):
        for u in (".assets/figures_0922/p37.png", "../0917/.assets/figures_0917/x.svg"):
            self.assertEqual(relocate(u), u)

    def test_rebase(self):
        md = ("![a](.assets/figures_1001/x.svg) [b](정리노트_1001_X.html#s1) [c](../0917/정리노트_0917_X.html) "
              "[d](.assets/복습문제_1001_X.md#p2) [e](#top) [f](https://x.y) ![g](./.assets/figures_1001/p.png)")
        self.assertEqual(rebase_md(md),
              "![a](figures_1001/x.svg) [b](../정리노트_1001_X.html#s1) [c](../../0917/정리노트_0917_X.html) "
              "[d](복습문제_1001_X.md#p2) [e](#top) [f](https://x.y) ![g](figures_1001/p.png)")

    def test_rebase_keeps_encoding(self):
        t = "[원 문제 보기](%EB%B3%B5%EC%8A%B5.html#p1)"
        self.assertEqual(rebase_md(t), "[원 문제 보기](../%EB%B3%B5%EC%8A%B5.html#p1)")


if __name__ == "__main__":
    unittest.main()
