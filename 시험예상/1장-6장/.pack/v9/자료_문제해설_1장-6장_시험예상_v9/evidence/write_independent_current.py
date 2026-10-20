"""Blind independent re-solution record. Reads only the blinded question input."""
import hashlib
import json
import re
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parents[1]
INPUT = WORK / "blind-current-questions.json"
OUTPUT = WORK / "evidence/independent-current.json"

LECTURES = {
    n: next((ROOT / "강의노트").glob(f"{n}장*.pdf")) for n in range(1, 7)
}
NOTES = {
    "0903": next((ROOT / "복습노트/0903").glob("정리노트_*.html")),
    "0917": next((ROOT / "복습노트/0917").glob("정리노트_*.html")),
    "0922": next((ROOT / "복습노트/0922").glob("정리노트_*.html")),
    "1008": next((ROOT / "복습노트/1008").glob("정리노트_*.html")),
    "1013": next((ROOT / "복습노트/1013").glob("정리노트_*.html")),
    "1015": next((ROOT / "복습노트/1015").glob("정리노트_*.html")),
}
SVG = ROOT / "웹과제/1장/image/q09.svg"

# id, answer, method, rationale, material location, ambiguity
ROWS = """
p1|A|qualitative|한 지역의 같은 종 개체가 모인 단위가 개체군이다.|L1:1| 
p2|A|qualitative|원자번호는 원자핵의 양성자 수이다. 전자 수는 중성 원자에서만 그 수와 같다.|L1:1| 
p3|C|qualitative|방추사와 소기관 이동에는 주로 미세소관이 관여한다. 미세섬유는 액틴 성분이다.|L1:5-6| 
p4|C|qualitative|원본 그림의 두 분자 모두 중심 탄소에 H₃N⁺, COO⁻, H와 서로 다른 R기를 지닌 아미노산이다. 아미노산 중합체는 폴리펩티드·단백질이다.|L1:3;N0903:s5-amino-acid;SVG:q09.svg| 
p5|B|qualitative|땀의 증발에 의한 냉각은 물의 높은 기화열에 의존한다. 작은 기화열이라는 진술이 반대다.|L1:2| 
p6|E|qualitative|리보솜은 막으로 둘러싸인 내막계 구획이 아니다. 소포체·골지체·소낭과 원형질막은 내막계에 포함된다.|L1:5| 
p7|B|qualitative|친수성 인산기 머리는 양쪽 물에 닿고 소수성 지방산 꼬리는 이중층 내부로 향한다.|L1:3,6| 
p8|D|qualitative|핵막이 없고 DNA가 핵양체에 놓인 세포는 원핵세포이며 리보솜은 원핵세포에도 있다.|L1:5| 
p9|D|exact|정육면체의 표면적/부피는 6a²/a³=6/a. A는 6, B는 3이므로 2배다.|L1:4| 
p10|E|qualitative|녹말과 섬유소 모두 포도당 중합체다. 기본 단위를 아미노산·지방산이라고 한 E가 틀리다.|L1:2-3| 
p11|B|qualitative|효소는 촉매로서 반응 뒤 변하지 않아 반복 사용된다.|L2:1| 
p12|D|qualitative|세포호흡의 시트르산 회로는 아세틸기를 CO₂로 산화한다. 광의존반응은 광합성 과정이다.|L2:2| 
p13|D|qualitative|NADP⁺는 광의존반응에서 마지막 전자수용체이며 전자를 받아 NADPH가 된다.|L2:4-5| 
p14|C|exact|한 회전에 CO₂ 한 분자가 고정되고 포도당에는 탄소 여섯 개가 있으므로 여섯 회전이 필요하다.|L2:5| 
p15|E|exact|발효는 NAD⁺를 재생해 해당과정을 지속시킨다. 포도당 한 분자의 순 ATP 수지는 해당과정의 2개다.|L2:2-3| 
p16|A|qualitative|지방 탄소는 평균적으로 더 환원되어 있어 단위 질량을 산화할 때 더 많은 전자와 에너지를 제공한다.|L1:3;L2:2| 
p17|B|qualitative|H⁺가 ATP 합성효소를 우회해 새면 막을 가로지르는 기울기가 줄어 산화적 인산화의 ATP 합성이 감소한다.|L2:3| 
p18|A|qualitative|기공 폐쇄로 CO₂가 낮고 O₂가 높으면 루비스코가 RuBP에 O₂를 붙이는 산소화 반응의 상대 비율이 높아진다.|L2:5| 
p19|C|qualitative|틸라코이드막의 광의존반응에서 물이 분해되고 스트로마의 캘빈회로에서 CO₂가 고정된다.|L2:4-5| 
p20|B|qualitative|동원체는 복제된 자매염색분체가 연결된 염색체의 지역이다.|L3:1-2| 
p21|C|qualitative|암세포가 원래 종양을 떠나 다른 부위로 퍼져 새 종양을 형성하는 과정은 전이다.|L3:3| 
p22|E|exact|G₂의 DNA 100은 복제 후 4C에 해당한다. 감수 I 뒤 각 세포는 복제된 염색체를 절반만 받아 중기 II에서 2C, 즉 50이다.|L3:1,4|한 세포당 DNA 양으로 읽는다.
p23|D|qualitative|p53은 DNA 손상 시 세포주기를 멈추고 수선 또는 세포사멸을 촉진하는 종양 억제 단백질이다.|L3:2-3;N0917:s5-suppressor| 
p24|E|qualitative|G₁은 DNA 복제 이전의 세포 성장기이고 DNA 복제는 S기에 일어난다.|L3:1| 
p25|B|exact|2n=8이면 독립 분배되는 상동염색체 쌍은 n=4쌍이다. 교차·돌연변이 없이 가능한 조합은 2⁴=16종류다.|L3:4-5| 
p26|C|qualitative|유사분열 후기에는 자매염색분체, 감수 I 후기에는 상동염색체가 서로 분리된다.|L3:2,4| 
p27|E|qualitative|그림은 (가) 2C 일정, (나) 2C→4C, (다) 4C 일정이다. G₂에서 다시 8C로 복제하지 않고 M기에 들어간다.|L3:1-2| 
p28|A|qualitative|감수 I 전기에 접합한 상동염색체의 비자매염색분체가 대응 절편을 교환하면 새로운 대립유전자 조합이 생긴다.|L3:4| 
p29|B|qualitative|단일 유전자의 변화가 출혈·멍·관절 통증 등 여러 형질과 증상에 영향을 주므로 다면발현이다.|L4:4| 
p30|C|qualitative|유전자는 염색체 DNA의 특정 좌위에 있고 한 염색체에는 많은 유전자가 존재한다.|L4:3| 
p31|B|exact|남자 아이는 아버지에게 Y, 보인자 어머니에게 정상 X 또는 색맹 X를 각각 1/2로 받으므로 조건부 확률은 50%다.|L4:6|이미 남자 아이로 조건화된 확률이다.
p32|E|qualitative|암컷 포유류가 X 염색체 하나를 불활성화해 X 연관 유전자 발현량을 맞추는 현상이 유전자 정량 보정이다.|L4:6| 
p33|D|qualitative|전좌는 보통 비상동염색체 사이의 절편 이동 또는 교환이다. 상동염색체 사이에서만이라는 제한이 틀리다.|L4:7| 
p34|C|exact|Iᴬi×Iᴮi에서 두 부모가 각각 i를 줄 확률이 1/2이므로 ii의 확률은 1/4이다.|L4:4| 
p35|B|exact|pp와 교배해 보라:흰이 1:1이면 보라 부모가 P와 p 배우자를 같은 비율로 내는 Pp이다.|L4:1-2| 
p36|A|qualitative|가까이 연관된 두 좌위 사이에 교차가 드물면 부모형 대립유전자 조합이 재조합형보다 자주 전달된다.|L4:4-5| 
p37|C|exact|Rr×Rr의 유전자형 RR:Rr:rr=1:2:1이고 불완전우성에서 각각 빨강:분홍:흰에 대응한다.|L4:3| 
p38|E|qualitative|복제 중 DNA 중합효소의 3′→5′ 핵산가수분해효소 작용이 새로 잘못 넣은 뉴클레오타이드를 제거한다.|L5:2| 
p39|A|qualitative|넌센스 돌연변이는 아미노산 지정 코돈을 종결 코돈으로 바꾸어 번역을 조기에 끝낸다.|L5:6| 
p40|D|exact|3′-TAC CGA GTT ACT-5′ 주형에 역평행·상보적인 RNA는 5′-AUG GCU CAA UGA-3′이다.|L5:3-4| 
p41|B|qualitative|선택적 이어맞추기로 한 pre-mRNA에서 엑손 조합이 다른 여러 성숙 mRNA를 만들 수 있다.|L5:4,8| 
p42|B|qualitative|tRNA는 아미노산을 리보솜으로 운반하며 안티코돈으로 mRNA 코돈과 짝짓는다.|L5:5-6| 
p43|B|qualitative|전사 속도가 같을 때 축적량을 늘린 더 긴 mRNA 수명은 분해속도 감소로 가장 직접 설명된다.|L5:8| 
p44|D|qualitative|두 새 가닥 모두 5′→3′로 합성되므로 복제분기점 진행과 반대 방향인 지체가닥은 짧은 오카자키 절편을 반복 합성한다.|L5:2| 
p45|A|qualitative|억제자가 작동자에 결합하지 못하면 젖당이 없어도 그 억제자에 의한 전사 차단은 풀린다.|L5:6-7|다른 조절은 문제에서 제외했다.
p46|B|exact|AUG·GAA·UGG가 각각 아미노산 하나를 지정하고 UAA는 종결이므로 3개다.|L5:3| 
p47|B|exact|어머니 8·10과 자녀 10·12를 비교하면 자녀의 12는 부계에서 와야 한다. 12를 가진 후보 B만 배제할 수 없다.|L6:2|단일 좌위로 친부를 확정하는 것은 아니다.
p48|E|qualitative|점착성 말단의 염기쌍이 붙은 뒤 당-인산 골격의 공유결합을 완성하는 것은 DNA 연결효소다.|L6:1;N1008:s5-ligation| 
p49|D|qualitative|유전체에는 단백질 암호화 엑손뿐 아니라 인트론과 비암호화 DNA도 있으므로 전체가 엑손이라는 D가 틀리다.|L6:5;N1015:s1-genome| 
p50|C|qualitative|열순환 PCR 한 주기는 변성으로 두 가닥 분리, 프라이머 결합, 중합효소 신장의 순서다.|L6:1-2;N1013:s0-pcr-cycle| 
p51|A|qualitative|DNA는 음전하라 양극으로 움직이고, 같은 겔에서 작은 200 bp 조각이 800 bp보다 더 멀리 이동한다.|L6:2| 
p52|B|qualitative|가이드 RNA가 표적 DNA와 상보적으로 짝을 지어 위치를 안내하고 Cas9이 DNA를 절단한다.|L6:6| 
p53|D|qualitative|체세포 핵 A가 핵 DNA를, 핵을 제거한 난자 B가 미토콘드리아 DNA를 제공한다. C는 자궁 제공자다.|L6:3-4;N1013:s4-clone| 
p54|D|qualitative|세균에 외래 DNA를 운반하고 복제시키는 대표 클로닝 벡터는 플라스미드다.|L6:1| 
p55|C|qualitative|목적에 따라 유전자를 인위적으로 조작하는 기술 분야는 유전공학이다.|L6:1| 
p56|뉴클레오타이드|qualitative|질소 염기+5탄당의 뉴클레오사이드에 인산기가 붙으면 뉴클레오타이드다.|L1:4| 
p57|수소결합|qualitative|DNA 두 가닥 사이의 상보적 염기쌍은 수소결합으로 연결된다.|L1:4| 
p58|안쪽|qualitative|물에서 접힌 구형 단백질은 비극성 곁사슬을 물을 피하는 내부에 주로 묻는다.|N0903:s5-structure| 
p59|비타민|qualitative|금속 이온은 무기 보조인자이고 여러 조효소의 유기 전구체는 비타민이다.|L2:1| 
p60|산화|qualitative|산화의 정의는 물질이 전자를 잃는 것이다.|L2:2| 
p61|40|exact|활성화에너지는 원래 100−20=80, 효소 존재 시 60−20=40이므로 낮춘 크기는 40이다.|L2:1| 
p62|2|exact|해당과정은 탄소 6개 포도당 한 분자를 탄소 3개 피루브산 두 분자로 분해한다.|L2:2| 
p63|전기|qualitative|염색체 응축은 유사분열 전기에 시작하고 중기에 적도판 정렬이 일어난다.|L3:2| 
p64|없다|qualitative|감수분열에 앞서 DNA가 한 번 복제된 뒤 I과 II 사이에는 다시 복제되지 않는다.|L3:1,4| 
p65|3|exact|2n=6의 상동염색체 3쌍이 감수분열로 분리되므로 각 최종 딸세포는 n=3개다.|L3:3-4| 
p66|사이클린|qualitative|주기적으로 농도가 변하며 CDK에 결합해 활성을 조절하는 단백질은 사이클린이다.|L3:2| 
p67|다인자유전|qualitative|여러 유전자가 하나의 피부색 형질에 기여하는 유전 양식은 다인자유전이다.|L4:4| 
p68|2n+1|exact|(n+1) 배우자와 n 배우자가 합쳐지면 접합자 염색체 수는 2n+1이다.|L4:7| 
p69|1/4|exact|AaBb가 ab 배우자를 낼 확률은 독립분리로 1/2×1/2=1/4이고 aabb는 ab만 낸다.|L4:2-3| 
p70|침묵 돌연변이|qualitative|코돈이 바뀌어도 유전암호의 중복성으로 아미노산이 그대로인 치환은 침묵 돌연변이다.|L5:6| 
p71|프로테아좀|qualitative|유비퀴틴은 분해 표지이고 이를 인식해 짧은 수명 단백질을 분해하는 복합체는 프로테아좀이다.|L5:9;N1008:s3-proteasome| 
p72|22|exact|이중가닥 DNA에서 A=T=28%이면 G+C=44%, G=C이므로 G=22%다.|L5:1| 
p73|3|qualitative|수업의 사람 반수체 유전체 한 세트는 대략 30억 염기쌍이므로 십억 단위 숫자는 3이다.|L6:5;N1015:s1-genome|상세 근삿값 32억을 쓰면 3.2이나 문항은 '대략 몇 십억'을 요구한다.
p74|메틸화|qualitative|세균은 자기 DNA의 제한효소 인식 부위를 메틸화해 절단되지 않도록 보호한다.|L6:1| 
p75|128|exact|전체 이중가닥 분자 수는 초기 2×2⁶=128이다. 정확한 길이의 표적 산물만 세는 계산은 아니다.|N1013:s0-pcr-cycle| 
""".strip().splitlines()

