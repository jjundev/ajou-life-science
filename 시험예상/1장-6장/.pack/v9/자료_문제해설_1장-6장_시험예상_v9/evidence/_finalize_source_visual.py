import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.scratch' / 'review-deps'))
from bs4 import BeautifulSoup

OUT = WORK / 'evidence' / 'source-visual-full.json'
report = json.loads(OUT.read_text(encoding='utf-8'))
pack = json.loads(Path(report['pack_path']).read_text(encoding='utf-8'))
pack_items = {p['id']: p for p in pack['problems']}
ref_map = {r['path']: r['sha256'] for r in report['references']}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add_ref(path):
    path = path.resolve()
    ref_map[str(path)] = sha(path)
    return {'path': str(path), 'sha256': ref_map[str(path)]}

def text(node):
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip() if node else ''

PAST = {
    'p1': '1강 합본 PDF 1쪽 말미~2쪽 첫 줄 16번: 같은 지역·같은 종, 보기 1~4와 붉은 1번 일치.',
    'p2': '1강 합본 PDF 1쪽 1번: 원자번호 발문, 양성자 수 등 보기 1~5와 붉은 1번 일치.',
    'p11': '2강 합본 PDF 3쪽 39번: 효소 재사용 문장과 보기 1~4, 붉은 2번 일치.',
    'p12': '2강 합본 PDF 1쪽 2번: 과정/생성물 짝의 네 보기와 붉은 4번 일치.',
    'p20': '3강 합본 PDF 1쪽 7번: 동원체 빈칸과 보기 1~4, 붉은 2번 일치.',
    'p21': '3강 합본 PDF 2쪽 24번: 암세포가 다른 곳으로 퍼지는 과정, 보기 1~5와 붉은 3번 일치.',
    'p29': '4강 합본 PDF 2쪽 22번: 혈우병의 여러 증상·단일 유전자 조건, 보기 1~4와 붉은 2번 일치.',
    'p42': '5강 합본 PDF 4쪽 34번: 번역 중 tRNA 기능, 보기 1~4와 붉은 2번 일치.',
    'p54': '6강 합본 PDF 4쪽 28번: 세균 삽입 클로닝 벡터, 보기 1~4와 붉은 4번 일치.',
    'p55': '6강 합본 PDF 2쪽 10번: 인위적 유전자 조작 기술, 보기 1~5와 붉은 3번 일치.',
}

