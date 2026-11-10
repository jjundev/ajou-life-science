#!/usr/bin/env python3
"""9단계 해설 연결 준비: explanation-retry.json(attempt=0·검증 스냅샷) 기록 + bio-problem-explain extract.

CLI:
  explain_handoff.py init --repo <REPO> --html <연습형 v<K>.html> --controller-run <RUN> --explain-run <빈 EXPLAIN_RUN>

이미 retry 기록이 있으면 attempt·history를 보존하고 active_explain_run만 바꾼다(새 RUN 재추출).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

EXPLAIN_CLI = Path(__file__).resolve().parents[2] / "bio-problem-explain" / "scripts" / "mpe_cli.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(html: Path) -> dict[str, str]:
    m = re.search(r"_v(\d+)\.html$", html.name)
    if not m or "_시험형_" in html.name:
        raise SystemExit("연습형 문제판(복습문제_<N>장_웹과제예상_v<K>.html)의 명시 경로가 필요해요")
    src = html.parent / ".pack" / f"v{m.group(1)}"
    files = [html, html.with_name(html.name.replace("_v", "_시험형_v"))]
    files += sorted(p for p in src.rglob("*") if p.is_file())
    return {str(p.resolve()): sha256(p) for p in files if p.is_file()}


def init(repo: Path, html: Path, controller: Path, explain_run: Path) -> int:
    html = html.resolve()
    controller.mkdir(parents=True, exist_ok=True)
    retry_path = controller / "explanation-retry.json"
    retry = json.loads(retry_path.read_text(encoding="utf-8")) if retry_path.is_file() else {
        "attempt": 0, "active_explain_run": "", "history": [], "verified_snapshot": {}}
    retry["active_explain_run"] = str(explain_run.resolve())
    retry["verified_snapshot"] = {"html": str(html), "files": snapshot(html)}
    retry_path.write_text(json.dumps(retry, ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run([sys.executable, str(EXPLAIN_CLI), "extract", "--repo", str(repo),
                             "--target", str(html), "--run", str(explain_run)])
    if result.returncode:
        return result.returncode
    for folder in explain_run.iterdir():
        if folder.is_dir() and (folder / "evidence").is_dir():
            (folder / "evidence" / "explanation-retry.json").write_text(
                retry_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"handoff: attempt={retry['attempt']} · 스냅샷 {len(retry['verified_snapshot']['files'])}개 → {retry_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--html", type=Path, required=True)
    p.add_argument("--controller-run", type=Path, required=True)
    p.add_argument("--explain-run", type=Path, required=True)
    args = parser.parse_args(argv)
    return init(args.repo, args.html, args.controller_run, args.explain_run)


if __name__ == "__main__":
    sys.exit(main())
