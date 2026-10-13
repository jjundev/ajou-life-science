import shutil
import tempfile
import unicodedata
import unittest
from pathlib import Path

from scripts.migrate_review_assets import (
    broken_links,
    export_block,
    migrate_day,
    rewrite_html,
    rewrite_md,
)

ROOT = Path(__file__).resolve().parents[1]
ASSET_JS = ROOT / ".agents/skills/bio-review-pack/assets/review-interaction.js"
BLOCK = export_block(ASSET_JS.read_text(encoding="utf-8"))

OLD_BLOCK = """async function resolveExportDir(root, documentId, range) {
    const child = async (dir, name, create) => {
      try { return await dir.getDirectoryHandle(name, create ? {create:true} : undefined); }
      catch (error) { if (error && error.name === 'NotFoundError') return null; throw error; }
    };
    if (root.name === '풀이기록') return root;
    return child(root, '풀이기록', true);
  }
  """


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
        write(d / "복습문제_0922_X.html",
              "<script>\n  " + OLD_BLOCK + "const isCancel = e => !!e;\n</script>\n"
              '<img src="figures_0922/p37.png">\n')
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
        acts = migrate_day(self.day, BLOCK, apply=False)
        self.assertTrue(any(a.startswith("move ") for a in acts))
        self.assertEqual(snapshot(self.root), before)

    def test_apply_layout_and_links(self):
        migrate_day(self.day, BLOCK, apply=True)
        self.assertEqual(sorted(nfc(p.name) for p in self.day.iterdir()),
                         [".assets", ".pack", "문제설명_0922_X.html", "복습문제_0922_X.html",
                          "인터렉티브_01_a.html", "정리노트_0922_X.html"])
        self.assertIn('src=".assets/figures_0922/p37.png"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn('href="../0917/정리노트_0917_Y.html"', read(self.day / "정리노트_0922_X.html"))
        self.assertIn("생성 파일: .assets/자료_인터렉티브_01_a/Main.dc.html",
                      read(self.day / "인터렉티브_01_a.html"))
        self.assertIn("'.assets'", read(self.day / "복습문제_0922_X.html"))
        md = read(self.day / ".assets/정리노트_0922_X.md")
        self.assertIn("](복습문제_0922_X.md#p1)", md)
        self.assertIn("](figures_0922/a.svg)", md)
        self.assertIn("](../%EC%A0%95", md)
        self.assertIn("](../../0917/정리노트_0917_Y.html)", read(self.day / ".assets/장마감_0922_3장.md"))
        self.assertEqual(broken_links(self.day), [])

    def test_migrate_is_idempotent(self):
        migrate_day(self.day, BLOCK, apply=True)
        once = snapshot(self.root)
        self.assertEqual(migrate_day(self.day, BLOCK, apply=True), [])
        self.assertEqual(snapshot(self.root), once)

    def test_name_clash_stops(self):
        (self.day / ".assets/figures_0922").mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            migrate_day(self.day, BLOCK, apply=True)

    def test_export_block_requires_single_markers(self):
        with self.assertRaises(ValueError):
            export_block("no markers here")


class TestPieces(unittest.TestCase):
    def test_export_block_rejects_duplicate_start(self):
        js = "async function resolveExportDir(){}\nasync function resolveExportDir(){}\nconst isCancel=1"
        with self.assertRaises(ValueError):
            export_block(js)

    def test_rewrite_html_block_replaced_and_old_gone(self):
        html = "<script>\n  " + OLD_BLOCK + "const isCancel = 1;\n</script>"
        out = rewrite_html(html, BLOCK)
        self.assertIn(BLOCK + "const isCancel = 1;", out)
        self.assertEqual(out.count("async function resolveExportDir"), 1)
        self.assertEqual(rewrite_html(html, None), html)

    def test_rewrite_html_leaves_external_and_html_links(self):
        html = ('<a href="#p1"></a><a href="https://x/y.png"></a>'
                '<a href="%EC%A0%95.html#s"></a><img src="data:image/png;base64,AA">')
        self.assertEqual(rewrite_html(html, BLOCK), html)

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
