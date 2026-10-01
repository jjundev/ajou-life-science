#!/usr/bin/env python3
"""
이미 만든 복습팩에 문항을 덧붙인다(보강 모드). 기존 카드 번호를 그대로 두고 복습문제만 다시 쓴다.

  augment.py extract <팩 폴더> <RUN>   기존 카드 → RUN/cards/, manifest → RUN/manifest.json
  augment.py build   <팩 폴더> <RUN>   보호 검사 → 정렬·문구 갱신 → 복습문제 HTML만 쓰기 → .pack 기록

manifest는 <팩 폴더>/.pack/manifest.json을 쓰고, 없으면 정리노트·복습문제 HTML에서 복원한다
(금지어 [], anchor=예고 토픽, level 2, required_terms []).
"""

from __future__ import annotations

from collections import Counter
import html
import json
from pathlib import Path
import re
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_html  # noqa: E402
import manifest as manifest_mod  # noqa: E402

CARD_RE = re.compile(r'<article class="card" id="(p\d+)"[^>]*>.*?</article>', re.S)
PACK_NAME_RE = re.compile(r"^(정리노트|복습문제)_(\d{4}(?:-\d{4})?)_([A-Za-z0-9_]+)\.html$")
SECTION_RE = re.compile(r'<section id="(s\d+)"><h2>(.*?)</h2>(.*?)\n    </section>', re.S)
PART_RE = re.compile(r'<section id="(part[A-Z])"><h2>(.*?)</h2>(.*?)\n    </section>', re.S)
TOPIC_HEAD_RE = re.compile(r'<article class="topic" id="([\w-]+)"><h3>(.*?)</h3>', re.S)
DEFAULT_PARTS = {"partA": ("A. 웹과제", "A 웹과제"), "partB": ("B. 기출", "B 기출"), "partC": ("C. 변형 연습", "C 변형")}
RECONSTRUCTED_NOTE = "HTML에서 복원: 금지어 미복원, anchor·level·required_terms 임시값"


class AugmentError(RuntimeError):
    pass


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def find_pack_files(pack_dir: Path | str) -> tuple[Path, Path]:
    """(정리노트, 복습문제) HTML의 실제 경로. NFD 파일명도 NFC로 비교해 찾는다."""
    pack_dir = Path(pack_dir)
    found: dict[str, Path] = {}
    for p in pack_dir.iterdir() if pack_dir.is_dir() else []:
        m = PACK_NAME_RE.match(nfc(p.name))
        if m and p.is_file():
            found[m.group(1)] = p
    if "정리노트" not in found or "복습문제" not in found:
        raise AugmentError(f"{pack_dir}: 정리노트·복습문제 HTML이 둘 다 있어야 함")
    return found["정리노트"], found["복습문제"]


def _need(pattern: str | re.Pattern, text: str, what: str) -> re.Match:
    m = re.search(pattern, text, re.S)
    if not m:
        raise AugmentError(f"복원 실패: {what}")
    return m


def _toc(text: str) -> dict[str, str]:
    nav = _need(r'<nav class="toc" aria-label="목차">(.*?)</nav>', text, "목차").group(1)
    return {k: html.unescape(v) for k, v in re.findall(r'<a href="#([\w-]+)">(.*?)</a>', nav)}


