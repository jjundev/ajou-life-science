# 5장 v1 문제설명 content 검토

검토자: content_review (설명 저작과 다른 에이전트). 상태: **pass, p1:main–p15:main 15/15 (요약 수정 재검토 완료)**.

모든 p1.html–p15.html이 실제로 존재한 이후 각각의 전문을 읽었다. source.json의 최종 A–E 보기 순서와 정답을 기준으로 일곱 구역, 단서→개념 연결, 영어 용어·뜻·판단 규칙·적용 범위, 실제 첫 줄, 모든 보기의 판정 근거, 답, 별도 검산, 부정형 방향, retry 1–3개, 요약과 본문의 일치를 확인했다. 이 검토는 정답 비공개 독립 재풀이를 대체하지 않는다. 문제·해설 조각·build/review.json은 변경하지 않았다.

## 문항별 확인

| item | status | 구체 근거 |
|---|---|---|
| p1:main | pass | C. 반보존적 정의를 이번 복제의 부모/새 가닥으로 정확히 한정하고, 분산적 모형 A 및 구조 설명 D와 구별한다. start O1/O2와 N1/N2는 recall의 기호 뜻과 연결된다. verify는 기존 두 가닥 보존과 새 두 가닥 추가라는 수지 검산이다. pitfall에서 ‘항상’을 최초 조상 가닥의 영구 보존으로 일반화하지 않는다. 강의노트 1쪽·1001 s4-semiconservative와 일치. |
| p2:main | pass | A. 부정형 방향을 understand·결론·pitfall에서 밝히며, 코돈/개시/정지/안티코돈의 세 염기 구간과 miRNA 전체 분자를 구별한다. A–E 모두 동일 명제 ‘세 뉴클레오타이드’에 대해 판단하고 사례 검산을 정의 및 강의노트 3·5·8쪽 대조로 보완한다. 1008 s2-rnai와 일치. |
| p3:main | pass | E. 원문 발문+변형 보기임을 공개한다. 작동자 DNA·억제자 단백질·알로락토스 유도자의 결합 대상을 설명하며 A–D의 각 오류를 구별한다. 억제 해제가 모든 환경에서 최대 전사량을 보장한다고 쓰지 않는다. verify는 역방향 원인 확인 및 강의노트 6–7쪽 대조. 1006 s5-operon과 일치. |
| p4:main | pass | D. 부정형 방향, 기출 변형 안내, DNA 서열/단백질 분류가 정확하다. D의 증폭자=단백질 혼동을 지적하고 E의 공간 접근과 서열상 위치를 구별한다. verify는 결합 자리/결합 물질 관계와 강의노트 7–8쪽·1008 s1-initiation 대조. |
| p5:main | pass | B. 22% 원기출에서 18%로 바뀐 조건을 공개한다. 이중가닥 전체에 G=C·A=T 적용 이유와 기호 뜻을 설명하고 A=T32%, G=C18%를 정확히 계산한다. verify는 100염기/32쌍 구성 및 B를 가정한 108% 모순으로 다른 경로 확인한다. 부정형·모든 판정·요약 수식 일치. 1001 s3-dna-structure. |
| p6:main | pass | B. 위 주형 3′→5′ 오른쪽, 아래 주형 왼쪽 읽기를 분기점 오른쪽 진행과 연결한다. 두 새 가닥 모두 5′→3′이며 X 선도·Y 지연. start 실제 방향 기록과 verify의 새 가닥 양끝/성장 3′끝 표시가 별도 검산 역할을 한다. A–E 판정과 SVG 방향 일치. 강의노트 2쪽·1001 s5-strands. |
| p7:main | pass | E. 주형 CCTACTGCGGGATTCCG의 상보 RNA GGAUGACGCCCUAAGGC가 정확하다. 첫 AUG부터 AUG/ACG/CCC/UAA로 묶고 종결 제외 3잔기. A 주형/암호화 혼동, B 개시 누락, C 종결 포함, D 종결 뒤 포함을 설명한다. verify RNA→DNA 역복원과 위치 3–11번 9염기/3=3 검산이 정확하다. 1006 s3-trna·s2-start-stop. |
| p8:main | pass | A. X124/Y134와 전구체1234를 실제 첫 줄에 적고 E3/E2 건너뛰기와 순서 유지 원리를 설명한다. DNA 불변·전구체에 이미 E4 존재·성숙 RNA의 엑손 조합 차이를 모든 보기에 적용한다. verify는 엑손별 포함 집합 재확인 및 강의노트 8쪽 대조. 1008 s2-splicing. |
| p9:main | pass | D. X 글리신 유지=침묵, Y 세린→프롤린=과오, Z 시스테인→종결=정지. 염기쌍 치환 조건 및 결과 분류 이유가 설명되고 E의 틀이동 혼동은 길이/원인으로 배제한다. verify 치환 위치 및 길이3 유지와 강의노트 6쪽 대조. 1006 s4-substitution. |
| p10:main | pass | C. 전사 억제자 결합 불가와 lacZ 번역 조기종결을 별개 단계로 나눈다. 정상 프로모터/전사 및 동일 다른 조건에서 두 젖당 조건 모두 전사, 발문 기능 상실/기존 기능성 LacZ 없음으로 모두 기능성 효소 없음. 다른 유전자 영향 없음도 적용한다. verify 변이 두 효과를 따로 검토 후 재결합하며 강의노트 6–7쪽과 일치. 짧은 산물의 기능상실을 일반 법칙으로 확대하지 않는다. |
| p11:main | pass | D. 부정형 방향을 굵게 표시하고 대상/효과를 구별한다. 히스톤 아세틸화 양전하 감소→결합 완화→접근 가능, 메틸화는 제시된 프로모터 사례에 한정한다. A–E와 요약 일치. 강의노트 7–8쪽 추출 및 교과서 실제 113쪽 이미지의 아세틸화/메틸화 설명과 대조해 검산 주장 확인. |
| p12:main | pass | C. X·Y DNA와 원·사각형 단백질을 구별하며 X 활성자/Y 개시 복합체 위치를 정확히 읽는다. 접힘은 삭제가 아니라 공간 거리 감소임을 설명한다. verify는 그림 명시 조건 3개로 A/B/D 소거 후 전사/번역 구분으로 E 배제. 1008 s1-initiation·교과서113쪽 원리와 일치. |
| p13:main | pass | B. 전사 속도와 mRNA 잔량을 생성/분해 수지로 나누고 발문에 명시된 절단·분해 경로에 한정한다. 단백질 생산량 감소와 기존 단백질 즉시 소멸을 구별한다. verify 배수 비유 및 실제 교과서 114쪽 그림5.23/115쪽 RNAi 본문 대조. 그림 번호·쪽과 주장 모두 확인. |
| p14:main | pass | E. 초기량·합성률 동일 조건으로 전체 단백질 증가를 분해 감소로 연결하고 표지된 단백질 증가로 표지 이후 처리 억제로 좁힌다. D가 전체 S 증가만 설명할 수 있으나 표지 S 증가를 설명하지 못한다는 구별이 명시된다. verify E가 mRNA/전체/표지된 S 세 관찰을 모두 예측하는지 확인하며 강의노트9쪽 및 실제 교과서115쪽 표지→프로테아좀 분해 설명과 일치. 전체+부분 합산 함정도 정확하다. |
| p15:main | pass | A. 전형적 진핵 핵유전자 가공이라는 적용 범위를 명시한다. 5′cap/3′poly(A), 인트론 제거·엑손 연결, 핵내 가공/핵밖 번역을 설명하고 모든 보기 판정 및 부정형 결론 정확하다. verify 시간 흐름과 강의노트4–5쪽 대조. 모든 엑손이 번역된다는 일반화도 방지한다. 1006 s1-processing. |

