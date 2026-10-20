import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.scratch/review-deps').resolve()))
from bs4 import BeautifulSoup

ROOT = Path.cwd()
WORK = ROOT / '.scratch/exam1-revision-20261020/work'
QUESTIONS = json.loads((WORK / 'blind-questions.json').read_text(encoding='utf-8'))
CATALOG = json.loads((WORK / 'note-catalog.json').read_text(encoding='utf-8'))
NOTES = {int(Path(x['path']).parts[1]): ROOT / x['path'] for x in CATALOG}

# Each conclusion was derived from the blind question and the cited class material.
# Fields: id | answer | method | note date:anchor | rationale | ambiguity.
RAW = r'''
p1|A|qualitative|901:s2-hierarchy|같은 장소의 같은 종 개체 집합은 개체군이다. 군집은 여러 종, 생태계는 비생물 환경까지 포함한다.|
p2|A|qualitative|903:s1-atom|원자번호의 정의는 핵 안 양성자 수이다. 전자 수는 중성 원자에서만 우연히 같다.|
p3|C|qualitative|910:s1-cytoskeleton|방추사와 소기관 이동의 주된 골격은 미세소관이다. 미세섬유는 액틴 성분이므로 그 기능 짝이 틀렸다.|
p4|C|qualitative|903:s5-amino-acid|그림의 두 중심 탄소에는 아미노기·카복실기·수소와 서로 다른 곁사슬이 있다. 아미노산이 펩타이드 결합으로 중합하여 폴리펩티드·단백질이 된다.|시험 파일 기준 그림 상대경로가 없고 원본 웹과제 SVG를 확인함
p5|B|qualitative|903:s2-heat|물은 기화열이 커서 땀이 기화할 때 열을 많이 빼앗는다. ‘작은 기화열’만 반대이다.|
p6|E|qualitative|908:s3-endomembrane|리보솜은 막으로 둘러싸인 내막계 구성원이 아니다. 나머지는 막 구조이거나 내막계와 연결된다.|
p7|B|qualitative|903:s4-phospholipid|친수성 인산 머리는 물을 향하고 소수성 지방산 꼬리는 이중층 안에서 마주한다.|
p8|D|qualitative|908:s2-prokaryote|핵막 없이 핵양체에 DNA가 있고 리보솜은 있는 세포이므로 원핵세포이다.|
p9|D|exact|908:s2-cell-size|정육면체의 표면적/부피는 6a²/a³=6/a. a=1이면 6, a=2이면 3이어서 2배이다.|
p10|E|qualitative|903:s3-alpha-beta|녹말과 섬유소는 모두 포도당 중합체이고 결합 방식이 다르다. 아미노산·지방산이 단위체라는 E가 틀렸다.|
p11|B|qualitative|910:s3-enzyme|효소는 촉매로 반응 전후 소모되지 않아 재사용된다. 기질 특이성이 있고 고열은 변성을 일으킨다.|
p12|D|qualitative|910:s4-krebs|세포호흡의 시트르산 회로는 탄소를 CO₂로 방출한다. 광의존반응은 세포호흡 단계가 아니다.|
p13|D|qualitative|915:s3-electron-flow|NADP⁺는 광의존반응 말단에서 전자를 받아 NADPH가 된다. 광자 흡수·물 분해·ATP 합성의 주체가 아니다.|
p14|C|exact|915:s4-calvin|한 회전에 CO₂ 한 분자씩 고정된다. 포도당의 탄소 여섯 개를 얻으려면 여섯 회전이 필요하다.|
p15|E|exact|915:s1-fermentation|젖산 발효는 NAD⁺를 재생하여 해당과정을 계속하게 한다. 포도당당 ATP 순생산은 해당과정의 2분자이다.|
p16|A|qualitative|910:s4-redox|지방의 탄소는 포도당 탄소보다 환원도가 높아 산화될 때 더 많은 전자를 전자전달계에 보낸다. 같은 질량에서 ATP 수율이 큰 화학적 근거다.|
p17|B|qualitative|910:s5-atp-synthase|H⁺가 ATP 합성효소를 우회하면 막간 H⁺ 기울기가 소실되어 화학삼투 ATP 합성이 줄어든다.|
p18|A|qualitative|915:s4-photorespiration|기공 폐쇄로 CO₂가 줄고 O₂ 비중이 커지면 루비스코의 산소화 반응 비율이 올라 광호흡이 증가한다.|
p19|C|qualitative|915:s3-photosystem|광의존반응은 틸라코이드에서 물을 분해하고, 캘빈회로는 스트로마에서 CO₂를 고정한다.|
p20|B|qualitative|917:s2-sister-homolog|동원체는 자매염색분체가 결합한 염색체 부위이다. 중기판이나 말단은 아니다.|
p21|C|qualitative|917:s5-tumor|악성 종양 세포가 원래 위치를 떠나 다른 조직에 정착·퍼지는 현상은 전이이다.|
p22|E|exact|922:s2-two-divisions|G₂ 2배체 DNA 양 100이 감수 I 뒤 두 세포로 절반씩 나뉜다. 중기 II 각 세포는 복제 염색분체를 지녀 50이다.|
p23|D|qualitative|917:s5-suppressor|p53은 DNA 손상 시 세포주기 정지·수선 또는 세포사멸에 관여하는 종양 억제 경로이다.|
p24|E|qualitative|917:s3-phases|G₁에서는 세포 성장과 소기관 증식이 진행된다. DNA 복제는 S, 방추사·응축·세포질분열은 M이다.|
p25|B|exact|922:s3-assortment|2n=8이면 n=4쌍이다. 교차가 없을 때 독립 배열 조합은 2⁴=16종이다.|
p26|C|qualitative|922:s2-two-divisions|유사분열 후기에는 자매염색분체, 감수 I 후기에는 상동염색체가 분리된다.|
p27|E|qualitative|917:s3-phases|간기의 G₁은 2C, S에서 4C로 복제, G₂에서 4C 유지이다. G₂에서 다시 8C가 되는 주장은 틀렸다.|
p28|A|qualitative|922:s3-crossover|감수 I 전기 접합된 상동염색체의 비자매염색분체가 대응 절편을 교환하여 재조합을 만든다.|
p29|B|qualitative|929:s1-many|하나의 혈우병 관련 유전자 변화가 출혈·멍·빈혈 등 여러 표현형에 영향을 주는 것은 다면발현이다.|
p30|C|qualitative|929:s0-locus|염색체는 DNA와 단백질로 구성되고 DNA 위에 많은 유전자 좌위가 있다.|
p31|B|exact|929:s3-carrier|아들은 아버지에게 Y를 받고 보인자 어머니의 두 X 중 하나를 받는다. 색맹 X가 전달될 확률은 1/2이다.|
p32|E|qualitative|929:s3-inactivation|암컷 포유류에서 두 X 중 하나를 불활성화하여 X 연결 유전자 발현량을 맞춘다.|
p33|D|qualitative|929:s4-structural|전좌는 주로 비상동염색체 사이 절편 이동·교환이다. 상동염색체 사이에서만 일어난다는 D가 틀렸다.|
p34|C|exact|929:s1-abo|Iᴬi×Iᴮi의 배우자는 Iᴬ/i와 Iᴮ/i가 각각 반반이다. ii 조합은 1/2×1/2=1/4이다.|
p35|B|exact|929:s0-independent|pp와 검정교배에서 Pp는 Pp:pp=1:1, PP는 모두 보라색이다. 관측 1:1은 Pp를 가리킨다.|
p36|A|qualitative|929:s2-morgan|가까운 두 좌위의 교차 확률이 낮으면 연관된 부모형 대립유전자 조합이 함께 전달되기 쉽다.|
p37|C|exact|929:s1-incomplete|Rr×Rr는 RR:Rr:rr=1:2:1이고 불완전우성으로 빨강:분홍:흰색도 1:2:1이다.|
p38|E|qualitative|1001:s6-proofreading|DNA 중합효소의 교정은 잘못 붙인 염기를 3′→5′ 엑소뉴클레아제 방향으로 제거한다.|
p39|A|qualitative|1006:s4-substitution|넌센스 치환은 아미노산 지정 코돈을 종결 코돈으로 바꿔 번역을 일찍 멈춘다.|
p40|D|exact|1006:s1-transcription|3′-TAC CGA GTT ACT-5′ 주형에 상보·역평행 RNA를 쓰면 5′-AUG GCU CAA UGA-3′이다.|
p41|B|qualitative|1006:s1-processing|선택적 이어맞추기는 같은 pre-mRNA의 엑손을 다른 조합으로 연결하여 서로 다른 mRNA를 만든다.|
p42|B|qualitative|1006:s3-trna|tRNA는 안티코돈으로 mRNA 코돈을 읽고 해당 아미노산을 리보솜으로 운반한다.|
p43|B|qualitative|1008:s2-splicing|전사 속도가 같을 때 mRNA 축적량 증가의 직접 원인은 분해 속도 감소, 곧 mRNA 수명 조절이다.|
p44|D|qualitative|1001:s5-strands|DNA 중합효소는 둘 다 5′→3′로만 연장한다. 분기점 진행과 반대쪽 주형에서는 오카자키 절편이 이어진다.|
p45|A|qualitative|1006:s5-operon|작동자에 못 붙는 억제자는 젖당이 없어도 전사를 억제하지 못한다. 다른 조절은 문제에서 제외했다.|
p46|B|exact|1006:s2-start-stop|AUG·GAA·UGG는 각각 아미노산 한 개를 지정하고 UAA는 종결이다. 합계 3개이다.|
p47|B|exact|1013:s2-parentage|자녀 10,12 중 10은 어머니 8,10에서 왔으므로 부친은 12를 줘야 한다. 12가 있는 후보 B만 배제되지 않는다.|
p48|E|qualitative|1008:s5-ligation|점착성 말단의 염기쌍 형성 후 당-인산 골격의 인산다이에스터 공유결합은 DNA 연결효소가 봉합한다.|
p49|D|qualitative|1015:s1-genome|유전체에는 인트론·조절서열·유전자 사이 DNA 등이 있으며 전부 단백질 암호화 엑손은 아니다.|
p50|C|qualitative|1013:s0-pcr-cycle|PCR 한 주기는 가열 변성, 냉각 프라이머 결합, 중합효소 신장 순으로 진행한다.|
p51|A|qualitative|1013:s1-gel|DNA는 인산 골격 때문에 음전하로 (+)극으로 이동하며 작은 200 bp가 겔에서 더 멀리 이동한다.|
p52|B|qualitative|1015:s3-mechanism|가이드 RNA가 표적 DNA와 상보적으로 짝짓고 Cas9은 DNA를 절단하는 효소이다.|
p53|D|qualitative|1013:s4-clone|체세포 핵 A가 핵 DNA를, 핵 제거 난자 B가 미토콘드리아 DNA를 제공한다. 대리모 C는 핵 유전자를 주지 않는다.|
p54|D|qualitative|1008:s4-vector|세균에 외부 유전자를 실어 나르는 대표 클로닝 벡터는 자체 복제하는 플라스미드이다.|
p55|C|qualitative|1013:s5-plant|유전자를 인위적으로 조작하여 생물에 응용하는 기술의 포괄 명칭은 유전공학이다.|
p56|뉴클레오타이드|qualitative|908:s1-nucleotide|염기와 오탄당은 뉴클레오사이드이며 여기에 인산기가 붙은 핵산 단위체는 뉴클레오타이드이다.|
p57|수소결합|qualitative|908:s1-double-helix|DNA 양 가닥의 상보 염기쌍 사이에는 수소결합이 형성된다. 당-인산 골격 공유결합과 구별된다.|
p58|안쪽|qualitative|903:s5-structure|수용액에서 비극성 곁사슬은 물 접촉을 줄이기 위해 접힌 단백질 내부에 주로 묻힌다.|
p59|비타민|qualitative|910:s3-cofactor|많은 유기 조효소의 전구체가 되는 영양소 부류는 비타민이다. 금속 이온은 무기 보조인자다.|
p60|산화|qualitative|910:s4-redox|전자 상실은 산화, 전자 획득은 환원이다.|
p61|40|exact|910:s3-enzyme|효소 없을 때 활성화에너지 100−20=80, 있을 때 60−20=40 kJ/mol. 감소량은 40이다.|
p62|2|exact|910:s4-glycolysis|6탄소 포도당 한 분자가 해당과정에서 3탄소 피루브산 두 분자로 갈라진다.|
p63|전기|qualitative|922:s1-phases|염색체 응축이 시작되고 중기판 배열 전인 유사분열 초기는 전기다.|
p64|없다|qualitative|922:s2-two-divisions|감수 I 전의 S기에서 한 번 복제한 뒤 감수 I과 II 사이에는 DNA 복제가 없다.|
p65|3|exact|922:s2-two-divisions|2n=6이면 상동염색체 3쌍이므로 감수분열 후 배우자 하나의 염색체 수는 n=3이다.|
p66|사이클린|qualitative|917:s4-cyclin-cdk|단계에 따라 양이 달라져 CDK에 결합하고 활성을 조절하는 단백질은 사이클린이다.|
p67|다인자유전|qualitative|929:s1-many|피부색처럼 여러 유전자 좌위가 한 형질에 기여하는 것은 다인자유전이다. 다면발현은 반대 관계이다.|
p68|2n+1|exact|1001:s1-nondisjunction|(n+1) 배우자와 n 배우자의 수정 결과 염색체 수는 (n+1)+n=2n+1이다.|
p69|1/4|exact|929:s0-independent|AaBb는 독립분리로 AB·Ab·aB·ab를 각 1/4 만들고 aabb는 ab만 만든다. ab×ab만 aabb이므로 1/4이다.|
p70|침묵 돌연변이|qualitative|1006:s4-substitution|코돈은 달라져도 지정 아미노산이 같은 동의적 치환은 침묵 돌연변이다.|
p71|프로테아좀|qualitative|1008:s3-proteasome|유비퀴틴 표지 단백질을 인식해 분해하는 큰 복합체는 프로테아좀이다.|
p72|22|exact|1001:s3-dna-structure|이중가닥에서 A=T=28%라 A+T=56%; 남은 G+C=44%이고 G=C이므로 G=22%이다.|
p73|3|exact|1015:s1-genome|수업의 반수체 인간 유전체 한 세트는 대략 30억 염기쌍이다. 십억 단위 수는 3이다.|같은 노트의 더 자세한 근삿값 32억을 쓰면 3.2가 될 수 있으나 질문의 ‘대략 몇 십억’은 3을 지시함
p74|메틸화|qualitative|1008:s5-restriction|세균은 제한효소 인식 부위의 자기 DNA 염기를 메틸화하여 절단을 피한다. 강의노트 6장 PDF p1에서 직접 확인했다.|
p75|128|exact|1013:s0-pcr-cycle|초기 이중가닥 DNA 2개에 여섯 번 2배 증폭을 적용하면 2×2⁶=128개이다.|
'''

