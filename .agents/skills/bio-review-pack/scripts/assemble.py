#!/usr/bin/env python3
"""
manifest + 조각 파일 → 정리노트/복습문제 HTML 두 개 (표준 라이브러리만 사용).

실행 폴더 구조:
  RUN/manifest.json
  RUN/sections/<section-id>.html   (섹션 안쪽: <article class="topic"> 들, <script> 가능)
  RUN/cards/<problem-id>.html      (<article class="card"> 하나)
  RUN/figures/*                    (카드 원문 그림 등, out/.assets/figures_<range>/ 로 복사) (SVG 금지)
조각 안의 {{NOTE_HREF}} / {{REVIEW_HREF}} 는 실제 파일명으로 바뀐다.
<script> 블록은 조각에서 빼서 </body> 앞({{SCRIPTS}})으로 모은다.
CLI: assemble.py --run RUN --out 복습노트/<range>
"""

from __future__ import annotations

import argparse
from datetime import date
import html
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as manifest_mod  # noqa: E402
from assets_path import SIDE  # noqa: E402
import review_interaction

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SLOT_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)


class AssembleError(RuntimeError):
    pass


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def fill(template: str, values: dict[str, str]) -> str:
    missing = sorted(set(SLOT_RE.findall(template)) - values.keys())
    if missing:
        raise AssembleError(f"템플릿 슬롯 값 없음: {missing}")
    return SLOT_RE.sub(lambda mo: values[mo.group(1)], template)


def split_scripts(fragment: str) -> tuple[str, list[str]]:
    scripts = SCRIPT_RE.findall(fragment)
    return SCRIPT_RE.sub("", fragment), scripts


def read_fragment(path: Path, m: dict) -> str:
    if not path.exists():
        raise AssembleError(f"조각 파일 없음: {path}")
    text = path.read_text(encoding="utf-8")
    return text.replace("{{NOTE_HREF}}", manifest_mod.note_name(m)).replace("{{REVIEW_HREF}}", manifest_mod.review_name(m))


def build_note(m: dict, run_dir: Path) -> str:
    more_ui = (ASSETS / "note-more.js").read_text(encoding="utf-8").rstrip()
    sections, scripts = [], [f'<script id="more-ui">\n{more_ui}\n</script>']
    for sec in m["sections"]:
        body, found = split_scripts(read_fragment(run_dir / "sections" / f"{sec['id']}.html", m))
        scripts += found
        sections.append(f'    <section id="{sec["id"]}"><h2>{esc(sec["title"])}</h2>\n{body.strip()}\n    </section>')
    return fill((ASSETS / "note-template.html").read_text(encoding="utf-8"), {
        "PAGE_TITLE": esc(f"{m['course']} 정리노트 {m['range']}"),
        "BRAND": "정리노트",
        "DESCRIPTION": esc(m["note_subtitle"]),
        "TOC": "".join(f'<a href="#{s["id"]}">{esc(s["short"])}</a>' for s in m["sections"]),
        "TITLE": esc(m["note_title"]),
        "SUBTITLE": esc(m["note_subtitle"]),
        "SECTIONS": "\n".join(sections),
        "FOOTER": m["footer_note"],
        "SCRIPTS": "\n".join(f"  {s}" for s in scripts),
        "RANGE": m["range"],
    })


def build_review(m: dict, run_dir: Path) -> str:
    parts, scripts = [], []
    for part in m["parts"]:
        cards = []
        for q in (q for q in m["problems"] if q["part"] == part["id"]):
            body, found = split_scripts(read_fragment(run_dir / "cards" / f"{q['id']}.html", m))
            scripts += found
            cards.append(body.strip())
        parts.append(f'    <section id="{part["id"]}"><h2>{esc(part["title"])}</h2>\n' + "\n".join(cards) + "\n    </section>")
    source = fill((ASSETS / "review-template.html").read_text(encoding="utf-8"), {
        "PAGE_TITLE": esc(f"{m['course']} 복습문제 {m['range']}"),
        "DESCRIPTION": esc(m["review_title"]),
        "TOC": "".join(f'<a href="#{p["id"]}">{esc(p["short"])}</a>' for p in m["parts"]),
        "NOTE_HREF": manifest_mod.note_name(m),
        "TITLE": esc(m["review_title"]),
        "INTRO": m["review_intro"],
        "PARTS": "\n".join(parts),
        "FOOTER": m["footer_review"],
        "SCRIPTS": "\n".join(f"  {s}" for s in scripts),
        "RANGE": m["range"],
    })
    return review_interaction.install(source, manifest_mod.review_name(m))


