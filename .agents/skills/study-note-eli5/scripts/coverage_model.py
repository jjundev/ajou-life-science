"""Coverage-manifest validation for Study Note ELI5 artifacts."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

SOURCE_ROLES = {"note", "quiz", "reference"}
READ_STATES = {"read", "unread", "missing"}
BLOCK_KINDS = {
    "teaching", "review", "supplement", "boundary", "metadata", "question_map"
}
SCOPES = {"teaching", "review", "supplement", "deferred"}
QUESTION_STATES = {"included", "review", "deferred"}
FACT_KINDS = {
    "definition", "structure", "process_step", "quantity", "direction",
    "condition", "exception", "contrast",
}


EXTERNAL_BLOCK_KINDS = {"supplement", "review"}


def is_external(block: dict) -> bool:
    """A supplement/review block with no note lines; its facts cite reference sources."""
    return block.get("kind") in EXTERNAL_BLOCK_KINDS and "start" not in block and "end" not in block


def inventory_digest(inventory: dict) -> str:
    value = json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _objects(values: Any, label: str, errors: list[str]) -> list[dict]:
    if not isinstance(values, list):
        errors.append(f"{label} must be a list")
        return []
    result = []
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            errors.append(f"{label}[{index}] must be an object")
        else:
            result.append(value)
    return result


def shape_errors(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["coverage must be an object"]
    errors: list[str] = []
    if data.get("schema_version") not in {1, 2}:
        errors.append("unsupported schema_version")
    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        errors.append("inventory must be an object")
        return errors
    if not _nonempty(inventory.get("main_source")):
        errors.append("main_source must be a nonempty string")
    if not _nonempty(data.get("inventory_sha256")):
        errors.append("inventory_sha256 must be a nonempty string")
    for label in ("sources", "blocks", "facts", "concepts", "questions"):
        for item in _objects(inventory.get(label), label, errors):
            if not _nonempty(item.get("id")):
                errors.append(f"{label} item has empty id")
    if not isinstance(data.get("mappings"), list):
        errors.append("mappings must be a list")
    if not isinstance(data.get("review"), dict):
        errors.append("review must be an object")
    return errors

def v2_errors(data: dict) -> list[str]:
    if data.get("schema_version") != 2:
        return []
    errors = []
    inventory = data["inventory"]
    fact_ids = {fact.get("id") for fact in inventory["facts"]}
    for fact in inventory["facts"]:
        ident = fact.get("id")
        kind = fact.get("kind")
        if kind not in FACT_KINDS:
            errors.append(f"v2 fact missing kind: {ident}")
        if kind == "process_step":
            dimensions = fact.get("dimensions")
            if not isinstance(dimensions, dict):
                dimensions = {}
            for key in ("location", "input", "output"):
                value = dimensions.get(key)
                if value in (None, "", []):
                    errors.append(f"process fact missing dimension: {ident}/{key}")
    for question in inventory["questions"]:
        if question.get("status") == "deferred":
            continue
        ident = question.get("id")
        if question.get("format") not in {"multiple_choice", "short_answer"}:
            errors.append(f"v2 question missing format: {ident}")
        requirements = question.get("requirements")
        if not isinstance(requirements, list) or not requirements:
            errors.append(f"v2 question missing requirements: {ident}")
        elif any(requirement not in fact_ids for requirement in requirements):
            errors.append(f"v2 question unknown requirement: {ident}")
        if question.get("grading") not in {"single", "ambiguous", "rubric"}:
            errors.append(f"v2 question missing grading: {ident}")
        if not isinstance(question.get("answerability"), dict):
            errors.append(f"v2 question missing answerability: {ident}")
    return errors


def _ids(items: list[dict], label: str, errors: list[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        ident = item.get("id")
        if not _nonempty(ident):
            continue
        if ident in result:
            errors.append(f"duplicate {label} id: {ident}")
        result[ident] = item
    return result


def reference_errors(inventory: dict) -> list[str]:
    errors: list[str] = []
    sources = _ids(inventory["sources"], "source", errors)
    blocks = _ids(inventory["blocks"], "block", errors)
    facts = _ids(inventory["facts"], "fact", errors)
    concepts = _ids(inventory["concepts"], "concept", errors)
    questions = _ids(inventory["questions"], "question", errors)
    main = sources.get(inventory["main_source"])
    if main is None or main.get("role") != "note":
        errors.append("main_source must reference a note source")
    for source in sources.values():
        if source.get("role") not in SOURCE_ROLES:
            errors.append(f"invalid source role: {source.get('id')}")
        if source.get("read_status") not in READ_STATES:
            errors.append(f"invalid source read_status: {source.get('id')}")
        for key in ("path", "sha256"):
            if not _nonempty(source.get(key)):
                errors.append(f"source {source.get('id')} missing {key}")
    claimed: set[str] = set()
    scope_by_kind = {"teaching": "teaching", "review": "review", "supplement": "supplement", "boundary": "deferred"}
    for block in blocks.values():
        kind = block.get("kind")
        if kind not in BLOCK_KINDS:
            errors.append(f"invalid block kind: {block.get('id')}")
        fact_ids = block.get("fact_ids")
        if not isinstance(fact_ids, list) or any(not _nonempty(value) for value in fact_ids):
            errors.append(f"invalid fact_ids: {block.get('id')}")
            fact_ids = []
        if kind == "metadata":
            if fact_ids or not _nonempty(block.get("reason")):
                errors.append(f"metadata block needs empty facts and reason: {block.get('id')}")
        elif kind == "question_map":
            question_ids = block.get("question_ids")
            if fact_ids or not isinstance(question_ids, list) or not question_ids:
                errors.append(f"question_map needs question_ids: {block.get('id')}")
            else:
                for question_id in question_ids:
                    if question_id not in questions:
                        errors.append(
                            f"question_map references unknown question: "
                            f"{block.get('id')}/{question_id}"
                        )
        elif not fact_ids:
            errors.append(f"content block needs facts: {block.get('id')}")
        if is_external(block):
            if not _nonempty(block.get("reason")):
                errors.append(f"external block needs reason: {block.get('id')}")
            for fact_id in fact_ids:
                evidence = facts.get(fact_id, {}).get("evidence")
                source_id = evidence.get("source_id") if isinstance(evidence, dict) else None
                if source_id == inventory["main_source"] or source_id not in sources:
                    errors.append(f"external block fact must cite a non-note source: {fact_id}")
        for fact_id in fact_ids:
            if fact_id not in facts:
                errors.append(f"unknown fact in block: {block.get('id')}/{fact_id}")
                continue
            if fact_id in claimed:
                errors.append(f"fact in multiple blocks: {fact_id}")
            claimed.add(fact_id)
            if facts[fact_id].get("block_id") != block.get("id"):
                errors.append(f"fact block mismatch: {fact_id}")
            if kind in scope_by_kind and facts[fact_id].get("scope") != scope_by_kind[kind]:
                errors.append(f"fact scope mismatch: {fact_id}")
    for fact in facts.values():
        ident = fact.get("id")
        if ident not in claimed:
            errors.append(f"fact not claimed by block: {ident}")
        if fact.get("block_id") not in blocks:
            errors.append(f"fact references unknown block: {ident}")
        if fact.get("scope") not in SCOPES:
            errors.append(f"invalid fact scope: {ident}")
        if not _nonempty(fact.get("statement")):
            errors.append(f"fact missing statement: {ident}")
        if not isinstance(fact.get("qualifiers"), list) or any(not isinstance(x, str) for x in fact.get("qualifiers", [])):
            errors.append(f"invalid qualifiers: {ident}")
        concept_id = fact.get("concept_id")
        if fact.get("scope") != "deferred" and concept_id not in concepts:
            errors.append(f"unknown concept: {ident}/{concept_id}")
        evidence = fact.get("evidence")
        if not isinstance(evidence, dict) or evidence.get("source_id") not in sources:
            errors.append(f"invalid fact evidence: {ident}")
        elif not _nonempty(evidence.get("locator")) or not _nonempty(evidence.get("quote")):
            errors.append(f"incomplete fact evidence: {ident}")
    for concept in concepts.values():
        if not _nonempty(concept.get("title")) or not isinstance(concept.get("prerequisites"), list):
            errors.append(f"invalid concept: {concept.get('id')}")
        for prerequisite in concept.get("prerequisites", []):
            if prerequisite not in concepts or prerequisite == concept.get("id"):
                errors.append(f"invalid prerequisite: {concept.get('id')}/{prerequisite}")
    def visit(ident: str, seen: set[str]) -> bool:
        if ident in seen:
            return True
        return any(visit(item, seen | {ident}) for item in concepts[ident].get("prerequisites", []) if item in concepts)
    for ident in concepts:
        if visit(ident, set()):
            errors.append(f"cyclic prerequisite: {ident}")
    for question in questions.values():
        ident = question.get("id")
        source = sources.get(question.get("source_id"))
        fact_ids = question.get("fact_ids")
        if source is None or source.get("role") != "quiz":
            errors.append(f"question source must be quiz: {ident}")
        if question.get("status") not in QUESTION_STATES or not isinstance(fact_ids, list) or not fact_ids:
            errors.append(f"invalid question: {ident}")
            continue
        if any(fact_id not in facts for fact_id in fact_ids):
            errors.append(f"question has unknown fact: {ident}")
        if question.get("status") == "deferred":
            if not _nonempty(question.get("reason")):
                errors.append(f"deferred question needs reason: {ident}")
        elif not any(facts.get(fact_id, {}).get("scope") != "deferred" for fact_id in fact_ids):
            errors.append(f"active question needs active fact: {ident}")
        if not _nonempty(question.get("locator")):
            errors.append(f"question missing locator: {ident}")
    return errors


def line_errors(lines: list[str], blocks: list[dict]) -> list[str]:
    errors: list[str] = []
    covered: Counter[int] = Counter()
    for block in blocks:
        if is_external(block):
            continue
        start, end = block.get("start"), block.get("end")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            errors.append(f"invalid source range: {block.get('id')}")
            continue
        covered.update(range(start, end + 1))
    for number, line in enumerate(lines, 1):
        if line.strip() and not covered[number]:
            errors.append(f"uncovered source line: {number}")
        if covered[number] > 1:
            errors.append(f"overlapping source line: {number}")
    return errors

def metadata_content_errors(lines: list[str], blocks: list[dict]) -> list[str]:
    """Reject learning assertions hidden inside broad metadata ranges."""
    errors = []
    table_headers = {
        index for index in range(len(lines) - 1)
        if lines[index].lstrip().startswith("|")
        and re.fullmatch(r"\s*\|[\s:|\-]+\|\s*", lines[index + 1])
    }
    for block in blocks:
        if block.get("kind") != "metadata":
            continue
        start, end = block.get("start"), block.get("end")
        if type(start) is not int or type(end) is not int:
            continue
        for number in range(start, min(end, len(lines)) + 1):
            line = lines[number - 1].strip()
            allowed = (
                not line
                or bool(re.match(r"^#{1,6}\s", line))
                or line in {">", "---"}
                or bool(re.fullmatch(r"\|[\s:|\-]+\|", line))
                or number - 1 in table_headers
                or (line.startswith(">") and ("주 자료:" in line or "문제 풀이는" in line))
            )
            if not allowed:
                errors.append(f"metadata contains learning content: {block.get('id')} line {number}")
    return errors


def validate_inventory(data: dict, base: Path) -> list[str]:
    errors = shape_errors(data)
    if errors:
        return errors
    inventory = data["inventory"]
    errors.extend(reference_errors(inventory))
    errors.extend(v2_errors(data))
    if data["inventory_sha256"] != inventory_digest(inventory):
        errors.append("inventory hash mismatch")
    sources = {source["id"]: source for source in inventory["sources"] if _nonempty(source.get("id"))}
    main_lines: list[str] | None = None
    for source in sources.values():
        source_id = source["id"]
        if source.get("read_status") != "read":
            errors.append(f"source not read: {source_id}")
        try:
            path = (base / source["path"]).resolve()
            if file_digest(path) != source.get("sha256"):
                errors.append(f"source hash mismatch: {source_id}")
            if source_id == inventory["main_source"]:
                main_lines = path.read_text(encoding="utf-8").splitlines()
                errors.extend(line_errors(main_lines, inventory["blocks"]))
                errors.extend(metadata_content_errors(main_lines, inventory["blocks"]))
        except (OSError, UnicodeError) as error:
            errors.append(f"cannot read source {source_id}: {error}")
    if main_lines is not None:
        block_by_id = {block.get("id"): block for block in inventory["blocks"]}
        for fact in inventory["facts"]:
            evidence = fact.get("evidence", {})
            if evidence.get("source_id") == inventory["main_source"]:
                block = block_by_id.get(fact.get("block_id"))
                if block and type(block.get("start")) is int and type(block.get("end")) is int:
                    text = "\n".join(main_lines[block["start"] - 1:block["end"]])
                    if evidence.get("quote") not in text:
                        errors.append(f"fact quote not in source block: {fact.get('id')}")
    return errors
