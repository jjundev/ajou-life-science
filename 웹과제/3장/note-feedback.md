# 3장 실제 웹과제 — 정리노트 본문 생성 피드백

## 상태와 근거

2026-10-15 작성. 평가 `web-20261001-ch03`의 **13문항·14화면**을 대상으로 한 다음 본문 저작용 입력이다. 공식 답은 13개 모두 미확인(`official_answer: null`)이며, 원본은 2026-10-01 제출 전 선택 화면이다. 실제 제출·공식 채점 결과는 없다. 전체 수 13은 `intake.md`에 보존된 **2026-10-01의 사용자 확인값**이며 이번 대화의 새 확인 진술이 아니다.

- q12는 s12(무선택)·s13(선택)의 같은 문항이고, q13은 s14다. 두 화면으로 최초 판단이나 최종 제출을 알 수 없다.
- q01·q05·q06은 무선택이다. q07·q12는 제출 전 선택과 분석 답이 다르지만 공식 오답·확정 개인 오개념으로 취급하지 않는다. q11은 분류 기준에 따른 모호성을 유지한다. 개인 학습 원인 가설은 이 입력에서 생략한다.
- 아래 ‘현재 설명 충분’은 현재 자료의 개념 제공 여부다. 응시 전에도 같은 문장이 있었거나 사용자가 읽었다는 증거, 예상문제 적중·숙달 증거가 아니다. 현행 노트에는 캡처 뒤 보강된 부분이 있다. 자세한 시점 한계는 분석 보고서 1절을 따른다.
- 입력 작성 상태는 **다음 생성부터 사용 예정**이다. 기존 노트·해설·스킬·정본 bank를 수정하거나 재생성하지 않았으며, 본문 반영 완료나 실행 감사 완료를 뜻하지 않는다.

분석 근거: [전체 문항 대조·최소 개선안](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/feedback/20261015-211427-12cad335/report.md>) 4·6절 및 [근거 목록](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/feedback/20261015-211427-12cad335/evidence.json>). 원본 파일명·선택 상태는 [INTAKE](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/intake.md>)와 [BANK](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/questions.json>)를 따른다. 기존 [본문 피드백 절차](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.agents/skills/bio-review-pack/references/note-feedback.md>)를 그대로 사용한다.

아래 별칭은 문항별 근거의 실제 파일이다. SHA256은 이번 입력 작성 시 현재 바이트로 재계산했고 기존 evidence 목록과 일치했다. PDF 쪽수는 1-based이며, 교재 인쇄 쪽과 구별한다. 강의노트 3장 p1과 교재 PDF p4=인쇄 p57을 다시 대조했다. 그 밖의 원본 시각 판독·교재 렌더 대조 위치는 앞선 보고서와 동일 해시의 근거 기록을 인계하며, 이번에 모든 이미지를 다시 판독했다는 뜻은 아니다. 다음 생성 실행에서도 필요한 원천을 다시 읽고 실제 사용 범위·해시를 남긴다.

