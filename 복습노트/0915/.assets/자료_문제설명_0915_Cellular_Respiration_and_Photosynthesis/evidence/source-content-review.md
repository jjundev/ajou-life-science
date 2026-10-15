# Fresh source_visual/content review — 2026-10-15

Reviewer: Codex final_review (fresh-context final reviewer). 저작물 변경 없이 검토증거만 작성했다. 과거 pass는 재사용하지 않았다.

**source_visual: 93 pass. content: 88 pass / 5 fail. 두 팩 모두 발행 보류.**

현재 WORK/explain/0910·0915 source.json의 53+40문항과 explanations/*.html 93개 전문을 실제 읽었다. 아래 source_visual은 원자료 대조 완료를 뜻한다. 0910 p10 원문 NAD/카드 NADP 차이 등 기존 전사 결함은 현재 해설에 명시 공개되어 있음을 확인했다. 인쇄 조판오류, 밀린 그림, 보기 없는 원문도 현재 안내와 대조했다.

변형은 두 .pack/variants.md 전체 행, 해당 정리노트 토픽, 지정 교재 쪽과 대조했다. source_visual의 pass는 과거 카드가 원문과 완벽히 동일하다는 선언이나 기존 원문 오류에 대한 무조건 승인이 아니다.

0915 p28의 C는 식물에서도 내막만이라고 하므로 틸라코이드막을 배제한다. 현재 E 풀이가 타당하다. 0915 p3는 직접 발효단계의 NAD+와 앞선 해당과정의 ATP를 recall/start/solve/verify/sum에서 구별하여 이 해석의 설명은 충분하다. 카드 mode=ambiguous를 바꾸지 않는다.

## 실제 읽은 원자료


- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/23, 24 소스/1강 합본.pdf` — PDF2·3 텍스트+실제 렌더;22·40번; SHA256 `734b68436fc7a4e55f24360495ef46ab5d85ce25499a9576681adabd20b9ff7b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/23, 24 소스/2강 합본.pdf` — PDF1–4 텍스트+실제 렌더 전체;밀린13번·14번그림 포함; SHA256 `8155cfcb6b9cf49ddc63624216239114c1d8e4625bd55fdd0f3f8b71838b600e`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/1장/questions.json` — q12 original·observations·analysis; SHA256 `9e53575519a304b5f370d50e267c58fc1ce5d995ac2659a8f709723cd18dff7d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/questions.json` — q01–q16 original 조건·보기·observations·issues·assets; SHA256 `e0d4dec4e995a271e88386a21ebfa9ab09a3b1173381cd38b954d7553b1c7658`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/교과서/생명과학_기초와_응용_2판/01장_생물분자와_세포.pdf` — 실제 렌더 인쇄p12,20–23; SHA256 `78f993b661f74f7d039d65afc1431d2d27521474e38617d2b4b819318e421455`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/교과서/생명과학_기초와_응용_2판/02장_세포호흡과_광합성.pdf` — 실제 렌더 인쇄p32–51 전체; SHA256 `9b7011465c9f38c91420d9eecab00de15dd47fafb00b23a699fd9b194a8d8b42`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/강의노트/2장 세포호흡과 광합성.pdf` — PDF1–5 추출본문 전체; SHA256 `d73db7dd54af5ffac2232acd74f8a4084ce2b9a11e73be9c8331fd59632db89f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/STT/0910 생명.md` — 05:11,23:47,45:09,69:12 주변; SHA256 `d88fbc55eda6e93446507aa34ca01d3afb9ba802e17a9b7604e2a584ed92fdc0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/STT/0915 생명.md` — 15:27,15:47,27:04,27:43,32:30 주변; SHA256 `67ab58ae4c819ebe1195841a48b1dd00487a68c0f0fd566738416ceebc818f65`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/STT/0903 생명.md` — 41:32 주변; SHA256 `ebfa0e5712d432be9498dd5f76636363c8ae0b0a067cc58e8688b2de053d8822`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/note-feedback.md` — 전체16행·불확실성; SHA256 `9b8e735f5f7ca64f7af9d65a390f0492e4215ea6e27385180960a084e5325056`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0910/.pack/variants.md` — 전체설계행; SHA256 `0acc7443b2917a48ead53459a1339b78a5280bd1f643d015b00aef4fa468e3b2`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0910/정리노트_0910_Cells_and_Cellular_Respiration.html` — 변형근거토픽 formal 및 관련warn/supp/피드백16행근거; SHA256 `13dd3257de0771196d570dbce0a521f694b77f84c9809c9d52e8028131634c30`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0910/.pack/note-feedback-audit.md` — 전체8행; SHA256 `d3c3a991cfe343a6a7de305737320265578fcab3c2841d15ad0fbb726b7e0c6b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0915/.pack/variants.md` — 전체설계행; SHA256 `0056c8aef63609d521216360e563a7208591282b1c417e214481a6f438f73fe0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0915/정리노트_0915_Cellular_Respiration_and_Photosynthesis.html` — 변형근거토픽 formal 및 관련warn/supp/피드백16행근거; SHA256 `f63feeb209e363465a5a575e6f23079200fc5c70d20338cba063607e3c4f5590`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0915/.pack/note-feedback-audit.md` — 전체8행; SHA256 `ddbdf5bef7b44fa72ed961bd58ecf02cf1bb513f3dc531026aa28472035623d8`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/image/q04.svg` — 실제 렌더와 source 인라인그림 대조; SHA256 `930ce9dcfb47f36a909be76fa32e9ae44e16d523f5c119a711e6581931afce4a`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/image/q09.svg` — 실제 렌더와 source 인라인그림 대조; SHA256 `ec269182ad88b81a554d319fed311d7f4647a2eeef0b884304b2f22eb53bcb2d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/image/q15.svg` — 실제 렌더와 source 인라인그림 대조; SHA256 `e4ec1e1901626ff66b1e59c74e3ff2be869a905782e6fd159521242409a18605`

신규 PDF/SVG 렌더를 `/tmp/bio-final-review-20261015/`에서 직접 열었다. class 의존 변형 SVG는 원본 CSS fig-ink/accent/danger/text 속성을 임시 렌더에 적용해 표지와 기하를 확인했다. 저작 SVG 변경 없음. p11 crop은 WORK/pack/0910/figures/p11.png를 기출PDF2·교재p34와 직접 대조했다.

## 문항별 결과

각 content 대상은 해당 explanations/pN.html 전체 8구역과 source.json 같은 문항이다. 변형 원천은 variants.md 같은 ID 행 및 해당 노트토픽이다. source_visual과 content는 독립검산을 대체하지 않는다.

### 0910

source: `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/source.json`
input_hash: `f91cf439ff2bd2799314b4ab39a30a441bbeaa47a77a5e5009fa0773e203a926`

| item | source_visual | content | 원천 및 결론 |
|---|---|---|---|
| p2:main | pass | pass | 웹과제 1장 q12; 웹과제 1장 q12 (스크린샷 s13); 방추사 기능은 미세소관 C;교재1 p20–22 |
| p3:main | pass | pass | 기출 1강 40; 기출 1강 합본 40번 (PDF 3쪽); 능동수송 농도반대 5;교재1 p23 |
| p4:main | pass | pass | 기출 2강 1; 기출 2강 합본 1번 (PDF 1쪽); ATP·열 모두 사실 결함 공개,인쇄1;교재2 p43 |
| p5:main | pass | pass | 기출 2강 2; 기출 2강 합본 2번 (PDF 1쪽); 호흡+생성물 두조건4;교재2 p40 |
| p6:main | pass | pass | 기출 2강 6; 기출 2강 합본 6번 (PDF 1쪽); Ea 감소/방향불변1;교재2 p33–34 |
| p7:main | pass | pass | 기출 2강 7; 기출 2강 합본 7번 (PDF 1쪽); 비타민4,분해안됨은 연료아님으로 제한;교재2 p34–35 |
| p8:main | pass | pass | 기출 2강 8; 기출 2강 합본 8번 (PDF 1쪽); ATP 인산기 손실2;교재2 p32–33 |
| p9:main | pass | pass | 기출 2강 10; 기출 2강 합본 10번 (PDF 1쪽); 스트로마1;교재1 p21–22 |
| p10:main | pass | pass | 기출 2강 11; 기출 2강 합본 11번 (PDF 1쪽); 원문NAD/카드NADP 차이공개,ATP4;교재2 p32 |
| p11:main | pass | pass | 기출 2강 14; 기출 2강 합본 14번 (PDF 2쪽 왼쪽). 문제가 가리키는 "위 그림"은 합본에서 제자리에 인쇄되지 않고 PDF 2쪽 오른쪽 아래(24번 옆)로 밀려 인쇄되어 있어요. 그 그림을 잘라 문제 위에 넣었어요.; 젖당3,밀린그림 crop 직접대조;교재2 p34그림2.4 |
| p12:main | pass | pass | 기출 2강 15; 기출 2강 합본 15번 (PDF 2쪽 왼쪽). 원문의 "H^〖+〗"는 첨자가 깨진 조판 오류라서 의도한 글자인 H⁺로 옮겼어요.; ATP합성효소+ADP인산화5;교재2 p41–42 |
| p13:main | pass | pass | 기출 2강 16; 기출 2강 합본 16번 (PDF 2쪽 왼쪽); ATP공급 아닌 촉매3;교재2 p33–34 |
| p14:main | pass | pass | 기출 2강 18; 기출 2강 합본 18번 (PDF 2쪽). 문제와 보기 (1)~(3)은 2쪽 왼쪽 아래에 있고, 보기 (3)의 끝("한다.")과 보기 (4)는 2쪽 오른쪽 위로 넘어가 있어요.; 식물도 호흡4;교재2 p36 |
| p15:main | pass | pass | 기출 2강 19; 기출 2강 합본 19번 (PDF 2쪽 오른쪽); Ea 감소4;교재2 p33–34 |
| p16:main | pass | pass | 기출 2강 22; 기출 2강 합본 22번 (PDF 2쪽 오른쪽). 원문 보기 (2)의 "H〖〗^〖+〗"는 첨자가 깨진 조판 오류라서 의도한 글자인 H⁺로 옮겼어요.; ETC는 기울기형성2;교재2 p41–42 |
| p17:main | pass | fail | 기출 2강 23; 기출 2강 합본 23번 (PDF 2쪽 오른쪽). 원문에는 보기가 없는 서술형 문항이에요.; FAIL I2: solve24 모든반응 일반화;교재2 p32–34 |
| p18:main | pass | pass | 기출 2강 25; 기출 2강 합본 25번 (PDF 3쪽 왼쪽). 원문 보기 (1)의 "CO〖〗_〖2〗"는 첨자가 깨진 조판 오류라서 의도한 글자인 CO₂로 옮겼어요.; CoQ도 운반체 결함공개,인쇄5;교재2 p38,41 |
| p19:main | pass | fail | 기출 2강 27; 기출 2강 합본 27번 (PDF 3쪽 왼쪽); FAIL I1: FADH2→I 경로;교재2 p41–42 |
| p20:main | pass | pass | 기출 2강 28; 기출 2강 합본 28번 (PDF 3쪽 왼쪽); NAD+1/무한대 원문결함공개;교재2 p38 |
| p21:main | pass | pass | 기출 2강 29; 기출 2강 합본 29번 (PDF 3쪽). 원문에도 보기가 없는 서술형 문항이에요.; 단답 ATP합성;교재2 p36–37,42 |
| p22:main | pass | pass | 기출 2강 30; 기출 2강 합본 30번 (PDF 3쪽); 20종5/기질 일반화결함공개;교재1 p12 |
| p23:main | pass | pass | 기출 2강 33; 기출 2강 합본 33번 (PDF 3쪽); 내막 산화적인산화3;교재2 p37–42 |
| p24:main | pass | pass | 기출 2강 35; 기출 2강 합본 35번 (PDF 3쪽); 인산기손실4;교재2 p32–33 |
| p25:main | pass | pass | 기출 2강 37; 기출 2강 합본 37번 (PDF 3쪽); 모두필요3/개별참 공개;교재2 p42 |
| p26:main | pass | pass | 기출 2강 38; 기출 2강 합본 38번 (PDF 3쪽). 원문에도 보기가 없는 서술형 문항이에요.; 인쇄 전자전달계의 압축표현 공개/4+28;교재2 p42 |
| p27:main | pass | pass | 기출 2강 39; 기출 2강 합본 39번 (PDF 3쪽); 효소재사용2;교재2 p34–35 |
| p28:main | pass | pass | 기출 2강 42; 기출 2강 합본 42번 (PDF 4쪽); 4 높이 모호/인쇄답없음 공개,분석1;교재2 p33–34 |
| p29:main | pass | pass | 기출 2강 43; 기출 2강 합본 43번 (PDF 4쪽); 내막펌핑O2/4;교재2 p41–42 |
| p30:main | pass | pass | 기출 2강 44; 기출 2강 합본 44번 (PDF 4쪽); 모든반응 과장을 자발반응으로 제한,4;교재2 p33–34 |
| p31:main | pass | pass | 생성 변형 s0-chloroplast; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 미토콘드리아 내막(크리스테로 접힘)과 엽록체 내막(매끈하고 틸라코이드가 따로 있음), 미토콘드리아 기질과 엽록체 스트로마의 대응. 근거 토픽: s0-chloroplast(엽록체: 이중막 안의 틸라코이드); 기질↔스트로마1;s0-chloroplast/교재1 p20–22 |
| p32:main | pass | pass | 생성 변형 s1-cytoskeleton; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 세포골격 세 종류(미세소관, 중간섬유, 미세섬유)의 기능과 단위체 구분. 근거 토픽: s1-cytoskeleton(세포골격: 물풍선이 아니라 텐트); 미세섬유액틴2;s1-cytoskeleton/교재1 p20–21 |
| p33:main | pass | pass | 생성 변형 s1-cytoskeleton; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 소낭 수송에서 트랙(미세소관), 운동단백질(키네신), 화물(소낭)의 역할 구분. 근거 토픽: s1-cytoskeleton(세포골격: 물풍선이 아니라 텐트); 미세소관·키네신·소낭1;s1-cytoskeleton |
| p34:main | pass | pass | 생성 변형 s2-atp; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 리보스(RNA)와 디옥시리보스(DNA), 아데노신(아데닌 + 리보스)과 아데닌, ATP → ADP에서 에너지가 나오는 방향. 앞선 수업(0908)의 퓨린 염기 개념을 ㄷ에 엮었어요. 근거 토픽: s2-atp(ATP: 저금해 두었다 꺼내 쓰는 에너지); 리보스·퓨린·ADP ㄴㄷ4;s2-atp/교재2 p33 |
| p35:main | pass | pass | 생성 변형 s3-temp-ph; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 온도가 오르면 활성이 오르다가 변성으로 떨어지는 두 구간, 그리고 "효소는 변하지 않는다"가 적용되는 범위. 근거 토픽: s3-temp-ph(온도와 pH: 구조가 깨지면 기능이 깨진다); 최적온도 뒤 변성3;s3-temp-ph/교재2 p35 |
| p36:main | pass | pass | 생성 변형 s4-redox; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 환원된(떨어질 전자, 곧 C–H를 많이 가진) 물질일수록 에너지가 많다는 원리. 근거 토픽: s4-redox(산화·환원: 전자는 끌어당기는 쪽으로 떨어진다); 지방>포도당>CO2/1;s4-redox/교재2 p36,39 |
| p37:main | pass | pass | 생성 변형 s4-redox; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 누가 산화되고 누가 환원되는지, 산화와 환원이 동시에 일어난다는 점, NAD⁺ → NADH의 방향. 근거 토픽: s4-redox(산화·환원: 전자는 끌어당기는 쪽으로 떨어진다); 포도당산화·산소환원2;s4-redox/교재2 p36–38 |
| p38:main | pass | pass | 생성 변형 s5-phosphorylation; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 기질 수준 인산화(기질이 인산기를 ADP에 직접 넘김)와 산화적 인산화(전자전달계, H⁺ 기울기, ATP 합성효소). 근거 토픽: s5-phosphorylation(기질 수준 인산화와 산화적 인산화); H+ 방식만 산화적3;s5-phosphorylation/교재2 p37–42 |
| p39:main | pass | pass | 생성 변형 s5-atp-synthase; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: H⁺의 방향(퍼낼 때는 기질 → 막 사이 공간, 돌아올 때는 ATP 합성효소 통과), 전자의 에너지가 바로 ATP가 되지 않는다는 점. 근거 토픽: s5-atp-synthase(H⁺ 기울기와 ATP 합성효소); 펌프방향·귀환·ATP3;s5-atp-synthase/교재2 p41–42 |
| p40:main | pass | pass | 기출 1강 22; 기출 1강 합본 22번 (PDF 2쪽). 원문에서 문항 옆에 붙은 물 분자 그림은 26번 문항("위 그림을 보고")의 그림이라 옮기지 않았어요.; 세포벽모양 모호 공개,인쇄2;교재1 p21–23 |
| p41:main | pass | pass | 웹과제 2장 q02; 웹과제 2장 q02 (스크린샷 s02); 같은질량 환원도A;교재2 p36,39/STT0910 45:09 |
| p42:main | pass | pass | 웹과제 2장 q04; 웹과제 2장 q04 (스크린샷 s04); II·III·IV 높이 대조,E;bank q04.svg/교재2 p34 |
| p43:main | pass | fail | 웹과제 2장 q05; 웹과제 2장 q05 (스크린샷 s05); FAIL I1: start19 FADH2→I 경로;교재2 p41–42 |
| p44:main | pass | pass | 웹과제 2장 q08; 웹과제 2장 q08 (스크린샷 s08); 일반적고온변성D;교재2 p34–35 |
| p45:main | pass | pass | 웹과제 2장 q09; 웹과제 2장 q09 (스크린샷 s09); 가나 CO2/다는물,A;bank q09.svg/교재2 p37–42 |
| p46:main | pass | pass | 웹과제 2장 q12; 웹과제 2장 q12 (스크린샷 s13); 해당산물A;교재2 p38 |
| p47:main | pass | pass | 웹과제 2장 q15; 웹과제 2장 q15 (스크린샷 s16); ATP 구조·가수분해C;bank q15.svg/교재2 p32–33 |
| p48:main | pass | pass | 웹과제 2장 q16; 웹과제 2장 q16 (스크린샷 s17); 전자유지+귀환차단E·누출반대·역압제한 명시;교재2 p41–42 |
| p49:main | pass | pass | 생성 변형 s3-enzyme; 기출 2강 6번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: 활성 부위가 효소의 일부인지 기질의 일부인지, 효소가 바꾸는 것(활성화 에너지)과 바꾸지 않는 것(에너지 차이, 반응 방향). 근거 토픽: s3-enzyme(효소는 언덕을 낮춘다); 활성부위 주인3/북극눈벼룩 -10C 확인;s3-enzyme/교재2 p33–35 |
| p50:main | pass | pass | 생성 변형 s4-krebs; 기출 2강 25번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: FADH₂도 NADH와 같은 전자 운반체라는 점, 전자를 마지막으로 받는 산소(최종 전자수용체)와 전자를 실어 나르는 운반체의 구분, 전자가 아닌 인산기를 주고받는 ATP·ADP. 근거 토픽: s4-krebs(피루브산 산화와 시트르산 회로); FADH2운반체4;s4-krebs/교재2 p39–40 |
| p51:main | pass | pass | 생성 변형 s5-phosphorylation; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: "기질 수준 인산화"의 기질(반응물, substrate)과 미토콘드리아 기질(공간, matrix), 세포호흡 단계별 장소(세포질, 기질, 내막). 근거 토픽: s5-phosphorylation(기질 수준 인산화와 산화적 인산화); 그림A외막B내막C막간D기질E세포질/5;s5-phosphorylation |
| p52:main | pass | pass | 생성 변형 s0-vacuole-wall; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 세포막(인지질 이중층, 말랑함, 안쪽)과 세포벽(셀룰로스, 단단함, 바깥쪽)의 위치와 성분, 액포의 리소좀 역할, 식물세포도 미토콘드리아로 세포호흡을 한다는 점. 근거 토픽: s0-vacuole-wall(액포와 세포벽: 식물세포만의 창고와 벽), 함께 쓰는 토픽: s0-chloroplast; 그림A벽B막C액포D엽록체E미토/2;s0-vacuole-wall |
| p53:main | pass | pass | 생성 변형 s2-atp-use; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 물질이 옮겨 가면 늘 에너지가 든다는 착각, 확산(농도기울기를 따라, 에너지 불필요)과 능동수송(농도기울기와 반대로, 에너지 필요)의 방향 구분. 근거 토픽: s2-atp-use(ATP를 쓰는 곳); 고→저확산1/단백질인산화보충;s2-atp-use/교재1 p23·교재2 p33 |
| p54:main | pass | pass | 생성 변형 s4-nad; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: NAD⁺가 "산화된 형태"라는 이름과, 전자를 받을 때 일어나는 일(환원)의 구분, 탄소의 행방(CO₂)과 전자의 행방(NADH·FADH₂), 운반체가 재생되어 다시 쓰인다는 점. 근거 토픽: s4-nad(NAD⁺와 세포호흡 3단계); NAD+ 받으면환원4;s4-nad/교재2 p36,38 |

실제 읽은 source/설명 파일 SHA256:

- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/source.json` — `4843d0bd2a82724638fca4c1571de5853aa7d9df7d84ac1be2f20eb475a8d23f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p2.html` — `5fd24e70133afd1f9b0414b45b2cfd8df32cb634976a575ba8497f433a08161e`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p3.html` — `f006641d3d036fd9378e648f4848e8dd53d9e08ad7173808588fd1d28b2da9a7`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p4.html` — `4ca74a758bf85e39df7beb45536a86fa7e36251798fca64db8f0fd6b35f01b6d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p5.html` — `565bee7ae89dec8c84f76976cbcd14628743f5bb2ce9ec7aa7957f5919eea355`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p6.html` — `34a3f79b88efcd9f136ce2fe5422c66fdbe1ab841eb05bba7f4f3d4be73f7385`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p7.html` — `630927da69811935c529cd1798341e328975f8b7362d40e11e0579aa0f1432e2`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p8.html` — `c974cd4cbe28dd2c865e5e38cab8be855f7fe357b1ca5222fcdbf41a59c7b78b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p9.html` — `9eea3843e4f056604f2da48f2fd8b3f1c735befa9bbde326e6af2706698d9756`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p10.html` — `d24b2b07a6b0a306c2c29fb3784d2b3fbb123cc2483d95f421ea5bfabd2e6bfe`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p11.html` — `0939a7612d115352084d39a26ca3ea15b79725ef76c42251070e7482b626baeb`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p12.html` — `c25f78ee2097fcd50826908ac267aa6fa88b036af306fe0eb1924cf0f5f566dd`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p13.html` — `a7aee15c8b740e1a33b5a535d95fbdf9ff89f2dd62623061acb0f94f183f7981`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p14.html` — `693dbc7d26ab8539b56fc94aea97367dbb32ff6df374e726c18b0eb5026ffb6a`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p15.html` — `6738ee05952ff7ec397b2033ddb94a93d98f6c9242fbe4fc6a93a47d47d48707`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p16.html` — `7ebd571c29f3a1d75ca64bc9b15f66ee0abdd1dd4b348e16a7b7f6e0a156d049`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p17.html` — `550347005affc0e84d239e6687e13bdbde924b84389150b808d7da8c18c46bb9`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p18.html` — `d49a484db9bc234bcb9163fc83b48a336872317bdd6a1ac55a584a2ff80ce6b1`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p19.html` — `54d837bd01b37f02fa21a63e281348531437abf06e7a2ceb8a09b55edc64f1d4`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p20.html` — `a8181a17345abe49ac6d08e8687d8887fa15ba7449ae5136172dfc32750b5271`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p21.html` — `2b0169e2f5ed8b25293fecbababe9ebe3734c6abdf25c3fd525d5ead0c04b5fd`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p22.html` — `8ad8ec7afa328c8487cf8098f6ac78524d4ed92bb483b37a16b05f935e9b3dc0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p23.html` — `deff0c3975e3be324a8903796daf05f57dd2119f8fcd5a560672012830ac10e7`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p24.html` — `b89ae48b8ef393666d733ff890f0fa7d98e86aa435616e8b5195f550ccf1dd2e`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p25.html` — `45601ed13ec04561025a2552ee7509db50711a4dafdc486a2e87612cb12fa84b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p26.html` — `22aaa6c80eb97a7000384f6759ba3ff738ec8221483721c93a77a2527b9e3c98`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p27.html` — `a099637bf62eec921bf71e9aa649bb50fe6086bca2405cc79b054a2561292c82`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p28.html` — `595c1147204df919bcbbb9b17c590222dbc081180d4de8ef1fc5de9c3510ec87`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p29.html` — `f117608536476e9ed88f4906d870890ea8b8533281b4c2a699103655d081c82d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p30.html` — `a490dc86d342f7e2490a686a2c00a557be8078c1eccced14ec920d1185fc1612`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p31.html` — `894d402f19e1d35f14f831bc7de7422969407048639af340c6e0f50b944dddf1`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p32.html` — `f6d0a3f481c42dc13433f5b48cfe7ea44339656e4c3f5640fda5b1936312d8ba`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p33.html` — `3603dc918dc44869be4ce1e6c741901298a1d685abd7e119ca50685d4f620cd0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p34.html` — `c4e494ba66c05f35f92aeb87707ad4ccf077a6f3778ff86ca7f62fac63a7371f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p35.html` — `5db9dfcefff79305fd4a9b9face92798f7827dfdc5d160c476c518e78b91d364`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p36.html` — `d100815c4b9080c1524ca5496748368393eba4fb1b3e0d38a93dcfe1c12f72b0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p37.html` — `06d56ee7337890dc0e0349073ae3ea861743cca0e0e527d5ddee085d31358635`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p38.html` — `cc45fcc851eb06dba5aa57f01c049da1d16989199b2a517f398da6b3bf0fc301`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p39.html` — `ffee1a2e9fc8b08d16ebaf2054c97aa6ae771cef812a71173d1c81250cfc9a12`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p40.html` — `2f9ac0acf3da8e4f1e6cde62ae8bedc04b25ab211ffc315db8eb5a3ebc1a2f27`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p41.html` — `c4b83441183f59af22ce0a8a628135cb46d1fa9a46b3539c879c41beda501d09`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p42.html` — `0a1c6aa397e48dda93028172ce0491ea82bc866f8d05917c8f3e3c91ee7eec86`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p43.html` — `1ca4ac72811c8ad2c17d8f28322a34948c1bc84ebbf8163269b4c2122ad5dee1`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p44.html` — `c685796ac707b7c021e027926c6f05fcb1959b634ff9713ed38e1d844c305acd`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p45.html` — `ab85635ec803115a14fa869506d6cea966900afa070593468ab4a5a3360ad53f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p46.html` — `f4131b6480786126f0374c89d20d22244535a74bf520249ec3858a0e2db11ff4`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p47.html` — `2d25808d14827cd9bfe96d9c1c6df033885834e8d467b92eb5d02c53f77e4ad7`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p48.html` — `351d0c44abf08e681a92af6a0d608c34d898e7262478f5014d69844e32e2c16f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p49.html` — `679b711bf23592a1328f50a411fc551d9894ec1e9ae5c11d818ce8e07737197f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p50.html` — `a8641ba04cd0ce88cdbc71d2a64dbc290db58bea91226bcb3ae5cc516c28beaa`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p51.html` — `5aa675b2ecab5d0fd3a4273cd163edbea5f5beb4a4ff12e83c31bd8fb0421781`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p52.html` — `4f765c88c1b26633634df61bda4abfb01eb3cfe24a4861606be3f62d39a7b01d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p53.html` — `c39e9dca638c50118f197e112e4cd99eb437a6429534a1dc8ebb1f2e01ae56bf`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0910/review-0910-Cells_and_Cellular_Respiration/explanations/p54.html` — `e0534f4bb14a523ceed8649bb6e3ce00cfda3bf3ea8e3858ee6605fdc44346d6`

### 0915

source: `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/source.json`
input_hash: `68876bf5a9dfd4ade34f0f8ed6915826a83b1c4d92506a185bb32177ae516aca`

| item | source_visual | content | 원천 및 결론 |
|---|---|---|---|
| p1:main | pass | pass | 기출 2강 3; 기출 2강 합본 3번 (PDF 1쪽); 첫안정산물 탄소수1;교재2 p50 |
| p2:main | pass | pass | 기출 2강 4; 기출 2강 합본 4번 (PDF 1쪽); 물분해·전자1;교재2 p46 |
| p3:main | pass | pass | 기출 2강 5; 기출 2강 합본 5번 (PDF 1쪽). 원문의 NAD 위첨자 표기 깨짐을 NAD⁺로 바로잡았어요.; 직접발효단계 NAD+2/앞선해당ATP 구분을 전구역 유지;교재2 p43 |
| p4:main | pass | pass | 기출 2강 9; 기출 2강 합본 9번 (PDF 1쪽); 명반응 물→O2/4틀림;교재2 p44–48 |
| p5:main | pass | pass | 기출 2강 12; 기출 2강 합본 12번 (PDF 1쪽); 루비스코O2기질2;교재2 p50 |
| p6:main | pass | fail | 기출 2강 13; 기출 2강 합본 13번 (PDF 1쪽). 합본에서 이 문항의 질문과 보기는 11번 옆에 이미지로 밀려 인쇄되어 있고, 13번 자리에는 답만 남아 있어요(PDF 2쪽 위).; FAIL I3: verify34 원자수보존1뿐 주장은5와 모순 |
| p7:main | pass | pass | 기출 2강 17; 기출 2강 합본 17번 (PDF 2쪽); O2출처물1;교재2 p44–48 |
| p8:main | pass | pass | 기출 2강 21; 기출 2강 합본 21번 (PDF 2쪽). 합본에 보기 번호만 있고 보기 글이 인쇄되지 않아, 보기 없이 답을 쓰는 문항으로 실었어요.; 원문보기없음 공개,G3P단답;교재2 p48–49 |
| p9:main | pass | pass | 기출 2강 24; 기출 2강 합본 24번 (PDF 2쪽). 원문 CO₂ 표기 깨짐을 바로잡았어요. 문항 옆에 인쇄된 효소 그림은 14번 그림이라 싣지 않았어요.; 한회전 탄수화물단위4;교재2 p50 |
| p10:main | pass | pass | 기출 2강 26; 기출 2강 합본 26번 (PDF 3쪽). 원문 NADP 위첨자 표기 깨짐을 바로잡았어요.; NADP+수용체4;교재2 p46–48 |
| p11:main | pass | pass | 기출 2강 31; 기출 2강 합본 31번 (PDF 3쪽). 원문 H₂O, CO₂ 표기 깨짐을 바로잡았어요.; 연결 ATP·NADPH4;교재2 p44 |
| p12:main | pass | pass | 기출 2강 32; 기출 2강 합본 32번 (PDF 3쪽). 보기 (4)의 '이산회탄소'는 원문 표기 그대로예요(이산화탄소의 오타).; 암반응O2 틀림3;교재2 p44,47–48 |
| p13:main | pass | pass | 기출 2강 36; 기출 2강 합본 36번 (PDF 3쪽); 젖산3/무기호흡 원문을발효뜻으로구분;교재2 p43 |
| p14:main | pass | pass | 기출 2강 40; 기출 2강 합본 40번 (PDF 3쪽). 합본에 보기가 인쇄되지 않고 답만 있어, 보기 없이 답을 쓰는 문항으로 실었어요.; CAM밤고정낮닫음;교재2 p50–51 |
| p15:main | pass | pass | 기출 2강 41; 기출 2강 합본 41번 (PDF 4쪽). 원문 CO₂ 표기 깨짐을 바로잡았어요.; FAD 비투입2;교재2 p47,50 |
| p16:main | pass | pass | 생성 변형 s0-atp-yield; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 기질 수준 인산화와 산화적 인산화의 개수. 근거 토픽: 포도당 한 분자에서 ATP 32개(s0-atp-yield); 10x2.5+2x1.5=28/3;s0-atp-yield/교재2 p42 |
| p17:main | pass | pass | 생성 변형 s0-chemiosmosis; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 전자 흐름과 H⁺ 농도 기울기의 짝, 직접 에너지원과 궁극 에너지원, 이론과 과정의 이름. 근거 토픽: 화학삼투설과 최종 전자수용체(s0-chemiosmosis); 전자유지·누출 기울기감소2;s0-chemiosmosis/교재2 p41–42 |
| p18:main | pass | pass | 생성 변형 s1-no-oxygen; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 산소가 없으면 전자전달계만 멈춘다는 착각(NAD⁺ 고갈). 근거 토픽: 산소가 없으면 해당과정도 멈춘다(s1-no-oxygen); 발효불가 NAD+고갈2;s1-no-oxygen/교재2 p43 |
| p19:main | pass | pass | 생성 변형 s1-fermentation; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 젖산 발효와 알코올 발효의 전자수용체, 발효와 세포호흡의 최종 전자수용체. 근거 토픽: 젖산 발효와 알코올 발효(s1-fermentation); 아세트알데하이드3;s1-fermentation/교재2 p43 |
| p20:main | pass | pass | 생성 변형 s3-pigments; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 흡수 스펙트럼과 작용 스펙트럼. 근거 토픽: 엽록체와 광합성 색소(s3-pigments); 산소측정 작용스펙트럼2;s3-pigments/교재2 p46–47 |
| p21:main | pass | pass | 생성 변형 s3-electron-flow; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 광계 1·2의 번호와 전자 흐름 순서, 물의 광분해 위치. 근거 토픽: 명반응의 전자 흐름과 ATP 합성(s3-electron-flow); 물→PSII→ETC→PSI→NADP+/2;s3-electron-flow/교재2 p48 |
| p22:main | pass | pass | 생성 변형 s3-electron-flow; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 미토콘드리아와 엽록체의 H⁺ 이동 방향, ATP 생성 장소. 근거 토픽: 명반응의 전자 흐름과 ATP 합성(s3-electron-flow); 내강H+/스트로마ATP2;s3-electron-flow/교재2 p48 |
| p23:main | pass | pass | 생성 변형 s4-photorespiration; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 광호흡과 세포호흡, 루비스코의 두 기능. 근거 토픽: 광호흡과 C4·CAM 식물(s4-photorespiration); 기공닫힘CO2감소O2상대증가2;s4-photorespiration/교재2 p50 |
| p24:main | pass | pass | 기출 2강 20; 기출 2강 합본 20번 (PDF 2쪽); 수업교재32ATP기준5;교재2 p42 |
| p25:main | pass | pass | 기출 2강 34; 기출 2강 합본 34번 (PDF 3쪽); 무산소근육 순2ATP4;교재2 p43 |
| p26:main | pass | pass | 웹과제 2장 q01; 웹과제 2장 q01 (스크린샷 s01); 명반응 CO2고정아님B;교재2 p44 |
| p27:main | pass | pass | 웹과제 2장 q03; 웹과제 2장 q03 (스크린샷 s03); 무산소근육 순2ATP E;교재2 p38,43 |
| p28:main | pass | pass | 웹과제 2장 q06; 웹과제 2장 q06 (스크린샷 s06); C의만은 틸라코이드배제라거짓/E;주어누락공개;교재2 p41,48 |
| p29:main | pass | pass | 웹과제 2장 q07; 웹과제 2장 q07 (스크린샷 s07); 관계→광계 해석조건 본문verify sum 유지/B;교재2 p45–46 |
| p30:main | pass | pass | 웹과제 2장 q10; 웹과제 2장 q10 (스크린샷 s10, s11); 암반응 O2 C틀림;교재2 p44,47–48 |
| p31:main | pass | pass | 웹과제 2장 q11; 웹과제 2장 q11 (스크린샷 s12); C6/회전C1=6/C;교재2 p48–50 |
| p32:main | pass | fail | 웹과제 2장 q13; 웹과제 2장 q13 (스크린샷 s14); FAIL I4: verify35 반대가정 결론 역전;교재2 p46–48 |
| p33:main | pass | pass | 웹과제 2장 q14; 웹과제 2장 q14 (스크린샷 s15); 다섯구역 분석D/공식미확인/C압축유보/전자방향일관;교재2 p38,43 |
| p34:main | pass | pass | 생성 변형 s4-calvin; 기출 2강 41번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: 광독립반응(암반응)에서 '빛이 직접 필요 없다'는 뜻, 캘빈 회로의 세 가지 투입물. 근거 토픽: 캘빈 회로의 세 단계(s4-calvin). 캘빈 회로에 꼭 들어가는 재료가 세 가지뿐이라 보기를 4개로 두었어요. 보기 CO₂·NADPH·ATP는 투입물이 셋뿐이라 원문 보기와 같은 낱말을 쓸 수밖에 없었어요.; 직접빛은 비투입3;s4-calvin/교재2 p47,50 |
| p35:main | pass | pass | 생성 변형 s2-reverse; 기출 2강 31번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: 두 반응을 잇는 분자(ATP·NADPH와 그 빈 형태 ADP·NADP⁺), 호흡의 운반체 NADH와 광합성의 운반체 NADPH, 회로 안에서만 도는 물질. 근거 토픽: 광합성은 세포호흡을 거꾸로 돌린 것(s2-reverse).; 돌아가는ADP·NADP+2;s2-reverse/교재2 p44 |
| p36:main | pass | pass | 생성 변형 s3-photosystem; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 안테나 색소가 넘기는 것(에너지)과 반응 중심이 내주는 것(전자 자체), 물의 전자를 받는 광계의 번호. 근거 토픽: 광계와 물의 광분해(s3-photosystem); I에너지II전자III물전자/(가)P680/(다)O2/5;s3-photosystem/교재2 p46,48 |
| p37:main | pass | pass | 생성 변형 s4-calvin; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 효소 루비스코와 CO₂를 받는 5탄소 분자 RuBP, 캘빈 회로 세 단계의 물질 순서. 근거 토픽: 캘빈 회로의 세 단계(s4-calvin); A=PGA B=G3P C=RuBP/효소구별4;s4-calvin/교재2 p48–49 |
| p38:main | pass | pass | 생성 변형 s1-efficiency; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 에너지의 양과 에너지 효율(비율), ATP에 담기는 몫과 열로 나가는 몫. 근거 토픽: 세포호흡의 에너지 효율 34%(s1-efficiency); 64ATP/467.2+904.8=1372/34%유지3/수업교재수치차이공개;s1-efficiency |
| p39:main | pass | pass | 생성 변형 s3-electron-flow; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: '빛이 직접 필요 없다'와 '명반응 없이도 돈다'의 차이, 명반응 전자 흐름 순서와 ATP·NADPH 생성의 짝. 근거 토픽: 명반응의 전자 흐름과 ATP 합성(s3-electron-flow); PSII→PQ차단/ATP·NADPH감소/동일속도4틀림;s3-electron-flow/교재2 p47 |
| p40:main | pass | pass | 생성 변형 s2-autotroph; 원문 기출이 아닌 생성 변형이에요. 다루는 혼동: 독립영양 안의 광독립영양과 화학독립영양, 이화 과정과 동화 과정. 근거 토픽: 이화와 동화, 독립영양과 종속영양(s2-autotroph); CO2탄소원·무기물에너지·동화 ㄱㄷ4;s2-autotroph/교재2 p44 |

실제 읽은 source/설명 파일 SHA256:

- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/source.json` — `9d4f73318394c9b2d6ed4ee65110380d5dcccd66bf57be61c868f1285ac87512`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p1.html` — `668d275bb9ccd2fbbad86c612598c5b65bbecde40c40905d57a4cf159f23597a`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p2.html` — `b99b179db8afee4c9bba77c3b7a52a537a07471bad6063e29a15c04d785a616f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p3.html` — `28552b5361af6b4088389ddca4e882e04e1f635c176cd63ba2ac935fa10f49c4`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p4.html` — `e423343b1df3a9b22768e846ec1634c48c7c62f36d53fe65139f1040e3a0fd9f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p5.html` — `85f9f02223e6793ce80b361fc116075c5c2863f094708f94facb0de6e04a49d8`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p6.html` — `888a0ddabcda11d61bcb46d73d0659e46622621bc2c0bd7c3bedf03d36e163a8`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p7.html` — `6a74f8ba9192fbee41578fd2c2335cd4e09ef8260753b00729847f9ef95c02f9`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p8.html` — `ee09beded1662afa510d8a59d944312782aa5365024a4ebeb184a1c85c652b40`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p9.html` — `61741da53eae9d2037b43cca81af27403d2c546c3296ecee5b3cb9acfceabc38`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p10.html` — `d6995860d4b9604ff2e19b42ee841302e23cdeb579b5c51a9592bdb32db485b6`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p11.html` — `02b92f594476dcaced915297bbfb287486c1aee213f728507ec19da127a319e9`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p12.html` — `02deda619fe812c882546c1b6d0e78b0f8b750f382b1bc7c87ce12eb37f19bc0`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p13.html` — `821004692471f20dbc6cee91d2229b99a897a2d623f4fa66751e0e42c2169b4b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p14.html` — `1699de4689bbc540cc623bb09e792a37cae1aa22a97c9e63e36fb13c181f4172`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p15.html` — `f908d9a550a23b5beada438adc2e2f4511d25b29074f42afe6d214adbb7d76be`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p16.html` — `a796bf522e57cc2505cdcba03e0c9148c569fd1b7a7990a678b21496326a76c8`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p17.html` — `1e125c47a12751759909a2c9ba6c9fe376f14fce1b769e22bcf2c8ec7c373d54`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p18.html` — `cb096f9f314a1a38252533514be2d5c9c5e25ea2998b443bfa34ebbef0cf28a9`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p19.html` — `cc0fb5e368f8795d228c5f8835585bcaedb4860a1791a67670b25b9a11869c62`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p20.html` — `f9df1d24df8c093c0f5b23c18284e67dd1c135aea570893c2023f3ffed1eccb1`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p21.html` — `4329a2acd9e17d0425c9074b6352f8fe6b0b7c50563a849f482bcb60aaa69493`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p22.html` — `736d61441964dd6d9db2b336a36967630f5a58f865a5870fd5a6c3451dd51f5f`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p23.html` — `8126b430e5a3b84538538a5445b6a016cee60d289677ededf56e28c5d04ffa3b`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p24.html` — `b9f6b28827884f2ecc8506ed6247d411749acebd547c7a85390e3c6525c59642`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p25.html` — `74c8f5420c53ffe66dcbbe984f4fe8aca63387b2b8dac67f6cf5a6cbeb0abe2e`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p26.html` — `c5d64668b442557c60f7a830958a7e300396feca21b6b66b0ba65e8a136f461e`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p27.html` — `1baadb3df3250ac07bf1c6885df6247e16136fce4c5cfb9f462df897a936c840`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p28.html` — `cfae634804731593e7b0ababf6493ad5a3e259f85c337797ede041d74a27b163`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p29.html` — `9556436883b456f89e38dc4546cb9308e3cb361a7e5eb86b48ce3395aacb5a42`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p30.html` — `b79e8efd2b49eb37bb62660e7808fd4c48e78fa881d60677b6ab739e3672a257`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p31.html` — `ced91eb443879f17309d40a685b02b230eca7aebedeb8fbe7f46ba4b77ab6a8c`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p32.html` — `8abb94ff21c0003bb057641e8eb9e4dc20640866e398dc49cfda6a116ca5e75d`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p33.html` — `55ab8f99c9e2addf09236dbc5afc27a30a33af5f24fa7a61c7dec2037cb155e5`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p34.html` — `9c27272e791607f84bf07463a7cd097d59afb20e8325ba252b4d17183a88b9de`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p35.html` — `dd470258427c0e2d002fe5e2889d758d17c50369072ebc2e3eee7f0c49505f02`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p36.html` — `84345ff6e5a1687a4544342c44741c0fcc025efbe1613a00bcffa70d5fa9a1cc`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p37.html` — `ed72495cb31b9290c9b9f9326cecb077de59a9cdb0412893605a455aa4f5e3ff`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p38.html` — `d535e1260e5246612f434ba7627344461501f1d7e87a7b74b16cb686354a11c8`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p39.html` — `932727000285269dac4add61ecf52e63f07ce2f52ad1d4582d67fdd08c3862a3`
- `/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/explanations/p40.html` — `bd1346a7788c64402750651b430a3b3e853875d2bfff7a6c7951f422d8184e50`
