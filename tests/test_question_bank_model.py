import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from question_bank_fixture import make_bank
from scripts.question_bank.model import (
    asset_payload,
    canonical_digest,
    load_bank,
    question_payload,
    resolve_local,
    validate_bank,
)


class BankModelTests(unittest.TestCase):
    def test_valid_draft_keeps_selected_answer_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)

            self.assertEqual(validate_bank(bank, base, repo_root=base), [])
            question = bank["questions"][0]
            self.assertEqual(question["observations"]["selected_option_id"], "B")
            self.assertEqual(question["analysis"]["answer_option_id"], "A")

    def test_answer_must_name_an_existing_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            bank["questions"][0]["analysis"]["answer_option_id"] = "Z"

            self.assertTrue(validate_bank(bank, base, repo_root=base))

    def test_every_option_needs_exactly_one_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            del bank["questions"][0]["analysis"]["option_diagnostics"]["B"]

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("diagnostic" in error for error in errors))

    def test_changed_source_bytes_fail_stored_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            (base / "raw/fixture.txt").write_text("changed", encoding="utf-8")

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("hash" in error for error in errors))

    def test_schema_rejects_unknown_version_and_extra_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            bank["schema_version"] = 2
            bank["unexpected"] = True

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("schema_version" in error for error in errors))
            self.assertTrue(any("unexpected" in error for error in errors))

    def test_duplicate_source_question_id_and_number_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            bank["sources"].append(copy.deepcopy(bank["sources"][0]))
            bank["questions"].append(copy.deepcopy(bank["questions"][0]))
            bank["assessment"]["expected_question_count"] = 2

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("source id" in error for error in errors))
            self.assertTrue(any("question id" in error for error in errors))
            self.assertTrue(any("question number" in error for error in errors))

    def test_question_numbers_cover_expected_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            bank["assessment"]["expected_question_count"] = 2

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("question numbers" in error for error in errors))

    def test_references_must_be_registered_and_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            question = bank["questions"][0]
            question["source_ids"] = ["missing"]
            question["observations"]["selected_source_id"] = "s1"
            question["original"]["content"].append(
                {"type": "figure", "asset_id": "missing-figure"}
            )
            bank["assessment"]["evidence_source_ids"] = ["missing"]
            bank["sources"][0]["path"] = "../outside.txt"

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("assessment source" in error for error in errors))
            self.assertTrue(any("question source" in error for error in errors))
            self.assertTrue(any("selected_source_id" in error for error in errors))
            self.assertTrue(any("figure asset" in error for error in errors))
            self.assertTrue(any("outside root" in error for error in errors))

    def test_unresolved_answer_has_no_resolved_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            analysis = bank["questions"][0]["analysis"]
            analysis["answer_status"] = "unresolved"
            analysis["grading"] = "unresolved"
            analysis["answer_option_id"] = "A"

            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any("unresolved" in error for error in errors))

    def test_verified_review_uses_fresh_file_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            question = bank["questions"][0]
            question["review"] = {
                "status": "verified",
                "payload_sha256": canonical_digest(
                    question_payload(bank, question, base, repo_root=base)
                ),
                "notes": "원본과 비교함",
            }
            self.assertEqual(validate_bank(bank, base, complete=True, repo_root=base), [])

            (base / "evidence.md").write_text("바뀐 근거", encoding="utf-8")
            errors = validate_bank(bank, base, complete=True, repo_root=base)
            self.assertTrue(any("review hash" in error for error in errors))

    def test_complete_rejects_pending_and_draft_allows_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)

            self.assertEqual(validate_bank(bank, base, repo_root=base), [])
            errors = validate_bank(bank, base, complete=True, repo_root=base)
            self.assertTrue(any("pending" in error for error in errors))

    def test_asset_payload_reads_sources_and_both_svg_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            (base / "image").mkdir()
            exam = base / "image/q.svg"
            explained = base / "image/q.explained.svg"
            exam.write_bytes(b"exam-v1")
            explained.write_bytes(b"explained-v1")
            asset = {
                "id": "figure-1",
                "exam": {
                    "path": "image/q.svg",
                    "sha256": hashlib.sha256(exam.read_bytes()).hexdigest(),
                    "alt": "문제 그림",
                },
                "explained": {
                    "path": "image/q.explained.svg",
                    "sha256": hashlib.sha256(explained.read_bytes()).hexdigest(),
                    "alt": "해설 그림",
                },
                "source_ids": ["s1"],
                "review": {
                    "status": "pending",
                    "payload_sha256": None,
                    "notes": None,
                },
            }
            bank["assets"].append(asset)
            bank["questions"][0]["original"]["content"].append(
                {"type": "figure", "asset_id": "figure-1"}
            )
            payload_before = asset_payload(bank, asset, base)
            exam.write_bytes(b"exam-v2")
            payload_after = asset_payload(bank, asset, base)

            self.assertNotEqual(payload_before, payload_after)
            self.assertTrue(
                any(
                    "exam" in error and "hash" in error
                    for error in validate_bank(bank, base, repo_root=base)
                )
            )

    def test_resolve_local_rejects_absolute_and_parent_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertEqual(
                resolve_local(base, "raw/a.txt"), (base / "raw/a.txt").resolve()
            )
            with self.assertRaisesRegex(ValueError, "absolute path"):
                resolve_local(base, "/tmp/a.txt")
            with self.assertRaisesRegex(ValueError, "outside root"):
                resolve_local(base, "../a.txt")

    def test_canonical_digest_is_sorted_compact_utf8_json(self):
        self.assertEqual(
            canonical_digest({"b": 1, "a": "한"}),
            "67f2fd255e411935d63adb1352ddb23efd6054c61d3131965ab2809e0c10d61f",
        )

    def test_load_bank_wraps_io_and_json_errors_with_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            missing = base / "missing.json"
            with self.assertRaisesRegex(ValueError, str(missing)):
                load_bank(missing, repo_root=base)
            invalid = base / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, str(invalid)):
                load_bank(invalid, repo_root=base)

    def test_load_bank_returns_data_without_mutating_input_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path, bank = make_bank(base)
            before = path.read_bytes()

            loaded = load_bank(path, repo_root=base)

            self.assertEqual(loaded, bank)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
