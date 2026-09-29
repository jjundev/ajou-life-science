from contextlib import redirect_stderr, redirect_stdout
import datetime as dt
import io
from pathlib import Path
import tempfile
import unicodedata
import unittest

import _preview_util  # noqa: F401  (scripts 경로)
import preview_files as pf

TUE_0922 = dt.date(2026, 9, 22)
SAT_0926 = dt.date(2026, 9, 26)


def tags(*texts):
    return "".join(f'<span class="tag slide">{t}</span>' for t in texts)


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class RepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        for name in ("3장 세포분열.pdf", "4장 유전.pdf", "12장 신경계와 감각계.pdf", "notes.txt"):
            write(self.repo / "강의노트" / name, "%PDF")
        write(self.repo / "STT" / "0917 생명.md")
        write(self.repo / "STT" / "0922 생명.md")
        write(self.repo / "복습노트" / "0917" / "정리노트_0917_Cell_Division.html", tags("3장 p1", "3장 p2–p5"))
        write(self.repo / "복습노트" / "0922" / "정리노트_0922_Heredity.html", tags("3장 p5", "4장 p1–p2", "4장 p2"))
        write(self.repo / "복습노트" / "0922" / "복습문제_0922_Heredity.html", tags("9장 p9"))

    def tearDown(self):
        self._tmp.cleanup()


class TestPick(RepoCase):
    def test_start_from_latest_note(self):
        date, ch, page, pdf = pf.pick(self.repo, "0929")
        self.assertEqual((date, ch, page, unicodedata.normalize("NFC", pdf.name)), ("0929", 4, 2, "4장 유전.pdf"))

    def test_range_note_uses_end_date(self):
        write(self.repo / "복습노트" / "0923-0924" / "정리노트_0923-0924_More.html", tags("4장 p5"))
        self.assertEqual(pf.latest_review_note(self.repo)[0], "0924")
        self.assertEqual(pf.pick(self.repo, "0929")[2], 5)

    def test_range_tag_uses_end_page(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_X.html", tags("4장 p3–p6"))
        self.assertEqual(pf.pick(self.repo, "0929")[1:3], (4, 6))

    def test_two_digit_chapter(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_X.html", tags("12장 p1"))
        self.assertEqual(unicodedata.normalize("NFC", pf.pick(self.repo, "0929")[3].name), "12장 신경계와 감각계.pdf")

    def test_default_date_skips_class_with_stt(self):
        self.assertEqual(pf.next_class_date(TUE_0922, {"0922"}), "0924")
        self.assertEqual(pf.pick(self.repo, today=TUE_0922)[0], "0924")

    def test_default_date_from_weekend(self):
        self.assertEqual(pf.next_class_date(SAT_0926, set()), "0929")

    def test_default_existing_note_stops(self):
        write(self.repo / "예습노트" / "0929" / "예습노트_0929_X.html", "<html></html>")
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, today=SAT_0926)
        self.assertIn("이미", str(cm.exception))
        self.assertEqual(pf.pick(self.repo, "0929")[0], "0929")  # 날짜를 주면 다시 만들 수 있다

    def test_date_with_stt_stops(self):
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0922")
        self.assertIn("bio-review-pack", str(cm.exception))

    def test_bad_date(self):
        for bad in ("929", "1340", "0230x", "abcd", "0001"):
            with self.subTest(date=bad):
                with self.assertRaises(pf.PickError):
                    pf.pick(self.repo, bad)

    def test_no_review_notes(self):
        for p in (self.repo / "복습노트").rglob("*.html"):
            p.unlink()
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("직접", str(cm.exception))

    def test_note_without_tags(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_Old.html", "<p>태그 없음</p>")
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("쪽 태그", str(cm.exception))
        self.assertIn("정리노트_0924_Old.html", str(cm.exception))

    def test_missing_chapter_pdf(self):
        (self.repo / "강의노트" / "4장 유전.pdf").unlink()
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("ajou-bb", str(cm.exception))

    def test_stt_underscore_name(self):
        write(self.repo / "STT" / "0929_생명.md")
        self.assertIn("0929", pf.stt_dates(self.repo))

    def test_nfd_names(self):
        repo = Path(self._tmp.name) / "nfd"
        write(repo / unicodedata.normalize("NFD", "강의노트") / unicodedata.normalize("NFD", "4장 유전.pdf"), "%PDF")
        write(repo / unicodedata.normalize("NFD", "복습노트") / "0922" / unicodedata.normalize("NFD", "정리노트_0922_X.html"), tags("4장 p2"))
        write(repo / unicodedata.normalize("NFD", "STT") / unicodedata.normalize("NFD", "0922 생명.md"))
        self.assertEqual(pf.pick(repo, today=TUE_0922)[:3], ("0924", 4, 2))

    def test_cli_pick(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pf.main(["pick", "--repo", str(self.repo), "--date", "0929"])
        self.assertEqual(code, 0)
        date, ch, page, pdf = out.getvalue().strip().split("\t")
        self.assertEqual((date, ch, page, unicodedata.normalize("NFC", Path(pdf).name)), ("0929", "4", "2", "4장 유전.pdf"))

    def test_cli_error_exit_code(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = pf.main(["pick", "--repo", str(self.repo), "--date", "0922"])
        self.assertEqual(code, 1)
        self.assertIn("0922", err.getvalue())


class TestBackup(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        self.run = Path(self._tmp.name) / "run"
        self.run.mkdir(parents=True)
        self.dir = self.repo / "예습노트" / "0929"
        self.dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_nothing_to_back_up(self):
        self.assertIsNone(pf.backup(self.repo, "0929", self.run))
        self.assertIsNone(pf.backup(self.repo, "1001", self.run))  # 폴더 자체가 없음

    def test_copies_only_this_date(self):
        (self.dir / "예습노트_0929_A.html").write_text("a", encoding="utf-8")
        (self.dir / "예습노트_0929_A.md").write_text("a", encoding="utf-8")
        (self.dir / "figures_0929").mkdir()
        (self.dir / "figures_0929" / "f.svg").write_text("<svg/>", encoding="utf-8")
        (self.dir / "memo.txt").write_text("x", encoding="utf-8")
        dst = pf.backup(self.repo, "0929", self.run)
        self.assertTrue(dst.name.startswith("previous-"))
        self.assertEqual(sorted(p.name for p in dst.iterdir()), ["figures_0929", "예습노트_0929_A.html", "예습노트_0929_A.md"])
        self.assertTrue((dst / "figures_0929" / "f.svg").exists())

    def test_each_backup_new_folder(self):
        (self.dir / "예습노트_0929_A.html").write_text("a", encoding="utf-8")
        a, b = pf.backup(self.repo, "0929", self.run), pf.backup(self.repo, "0929", self.run)
        self.assertNotEqual(a, b)

    def test_bad_args(self):
        with self.assertRaises(pf.PickError):
            pf.backup(self.repo, "929", self.run)
        with self.assertRaises(pf.PickError):
            pf.backup(self.repo, "0929", self.run / "missing")

    def test_nfd_notes_dir_backed_up(self):
        nfd = self.repo.parent / "repo2" / unicodedata.normalize("NFD", "예습노트") / "0929"
        nfd.mkdir(parents=True)
        (nfd / unicodedata.normalize("NFD", "예습노트_0929_A.html")).write_text("a", encoding="utf-8")
        dst = pf.backup(self.repo.parent / "repo2", "0929", self.run)
        self.assertEqual([unicodedata.normalize("NFC", p.name) for p in dst.iterdir()], ["예습노트_0929_A.html"])


if __name__ == "__main__":
    unittest.main()
