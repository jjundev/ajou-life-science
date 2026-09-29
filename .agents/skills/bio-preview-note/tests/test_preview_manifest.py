import copy
import io
import json
from contextlib import redirect_stdout
import unittest

from _preview_util import MINI_RUN

import preview_manifest as pm

BASE = json.loads((MINI_RUN / "manifest.json").read_text(encoding="utf-8"))


def errors_with(mutate):
    m = copy.deepcopy(BASE)
    mutate(m)
    return pm.validate(m)


def topic(m, s, t):
    return m["sections"][s]["topics"][t]


class TestPreviewManifest(unittest.TestCase):
    def test_fixture_valid(self):
        self.assertEqual(pm.validate(BASE), [])
        self.assertEqual(pm.load(MINI_RUN / "manifest.json")["range"], "0101")

    def test_names(self):
        self.assertEqual(pm.note_name(BASE), "예습노트_0101_Mini_Preview.html")
        self.assertEqual(pm.fig_dir_name("0101"), "figures_0101")

    def test_missing_top_level_key(self):
        errs = errors_with(lambda m: m.pop("pdfs"))
        self.assertTrue(any("manifest.pdfs" in e for e in errs), errs)

    def test_bad_range(self):
        for bad in ("929", "0929-1001", "L04"):
            with self.subTest(range=bad):
                errs = errors_with(lambda m: m.update(range=bad))
                self.assertTrue(any("manifest.range" in e for e in errs), errs)

    def test_bad_chapters(self):
        for bad in ([], ["4장"], [4]):
            with self.subTest(chapters=bad):
                errs = errors_with(lambda m: m.update(chapters=bad))
                self.assertTrue(any("manifest.chapters" in e for e in errs), errs)

    def test_bad_pdfs(self):
        for bad in ([], ["4장 유전.pdf"]):
            with self.subTest(pdfs=bad):
                errs = errors_with(lambda m: m.update(pdfs=bad))
                self.assertTrue(any("manifest.pdfs" in e for e in errs), errs)

    def test_stt_layer_rejected(self):
        errs = errors_with(lambda m: topic(m, 1, 0)["layers"].append("prof"))
        self.assertTrue(any("알 수 없는 레이어" in e for e in errs), errs)

    def test_concept_topic_needs_eli5_and_formal(self):
        errs = errors_with(lambda m: topic(m, 1, 1).update(layers=["eli5", "listen"]))
        self.assertTrue(any("eli5와 formal" in e for e in errs), errs)

    def test_slides_format(self):
        for bad in ("4장 p2-3", "4장 p2–3", "p2", "4장", "s2", "4 p2", ""):
            with self.subTest(slides=bad):
                errs = errors_with(lambda m: topic(m, 1, 0).update(slides=bad))
                self.assertTrue(any(".slides" in e for e in errs), errs)

    def test_slides_ok(self):
        for good in ("4장 p3", "12장 p1–p6"):
            with self.subTest(slides=good):
                self.assertEqual(errors_with(lambda m: topic(m, 1, 0).update(slides=good)), [])

    def test_s0_topic_may_omit_slides(self):
        self.assertEqual(errors_with(lambda m: topic(m, 0, 0).update(slides="")), [])
        errs = errors_with(lambda m: topic(m, 0, 0).update(slides="p2"))
        self.assertTrue(any(".slides" in e for e in errs), errs)

    def test_exam_terms_must_be_required_terms(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(exam_terms=["멘델"]))
        self.assertTrue(any("exam_terms" in e and "required_terms" in e for e in errs), errs)

    def test_exam_terms_need_listen(self):
        errs = errors_with(lambda m: topic(m, 1, 1).update(exam_terms=["불완전우성"]))
        self.assertTrue(any("exam_terms" in e and "listen" in e for e in errs), errs)

    def test_exam_terms_type(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(exam_terms="독립의 법칙"))
        self.assertTrue(any("exam_terms" in e for e in errs), errs)

    def test_exam_terms_optional(self):
        self.assertEqual(errors_with(lambda m: topic(m, 1, 0).pop("exam_terms")), [])

    def test_figure_ref_type(self):
        for bad in ("", "  ", ["그림 4.3"], 4.3):
            with self.subTest(figure_ref=bad):
                errs = errors_with(lambda m: topic(m, 1, 0).update(figure_ref=bad))
                self.assertTrue(any("figure_ref" in e for e in errs), errs)

    def test_figure_ref_needs_eli5(self):
        errs = errors_with(lambda m: topic(m, 2, 0).update(figure_ref="그림 4.3"))
        self.assertTrue(any("figure_ref" in e and "eli5" in e for e in errs), errs)

    def test_section_ids_in_order(self):
        errs = errors_with(lambda m: m["sections"][0].update(id="s9"))
        self.assertTrue(any("s0이어야 함" in e for e in errs), errs)

    def test_topic_id_prefix(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(id="s0-dihybrid"))
        self.assertTrue(any("s1-로 시작" in e for e in errs), errs)

    def test_last_section_needs_cheatsheet_and_links(self):
        errs = errors_with(lambda m: m["sections"][2]["topics"].pop(0))
        self.assertTrue(any("s2-cheatsheet" in e for e in errs), errs)

    def test_single_section_rejected(self):
        errs = errors_with(lambda m: m.update(sections=m["sections"][:1]))
        self.assertTrue(any("2개 이상" in e for e in errs), errs)

    def test_supp_on_summary_topic_rejected(self):
        errs = errors_with(lambda m: topic(m, 2, 0).update(supp=True))
        self.assertTrue(any(".supp" in e for e in errs), errs)

    def test_link_to_unknown_topic(self):
        errs = errors_with(lambda m: m["links"].append({"topic": "s7-x", "href": "#a"}))
        self.assertTrue(any("없는 토픽" in e for e in errs), errs)

    def test_cli_ok(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pm.main([str(MINI_RUN / "manifest.json")])
        self.assertEqual((code, out.getvalue().strip()), (0, "OK"))


if __name__ == "__main__":
    unittest.main()
