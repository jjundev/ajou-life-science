import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from study_guide_fixture import ROOT
from build_guide import main as build_main
from verify_guide import run_coverage

NOTE = """# 효소

효소는 활성화에너지를 낮춘다.

평형은 바꾸지 않는다.

## 부록. 문항 ↔ 개념 매핑

| 출처 | # | 무엇을 묻는가 | 노트 위치 | 상태 |
|---|---:|---|---|---|
| 2강 | 6 | 효소의 잘못된 설명 | 효소 | |
"""

GUIDE = '''import guide_kit as kit
from guide_kit import F, Q, T, R, section

SOURCES = [dict(id="note", path="note.md", role="note"), dict(id="quiz", path="quiz.txt", role="quiz")]
CONCEPTS = [("enzyme", "효소", [])]
kit.TITLES.update({"enzyme": "효소"})
BLOCKS = [("b0", 1, 1, "metadata", "단원 제목", None),
          ("b1", 3, 3, "teaching", "본문", None),
          ("b2", 5, 5, "teaching", "본문", None),
          ("map", 7, 11, "question_map", "문항 매핑", ["2강:6"])]
FACTS = [F("f1", "b1", "definition", "enzyme", "효소는 활성화에너지를 낮춘다.", "효소는 활성화에너지를 낮춘다."),
         F("f2", "b2", "exception", "enzyme", "평형은 바꾸지 않는다.", "평형은 바꾸지 않는다.")]
QUESTIONS = [Q("2강:6", "included", "enzyme", "1", "효소에 대한 설명 중 틀린 것은?",
               ["비가역 반응을 가역 반응으로 만든다.", "활성화에너지를 낮춘다."], 1, 1, "single", ["f2", "f1"],
               {1: "틀린 설명: 평형은 그대로다.", 2: "옳은 설명이다."}, "속도와 평형을 혼동하기 쉽다.",
               "효소는 활성화에너지만 낮추고 평형은 바꾸지 않는다.")]
DEFERRED = {}
SECTIONS = [section("enzyme", "개념", "효소",
                    T("t-barrier", "f1", "효소는 활성화에너지를 낮춘다.")
                    + T("t-balance", "f2", "반응의 평형은 바꾸지 않는다.")
                    + R("효소가 바꾸지 않는 것은?", "반응의 평형"))]
BOUNDARY = '<section class="card" id="scope-boundary" data-role="boundary"><p>이번 범위 밖 없음</p></section>'
META = dict(note="note.md", output_stem="note-eli5-complete", title="효소 가이드",
            quiz_sources={"2강": dict(source_id="quiz", path="quiz.txt", label="2강 합본")},
            groups=[("enzyme", "효소")], header_html="<header>{total}문항</header>",
            scope_notes_html="<p>범위 설명</p>", footer="끝")
'''


def build(base: Path, guide: str = GUIDE, *extra: str) -> tuple[int, str]:
    (base / "note.md").write_text(NOTE, encoding="utf-8")
    (base / "quiz.txt").write_text("2강 6: 효소에 대한 설명 중 틀린 것은?\n", encoding="utf-8")
    (base / "guide.py").write_text(guide, encoding="utf-8")
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        rc = build_main([str(base / "guide.py"), "--out-dir", str(base), *extra])
    return rc, output.getvalue()


class BuildGuideTests(unittest.TestCase):
    def test_built_guide_passes_draft_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            rc, output = build(base)
            self.assertEqual(rc, 0, output)
            errors = run_coverage(base / "note-eli5-complete.html", base / "note-eli5-complete.coverage.json",
                                  "draft", base / "note-eli5-complete.question-scope.json")
            self.assertEqual(errors, [])

    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            build(base)
            first = (base / "note-eli5-complete.html").read_bytes()
            build(base)
            self.assertEqual(first, (base / "note-eli5-complete.html").read_bytes())

    def test_fact_without_visible_teaching_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            rc, output = build(Path(directory), GUIDE.replace('T("t-balance", "f2", "반응의 평형은 바꾸지 않는다.")', '""'))
            self.assertEqual(rc, 1)
            self.assertIn("fact not taught in html: f2", output)

    def test_refuses_to_overwrite_an_html_it_did_not_build(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "note-eli5-complete.html").write_text("<!doctype html>수작업", encoding="utf-8")
            rc, output = build(base)
            self.assertEqual(rc, 1)
            self.assertIn("refusing to overwrite", output)

    def test_0910_data_reproduces_the_reviewed_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = build_main([str(ROOT / "정리노트/eli5/src/0910/guide.py"), "--out-dir", directory])
            self.assertEqual(rc, 0, output.getvalue())
            self.assertEqual((Path(directory) / "0910-eli5.html").read_bytes(),
                             (ROOT / "정리노트/eli5/0910-eli5.html").read_bytes())


if __name__ == "__main__":
    unittest.main()
