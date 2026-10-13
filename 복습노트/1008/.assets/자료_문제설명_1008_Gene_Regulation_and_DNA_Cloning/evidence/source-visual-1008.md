# source_visual 검토 1008 (reviewer: content/source_visual 검토 에이전트, 저작 에이전트와 별개)

방법: 기출은 `23, 24 소스/5강 합본.pdf`·`6강 합본.pdf` 1~5쪽을 pdftotext -layout으로 추출해 카드(source.json)의 발문·보기와 글자 단위로 대조. pdfimages 결과 1~5쪽에 삽입 이미지 0개(그림 없는 텍스트 문항). 인쇄 답은 `.pack/key-check.md`(PNG 육안 확인 기록)와 대조. 생성 변형은 `복습노트/1008/.pack/variants.md` 같은 id 행의 '문제 요지'와 카드 발문을 문자열 비교(12문항 모두 완전 일치), '의도한 정답'·'오답 보기의 의도' 열과 보기 순서 대조, 근거 토픽 anchor가 `정리노트_1008_Gene_Regulation_and_DNA_Cloning.md`에 존재함을 확인. 그림 문항 p12·p17은 카드 SVG를 `복습노트/1008/figures_1008/p12-exam.svg`·`p17-exam.svg`(aria-label 동일)와 대조.

| id | 원자료(파일·쪽) | 대조 결과 | pass/fail |
|---|---|---|---|
| p1 | 5강 합본.pdf PDF 2쪽, 13번 | 발문·보기 (1)~(5) 원문과 동일. 그림 없음. 인쇄 답 ⑤ = 카드 (5) | pass |
| p2 | 5강 합본.pdf PDF 3쪽, 24번 | 보기 (3) 카드 "두 세포는" vs 원문 "두 세포가" — 주격/보조사 차이일 뿐 주어·서술 내용(같은 유전자로 출발 → 차등 제거) 동일, 판정 결과 불변. 나머지 글자 동일. 인쇄 답 ① = 카드 (1). 차기 재생성 시 "가"로 맞추기 권장(발행 차단 아님) | pass |
| p3 | 5강 합본.pdf PDF 4쪽, 33번 | 발문·보기 5개 동일. 인쇄 답 ④ = 카드 (4) | pass |
| p4 | 5강 합본.pdf PDF 5쪽, 45번 | 발문·보기 5개 동일. 인쇄 답 ③ = 카드 (3) | pass |
| p5 | 6강 합본.pdf PDF 1쪽, 1번 | 발문·보기 동일. 인쇄 답 ① = 카드 (1) | pass |
| p6 | 6강 합본.pdf PDF 2쪽, 10번 | 발문·보기 동일. 인쇄 답 ③ = 카드 (3) | pass |
| p7 | 6강 합본.pdf PDF 2쪽, 11번 | 발문·보기 동일(원문도 마침표 없음). 인쇄 답 ⑤ = 카드 (5) | pass |
| p8 | 6강 합본.pdf PDF 2쪽(발문)~3쪽(보기), 17번 | 발문·보기 4개 동일. 카드 표기 "PDF 2쪽"은 발문 위치 기준, 보기는 3쪽으로 이어짐(설명 조각은 "PDF 2~3쪽"으로 정확히 표기). 인쇄 답 ③ = 카드 (3) | pass |
| p9 | 6강 합본.pdf PDF 4쪽, 28번 | 발문·보기 4개 동일. 인쇄 답 ④ = 카드 (4) | pass |
| p10 | variants.md p10 행, 정리노트 #s0-chromatin, 교과서 05장 PDF22(p.113) | 발문 = 문제 요지 완전 일치. 정답 (2)=의도 정답. 오답 4개가 오답 의도 열과 순서대로 대응 | pass |
| p11 | variants.md p11 행(기출 5강 33 발문 유지), 정리노트 #s1-initiation, 교과서 p.113 | 발문 일치(원문 33번 발문과도 동일). (4) 증폭자=RNA 중합효소 거짓, 나머지 TATA/메틸화/아세틸화/억제자 참 = 설계와 일치. 정답 (4) | pass |
| p12 | variants.md p12 행, 정리노트 #s2-splicing, 교과서 p.114~115, figures_1008/p12-exam.svg | 발문 일치. 그림: 최초 RNA A·B·C(인트론 연결선), mRNA1 A-B-C, mRNA2 A-C — 설계("A-B-C와 A-C, 순서 유지")와 일치, 저장소 SVG와 동일 내용. 정답 (3) | pass |
| p13 | variants.md p13 행, 정리노트 #s2-rnai, 교과서 p.114 그림 5.23 | 발문 일치, 정답 (1) | pass |
| p14 | variants.md p14 행, 정리노트 #s3-translation, 교과서 p.112 그림 5.21·p.115 | 발문 일치, 정답 (5), 오답 의도 4개 순서 대응 | pass |
| p15 | variants.md p15 행, 정리노트 #s3-proteasome, 교과서 p.115 | 발문 일치, 정답 (2) | pass |
| p16 | variants.md p16 행, 정리노트 #s4-vector | 발문 일치(“다른 프로모터는 없다” 조건 포함), 정답 (4) | pass |
| p17 | variants.md p17 행, 정리노트 #s5-restriction, 교과서 06장 PDF4(p.121), figures_1008/p17-exam.svg | 발문 일치. 그림 A 5′GAATTC3′/3′CTTAAG5′, B 5′GATTAC3′/3′CTAATG5′ — 상보 관계 정확, 설계와 동일. 정답 (1) | pass |
| p18 | variants.md p18 행(기출 6강 11 발문 유지), 정리노트 #s5-restriction, 교과서 p.121 그림 6.3 | 발문 일치, 정답 (3), 오답 의도 대응 | pass |
| p19 | variants.md p19 행, 정리노트 #s5-ligation, 교과서 p.121 그림 6.3 ③ | 발문 일치, 정답 (5) | pass |
| p20 | variants.md p20 행, 정리노트 #s5-cloning, 교과서 06장 PDF3(p.120) 그림 6.2 ⑤ | 발문 일치, 정답 (2) | pass |
| p21 | variants.md p21 행, 정리노트 #s1-initiation(DNA 굽힘 그림), 교과서 p.113 | 발문 일치, 정답 (4) | pass |

종합: pass (21/21). 의미를 바꾸는 불일치 없음. 비차단 메모 2건: p2 "는/가" 조사 차이, p8 쪽 표기(보기가 3쪽으로 이어짐).
