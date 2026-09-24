import guide_kit as kit


SOURCES = [
    {"id": "note", "role": "note", "path": "0917.md", "label": "0917 범위 원천"},
    {"id": "stt", "role": "reference", "path": "../STT/0917 생명.md", "label": "0917 실강 STT"},
    {"id": "lecture", "role": "reference", "path": "../강의노트/3장 세포분열.pdf", "label": "3장 강의노트"},
    {"id": "quiz3", "role": "quiz", "path": "../23, 24 소스/3강 합본.pdf", "label": "3강 합본 원문"},
]

CONCEPTS = [
    ("chromosome", "염색체 관계 읽기", ()),
    ("division", "2n·n과 분리 대상", ("chromosome",)),
    ("cycle", "G1-S-G2-M과 확인점", ("chromosome",)),
    ("control", "세포주기 조절과 암 유전자", ("cycle",)),
    ("tumor", "양성·악성 종양과 전이", ("control",)),
]
kit.TITLES.update({c: title for c, title, _ in CONCEPTS})

ACTIVE = [1, 2, 3, 5, 7, 11, 14, 18, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 34, 36, 37, 38, 40]
DEFERRED_NUMBERS = [4, 6, 8, 9, 10, 12, 13, 15, 16, 17, 19, 21, 23, 32, 33, 35, 39]

BLOCKS = [
    ("header", 1, 20, "teaching", "제목·출처·30초 요약·장 경계", []),
    ("hela", 22, 34, "teaching", "HeLa와 분열 제한", ["3강:24", "3강:28", "3강:29"]),
    ("chromosome", 36, 54, "teaching", "염색체 관계", [f"3강:{n}" for n in (7, 25, 26, 27, 36, 37, 38)]),
    ("division", 56, 71, "teaching", "배수성과 분리 대상", [f"3강:{n}" for n in (3, 5, 11, 14, 22, 34)]),
    ("cycle", 73, 92, "teaching", "세포주기와 확인점", [f"3강:{n}" for n in (1, 2, 20, 30, 31, 40)]),
    ("control", 94, 127, "teaching", "사이클린·외부 신호·암 유전자", ["3강:18", "3강:28"]),
    ("tumor", 129, 141, "teaching", "종양과 전이", ["3강:24", "3강:29"]),
    ("boundary", 143, 149, "boundary", "다음 회차 경계와 보류 목록", [f"3강:{n}" for n in DEFERRED_NUMBERS]),
    ("supplement", 151, 165, "supplement", "강의노트·원문 문제 보충과 충돌", ["3강:18", "3강:20", "3강:25", "3강:30"]),
    ("mapping", 167, 200, "question_map", "생성 회상 변형과 활성 문항 매핑", [f"3강:{n}" for n in ACTIVE]),
]

