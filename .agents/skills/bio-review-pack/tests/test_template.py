"""정리노트 템플릿이 예습 스킬(bio-preview-note)과 공유하는 슬롯·스타일을 지킨다."""

import re
import unittest

from _util import SKILL

TEMPLATE = SKILL / "assets" / "note-template.html"
SLOTS = {"BRAND", "DESCRIPTION", "FOOTER", "PAGE_TITLE", "RANGE", "SCRIPTS", "SECTIONS", "SUBTITLE", "TITLE", "TOC"}


class TestNoteTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")

    def test_slots(self):
        self.assertEqual(set(re.findall(r"\{\{([A-Z_]+)\}\}", self.text)), SLOTS)

    def test_brand_is_slot(self):
        self.assertIn('<strong class="brand">{{BRAND}}</strong>', self.text)

    def test_preview_styles(self):
        for sel in (".layer.listen", ".layer.listen .layer-title", ".badge.exam"):
            with self.subTest(sel=sel):
                self.assertIn(sel, self.text)


class TestScrollbar(unittest.TestCase):
    def test_themed_scrollbar(self):
        for name in ("note-template.html", "review-template.html"):
            text = (SKILL / "assets" / name).read_text(encoding="utf-8")
            with self.subTest(template=name):
                self.assertEqual(len(re.findall(r"--scroll: #[0-9a-f]{6}; --scroll-hover: #[0-9a-f]{6};", text)), 3)
                for s in ("--scroll: #c9d0db; --scroll-hover: #9aa3b2;", "--scroll: #3f414b; --scroll-hover: #5b5e6a;",
                          ".panel-inner::-webkit-scrollbar-thumb { background: var(--scroll);",
                          ".panel-inner::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }",
                          ".content, .panel-inner { scrollbar-width: thin; scrollbar-color: var(--scroll) transparent; }"):
                    self.assertIn(s, text)


if __name__ == "__main__":
    unittest.main()
