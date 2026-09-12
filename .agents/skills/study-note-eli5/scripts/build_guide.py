#!/usr/bin/env python3
"""Render a Study Note ELI5 guide + coverage JSON + audited scope lock from a data module.

Usage: build_guide.py 정리노트/eli5-src/MMDD/guide.py [--out-dir DIR] [--force]

The data module (see references/coverage-contract.md, "Guide data module")
defines META, SOURCES, CONCEPTS, BLOCKS, FACTS, QUESTIONS, DEFERRED, SECTIONS
and BOUNDARY. The fact → HTML mapping is read from data-facts attributes, so a
fact that is not visibly taught fails the build. An existing review record is
kept; if the HTML changed, its artifact hash no longer matches and complete
validation fails until the review is redone.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import guide_kit as kit  # noqa: E402
from build_question_scope import build_lock  # noqa: E402

MARK = "①②③④⑤⑥⑦⑧⑨⑩"
SCOPE_OF = {"teaching": "teaching", "review": "review", "supplement": "supplement", "boundary": "deferred"}

CSS = """:root{--bg:#f7f8fb;--card:#fff;--ink:#172033;--muted:#5b6478;--line:#dfe5ef;--blue:#356ae6;--teal:#07877f;--rose:#b83d59;--gold:#8a5a00;--dark:#182238}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 system-ui,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}
.wrap{max-width:920px;margin:auto;padding:28px 18px 80px}header,.card,footer{border-radius:18px;padding:20px}
header{background:linear-gradient(135deg,#1d2c53,#356ae6);color:#fff}header h1{margin:.2em 0;font-size:1.6em;line-height:1.3}header a{color:#fff}
.card{background:var(--card);border:1px solid var(--line);margin-top:14px}h2{margin:.1em 0 .4em;line-height:1.35}
.kicker{margin:0;color:var(--blue);font-weight:700;font-size:.85em;letter-spacing:.04em}.pre{font-size:.9em;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.mini{margin:0;background:#f0f4fb;border:1px solid var(--line);border-radius:12px;padding:12px;font-size:.95em}
.flow{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 14px}.step{flex:1;min-width:92px;text-align:center;background:#eef3ff;border:1px solid #c9d7fb;border-radius:12px;padding:8px 6px;color:var(--ink);text-decoration:none;font-size:.9em}
.analogy{background:#fff8e6;border:1px solid #f1dca6;border-radius:14px;padding:12px 14px;margin:10px 0}.limit{background:#f4f4f6;border:1px dashed #b9bfcc;border-radius:14px;padding:10px 14px;margin:10px 0}
.warn{background:#fff0f3;border:1px solid #f3c4ce;border-radius:14px;padding:10px 14px;margin:10px 0}.analogy p,.limit p,.warn p{margin:.3em 0 0}
.b{display:inline-block;font-size:.72em;font-weight:700;border-radius:999px;padding:1px 8px;vertical-align:2px;margin-right:2px}.b.sup{background:#e6f0ff;color:#1d4fc4}.b.fix{background:#fdecef;color:#a1304b}.b.prof{background:#fff1cc;color:#7a5200}.b.rev{background:#e3f6f3;color:#056b65}.b.gen{background:#efe9fb;color:#5b3aa0}
.fig{margin:12px 0;padding:10px;background:#fbfcff;border:1px solid var(--line);border-radius:14px}.fig figcaption{font-size:.85em;color:var(--muted);margin-top:4px}svg{max-width:100%;height:auto;display:block;margin:auto}
.recall{background:#f1fbf8;border:1px solid #bfe7dd;border-radius:14px;padding:12px 14px;margin:12px 0}.recall p{margin:.3em 0}
.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;margin:10px 0;font-size:.95em}th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:#f0f4fb}
.note{font-size:.9em;color:var(--muted)}.boundary{background:#fff7e6;border:1px solid #f1dca6;border-radius:14px;padding:4px 14px;margin:10px 0}
h3.group{margin:28px 0 4px;padding-left:10px;border-left:5px solid var(--blue)}.q .qid{margin:0;color:var(--muted);font-size:.88em}.q .stem{font-weight:600;margin:.4em 0}
.opts{list-style:none;padding:0;margin:.3em 0}.opts li{padding:6px 10px;border:1px solid var(--line);border-radius:10px;margin:5px 0}
.caution{font-size:.88em;color:var(--gold);margin:.4em 0}details{margin-top:8px}summary{cursor:pointer;font-weight:700;color:var(--blue)}.diag li{margin:3px 0}
.conflict{background:#fff4d6;border:1px solid #f1dca6;border-radius:12px;padding:10px 12px;margin:8px 0;font-size:.93em}.remedy{font-size:.92em}
.deferred{background:#fafafa;border-style:dashed}blockquote{margin:8px 0;padding:6px 12px;border-left:4px solid #b9bfcc;color:var(--muted)}
footer{background:var(--dark);color:#fff;margin-top:14px}a:focus-visible,summary:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
@media(max-width:640px){.grid{grid-template-columns:1fr}.wrap{padding:16px 10px 60px}header h1{font-size:1.3em}}
@media print{body{background:#fff;color:#000;font-size:12pt}.wrap{max-width:none;padding:0}.grid{display:block}.card{break-inside:auto;border-color:#999}svg,.fig,article{break-inside:avoid}details>:not(summary){display:block!important}header{background:none;color:#000;border:1px solid #999}header a{color:#000}}"""

SCRIPT = ('<script>\nlet printState=null;window.addEventListener("beforeprint",()=>{if(printState!==null)return;'
          'printState=[...document.querySelectorAll("details")].map(el=>[el,el.open]);printState.forEach(([el])=>{el.open=true})});'
          'window.addEventListener("afterprint",()=>{if(printState===null)return;printState.forEach(([el,wasOpen])=>{el.open=wasOpen});printState=null});\n</script>')

def legend(note_name: str) -> str:
    b = kit.BADGES
    return (f'<p>표시: <span class="b sup">{b["sup"]}</span> {note_name} 본문에는 없지만 연결 문항을 풀려고 강의노트·STT·원문 그림에서 가져온 내용 · '
            f'<span class="b fix">{b["fix"]}</span> 과장·일반화를 바로잡는 단서 · <span class="b rev">{b["rev"]}</span> 직전 회차 노트 · '
            f'<span class="b prof">{b["prof"]}</span> · <span class="b gen">{b["gen"]}</span> 이 가이드가 만든 비유. '
            '회상 질문은 모두 생성 질문이며 원본 문항 수에 넣지 않습니다.</p>')

DEFAULT_ROUTINE = '''<section class="card" id="study-routine"><p class="kicker">다음 공부</p><h2>틀린 문제는 이렇게 복습합니다</h2>
<ul><li><b>용어</b>를 몰랐다 → 해설의 링크로 개념 절에 가서 굵은 글씨 정의를 소리 내어 읽습니다.</li>
<li><b>개념을 혼동</b>했다 → 개념 절의 ⚠️ 상자와 비교 문장을 봅니다.</li>
<li><b>과정·방향</b>이 헷갈렸다 → 그림의 화살표를 손으로 따라 그립니다.</li>
<li><b>조건·단위</b>를 놓쳤다 → 표의 기준 열을 다시 봅니다.</li></ul>
<p>맞혔더라도 이유를 한 문장으로 설명하지 못했다면 복습 대상입니다. 오늘은 그림과 설명을 읽고, <b>다음 공부를 시작할 때</b> 설명을 가린 채 회상 질문부터 답해 보세요. <b>주간 복습</b>에서는 여러 절의 문제를 섞어서 풉니다.</p></section>'''

QUESTIONS_INTRO = ('<section class="card" id="questions"><p class="kicker">원본 문제</p><h2>원본 문항 적용</h2>'
                   '<p>보기를 먼저 고르고(단답형은 먼저 써 보고) 해설을 여세요. 해설의 링크는 필요한 개념 절로 돌아갑니다.</p></section>')


def load_data(path: Path):
    """Import a data module with its sibling modules, then forget them."""
    data_dir = path.parent.resolve()
    before = set(sys.modules)
    kit.TITLES.clear()
    kit.BADGES.clear()
    kit.BADGES.update(kit.DEFAULT_BADGES)
    sys.path.insert(0, str(data_dir))
    try:
        spec = importlib.util.spec_from_file_location("_eli5_guide_data", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(data_dir))
        for name in set(sys.modules) - before:
            file = getattr(sys.modules[name], "__file__", None)
            if file and Path(file).resolve().is_relative_to(data_dir):
                del sys.modules[name]
    return module


def qanchor(ident: str) -> str:
    src, n = ident.split(":")
    return f"q{re.match(r'\d+', src).group(0)}-{n}"


def concept_order(reqs, fact_by_id):
    seen = []
    for r in reqs:
        c = fact_by_id[r]["concept"]
        if c and c not in seen:
            seen.append(c)
    return seen


def active_card(q, meta, fact_by_id, titles):
    fmt = "multiple_choice" if q["opts"] else "short_answer"
    status_label = {"included": "이번 회차 포함", "review": "지난 회차 복습"}[q["status"]]
    src, n = q["id"].split(":")
    label = meta["quiz_sources"][src]["label"]
    head = f'<p class="qid"><b>{src} {n}번</b> · 원문 {label} p{q["page"]} · {status_label}' + \
           (" · 원문 단답형" if fmt == "short_answer" else "") + "</p>"
    opts = "".join(f"<li>{MARK[i]} {o}</li>" for i, o in enumerate(q["opts"]))
    prompt = f'<div data-part="prompt"><p class="stem">{q["stem"]}</p>' + (f'<ul class="opts">{opts}</ul>' if opts else
             '<p class="note">원문에 보기가 없습니다. 먼저 한두 문장으로 답을 써 보세요.</p>') + "</div>"
    if q["fig"]:
        prompt += f'<p class="note">원문의 ‘위 그림’ → <a href="#{q["fig"][0]}">{q["fig_note"]}</a>을 보고 푸세요.</p>'
    caution = ('<p class="caution">⚠️ 원문·답지·동반 퀴즈와 관련해 알아 둘 점이 있습니다 — 풀고 나서 해설에서 확인하세요.</p>'
               if q["conflict"] else "")
    if fmt == "multiple_choice":
        a = q["ans"]
        if q["grading"] == "ambiguous":
            answer = f"출제 의도 정답: {MARK[a-1]} {q['opts'][a-1]}" + "".join(
                f" · 함께 인정할 수 있는 답: {MARK[i-1]} {q['opts'][i-1]}" for i in q["also_accept"])
        elif q["key"] is None:
            answer = f"정답(판단): {MARK[a-1]} {q['opts'][a-1]} — 원문에 인쇄된 정답 표시 없음"
        elif q["key"] != a:
            answer = f"정답(판단): {MARK[a-1]} {q['opts'][a-1]} — 인쇄 정답 {MARK[q['key']-1]}은 오류로 판단"
        else:
            answer = f"정답: {MARK[a-1]} {q['opts'][a-1]}"
        diag = "".join(f"<li>{MARK[i-1]} {t}</li>" for i, t in sorted(q["diag"].items()))
        extra = f'<p><b>보기별 진단</b></p><ul class="diag">{diag}</ul>'
    else:
        answer = f"원문에 인쇄된 답: “{q['printed']}”"
        extra = '<p><b>채점 기준(루브릭)</b></p><ul class="diag">' + "".join(f"<li>{r}</li>" for r in q["rubric"]) + "</ul>"
    conflict = (f'<div class="conflict" id="cf-{qanchor(q["id"])}" data-role="source-conflict"><b>원문·답지 충돌 공개</b> {q["conflict"]}</div>'
                if q["conflict"] else "")
    remedy = " · ".join(f'<a data-remedy="{q["remedy"]}" href="#concept-{c}">{titles[c]}</a>'
                        for c in concept_order(q["reqs"], fact_by_id))
    solution = (f'<details data-role="solution"><summary>정답과 근거 보기</summary>'
                f'<p data-part="answer"><b>{answer}</b></p><p data-part="reason"><b>근거</b> {q["reason"]}</p>{extra}'
                f'<p data-part="trap"><b>고르기 쉬운 함정</b> {q["trap"]}</p>{conflict}'
                f'<p class="remedy">틀렸거나 이유를 설명하지 못했다면 돌아가기: {remedy}</p></details>')
    return (f'<article class="card q" id="{qanchor(q["id"])}" data-question-id="{q["id"]}" data-status="{q["status"]}" '
            f'data-format="{fmt}">{head}{prompt}{caution}{solution}</article>')


def deferred_card(ident, reason, later):
    src, n = ident.split(":")
    return (f'<article class="card q deferred" id="{qanchor(ident)}" data-question-id="{ident}" data-status="deferred">'
            f'<p class="qid"><b>{src} {n}번</b> · 보류</p><p data-part="deferred-reason"><b>보류 사유</b> {reason}</p>'
            f'<p><b>먼저 배워야 할 후속 내용</b> {later}</p></article>')


def question_errors(d, fact_by_id):
    errors = []
    groups = {g for g, _ in d.META["groups"]}
    for q in d.QUESTIONS:
        ident = q["id"]
        if q["group"] not in groups:
            errors.append(f"unknown question group: {ident}/{q['group']}")
        if q["id"].split(":")[0] not in d.META["quiz_sources"]:
            errors.append(f"question source not in META quiz_sources: {ident}")
        unknown = [r for r in q["reqs"] if r not in fact_by_id]
        if not q["reqs"] or unknown:
            errors.append(f"question requirements empty or unknown: {ident} {unknown}")
        if q["opts"]:
            n = len(q["opts"])
            if set(q["diag"]) != set(range(1, n + 1)):
                errors.append(f"diag must cover options 1..{n}: {ident}")
            if not (isinstance(q["ans"], int) and 1 <= q["ans"] <= n) or (q["key"] is not None and not 1 <= q["key"] <= n):
                errors.append(f"answer/key out of range: {ident}")
            if q["grading"] == "ambiguous" and not q["also_accept"]:
                errors.append(f"ambiguous question needs also_accept: {ident}")
            if q["grading"] == "ambiguous" and not q["conflict"]:
                errors.append(f"ambiguous question needs a disclosed conflict: {ident}")
        elif not (q["printed"] or q["rubric"]) or q["grading"] != "rubric":
            errors.append(f"short-answer question needs printed answer, rubric and grading=rubric: {ident}")
    return errors


def build(data_path: Path, out_dir: Path | None = None, force: bool = False) -> tuple[dict, list[str]]:
    d = load_data(data_path)
    meta = d.META
    data_dir = data_path.parent.resolve()
    note_path = (data_dir / meta["note"]).resolve()
    note_dir = note_path.parent
    out_dir = (out_dir or note_dir).resolve()
    stem = meta["output_stem"]
    out_html, out_cov = out_dir / f"{stem}.html", out_dir / f"{stem}.coverage.json"
    out_lock = out_dir / f"{stem}.question-scope.json"
    errors: list[str] = []
    if out_html.exists() and not out_cov.exists() and not force:
        return {}, [f"refusing to overwrite {out_html.name}: not a build_guide output (no {out_cov.name}); use --force"]

    titles = {c: t for c, t, _ in d.CONCEPTS}
    kit.TITLES.update(titles)
    note_lines = note_path.read_text(encoding="utf-8").splitlines()
    block_by_id = {b[0]: b for b in d.BLOCKS}
    fact_by_id = {f["id"]: f for f in d.FACTS}
    if len(fact_by_id) != len(d.FACTS):
        errors.append("duplicate fact ids")

    facts_json = []
    for f in d.FACTS:
        if f["block"] not in block_by_id:
            errors.append(f"fact in unknown block: {f['id']}")
            continue
        bid, start, end, kind, _, _ = block_by_id[f["block"]]
        loc = f["loc"]
        if f["src"] == "note":
            if start is None:
                errors.append(f"note fact in a block without note lines: {f['id']}")
                hits = []
            else:
                hits = [n for n in range(start, end + 1) if f["quote"] in note_lines[n - 1]]
                if not hits:
                    errors.append(f"quote not in block: {f['id']}")
            loc = f"{note_path.name}:{hits[0] if hits else start}"
        item = {"id": f["id"], "block_id": bid, "statement": f["statement"], "kind": f["kind"],
                "qualifiers": f["qual"], "concept_id": f["concept"], "scope": SCOPE_OF[kind],
                "evidence": {"source_id": f["src"], "locator": loc, "quote": f["quote"]}}
        if f["dims"]:
            item["dimensions"] = f["dims"]
        facts_json.append(item)

    blocks_json = []
    for bid, start, end, kind, reason, qids in d.BLOCKS:
        b = {"id": bid}
        if start is not None:
            b.update(start=start, end=end)
        b.update(kind=kind, fact_ids=[f["id"] for f in d.FACTS if f["block"] == bid], reason=reason)
        if qids:
            b["question_ids"] = qids
        blocks_json.append(b)

    sources_json = [{**s, "sha256": hashlib.sha256((note_dir / s["path"]).resolve().read_bytes()).hexdigest(),
                     "read_status": "read"} for s in d.SOURCES]
    concepts_json = [{"id": c, "title": t, "prerequisites": p, "prior_note": meta.get("prior_notes", {}).get(c, "")}
                     for c, t, p in d.CONCEPTS]
    errors.extend(question_errors(d, fact_by_id))

    # ── HTML ──
    inc = [q["id"] for q in d.QUESTIONS if q["status"] == "included"]
    rev = [q["id"] for q in d.QUESTIONS if q["status"] == "review"]
    deferred_ids = list(d.DEFERRED)
    counts = dict(inc=len(inc), rev=len(rev), deferred=len(deferred_ids), total=len(inc) + len(rev) + len(deferred_ids))
    qparts = []
    for g, title in meta["groups"]:
        cards = "".join(active_card(q, meta, fact_by_id, titles) for q in d.QUESTIONS if q["group"] == g)
        qparts.append(f'<h3 class="group">{title}</h3>{cards}')
    qparts.append(f'<h3 class="group" id="deferred-questions">보류 문항 {counts["deferred"]}개 — 답 없이 사유만</h3>' +
                  "".join(deferred_card(i, r, later) for i, (r, later, _) in d.DEFERRED.items()))
    fmt_ids = lambda ids: ", ".join(i.replace(":", " ") for i in ids)
    scope = (f'<section class="card" id="question-scope"><p class="kicker">문항 범위</p><h2>원본 문항 {counts["total"]}개를 모두 셉니다</h2>\n'
             f'<div class="tablewrap"><table><tr><th>상태</th><th>개수</th><th>문항</th></tr>\n'
             f'<tr><td>이번 회차 포함</td><td>{counts["inc"]}</td><td>{fmt_ids(inc)}</td></tr>\n'
             f'<tr><td>지난 회차 복습</td><td>{counts["rev"]}</td><td>{fmt_ids(rev)}</td></tr>\n'
             f'<tr><td>보류</td><td>{counts["deferred"]}</td><td>{fmt_ids(deferred_ids)}</td></tr>\n'
             f'<tr><td><b>합계</b></td><td><b>{counts["total"]}</b></td><td>{note_path.name}의 매핑표·복습 줄·보류 줄에서 뽑아 고정한 범위</td></tr></table></div>\n'
             f'{meta["scope_notes_html"]}\n{legend(note_path.name)}</section>')
    header = meta["header_html"].format(**counts)
    body = "".join([header, d.SECTIONS[0], scope] + list(d.SECTIONS[1:]) + [
        d.BOUNDARY, QUESTIONS_INTRO, "".join(qparts), meta.get("routine_html", DEFAULT_ROUTINE),
        f"<footer>{meta['footer']}</footer>"])
    html = (f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{meta["title"]}</title>\n<style>\n{CSS}\n</style>\n</head>\n<body>\n<main class="wrap">\n{body}\n</main>\n{SCRIPT}\n</body></html>\n')

    mapping: dict[str, list[str]] = {}
    for ident, facts in re.findall(r'id="([^"]+)" data-facts="([^"]+)"', html):
        for fid in facts.split():
            if fid not in fact_by_id:
                errors.append(f"unknown fact in html: {fid}@{ident}")
            mapping.setdefault(fid, []).append(ident)
    errors.extend(f"fact not taught in html: {fid}" for fid in fact_by_id if fid not in mapping)
    html_ids = set(re.findall(r'\bid="([^"]+)"', html))

    # ── coverage questions + scope audits ──
    questions_json, audits = [], {}
    for q in d.QUESTIONS:
        fmt = "multiple_choice" if q["opts"] else "short_answer"
        src = q["id"].split(":")[0]
        qsrc = meta["quiz_sources"].get(src, {})
        targets = sorted({t for r in q["reqs"] for t in mapping.get(r, [])})
        ans = {"teaching_target_ids": targets}
        if fmt == "multiple_choice":
            ans["option_diagnostics"] = {str(i): t for i, t in sorted(q["diag"].items())}
        else:
            ans["rubric"] = q["rubric"]
        if q["fig"]:
            ans["figure_target_ids"] = q["fig"]
            errors.extend(f"figure id not in html: {q['id']}/{f}" for f in q["fig"] if f not in html_ids)
        item = {"id": q["id"], "source_id": qsrc.get("source_id"), "locator": f"{qsrc.get('label')} p{q['page']}",
                "status": q["status"], "fact_ids": q["reqs"], "reason": "", "format": fmt, "grading": q["grading"],
                "requirements": q["reqs"], "answerability": ans, "printed_key": q["key"], "answer": q["ans"]}
        if fmt == "multiple_choice":
            item["option_count"] = len(q["opts"])
        if q["fig"]:
            item["diagram_required"] = True
        questions_json.append(item)
        audit = {"format": fmt, "grading": q["grading"], "requirements": q["reqs"],
                 "source_evidence": {"source_path": qsrc.get("path"), "page": q["page"], "quote": q["stem"][:40]},
                 "audit_status": "confirmed"}
        if fmt == "multiple_choice":
            audit["option_count"] = len(q["opts"])
        audits[q["id"]] = audit
    for ident, (reason, later, fids) in d.DEFERRED.items():
        qsrc = meta["quiz_sources"].get(ident.split(":")[0], {})
        questions_json.append({"id": ident, "source_id": qsrc.get("source_id"), "locator": qsrc.get("label"),
                               "status": "deferred", "fact_ids": fids, "reason": reason, "later_prerequisite": later})

    inventory = {"main_source": "note", "sources": sources_json, "blocks": blocks_json, "facts": facts_json,
                 "concepts": concepts_json, "questions": questions_json}
    inv_hash = hashlib.sha256(json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    review = {"status": "pending", "inventory_change_reason": ""}
    if out_cov.exists():
        review = json.loads(out_cov.read_text(encoding="utf-8")).get("review", review)
    coverage = {"schema_version": 2, "delivery_mode": meta.get("delivery_mode", "complete"), "inventory": inventory,
                "inventory_sha256": inv_hash,
                "mappings": [{"fact_id": fid, "target_ids": ids} for fid, ids in mapping.items()], "review": review}
    if errors:
        return {}, errors

    overrides = []
    if meta.get("overrides"):
        overrides = json.loads((data_dir / meta["overrides"]).read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    lock, lock_errors = build_lock(note_path, out_lock, overrides, audits)
    if lock_errors:
        return {}, lock_errors
    out_html.write_text(html, encoding="utf-8")
    out_cov.write_text(json.dumps(coverage, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"html": out_html, "coverage": out_cov, "scope": out_lock, "counts": counts, "facts": len(d.FACTS),
            "html_sha256": hashlib.sha256(html.encode()).hexdigest(), "review_kept": review.get("status") == "complete"}, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, help="guide data module (e.g. 정리노트/eli5-src/0910/guide.py)")
    parser.add_argument("--out-dir", type=Path, help="default: the note's directory")
    parser.add_argument("--force", action="store_true", help="overwrite an HTML that has no matching coverage JSON")
    args = parser.parse_args(argv)
    result, errors = build(args.data.resolve(), args.out_dir, args.force)
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    c = result["counts"]
    print(f"WROTE {result['html']} ({result['facts']} facts; {c['total']} questions = {c['inc']} included, "
          f"{c['rev']} review, {c['deferred']} deferred; html sha256 {result['html_sha256'][:12]})")
    print(f"WROTE {result['coverage']}\nWROTE {result['scope']}")
    if result["review_kept"]:
        print("NOTE: kept the previous review record — complete validation fails if the artifact changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
