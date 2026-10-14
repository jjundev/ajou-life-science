"""스킬 테스트 공통 도구. 임시 저장소에 작은 세트를 만든다."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

NOTE_REL = "복습노트/0000/정리노트_0000_T.html"
LINK = f"../../{NOTE_REL}#s1-t"


def card_html(i: int, answer: str, *, types: str = "계산", kind: str = "예상",
              stem: str | None = None, options: list[str] | None = None) -> str:
    options = options or [f"보기 {i}{c}" for c in "ABCDE"]
    stem = stem or f"문제 {i}번 발문이다?"
    neg = "부정형" in types.split()
    diag = "".join(
        f"<li>{c}. {'맞아요' if ((c != answer) if neg else (c == answer)) else '틀려요'}. 이유 {c}예요.</li>"
        for c in "ABCDE")
    choices = "".join(f"<li>{c}. {t}</li>" for c, t in zip("ABCDE", options))
    return (f'<article class="card" id="p{i}" data-source="예상 9장 {i}" data-types="{types}">\n'
            f'  <h3>P{i}. [{kind}] 제목 {i}</h3>\n'
            f'  <div class="problem"><p>{stem}</p>\n    <ul class="choices">{choices}</ul></div>\n'
            f'  <details class="original"><summary>원문 정보 보기</summary>예상 문제예요.</details>\n'
            f'  <details class="hint"><summary>힌트 보기</summary>힌트예요.</details>\n'
            f'  <details class="solution"><summary>풀이 보기</summary>\n'
            f'    <ol class="steps">{diag}<li>수업과의 연결: 노트와 이어져요(<a href="{LINK}">정리노트</a>).</li></ol>\n'
            f'    <p class="answer">정답: {answer}</p>\n  </details>\n</article>\n')


def overview_html(cid: str = "o1") -> str:
    return (f'<article class="card" id="{cid}" data-source="예상 9장 개요">\n  <h3>개요</h3>\n'
            f'  <div class="problem"><p>개요 내용이에요.</p></div>\n</article>\n')


def make_repo(tmp: Path) -> Path:
    note = tmp / NOTE_REL
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text('<!DOCTYPE html><html lang="ko"><body><a id="s1-t"></a></body></html>', encoding="utf-8")
    return tmp


def make_set(repo: Path, chapter: int, version: int, cards: dict[str, str],
             pack_extra: dict | None = None) -> Path:
    src = repo / "웹과제예상" / f"{chapter}장" / ".pack" / f"v{version}"
    (src / "cards").mkdir(parents=True, exist_ok=True)
    for cid, html in cards.items():
        (src / "cards" / f"{cid}.html").write_text(html, encoding="utf-8")
    graded = [c for c in cards if c.startswith("p")]
    pack = {
        "course": "생명과학", "chapter": chapter, "version": version,
        "note_href": f"../../{NOTE_REL}",
        "review_title": f"{chapter}장 웹과제 예상 v{version}", "review_intro": "소개예요.",
        "footer_review": "근거예요.",
        "parts": [{"id": "partA", "title": "A. 개요", "short": "개요"},
                  {"id": "partC", "title": "C. 새 문제", "short": "새 문제"}],
        "problems": [{"id": c, "part": "partA" if c.startswith("o") else "partC"} for c in cards],
        "answer_key": {c: "" for c in graded},
        "forbidden": ["금지어"], "types_required": {}, "exam_sources": {}, "legacy": True,
        "used_exam_sources": [],
    }
    for c in graded:
        pack["answer_key"][c] = re.search(r"정답: ([A-E])", cards[c]).group(1)
    pack.update(pack_extra or {})
    (src / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return src


def exam_card_html(source: str, stem: str, options: list[str], answer_no: int, cid: str = "p1") -> str:
    lis = "".join(f"<li>({n}) {t}</li>" for n, t in enumerate(options, 1))
    return (f'<article class="card" id="{cid}" data-source="{source}">\n<h3>P1. 기출</h3>\n'
            f'<div class="problem"><p>{stem}</p><ul class="choices">{lis}</ul></div>\n'
            f'<details class="solution"><summary>풀이 보기</summary><ol class="steps"></ol>'
            f'<p class="answer">정답: ({answer_no})</p></details></article>\n')


def write_pool(repo: Path, cards_html: list[str]) -> Path:
    f = repo / "복습노트" / "0000" / "복습문제_0000_T.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("<html><body>" + "".join(cards_html) + "</body></html>", encoding="utf-8")
    return f
