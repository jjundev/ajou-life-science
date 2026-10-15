# 5장 웹과제 피드백 스킬 구현 검토

최신 상태: 사용자가 지정한 잔여 1·2번을 후속 보완해 인용 Minor와 스킬 형식 오류를 해소했다. 아래 초기 검토는 당시 기록이며 마지막 「후속 보완」 절을 함께 읽는다.

2026-10-15. 기준 commit `b69a977`. 사용자의 Native 구현 요청에 따라 격리 worktree에서 직접 수정했다. 커밋·push·main 병합은 하지 않았다. 기존 UI·학습 산출물은 재생성하지 않았다.

## 변경 범위

| 요구 | 수정 위치 | 검토 |
|---|---|---|
| 등록 후 장별 피드백 | web-quiz-extract/SKILL.md, 웹과제/5장/note-feedback.md | 전체 q01~q17/source 연결, bank 게시와 피드백 완료 분리 |
| 공통 관찰·판별 기준 | bio-review-pack/references/webquiz-style.md, note-feedback.md | 5장 사실과 개인 가설 분리, 기존 8열 audit 유지 |
| 본문·생성 연습·코칭 | bio-review-pack의 SKILL/content-rules/problem-selection/review-prompt, bio-review-coach/SKILL.md | 병기와 회상 구별, 선택적 단위·단계 비교, 분석만 요청하면 퀴즈 미시작 |
| 예상 설계 | bio-webquiz-forecast/SKILL 및 blueprint/forecast-rules/card-brief/blind-brief | 15문항·기출5/신규10·정답 배합 유지, 한 요소 예외의 목적/이전 카드 기록 |
| 해설 | bio-problem-explain authoring/verification/provenance | recall/pitfall 연결, 원문 보존·독립 검산 입력 경계 유지 |
| 커닝페이퍼 | bio-cheatsheet SKILL/content-rules/panic-patterns/section-brief/review-brief | 5장 관찰, ② 근거 있는 명칭 단서, refresh 범위 유지 |

위 스킬 경로의 접두어는 `.agents/skills/`다. 생산 코드·템플릿·JSON 스키마·검사 assertion은 수정하지 않았다. `.claude/skills`의 여섯 심볼릭 링크가 모두 원본으로 해석됨을 확인했다.

## 사례 R1~R5

실제 원문·노트 문장과 새 지침을 대조한 저작/검토 절차 점검이다. 에이전트의 판정이 학생의 숙달이나 생성물 학습 효과를 증명하지 않는다. 원래 기대와 실제 판단을 아래에 기록했다. 상세 scratch 입력은 이 worktree의 `.superpowers/sdd/2026-10-15-bio-ch5-feedback-skills/cases.md`에 남겼다.

### R1 제출 전 선택과 문항 불확실성

입력: 5장 bank/intake의 q03 A/B, q06 A/D, q09 C/A(캡처 선택/분석), q07 무선택·방향 생략. 공식 답은 모두 null이다. 기대: 선택 차이는 공식 오답으로 환산하지 않고 q07은 가정·무선택을 분리해 진단 보류한다. 실제: 새 note-feedback의 출제 관찰/개인 가설이 이를 분리하며 q07은 제시 서열을 5′→3′로 읽을 때만 AUG CCU GGA UAG→Pro라고 밝혔다. 통과. 원문 선택·답안은 그대로다.

### R2 기존 영어 병기와 다른 장

입력: 1006 정리노트 MD L484에 `정지 돌연변이(nonsense mutation) | UGC가 UGA로`, 예상 v1 p9의 `정지(무의미)`, v4 p9의 한국어 서열/개수 질문. 기대: 영어 병기 부재로 진단하지 않고 다른 이름에서의 회상은 별도로 확인한다. 실제: 공통 저작/검토·코치가 기존 설명 충분을 유지하며 이름→현상/현상→이름 연습을 연결한다. 통과.

대조 입력: 4장 피드백 q01의 ABO/복대립 설명은 5장 nonsense와 무관하다. 같은 원칙으로 집단의 대립유전자 수/개인의 대립유전자 수를 구별할 수 있고 nonsense를 억지로 추가하지 않는다. 8장 피드백 파일은 없음을 실제 확인했으며 그 장의 용어·비율을 추정하지 않는다. 이 사례는 새 8장 노트를 작성한 검사가 아니다.

### R3 한 요소 전환과 복사 금지