F = kit.F
FACTS = [
    F("h1", "header", "definition", "chromosome", "복제 염색체는 동일한 자매염색분체 둘이 동원체로 붙은 구조다.", "S기 DNA 복제로 생긴 한 염색체의 동일한 두 사본이며 동원체에서 붙어 있다."),
    F("h2", "header", "direction", "cycle", "세포주기는 G1, S, G2, M 순서로 진행된다.", "G1 성장 → S DNA 복제 → G2 분열 준비·복제 확인 → M 핵분열·세포질분열 순서다."),
    F("r0", "header", "contrast", "cycle", "0917은 3장 세포분열 범위다.", "3장 세포분열"),
    F("c1", "chromosome", "contrast", "chromosome", "평상시의 풀린 DNA는 염색질이고 분열기의 응축된 형태는 염색체다.", "평상시 DNA는 정보를 읽어 쓸 수 있도록 비교적 풀린"),
    F("c2", "chromosome", "structure", "chromosome", "자매염색분체는 S기 복제로 생긴 한 염색체의 동일한 두 사본이다.", "복제된 한 염색체는 동일한 DNA 사본 둘이 붙은 형태"),
    F("c3", "chromosome", "structure", "chromosome", "동원체는 자매염색분체가 서로 붙어 있는 부위다.", "두 자매염색분체가 붙은 부위가"),
    F("c4", "chromosome", "contrast", "chromosome", "상동염색체는 부모에게서 하나씩 받은 같은 종류의 염색체로 같은 유전자 자리에 다른 대립유전자가 있을 수 있다.", "엄마와 아빠에게서 하나씩 받은 같은 종류의 염색체다."),
    F("c5", "division", "quantity", "chromosome", "사람 체세포의 염색체 46개는 23쌍의 상동염색체다.", "사람 체세포는 2n=46, 즉 상동염색체 23쌍"),
    F("c6", "supplement", "structure", "chromosome", "3강 25번 그림의 X는 방추사 미세소관이 부착되는 동원체 위치다.", "X는 방추사 미세소관이 붙는 동원체 위치다."),
    F("c7", "supplement", "contrast", "chromosome", "3강 25번 그림에서 A·B·C는 서로 다른 유전자 자리이고 A와 a는 같은 자리의 대립유전자다.", "A와 a처럼 같은 자리의 다른 버전은 대립유전자다."),
    F("c8", "chromosome", "condition", "chromosome", "염색체는 분열기에 DNA가 히스톤과 함께 응축될 때 관찰하기 쉬워 분열 중인 양파 뿌리 끝을 예로 사용한다.", "분열 중인 세포가 많은 양파 뿌리 끝 같은 조직을 사용한다."),
    F("d1", "division", "definition", "division", "2배체는 상동염색체 쌍을 갖고 반수체는 각 쌍에서 하나만 갖는다.", "상동염색체 쌍을 가진 세포는"),
    F("d2", "division", "quantity", "division", "사람 체세포는 2n=46이고 생식세포는 n=23이다.", "사람의 정자와 난자는 n=23인 반수체 배우자다."),
    F("d3", "division", "process_step", "division", "유사분열에서는 자매염색분체가 분리되어 같은 염색체 수의 딸세포 둘을 만든다.", "유사분열에서는 복제된 염색체의", dims={"location": "유사분열 M기", "input": "복제된 2배체 부모세포", "output": "부모와 같은 염색체 수의 딸세포 2개"}),
    F("d4", "division", "process_step", "division", "감수분열 I에서는 상동염색체, 감수분열 II에서는 자매염색분체가 분리된다.", "감수분열 I: 상동염색체가 분리", dims={"location": "감수분열 I과 II", "input": "상동염색체 쌍과 복제 염색체", "output": "상동염색체 분리 뒤 자매염색분체 분리"}),
    F("d5", "division", "condition", "division", "정자와 난자는 감수분열로 만들어지는 반수체 배우자로 각 상동염색체 쌍에서 하나씩 가진다.", "각 쌍에서 하나만 가진 세포는"),
    F("d6", "division", "exception", "division", "n 상태는 이 수업에서 1배체가 아니라 반수체라고 부른다.", "반수체를 ‘1배체’라고 부르지 않는다"),
    F("d7", "supplement", "condition", "division", "한 사람이 만든 정자나 난자가 모두 유전적으로 동일하다고 단정할 수 없으며 다양성의 구체적 기작은 다음 회차 범위다.", "한 사람이 만든 정자나 난자를 모두 유전적으로 동일하다고 단정할 수는 없"),
    F("y1", "cycle", "direction", "cycle", "세포주기는 G1에서 성장, S에서 DNA 복제, G2에서 준비·확인, M에서 핵분열과 세포질분열 순으로 진행된다.", "한 번 분열한 세포가 다음 분열을 마칠 때까지의 반복 과정이다."),
    F("y2", "cycle", "process_step", "cycle", "S기에는 DNA가 복제되고 G2 확인점은 복제가 정상적으로 끝났는지 검사한다.", "S기는 DNA를 복제하는 단계이고", dims={"location": "핵의 S기와 S기 뒤 G2 확인점", "input": "복제 전 DNA", "output": "복제 DNA와 통과 또는 정지 신호"}),
    F("y3", "cycle", "definition", "cycle", "간기는 G1·S·G2이며 세포는 대부분의 시간을 간기에 보낸다.", "G1·S·G2를 합쳐"),
    F("y4", "cycle", "condition", "cycle", "확인점은 이전 단계가 완결되지 않으면 세포주기를 멈춘다.", "앞 단계가 끝나지 않았거나 문제가 있으면 다음 단계 진행을 멈춘다."),
    F("y5", "supplement", "condition", "cycle", "사이클린은 농도가 주기적으로 변하며 CDK와 결합해 세포주기를 진행시킨다.", "사이클린 농도가 세포주기에 따라 변한다고 명시한다."),
    F("y6", "cycle", "exception", "cycle", "분열하지 않는 신경세포처럼 일부 세포는 G1에서 빠져나와 G0에 머문다.", "신경세포처럼 분열하지 않는 세포는"),
    F("y7", "supplement", "definition", "cycle", "유사분열 M기는 전기·중기·후기·말기로 나뉜다.", "전기·중기·후기·말기로 나눈다."),
    F("y8", "cycle", "condition", "cycle", "세포주기 길이는 세포 종류와 G1 길이에 따라 달라지며 약 하루는 사람 세포의 강의 예시다.", "G1 길이가 세포 종류마다 달라 전체 주기도 달라진다."),
    F("y9", "cycle", "condition", "cycle", "확인점은 DNA 복제 완료, 방추사 부착, 분열 시기 적절성을 검사한다.", "DNA 복제가 제대로 끝났는지, 방추사가 염색체에 제대로 붙었는지, 지금이 분열할 시기인지 확인"),
    F("a1", "control", "process_step", "control", "외부 성장 신호는 수용체와 세포내 전달 단백질을 거쳐 사이클린·CDK를 활성화한다.", "신호분자가 알맞은", dims={"location": "세포막 수용체에서 세포 내부", "input": "성장인자 신호", "output": "사이클린·CDK 활성과 분열 진행"}),
    F("a2", "control", "contrast", "control", "정상 분열 촉진 유전자는 원발암 유전자이고 신호 없이 계속 켜지는 돌연변이형은 발암 유전자다.", "정상적인 성장 신호가 있을 때만 분열을 촉진하는 유전자를"),
    F("a3", "control", "condition", "control", "종양 억제 유전자는 손상 DNA를 고치거나 분열을 멈추며 기능 상실 시 돌연변이 축적 위험이 커진다.", "세포주기를 멈추고 손상된 DNA를 고치도록 돕는다."),
    F("a4", "tumor", "condition", "control", "암은 보통 여러 돌연변이가 단계적으로 축적되며 발생한다.", "여러 돌연변이가 차례로 축적"),
    F("a5", "control", "definition", "control", "p53과 BRCA1은 대표적인 종양 억제 유전자다.", "p53과 BRCA1이 대표적인 예다."),
    F("a6", "control", "condition", "control", "BRCA1 변이는 암 위험을 높이지만 곧바로 암 진단을 뜻하지 않는다.", "종양 억제 유전자 변이가 위험을 높이지만 곧바로 암 진단을 뜻하지는 않는다"),
    F("a7", "control", "contrast", "control", "강의의 BRCA1 사례는 자연 상태 유전자 서열과 사람이 가공한 서열의 특허 가능성을 구분한다.", "자연 상태의 인간 유전자 서열과 사람이 가공한 서열의 특허 가능성"),
    F("a8", "control", "direction", "control", "염기서열 분석 기술은 세대가 발전하며 더 빠르고 저렴해졌다는 흐름으로 소개되었다.", "염기서열 분석 기술의 비용·속도 변화도 소개했다."),
    F("t1", "tumor", "contrast", "tumor", "양성 종양은 자리에 머물고 악성 종양은 주변 침범이나 전이가 가능하다.", "원래 위치에 머물면"),
    F("t2", "tumor", "definition", "tumor", "전이는 암세포가 원래 위치를 벗어나 신체의 다른 곳으로 퍼지는 과정이다.", "암세포가 원래 위치를 떠나 다른 곳으로 퍼지는 과정"),
    F("t3", "tumor", "contrast", "tumor", "정상 세포는 접촉 저해를 보이지만 암세포는 이를 잃어 겹쳐 자랄 수 있다.", "암세포는 접촉 저해를 잃어"),
    F("t4", "hela", "definition", "tumor", "HeLa는 헨리에타 랙스의 자궁경부암에서 유래해 계속 분열하며 연구에 쓰인 세포주다.", "헨리에타 랙스의 자궁경부암에서 유래한 세포주다."),
    F("t5", "hela", "contrast", "tumor", "정상 사람 세포는 보통 분열 횟수가 제한되지만 암세포주는 계속 증식할 수 있다.", "정상 사람 세포는 보통 분열 횟수가 제한"),
    F("t6", "hela", "condition", "tumor", "HeLa 연구에는 유족이 세포 사용을 뒤늦게 안 동의·권리 문제가 함께 남는다.", "유족이 세포 사용을 뒤늦게 알았다는 이야기는"),
    F("t7", "hela", "quantity", "tumor", "강의의 30~50회·하루·20분 수치는 세포 종류와 조건에 따라 분열 속도가 다름을 보여 주는 예시다.", "이 수치는 모든 세포의 고정값이 아니라"),
    F("t8", "tumor", "condition", "tumor", "강의의 대여섯 개 돌연변이는 누적 과정을 보여 주는 예시이며 모든 암의 고정 문턱값이 아니다.", "모든 암에 적용되는 고정 문턱값은 아니다."),
    F("b1", "boundary", "condition", "division", "단계별 유사·감수분열과 재조합·DNA량 계산은 다음 회차 범위다.", "유사분열과 감수분열의 단계별 과정·그림 비교가 이어진다."),
]
