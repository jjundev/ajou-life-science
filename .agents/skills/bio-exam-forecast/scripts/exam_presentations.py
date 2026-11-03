"""Two standalone presentations of one authored set; no academic approvals."""
import hashlib
import html
import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
ROOT = Path(__file__).resolve().parents[4]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def names(pack):
    version = pack['version']
    if pack.get('profile') == 'exam':
        stem = f'시험예상문제_{pack["range"]}'
        return {'exam': f'{stem}_v{version}.html', 'practice': f'{stem}_연습형_v{version}.html'}
    stem = f'복습문제_{pack["chapter"]}장_웹과제예상'
    return {'practice': f'{stem}_v{version}.html', 'exam': f'{stem}_시험형_v{version}.html'}


def explanation_name(pack):
    label = pack['range'] if pack.get('profile') == 'exam' else f'{pack["chapter"]}장'
    kind = '시험예상' if pack.get('profile') == 'exam' else '웹과제예상'
    return f'문제해설_{label}_{kind}_v{pack["version"]}.html'


def set_hash(src):
    """Same authored questions/answers/order, regardless of the runtime."""
    src = Path(src)
    pack = json.loads((src / 'pack.json').read_text(encoding='utf-8'))
    if pack.get('profile') == 'exam':
        return digest(pack['problems'])
    return digest([(p['id'], (src / 'cards' / (p['id'] + '.html')).read_text(encoding='utf-8'))
                   for p in pack['problems'] if p['id'].startswith('p')])


def source_hash(src):
    src = Path(src)
    paths = [src / 'pack.json', src / 'blueprint.md']
    paths += sorted((src / 'cards').glob('*.html'))
    return digest([(p.relative_to(src).as_posix(), sha(p)) for p in paths if p.is_file()])


def decorate(text, pack, mode, question_hash):
    """Keep existing filenames; identify the mode in the page and its record."""
    outputs = names(pack)
    label = '연습형' if mode == 'practice' else '시험형'
    partner = 'exam' if mode == 'practice' else 'practice'
    meta = dict(mode=mode, documentId=outputs[mode], questionSetHash=question_hash,
                partner=outputs[partner], explanation=explanation_name(pack))
    payload = json.dumps(meta, ensure_ascii=False).replace('<', '\\u003c')
    text = text.replace('</head>', '<script type="application/json" id="presentation-meta">' + payload + '</script>\n</head>')
    text = re.sub(r'(<title>)(.*?)(</title>)', lambda m:m[1]+m[2]+' · '+label+m[3], text, count=1)
    text = re.sub(r'(<h1[^>]*>)(.*?)(</h1>)', lambda m:m[1]+m[2]+' · '+label+m[3], text, count=1, flags=re.S)
    nav = ('<nav class="presentation-links" aria-label="학습 도구"'
           + (' hidden' if mode == 'exam' else '') + '>'
           + f'<strong>{label}</strong> '
           + '<button class="text-btn" type="button" id="open-explanation"'
           + (' hidden' if mode == 'exam' else '') + '>상세 해설 열기</button></nav>')
    if mode == 'practice':
        button = '<button class="text-btn" type="button" id="open-explanation">상세 해설</button>'
        text = text.replace('<button class="text-btn theme-toggle"', button + '<button class="text-btn theme-toggle"', 1)
    else:
        text = text.replace('<main id="main">', '<main id="main">' + nav)
    # Some preserved review shells have a class on main rather than an id.
    if mode == 'exam' and 'class="presentation-links"' not in text:
        text = re.sub(r'(<main\b[^>]*>)', lambda m:m[1]+nav, text, count=1)
    css = '<style>.topbar .brand{overflow:hidden;text-overflow:ellipsis}.presentation-links{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:12px 0;font-size:var(--fs-small);}.presentation-links button{min-height:44px;display:inline-flex;align-items:center;}.presentation-links[hidden],#open-explanation[hidden]{display:none!important}.check-answer{min-height:44px;margin:8px 0}</style>'
    text = text.replace('</head>', css + '</head>')
    # Clear only this forecast's progress before the shared pager reads it.
    bootstrap = """<script>(()=>{try{sessionStorage.removeItem('od-review-solved:'+document.body.dataset.range);}catch{}if(location.hash==='#exam-results')history.replaceState(null,'',location.pathname+location.search+'#p1');})();</script>"""
    text = re.sub(r'(<body\b[^>]*>)', lambda m:m[1]+bootstrap, text, count=1)
    # Forecast practice is visit-local; ordinary review packs retain their policy.
    text = text.replace("try { storage = window.sessionStorage; } catch {}", "/* Forecast answers reset on every load. */")
    script = """<script>(()=>{const meta=JSON.parse(document.getElementById('presentation-meta').textContent);document.getElementById('open-explanation').addEventListener('click',()=>{location.href=meta.explanation;});})();</script>"""
    return text.replace('</body>', script + '</body>')


