#!/usr/bin/env python3
"""웹과제 예상 문제 묶음(pack.json + cards/) → 복습문제 형식 HTML.

bio-review-pack의 assemble.build_review를 그대로 써서 복습문제 HTML과 같은 템플릿·채점 상호작용을 쓴다.
상단 정리노트 링크만 pack.json의 note_href로 바꾼다. 출력은 src 폴더의 두 단계 위(웹과제예상/)에 쓴다.
CLI: python scripts/build_webquiz_forecast.py 웹과제예상/src/4장
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/skills/bio-review-pack/scripts"))
import assemble  # noqa: E402
import manifest as manifest_mod  # noqa: E402


def load(src_dir: str | Path) -> dict:
    return json.loads((Path(src_dir) / "pack.json").read_text(encoding="utf-8"))


def render(src_dir: str | Path) -> tuple[str, str]:
    src_dir = Path(src_dir)
    m = load(src_dir)
    html = assemble.build_review(m, src_dir)
    default = f'href="{manifest_mod.note_name(m)}"'
    if html.count(default) != 1:
        raise assemble.AssembleError(f"정리노트 링크 자리를 찾지 못함: {default}")
    return manifest_mod.review_name(m), html.replace(default, f'href="{m["note_href"]}"')


def build(src_dir: str | Path) -> Path:
    name, html = render(src_dir)
    out = Path(src_dir).resolve().parents[1] / name
    out.write_text(html, encoding="utf-8", newline="\n")
    return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("사용법: build_webquiz_forecast.py <src 폴더>", file=sys.stderr)
        return 2
    try:
        print(build(args[0]))
    except (assemble.AssembleError, ValueError) as e:
        print(f"빌드 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
