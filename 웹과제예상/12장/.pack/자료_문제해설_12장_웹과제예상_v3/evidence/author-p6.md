# author-p6 (p6–p10) 근거

담당: p6–p10 새 예상문제(기출 원문 없음, original은 출처 안내). REPO=/Users/hyunjun_macbook_pro/Documents/Univ/생명과학
판정 전 blueprint.md·pack.json(answer_key p6 B, p7 E, p8 D, p9 C, p10 A)·cards/p6~p10.html·source.json choice.answer와 대조: 모두 일치. source.json과 카드 원문 일치.

## 읽은 자료

| 자료 | 경로 | SHA-256 |
| --- | --- | --- |
| 정리노트 1112 | REPO/복습노트/1112/정리노트_1112_Nervous_and_Sensory_Systems.html | 7bfa93631e19af1fcc36524d59d06b4b6653baf213d63d391562747d0dd18f94 |
| 정리노트 1117 | REPO/복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html | 6fe518f376cbf1a48f9592854b8bbf4967f183e746331dbabb630bcaf7abf28e |
| 강의노트 | REPO/강의노트/12장 신경계와 감각계.pdf (p1–4 텍스트) | ff1c6ce2762183da3cee56fed83a63bc6f24612f41fa0785e225cefd10a7eb14 |
| 교과서 | REPO/교과서/생명과학_기초와_응용_2판/12장_신경계_감각계_근육계.pdf (PDF 4·5·6·8·9·10쪽=교재 p.263·264·265·267·268·269, 이미지 판독) | 73de4f951a8ccc2c185423f8ad7a3c96acdba1ef6c142accd68ed8ace8484af7 |
| STT(보조) | REPO/STT/1112 생명.md 79·81·87·123행 | - |
| 설계 | REPO/웹과제예상/12장/.pack/v3/blueprint.md | a0d826166983753f4a8a0d37d0057754eeec60a09d166402f1b6fcb1be95aafc |
| 팩 | REPO/웹과제예상/12장/.pack/v3/pack.json | 3d63e4fd78089b15b9bbf153b0ce7ca318f15fe72f9295fcea63c7796134398f |

카드(SHA는 evidence/explanation-retry.json의 verified_snapshot 값): p6 397721d3…, p7 c551b4b8…, p8 85114bb3…, p9 5cdb54b3…, p10 f18bd299….

## 문항별

| 문항 | 링크 앵커(본문을 읽고 존재 확인) | 자료 위치 | 재풀이 | 답 |
| --- | --- | --- | --- | --- |
| p6 | 1112#s2-all-or-none | 강의노트 12장 p2(실무율·역치), 교재 p.264(실무율, 그림 12.5) | 카드 SVG 좌표를 직접 읽음: (가) y=36(+30) 봉우리 5개(x 109·145·181·217·253), (나) 최고 y=197로 역치선 y=190 아래, (다) 봉우리 1개(y=260=+30). 0→1→5, 높이 동일, (나)도 −70에서 상승 | B |
| p7 | 1112#s2-action(직접 근거: HTML의 "농도 차는 뒤집히지 않으며" 문단과 '활동전위 중 이온 농도 분포' 행), 1112#s1-channel-pump | 강의노트 12장 p2(펌프 3 Na⁺ 밖·2 K⁺ 안), 교재 p.264(펌프 방향·농도), p.265("K⁺ 이온이 그들의 농도기울기에 반응하여" 유출). '드나든 양은 극히 일부'의 직접 근거는 정리노트 1112 HTML뿐이고 대응 MD에는 아직 없음 | 통로 기준 채널: B·C·E / 농도 유지(K⁺ 안·Na⁺ 밖): A·E → 교집합 E. D는 Na⁺ 바깥만 참. pitfall의 '적은 이온 이동으로도 막전위 변화'는 같은 문단의 내용에서 이어짐 | E |
| p8 (부정형) | 1112#s0-neuron, #s2-conduction, #s3-release | 강의노트 12장 p1(뉴런 부위·랑비에 결절·말단의 분비), 교재 p.263(수상돌기·축삭말단·랑비에 결절), p.265(결절의 Na⁺ 통로와 활동전위), p.267 그림 12.7(Ca²⁺가 축삭말단으로) | 카드 SVG와 aria-label로 (가) 수상돌기, (나) 세포체, (다) 축삭 초기분절, (라) 첫째·둘째 덮개 사이 결절, (마) 말단 확인. A·B·C·E 참, D 거짓 | D |
| p9 | 1112#s4-removal, #s3-release | 교재 p.268(코카인의 재흡수 차단), p.267 그림 12.7(Ca²⁺→분비→수용체) | 대조와 다른 칸: P는 (1) 반응만, Q는 (2) 반응·제거 시간. 다섯 작용의 예측을 표와 대조: 모방만 (1) 반응 가능, 회수 차단만 분비량 동일+제거 지연 → P 모방·Q 회수 차단. 유일성은 카드의 '한 가지 작용만·그 밖의 조건 동일' 가정에 의존함을 understand·verify에 유지 | C |
| p10 | 1117#s1-spinal-reflex, 1112#s3-excite-inhibit | 강의노트 12장 p4(굽힘 반사: 한쪽 근육 수축·신근 이완), 교재 p.269(굴근 수축·신근 이완), 1117 노트 '팔을 펼 때' 행 | X −70→−76(역치 차 15→21 mV)·발화 없음 → 억제 → 이두근 이완 / Y −70→−55 역치 도달·발화 → 흥분 → 삼두근 수축 → 폄. 대표 뉴런·두 근육만의 작용이라는 가상 조건을 understand·verify·sum에 유지 | A |

## 자료 사이 표현 차이(답 영향 없음)

- p8 C: 교재 p.265는 "일단 활동전위가 뉴런의 수상돌기 끝에서 시작되면"이라고 쓰지만, STT 1112(79·81·87·123행)와 정리노트 1112 s0-neuron·s2-action은 수상돌기의 국소 변화가 퍼져 축삭 시작부(둔덕 다음 초기분절)에서 활동전위가 생긴다고 설명함. 기존 12장 팩(1112 복습문제·v2)도 초기분절 기준을 사용함. 보기 C는 '보통'이라는 한정이 있고, D는 교재 p.263·267로도 명백히 틀려 분석 답 D가 유지됨. 해설은 수업·정리노트 기준으로 씀. 내용 검토자가 disputed/결함 공개 필요 여부를 확인하도록 기록함.

## 원문 준수

새 문제를 기출로 표현하지 않음. 본문에 자료 쪽 출처 없음. 13장 내용, 골격 관련 용어, 원문자 없음(이두근·삼두근은 카드 용어). 선택 구역: p6 start, p7 pitfall, p8 start·pitfall, p9 start·pitfall·retry, p10 start·pitfall.
