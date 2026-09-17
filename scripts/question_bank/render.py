"""Offline QA preview and reusable SVG templates for validated question banks."""
from __future__ import annotations

from html import escape
import os
from pathlib import Path
from urllib.parse import quote

from .model import REPO_ROOT, resolve_local
from .svg import inline_svg


def _component(value: str, *, hyphens: bool = False) -> str:
    # Escape underscores too, so literal escape-looking IDs cannot collide.
    return ''.join(c if c.isascii() and (c.isalnum() or (hyphens and c == '-'))
                   else f'_{ord(c):x}_' for c in value)


def figure_id(assessment_id: str, asset_id: str, variant: str) -> str:
    """Stable template ID; the asset component cannot contain the '-' separator."""
    if variant not in {'exam', 'explained'}:
        raise ValueError('unknown figure variant: ' + variant)
    return f'figure-{_component(assessment_id, hyphens=True)}-{_component(asset_id)}-{variant}'


def _figure(asset: dict, base: Path, variant: str, prefix: str) -> str:
    entry = asset[variant]
    return inline_svg(resolve_local(base, entry['path']).read_text(encoding='utf-8'), prefix, entry['alt'])


def figure_templates(bank: dict, base: Path) -> str:
    """Return inert exam/explained templates, namespaced by bank, asset and variant.

    Consumers should clone a template once per document or re-namespace repeated
    instances. The static QA preview embeds separately namespaced SVGs directly.
    """
    parts = []
    for asset in bank['assets']:
        for variant in ('exam', 'explained'):
            identifier = figure_id(bank['assessment']['id'], asset['id'], variant)
            svg = _figure(asset, base, variant, identifier + '-svg')
            parts.append(f'<template id="{identifier}">{svg}</template>')
    return '\n'.join(parts)


def _link(path: Path, output_dir: Path, label: str) -> str:
    relative = os.path.relpath(path.resolve(), output_dir.resolve())
    return f'<a href="{escape(quote(Path(relative).as_posix(), safe="/"), quote=True)}">{escape(label)}</a>'


def render_options(options: list[dict]) -> str:
    return '<ol class="options">' + ''.join(
        f'<li data-option-id="{escape(o["id"], quote=True)}"><b>{escape(o["id"])}</b> '
        f'<span>{escape(o["text"])}</span></li>' for o in options) + '</ol>'


