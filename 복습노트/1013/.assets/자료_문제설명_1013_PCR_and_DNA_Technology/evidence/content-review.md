# 1013 문제설명 content 검토

리뷰어: 독립 재풀이를 먼저 완료한 별도 에이전트. 이번 작업은 content 검토이며 설명 저작·파일 수정은 수행하지 않았다.

대상 stage: stage/922680d237c8441ab1769d0d87914de4/문제설명_1013_PCR_and_DNA_Technology.html 및 explanations/p1.html~p37.html. source.json·최종노트·교재 실제 PNG5–12·강의자료·key-check.md·variants.md와 bio-problem-explain SKILL/authoring.md/verification.md를 대조했다.

전체 37개 조각을 내용별로 읽었다. 전부 일곱구역 understand→recall→start→solve→verify→pitfall→retry 순서, solve/verify main표지 각1개, 전보기 판정과 요약이 있다. assembled stage의 pN article과 조각은 태그·공백·entity 정규화 뒤 의미텍스트가 모두 일치한다. 링크주소 재작성 때문에 원문 조각 문자열 전체의 byte 포함 검사는 성립하지 않으므로 이를 구조실패로 취급하지 않았다. 이 content 검토는 브라우저·source_visual 검토를 대신하지 않는다.

| item | status | 검토 근거 |
|---|---|---|
| p1:main | pass | 환경 우려를 조건부 가능성으로 판정하고 GMO 보편 유해성 단정을 피함. |
| p2:main | pass | STR 단서→좌위·반복수→길이, 교재 그림으로 검산. |
| p3:main | pass | 부정방향 굵게·법적 효력·쌍둥이 예외, 강의 p2–3 대조. |
| p4:main | pass | 절단/삽입/증폭 동사로 기능 분리 및 소거. |
| p5:main | pass | 가능한 식물개량 목적과 모든 작물의 실제성질 구별. |
| p6:main | pass | N₀·n·Nn 정의와 이상조건, 1024³ 별도검산 정확. |
| p7:main | pass | 도구 역할과 PCR 대조; 모든 벡터 동시필수 오해 방지. |
| p8:main | pass | 체세포핵치환 용어결함 understand strong 공개·solve/시험대처 연계. |
| p9:main | pass | 부정방향과 열/헬리케이스 구별, 네 필수요소 대조. |
| p10:main | pass | 내성잡초 선택과 사용량 관계, 민감한 잡초 반대상황 검산. |
| p11:main | pass | 비암호화 STR 길이·증폭후분리·쌍둥이 예외 전보기 판정. |
| p12:main | pass | 환자유전자치료와 식품섭취 구별, ADA과정 별도검산. |
| p13:main | pass | 전류·겔·DNA시료·세균클로닝 전보기 판정과 도식소거. |
| p14:main | pass | 인산 음전하가 방향원인, 길이/중력/절단 구분. |
| p15:main | pass | 보완 조각 재검토: understand에 strong 문항결함으로 전기장/겔 조건 미지정·기술유일성 한계를 공개. solve①은 크로마토그래피 분리가능성 유지, pitfall은 일반판단과 수업맥락④를 구별. 요구했던 결함공개 누락 해소. |
| p16:main | pass | understand strong 문항결함, ① 상속해석·③ 유래/밴드 구분, 11/11 반례검산, 시험확신보류 정확. |
| p17:main | pass | 목적과 위험 구별, 필수아미노산 포괄표현 strong 공개·교재 아미노산함량 목적 유지. |
| p18:main | pass | understand strong 인쇄정답오류(인쇄③/수업⑤) 및 문항결함 함께 공개; solve③ 교재pp122–123 참·⑤ UV조건부, pitfall 공식답 재확인 제시. |
| p19:main | pass | 체세포전달X와 생식계열 구분, 법률주장 수업·교재시점 한정. |
| p20:main | pass | 추출·증폭·검출 단계 분리와 남아있는DNA 조건, 모든서열/프라이머/육안/숙주 오답 판정. |
| p21:main | pass | 고온반복 조건이 내열효소 선택이유, 다른기술 절대독점 아님 공개. |
| p22:main | pass | STR 표지와 transformation/plasmid 도구 구별. |
| p23:main | pass | understand strong motif/전체STR 모호성, solve① 엄밀히참가능·⑤ 단일좌위값항상고유아님, pitfall 조건과 시험대처 정확. |
| p24:main | pass | ADA 뜻·환자백혈구유전자도입, 장기/응고인자투여 경계 및교재사례검산. |
| p25:main | pass | 최고임상효과 순위아닌 정상유전자 결핍보완 원리, 암치료 불가능 주장을 피함. |
| p26:main | pass | 두반대주형프라이머·dNTP·내열성·양끝서열정보 전보기역할 판정. |
| p27:main | pass | 초기3×2⁵=96, 0~5주기 3/6/12/24/48/96 별도검산. |
| p28:main | pass | RNA만·같은프라이머·DNA오염없음 조건으로 역전사출력분리, B경로소거. |
| p29:main | pass | 같은시간/조건/선형DNA, 거리C>B>A·길이A>B>C, 속도=거리/시간 별도검산. |
| p30:main | pass | 50에 프라이머포함 명시; 50+6r로92/110/128 bp; +18차이로재계산·거리A>B>C; 노트80/4암기 방지. |
| p31:main | pass | 12엄마/14후보 상속양립, 네자녀조합8/10·8/14·12/10·12/14모두 검산, 단일좌위확정X. |
| p32:main | pass | 효모발현벡터·환자조작없음 두대상구분, 부정방향·전보기판정. |
| p33:main | pass | ㄱ맞/ㄴ맞/ㄷ틀 각각 먼저 판정한 뒤 다섯조합소거, summary와 일치. |
| p34:main | pass | 핵A/mtDNA B/자궁C 별도역추적, 교재핵치환과수업mtDNA 출처분리. |
| p35:main | pass | β카로틴축적증가 목적에 합성감소⑤ 반박, ③유출관리참·원기출개념과변형개념차이 공개. |
| p36:main | pass | 기질·에너지조건이있는 루시퍼레이스리포터 출력, 전체유전자교체나내성증명 아님. |
| p37:main | pass | 처리전변이·처리후선택·번식, 역시간검산으로 목적변이·독성인과 배제. |

