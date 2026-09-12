#!/usr/bin/env python3
"""Check a study-note ELI5 HTML artifact for required coverage markers."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

DEFAULT_MARKERS = ("30초", "문항별", "범위")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--questions", help="Comma-separated expected question numbers")
    parser.add_argument("--marker", action="append", default=[], help="Additional required text marker")
    args = parser.parse_args()

    errors: list[str] = []
    path = args.artifact
    if not path.is_file():
        errors.append(f"missing artifact: {path}")
        print("\n".join(errors))
        return 1

    text = path.read_text(encoding="utf-8")
    if not text.lstrip().lower().startswith("<!doctype html>"):
        errors.append("artifact does not start with <!doctype html>")
    if "</html>" not in text.lower():
        errors.append("artifact has no closing </html>")
    if len(text) < 1000:
        errors.append("artifact is unexpectedly short")

    for marker in (*DEFAULT_MARKERS, *args.marker):
        if marker not in text:
            errors.append(f"missing marker: {marker}")

    if args.questions:
        expected = [q.strip() for q in args.questions.split(",") if q.strip()]
        found = re.findall(r'class=["\']qnum["\'][^>]*>\s*([^<]+)', text)
        found = [q.strip() for q in found]
        missing = [q for q in expected if q not in found]
        if missing:
            errors.append(f"missing question cards: {', '.join(missing)}")
        if len(found) != len(expected):
            errors.append(f"question card count {len(found)} != expected {len(expected)}")

    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"PASS: {path} ({len(text.encode('utf-8'))} bytes)")
    if args.questions:
        print(f"Question cards verified: {len(expected)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