## 공통 확인 및 편집 메모

- 각 문항은 understand/recall/start/solve/verify/pitfall/retry 일곱 구역과 main 소문항 표지, summary-group을 갖는다. 긴 개념 설명을 start에 복제하지 않았다.
- 부정형 p2·p4·p5·p11·p15의 방향 및 답은 일치한다. ㄱㄴㄷ형·교배 문항은 없다.
- p1·p2 원문형, p3·p4 발문 유지 변형, p5 수치 변형, p6–p15 새 예상이라는 blueprint/pack 맥락과 해설 주장이 일치한다. 새 예상에 실제 기출 출처를 덧씌우는 주장, 정답/조건 충돌, 자료 오류 은폐는 발견하지 않았다.
- p1–p10의 sum 검산을 1–2문장으로 줄인 수정 뒤 열 문항의 요약 전체를 다시 읽었다. p5 단축 초안의 104%는 A=T 조건 및 본문108%와 달라 재수정 요청했으며, 현재 문장 “B의 A36%라면 T도36%여서 합이108%”를 직접 확인했다. 현재 열 문항 요약과 p11–p15 요약의 개념·첫 줄·답·검산은 모두 본문과 일치한다.

## 실제 읽은 자료

- 현재 source.json, explanations/p1.html–p15.html 전문.
- 웹과제예상/5장/src/v1/blueprint.md: 모드·최종 답·노트 앵커·원문 적용 범위.
- .agents/skills/bio-problem-explain/references/authoring.md 및 verification.md 전문.
- 복습노트/1001 정리노트 s3/s4/s5, 복습노트/1006 정리노트 s1–s5, 복습노트/1008 정리노트 s0–s3.
- 강의노트 5장 DNA 복제와 유전자의 발현.pdf의 .scratch/webquiz-forecast/5장-v1/lecture.txt 1–9쪽 추출 전문.
- 교과서 05장 PDF의 기존 실제 렌더 이미지 textbook-p113.png, textbook-23.png(인쇄114), textbook-24.png(인쇄115)를 직접 열어 읽음. textbook-25·26 이미지도 열었으며 인쇄116·117로 확인해 114·115 대조 자료로 사용하지 않음.

