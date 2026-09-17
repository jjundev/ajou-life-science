"""Student note adapter for complete, validated question banks.

Call load_bank(..., complete=True) before export; this adapter checks eligibility,
but file hashes remain the loader's responsibility. No observation is exported.
"""
from __future__ import annotations

from copy import deepcopy
import json

from .render import figure_id

START = '/* QUESTION-DATA-START */'
END = '/* QUESTION-DATA-END */'


def export_note_items(bank: dict, entries: list[dict]) -> list[dict]:
    """Export included/review items in scope order, with zero-based answers."""
    questions = {q['id']: q for q in bank['questions']}
    if any(q['review']['status'] != 'verified' for q in bank['questions']) or any(
            a['review']['status'] != 'verified' for a in bank['assets']):
        raise ValueError('note export requires a verified bank')
    if any(q['analysis']['answer_status'] != 'reasoned' or
           q['analysis'].get('grading') == 'unresolved' for q in bank['questions']):
        raise ValueError('cannot export unresolved answers')
    seen, result = set(), []
    source = bank['assessment']['id']
    for entry in entries:
        qid = entry['id']
        if qid in seen or qid not in questions:
            raise ValueError('duplicate or unknown scope question: ' + qid)
        seen.add(qid)
        if entry['status'] not in {'included', 'review', 'deferred'}:
            raise ValueError('unknown scope status: ' + entry['status'])
        if entry['status'] == 'deferred':
            continue
        q = questions[qid]
        original, analysis = q['original'], q['analysis']
        if original['format'] != 'single_choice':
            raise ValueError('unsupported question format: ' + original['format'])
        option_ids = [o['id'] for o in original['options']]
        answer = option_ids.index(analysis['answer_option_id'])
        accepted = [option_ids.index(o) for o in analysis['also_accept']]
        content = deepcopy(original['content'])
        exam, explained = [], []
        for block in content:
            if block['type'] == 'figure':
                block['figureId'] = figure_id(source, block['asset_id'], 'exam')
                exam.append(block['figureId'])
                explained.append(figure_id(source, block['asset_id'], 'explained'))
        diagnostics = [dict(optionId=o, **deepcopy(analysis['option_diagnostics'][o])) for o in option_ids]
        refs = deepcopy(entry['refs'])
        if not refs:
            raise ValueError('active note question requires refs: ' + qid)
        result.append({
            'n': q['number'], 'src': source, 'qid': qid,
            'q': next((b['text'] for b in content if b['type'] == 'text'), '문제 ' + str(q['number'])),
            'content': content, 'opts': [o['text'] for o in original['options']],
            'optionIds': option_ids, 'answer': answer, 'also_accept': accepted,
            'why': analysis['reason'], 'diagnostics': diagnostics,
            'trap': {i: d['explanation'] for i, d in enumerate(diagnostics)
                     if i != answer and i not in accepted},
            'keyNote': '분석 기준의 답과 해설이며 공식 채점 결과가 아닙니다.' +
                       ''.join('\n' + issue['description'] for issue in analysis['issues']),
            'answerLabel': '분석 기준', 'ref': refs[0]['section'], 'refs': refs,
            'examFigureIds': exam, 'explainedFigureIds': list(dict.fromkeys(explained)),
        })
    return result


def script_json(value: object) -> str:
    """Serialize JSON without an HTML script terminator or JS line separator."""
    text = json.dumps(value, ensure_ascii=False)
    for old, new in [('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                     ('\u2028', '\\u2028'), ('\u2029', '\\u2029')]:
        text = text.replace(old, new)
    # Literal delimiter text belongs to JSON strings, never parser markers.
    return text.replace('/* QUESTION-DATA-', r'\u002f* QUESTION-DATA-')


def render_note(template: str, meta: dict, items: list[dict], figures: str = '') -> str:
    """Replace exactly one data region; place validated inert SVGs before script.

    figures is produced by render.figure_templates. refs.href is already resolved
    by the caller; no filesystem assumptions or bank mutation occur here.
    """
    if template.count(START) != 1 or template.count(END) != 1:
        raise ValueError('template must contain exactly one question data marker pair')
    start, end = template.index(START), template.index(END)
    if start >= end:
        raise ValueError('question data markers are reversed')
    script = template.rfind('<script>', 0, start)
    if script < 0 or template.find('</script>', script, end) >= 0:
        raise ValueError('question data markers must be inside one inline script')
    data = START + '\nconst META = ' + script_json(meta) + ';\nconst QUIZ = ' + script_json(items) + ';\n'
    result = template[:start] + data + template[end:]
    return result[:script] + figures + '\n' + result[script:]
