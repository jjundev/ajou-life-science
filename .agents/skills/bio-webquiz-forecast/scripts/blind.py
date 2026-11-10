#!/usr/bin/env python3
"""예상 세트 HTML → 정답·풀이를 뺀 블라인드 풀이용 Markdown.
CLI: blind.py <html> <out.md> [--only p2,p13]

사본 옆에 `<out.md>.cards.json`(사본에 담은 카드 id → `.pack/v<K>/cards/<id>.html` SHA-256)을 남긴다.
blind_ledger.py record가 이 기록으로 리뷰어가 실제로 본 카드 판을 묶는다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402

PACK = ".pack"
HTML_VERSION_RE = re.compile(r"_v(\d+)\.html$")


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


def graded_cards(html: str, only: set[str] | None = None) -> list[dict]:
    out = [c for c in cards.parse_cards(html).values() if c["options"]]
    if only is not None:
        missing = only - {c["id"] for c in out}
        if missing:
            raise ValueError(f"사본에 없는 카드: {sorted(missing)}")
        out = [c for c in out if c["id"] in only]
    return out


def blind_markdown(html: str, only: set[str] | None = None) -> str:
    parts = []
    for c in graded_cards(html, only):
        lines = [f"## {c['title']}", "", c["stem"], ""]
        extra = _problem_lines(c["body"])
        if extra:
            lines += extra + [""]
        lines += [f"- {l}. {t}" for l, t in zip("ABCDE", c["options"])] + [""]
        parts.append("\n".join(lines))
    return "\n".join(parts)


def source_dir(html_path: Path) -> Path | None:
    m = HTML_VERSION_RE.search(html_path.name)
    if not m:
        return None
    src = html_path.parent / PACK / f"v{m.group(1)}"
    return src if (src / "cards").is_dir() else None


def card_hashes(src: Path, ids: list[str]) -> dict[str, str]:
    return {cid: hashlib.sha256((src / "cards" / f"{cid}.html").read_bytes()).hexdigest() for cid in ids}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="블라인드 풀이 사본 만들기")
    parser.add_argument("html", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--only", help="쉼표로 구분한 카드 id(수정한 카드만 다시 풀 때)")
    args = parser.parse_args(argv)
    only = {s.strip() for s in args.only.split(",") if s.strip()} if args.only else None
    html_path = args.html.resolve()
    html = html_path.read_text(encoding="utf-8")
    try:
        chosen = graded_cards(html, only)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(blind_markdown(html, only), encoding="utf-8")
    src = source_dir(html_path)
    if src is not None:
        record = {"html": str(html_path), "src": str(src.resolve()),
                  "cards": card_hashes(src, [c["id"] for c in chosen])}
        Path(str(args.out) + ".cards.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
