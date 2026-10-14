"""웹과제예상/<N>장/ 부속 파일을 숨김 폴더 `.pack/`으로 옮기는 일회성 이전 스크립트.

장 폴더 루트에는 *.html 과 .pack/ 만 남긴다. `src/v<K>/`는 `.pack/v<K>/`로, 그 밖의 비 HTML
항목(문제해설 MD, figures_*, 자료_*)은 `.pack/<이름>`으로 간다. 루트 HTML의 상대 src/href는
`relocate`로, 옮긴 MD의 `](t)`는 `migrate_md`로, 자료 폴더의 manifest.json·validation.json은
`rewrite_record`로 고친다.

    python scripts/migrate_forecast_pack.py [ROOT=웹과제예상] [--apply] [--check]

기본은 dry-run(할 일만 출력)이다. 새 내용은 옮기기 전에 모두 계산하고, 충돌이 있으면 아무것도
옮기지 않는다. 파일은 바이트로 읽고 써서 CRLF를 지킨다. 두 번 돌려도 결과가 같다.
git 기록은 커밋 때 `git add -A 웹과제예상`의 rename 감지가 처리한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
REVIEW_SCRIPTS = REPO / ".agents" / "skills" / "bio-review-pack" / "scripts"
if str(REVIEW_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS))

from assets_path import PACK, migrate_md, moves, relocate  # noqa: E402

SRC = "src"
RECORDS = ("manifest.json", "validation.json")
HASHED = ("files", "artifact_hashes")

_ATTR = re.compile(r'(src|href)="([^"]*)"')
# 검사용: `](t)`, `](t "제목")`, `](<t>)` 모두에서 대상만 뽑는다.
_MD_CHECK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
_CHAPTER = re.compile(r"[1-9]\d*장")
_VERSION = re.compile(r"v\d+")
_SRC_PATH = re.compile(r"([\\/])src([\\/])(v\d+)(?=[\\/])")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _nfc(name: str) -> str:
    return unicodedata.normalize("NFC", name)


def _read(p: Path) -> str:
    return p.read_bytes().decode("utf-8")


def _write(p: Path, text: str) -> None:
    p.write_bytes(text.encode("utf-8"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_html(name: str) -> bool:
    return _nfc(name).lower().endswith((".html", ".htm"))


def rewrite_html(text: str) -> str:
    """장 폴더 루트 HTML의 상대 src/href를 `.pack/` 이전 뒤 위치로 고친다."""
    return _ATTR.sub(lambda m: f'{m.group(1)}="{relocate(m.group(2), PACK)}"', text)


def rewrite_record(text: str, digests: dict[str, str]) -> str:
    """해설 manifest.json·validation.json 본문을 이전 뒤 위치에 맞게 고친다.

    문자열 속 `src\\v<K>`·`src/v<K>` 경로는 `.pack`으로, `files`·`artifact_hashes`의 장 폴더 기준
    키는 `relocate`로 옮긴다. 키가 `digests`(옛 키 NFC → 새 내용 해시)에 있으면 해시도 바꾼다.
    """
    nl = "\r\n" if "\r\n" in text else "\n"

    def fix(o):
        if isinstance(o, dict):
            return {k: fix(v) for k, v in o.items()}
        if isinstance(o, list):
            return [fix(x) for x in o]
        if isinstance(o, str):
            return _SRC_PATH.sub(lambda m: m.group(1) + PACK + m.group(2) + m.group(3), o)
        return o

    data = fix(json.loads(text))
    for key in HASHED:
        if isinstance(data.get(key), dict):
            data[key] = {relocate(name, PACK): digests.get(_nfc(name), digest)
                         for name, digest in data[key].items()}
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").replace("\n", nl)


def _sorted(paths):
    return sorted(paths, key=lambda p: _nfc(p.name))


def migrate_chapter(chapter: Path, apply: bool) -> list[str]:
    """장 폴더 하나의 할 일(`move X -> Y`, `rewrite Z`)을 돌려주고, `apply`일 때만 실행한다."""
    chapter = Path(chapter)
    pack = chapter / PACK
    src = chapter / SRC
    versions = _sorted(p for p in src.iterdir() if p.is_dir()) if src.is_dir() else []
    if src.is_dir() and any(not (p.is_dir() and _VERSION.fullmatch(p.name)) for p in src.iterdir()):
        raise ValueError(f"{src}에 v<K> 폴더가 아닌 항목이 있음")
    movers = [p for p in _sorted(chapter.iterdir()) if _nfc(p.name) != SRC and moves(p.name, PACK)]
    plan = [(v, pack / v.name) for v in versions] + [(p, pack / p.name) for p in movers]
    clash = [str(dst.relative_to(chapter)) for _, dst in plan if dst.exists()]
    if clash:
        raise FileExistsError(f"{chapter}에 이미 있음: {', '.join(clash)}")

    # 옮기기 전에 새 내용을 모두 계산한다.
    digests: dict[str, str] = {}
    html = []
    for p in _sorted(q for q in chapter.iterdir() if q.is_file() and _is_html(q.name)):
        old = _read(p)
        new = rewrite_html(old)
        if new != old:
            html.append((p, new))
            digests[_nfc(p.name)] = _sha(new)
    mds = []
    for p in movers:
        if p.is_file() and _nfc(p.name).lower().endswith(".md"):
            old = _read(p)
            new = migrate_md(old, PACK)
            if new != old:
                mds.append((p.name, new))
                digests[_nfc(p.name)] = _sha(new)
    records = []
    for p in movers:
        for name in RECORDS:
            f = p / name
            if p.is_dir() and f.is_file():
                old = _read(f)
                new = rewrite_record(old, digests)
                if new != old:
                    records.append((Path(p.name) / name, new))
                    # validation.json records manifest.json's hash; RECORDS order rewrites manifest first.
                    digests[_nfc(f"{p.name}/{name}")] = _sha(new)

    actions = [f"move {SRC}/{v.name} -> {PACK}/{v.name}" for v in versions]
    actions += [f"move {_nfc(p.name)} -> {PACK}/{_nfc(p.name)}" for p in movers]
    actions += [f"rewrite {_nfc(p.name)}" for p, _ in html]
    actions += [f"rewrite {PACK}/{_nfc(name)}" for name, _ in mds]
    actions += [f"rewrite {PACK}/{_nfc(rel.as_posix())}" for rel, _ in records]
    if apply and actions:
        pack.mkdir(exist_ok=True)
        for old, dst in plan:
            os.rename(old, dst)
        if src.is_dir():
            src.rmdir()
        for p, new in html:
            _write(p, new)
        for name, new in mds:
            _write(pack / name, new)
        for rel, new in records:
            _write(pack / rel, new)
    return actions


def _relative(url: str) -> bool:
    return bool(url) and url[0] not in "#/" and not _SCHEME.match(url)


def _missing(base: Path, url: str) -> bool:
    path = unquote(re.split(r"[?#]", url, maxsplit=1)[0])
    return bool(path) and not os.path.exists(base / path)


def problems(chapter: Path) -> list[str]:
    """루트에 남은 비 HTML 항목(`stray: …`)과 대상이 없는 상대 링크(`broken: …`)."""
    chapter = Path(chapter)
    out = [f"stray: {_nfc(p.name)}" for p in _sorted(chapter.iterdir())
           if _nfc(p.name) not in (PACK, ".DS_Store") and not _is_html(p.name)]
    for p in _sorted(q for q in chapter.iterdir() if q.is_file() and _is_html(q.name)):
        for m in _ATTR.finditer(_read(p)):
            if _relative(m.group(2)) and _missing(chapter, m.group(2)):
                out.append(f"broken: {_nfc(p.name)}: {m.group(2)}")
    pack = chapter / PACK
    if pack.is_dir():
        for p in _sorted(q for q in pack.iterdir() if q.is_file() and _nfc(q.name).lower().endswith(".md")):
            for m in _MD_CHECK.finditer(_read(p)):
                if _relative(m.group(1)) and _missing(pack, m.group(1)):
                    out.append(f"broken: {PACK}/{_nfc(p.name)}: {m.group(1)}")
    return out


def _chapters(root: Path) -> list[Path]:
    return _sorted(p for p in root.iterdir() if p.is_dir() and _CHAPTER.fullmatch(_nfc(p.name)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="웹과제예상 장 폴더 부속 파일을 .pack/으로 옮긴다.")
    ap.add_argument("root", nargs="?", default="웹과제예상")
    ap.add_argument("--apply", action="store_true", help="실제로 옮기고 고친다(기본은 dry-run)")
    ap.add_argument("--check", action="store_true", help="남은 항목·깨진 링크를 출력하고 있으면 종료 코드 1")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Windows 콘솔에서 한글 이름 출력
        sys.stdout.reconfigure(encoding="utf-8")

    root = Path(args.root)
    if not root.is_dir():
        print(f"폴더 없음: {root}", file=sys.stderr)
        return 2
    chapters = _chapters(root)

    if args.apply or not args.check:
        total = 0
        for ch in chapters:
            acts = migrate_chapter(ch, apply=args.apply)
            total += len(acts)
            for a in acts:
                print(f"{_nfc(ch.name)}: {a}")
        verb = "applied" if args.apply else "planned (dry-run)"
        print(f"{total} actions {verb}" if total else "nothing to do")

    if args.check:
        found = [f"{_nfc(ch.name)}/{x}" for ch in chapters for x in problems(ch)]
        for x in found:
            print(x)
        print(f"{len(found)} problems")
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
