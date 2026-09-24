"""0915 complete ELI5 guide data. Rebuild with build_guide.py."""
import guide_kit as kit


SOURCES = [
    {"id": "note", "role": "note", "path": "0915.md", "label": "0915 정리노트"},
    {"id": "stt", "role": "reference", "path": "../STT/0915 생명.md", "label": "0915 실강 STT"},
    {"id": "lecture", "role": "reference", "path": "../강의노트/2장 세포호흡과 광합성.pdf", "label": "2장 강의노트"},
    {"id": "quiz2", "role": "quiz", "path": "../23, 24 소스/2강 합본.pdf", "label": "2강 합본 원문"},
]

CONCEPTS = [
    ("resp", "세포호흡의 전자·H+ 장치", ()),
    ("ferm", "발효: NAD+ 되살리기", ("resp",)),
    ("overview", "광합성 큰 지도", ("resp",)),
    ("structure", "엽록체·광계", ("overview",)),
    ("light", "빛반응", ("structure",)),
    ("calvin", "캘빈 회로", ("overview", "light")),
    ("photoresp", "광호흡과 건조 적응", ("calvin",)),
]
kit.TITLES.update({c: title for c, title, _ in CONCEPTS})

BLOCKS = [
    ("intro", 1, 14, "teaching", "제목과 시험 직전 요약", []),
    ("resp", 16, 24, "teaching", "세포호흡 전자 흐름·화학삼투", []),
    ("ferm", 26, 32, "teaching", "발효", ["2강:5", "2강:36"]),
    ("overview", 34, 40, "teaching", "광합성 개관", ["2강:31"]),
    ("structure", 42, 48, "teaching", "엽록체·색소·광계", []),
    ("light", 50, 56, "teaching", "빛반응", ["2강:4", "2강:9", "2강:17", "2강:26", "2강:32"]),
    ("calvin", 58, 64, "teaching", "캘빈 회로", ["2강:21", "2강:24", "2강:41"]),
    ("photoresp", 66, 72, "teaching", "광호흡·C4·CAM", ["2강:12", "2강:40"]),
    ("mapping", 74, 93, "question_map", "원본 문항 범위", [
        "2강:3", "2강:4", "2강:5", "2강:9", "2강:12", "2강:17", "2강:21", "2강:24",
        "2강:26", "2강:31", "2강:32", "2강:36", "2강:40", "2강:41",
    ]),
    ("c3c4", None, None, "supplement", "2강 3번의 명명 기준은 요약 노트에 없어 원문에서 보충", ["2강:3"]),
]

