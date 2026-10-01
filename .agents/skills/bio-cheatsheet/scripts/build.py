"""spec.json과 구역 조각으로 커닝페이퍼 HTML을 만들고 쪽을 나눈 뒤 PDF로 출력한다.

사용: python3 build.py SPEC SECTIONS_DIR OUT_DIR [--no-pdf]
출력: OUT_DIR/cheatsheet_<N>장.html (+ .pdf)

쪽 나눔: 모든 구역을 1쪽에 넣고 Chrome으로 넘침을 잰다. 넘친 쪽의 첫 넘침 구역부터 그 쪽 끝까지를
다음 쪽 맨 앞으로 옮기고 다시 잰다. 넘침이 없어질 때까지 반복한다.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / "assets" / "cheatsheet-template.html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE1_MARK = "<!-- ════════════ 1쪽"
TAIL_MARK = "<!-- 넘침 경고: 각 쪽"
MAX_PAGES = 20


class BuildError(Exception):
    pass


@dataclass
class Template:
    head: str       # 문서 시작 ~ 1쪽 앞 (<body>, 테마 체크박스 포함)
    tail: str       # 넘침 경고 스크립트 ~ 문서 끝
    theme_btn: str  # 1쪽 제목 줄의 테마 버튼 <label>


def load_template(path: Path = TEMPLATE) -> Template:
    src = path.read_text(encoding="utf-8")
    try:
        head = src[: src.index(PAGE1_MARK)]
        tail = src[src.index(TAIL_MARK):]
    except ValueError as e:
        raise BuildError(f"템플릿 표시를 찾지 못함: {e}") from e
    m = re.search(r'<label for="theme-light" class="theme-btn".*?</label>', src, re.S)
    if not m:
        raise BuildError("템플릿에 테마 버튼이 없음")
    return Template(head.rstrip() + "\n\n", tail, m.group(0))


def label_of(fragment: str) -> str:
    m = re.search(r'<span class="sec-label">(.*?)</span>', fragment, re.S)
    if not m:
        raise BuildError(f"sec-label 없는 조각: {fragment[:80]!r}")
    return re.sub(r"\s+", " ", m.group(1)).strip()


def load_fragments(spec: dict, sections_dir: Path) -> list[str]:
    """조각 파일(*.html)을 읽어 spec의 라벨 순서로 돌려준다."""
    by_label: dict[str, str] = {}
    for f in sorted(sections_dir.glob("*.html")):
        text = f.read_text(encoding="utf-8").strip()
        if text.count('<section class="sec">') != 1:
            raise BuildError(f"{f.name}: <section class=\"sec\">가 정확히 하나여야 함")
        lab = label_of(text)
        if lab in by_label:
            raise BuildError(f"라벨 중복: {lab}")
        by_label[lab] = text
    want = [s["label"] for s in spec["sections"]]
    missing = [l for l in want if l not in by_label]
    extra = [l for l in by_label if l not in want]
    if missing or extra:
        raise BuildError(f"조각 불일치 — 없음: {missing}, spec에 없는 조각: {extra}")
    return [by_label[l] for l in want]


def _indent(fragment: str, pad: str = "    ") -> str:
    return "\n".join(pad + line if line.strip() else "" for line in fragment.splitlines())


def _page(i: int, n: int, title: str, frags: list[str], theme_btn: str) -> str:
    toc = " · ".join(label_of(f) for f in frags)
    btn = f"\n      {theme_btn}" if i == 1 else ""
    body = "\n\n".join(_indent(f) for f in frags)
    return (
        f"<!-- ════════════ {i}쪽 ════════════ -->\n"
        f'<section class="page" aria-label="{i}쪽">\n'
        f'  <header class="page-head">\n'
        f'    <div class="page-title-row">\n'
        f'      <h1 class="page-title">{title}</h1>\n'
        f'      <span class="page-no">{i} / {n}</span>{btn}\n'
        f"    </div>\n"
        f'    <div class="page-bar" aria-hidden="true"></div>\n'
        f'    <p class="page-toc">{toc}</p>\n'
        f"  </header>\n\n"
        f'  <div class="page-body">\n\n{body}\n\n  </div>\n'
        f"</section>\n\n"
    )


def render(tpl: Template, title: str, stem: str, pages: list[list[str]]) -> str:
    head = tpl.head.replace("cheatsheet-template-sample.pdf", f"{stem}.pdf")
    head = head.replace("cheatsheet-template.html", f"{stem}.html")
    head = re.sub(r"<title>.*?</title>", f"<title>{title} 커닝페이퍼</title>", head, count=1)
    head = head.replace("웹과제 커닝페이퍼 템플릿", f"웹과제 커닝페이퍼 — {title}", 1)
    n = len(pages)
    return head + "".join(_page(i, n, title, p, tpl.theme_btn) for i, p in enumerate(pages, 1)) + tpl.tail


def parse_overflow(dom: str) -> list[tuple[int, str]]:
    m = re.search(r'data-overflow="([^"]*)"', dom)
    if not m:
        return []
    out = []
    for item in m.group(1).split(", "):
        page, label = item.split("쪽 ", 1)
        out.append((int(page), label.strip()))
    return out


def chrome_overflow(html: Path) -> list[tuple[int, str]]:
    dom = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000",
         "--dump-dom", html.resolve().as_uri()],
        capture_output=True, text=True, timeout=120, check=True,
    ).stdout
    return parse_overflow(dom)


def paginate(frags: list[str], probe, max_pages: int = MAX_PAGES) -> list[list[str]]:
    """probe(pages) -> [(쪽 번호, 라벨)]. 넘침이 없을 때까지 꼬리를 다음 쪽으로 민다."""
    pages = [list(frags)]
    while True:
        over = probe(pages)
        if not over:
            return pages
        p = min(pg for pg, _ in over)
        labels = [label_of(f) for f in pages[p - 1]]
        first = min(labels.index(lab) for pg, lab in over if pg == p and lab in labels)
        if first == 0:
            raise BuildError(f"{p}쪽 첫 구역 '{labels[0]}'이 한 쪽보다 큼 — 구역을 둘로 나눌 것")
        tail = pages[p - 1][first:]
        del pages[p - 1][first:]
        if p == len(pages):
            pages.append([])
        pages[p] = tail + pages[p]
        if len(pages) > max_pages:
            raise BuildError(f"{max_pages}쪽을 넘음 — 구역 내용을 줄일 것")


def print_pdf(html: Path, pdf: Path) -> None:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
         f"--print-to-pdf={pdf.resolve()}", html.resolve().as_uri()],
        capture_output=True, timeout=180, check=True,
    )


def build(spec_path: Path, sections_dir: Path, out_dir: Path, pdf: bool = True) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    title = spec["title"]
    stem = f"cheatsheet_{spec['chapter']}장"
    tpl = load_template()
    frags = load_fragments(spec, sections_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html = out_dir / f"{stem}.html"

    def probe(pages):
        html.write_text(render(tpl, title, stem, pages), encoding="utf-8")
        return chrome_overflow(html)

    pages = paginate(frags, probe)
    html.write_text(render(tpl, title, stem, pages), encoding="utf-8")
    if pdf:
        print_pdf(html, html.with_suffix(".pdf"))
    print(f"{html} — {len(pages)}쪽, 구역 {len(frags)}개" + (" (+PDF)" if pdf else ""))
    return html


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("sections", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args(argv)
    try:
        build(a.spec, a.sections, a.out, pdf=not a.no_pdf)
    except BuildError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