| 별칭 | 실제 파일 | SHA256 | 사용 범위 |
|---|---|---|---|
| BANK | [웹과제/3장/questions.json](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/questions.json>) | `4efb4aa35097c59f49a096ae8f56101affcc47faaebb246a30ee5eb82178dc98` | assessment; questions q01–q13; observations/analysis/issues; sources s01–s14 |
| INTAKE | [웹과제/3장/intake.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/intake.md>) | `5dbfc3dd72b205a69a6a97c54f7f4edeeebd0d43179d68c6fa54df8e7aee6b23` | 평가 정보, 선택·중복·표기 메모, 원본 인벤토리 전체 |
| s01 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.11.46.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.11.46.png>) | `207356a144abc38ad6a231f1be19abfcf460e1f50fd1c5593e46383f99c1ee6c` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s02 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.12.52.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.12.52.png>) | `67d041a1d145ff81140fd539d827dcfb620db2dab74e363401ce0b54fec03541` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s03 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.20.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.20.png>) | `8836ec7759deaf119d20f3ecbb2c6bf09676e60a23e41427debb1cc1268947ef` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s04 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.39.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.39.png>) | `af238c8b3b3c86ade785d3ef59bfb12be188f97f1b5bd426313cda281013d6be` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s05 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.51.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.13.51.png>) | `6349365a69be006a77a28c04f7e7947d9f1edab6211ba2f3e98c95883f88c0b7` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s06 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.14.31.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.14.31.png>) | `34195e96617c7aa6a8ceea822d5c20fa0ce50b16d6b62809251ce898df0fee49` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s07 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.15.15.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.15.15.png>) | `5398e281e82c66084a3e6328dd42597d5980dddada9c041a088e60784de353c8` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s08 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.15.41.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.15.41.png>) | `d3408b9bc09c0396dd9ff5b211e4ac17445326ec2f7730a9f9e55e908e55cde9` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s09 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.16.47.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.16.47.png>) | `c447a890d2d0919a584d1b102f4e4cf463093fc02e8d27cd1530686c127a0601` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s10 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.05.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.05.png>) | `21ffa6131fdbac448241ed887bf573c768d2a6241c1f36754707c8ad185da70e` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s11 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.39.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.39.png>) | `c4efc24e9879be2794d59536e70ac5f6900d0028bf77a43722258ae0d7bb843a` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s12 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.52.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.17.52.png>) | `3a8993265c77e83e03fb83ab754906f20c855e13c93694b9ba1bad6c02016681` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s13 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.18.36.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.18.36.png>) | `93038002e682397aa9cb50d7d3a9f8a7f76f93e4e83213c4f087e354bbdc1f0d` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| s14 | [웹과제/3장/raw/스크린샷 2026-10-01 오후 12.19.04.png](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/raw/스크린샷 2026-10-01 오후 12.19.04.png>) | `adde3febdcaecb6b05aee06f4ab6d8523ac474813af605eaa14638000380b934` | 전체 원본 화면; 문항 연결은 아래 원본 필드 |
| N17 | [복습노트/0917/.assets/정리노트_0917_Cell_Division.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md>) | `13325bcb902b5fdaa32666d335e54b4f0b8b2229316d133e52969adfdd460b16` | L230–268, L283–378, #s2-ploidy, L492–539, L954–975, L1067–1088 |
| N22 | [복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md>) | `36ca7262ee9926d3b82850eddc57a10911bfe1243005e851b95539fefc16098c` | L159–181, L253–295, L555–607, L721–751, L793–828 |
| N29 | [복습노트/0929/.assets/정리노트_0929_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0929/.assets/정리노트_0929_Heredity.md>) | `83ce4f2f54e150cf47359e920547f5326ece8aab89bead807a3fa828b55a039f` | #s2-morgan L391–420 |
| R17 | [복습노트/0917/.assets/복습문제_0917_Cell_Division.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/복습문제_0917_Cell_Division.md>) | `af89d5c6776bbe8d6bd6fd264f4e77023021519017e85d95e31d79e822f6160d` | P30–P35 |
| R22 | [복습노트/0922/.assets/복습문제_0922_Cell_Division_and_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/복습문제_0922_Cell_Division_and_Heredity.md>) | `5d9acbcf97e001269991e273da03cd71f30ab660312ba3639c5e43701bb5d8e4` | P4, P38–P43, P47 |
| R29 | [복습노트/0929/.assets/복습문제_0929_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0929/.assets/복습문제_0929_Heredity.md>) | `6baf278356a1ee325b54fe13998a37a58691fc1d56bc991c70b68ada92691e1f` | P43 |
| E17 | [복습노트/0917/.assets/문제설명_0917_Cell_Division.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/문제설명_0917_Cell_Division.md>) | `5175c25b52ba9b6dc0ba0ec16f4539a00b76e8ec0aebf30748fc91a01720532b` | P35 L568–610 |
| E22 | [복습노트/0922/.assets/문제설명_0922_Cell_Division_and_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/문제설명_0922_Cell_Division_and_Heredity.md>) | `ff94f76bc41d2dc7b10ada3011075f2e25461c911ac0213a20ac8019e3549f6a` | P42 L498–542 |
| E29 | [복습노트/0929/.assets/문제설명_0929_Heredity.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0929/.assets/문제설명_0929_Heredity.md>) | `f5cb7a0dedbf7ba5f70c9f220ace2903f76e73d5607a1b81b785afaca788015b` | P43 L86–133 |
| T17 | [STT/0917 생명.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/STT/0917 생명.md>) | `fa2730f4232674828d890596e5ea2c72f306a45fa84d490c860fb399052d3c87` | L356–366, Part 02 17:09–17:33 |
| T22 | [STT/0922 생명.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/STT/0922 생명.md>) | `25788b5424976fdcf9c0c140cb5303f31a2b5b324b7187c1d84e7b1c1a572848` | L270–282, L914–923 |
| T29 | [STT/0929 생명.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/STT/0929 생명.md>) | `f77b183a8e25dc1e78e2fcef912f29b75b2633265829d697ca0f800f6062ff40` | L58–68 |
| SL3 | [강의노트/3장 세포분열.pdf](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/강의노트/3장 세포분열.pdf>) | `752cf8bf606b4e4100470310748d7404223097046d8fcc2beac478df6e7b8728` | PDF p1 G1/S/G2, p2 분열 단계, p3–5 감수분열 |
| BOOK3 | [교과서/생명과학_기초와_응용_2판/03장_세포분열.pdf](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/교과서/생명과학_기초와_응용_2판/03장_세포분열.pdf>) | `45524873ede1eff000753ba817252288e9c63feabe692e7d8785e9f97e6738c1` | PDF p4=인쇄 p57; 보고서의 p5=58, p11=64, p14=67 |
| GLOSS | [교과서/생명과학_기초와_응용_2판/부록_용어풀이.pdf](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/교과서/생명과학_기초와_응용_2판/부록_용어풀이.pdf>) | `057aa3cae4056f0ed6f8f20d059c143b606020cda4601bba7902d3263974ddc3` | PDF p12=G-12 histone |
| NF | [.agents/skills/bio-review-pack/references/note-feedback.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.agents/skills/bio-review-pack/references/note-feedback.md>) | `2b945c5cfd5014ba3050731d7b6151a8fc52ba5c7cc6e163516d987a0e5b3520` | 전체: 입력·8열 감사·보충·augment 경계 |
| 분석 report.md | [report.md](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/feedback/20261015-211427-12cad335/report.md>) | `e83f108139587ecec1e1197cd134923ff9e1d6812d8af062a05130049ea46ec5` | 문항 대조·개선안 및 근거 해시 |
| 분석 evidence.json | [evidence.json](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/웹과제/3장/feedback/20261015-211427-12cad335/evidence.json>) | `c53681a356b75e11ad71b6244e0cdba8c0da2483f6d0813f05970191ab53e613` | 문항 대조·개선안 및 근거 해시 |

