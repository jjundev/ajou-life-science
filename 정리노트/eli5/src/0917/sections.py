import guide_kit as kit


T, R, B = kit.T, kit.R, kit.B


def diagram_chromosome():
    inner = (
        '<rect x="28" y="24" width="584" height="252" rx="24" fill="#f7f1e8"/>'
        '<text x="170" y="58" text-anchor="middle" font-weight="700">엄마에게서 온 염색체</text>'
        '<text x="470" y="58" text-anchor="middle" font-weight="700">아빠에게서 온 상동염색체</text>'
        '<path d="M150 78 C130 105 138 125 150 142 C138 160 130 184 150 210 L190 210 C210 184 202 160 190 142 C202 125 210 105 190 78 Z" fill="#e99b72" stroke="#c64f43" stroke-width="4"/>'
        '<path d="M450 78 C430 105 438 125 450 142 C438 160 430 184 450 210 L490 210 C510 184 502 160 490 142 C502 125 510 105 490 78 Z" fill="#79acd1" stroke="#356fa3" stroke-width="4"/>'
        '<line x1="140" y1="103" x2="200" y2="103" stroke="#172033" stroke-width="4"/><text x="126" y="108" text-anchor="end" font-weight="700">A</text>'
        '<line x1="140" y1="168" x2="200" y2="168" stroke="#172033" stroke-width="4"/><text x="126" y="173" text-anchor="end" font-weight="700">B</text>'
        '<line x1="140" y1="195" x2="200" y2="195" stroke="#172033" stroke-width="4"/><text x="126" y="200" text-anchor="end" font-weight="700">C</text>'
        '<line x1="440" y1="103" x2="500" y2="103" stroke="#172033" stroke-width="4"/><text x="514" y="108" font-weight="700">a</text>'
        '<line x1="440" y1="168" x2="500" y2="168" stroke="#172033" stroke-width="4"/><text x="514" y="173" font-weight="700">b</text>'
        '<line x1="440" y1="195" x2="500" y2="195" stroke="#172033" stroke-width="4"/><text x="514" y="200" font-weight="700">c</text>'
        '<circle cx="170" cy="142" r="8" fill="#172033"/><path d="M82 142 L152 142" stroke="#172033" stroke-width="3"/><text x="72" y="147" text-anchor="end" font-weight="700">X</text>'
        '<circle cx="470" cy="142" r="8" fill="#172033"/>'
        '<path d="M250 142 L390 142" stroke="#172033" stroke-width="3" stroke-dasharray="7 7"/><text x="320" y="128" text-anchor="middle">상동 관계</text>'
        '<text x="320" y="242" text-anchor="middle">같은 A/a·B/b·C/c 자리 · X는 방추사 부착 부위</text>'
    )
    return kit.svg("fig-chromosome", 640, 300, "3강 25번의 두 상동염색체와 A/a·B/b·C/c 유전자 자리", inner)


def diagram_division():
    inner = (
        '<rect x="20" y="24" width="600" height="236" rx="24" fill="#eef5f4"/>'
        '<text x="320" y="58" text-anchor="middle" font-weight="700">분리 대상을 먼저 묻는다</text>'
        '<text x="115" y="118" text-anchor="middle" font-size="22">유사분열</text><text x="115" y="154" text-anchor="middle">자매염색분체 분리</text><text x="115" y="194" text-anchor="middle" font-weight="700">2n → 2n + 2n</text>'
        '<path d="M215 144 L292 144" stroke="#172033" stroke-width="4"/><polygon points="302,144 284,134 284,154" fill="#172033"/>'
        '<text x="410" y="104" text-anchor="middle" font-size="22">감수 I</text><text x="410" y="136" text-anchor="middle">상동염색체 분리</text><text x="410" y="168" text-anchor="middle" font-size="22">감수 II</text><text x="410" y="200" text-anchor="middle">자매염색분체 분리 → n</text>'
    )
    return kit.svg("fig-division", 640, 284, "유사분열과 감수분열의 분리 대상", inner)