F = kit.F
FACTS = [
    F("i1", "intro", "contrast", "resp", "산화적 인산화에서는 전자전달계가 만든 H+ 농도기울기가 ATP 합성효소를 작동시킨다.", "전자전달계가 만든 H+ 농도기울기가 ATP 합성효소를 돌린다."),
    F("i2", "intro", "process_step", "ferm", "발효는 NAD+를 재생하여 해당과정의 순 2 ATP 생산을 유지한다.", "NADH가 유기 중간산물에 전자를 주어 NAD+를 되살리고, 해당과정의 순 2 ATP를 유지한다.", dims={"location": "세포질의 해당과정 뒤", "input": "NADH와 유기 중간산물", "output": "NAD+와 발효 산물"}),
    F("i3", "intro", "direction", "overview", "광합성에서는 물의 전자가 NADPH를 거쳐 CO2 환원에 쓰이고, ATP·NADPH가 캘빈 회로에 공급된다.", "물의 전자는 NADPH를 거쳐 CO2로 가고, 빛반응의 ATP·NADPH가 캘빈 회로의 CO2 고정에 쓰인다."),
    F("i4", "intro", "condition", "photoresp", "덥고 건조해 기공이 닫히면 CO2는 감소하고 O2는 증가해 광호흡이 늘어난다.", "덥고 건조해 기공이 닫히면 CO2는 줄고 O2는 늘어 루비스코가 O2를 쓰며 에너지가 낭비된다."),

    F("r1", "resp", "direction", "resp", "포도당의 전자는 NADH·FADH2를 거쳐 전자전달계로 들어가며, 산소가 전자와 H+를 받아 물이 된다.", "포도당에서 나온 전자는 NADH와 FADH2에 실려 전자전달계로 들어간다."),
    F("r2", "resp", "process_step", "resp", "전자 이동 에너지는 H+를 막 너머로 능동수송해 PMF를 만들고, H+가 ATP 합성효소를 지날 때 ATP가 생성된다.", "전자 이동에서 나온 에너지는 H+를 막 너머로 능동수송해 농도기울기와 전기적 기울기, 즉 양성자 구동력(PMF)을 만든다.", dims={"location": "미토콘드리아 내막", "input": "전자 이동 에너지와 H+", "output": "H+ 전기화학 기울기와 ATP"}),
    F("r3", "resp", "contrast", "resp", "기질수준 인산화는 기질이 인산기를 직접 건네고, 산화적 인산화는 H+ 기울기로 ATP를 만든다.", "해당과정과 시트르산 회로의 ATP는 기질이 인산기를 직접 건네는 기질수준 인산화다."),
    F("r4", "resp", "quantity", "resp", "강의의 ATP 장부는 포도당 1분자당 기질수준 4, 산화적 인산화 약 28, 합계 32 ATP다.", "포도당 1분자당 기질수준 인산화 4 ATP와 산화적 인산화 약 28 ATP, 합계 32 ATP로 계산한다."),
    F("r5", "resp", "condition", "resp", "산소가 없으면 NADH가 NAD+로 돌아가지 못해 해당과정이 멈추며, 발효가 NAD+를 재생해 이를 막는다.", "산소가 없으면 전자전달계 끝에서 전자를 넘길 수 없어 NADH가 NAD+로 되돌아가지 못한다."),

    F("f1", "ferm", "process_step", "ferm", "젖산 발효에서 피루브산은 NADH의 전자를 받아 젖산이 된다.", "젖산 발효에서는 피루브산이 NADH의 전자를 받아 젖산이 된다.", dims={"location": "산소 부족 세포질", "input": "피루브산과 NADH", "output": "젖산과 NAD+"}),
    F("f2", "ferm", "condition", "ferm", "젖산 발효는 산소가 부족한 동물 근육과 젖산균에서 일어나며 요구르트·김치의 신맛은 젖산과 연결된다.", "산소가 부족한 동물 근육과 젖산균에서 일어나며, 요구르트·김치의 신맛도 젖산과 연결된다."),
    F("f3", "ferm", "process_step", "ferm", "알코올 발효에서 효모는 피루브산에서 CO2를 떼고, 아세트알데하이드를 NADH로 환원해 에탄올을 만든다.", "알코올 발효에서는 효모가 피루브산에서 CO2를 떼어 아세트알데하이드를 만들고, 이것이 NADH의 전자를 받아 에탄올이 된다.", dims={"location": "효모 세포질", "input": "피루브산과 NADH", "output": "CO2, 에탄올, NAD+"}),
    F("f4", "ferm", "definition", "ferm", "발효는 포도당 분해의 유기 대사 중간산물이 전자를 받아 NAD+ 재생을 가능하게 하는 과정이다.", "포도당 분해에서 생긴 유기 대사 중간산물이 전자를 받는다는 점이다."),
    F("f5", "ferm", "contrast", "ferm", "발효는 ATP를 많이 만드는 길이 아니라 NAD+를 되살려 해당과정의 ATP 2개를 얻는 비상 경로다.", "발효는 ATP를 많이 만드는 길이 아니라 NAD+를 되살려 ATP 2개라도 얻는 비상 경로다."),

    F("o1", "overview", "contrast", "overview", "세포호흡은 전자가 포도당에서 산소로 내려가 ATP를 얻는 이화 과정이고, 광합성은 CO2를 유기물로 만들기 위해 ATP와 전자를 넣는 동화 과정이다.", "세포호흡은 포도당의 전자가 NADH를 거쳐 산소로 내려가며 ATP를 얻는 이화 과정이다."),
    F("o2", "overview", "direction", "overview", "광합성에서 CO2 환원에 필요한 전자는 NADPH가 공급한다.", "전자는 NADPH가 공급한다."),
    F("o3", "overview", "definition", "overview", "독립영양생물은 CO2로부터 유기물을 만들며, 광독립영양생물은 빛, 화학독립영양생물은 무기물 산화 에너지를 쓴다.", "CO2로부터 유기물을 스스로 만드는 생물은 독립영양생물이다."),
    F("o4", "overview", "contrast", "overview", "종속영양생물은 유기물을 얻어야 하며, 사람과 동물은 종속영양생물이다.", "사람과 동물은 유기물을 얻어야 하는 종속영양생물이다."),
    F("o5", "overview", "process_step", "overview", "빛반응은 ATP와 NADPH를 만들고, 캘빈 회로는 ATP·NADPH·CO2로 탄수화물을 만든다.", "빛반응은 빛 에너지로 ATP와 NADPH를 만들고, 광독립반응인 캘빈 회로는 ATP·NADPH·CO2를 써 탄수화물을 만든다.", dims={"location": "틸라코이드 막과 스트로마", "input": "빛 또는 ATP·NADPH·CO2", "output": "ATP·NADPH 또는 탄수화물"}),
    F("o6", "overview", "exception", "overview", "광독립반응은 빛이 직접 필요 없다는 뜻이지 ATP와 NADPH 없이 일어난다는 뜻은 아니다.", "‘광독립’은 빛이 직접 필요 없다는 뜻이지, 빛반응이 공급한 ATP와 NADPH 없이 된다는 뜻은 아니다."),

    F("s1", "structure", "structure", "structure", "스트로마는 엽록체 내막 안의 유동액이고, 틸라코이드 더미는 그라나다.", "스트로마는 내막 안의 유동액이며, 틸라코이드가 쌓인 더미는 그라나다."),
    F("s2", "structure", "structure", "structure", "빛반응의 색소·전자전달계·ATP 합성효소는 틸라코이드 막에 있고, 캘빈 회로는 스트로마에서 일어난다.", "빛반응의 색소·전자전달계·ATP 합성효소는 틸라코이드 막에 있고, 캘빈 회로는 스트로마에서 일어난다."),
    F("s3", "structure", "definition", "structure", "엽록소 a·b, 카로티노이드, 크산토필은 서로 다른 파장의 빛을 흡수하는 색소다.", "엽록소 a·b, 카로티노이드, 크산토필 같은 색소는 서로 다른 파장의 빛을 흡수한다."),
    F("s4", "structure", "direction", "structure", "엽록소가 녹색빛을 주로 반사해 식물이 녹색으로 보인다.", "엽록소가 녹색빛을 주로 반사하므로 식물이 녹색으로 보인다."),
    F("s5", "structure", "contrast", "structure", "흡수 스펙트럼은 흡수한 빛의 양, 작용 스펙트럼은 파장별 광합성 정도를 나타낸다.", "흡수 스펙트럼은 색소가 파장별로 흡수한 빛의 양이고, 작용 스펙트럼은 파장별 광합성 정도다."),
    F("s6", "structure", "structure", "structure", "광계는 안테나 복합체와 반응중심으로 이루어진다.", "광계는 많은 색소가 있는 안테나 복합체와 반응중심으로 이루어진다."),
    F("s7", "structure", "process_step", "structure", "안테나 색소의 빛 에너지는 반응중심으로 전달되고, 들뜬 전자가 전자수용체로 이동한다.", "안테나 색소가 받은 빛 에너지는 반응중심 엽록소로 전달되고, 반응중심의 들뜬 전자가 전자수용체로 이동한다.", dims={"location": "광계의 틸라코이드 막", "input": "광자 에너지", "output": "전자수용체로 이동한 들뜬 전자"}),

    F("l1", "light", "process_step", "light", "광계 II(P680)가 잃은 전자는 물의 광분해로 보충되고, 물은 전자와 H+를 내며 O2를 만든다.", "빛반응에서 광계 II의 반응중심(P680)은 빛을 받아 전자를 내보낸다.", dims={"location": "광계 II", "input": "빛과 물", "output": "들뜬 전자, H+, O2"}),
    F("l2", "light", "direction", "light", "광합성에서 방출되는 산소의 직접 기원은 CO2가 아니라 물이다.", "광합성에서 방출되는 산소의 직접 기원은 CO2가 아니라 물이다."),
    F("l3", "light", "process_step", "light", "광계 II 전자는 전자전달계를 따라 이동하며, 에너지로 H+가 틸라코이드 내강에 쌓인다.", "광계 II에서 나온 전자는 플라스토퀴논 등을 포함한 전자전달계를 따라 이동한다.", dims={"location": "틸라코이드 막과 내강", "input": "광계 II의 전자", "output": "내강의 H+ 농도기울기"}),
    F("l4", "light", "process_step", "light", "H+가 틸라코이드 내강에서 스트로마로 ATP 합성효소를 지나면 ATP가 합성되며 이를 광인산화라 한다.", "H+가 내강에서 스트로마로 ATP 합성효소를 지나갈 때 ATP가 합성된다.", dims={"location": "틸라코이드 막", "input": "내강의 H+ 기울기와 ADP·Pi", "output": "스트로마의 ATP"}),
    F("l5", "light", "process_step", "light", "광계 I의 들뜬 전자는 페레독신과 NADP+ 환원효소를 거쳐 NADP+를 NADPH로 환원한다.", "광계 I의 들뜬 전자는 페레독신을 거쳐 NADP+ 환원효소로 가고, NADP+는 전자와 H+를 받아 NADPH가 된다.", dims={"location": "광계 I 쪽 스트로마 표면", "input": "광계 I 전자, NADP+, H+", "output": "NADPH"}),
    F("l6", "light", "definition", "light", "NADP+는 빛반응의 최종 전자수용체다.", "따라서 NADP+는 빛반응의 최종 전자수용체다."),

    F("c1", "calvin", "definition", "calvin", "캘빈 회로는 스트로마에서 ATP·NADPH로 CO2를 고정해 탄수화물을 만드는 광독립반응이다.", "캘빈 회로는 스트로마에서 ATP와 NADPH를 사용해 CO2를 고정하고 탄수화물을 만드는 광독립반응이다."),
    F("c2", "calvin", "process_step", "calvin", "캘빈 회로의 첫 단계는 CO2가 5탄당 RuBP와 결합하는 탄소고정이다.", "기공을 통해 들어온 CO2가 5탄당 RuBP와 결합하는 첫 단계가 탄소고정이다.", dims={"location": "엽록체 스트로마", "input": "CO2와 RuBP", "output": "불안정 6탄소 중간체"}),
    F("c3", "calvin", "process_step", "calvin", "불안정한 6탄소 물질은 3-PGA 두 분자로 갈라지고, ATP와 NADPH를 쓰는 환원 단계를 거쳐 G3P가 된다.", "RuBP(5C)와 CO2(1C)가 결합해 생긴 불안정한 6탄소 물질은 곧 3-인산글리세르산(3-PGA) 두 분자로 갈라진다.", dims={"location": "엽록체 스트로마", "input": "3-PGA, ATP, NADPH", "output": "G3P"}),
    F("c4", "calvin", "process_step", "calvin", "G3P 일부는 당 합성에 쓰이고, 나머지는 ATP를 써 RuBP를 재생한다.", "생긴 G3P 일부는 당 합성에 쓰이고, 나머지는 ATP를 써 RuBP를 재생한다.", dims={"location": "엽록체 스트로마", "input": "G3P와 ATP", "output": "당 전구체와 재생된 RuBP"}),
    F("c5", "calvin", "quantity", "calvin", "CO2가 6번 들어오는 6회전 뒤 포도당 같은 6탄당 1분자를 만들 수 있다.", "CO2 6분자가 차례로 들어오는 6회전이 지나면 포도당 같은 6탄당 1분자를 만들 수 있다."),
    F("c6", "calvin", "condition", "calvin", "캘빈 회로의 필수 투입물은 ATP, NADPH, CO2이며 FAD는 아니다.", "캘빈 회로는 스트로마에서 ATP와 NADPH를 사용해 CO2를 고정하고 탄수화물을 만드는 광독립반응이다."),

    F("p1", "photoresp", "structure", "photoresp", "기공은 CO2가 들어오고 O2와 물이 나가는 구멍이며, 증산은 식물을 식힌다.", "기공은 CO2가 들어오고 O2와 물이 나가는 구멍이다."),
    F("p2", "photoresp", "condition", "photoresp", "매우 덥고 건조하면 물을 아끼기 위해 기공이 닫힌다.", "매우 덥고 건조하면 물을 아끼려고 기공이 닫힌다."),
    F("p3", "photoresp", "process_step", "photoresp", "기공이 닫히면 CO2는 줄고 O2는 늘어 루비스코가 O2를 기질로 써 광호흡이 증가한다.", "기공을 닫은 채 광합성이 이어지면 CO2 농도는 내려가고 O2 농도는 올라간다.", dims={"location": "잎 기공·엽록체", "input": "낮은 CO2, 높은 O2", "output": "루비스코의 산소화 반응과 광호흡"}),
    F("p4", "photoresp", "condition", "photoresp", "광호흡은 독성 물질을 처리하는 데 에너지를 써 식물 성장을 떨어뜨린다.", "독성 물질을 처리하느라 에너지를 쓰는 광호흡이 늘어 식물의 성장이 떨어진다."),
    F("p5", "photoresp", "contrast", "photoresp", "C4·CAM 식물은 CO2 농축·저장 전략으로 광호흡을 줄이며, CAM 식물은 낮 고온·건조 사막 환경에 잘 적응한다.", "C4·CAM 식물은 CO2를 농축하거나 저장하는 전략으로 광호흡을 줄인다."),
    F("p6", "c3c4", "definition", "photoresp", "C3·C4라는 이름은 CO2 고정 때 처음 만들어지는 안정한 분자의 탄소 수에서 왔다.", "대사과정에서 이산화탄소가 고정될 때, 생성된 첫번째로 안정한 분자의 탄소 수", src="quiz2", loc="2강 합본 원문 p1"),
]