DERIVED = {
    'p7': '1장 강의 PDF 3쪽 인지질의 인산기·글리세롤·두 지방산과 6쪽 이중막의 머리/꼬리 방향을 대조.',
    'p8': '1장 강의 PDF 5쪽 원핵세포의 핵양체·리보솜, 핵막 부재와 진핵세포의 막성 핵을 대조.',
    'p9': '1장 강의 PDF 4쪽 세포가 작은 이유인 표면적/부피 비를 확인; 정육면체 6a²/a³로 새 길이 조건을 점검.',
    'p10': '1장 강의 PDF 2~3쪽 녹말·섬유소의 포도당 단위, 6쪽 식물 세포벽의 섬유소를 대조.',
    'p17': '2장 강의 PDF 3쪽 H⁺ 기울기가 ATP 합성효소의 에너지원임을 확인하고 누출이라는 변경 조건을 대조.',
    'p18': '2장 강의 PDF 5쪽 고온·기공 닫힘 때 CO₂ 감소/O₂ 증가와 루비스코 산소화효소 작용을 대조.',
    'p19': '2장 강의 PDF 4~5쪽 틸라코이드의 물 분해와 스트로마의 CO₂ 고정을 표 (가)/(나)에 대조.',
    'p26': '3장 강의 PDF 2쪽 유사분열 후기 자매분체 분리, 4쪽 감수 I의 상동염색체 접합·분배를 대조.',
    'p27': '3장 강의 PDF 1~2쪽 간기 DNA 복제와 유사분열 전 단계에 새 2C→4C 그래프 조건을 대조.',
    'p28': '3장 강의 PDF 4~5쪽 감수 전기 I 상동염색체 접합·교차·재조합을 대조.',
    'p34': '4장 강의 PDF 4쪽 ABO의 Iᴬ·Iᴮ·i 관계와 ii=O형을 부모 유전자형에 대조.',
    'p35': '4장 강의 PDF 2쪽 우성/열성 단성교배와 분리 법칙에 1:1 검정교배 결과를 대조.',
    'p36': '4장 강의 PDF 4~5쪽 같은 염색체 유전자의 연관과 재조합을 가까운 두 유전자 조건에 대조.',
    'p37': '4장 강의 PDF 3쪽 불완전 우성의 붉음:분홍:흰색 1:2:1 사례와 새 RR/Rr/rr 표기를 대조.',
    'p43': '5장 강의 PDF 8쪽 전사 후 조절의 mRNA 분해속도·반감기 변화와 같은 전사속도 조건을 대조.',
    'p44': '5장 강의 PDF 1~2쪽 새 가닥 5′→3′ 합성과 지체가닥의 역방향 오카자키 절편을 대조.',
    'p45': '5장 강의 PDF 7쪽 Lac 억제자의 작동자 결합과 알로락토스에 의한 비활성화를 결합 불능 돌연변이 조건에 대조.',
    'p46': '5장 강의 PDF 3~6쪽 mRNA 코돈·종결 코돈과 문항에 제공된 코돈표를 대조.',
    'p47': '6장 강의 PDF 2~3쪽 STR 좌위별 대립유전자를 부모에게서 하나씩 받는 친자확인 원리를 새 반복 횟수 표에 대조.',
    'p48': '6장 강의 PDF 1쪽 제한효소·점착성 말단, 5장 PDF 2쪽 DNA 연결효소가 골격의 틈을 메운다는 서술을 대조.',
    'p49': '6장 강의 PDF 5쪽 유전자와 비암호화 DNA를 포함한 유전체학, 교과서 6장 PDF 14~16쪽 비암호화 서열·단백질체·컴퓨터 자료분석을 대조.',
    'p50': '6장 강의 PDF 1~2쪽 PCR 주형·프라이머·중합효소와 수업의 변성→결합→신장 순서를 대조.',
    'p51': '6장 강의 PDF 2쪽 DNA의 음전하와 작은 절편의 빠른 겔 이동을 200/800 bp 조건에 대조.',
    'p52': '6장 강의 PDF 6쪽 guide RNA의 상보 DNA 결합과 Cas9의 절단 역할을 대조.',
    'p53': '6장 강의 PDF 4쪽 제핵 난자·체세포 핵·대리모의 돌리 절차와 문항의 난자 미토콘드리아 가정을 대조.',
    'p56': '1장 강의 PDF 4쪽 뉴클레오사이드(염기+5탄당)+인산기=뉴클레오타이드를 대조.',
    'p57': '1장 강의 PDF 4쪽 이중나선 상보 염기쌍의 수소결합을 당-인산 골격 제외 조건과 대조.',
    'p58': '1장 강의 PDF 2쪽 물속 비극성 부분의 소수성 결합/모임과 3~4쪽 단백질 곁사슬·접힘을 대조.',
    'p59': '2장 강의 PDF 1쪽 비타민 등의 유기 보조인자/조효소와 무기 금속 보조인자를 대조.',
    'p60': '2장 강의 PDF 2쪽 산화-환원에서 전자 상실=산화를 대조.',
    'p61': '2장 강의 PDF 1쪽 효소가 활성화에너지를 낮춘다는 정의에 20/100/60 kJ/mol 조건을 대조.',
    'p62': '2장 강의 PDF 2쪽 해당과정의 포도당 1분자→피루브산 2분자를 대조.',
    'p63': '3장 강의 PDF 2쪽 유사분열 전기의 염색체 응축과 중기의 배열을 대조.',
    'p64': '3장 강의 PDF 3~4쪽 감수분열 2회와 전기 I 이전 간기의 복제 조건을 대조.',
    'p65': '3장 강의 PDF 3~4쪽 2배체에서 반수체로 줄어드는 감수분열을 2n=6에 적용.',
    'p66': '3장 강의 PDF 2쪽 사이클린·CDK 내부 세포주기 조절자를 대조.',
    'p67': '4장 강의 PDF 4쪽 피부색의 다인자유전과 한 유전자의 다면발현을 구별.',
    'p68': '4장 강의 PDF 7쪽 비분리로 여분 염색체가 생기는 내용을 n+1과 n의 수정 조건에 대조.',
    'p69': '4장 강의 PDF 2~3쪽 독립분리·양성잡종 배우자 비율을 AaBb×aabb에 적용.',
    'p70': '5장 강의 PDF 6쪽 코돈은 바뀌지만 아미노산은 그대로인 침묵 돌연변이를 대조.',
    'p71': '5장 강의 PDF 9쪽 유비퀴틴 표지 단백질을 프로테아좀이 분해하는 과정을 대조.',
    'p72': '5장 강의 PDF 1쪽 [A]=[T], [G]=[C]를 전체 A 28% 조건에 적용.',
    'p73': 'STT/1015 생명.md 49~55행의 한 세트 n=23, 약 30억(정확히 32억) 염기쌍을 직접 대조.',
    'p74': '6장 강의 PDF 1쪽 자기 DNA의 제한효소 인식 염기 메틸화 보호를 대조.',
    'p75': '6장 강의 PDF 1~2쪽 PCR 증폭과 문항의 매 주기 정확히 2배라는 명시 가정을 대조.',
}

