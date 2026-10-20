# source_visual 再검토 — 1013 / 1015

검토일: 2026-10-20 KST. 원문·노트는 읽기만 했으며, 이 evidence와 임시 PNG만 새로 작성했다.

## 실제 수행 및 범위

- 기출 6강 합본 PDF 1~5쪽을 pdftoppm 115 dpi로 렌더링하고 view_image로 5쪽 모두 직접 보았다. 1013 기출 원문 25문항과 1015 기출 원문 7문항의 발문·보기 순서·수치·부정 표현을 PDF와 대조했다.
- 1013의 생성 변형 12문항(p26~p37), 1015 생성 변형 12문항(p8~p19)의 모든 문제·보기·표·인라인 SVG 마크업을 읽고 같은 날짜 .pack/variants.md의 근거 토픽과 대조했다. 생성 변형을 실제 기출로 분류하지 않았다.
- 교재 PDF의 인쇄 121~128, 130~137쪽(파일 4~11,13~20쪽)을 pdftoppm으로 렌더링 후 view_image로 직접 확인했다. PCR 그림6.4, 겔 그림6.5, STR 그림6.6, 복제양 그림6.8, 발광담배 그림6.9, 황금쌀 그림6.10, CRISPR 그림b·PERV 그림c를 확인했다.
- 관련 두 정리노트에서 PCR/RT/STR/친자/핵치환/발현/미세배열/CRISPR/위험 설명을 읽고 variants 토픽과 연결됨을 확인했다. 인쇄물의 핵치환 설명은 핵 유전정보 중심이며 미토콘드리아 제공자라는 보충은 노트의 해당 설명을 근거로 구별했다.
- 이번 역할은 출처/전사와 그림의 의미 대조이다. 정답의 독립 재풀이와 최종 HTML 시각 배치는 별도 역할이다. HTML 인라인 SVG 4개의 실제 브라우저 렌더링은 본 역할에서 직접 보지 않았으며 browser 검토 대상으로 전달했다.

## 원문별 대조