def diagram(ident, label, body):
    return kit.svg(ident, 760, 210, label, body)


def box(title, content, cls="warn"):
    return kit.box(cls, title, content)


SECTIONS = [
    ('<section class="card" id="quick-map" data-role="teaching"><p class="kicker">0</p><h2>30초 지도 — 전자 흐름만 잡으면 된다</h2>' + """
      <div class="grid">
        <p class="mini" id="map-resp"><b>호흡</b><br>연료 전자 → 전자전달계 → H+ 댐 → ATP 합성효소</p>
        <p class="mini" id="map-ferm"><b>발효</b><br>NADH 전자 → 유기 중간산물 → NAD+ 재생 → 해당과정 2 ATP</p>
        <p class="mini" id="map-photo"><b>광합성</b><br>물 전자 → NADPH, 빛 → ATP → CO2를 당으로</p>
        <p class="mini" id="map-dry"><b>건조할 때</b><br>기공 닫힘 → CO2↓·O2↑ → 광호흡↑; C4·CAM은 우회</p>
      </div>
      <p class="analogy" id="map-analogy"><b>비유 — 물레방아와 충전지</b> 호흡·빛반응은 먼저 H+를 한쪽에 모아 물레방아(ATP 합성효소)를 돌리고, 광합성은 NADPH라는 충전지와 ATP를 들고 CO2를 당으로 조립합니다.</p>
      <p class="limit" id="map-limit"><b>비유의 한계</b> H+와 전자는 물·전기가 아니며, 실제로는 막 단백질과 산화환원 반응이 선택적으로 움직입니다.</p>
      """ + kit.R("빛반응과 캘빈 회로를 직접 이어 주는 두 분자는?", "ATP와 NADPH입니다. 둘 다 빛반응에서 만들어져 캘빈 회로의 CO2 고정·환원에 쓰입니다.") + '</section>'),

    kit.section("resp", "1", "세포호흡의 끝 — 전자만 ATP가 되지 않는다", """
      <div class="analogy"><b>교수님 비유</b><p>전자는 높은 층에서 낮은 층으로 내려가고, 그 힘으로 먼저 H+를 한쪽에 모은 뒤 ATP 합성효소라는 물레방아를 돌립니다.</p></div>
      """ + diagram("fig-resp", "세포호흡: 전자 흐름이 H+ 기울기를 만들고 ATP 합성효소가 ATP를 만든다",
          '<rect x="30" y="28" width="150" height="55" rx="12" fill="#e8efff"/><text x="105" y="61" text-anchor="middle">NADH/FADH2 전자</text>'
          '<path d="M185 55H310" stroke="#356ae6" stroke-width="4"/><polygon points="310,55 296,48 296,62" fill="#356ae6"/>'
          '<rect x="315" y="28" width="150" height="55" rx="12" fill="#e8f8f5"/><text x="390" y="61" text-anchor="middle">전자전달계</text>'
          '<path d="M470 55H585" stroke="#356ae6" stroke-width="4"/><polygon points="585,55 571,48 571,62" fill="#356ae6"/>'
          '<rect x="590" y="28" width="140" height="55" rx="12" fill="#fff3e4"/><text x="660" y="61" text-anchor="middle">O₂ → H₂O</text>'
          '<path d="M390 90V138" stroke="#b83d59" stroke-width="4"/><polygon points="390,138 383,124 397,124" fill="#b83d59"/><text x="455" y="123" fill="#b83d59">H+를 한쪽에 축적</text>'
          '<rect x="290" y="148" width="200" height="42" rx="12" fill="#fff0f3"/><text x="390" y="175" text-anchor="middle">H+ 기울기 → ATP 합성효소 → ATP</text>') +
      kit.T("resp-t1", "i1 r1 r2", "<b>정확한 순서</b>: NADH·FADH2의 전자가 전자전달계에서 산소 쪽으로 내려갑니다. 이 에너지로 H+를 퍼내고, H+가 ATP 합성효소를 통과해 돌아올 때 ATP가 만들어집니다.") +
      kit.T("resp-t2", "r3 r4", "<b>장부</b>: 기질수준 인산화는 인산기를 직접 건네고, 산화적 인산화는 H+ 기울기를 씁니다. 이 강의의 포도당 1분자 계산은 4 + 약 28 = <b>32 ATP</b>입니다.") +
      box("⚠️ 산소가 없으면", "<p id=\"resp-warn\" data-facts=\"r5\">산소가 전자를 받을 수 없으면 NADH가 NAD+로 돌아가지 못해 해당과정도 막힙니다. 발효는 이때 NAD+를 다시 만드는 안전장치입니다.</p>") +
      kit.R("전자전달계와 ATP 합성효소의 일을 한 문장씩 구분해 보세요.", "전자전달계는 H+ 기울기를 만들고, ATP 합성효소는 H+가 기울기를 따라 지나갈 때 ATP를 만듭니다.")),

    kit.section("ferm", "2", "발효 — NAD+ 빈 택시를 만들어 해당과정을 살린다", """
      <div class="analogy"><b>비유</b><p>NAD+는 빈 택시, NADH는 손님(전자)을 태운 택시입니다. 산소가 없으면 목적지가 막히므로, 발효는 근처 유기 중간산물에게 손님을 내려주어 빈 택시를 다시 만듭니다.</p></div>
      """ + diagram("fig-fermentation", "발효: NADH의 전자를 유기 중간산물에 주어 NAD+를 재생한다",
          '<rect x="35" y="68" width="150" height="58" rx="12" fill="#e8efff"/><text x="110" y="94" text-anchor="middle">NADH</text><text x="110" y="114" text-anchor="middle">전자 전달</text>'
          '<path d="M190 97H315" stroke="#356ae6" stroke-width="4"/><polygon points="315,97 301,90 301,104" fill="#356ae6"/>'
          '<rect x="320" y="68" width="150" height="58" rx="12" fill="#fff3e4"/><text x="395" y="94" text-anchor="middle">피루브산</text><text x="395" y="114" text-anchor="middle">또는 아세트알데하이드</text>'
          '<path d="M475 97H600" stroke="#356ae6" stroke-width="4"/><polygon points="600,97 586,90 586,104" fill="#356ae6"/>'
          '<rect x="605" y="68" width="120" height="58" rx="12" fill="#e8f8f5"/><text x="665" y="94" text-anchor="middle">젖산</text><text x="665" y="114" text-anchor="middle">/ 에탄올</text>'
          '<path d="M110 145V180H250" stroke="#07877f" stroke-width="4"/><polygon points="250,180 236,173 236,187" fill="#07877f"/><text x="180" y="170" fill="#07877f">NAD+ 재생 → 해당과정 계속</text>') +
      kit.T("ferm-t1", "f1 f2", "<b>젖산 발효</b>: 피루브산이 NADH의 전자를 받아 젖산이 됩니다. 산소가 부족한 근육·젖산균에서 일어나며, 요구르트와 김치의 신맛은 젖산과 연결됩니다.") +
      kit.T("ferm-t2", "f3", "<b>알코올 발효</b>: 효모는 피루브산에서 CO2를 떼어 아세트알데하이드를 만들고, 이를 환원해 에탄올을 만듭니다. CO2가 빵을 부풀립니다.") +
      kit.T("ferm-t3", "i2 f4 f5", "<b>한 줄 정의</b>: 발효는 유기 대사 중간산물이 전자를 받아 NAD+를 재생하는 경로입니다. 목적은 ATP를 많이 얻는 것이 아니라 해당과정의 <b>순 2 ATP</b>를 포기하지 않는 것입니다.") +
      box("⚠️ 원문 36번의 표현", "<p id=\"ferm-warn\" data-facts=\"f1 f2\">원문 선택지에는 ‘무기호흡과정 동안 생성된 젖산’이라고 쓰였지만, 수업 범위의 정확한 이름은 <b>젖산 발효</b>입니다.</p>") +
      kit.R("산소가 없을 때 발효가 꼭 필요한 직접 이유는?", "NADH를 NAD+로 되돌려 해당과정이 계속 전자를 받을 수 있게 하기 위해서입니다."), ("resp",)),

    kit.section("overview", "3", "광합성 큰 지도 — CO2에 전자와 ATP를 넣는다", """
      <div class="analogy"><b>비유</b><p>세포호흡은 높은 곳의 전자가 아래로 내려오며 발전하는 수력발전이고, 광합성은 햇빛으로 전자를 다시 끌어올려 CO2로 ‘당 블록’을 조립하는 공장입니다.</p></div>
      """ + diagram("fig-overview", "세포호흡과 광합성의 전자·에너지 흐름 비교",
          '<text x="190" y="28" text-anchor="middle" font-weight="700">세포호흡</text><text x="570" y="28" text-anchor="middle" font-weight="700">광합성</text>'
          '<text x="65" y="85">포도당</text><path d="M125 80H240" stroke="#356ae6" stroke-width="4"/><polygon points="240,80 226,73 226,87" fill="#356ae6"/><text x="182" y="70">NADH</text><path d="M245 80H340" stroke="#356ae6" stroke-width="4"/><polygon points="340,80 326,73 326,87" fill="#356ae6"/><text x="355" y="85">O₂</text>'
          '<text x="448" y="85">H₂O</text><path d="M505 80H610" stroke="#07877f" stroke-width="4"/><polygon points="610,80 596,73 596,87" fill="#07877f"/><text x="557" y="70">NADPH</text><path d="M615 80H720" stroke="#07877f" stroke-width="4"/><polygon points="720,80 706,73 706,87" fill="#07877f"/><text x="700" y="110">CO₂ → 당</text>'
          '<text x="190" y="158" fill="#b83d59">전자 내려감 + ATP 생성</text><text x="570" y="158" fill="#b83d59">빛으로 전자 올림 + ATP 사용</text>') +
      kit.T("overview-t1", "o1 o2", "<b>반대 방향</b>: 세포호흡은 포도당 전자가 산소로 내려가 ATP를 얻는 이화 과정입니다. 광합성은 CO2를 유기물로 만들기 위해 ATP와 전자를 넣는 동화 과정이고, 그 전자는 NADPH가 가져옵니다.") +
      kit.T("overview-t2", "o3 o4", "<b>누가 만드는가</b>: CO2에서 유기물을 만드는 독립영양생물은 생산자입니다. 빛을 쓰면 광독립영양, 무기물 산화를 쓰면 화학독립영양입니다. 사람·동물은 유기물을 먹어야 하는 종속영양생물입니다.") +
      kit.T("overview-t3", "i3 o5 o6", "<b>두 단계의 연결</b>: 빛반응은 <b>ATP와 NADPH</b>를 만들고, 캘빈 회로는 그것들과 CO2로 탄수화물을 만듭니다. 광독립반응도 ATP·NADPH 공급에는 의존합니다.") +
      box("⚠️ 암반응이라는 이름", "<p id=\"overview-warn\" data-facts=\"o6\">‘빛이 직접 필요 없다’는 뜻입니다. 어두운 곳에서 ATP·NADPH가 새로 공급되지 않으면 캘빈 회로는 오래 지속될 수 없습니다.</p>") +
      kit.R("빛반응과 광독립반응을 연결하는 분자 두 개는?", "ATP와 NADPH입니다."), ("resp",)),

    kit.section("structure", "4", "엽록체·광계 — 빛을 모아 전자를 튀긴다", """
      <div class="analogy"><b>비유</b><p>틸라코이드는 녹차 초코파이, 그라나는 그 초코파이를 쌓은 더미입니다. 초코파이 막 안의 광계는 많은 안테나가 빛을 모아 중앙 반응중심에 보내는 접시입니다.</p></div>
      """ + diagram("fig-chloroplast", "엽록체: 틸라코이드 막에서 빛반응, 스트로마에서 캘빈 회로",
          '<ellipse cx="380" cy="105" rx="340" ry="82" fill="#e8f8e8" stroke="#07877f" stroke-width="4"/><text x="110" y="70">외막·내막</text><text x="580" y="168">스트로마: 캘빈 회로</text>'
          '<g fill="#77b96a" stroke="#315f31" stroke-width="2"><rect x="275" y="55" width="180" height="18" rx="9"/><rect x="275" y="80" width="180" height="18" rx="9"/><rect x="275" y="105" width="180" height="18" rx="9"/><rect x="275" y="130" width="180" height="18" rx="9"/></g><text x="365" y="175" text-anchor="middle">그라나 = 쌓인 틸라코이드</text><text x="365" y="46" text-anchor="middle">틸라코이드 막: 색소·전자전달계·ATP 합성효소</text>') +
      kit.T("structure-t1", "s1 s2", "<b>장소</b>: 스트로마는 내막 안의 유동액, 그라나는 틸라코이드 더미입니다. 빛반응 장비는 틸라코이드 막에, 캘빈 회로는 스트로마에 있습니다.") +
      kit.T("structure-t2", "s3 s4 s5", "<b>색소</b>: 엽록소 a·b, 카로티노이드, 크산토필은 서로 다른 빛을 흡수합니다. 녹색빛은 주로 반사되어 식물이 녹색으로 보입니다. 흡수 스펙트럼은 흡수량, 작용 스펙트럼은 실제 광합성 정도입니다.") +
      kit.T("structure-t3", "s6 s7", "<b>광계</b>: 안테나 복합체가 빛 에너지를 모아 반응중심으로 전달하면, 반응중심의 들뜬 전자가 전자수용체로 이동합니다.") +
      kit.R("스트로마와 틸라코이드 막에서 각각 일어나는 일은?", "스트로마에서는 캘빈 회로, 틸라코이드 막에서는 색소·전자전달계·ATP 합성효소가 작동하는 빛반응이 일어납니다."), ("overview",)),

    kit.section("light", "5", "빛반응 — 물의 전자를 NADPH까지 끌어올린다", """
      <div class="analogy"><b>비유</b><p>광계 II와 I은 햇빛으로 전자를 두 번 들어 올리는 리프트입니다. 전자가 II에서 I로 내려오는 구간의 에너지로 H+를 내강에 쌓고, I에서 다시 올려 NADPH 충전지에 담습니다.</p></div>
      """ + diagram("fig-light", "빛반응의 전자 흐름과 H+ 흐름: H₂O → PSII → ETC → PSI → NADPH",
          '<text x="48" y="72">H₂O</text><path d="M85 68H165" stroke="#356ae6" stroke-width="4"/><polygon points="165,68 151,61 151,75" fill="#356ae6"/><rect x="170" y="42" width="92" height="52" rx="12" fill="#fff3e4"/><text x="216" y="73" text-anchor="middle">광계 II</text><path d="M267 68H360" stroke="#356ae6" stroke-width="4"/><polygon points="360,68 346,61 346,75" fill="#356ae6"/><rect x="365" y="42" width="88" height="52" rx="12" fill="#e8efff"/><text x="409" y="73" text-anchor="middle">ETC</text><path d="M458 68H535" stroke="#356ae6" stroke-width="4"/><polygon points="535,68 521,61 521,75" fill="#356ae6"/><rect x="540" y="42" width="88" height="52" rx="12" fill="#fff3e4"/><text x="584" y="73" text-anchor="middle">광계 I</text><path d="M633 68H710" stroke="#356ae6" stroke-width="4"/><polygon points="710,68 696,61 696,75" fill="#356ae6"/><text x="714" y="73">NADPH</text>'
          '<text x="45" y="110" fill="#b83d59">O₂ + H+</text><path d="M409 98V155" stroke="#b83d59" stroke-width="4"/><polygon points="409,155 402,141 416,141" fill="#b83d59"/><text x="438" y="133" fill="#b83d59">H+를 내강에 축적</text><path d="M570 166H470" stroke="#07877f" stroke-width="4"/><polygon points="470,166 484,159 484,173" fill="#07877f"/><text x="520" y="196" text-anchor="middle" fill="#07877f">내강 → ATP 합성효소 → 스트로마 ATP</text>') +
      kit.T("light-t1", "l1 l2", "<b>시작</b>: 광계 II(P680)가 잃은 전자는 <b>물</b>의 광분해가 보충합니다. 물은 전자와 H+를 내고 O2를 만듭니다. 그래서 방출 O2의 직접 기원은 물입니다.") +
      kit.T("light-t2", "l3 l4", "<b>ATP 만들기</b>: 광계 II 전자가 전자전달계를 내려가며 H+를 틸라코이드 <b>내강</b>에 쌓습니다. H+가 내강에서 <b>스트로마</b>로 ATP 합성효소를 통과할 때 ATP가 합성됩니다(광인산화).") +
      kit.T("light-t3", "l5 l6", "<b>NADPH 만들기</b>: 전자는 광계 I에서 다시 빛을 받아 들뜨고, 페레독신·NADP+ 환원효소를 거쳐 NADP+를 NADPH로 만듭니다. 따라서 NADP+는 빛반응의 최종 전자수용체입니다.") +
      box("⚠️ 꼭 구분", "<p id=\"light-warn\" data-facts=\"l2 l4 l6\">빛반응에서 <b>물은 분해</b>되어 O2를 만들고, <b>산소가 분해되어 물을 만드는 것</b>은 세포호흡 전자전달계 끝의 이야기입니다. ATP와 NADPH는 빛반응 산물입니다.</p>") +
      kit.R("광계 II에서 NADPH까지 전자의 출발지와 도착지를 말해 보세요.", "출발지는 물이고, 광계 II·전자전달계·광계 I을 거쳐 최종적으로 NADP+를 환원해 NADPH가 됩니다."), ("structure",)),

    kit.section("calvin", "6", "캘빈 회로 — CO2를 붙이고, 환원하고, 출발물을 재생한다", """
      <div class="analogy"><b>비유</b><p>회전초밥 레일의 빈 접시가 RuBP입니다. CO2 한 조각을 올린 뒤 ATP·NADPH로 가공해 G3P를 만들고, 대부분의 접시는 다시 빈 RuBP로 돌아가야 다음 CO2를 받을 수 있습니다.</p></div>
      """ + diagram("fig-calvin", "캘빈 회로: 탄소고정 → 환원 → RuBP 재생",
          '<circle cx="385" cy="108" r="72" fill="#eef3ff" stroke="#356ae6" stroke-width="4"/><text x="385" y="113" text-anchor="middle" font-weight="700">캘빈 회로</text><text x="385" y="134" text-anchor="middle">스트로마</text>'
          '<text x="100" y="70">CO₂ + RuBP</text><path d="M205 75H290" stroke="#356ae6" stroke-width="4"/><polygon points="290,75 276,68 276,82" fill="#356ae6"/><text x="116" y="102">① 탄소고정</text>'
          '<text x="560" y="70">3-PGA → G3P</text><path d="M480 75H540" stroke="#356ae6" stroke-width="4"/><polygon points="540,75 526,68 526,82" fill="#356ae6"/><text x="570" y="102">② ATP + NADPH 환원</text>'
          '<text x="275" y="205">③ 일부 G3P는 당, 나머지는 ATP로 RuBP 재생</text>') +
      kit.T("calvin-t1", "c1 c2", "<b>1단계 탄소고정</b>: 스트로마에서 CO2가 5탄당 RuBP에 붙습니다. 캘빈 회로는 ATP·NADPH·CO2로 탄수화물을 만드는 광독립반응입니다.") +
      kit.T("calvin-t2", "c3", "<b>2단계 환원</b>: 불안정 6탄소 물질은 3-PGA 두 분자로 갈라지고, ATP와 NADPH를 써 <b>G3P</b>가 됩니다. 21번의 원문 답은 G3P입니다.") +
      kit.T("calvin-t3", "c4 c5 c6", "<b>3단계 재생</b>: G3P 일부는 당 합성에 쓰고, 나머지는 ATP를 써 RuBP를 재생합니다. CO2가 6번 들어온 뒤 6탄당 1분자를 만들 수 있습니다. 필수 투입물은 ATP·NADPH·CO2이고 <b>FAD는 아닙니다</b>.") +
      box("⚠️ ‘한 회전’의 말", "<p id=\"calvin-warn\" data-facts=\"c3 c4 c5\">원문 24번은 한 CO2 고정에서 ‘탄수화물 한 단위’를 묻는 수업용 표현입니다. 포도당 1분자까지의 전체 장부는 CO2 6회전이라는 기준을 함께 잡으세요.</p>") +
      kit.R("캘빈 회로의 세 단계를 순서대로 말해 보세요.", "탄소고정(CO2 + RuBP) → ATP·NADPH를 쓰는 환원(G3P) → RuBP 재생입니다."), ("overview", "light")),

    kit.section("photoresp", "7", "광호흡 — 기공을 닫으면 루비스코가 O2를 잡는다", """
      <div class="analogy"><b>비유</b><p>루비스코는 원래 CO2 손님을 받는 문지기입니다. 기공을 닫아 CO2 손님은 줄고 O2 손님이 몰리면, 실수로 O2를 받았다가 뒷정리에 에너지를 쓰게 됩니다.</p></div>
      """ + diagram("fig-photoresp", "고온·건조: 기공 닫힘 → CO₂ 감소·O₂ 증가 → 광호흡",
          '<rect x="45" y="56" width="130" height="72" rx="12" fill="#fff3e4"/><text x="110" y="85" text-anchor="middle">덥고 건조</text><text x="110" y="108" text-anchor="middle">기공 닫힘</text><path d="M180 92H305" stroke="#b83d59" stroke-width="4"/><polygon points="305,92 291,85 291,99" fill="#b83d59"/><text x="242" y="76" fill="#b83d59">CO₂↓, O₂↑</text>'
          '<rect x="310" y="56" width="140" height="72" rx="12" fill="#fff0f3"/><text x="380" y="85" text-anchor="middle">루비스코가</text><text x="380" y="108" text-anchor="middle">O₂를 기질로 사용</text><path d="M455 92H580" stroke="#b83d59" stroke-width="4"/><polygon points="580,92 566,85 566,99" fill="#b83d59"/><rect x="585" y="56" width="130" height="72" rx="12" fill="#e8efff"/><text x="650" y="85" text-anchor="middle">광호흡</text><text x="650" y="108" text-anchor="middle">에너지 소모·성장↓</text>'
          '<text x="380" y="176" text-anchor="middle" fill="#07877f">C4·CAM: CO₂를 농축·저장해 이 상황을 줄임</text>') +
      kit.T("photoresp-t1", "p1 p2", "<b>시작 조건</b>: 기공은 CO2가 들어오고 O2·물이 나가는 구멍입니다. 덥고 건조하면 물을 아끼기 위해 기공을 닫습니다.") +
      kit.T("photoresp-t2", "i4 p3 p4", "<b>광호흡</b>: 기공이 닫히면 CO2는 줄고 O2는 늘어, 루비스코가 CO2 대신 O2를 기질로 사용합니다. 독성 물질 처리에 에너지를 써 성장에 손해가 납니다.") +
      kit.T("photoresp-t3", "p5", "<b>C4·CAM의 해결</b>: CO2를 농축하거나 저장해 광호흡을 줄입니다. 원문이 묻는 낮 고온·건조 사막 적응 식물은 <b>CAM 식물</b>입니다.") +
      kit.T("photoresp-t4", "p6", "<b>C3·C4 이름</b>: CO2를 고정할 때 처음 생기는 안정한 분자의 탄소 수가 3이면 C3, 4이면 C4입니다.") +
      box("⚠️ 광호흡은 에너지를 만드는 호흡이 아니다", "<p id=\"photoresp-warn\" data-facts=\"p3 p4\">광호흡은 O2를 이용하지만 ATP를 얻는 세포호흡과 달리 에너지를 소모하는 손실 경로입니다.</p>") +
      kit.R("광호흡을 늘리는 세 조건을 연결해 보세요.", "고온·건조 → 기공 닫힘 → CO2 감소·O2 증가 → 루비스코의 O2 사용 → 광호흡 증가입니다."), ("calvin",)),
]


