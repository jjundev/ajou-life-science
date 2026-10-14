"""등록 보류 문항도 본문 개념 전달에서 사라지지 않아야 한다."""
import tempfile
import unittest
from pathlib import Path

from _util import SKILL
import assemble


class TestNoteFeedbackFlow(unittest.TestCase):
    def test_raw_only_feedback_reaches_planning_and_writer(self):
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        rules = (SKILL / "references/note-feedback.md").read_text(encoding="utf-8")
        writer = (SKILL / "references/content-rules.md").read_text(encoding="utf-8")
        self.assertIn("references/note-feedback.md", entry)
        self.assertIn("questions.json", rules)
        self.assertIn("partA", rules)
        self.assertIn("note-feedback-audit.md", writer)
        self.assertIn("카드 포함 여부", writer)

    def test_lite_checks_feedback_not_only_generated_cards(self):
        review = (SKILL / "references/review-prompt.md").read_text(encoding="utf-8")
        self.assertIn("## 본문 피드백 검토 (항상, lite 포함)", review)
        self.assertIn("note-feedback-audit.md", review)
        self.assertIn("본문 문장", review)

    def test_ch4_covers_all_sources_without_claiming_official_answers(self):
        repo = SKILL.parents[2]
        feedback = (repo / "웹과제/4장/note-feedback.md").read_text(encoding="utf-8")
        for n in range(1, 16):
            self.assertIn(f"### q{n:02d} ", feedback)
            self.assertIn(f"s{n:02d}", feedback)
        for term in ("공식 답 미확인", "세 대립유전자", "아들일 때", "분홍꽃", "수용체 수준"):
            self.assertIn(term, feedback)


class TestNoteFeedbackRecords(unittest.TestCase):
    def test_full_records_preserve_feedback_audit_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            run, out = Path(t) / "run", Path(t) / "out"
            run.mkdir()
            payload = "# 본문 피드백\n| 4장 q13 | s1-dominance | 적용 |\n".encode()
            (run / "note-feedback-audit.md").write_bytes(payload)
            assemble.save_pack_records(run, out, "full", [])
            self.assertEqual((out / ".pack/note-feedback-audit.md").read_bytes(), payload)

    def test_augment_cannot_replace_body_verification(self):
        with tempfile.TemporaryDirectory() as t:
            run, out = Path(t) / "run", Path(t) / "out"
            run.mkdir()
            pack = out / ".pack"
            pack.mkdir(parents=True)
            (pack / "note-feedback-audit.md").write_text("old body review", encoding="utf-8")
            (run / "note-feedback-audit.md").write_text("unapplied new feedback", encoding="utf-8")
            assemble.save_pack_records(run, out, "augment", [])
            self.assertEqual((pack / "note-feedback-audit.md").read_text(encoding="utf-8"), "old body review")


if __name__ == "__main__":
    unittest.main()
