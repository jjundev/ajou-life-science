# source_visual 검토 — 12장 웹과제 예상 v3

검토자: source_visual 검토 에이전트(저작자와 별도). 렌더해 본 기출 쪽: `23, 24 소스/12강 합본.pdf` p.1·3·4·5(4쪽). 교과서·강의노트 PDF는 열지 않음.

- 원문 대조: `python3 .agents/skills/bio-webquiz-forecast/scripts/check.py --strict <v3 HTML>` → `OK`, exit 0. `[exam-verbatim]`·`[exam-twin]`·`[exam-number]` 지적 0.
- 추출 대조: source.json의 문제 HTML SHA-256과 context_hashes 5개가 현재 파일과 일치. p1–p15 source.json 발문·보기 = cards/pN.html, 추출 정답 = pack.json answer_key, 발문·보기가 stage HTML에 모두 존재(p9·p10 표 텍스트 포함).
- 그림 대조: p4·p6·p8·p12·p13의 카드 SVG = stage HTML 인라인 SVG(요소·좌표 동일), stage figures 파일 5개는 이름표가 같고 요소 1개(배경) 추가. 카드·stage(light/dark)·figures 파일을 Chromium으로 렌더해 직접 봄. 잘림·겹침 없음.

| 문항 | 원자료·위치 | 대조 결과 | 판정 |
| --- | --- | --- | --- |
| p1 | 12강 합본 8번, p.1 | 발문 원문 그대로(`__시킨다` 포함), 보기 5개 문구 동일·순서만 변경. 인쇄(빨강) 정답 ④감소 = 카드 E | pass |
| p2 | 12강 합본 41번, 발문 p.4·보기 p.5 | 발문·보기 5개 원문 그대로, 순서만 변경. 인쇄 정답 1(세 가지 종류의 포톱신) = 카드 B | pass |
| p3 | 12강 합본 33번, 발문 p.3·보기 p.4 | 발문 원문 그대로, 보기 교체 쌍둥이. 원문 정답 ①보기 모두 가능성(재흡수 방지·분해 억제·합성 증가·수용체 증가) ↔ 새 정답 D(소포 융합 증가). “네 방법 묶음” 안내가 원문과 일치 | pass |
| p4 | 12강 합본 35번, p.4(발문·그림·보기) | 발문 원문 그대로(‘위 그림’ 포함). 원본 그림 1 활동전위 도착·2 전압개폐성 Ca²⁺ 채널·3 소포와 시냅스전세포막 융합·4 틈을 건너 결합·5 리간드개폐성 이온채널 ↔ 새 그림 활동전위 화살표·(가)·(나)·(다)+결합 알갱이·(라)로 대응. 원문 정답 ②(소포가 시냅스후막으로 함입) ↔ 새 정답 A((라)가 막전위로 열림), 1112 s3-release와 일치 | pass |
| p5 | 12강 합본 7번, p.1 | 발문 원문 그대로. 원문 ①추론 ②음악·예술(정답) ③말하기 ④쓰기 ⑤수학 ↔ 카드 B·정답 교체·A·D·E, 정답 C 공간 인지. 1117 s3-hemispheres와 일치 | pass |
| p6 | 1112 정리노트 s2-all-or-none | (나) 역치 아래 변화·(다) +30 봉우리 1개·(가) +30 봉우리 5개, −70/−55/+30 눈금과 자극 막대 동일. 높이 일정·빈도 증가가 노트와 일치, 정답 B | pass |
| p7 | 1112 정리노트 HTML s2-action, MD s1-channel-pump | 드나드는 이온 극히 일부·농도 차 유지·K⁺ 채널 유출, 펌프는 Na⁺ 밖·K⁺ 안이 노트와 일치, 정답 E | pass |
| p8 | 1112 정리노트 s0-neuron, s2-conduction·s3-release | 지시선이 (가) 가지 (나) 핵 있는 둥근 부분 (다) 좁아진 자리 다음 (라) 첫째·둘째 덮개 사이 (마) 갈라진 끝을 가리킴. 보기 A–E의 부위와 대응, 정답 D | pass |
| p9 | 1112 정리노트 s4-removal | 모르핀형 직접 결합, 재흡수 억제의 틈 잔류 연장, 분비량·제거량 구별이 노트와 일치. 표 stage와 일치, 정답 C | pass |
| p10 | 1117 정리노트 s1-spinal-reflex | 펼 때 이두근 이완·억제성, 삼두근 수축·흥분성이 노트 표와 일치. 표 stage와 일치, 정답 A | pass |
| p11 | 1117 정리노트 s2-thalamus | 척수→뇌간 중심부(망상체)→시상→대뇌, 망상체 필터·시상 중계가 노트와 일치, 정답 E | pass |
| p12 | 1117 정리노트 s3-lobes·s3-imaging | 앞쪽 화살표 오른쪽, (가) 오른쪽 위 전두엽·(나) 아래 측두엽·(다) 왼쪽 위 두정엽·(라) 왼쪽 끝 후두엽. 체성 감각=두정엽, PET 포도당이 노트와 일치, 정답 C | pass |
| p13 | 1117 정리노트 s4-hearing | 오른쪽 타원창 옆 좁은 쪽 모세포 3개가 ×, 범례·손상 구간 괄호 표시됨. 좁은 앞부분=높은 음, 넓은 끝=낮은 음이 노트와 일치, 정답 B((가)~(마) 기호는 쓰지 않는 그림) | pass |
| p14 | 1117 정리노트 s5-photoreceptors·s4-hearing | 간상세포 빛에 글루탐산 분비 감소, 모세포 굽힘이 분비 자극·활동전위는 청각 신경이 노트와 일치, 정답 A | pass |
| p15 | 1117 정리노트 s5-retina·s5-eye·s5-photoreceptors | 약한 빛 동공 커짐·간상세포만 반응·중심오목에 간상세포 없음·주변 망막에 많음이 노트와 일치, 정답 D | pass |

노트 앵커 16개(1112 7개·1117 9개)가 해당 정리노트 HTML에 존재함. 결함 0(source_visual-fixes.tsv 없음).

## attempt 1 재확인 (현재 stage/c7fff84fe4b64710a8afcf7fd27ea3cb)

input_hash `9d8cc069294ffd6506f0cb1c4f99f5f4e88cff7d169e79d1ee2d8a6b12ccaa81`, 이전 stage `a03170b4cb4d42d199b81ba0c6753954`. PDF는 다시 렌더하지 않음(문제 카드와 원자료 대조 결과가 바뀌지 않음).

- 문제 HTML SHA-256·context_hashes 5개·카드 15개 SHA-256(review.json references)이 현재 파일과 일치. 15문항 카드 발문·보기 = source.json, 정답 = answer_key, 발문·보기·p9/p10 표가 현재 stage HTML에 모두 있음.
- 현재 stage HTML과 이전 stage의 줄 단위 차이는 해설 문단 2개뿐(p8 recall, p12 pitfall). 문제 본문·보기·원문 안내·SVG는 차이 0.
- p4·p6·p8·p12·p13: 카드 SVG = stage 인라인 SVG, figures 파일은 배경 사각형 1개만 추가되고 나머지 요소·이름표 동일. figures 5개의 SHA-256이 이전 stage와 같아 앞의 렌더 확인을 그대로 적용.
- 그 밖에 달라진 stage 파일: 해설 MD, fragments p8·p12, manifest, evidence. p1–p15 판정 모두 pass 유지, 결함 0.
