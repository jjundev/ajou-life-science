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


def _figure(m: re.Match) -> str:
    label = re.search(r'aria-label="([^"]*)"', m.group(1))
    inner = cards.text(m.group(2))
    return f"[그림: {label.group(1) if label else ''} {inner}".rstrip() + "]</p>"


def _problem_lines(body: str) -> list[str]:
    """발문 뒤, 보기 앞의 내용(그림 설명·글자, 표, 단서 문단, ㄱㄴㄷ 진술)을 줄 단위로."""
    m = re.search(r'<div class="problem">(.*?)<ul class="choices">', body, re.S)
    if not m:
        return []
    seg = re.sub(r"^\s*<p>.*?</p>", "", m.group(1), count=1, flags=re.S)  # 발문은 이미 넣었다
    seg = re.sub(r"<svg\b([^>]*)>(.*?)</svg>", _figure, seg, flags=re.S)
    lines = [cards.text(x) for x in re.split(r"</(?:p|li|tr|figcaption)>", seg)]
    return [l for l in lines if l]


def blind_markdown(html: str) -> str:
    parts = []
    for c in cards.parse_cards(html).values():
        if not c["options"]:
            continue
        lines = [f"## {c['title']}", "", c["stem"], ""]
        extra = _problem_lines(c["body"])
        if extra:
            lines += extra + [""]
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
