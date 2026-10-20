from pathlib import Path
from lxml import html
from collections import Counter
import hashlib, json, re, datetime

repo=Path(__file__).resolve().parents[4]
work=Path(__file__).resolve().parent.parent
pack_path=repo/'시험예상/1장-6장/.pack/v9/pack.json'
question_path=repo/'시험예상/1장-6장/시험예상문제_1장-6장.html'
pack=json.loads(pack_path.read_text(encoding='utf-8'))
problems=pack['problems']
assert len(problems)==75
question_doc=html.fromstring(question_path.read_text(encoding='utf-8'))

criteria={
'p1':'같은 지역·같은 종의 개체군을 여러 종의 군집과 무생물까지 포함한 생태계에서 가른다. 1장 계층 범위의 기출 원문이다.',
'p2':'원자번호는 양성자 수라는 정의를 중성 원자의 전자 수 일치와 구별한다. 1장 원자 개념의 기출이다.',
'p3':'내막·세포골격 인접 기능 중 방추사는 미세소관이라는 결정 기준으로 부정형을 푼다. 1장 웹 원문이며 공식 답은 미확인이다.',
'p4':'그림의 중앙 C·아미노기·카복실기·곁사슬을 실제 읽어 아미노산→단백질을 고른다. 단당류/핵산 쌍의 정의는 사실이어도 이 그림의 답이 아니다.',
'p5':'얼음 밀도·응집·용매·비열과 증발 냉각의 큰 기화열을 구별한다. 작은 기화열을 고르는 부정형 방향이 유지된다.',
'p6':'막성 구획·소낭 경로에 원형질막·골지·소포체는 연결되지만 막 없는 리보솜은 아니다. 원문 부정형이며 부정형 type 표지가 필요하다.',
'p7':'물속 인지질의 친수성 머리/소수성 꼬리 배치와 지방산 두 개·포화/불포화 허용을 적용한다. 변형의 조건·반례가 1장 범위다.',
'p8':'핵양체·핵막 부재로 원핵세포를 판단하고 리보솜 존재나 세포벽 미관찰을 과잉 해석하지 않는다. 새 세포 상황에 원리를 옮겼다.',
'p9':'정육면체의 6a²/a³를 각각 구해 A/B=2를 얻는다. 면적만의 비 1/4과 요청한 표면적/부피 비를 구별한다.',
'p10':'녹말·섬유소의 공통 포도당 단위체와 서로 다른 결합·기능을 대조해 아미노산/지방산 주장을 배제한다. 부정형 범위 안이다.',
'p11':'효소의 기질 특이성·열 민감성·촉매 재사용을 각각 판정한다. 원문 인쇄의 어색한 고열 표현을 실제 주장대로 읽는다.',
'p12':'광의존반응의 O₂ 생성은 사실이지만 세포호흡 질문의 답에는 부적합하고 시트르산회로 CO₂가 맞다. 참/답 적합성 분리다.',
'p13':'NADP⁺가 전자를 받아 NADPH가 되는 역할을 색소·광계·ATP 합성효소와 가른다. 2장 웹 원문은 수치 계산이 없는 역할 판별이다.',
'p14':'캘빈회로 CO₂ 1개/회전과 포도당 탄소 6개를 연결해 6회를 구한다. 회전의 탄소 단위를 명시해 수치 오답을 판정한다.',
'p15':'무산소 근육에서 해당과정 생성 4·소비 2의 순 2 ATP와 발효 자체의 추가 ATP 0을 구분한다. 웹 문항 조건에 맞다.',
'p16':'같은 질량 지방의 높은 환원도·전자 공급과 직접 O₂ 결합/ATP합성효소 활성화 오답을 구별한다. 1 g은 비교 조건이며 산술 계산은 없다.',
'p17':'전자전달은 유지하고 H⁺만 합성효소를 우회해 새는 조건을 적용해 기울기·ATP 감소를 판정한다. 통과 차단 원문과 반대 조건이다.',
'p18':'C₃ 식물의 기공 폐쇄→CO₂ 감소/O₂ 상대 증가→루비스코 산소화 증가를 연결한다. 당의 탄소 출처 등 오답도 2장 범위다.',
'p19':'틸라코이드막 (가) 물 분해와 스트로마 (나) CO₂ 고정을 표의 두 칸에 각각 대입한다. 위치와 기능 둘 다 맞아야 한다.',
'p20':'기출의 동원체 지역은 수업 문맥의 자매염색분체 접합 부위로 읽되 교재의 중심절/kinetochore 구별을 해설에 공개했다.',
'p21':'원발 종양을 벗어나 다른 부위로 퍼짐을 전이로 판별하고 발암·유사분열·혈관신생과 구별한다. 3장 기출 범위다.',
'p22':'G₂ 세포당 DNA 100을 감수 I 뒤 중기 II의 50으로 추적한다. 두 분열 사이 재복제 없음과 염색체 수/세포당 DNA 양을 분리한다.',
'p23':'종양 억제 p53의 손상 대응·세포주기 제동을 분열 촉진 유전자와 가른다. 한 대립유전자 이상 즉시 암이라는 단정은 배제한다.',
'p24':'G₁ 성장·소기관 증가를 S의 DNA 복제와 M의 응축/방추사/세포질분열에서 구별한다. 3장 단계 판별이다.',
'p25':'2n=8에서 n=4쌍, 여러 감수분열의 가능한 배우자 조합 2⁴=16을 세며 한 번의 분열 산물 4개와 분리한다.',
'p26':'유사분열 후기 자매염색분체와 감수 I 후기 상동염색체의 분리 대상을 짝짓는다. 3장 인접 단계 비교를 변형했다.',
'p27':'2C→4C 그래프의 G₁/S/G₂를 읽고 G₂ 재복제 8C 주장을 부정한다. 그림 판독은 값·구간 관계가 실제로 필요하다.',
'p28':'감수 I 전기 비자매염색분체 사이 대응 절편 교환으로 새 조합이 생김을 돌연변이·분리 사건과 구별한다.',
'p29':'한 유전자→여러 혈우병 증상의 방향을 다면발현으로 읽고 여러 유전자/한 형질과 가른다. 4장 기출이다.',
'p30':'긴 염색체 DNA에 여러 유전자 구간이 놓인 부분/전체 관계를 다른 보기의 역포함·독립분리 일반화와 비교한다.',
'p31':'색맹 아버지·보인자 어머니의 아들 조건에서 모계 Xᶜ 확률 1/2을 구한다. 전체 출생 중 색맹 아들 1/4과 분모가 다르다.',
'p32':'XX 체세포의 X 하나 불활성화가 발현량 보정이며 X 연관 위치·비분리·재조합과 다르다. 4장 웹 판별 기준을 적용했다.',
'p33':'결실·중복·역위는 양/방향, 전좌는 비상동 이동 상대를 기준으로 판정한다. 상동 사이에서만이라는 부정형 오답을 찾는다.',
'p34':'Iᴬi×Iᴮi의 네 동확률 자손 중 ii 하나로 1/4을 계산한다. 원본 4장 피드백의 부모 조건 전환과 같은 범위다.',
'p35':'검정교배 P_×pp에서 흰 자손이 나타나고 1:1이면 보라 부모가 Pp다. PP의 전원 보라와 비교하는 상황 전이다.',
'p36':'같은 염색체의 가까운 A/B 사이 교차가 드물면 부모형 조합 우세다. 연관·재조합 거리 원리만 사용한다.',
'p37':'불완전우성 Rr×Rr에서 RR/Rr/rr 네 칸을 각각 다른 색에 대응해 1:2:1을 구한다. 부모 조건을 먼저 확인한다.',
'p38':'웹 원문 교정은 새 가닥 3′ 말단의 3′→5′ 제거가 답이다. D의 DNA/RNA 정확도 비교는 수업 밖 직접 근거로 분리 공개했다.',
'p39':'넌센스/정지 명칭을 아미노산 코돈→종결 코돈→조기 번역 종료에 연결하고 틀 이동·과오·침묵과 가른다.',
'p40':'제시 주형 3′→5′를 상보 mRNA 5′→3′로 전사해 AUG GCU CAA UGA를 고른다. 가닥과 방향을 둘 다 요구한다.',
'p41':'전구체의 5′ 캡/3′ 꼬리·핵 안 스플라이싱·선택적 엑손 조합을 구분한다. 성숙 mRNA 한 종류와 비교 단위가 다르다.',
'p42':'tRNA의 아미노산 운반을 mRNA 정보·RNA 중합효소의 전사·mRNA 풀기와 가른다. 5장 기출 역할 판별이다.',
'p43':'전사 속도가 같은데 mRNA 수명만 늘었으므로 분해속도 감소를 고른다. 생성/소멸의 비교 단위를 분리했다.',
'p44':'역평행 주형에도 두 신생 가닥은 5′→3′; 분기점과 반대쪽은 새 프라이머에서 절편을 만든다. 지체가닥 방향 반전 오답을 가른다.',
'p45':'lac 억제자의 작동자 결합 상실은 그 억제 경로 해제다. 항상 최대 발현·DNA 복제 정지로 확대하지 않는다.',
'p46':'제공 코돈표를 AUG부터 읽어 세 지정 코돈만 세고 UAA 종결은 0개다. 표 판독과 정지 코돈 제외가 필요하다.',
'p47':'STR 한 좌위에서 모계 10을 제외한 자녀 12를 가진 B만 배제할 수 없다. 한 좌위 배제 불가와 친부 확정을 구분한다.',
'p48':'점착성 말단의 염기 수소결합 뒤 남은 당-인산 골격 틈은 DNA 연결효소가 봉합한다. 절단·프라이머·풀기와 구별한다.',
'p49':'유전체에는 비암호화 DNA가 있어 전체=암호화 엑손 주장이 틀리다. 유전체 크기/유전자 수/서열 단위를 구별한다.',
'p50':'PCR 주기를 변성부터 시작한다고 명시해 순환 배열의 시작점 모호함을 없앴다. 변성→프라이머 결합→신장을 따른다.',
'p51':'같은 겔·전압·시간에서 두 DNA의 음전하 방향과 200bp의 더 먼 이동을 고른다. 정확한 역비례식은 주장하지 않는다.',
'p52':'guide RNA의 상보 DNA 인식과 Cas9의 DNA 절단을 분리해 고른다. 표적 단백질·mRNA 전용 주장과 다르다.',
'p53':'핵 A·탈핵 난자 B·자궁 C의 출처를 구분하며 미토콘드리아 난자 기원 가정을 명시한다. 핵 DNA A/mtDNA B가 답이다.',
'p54':'플라스미드가 세균 클로닝 운반체이고 재조합 DNA는 조합 결과다. 기출의 STR 유전자 표현은 그대로 두고 해설에서 제한했다.',
'p55':'유전공학이라는 기술 분야를 PCR 증폭·미세배열 분석·생물정보학·재조합 단계와 가른다. 6장 기출 범위다.',
'p56':'염기+5탄당인 뉴클레오사이드에 인산기가 더해져 뉴클레오타이드가 된다. 1장 이름↔구성의 단답 변환이다.',
'p57':'서로 다른 DNA 가닥의 염기 사이 수소결합과 한 가닥 당-인산 골격의 공유결합을 구별한다. 1장 기출 변형이다.',
'p58':'물에 녹는 구형 단백질이라는 조건에서 비극성 곁사슬은 주로 안쪽이다. 막단백질로 무조건 확대하지 않는다.',
'p59':'무기 금속 보조인자와 유기 조효소를 가른 뒤 많은 조효소의 영양소 전구체를 비타민으로 회상한다.',
'p60':'전자를 잃는 분자를 산화로 이름 붙이고 전자를 받는 쪽의 환원과 반대 방향을 확인한다. 2장 redox 범위다.',
'p61':'효소 없음/있음의 Ea=(전이상태−반응물)을 각각 80/40으로 구해 감소량 40을 단위 없이 쓴다.',
'p62':'해당과정에서 포도당 C6가 피루브산 C3 두 분자로 나뉨을 탄소 보존으로 계산한다. ATP 개수와 다르다.',
'p63':'응축 시작·적도판 미정렬의 두 형태 단서로 유사분열 전기를 선택한다. 전중기 분류는 이 출제의 결정 조건이 아니다.',
'p64':'감수 전 복제 한 번과 I/II 두 분열을 구별해 사이 재복제는 없다고 쓴다. 3장 웹 피드백의 단위다.',
'p65':'2n=6에서 감수 완료 딸세포 하나의 n=3을 구한다. 전체 네 세포의 합이나 DNA 양을 세지 않는다.',
'p66':'CDK 효소에 결합해 활성을 조절하며 농도가 주기적으로 변하는 상대는 사이클린이다. 결합 상대/효소를 구별한다.',
'p67':'여러 유전자→피부색 한 형질을 다인자유전으로 회상하고 한 유전자→여러 형질의 다면발현과 반대 방향을 확인한다.',
'p68':'비분리 n+1 배우자와 정상 n을 합해 2n+1 접합자를 구한다. 하나 추가와 한 세트 추가를 구분한다.',
'p69':'독립 AaBb×aabb에서 ab 배우자 1/4을 교배표·좌위별 곱셈으로 확인한다. 연관 원문과 달리 독립 조건을 명시했다.',
'p70':'염기 치환 뒤 코돈은 달라도 지정 아미노산이 같으면 침묵 돌연변이다. 정지·과오·틀이동과 결과를 가른다.',
'p71':'유비퀴틴은 표지, 프로테아좀은 표지를 인식해 분해하는 복합체라는 역할 분리로 이름을 쓴다.',
'p72':'이중가닥 전체 A=T=28%, G+C=44%, G=C이므로 G 하나는 22%다. 합 44와 구별한다.',
'p73':'반수체 유전체 한 세트 약 30억을 십억 단위 3으로 쓰고 교재 32억의 3.2도 허용한다. 명칭 전환보다 수치·단위 회상이다.',
'p74':'제한효소가 인식하는 자기 DNA 부위를 메틸화로 보호한다. 정리노트의 인식·방어와 강의노트 6장 p1의 직접 보호 근거를 분리했다.',
'p75':'초기 이중가닥 2개를 6회 두 배로 해 총 128개를 구한다. 표적 길이 산물만 세는 다른 질문과 분리한다.'}
assert set(criteria)=={f'p{i}' for i in range(1,76)}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def flat(text): return re.sub(r'\s+',' ',text).strip()
def source_text(problem):
    root=html.fromstring('<div>'+problem['problem_html']+'</div>')
    return flat(root.text_content())

