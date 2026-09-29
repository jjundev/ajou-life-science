#!/usr/bin/env python3
"""
생명과학 예습노트 HTML 검사기 (표준 라이브러리만 사용).

- 공통·계약 검사는 bio-review-pack의 check_common/check_note를 그대로 쓴다
  (예고 금지어는 없고, 보충 배지는 이 파일에서 "교과서 보충"으로 따로 검사한다).
- 예습 전용: 쪽 태그, 교과서 보충 배지, STT 레이어 금지, 분량(600자·eli5 2문장·listen 2항목), 기출 배지.
- 분량은 레이어 안 글자만 센다. 공백, TeX($…$, $$…$$), 그림(svg·figure), 레이어 제목, 배지, 태그, 요약 패널은 뺀다.
- 문장은 블록(p, li, br …) 경계와 "." "?" "!" 뒤 공백에서 나눈다. 인라인 태그(b, a, span)는 문장을 나누지 않는다.
- 쪽 태그는 .tag.slide 글자가 manifest slides와 정확히 같아야 한다("4장 p3"이 "4장 p31"에 통과하지 않게).
- 들을 때 포인트는 교수님 발언을 예측하지 않는다("~하실 거예요" 같은 문장은 listen-predicts).
- 기출 배지(<span class="badge exam">기출</span>)는 exam_terms가 있는 토픽의 들을 때 포인트에만, 그 용어와 함께 쓴다.
- 그림: 쉽게 말하면 레이어의 SVG는 1개까지. figure_ref가 있는 토픽은 SVG 1개와, figcaption에 figure_ref·"다시 그렸어요"(출처)가 필요하다.
  교과서 그림을 잘라 넣은 <img>나 SVG 안 <image>는 src 종류(data: URI 포함)와 관계없이 쓰지 않는다(textbook-image).
- 그림 크기(높이 예산): 쉽게 말하면 SVG는 viewBox가 있어야 하고, 폭 600 이하(템플릿 max-width 560px에서 글자가
  줄지 않게), 세로/가로 0.25 이하(560×140, 가로:세로 4:1)여야 한다(figure-size). 토픽 전체 높이는 브라우저 검사가 본다.
CLI: preview_check.py --manifest RUN/manifest.json --note NOTE.html
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401
from check_html import VOID_TAGS, Problem, check_common, check_file, check_note, parse_html  # noqa: E402
import preview_manifest as pm  # noqa: E402

SUPP_LABEL = "교과서 보충"
EXAM_LABEL = "기출"
FIG_SOURCE = "다시 그렸어요"
MAX_FIGURES = 1
MAX_FIG_WIDTH = 600
MAX_FIG_RATIO = 0.25  # 세로/가로: 560×140
STT_LAYERS = {"prof", "warn"}
MAX_CHARS = 600
MAX_ELI5_SENTENCES = 2
MAX_LISTEN_ITEMS = 2
LAYER_KINDS = ("eli5", "formal", "listen", "supp")
SKIP_TAGS = {"svg", "figure", "script", "style"}
SKIP_CLASSES = {"layer-title", "badge", "sum", "tags"}
BLOCK_TAGS = {"p", "div", "li", "ul", "ol", "br", "dl", "dt", "dd", "table", "tr", "td", "th", "blockquote", "h3", "h4"}
MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$]*\$", re.S)
# 교수님 발언 예측: "강조하실 거예요", "짚으실 거예요", "나올 거예요", "물어보실 수 있어요"
PREDICT_RE = re.compile(r"(?:실|주실|으실)\s*(?:거예요|겁니다|수\s*있어요)|나올\s*거예요")


@dataclass
class TopicStats:
    text: str = ""
    eli5: str = ""
    listen_items: int = 0
    listen: str = ""
    exam_badges: int = 0
    eli5_svgs: int = 0
    captions: str = ""
    svg_boxes: list[str] = field(default_factory=list)
    slide_tags: list[str] = field(default_factory=list)


class _StatsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stats: dict[str, TopicStats] = {}
        # (tag, topic_id, layer_kind, skip, in_slide_tag)
        self.stack: list[tuple[str, str | None, str | None, bool, bool]] = []

    def _top(self) -> tuple[str | None, str | None, bool, bool]:
        return self.stack[-1][1:] if self.stack else (None, None, False, False)

    def _block_break(self, tag: str) -> None:
        topic, layer, skip, _ = self._top()
        if tag in BLOCK_TAGS and topic and layer == "eli5" and not skip:
            self.stats[topic].eli5 += "\n"  # 블록 경계 = 문장 경계(마침표가 없어도)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        cls = set(a.get("class", "").split())
        topic, layer, skip, in_slide = self._top()
        if tag == "article" and "topic" in cls and a.get("id"):
            topic, layer = a["id"], None
            self.stats[topic] = TopicStats()
        if topic and tag == "div" and "layer" in cls:
            layer = next((k for k in LAYER_KINDS if k in cls), "other")
        if topic and {"tag", "slide"} <= cls:
            in_slide = True
            self.stats[topic].slide_tags.append("")
        if topic and layer == "listen" and {"badge", "exam"} <= cls:
            self.stats[topic].exam_badges += 1
        if topic and layer == "eli5" and tag == "svg":
            self.stats[topic].eli5_svgs += 1
            self.stats[topic].svg_boxes.append(a.get("viewbox", ""))  # HTMLParser는 속성 이름을 소문자로 준다
        skip = skip or tag in SKIP_TAGS or bool(cls & SKIP_CLASSES)
        if topic and layer == "listen" and tag == "li" and not skip:
            self.stats[topic].listen_items += 1
        if tag not in VOID_TAGS:
            self.stack.append((tag, topic, layer, skip, in_slide))
        self._block_break(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        self._block_break(tag)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        topic, layer, skip, in_slide = self._top()
        if topic and in_slide:
            self.stats[topic].slide_tags[-1] += data
        if topic and layer == "eli5" and any(e[0] == "figcaption" for e in self.stack):
            self.stats[topic].captions += data  # figure 안이라 본문 글자 수에서는 빠진다
        if topic and layer and not skip:
            st = self.stats[topic]
            st.text += data
            if layer == "eli5":
                st.eli5 += data
            if layer == "listen":
                st.listen += data


class _ImageParser(HTMLParser):
    """<img>와 SVG 안 <image>를 src 종류(파일·data: URI)와 관계없이 모두 찾는다."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("img", "image"):
            a = {k: (v or "") for k, v in attrs}
            src = a.get("src") or a.get("href") or a.get("xlink:href") or ""
            self.found.append(f"<{tag}> {src[:40]}")


