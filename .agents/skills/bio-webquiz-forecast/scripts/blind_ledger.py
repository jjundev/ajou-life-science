#!/usr/bin/env python3
"""블라인드 풀이 결과를 카드 해시와 함께 쌓는 기록(ledger).

카드를 고치면 바뀐 카드만 새 리뷰어가 다시 풀고(delta) 기존 판정과 병합한다.
해설기의 `mpe_cli.py import-blind`가 이 기록으로 independent 검토를 채운다.

CLI:
  blind_ledger.py record <SRC> <blind-answers.md> <ledger.json> --blind <blind.md> --round <n>
  blind_ledger.py changed <SRC> <ledger.json>     바뀌었거나 기록 없는 카드 id(쉼표 구분) 출력
  blind_ledger.py status <SRC> <ledger.json>      15/15 일치·이의 0·해시 일치면 exit 0
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROW_ID_RE = re.compile(r"^\s*\**\s*[pP](\d+)\b")
ANSWER_RE = re.compile(r"\b([A-E])\b")
EMPTY_OBJECTIONS = {"", "-", "—", "–", "없음", "none", "None", "x", "X"}
DELTA_LIMIT = 5  # 이보다 많이 바뀌면 전체를 다시 푼다


class LedgerError(RuntimeError):
    pass


def card_hash(src: Path, cid: str) -> str:
    return hashlib.sha256((src / "cards" / f"{cid}.html").read_bytes()).hexdigest()


def answer_key(src: Path) -> dict[str, str]:
    return json.loads((src / "pack.json").read_text(encoding="utf-8"))["answer_key"]


def parse_answers(text: str) -> dict[str, dict]:
    """`| 카드 | 고른 답 | 근거 | 이의 | 최소 풀이 단계 | 수준 |` 표를 읽는다."""
    rows: dict[str, dict] = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = ROW_ID_RE.match(cells[0]) if cells else None
        if not m or len(cells) < 6:
            continue
        cid = f"p{int(m.group(1))}"
        if cid in rows:
            raise LedgerError(f"{cid}: 표에 두 번 나옴")
        ans = ANSWER_RE.search(cells[1])
        objection = cells[3].strip()
        rows[cid] = {"answer": ans.group(1) if ans else "",
                     "basis": cells[2],
                     "objection": "" if objection in EMPTY_OBJECTIONS else objection,
                     "steps": cells[4], "level": cells[5]}
    if not rows:
        raise LedgerError("블라인드 답 표를 찾지 못함(| 카드 | 고른 답 | 근거 | 이의 | 최소 풀이 단계 | 수준 |)")
    return rows


def load(path: Path) -> dict:
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("cards"), dict):
            raise LedgerError(f"ledger 형식 오류: {path}")
        return data
    return {"version": 1, "src": "", "cards": {}}


def record(src: Path, answers: Path, ledger: Path, blind: Path, round_no: int) -> dict:
    src = src.resolve()
    sidecar = Path(str(blind) + ".cards.json")
    if not sidecar.is_file():
        raise LedgerError(f"사본 기록 없음: {sidecar} (blind.py로 만든 사본이어야 함)")
    copy = json.loads(sidecar.read_text(encoding="utf-8"))
    if Path(copy["src"]).resolve() != src:
        raise LedgerError(f"사본의 세트({copy['src']})와 SRC가 다름")
    rows = parse_answers(answers.read_text(encoding="utf-8"))
    if set(rows) != set(copy["cards"]):
        raise LedgerError(f"표의 카드 {sorted(rows)} ≠ 사본의 카드 {sorted(copy['cards'])}")
    data = load(ledger)
    if data["src"] and Path(data["src"]).resolve() != src:
        raise LedgerError("다른 세트의 ledger")
    data["src"] = str(src)
    for cid, row in rows.items():
        data["cards"][cid] = {**row, "sha256": copy["cards"][cid], "round": round_no,
                              "answers_file": str(answers.resolve()), "blind_file": str(blind.resolve())}
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def changed(src: Path, data: dict) -> list[str]:
    out = []
    for cid in answer_key(src):
        entry = data["cards"].get(cid)
        if entry is None or entry.get("sha256") != card_hash(src, cid):
            out.append(cid)
    return sorted(out, key=lambda c: int(c[1:]))


def problems(src: Path, data: dict) -> list[str]:
    key = answer_key(src)
    out = [f"{cid}: 블라인드 이후 카드 변경 또는 미풀이" for cid in changed(src, data)]
    for cid, want in key.items():
        entry = data["cards"].get(cid)
        if entry is None:
            continue
        if entry.get("answer") != want:
            out.append(f"{cid}: 블라인드 답 {entry.get('answer') or '없음'} ≠ answer_key {want}")
        if entry.get("objection"):
            out.append(f"{cid}: 이의 — {entry['objection']}")
    extra = set(data["cards"]) - set(key)
    if extra:
        out.append(f"answer_key에 없는 카드 기록: {sorted(extra)}")
    return out


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("src", type=Path)
    rec.add_argument("answers", type=Path)
    rec.add_argument("ledger", type=Path)
    rec.add_argument("--blind", type=Path, required=True)
    rec.add_argument("--round", type=int, required=True)
    for name in ("changed", "status"):
        p = sub.add_parser(name)
        p.add_argument("src", type=Path)
        p.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            data = record(args.src, args.answers, args.ledger, args.blind, args.round)
            print(f"record: {len(data['cards'])}개 카드 기록 → {args.ledger}")
            return 0
        data = load(args.ledger)
        if args.command == "changed":
            ids = changed(args.src, data)
            print(",".join(ids))
            if len(ids) > DELTA_LIMIT:
                print(f"바뀐 카드 {len(ids)}개 > {DELTA_LIMIT}: 전체 블라인드를 다시 푼다", file=sys.stderr)
            return 0
        found = problems(args.src, data)
        total = len(answer_key(args.src))
        if found:
            print("\n".join(found))
            return 1
        print(f"OK: 블라인드 {total}/{total} 일치 · 이의 0 · 카드 해시 일치")
        return 0
    except (LedgerError, OSError, KeyError, ValueError) as e:
        print(f"[ledger] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
