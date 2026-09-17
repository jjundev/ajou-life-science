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

from repo_bootstrap import enable_repo_imports

PROTECTED = {"bank_id", "bank_path", "refs", "prerequisite", "id", "status", "source_locator", "reason", "override_reason", "override_evidence"}


def build_lock(note: Path, output: Path, overrides: list, audits: dict, *, web_scope: Path | None = None) -> tuple[dict | None, list[str]]:
    """Write the lock for note to output; return (lock, errors)."""
    if not isinstance(overrides, list):
        return None, ["overrides must be a JSON array"]
    if not isinstance(audits, dict):
        return None, ["audits must be a JSON object keyed by question ID"]
    base = extract_question_scope(note.read_text(encoding="utf-8"))
    web_sources = None
    if web_scope is not None:
        root = enable_repo_imports()
        from scripts.question_bank.scope import load_web_scope, file_hash, protect_paths
        manifest = (note.parent / web_scope).resolve()
        entries, banks = load_web_scope(manifest, root)
        paths = list(dict.fromkeys(Path(e['bank_path']) for e in entries))
        from scripts.question_bank.__main__ import _protect_inputs
        for path in paths:
            _protect_inputs(banks[next(e['bank_id'] for e in entries if e['bank_path'] == str(path))], path, output)
        from scripts.question_bank.model import resolve_local
        protect_paths(output, [note, manifest, *[resolve_local(root, r['path']) for e in entries for r in e['refs']]])
        web_sources = {
            'web_scope': {'path': os.path.relpath(manifest, output.parent.resolve()), 'sha256': file_hash(manifest)},
            'banks': [{'path': os.path.relpath(path, output.parent.resolve()), 'sha256': file_hash(path)} for path in paths],
        }
        for entry in entries:
            if entry['id'] in base:
                return None, ['question id collision: ' + entry['id']]
            base[entry['id']] = {k: v for k, v in entry.items() if k != 'bank_path'}
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
    if web_sources:
        lock['schema_version'] = 2
        lock.update(web_sources)
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
    parser.add_argument("--web-scope", type=Path)
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
        lock, errors = build_lock(args.note, args.output, overrides, audits,
                                  web_scope=args.web_scope.resolve() if args.web_scope else None)
    except (OSError, UnicodeError, ValueError) as error:
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
