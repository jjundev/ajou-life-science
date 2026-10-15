# 1015 문제설명 독립 content 검토

검토자: explain_review 독립 검토 에이전트 (설명 저작에 참여하지 않음).
상태: pass. 최종 source.json의 19문항 및 최종 explanations/p1.html~p19.html을 각각 전체 읽고 판단함. 일괄 추정 승인이 아님.

범위: understand/recall/start/solve/verify/pitfall/retry, 7구역 순서·main 표지·부정형 방향·실제 첫 줄·모든 보기 판정·요약 일치·자료 충돌 공개. 정답 비공개 독립 재풀이는 별도 evidence/independent-1015.md 담당이며 이 보고서는 content 검토임.

읽은 근거: 최종 정리노트_1015_Genomics_and_CRISPR.html 전체, 교재 실제 PNG book-11·13~20 (인쇄128·130~137), slides.txt의 6장 p3~4, authoring.md·verification.md, 최종 source.json 및 independent-1015.md. 원문 기출 PDF의 별도 시각 대조는 source-visual.md의 책임 범위로 유지함.

|문항(main)|판정|답|실제 확인한 근거·내용|
|---|---|---|---|
|p1:main|pass|3 조건부|암호화 DNA를 cDNA와 동일시하지 않고 understand·solve·pitfall에서 cDNA 해석 조건과 원문 결함을 공개. RNA→cDNA→탐침 결합→발현 비교를 적용 조건과 연결. 다섯 보기 및 인쇄 답의 조건부 유지가 교재 p131·133과 일치.|
|p2:main|pass|4|데이터베이스·서열 단서에서 생물정보학 정의와 계산 분석을 연결. 분자생물학의 넓은 범위, 유전공학·단백질체학·시스템생물학을 실제 작업 기준으로 구분. 교재 p130/p132 정의 대조 검산.|
|p3:main|pass|2|부정형 방향을 굵게 밝혔고 모든 보기 판정. CCR5 효과를 해당 수용체 이용 경로로 한정하는 문항 결함 공개가 understand·solve·pitfall에 있음. 발광 담배의 특정 교재 사례가 고전 형질전환이라는 기준을 적용하고 CRISPR 삽입 가능성도 보존. p128/136/137과 일치.|
|p4:main|pass|4|최종 원문의 250,000을 25만으로 읽어 25,000과 구분. 염기쌍 수와 유전자 수의 단위, 초기 예상보다 적음, 다른 종 적용 가능성을 모두 정확히 판정. ACGT+GTAA→ACGTAA의 중첩 예와 교재 p131/133 대조로 단일4를 검산.|
|p5:main|pass|2|원하는 표적의 안내·절단 단서에서 guide RNA/Cas9을 구분. 제한효소도 DNA를 자른다는 사실을 숨기지 않고 표적 설계 맥락으로 비교. 각 도구와 cDNA의 물질·기능 판정이 정확. 교재 p134~135 및 강의 p6 대조.|
|p6:main|pass|4|부정형 방향 명시. 특정 세포·조건의 전체 집합과 몇몇 단백질을 구분. 선택적 이어맞추기와 단백질 변형으로 단백질 종류 증가 가능성을 설명. 다섯 보기의 판단과 p131~132의 정의·연구과제·약 개발 대조가 타당.|
|p7:main|pass|3|부정형 방향 명시. 미지 유전자 발견 증가와 인간 유전자 총수의 초기 예상 대비 감소를 다른 비교로 명확히 분리. 암호화 서열 조건을 붙여 아미노산 추론을 설명. p130·131 대조로 두 많다의 혼동을 독립 검산.|
|p8:main|pass|4|변형의 현재 (3)이 유전체 전체 서열 직접 해독임을 정확히 반영. RNA 유래 cDNA와 결합 신호를 측정 원리로 설명하고 다섯 보기 판정. 원문의 조건부3 기억으로 바꾸지 않음. 노트 실험 순서/교재 p131 대조.|
|p9:main|pass|2|부정형 방향 명시. 전체 단백질 집합·조건 의존·약물 표적과 수의 관계를 구별. 언제나 같다는 주장에 엑손 조합 1·2/1·3이라는 기전적 반례를 제시. 답 및 요약이 본문과 일치.|
|p10:main|pass|3|같은 전구RNA 및 A·B/A·C라는 실제 도식 단서를 읽고 RNA 가공 개념을 선택. 엑손/인트론 정의와 적용 조건을 설명. DNA 삭제/염색체 수/단백질→DNA 전환과 혼동하지 않음. 그림 다시 읽기와 교재 p131로 검산.|
|p11:main|pass|2|전사 산물=RNA와 절단 효소=단백질이라는 물질 종류 기준 및 상보성 안내 원리를 설명. 실제 첫 줄에서 두 자리를 구분. 다섯 조합 모두 판정하고 물질 종류 소거 및 교재 p135 구성 요소로 검산.|
|p12:main|pass|3|같은 DNA와 조건별 RNA 양을 별개의 정보로 구분. 측정조건을 맞춘다는 전제와 RNA→DNA→결합 신호 기전을 연결. 다섯 방법 모두 판정하고 실험 입력/출력이 질문 목표와 연결되는지 검산.|
|p13:main|pass|2|1염기 결실·관찰된 읽는 틀 변화를 단서로 암호화 부위/3염기 코돈 조건을 설명. 재연결≠원래 기능 보존과 Cas9/수선 역할 구분이 정확. 실제 염기서열이 아님을 밝힌 ABC 묶음 예가 타당한 독립 구조 검산이며 모든 indel 일반화도 경계.|
|p14:main|pass|4|부정형 방향 명시. 다른 조건이 같을 때 긴 서열의 완전 일치가 더 어려운 원리와 부분 유사서열 오프타깃을 구분. 다섯 보기 및 수업 비교 판정이 정확. 교재 p137의 실제 반례가 완전히 사라짐 주장을 반박.|
|p15:main|pass|5|부정형 방향 명시. 생명정보학 동의어, 서열 비교·코딩서열 아미노산 추론과 모든 실제 기능 확정의 구별을 단서부터 설명. 다섯 보기별 근거가 있고 분석 출력/기능 연구 질문을 분리한 검산이 유효.|
|p16:main|pass|4|같은 DNA/같은 총량/다른 엑손조합이라는 실제 조건을 정확히 분리. 선택적 이어맞추기와 단백질체의 종류 정보를 연결. 양이 같으면 종류도 같다는 주장을 100개씩의 다른 조합 예로 반박하며 다섯 보기 모두 판정.|
|p17:main|pass|3|부정형 방향 명시. 결실/다른위치절단/생존 관찰의 서로 다른 범주를 단서와 원리로 연결. 생존이 모든 기능 안전성을 뜻하지 않음을 결론 범위와 자료 범위로 검산. 기능 변화 가능을 필연적 죽음으로 과장하지 않음.|
|p18:main|pass|4|성숙면역세포=체세포, CCR5 이용 경로의 제한된 목표, 미완료 안전성 검사를 각각 해석. 후손 전달/완전면역/검사생략/기능유지 보장을 모두 반박. 세 칸 검산과 교재 p137·강의 p3~4 대조가 타당. 강의 p3~4 원문 텍스트에서 실제 구분을 확인.|
|p19:main|pass|2|암호화 여부와 생물학적 기능 여부를 별개 기준으로 가르침. promoter/전사 조절의 실제 반례와 전체 DNA 범위를 연결. 다섯 보기 판정과 교재 p131/반례 검산이 정확. solve (3)의 짧은 인용 모든 DNA는 문맥상 비암호화 DNA를 가리킴; 학습 판단에는 혼동 없음.|

