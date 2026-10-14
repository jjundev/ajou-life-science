#!/usr/bin/env python3
"""웹과제 예상 세트 검사기. CLI: check.py <웹과제예상/<N>장/복습문제_…_v<K>.html>"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402  (bio-review-pack 경로도 여기서 추가된다)
import cards  # noqa: E402
import check_html  # noqa: E402
import exam_pool  # noqa: E402

DEFAULT_EXAM_COUNTS = {"기출그대로": 2, "기출쌍둥이": 2, "기출숫자": 1}
TITLE_KIND = {"기출그대로": "기출 예상", "기출쌍둥이": "기출 변형", "기출숫자": "기출 변형"}
FIG_CLASSES = {"fig-ink", "fig-accent", "fig-dot", "fig-text", "fig-muted"}
HELP_PHRASES = ("답을 선택하면", "여기를 눌러", "다른 보기도 눌러")
NOTE_LINK_RE = re.compile(r'href="\.\./\.\./복습노트/\d{4}/정리노트_[^"#]+\.html#s\d+-[a-z0-9-]+"')


def _webquiz_stems(repo: Path, chapter: int) -> set[str]:
    f = repo / "웹과제" / f"{chapter}장" / "questions.json"
    if not f.is_file():
        return set()
    data = json.loads(f.read_text(encoding="utf-8"))
    qs = data["questions"] if isinstance(data, dict) else data
    out = set()
    for q in qs:
        texts = [c["text"] for c in q.get("original", {}).get("content", []) if c.get("type") == "text"]
        if texts:
            out.add(cards.norm(texts[0]))
    return out


def _question(c: dict) -> tuple[str, tuple[str, ...]]:
    """번호가 달라도 같은 기출 문제인지 가리는 키(발문 + 보기 집합)."""
    return cards.norm(c["stem"]), tuple(sorted(map(cards.norm, c["options"])))


def _earlier(src: Path, version: int) -> tuple[set[str], set[str]]:
    """이전 버전들의 (발문 정규화 집합, 사용한 기출 번호 집합)."""
    stems, sources = set(), set()
    for d in src.parent.iterdir():
        m = re.fullmatch(r"v(\d+)", d.name)
        if not m or int(m.group(1)) >= version or not (d / "pack.json").is_file():
            continue
        pack = json.loads((d / "pack.json").read_text(encoding="utf-8"))
        sources |= {e["source"] for e in pack.get("exam_sources", {}).values()}
        sources |= set(pack.get("used_exam_sources", []))
        for f in (d / "cards").glob("p*.html"):
            for c in cards.parse_cards(f.read_text(encoding="utf-8")).values():
                if c["stem"]:
                    stems.add(cards.norm(c["stem"]))
    return stems, sources


def check(html_path: Path | str) -> list[str]:
    html_path = Path(html_path).resolve()
    m = re.search(r"_v(\d+)\.html$", html_path.name)
    if not m:
        return [f"[checker] {html_path.name}: 파일명에 _v<K>가 없음"]
    src = html_path.parent / build.PACK / f"v{m.group(1)}"
    repo = html_path.parents[2]
    pack = build.load_pack(src)
    source = html_path.read_text(encoding="utf-8")
    probs = [f"[checker] {p}" for p in check_html.check_file(html_path)]

    name, fresh = build.render(src)
    if name != html_path.name or fresh != source:
        probs.append(f"[stale] {html_path.name}: .pack/v{pack['version']}로 다시 빌드한 결과와 다름")

    parsed = cards.parse_cards(source)
    graded = {cid: c for cid, c in parsed.items() if c["options"]}
    key = pack["answer_key"]
    for cid, c in graded.items():
        got = "ABCDE"[c["answer_index"]] if c["answer_index"] is not None else None
        if key.get(cid) != got:
            probs.append(f"[answer-key] {cid}: 카드 {got}, answer_key {key.get(cid)}")
    if set(key) != set(graded):
        probs.append(f"[answer-key] 세트: answer_key 카드 {sorted(key)} ≠ 채점 카드 {sorted(graded)}")
    if graded and len(graded) % 5 == 0:
        spread = Counter(key.get(cid) for cid in graded)
        if any(spread[l] != len(graded) // 5 for l in "ABCDE"):
            probs.append(f"[answer-spread] 세트: {dict(spread)}")

    exams = pack.get("exam_sources", {})
    for cid, c in graded.items():
        kind = TITLE_KIND.get(exams.get(cid, {}).get("mode"), "예상")
        if not c["title"].startswith(f"{cid.upper()}. [{kind}]"):
            probs.append(f"[structure] {cid}: 제목은 '{cid.upper()}. [{kind}]'로 시작해야 함")
        order = re.findall(r'<h3>|<div class="problem">|<details class="(?:original|hint|solution)">', c["body"])
        if order != ["<h3>", '<div class="problem">', '<details class="original">',
                     '<details class="hint">', '<details class="solution">']:
            probs.append(f"[structure] {cid}: 순서 {order}")
        if "수업과의 연결" not in c["body"] or not NOTE_LINK_RE.search(c["body"]):
            probs.append(f"[structure] {cid}: 수업과의 연결 줄 또는 정리노트 앵커 링크 없음")
        labels = [l for l, _ in c["diagnoses"]]
        if labels != list("ABCDE"[:len(c["options"])]):
            probs.append(f"[diagnosis] {cid}: 보기 진단 {labels}")
        verdict = "틀려요" if "부정형" in c["types"] else "맞아요"
        hits = [l for l, v in c["diagnoses"] if v == verdict]
        if hits != [key.get(cid)]:
            probs.append(f"[diagnosis] {cid}: '{verdict}'인 보기 {hits} (정답 {key.get(cid)} 하나여야 함)")

    counts = Counter(t for c in graded.values() for t in c["types"])
    for t, n in pack.get("types_required", {}).items():
        if counts[t] < n:
            probs.append(f"[types] 세트: {t} {counts[t]}개 < {n}")

    for svg in re.findall(r"<svg\b(?![^>]*aria-hidden).*?</svg>", "".join(c["body"] for c in parsed.values()), re.S):
        bad = []
        if 'role="img"' not in svg:
            bad.append("role=img 없음")
        if re.search(r"#[0-9a-fA-F]{3,6}\b|\s(?:fill|stroke)=\"", svg):
            bad.append("직접 색 지정")
        vb = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) ', svg)
        if not vb or float(vb.group(1)) > 360:
            bad.append("viewBox 너비 > 360")
        if set(re.findall(r'class="([^"]+)"', svg)) - FIG_CLASSES:
            bad.append("fig-* 밖 클래스")
        if bad:
            probs.append(f"[figure] svg: {', '.join(bad)}")

    all_text = " ".join(cards.text(c["body"]) for c in parsed.values())
    for w in list(pack.get("forbidden", [])) + list(HELP_PHRASES):
        if w in all_text:
            probs.append(f"[wording] 세트: '{w}'")
    if re.search(r"[①-⑳]", all_text):
        probs.append("[wording] 세트: 원문자 ①~⑳")
    if re.search(r"<details[^>]*\sopen[\s>=]", source):
        probs.append("[open-details] 세트: 펼친 details 있음")

    earlier_stems, earlier_sources = _earlier(src, pack["version"])
    if not pack.get("legacy"):
        want = pack.get("exam_counts", DEFAULT_EXAM_COUNTS)
        got = Counter(e["mode"] for e in exams.values())
        if dict(got) != want:
            probs.append(f"[exam-count] 세트: {dict(got)} ≠ {want}")
        pool = exam_pool.load_pool(repo, pack["chapter"])
        earlier_qs = {_question(pool[s]) for s in earlier_sources if s in pool}
        seen_sources, seen_qs = set(), set()
        for cid, e in exams.items():
            c, orig = graded.get(cid), pool.get(e["source"])
            if c is None or orig is None:
                probs.append(f"[exam-missing] {cid}: 카드 또는 원문 {e['source']} 없음")
                continue
            if e["source"] in earlier_sources:
                probs.append(f"[exam-reuse] {cid}: {e['source']}는 이전 버전에서 썼음")
            elif _question(orig) in earlier_qs:
                probs.append(f"[exam-reuse] {cid}: {e['source']}는 이전 버전에서 쓴 기출과 같은 문제(번호만 다름)")
            if e["source"] in seen_sources or _question(orig) in seen_qs:
                probs.append(f"[exam-reuse] {cid}: {e['source']}와 같은 기출 문제를 이 세트에서 이미 썼음")
            seen_sources.add(e["source"])
            seen_qs.add(_question(orig))
            same_stem = cards.norm(c["stem"]) == cards.norm(orig["stem"])
            keyed = cards.norm(c["options"][c["answer_index"]])
            orig_answer = cards.norm(orig["options"][orig["answer_index"]])
            if e["mode"] == "기출그대로":
                if not same_stem or sorted(map(cards.norm, c["options"])) != sorted(map(cards.norm, orig["options"])) \
                        or keyed != orig_answer:
                    probs.append(f"[exam-verbatim] {cid}: 발문·보기·정답이 {e['source']} 원문과 다름")
            elif e["mode"] == "기출쌍둥이":
                if not same_stem or keyed == orig_answer:
                    probs.append(f"[exam-twin] {cid}: 발문이 원문과 같고 정답 문장은 원문 정답과 달라야 함")
            elif e["mode"] == "기출숫자":
                if same_stem and sorted(map(cards.norm, c["options"])) == sorted(map(cards.norm, orig["options"])):
                    probs.append(f"[exam-number] {cid}: 숫자·조건이 {e['source']} 원문과 같음")
    exam_ids = set(exams)
    quiz = _webquiz_stems(repo, pack["chapter"])
    for cid, c in graded.items():
        if cid in exam_ids:
            continue
        s = cards.norm(c["stem"])
        if s in earlier_stems:
            probs.append(f"[stem-dup] {cid}: 이전 버전과 같은 발문")
        if s in quiz:
            probs.append(f"[webquiz-copy] {cid}: 실제 웹과제 발문과 같음")
    return probs


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    sys.stdout.reconfigure(encoding="utf-8")
    if len(args) != 1:
        print("사용법: check.py <html>", file=sys.stderr)
        return 2
    try:
        probs = check(args[0])
    except (build.BuildError, KeyError, FileNotFoundError) as e:
        print(f"[checker] 검사 실패: {e}")
        return 1
    print("\n".join(probs) if probs else "OK")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