def embedded_images(source: str) -> list[str]:
    parser = _ImageParser()
    parser.feed(source)
    parser.close()
    return parser.found


def topic_stats(source: str) -> dict[str, TopicStats]:
    parser = _StatsParser()
    parser.feed(source)
    parser.close()
    return parser.stats


def _strip_math(text: str, repl: str = "") -> str:
    return MATH_RE.sub(repl, text.replace("\\$", ""))  # TeX 안의 \$는 구분자가 아니다


def visible_chars(text: str) -> int:
    return len(re.sub(r"\s", "", _strip_math(text)))


def sentences(text: str) -> int:
    """블록 경계(줄바꿈)와 "." "?" "!" 뒤 공백에서 나눈 문장 수."""
    t = _strip_math(text, "X")
    return sum(len([p for p in re.split(r"(?<=[.?!])\s+", line.strip()) if p.strip()]) for line in t.split("\n"))


def contract_view(m: dict) -> dict:
    """복습 check_note에 넘길 사본: 예고 금지어 없음, 보충 배지는 여기서 따로 검사."""
    v = copy.deepcopy(m)
    for sec in v["sections"]:
        for t in sec["topics"]:
            t["supp"] = False
    v["preview_topic"] = v["sections"][-1]["topics"][-1]["id"]
    v["forbidden_outside_preview"] = []
    return v


def _exam_problems(t: dict, st: TopicStats) -> list[Problem]:
    exam = t.get("exam_terms", [])
    out: list[Problem] = []
    if exam and not st.exam_badges:
        out.append(Problem("exam-mark", t["id"], f"들을 때 포인트에 '{EXAM_LABEL}' 배지(<span class=\"badge exam\">) 필요"))
    if not exam and st.exam_badges:
        out.append(Problem("exam-mark", t["id"], "manifest exam_terms가 없는데 기출 배지가 있음"))
    out += [Problem("exam-mark", t["id"], f"들을 때 포인트에 기출 용어 '{term}' 없음") for term in exam if term not in st.listen]
    return out


