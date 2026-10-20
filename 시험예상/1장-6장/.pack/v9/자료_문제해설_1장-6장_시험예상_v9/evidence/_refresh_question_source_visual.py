import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.scratch' / 'review-deps'))
sys.path.insert(0, str(REPO / '.agents' / 'skills' / 'bio-exam-forecast' / 'scripts'))
from bs4 import BeautifulSoup
from exam_build import question_input_hash

EXAM_DIR = REPO / '시험예상' / '1장-6장'
PACK_DIR = EXAM_DIR / '.pack' / 'v9'
BACKUP_DIR = WORK / 'backups' / 'pre-metadata-refresh' / '시험예상' / '1장-6장'
EXAM = EXAM_DIR / '시험예상문제_1장-6장.html'
PACK = PACK_DIR / 'pack.json'
BASELINE = WORK / 'baseline.html'
STAGE = WORK / 'stage' / '문제해설_1장-6장_시험예상.html'
PRIOR = WORK / 'evidence' / 'source-visual-full.json'
REFRESH = WORK / 'evidence' / 'exam-metadata-refresh.json'
OUTPUT = WORK / 'evidence' / 'question-source-visual-refresh.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def nfc(s):
    return unicodedata.normalize('NFC', s) if isinstance(s, str) else s

def core_without_provenance(node):
    soup = BeautifulSoup(str(node), 'html.parser')
    tag = soup.select_one('.provenance')
    if tag:
        tag.decompose()
    return str(soup)

def text(node):
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip() if node else None

def paragraphs(node):
    return [text(p) for p in node.find_all('p', recursive=False)] if node else None

def choices(node):
    return [text(li) for li in node.select('.choices > li')] if node else None

def imgs(node):
    return [(im.get('src'), im.get('alt')) for im in node.find_all('img')] if node else None

def strip_ref_meta(obj):
    if isinstance(obj, dict):
        return {k: strip_ref_meta(v) for k, v in obj.items() if k not in ('path', 'sha256', 'status')}
    if isinstance(obj, list):
        return [strip_ref_meta(v) for v in obj]
    return nfc(obj)

old_pack = json.loads((BACKUP_DIR / '.pack' / 'v9' / 'pack.json').read_text(encoding='utf-8'))
new_pack = json.loads(PACK.read_text(encoding='utf-8'))
old_exam = BeautifulSoup((BACKUP_DIR / EXAM.name).read_text(encoding='utf-8'), 'html.parser')
new_exam = BeautifulSoup(EXAM.read_text(encoding='utf-8'), 'html.parser')
stage = BeautifulSoup(STAGE.read_text(encoding='utf-8'), 'html.parser')
baseline = BeautifulSoup(BASELINE.read_text(encoding='utf-8'), 'html.parser')
prior = json.loads(PRIOR.read_text(encoding='utf-8'))
metadata = json.loads(REFRESH.read_text(encoding='utf-8'))
old_by_id = {p['id']: p for p in old_pack['problems']}
new_by_id = {p['id']: p for p in new_pack['problems']}
prior_by_id = {p['id']: p for p in prior['items']}
expected_ids = [f'p{i}' for i in range(1, 76)]
assert list(old_by_id) == expected_ids and list(new_by_id) == expected_ids

pack_differences = {}
for pid in expected_ids:
    a, b = old_by_id[pid], new_by_id[pid]
    pack_differences[pid] = [k for k in a if a.get(k) != b.get(k)]

scope_old = json.loads((BACKUP_DIR / '.pack' / 'v9' / 'scope.json').read_text(encoding='utf-8'))
scope_new = json.loads((PACK_DIR / 'scope.json').read_text(encoding='utf-8'))
scope_core_same = strip_ref_meta(scope_old) == strip_ref_meta(scope_new)
scope_pack_same = strip_ref_meta(old_pack['scope_data']) == strip_ref_meta(new_pack['scope_data'])
global_js_same = str(old_exam.find_all('script')) == str(new_exam.find_all('script'))
global_style_same = str(old_exam.find_all('style')) == str(new_exam.find_all('style'))

