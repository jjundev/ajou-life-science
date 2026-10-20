import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.scratch' / 'review-deps'))
from bs4 import BeautifulSoup
import fitz

PACK_PATH = REPO / '시험예상' / '1장-6장' / '.pack' / 'v9' / 'pack.json'
EXAM_PATH = REPO / '시험예상' / '1장-6장' / '시험예상문제_1장-6장.html'
BASELINE_PATH = WORK / 'baseline.html'
OUT_PATH = WORK / 'evidence' / 'source-visual-full.json'
PAGE_DIR = WORK / 'evidence' / 'source-pages'
PAGE_DIR.mkdir(parents=True, exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def resolve(path):
    cur = REPO
    for part in Path(path).parts:
        norm = unicodedata.normalize('NFC', part)
        matches = [p for p in cur.iterdir() if unicodedata.normalize('NFC', p.name) == norm]
        if not matches:
            return cur / part
        cur = matches[0]
    return cur

def txt(node):
    return node.get_text(' ', strip=True) if node else ''

def clean(t):
    return re.sub(r'\s+', ' ', t).strip()

def html_content(s):
    return BeautifulSoup(s, 'html.parser')

pack = json.loads(PACK_PATH.read_text(encoding='utf-8'))
exam = BeautifulSoup(EXAM_PATH.read_text(encoding='utf-8'), 'html.parser')
baseline = BeautifulSoup(BASELINE_PATH.read_text(encoding='utf-8'), 'html.parser')
bank_cache = {}
ref_map = {}
page_map = {}
items = []

for p in pack['problems']:
    pid = p['id']
    card = exam.select_one('#' + pid)
    pane = baseline.select_one('#' + pid + ' [data-source-field="conditions"]')
    pack_html = html_content(p['problem_html'])
    original = card.select_one('.problem') if card else None
    tests = {}
    tests['card_exists'] = card is not None
    tests['baseline_problem_exists'] = pane is not None
    tests['stem_pack_exam'] = [txt(x) for x in pack_html.find_all('p')] == [txt(x) for x in original.find_all('p')] if original else False
    tests['stem_exam_baseline'] = [txt(x) for x in original.find_all('p')] == [txt(x) for x in pane.find_all('p')] if original and pane else False
    tests['choices_pack_exam'] = [txt(x) for x in pack_html.select('.choices li')] == [txt(x) for x in original.select('.choices li')] if original else False
    tests['choices_exam_baseline'] = [txt(x) for x in original.select('.choices li')] == [txt(x) for x in pane.select('.choices li')] if original and pane else False
    tests['figures_pack_exam'] = [(x.get('src'), x.get('alt')) for x in pack_html.find_all('img')] == [(x.get('src'), x.get('alt')) for x in original.find_all('img')] if original else False
    tests['figures_exam_baseline'] = [(x.get('src'), x.get('alt')) for x in original.find_all('img')] == [(x.get('src'), x.get('alt')) for x in pane.find_all('img')] if original and pane else False
    tests['option_model_matches_choices'] = [clean(re.sub(r'^\(\d+\)\s*', '', txt(x))) for x in pack_html.select('.choices li')] == [clean(o['text']) for o in p.get('options', [])] if p['format'] == 'mcq' else True
    refs = []
    for ref in p.get('source_refs', []):
        path = resolve(ref['path'])
        rec = {'path': str(path), 'role': ref.get('role'), 'locator': ref.get('locator'), 'candidate_id': p.get('candidate_id'), 'exists': path.exists(), 'expected_sha256': ref.get('sha256')}
        if path.exists():
            rec['sha256'] = ref_map.setdefault(str(path), sha(path))
            rec['hash_matches_pack'] = not ref.get('sha256') or rec['sha256'] == ref['sha256']
        else:
            rec['hash_matches_pack'] = False
        refs.append(rec)
    source = {'basis': p['origin'] + '/' + p['mode'], 'candidate_id': p.get('candidate_id'), 'references': refs}
    if p['origin'] == 'web':
        bref = next((r for r in refs if r['role'] in ('bank', 'bank_variant_basis')), None)
        if bref and bref['exists']:
            if bref['path'] not in bank_cache:
                bank_cache[bref['path']] = json.loads(Path(bref['path']).read_text(encoding='utf-8'))
            bank = bank_cache[bref['path']]
            q = next((q for q in bank['questions'] if q['id'] == bref['locator']), None)
            source['bank_question_found'] = q is not None
            if q:
                source['bank_question_id'] = q['id']
                if p['mode'] == 'original':
                    source['bank_stems_match'] = [clean(c['text']) for c in q['original']['content'] if c['type'] == 'text'] == [clean(txt(x)) for x in pack_html.find_all('p')]
                    source['bank_options_match'] = [(o['id'], clean(o['text'])) for o in q['original']['options']] == [(o['id'], clean(o['text'])) for o in p['options']]
                    assets = []
                    for content in q['original']['content']:
                        if content['type'] == 'figure':
                            asset = next((a for a in bank['assets'] if a['id'] == content['asset_id']), None)
                            if asset:
                                img_path = Path(bref['path']).parent / asset['exam']['path']
                                assets.append({'path': str(img_path), 'exists': img_path.exists(), 'sha256': sha(img_path) if img_path.exists() else None, 'expected_sha256': asset['exam']['sha256'], 'src_in_problem': [x.get('src') for x in pack_html.find_all('img')]})
                    source['bank_figures'] = assets
                else:
                    source['variant_basis_stem'] = ' '.join(c['text'] for c in q['original']['content'] if c['type'] == 'text')
        else:
            source['bank_question_found'] = False
    if p['origin'] == 'past' and p['mode'] == 'original':
        pdf_ref = next((r for r in refs if r['role'] == 'past_original_pdf'), None)
        if pdf_ref and pdf_ref['exists']:
            doc = fitz.open(pdf_ref['path'])
            pgnums = [int(x) for x in re.search(r'PDF ([\d, ]+)쪽', pdf_ref['locator']).group(1).replace(' ', '').split(',')]
            pages = []
            for n in pgnums:
                page = doc[n-1]
                filename = f'past-ch{p["primary_chapter"]}-p{n}.png'
                output = PAGE_DIR / filename
                if not output.exists():
                    page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(output)
                page_map[str(output)] = {'path': str(output), 'source_pdf': pdf_ref['path'], 'page': n, 'sha256': sha(output)}
                pages.append({'page': n, 'render_path': str(output), 'render_sha256': page_map[str(output)]['sha256'], 'text_excerpt': clean(page.get_text())[:1200]})
            source['past_pages'] = pages
            doc.close()
    if p['origin'] == 'new' or p['mode'] == 'variant':
        source['transformation'] = p.get('transformation')
        source['teaching_pages'] = []
        for ref in refs:
            if ref['role'] == 'teaching' and ref['exists'] and Path(ref['path']).suffix.lower() == '.pdf':
                doc = fitz.open(ref['path'])
                m = re.search(r'PDF p\.([0-9]+)(?:-([0-9]+))?', ref['locator'] or '')
                if m:
                    start, end = int(m.group(1)), int(m.group(2) or m.group(1))
                    if end <= len(doc):
                        for n in range(start, end + 1):
                            source['teaching_pages'].append({'path': ref['path'], 'page': n, 'text_excerpt': clean(doc[n-1].get_text())[:1300]})
                    else:
                        source['teaching_page_out_of_range'] = [start, end, len(doc)]
                doc.close()
    status = 'pass' if all(tests.values()) and all(r['hash_matches_pack'] for r in refs) else 'fail'
    if p['origin'] == 'web' and p['mode'] == 'original':
        if not all([source.get('bank_question_found'), source.get('bank_stems_match'), source.get('bank_options_match')]) or any(not a['exists'] or a['sha256'] != a['expected_sha256'] for a in source.get('bank_figures', [])):
            status = 'fail'
    if p['origin'] == 'web' and p['mode'] == 'variant' and not source.get('bank_question_found'):
        status = 'fail'
    if p['origin'] == 'past' and p['mode'] == 'original':
        status = 'needs_visual_review' if status == 'pass' else status
    if p['origin'] == 'new' or p['mode'] == 'variant':
        status = 'needs_semantic_review' if status == 'pass' else status
    items.append({'id': pid, 'status': status, 'format': p['format'], 'origin': p['origin'], 'mode': p['mode'], 'candidate_id': p.get('candidate_id'), 'problem_text': clean(txt(pack_html)), 'checks': tests, 'source': source})

report = {'schema_version': 1, 'reviewer': 'source_visual agent', 'status': 'in_progress', 'scope': 'exam p1-p75', 'exam_path': str(EXAM_PATH), 'pack_path': str(PACK_PATH), 'baseline_path': str(BASELINE_PATH), 'references': [{'path': x, 'sha256': y} for x, y in sorted(ref_map.items())] + [{'path': str(path), 'sha256': sha(path)} for path in (EXAM_PATH, PACK_PATH, BASELINE_PATH)], 'rendered_pages': list(page_map.values()), 'items': items, 'counts': dict(Counter(x['status'] for x in items))}
OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'counts': report['counts'], 'rendered_pages': len(page_map), 'references': len(report['references']), 'failed': [(x['id'], [k for k, v in x['checks'].items() if not v], [r['path'] for r in x['source']['references'] if not r['hash_matches_pack']]) for x in items if x['status'] == 'fail']}, ensure_ascii=False, indent=2))
