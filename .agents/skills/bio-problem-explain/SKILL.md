---
name: bio-problem-explain
description: 생명과학 복습노트의 기존 복습문제 또는 명시 경로의 웹과제·시험 예상문제 HTML로 문제 단서, 떠올릴 개념, 첫 줄, 보기별 판정과 이유, 완성 답과 검산을 펼친 문제설명 HTML·MD를 만든다. 문제설명, 문제해설, 입문 풀이 설명, 기존 팩 백필 또는 /bio-problem-explain [MMDD|MMDD-MMDD|all|HTML경로] [lite]에 사용한다. 복습팩 생성(bio-review-pack)과 새 문제 출제에는 사용하지 않는다.
---

# 생명과학 문제풀이 입문 설명

공부가 덜 되어 용어 인식이나 감으로 답을 고르는 학생도 선지를 판단할 수 있도록 문제의 요구 → 판단 기준 → 각 선지에 기준 적용 → 판정과 답 → 확인을 보여 준다. 기존 복습문제 HTML을 입력으로 사용하며 머신러닝기초 문제설명 템플릿과 로컬 KaTeX/Pretendard를 그대로 사용한다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다.

**인자**: `[MMDD | MMDD-MMDD | all | HTML경로] [lite]`
- `lite`: 저작 에이전트를 sonnet으로 한다. 네 검토(source_visual·content·independent·browser)와 기계 검사는 lite에서도 생략하지 않는다.

**서브에이전트가 없는 환경**: 병렬 저작 대신 같은 브리프로 문항 묶음을 차례로 직접 쓴다. 독립 검산은 새 세션에서 정답·풀이를 지운 문항과 정리노트·교과서·강의노트만 열어 수행한다. 모델 지정은 Claude에서는 opus/sonnet 그대로 따르고, GPT 등 다른 모델 환경에서는 opus→sol, sonnet→luna로 바꿔 읽는다(이 문서와 references의 모든 모델 지정에 적용).

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-problem-explain`)의 절대 경로. `.claude/skills/bio-problem-explain`은 이 폴더를 가리키는 심볼릭 링크다. 링크 경로가 아니라 원본 경로로 푼다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/bio-problem-explain/<range>/` (scratchpad가 없으면 `/tmp/bio-problem-explain/<range>/`). extract는 비어 있는 RUN만 받으므로 같은 range를 다시 돌릴 때는 `<range>-2/`처럼 새 폴더를 쓴다.
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 셸 명령의 `$SKILL`, `$RUN`, `$REPO`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 Bash 호출 맨 앞에 세미콜론으로 먼저 설정한다(`SKILL=…; RUN=…; REPO=…; python3 "$SKILL/scripts/…" …`). `RUN=… python3 …`처럼 같은 명령 앞에 붙이는 형식은 쓰지 않는다. 셸이 인자의 `"$RUN"`을 그 설정보다 먼저 펼쳐 빈 경로가 되기 때문이다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.
- 장 번호 `N`은 `강의노트/N장*.pdf`, `23, 24 소스/N강 합본.pdf`(파일명에 `+`가 섞여 있다), `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`(두 자리), `웹과제/N장/`에서 같은 수를 쓴다.

## 대상과 보존

- `1008`: 해당 날짜. `0922-0924`: 그 기간의 팩. 날짜 폴더는 `복습노트/<range>/`다.
- `all`: `복습노트/*/복습문제_*.html` 전체를 끝 날짜 내림차순(최신 → 0901)으로 처리한다. 실행기의 `--target all`과 같은 순서다. 백필은 **팩마다 RUN 하나**를 쓰고, 각 팩의 HTML 경로를 `--target`으로 넘겨 아래 1~7단계를 팩 단위로 차례로 수행한다. 한 팩이 보류되어도 다음 팩을 계속한다.
- 저장소 내부 HTML 경로: 해당 복습문제 파일을 명시한다. 예상문제는 `웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html` 명시 경로만 받는다. forecast profile로 p1–p15 전체를 설명하고 o1·o2는 제외한다. 장·버전·manifest·카드·정답키가 다르거나 누락/중복이면 거부한다. 예상문제 자동 백필은 하지 않으며 all과 최신 선택은 복습노트만 유지한다.
- 시험 예상 명시 입력: `시험예상/<범위>/시험예상문제_<범위>_v<K>.html`은 exam profile로 p1~p75(객관식55+단답20)를 설명한다. 단답형 정답·허용답·대소문자 규칙을 보존하고 설명한다. 문제의 네 검토 완료와 현재 source-manifest를 확인하며 MD 변경·부재 파일 신규 등장도 이전 RUN을 무효화한다. 부속 MD/그림/자료는 `.pack/v<K>/`에 둔다. 기존 all/최신에 시험 세트를 추가하지 않는다. 문제·해설 합계 수정 예산은 시험 RUN의 기록을 유지한다.
- 인자 없음: 파일명 날짜 기준 최신 복습문제 팩.