assert len(PAST) == 10 and len(DERIVED) == 45
assert len(report['items']) == 75
candidate_unique = len({item['candidate_id'] for item in report['items']}) == 75

EXAM_DIR = Path(report['exam_path']).parent
for item in report['items']:
    pid = item['id']
    p = pack_items[pid]
    src = item['source']
    candidate_matches = True
    if item['origin'] == 'web' and item['mode'] == 'original':
        candidate_matches = item['candidate_id'] == src.get('bank_question_id')
    elif item['origin'] == 'past' and item['mode'] == 'original':
        parsed = re.fullmatch(r'기출 (\d+)강 (\d+)', item['candidate_id'])
        pdfref = next((r for r in src['references'] if r['role'] == 'past_original_pdf'), None)
        candidate_matches = bool(parsed and pdfref and f'{parsed.group(2)}번' in pdfref['locator'] and int(parsed.group(1)) == p['primary_chapter'])
    src['candidate_id_check'] = {'unique_in_pack': candidate_unique, 'matches_origin_locator': candidate_matches}
    if item['origin'] == 'past':
        card_ref = next((r for r in src['references'] if r['role'] == 'past_review_card'), None)
        if card_ref and card_ref['exists']:
            soup = BeautifulSoup(Path(card_ref['path']).read_text(encoding='utf-8'), 'html.parser')
            node = soup.select_one('#' + card_ref['locator'] + ' .problem')
            src['current_review_card_problem_found'] = node is not None
            if item['mode'] == 'original':
                src['current_review_card_matches_pack'] = text(node) == item['problem_text']
            else:
                src['current_review_card_basis'] = text(node)
    frag = WORK / 'fragments' / f'{pid}.html'
    if frag.exists():
        f = BeautifulSoup(frag.read_text(encoding='utf-8'), 'html.parser')
        note_recs = []
        for a in f.select('[data-explanation="recall"] a[href]'):
            h = unquote(a['href'])
            pathpart, _, anchor = h.partition('#')
            target = (EXAM_DIR / pathpart).resolve()
            rec = {'path': str(target), 'anchor': anchor, 'link_text': text(a), 'exists': target.exists()}
            if target.exists():
                add_ref(target)
                rec['sha256'] = ref_map[str(target)]
                note = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
                section = note.find(id=anchor)
                rec['anchor_found'] = section is not None
                if section:
                    rec['section_excerpt'] = text(section)[:500]
            note_recs.append(rec)
        src['current_note_sections'] = note_recs
    item['review'] = {'reviewer': 'source_visual agent', 'evidence': ''}
    if pid in PAST:
        item['review']['evidence'] = PAST[pid] + ' 렌더 이미지 실제 view_image 확인. 현재 참고 복습카드의 해당 문제와도 지문·보기 일치.'
        src['past_pages_viewed'] = True
    elif item['origin'] == 'web' and item['mode'] == 'original':
        item['review']['evidence'] = f"{src['references'][0]['path']}의 {src.get('bank_question_id')} original.content/options와 현 문제의 모든 문단·보기 ID/문구 직접 대조."
    else:
        item['review']['evidence'] = DERIVED[pid] + ' 현재 원자료/정리노트 절을 재확인.'
    src['source_ref_hash_mismatch'] = [r['path'] for r in src['references'] if not r['hash_matches_pack']]
    # Stale provenance hashes are recorded separately. Current source content is checked above.
    preserved = all(item['checks'][k] for k in ('card_exists', 'baseline_problem_exists', 'stem_pack_exam', 'stem_exam_baseline', 'choices_pack_exam', 'choices_exam_baseline', 'option_model_matches_choices'))
    figure_ok = item['checks']['figures_pack_exam'] and item['checks']['figures_exam_baseline']
    if pid == 'p4':
        paths = [REPO / '웹과제' / '1장' / 'image' / 'q09.svg', EXAM_DIR / '.pack' / 'v9' / 'assets' / 'bcd017d498d7e5cf.svg', EXAM_DIR / '.pack' / 'v3' / 'figures_문제해설_1장-6장_시험예상_v3' / 'bcd017d498d7e5cf-bcd017d498d7e5cf.svg']
        src['figure_copy_hashes'] = [add_ref(path) for path in paths]
        figure_ok = len({sha(path) for path in paths}) == 1 and all(path.exists() for path in paths)
        item['review']['evidence'] += ' 그림은 웹과제 원본 SVG·시험 .pack/v9 복사본·기존 해설 .pack/v3 복사본이 같은 SHA-256; 경로만 다름.'
    if not preserved or not figure_ok:
        item['status'] = 'fail'
        item['review']['evidence'] += ' 원문 보존 또는 그림 비교 실패.'
    elif not candidate_unique or not candidate_matches:
        item['status'] = 'fail'
        item['review']['evidence'] += ' candidate_id와 출처 항목 불일치.'
    elif item['origin'] == 'web' and item['mode'] == 'original' and not all([src.get('bank_question_found'), src.get('bank_stems_match'), src.get('bank_options_match')]):
        item['status'] = 'fail'
    elif item['origin'] == 'web' and item['mode'] == 'variant' and not src.get('bank_question_found'):
        item['status'] = 'fail'
    elif item['origin'] == 'past' and item['mode'] == 'original' and not src.get('current_review_card_matches_pack'):
        item['status'] = 'fail'
    elif any(not r['exists'] for r in src['references']):
        item['status'] = 'fail'
    elif (item['origin'] == 'new' or item['mode'] == 'variant') and not any(r.get('anchor_found') for r in src.get('current_note_sections', [])):
        item['status'] = 'needs_note_review'
    else:
        item['status'] = 'pass'
    item['review']['status'] = item['status']
    if src['source_ref_hash_mismatch']:
        item['review']['evidence'] += ' pack.json의 일부 과거 참조 SHA와 현재 바이트 SHA 불일치; 현재 SHA를 references에 기록했고 현재 대상 절/카드 원문으로 다시 대조. 공식 source-manifest 검사는 별도 차단.'