## 문항별 본문 저작 입력

다음 방향은 실행 계획이다. 각 범위에서 실제 충족 여부를 확인한 뒤에만 실행 감사표에 결과를 기록한다. N17/N22/N29는 각각 0917/0922/0929 노트이며 R·E도 날짜를 함께 해석한다.

### q01 유사분열의 모양과 순서

- 원본: s01
- 판별 기준: 응축 → 중앙 배열 → 자매염색분체의 양극 분리 → 두 핵 형성을 연결한다. 둥근 핵이 보이는 간기와도 구별한다.
- 근거: N22 #s1-phases L253–269; R22 P38; 원사진과 승인된 단순화 도식의 차이는 INTAKE.
- 처리 방향: 현재 설명 충분: 순서·형태 기준을 유지한다. 사진 자체와 도식을 동일시하거나 도식 존재로 사진 판독 능력을 확인했다고 쓰지 않는다. 무선택을 진단에 쓰지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s1-phases>) — formal/warn의 중앙 배열·두 무리·두 핵 기준. 기존 원사진 판독 한계 공개 유지.

### q02 염색체 쌍 수와 배우자 종류

- 원본: s02
- 판별 기준: 2n에서 상동염색체 쌍 수 n을 구한 뒤 2ⁿ을 계산한다. 교차를 제외한 한 개체의 여러 번 감수분열에서 가능한 종류이며 한 번에 생기는 세포 수와 구별한다.
- 근거: N22 #s3-assortment L793–828; R22 P39와 기존 단위 전환 연습.
- 처리 방향: 현재 설명 충분: 쌍 수·세포 수·종류 수를 구별하는 최소 과정을 유지한다. 선택 일치로 숙달을 확정하지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s3-assortment>) — formal의 쌍 수→지수 과정과 warn의 한 개체/한 세포 한 번 구별.