여러 slug 또는 같은 range의 팩이 겹치면(**여러 후보**) 후보를 보여 주고 경로를 명시하게 한다. 대상이 없으면(**대상 없음**) 중단한다. 최신 또는 명시한 팩이 0문항이면 **문항 없음**과 비어 있지 않은 후보를 안내하고 중단한다. 이전 날짜로 자동 이동하지 않는다. 새로운 문제를 출제하지 않는다.

원 HTML·MD·그림·정리노트·`.pack/`·기출 PDF·웹과제를 수정하지 않는다. `.problem` 전체의 지문·보기·수치와 기출 원문을 보존한다. 카드의 정답·풀이는 독립 검산을 대신하지 않는다. 질문 소문항과 보기 목록을 구별하며(보기 `ul/ol.choices`는 소문항이 아니다), 질문 경계가 모호하면 추출을 보류한다. 소문항을 임의로 합치지 않는다.

## 참조 자료

시험 예상(exam) 해설의 본문 제목과 왼쪽 목차는 동일한 `[출제 방식] PN. 문제개념`으로 표시한다. `pack.json`의 `concept_summary`를 재사용하고 `past/original → 기출 원문`, `past/variant → 기출 변형`, `web/original → 웹과제 원문`, `web/variant → 웹과제 변형`, `new/generated → 새 예상문제`로 표기한다. 예: `[웹과제 원문] P4. 생체분자의 구조와 중합체`. 표시 번호만 대문자로 하고 앵커 `#p4`는 유지한다. 개념 요약이 없거나 출제 방식이 불명확하면 정답에서 제목을 추측하지 말고 메타데이터를 확인한다. 시험 해설의 문제 패널 선택지는 실제 option ID를 사용해 `A.`, `B.` 등으로 통일한다. 기존 `(1)` 같은 선두 번호는 화면에서 대체하여 중복 표시하지 않는다. 원문 데이터·정답 모델과 보기 내용 자체는 보존한다. 시험 해설 문제 패널의 첫 문단 선두에 있는 원본 문항 번호(`1. ` 등)는 화면에서 제거한다. 제목 번호·소수·단위 수량·문장 중간 숫자는 유지한다. 화면 제목에는 내부 버전 번호를 표시하지 않는다. 이 규칙은 시험 해설에만 적용한다.

필요한 범위만 실제로 열어 읽고, 사용한 파일의 절대 경로와 SHA-256을 `review.json`의 references에 기록한다.

- 강의노트: `강의노트/N장*.pdf`
- 교과서: `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`
- 기출 합본: `23, 24 소스/N강 합본.pdf` (카드의 `data-source="기출 N강 k"`가 가리키는 쪽)
- 웹과제: `웹과제/N장/questions.json` (응시한 장만 있다)
- 정리노트: `복습노트/<range>/정리노트_<range>_<slug>.html`
- 팩 검토 기록: `복습노트/<range>/.pack/key-check.md`(정답 대조), `복습노트/<range>/.pack/question-audit.md`(문항 감사), `복습노트/<range>/.pack/variants.md`(생성 변형 설계). key-check.md·question-audit.md는 일부 팩에만 있다. 없으면 카드 정답과 variants.md의 `의도한 정답과 이유` 열로 대조하고 evidence에 "key-check 없음"을 적는다. 파일이 없다는 것만으로는 disputed가 아니다.
- forecast 근거: 해당 `웹과제예상/<N>장/.pack/v<K>/pack.json`과 `blueprint.md`(정답키·기출 모드·노트 앵커). key-check/variants가 없다는 것을 오류로 보지 않고 이 두 파일과 실제 관련 자료를 대조한다. 문맥 해시가 달라지면 새 RUN에서 재추출한다.
- STT(`STT/MMDD 생명.md`)는 필요한 경우 보조로만 쓴다. 수업 밖 보충은 표시한다.