def _figure_size_problems(topic_id: str, box: str) -> list[Problem]:
    try:
        _, _, w, h = (float(x) for x in box.replace(",", " ").split())
    except ValueError:
        return [Problem("figure-size", topic_id, f"SVG viewBox 필요(예: \"0 0 560 140\"): {box!r}")]
    if w <= 0 or h <= 0:
        return [Problem("figure-size", topic_id, f"viewBox 폭·높이가 양수여야 함: {box!r}")]
    out: list[Problem] = []
    if w > MAX_FIG_WIDTH:
        out.append(Problem("figure-size", topic_id, f"viewBox 폭 {w:g} > {MAX_FIG_WIDTH}: 560 안팎으로(넓으면 글자가 줄어든다)"))
    if h / w > MAX_FIG_RATIO:
        out.append(Problem("figure-size", topic_id, f"viewBox {w:g}×{h:g}: 세로/가로 {h / w:.2f} > {MAX_FIG_RATIO} (560×140 이하로 낮춘다)"))
    return out


def _figure_problems(t: dict, st: TopicStats) -> list[Problem]:
    ref = t.get("figure_ref")
    out: list[Problem] = []
    for box in st.svg_boxes:
        out += _figure_size_problems(t["id"], box)
    if st.eli5_svgs > MAX_FIGURES:
        out.append(Problem("figure", t["id"], f"쉽게 말하면 그림 {st.eli5_svgs}개 > {MAX_FIGURES}개"))
    if ref and not st.eli5_svgs:
        out.append(Problem("figure", t["id"], f"figure_ref '{ref}'인데 쉽게 말하면 레이어에 SVG 그림이 없음"))
    if ref and st.eli5_svgs and (ref not in st.captions or FIG_SOURCE not in st.captions):
        out.append(Problem("figure-source", t["id"], f"figcaption에 '{ref}'와 '{FIG_SOURCE}' 필요(예: \"교과서 {ref}을 단순하게 다시 그렸어요\")"))
    return out


def check_preview(m: dict, note_path: Path | str) -> list[Problem]:
    path = Path(note_path)
    source = path.read_text(encoding="utf-8")
    doc = parse_html(source)
    out = check_common(doc, source, path) + check_note(doc, contract_view(m))
    out += [Problem("textbook-image", path.name, f"{img}: 교과서 그림은 잘라 넣지 말고 SVG로 다시 그린다")
            for img in embedded_images(source)]
    stats = topic_stats(source)
    for sec in m["sections"]:
        for t in sec["topics"]:
            con = doc.containers.get(t["id"])
            if con is None or not t["layers"]:
                continue
            st = stats.get(t["id"], TopicStats())
            if t["slides"] and t["slides"] not in (s.strip() for s in st.slide_tags):
                out.append(Problem("slide-tag", t["id"], f"'{t['slides']}' 태그 없음 (있는 태그: {st.slide_tags})"))
            if t["supp"] and ("supp" not in con.child_classes or SUPP_LABEL not in con.text):
                out.append(Problem("missing-supp", t["id"], f"layer supp + '{SUPP_LABEL}' 필요"))
            stt = STT_LAYERS & con.child_classes
            if stt:
                out.append(Problem("stt-layer", t["id"], ", ".join(sorted(stt))))
            n = visible_chars(st.text)
            if n > MAX_CHARS:
                out.append(Problem("topic-long", t["id"], f"본문 {n}자 > {MAX_CHARS}자"))
            k = sentences(st.eli5)
            if k > MAX_ELI5_SENTENCES:
                out.append(Problem("eli5-long", t["id"], f"쉽게 말하면 {k}문장 > {MAX_ELI5_SENTENCES}문장"))
            if PREDICT_RE.search(_strip_math(st.listen)):
                out.append(Problem("listen-predicts", t["id"], "교수님 발언을 예측하는 문장(\"~하실 거예요\") 대신 \"~가 나오면 ~해 보세요\"로"))
            if st.listen_items > MAX_LISTEN_ITEMS:
                out.append(Problem("listen-long", t["id"], f"들을 때 포인트 {st.listen_items}개 > {MAX_LISTEN_ITEMS}개"))
            out += _exam_problems(t, st)
            out += _figure_problems(t, st)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--manifest")
    ap.add_argument("--note")
    args = ap.parse_args(argv)
    problems: list[Problem] = []
    if args.manifest:
        if not args.note:
            ap.error("--manifest에는 --note가 필요")
        if not Path(args.note).is_file():
            print(f"노트 파일 없음: {args.note}")
            return 1
        try:
            problems += check_preview(pm.load(args.manifest), args.note)
        except pm.ManifestError as e:
            print(f"manifest 오류: {e}")
            return 1
    for name in args.files:
        problems += check_file(name)
    for p in problems:
        print(p)
    print("OK" if not problems else f"FAIL ({len(problems)})")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
