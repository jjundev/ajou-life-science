"""커닝페이퍼 HTML·PDF 기계 검사. 위반을 한 줄씩 출력하고, 하나라도 있으면 종료 코드 1.

사용: python3 check.py HTML SPEC [--no-files]
  --no-files  HTML 내용만 검사한다(넘침·PDF 검사 생략).
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

PLACEHOLDERS = ["키워드 A", "구역 제목", "견본", "박스 A", "오답 문장 예시", "쪽 제목"]
ASCII_FORMULA = re.compile(
    r"(?<![A-Za-z0-9])(CO2|H2O|O2|N2|C6H12O6|FADH2|NADH2)(?![0-9])|(?<![A-Za-z])(NADP?|H|Na|K|Ca|Cl)\+"
)
FIG_COL_PX = 357   # A4 2단 한 단 너비(≈94.5mm)를 CSS px로
FIG_MAX_PX = 132   # --fig-max 35mm를 CSS px로


def strip_comments(s: str) -> str:
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def text(html: str) -> str:
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def body_of(html: str) -> str:
    return html.split("<body", 1)[1]


def pages_of(body: str) -> list[str]:
    return strip_comments(body).split('<section class="page"')[1:]


def sections_of(fragment: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r'<section class="sec">(.*?)</section>', fragment, re.S):
        out.append((build.label_of(m.group(0)), m.group(1)))
    return out


def _close_of(s: str, tag: str, start: int) -> int | None:
    """start에서 열린 <tag>의 짝 닫는 태그 끝 위치."""
    depth = 0
    for m in re.finditer(rf"<(/?){tag}\b[^>]*>", s[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.end()
    return None


def check_html(html: str, spec: dict) -> list[str]:
    probs: list[str] = []
    head = html.split("<html", 1)[0]
    if head.count("<!--") > 1:
        probs.append("head 주석 안에 '<!--'가 있음 — 주석이 일찍 닫혀 본문이 깨진다")
    body = body_of(html)
    clean = strip_comments(body)
    pages = pages_of(body)
    secs = sections_of(clean)
    sec_map = dict(secs)
    want = [s["label"] for s in spec["sections"]]

    # 구조
    if [l for l, _ in secs] != want:
        probs.append(f"라벨 순서가 spec과 다름: {[l for l, _ in secs]} ≠ {want}")
    for i, p in enumerate(pages, 1):
        m = re.search(r'<p class="page-toc">(.*?)</p>', p, re.S)
        labels = [l for l, _ in sections_of(p)]
        if not m or text(m.group(1)) != " · ".join(labels):
            probs.append(f"{i}쪽 목차 줄이 그 쪽 구역 라벨과 다름")
        no = re.search(r'<span class="page-no">(.*?)</span>', p)
        if not no or text(no.group(1)) != f"{i} / {len(pages)}":
            probs.append(f"{i}쪽 쪽 번호가 '{i} / {len(pages)}'가 아님")
        if ('class="theme-btn"' in p) != (i == 1):
            probs.append(f"{i}쪽 테마 버튼 — 1쪽에만 하나 있어야 함")
    t_all = text(clean)
    for ph in PLACEHOLDERS:
        if ph in t_all:
            probs.append(f"템플릿 견본 문구가 남음: '{ph}'")

    # 내용
    if "정답" in t_all or re.search(r"\([1-5]\)", t_all):
        probs.append("답 번호·'정답' 표기가 있음 — 보기 번호는 바뀌므로 쓰지 않는다")
    traps = len(re.findall(r'<div class="trap">', body))
    sourced = len(re.findall(r'<!--\s*출처:[^>]*?-->\s*<div class="trap">', body))
    if sourced != traps:
        probs.append(f"출처 주석 없는 함정 {traps - sourced}개 — <div class=\"trap\"> 바로 앞에 <!-- 출처: … -->")
    for s in spec["sections"]:
        lab = s["label"]
        if lab not in sec_map:
            continue
        inner = sec_map[lab]
        n = inner.count('class="trap-x"')
        if s.get("traps", True):
            if not 1 <= n <= 3:
                probs.append(f"{lab}: 함정 {n}개 — 1~3개")
        elif n:
            probs.append(f"{lab}: 함정을 두지 않는 고정 구역인데 함정 {n}개")
        lm = re.search(r'<(p|div) class="later">', inner)
        if lm:
            if not inner[lm.end():].lstrip().startswith('<span class="badge prof">교수님: 몰라도 됨</span>'):
                probs.append(f"{lab}: later 블록 첫 요소에 '교수님: 몰라도 됨' 배지가 없음")
            end = _close_of(inner, lm.group(1), lm.start())
            if end is None or text(inner[end:]):
                probs.append(f"{lab}: later 블록이 구역 맨 끝이 아님")
        st = text(inner)
        for term in s.get("terms", []):
            if term not in st:
                probs.append(f"{lab}: 필수 용어 '{term}' 없음")
    for term in spec.get("chapter_terms", []):
        if term not in t_all:
            probs.append(f"장마감 필수 용어 '{term}'이 시트 어디에도 없음")
    for m in ASCII_FORMULA.finditer(t_all):
        probs.append(f"ASCII 화학식 '{m.group(0)}' — 유니코드 첨자(CO₂, NAD⁺)로")

    # SVG
    if re.search(r'(fill|stroke)="#|style="[^"]*#[0-9a-fA-F]{3}', clean):
        probs.append("SVG에 색을 직접 적음 — fig-* 클래스만")
    for vb in re.findall(r'viewBox="([^"]+)"', clean):
        _, _, w, h = (float(x) for x in vb.replace(",", " ").split())
        if w > 360 or (w > 8 and h * FIG_COL_PX / w > FIG_MAX_PX):
            probs.append(f"SVG viewBox {vb} — 폭 ≤360, 인쇄 높이 ≤35mm(높이×357/폭 ≤132)")
    dup = [i for i, c in Counter(re.findall(r'\sid="([^"]+)"', clean)).items() if c > 1]
    if dup:
        probs.append(f"id 중복: {dup} — marker id는 문서 전체에서 유일하게")
    return probs


def check_files(html_path: Path, spec: dict) -> list[str]:
    probs = check_html(html_path.read_text(encoding="utf-8"), spec)
    if not Path(build.CHROME).exists():
        return probs + ["(미실행) Chrome 없음 — 넘침·PDF 검사 생략"]
    over = build.chrome_overflow(html_path)
    if over:
        probs.append(f"넘침: {over} — build.py를 다시 실행")
    pdf = html_path.with_suffix(".pdf")
    if not pdf.exists():
        return probs + ["PDF 없음"]
    if pdf.stat().st_mtime < html_path.stat().st_mtime:
        probs.append("PDF가 HTML보다 오래됨 — build.py로 다시 출력")
    if not (shutil.which("pdfinfo") and shutil.which("pdffonts")):
        return probs + ["(미실행) poppler 없음 — PDF 쪽 수·폰트 검사 생략"]
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    n_pdf = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    n_html = len(pages_of(body_of(html_path.read_text(encoding="utf-8"))))
    if n_pdf != n_html:
        probs.append(f"PDF {n_pdf}쪽 ≠ HTML {n_html}쪽")
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
    if "Pretendard" not in fonts:
        probs.append("PDF에 Pretendard가 없음 — 웹폰트가 안 받아진 채 출력됨(네트워크 확인 후 재출력)")
    return probs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", type=Path)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--no-files", action="store_true")
    a = ap.parse_args(argv)
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    probs = check_html(a.html.read_text(encoding="utf-8"), spec) if a.no_files else check_files(a.html, spec)
    for p in probs:
        print(p)
    hard = [p for p in probs if not p.startswith("(미실행)")]
    print("OK" if not hard else f"위반 {len(hard)}건")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
