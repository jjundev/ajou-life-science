"""완성된 커닝페이퍼 HTML에서 구역 조각을 다시 뽑는다. build.py의 역연산(refresh 모드용).

사용: python3 extract.py HTML SECTIONS_DIR [--spec SPEC]
출력: SECTIONS_DIR/NN.html (문서 순서대로 01부터). --spec을 주면 라벨이 spec과 같은지 확인한다.

구역 앞에 붙은 주석(구역 출처 주석)도 조각에 함께 담는다. build.py가 넣은 4칸 들여쓰기는 걷어낸다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

SEC = re.compile(r'<section class="sec">.*?</section>', re.S)
LEAD_COMMENT = re.compile(r"<!--(?:(?!<!--).)*?-->[ \t]*\n?[ \t]*$", re.S)
PAD = "    "


def _dedent(s: str) -> str:
    return "\n".join(l[len(PAD):] if l.startswith(PAD) else l for l in s.splitlines())


def extract(html: str) -> list[str]:
    """구역 조각을 문서 순서대로 돌려준다(앞 주석 포함, 들여쓰기 제거)."""
    body = html.split("<body", 1)[1] if "<body" in html else html
    frags = []
    for m in SEC.finditer(body):
        start = m.start()
        before = body[:start]
        # 구역 바로 앞의 주석들(빈 줄 없이 붙은 것)을 거꾸로 모은다
        while True:
            c = LEAD_COMMENT.search(before)
            if not c or c.group(0).lstrip().startswith("<!-- ════"):
                break
            start = c.start()
            before = body[:start]
        # 줄 머리의 들여쓰기까지 포함해 잘라야 dedent가 맞는다
        line_start = body.rfind("\n", 0, start) + 1
        if body[line_start:start].strip() == "":
            start = line_start
        frags.append(_dedent(body[start:m.end()]).strip())
    if not frags:
        raise build.BuildError("구역(<section class=\"sec\">)을 하나도 찾지 못함")
    labels = [build.label_of(f) for f in frags]
    dup = sorted({l for l in labels if labels.count(l) > 1})
    if dup:
        raise build.BuildError(f"라벨 중복: {dup}")
    return frags


def write(frags: list[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(frags, 1):
        (out_dir / f"{i:02d}.html").write_text(f + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", type=Path)
    ap.add_argument("sections", type=Path)
    ap.add_argument("--spec", type=Path)
    a = ap.parse_args(argv)
    try:
        frags = extract(a.html.read_text(encoding="utf-8"))
        if a.spec:
            want = [s["label"] for s in json.loads(a.spec.read_text(encoding="utf-8"))["sections"]]
            got = [build.label_of(f) for f in frags]
            if got != want:
                raise build.BuildError(f"라벨이 spec과 다름: {got} ≠ {want} — 전체 재생성을 권함")
        write(frags, a.sections)
    except build.BuildError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    print(f"{a.sections} — 조각 {len(frags)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
