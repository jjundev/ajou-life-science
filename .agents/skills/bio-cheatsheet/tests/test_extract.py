import json
from pathlib import Path
import shutil
import tempfile
import unittest

from _util import MINI

import build
import extract


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.spec = json.loads((MINI / "spec.json").read_text(encoding="utf-8"))
        self.tpl = build.load_template()
        self.frags = build.load_fragments(self.spec, MINI / "sections")
        self.html = build.render(self.tpl, self.spec["title"], "cheatsheet_9장", [self.frags[:2], self.frags[2:]])

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_fragments_match_sources(self):
        self.assertEqual(extract.extract(self.html), self.frags)

    def test_leading_source_comment_kept(self):
        self.assertTrue(extract.extract(self.html)[2].startswith("<!-- 출처: 복습노트/0922"))

    def test_round_trip(self):
        out = self.tmp / "sections"
        extract.write(extract.extract(self.html), out)
        again = build.load_fragments(self.spec, out)
        html2 = build.render(self.tpl, self.spec["title"], "cheatsheet_9장", [again[:2], again[2:]])
        self.assertEqual(html2, self.html)

    def test_spec_mismatch_fails(self):
        p = self.tmp / "c.html"
        p.write_text(self.html, encoding="utf-8")
        spec = json.loads(json.dumps(self.spec))
        spec["sections"][2]["label"] = "③ 딴 구역"
        sp = self.tmp / "spec.json"
        sp.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(extract.main([str(p), str(self.tmp / "s"), "--spec", str(sp)]), 1)
        self.assertFalse((self.tmp / "s").exists())

    def test_no_sections_fails(self):
        with self.assertRaises(build.BuildError):
            extract.extract("<html><body><p>없음</p></body></html>")


if __name__ == "__main__":
    unittest.main()