### q03 분리되는 대상의 비교

- 원본: s03
- 판별 기준: 유사분열 후기는 자매염색분체, 감수 I은 상동염색체, 감수 II는 자매염색분체를 분리한다.
- 근거: N17 #s2-ploidy; N22 #s2-two-divisions L555–560; R22 P40.
- 처리 방향: 현재 설명 충분: ‘분리’라는 동사뿐 아니라 대상과 단계를 짝지어 유지한다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s2-two-divisions>) — formal의 I/II 비교와 [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s2-ploidy>) 이전 개념 연결.

### q04 세포주기 단계와 기능

- 원본: s04
- 판별 기준: G1 성장·분자 합성, S DNA 복제, G2 분열 준비, M 실제 분열의 순서와 기능을 짝짓는다.
- 근거: N17 #s3-phases L510–539; N22 #s1-interphase L159–181; SL3 PDF p1; R17 P30.
- 처리 방향: 현재 G1 판별 설명은 충분하다. q12 보강과 연결하되 모든 단백질 합성을 G2로 옮기지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s3-phases>) — formal/warn의 기능 짝 유지; q12의 최소 보강만 공유.

### q05 염색체 포장과 응축 시점

- 원본: s05
- 판별 기준: DNA–히스톤 구성, 복제된 자매 관계, 전기의 응축 시작과 중기의 중앙 배열을 구별한다. 히스톤 양전하는 DNA 결합 설명이다.
- 근거: N17 #s2-chromatin L230–268; N22 #s1-phases L255–256; GLOSS PDF p12=G-12 histone; R17 P31.
- 처리 방향: 현재 설명 충분: 기존 양전하 보충과 단계 구분을 유지한다. 무선택·사후 보강으로 응시 전 노출이나 결함을 추정하지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s2-chromatin>) — formal/supp 유지; [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s1-phases>)의 응축/배열 비교 연결.

### q06 상동·자매·대립유전자·동원체

- 원본: s06
- 판별 기준: 그림에서 같은 좌위 A/a의 대립유전자 관계, 상동염색체 쌍, 복제로 생긴 자매염색분체와 동원체 위치를 구별한다. 모양만 같다고 모두 자매로 부르지 않는다.
- 근거: N17 #s2-sister-homolog L283–378; N22 #s1-interphase L167–181; R17 P32.
- 처리 방향: 현재 설명 충분: 이름·기원·위치를 함께 유지하고 무선택을 취약점으로 취급하지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s2-sister-homolog>) — formal/warn의 관계 비교와 기존 그림 라벨.

### q07 교차·재조합과 연관

- 원본: s07
- 판별 기준: 교차는 물리적 교환, 재조합은 새 대립유전자 조합이다. 분배·수정도 다양성을 만든다. 연관은 같은 염색체 유전자들이 함께 전달되는 경향이며 연관돼도 교차로 재조합형이 생길 수 있다.
- 근거: N22 #s3-crossover L721–751; N29 #s2-morgan L391–420; T22 L914–923, T29 L58–68; R22 P4/P47, R29 P43.
- 처리 방향: 현재 개념·연습은 충분하므로 회차 연결을 우선한다. 0922에서는 당시 미학습인 연관을 앞당겨 가르치지 않고 이름만 예고하거나 보류한다. 0929에서는 이전 교차/재조합과 연결한다. 추가 명칭 훈련을 개인 필수로 정하지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s3-crossover>) — 0922 formal의 교환→새 조합 유지; 0929 [N29](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0929/.assets/정리노트_0929_Heredity.md#s2-morgan>) formal/warn에서 이전 [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s3-crossover>)로 연결. 0917 범위로 이동 금지.

### q08 종양 억제 기능과 암 위험

- 원본: s08
- 판별 기준: 정상 촉진 유전자·변이 발암 유전자·종양 억제 유전자를 구별한다. 종양 억제 기능 상실은 위험 증가이며 단일 변화가 즉시 암을 보장하지 않는다.
- 근거: N17 #s5-suppressor L954–975, #s5-oncogene; R17 P33.
- 처리 방향: 현재 중심 기능 설명 충분: 유지한다. p53 사멸 경로 세부를 이번에 모두 검증한 것으로 확대하지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s5-suppressor>) — formal/warn의 정상 기능·기능 상실·위험 증가 대비.

