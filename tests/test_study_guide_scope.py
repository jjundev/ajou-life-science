import json
import sys
import unittest
from pathlib import Path

from study_guide_fixture import ROOT

SCRIPTS = ROOT / ".agents/skills/study-note-eli5/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from question_scope import (  # noqa: E402
    apply_overrides,
    extract_question_scope,
    scope_digest,
    validate_question_coverage,
    validate_scope_audit,
    validate_scope_lock,
)
from build_question_scope import main as build_scope  # noqa: E402


class QuestionScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note_path = ROOT / "정리노트/0910.md"
        cls.markdown = cls.note_path.read_text(encoding="utf-8")

    def test_0910_source_defines_all_52_question_ids(self):
        base = extract_question_scope(self.markdown)
        self.assertEqual(len(base), 52)
        self.assertEqual(
            {status: sum(item["status"] == status for item in base.values())
             for status in ("included", "review", "deferred")},
            {"included": 30, "review": 6, "deferred": 16},
        )
        self.assertTrue(all(
            item.get("reason")
            for item in base.values() if item["status"] == "deferred"
        ))

    def test_single_source_numeric_mapping_keeps_source_qualified_ids(self):
        markdown = """# 0917

원문: `23, 24 소스/3강 합본.pdf`

> 보류: 3강 4 — 다음 회차 단계별 분열

## 부록. 문항 ↔ 개념 매핑

| 문항 번호 | 질문 요약 | 노트 위치 | 상태 |
|---:|---|---|---|
| 1 | 간기 | §1 | 포함 |
| 2 | 확인점 | §1 | 포함 |
"""
        scope = extract_question_scope(markdown)
        self.assertEqual(set(scope), {"3강:1", "3강:2", "3강:4"})
        self.assertEqual(scope["3강:1"]["source_locator"], "문항 매핑표")
        self.assertEqual(scope["3강:4"]["status"], "deferred")

    def test_evidenced_override_reclassifies_without_deleting_id(self):
        base = extract_question_scope(self.markdown)
        overrides = [{
            "id": "2강:13", "from": "included", "to": "deferred",
            "reason": "원본 PDF 문항은 광합성 반응식이며 이번 범위 밖",
            "evidence": {
                "source_path": "23, 24 소스/2강 합본.pdf",
                "page": "1-2", "quote": "다음의 화학 반응 중 광합성을",
            },
        }]
        final, errors = apply_overrides(base, overrides)
        self.assertEqual(errors, [])
        self.assertEqual(len(final), 52)
        self.assertEqual(final["2강:13"]["status"], "deferred")
        self.assertEqual(sum(item["status"] == "included" for item in final.values()), 29)
        self.assertEqual(sum(item["status"] == "deferred" for item in final.values()), 17)

    def test_six_declared_questions_cannot_cover_52_source_questions(self):
        scope = extract_question_scope(self.markdown)
        coverage = json.loads(
            (ROOT / "tests/fixtures/study_guide/0910-eli5-audited.coverage.json").read_text(encoding="utf-8")
        )
        errors = validate_question_coverage(coverage, scope)
        self.assertIn("question universe mismatch: 46 missing, 0 unexpected", errors)
        self.assertIn("missing question: 1강:7", errors)
        self.assertIn("missing question: 2강:44", errors)

    def test_scope_lock_is_bound_to_current_note_and_evidence(self):
        base = extract_question_scope(self.markdown)
        lock = {
            "schema_version": 1,
            "source": {"path": "0910.md", "sha256": ""},
            "base_questions": list(base.values()),
            "overrides": [],
            "questions": list(base.values()),
        }
        from coverage_model import file_digest
        lock["source"]["sha256"] = file_digest(self.note_path)
        lock["scope_sha256"] = scope_digest(lock)
        self.assertEqual(validate_scope_lock(lock, self.note_path), [])
        lock["questions"].pop()
        self.assertTrue(validate_scope_lock(lock, self.note_path))

    def test_builder_writes_a_valid_lock_with_override(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "0910.question-scope.json"
            override = Path(directory) / "overrides.json"
            audits = Path(directory) / "audits.json"
            override.write_text(json.dumps([{
                "id": "2강:13", "from": "included", "to": "deferred",
                "reason": "원본 PDF 문항은 광합성 범위",
                "evidence": {
                    "source_path": "2강 합본.pdf", "page": "1-2",
                    "quote": "광합성을 가장 적절히",
                },
            }], ensure_ascii=False), encoding="utf-8")
            audits.write_text(json.dumps({
                "2강:1": {
                    "audit_status": "confirmed",
                    "format": "multiple_choice", "option_count": 4,
                    "grading": "ambiguous", "requirements": ["atp", "heat"],
                    "source_evidence": {
                        "source_path": "2강 합본.pdf", "page": "1",
                        "quote": "방출된 에너지는 어디로 가는가",
                    },
                }
            }, ensure_ascii=False), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_scope([
                    str(self.note_path), str(output), "--overrides", str(override),
                    "--audits", str(audits),
                ]), 0)
            lock = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(validate_scope_lock(lock, self.note_path), [])
            self.assertEqual(len(lock["questions"]), 52)
            q1 = next(item for item in lock["questions"] if item["id"] == "2강:1")
            self.assertEqual(q1["requirements"], ["atp", "heat"])
            self.assertIn(
                "scope question audit pending: 1강:7",
                validate_scope_audit(lock),
            )

    def test_coverage_cannot_shrink_question_requirements(self):
        scope = {
            "2강:20": {
                "id": "2강:20", "status": "included",
                "format": "multiple_choice", "grading": "single",
                "requirements": ["glycolysis-net", "respiration-total"],
            }
        }
        coverage = {
            "inventory": {"questions": [{
                "id": "2강:20", "status": "included",
                "requirements": ["glycolysis-net"],
            }]}
        }
        self.assertIn(
            "question requirements mismatch: 2강:20",
            validate_question_coverage(coverage, scope),
        )

    def test_missing_scope_source_returns_error_instead_of_traceback(self):
        lock = {
            "schema_version": 1,
            "source": {"path": "missing.md", "sha256": "0" * 64},
            "base_questions": [], "overrides": [], "questions": [],
            "scope_sha256": "",
        }
        errors = validate_scope_lock(lock, Path("/definitely/missing/note.md"))
        self.assertTrue(errors)
        self.assertIn("cannot read scope source", errors[0])


if __name__ == "__main__":
    unittest.main()
