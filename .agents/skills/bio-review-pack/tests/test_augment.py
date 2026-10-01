"""보강 모드(scripts/augment.py): 기존 카드·manifest 추출과 복습문제만 다시 조립."""

import json
from pathlib import Path
import shutil
import tempfile
import unicodedata
import unittest

from _util import MINI_RUN, REPO

import assemble
import augment


def fixture_pack(tmp: Path) -> Path:
    """mini-run을 조립한 팩 폴더(.pack 포함)."""
    pack = tmp / "pack"
    assemble.assemble(MINI_RUN, pack)
    return pack


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pack = fixture_pack(self.tmp)
        self.run = self.tmp / "run"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_extract_uses_pack_manifest(self):
        info = augment.extract(self.pack, self.run)
        self.assertFalse(info["reconstructed"])
        self.assertEqual(info["next_id"], "p3")
        self.assertEqual(info["parts"], {"partA": 1, "partB": 1})
        self.assertEqual(sorted(p.name for p in (self.run / "cards").iterdir()), ["p1.html", "p2.html"])
        card = (self.run / "cards" / "p2.html").read_text(encoding="utf-8")
        self.assertTrue(card.startswith('<article class="card" id="p2" data-source="기출 3강 7">'))
        self.assertTrue(card.endswith("</article>"))
        base = json.loads((self.run / "work" / "base-ids.json").read_text(encoding="utf-8"))
        self.assertEqual(base["p2"], {"part": "partB", "source": "기출 3강 7", "answer": "(2)"})
        self.assertEqual(json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))["forbidden_outside_preview"], ["d-separation"])

    def test_extract_reconstructs_without_pack(self):
        shutil.rmtree(self.pack / ".pack")
        info = augment.extract(self.pack, self.run)
        self.assertTrue(info["reconstructed"])
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["forbidden_outside_preview"], [])
        self.assertEqual(m["preview_topic"], "s2-next")
        self.assertEqual([s["id"] for s in m["sections"]], ["s1", "s2"])
        self.assertEqual(m["sections"][0]["short"], "1 기초")
        self.assertTrue(m["sections"][0]["topics"][1]["supp"])
        self.assertEqual([q["id"] for q in m["problems"]], ["p1", "p2"])
        self.assertEqual(m["problems"][1]["answer"], "(2)")
        self.assertIn("금지어 미복원", (self.run / "work" / "reconstructed.txt").read_text(encoding="utf-8"))

    def test_pack_manifest_mismatch_stops(self):
        m = json.loads((self.pack / ".pack" / "manifest.json").read_text(encoding="utf-8"))
        m["problems"] = [q for q in m["problems"] if q["id"] != "p2"]
        (self.pack / ".pack" / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.extract(self.pack, self.run)
        self.assertIn("p2", str(cm.exception))

    def test_nfd_file_names(self):
        for p in list(self.pack.iterdir()):
            if p.suffix == ".html":
                p.rename(self.pack / unicodedata.normalize("NFD", p.name))
        note, review = augment.find_pack_files(self.pack)
        self.assertEqual(unicodedata.normalize("NFC", review.name), "복습문제_0101-0102_Mini_Test.html")
        self.assertTrue(review.exists())
        self.assertEqual(augment.extract(self.pack, self.run)["next_id"], "p3")


class TestReconstructRealPacks(unittest.TestCase):
    """저장소의 실제 팩마다: HTML에서 복원한 manifest로 다시 조립하면 원본과 바이트까지 같다."""

    def test_round_trip_from_html(self):
        packs = sorted(p for p in (REPO / "복습노트").iterdir() if p.is_dir() and not p.name.startswith("."))
        checked = 0
        for pack in packs:
            try:
                note, review = augment.find_pack_files(pack)
            except augment.AugmentError:
                continue
            with self.subTest(pack=pack.name), tempfile.TemporaryDirectory() as tmp:
                m = augment.reconstruct(note, review)
                run = Path(tmp)
                (run / "cards").mkdir()
                html = review.read_text(encoding="utf-8")
                for c in augment.CARD_RE.finditer(html):
                    (run / "cards" / f"{c.group(1)}.html").write_text(c.group(0), encoding="utf-8")
                self.assertEqual(assemble.build_review(m, run), html)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
