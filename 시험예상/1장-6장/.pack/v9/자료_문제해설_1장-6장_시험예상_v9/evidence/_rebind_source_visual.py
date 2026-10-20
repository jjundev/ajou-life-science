import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.scratch' / 'review-deps'))
from bs4 import BeautifulSoup

REPORT_PATH = WORK / 'evidence' / 'source-visual-full.json'
STAGE_PATH = WORK / 'stage' / '문제해설_1장-6장_시험예상.html'
EVIDENCE_PATH = WORK / 'evidence' / 'source-visual-final-rebind.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def ptexts(node):
    return [norm(p.get_text(' ', strip=True)) for p in node.find_all('p', recursive=False)] if node else None

def choices(node):
    return [norm(li.get_text(' ', strip=True)) for li in node.select('.choices > li')] if node else None

def images(node):
    return [(im.get('src'), im.get('alt')) for im in node.find_all('img')] if node else None

def semantic_img(pathpart, base):
    p = (base / pathpart).resolve()
    return {'path': str(p), 'exists': p.exists(), 'sha256': digest(p) if p.exists() else None}

report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
exam_path = Path(report['exam_path'])
baseline_path = Path(report['baseline_path'])
pack_path = Path(report['pack_path'])
stage_raw = STAGE_PATH.read_bytes()
stage_sha = hashlib.sha256(stage_raw).hexdigest()
stage = BeautifulSoup(stage_raw.decode('utf-8'), 'html.parser')
baseline = BeautifulSoup(baseline_path.read_text(encoding='utf-8'), 'html.parser')
exam = BeautifulSoup(exam_path.read_text(encoding='utf-8'), 'html.parser')
pack = json.loads(pack_path.read_text(encoding='utf-8'))
pack_items = {p['id']: p for p in pack['problems']}
checks = []

for item in report['items']:
    pid = item['id']
    staged = stage.select_one('#' + pid + ' [data-source-field="conditions"]')
    before = baseline.select_one('#' + pid + ' [data-source-field="conditions"]')
    original = exam.select_one('#' + pid + ' .problem')
    packed = BeautifulSoup(pack_items[pid]['problem_html'], 'html.parser')
    rec = {
        'id': pid,
        'stage_present': staged is not None,
        'baseline_present': before is not None,
        'exam_present': original is not None,
        'stage_equals_baseline_html': str(staged) == str(before),
        'stage_equals_exam_stems': ptexts(staged) == ptexts(original),
        'stage_equals_pack_stems': ptexts(staged) == ptexts(packed),
        'stage_equals_exam_choices': choices(staged) == choices(original),
        'stage_equals_pack_choices': choices(staged) == choices(packed),
        'stage_equals_exam_figure_alts': [alt for _, alt in images(staged) or []] == [alt for _, alt in images(original) or []],
        'stage_equals_pack_figure_alts': [alt for _, alt in images(staged) or []] == [alt for _, alt in images(packed) or []],
    }
    stage_assets = [semantic_img(src, exam_path.parent) for src, _ in images(staged) or []]
    exam_assets = [semantic_img(src, exam_path.parent) for src, _ in images(original) or []]
    rec['stage_figure_assets'] = stage_assets
    rec['exam_figure_assets'] = exam_assets
    rec['figure_bytes_match'] = [a['sha256'] for a in stage_assets] == [a['sha256'] for a in exam_assets] and all(a['exists'] for a in stage_assets + exam_assets)
    rec['status'] = 'pass' if all(v for k, v in rec.items() if k.startswith('stage_') and isinstance(v, bool)) and rec['figure_bytes_match'] else 'fail'
    checks.append(rec)

reference_checks = []
for ref in report['references']:
    p = Path(ref['path'])
    actual = digest(p) if p.exists() else None
    reference_checks.append({'path': str(p), 'previous_sha256': ref['sha256'], 'current_sha256': actual, 'exists': p.exists(), 'unchanged_from_previous_report': actual == ref['sha256']})

source_checks = [x for x in reference_checks if Path(x['path']) != STAGE_PATH.resolve()]
stage_ref = next(x for x in reference_checks if Path(x['path']) == STAGE_PATH.resolve())
result = {
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
    'stage_path': str(STAGE_PATH.resolve()),
    'old_stage_sha256_from_previous_report': stage_ref['previous_sha256'],
    'current_stage_sha256': stage_sha,
    'previous_stage_content_available': False,
    'old_to_new_full_diff_status': 'not_verifiable_without_previous_stage_bytes',
    'repair_scope_record': str(WORK / 'evidence' / 'final-repair.json'),
    'repair_scope_record_sha256': digest(WORK / 'evidence' / 'final-repair.json'),
    'problem_panel_checks': checks,
    'problem_panels_pass': sum(x['status'] == 'pass' for x in checks),
    'source_reference_checks': source_checks,
    'source_references_match_previous_report': sum(x['unchanged_from_previous_report'] for x in source_checks),
    'source_references_total': len(source_checks),
    'source_reference_failures': [x for x in source_checks if not x['unchanged_from_previous_report']],
}
if digest(STAGE_PATH) != stage_sha:
    raise RuntimeError('stage changed during validation')
if len(checks) != 75 or result['problem_panels_pass'] != 75 or result['source_references_match_previous_report'] != len(source_checks):
    EVIDENCE_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    raise RuntimeError('source visual final rebind failed; report left unchanged')

EVIDENCE_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
report['previous_stage_sha256'] = stage_ref['previous_sha256']
report['stage_problem_panel_comparison'] = {
    'path': str(STAGE_PATH.resolve()),
    'sha256': stage_sha,
    'baseline_path': str(baseline_path),
    'exact_html_equal_count': result['problem_panels_pass'],
    'differences': [],
    'evidence': str(EVIDENCE_PATH),
}
for ref in report['references']:
    if Path(ref['path']) == STAGE_PATH.resolve():
        ref['sha256'] = stage_sha
report['final_stage_rebind'] = {
    'status': 'pass',
    'evidence_path': str(EVIDENCE_PATH),
    'evidence_sha256': digest(EVIDENCE_PATH),
    'current_stage_sha256': stage_sha,
    'source_references_rechecked': len(source_checks),
    'source_references_unchanged': len(source_checks),
    'problem_panels_rechecked': len(checks),
    'problem_panels_unchanged': len(checks),
    'edit_scope_limitation': 'Earlier stage bytes are unavailable. final-repair.json records P38 solve D and P74 recall; exact old/new full-stage diff cannot be proven from a hash alone.',
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'stage_sha256': stage_sha, 'problem_panels_pass': len(checks), 'source_references_unchanged': len(source_checks), 'evidence': str(EVIDENCE_PATH)}, ensure_ascii=False, indent=2))