scratch 신규 p6의 이전 발문 `암호화 부위에 정지 돌연변이가 생겼다. 번역 결과의 특징을 고르시오.`를 `정지`→`넌센스`만 바꾼다. 같은 조건·보기(A 조기 종결/B 아미노산 유지/C 코돈 구분 이동/D 전사 개시 차단/E 프라이머 생성)를 유지한다. 기대: q09·강의노트 PDF6을 근거로 이전 scratch 카드·변경 요소·이름→현상 목적을 기록하면 좁은 예외 허용. 실제: blueprint 목록과 카드 브리프가 이를 허용한다. 제목은 ‘변이의 결과’로, 대응은 풀이에서만 공개한다. 이것은 v5 발행이나 실제 웹과제 복제가 아니다.

목적 없이 이전 발문을 그대로 두고 보기 순서만 바꾸는 후보는 거부한다. 목적 기록이 있어도 동일 발문은 거부한다. 기존 `test_stem_dup_across_versions`·`test_webquiz_copy`가 그대로 통과한다. 자동 검사기는 교육적 목적을 판정하지 않으므로 한 요소 예외의 의미 검토는 저작자/리뷰어의 책임이다. 기대 행동과 일치.

### R4 부재·근거 부족·lite·augment

기대와 실제: 피드백 파일 부재→미작성; 검증할 근거 쪽/문장이 없는 주장→판독·근거 불확실 보류; 충분한 기존 설명→실제 문장으로 충족을 기록하고 중복 방지. full/lite 모두 실제 본문 문장으로 검토하고 ‘예정’을 완료로 세지 않는다. augment는 본문을 바꾸지 않으므로 새 본문 반영으로 보고하지 않는다. 기존 `test_full_records_preserve_feedback_audit_bytes`와 augment 보존 검사가 통과하고, 4장 provisional 상태도 유지됐다. 새 노트 반영을 실행한 것은 아니다.

### R5 원문·해설·동의어·회상

입력: q09 원문의 `넌센스 돌연변이(nonsense mutation)`와 강의노트 PDF6의 `정지 돌연변이(Nonsense mutation)`. 기대: 원문에 번역을 끼워 넣지 않고 해설 recall에서 근거 있는 대응, pitfall에서 종결 코돈으로 바뀜/번역틀 이동의 차이를 설명한다. 실제 지침이 이 경계를 갖췄고 보호 해시가 일치한다. 확인한 자료에 없는 가상 동의어 후보는 제외한다. `무의미`를 쓸 때는 실제 v1 p9의 출처로 연결한다. 해설 공개 후 성공은 독립 회상으로 세지 않는다. 기존 독립 검산 정답 비공개·네 검토·최대 2회 수리·발행 보류 계약 유지. 통과.

## 실행 검증

테스트 Python: `/tmp/bio-forecast-test-env/bin/python`. 모든 pytest는 `_util` 모듈 충돌을 피하도록 스킬마다 별도 프로세스에서 실행했다. 시작 baseline도 review-pack 196, forecast 45, explanation 177, cheatsheet 49로 통과했다.

| 실행 명령 (저장소 루트) | 종료 코드 | 실제 결과 |
|---|---:|---|
| `BIO_TEST_PY -m pytest .agents/skills/bio-review-pack/tests -q` | 0 | 196 passed, 230 subtests passed in 2.49s |
| `BIO_TEST_PY -m pytest .agents/skills/bio-webquiz-forecast/tests -q` | 0 | 45 passed in 0.29s |
| `BIO_TEST_PY -m pytest .agents/skills/bio-problem-explain/tests -q` | 0 | 177 passed in 24.66s |
| `BIO_TEST_PY -m pytest .agents/skills/bio-cheatsheet/tests -q` | 0 | 49 passed, 3 subtests passed in 29.05s |
| `기존 .venv-question-bank/bin/python -m scripts.question_bank validate 웹과제/5장/questions.json --complete` | 0 | Valid: 17 questions (complete) |
| `BIO_TEST_PY RUN/check_ch5_feedback.py` | 0 | PASS: 17개 피드백 ID/source 대조 |
| `git diff --check` | 0 | 출력 없음(위반 없음) |

전체 자동 검사: **467 passed**, 별도 subtest 233개. 첫 피드백 수용 검사는 `5장 note-feedback 누락`으로 실패한 뒤 작성 후 17 ID/source 대조로 통과했다. 지침의 문구를 복제하는 새 테스트는 추가하지 않았다. task별 관련 검사도 실행했다(review-pack 46/forecast27/explanation85/cheatsheet9).

