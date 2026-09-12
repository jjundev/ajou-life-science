import hashlib
import tempfile
import unittest
from pathlib import Path

from study_guide_fixture import case
from coverage_model import inventory_digest, validate_inventory


def with_external_block(base: Path, source_id: str, block: dict | None = None) -> dict:
    """Fixture plus one supplement fact that no note line states."""
    data = case(base)
    ref = "강의노트: 비타민 등의 유기보조 인자들: 조효소(coenzyme)\n"
    (base / "ref.txt").write_text(ref, encoding="utf-8")
    inventory = data["inventory"]
    inventory["sources"].append({
        "id": "ref", "path": "ref.txt", "role": "reference",
        "sha256": hashlib.sha256(ref.encode()).hexdigest(), "read_status": "read",
    })
    inventory["blocks"].append(block or {
        "id": "sup", "kind": "supplement", "fact_ids": ["f3"],
        "reason": "연결 문항을 풀기 위한 강의노트 보충",
    })
    inventory["facts"].append({
        "id": "f3", "block_id": "sup", "statement": "비타민 등 유기 보조인자를 조효소라 한다.",
        "qualifiers": [], "concept_id": "enzyme", "scope": "supplement",
        "evidence": {"source_id": source_id, "locator": "p1", "quote": "조효소"},
    })
    data["inventory_sha256"] = inventory_digest(inventory)
    return data


class ExternalBlockTests(unittest.TestCase):
    def test_supplement_fact_from_a_reference_needs_no_note_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.assertEqual(validate_inventory(with_external_block(base, "ref"), base), [])

    def test_external_block_fact_cannot_cite_the_note(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            errors = validate_inventory(with_external_block(base, "note"), base)
            self.assertIn("external block fact must cite a non-note source: f3", errors)

    def test_external_block_needs_a_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            block = {"id": "sup", "kind": "supplement", "fact_ids": ["f3"], "reason": ""}
            errors = validate_inventory(with_external_block(base, "ref", block), base)
            self.assertIn("external block needs reason: sup", errors)

    def test_teaching_block_still_needs_note_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            block = {"id": "sup", "kind": "teaching", "fact_ids": ["f3"], "reason": ""}
            data = with_external_block(base, "ref", block)
            data["inventory"]["facts"][-1]["scope"] = "teaching"
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn("invalid source range: sup", validate_inventory(data, base))


if __name__ == "__main__":
    unittest.main()
