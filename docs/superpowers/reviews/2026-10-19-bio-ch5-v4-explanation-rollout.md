# 5장 v4 전체 해설 개선 — 개선본 작성 / 발행 보류

15문항 해설을 판단 기준 중심으로 작성하고 전체75선지를 감사했다. **P1 원문이 단일 정답을 허용하지 않아 기존 해설 교체는 보류했다.** 기존 HTML/MD/자료107파일과 보호526항목은 기준선과 같으며 원 문제·정답키·공통스킬·템플릿은 수정하지 않았다.

## 결과물

- [미발행 개선 HTML](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/stage/3bb145c93a7d4e548fc2c07e91d33425/문제해설_5장_웹과제예상_v4.html) / [미발행 MD](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/stage/3bb145c93a7d4e548fc2c07e91d33425/.pack/문제해설_5장_웹과제예상_v4.md)
- [15개 저작 조각](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/explanations) / [75선지 감사표](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/evidence/option-audit.md)
- [현재 검토 JSON](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/review.json) / [발행 게이트의 실제 거부 사유](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/final-gate-errors.txt)
- [새 독립 풀이](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/independent-result.md) / [보완 후 독립 반복 풀이](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/independent-repeat.md)
- [최종 검토와 수정 결정](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/final-review.md) / [원자료 화면 대조](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/evidence/source-visual.md) / [보충 근거와 접근 한계](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/forecast-5장-웹과제예상_v4/evidence/supplemental-sources.md)
- [브라우저 결과](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/browser-result.json) / [화면 증거](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/screenshots) / [회귀 테스트 기록](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/test-suite.log)
- [기존 발행본의 교체 전 스냅샷](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/pre-publish) / [보존 검사](/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/preservation-check.txt)

이 개선본은 새 stage에 있으며 발행 승인을 뜻하지 않는다. 문제 패널의 자동채점은 보존된 원 정답키를 따르므로 P1의 E 표시도 학술적 단일 정답 승인으로 해석하면 안 된다. RUN은 git에서 제외되는 실행 자료이고 이 보고서에는 위치를 기록했다. 별도 커밋 요청 시 필요한 자료를 보존할 범위를 정해 명시 경로만 포함해야 한다.

상대 링크를 실제 최종 경로와 같은 구조에서 확인하려면 아래 로컬 미리보기 도우미를 사용한다. 시험용 서버는 검토 후 모두 종료했다. HTML을 파일로 바로 열면 정리노트 상대 링크는 stage 위치 때문에 연결되지 않을 수 있다.

```sh
python3 "/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학/tmp/bio-ch5-v4-explanation-rollout-20261019-165607/preview.py" 8768
```

서버 실행 후 `http://127.0.0.1:8768/웹과제예상/5장/문제해설_5장_웹과제예상_v4.html#p1`에서 확인한다. 기존 장 파일을 이동하거나 stage HTML을 패치하지 않는다.

## 적용과 감사

필수 understand/recall/solve/verify를 사용하고 실제 정렬이 필요한 P5/P9에만 start를 남겼다. P1/P2/P7에는 문항 결함과 시험 대처를 공개했다. 각 문항의 삭제·통합 문장과 유지 이유는 감사표 마지막에 기록했다. 문장 수나 감소율을 목표로 삼지 않았다.

|문항|개선 내용|독립 답/상태|
|---|---|---|
|P1|교정·수선·잔여 오류 기준, 메타 보기의 결과적 판정과 모순 공개|단일 답 불가, disputed|
|P2|코돈/아미노산 수와 성질의 판별, DNA/U 표제 통일|B, RNA 코돈으로 해석|
|P3|시범의 실제 A–E 대응과 방향 검산 유지; 조각 바이트 동일|D|
|P4|직접 참여 역할과 부정형 선택을 구별|A|
|P5|10자리 × 5후보 대조, E 단순 역순이라는 기존 오진 제거|C, exact|
|P6|실제 SVG 좌우·말단·프라이머 범례로 각 주장 판정|D|
|P7|원문에 없는 전제 공개, 비율 동률로 구조 확정 금지|B, 공개 전제 조건부|
|P8|DNA서열/단백질과 결합 역할, 매개체 원연구 보충|A|
|P9|실제 염기번호 7–9, UAC→UAA, 종결코돈 제외|E, 정상5/변이2 exact|
|P10|표 +/+와 −/−, 결합 상대와 가능한 원인/확정 원인 구별|C|
|P11|말단 구조·기능·암호화 영역 구별, 불필요 꼬리 길이 삭제|A|
|P12|같은 다섯 비교 항목과 프라이머/신장 방향 구별|B|
|P13|전하→결합→접근성 인과, 메틸화 범위와 유일성 제한|C|
|P14|표지·장치·기질·직접 산물·회수 구별, 부정형 검산 표현 교정|E|
|P15|RNA 표적/조절 단계 및 상보성별 기본 모형, 배타적 단정 금지|D, 보충 원연구로 범위 확인|

75행 중73 pass, P1 B/E 두 행 disputed다. P1의 A/C/D 생물학 진술은 근거와 맞지만, E를 틀리다고 읽으면 B ‘모두 맞다’도 틀리다. E가 참이라고 읽으면 오답이 없어져 어느 해석에서도 현재 구성은 엄밀한 단일 오답 문항이 아니다. 기출 합본 PDF p.2 Q15 인쇄⑤와 예상키 E가 같아도 이 논리 결함은 사라지지 않는다. 이를 해설만으로 수정한 것처럼 처리하지 않았다.