출처 provenance는 기존 `port_provenance.py --source /Users/hyunjun_macbook_pro/Documents/Univ/자구알`로 갱신했다. 변경은 authoring.md·verification.md의 destination_sha256 두 값뿐이며 pinned source commit·source_sha256은 그대로다.

추가 `skill-creator/quick_validate.py`: 시스템 Python으로 4스킬 통과. bio-review-pack·bio-webquiz-forecast는 `Description cannot contain angle brackets (< or >)` 실패이며 HEAD의 기존 SKILL.md를 임시 폴더에서 검증해 같은 실패를 재현했다. 이번 변경은 description을 수정하지 않는다. 이 두 기존 실패는 전체 검사 통과 숫자와 별개다. 테스트용 Python의 PyYAML 부재는 시스템 Python 사용으로, jsonschema 부재는 기존 question-bank venv 사용으로 해결했으며 프로젝트 의존성을 바꾸지 않았다.

UI 산출물을 수정하지 않았으므로 새 브라우저 확인·노트/예상문제/해설/시트 발행은 수행하지 않았다. 이미 검증된 원본 quiz의 브라우저 기록을 이번 스킬 검증으로 재사용하지 않는다.

## 보존·완료 경계

- 시작 시 웹과제·복습노트·웹과제예상 아래 **3,524파일**의 path/SHA256을 저장했고 모두 동일했다. bank/raw/SVG·1006/1008 등 기존 노트·예상 v1~v4·풀이기록·기존 감사표를 포함한다. 새 note-feedback은 초기 보호 목록 밖의 계획된 파일이다.
- `.claude/skills` 링크 수정 없음, Markdown 신규 링크 누락 없음, git diff --check 통과. 새 실행 산출물은 장별 note-feedback과 이 검토 문서이며 계획/명세는 기존 채팅에서 준비된 파일을 격리 경로에 복사했다.
- stale.py 실제 결과: 2·3·4장 `basis 없음`, 5장 `새 웹과제 미반영: 5장 / panic-patterns 갱신 전`. 기존 시트의 갱신 필요 알림이다. ② 본문 변경이 필요하면 refresh가 아닌 전체 재생성 대상으로 보고한다. 이번 요청에서는 재생성하지 않았다.
- 개인 학습 가설은 모두 미확인이다. q07 진단, 공식 채점·최종 제출 답·확신도, 장기 숙달·학습 효과는 확인하지 않았다. 스킬 지침·피드백 작성과 기존 노트 본문 반영을 구별한다.

## 실행 판단 기록

- 승인된 계획/Native 실행에 따라 격리 worktree와 마지막 별도 리뷰어를 사용한다. 커밋 요청이 없어 변경은 미커밋으로 유지한다(비용: main에 반영하려면 후속 통합 필요).
- 기본 체크아웃의 미추적 bio-webquiz-feedback 스킬은 동시 작업으로 보고 그대로 둔다(비용: 미공개 스킬의 추가 변경은 이번 구현에 통합하지 않음).
- 테스트 Python에 없는 검증 의존성은 기존 런타임으로 실행했다(비용: bank 재검증에는 기본 체크아웃의 venv 필요).
- 미커밋 변경에는 commit-range review-package를 적용할 수 없어 변경 diff·새 파일 전문·SHA256으로 리뷰 패키지를 만든다(비용: 검토 대상은 commit ID 대신 스냅샷 해시에 연결됨).
- 조건부 커밋은 생략하고 실행 증거는 미커밋 작업과 함께 보존한다(비용: 통합 때까지 ignored scratch 폴더 유지).

## 독립 전체 검토

작성에 참여하지 않은 별도 리뷰어가 계획·명세·전체 변경과 실제 원천을 대조했다. Critical 0, Important 0, Minor 1. 리뷰어가 별도로 실행한 관련 테스트 73개, 피드백 ID/source 검사, 원천 11개 해시, 보호 파일 3,524개 및 검토 스냅샷 25개의 일치를 확인했다. 전체 467개 검사는 저작자 실행 로그를 검토했다.