|날짜/문항|대조한 출처|관찰|
|---|---|---|
|1013 p1|기출 PDF 1쪽 원문3|발문·보기/수치 보존 확인|
|1013 p2|기출 PDF 1쪽 원문5|발문·보기/수치 보존 확인|
|1013 p3|기출 PDF 1쪽 원문6|발문·보기/수치 보존 확인|
|1013 p4|기출 PDF 1쪽 원문7|발문·보기/수치 보존 확인|
|1013 p5|기출 PDF 1쪽 원문8|발문·보기/수치 보존 확인|
|1013 p6|기출 PDF 2쪽 원문9|발문·보기/수치 보존 확인|
|1013 p7|기출 PDF 2쪽 원문12|발문·보기/수치 보존 확인|
|1013 p8|기출 PDF 2쪽 원문13|발문·보기/수치 보존 확인|
|1013 p9|기출 PDF 2쪽 원문14|발문·보기/수치 보존 확인|
|1013 p10|기출 PDF 2쪽 원문15|발문·보기/수치 보존 확인|
|1013 p11|기출 PDF 2쪽 원문16|발문·보기/수치 보존 확인|
|1013 p12|기출 PDF 3쪽 원문18|발문·보기/수치 보존 확인|
|1013 p13|기출 PDF 3쪽 원문20|발문·보기/수치 보존 확인|
|1013 p14|기출 PDF 3쪽 원문23|발문·보기/수치 보존 확인|
|1013 p15|기출 PDF 3쪽 원문24|발문·보기/수치 보존 확인|
|1013 p16|기출 PDF 3쪽 원문25|발문·보기/수치 보존 확인|
|1013 p17|기출 PDF 4쪽 원문26|발문·보기/수치 보존 확인|
|1013 p18|기출 PDF 4쪽 원문27|발문·보기/수치 보존 확인|
|1013 p19|기출 PDF 4쪽 원문30|발문·보기/수치 보존 확인|
|1013 p20|기출 PDF 4쪽 원문31|발문·보기/수치 보존 확인|
|1013 p21|기출 PDF 4~5쪽 원문32|발문·보기/수치 보존 확인|
|1013 p22|기출 PDF 5쪽 원문33|발문·보기/수치 보존 확인|
|1013 p23|기출 PDF 5쪽 원문35|발문·보기/수치 보존 확인|
|1013 p24|기출 PDF 5쪽 원문36|발문·보기/수치 보존 확인|
|1013 p25|기출 PDF 5쪽 원문37|발문·보기/수치 보존 확인|
|1013 p26|.pack/variants.md p26 / 생성 변형 s0-pcr-components|문제 조건·보기·토픽 일치|
|1013 p27|.pack/variants.md p27 / 생성 변형 s0-pcr-cycle|문제 조건·보기·토픽 일치|
|1013 p28|.pack/variants.md p28 / 생성 변형 s0-pcr-uses|문제 조건·보기·토픽 일치|
|1013 p29|.pack/variants.md p29 / 생성 변형 s1-gel|문제 조건·보기·토픽 일치; 음극 홈 y45 / A90·B140·C195 / 아래 양극 y223로 거리 순서 확인|
|1013 p30|.pack/variants.md p30 / 생성 변형 s2-str|문제 조건·보기·토픽 일치|
|1013 p31|.pack/variants.md p31 / 생성 변형 s2-parentage|문제 조건·보기·토픽 일치|
|1013 p32|.pack/variants.md p32 / 생성 변형 s3-protein|문제 조건·보기·토픽 일치|
|1013 p33|.pack/variants.md p33 / 생성 변형 s3-therapy|문제 조건·보기·토픽 일치|
|1013 p34|.pack/variants.md p34 / 생성 변형 s4-clone|문제 조건·보기·토픽 일치; SVG A체세포→B핵제거난자→C자궁과 제시문 주체 일치|
|1013 p35|.pack/variants.md p35 / 생성 변형 s5-plant|문제 조건·보기·토픽 일치|
|1013 p36|.pack/variants.md p36 / 생성 변형 s5-plant|문제 조건·보기·토픽 일치|
|1013 p37|.pack/variants.md p37 / 생성 변형 s5-gmo|문제 조건·보기·토픽 일치|
|1015 p1|기출 PDF 1쪽 원문2|발문·보기/수치 보존 확인|
|1015 p2|기출 PDF 1쪽 원문4|발문·보기/수치 보존 확인|
|1015 p3|기출 PDF 3쪽 원문19|발문·보기/수치 보존 확인|
|1015 p4|기출 PDF 3쪽 원문21|발문·보기/수치 보존 확인|
|1015 p5|기출 PDF 3쪽 원문22|발문·보기/수치 보존 확인|
|1015 p6|기출 PDF 4쪽 원문29|발문·보기/수치 보존 확인|
|1015 p7|기출 PDF 5쪽 원문34|발문·보기/수치 보존 확인|
|1015 p8|.pack/variants.md p8 / 생성 변형 s2-array|문제 조건·보기·토픽 일치|
|1015 p9|.pack/variants.md p9 / 생성 변형 s1-proteome|문제 조건·보기·토픽 일치|
|1015 p10|.pack/variants.md p10 / 생성 변형 s1-splicing|문제 조건·보기·토픽 일치; 동일 전구RNA A-B-C → (가)A-B/(나)A-C 표지와 보기3 일치|
|1015 p11|.pack/variants.md p11 / 생성 변형 s3-mechanism|문제 조건·보기·토픽 일치; 전사 산물(가), 절단 단백질(나) 분담이 표지와 일치|
|1015 p12|.pack/variants.md p12 / 생성 변형 s2-array|문제 조건·보기·토픽 일치|
|1015 p13|.pack/variants.md p13 / 생성 변형 s3-repair|문제 조건·보기·토픽 일치|
|1015 p14|.pack/variants.md p14 / 생성 변형 s3-specificity|문제 조건·보기·토픽 일치|
|1015 p15|.pack/variants.md p15 / 생성 변형 s2-bioinfo|문제 조건·보기·토픽 일치|
|1015 p16|.pack/variants.md p16 / 생성 변형 s1-splicing|문제 조건·보기·토픽 일치|
|1015 p17|.pack/variants.md p17 / 생성 변형 s4-risks|문제 조건·보기·토픽 일치|
|1015 p18|.pack/variants.md p18 / 생성 변형 s4-applications|문제 조건·보기·토픽 일치|
|1015 p19|.pack/variants.md p19 / 생성 변형 s1-genome|문제 조건·보기·토픽 일치|

## 중요 결함·수치 재확인

