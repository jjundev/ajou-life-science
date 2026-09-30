import json
from pathlib import Path
import shutil
import tempfile
import unittest

from _util import MINI_RUN

import assemble


class TestAssemble(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.note, self.review = assemble.assemble(MINI_RUN, self.tmp)
        self.note_html = self.note.read_text(encoding="utf-8")
        self.review_html = self.review.read_text(encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_output_names(self):
        self.assertIn('id="review-interaction-model"', self.review_html)
        self.assertNotIn('id="review-interaction-model"', self.note_html)
        self.assertEqual(self.note.name, "정리노트_0101-0102_Mini_Test.html")
        self.assertEqual(self.review.name, "복습문제_0101-0102_Mini_Test.html")

    def test_sections_toc_and_titles(self):
        self.assertIn('<nav class="toc" aria-label="목차"><a href="#s1">1 기초</a><a href="#s2">2 요약·예고</a></nav>', self.note_html)
        self.assertIn('<section id="s1"><h2>1. 기초 통계</h2>', self.note_html)
        self.assertIn("<h1>Mini — 테스트 정리노트</h1>", self.note_html)
        self.assertIn("<title>생명과학 정리노트 0101-0102</title>", self.note_html)
        self.assertIn("<title>생명과학 복습문제 0101-0102</title>", self.review_html)

    def test_note_brand(self):
        self.assertIn('<strong class="brand">정리노트</strong>', self.note_html)

    def test_scripts_moved_after_main(self):
        main_end = self.note_html.index("</main>")
        self.assertGreater(self.note_html.index('<script id="widget-mean-ui">'), main_end)

    def test_href_tokens_replaced_and_no_slots_left(self):
        self.assertIn('href="복습문제_0101-0102_Mini_Test.html"', self.note_html)
        self.assertIn('<a class="top-link" href="정리노트_0101-0102_Mini_Test.html">', self.review_html)
        self.assertNotIn("{{", self.note_html + self.review_html)

    def test_review_parts(self):
        self.assertIn('<section id="partA"><h2>A. 교과서 예제</h2>', self.review_html)
        self.assertIn('<section id="partB"><h2>B. 기출</h2>', self.review_html)

    def test_card_figures_copied(self):
        # 카드 원문 그림(RUN/figures/)은 산출물 figures_<range>/ 로 복사된다.
        self.assertEqual((self.tmp / "figures_0101-0102" / "p2.png").read_bytes(),
                         (MINI_RUN / "figures" / "p2.png").read_bytes())

    def test_progress_keys_are_scoped_by_range(self):
        # 팩마다 p1, s1-… id가 겹치므로 진행 기록 키에 기간이 들어가야 한다.
        for html in (self.note_html, self.review_html):
            self.assertIn('data-range="0101-0102"', html)
            self.assertIn("const KEY = 'od-review-solved:' + RANGE;", html)
            self.assertIn("const KEY = 'od-note-read:' + RANGE;", html)

    def test_answers_and_progress_use_session_storage_only(self):
        # 푼 흔적은 탭을 닫으면 사라져야 한다(뒤로가기·새로고침엔 유지). 영구 저장(localStorage)은 화면 설정 전용.
        self.assertIn("window.sessionStorage", self.review_html)
        self.assertNotIn("window.localStorage", self.review_html)
        review = self.review_html
        section = review[review.index("function setupReview()"):review.index("function setupNote()")]
        self.assertIn("tabStore.get(KEY", section)
        self.assertNotIn("store.get(KEY", section)
        self.assertNotIn("store.set(KEY", section)

    def test_theme_toggle_in_both_pages(self):
        for html in (self.note_html, self.review_html):
            self.assertIn('id="theme-toggle"', html)
            self.assertIn('<script id="theme-ui">', html)
            # 저장된 테마는 첫 페인트 전에(head에서) 적용한다
            head = html.split("</head>", 1)[0]
            self.assertIn("localStorage.getItem('od-theme')", head)

    def test_missing_fragment_raises(self):
        run = self.tmp / "run"
        shutil.copytree(MINI_RUN, run)
        (run / "cards" / "p1.html").unlink()
        with self.assertRaises(assemble.AssembleError):
            assemble.assemble(run, self.tmp / "out")

    def test_missing_card_writes_neither_file(self):
        run = self.tmp / "run"
        shutil.copytree(MINI_RUN, run)
        (run / "cards" / "p1.html").unlink()
        out = self.tmp / "out2"
        with self.assertRaises(assemble.AssembleError):
            assemble.assemble(run, out)
        self.assertEqual(list(out.iterdir()), [])
        # 이미 있는 팩도 그대로 남는다
        before = {p.name: p.read_bytes() for p in (self.note, self.review)}
        with self.assertRaises(assemble.AssembleError):
            assemble.assemble(run, self.tmp)
        self.assertEqual({p.name: p.read_bytes() for p in (self.note, self.review)}, before)

    def _svg_run_rejected(self, name):
        run = self.tmp / "run-svg"
        shutil.copytree(MINI_RUN, run)
        (run / "figures" / name).write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        out = self.tmp / "out-svg"
        with self.assertRaises(assemble.AssembleError) as cm:
            assemble.assemble(run, out)
        self.assertIn(name, str(cm.exception))
        # 실패한 조립은 정리노트·복습문제 HTML을 어느 쪽도 쓰지 않는다.
        self.assertEqual(sorted(out.glob("*.html")) if out.exists() else [], [])

    def test_svg_figure_rejected_before_writing(self):
        # SVG는 카드에 인라인한다. RUN/figures/에 두면 html2md가 나중에 지운다.
        self._svg_run_rejected("x.svg")

    def test_uppercase_svg_figure_rejected(self):
        self._svg_run_rejected("X.SVG")

    def test_fill_rejects_missing_slot(self):
        with self.assertRaises(assemble.AssembleError):
            assemble.fill("<p>{{NOPE}}</p>", {})

    def test_fill_does_not_expand_slots_inside_values(self):
        self.assertEqual(assemble.fill("{{A}}", {"A": "{{B}}"}), "{{B}}")


if __name__ == "__main__":
    unittest.main()
