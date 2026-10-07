import unittest

from _util import SKILL
import check

REPO = SKILL.parents[2]
V1 = REPO / "웹과제예상" / "4장" / "복습문제_4장_웹과제예상_v1.html"


class TestRepoV1(unittest.TestCase):
    def test_v1_passes_check(self):
        self.assertTrue(V1.is_file(), V1)
        self.assertEqual(check.check(V1), [])

    def test_old_layout_removed(self):
        for p in ("웹과제예상/복습문제_4장_웹과제예상.html", "웹과제예상/src/4장",
                  "scripts/build_webquiz_forecast.py", "tests/test_webquiz_forecast_ch4.py"):
            self.assertFalse((REPO / p).exists(), p)


if __name__ == "__main__":
    unittest.main()