## 결함과 수정 요청

- Critical/Important 수정 요청 없음.
- p1은 의도상3을 유지하되 cDNA 조건부 원문 결함을 숨기지 않았으므로 공개 요건 충족.
- p3은 의도상2를 유지하되 CCR5 일반화의 결함을 공개하고 모든 HIV 침입 불가·완치 보장을 거부하므로 공개 요건 충족.
- p4는 최종 원문 250,000 기준 단일4. 이전 전사본 25,000의 논쟁을 현재 원문에 적용하지 않았음.
- 원문·설명 조각을 수정하지 않았음. 아래 해시의 현재19조각을 대상으로만 이 승인 사용.

## 검토한 파일 해시

```text
293cfca837864d72163fee1436d9114bfa062028890816b93565afa41dfcbad3  source.json
c2a3babbd5c95c813afa97cd2c4cdb981a6fdc24ad6639c01d4a4401c629cda0  explanations/p1.html
ee91fbe1f886e41fb7eddcd031d7929249abd332cf9c781a1c92ade5ba8f6842  explanations/p2.html
3d835c90824911130d0793d02525039778d72454f3e025caf21fe0d32965263a  explanations/p3.html
2e386239bd9e21c1155feb55be193c8cf12209355da508b7513d048dcf053920  explanations/p4.html
5f41bf9c747ba120d003d049c73580a14d3d668b3348c7e62b0a37af623868bb  explanations/p5.html
eca0dd3bf9d4c966683ba76731cb53fcec2aef3c269f65fbffcfe138b70e89ff  explanations/p6.html
52fdf89f8dfe1d22ed367b2db618bdbba8dd3d57418a2afd2c2ccd493115d4bf  explanations/p7.html
21dbf3561d104f58cc4e7c64ad65b2266608a48500fba30884f160f200c418a0  explanations/p8.html
32830ba8a519e80595f9f5367b99913a2d0f02ef59ba5eb391db50242d14c942  explanations/p9.html
74e467ca63054e9019fbf9758879c49cd2aba43f064b757099fdcb67bfe60145  explanations/p10.html
61e753cc5f81d9900352f2e724475cf9fd81a01df2164963437e6f38a3d2af82  explanations/p11.html
4709d213e2e30f514d79c2b1a2dfcabe458a7d04b2335786ed1732c563f23aba  explanations/p12.html
6ec845bca8bbdb2841065e66b095216fab2f1a54be2f4a9dcd0ec17b5496a05e  explanations/p13.html
9aa773acb099a241ecd9e3146ac69e724440e070bf7de91b6d983af568428d4b  explanations/p14.html
aadef2829313e6995c0141453008ff8137e38001b61034d23cc3015eb4d0d1e2  explanations/p15.html
24f4aa51244f089186b8bfcf13622e4734a25bab28911132135adce9df7b6f16  explanations/p16.html
bbaede842cd565d6371c14ac3cd96549c484614b6897a14aefd0369e9c74e65c  explanations/p17.html
d24dd5106dc37f6c2f250aded74986e473f6d95ea1fc7edb24f6e8bf69b9f5ae  explanations/p18.html
dd490b3665e429bbbc96530bf4d1faf9b27f4dd9316ae7988f878b15fd756a78  explanations/p19.html
```