rows = {}
for line in RAW.strip().splitlines():
    pid, answer, method, locator, rationale, ambiguity = line.split('|')
    date, anchor = locator.split(':')
    path = NOTES[int(date)]
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    element = soup.find(id=anchor)
    if element is None:
        raise ValueError(f'{pid}: missing {path}#{anchor}')
    excerpt = element.get_text(' ', strip=True)
    rows[pid] = {
        'answer': answer,
        'method': method,
        'rationale': rationale,
        'sources': [f'{path.relative_to(ROOT).as_posix()}#{anchor}'],
        'source_excerpt': excerpt[:180],
        'ambiguity': ambiguity or None,
    }

question_ids = {q['id'] for q in QUESTIONS}
if set(rows) != question_ids or len(rows) != 75:
    raise ValueError(f'coverage: {len(rows)} of {len(question_ids)}, missing={question_ids-set(rows)}')
for q in QUESTIONS:
    row = rows[q['id']]
    if q['format'] == 'mcq' and row['answer'] not in {x['id'] for x in q['options']}:
        raise ValueError(f"{q['id']}: option absent")

image = ROOT / '웹과제/1장/image/q09.svg'
image_text = image.read_text(encoding='utf-8')
if 'H3N' not in image_text or 'COO' not in image_text:
    raise ValueError('p4 question image not confirmed')