def _answer(card: str) -> str:
    m = re.search(r'<p class="answer">정답:\s*(.*?)</p>', card, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def reconstruct(note_path: Path, review_path: Path) -> dict:
    """정리노트·복습문제 HTML에서 manifest를 복원한다. 복습문제 조립에 쓰는 값은 원문 그대로다."""
    note, review = note_path.read_text(encoding="utf-8"), review_path.read_text(encoding="utf-8")
    name = PACK_NAME_RE.match(nfc(review_path.name))
    range_, slug = name.group(2), name.group(3)
    hero_r = _need(r"<h1>(.*?)</h1>\s*<p>(.*?)</p>", review, "복습문제 제목·안내")
    hero_n = _need(r"<h1>(.*?)</h1>\s*<p>(.*?)</p>", note, "정리노트 제목·부제")
    toc_n, toc_r = _toc(note), _toc(review)
    sections, topic_ids, links = [], [], []
    for sm in SECTION_RE.finditer(note):
        topics = []
        for chunk in re.split(r'(?=<article class="topic" id=")', sm.group(3)):
            tm = TOPIC_HEAD_RE.match(chunk)
            if not tm:
                continue
            layers: list[str] = []
            for layer in re.findall(r'<div class="layer (\w+)', chunk):
                if layer in manifest_mod.LAYER_NAMES and layer not in layers:
                    layers.append(layer)
            tid = tm.group(1)
            topics.append({"id": tid, "title": html.unescape(tm.group(2)), "required_terms": [],
                           "layers": layers, "supp": check_html.SUPP_LABEL in chunk})
            topic_ids.append(tid)
            if tid.endswith("-links"):
                links += [{"topic": tid, "href": h} for h in re.findall(r'href="([^"#][^"]*)"', chunk)]
        sid = sm.group(1)
        sections.append({"id": sid, "title": html.unescape(sm.group(2)),
                         "short": toc_n.get(sid, html.unescape(sm.group(2))), "topics": topics})
    if not topic_ids:
        raise AugmentError("복원 실패: 정리노트 토픽 없음")
    preview = next((t for t in topic_ids if t.endswith("-next")), topic_ids[-1])
    parts, problems = [], []
    for pm in PART_RE.finditer(review):
        pid = pm.group(1)
        parts.append({"id": pid, "title": html.unescape(pm.group(2)),
                      "short": toc_r.get(pid, DEFAULT_PARTS.get(pid, (pid, pid))[1])})
        for c in CARD_RE.finditer(pm.group(3)):
            source = html.unescape(_need(r'data-source="([^"]*)"', c.group(0), f"{c.group(1)} data-source").group(1))
            answer = _answer(c.group(0))
            problems.append({"id": c.group(1), "part": pid, "source": source,
                             "variant": pid == "partC" or source.startswith("생성 변형"),
                             "anchor": preview, "level": 2, "date": range_[:4],
                             "terms": [f"정답: {answer}"] if answer else [], "answer": answer})
    return {
        "course": html.unescape(_need(r"<title>(.*?) 복습문제 ", review, "페이지 제목").group(1)),
        "range": range_, "slug": slug,
        "note_title": html.unescape(hero_n.group(1)), "note_subtitle": html.unescape(hero_n.group(2)),
        "review_title": html.unescape(hero_r.group(1)), "review_intro": hero_r.group(2),
        "footer_note": _need(r"<footer>(.*?)</footer>", note, "정리노트 꼬리말").group(1),
        "footer_review": _need(r"<footer>(.*?)</footer>", review, "복습문제 꼬리말").group(1),
        "sessions": [], "preview_topic": preview, "forbidden_outside_preview": [],
        "sections": sections, "parts": parts, "problems": problems, "links": links,
    }


def extract(pack_dir: Path | str, run_dir: Path | str) -> dict:
    pack_dir, run_dir = Path(pack_dir), Path(run_dir)
    note_path, review_path = find_pack_files(pack_dir)
    review = review_path.read_text(encoding="utf-8")
    cards = {m.group(1): m.group(0) for m in CARD_RE.finditer(review)}
    if not cards:
        raise AugmentError(f"{review_path.name}: 카드 없음")
    saved = pack_dir / ".pack" / "manifest.json"
    if saved.is_file():
        m = manifest_mod.load(saved)
        ids = {q["id"] for q in m["problems"]}
        if ids != set(cards):
            raise AugmentError(".pack manifest와 복습문제 HTML의 카드가 다름: "
                               f"manifest에만 {sorted(ids - set(cards))}, HTML에만 {sorted(set(cards) - ids)}")
        reconstructed = False
    else:
        m = reconstruct(note_path, review_path)
        errors = manifest_mod.validate(m)
        if errors:
            raise AugmentError("복원한 manifest 검증 실패:\n" + "\n".join(errors))
        reconstructed = True
    (run_dir / "cards").mkdir(parents=True, exist_ok=True)
    (run_dir / "work").mkdir(parents=True, exist_ok=True)
    for pid, text in cards.items():
        (run_dir / "cards" / f"{pid}.html").write_text(text, encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base = {q["id"]: {"part": q["part"], "source": q["source"], "answer": q["answer"]} for q in m["problems"]}
    (run_dir / "work" / "base-ids.json").write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note_file = run_dir / "work" / "reconstructed.txt"
    if reconstructed:
        note_file.write_text(RECONSTRUCTED_NOTE + "\n", encoding="utf-8")
    elif note_file.exists():
        note_file.unlink()
    return {"next_id": f"p{max(int(i[1:]) for i in base) + 1}",
            "parts": dict(Counter(q["part"] for q in m["problems"])), "reconstructed": reconstructed}