def render_preview(bank: dict, base: Path, *, output_dir: Path | None = None,
                   repo_root: Path | None = None) -> str:
    """Render a previously validated bank without scripts or external requests.

    base is the bank directory; links are relative to output_dir (default: base).
    The CLI validates before calling this pure renderer.
    """
    base = Path(base)
    output_dir = base if output_dir is None else Path(output_dir)
    repo_root = REPO_ROOT if repo_root is None else Path(repo_root)
    sources = {s['id']: s for s in bank['sources']}
    assets = {a['id']: a for a in bank['assets']}

    def source_links(ids: list[str]) -> str:
        return ' · '.join(_link(resolve_local(base, sources[s]['path']), output_dir,
                                Path(sources[s]['path']).name) for s in ids)

    assessment = bank['assessment']
    parts = ['<!doctype html><html lang="ko"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f'<title>{escape(assessment["title"])} · 원문 미리보기</title>',
             '<style>' + CSS + '</style></head><body><main>',
             f'<header><p class="eyebrow">웹과제 · {escape(assessment["date"])}</p>',
             f'<h1>{escape(assessment["title"])}</h1>',
             f'<p>{len(bank["questions"])}문항 · {sum(len(q["original"]["options"]) for q in bank["questions"])}보기</p>',
             '<p class="notice">스크린샷에서 문구와 그림을 복원한 검토용 미리보기입니다. '
             '원본 화면의 배치와 다를 수 있습니다. 원본 링크로 대조하세요. '
             '캡처 선택과 분석 해설은 각각 펼쳐 확인할 수 있습니다.</p>',
             '<p class="sources">평가 정보 출처: ' + source_links(assessment['evidence_source_ids']) + '</p></header>']
    review_labels = {'pending': '미검토', 'needs_review': '재검토 필요', 'verified': '원본 대조 검토 완료'}
    phases = {'pre_submission': '제출 전', 'post_submission': '제출 후', 'unknown': '시점 불명'}
    grading_labels = {'single': '단일 답', 'ambiguous': '표현 또는 채점 기준이 모호함', 'unresolved': '미확정'}
    for question in bank['questions']:
        qid = escape(question['id'], quote=True)
        parts.append(f'<article data-question-id="{qid}"><h2>문제 {question["number"]}</h2>')
        parts.append(f'<p class="meta">{question["points"]}점 · {review_labels[question["review"]["status"]]}</p>')
        figure_blocks = []
        for index, block in enumerate(question['original']['content']):
            if block['type'] == 'text':
                parts.append('<p class="prompt">' + escape(block['text']) + '</p>')
            elif block['type'] == 'statements':
                parts.append('<ol class="statements">' + ''.join(
                    f'<li><b>{escape(item["id"])}</b> {escape(item["text"])}</li>'
                    for item in block['items']) + '</ol>')
            elif block['type'] == 'figure':
                asset = assets[block['asset_id']]
                figure_blocks.append((index, asset))
                prefix = figure_id(assessment['id'], asset['id'], 'exam') + f'-q{question["number"]}-b{index}'
                parts.append('<figure>' + _figure(asset, base, 'exam', prefix) + '</figure>')
            else:
                raise ValueError('unsupported content block: ' + str(block['type']))
        parts.append(render_options(question['original']['options']))
        parts.append('<p class="sources">원본: ' + source_links(question['source_ids']) + '</p>')
        observations = question['observations']
        parts.append('<details data-role="observations"><summary>캡처 관찰 기록</summary>')
        parts.append('<p>캡처 시점: ' + phases[observations['phase']] + '</p>')
        parts.append('<p>캡처 선택: ' + escape(observations['selected_option_id'] or '확인되지 않음') + '</p>')
        if observations['selected_source_id'] is not None:
            parts.append('<p>선택 근거: ' + source_links([observations['selected_source_id']]) + '</p>')
        official = observations['official_answer']
        if official is None:
            parts.append('<p>공식 답: 확인되지 않음</p>')
        else:
            parts.append('<p>공식 답: ' + escape(', '.join(official['option_ids'])) + '</p><p>' + source_links(official['source_ids']) + '</p>')
        parts.append('</details><details data-role="solution"><summary>분석 기준 해설 · 보기별 진단</summary>')
        analysis = question['analysis']
        parts.append('<p><strong>분석 기준 답: ' + escape(analysis['answer_option_id'] or '미확정') + '</strong> · '
                     + grading_labels[analysis['grading']] + '</p>')
        parts.append('<p>이 해설은 분석 결과입니다. 공식 답의 확인 여부는 캡처 관찰 기록에 표시합니다.</p>')
        if analysis['also_accept']:
            parts.append('<p>추가 허용: ' + escape(', '.join(analysis['also_accept'])) + '</p>')
        parts.append('<p>' + escape(analysis['reason']) + '</p>')
        for index, asset in figure_blocks:
            prefix = figure_id(assessment['id'], asset['id'], 'explained') + f'-q{question["number"]}-b{index}'
            parts.append('<figure>' + _figure(asset, base, 'explained', prefix) + '</figure>')
            parts.append('<p class="meta">그림 검토: ' + review_labels[asset['review']['status']] + '</p>')
        parts.append('<h3>보기별 선택 적합성</h3><ol class="diagnostics">')
        for option in question['original']['options']:
            diagnostic = analysis['option_diagnostics'][option['id']]
            label = {True: '답으로 적합', False: '답으로 부적합', None: '미확정'}[diagnostic['is_answer']]
            parts.append(f'<li data-diagnostic-id="{escape(option["id"], quote=True)}"><b>{escape(option["id"])} · {label}</b>'
                         f'<p>{escape(diagnostic["explanation"])}</p></li>')
        parts.append('</ol>')
        if analysis['issues']:
            parts.append('<h3>원문 주의점</h3><ul>')
            for issue in analysis['issues']:
                parts.append('<li>' + escape(issue['description']) + '<p class="sources">'
                             + source_links(issue['source_ids']) + '</p></li>')
            parts.append('</ul>')
        parts.append('<h3>필요 지식과 근거</h3><ul>')
        for requirement in analysis['requirements']:
            parts.append('<li>' + escape(requirement['statement']) + '<ul>')
            for evidence in requirement['evidence']:
                label = evidence['path'] + ' · ' + evidence['locator']
                parts.append('<li>' + _link(resolve_local(repo_root, evidence['path']), output_dir, label)
                             + '<blockquote>' + escape(evidence['quote']) + '</blockquote></li>')
            parts.append('</ul></li>')
        parts.append('</ul>')
        if question['review']['notes']:
            parts.append('<p class="meta">검토 기록: ' + escape(question['review']['notes']) + '</p>')
        parts.append('</details></article>')
    parts.append('</main></body></html>\n')
    return '\n'.join(parts)


CSS = '''
:root { color-scheme: light; font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif; color: #202830; background: #f3f5f7; }
* { box-sizing: border-box; }
body { margin: 0; line-height: 1.65; }
main { max-width: 960px; margin: auto; padding: 32px 24px 64px; }
header { margin-bottom: 32px; }
h1 { font-size: 1.85rem; line-height: 1.3; }
h2 { font-size: 1.3rem; margin: 0; }
h3 { font-size: 1.05rem; margin: 24px 0 10px; }
p { white-space: pre-wrap; overflow-wrap: anywhere; }
a { color: #245895; overflow-wrap: anywhere; }
.eyebrow, .meta, .sources { color: #526272; font-size: .875rem; }
.notice { background: #e7eef5; border-left: 3px solid #708ba4; padding: 14px 18px; }
article { background: #fff; border: 1px solid #dce2e8; border-radius: 12px; padding: 28px; margin-bottom: 24px; }
.prompt { font-size: 1.1rem; }
.options, .statements, .diagnostics { padding: 0; list-style: none; }
.options li { display: flex; align-items: baseline; gap: 12px; padding: 10px 12px; margin: 8px 0; background: #f6f8fa; border: 1px solid #e2e6ea; border-radius: 6px; }
.options b { flex: 0 0 1.2em; }
.options span, .statements li, .diagnostics li { overflow-wrap: anywhere; white-space: pre-wrap; }
.statements li { margin: 8px 0; }
.diagnostics li { margin: 16px 0; }
figure { margin: 24px 0; }
svg { display: block; width: 100%; height: auto; }
details { border-top: 1px solid #dce2e8; margin-top: 14px; padding-top: 14px; }
summary { cursor: pointer; color: #304c65; padding: 4px 0; }
blockquote { margin: 8px 0 16px; padding-left: 12px; border-left: 2px solid #cdd8e3; }
li { overflow-wrap: anywhere; }
@media (max-width: 480px) {
  main { padding: 20px 10px 40px; }
  article { padding: 16px 12px; }
  h1 { font-size: 1.5rem; }
  .options li { padding: 9px 8px; gap: 6px; }
  ul { padding-left: 20px; }
}
'''
