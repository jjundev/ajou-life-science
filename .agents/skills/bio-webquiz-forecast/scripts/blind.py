#!/usr/bin/env python3
"""예상 세트 HTML → 정답·풀이를 뺀 블라인드 풀이용 Markdown.
CLI: blind.py <html> <out.md>
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402


def blind_markdown(html: str) -> str:
    parts = []
    for c in cards.parse_cards(html).values():
        if not c["options"]:
            continue
        lines = [f"## {c['title']}", "", c["stem"], ""]
        problem = re.search(r'<div class="problem">(.*?)<ul class="choices">', c["body"], re.S)
        if problem:
            for ul in re.findall(r"<ul>(.*?)</ul>", problem.group(1), re.S):
                lines += [cards.text(li) for li in re.findall(r"<li>(.*?)</li>", ul, re.S)] + [""]
        lines += [f"- {l}. {t}" for l, t in zip("ABCDE", c["options"])] + [""]
        parts.append("\n".join(lines))
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("사용법: blind.py <html> <out.md>", file=sys.stderr)
        return 2
    Path(args[1]).write_text(blind_markdown(Path(args[0]).read_text(encoding="utf-8")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
