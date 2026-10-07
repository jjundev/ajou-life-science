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

OVERRIDE_STYLE = '<style id="forecast-overrides">.review-export-bar { display: none !important; }</style>'


def load(src_dir: str | Path) -> dict:
    return json.loads((Path(src_dir) / "pack.json").read_text(encoding="utf-8"))


def render(src_dir: str | Path) -> tuple[str, str]:
    src_dir = Path(src_dir)
    m = load(src_dir)
    html = assemble.build_review(m, src_dir)
    default = f'href="{manifest_mod.note_name(m)}"'
    if html.count(default) != 1:
        raise assemble.AssembleError(f"정리노트 링크 자리를 찾지 못함: {default}")
    html = html.replace(default, f'href="{m["note_href"]}"')
    # JSON 내보내기는 복습노트/<날짜>/풀이기록 폴더 구조를 전제로 하고 저장 폴더 기억을 모든 팩이 함께 쓴다.
    # 이 페이지에서 쓰면 그 기억을 지우므로 내보내기 막대를 숨긴다(공용 assets는 고치지 않는다).
    if html.count("</head>") != 1:
        raise assemble.AssembleError("</head>가 하나가 아님")
    html = html.replace("</head>", OVERRIDE_STYLE + "\n</head>")
    return manifest_mod.review_name(m), html


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
