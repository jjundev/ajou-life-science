import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "웹과제예상/4장_웹과제예상.html"
SECTION_IDS = ["format", "topics", "mock", "last"]


def raw() -> str:
    return HTML.read_text(encoding="utf-8")


def body() -> str:
    return re.sub(r"<!--.*?-->", "", raw().split("<body", 1)[1], flags=re.S)


def text(html: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", t).strip()


def section(sec_id: str) -> str:
    m = re.search(rf'<section class="sec" id="{sec_id}">(.*?)</section>', body(), re.S)
    if not m:
        raise AssertionError(f"구역 없음: {sec_id}")
    return m.group(1)


class Skeleton(unittest.TestCase):
    def test_title(self):
        self.assertIn("<title>4장 웹과제 예상</title>", raw())

    def test_sections_in_order(self):
        found = re.findall(r'<section class="sec" id="([a-z]+)">', body())
        self.assertEqual(found, SECTION_IDS)

    def test_no_script(self):
        self.assertNotIn("<script", raw())

    def test_theme_tokens(self):
        r = raw()
        self.assertIn("@media (prefers-color-scheme: dark)", r)
        self.assertRegex(r, r"body\s*\{[^}]*background:\s*var\(--bg\)")

    def test_font_fallback(self):
        r = raw()
        self.assertIn("'Malgun Gothic'", r)
        self.assertIn("system-ui", r)


if __name__ == "__main__":
    unittest.main()