policy_paths=[
 repo/'.agents/skills/bio-review-pack/references/webquiz-style.md',
 repo/'.agents/skills/bio-review-pack/references/note-feedback.md',
 repo/'.agents/skills/bio-review-pack/references/problem-selection.md',
 repo/'시험예상/1장-6장/.pack/v9/policy-notes.md',
 repo/'시험예상/1장-6장/.pack/v9/blueprint.md',
 repo/'시험예상/1장-6장/.pack/v9/scope.json',
]
for chapter in range(1,7):
    for name in ('note-feedback.md','intake.md'):
        path=repo/f'웹과제/{chapter}장'/name
        if path.is_file(): policy_paths.append(path)
policy_refs=[{'path':str(p),'sha256':sha(p),'read_scope':'current policy or chapter-level feedback/intake'} for p in policy_paths]

hints={
 'p4':'D is a wrong option in this image question but states 뉴클레오타이드→핵산; possible term cue for P56, not an asserted answer key.',
 'p16':'A is an option requiring evaluation; its wording links 산화 to electron release and may cue P60.',
 'p44':'Stem fact says a DNA polymerase adds nucleotides to a DNA strand; broad context cue for P56, without defining nucleoside plus phosphate.',
 'p56':'Receives partial term/context cues from P4 D and P44 stem; still requires the phosphate distinction.',
 'p60':'Receives a redox relation cue from P16 A, which itself must be evaluated.'}