## 검토한 파일 SHA-256

- explanations/p1.html : dae8ec964681febbc613bfe90952ba8d9a3d72e1b9376b784db427faf310bcff
- explanations/p2.html : d8ea7bb36522db30921844d7dc137147795b0b485b8b6caa8b33894550106f07
- explanations/p3.html : 208394290c34eed6eac5fd8cff348fea03d15bdb9ba43dbe84a34380f6204f3f
- explanations/p4.html : 5444b8b6956d9aa5164624860b67451182f2382cd7fb933b9fae786927487176
- explanations/p5.html : d307d9e293edb9dad6e6083c3e48dff5ab3cd0cae22a84892bef649fb454f57c
- explanations/p6.html : 514006e197e64fdef1de8e4260f74bdca62fa3d42e53ca8db407be8e17e95797
- explanations/p7.html : 6ae02907e67da1da1d7e166578f10e186e9e84481019fea7ab40fe9de36226e0
- explanations/p8.html : 2f57153b7fbd2df630f928e957bf4e31f31165f5c5a155f588df6b98b65e0523
- explanations/p9.html : 5a75d045557ea870e4af59c9446a218f5ac09f509d660ea5baaa85f98561d2e8
- explanations/p10.html : b607fd3a2d32837b055e79d44c829c164a0d667c0ebe42b7fedac133199cf8fc
- explanations/p11.html : f9cec0268751664b5dc893e35166f17c5033d8654a6dc6cc4c53c5509bb77b7f
- explanations/p12.html : d324ea96bfc609c1f9d3b4472b2c71e9a0fadf6ca6599299468ddff76d14899c
- explanations/p13.html : 594b7fbd57a31e88681c490c951252db6b1d9a9d9e5688218d0f4aedf10ffc85
- explanations/p14.html : a6ca8f836ed9326098c92ff407183128a976840b9c386097ed74737b5f10a7ff
- explanations/p15.html : f8190f9c4db24fb1829a53896843e89f1848f3f5bb545b597672456c90627104
- source.json : ce904e32afcf70b571fd2c894ae9b8638dd68af4fd65a65b741b80b04e9ac51d
