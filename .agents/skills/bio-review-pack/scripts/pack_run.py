#!/usr/bin/env python3
"""
복습팩 실행 기록 집계기 (표준 라이브러리만 사용).

서브에이전트는 상세 결과를 RUN/work/reports/ 의 TSV 파일에 쓰고 메인에는 영수증만 돌려준다.
이 스크립트가 그 파일들을 합치고 대조해, 메인 에이전트가 읽을 몇 줄만 출력한다.
규칙은 references/report-contract.md 에 있다.

  pack_run.py context       --run RUN --sid s3     섹션 작성자가 자기 브리프 값을 직접 읽는다
  pack_run.py merge-problems --run RUN             문항 감사자의 work/problems.json 을 manifest 에 넣는다
  pack_run.py audit-merge   --run RUN              rows-*.tsv → RUN/summary-audit.md
  pack_run.py feedback-merge --run RUN             feedback-*.tsv → RUN/note-feedback-audit.md 의 적용 상태 절
  pack_run.py blind-check   --run RUN              blind.tsv 답·수준 대조 및 문항 이의 처리 → RUN/blind-results.md
  pack_run.py fixes         --run RUN              findings-*.tsv → 담당 작성자별 RUN/work/fixes/<담당>.txt
  pack_run.py status        --run RUN              보고서용 집계 한 화면
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

REPORTS = Path("work") / "reports"
FIXES = Path("work") / "fixes"
SEVERITIES = ("critical", "important", "minor-easy", "minor")
APPLIED = ("critical", "important", "minor-easy")
BAD_VERDICT = re.compile(r"누락|수정 필요")
APPLIED_HEAD = "## 작성 후 적용 상태"
MAX_LINES = 12


class RunError(ValueError):
    pass


def load_manifest(run: Path) -> dict:
    path = run / "manifest.json"
    if not path.is_file():
        raise RunError(f"manifest 없음: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_tsv(path: Path, columns: int) -> list[list[str]]:
    """탭 구분 행을 읽는다. 머리글 행(#으로 시작)과 빈 줄은 건너뛰고, 칸 수가 모자라면 빈 칸으로 채운다."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = [c.strip() for c in line.split("\t")]
        if len(cells) > columns:
            cells = cells[: columns - 1] + [" ".join(cells[columns - 1:])]
        rows.append(cells + [""] * (columns - len(cells)))
    return rows


def report_files(run: Path, prefix: str) -> list[Path]:
    folder = run / REPORTS
    return sorted(folder.glob(f"{prefix}*.tsv")) if folder.is_dir() else []


def topic_sections(m: dict) -> dict[str, str]:
    return {t["id"]: s["id"] for s in m["sections"] for t in s["topics"]}


def card_group(pid: str) -> str:
    """p1–p10 → cards-p1, p11–p20 → cards-p11 (카드 작성자 묶음)."""
    n = int(pid[1:])
    return f"cards-p{(n - 1) // 10 * 10 + 1}"


def owner_of(item_id: str, m: dict) -> str | None:
    """결함 id(토픽·섹션·카드)를 고칠 담당 작성자를 찾는다."""
    topics = topic_sections(m)
    sections = {s["id"] for s in m["sections"]}
    cards = {p["id"] for p in m["problems"]}
    if item_id in topics:
        return topics[item_id]
    if item_id in sections:
        return item_id
    if item_id in cards:
        return card_group(item_id)
    head = item_id.split("-", 1)[0]
    return head if head in sections else None


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def short(lines: list[str], limit: int = MAX_LINES) -> list[str]:
    if len(lines) <= limit:
        return lines
    return lines[:limit] + [f"… 외 {len(lines) - limit}건 (파일 참조)"]


# ---------- context ----------

def audit_rows_for(run: Path, sources: set[str]) -> dict[str, str]:
    """question-audit.md 에서 '출처 번호' → '질문 요약 / 필요한 개념' 을 뽑는다(없으면 빈 dict)."""
    path = run / "question-audit.md"
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and f"{cells[0]} {cells[1]}" in sources:
            out[f"{cells[0]} {cells[1]}"] = f"{cells[2]} / 필요한 개념: {cells[3]}"
    return out


def context(run: Path, sid: str) -> str:
    m = load_manifest(run)
    section = next((s for s in m["sections"] if s["id"] == sid), None)
    if section is None:
        raise RunError(f"섹션 없음: {sid}")
    ids = [t["id"] for t in section["topics"]]
    problems = [p for p in m["problems"] if p.get("anchor") in ids]
    audit = audit_rows_for(run, {p["source"] for p in problems})
    out = [f"# 섹션 {sid} — {section['title']}", "", "## 토픽"]
    for t in section["topics"]:
        out.append(f"- {t['id']} · {t['title']} · layers={t['layers']} · supp={t.get('supp', False)}")
        out.append(f"  required_terms: {json.dumps(t['required_terms'], ensure_ascii=False)}")
    out += ["", "## 이 섹션의 links (href 글자 그대로)"]
    links = [l for l in m["links"] if l["topic"] in ids]
    out += [f"- {l['topic']} → {l['href']}" for l in links] or ["- 없음"]
    out += ["", "## 이 섹션 토픽이 받쳐야 할 문항 (번호·정답은 본문에 쓰지 않는다)"]
    for p in problems:
        terms = [t for t in p.get("terms", []) if not t.startswith("정답:")]
        out.append(f"- {p['anchor']} ← {p['source']} (수준 {p.get('level')}) · 판별 용어 {json.dumps(terms, ensure_ascii=False)}"
                   + (f" · {audit[p['source']]}" if p["source"] in audit else ""))
    if not problems:
        out.append("- 없음")
    out += ["", f"## 금지어 (예고 토픽 {m['preview_topic']} 안에서만 허용)",
            json.dumps(m["forbidden_outside_preview"], ensure_ascii=False)]
    return "\n".join(out)


# ---------- merge-problems ----------

def merge_problems(run: Path) -> list[str]:
    m = load_manifest(run)
    path = run / "work" / "problems.json"
    if not path.is_file():
        raise RunError(f"문항 설계 없음: {path}")
    design = json.loads(path.read_text(encoding="utf-8"))
    problems = design.get("problems", [])
    topics = {t["id"]: t for s in m["sections"] for t in s["topics"]}
    errors = [f"{p.get('id')}: anchor {p.get('anchor')!r} 가 manifest 토픽이 아님"
              for p in problems if p.get("anchor") not in topics]
    if errors:
        raise RunError("\n".join(errors))
    m["problems"] = problems
    if "parts" in design:
        m["parts"] = design["parts"]
    out = [f"문항 {len(problems)}개 반영 (" + ", ".join(
        f"{part} {sum(p.get('part') == part for p in problems)}" for part in ("partA", "partB", "partC")) + ")"]
    for req in design.get("topic_requests", []):
        t = topics.get(req.get("topic"))
        if t is None:
            out.append(f"요청 무시: 토픽 {req.get('topic')!r} 없음")
            continue
        added = [x for x in req.get("add_terms", []) if x and x not in t["required_terms"]]
        t["required_terms"] += added
        if req.get("supp") and not t.get("supp"):
            t["supp"] = True
            added.append("supp=true")
        if added:
            out.append(f"{t['id']}: {', '.join(added)} — {req.get('why', '')}".rstrip(" —"))
    (run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return short(out)


# ---------- audit-merge ----------

def audit_merge(run: Path) -> list[str]:
    m = load_manifest(run)
    order = {t: i for i, t in enumerate(topic_sections(m))}
    rows, files = [], report_files(run, "rows-")
    for f in files:
        rows += read_tsv(f, 4)
    if not rows:
        raise RunError(f"감사행 없음: {run / REPORTS}/rows-<sid>.tsv")
    rows.sort(key=lambda r: order.get(r[0], len(order)))
    bad = [r for r in rows if BAD_VERDICT.search(r[3])]
    learn = [t["id"] for s in m["sections"] for t in s["topics"] if t["layers"]]
    covered = {r[0] for r in rows}
    lead = {r[0] for r in rows if r[1].startswith("첫 문장 검토")}
    no_rows = [t for t in learn if t not in covered]
    no_lead = [t for t in learn if t in covered and t not in lead]
    text = [f"# {m['range']} 본문–요약 전수 대조", "",
            f"행 {len(rows)}개 · 누락/수정 필요 {len(bad)}개 · 감사행 없는 학습 토픽 {len(no_rows)}개 · 첫 문장 검토 없는 토픽 {len(no_lead)}개",
            "", "| 토픽 | 본문의 핵심 주장 | 대응하는 요약 문장 | 판정·생략 이유 |", "|---|---|---|---|"]
    text += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    (run / "summary-audit.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    findings = [["important", r[0], f"요약 대조 {r[3]}: {r[1]}", "요약 문장을 고치고 감사행을 다시 쓴다"] for r in bad]
    findings += [["important", t, "감사행이 없다", "본문–요약 전수 대조 감사행을 쓴다"] for t in no_rows]
    findings += [["important", t, "첫 문장 검토 행이 없다", "첫 문장 검토 행을 더한다"] for t in no_lead]
    write_findings(run, "audit", findings)
    out = [f"summary-audit.md: 행 {len(rows)} (파일 {len(files)}) · 누락/수정 필요 {len(bad)} · 감사행 없음 {len(no_rows)} · 첫 문장 검토 없음 {len(no_lead)}"]
    out += [f"- {r[0]}: {r[3]}" for r in bad] + [f"- {t}: 감사행 없음" for t in no_rows] + [f"- {t}: 첫 문장 검토 없음" for t in no_lead]
    return short(out)


def write_findings(run: Path, name: str, findings: list[list[str]]) -> None:
    path = run / REPORTS / f"findings-{name}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if findings:
        path.write_text("".join("\t".join(c.replace("\t", " ") for c in f) + "\n" for f in findings), encoding="utf-8")
    elif path.exists():
        path.unlink()


# ---------- feedback-merge ----------

def feedback_merge(run: Path) -> list[str]:
    path = run / "note-feedback-audit.md"
    rows, files = [], report_files(run, "feedback-")
    for f in files:
        rows += read_tsv(f, 4)
    if not path.is_file():
        raise RunError(f"본문 피드백 감사표 없음: {path}")
    base = path.read_text(encoding="utf-8").split(APPLIED_HEAD)[0].rstrip("\n")
    table = [APPLIED_HEAD, "", "| 피드백 ID | 실제 토픽 | 본문 문장 | 반영 상태 |", "|---|---|---|---|"]
    table += ["| " + " | ".join(cell(c) for c in r) + " |" for r in sorted(rows)]
    path.write_text(base + "\n\n" + "\n".join(table) + "\n", encoding="utf-8")
    states: dict[str, int] = {}
    for r in rows:
        key = r[3].split(":", 1)[0].split(" — ", 1)[0].strip() or "상태 없음"
        states[key] = states.get(key, 0) + 1
    return [f"note-feedback-audit.md: 적용 상태 {len(rows)}행 (파일 {len(files)}) · "
            + " · ".join(f"{k} {v}" for k, v in sorted(states.items()))]


# ---------- blind-check ----------

def norm_answer(text: str) -> str:
    return re.sub(r"\s+", "", text).strip("`").lower()


def blind_check(run: Path) -> list[str]:
    m = load_manifest(run)
    path = run / REPORTS / "blind.tsv"
    if not path.is_file():
        raise RunError(f"블라인드 결과 없음: {path}")
    got = {r[0]: r for r in read_tsv(path, 7)}
    only = set(got)  # 재검사·보강에서는 사본에 넣은 문항만 대조한다
    wrong_count = objection_count = unrecorded_count = 0
    issues, level_diff, findings, table = [], [], [], []
    problems = [p for p in m["problems"] if p["id"] in only]
    for p in problems:
        r = got[p["id"]]
        pid = p["id"]
        ok = norm_answer(r[1]) == norm_answer(str(p["answer"]))
        level = r[5].strip()
        objection = "" if r[6] == "없음" else r[6]
        unrecorded_count += not r[6]
        result = "일치" if ok else "불일치"
        table.append(f"| {pid} | {cell(r[1])} | {p['answer']} | {result} | {cell(r[2])} | {cell(r[3])} | {cell(r[4])} | {level} | {p.get('level')} | {cell(r[6] or '미기록')} |")
        detail = []
        if not ok:
            wrong_count += 1
            detail.append(f"리뷰어 {r[1]} / manifest {p['answer']} — {r[3] or '빠진 사실 미기재'}")
        if objection:
            objection_count += 1
            detail.append(f"문항 이의: {objection}")
        if detail:
            reason = " · ".join(detail)
            issues.append(f"- {pid} ({p['source']}, anchor {p['anchor']}): {reason}")
            if objection:
                target = pid
                fix = ("변형의 발문·조건·보기를 검토해 정답을 하나로 고치고 다시 풀이한다" if p.get("variant")
                       else "원문 발문·보기는 보존한다. 근거를 문항 감사 담당과 대조하고, 이의가 타당하면 key-check.md와 카드의 채점 주의·해설에 반영한다")
            elif p.get("variant"):
                target = pid
                fix = "변형이 유일 정답·범위 안인지 먼저 확인하고, 멀쩡하면 anchor 토픽에 빠진 사실을 가르친다"
            else:
                target = p["anchor"]
                fix = "빠진 사실을 본문이나 보충 레이어에 가르친다(카드 풀이를 바꿔 맞추지 않는다)"
            findings.append(["critical", target, f"블라인드 {pid}: {reason}", fix])
        if level != str(p.get("level")):
            level_diff.append(f"{pid}({'변형' if p.get('variant') else '원문'} 설계 {p.get('level')}→독립 {level or '?'})")
    unknown = sorted(only - {p["id"] for p in m["problems"]})
    head = (f"정리노트만으로 {len(problems) - wrong_count}/{len(problems)} 풀림(답 일치) · "
            f"불일치·근거 없음 {wrong_count} · 문항 이의 {objection_count} · "
            f"문항 이의 미기록 {unrecorded_count} · 수준 불일치 {len(level_diff)}")
    text = [f"# {m['range']} 블라인드 풀이 검사", "", head, "",
            "| 문항 | 리뷰어 답 | manifest | 대조 | 근거 토픽 | 빠진 사실 | 최소 풀이 단계 | 독립 수준 | 설계 수준 | 문항 이의 |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    out_path = run / "blind-results.md"
    previous = out_path.read_text(encoding="utf-8").rstrip("\n") + "\n\n" if out_path.is_file() else ""
    out_path.write_text(previous + "\n".join(text + table) + "\n", encoding="utf-8")
    write_findings(run, "blind", findings)
    out = [f"blind-results.md: {head}"] + issues
    if level_diff:
        out.append("수준 불일치: " + ", ".join(level_diff))
    if unknown:
        out.append("manifest에 없는 문항 id: " + ", ".join(unknown))
    return short(out)


# ---------- fixes ----------

def collect_findings(run: Path) -> list[list[str]]:
    rows = []
    for f in report_files(run, "findings-"):
        source = f.stem[len("findings-"):]
        for r in read_tsv(f, 4):
            sev = r[0].lower()
            rows.append([sev if sev in SEVERITIES else "important", r[1].strip("[]`"), r[2], r[3], source])
    return rows


def fixes(run: Path) -> list[str]:
    m = load_manifest(run)
    rows = collect_findings(run)
    folder = run / FIXES
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.txt"):
        old.unlink()
    by_owner: dict[str, list[list[str]]] = {}
    orphans, skipped = [], []
    for r in rows:
        if r[0] not in APPLIED:
            skipped.append(r)
            continue
        owner = owner_of(r[1], m)
        (by_owner.setdefault(owner, []) if owner else orphans).append(r)
    for owner, items in sorted(by_owner.items()):
        items.sort(key=lambda r: (SEVERITIES.index(r[0]), r[1]))
        body = [f"# {owner} 수정 요청 ({len(items)}건) — 모두 고친 뒤 영수증만 보고한다", ""]
        body += [f"- [{r[0]}] {r[1]} ({r[4]}): {r[2]} → {r[3]}" for r in items]
        (folder / f"{owner}.txt").write_text("\n".join(body) + "\n", encoding="utf-8")
    unapplied = run / REPORTS / "unapplied.tsv"
    left = skipped + orphans
    if left:
        unapplied.parent.mkdir(parents=True, exist_ok=True)
        unapplied.write_text("".join("\t".join(c.replace("\t", " ") for c in r) + "\n" for r in left), encoding="utf-8")
    elif unapplied.exists():
        unapplied.unlink()
    counts = {s: sum(r[0] == s for r in rows) for s in SEVERITIES}
    out = ["결함 " + " · ".join(f"{s} {n}" for s, n in counts.items()) + f" → 수정 요청 {sum(map(len, by_owner.values()))}건"]
    out += [f"- {owner}: {len(items)}건 → {folder / (owner + '.txt')}" for owner, items in sorted(by_owner.items())]
    if orphans:
        out.append(f"담당을 못 찾은 결함 {len(orphans)}건 (메인이 판단): " + ", ".join(sorted({r[1] for r in orphans})))
    if skipped:
        out.append(f"반영하지 않는 minor {len(skipped)}건 → {unapplied} (보고서에 건수만 적는다)")
    return short(out, 20)


# ---------- status ----------

def status(run: Path) -> list[str]:
    m = load_manifest(run)
    problems = m["problems"]
    variants = [p for p in problems if p.get("variant")]
    out = [f"범위 {m['range']} · 섹션 {len(m['sections'])} · 토픽 {sum(len(s['topics']) for s in m['sections'])}",
           f"문항 {len(problems)}: " + " · ".join(
               f"{part['id']} {sum(p.get('part') == part['id'] for p in problems)}" for part in m["parts"])
           + f" · 변형 기본 {sum(p.get('level') in (1, 2) for p in variants)} · 심화 {sum(p.get('level') == 3 for p in variants)}"]
    for name in ("summary-audit.md", "blind-results.md"):
        path = run / name
        if path.is_file():
            lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith(("#", "|"))]
            out.append(f"{name}: {lines[-1] if lines else '요약 줄 없음'}")
        else:
            out.append(f"{name}: 없음")
    counts: dict[str, int] = {}
    for r in collect_findings(run):
        counts[r[0]] = counts.get(r[0], 0) + 1
    out.append("남은 결함 파일: " + (" · ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "없음"))
    unapplied = run / REPORTS / "unapplied.tsv"
    out.append(f"반영하지 않은 항목: {len(read_tsv(unapplied, 5)) if unapplied.is_file() else 0}건")
    fixed = report_files(run, "fixed-")
    out.append(f"수정 영수증 파일: {len(fixed)}개")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("context", "merge-problems", "audit-merge", "feedback-merge", "blind-check", "fixes", "status"):
        sub = commands.add_parser(name)
        sub.add_argument("--run", type=Path, required=True)
        if name == "context":
            sub.add_argument("--sid", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "context":
            print(context(args.run, args.sid))
            return 0
        lines = {"merge-problems": merge_problems, "audit-merge": audit_merge, "feedback-merge": feedback_merge,
                 "blind-check": blind_check, "fixes": fixes, "status": status}[args.command](args.run)
    except (RunError, json.JSONDecodeError, KeyError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
