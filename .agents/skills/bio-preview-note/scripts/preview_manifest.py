#!/usr/bin/env python3
"""
생명과학 예습노트 manifest.json 로더·검증기 (표준 라이브러리만 사용).

manifest는 한 번의 실행(수업일 하나)에 대한 계약이다. preview_assemble.py와 preview_check.py가 읽는다.
CLI: preview_manifest.py RUN/manifest.json   (검증만, 오류가 있으면 목록 출력 후 종료 코드 1)
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401  (bio-review-pack/scripts를 import 경로에 넣는다)
from manifest import ManifestError, _need, _objects, _strings  # noqa: E402  (복습 스킬 공용 도우미)

LAYER_NAMES = {"eli5", "formal", "listen"}
CONCEPT_LAYERS = {"eli5", "formal"}
TOP_LEVEL_TYPES = {
    "course": str, "range": str, "chapters": list, "slug": str, "pdfs": list,
    "note_title": str, "note_subtitle": str, "footer_note": str,
    "sections": list, "links": list,
}
RANGE_RE = re.compile(r"\d{4}")
CHAPTER_RE = re.compile(r"\d{1,2}")
SLUG_RE = re.compile(r"[A-Za-z0-9_]+")
ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
SLIDES_RE = re.compile(r"\d{1,2}장 p\d+(–p\d+)?")  # 범위는 en dash(–)
PDF_PREFIX = "강의노트/"


def _check_exam_terms(t: dict, tw: str, errors: list[str]) -> None:
    if "exam_terms" not in t:
        return
    exam = t["exam_terms"]
    if not isinstance(exam, list) or not all(isinstance(x, str) and x for x in exam):
        errors.append(f"{tw}.exam_terms: 빈 문자열이 아닌 문자열 목록이어야 함")
        return
    missing = [x for x in exam if x not in t["required_terms"]]
    if missing:
        errors.append(f"{tw}.exam_terms: required_terms에 없는 용어 {missing}")
    if exam and "listen" not in t["layers"]:
        errors.append(f"{tw}.exam_terms: listen 레이어가 있는 토픽에만 쓸 수 있음")


def _check_figure_ref(t: dict, tw: str, errors: list[str]) -> None:
    """figure_ref: 이 토픽이 따라 그릴 교과서·강의노트 그림(예: "그림 4.3"). 있으면 eli5에 SVG 1개가 필요하다."""
    if "figure_ref" not in t:
        return
    ref = t["figure_ref"]
    if not isinstance(ref, str) or not ref.strip():
        errors.append(f"{tw}.figure_ref: 빈 문자열이 아닌 문자열이어야 함(예: \"그림 4.3\")")
        return
    if "eli5" not in t["layers"]:
        errors.append(f"{tw}.figure_ref: eli5 레이어가 있는 토픽에만 쓸 수 있음")


def validate(m: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(m, dict):
        return ["manifest: JSON 객체 필요"]
    for key, typ in TOP_LEVEL_TYPES.items():
        _need(m, key, typ, "manifest", errors)
    if errors:
        return errors
    if not RANGE_RE.fullmatch(m["range"]):
        errors.append(f"manifest.range: 네 자리 수업 날짜(MMDD)여야 함: {m['range']}")
    if not SLUG_RE.fullmatch(m["slug"]):
        errors.append(f"manifest.slug: 영문·숫자·밑줄만: {m['slug']}")
    if not m["chapters"] or not all(isinstance(c, str) and CHAPTER_RE.fullmatch(c) for c in m["chapters"]):
        errors.append(f"manifest.chapters: 장 번호 문자열 목록이어야 함(예: [\"4\"]): {m['chapters']}")
    if not m["pdfs"] or not all(isinstance(p, str) and p.startswith(PDF_PREFIX) for p in m["pdfs"]):
        errors.append(f"manifest.pdfs: '{PDF_PREFIX}'로 시작하는 경로 목록이어야 함: {m['pdfs']}")
    if len(m["sections"]) < 2:
        errors.append("sections: '미리 알아둘 것'과 '한눈에 보기'를 포함해 2개 이상 필요")

    seen: set[str] = set()
    topic_ids: set[str] = set()

    def new_id(value: str, where: str) -> None:
        if not ID_RE.fullmatch(value):
            errors.append(f"{where}: id 형식 오류: {value}")
        if value in seen:
            errors.append(f"{where}: 중복 id: {value}")
        seen.add(value)

    for i, sec in _objects(m["sections"], "sections", errors):
        where = f"sections[{i}]"
        if not all([_need(sec, "id", str, where, errors), _need(sec, "title", str, where, errors),
                    _need(sec, "short", str, where, errors), _need(sec, "topics", list, where, errors)]):
            continue
        new_id(sec["id"], where)
        if sec["id"] != f"s{i}":
            errors.append(f"{where}.id: s{i}이어야 함: {sec['id']}")
        for j, t in _objects(sec["topics"], f"{where}.topics", errors):
            tw = f"{where}.topics[{j}]"
            ok = all([_need(t, "id", str, tw, errors), _need(t, "title", str, tw, errors),
                      _need(t, "slides", str, tw, errors), _need(t, "required_terms", list, tw, errors),
                      _need(t, "layers", list, tw, errors), _need(t, "supp", bool, tw, errors)])
            if not ok:
                continue
            new_id(t["id"], tw)
            topic_ids.add(t["id"])
            if not t["id"].startswith(f"{sec['id']}-"):
                errors.append(f"{tw}.id: {sec['id']}-로 시작해야 함: {t['id']}")
            _strings(t["required_terms"], f"{tw}.required_terms", errors)
            if not all(isinstance(x, str) for x in t["layers"]):
                errors.append(f"{tw}.layers: 문자열 목록이어야 함")
                continue
            unknown = set(t["layers"]) - LAYER_NAMES
            if unknown:
                errors.append(f"{tw}.layers: 알 수 없는 레이어 {sorted(unknown)}")
            if t["layers"]:
                if not CONCEPT_LAYERS <= set(t["layers"]):
                    errors.append(f"{tw}.layers: 개념 토픽은 eli5와 formal 필요")
                # s0(미리 알아둘 것)은 강의노트 쪽이 아니라 선수 개념이라 빈 문자열을 허용한다
                if not SLIDES_RE.fullmatch(t["slides"]) and not (sec["id"] == "s0" and t["slides"] == ""):
                    errors.append(f"{tw}.slides: '4장 p3' 또는 '4장 p3–p4'(en dash) 형식이어야 함(s0만 빈 문자열 허용): {t['slides']!r}")
            elif t["supp"]:
                errors.append(f"{tw}.supp: 레이어가 없는 토픽은 false여야 함")
            _check_exam_terms(t, tw, errors)
            _check_figure_ref(t, tw, errors)

    last = m["sections"][-1] if m["sections"] else None
    if isinstance(last, dict) and isinstance(last.get("id"), str) and isinstance(last.get("topics"), list):
        ids = {t.get("id") for t in last["topics"] if isinstance(t, dict)}
        for suffix in ("cheatsheet", "links"):
            if f"{last['id']}-{suffix}" not in ids:
                errors.append(f"sections[-1]: 토픽 {last['id']}-{suffix} 필요")

    for i, link in _objects(m["links"], "links", errors):
        where = f"links[{i}]"
        if _need(link, "topic", str, where, errors) and link["topic"] not in topic_ids:
            errors.append(f"{where}.topic: 없는 토픽: {link['topic']}")
        _need(link, "href", str, where, errors)
    return errors


def load(path: Path | str) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ManifestError(f"{path}: 파일을 읽을 수 없음: {e}") from e
    try:
        m = json.loads(text)
    except json.JSONDecodeError as e:
        raise ManifestError(f"{path}: JSON 형식 오류: {e}") from e
    errors = validate(m)
    if errors:
        raise ManifestError("\n".join(errors))
    return m


def note_name(m: dict) -> str:
    return f"예습노트_{m['range']}_{m['slug']}.html"


def fig_dir_name(range_: str) -> str:
    return f"figures_{range_}"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("사용법: preview_manifest.py RUN/manifest.json", file=sys.stderr)
        return 2
    try:
        load(argv[0])
    except ManifestError as e:
        print(e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
