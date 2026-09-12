#!/usr/bin/env python3
"""Build a source-bound question scope lock.

Phase 1 (before authoring): run without --audits to lock IDs and statuses.
Phase 2 (after the fact inventory): build_guide.py calls build_lock() with
per-question audits (format, option_count, grading, requirements = fact IDs,
source_evidence, audit_status) and rewrites the same lock file.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from coverage_model import file_digest
from question_scope import apply_overrides, extract_question_scope, scope_digest

PROTECTED = {"id", "status", "source_locator", "reason", "override_reason", "override_evidence"}


def build_lock(note: Path, output: Path, overrides: list, audits: dict) -> tuple[dict | None, list[str]]:
    """Write the lock for note to output; return (lock, errors)."""
    if not isinstance(overrides, list):
        return None, ["overrides must be a JSON array"]
    if not isinstance(audits, dict):
        return None, ["audits must be a JSON object keyed by question ID"]
    base = extract_question_scope(note.read_text(encoding="utf-8"))
    final, errors = apply_overrides(base, overrides)
    if errors:
        return None, errors
    for ident, audit in audits.items():
        if ident not in final:
            return None, [f"audit references unknown question: {ident}"]
        if not isinstance(audit, dict) or PROTECTED & set(audit):
            return None, [f"invalid or protected audit fields: {ident}"]
        final[ident].update(audit)
    source_path = os.path.relpath(note.resolve(), output.parent.resolve())
    lock = {
        "schema_version": 1,
        "source": {"path": source_path, "sha256": file_digest(note)},
        "base_questions": list(base.values()),
        "overrides": overrides,
        "questions": list(final.values()),
    }
    lock["scope_sha256"] = scope_digest(lock)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return lock, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("note", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--audits", type=Path)
    args = parser.parse_args(argv)
    try:
        overrides = (
            json.loads(args.overrides.read_text(encoding="utf-8"))
            if args.overrides else []
        )
        audits = (
            json.loads(args.audits.read_text(encoding="utf-8"))
            if args.audits else {}
        )
        lock, errors = build_lock(args.note, args.output, overrides, audits)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"FAIL: cannot load scope inputs: {error}")
        return 1
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    counts = {
        status: sum(item["status"] == status for item in lock["questions"])
        for status in ("included", "review", "deferred")
    }
    print(
        f"WROTE {args.output}: {len(lock['questions'])} questions "
        f"({counts['included']} included, {counts['review']} review, "
        f"{counts['deferred']} deferred)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
