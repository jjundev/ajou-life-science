import re
import unittest

from _util import SKILL
import check

REPO = SKILL.parents[2]
V1 = REPO / "웹과제예상" / "4장" / "복습문제_4장_웹과제예상_v1.html"


class TestRepoV1(unittest.TestCase):
    def test_v1_passes_check(self):
        self.assertTrue(V1.is_file(), V1)
        self.assertEqual(check.check(V1), [])

    def test_chapter_folders_hold_only_html_and_pack(self):
        chapters = [d for d in (REPO / "웹과제예상").iterdir() if re.fullmatch(r"[1-9]\d*장", d.name)]
        self.assertGreaterEqual(len(chapters), 2)
        for d in chapters:
            extra = sorted(p.name for p in d.iterdir() if p.name != ".pack" and not p.name.endswith(".html"))
            self.assertEqual(extra, [], d.name)
            self.assertTrue((d / ".pack" / "v1" / "pack.json").is_file(), d.name)

    def test_old_layout_removed(self):
        for p in ("웹과제예상/복습문제_4장_웹과제예상.html", "웹과제예상/src/4장",
                  "scripts/build_webquiz_forecast.py", "tests/test_webquiz_forecast_ch4.py"):
            self.assertFalse((REPO / p).exists(), p)


if __name__ == "__main__":
    unittest.main()