def practice_from_exam(text, pack, question_hash):
    from exam_practice import render_practice
    return decorate(render_practice(text, pack), pack, 'practice', question_hash)


def write_pair(src, texts):
    src = Path(src)
    pack = json.loads((src / 'pack.json').read_text(encoding='utf-8'))
    outputs = names(pack)
    for mode in ('practice', 'exam'):
        (src.parent.parent / outputs[mode]).write_text(texts[mode], encoding='utf-8', newline='\n')
    record = dict(schema_version=1, question_set_hash=set_hash(src), source_hash=source_hash(src),
                  files={mode:dict(name=name, sha256=sha(src.parent.parent / name)) for mode,name in outputs.items()})
    (src / 'presentations.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def check_pair(src):
    src = Path(src)
    marker = src / 'presentations.json'
    if not marker.exists():
        pack = json.loads((src / 'pack.json').read_text(encoding='utf-8'))
        for name in names(pack).values():
            path = src.parent.parent / name
            if path.is_file() and 'id="presentation-meta"' in path.read_text(encoding='utf-8'):
                return ['두 풀이형 presentations.json 누락']
        return []  # Preserved single-presentation versions keep their original contract.
    errors = []
    try:
        pack = json.loads((src / 'pack.json').read_text(encoding='utf-8'))
        record = json.loads(marker.read_text(encoding='utf-8'))
        outputs = names(pack)
        if record.get('schema_version') != 1 or record.get('source_hash') != source_hash(src) or record.get('question_set_hash') != set_hash(src):
            errors.append('두 풀이형 원본 변경: 재빌드·재검토 필요')
        if set(record['files']) != {'practice', 'exam'}:
            errors.append('연습형·시험형 기록 필요')
        for mode,name in outputs.items():
            path = src.parent.parent / name
            row = record['files'].get(mode, {})
            if row.get('name') != name or row.get('sha256') != sha(path):
                errors.append(mode + ': 풀이 HTML 누락/변경')
            match = re.search(r'<script type="application/json" id="presentation-meta">(.*?)</script>', path.read_text(encoding='utf-8'), re.S)
            meta = json.loads(match[1]) if match else {}
            if meta.get('mode') != mode or meta.get('documentId') != name or meta.get('questionSetHash') != record['question_set_hash']:
                errors.append(mode + ': 문제 집합/풀이 형태 불일치')
        if pack.get('profile') == 'exam':
            expected = practice_from_exam((src.parent.parent / outputs['exam']).read_text(encoding='utf-8'), pack, record['question_set_hash'])
            if (src.parent.parent / outputs['practice']).read_text(encoding='utf-8') != expected:
                errors.append('practice: 원본/복습문제 렌더 불일치')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('두 풀이형 검사 실패: ' + str(exc))
    return errors


def pair_paths(src):
    src = Path(src)
    if not (src / 'presentations.json').exists():
        return []
    pack = json.loads((src / 'pack.json').read_text(encoding='utf-8'))
    return [src / 'presentations.json', *(src.parent.parent / name for name in names(pack).values())]


def web_exam(practice, pack):
    """Adapt authored quiz cards to the existing deferred-grading runtime."""
    from exam_dom import parse, inner, outer
    from exam_build import casefold_map
    text = re.sub(r'<!-- review-interaction:start -->.*?<!-- review-interaction:end -->\n?', '', practice, flags=re.S)
    models = {}

    def convert(match):
        markup = match[0]
        node = next(parse(markup).find_all(lambda n:n.tag == 'article'))
        id_ = node.attrs['id']
        if id_.startswith('o'):
            return ''
        problem = next(node.find_all(lambda n:'problem' in n.classes))
        choices = next(problem.find_all(lambda n:'choices' in n.classes))
        options = [n for n in choices.children if getattr(n,'tag',None) == 'li']
        labels = 'ABCDE'[:len(options)]
        inputs = '<fieldset><legend>답 선택</legend>' + ''.join(
            f'<label><input type="radio" name="{id_}" value="{letter}"> ' + inner(option) + '</label>'
            for letter,option in zip(labels,options)) + '</fieldset>'
        solution = next(node.find_all(lambda n:'solution' in n.classes))
        steps = next(solution.find_all(lambda n:'steps' in n.classes))
        answer = next(solution.find_all(lambda n:'answer' in n.classes))
        title = next(node.find_all(lambda n:n.tag == 'h3'))
        models[id_] = dict(format='mcq', answer=dict(kind='choice', option_id=pack['answer_key'][id_]))
        provenance = html.escape(json.dumps(dict(refs=[dict(path=node.attrs.get('data-source',''),locator='')]), ensure_ascii=False))
        return (f'<article class="card" id="{id_}">' + outer(title)
                + '<div class="problem">' + inner(problem) + '</div><div class="exam-input">' + inputs
                + '</div><p class="result" role="status"></p><div class="solution" hidden>' + outer(steps) + outer(answer)
                + '</div><div class="provenance" hidden>' + provenance + '</div></article>')

    text = re.sub(r'<article\b[^>]*class="card"[^>]*>.*?</article>', convert, text, flags=re.S)
    text = text.replace('data-panels="review"', 'data-panels="exam"')
    text = text.replace('<div class="aids"></div>', '<div class="aids" id="exam-aid"></div>')
    text = text.replace('<button class="text-btn theme-toggle"', '<button class="text-btn" id="reset-exam" type="button">다시 풀기</button><button class="text-btn theme-toggle"')
    text = text.replace('</head>', (ASSETS / 'exam-template.html').read_text(encoding='utf-8') + '</head>')
    text = text.replace('</main>', (ASSETS / 'exam-results.html').read_text(encoding='utf-8') + '</main>')
    controls = '<div class="exam-actions"><button class="btn btn-primary" id="submit-exam" type="button" hidden>전체 제출</button><p id="summary" role="status" aria-live="polite"></p></div>'
    text = text.replace('<div class="pager-inner">', controls + '<div class="pager-inner">')
    meta = dict(documentId=names(pack)['exam'],range=f'{pack["chapter"]}장',examVersion=pack['version'])
    def data(id_,value):
        return '<script type="application/json" id="'+id_+'">'+json.dumps(value,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    scripts = data('exam-meta',meta) + data('exam-model',models) + data('exam-casefold',casefold_map())
    scripts += '<script>' + (ROOT / '.agents/skills/bio-review-pack/assets/review-prompt.js').read_text(encoding='utf-8') + '</script>'
    scripts += '<script>' + (ASSETS / 'exam-runtime.js').read_text(encoding='utf-8') + '</script>'
    return text.replace('<script id="theme-ui">', scripts + '<script id="theme-ui">')