### q09 감수분열 사이 재복제 없음

- 원본: s09
- 판별 기준: 감수분열 전 DNA 복제 한 번과 분열 두 번을 연결한다. 감수 I과 II 사이에는 DNA를 다시 복제하지 않는다.
- 근거: N22 #s2-two-divisions L595–607; BOOK3 PDF p14=인쇄 p67의 분열간기; R22 P41.
- 처리 방향: 현재 설명 충분: q03의 분리 대상과 q13의 DNA 양을 같은 흐름으로 연결한다. 원문의 M기 표현을 일반 세포주기 정의로 확대하지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s2-two-divisions>) — formal/supp의 1회 복제·2회 분열과 중간 무복제 근거.

### q10 접촉 저해와 암세포

- 원본: s10
- 판별 기준: 정상 세포는 이웃과 닿으면 성장·분열을 멈추지만 암세포는 접촉 저해를 잃고 증식할 수 있다. 정상/암 대비와 전이를 구별한다.
- 근거: N17 #s5-tumor L1067–1088; R17 P34.
- 처리 방향: 현재 설명 충분: 정상과 암의 대비를 유지한다. 원문 ‘측징’ 오타는 bank issues대로 보존하며 원문을 수리하지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s5-tumor>) — formal 비교와 warn의 접촉 저해 방향.

### q11 전기와 전중기 분류의 모호성

- 원본: s11
- 판별 기준: 적도면 정렬은 중기다. 핵막 소실은 엄격한 5단계에서는 전중기이고 수업의 4단계 통합에서는 전기에 포함한다.
- 근거: N22 #s1-phases L253–277·295; SL3 PDF p2; T22 L270–282; R22/E22 P42.
- 처리 방향: 모호성 유지: 수업 통합 기준과 엄격한 전중기 구분을 병기한다. 단일 공식 답으로 확정하지 않고 답 글자 암기를 지시하지 않는다. 이 문항을 개인 취약점·확정 정답률 근거로 쓰지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s1-phases>) — formal/warn의 4단계/5단계 구별과 P42의 기존 결함 공개 유지.

### q12 G2 재료 준비와 M기 실행