Minor(보류): q12는 frameshift, q15는 아세틸화의 직접 인용을 주변 인용보다 우선하면 추적이 쉬워진다. q03 DNA 메틸화도 직접 인용을 보강할 여지가 있다. 각 실제 강의노트 쪽과 보존 bank requirements에 해당 근거가 있고 피드백 판별 기준 자체는 맞으므로 기능 차단이 없는 인용 정리로 분류를 유지한다. Native 실행 규칙에 따라 이 Minor는 후속 정리 대상으로 남기고 범위를 더 늘리지 않았다.

리뷰어가 판단을 유보한 항목에 대한 실행 판단:
- 공식 정답·최종 제출 답·확신도·실제 학습 여부·숙달 효과: 자료가 없으므로 확인하지 않은 상태 유지. 비용: 개인 진단/효과 검증은 별도 독립 응답이 필요하다.
- 새 학습 산출물의 전체 생성·브라우저 품질: 이번 범위가 스킬 유지보수이므로 미수행 유지. 비용: 다음 실제 생성 때 기존 전체 발행 검증을 수행해야 한다.
- 기존 bank 17문항 전체의 재등록 수준 원본 감사: 바이트를 바꾸지 않고 complete 검증·보호 해시·핵심 원본/근거 대조를 수행했으므로 전체 재등록 감사는 반복하지 않는다. 비용: 기존 원문 판독의 모든 잠재 오류를 새로 배제한 것은 아니다.

판정: 승인된 설계에 부합하며 차단할 결함 없음. Minor 1건을 공개하고 미커밋 worktree 상태로 전달한다. main에 자동 병합하지 않는다. 스킬 소스·피드백은 리뷰 스냅샷 이후 변경하지 않았으며 이 절은 실제 리뷰 결과만 덧붙인 것이다.

최종 원천 대조 보완: 이미지형 교재 PDF 9·11·23쪽을 렌더링해 직접 확인했다. 프라이머 대체·교정, 코돈표·퇴화성, 선택적 이어맞추기 인용이 원문과 일치했다. 렌더링은 RUN/textbook-p9.png·p11.png·p23.png에 보존한다.


## 후속 보완 — 사용자 지정 1·2번 (2026-10-15)

사용자는 앞서 남긴 1번 근거 인용과 2번 기존 스킬 형식 오류를 정리하라고 명시했다. 이 후속 범위에서는 아래 세 파일의 사실·표현을 보완했다. main 통합이나 기존 학습 자료 재생성은 이번 선택 항목이 아니다.

- `웹과제/5장/note-feedback.md`: q03은 강의노트 PDF 8쪽의 DNA 메틸화, q12는 PDF 6쪽의 번역틀 이동, q15는 PDF 7쪽의 히스톤 아세틸화 문장을 직접 대조하고 각 근거 목록 맨 앞에 인용했다. 분석 답·원본 bank는 바꾸지 않았다.
- `bio-review-pack/SKILL.md`와 `bio-webquiz-forecast/SKILL.md`: description의 꺾쇠 경로 표기를 ‘날짜별 폴더’·‘장별 폴더’로 바꿨다. 본문의 실제 경로·호출법은 그대로다.
- 새 scratch 수용 검사 `RUN/check_followup.py`에서 기존 bank의 핵심 evidence와 q03/q12/q15 인용의 연결 및 두 스킬 메타데이터를 확인했다. 보완 전에는 5항목 모두 실패했고, 보완 뒤에는 모두 통과했다. 이 검사는 새 생성 규칙의 문구를 복제하는 생산 테스트가 아니라 source와 피드백 데이터의 대응 검사다.
- 여섯 스킬의 `skill-creator/quick_validate.py`가 전부 종료 코드 0으로 통과했다. 따라서 앞서 기록한 기존 형식 검사 실패 2건은 현재 해소됐다.
- 전체 자동 검사를 스킬별 별도 프로세스로 재실행했다: review-pack 196, forecast 45, explanation 177, cheatsheet 49, 합계 **467 passed**(subtest 233개 별도). bank complete, 17 ID/source 수용 검사, 보호 파일 **3,524개 SHA256 일치**, `git diff --check`도 통과했다.

기존 별도 전체 리뷰의 Minor 1건은 위 직접 인용 보완으로 해소됐다. 이번 소규모 보완은 작성자가 원문과 검사로 확인했으며 새 독립 리뷰를 수행했다고 주장하지 않는다. 미확인 학습 가설·공식 채점·학생 숙달과 기존 산출물 재생성 여부는 종전 경계를 유지한다. 사용자 요청에 따라 현재 검증된 변경을 작업 브랜치에 커밋한다.
