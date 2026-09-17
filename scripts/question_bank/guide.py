"""Adapt a complete, validated bank to the ELI5 authoring dictionary interface.

The scope loader owns source/hash validation. This adapter owns exact scope and
binding coverage; the guide builder additionally checks that every mapped fact
exists and is visibly taught. Inputs are never modified.
"""
from __future__ import annotations

from copy import deepcopy
from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .note import export_note_items
from .render import figure_templates
from .scope import assert_same_ids
from .svg import inline_svg


def bank_to_guide(bank: dict, bindings: dict, base: Path, entries: list[dict]) -> tuple[list, dict, str]:
    """Return active Q dictionaries, deferred entries and validated SVG templates.

    bindings is keyed by active qid, with group/status/requirement_facts. entries
    must classify the full bank after evidence-backed status overrides. Returned
    content is the original content; figure targets/markup are derivative fields.
    The returned templates are render material, never appended to student HTML.
    """
    assert_same_ids({q['id'] for q in bank['questions']}, [e['id'] for e in entries])
    active = {e['id'] for e in entries if e['status'] != 'deferred'}
    assert_same_ids(active, list(bindings))
    # Shared eligibility, option-order and analysis checks. No observations leak.
    items = {i['qid']: i for i in export_note_items(bank, entries)}
    by_id = {q['id']: q for q in bank['questions']}
    sources = {s['id']: s for s in bank['sources']}
    templates = figure_templates(bank, base)
    questions, deferred = [], {}
    for entry in entries:
        ident = entry['id']
        if entry['status'] == 'deferred':
            reason = entry.get('override_reason') or entry.get('reason')
            if not reason or not entry.get('prerequisite'):
                raise ValueError('deferred requires reason and prerequisite: ' + ident)
            deferred[ident] = (reason, entry['prerequisite'], [])
            continue
        binding = bindings[ident]
        if binding.get('status') != entry['status']:
            raise ValueError('binding must match final scope status: ' + ident)
        if not isinstance(binding.get('group'), str) or not binding['group'].strip():
            raise ValueError('binding requires group: ' + ident)
        q, item = by_id[ident], items[ident]
        analysis = q['analysis']
        requirements = binding.get('requirement_facts')
        if not isinstance(requirements, dict):
            raise ValueError('binding requires requirement_facts: ' + ident)
        assert_same_ids({r['id'] for r in analysis['requirements']}, list(requirements))
        facts = []
        for requirement in analysis['requirements']:
            ids = requirements[requirement['id']]
            if not isinstance(ids, list) or not ids or any(not isinstance(f, str) or not f.strip() for f in ids):
                raise ValueError('requirement needs nonempty fact IDs: ' + ident + '/' + requirement['id'])
            facts.extend(f for f in ids if f not in facts)
        labels = item['optionIds']
        official = q['observations']['official_answer']
        if official is not None and len(official['option_ids']) != 1:
            raise ValueError('ELI5 single-choice key requires one official option: ' + ident)
        locator = '스크린샷 ' + ', '.join(sources[s]['path'] for s in q['source_ids']) + f' · 문항 {q["number"]}'
        bank_path = entry.get('bank_path', str(Path(base) / 'questions.json'))
        conflict = '\n'.join(issue['description'] for issue in analysis['issues']) or None
        questions.append(dict(
            id=ident, status=entry['status'], group=binding['group'], page=locator,
            stem=item['q'], opts=item['opts'], option_labels=labels,
            key=labels.index(official['option_ids'][0]) + 1 if official is not None else None,
            ans=item['answer'] + 1, grading=analysis['grading'], reqs=facts,
            diag={i + 1: d['explanation'] for i, d in enumerate(item['diagnostics'])},
            trap='각 보기의 조건을 원문과 대조하세요.', reason=analysis['reason'],
            remedy=binding.get('remedy', 'confusion'), conflict=conflict,
            fig=[], fig_note=None, printed=None, rubric=None, also_accept=[i + 1 for i in item['also_accept']],
            content=deepcopy(q['original']['content']), locator=locator,
            source_evidence=dict(source_path=bank_path, page=locator, quote=item['q']),
            bank_origin=True, explained_figures=[],
            requirement_facts=deepcopy(requirements),
        ))
    _attach_figures(questions, templates)
    return questions, deferred, templates


def _attach_figures(questions: list[dict], templates: str) -> None:
    """Populate derivative instance markup on new Q dictionaries only.

    Every mounted SVG is namespaced again, even when the same asset occurs twice.
    Template IDs come from the producer helper; no source data is altered.
    """
    from .render import figure_id
    by_id = dict(re.findall(r'<template id="([^"]+)">(.*?)</template>', templates, re.S))
    for q in questions:
        q['figure_markup'] = {}
        for index, block in enumerate(q['content']):
            if block['type'] != 'figure':
                continue
            for variant in ('exam', 'explained'):
                template_id = figure_id(q['id'].rsplit(':', 1)[0], block['asset_id'], variant)
                if template_id not in by_id:
                    raise ValueError('missing question figure: ' + template_id)
                target = template_id + '-q' + q['id'].encode('utf-8').hex() + f'-b{index}'
                alt = ET.fromstring(by_id[template_id]).get('aria-label', '')
                svg = inline_svg(by_id[template_id], target + '-svg', alt)
                markup = (f'<figure class="fig" id="{escape(target, quote=True)}" '
                          f'data-role="figure-evidence" data-figure-variant="{variant}">{svg}</figure>')
                if variant == 'exam':
                    q['fig'].append(target)
                    q['figure_markup'][index] = markup
                else:
                    q['explained_figures'].append(markup)