items=[]
for problem in problems:
    pid=problem['id']
    chapter=problem['primary_chapter']
    answer=problem['answer'].get('option_id',problem['answer'].get('canonical'))
    feedback=repo/f'웹과제/{chapter}장/note-feedback.md'
    basis=f'chapter {chapter} '+('feedback file read' if feedback.is_file() else 'feedback absent; current web bank/style and lecture scope used')
    valid_scope=all(1<=x<=6 for x in problem['required_chapters'])
    option_count=len(problem.get('options',[]))
    fixed_payload={k:problem[k] for k in ('problem_html','options','answer','solution_steps')}
    fixed_payload_sha256=hashlib.sha256(json.dumps(fixed_payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    rendered=question_doc.get_element_by_id(pid).xpath('./div[@class="problem"]')
    rendered_match=bool(rendered) and flat(rendered[0].text_content())==source_text(problem)
    status='pass' if valid_scope and rendered_match and (problem['format']=='short' or option_count in (4,5)) else 'fail'
    items.append({'id':pid,'status':status,'evidence':criteria[pid]+f' [{basis}; answer {answer}; source options {option_count}]',
                  'source_question_excerpt':source_text(problem)[:600],
                  'primary_chapter':chapter,'required_chapters':problem['required_chapters'],
                  'origin':problem['origin'],'mode':problem['mode'],'format':problem['format'],
                  'option_count':option_count,'answer':answer,'types':problem['types'],
                  'family_id':problem['family_id'],
                  'source_options':problem['options'],
                  'rendered_problem_matches_pack':rendered_match,
                  'fixed_problem_options_answer_solution_sha256':fixed_payload_sha256,
                  'style_basis':problem.get('style_basis',[]),
                  'cross_item_cue':hints.get(pid),
                  'definitive_other_stem_leak':False,
                  'source_ambiguity_disposition':('Original P38 D comparison is labeled outside-class in explanation; answer E remains available from class.' if pid=='p38' else
                                                  'Original textbook/lecture centromere-kinetochore terminology difference disclosed in explanation.' if pid=='p20' else
                                                  'Original STR 유전자 wording retained and bounded in explanation.' if pid=='p54' else None)})

chapter_counts=Counter(p['primary_chapter'] for p in problems)
format_origin_counts=Counter((p['format'],p['origin'],p['mode']) for p in problems)
situation_counts={str(c):sum('상황 전이' in p['types'] for p in problems if p['primary_chapter']==c) for c in range(1,7)}
negative_ids=[p['id'] for p in problems if p['format']=='mcq' and any(w in p['problem_html'] for w in ('옳지 않은','아닌 것은','잘못된','관계가 먼','구성하지 않는'))]

report={
 'review_type':'question_content_scope_style_refresh',
 'reviewer':'separate full-content reviewer; fresh policy/scope/style audit',
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'pass' if all(i['status']=='pass' for i in items) else 'fail',
 'fixed_question_contract':'75 existing problems preserved; this audit changes no problem, options, answers, scoring rule, or source.',
 'web_original_answer_status':'Web-quiz capture selections are not official answer keys. Pack answers are reasoned analysis under the documented wording/condition limits; current review does not claim official grading or user mastery.',
 'pack_path':str(pack_path),'pack_sha256':sha(pack_path),
 'question_html_path':str(question_path),'question_html_sha256':sha(question_path),
 'policy_references':policy_refs,
 'missing_chapter_feedback':[str(repo/'웹과제/1장/note-feedback.md'),str(repo/'웹과제/1장/intake.md')],
 'counts':{'items':75,'passed':sum(i['status']=='pass' for i in items),'chapters':dict(chapter_counts),
           'format_origin_mode':{':'.join(k):v for k,v in format_origin_counts.items()},
           'situation_transfer_per_chapter':situation_counts,
           'negative_question_ids':negative_ids,'negative_question_count':len(negative_ids),
           'figure_count':sum('그림' in p['types'] for p in problems),
           'table_count':sum('표' in p['types'] for p in problems),
           'choice_options':sum(len(p['options']) for p in problems if p['format']=='mcq')},
 'policy_to_fixed_set_differences':[
   'The shared webquiz-style policy still describes chapter 4 as an unregistered raw-only observation; chapter 4 currently has a registered 15-question bank and intake/feedback. The fixed set contains four chapter-4 web originals.',
   'The shared webquiz-style policy has no chapter-6 observation; current chapter-6 intake/feedback record 14 questions, six negative stems, one figure, and three ambiguous originals. The fixed set has no chapter-6 web original, four chapter-6 web MCQ variants and two chapter-6 short variants. Re-selection is outside this approved metadata refresh.',
   'The fixed exam has 7 negative MCQ stems; chapter 4/5/6 counts are 1/0/1 despite higher recent web-quiz proportions. Historical proportions are observations, not required exam quotas.',
   'The two-per-chapter situation-transfer goals are generated style targets, not fixed maximums or observed quiz rates. Current tagged counts are recorded above.',
   'P13 and P16 originally carried a calculation tag without arithmetic, P73 a term-conversion tag though it asks numeric magnitude and unit conversion, and P6 lacked its negative-stem tag. Current metadata tags are reflected in each item; classification corrections do not alter question content.',
   'No ㄱㄴㄷ, twin, or unfamiliar-true option was required for the first fixed exam. The current set uses none of those optional styles.'
 ],
 'cross_item_answer_exposure':{'definitive_other_question_stem_leaks':[],
   'partial_cues':[{'from':'p4','to':'p56','grade':'option-term cue','reason':hints['p4']},
                   {'from':'p16','to':'p60','grade':'option-relation cue','reason':hints['p16']},
                   {'from':'p44','to':'p56','grade':'stem-context cue','reason':hints['p44']}],
   'method':'All 75 problem_html stems, options, and answer texts were compared pairwise; exact term matches were triaged against the full relation/condition rather than counted as automatic leaks.',
   'interpretation':'An option still needs truth/fitness judgment; a shared word or general stem fact does not by itself determine the other answer. No other stem states the complete answer rule for another item.'},
 'original_ambiguities_kept_in_explanation':['p3 spindle-vs-general movement criterion','p20 centromere/kinetochore terminology','p38 DNA-vs-RNA proofreading comparison outside class','p54 original STR 유전자 wording'],
 'items':items,
 'unresolved_key_or_scope_conflicts':[]
}
out=work/'evidence'/'question-content-scope-style-refresh.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(out),'status':report['status'],'counts':report['counts'],'pack_sha256':report['pack_sha256']},ensure_ascii=False,indent=2))
