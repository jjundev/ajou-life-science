#!/usr/bin/env python3
"""복습팩 복습문제 HTML에서 '기출 <N>강 M' 카드를 모은다.
CLI: exam_pool.py <repo> <N>  → JSON 배열(stdout)
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402


def _num(source: str) -> int:
    return int(source.rsplit(" ", 1)[1])


def load_pool(repo: Path | str, chapter: int) -> dict[str, dict]:
    repo = Path(repo)
    pat = re.compile(rf"기출 {chapter}강 \d+")
    pool: dict[str, dict] = {}
    for f in sorted(repo.glob("복습노트/*/복습문제_*.html")):
        for c in cards.parse_cards(f.read_text(encoding="utf-8")).values():
            if pat.fullmatch(c["source"]) and c["answer_index"] is not None and c["source"] not in pool:
                pool[c["source"]] = dict(c, file=f.relative_to(repo).as_posix())
    return dict(sorted(pool.items(), key=lambda kv: _num(kv[0])))


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("사용법: exam_pool.py <repo> <N>", file=sys.stderr)
        return 2
    pool = load_pool(args[0], int(args[1]))
    rows = [dict(source=s, stem=c["stem"], options=c["options"], answer=c["options"][c["answer_index"]],
                 file=c["file"]) for s, c in pool.items()]
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
