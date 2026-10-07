#!/usr/bin/env python3
"""복습팩 복습문제 HTML에서 '기출 <N>강 M' 카드를 모은다.
CLI: exam_pool.py <repo> <N> [--out <file>]  → JSON 배열(stdout 또는 UTF-8 파일)
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
            if (pat.fullmatch(c["source"]) and c["answer_index"] is not None
                    and c["answer_index"] < len(c["options"]) and c["source"] not in pool):
                pool[c["source"]] = dict(c, file=f.relative_to(repo).as_posix())
    return dict(sorted(pool.items(), key=lambda kv: _num(kv[0])))


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    out = None
    if len(args) == 4 and args[2] == "--out":
        out, args = Path(args[3]), args[:2]
    if len(args) != 2:
        print("사용법: exam_pool.py <repo> <N> [--out <file>]", file=sys.stderr)
        return 2
    pool = load_pool(args[0], int(args[1]))
    rows = [dict(source=s, stem=c["stem"], options=c["options"], answer=c["options"][c["answer_index"]],
                 file=c["file"]) for s, c in pool.items()]
    data = json.dumps(rows, ensure_ascii=False, indent=2)
    if out:
        # 셸 리디렉션(PowerShell의 >)은 인코딩을 바꿀 수 있어 파일은 직접 UTF-8로 쓴다.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(data + "\n", encoding="utf-8", newline="\n")
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
