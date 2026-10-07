"""낡은 커닝페이퍼를 찾는다. spec.json의 basis를 지금 저장소 상태와 비교한다.

사용: python3 stale.py REPO [--basis]
  --basis  지금 상태로 채운 basis JSON만 출력한다(새 spec에 붙여 넣을 값).
출력: 낡은 시트마다 "N장: 이유" 한 줄. 없으면 "낡은 시트 없음". 종료 코드는 언제나 0.

낡음 기준: basis 없음 / 등록된 웹과제가 basis.webquiz보다 많음 / panic-patterns 해시가 다름.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

SKILL = Path(__file__).resolve().parents[1]
PANIC = SKILL / "references" / "panic-patterns.md"
BASIS_KEYS = ("built", "webquiz", "panic_patterns")


def panic_hash(path: Path = PANIC) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def registered_webquiz(repo: Path) -> list[str]:
    """questions.json이나 raw/ 화면이 있는 웹과제 장 목록("1장" 꼴, 장 번호 순)."""
    found = []
    for d in (repo / "웹과제").glob("*장"):
        if re.fullmatch(r"\d+장", d.name) and ((d / "questions.json").exists() or any((d / "raw").glob("*"))):
            found.append(d.name)
    return sorted(found, key=lambda s: int(s[:-1]))


def current_basis(repo: Path, panic: Path = PANIC) -> dict:
    return {"built": date.today().isoformat(), "webquiz": registered_webquiz(repo),
            "panic_patterns": panic_hash(panic)}


def stale_reasons(spec: dict, repo: Path, panic: Path = PANIC) -> list[str]:
    b = spec.get("basis")
    if not isinstance(b, dict) or any(k not in b for k in BASIS_KEYS):
        return ["basis 없음(이 기능 전에 만든 시트)"]
    why = []
    new = [w for w in registered_webquiz(repo) if w not in b["webquiz"]]
    if new:
        why.append(f"새 웹과제 미반영: {', '.join(new)}")
    if b["panic_patterns"] != panic_hash(panic):
        why.append("panic-patterns 갱신 전")
    return why


def scan(repo: Path, panic: Path = PANIC) -> list[tuple[str, list[str]]]:
    out = []
    root = repo / "웹과제예상" / "커닝페이퍼"
    for spec_path in sorted(root.glob("*장/spec.json"), key=lambda p: int(p.parent.name[:-1])):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        why = stale_reasons(spec, repo, panic)
        if why:
            out.append((spec_path.parent.name, why))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--basis", action="store_true")
    a = ap.parse_args(argv)
    if a.basis:
        print(json.dumps(current_basis(a.repo), ensure_ascii=False))
        return 0
    rows = scan(a.repo)
    for ch, why in rows:
        print(f"{ch}: {' / '.join(why)}")
    if not rows:
        print("낡은 시트 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
