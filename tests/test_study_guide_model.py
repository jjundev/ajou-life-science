import tempfile
import unittest
from pathlib import Path
from study_guide_fixture import case
from coverage_model import inventory_digest, validate_inventory


class InventoryTests(unittest.TestCase):
    def test_source_fact_without_a_question_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            self.assertEqual(validate_inventory(data, base), [])
            data["inventory"]["blocks"].pop(1)
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn("uncovered source line: 3", validate_inventory(data, base))

    def test_changed_source_invalidates_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            (base / "note.md").write_text("다른 내용", encoding="utf-8")
            self.assertIn("source hash mismatch: note", validate_inventory(data, base))

    def test_malformed_input_is_an_error_list(self):
        with tempfile.TemporaryDirectory() as directory:
            for data in ([], {}, {"schema_version": 2}, {"schema_version": 1, "inventory": None}):
                with self.subTest(data=data):
                    self.assertTrue(validate_inventory(data, Path(directory)))

    def test_rejects_broken_inventory_links(self):
        changes = [
            lambda i: i["facts"].append(dict(i["facts"][0])),
            lambda i: i["blocks"][1].update(start=0),
            lambda i: i["blocks"][1].update(start=1),
            lambda i: i["facts"][0].update(concept_id="missing"),
            lambda i: i["concepts"][0].update(prerequisites=["enzyme"]),
            lambda i: i["sources"][1].update(read_status="unread"),
            lambda i: i["blocks"][0].update(reason=""),
            lambda i: i["questions"][0].update(source_id="note"),
        ]
        for change in changes:
            with tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                data = case(base)
                change(data["inventory"])
                data["inventory_sha256"] = inventory_digest(data["inventory"])
                self.assertTrue(validate_inventory(data, base))

    def test_metadata_cannot_swallow_summary_and_review_facts(self):
        from coverage_model import metadata_content_errors

        note = (Path(__file__).resolve().parents[1] / "정리노트/0910.md").read_text(
            encoding="utf-8"
        ).splitlines()
        blocks = [{
            "id": "bad-meta", "start": 1, "end": 29, "kind": "metadata",
            "fact_ids": [], "reason": "제목과 안내",
        }]
        errors = metadata_content_errors(note, blocks)
        self.assertIn("metadata contains learning content: bad-meta line 11", errors)
        self.assertIn("metadata contains learning content: bad-meta line 22", errors)

    def test_v2_requires_atomic_fact_kinds(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            data["schema_version"] = 2
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn("v2 fact missing kind: f1", validate_inventory(data, base))

    def test_process_fact_requires_structured_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            data["schema_version"] = 2
            for fact in data["inventory"]["facts"]:
                fact.update(kind="definition")
            data["inventory"]["facts"][0].update(kind="process_step", dimensions={})
            question = data["inventory"]["questions"][0]
            question.update(
                format="multiple_choice", requirements=["f2"], grading="single",
                answerability={
                    "teaching_target_ids": ["fact-balance"],
                    "option_diagnostics": {"1": "오답 근거"},
                },
            )
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn(
                "process fact missing dimension: f1/location",
                validate_inventory(data, base),
            )

    def test_question_map_is_not_metadata_and_must_name_real_questions(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            data["inventory"]["blocks"].append({
                "id": "qmap", "start": 1, "end": 1, "kind": "question_map",
                "fact_ids": [], "question_ids": ["2강:6"], "reason": "",
            })
            data["inventory"]["blocks"][0]["start"] = 2
            data["inventory"]["blocks"][0]["end"] = 2
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            errors = validate_inventory(data, base)
            self.assertNotIn("invalid block kind: qmap", errors)
            self.assertNotIn("content block needs facts: qmap", errors)
            data["inventory"]["blocks"][-1]["question_ids"] = ["2강:99"]
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn(
                "question_map references unknown question: qmap/2강:99",
                validate_inventory(data, base),
            )
