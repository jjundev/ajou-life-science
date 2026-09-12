"""Authoring helpers for Study Note ELI5 guide data modules (used with build_guide.py).

A data module builds its concept sections with these helpers. Every teaching
element that states a fact is written with T(id, "fact ids", html); the
builder derives the fact → HTML mapping from those data-facts attributes.
Fill TITLES from the data module's CONCEPTS before building sections.
"""
from __future__ import annotations
import math

TITLES: dict[str, str] = {}


def F(id, block, kind, concept, statement, quote, src="note", loc=None, qual=(), dims=None):
    """One atomic fact. src='note' facts get their locator from the note block."""
    return dict(id=id, block=block, kind=kind, concept=concept, statement=statement,
                quote=quote, src=src, loc=loc, qual=list(qual), dims=dims)


def Q(id, status, group, page, stem, opts, key, ans, grading, reqs, diag, trap, reason,
      remedy="confusion", conflict=None, fig=None, fig_note=None, printed=None, rubric=None,
      also_accept=None):
    """One active original question in its original wording and option order.

    opts=[] means an original short-answer question (give printed + rubric).
    key is the printed key (None if none is printed); ans is the guide's answer.
    grading='ambiguous' requires also_accept (other defensible option numbers).
    fig lists the SVG ids a diagram-dependent question needs; fig_note names them.
    """
    return dict(id=id, status=status, group=group, page=page, stem=stem, opts=opts, key=key,
                ans=ans, grading=grading, reqs=reqs, diag=diag, trap=trap, reason=reason,
                remedy=remedy, conflict=conflict, fig=list(fig or []), fig_note=fig_note,
                printed=printed, rubric=rubric, also_accept=list(also_accept or []))


def T(id, facts, html, tag="p", cls=None):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag} id="{id}" data-facts="{facts}"{c}>{html}</{tag}>'


def R(q, a):
    return ('<div class="recall" data-role="recall" data-generated="true"><b>생성 회상 질문</b>'
            f'<p>{q}</p><details><summary>모범 답 보기</summary><p data-part="model-answer">{a}</p></details></div>')


DEFAULT_BADGES = {"sup": "강의노트·자료 보충", "fix": "정확성 보충", "prof": "교수님 비유",
                  "rev": "직전 회차 복습", "gen": "생성 비유"}
BADGES: dict[str, str] = dict(DEFAULT_BADGES)  # a data module may rename, e.g. BADGES["rev"] = "0908 복습"


def B(kind):
    return f'<span class="b {kind}">{BADGES[kind]}</span>'


def box(cls, title, html):
    return f'<div class="{cls}"><b>{title}</b>{html}</div>'


def section(cid, num, title, body, prereqs=()):
    pre = ""
    if prereqs:
        links = " · ".join(f'<a href="#concept-{p}">{TITLES.get(p, p)}</a>' for p in prereqs)
        pre = f'<p class="pre">먼저 떠올릴 개념: {links}</p>'
    return (f'<section class="card concept" id="concept-{cid}" data-concept="{cid}" data-role="teaching">'
            f'<p class="kicker">{num}</p><h2>{title}</h2>{pre}{body}</section>')


def arrow(x1, y1, x2, y2, color="#172033", w=3, head=11):
    """Line with a polygon head (SVG markers need url(), which the validator rejects)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = head * 0.55 * math.sin(ang), -head * 0.55 * math.cos(ang)
    pts = f"{x2:.0f},{y2:.0f} {bx + px:.0f},{by + py:.0f} {bx - px:.0f},{by - py:.0f}"
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx:.0f}" y2="{by:.0f}" stroke="{color}" stroke-width="{w}"/>'
            f'<polygon points="{pts}" fill="{color}"/>')


def svg(id, w, h, label, inner):
    return (f'<figure class="fig"><svg id="{id}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}" '
            f'font-size="14" font-family="system-ui, sans-serif">{inner}</svg><figcaption>{label}</figcaption></figure>')


def txt(x, y, s, size=14, color="#172033", anchor="middle", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'