- **1015 p4:** 기출 PDF 3쪽 원문21 보기5는 정확히 `250,000`이다. 교재 인쇄133쪽 문제5(e)도 `250,000`이며, 원 복습문제와 기존 설명 조각은 이를 25만으로 읽는다. 25,000으로 재전사하면 안 된다. 카드/기존 해설의 (4) 판정과 원문의 수치가 맞는다.
- **1015 p1:** 기출 PDF 1쪽 원문2 보기3은 “암호화 DNA”라고만 하며 cDNA를 명시하지 않는다. 기존 설명 fragment p1 understand에 `문항 결함` 공개가 있고, RNA 유래 cDNA로 해석할 때 인쇄3이 성립한다는 조건과 유전체DNA 해석의 한계를 보존한다. 교재131쪽 미세배열의 발현 비교 설명 및133쪽 문제6과 대조했다.
- **1013 p18:** 기출 PDF4쪽 원문27의 인쇄 빨간 답은3, 보기5는 가시광선이라고 되어 있다. 교재122쪽은 아가로오스가 큰 DNA 분리에 적합하다고 설명하며123쪽 그림6.5 단계4는 자외선 조사로 형광을 내게 한다. 기존 fragment p18은 인쇄3 오류 및 수업 UV 조건의 카드5와 광원·염료 생략에 따른 문항 결함을 함께 공개한다. 무조건5가 보편적으로 틀리다는 주장으로 바꾸면 안 된다.
- **1013 p8/p16/p23 및1015 p3:** 원문 표현의 생식세포 클로닝, 눈에 보이는 밴드의 절반, STR 서열·반복수, CCR5 침입 경로와 관련된 해석 한계를 임의로 원문 수정하지 않았다. 이번 링크 추가는 이러한 공개를 유지해야 한다.

## 원 문제/정리노트 해시 보존

- 복습문제_1013_PCR_and_DNA_Technology.html: baseline과 바이트 SHA256 일치 = True
- 정리노트_1013_PCR_and_DNA_Technology.html: baseline과 바이트 SHA256 일치 = True
- 복습문제_1015_Genomics_and_CRISPR.html: baseline과 바이트 SHA256 일치 = True
- 정리노트_1015_Genomics_and_CRISPR.html: baseline과 바이트 SHA256 일치 = True

## 사용 파일 절대 경로 및 SHA256

- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/23, 24 소스/6강 합본.pdf`
  SHA256 `487c1d07813ac7bce4da0755131e74133eb9284d92d055c0c9bdafbefd26b83e`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/교과서/생명과학_기초와_응용_2판/06장_DNA_기술과_유전체학.pdf`
  SHA256 `75ef10330fd5c19f77b824f1b682762666c0ddd25d65708bfdf465294d8464cb`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1013/복습문제_1013_PCR_and_DNA_Technology.html`
  SHA256 `71cafe0d17dace023494abbbec115c2a909cc023bdb89be2bd5d883305317b74`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1013/정리노트_1013_PCR_and_DNA_Technology.html`
  SHA256 `d069d0f7e0f3837e8f7f036a74d9bb5d5f7bb39bb59d15c61985cb392abcbcb8`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1013/.pack/variants.md`
  SHA256 `301df2c7a38163af87849a11d244b965aa42a7b96d20adc664ceb0300f24911d`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1015/복습문제_1015_Genomics_and_CRISPR.html`
  SHA256 `308b2acb719a578b101a103b51b6626256f9558bad37ba931a3437e47aeb8cce`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1015/정리노트_1015_Genomics_and_CRISPR.html`
  SHA256 `253f46e8dc2bb59538b6af1573313c50aa2117598b30bb4594bcf00baf7f3922`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1015/.pack/variants.md`
  SHA256 `1bd83eaf570cc28cb80455b31d63f146ff52869a98ade0ffc5351d4c21834801`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1013/.assets/자료_문제설명_1013_PCR_and_DNA_Technology/fragments/p18.html`
  SHA256 `4bb679e63142175a2e7b4562523aa0fa6d8d7ff0db8f90c0f8b0f6cf4e5cccdb`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1015/.assets/자료_문제설명_1015_Genomics_and_CRISPR/fragments/p1.html`
  SHA256 `c2a3babbd5c95c813afa97cd2c4cdb981a6fdc24ad6639c01d4a4401c629cda0`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/1015/.assets/자료_문제설명_1015_Genomics_and_CRISPR/fragments/p4.html`
  SHA256 `2e386239bd9e21c1155feb55be193c8cf12209355da508b7513d048dcf053920`

## 판정

출처 전사/조건/그림 의미의 source_visual 범위: PASS. 기존 결함 공개 유지 조건. 최종 조립본의 링크 표시·원문 패널과 4개 SVG 실제 화면은 browser 검토에서 별도로 확인해야 한다. 신규 링크의 의미 적합성은 content 역할에서 확인한다.