## 저작과 독립 검산 분담

- 저작: 문항 10개당 에이전트 1명을 **한 메시지에서 병렬로** 띄운다. 모델은 opus, `lite`이면 sonnet이다. 각 에이전트에게 자기 문항 ID, `source.json` 경로, [저작 규칙](references/authoring.md), 위 참조 자료를 준다. 서브에이전트가 없으면 같은 묶음을 차례로 직접 쓴다.
- 독립 검산: 저작 에이전트와 **별도인** 에이전트 1명이 맡는다. 이 에이전트에게는 카드의 정답·풀이·설명 조각을 주지 않고 문항(지문·보기·그림)과 정리노트·교과서·강의노트만 준다. 다시 푼 답을 컨트롤러가 카드 정답과 `.pack/key-check.md`(없으면 `.pack/variants.md`의 `의도한 정답과 이유` 열)에 대조한다. forecast에서는 컨트롤러가 해당 버전 pack.json/blueprint.md로 대조한다. 독립 검산자에게 그 정답키·설계표·개요의 정답을 제공하지 않는다. 기준은 [검토 기록](references/verification.md)의 independent 항목이다.

## 실행

저장소 루트에서 Python 3.10 이상을 사용한다. 실행기는 표준 라이브러리만 필요하다. 설치만으로 실제 수업 산출물을 만들지 않는다.

1. 고유 RUN을 정하고 추출한다.

   ```sh
   SKILL=…; REPO=…; RUN=…; python3 "$SKILL/scripts/mpe_cli.py" extract --repo "$REPO" --target 1008 --run "$RUN"
   ```

2. 대상 디렉터리의 `source.json`을 읽는다. 문항 ID·전체 문제·소문항·보기·원문·그림·참고 풀이를 확인한다. 카드의 출처(기출 합본 쪽, 웹과제 questions.json 항목), 교과서·강의노트의 해당 장, 관련 정리노트를 필요한 범위에서 실제로 읽고 원 페이지와 대조한다. `.pack/key-check.md`와 `.pack/question-audit.md`에서 그 문항의 정답 대조·보류 기록을 확인한다(없는 팩이면 건너뛴다). `data-source="생성 변형 …"` 카드는 `.pack/variants.md`에서 같은 id 행(근거 토픽, 형태 열의 교재 쪽, 의도한 정답과 이유)을 읽는다. STT는 필요한 경우 보조로 사용한다. 수업 밖 보충은 표시한다. `source.json`을 수동 수정하면 재추출 검사가 거부한다.
   forecast는 복습노트 `.pack/`의 key-check·variants 대신 `웹과제예상/<N>장/.pack/v<K>/`의 pack.json/blueprint.md를 읽고 원문 그대로와 변형·새 예상문항을 구분한다. 기존 실제 기출로 표시하지 않는다.