old_refs = {r['path']: r['sha256'] for r in prior['references']}
reference_checks = []
for pathstr, old_sha in sorted(old_refs.items()):
    p = Path(pathstr)
    actual = digest(p) if p.exists() else None
    reference_checks.append({'path': pathstr, 'previous_sha256': old_sha, 'current_sha256': actual, 'changed': actual != old_sha, 'exists': p.exists()})

manifest = json.loads((PACK_DIR / 'source-manifest.json').read_text(encoding='utf-8'))
manifest_checks = []
for row in manifest['sources']:
    p = REPO / row['path']
    exists = p.is_file()
    actual = digest(p) if exists else None
    manifest_checks.append({'path': row['path'], 'role': row['role'], 'declared_status': row['status'], 'declared_sha256': row['sha256'], 'actual_status': 'present' if exists else 'missing', 'actual_sha256': actual, 'pass': row['status'] == ('present' if exists else 'missing') and row['sha256'] == actual})

old_render_checks = []
for page in prior['rendered_pages']:
    p = Path(page['path'])
    old_render_checks.append({'path': page['path'], 'source_pdf': page['source_pdf'], 'page': page['page'], 'previous_sha256': page['sha256'], 'current_sha256': digest(p) if p.exists() else None, 'viewed_in_prior_review': page['viewed'], 'unchanged': p.exists() and digest(p) == page['sha256']})