# Additional pages read visually while checking P49 and the cross-chapter P48 basis.
extra = [REPO / '강의노트' / '5장 DNA 복제와 유전자의 발현.pdf', REPO / '교과서' / '생명과학_기초와_응용_2판' / '06장_DNA_기술과_유전체학.pdf']
for path in extra:
    add_ref(path)
for n in (14, 15, 16, 17):
    path = WORK / 'evidence' / 'source-pages' / f'textbook-ch6-p{n}.png'
    report['rendered_pages'].append({'path': str(path), 'source_pdf': str(extra[1]), 'page': n, 'sha256': sha(path), 'viewed': True})
for rec in report['rendered_pages']:
    if Path(rec['path']).name.startswith('past-'):
        rec['viewed'] = True

report['references'] = [{'path': path, 'sha256': digest} for path, digest in sorted(ref_map.items())]
stage_path = WORK / 'stage' / '문제해설_1장-6장_시험예상.html'
if stage_path.exists():
    before = BeautifulSoup(Path(report['baseline_path']).read_text(encoding='utf-8'), 'html.parser')
    stage = BeautifulSoup(stage_path.read_text(encoding='utf-8'), 'html.parser')
    differences = [item['id'] for item in report['items'] if str(before.select_one('#' + item['id'] + ' [data-source-field="conditions"]')) != str(stage.select_one('#' + item['id'] + ' [data-source-field="conditions"]'))]
    report['stage_problem_panel_comparison'] = {'path': str(stage_path), 'sha256': sha(stage_path), 'baseline_path': report['baseline_path'], 'exact_html_equal_count': 75 - len(differences), 'differences': differences}
    report['references'].append({'path': str(stage_path), 'sha256': sha(stage_path)})
report['counts'] = dict(Counter(item['status'] for item in report['items']))
report['status'] = 'pass' if report['counts'] == {'pass': 75} else 'incomplete'
report['review_scope_note'] = '원문 보존·source_refs/candidate_id·기출 PDF 실제 시각·웹과제 original JSON·변형/신규의 현재 강의자료와 정리노트 근거를 검토했다. 현재 pack source-manifest와 달라진 파일의 원인/재발행 허용 여부는 이 보고서의 pass와 별개다.'
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'status': report['status'], 'counts': report['counts'], 'refs': len(ref_map), 'pages_viewed': sum(bool(r.get('viewed')) for r in report['rendered_pages']), 'missing_note': [x['id'] for x in report['items'] if x['status'] == 'needs_note_review'], 'fail': [x['id'] for x in report['items'] if x['status'] == 'fail']}, ensure_ascii=False, indent=2))
