#!/usr/bin/env python3
"""Validate legacy or coverage-backed Study Note ELI5 guides."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from coverage_model import file_digest, validate_inventory
from guide_html import partial_delivery_errors, parse_guide, validate_html
from question_scope import (
    validate_question_coverage,
    validate_scope_audit,
    validate_scope_lock,
)

DEFAULT_MARKERS = ("30초", "문항별", "범위")

def legacy_errors(path: Path, questions: str | None, markers: list[str]) -> list[str]:
    if not path.is_file():
        return [f"missing artifact: {path}"]
    text = path.read_text(encoding="utf-8")
    errors = []
    if not text.lstrip().lower().startswith("<!doctype html>"): errors.append("artifact does not start with <!doctype html>")
    if "</html>" not in text.lower(): errors.append("artifact has no closing </html>")
    if len(text) < 1000: errors.append("artifact is unexpectedly short")
    for marker in (*DEFAULT_MARKERS, *markers):
        if marker not in text: errors.append(f"missing marker: {marker}")
    if questions:
        wanted = [item.strip() for item in questions.split(",") if item.strip()]
        found = [item.strip() for item in re.findall(r'class=["\']qnum["\'][^>]*>\s*([^<]+)', text)]
        missing = [item for item in wanted if item not in found]
        if missing: errors.append(f"missing question cards: {', '.join(missing)}")
        if len(found) != len(wanted): errors.append(f"question card count {len(found)} != expected {len(wanted)}")
    return errors

def fact_review_errors(data: dict) -> list[str]:
    checks = data.get("review", {}).get("fact_checks")
    facts = {fact["id"] for fact in data["inventory"]["facts"]}
    if not isinstance(checks, list): return ["review incomplete: fact_checks"]
    errors, seen = [], set()
    for check in checks:
        if not isinstance(check, dict) or check.get("fact_id") not in facts:
            errors.append("invalid fact review"); continue
        ident = check["fact_id"]
        if ident in seen: errors.append(f"duplicate fact review: {ident}")
        seen.add(ident)
        if check.get("status") != "pass" or not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
            errors.append(f"review incomplete: fact {ident}")
    errors.extend(f"review missing fact: {ident}" for ident in facts - seen)
    return errors

def conflict_review_errors(data: dict, artifact: Path) -> list[str]:
    conflicts = data.get("review", {}).get("conflicts")
    if not isinstance(conflicts, list): return ["review incomplete: conflicts"]
    guide, errors, seen = parse_guide(artifact.read_text(encoding="utf-8")), [], set()
    for conflict in conflicts:
        if not isinstance(conflict, dict) or not isinstance(conflict.get("id"), str) or not conflict["id"]:
            errors.append("invalid conflict"); continue
        ident = conflict["id"]
        if ident in seen: errors.append(f"duplicate conflict: {ident}")
        seen.add(ident)
        if conflict.get("status") == "open": errors.append(f"open conflict: {ident}"); continue
        if conflict.get("status") != "resolved": errors.append(f"invalid conflict status: {ident}"); continue
        if any(not isinstance(conflict.get(key), str) or not conflict[key].strip() for key in ("source_claim", "resolution", "evidence", "target_id")):
            errors.append(f"incomplete resolved conflict: {ident}"); continue
        node = guide.ids.get(conflict["target_id"])
        if node is None or not any(text.strip() for text in [*node.text, *(child.text[0] if child.text else "" for child in node.children)]):
            errors.append(f"conflict target missing: {ident}")
    return errors

def validate_review(data: dict, artifact: Path) -> list[str]:
    review = data.get("review")
    if not isinstance(review, dict) or review.get("status") != "complete": return ["review not complete"]
    errors = []
    if review.get("artifact_sha256") != file_digest(artifact): errors.append("review artifact hash mismatch")
    if review.get("inventory_sha256") != data.get("inventory_sha256"): errors.append("review inventory hash mismatch")
    if not isinstance(review.get("inventory_change_reason"), str): errors.append("review missing inventory_change_reason")
    for key in ("source_audit", "reverse_audit", "visual_audit"):
        value = review.get(key)
        if not isinstance(value, dict) or value.get("status") != "pass" or not isinstance(value.get("notes"), str) or not value["notes"].strip():
            errors.append(f"review incomplete: {key}")
    errors.extend(fact_review_errors(data))
    if data.get("schema_version") == 2:
        errors.extend(question_review_errors(data))
    errors.extend(conflict_review_errors(data, artifact))
    return errors

def question_review_errors(data: dict) -> list[str]:
    active = {
        item["id"] for item in data["inventory"]["questions"]
        if item.get("status") != "deferred"
    }
    checks = data.get("review", {}).get("question_checks")
    if not isinstance(checks, list):
        return ["review incomplete: question_checks"]
    errors, seen = [], set()
    for check in checks:
        if not isinstance(check, dict) or check.get("question_id") not in active:
            errors.append("invalid question review")
            continue
        ident = check["question_id"]
        if ident in seen:
            errors.append(f"duplicate question review: {ident}")
        seen.add(ident)
        targets = check.get("teaching_target_ids")
        valid = (
            check.get("status") == "pass"
            and check.get("used_external_knowledge") is False
            and isinstance(targets, list) and bool(targets)
            and isinstance(check.get("option_or_rubric_check"), str)
            and bool(check["option_or_rubric_check"].strip())
            and isinstance(check.get("evidence"), str)
            and bool(check["evidence"].strip())
        )
        if not valid:
            errors.append(f"question review incomplete: {ident}")
    errors.extend(f"question review missing: {ident}" for ident in sorted(active - seen))
    return errors

def find_source_base(manifest: Path, data: dict) -> Path:
    base = manifest.parent
    main_src = data.get("inventory", {}).get("main_source", "note")
    sources = {s.get("id"): s.get("path") for s in data.get("inventory", {}).get("sources", [])}
    main_path = sources.get(main_src)
    if main_path and (base / main_path).exists():
        return base
    for p in [manifest.parent.parent, manifest.parent.parent.parent]:
        if main_path and (p / main_path).exists():
            return p
    return manifest.parent


def find_scope_source(scope_path: Path, scope: dict) -> Path:
    rel = scope.get("source", {}).get("path", "")
    if not rel:
        return scope_path.parent
    target_name = Path(rel).name
    base = scope_path.parent
    if (base / rel).exists():
        return base / rel
    if (base / target_name).exists():
        return base / target_name
    for p in [scope_path.parent.parent, scope_path.parent.parent.parent]:
        if (p / rel).exists():
            return p / rel
        if (p / target_name).exists():
            return p / target_name
    return scope_path.parent / rel


def run_coverage(
    artifact: Path,
    manifest: Path,
    phase: str,
    scope_path: Path | None = None,
    allow_partial: bool = False,
) -> list[str]:
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        html = artifact.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [f"cannot load inputs: {error}"]
    base_dir = find_source_base(manifest, data)
    errors = validate_inventory(data, base_dir)
    if scope_path is None:
        errors.append("coverage validation requires --scope")
    if scope_path is not None:
        try:
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            source_path = find_scope_source(scope_path, scope)
            errors.extend(validate_scope_lock(scope, source_path))
            if phase == "complete":
                errors.extend(validate_scope_audit(scope))
            scoped = {
                item["id"]: item for item in scope.get("questions", [])
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            partial = data.get("delivery_mode") == "partial"
            if partial and not allow_partial:
                errors.append("partial delivery requires explicit --allow-partial")
            if allow_partial and (not partial or "partial" not in artifact.stem):
                errors.append("partial delivery requires partial filename and manifest")
            if phase == "complete" and partial:
                errors.append("partial delivery cannot pass complete validation")
            errors.extend(validate_question_coverage(data, scoped, allow_partial and partial))
            if allow_partial and partial:
                errors.extend(partial_delivery_errors(html, data, scoped))
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as error:
            errors.append(f"cannot load question scope: {error}")
    errors.extend(validate_html(html, data))
    if phase == "complete": errors.extend(validate_review(data, artifact))
    return errors

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--scope", type=Path)
    parser.add_argument("--phase", choices=("structure", "draft", "complete"))
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--questions")
    parser.add_argument("--marker", action="append", default=[])
    args = parser.parse_args(argv)
    if args.coverage and (args.questions or args.marker): parser.error("--coverage cannot be combined with legacy --questions or --marker")
    if not args.coverage and (args.phase or args.scope or args.allow_partial): parser.error("--phase, --scope and --allow-partial require --coverage")
    if args.coverage:
        phase = args.phase or "complete"
        errors = run_coverage(
            args.artifact, args.coverage, phase, args.scope, args.allow_partial
        )
        if errors: print("FAIL"); print("\n".join(f"- {error}" for error in errors)); return 1
        if phase in {"structure", "draft"}:
            print("DRAFT VALIDATION ONLY; this is not a complete study guide")
        else:
            print("PASS: complete question universe + recorded review; semantic accuracy is not machine-proven")
        return 0
    errors = legacy_errors(args.artifact, args.questions, args.marker)
    if errors: print("FAIL"); print("\n".join(f"- {error}" for error in errors)); return 1
    print(f"LEGACY STRUCTURE ONLY: {args.artifact}"); return 0

if __name__ == "__main__":
    raise SystemExit(main())
