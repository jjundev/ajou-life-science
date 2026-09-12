import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from study_guide_fixture import HTML, case, reviewed
from verify_guide import main, validate_review
from question_scope import extract_question_scope, scope_digest
from coverage_model import inventory_digest

class CliTests(unittest.TestCase):
    def test_structure_without_scope_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = case(base); artifact = base / "guide.html"; manifest = base / "guide.json"
            artifact.write_text(HTML, encoding="utf-8"); manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(artifact), "--coverage", str(manifest), "--phase", "structure"]), 1)
            self.assertIn("coverage validation requires --scope", output.getvalue())
            self.assertTrue(validate_review(data, artifact))

    def test_html_edit_invalidates_review(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = reviewed(case(base), HTML); artifact = base / "guide.html"
            artifact.write_text(HTML, encoding="utf-8")
            self.assertEqual(validate_review(data, artifact), [])
            artifact.write_text(HTML.replace("평형은 바꾸지 않습니다.", "평형을 바꿉니다."), encoding="utf-8")
            self.assertIn("review artifact hash mismatch", validate_review(data, artifact))

    def test_open_conflict_blocks_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = reviewed(case(base), HTML); artifact = base / "guide.html"
            artifact.write_text(HTML, encoding="utf-8"); data["review"]["conflicts"] = [{"id": "c1", "status": "open"}]
            self.assertIn("open conflict: c1", validate_review(data, artifact))

    def test_legacy_pass_is_labeled_structure_only(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "old.html"
            artifact.write_text('<!doctype html><html><body>30초 문항별 범위 <b class="qnum">6</b>' + "설명 " * 400 + "</body></html>", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output): self.assertEqual(main([str(artifact), "--questions", "6"]), 0)
            self.assertIn("LEGACY STRUCTURE ONLY", output.getvalue())

    def test_complete_coverage_requires_scope_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = reviewed(case(base), HTML)
            artifact, manifest = base / "guide.html", base / "guide.json"
            artifact.write_text(HTML, encoding="utf-8")
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(artifact), "--coverage", str(manifest)]), 1)
            self.assertIn("coverage validation requires --scope", output.getvalue())

    def test_real_0910_partial_manifest_reports_46_missing(self):
        root = Path(__file__).resolve().parents[1]
        note = root / "정리노트/0910.md"
        base_questions = extract_question_scope(note.read_text(encoding="utf-8"))
        lock = {
            "schema_version": 1,
            "source": {"path": "0910.md", "sha256": __import__("hashlib").sha256(note.read_bytes()).hexdigest()},
            "base_questions": list(base_questions.values()),
            "overrides": [],
            "questions": list(base_questions.values()),
        }
        lock["scope_sha256"] = scope_digest(lock)
        scope = root / "정리노트/0910.question-scope.test.json"
        try:
            scope.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = main([
                    str(root / "정리노트/0910-eli5-audited.html"),
                    "--coverage", str(root / "정리노트/0910-eli5-audited.coverage.json"),
                    "--scope", str(scope), "--phase", "draft",
                ])
            self.assertEqual(rc, 1)
            self.assertIn("question universe mismatch: 46 missing", output.getvalue())
        finally:
            scope.unlink(missing_ok=True)

    def test_partial_delivery_needs_explicit_filename_manifest_and_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = case(base)
            scope_questions = [{"id": "2강:6", "status": "included", "source_locator": "문항"}]
            lock = {
                "schema_version": 1,
                "source": {"path": "note.md", "sha256": __import__("hashlib").sha256((base / "note.md").read_bytes()).hexdigest()},
                "base_questions": scope_questions,
                "overrides": [],
                "questions": scope_questions,
            }
            lock["scope_sha256"] = scope_digest(lock)
            artifact, manifest, scope = base / "guide-partial.html", base / "guide.json", base / "scope.json"
            artifact.write_text(HTML, encoding="utf-8")
            data["delivery_mode"] = "partial"
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            scope.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(artifact), "--coverage", str(manifest), "--scope", str(scope), "--phase", "draft"]), 1)
            self.assertIn("partial delivery requires explicit --allow-partial", output.getvalue())

    def test_complete_rejects_unaudited_question_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(__file__).resolve().parents[1]
            note = root / "정리노트/0910.md"
            questions = extract_question_scope(note.read_text(encoding="utf-8"))
            scoped = list(questions.values())
            lock = {
                "schema_version": 1,
                "source": {"path": str(note), "sha256": __import__("hashlib").sha256(note.read_bytes()).hexdigest()},
                "base_questions": scoped, "overrides": [], "questions": scoped,
            }
            lock["scope_sha256"] = scope_digest(lock)
            scope = Path(directory) / "scope.json"
            scope.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([
                    str(root / "정리노트/0910-eli5-audited.html"),
                    "--coverage", str(root / "정리노트/0910-eli5-audited.coverage.json"),
                    "--scope", str(scope),
                ]), 1)
            self.assertIn("scope question audit pending: 2강:1", output.getvalue())

    def test_v2_review_requires_question_by_question_solvability_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = reviewed(case(base), HTML)
            data["schema_version"] = 2
            for fact in data["inventory"]["facts"]:
                fact["kind"] = "definition"
            data["inventory"]["questions"][0].update({
                "format": "multiple_choice", "option_count": 2,
                "requirements": ["f2"],
                "grading": "single",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "평형과 속도 구분"},
                },
            })
            artifact = base / "guide.html"
            artifact.write_text(HTML.replace(
                'data-question-id="2강:6"',
                'data-question-id="2강:6" data-format="multiple_choice"',
            ), encoding="utf-8")
            data["review"]["artifact_sha256"] = __import__("hashlib").sha256(artifact.read_bytes()).hexdigest()
            self.assertIn(
                "review incomplete: question_checks",
                validate_review(data, artifact),
            )

    def test_minimal_v2_guide_can_pass_complete_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); data = case(base)
            note = (base / "note.md").read_text(encoding="utf-8")
            note += "\n## 부록. 문항 ↔ 개념 매핑\n\n| 출처 | # | 내용 |\n|---|---|---|\n| 2강 | 6 | 효소 |\n"
            (base / "note.md").write_text(note, encoding="utf-8")
            data["schema_version"] = 2
            data["inventory"]["sources"][0]["sha256"] = __import__("hashlib").sha256(note.encode()).hexdigest()
            data["inventory"]["blocks"].extend([
                {"id": "appendix-meta", "start": 6, "end": 10, "kind": "metadata", "fact_ids": [], "reason": "부록 구조"},
                {"id": "appendix-map", "start": 11, "end": 11, "kind": "question_map", "fact_ids": [], "question_ids": ["2강:6"], "reason": ""},
            ])
            for fact in data["inventory"]["facts"]:
                fact["kind"] = "definition"
            question = data["inventory"]["questions"][0]
            question.update({
                "format": "multiple_choice", "option_count": 2,
                "requirements": ["f2"],
                "grading": "single",
                "answerability": {
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {
                        "1": "평형과 속도를 혼동",
                        "2": "활성화에너지 감소",
                    },
                },
            })
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            html = HTML.replace(
                'data-question-id="2강:6"',
                'data-question-id="2강:6" data-format="multiple_choice"',
            )
            data = reviewed(data, html)
            data["review"]["question_checks"] = [{
                "question_id": "2강:6", "status": "pass",
                "teaching_target_ids": ["fact-balance"],
                "used_external_knowledge": False,
                "option_or_rubric_check": "각 선택지를 본문 근거로 판정",
                "evidence": "정답을 열기 전에 평형 불변 설명으로 판정",
            }]
            scoped = extract_question_scope(note)
            audited = dict(scoped["2강:6"])
            audited.update({
                "audit_status": "confirmed", "format": "multiple_choice",
                "option_count": 2,
                "grading": "single", "requirements": ["f2"],
                "source_evidence": {
                    "source_path": "quiz.txt", "page": "1",
                    "quote": "효소에 대한 설명 중 틀린 것은",
                },
            })
            lock = {
                "schema_version": 1,
                "source": {"path": "note.md", "sha256": __import__("hashlib").sha256(note.encode()).hexdigest()},
                "base_questions": list(scoped.values()),
                "overrides": [], "questions": [audited],
            }
            lock["scope_sha256"] = scope_digest(lock)
            artifact, manifest, scope = base / "guide.html", base / "guide.json", base / "scope.json"
            artifact.write_text(html, encoding="utf-8")
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            scope.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main([
                    str(artifact), "--coverage", str(manifest),
                    "--scope", str(scope), "--phase", "complete",
                ])
            self.assertEqual(result, 0, output.getvalue())
            self.assertIn("PASS: complete question universe", output.getvalue())