locations = {}
for n, path in LECTURES.items():
    locations[f"L{n}"] = path
for date, path in NOTES.items():
    locations[f"N{date}"] = path
locations["SVG"] = SVG

questions = json.loads(INPUT.read_text(encoding="utf-8"))
assert [q["id"] for q in questions] == [f"p{i}" for i in range(1, 76)]
items = []
for row in ROWS:
    parts = [part.strip() for part in row.split("|")]
    assert len(parts) == 6, row
    qid, answer, method, rationale, location, ambiguity = parts
    q = questions[int(qid[1:]) - 1]
    assert q["id"] == qid
    if q["format"] == "mcq":
        assert answer in [option["id"] for option in q["options"]]
    elif q["format"] == "short":
        assert answer
    for ref in location.split(";"):
        assert ref.split(":")[0] in locations
    items.append({
        "id": qid,
        "answer": answer,
        "method": method,
        "rationale": rationale,
        "source_locations": location.split(";"),
        "ambiguity": ambiguity or None,
    })

used_codes = set()
for item in items:
    used_codes.update(loc.split(":")[0] for loc in item["source_locations"])
refs = []
for code in sorted(used_codes):
    path = locations[code]
    refs.append({
        "code": code,
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    })

result = {
    "reviewer": "정답 비공개 독립 재풀이 에이전트",
    "scope": "현재 blind-current-questions.json의 p1–p75",
    "visual_checks": {
        "p4": "웹과제/1장/image/q09.svg를 PDF 렌더러로 열어 두 아미노산의 공통 골격과 R기를 직접 확인함",
        "p27": "문제 입력의 SVG를 렌더링해 (가) 2C, (나) 2C→4C, (다) 4C를 직접 확인함",
    },
    "question_input": {
        "path": str(INPUT.resolve()),
        "sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
    },
    "references": refs,
    "items": items,
}
for item in items:
    for loc in item["source_locations"]:
        code, specific = loc.split(":", 1)
        path = locations[code]
        if code.startswith("L"):
            pages = []
            for part in specific.split(","):
                pages.extend(int(value) for value in part.split("-"))
            assert all(1 <= page <= len(pymupdf.open(path)) for page in pages), loc
        elif code.startswith("N"):
            assert re.search(r'id=["\']' + re.escape(specific) + r'["\']', path.read_text(encoding="utf-8")), loc
        else:
            assert specific == path.name, loc
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
print("items", len(items), "references", len(refs))