3. [저작 규칙](references/authoring.md)을 읽고 `explanations/pN.html`을 작성한다(위 분담대로 병렬 저작). 필수 직계 구역은 `understand → recall → solve → verify`다. `start`는 recall 뒤, `pitfall`·`retry`는 verify 뒤에 별도의 도움이 있을 때만 넣으며 빈 구역·반복 문장은 생략한다. 문항 결함·인쇄 정답 오류의 공개와 대처는 아래 규칙을 유지한다. 모든 소문항의 solve/verify 표지, 펼친 답과 우측 요약이 필요하다. 객관식 recall에는 확인할 대상·관계·적용 조건을 판단 기준으로 제시하고, solve는 모든 선지의 실제 주장에 그 기준을 적용해 선택·제외 이유를 쓴다. 진술의 참·거짓과 답으로서의 적합성을 구별한다. 요약에는 핵심 기준과 결론만 짧게 남긴다. CLI는 설명을 자동 저작하지 않는다. 모든 profile의 문항마다 recall에 관련 정리노트의 실제 개념 앵커 링크를 최소 1개 넣는다. 대응 절이 없을 때만 [저작 규칙](references/authoring.md)의 `data-note-link-omitted` 선언과 `content.note_link_exceptions` 내용 검토 승인을 사용한다. 링크와 생략 사유 모두 없는 문항은 build/check/publish에서 거부한다. 링크 개수만 채우지 말고 개념 적합성을 문항별 검토한다.
4. 정답을 보지 않은 별도 에이전트의 재풀이, 교과서 쪽 대조, 교배표 재계산 등으로 답을 확인하고 `evidence/`에 근거를 보관한다. 원문 충돌과 문항 결함은 구분한다.
   - (A) 충돌: (C)에 해당하지 않으면서 카드 정답이 인쇄 답안지·기출·웹과제·key-check 판단 답 또는 독립 재풀이 답과 다르면 몰래 수정하거나 정상 답으로 승인하지 않고 disputed로 남기며, 그 팩은 발행을 보류한다.
   - (B) 결함 공개: 카드 정답이 인쇄 답·key-check·독립 재풀이와 모두 같고 문항 표현만 결함(다른 보기도 논쟁 여지, 방향·가닥 누락, 오타)이면 설명을 쓰되 understand에 `<strong>문항 결함:</strong>` 한 줄, solve에서 논쟁 보기를 정직하게 판정("엄밀히는 맞을 수도 있어요 — 이유"), pitfall에 시험 대처를 적는다. content 검토는 공개가 정확한지 확인한다. 이 경우는 disputed가 아니다.
   - (C) 인쇄 정답 오류: 카드 정답이 기출 인쇄 정답과만 다르고, 교과서·강의노트 근거와 독립 재풀이 답(있으면 key-check 판단 답)이 모두 카드 정답과 같으면 설명을 쓰고 발행한다. understand에 `<strong>인쇄 정답 오류:</strong>` 한 줄로 인쇄 정답과 카드 정답을 함께 밝히고, solve에서 인쇄 정답 보기가 왜 틀렸는지 근거 쪽과 함께 판정하며, pitfall에 시험에서 인쇄 정답을 만났을 때의 대처를 적는다. 이 경우는 disputed가 아니다.
5. 조립과 기계 검사를 실행한다. build는 새 stage를 만들고 검토 상태를 모두 `not_run`으로 초기화한다.

   ```sh
   SKILL=…; RUN=…; python3 "$SKILL/scripts/mpe_cli.py" build --run "$RUN"
   SKILL=…; RUN=…; python3 "$SKILL/scripts/mpe_cli.py" check --run "$RUN"
   ```

6. [검토 기록](references/verification.md)을 읽고 실제 source_visual/content/independent/browser 결과를 `review.json`에 기록한다. 사용한 참조 파일의 절대 path와 SHA-256을 references에 기록한다. 구조 통과를 정답 검증으로 기록하지 않는다. 로컬 브라우저에서 1280×900/375×812, light/dark의 모든 문항·목차·이전/다음·요약·수식·그림·표를 확인한다. 콘솔·KaTeX 오류·누락 자원·외부 요청·문서 가로 넘침은 0이어야 한다. stage의 원 문제/개념 링크는 최종 발행 디렉터리 기준이므로 실제 원 파일과 anchor도 대조한다. 문제는 넓은 화면에서 목차 오른쪽·본문 왼쪽의 문제 패널 [문제 | 원문] 탭(원문 탭은 원문이 있는 문항만)으로 기본 표시되고, 패널 머리 버튼이나 끌어서 붙이기·떼기로 오른쪽에 붙이거나 띄운 창(이동·크기 조절)으로 바꿀 수 있으며 방식·위치는 `od-panels:explain:v2:prob`에 기억된다. 요약은 오른쪽 요약 패널, 좁은 화면에서 해설 위 접힘 버튼으로 표시된다. 템플릿 결함은 근거를 보고하며 임의로 템플릿을 수정하지 않는다. 네 검토는 `lite`에서도 생략하지 않는다.
7. 실제 검토 네 가지(source_visual·content·independent·browser)가 모두 pass이고 현재 해시가 일치하면 사용자 호출 범위에서 추가 확인 없이 발행한다. 미검토·변경·실패·disputed는 해당 팩의 발행을 막는다.

   ```sh
   SKILL=…; RUN=…; python3 "$SKILL/scripts/mpe_cli.py" publish --run "$RUN"
   ```