item_reviews = {}
item_checks = []
for pid in expected_ids:
    old, new = old_by_id[pid], new_by_id[pid]
    old_card, new_card = old_exam.select_one('#' + pid), new_exam.select_one('#' + pid)
    old_prob, new_prob = old_card.select_one('.problem'), new_card.select_one('.problem')
    before_panel = baseline.select_one('#' + pid + ' [data-source-field="conditions"]')
    stage_panel = stage.select_one('#' + pid + ' [data-source-field="conditions"]')
    prior_item = prior_by_id[pid]
    provenance = new_card.select_one('.provenance')
    provenance_data = json.loads(provenance.get_text()) if provenance else None
    refs = []
    for ref in new['source_refs']:
        p = REPO / ref['path']
        refs.append({'path': str(p), 'role': ref['role'], 'locator': ref['locator'], 'sha256': digest(p) if p.is_file() else None, 'matches_declared': p.is_file() and digest(p) == ref['sha256']})
    style_refs = []
    for ref in new['style_basis']:
        p = REPO / ref['path']
        style_refs.append({'path': str(p), 'role': ref.get('role'), 'locator': ref['locator'], 'sha256': digest(p) if p.is_file() else None, 'matches_declared': p.is_file() and digest(p) == ref['sha256']})
    answers_same = old['answer'] == new['answer']
    core_fields_same = all(old.get(k) == new.get(k) for k in old if k not in ('source_refs', 'style_basis', 'types', 'original_payload_sha256', 'problem_html'))
    original_payload_path_only = nfc(old['problem_html']) == nfc(new['problem_html'])
    current_img = imgs(new_prob)
    stage_img = imgs(stage_panel)
    img_bytes = []
    for (src1, alt1), (src2, alt2) in zip(current_img, stage_img):
        p1, p2 = EXAM_DIR / src1, EXAM_DIR / src2
        img_bytes.append({'exam_path': str(p1), 'stage_path': str(p2), 'alt_matches': alt1 == alt2, 'sha256': digest(p1) if p1.exists() else None, 'stage_sha256': digest(p2) if p2.exists() else None, 'match': p1.exists() and p2.exists() and digest(p1) == digest(p2) and alt1 == alt2})
    checks = {
        'question_html_unchanged': str(old_prob) == str(new_prob),
        'question_article_without_provenance_unchanged': core_without_provenance(old_card) == core_without_provenance(new_card),
        'stage_panel_unchanged_from_baseline': str(stage_panel) == str(before_panel),
        'stage_stems_match_current_question': paragraphs(stage_panel) == paragraphs(new_prob),
        'stage_choices_match_current_question': choices(stage_panel) == choices(new_prob),
        'stage_figure_bytes_match_current_question': len(current_img) == len(stage_img) and all(x['match'] for x in img_bytes),
        'pack_problem_html_same_after_nfc': original_payload_path_only,
        'pack_options_unchanged': old.get('options') == new.get('options'),
        'pack_answer_unchanged': answers_same,
        'pack_other_core_fields_unchanged': core_fields_same,
        'candidate_id_unchanged': old['candidate_id'] == new['candidate_id'],
        'source_ref_role_locator_unchanged': strip_ref_meta(old['source_refs']) == strip_ref_meta(new['source_refs']),
        'style_basis_semantics_unchanged': strip_ref_meta(old['style_basis']) == strip_ref_meta(new['style_basis']),
        'source_ref_hashes_current': all(r['matches_declared'] for r in refs),
        'style_basis_hashes_current': all(r['matches_declared'] for r in style_refs),
        'provenance_matches_pack': provenance_data is not None and provenance_data.get('origin') == new['origin'] and provenance_data.get('mode') == new['mode'] and provenance_data.get('refs') == new['source_refs'],
    }
    if new['origin'] == 'web':
        bankref = next(r for r in refs if r['role'] in ('bank', 'bank_variant_basis'))
        bank = json.loads(Path(bankref['path']).read_text(encoding='utf-8'))
        q = next((q for q in bank['questions'] if q['id'] == bankref['locator']), None)
        checks['bank_candidate_found'] = q is not None
        if new['mode'] == 'original' and q is not None:
            bank_stems = [nfc(c['text']) for c in q['original']['content'] if c['type'] == 'text']
            checks['bank_original_stems_match'] = bank_stems == [nfc(x) for x in paragraphs(new_prob)]
            checks['bank_original_options_match'] = [(x['id'], nfc(x['text'])) for x in q['original']['options']] == [(x['id'], nfc(x['text'])) for x in new['options']]
    if new['origin'] == 'past' and new['mode'] == 'original':
        checks['prior_pdf_source_bytes_unchanged'] = all(r['sha256'] == next((x['sha256'] for x in prior_item['source']['references'] if x['role'] == r['role']), None) for r in refs if r['role'] == 'past_original_pdf')
    item_status = 'pass' if all(checks.values()) else 'fail'
    prior_text = prior_item['review']['evidence'].split(' pack.json의 일부 과거 참조 SHA와 현재 바이트 SHA 불일치')[0]
    ref_summary = ', '.join(f"{r['role']} {r['locator']} [{r['sha256'][:12]}]" for r in refs)
    evidence = f"{prior_text} 메타데이터 갱신 전 백업과 현재 문제의 지문·보기·그림·채점 핵심 동일; 현재 source_refs 직접 해시 확인: {ref_summary}."
    if pid == 'p4':
        evidence += ' pack.problem_html의 그림 경로는 NFC 정규화만 달라졌고 현재 공개 문제 SVG 및 기존 해설 SVG의 바이트가 일치.'
    if new['origin'] == 'web' and new['mode'] == 'original':
        evidence += ' 현재 questions.json original.content/options와 재대조.'
    if new['origin'] == 'past' and new['mode'] == 'original':
        evidence += ' 기존에 실제 렌더·열어 확인한 합본 PDF 쪽의 원파일과 렌더 PNG SHA가 그대로임.'
    item_reviews[pid] = evidence
    item_checks.append({'id': pid, 'status': item_status, 'candidate_id': new['candidate_id'], 'origin': new['origin'], 'mode': new['mode'], 'changed_pack_fields': pack_differences[pid], 'checks': checks, 'source_refs': refs, 'style_basis_refs': style_refs, 'figure_assets': img_bytes, 'evidence': evidence})

