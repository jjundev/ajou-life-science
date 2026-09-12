#!/usr/bin/env python3
"""Write a copy of a guide with every answer removed, for the independent solvability review.

Usage: make_blind_copy.py GUIDE.html BLIND.html

Removes each <details data-role="solution"> block (nested <details> included)
and fails if any answer, reason, trap or source-conflict text survives. Give
only BLIND.html to a reviewer who did not write the solutions.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

OPEN = '<details data-role="solution"'
LEAK = re.compile(r'data-part="(answer|reason|trap)"|data-role="(solution|source-conflict)"')


def strip_solutions(html: str) -> tuple[str, int, list[str]]:
    """Return (blind html, removed block count, errors)."""
    out, pos, removed = [], 0, 0
    while (start := html.find(OPEN, pos)) != -1:
        depth, cursor = 0, start
        for match in re.finditer(r"<details\b|</details>", html[start:]):
            depth += 1 if match.group(0) == "<details" else -1
            if depth == 0:
                cursor = start + match.end()
                break
        else:
            return html, removed, [f"unclosed solution block at offset {start}"]
        out.append(html[pos:start])
        pos, removed = cursor, removed + 1
    out.append(html[pos:])
    blind = "".join(out)
    leaks = sorted({m.group(0) for m in LEAK.finditer(blind)})
    return blind, removed, [f"answer content outside a solution block: {leak}" for leak in leaks]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    blind, removed, errors = strip_solutions(args.artifact.read_text(encoding="utf-8"))
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    args.output.write_text(blind, encoding="utf-8")
    cards = len(re.findall(r'data-question-id="[^"]+" data-status="(?:included|review)"', blind))
    print(f"WROTE {args.output}: removed {removed} solution blocks; {cards} active question cards to answer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
