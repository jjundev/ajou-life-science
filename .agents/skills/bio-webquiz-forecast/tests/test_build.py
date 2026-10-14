import tempfile
import unittest
from pathlib import Path

from _util import card_html, make_repo, make_set, overview_html
import build


def five():
    cards = {"o1": overview_html()}
    cards.update({f"p{i}": card_html(i, "ABCDE"[i - 1]) for i in range(1, 6)})
    return cards


class TestBuild(unittest.TestCase):
    def test_render_substitutions(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 2, five())
            name, html = build.render(src)
            self.assertEqual(name, "복습문제_9장_웹과제예상_v2.html")
            self.assertEqual(html.count('data-range="9장-v2"'), 1)
            self.assertNotIn('data-range="9장"', html)
            self.assertEqual(html.count('href="../../복습노트/0000/정리노트_0000_T.html"'), 1)  # 상단 링크만(카드 링크는 #s1-t)
            self.assertEqual(html.count(build.OVERRIDE_STYLE), 1)
            self.assertIn('"documentId": "복습문제_9장_웹과제예상_v2.html"', html)

    def test_build_writes_to_chapter_dir(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            out = build.build(make_set(repo, 9, 1, five()))
            self.assertEqual(out, repo.resolve() / "웹과제예상" / "9장" / "복습문제_9장_웹과제예상_v1.html")
            self.assertNotIn(b"\r\n", out.read_bytes())

    def test_folder_must_match_pack(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 1, five(), {"version": 3})
            with self.assertRaises(build.BuildError):
                build.render(src)

    def test_next_version(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "웹과제예상" / "9장"
            self.assertEqual(build.next_version(d), 1)
            (d / ".pack" / "v1").mkdir(parents=True)
            (d / "복습문제_9장_웹과제예상_v3.html").write_text("x", encoding="utf-8")
            self.assertEqual(build.next_version(d), 4)

    def test_next_version_ignores_pack_side_files(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "웹과제예상" / "9장"
            (d / ".pack" / "v2").mkdir(parents=True)
            (d / ".pack" / "figures_문제해설_9장_웹과제예상_v9").mkdir()
            (d / ".pack" / "자료_문제해설_9장_웹과제예상_v9").mkdir()
            (d / ".pack" / "문제해설_9장_웹과제예상_v9.md").write_text("x", encoding="utf-8")
            (d / "src" / "v7").mkdir(parents=True)  # 옛 위치는 보지 않는다
            self.assertEqual(build.next_version(d), 3)

    def test_init_refuses_existing(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            src = build.init_version(repo, 9)
            self.assertEqual(src, repo / "웹과제예상" / "9장" / ".pack" / "v1")
            self.assertTrue((src / "cards").is_dir())
            self.assertEqual(build.init_version(repo, 9).name, "v2")
            (repo / "웹과제예상" / "9장" / ".pack" / "v3").mkdir()
            with self.assertRaises(build.BuildError):
                build.init_version(repo, 9, version=3)

    def test_old_src_layout_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 1, five())
            old = src.parents[1] / "src" / "v1"
            old.parent.mkdir()
            src.rename(old)
            with self.assertRaises(build.BuildError):
                build.render(old)


if __name__ == "__main__":
    unittest.main()
