import json
from pathlib import Path
import shutil
import tempfile
import unittest

from _util import HAS_CHROME, HAS_POPPLER, MINI

import build
import check


class Base(unittest.TestCase):
    """미니 fixture를 PDF 없이 조립해 두고, 위반을 하나씩 심어 본다."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.spec = json.loads((MINI / "spec.json").read_text(encoding="utf-8"))
        tpl = build.load_template()
        frags = build.load_fragments(cls.spec, MINI / "sections")
        cls.good = build.render(tpl, cls.spec["title"], "cheatsheet_9장", [frags[:2], frags[2:]])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def problems(self, html: str, spec: dict | None = None) -> list[str]:
        return check.check_html(html, spec or self.spec)

    def assertFlags(self, html: str, needle: str, spec: dict | None = None):
        probs = self.problems(html, spec)
        self.assertTrue(any(needle in p for p in probs), f"'{needle}' 위반을 못 잡음: {probs}")


class TestGood(Base):
    def test_good_passes(self):
        self.assertEqual(self.problems(self.good), [])


class TestStructure(Base):
    def test_label_order(self):
        spec = json.loads(json.dumps(self.spec))
        spec["sections"][1], spec["sections"][2] = spec["sections"][2], spec["sections"][1]
        self.assertFlags(self.good, "라벨 순서", spec)

    def test_toc_mismatch(self):
        self.assertFlags(self.good.replace('<p class="page-toc">③ 미니 구역</p>', '<p class="page-toc">③ 딴 이름</p>'), "목차")

    def test_page_numbers(self):
        self.assertFlags(self.good.replace('<span class="page-no">2 / 2</span>', '<span class="page-no">2 / 3</span>'), "쪽 번호")

    def test_theme_button_only_page1(self):
        btn = build.load_template().theme_btn
        html = self.good.replace('<span class="page-no">2 / 2</span>', '<span class="page-no">2 / 2</span>' + btn)
        self.assertFlags(html, "테마 버튼")

    def test_nested_head_comment(self):
        self.assertFlags(self.good.replace("■ 크기 토큰 위치", "■ <!--@X--> 크기 토큰 위치", 1), "head 주석")

    def test_placeholder(self):
        self.assertFlags(self.good.replace("세부 효소 이름", "견본 문장"), "견본")


class TestContent(Base):
    def test_answer_words(self):
        self.assertFlags(self.good.replace("세부 효소 이름", "정답은 (3)"), "답 번호")

    def test_trap_without_source(self):
        html = self.good.replace('<!-- 출처: 복습노트/0922 정리노트 L122 -->\n      <div class="trap">', '<div class="trap">')
        self.assertFlags(html, "출처 주석")

    def test_trap_count(self):
        trap = '<!-- 출처: x -->\n<div class="trap"><span class="trap-x">✗ a</span><span class="trap-ok">✓ b</span></div>\n'
        html = self.good.replace('<p class="later">', trap * 3 + '<p class="later">')
        self.assertFlags(html, "함정 4개")

    def test_trap_in_fixed_section(self):
        trap = '<!-- 출처: x -->\n<div class="trap"><span class="trap-x">✗ a</span><span class="trap-ok">✓ b</span></div>\n'
        html = self.good.replace('<dl class="kv">', trap + '<dl class="kv">')
        self.assertFlags(html, "함정을 두지 않는")

    def test_later_must_be_last_with_badge(self):
        html = self.good.replace('<p class="later"><span class="badge prof">교수님: 몰라도 됨</span> 세부 효소 이름.</p>',
                                 '<p class="later">세부 효소 이름.</p><p>뒤에 더</p>')
        probs = self.problems(html)
        self.assertTrue(any("later" in p and "배지" in p for p in probs), probs)
        self.assertTrue(any("later" in p and "맨 끝" in p for p in probs), probs)

    def test_ascii_formula(self):
        for bad in ("CO2가 나온다", "NAD+ 환원", "H2O 분해"):
            with self.subTest(bad=bad):
                self.assertFlags(self.good.replace("세부 효소 이름", bad), "유니코드")

    def test_ascii_ok_inside_words(self):
        self.assertEqual(self.problems(self.good.replace("세부 효소 이름", "C4 식물, PSII")), [])

    def test_terms(self):
        self.assertFlags(self.good.replace("자매염색분체", "두 가닥"), "자매염색분체")

    def test_chapter_terms(self):
        self.assertFlags(self.good.replace("상동염색체", "다른 것"), "상동염색체")


class TestSvg(Base):
    def fig(self, svg: str) -> str:
        return self.good.replace('<p class="later">', f'<figure class="mini-fig">{svg}</figure>\n<p class="later">')

    def test_svg_ok(self):
        svg = '<svg viewBox="0 0 340 120"><defs><marker id="m3a"></marker></defs><text class="fig-text">CO₂</text></svg>'
        self.assertEqual(self.problems(self.fig(svg)), [])

    def test_hardcoded_color(self):
        self.assertFlags(self.fig('<svg viewBox="0 0 300 100"><rect fill="#ff0000"/></svg>'), "색")

    def test_viewbox_too_wide(self):
        self.assertFlags(self.fig('<svg viewBox="0 0 500 100"></svg>'), "viewBox")

    def test_viewbox_too_tall(self):
        self.assertFlags(self.fig('<svg viewBox="0 0 200 120"></svg>'), "viewBox")

    def test_duplicate_ids(self):
        svg = '<svg viewBox="0 0 300 100"><marker id="arr"></marker><marker id="arr"></marker></svg>'
        self.assertFlags(self.fig(svg), "id 중복")


@unittest.skipUnless(HAS_CHROME and HAS_POPPLER, "Chrome/poppler 없음")
class TestFiles(unittest.TestCase):
    def test_full_build_passes_and_stale_pdf_fails(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            html = build.build(MINI / "spec.json", MINI / "sections", tmp)
            spec = json.loads((MINI / "spec.json").read_text(encoding="utf-8"))
            self.assertEqual(check.check_files(html, spec), [])
            html.write_text(html.read_text(encoding="utf-8").replace('<span class="page-no">1 / 1</span>', '<span class="page-no">1 / 1</span>'), encoding="utf-8")
            import os
            os.utime(html.with_suffix(".pdf"), (0, 0))
            self.assertTrue(any("PDF" in p for p in check.check_files(html, spec)))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