rows['p4']['sources'].append('웹과제/1장/image/q09.svg#web-ch01-q09-exam-desc')
rows['p74']['sources'] = ['강의노트/6장 DNA 기술과 유전체학.pdf#pdf-page-1']
import fitz
lecture = fitz.open(ROOT / '강의노트/6장 DNA 기술과 유전체학.pdf')
pdf_text = lecture[0].get_text()
idx = pdf_text.find('메틸')
if idx < 0:
    raise ValueError('p74: lecture citation not confirmed')
rows['p74']['source_excerpt'] = pdf_text[max(0, idx - 80):idx + 100].replace('\n', ' ')

ref_files = {ROOT / s.split('#')[0] for row in rows.values() for s in row['sources']}
result = {
    'reviewer': '정답 비공개 독립 검산 에이전트',
    'input': 'blind-questions.json only; no key, baseline, fragments, pack, or prior review opened',
    'question_sha256': hashlib.sha256((WORK / 'blind-questions.json').read_bytes()).hexdigest(),
    'coverage': {'total': 75, 'mcq': 55, 'short': 20},
    'image_check': {'item': 'p4', 'question_relative_src': '웹과제/1장/image/q09.svg', 'exists_relative_to_exam_folder': False, 'inspected_original': '웹과제/1장/image/q09.svg'},
    'references': {str(path.relative_to(ROOT).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(ref_files)},
    'items': rows,
}
out = WORK / 'evidence/independent-full.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out, 'items=', len(rows), 'references=', len(ref_files))