## 일괄 결론

explanations 조각 기준 content 37/37 pass. 최초 p15 조건 미지정 결함공개 누락 1건은 저작자가 수정했고, 검토자가 p15.html을 다시 직접 읽어 understand strong 공개·solve 논쟁보기·pitfall 수업맥락 대처를 확인했다. 정답·source·노트 변경은 없다.

stage/922680d237c8441ab1769d0d87914de4는 수정 전 p15를 포함한다. 현재 승인 범위는 최종 37개 raw 조각의 content이며 새 stage 재build 후 p15 반영 및 전체조각 의미텍스트 일치 재확인을 수행하기 전에는 해당 stage 최종 content 승인을 의미하지 않는다.

중점검토 p16·p18·p23은 조건부 판단을 단일정답 확신으로 과장하지 않는다. p18 인쇄③가 참인 이유와 수업맥락⑤ 선택 및 검출조건생략 모호성을 각각 공개했다. p30 계산·프라이머포함조건·길이와거리역순이 정확하다. p35 합성감소 함정이 β카로틴 축적목표와 반대임을 정확히 설명한다. p33은 진술별판정 후 조합을 고른다. recall은 단서·용어/기호뜻·조건·선택이유가 설명되어 있고 start는 실제로 적을 문장/첫행이다. verify에는 소거·교재쪽·반례·역경로·별도계산 중 하나 이상의 다른확인경로가 있어 solve를 단순히 되풀이한 검산으로만 끝나지 않는다.
