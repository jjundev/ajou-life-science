from contextlib import redirect_stdout
import io
from pathlib import Path
import shutil
import tempfile
import unittest

from _preview_util import MINI_RUN

import preview_assemble as pa
import preview_check as pc
import preview_manifest as pm

LEAD = "두 가지 특징은 서로 상관없이 따로 물려받아요."
FIG_SVG = '<svg id="fig-dihybrid" viewBox="0 0 160 40" role="img" aria-label="네 칸으로 나뉜 막대"><rect x="10" y="10" width="140" height="20" class="fig-ink"/></svg>'
FIG_SOURCE = "교과서 그림 4.3을 단순하게 다시 그렸어요."
LISTEN = "독립의 법칙이 나오면 정의를 그대로 받아 적어 두세요."
BADGE = '<span class="badge exam">기출</span> '


class TestPreviewCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.run = self.tmp / "run"
        shutil.copytree(MINI_RUN, self.run)
        self.m = pm.load(self.run / "manifest.json")

    def tearDown(self):
        self._tmp.cleanup()

    def patch(self, sid, old, new):
        p = self.run / "sections" / f"{sid}.html"
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def problems(self):
        note = pa.assemble(self.run, self.tmp / "out")
        return pc.check_preview(self.m, note)

    def codes(self):
        return {(p.code, p.where) for p in self.problems()}

    def test_fixture_passes(self):
        self.assertEqual(self.problems(), [])

    def test_missing_required_term(self):
        self.patch("s1", "이형접합자의 표현형", "잡종의 표현형")
        self.assertIn(("missing-term", "s1-incomplete"), self.codes())

    def test_slide_tag(self):
        self.patch("s1", "4장 p2–p3", "4장 p2")
        self.assertIn(("slide-tag", "s1-dihybrid"), self.codes())

    def test_slide_tag_exact_match(self):
        self.patch("s1", "4장 p2–p3", "4장 p2–p31")
        self.assertIn(("slide-tag", "s1-dihybrid"), self.codes())

    def test_supp_label(self):
        self.patch("s1", "교과서 보충", "보충")
        self.assertIn(("missing-supp", "s1-incomplete"), self.codes())

    def test_stt_layer(self):
        self.patch("s1", '<div class="layer listen">',
                   '<div class="layer prof"><span class="layer-title">교수님 말씀</span><p>가</p></div><div class="layer listen">')
        self.assertIn(("stt-layer", "s1-dihybrid"), self.codes())

    def test_eli5_sentences(self):
        self.patch("s1", LEAD, LEAD + " 두 번째 문장이에요. 세 번째 문장이에요.")
        self.assertIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_figcaption_not_counted_as_sentence(self):
        self.patch("s1", LEAD, LEAD + " 두 번째 문장이에요.")
        self.assertNotIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_eli5_sentences_without_periods(self):
        self.patch("s1", f'<p class="lead">{LEAD}</p>', '<p class="lead">첫 문장이에요</p><p>둘째 문장이에요</p><p>셋째예요</p>')
        self.assertIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_inline_markup_does_not_split_sentence(self):
        self.patch("s1", LEAD, "비율은 9:<b>3</b>이에요. 둘째 문장이에요.")
        self.assertNotIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_listen_predicting_professor(self):
        self.patch("s1", LISTEN, "독립의 법칙을 강조하실 거예요.")
        self.assertIn(("listen-predicts", "s1-dihybrid"), self.codes())

    def test_listen_items(self):
        self.patch("s1", f"{LISTEN}</li>", f"{LISTEN}</li><li>나</li><li>다</li>")
        self.assertIn(("listen-long", "s1-dihybrid"), self.codes())

    def test_topic_too_long(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", "나눠 담는 과정이에요.</p><p>" + "가" * 700 + "</p>")
        self.assertIn(("topic-long", "s0-meiosis"), self.codes())

    def test_math_not_counted(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", "나눠 담는 과정이에요.</p><p>$$" + "x_n + " * 300 + "x$$</p>")
        self.assertNotIn(("topic-long", "s0-meiosis"), self.codes())

    def test_summary_panel_not_counted(self):
        self.patch("s0", '<p class="sum-lead">감수분열은 상동염색체를 나눠요.</p>', '<p class="sum-lead">' + "가" * 700 + "</p>")
        self.assertNotIn(("topic-long", "s0-meiosis"), self.codes())

    def test_exam_badge_missing(self):
        self.patch("s1", BADGE, "")
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_badge_without_exam_terms(self):
        self.m["sections"][1]["topics"][0]["exam_terms"] = []
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_badge_outside_listen_ignored_but_required_inside(self):
        self.patch("s1", BADGE, "")
        self.patch("s1", '<p class="lead">', '<p class="lead"><span class="badge exam">기출</span> ')
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_term_must_appear_in_listen(self):
        self.patch("s1", LISTEN, "이 법칙이 나오면 정의를 그대로 받아 적어 두세요.")
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_figure_ref_needs_svg(self):
        self.patch("s1", FIG_SVG, "")
        self.assertIn(("figure", "s1-dihybrid"), self.codes())

    def test_figure_ref_on_topic_without_figure(self):
        self.m["sections"][1]["topics"][1]["figure_ref"] = "그림 4.5"
        self.assertIn(("figure", "s1-incomplete"), self.codes())

    def test_at_most_one_figure(self):
        self.patch("s1", "</figcaption></figure>",
                   '</figcaption></figure><figure class="figure"><svg id="fig-extra" viewBox="0 0 160 40" role="img" aria-label="추가"></svg></figure>')
        self.assertIn(("figure", "s1-dihybrid"), self.codes())

    def test_figure_source_in_caption(self):
        self.patch("s1", FIG_SOURCE, "")
        self.assertIn(("figure-source", "s1-dihybrid"), self.codes())

    def test_textbook_image_rejected(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", '나눠 담는 과정이에요.</p><img src="fig.png" alt="교과서 그림">')
        self.assertIn(("textbook-image", "예습노트_0101_Mini_Preview.html"), self.codes())

    def test_data_uri_image_rejected(self):
        self.patch("s1", f'<p class="lead">{LEAD}</p>', f'<p class="lead">{LEAD}</p><img src="data:image/png;base64,AAAA" alt="교과서 그림">')
        self.assertIn(("textbook-image", "예습노트_0101_Mini_Preview.html"), self.codes())

    def test_svg_embedded_image_rejected(self):
        self.patch("s1", '<rect x="10"', '<image href="data:image/png;base64,AAAA" width="160" height="40"/><rect x="10"')
        self.assertIn(("textbook-image", "예습노트_0101_Mini_Preview.html"), self.codes())

    def test_helpers(self):
        self.assertEqual(pc.visible_chars("가 나 $x^2$ $$y$$ 다"), 3)
        self.assertEqual(pc.sentences(" 하나예요. 둘이에요? 셋 "), 3)
        self.assertEqual(pc.sentences("값은 0.5예요."), 1)

    def test_badge_text_not_counted(self):
        stats = pc.topic_stats(
            '<article class="topic" id="t"><div class="layer listen"><ul><li><span class="badge exam">기출</span>가나</li></ul></div></article>')
        self.assertEqual(pc.visible_chars(stats["t"].text), 2)
        self.assertEqual(stats["t"].exam_badges, 1)

    def test_cli_missing_note(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pc.main(["--manifest", str(self.run / "manifest.json"), "--note", str(self.tmp / "none.html")])
        self.assertEqual(code, 1)
        self.assertIn("none.html", out.getvalue())

    def test_cli(self):
        note = pa.assemble(self.run, self.tmp / "out")
        with redirect_stdout(io.StringIO()):
            code = pc.main(["--manifest", str(self.run / "manifest.json"), "--note", str(note)])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