## 검증과 승인

- 조립·기계 검사 PASS,15조각 구조 PASS, 원본/문맥 재추출 동일성 PASS.
- 회귀 테스트 **208 passed**. 문맥 변경 무효화·재조립 승인 초기화·disputed 발행 차단·쓰기 실패 rollback·재발행 원본 보존 테스트가 실제 실행됐다.
- 브라우저:1280×900/375×812의 light/dark4조합 ×15문항=60뷰, A–E 선택/초기화 **300회**. 원문·요약·이전/다음·노트 앵커·원 문제 링크, P6/P8 그림 확대, P7/P10 표,1024 기본 패널·좌/우/띄우기·이동/크기 clamp 통과. 콘솔·자원·KaTeX 오류와 문서 가로 넘침0, 저작 구역의 불필요 짧은 math-row0. 최초 검사와 보완 후 전부 다시 실행했다.
- 실제 화면:전체15의 네 조합 설명 화면, 그림 확대·표를 확인하고, 수정된 P8/P14/P15 검산12화면을 추가로 직접 확인했다. 현재 화면 증거는 최종 stage를 기준으로 한다.
- source_visual pass. content와 independent는 **P1 disputed**, 나머지14 items pass. browser pass. 실제 `validate_reviews`는0오류가 아니므로 발행 불가.
- 현재 input_hash=`b8fa7b1d8282468e1629169687e9816331b70ed668ec42a39c1a9c87eb3c8b00`. artifact hash 110개 및 읽은 참조파일 SHA-256을 현재 값과 대조했다. stage 조립 이후 HTML/MD/manifest/evidence를 직접 수정하지 않았다.

최초 최종 검토의 Important3건은 한 번의 수정 패스에서 처리했다. P14의 ‘E 제외’ 표현을 정답 선택으로 바로잡고, P8 매개체의 종류와 P15 상보성별 결과에 직접 원연구 근거를 추가했다. 관련 검사 RED→GREEN 후 새 build/check·네 검토·208테스트·300선택 검사를 반복했다. 수정 횟수는 **attempt1/2**다. P1은 원문 수정 금지 범위 때문에 남은 횟수를 소비해 같은 판정을 반복하지 않았다.

## 보존·발행 상태

`publish`는 실행하지 않았다. 따라서 canonical HTML/MD/그림/자료107파일의 집합·바이트와 사전 스냅샷이 동일하다. 원 문제·pack.json·blueprint.md·다른 버전·기존 시범 보존 폴더와 수업자료를 포함한 보호526항목도 일치한다. 원래 main 작업 폴더의 장 파일 554개도 동일하다. publisher 백업/복구는 실제 발행이 없어 실행되지 않았고, RUN/pre-publish는 사전 안전 스냅샷이다. 쓰기 실패·복구는 기존 fixture 회귀 테스트에서 확인했다.

브랜치는 `codex/bio-ch5-explanation-pilot`, HEAD는 `8127868`을 유지했다. 이번 실행의 자동 커밋·병합·푸시는 없다. plan workspace와 RUN은 미커밋 작업 및 보류 근거가 남아 있어 삭제하지 않았다.

## 범위 판단과 남은 작업

- 기존 분리 작업 폴더와 직접 저작 방식을 유지했다. 비용/한계:main에는 자동 반영되지 않는다.
- P1 단일 답 충돌은 원문 수정 범위 밖이라 공개·보류했다. 비용:전체 해설의 기존 위치 교체도 보류된다. 다음 작업은 B 메타 보기와 E 오류 빈도/시점을 고쳐 다시 유일 정답을 검증하는 것이다. 수정 시 source/context가 바뀌므로 새 RUN으로 추출하고 전체 검토를 다시 해야 한다.
- 외부 개념 링크는 기존 renderer 계약이 거부하므로 본문에는 짧은 출처명만 남기고 URL/접근 범위는 근거 문서에 보관했다. 비용:보충 문헌을 본문에서 바로 클릭할 수 없다. 수업 밖 보충임은 본문에도 표시했다.
- P2 DNA/U와 P7 누락 전제는 원문을 고치지 않고 공개했다. 비용:원 문항의 표현 결함은 남아 있다.
- P10은 관찰된 표의 가능한 원인을 설명하는 범위로 유지하고 추가 포도당 조건을 삽입하지 않았다. 비용:임의 배양 조건의 발현량 예측으로 확대할 수 없다.
- P8 원 SVG 일부 글자 겹침은 그림 보존 범위로 유지했다. 비용:확대해도 일부 원본 표지의 근접 배치는 남는다.
- 학생 수행자료가 없어 학습 효과·숙달 향상은 판단하지 않았다. 비용:실제 학습 효과를 측정한 결과는 없다.
- 경미한 유보1건:P9의 표준 동의어 ‘무의미’는 인용 수업자료에 직접 병기돼 있지 않다. 의미는 nonsense와 같지만 추후 ‘정지/넌센스’로 명칭을 맞출 수 있다. 이번 Important 전용 수정 패스에서는 변경하지 않았다.
