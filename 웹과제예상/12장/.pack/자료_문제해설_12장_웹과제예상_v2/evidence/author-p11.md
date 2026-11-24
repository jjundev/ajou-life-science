# 저작 근거 기록 (p11–p15 · 12장 웹과제 예상 v2)

- 작업 대상: `복습문제_12장_웹과제예상_v2.html`의 p11, p12, p13, p14, p15 (모두 새 예상 문항)
- 참조 파일:
  - `source.json`: `/Users/hyunjun_macbook_pro/.gemini/antigravity/brain/51246bb2-fce7-4587-a6fe-acdd58ec65d4/scratch/bio-problem-explain/12장-웹과제예상-v2/forecast-12장-웹과제예상_v2/source.json`
  - `pack.json`: `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제예상/12장/.pack/v2/pack.json`
  - `blueprint.md`: `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제예상/12장/.pack/v2/blueprint.md`
  - 1117 정리노트 MD: `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1117/.assets/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.md`
  - 1117 정리노트 HTML: `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html`

## 문항별 근거 및 대조 결과

| 문항 | 정답 (카드 / pack.json / 독립 재풀이) | 원자료 충돌·결함 | 확인한 정리노트 앵커 (HTML·MD 모두 확인) | 확인한 강의노트·교재·수업 근거 (해설 본문 생략) |
| --- | --- | --- | --- | --- |
| p11 | E / E / E (일치) | 없음 | `../../복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html#s2-brainstem` (HTML L786, MD L388–477) | 1117 수업 · 강의노트 12장 p4. 연수(호흡 리듬 생성·심박수·구토/삼키기 반사), 뇌교(호흡 리듬 다듬기), 중뇌(안구 운동), 뇌사(뇌간 포함 전체 기능 상실·인공호흡기 필요) vs 식물인간(뇌간 생존·자발 호흡 가능). |
| p12 | B / B / B (일치) | 없음 | `../../복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html#s3-hemispheres` (HTML L1230, MD L849–936) | 1117 수업 · 강의노트 12장 p4–p5. 시야 기준 교차(두 눈 왼쪽 시야 → 우반구), 뇌량 절단 시 반구 간 전달만 차단, 언어 중추(좌반구), 교차 운동 지배(우반구 → 왼손). |
| p13 | D / D / D (일치) | 없음 | `../../복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html#s3-lobes` (HTML L1065, MD L672–761), `#s3-imaging` (HTML L1151, MD L764–846) | 1117 수업 · 강의노트 12장 p4–p5, 교재 12장 p.270·p.272 그림 12.13. 브로카(전두엽·표현)·베르니케(두정엽·측두엽 경계·이해), PET(방사성 표지 포도당 소모), fMRI(혈류·산소 소모 간접 측정), EEG(두피 전극 전기 신호 직접 측정, `#s3-hemispheres`), DMN(휴식 시 활성). |
| p14 | A / A / A (일치) | 없음 | `../../복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html#s5-eye` (HTML L1576, MD L1170–1250) | 1117 수업 · 강의노트 12장 p6, 교재 12장 p.276. 모양체근(강의노트)=섬모체근(수업, ciliary muscle). 수축 → 인대 장력 감소 → 수정체 구형(두꺼움) → 가까운 물체; 이완 → 인대 당김 → 수정체 얇아짐 → 먼 물체. 홍채는 동공 크기 조절. |
| p15 | C / C / C (일치) | 없음 | `../../복습노트/1117/정리노트_1117_Nervous_and_Sensory_Systems_and_Respiratory_and_Circulatory_Systems.html#s4-receptors` (HTML L1344, MD L943–1018) | 1117 수업 · 강의노트 12장 p5, 교재 12장 p.277. 자극 종류별 5유형(기계·광·화학·온도·통각), 청각·고유 수용기=기계 수용기, 5가지 기본 맛(짠·단·쓴·신·감칠맛)·후각=화학 수용기, 캡사이신(매운맛)=통각 수용기(nociceptor), 온도 수용기=피부+시상하부. |

## 점검 메모

- 모든 문항(p11–p15)은 `source.json`의 `subparts: ["main"]`에 맞춰 `solve`·`verify`에 `data-subpart="main"`을 1회씩 배치했다.
- 부정형 문항(p11, p13, p15)은 `understand`에 질문 방향을 `<strong>`으로 강조했고, 결론 문단에 부정형 선택 방향을 밝혔다.
- 모든 `recall`에 실제 확인된 1117 정리노트 개념 앵커 링크를 1개 이상 넣었으며, 해설 본문·요약에는 `(교재 ...)`, `(강의노트 ...)` 같은 자료 위치 출처를 쓰지 않았다.
- `pack.json`의 `forbidden` 금지어(호흡계·골격계·면역계 등)가 p11–p15 해설에 포함되지 않도록 확인했다.
