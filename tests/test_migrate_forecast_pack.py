import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

from scripts.migrate_forecast_pack import main, migrate_chapter, problems

STEM = "문제해설_5장_웹과제예상_v1"
FIG = f"figures_{STEM}"
DATA = f"자료_{STEM}"
NOTE = "../../복습노트/1001/정리노트_1001_X.html"
ENC_NOTE = "../../" + quote("복습노트") + "/1001/" + quote("정리노트_1001_X.html") + "#s4"


def crlf(text):
    return text.replace("\n", "\r\n").encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(p, raw):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw)


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None)
            for p in sorted(Path(root).rglob("*"))}


class TestMigrateForecast(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "웹과제예상"
        self.ch = self.root / "5장"
        put(Path(self.tmp.name) / "복습노트/1001/정리노트_1001_X.html", b"<html></html>")
        put(self.ch / "복습문제_5장_웹과제예상_v1.html", crlf(f'<a href="{NOTE}">노트</a>\n'))
        put(self.ch / "src/v1/pack.json", b'{"chapter": 5, "version": 1}')
        put(self.ch / "src/v1/blueprint.md", crlf("| 카드 |\n"))
        put(self.ch / "src/v1/cards/p1.html", b"<article></article>")
        self.html = crlf(f'<link href="{DATA}/vendor/katex/katex.min.css">\n'
                         f'<img src="{quote(FIG)}/explain-fig-1.svg">\n')
        put(self.ch / f"{STEM}.html", self.html)
        self.md = crlf(f"![그림]({FIG}/explain-fig-1.svg)\n[노트]({ENC_NOTE})\n[p1](#p1)\n")
        put(self.ch / f"{STEM}.md", self.md)
        put(self.ch / FIG / "explain-fig-1.svg", b"<svg/>")
        put(self.ch / DATA / "vendor/katex/katex.min.css", b"x")
        put(self.ch / DATA / "evidence/e.md", b"e")
        ctx = str(self.ch / "src" / "v1" / "pack.json").replace("/", "\\")
        manifest = {"context_hashes": [[ctx, "c"]],
                    "files": {f"{FIG}/explain-fig-1.svg": sha(b"<svg/>"), f"{STEM}.html": sha(self.html),
                              f"{STEM}.md": sha(self.md), f"{DATA}/evidence/e.md": sha(b"e")}}
        put(self.ch / DATA / "manifest.json", crlf(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"))
        validation = {"references": [{"path": ctx, "sha256": "c"}],
                      "artifact_hashes": {f"{STEM}.html": sha(self.html), f"{STEM}.md": sha(self.md)}}
        put(self.ch / DATA / "validation.json", crlf(json.dumps(validation, ensure_ascii=False, indent=2) + "\n"))
        put(self.root / "커닝페이퍼/5장/spec.json", b"{}")

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_changes_nothing(self):
        before = snapshot(self.root)
        acts = migrate_chapter(self.ch, apply=False)
        self.assertIn("move src/v1 -> .pack/v1", acts)
        self.assertEqual(snapshot(self.root), before)

    def test_apply_layout(self):
        migrate_chapter(self.ch, apply=True)
        self.assertEqual(sorted(p.name for p in self.ch.iterdir()),
                         sorted([".pack", "복습문제_5장_웹과제예상_v1.html", f"{STEM}.html"]))
        self.assertEqual(sorted(p.name for p in (self.ch / ".pack").iterdir()),
                         sorted(["v1", FIG, DATA, f"{STEM}.md"]))
        self.assertTrue((self.ch / ".pack/v1/cards/p1.html").is_file())
        self.assertEqual(problems(self.ch), [])

    def test_html_links_relocated(self):
        migrate_chapter(self.ch, apply=True)
        text = (self.ch / f"{STEM}.html").read_bytes().decode("utf-8")
        self.assertIn(f'href=".pack/{DATA}/vendor/katex/katex.min.css"', text)
        self.assertIn(f'src=".pack/{quote(FIG)}/explain-fig-1.svg"', text)
        review = (self.ch / "복습문제_5장_웹과제예상_v1.html").read_bytes()
        self.assertEqual(review, crlf(f'<a href="{NOTE}">노트</a>\n'))

    def test_md_links_rebased_and_crlf_kept(self):
        migrate_chapter(self.ch, apply=True)
        raw = (self.ch / ".pack" / f"{STEM}.md").read_bytes()
        text = raw.decode("utf-8")
        self.assertIn(f"]({FIG}/explain-fig-1.svg)", text)
        self.assertIn("](../" + ENC_NOTE + ")", text)
        self.assertIn("](#p1)", text)
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))

    def test_records_rewritten(self):
        migrate_chapter(self.ch, apply=True)
        pack = self.ch / ".pack"
        raw = (pack / DATA / "manifest.json").read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        manifest = json.loads(raw)
        self.assertIn("\\.pack\\v1\\pack.json", manifest["context_hashes"][0][0])
        files = manifest["files"]
        self.assertEqual(sorted(files), sorted([f".pack/{FIG}/explain-fig-1.svg", f"{STEM}.html",
                                                f".pack/{STEM}.md", f".pack/{DATA}/evidence/e.md"]))
        for name, digest in files.items():
            self.assertEqual(digest, sha((self.ch / name).read_bytes()), name)
        validation = json.loads((pack / DATA / "validation.json").read_bytes())
        self.assertIn("\\.pack\\v1\\pack.json", validation["references"][0]["path"])
        self.assertEqual(validation["artifact_hashes"][f".pack/{STEM}.md"], sha((pack / f"{STEM}.md").read_bytes()))
        self.assertEqual(validation["artifact_hashes"][f"{STEM}.html"], sha((self.ch / f"{STEM}.html").read_bytes()))

    def test_validation_tracks_rewritten_manifest_hash(self):
        validation = json.loads((self.ch / DATA / "validation.json").read_bytes())
        validation["artifact_hashes"][f"{DATA}/manifest.json"] = sha((self.ch / DATA / "manifest.json").read_bytes())
        put(self.ch / DATA / "validation.json", crlf(json.dumps(validation, ensure_ascii=False, indent=2) + "\n"))
        migrate_chapter(self.ch, apply=True)
        pack = self.ch / ".pack"
        hashes = json.loads((pack / DATA / "validation.json").read_bytes())["artifact_hashes"]
        self.assertEqual(hashes[f".pack/{DATA}/manifest.json"], sha((pack / DATA / "manifest.json").read_bytes()))

    def test_idempotent(self):
        migrate_chapter(self.ch, apply=True)
        after = snapshot(self.root)
        self.assertEqual(migrate_chapter(self.ch, apply=True), [])
        self.assertEqual(snapshot(self.root), after)

    def test_clash_moves_nothing(self):
        put(self.ch / ".pack/v1/pack.json", b"{}")
        before = snapshot(self.root)
        with self.assertRaises(FileExistsError):
            migrate_chapter(self.ch, apply=True)
        self.assertEqual(snapshot(self.root), before)

    def test_main_skips_non_chapter_and_checks(self):
        cheat = snapshot(self.root / "커닝페이퍼")
        self.assertEqual(main([str(self.root), "--check"]), 1)  # 루트에 src·md·figures가 남아 있음
        self.assertEqual(main([str(self.root), "--apply"]), 0)
        self.assertEqual(main([str(self.root), "--check"]), 0)
        self.assertEqual(snapshot(self.root / "커닝페이퍼"), cheat)


if __name__ == "__main__":
    unittest.main()
