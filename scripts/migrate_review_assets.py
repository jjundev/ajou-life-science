"""복습노트/<날짜>/ 부속 파일을 숨김 폴더 `.assets/`로 옮기는 일회성 이전 스크립트.

날짜 폴더 루트에는 *.html, .pack/, .assets/, .DS_Store 만 남긴다. 루트 HTML의 상대
src/href와 `생성 파일` 주석은 `relocate`로, 옮긴 MD의 `](t)`는 `rewrite_md`로 고치고,
복습문제 HTML에 인라인된 `resolveExportDir` 블록은 현재 review-interaction.js 것으로 바꾼다.

    python3 scripts/migrate_review_assets.py [ROOT=복습노트] [--apply] [--check]

기본은 dry-run(할 일만 출력)이다. 두 번 돌려도 결과가 같다(이미 `.assets/`에 있던 MD는
다시 쓰지 않는다). git 기록은 커밋 때 `git add -A`의 rename 감지가 처리한다.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
REVIEW_SCRIPTS = REPO / ".agents" / "skills" / "bio-review-pack" / "scripts"
ASSET_JS = REPO / ".agents" / "skills" / "bio-review-pack" / "assets" / "review-interaction.js"
if str(REVIEW_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS))

from assets_path import SIDE, moves, rebase_md, relocate  # noqa: E402

BLOCK_START = "async function resolveExportDir"
BLOCK_END = "const isCancel"

_ATTR = re.compile(r'(src|href)="([^"]*)"')
_GENERATED = re.compile(r"(<!-- 생성 파일: )(\S+?)(을 고친 뒤)")
_MD_TARGET = re.compile(r"(\]\()([^)\s]+)(\))")
# 검사용: `](t)`, `](t "제목")`, `](<t>)` 모두에서 대상만 뽑는다.
_MD_CHECK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
_DATE = re.compile(r"\d{4}(-\d{4})?")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _nfc(name: str) -> str:
    return unicodedata.normalize("NFC", name)


def _block_span(text: str) -> tuple[int, int]:
    if text.count(BLOCK_START) != 1 or text.count(BLOCK_END) != 1:
        raise ValueError(f"`{BLOCK_START}`·`{BLOCK_END}` 표식이 각각 정확히 한 번 있어야 한다")
    start, end = text.index(BLOCK_START), text.index(BLOCK_END)
    if end < start:
        raise ValueError(f"`{BLOCK_END}`가 `{BLOCK_START}`보다 앞에 있다")
    return start, end


def export_block(js: str) -> str:
    """`async function resolveExportDir`부터 `const isCancel` 직전까지를 잘라 낸다."""
    start, end = _block_span(js)
    return js[start:end]


def rewrite_html(text: str, block: str | None) -> str:
    """날짜 폴더 루트 HTML을 `.assets/` 이전 뒤 위치에 맞게 고친다."""
    if block is not None and BLOCK_START in text:
        start, end = _block_span(text)
        text = text[:start] + block + text[end:]
    text = _ATTR.sub(lambda m: f'{m.group(1)}="{relocate(m.group(2))}"', text)
    return _GENERATED.sub(lambda m: m.group(1) + relocate(m.group(2)) + m.group(3), text)


def rewrite_md(text: str) -> str:
    """날짜 폴더 루트에 있던 MD를 `.assets/` 안 위치에 맞게 고친다(한 번만 적용)."""
    return rebase_md(_MD_TARGET.sub(lambda m: m.group(1) + relocate(m.group(2)) + m.group(3), text))


def _root_html(day: Path) -> list[Path]:
    return sorted(p for p in day.iterdir()
                  if p.is_file() and _nfc(p.name).lower().endswith((".html", ".htm")))


def migrate_day(day: Path, block: str, apply: bool) -> list[str]:
    """날짜 폴더 하나의 할 일(`move X`, `rewrite Y`)을 돌려주고, `apply`일 때만 실행한다."""
    day = Path(day)
    side = day / SIDE
    entries = sorted(day.iterdir(), key=lambda p: _nfc(p.name))
    movers = [p for p in entries if moves(p.name)]

    # 1. 루트 MD를 읽어 둔다.
    mds = {_nfc(p.name): p.read_text(encoding="utf-8")
           for p in movers if p.is_file() and _nfc(p.name).lower().endswith(".md")}

    # 2. 이름이 겹치면 아무것도 옮기기 전에 멈춘다.
    existing = {_nfc(p.name) for p in side.iterdir()} if side.is_dir() else set()
    clash = [_nfc(p.name) for p in movers if _nfc(p.name) in existing]
    if clash:
        raise FileExistsError(f"{day}/{SIDE}에 이미 있음: {', '.join(clash)}")

    actions = [f"move {_nfc(p.name)}" for p in movers]
    if apply and movers:
        side.mkdir(exist_ok=True)
        for p in movers:
            os.rename(p, side / p.name)

    # 3. 루트 HTML을 다시 쓴다.
    for p in _root_html(day):
        old = p.read_text(encoding="utf-8")
        new = rewrite_html(old, block)
        if new != old:
            actions.append(f"rewrite {_nfc(p.name)}")
            if apply:
                p.write_text(new, encoding="utf-8")

    # 4. 방금 옮긴 MD만 `.assets/` 안 위치 기준으로 다시 쓴다.
    for name, old in mds.items():
        new = rewrite_md(old)
        if new != old:
            actions.append(f"rewrite {SIDE}/{name}")
            if apply:
                target = next(p for p in side.iterdir() if _nfc(p.name) == name)
                target.write_text(new, encoding="utf-8")
    return actions


def _relative(url: str) -> bool:
    return bool(url) and url[0] not in "#/" and not _SCHEME.match(url)


def _missing(base: Path, url: str) -> bool:
    path = unquote(re.split(r"[?#]", url, maxsplit=1)[0])
    return bool(path) and not os.path.exists(base / path)


def broken_links(day: Path) -> list[str]:
    """루트 HTML의 상대 src/href와 `.assets/*.md`의 상대 `](t)` 중 대상이 없는 것."""
    day = Path(day)
    broken = []
    for p in _root_html(day):
        for m in _ATTR.finditer(p.read_text(encoding="utf-8")):
            url = m.group(2)
            if _relative(url) and _missing(day, url):
                broken.append(f"{_nfc(p.name)}: {url}")
    side = day / SIDE
    if side.is_dir():
        for p in sorted(side.iterdir(), key=lambda p: _nfc(p.name)):
            if not (p.is_file() and _nfc(p.name).lower().endswith(".md")):
                continue
            for m in _MD_CHECK.finditer(p.read_text(encoding="utf-8")):
                url = m.group(1)
                if _relative(url) and _missing(side, url):
                    broken.append(f"{SIDE}/{_nfc(p.name)}: {url}")
    return broken


def _days(root: Path) -> list[Path]:
    return sorted((p for p in root.iterdir() if p.is_dir() and _DATE.fullmatch(_nfc(p.name))),
                  key=lambda p: _nfc(p.name))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="복습노트 날짜 폴더 부속 파일을 .assets/로 옮긴다.")
    ap.add_argument("root", nargs="?", default="복습노트")
    ap.add_argument("--apply", action="store_true", help="실제로 옮기고 고친다(기본은 dry-run)")
    ap.add_argument("--check", action="store_true", help="깨진 링크를 출력하고 있으면 종료 코드 1")
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"폴더 없음: {root}", file=sys.stderr)
        return 2
    days = _days(root)

    if args.apply or not args.check:
        block = export_block(ASSET_JS.read_text(encoding="utf-8"))
        total = 0
        for day in days:
            acts = migrate_day(day, block, apply=args.apply)
            total += len(acts)
            for a in acts:
                print(f"{_nfc(day.name)}: {a}")
            if acts:
                n_move = sum(a.startswith("move ") for a in acts)
                print(f"{_nfc(day.name)}: {n_move} move, {len(acts) - n_move} rewrite")
        verb = "applied" if args.apply else "planned (dry-run)"
        print(f"{total} actions {verb}" if total else "nothing to do")

    if args.check:
        broken = [f"{_nfc(day.name)}/{b}" for day in days for b in broken_links(day)]
        for b in broken:
            print(f"broken: {b}")
        print(f"{len(broken)} broken links")
        return 1 if broken else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