def diagram_cycle():
    inner = (
        '<circle cx="320" cy="180" r="116" fill="none" stroke="#d7dfdf" stroke-width="34"/>'
        '<path d="M320 64 A116 116 0 0 1 433 154" fill="none" stroke="#d89452" stroke-width="34"/>'
        '<path d="M433 154 A116 116 0 0 1 350 292" fill="none" stroke="#c45d54" stroke-width="34"/>'
        '<path d="M350 292 A116 116 0 0 1 207 205" fill="none" stroke="#4f88a8" stroke-width="34"/>'
        '<path d="M207 205 A116 116 0 0 1 320 64" fill="none" stroke="#4b796b" stroke-width="34"/>'
        '<text x="372" y="88" text-anchor="middle" font-weight="700">G1 성장</text><text x="421" y="236" text-anchor="middle" font-weight="700">S 복제</text>'
        '<text x="260" y="286" text-anchor="middle" font-weight="700">G2 확인</text><text x="220" y="124" text-anchor="middle" font-weight="700">M 분열</text>'
        '<text x="320" y="174" text-anchor="middle" font-size="20" font-weight="700">G1 → S → G2 → M</text><text x="320" y="204" text-anchor="middle">끝나지 않으면 확인점에서 정지</text>'
    )
    return kit.svg("fig-cycle", 640, 360, "G1 S G2 M 세포주기와 확인점", inner)


def diagram_control():
    inner = (
        '<rect x="24" y="28" width="592" height="212" rx="22" fill="#f7f1e8"/>'
        '<rect x="46" y="92" width="108" height="58" rx="14" fill="#e0a45d"/><text x="100" y="126" text-anchor="middle" font-weight="700">성장 신호</text>'
        '<path d="M154 121 L218 121" stroke="#172033" stroke-width="4"/><polygon points="230,121 210,110 210,132" fill="#172033"/>'
        '<rect x="230" y="82" width="112" height="78" rx="16" fill="#79acd1"/><text x="286" y="116" text-anchor="middle" font-weight="700">수용체</text><text x="286" y="140" text-anchor="middle">전달 단백질</text>'
        '<path d="M342 121 L406 121" stroke="#172033" stroke-width="4"/><polygon points="418,121 398,110 398,132" fill="#172033"/>'
        '<rect x="418" y="82" width="162" height="78" rx="16" fill="#4b796b"/><text x="499" y="116" text-anchor="middle" fill="white" font-weight="700">사이클린 + CDK</text><text x="499" y="140" text-anchor="middle" fill="white">분열 진행</text>'
        '<text x="320" y="210" text-anchor="middle">신호 없이 계속 켜짐 = 발암 유전자 · 멈춤 장치 상실 = 종양 억제 유전자 기능 상실</text>'
    )
    return kit.svg("fig-control", 640, 270, "외부 성장 신호에서 세포분열까지의 조절 경로", inner)


def diagram_tumor():
    inner = (
        '<rect x="20" y="28" width="280" height="214" rx="24" fill="#eef5f4"/><text x="160" y="62" text-anchor="middle" font-weight="700">정상·양성: 경계 안</text>'
        '<g fill="#4b796b">' + ''.join(f'<circle cx="{80+(i%4)*52}" cy="{112+(i//4)*52}" r="18"/>' for i in range(8)) + '</g>'
        '<rect x="340" y="28" width="280" height="214" rx="24" fill="#f8ebe8"/><text x="480" y="62" text-anchor="middle" font-weight="700">악성: 침범·전이</text>'
        '<g fill="#c45d54">' + ''.join(f'<circle cx="{400+(i%4)*42}" cy="{108+(i//4)*42}" r="18"/>' for i in range(12)) + '</g>'
        '<path d="M515 184 C550 196 570 210 598 222" stroke="#c45d54" stroke-width="5" fill="none"/><polygon points="604,225 585,211 582,231" fill="#c45d54"/>'
    )
    return kit.svg("fig-tumor", 640, 270, "접촉 저해가 있는 세포와 침범·전이하는 암세포", inner)