Q = kit.Q
QUESTIONS = [
    Q("2강:3", "included", "photoresp", "1", "C3와 C4식물은 어떻게 이름 붙여졌는가?",
      ["대사과정에서 이산화탄소가 고정될 때, 생성된 첫번째로 안정한 분자의 탄소 수", "탄소를 포함하는 분자가 발견된 순서", "식물이나 동물의 물질대사에 가장 먼저 참여하는 탄소 수", "식물이 위치하는 지리적 좌표와 연관"], 1, 1, "single", ["p6"],
      {1: "정답. CO2 고정 뒤 처음 안정한 산물의 탄소 수가 이름의 기준이다.", 2: "발견 순서가 아니라 탄소 수다.", 3: "동물 대사 참여 순서와 무관하다.", 4: "지리 좌표와 무관하다."}, "C3·C4의 C를 ‘탄소 발견 순서’로 읽기 쉽다.", "처음 안정한 CO2 고정 산물이 3탄소면 C3, 4탄소면 C4다."),
    Q("2강:4", "included", "light", "1", "광합성의 광의존반응에서 주요한 화학적 과정에는 (    )의 분해와 (     )의 방출이 포함된다.",
      ["물 - 전자", "ATP - 산소", "ATP - 전자", "물 - 질소"], 1, 1, "single", ["l1", "l2"],
      {1: "정답. 물이 광분해되어 전자·H+를 내고 O2가 생긴다.", 2: "ATP는 분해 대상이 아니라 빛반응 산물이다.", 3: "ATP가 아니라 물의 광분해가 전자를 공급한다.", 4: "방출되는 기체는 질소가 아니라 산소다."}, "산소가 생긴다는 점만 기억해 ATP를 고르기 쉽다.", "광계 II에서 물이 분해되어 전자가 공급된다."),
    Q("2강:5", "included", "ferm", "1", "다음 중 발효과정의 결과로 생산되는 분자는 어떤 것인가?",
      ["ATP", "NAD+", "NADPH", "NADH"], 2, 2, "single", ["f4", "f5"],
      {1: "해당과정에서 순 2 ATP가 생기지만, 발효의 직접 산물·목적은 NAD+ 재생이다.", 2: "정답. NADH가 전자를 유기 중간산물에 주어 NAD+가 된다.", 3: "NADPH는 광합성 빛반응의 전자운반체다.", 4: "NADH는 발효 전에 해당과정에서 만들어져 전자를 주는 쪽이다."}, "ATP가 발효 전체와 연결된다는 이유로 고르기 쉽다.", "발효는 NADH를 NAD+로 산화해 해당과정을 계속시키는 과정이다."),
    Q("2강:9", "included", "light", "1", "다음 중 광합성의 광의존반응 동안에 일어나지 않는 것은?",
      ["전자전달계가 캘빈회로에 사용될 ATP합성을 가동시킨다.", "엽록소로부터 나온 전자가 전자전달계에 첨가된다.", "물이 분해되면서 산소가 생산된다.", "산소가 분해되어서 물을 방출한다.", "NADPH가 생산되며, 캘빈회로에 전자를 운반한다."], 4, 4, "single", ["l1", "l2", "l3", "l4", "l5"],
      {1: "빛반응 전자전달계가 H+ 기울기를 만들고 ATP 합성효소가 ATP를 만든다.", 2: "광계의 들뜬 전자는 전자전달계로 이동한다.", 3: "물 광분해가 O2를 만든다.", 4: "정답. 이는 호흡의 끝과 뒤섞은 서술이다. 빛반응에서는 물이 분해되어 O2가 나온다.", 5: "NADPH는 빛반응에서 만들어져 캘빈 회로에 전자를 공급한다."}, "세포호흡의 O2 + 전자 + H+ → 물을 빛반응에 섞기 쉽다.", "빛반응에서는 물이 분해되고 NADPH·ATP가 만들어진다."),
    Q("2강:12", "included", "photoresp", "1", "광호흡 과정에서 일어나는 일은?",
      ["이산화탄소가 루비스코와 결합하여 RuBP를 생성한다.", "루비스코가 기질로 산소를 이용한다.", "산소가 루비스코와 결합하여 RuBP를 생성한다.", "효소인 루비스코가 기질로 이산화탄소를 사용한다.", "이산화탄소가 3-탄소 분자와 결합하여 4-탄소 분자를 생산한다."], 2, 2, "single", ["p3", "p4"],
      {1: "RuBP는 CO2와 결합하기 전부터 있는 5탄당이다.", 2: "정답. CO2 부족·O2 과다에서 루비스코가 O2를 기질로 사용한다.", 3: "O2가 RuBP를 만드는 것이 아니다.", 4: "이는 정상 탄소고정의 방향이지 광호흡이 아니다.", 5: "C4 경로와 섞은 보기다."}, "정상 광합성의 ‘루비스코 + CO2’를 그대로 고르기 쉽다.", "광호흡에서는 루비스코가 O2를 기질로 써 에너지를 소모하는 처리가 뒤따른다."),
    Q("2강:17", "included", "light", "2", "광합성 광의존반응에서 발생하는 산소의 기원은?",
      ["물", "포도당", "NADPH", "NADH", "이산화탄소"], 1, 1, "single", ["l1", "l2"],
      {1: "정답. 물 광분해에서 O2가 나온다.", 2: "포도당은 광합성의 생성물 쪽이다.", 3: "NADPH는 전자운반체이며 O2의 출발 물질이 아니다.", 4: "NADH는 주로 세포호흡 운반체다.", 5: "CO2는 탄소를 공급하지만 O2의 직접 기원은 아니다."}, "CO2가 광합성의 재료라서 산소도 CO2에서 온다고 생각하기 쉽다.", "빛반응의 물 광분해가 O2를 방출한다."),
    Q("2강:21", "included", "calvin", "2", "캘빈회로의 2단계 반응 중 NADPH에 의한 환원반응의 결과 생산되는 것은?",
      [], None, None, "rubric", ["c3"], {}, "ATP·NADPH가 쓰인다는 말만 기억하고 생성물 이름을 빼먹기 쉽다.", "3-PGA가 ATP와 NADPH를 쓰는 환원 단계를 거쳐 G3P가 된다.", printed="G3P", rubric=["G3P라고 쓴다.", "NADPH가 전자를 주는 환원 단계임을 덧붙이면 완전하다.", "3-PGA가 출발물질이라는 점을 구분하면 완전하다."]),
    Q("2강:24", "included", "calvin", "2", "캘빈회로의 한 회전에서 CO2 분자는 무엇을 생산하는가?",
      ["포도당 한 분자", "ATP", "ATP 6개 NADPH 6개", "탄수화물 한 단위", "6 NADPH"], 4, 4, "single", ["c3", "c4", "c5"],
      {1: "포도당 1분자는 CO2 6회전이라는 장부가 필요하다.", 2: "ATP는 캘빈 회로가 만드는 것이 아니라 쓰는 쪽이다.", 3: "ATP·NADPH는 빛반응의 산물이며 캘빈 회로의 투입물이다.", 4: "정답. 원문은 한 CO2 고정의 수업용 결과를 ‘탄수화물 한 단위’로 표현한다.", 5: "NADPH는 생성물이 아니라 환원력 투입물이다."}, "한 회전과 포도당 1분자 완성 장부를 섞기 쉽다.", "한 CO2 고정의 결과는 탄수화물 한 단위로 정리하고, 포도당 1분자는 CO2 6회전이라는 기준을 함께 기억한다.", conflict="원문은 ‘한 회전’의 순생산을 간략히 ‘탄수화물 한 단위’로 표현합니다. 수업 노트의 전체 장부는 CO2 6회전 후 6탄당 1분자이므로, ①과 섞지 않도록 이 차이를 공개합니다."),
    Q("2강:26", "included", "light", "3", "광합성 과정에서 NADP+의 역할은 무엇인가?",
      ["ADP를 ATP로 인산화", "빛에너지 흡수", "물을 산소와 수소로 분해", "전자수용체", "이산화탄소를 루비스코로 전환"], 4, 4, "single", ["l5", "l6"],
      {1: "ADP 인산화는 ATP 합성효소의 일이다.", 2: "빛을 주로 흡수하는 것은 색소·광계다.", 3: "물 광분해는 광계 II 쪽에서 일어난다.", 4: "정답. NADP+는 전자와 H+를 받아 NADPH가 되는 최종 전자수용체다.", 5: "CO2는 RuBP와 결합하며 NADP+가 전환시키지 않는다."}, "NADP+가 ATP·빛·물 분해와 모두 같은 막에서 일어나서 섞기 쉽다.", "NADP+는 빛반응 끝에서 전자를 받아 NADPH가 되는 전자수용체다."),
    Q("2강:31", "included", "overview", "3", "광의존반응과 광독립반응을 연결시키는 분자는?",
      ["G3P와 RuBP", "ADP와 H2O", "RuBP와 CO2", "ATP와 NADPH", "사이토크롬과 물"], 4, 4, "single", ["o5", "o6", "l4", "l5", "c1"],
      {1: "G3P·RuBP는 캘빈 회로 안의 물질이다.", 2: "ADP와 물은 관련 물질이지만 빛반응 산물을 캘빈 회로로 실어 나르는 쌍이 아니다.", 3: "RuBP·CO2는 캘빈 회로의 탄소고정 재료다.", 4: "정답. 빛반응이 ATP·NADPH를 만들고 캘빈 회로가 둘을 쓴다.", 5: "사이토크롬·물은 이 두 반응의 연결 산물이 아니다."}, "캘빈 회로에 쓰이는 CO2·RuBP를 연결 분자로 오해하기 쉽다.", "빛반응의 ATP·NADPH가 캘빈 회로로 전달된다."),
    Q("2강:32", "included", "light", "3", "다음 중 광합성에 대하여 잘못 설명하고 있는 것은?",
      ["햇빛이 엽록소에 부딪쳤을 때 방출된 전자들은 물에서부터 온 전자들에 의해서 대체된다.", "캘빈회로의 효소들은 엽록체의 스트로마에 존재한다.", "캘빈회로에서 생산된 산소는 대기로 방출한다.", "캘빈회로에서는 광의존반응으로부터 온 전자들과 ATP가 대기의 이산화탄소와 결합하여 당을 생성한다.", "햇빛은 엽록소에 있는 전자들을 더 높은 에너지 수준으로 올림으로써 광합성을 가동시킨다."], 3, 3, "single", ["l1", "l2", "l5", "c1", "s2"],
      {1: "광계 II가 잃은 전자는 물 광분해에서 보충된다.", 2: "캘빈 회로는 스트로마에서 일어난다.", 3: "정답. O2는 캘빈 회로가 아니라 물 광분해가 일어나는 빛반응에서 생긴다.", 4: "캘빈 회로는 빛반응에서 온 ATP·NADPH로 CO2를 환원해 당을 만든다.", 5: "빛은 광계 엽록소 전자를 높은 에너지 상태로 올린다."}, "광합성 전체에서 산소가 나옴을 알아도 어느 단계인지 섞기 쉽다.", "산소는 물의 광분해가 있는 빛반응에서 생기고, 캘빈 회로는 CO2를 환원한다."),
    Q("2강:36", "included", "ferm", "3", "요구르트의 신맛의 원인은 무엇인가?",
      ["시트르산 회로에서 미생물에 의해 방출된 시트르산", "해당과정 동안에 미생물에 의해 생성된 ADP", "미생물에 의해 무기호흡과정 동안 생성된 젖산", "미생물에 의해 지방이 분해되어 나온 지방산"], 3, 3, "single", ["f1", "f2"],
      {1: "요구르트 신맛의 핵심 산물은 시트르산이 아니라 젖산이다.", 2: "ADP는 신맛 물질이 아니다.", 3: "출제 의도 정답. 젖산균의 젖산 발효 산물인 젖산이 신맛과 연결된다.", 4: "지방산이 아니라 젖산이다."}, "원문이 ‘무기호흡’이라고 써서 용어까지 맞다고 받아들이기 쉽다.", "요구르트의 신맛은 젖산균의 젖산 발효로 생긴 젖산 때문이다.", conflict="원문 인쇄 정답은 ③이지만 ‘무기호흡과정’이라는 표현은 수업 내용과 맞지 않습니다. 젖산은 산소 부족에서 NAD+를 재생하는 <b>젖산 발효</b>의 산물입니다. 정답 선택지는 그대로 따르되, 용어 오류를 공개합니다."),
    Q("2강:40", "included", "photoresp", "3", "다음 중 사막과 같이 낮에 고온 건조한 환경에서 가장 잘 적응하는 식물은?",
      [], None, None, "rubric", ["p5"], {}, "C4와 CAM 모두 광호흡을 줄인다는 넓은 지식 때문에 원문이 요구한 답을 놓치기 쉽다.", "낮 고온·건조 사막 환경에 가장 잘 적응한 식물은 CAM 식물이다.", printed="CAM 식물", rubric=["CAM 식물이라고 쓴다.", "낮 고온·건조에서 CO2를 저장·농축해 광호흡을 줄이는 적응을 덧붙이면 완전하다."]),
    Q("2강:41", "included", "calvin", "4", "광독립반응의 진행을 위해 캘빈회로에서 반드시 요구되는 투입물질이 아닌 것은?",
      ["ATP", "FAD", "CO2", "NADPH"], 2, 2, "single", ["c1", "c6"],
      {1: "ATP는 캘빈 회로의 에너지 투입물이다.", 2: "정답. FAD는 이 회로의 필수 투입물로 제시되지 않는다.", 3: "CO2는 탄소고정의 재료다.", 4: "NADPH는 환원력(전자)을 공급한다."}, "세포호흡에서 친숙한 FAD를 광합성에도 넣기 쉽다.", "캘빈 회로는 ATP·NADPH·CO2를 쓰며 FAD는 필수 투입물이 아니다."),
]