forecast 자동 연결에서 검토가 실패하면 [예상 스킬의 수정·재검토 계약](../bio-webquiz-forecast/references/explanation-handoff.md)을 따른다. 해설기는 원본 문제를 고치지 않고 컨트롤러가 이번 호출의 새 버전만 수정한다. build 후 네 검토는 다시 수행하며 미해결이면 발행을 보류한다.

설명 소유 파일만 백업·교체하며 실패하면 복구한다. 다중 파일 교체는 OS 원자적 transaction이 아니다. 팩별 성공·보류 이유, HTML·MD와 백업 경로를 보고한다. `all`이나 기간 백필은 팩마다 한 행인 결과 표(range · slug · 문항 수 · 발행/보류 · 보류 이유 · HTML 경로)로 보고한다. 커밋·푸시는 별도 사용자 요청이 있을 때만 수행한다.

### 레이아웃만 바뀐 기존 발행분 재발행

템플릿·레이아웃만 바뀌고 원 복습문제와 설명 조각이 그대로이면 조각을 다시 쓰지 않는다. 팩마다 새 RUN으로 `rerender`를 실행하면 발행 자료 폴더의 `fragments/`·`evidence/`를 복사해 build하고, 발행된 `validation.json`의 input_hash가 현재 입력과 같을 때 references·content·independent 검토를 이식한다. 원 복습문제나 참조 자료가 `<style>`·실행 `<script>`(답 모델 같은 JSON 데이터 스크립트는 제외)나 상대 src/href 앞의 `.assets/`만 다르거나, 날짜 폴더 루트의 참조 파일이 `.assets/`로 옮겨지기만 했으면(MD는 이전 때 고친 링크 포함) 같은 입력으로 보고 참조 경로·hash를 새로 적는다. 그 밖의 변경·누락은 "참조 자료 변경"·"참조 자료 없음"으로 알리며, 그 참조로 한 검토를 다시 한다. 이어서 `check` → source_visual·browser 실제 검토 → `publish` 순서로 진행한다. "입력 변경: 네 검토 모두 다시 필요"가 나오면 1~7단계 전체를 따른다. `all`이면 최신 → 0901 순으로 팩마다 반복하고 위 결과 표로 보고한다.

   ```sh
   SKILL=…; RUN=…; python3 "$SKILL/scripts/mpe_cli.py" rerender --repo "$PWD" --target "$PWD/복습노트/1013/복습문제_1013_….html" --run "$RUN"
   ```

## 산출 위치

입력과 같은 날짜 폴더 `복습노트/<range>/`에는 `문제설명_<range>_<slug>.html`만 두고, 나머지는 숨김 폴더 `복습노트/<range>/.assets/` 안에 `.assets/문제설명_<range>_<slug>.md`, `.assets/figures_문제설명_<range>_<slug>/`, `.assets/자료_문제설명_<range>_<slug>/`로 저장한다. MD 안의 링크는 `.assets/` 기준이라 원 문제 보기는 `../복습문제_….html`이다. 자료 폴더에는 생성 기록·검토·설명 조각·검산·로컬 자원이 들어간다. 정리노트·복습문제에 링크를 자동 삽입하지 않는다. 읽음 상태 키는 `bio-problem-explain-review-<range>-<slug>`다.

forecast 출력은 같은 `웹과제예상/<N>장/` 폴더의 `문제해설_<N>장_웹과제예상_v<K>.html`과, 숨김 폴더의 `.pack/문제해설_<N>장_웹과제예상_v<K>.md`, `.pack/figures_문제해설_<N>장_웹과제예상_v<K>/`, `.pack/자료_문제해설_<N>장_웹과제예상_v<K>/`다. 장 폴더 루트에는 HTML과 `.pack/`만 둔다. 제목은 `생명과학 <N>장 웹과제 예상 v<K> 문제해설`, 읽음 상태 키는 `bio-problem-explain-forecast-<N>장-웹과제예상_v<K>`다. 기존 예상문제에 링크를 자동 삽입하지 않는다.

원본 고정 커밋과 바이트 해시는 [이식 기록](assets/port-provenance.json)에 있다. 실행 중 원본 저장소나 머신러닝기초 checkout을 참조하지 않는다.
