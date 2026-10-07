"""예상 세트·복습팩 카드 HTML 파서 (표준 라이브러리만)."""
from __future__ import annotations

import re

CARD_RE = re.compile(r'<article class="card" id="([^"]+)"([^>]*)>(.*?)</article>', re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
LABEL_RE = re.compile(r"^\s*(?:\((\d+)\)|([A-E])\.)\s*")
ANSWER_RE = re.compile(r'<p class="answer">\s*정답:\s*(?:\((\d+)\)|([A-E]))\s*</p>')
DIAG_RE = re.compile(r"<li>([A-E])\. (맞아요|틀려요)")


def text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def norm(s: str) -> str:
    return re.sub(r"[\W_]+", "", s)


def _options(body: str) -> list[str]:
    m = re.search(r'<ul class="choices">(.*?)</ul>', body, re.S)
    if not m:
        return []
    return [LABEL_RE.sub("", text(li), count=1) for li in re.findall(r"<li>(.*?)</li>", m.group(1), re.S)]


def parse_cards(html: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for cid, raw_attrs, body in CARD_RE.findall(html):
        attrs = dict(ATTR_RE.findall(raw_attrs))
        stem = re.search(r'<div class="problem">\s*<p>(.*?)</p>', body, re.S)
        title = re.search(r"<h3>(.*?)</h3>", body, re.S)
        ans = ANSWER_RE.search(body)
        options = _options(body)
        index = label = None
        if ans:
            label = ans.group(1) or ans.group(2)
            index = int(ans.group(1)) - 1 if ans.group(1) else "ABCDE".index(ans.group(2))
        out[cid] = dict(id=cid, source=attrs.get("data-source", ""), types=attrs.get("data-types", "").split(),
                        title=text(title.group(1)) if title else "", stem=text(stem.group(1)) if stem else "",
                        options=options, answer_index=index, answer_label=label,
                        diagnoses=DIAG_RE.findall(body), body=body)
    return out