def check_figures(run_dir: Path) -> None:
    """RUN/figures/ 에 SVG가 있으면 막는다(html2md.convert_pack이 나중에 지운다)."""
    src = run_dir / "figures"
    if not src.is_dir():
        return
    svgs = sorted(f.name for f in src.iterdir() if f.is_file() and f.suffix.lower() == ".svg")
    if svgs:
        raise AssembleError(f"RUN/figures/에는 PNG 등 래스터 그림만 둔다(SVG는 카드에 인라인): {', '.join(svgs)}")


def copy_figures(run_dir: Path, out_dir: Path, range_: str) -> int:
    """RUN/figures/ 의 파일을 out/.assets/figures_<range>/ 로 복사하고 개수를 돌려준다."""
    src = run_dir / "figures"
    if not src.is_dir():
        return 0
    dst = out_dir / SIDE / manifest_mod.fig_dir_name(range_)
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src.iterdir()):
        if f.is_file():
            shutil.copy2(f, dst / f.name)
            count += 1
    return count


PACK_RECORDS = ("manifest.json", "question-audit.md", "key-check.md", "variants.md", "problem-pages.txt",
                "note-feedback-audit.md", "summary-audit.md", "blind-results.md")
BODY_REVIEW_RECORDS = ("note-feedback-audit.md", "summary-audit.md", "blind-results.md")
REPORTS_DIR = Path("work") / "reports"  # 서브에이전트 상세 기록(TSV). references/report-contract.md
APPEND_ON_AUGMENT = ("question-audit.md", "key-check.md", "variants.md")


def _ids_text(ids: list[str]) -> str:
    if not ids:
        return "없음"
    if len(ids) <= 4:
        return ", ".join(ids)
    return f"{ids[0]}–{ids[-1]} ({len(ids)}개)"


def save_pack_records(run_dir: Path | str, out_dir: Path | str, mode: str, added_ids: list[str],
                      today: str | None = None, note: str = "") -> Path:
    """RUN의 설계 기록을 out/.pack/ 에 남긴다. 보강이면 감사·변형 기록은 이어 붙이고, 없는 파일은 이전 것을 둔다."""
    if mode not in ("full", "augment"):
        raise AssembleError(f"알 수 없는 mode: {mode}")
    run_dir, pack = Path(run_dir), Path(out_dir) / ".pack"
    pack.mkdir(parents=True, exist_ok=True)
    today = today or date.today().isoformat()
    for name in PACK_RECORDS:
        if mode == "augment" and name in BODY_REVIEW_RECORDS:
            continue  # augment는 본문을 바꾸지 않으므로 새 본문 검토로 덮어쓰지 않는다.
        src, dst = run_dir / name, pack / name
        if not src.is_file():
            continue
        if mode == "augment" and name in APPEND_ON_AUGMENT and dst.is_file():
            old = dst.read_text(encoding="utf-8").rstrip("\n")
            dst.write_text(f"{old}\n\n## {today} 보강\n\n{src.read_text(encoding='utf-8')}", encoding="utf-8")
        else:
            shutil.copyfile(src, dst)
    reports = run_dir / REPORTS_DIR
    if mode == "full" and reports.is_dir():  # 상세 검토 기록은 메인 컨텍스트 대신 여기에 남는다
        dst = pack / "reports"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(reports, dst)
    log = pack / "log.md"
    head = "" if log.is_file() else "# 팩 실행 기록\n\n"
    line = f"- {today} {mode}: 추가 {_ids_text(added_ids)}" + (f" — {note}" if note else "") + "\n"
    with open(log, "a", encoding="utf-8") as f:
        f.write(head + line)
    return pack


def assemble(run_dir: Path | str, out_dir: Path | str) -> tuple[Path, Path]:
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    m = manifest_mod.load(run_dir / "manifest.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    note_path = out_dir / manifest_mod.note_name(m)
    review_path = out_dir / manifest_mod.review_name(m)
    # 둘 다 만든 뒤에 쓴다: 조각이 하나라도 없으면 어느 파일도 바뀌지 않는다.
    note_html, review_html = build_note(m, run_dir), build_review(m, run_dir)
    check_figures(run_dir)
    note_path.write_text(note_html, encoding="utf-8")
    review_path.write_text(review_html, encoding="utf-8")
    copy_figures(run_dir, out_dir, m["range"])
    save_pack_records(run_dir, out_dir, "full", [q["id"] for q in m["problems"]])
    return note_path, review_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        for path in assemble(args.run, args.out):
            print(path)
    except (AssembleError, manifest_mod.ManifestError) as e:
        print(f"assemble 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
