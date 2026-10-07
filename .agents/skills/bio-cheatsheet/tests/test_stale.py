import json
from pathlib import Path
import shutil
import tempfile
import unittest

import _util  # noqa: F401  (scripts 경로 등록)
import stale


class TestStale(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.panic = self.repo / "panic.md"
        self.panic.write_text("패턴 v1", encoding="utf-8")
        for ch in ("1장", "2장"):
            (self.repo / "웹과제" / ch).mkdir(parents=True)
            (self.repo / "웹과제" / ch / "questions.json").write_text("{}", encoding="utf-8")
        (self.repo / "웹과제" / "3장" / "raw").mkdir(parents=True)  # 빈 raw는 등록 아님

    def tearDown(self):
        shutil.rmtree(self.repo)

    def sheet(self, ch: str, basis: dict | None):
        d = self.repo / "웹과제예상" / "커닝페이퍼" / ch
        d.mkdir(parents=True)
        spec = {"chapter": int(ch[:-1]), "sections": []}
        if basis is not None:
            spec["basis"] = basis
        (d / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    def fresh(self) -> dict:
        return stale.current_basis(self.repo, self.panic)

    def test_registered(self):
        self.assertEqual(stale.registered_webquiz(self.repo), ["1장", "2장"])
        (self.repo / "웹과제" / "3장" / "raw" / "s.png").write_bytes(b"x")
        self.assertEqual(stale.registered_webquiz(self.repo), ["1장", "2장", "3장"])

    def test_fresh_sheet_not_stale(self):
        self.sheet("2장", self.fresh())
        self.assertEqual(stale.scan(self.repo, self.panic), [])

    def test_missing_basis(self):
        self.sheet("2장", None)
        [(ch, why)] = stale.scan(self.repo, self.panic)
        self.assertEqual(ch, "2장")
        self.assertIn("basis 없음", why[0])

    def test_new_webquiz(self):
        b = self.fresh()
        b["webquiz"] = ["1장"]
        self.sheet("2장", b)
        [(_, why)] = stale.scan(self.repo, self.panic)
        self.assertIn("2장", why[0])

    def test_panic_changed(self):
        self.sheet("2장", self.fresh())
        self.panic.write_text("패턴 v2", encoding="utf-8")
        [(_, why)] = stale.scan(self.repo, self.panic)
        self.assertIn("panic-patterns", why[0])


if __name__ == "__main__":
    unittest.main()
