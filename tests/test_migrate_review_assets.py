import shutil
import tempfile
import unicodedata
import unittest
from pathlib import Path

from scripts.migrate_review_assets import (
    broken_links,
    migrate_day,
    rewrite_html,
    rewrite_md,
)
import review_interaction  # noqa: E402  (경로는 위 import가 sys.path에 넣는다)

REVIEW = "복습문제_0922_X.html"
CARD = """<article class="card" id="p1"><div class="problem"><p>틀린 것을 고르시오.</p>
<img src="figures_0922/p37.png" alt="그림">
<ul class="choices"><li>(1) 옳은 설명</li><li>(2) 틀린 설명</li></ul></div>
<details class="solution"><summary>풀이 보기</summary><ol class="steps">
<li>(1) 맞는 설명이므로 답이 아니에요.</li><li>(2) 틀린 설명이므로 답이에요.</li>
<li>수업과의 연결: 분류</li></ol><p class="answer">정답: (2)</p></details></article>"""
NEW_COMMENT = "<날짜>/.assets/풀이기록 without a picker"
OLD_COMMENT = "<날짜>/풀이기록 without a picker"


def old_review_html():
    """이전 전 복습문제: 옛 상호작용 JS(주석)와 루트 기준 img src로 만든 채점 모델."""
    html = review_interaction.install("<html><body>" + CARD + "</body></html>", REVIEW)
    assert html.count(NEW_COMMENT) == 1
    return html.replace(NEW_COMMENT, OLD_COMMENT)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def nfd(s):
    return unicodedata.normalize("NFD", s)


def read(p):
    return Path(p).read_text(encoding="utf-8")


def write(p, text=""):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def snapshot(root):
    out = {}
    for p in sorted(Path(root).rglob("*")):
        key = nfc(str(p.relative_to(root)))
        out[key] = p.read_bytes() if p.is_file() else None
    return out


class TestMigrate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "복습노트"
        self.day = self.root / "0922"
        d = self.day
        write(self.root / "0917" / "정리노트_0917_Y.html", "<p>0917</p>")
        write(d / nfd("정리노트_0922_X.html"),
              '<a href="../0917/정리노트_0917_Y.html">앞</a>\n'
              '<img src="figures_0922/p37.png">\n'
              '<a href="#s1">s1</a> <a href="https://example.com/a.png">ext</a>\n')
        write(d / REVIEW, old_review_html())
        write(d / nfd("문제설명_0922_X.html"),
              '<link rel="stylesheet" href="자료_문제설명_0922_X/vendor/katex/katex.min.css">\n')
        write(d / "인터렉티브_01_a.html",
              "<!-- 생성 파일: 자료_인터렉티브_01_a/Main.dc.html을 고친 뒤 "
              "bio-interactive/scripts/build.cjs로 다시 만드세요. -->\n<p>x</p>\n")
        write(d / nfd("정리노트_0922_X.md"),
              "[복습](복습문제_0922_X.md#p1)\n![f](figures_0922/a.svg)\n"
              "[원](%EC%A0%95%EB%A6%AC%EB%85%B8%ED%8A%B8_0922_X.html#s1)\n")
        write(d / "복습문제_0922_X.md", "# 복습\n")
        write(d / "장마감_0922_3장.md", "[n](../0917/정리노트_0917_Y.html)\n")
        (d / "figures_0922").mkdir()
        (d / "figures_0922" / "p37.png").write_bytes(b"\x89PNG")
        write(d / "figures_0922" / "a.svg", "<svg/>")
        write(d / nfd("자료_문제설명_0922_X") / "vendor/katex/katex.min.css", "body{}")
        write(d / nfd("자료_인터렉티브_01_a") / "Main.dc.html", "<p>src</p>")
        write(d / nfd("풀이기록") / "r.json", "{}")
        write(d / ".pack" / "manifest.json", "{}")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_dry_run_changes_nothing(self):
        before = snapshot(self.root)
        acts = migrate_day(self.day, apply=False)
        self.assertTrue(any(a.startswith("move ") for a in acts))
        self.assertEqual(snapshot(self.root), before)

    def test_apply_layout_and_links(self):
        migrate_day(self.day, apply=True)
        self.assertEqual(sorted(nfc(p.name) for p in self.day.iterdir()),
                         [".assets", ".pack", "문제설명_0922_X.html", "복습문제_0922_X.html",
                          "인터렉티브_01_a.html", "정리노트_0922_X.html"])
        self.assertIn('src=".assets/figures_0922/p37.png"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn('href="../0917/정리노트_0917_Y.html"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn("생성 파일: .assets/자료_인터렉티브_01_a/Main.dc.html",
                      read(self.day / "인터렉티브_01_a.html"))
        review = read(self.day / REVIEW)
        self.assertIn('src=".assets/figures_0922/p37.png"', review)
        self.assertIn(NEW_COMMENT, review)
        self.assertNotIn(OLD_COMMENT, review)
        self.assertEqual(review_interaction.install(review, REVIEW), review)
        md = read(self.day / ".assets/정리노트_0922_X.md")
        self.assertIn("](복습문제_0922_X.md#p1)", md)
        self.assertIn("](figures_0922/a.svg)", md)
        self.assertIn("](../%EC%A0%95", md)
        self.assertIn("](../../0917/정리노트_0917_Y.html)", read(self.day / ".assets/장마감_0922_3장.md"))
        self.assertEqual(broken_links(self.day), [])

    def test_migrate_is_idempotent(self):
        migrate_day(self.day, apply=True)
        once = snapshot(self.root)
        self.assertEqual(migrate_day(self.day, apply=True), [])
        self.assertEqual(snapshot(self.root), once)

    def test_name_clash_stops(self):
        (self.day / ".assets/figures_0922").mkdir(parents=True)
        before = snapshot(self.root)
        with self.assertRaises(FileExistsError):
            migrate_day(self.day, apply=True)
        self.assertEqual(snapshot(self.root), before)

    def test_review_install_error_moves_nothing(self):
        write(self.day / REVIEW, read(self.day / REVIEW).replace("정답: (2)", "정답: (9)"))
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            migrate_day(self.day, apply=True)
        self.assertEqual(snapshot(self.root), before)


class TestPieces(unittest.TestCase):
    def test_rewrite_html_leaves_external_and_html_links(self):
        html = ('<a href="#p1"></a><a href="https://x/y.png"></a>'
                '<a href="%EC%A0%95.html#s"></a><img src="data:image/png;base64,AA">')
        self.assertEqual(rewrite_html(html), html)

    def test_rewrite_md_relocates_then_rebases(self):
        out = rewrite_md("[a](정리노트_0922_X.html#s) ![b](./figures_0922/a.svg) "
                         "[c](../0917/figures_0917/b.png) [d](https://x/y.md) [e](#p1)")
        self.assertEqual(out, "[a](../정리노트_0922_X.html#s) ![b](figures_0922/a.svg) "
                              "[c](../../0917/.assets/figures_0917/b.png) [d](https://x/y.md) [e](#p1)")

    def test_broken_links_counts_titled_md_link(self):
        with tempfile.TemporaryDirectory() as t:
            day = Path(t) / "0922"
            write(day / ".assets" / "a.md", '[x](missing.html "t")\n[ok](a.md)\n')
            self.assertEqual(len(broken_links(day)), 1)
            self.assertIn("missing.html", broken_links(day)[0])


if __name__ == "__main__":
    unittest.main()