SECTIONS = [
    '<section class="card" id="map"><h2>30초 지도</h2>'
    '<p>복제 사본끼리는 <b>자매염색분체</b>, 부모에게서 하나씩 온 같은 종류는 <b>상동염색체</b>입니다.</p>'
    '<p>세포는 <b>G1 → S → G2 → M</b> 순서로 돌고, 확인점과 조절 유전자가 사고를 막습니다.</p>'
    '<p>0917은 3장 세포분열로 범위를 전환하며, 2강 문항은 이번 문항 집합에 다시 넣지 않습니다.</p></section>',
    kit.section("chromosome", "관계", "그림의 두 염색체를 관계로 읽기",
        T("chr-analogy", "c2 c4", B("prof") + " 교수님 비유: 이삿날에는 DNA 짐을 묶고, 복사본을 하나씩 나눕니다. 비유의 한계: 상동염색체는 복사본이 아니라 부모에게서 따로 받은 한 쌍입니다.") +
        diagram_chromosome() +
        T("chr-mechanism", "h1 c1 c2 c3 c4 c5 c6 c7 c8", "평상시에는 <b>염색질</b>, 분열기에는 DNA가 히스톤과 함께 응축된 <b>염색체</b>입니다. 그래서 분열 중인 세포가 많은 양파 뿌리 끝을 관찰 예로 씁니다. 복제된 한 염색체를 이루는 동일 사본 둘이 자매염색분체이고 동원체에서 붙습니다. 엄마 염색체와 아빠 염색체는 상동염색체이며 같은 A/a·B/b·C/c 자리에 다른 대립유전자가 있을 수 있습니다. 25번 그림의 X는 방추사 미세소관이 붙는 동원체 위치입니다.") +
        T("chr-warning", "c2 c4", "<b>⚠️ 판별 순서:</b> 복제로 생겼나? → 자매염색분체. 부모에게서 하나씩 왔나? → 상동염색체.", tag="div", cls="warn") +
        R("동원체와 자매염색분체를 각각 한 문장으로 말해 보세요.", "동원체는 자매염색분체가 붙는 부위이고, 자매염색분체는 S기 복제로 생긴 동일 사본 둘입니다.")),
    kit.section("division", "분리", "무엇이 갈라지는지를 먼저 본다",
        T("div-analogy", "d3 d4", B("gen") + " 생성 비유: 유사분열은 복사본을 두 상자에 한 장씩, 감수 I은 엄마판·아빠판을 먼저 갈라 담습니다. 비유의 한계: 실제 감수분열은 두 번의 핵분열과 복잡한 염색체 행동을 포함합니다.") +
        diagram_division() +
        T("div-mechanism", "d1 d2 d3 d4 d5 d6 d7", "2배체는 상동쌍을 갖고 반수체는 각 쌍에서 하나만 갖습니다. 이 수업에서는 n을 1배체가 아니라 <b>반수체</b>라고 부릅니다. 정자와 난자는 감수분열로 만들어지는 반수체 배우자이며, 한 사람이 만든 생식세포가 모두 유전적으로 동일하다고 단정할 수 없습니다. 다양성이 생기는 구체적 기작은 다음 회차에 배웁니다. 유사분열은 자매염색분체를 분리해 2n을 보존합니다. 감수 I은 상동염색체를, 감수 II는 자매염색분체를 분리합니다.") +
        T("div-warning", "d3 d4", "<b>⚠️ ‘상동’이면 감수 I, ‘자매’이면 유사분열 또는 감수 II를 먼저 떠올립니다.</b>", tag="div", cls="warn") +
        R("2n=46인 사람 세포가 유사분열하면 딸세포의 염색체 수는?", "각각 46개입니다. 유사분열은 염색체 수를 반으로 줄이지 않습니다."), prereqs=("chromosome",)),
    kit.section("cycle", "순서", "G1-S-G2-M과 멈춤 장치",
        T("cycle-analogy", "y4", B("prof") + " 교수님 비유: 보고서를 제출하기 전 학번·오타를 확인하고, 틀리면 고친 뒤 냅니다. 비유의 한계: 확인점은 의식적인 판단이 아니라 분자 신호망입니다.") +
        diagram_cycle() +
        T("cycle-mechanism", "h2 r0 y1 y2 y3 y4 y5 y6 y7 y8 y9", "0917은 3장 세포분열로 범위를 전환했습니다. G1은 성장, S는 DNA 합성, G2는 분열 준비와 복제 완료 확인, M은 <b>전기·중기·후기·말기</b>의 핵분열과 세포질분열입니다. G1·S·G2가 간기입니다. 사이클린 농도가 오르내리고 CDK와 결합해 다음 단계를 열며, 완료되지 않으면 확인점이 멈춥니다. 확인점은 DNA 복제 완료·방추사 부착·분열 시기 적절성을 검사합니다. 신경세포처럼 분열하지 않는 일부 세포는 G1에서 빠져나와 G0에 머뭅니다. 약 하루는 사람 세포의 강의 예시이며 주기 길이는 세포 종류와 G1 길이에 따라 달라집니다.") +
        T("cycle-warning", "y2 y4", "<b>⚠️ 이 수업의 문제 모형에서는 DNA 복제는 S기, 복제 완료 확인은 S기 뒤 G2 확인점입니다.</b>", tag="div", cls="warn") +
        R("DNA 중합효소가 가장 활발한 단계와 그 이유는?", "S기입니다. DNA 합성 자체가 일어나는 단계이기 때문입니다."), prereqs=("chromosome",)),
    kit.section("control", "조절", "가속 페달과 브레이크가 함께 필요하다",
        T("control-analogy", "a1 a2 a3", B("prof") + " 교수님 비유: 교수의 지시가 과대표·총무를 거쳐 학생에게 전달됩니다. 과대표가 고장나 지시 없이 계속 과제를 시키면 발암 유전자처럼 작동합니다. 비유의 한계: 실제 신호전달에는 많은 단백질과 되먹임이 있습니다.") +
        diagram_control() +
        T("control-mechanism", "a1 a2 a3 a4 a5 a6 a7 a8", "성장 신호가 수용체에 결합해야 전달 경로와 사이클린·CDK가 켜집니다. 원발암 유전자가 항상 켜지는 돌연변이를 얻으면 발암 유전자가 되고, 종양 억제 유전자가 고장나면 손상 수정과 정지가 어려워집니다. <b>p53과 BRCA1</b>이 대표적인 종양 억제 유전자입니다. BRCA1 변이는 위험을 높이지만 곧바로 암 진단을 뜻하지 않습니다. 강의는 이 사례로 자연 상태·가공 유전자 서열의 특허 구분과, 염기서열 분석이 더 빠르고 저렴해진 흐름도 소개했습니다. 보통 여러 변화가 축적되어 암으로 진행합니다.") +
        T("control-warning", "a3 a4", "<b>⚠️ 종양 억제 유전자 돌연변이 하나는 즉시 암 확정이 아니라, 돌연변이를 막거나 고칠 안전장치가 약해졌다는 뜻입니다.</b>", tag="div", cls="warn") +
        R("원발암 유전자와 발암 유전자의 차이는?", "원발암 유전자는 정상 분열 신호 유전자이고, 계속 켜지는 돌연변이형이 발암 유전자입니다."), prereqs=("cycle",)),
    kit.section("tumor", "확산", "덩어리와 암을 가르는 전이",
        T("tumor-analogy", "t1 t2 t3", B("gen") + " 생성 비유: 양성 종양은 자기 방 안에 머무는 손님, 악성 종양은 벽을 뚫고 다른 방까지 퍼지는 손님입니다. 비유의 한계: 실제 전이는 침윤·혈관 이동·정착의 여러 단계를 거칩니다.") +
        diagram_tumor() +
        T("tumor-mechanism", "t1 t2 t3 t4 t5 t6 t7 t8", "양성 종양은 자리에 머물지만 악성 종양은 주변을 침범하고 다른 곳으로 퍼질 수 있습니다. 이 확산이 전이입니다. 정상 세포는 서로 닿으면 멈추는 접촉 저해와 제한된 분열 횟수를 보이지만 암세포는 이를 잃을 수 있습니다. <b>HeLa</b>는 헨리에타 랙스의 자궁경부암에서 유래해 계속 분열하며 세포분열·항암제 연구에 널리 쓰인 세포주이고, 유족이 사용을 뒤늦게 안 동의·권리 문제도 남겼습니다. 강의의 정상세포 30~50회·HeLa 하루·대장균 20분과 암 관련 대여섯 개 돌연변이는 고정값이 아니라 조건과 누적 과정을 보여 주는 예시입니다.") +
        T("tumor-warning", "t3", "<b>⚠️ 문제에 ‘암세포의 특성이 아닌 것’이 나오면 접촉 저해 자체를 고릅니다. 암세포의 특징은 접촉 저해의 상실입니다.</b>", tag="div", cls="warn") +
        R("전이와 접촉 저해를 각각 정의해 보세요.", "전이는 암세포가 다른 곳으로 퍼지는 것이고, 접촉 저해는 정상 세포가 이웃과 닿으면 성장을 멈추는 성질입니다."), prereqs=("control",)),
]

BOUNDARY = '<section class="card boundary" id="boundary" data-role="boundary"><h2>이번 강의가 멈춘 곳</h2>' + T("boundary-b1", "b1", "0917은 세포주기 조절과 암까지 다루고 끝났습니다. 유사·감수분열의 단계별 그림, 재조합, 무작위 분배, DNA량 계산 17문항은 다음 회차 설명 뒤 풉니다.") + '</section>'
