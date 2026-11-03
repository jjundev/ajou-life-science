"""Render the mixed exam source with the existing review quiz presentation."""
import html
import json
import re
import sys
from pathlib import Path
from exam_contract import ExamError
from exam_dom import parse, inner, outer

ROOT = Path(__file__).resolve().parents[4]
REVIEW = ROOT / '.agents/skills/bio-review-pack'
sys.path.insert(0, str(REVIEW / 'scripts'))
import review_interaction


def render_practice(exam, pack):
    from exam_build import casefold_map
    from exam_presentations import names
    original = {n.attrs['id']: n for n in parse(exam).find_all(lambda n:n.tag == 'article')}
    cards = []
    for problem in pack['problems']:
        id_ = problem['id']
        node = original[id_]
        body = outer(next(node.find_all(lambda n:'problem' in n.classes)))
        title = outer(next(node.find_all(lambda n:n.tag == 'h3')))
        steps = ''.join('<li>' + step + '</li>' for step in problem['solution_steps'])
        answer = problem['answer']
        attrs = ''
        inputs = ''
        if problem['format'] == 'mcq':
            explanations = problem.get('option_explanations')
            ids = [option['id'] for option in problem['options']]
            if (not isinstance(explanations, dict) or set(explanations) != set(ids)
                or not all(isinstance(value, str) and value.strip() for value in explanations.values())):
                raise ExamError(f'{id_}: 보기별 설명 option_explanations가 필요합니다')
            steps = ''.join(f'<li data-explains="{html.escape(key, quote=True)}">{key}. {explanations[key]}</li>' for key in ids) + steps
            body_node = next(parse(body).find_all(lambda n:'problem' in n.classes))
            choices = next(body_node.find_all(lambda n:'choices' in n.classes))
            for option, key in zip((n for n in choices.children if getattr(n, 'tag', None) == 'li'), ids):
                option.attrs['data-choice'] = key
            body = outer(body_node)
            key = html.escape(answer['option_id'])
            attrs = ' data-grade-mode="single"'
        else:
            attrs = ' data-format="short" data-short-answer="' + html.escape(json.dumps(answer, ensure_ascii=False), quote=True) + '"'
            inputs = (f'<div class="short-input"><label for="answer-{id_}">단답형 답안</label>'
                      f'<input type="text" id="answer-{id_}" autocomplete="off">'
                      '<button class="btn check-answer" type="button">답 확인</button></div>')
            key = html.escape(answer['canonical']) + ' · 허용답: ' + html.escape(', '.join(answer['accepted']))
        cards.append(f'<article class="card" id="{id_}"{attrs}>' + title + body + inputs
                     + '<details class="solution"><summary>풀이</summary><ol class="steps">' + steps
                     + '</ol><p class="answer">정답: ' + key + '</p></details></article>')
    template = (REVIEW / 'assets/review-template.html').read_text(encoding='utf-8')
    # Match the locally bundled resources already selected by the exam renderer.
    head = exam.split('</head>', 1)[0]
    for url in re.findall(r'(?:href|src)="([^"]*\.pack/[^\"]+)"', head):
        if '/pretendard/' in url:
            template = re.sub(r'https://cdn.jsdelivr.net/npm/pretendard@[^" ]+/dist/web/static/pretendard.css', url, template)
        elif '/katex/' in url:
            template = re.sub(r'https://cdn.jsdelivr.net/npm/katex@[^" ]+/dist/', url.split('/katex/')[0]+'/katex/', template)
    # No associated single-date note exists for an exam spanning chapters.
    template = re.sub(r'\s*<a class="top-link"[^\n]+', '', template)
    css = '<style>.short-input{display:grid;gap:12px;margin:24px 0}.short-input input{width:100%;min-width:0;padding:12px 16px;font:inherit;background:var(--surface);color:var(--ink);border:1px solid var(--line);border-radius:8px}.short-input button{justify-self:start;min-height:44px}.short-input [hidden]{display:none!important}</style>'
    template = template.replace('</head>', css+'</head>')
    scripts = '<script>window.ReviewShortCasefold=' + json.dumps(casefold_map(), ensure_ascii=True) + ';</script>'
    values = dict(PAGE_TITLE='시험 예상문제 '+html.escape(pack['range']), DESCRIPTION='문항마다 답을 확인하고 보기별 이유를 비교해요.',
        RANGE='exam-practice-'+pack['range']+'-v'+str(pack['version']), TITLE='시험 예상문제 '+html.escape(pack['range']),
        INTRO='객관식 55문항 · 단답형 20문항. 답을 확인하고 다시 풀어 보세요. 새로고침하면 기록이 초기화됩니다.',
        NOTE_HREF='', TOC='<a href="#exam-mcq">객관식 1–55</a><a href="#exam-short">단답형 56–75</a>',
        PARTS='<section id="exam-mcq"><h2>객관식</h2>'+''.join(cards[:55])+'</section><section id="exam-short"><h2>단답형</h2>'+''.join(cards[55:])+'</section>',
        FOOTER='55+20은 연습용 구성입니다.', SCRIPTS=scripts)
    text = re.sub(r'\{\{([A-Z_]+)\}\}', lambda match:values[match[1]], template)
    return review_interaction.install(text, names(pack)['practice'])