- 원본: s12, s13
- 판별 기준: G1의 단백질 등 합성·성장, S의 DNA 복제, G2의 분열에 필요한 단백질 합성·준비와 M기의 방추체 형성·염색체 분리를 동사로 구별한다. 단백질 합성을 G2에만 한정하지 않는다.
- 근거: SL3 PDF p1의 G1/S/G2 정의; BOOK3 PDF p4=인쇄 p57의 G2 단백질 합성 계속; T17 L356–366은 분열 준비까지만 발화. N17 L514·539, N22 L163의 추상적 준비와 E17 P35 L568–610을 비교.
- 처리 방향: 다음 생성 최소 보강: 0917의 ‘잠깐 쉬면서’를 활동이 드러나는 설명으로 바꾸도록 한다. 기존 G1/S 단백질 합성 설명은 유지한다. 구체적 합성 내용은 수업 발화와 구별해 원천을 붙인다. 선택 불일치 원인을 확정하지 않는다.
- 저작 위치: [N17](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0917/.assets/정리노트_0917_Cell_Division.md#s3-phases>) — formal/warn의 준비/실행 대비; 발화보다 구체적인 내용은 기존 supp 배지·SL3/BOOK3 출처 사용. 0922 [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s1-interphase>)에는 짧은 구분과 0917 링크.

### q13 세포당 DNA 양의 비교

- 원본: s14
- 판별 기준: G2 DNA 양을 X라 하면 감수 I 완료 뒤 세포당 X/2이고, 중간 재복제 없이 중기 II도 X/2다. 염색체 수·염색분체 가닥 수·세포당 DNA 양을 구별한다.
- 근거: N22 #s2-two-divisions L590–607; BOOK3 PDF p11=인쇄 p64, p14=인쇄 p67; R22 P43.
- 처리 방향: 현재 설명 충분: 기호→새 수치와 비교 단위를 유지한다. q09와 같은 원리를 묶되 개인 전이 성공으로 해석하지 않는다.
- 저작 위치: [N22](</Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0922/.assets/정리노트_0922_Cell_Division_and_Heredity.md#s2-two-divisions>) — formal/supp의 세포당 DNA 양 표와 무복제 연결.

## 다음 저작·검토 지침

1. **최소 본문 보강은 q12다.** 다음 0917 #s3-phases의 권장 문장은 다음과 같다. “G2기에는 분열에 필요한 단백질 등을 합성하며 준비해요. M기에는 방추체 형성과 염색체 분리 등 실제 분열이 진행돼요. 단백질 합성이 G2기에서만 일어나는 것은 아니에요.” G1/S에서의 합성 설명을 유지하고, M기에는 합성이 전혀 없다는 단정을 만들지 않는다. T17의 발화보다 구체적인 부분은 기존 supp 출처·배지 규칙을 적용한다. 0922 #s1-interphase에는 짧은 대비와 이전 노트 링크로 연결한다. 문장 삽입 여부와 레이어 적합성은 다음 저작·의미 검토에서 확인한다.
2. **q07은 기존 설명과 연습을 연결한다.** R22 P4(명칭), P47(현상), R29 P43을 우선 활용한다. 해당 회차의 실제 수업 범위를 확인하고, 0922에 0929의 연관 설명을 당겨 넣지 않는다. 선택 불일치만으로 새 훈련·새 문제를 의무화하지 않는다.
3. **해설 표현 교정은 다음 해설 갱신 때 수행한다.** E17 P35 L610의 근거 없는 “처음에 A를 고른”을 제거하고 개인 선택보다 개념상 혼동을 설명한다. E29 P43 L128도 개인 선택 언급 대신 재조합/연관의 대비를 남기는 것을 우선한다. 선택 기록을 꼭 남기면 제출 전 캡처라는 점과 최종 제출·공식 채점 미확인을 함께 쓴다. 이 입력은 해설 수정·검토·재발행을 수행한 기록이 아니다.
4. **실행 감사표는 다음 생성에서 새로 작성한다.** NF의 8열 `피드백 ID | 원본 source | 필요 개념/판별 기준 | 범위 상태 | 대상 토픽/이전 노트 링크 | 계획 레이어 | 적용 상태 | 본문 문장 또는 보류 이유`를 사용한다. q01~q13을 매 실행에서 모두 검토하고 이번/이전/미학습/불확실 범위를 명시한다. 계획은 ‘예정’으로 남기고, 작성 뒤 실제 문장·정확한 링크 또는 보류 이유를 채운다. ‘기존 설명 충분’도 실제 판별 문장을 다시 확인한 결과로 기록한다. 입력·원본·강의노트·STT·교재의 실제 사용 경로·SHA256·범위를 남긴다. 현행 0922의 4장 감사표를 3장 검토 결과로 재사용하지 않는다.
5. **본문에서 원리를 가르친다.** 공식 답·원문 문항 번호·보기 글자를 학생 본문에 복사하지 않는다. ID는 이 입력과 감사표의 추적용이다. q11의 분류 모호성과 q01의 원사진/도식 차이를 보존한다. 카드에 있다는 이유로 본문 검토를 생략하지 않고 lite에서도 의미 검토를 수행한다. 단어·링크 검사 통과는 학습 효과 검증이 아니다.
6. **기존 팩 본문 적용은 별도 전체 재생성이다.** augment는 본문이나 기존 감사표를 바꾸지 않으므로 이번 입력의 적용 경로로 쓰지 않는다. 다음 전체 재생성에서 기존 백업·카드 번호·풀이기록 보존 및 조립·검사·본문 의미 검토를 수행한 뒤에만 결과를 보고한다. 이번에는 새 실행 감사표·`.pack/` 완료 기록을 만들지 않는다.
