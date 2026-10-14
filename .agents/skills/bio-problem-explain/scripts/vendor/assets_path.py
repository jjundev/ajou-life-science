"""
복습노트/<날짜>/ 부속 파일을 숨김 폴더 `.assets/`로 옮길 때 쓰는 경로 규칙 (표준 라이브러리만 사용).

날짜 폴더 루트에는 *.html 과 .pack/ 만 남고, MD·figures_*·자료_*·풀이기록·장마감_*.md 는
모두 `.assets/` 안으로 간다. 이 모듈은 그 판정과 상대 URL 변환만 맡는 순수 함수 모음이다.
URL 조각은 원문(인코딩된 채)을 그대로 이어 붙이고, 디코드·NFC 값은 판정에만 쓴다.
(macOS는 한글 이름을 NFD로 저장하므로 비교는 항상 NFC로 한다.)
웹과제예상/<N>장/ 은 같은 규칙을 side=PACK(".pack")으로 쓴다.
"""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import unquote

SIDE = ".assets"
PACK = ".pack"

_STAY = {PACK, SIDE, ".DS_Store", ""}
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_DATE = re.compile(r"\d{4}(-\d{4})?")
_MD_TARGET = re.compile(r"(\]\()([^)\s]+)(\))")


def _nfc(name: str) -> str:
    return unicodedata.normalize("NFC", name)


def moves(name: str, side: str = SIDE) -> bool:
    """폴더 바로 아래 항목 `name`이 부속 폴더 `side`로 가는가."""
    name = _nfc(name)
    if name in _STAY or name == side:
        return False
    return not name.lower().endswith((".html", ".htm"))


def _segment_moves(piece: str, side: str) -> bool:
    """URL 경로 조각(?query·#fragment 포함 가능, 인코딩 가능)이 `side`로 가는가."""
    return moves(unquote(re.split(r"[?#]", piece, maxsplit=1)[0]), side)


def _is_external(url: str) -> bool:
    return not url or url[0] in "#/" or bool(_SCHEME.match(url))


def _strip_dot_slash(url: str) -> str:
    while url.startswith("./"):
        url = url[2:]
    return url


def relocate(url: str, side: str = SIDE) -> str:
    """폴더 루트 HTML/MD 기준 상대 URL을 `side/` 이전 뒤 위치로 바꾼다."""
    if _is_external(url):
        return url
    path = _strip_dot_slash(url)
    parts = path.split("/")
    if parts[0] == "..":
        if (len(parts) >= 3 and _DATE.fullmatch(_nfc(unquote(parts[1])))
                and _segment_moves(parts[2], side)):
            return "/".join(parts[:2] + [side] + parts[2:])
        return url
    if _segment_moves(parts[0], side):
        return f"{side}/{path}"
    return url


def rebase_md(text: str, side: str = SIDE) -> str:
    """폴더 루트 기준으로 쓰인 MD의 `](target)`을 `side/` 안 MD 기준으로 바꾼다."""
    def fix(m: re.Match) -> str:
        target = m.group(2)
        if _is_external(target):
            return m.group(0)
        target = _strip_dot_slash(target)
        if target.startswith(side + "/"):
            target = target[len(side) + 1:]
        else:
            target = "../" + target
        return m.group(1) + target + m.group(3)

    return _MD_TARGET.sub(fix, text)


def migrate_md(text: str, side: str = SIDE) -> str:
    """폴더 루트에 있던 MD를 `side/` 안 위치에 맞게 고친다(이전 때 한 번만 적용)."""
    return rebase_md(_MD_TARGET.sub(lambda m: m.group(1) + relocate(m.group(2), side) + m.group(3), text), side)
