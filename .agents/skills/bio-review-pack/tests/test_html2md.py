from pathlib import Path
import shutil
import tempfile
import unicodedata
import unittest
import xml.dom.minidom

from _util import MINI_RUN

import assemble
import html2md


def page(body):
    return f'<html><body><main><div class="hero"><h1>t</h1></div>{body}</main></body></html>'


def small_pack(directory, note_body, review_body, nfd=False):
    names = ["정리노트_0101_X.html", "복습문제_0101_X.html"]
    if nfd:
        names = [unicodedata.normalize("NFD", n) for n in names]
    note, review = Path(directory) / names[0], Path(directory) / names[1]
    note.write_text(page(note_body), encoding="utf-8")
    review.write_text(page(review_body), encoding="utf-8")
    return note, review


class TestHtml2Md(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.note, self.review = assemble.assemble(MINI_RUN, self.tmp)
        (self.note_md, self.review_md), self.figs = html2md.convert_pack(self.note, self.review)
        self.md = Path(self.note_md).read_text(encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_outputs_and_check_pass(self):
        self.assertEqual(Path(self.note_md).name, "정리노트_0101-0102_Mini_Test.md")
        self.assertEqual(html2md.check_md(self.note, self.note_md), [])
        self.assertEqual(html2md.check_md(self.review, self.review_md), [])

    def test_card_image_kept_in_markdown(self):
        review_md = Path(self.review_md).read_text(encoding="utf-8")
        self.assertIn("![중기 염색체 그림](figures_0101-0102/p2.png)", review_md)
        self.assertIn("자매염색분체가 서로 부착되어 있는", review_md)
        self.assertEqual(html2md.check_md(self.review, self.review_md), [])

    def test_page_summary_rendered(self):
        self.assertIn("**페이지 요약**", self.md)
        self.assertIn("*핵심 식*", self.md)
        self.assertIn("- **분산(variance)** — 평균과의 차이를 제곱해 평균낸 값", self.md)

    def test_widget_static_becomes_figure_and_table(self):
        self.assertEqual(self.figs, 1)
        self.assertTrue((self.tmp / "figures_0101-0102" / "widget-mean-static.svg").exists())
        self.assertIn('<a id="widget-mean"></a>', self.md)
        self.assertIn("![평균 1.5 막대](figures_0101-0102/widget-mean-static.svg)", self.md)
        self.assertIn("| 1, 2 | $\\frac{3}{2}$ |", self.md)

    def test_reconversion_removes_orphan_svgs_only(self):
        fig = self.tmp / "figures_0101-0102"
        (fig / "old-orphan.svg").write_text("<svg/>", encoding="utf-8")
        (fig / "keep.txt").write_text("x", encoding="utf-8")
        (self.tmp / "outside.svg").write_text("<svg/>", encoding="utf-8")
        _, figs = html2md.convert_pack(self.note, self.review)
        self.assertEqual(figs, 1)
        self.assertEqual(sorted(p.name for p in fig.iterdir()), ["keep.txt", "p2.png", "widget-mean-static.svg"])
        self.assertTrue((self.tmp / "outside.svg").exists())

    def test_links_rewritten_to_md(self):
        self.assertIn("(복습문제_0101-0102_Mini_Test.md)", self.md)
        review = Path(self.review_md).read_text(encoding="utf-8")
        self.assertIn("**정답:**", review)

    def test_table_math_pipes(self):
        ctx = html2md.Ctx([], str(self.tmp), "figures_x")
        b = html2md.Builder()
        b.feed(r"<table><tr><th>a</th></tr><tr><td>$\|x\|$ | $|y|$</td></tr></table>")
        table = next(b.root.find_all(lambda n: n.tag == "table"))
        self.assertEqual(html2md.render_table(table, ctx)[2], r"| $\Vert x\Vert $ \| $\vert y\vert $ |")

    def test_check_md_detects_missing_math(self):
        Path(self.note_md).write_text(self.md.replace(r"\bar{x} = ", ""), encoding="utf-8")
        problems = html2md.check_md(self.note, self.note_md)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("수식 누락"))

    def test_bad_filename_rejected(self):
        bad = self.tmp / "note.html"
        shutil.copyfile(self.note, bad)
        with self.assertRaises(ValueError):
            html2md.convert_pack(bad, self.review)


    def test_svg_export_keeps_viewbox_case_and_size(self):
        ctx = html2md.Ctx([], str(self.tmp), "f")
        b = html2md.Builder()
        b.feed('<svg id="t" viewBox="0 0 720 400" width="100%" preserveAspectRatio="xMidYMid meet">'
               '<defs><marker id="m" markerWidth="6" markerHeight="6" refX="3" refY="3"/></defs>'
               '<linearGradient id="g" gradientUnits="userSpaceOnUse"/></svg>')
        svg = next(b.root.find_all(lambda n: n.tag == "svg"))
        html2md.export_svg(svg, ctx)
        root = xml.dom.minidom.parse(str(self.tmp / "t.svg")).documentElement
        self.assertEqual(root.getAttribute("viewBox"), "0 0 720 400")
        self.assertEqual((root.getAttribute("width"), root.getAttribute("height")), ("720", "400"))
        self.assertEqual(root.getAttribute("preserveAspectRatio"), "xMidYMid meet")
        self.assertFalse(root.hasAttribute("viewbox"))
        marker = root.getElementsByTagName("marker")[0]
        self.assertEqual((marker.getAttribute("refX"), marker.getAttribute("markerWidth")), ("3", "6"))
        self.assertEqual(len(root.getElementsByTagName("linearGradient")), 1)

    def test_unnamed_and_duplicate_figures_are_distinct_files(self):
        d = self.tmp / "p"
        d.mkdir()
        fig = '<figure><svg viewBox="0 0 10 10"><circle r="3"/></svg></figure>'
        dup = '<figure><svg id="same" viewBox="0 0 10 10"><rect width="1" height="1"/></svg></figure>'
        note, review = small_pack(d, f'<section id="s"><h2>A</h2>{fig}{dup}</section>',
                                  f'<section id="q"><h2>Q</h2>{fig}{dup}</section>')
        (note_md, review_md), figs = html2md.convert_pack(note, review)
        files = sorted(x.name for x in (d / "figures_0101").iterdir())
        self.assertEqual(figs, 4)
        self.assertEqual(files, ["note-fig-1.svg", "review-fig-1.svg", "same-2.svg", "same.svg"])
        self.assertEqual(html2md.check_md(note, note_md), [])
        self.assertEqual(html2md.check_md(review, review_md), [])

    def _math_pack(self):
        d = self.tmp / "m"
        d.mkdir()
        note, review = small_pack(d, r'<section id="s"><h2>A</h2><p>Let $a$ be a value, $\alpha$ and $\alpha$.</p></section>',
                                  '<section id="q"><h2>Q</h2><p>q</p></section>')
        (note_md, _), _ = html2md.convert_pack(note, review)
        md = Path(note_md).read_text(encoding="utf-8")
        self.assertEqual(html2md.check_md(note, note_md), [])
        return note, Path(note_md), md

    def test_check_md_detects_deleted_short_math(self):
        note, note_md, md = self._math_pack()
        note_md.write_text(md.replace("Let $a$ be", "Let be"), encoding="utf-8")
        problems = html2md.check_md(note, note_md)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("수식 누락: $a$"))
        note_md.write_text(md.replace("Let $a$ be", "Let a be"), encoding="utf-8")  # $ 없이 남은 것도 누락
        self.assertEqual(len(html2md.check_md(note, note_md)), 1)

    def test_check_md_detects_one_of_two_identical_formulas_lost(self):
        note, note_md, md = self._math_pack()
        note_md.write_text(md.replace(r" and $\alpha$", " and"), encoding="utf-8")
        problems = html2md.check_md(note, note_md)
        self.assertEqual(len(problems), 1)
        self.assertIn("(1/2)", problems[0])

    def test_check_md_detects_unrewritten_and_broken_links(self):
        md = self.md.replace("(복습문제_0101-0102_Mini_Test.md)", "(./복습문제_0101-0102_Mini_Test.html#q1)")
        md += "\n[x](../%EC%97%86%EC%9D%8C/x.html)\n"
        Path(self.note_md).write_text(md, encoding="utf-8")
        problems = html2md.check_md(self.note, self.note_md)
        self.assertEqual(len(problems), 2)
        self.assertTrue(problems[0].startswith("링크 미변환(.html): ./복습문제"))
        self.assertTrue(problems[1].startswith("링크 파일 없음: ../"))

    def test_nfd_named_pair_converts(self):
        d = self.tmp / "nfd"
        d.mkdir()
        nfd_link = unicodedata.normalize("NFD", "./복습문제_0101_X.html") + "#q"
        note, review = small_pack(d, f'<section id="s"><h2>A</h2><p><a href="{nfd_link}">q</a></p></section>',
                                  '<section id="q"><h2>Q</h2><p>q</p></section>', nfd=True)
        (note_md, review_md), _ = html2md.convert_pack(note, review)
        self.assertEqual(Path(note_md).name, "정리노트_0101_X.md")
        self.assertIn("(./복습문제_0101_X.md#q)", Path(note_md).read_text(encoding="utf-8"))
        self.assertEqual(html2md.check_md(note, note_md), [])


class TestOnlyReview(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.note, self.review = assemble.assemble(MINI_RUN, self.tmp)
        html2md.convert_pack(self.note, self.review)
        self.note_md = self.note.with_suffix(".md")
        self.review_md = self.review.with_suffix(".md")
        self.figs = self.tmp / "figures_0101-0102"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.figs.iterdir()}

    def test_only_review_leaves_note_md_and_figures(self):
        before_review, before_figs = self.review_md.read_bytes(), self.snapshot()
        marked = self.note_md.read_bytes() + b"\n<!-- untouched -->\n"
        self.note_md.write_bytes(marked)
        outs, _ = html2md.convert_pack(self.note, self.review, only="review")
        self.assertEqual([Path(o).name for o in outs], [self.review_md.name])
        self.assertEqual(self.note_md.read_bytes(), marked)
        self.assertEqual(self.review_md.read_bytes(), before_review)
        self.assertEqual(self.snapshot(), before_figs)

    def test_only_rejects_other_values(self):
        with self.assertRaises(ValueError):
            html2md.convert_pack(self.note, self.review, only="note")

    def test_cli_only_review_check(self):
        rc = html2md.main([str(self.note), str(self.review), "--only", "review", "--check"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