DEFERRED = {}

META = dict(
    note="../../../0915.md",
    overrides="../../meta/0915-eli5.question-scope-overrides.json",
    output_stem="0915-eli5",
    title="0915 생명과학 ELI5 · 발효와 광합성 학습 가이드",
    quiz_sources={"2강": dict(source_id="quiz2", path="../23, 24 소스/2강 합본.pdf", label="2강 합본 원문")},
    groups=[("ferm", "발효"), ("light", "빛반응"), ("calvin", "캘빈 회로"), ("overview", "광합성 큰 지도"), ("photoresp", "광호흡·건조 적응")],
    header_html=("<header><small>ELI5 학습 가이드 · 0915 생명과학 · 원천: 0915.md + 2강 원문 문제지</small>"
                 "<h1>발효와 광합성 — 전자의 출발지·도착지부터 그림으로</h1>"
                 "<p>포함 {inc}문항 · 복습 {rev}문항 · 보류 {deferred}문항 = {total}문항. 개념 그림을 먼저 보고, 원문 문항으로 확인하세요. 정답은 접혀 있으며 인쇄 시 펼쳐집니다.</p></header>"),
    scope_notes_html=("<p>0910 가이드에서 ‘후속 범위’로 보류된 <b>2강 3·4·5·9·12·17·21·24·26·31·32·36·40·41번</b>을 0915 실강 범위로 모두 전환했습니다. "
                      "문항 문장·보기·인쇄 답은 원문 PDF 4쪽을 이미지로 대조했습니다. 21·40번은 원문에 선택지가 보이지 않는 단답형으로, 보기를 새로 만들지 않았습니다. "
                      "24번의 한 회전 표현과 36번의 ‘무기호흡’ 용어 오류는 각 해설에 공개했습니다.</p>"),
    footer="한 줄 암기: 빛은 물의 전자를 NADPH까지 올리고 H+ 기울기로 ATP를 만든다. ATP·NADPH는 스트로마의 캘빈 회로에 가서 CO2를 당으로 만든다.",
)

BOUNDARY = '<section class="card boundary" id="boundary"><p class="kicker">범위 경계</p><h2>이번 가이드가 다루는 곳</h2><p>0915 실강의 발효·광합성 범위와 그에 직접 연결되는 2강 원문 14문항만 포함합니다. 2강의 나머지 세포호흡·효소 문항은 이미 0910 가이드 범위입니다.</p></section>'