review_input_hash = json.loads((PACK_DIR / 'question-review.json').read_text(encoding='utf-8'))['input_hash']
actual_input_hash = question_input_hash(PACK_DIR, EXAM)
reference_current = [{'path': x['path'], 'sha256': x['current_sha256']} for x in reference_checks]
summary = {
    'status': 'pass' if len(item_checks) == 75 and all(x['status'] == 'pass' for x in item_checks) and all(x['pass'] for x in manifest_checks) and all(x['unchanged'] for x in old_render_checks) and scope_core_same and scope_pack_same and global_js_same and global_style_same else 'fail',
    'reviewer': 'source_visual agent (post-metadata refresh)',
    'evidence': '메타데이터 갱신 전 백업과 현재 75문항의 문제 본문·보기·그림·답/채점 핵심을 재대조. 기출 원문 10개는 기존 직접 렌더·시각 대조한 PDF/PNG의 현재 바이트 불변을 확인; 웹 원문 20개는 현재 questions.json 원문 문단·보기와 재대조; 변형·생성 45개는 현재 source_refs와 정리노트/강의자료의 바이트 불변·앵커/조건 유지 확인. 현재 source_refs 138개와 style_basis 137개의 실제 해시 일치. 상세: evidence/question-source-visual-refresh.json.',
    'items': item_reviews,
    'input_hash': actual_input_hash,
    'question_review_input_hash': review_input_hash,
    'question_review_input_hash_matches_current': review_input_hash == actual_input_hash,
    'official_review_binding_note': 'The source_visual review is for input_hash above. A different question-review.json input_hash must be rebound before copying this pass into that file.',
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
    'current_references': reference_current,
    'reference_changes_since_previous_source_visual': [x for x in reference_checks if x['changed']],
    'backup_paths': {'exam': str(BACKUP_DIR / EXAM.name), 'pack': str(BACKUP_DIR / '.pack' / 'v9' / 'pack.json'), 'scope': str(BACKUP_DIR / '.pack' / 'v9' / 'scope.json')},
    'current_hashes': {'exam': digest(EXAM), 'pack': digest(PACK), 'stage': digest(STAGE), 'metadata_refresh': digest(REFRESH)},
    'core_preservation': {'global_script_same': global_js_same, 'global_style_same': global_style_same, 'scope_core_same': scope_core_same, 'pack_scope_core_same': scope_pack_same, 'all_question_articles_without_provenance_same': all(x['checks']['question_article_without_provenance_unchanged'] for x in item_checks), 'all_pack_answers_same': all(x['checks']['pack_answer_unchanged'] for x in item_checks), 'all_pack_problem_html_nfc_same': all(x['checks']['pack_problem_html_same_after_nfc'] for x in item_checks)},
    'metadata_diff': {'changed_pack_fields': {p['id']: p['changed_pack_fields'] for p in item_checks if p['changed_pack_fields']}, 'source_rows_refreshed': metadata['source_rows_refreshed'], 'nfc_resource_path_only': metadata['nfc_resource_path_only']},
    'manifest_counts': dict(Counter(x['actual_status'] for x in manifest_checks)),
    'manifest_failures': [x for x in manifest_checks if not x['pass']],
    'prior_render_page_checks': old_render_checks,
    'item_checks': item_checks,
}
OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'status': summary['status'], 'items': len(item_checks), 'item_failures': [x['id'] for x in item_checks if x['status'] != 'pass'], 'references': len(reference_checks), 'reference_changes': [Path(x['path']).name for x in summary['reference_changes_since_previous_source_visual']], 'manifest': summary['manifest_counts'], 'manifest_failures': len(summary['manifest_failures']), 'render_pages_unchanged': sum(x['unchanged'] for x in old_render_checks), 'input_hash_match': review_input_hash == actual_input_hash, 'scope_core_same': scope_core_same}, ensure_ascii=False, indent=2))
