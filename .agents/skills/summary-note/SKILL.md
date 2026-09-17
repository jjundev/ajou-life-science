---
name: summary-note
description: 회차 강의 STT에서 정리노트/MMDD.md + MMDD.html + tests/test_note_MMDD.py 를 만든다. "/summary-note MMDD", "/정리노트 MMDD", "MMDD 강의 듣고 왔어", "MMDD 정리노트 만들어줘" 에 쓴다. 규칙은 정리노트/CLAUDE.md 에 있고 이 스킬은 절차만 담는다. 4단계 게이트에서 반드시 멈춘다.
---

# summary-note — 회차 노트 작성 절차

내용 규칙은 저장소 루트의 `정리노트/CLAUDE.md`가 유일한 원천이다. 모든 shell/data 경로는 저장소 루트에서 실행하고, 먼저 그 규칙 전체를 읽는다.

4단계의 기존 범위 게이트 전에는 읽기·분류만 하고 파일을 만들지 않는다. 이미 같은 생성 범위에 대해 사용자가 승인한 뒤의 재검토·검증·신선도 갱신은 다시 허가받지 않는다.

## 0. 입력과 장 범위 확인

STT와 직전 노트를 찾고 STT를 전부 읽는다. 강의계획서보다 실제 STT 진도를 우선하며, 강의노트 PDF에서 실제 장·절을 대조한다. STT가 없으면 결석인지 파일 누락인지 확인한 뒤 결석 모드를 적용한다.

장별 bank는 한 날짜 노트가 소유하는 파일이 아니라 여러 회차가 함께 참조하는
근거다. 각 요청 MMDD의 날짜와 실제 범위는 사용자 요청과 해당 STT로만
확정하고, bank의 `assessment date`나 파일명에서 새 회차 날짜를 추론하지
않는다. 같은 bank를 쓰더라도 요청된 각 MMDD마다 전체 bank ID를 그 회차
기준으로 included/review/deferred 분류한다.

해당 장의 웹 자료를 다음처럼 구분한다.

웹 bank 명령은 `jsonschema`가 설치된 전용 interpreter를 쓴다. 저장소에
전용 venv가 없을 때만 먼저 준비한다.

```bash
if [[ ! -x .venv-question-bank/bin/python ]]; then
  python3 -m venv --system-site-packages .venv-question-bank
  .venv-question-bank/bin/python -m pip install 'jsonschema>=4.18,<5'
fi
```

1. 같은 장에 등록된 `웹과제/<장>/questions.json`이 있으면 저장소 루트에서 아래를 실행한다.
   ```bash
   .venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/<장>/questions.json' --complete
   ```
   실패한 review, stale hash, 참조 필드나 source를 구체적으로 보고하고 검토를 마친 뒤 진행한다. 미검토 자료를 누락처럼 무시하지 않는다.
2. 해당 장 raw 캡처는 있지만 `questions.json`이 없으면 **raw-only 미등록 근거**다. 파일과 범위를 확인하고 등록·검토가 남았다고 보고한다. 이를 자료 부재라고 부르거나 모든 알려진 웹 문항을 다뤘다고 주장하지 않는다.
3. 같은 장의 등록 bank도 raw-only 자료도 없을 때에만 웹 자료 없음으로 기록하고 기존 `23, 24 소스/N강 합본.pdf` 절차로 진행한다.

다른 장 bank는 원문 문항 집합에 합치지 않는다. 분류 경계·조건 변경·그림 판독 같은 출제 형태만 참고하고, 내용 근거는 현재 장 STT·강의노트·교재에서 찾는다.

## 1. 범위와 혼동 묶음

STT 시작의 복습, 마지막 발언, 끊긴 위치, 다음 회차 예고를 확인하여 범위표를 만든다. 교수님이 반복·되물음·주의한 항목과 문항의 오답 진단을 **핵심 혼동 묶음**으로 모은다. 고정 개수를 채우지 않는다.

각 묶음에는 필요하면 1–2개의 회상/생성 변형을 제안한다. 생성 변형은 실제 bank 원문과 분명히 구별하고 별도 영역에 둔다. bank 원문 집합이나 원문 문항 수를 늘리거나 줄이지 않는다.

## 2. 모든 문항과 보기 감사

기존 PDF는 페이지를 이미지로 렌더링하여 인쇄 답을 읽고 독립 판단과 대조한다. bank는 검증된 JSON의 원문·관찰·분석을 사용하며 화면의 선택 기록을 공식 답으로 바꾸지 않는다.

각 원문 문항마다 다음을 확인한다.

- 출처 ID와 원문 문항 ID, 실제 장·절, 상태(included/review/deferred)
- 판정 답의 종류: 공식 답, 분석 답, 미확정 중 무엇인지
- 모든 보기의 선택 적합성, 근거 requirement와 source, wording/conflict issue
- 그림 의존 여부와 exam 그림을 본문/문항 어디에서 먼저 가르칠지
- 해설에만 있던 필요 지식을 본문 또는 출처가 표시된 보충에서 먼저 가르칠 위치

bank v1은 `official_answer.option_ids` 배열을 보존한다. 현재 ELI5 adapter는 공식 답이 null 또는 정확히 하나일 때만 지원하며, 복수 공식 답은 잘라 쓰지 않고 거부한다. 현재 1장 17문항은 모두 공식 답이 null이다. 분석의 `also_accept`는 공식 답과 별개다.

## 3. 번호 유지

3단계는 별도 실행 단계로 두지 않는다. 2단계 감사 결과를 바로 기존 이름인
4단계 범위 게이트에 제시한다. 다른 문서가 인용하는 게이트 번호를 바꾸지
않기 위해 이 생략을 명시한다.

## 4. ⏸ 범위 게이트

기존 세 표를 제시하고 OK를 기다린다.

1. **범위와 경계**: 시작·끝·끊긴 방식·다음 회차 예고.
2. **문항 분류와 답 대조**: 문항마다 출처 ID, 판정 답의 종류, 전체 보기 감사 결과, 그림, 필요한 보충을 포함한다. 합계가 PDF 전체 및 각 bank 전체 ID 집합과 일치해야 한다.
3. **구조 제안**: §1…§N, 장 구분선, 보충의 실제 출처, exam 그림 위치, 회상/생성 변형 영역.

승인 뒤 작성할 MD의 웹 매핑표 헤더는 정확히 다음과 같다.

```markdown
| 출처 | 문항 ID | 질문 요약 | 절 | 상태 |
```

각 원본 bank ID를 deferred까지 정확히 한 번 적는다. HTML `QUIZ`에는 최종 included/review 문항만 들어간다.

## 5. 작성과 source graph

승인 뒤 `정리노트/MMDD.md`, `MMDD.html`, 생성 테스트를 만든다. 웹 bank가 있으면 `정리노트/meta/MMDD.web-scope.json`에서 전체 원본 ID를 included/review/deferred로 분류하고 실제 MD heading을 refs로 연결한다. 상세 형식과 경로 기준은 `웹과제/question-bank.schema.json`, `scripts.question_bank.scope`, study-note-eli5의 `references/coverage-contract.md`를 따른다.

현재 `_template.html`의 `QUESTION-DATA` marker 안에 새로 쓰는 `META`와
`QUIZ`는 PDF-only여도 JSON-compatible이어야 한다. 즉 key와 문자열을
쌍따옴표로 쓰고 JavaScript 전용 literal을 넣지 않는다. marker가 없는 기존
legacy HTML의 read compatibility는 유지한다. 이는 과거 artifact의 일괄
재작성을 허용하지 않는다. 기존 회차를 명시적으로 업데이트하면서 bank를
결합할 때는 current template과 strict JSON marker 계약으로 생성한다.

**bank-only 출력**에는 다음 CLI를 쓴다. 이 명령은 scope의 활성 bank
문항만 export하므로, 같은 회차에서 감사한 PDF 문항이 있다면 이 명령만
실행하여 legacy 문항을 조용히 잃어서는 안 된다.

```bash
.venv-question-bank/bin/python -m scripts.question_bank note \
  --scope 정리노트/meta/MMDD.web-scope.json \
  --meta /tmp/MMDD-meta.json \
  --output 정리노트/MMDD.html
.venv-question-bank/bin/python scripts/new_note_test.py MMDD \
  --web-scope 정리노트/meta/MMDD.web-scope.json
```

PDF+bank 혼합 회차는 [mixed-source recipe](references/mixed-source-note.md)를
따른다. 이 절차는 audited legacy payload를 명시적 임시 JSON으로 준비하고,
`export_note_items`의 bank 결과와 합쳐 `render_note`에 한 번 전달한다. 생성
테스트에는 `--quiz`와 `--web-scope`를 함께 주어 legacy 수/ID와 전체 bank
범위를 각각 검증한다.

웹 자료가 전혀 없는 기존 PDF-only 회차는 표준 Python으로 기존 경로를
유지한다. 현재 template marker까지 확인하는 임시 예시는
[PDF-only fallback sample](references/mixed-source-note.md#pdf-only-current-template-fallback-sample)을 따른다.

```bash
python3 scripts/new_note_test.py MMDD --quiz 7,8,11
```

`--meta` JSON은 적어도 네 자리 `date`와 비어 있지 않은 `title`을 가진다.
경로는 저장소 루트 기준이다. JSON과 검증된 SVG는 HTML에 삽입하며 브라우저
외부 요청을 만들지 않는다. 기존 unmarked HTML-only 회차는 읽기만 할 때
현상 유지하며, 명시적 bank 결합 업데이트에는 위 current template 계약을
적용한다.

MD 본문은 STT 진도만 가르치고, 필요한 추가 지식은 실제 근거에 따라 강의노트·교재·외부 참고로 표시한다. 30초 요약에서도 조건·분류 경계를 보존하고, 기능 경로 참여를 계의 구성원으로 바꾸지 않으며, 쉬운 설명에 시험 판별 용어를 남긴다.

## 6. 정합성과 신선도 재검토

과거 노트의 문항 매핑·예고 상태를 기존 범위 안에서 정리한다. 그 파일이 bank requirement의 evidence이면 full-file hash가 달라질 수 있으므로 **정리 뒤** bank complete 검증을 다시 실행한다. 영향받은 evidence와 diff를 확인한 뒤에만 review 기록을 갱신한다. 검증된 hash만 기계적으로 다시 계산하지 않는다. 최종 source를 기준으로 HTML, web scope와 ELI5 scope binding을 다시 만든다.

## 7. ELI5 연결과 검증

ELI5 source module의 `META.web_scope`는 `guide.py`가 있는 디렉터리 기준이며 builder가 절대 경로로 해석한다. `WEB_BINDINGS`는 override 뒤 최종 활성 web ID와 정확히 같고, 각 source requirement를 저자가 작성한 `FACTS`에 연결한다. Builder가 bank 문항을 자동으로 가져오므로 `QUESTIONS`에 손으로 중복하지 않는다. 세부 계약은 study-note-eli5 SKILL과 coverage contract를 읽는다.

전체 테스트, 해당 bank `validate --complete`, 생성 테스트와 브라우저 검증을 실행한다. 자동 검증, 실제 브라우저, 원본/의미 검토, 아직 확인하지 않은 항목을 서로 구분하여 보고한다.

## 8. 장 종료 보고

장이 끝나면 다음을 한 번 더 검토하고 보고한다.

1. 회차별 해당 절과 source 연결
2. 필수 그림과 시험 판별 용어
3. 남은 deferred 항목과 구체적 사유·선행조건
4. 시험 범위 확인 또는 불명 상태
5. 비교 문항과 생성 변형의 풀이 점검 결과

이 절차 자체는 새 장 요약 artifact를 자동 생성하지 않는다. 기존 승인 범위의 작업을 끝까지 검증한 뒤 명시된 파일만 stage한다. zip, `git add .`, 다른 장 bank 원문 혼합, 다음 회차 본문 당겨오기는 금지한다.

## 결석 모드

강의노트 해당 절과 교재로 재구성하고 STT 없음 경고를 헤더에 둔다. ⏪ 블록은 만들지 않으며 테스트 생성기에 `--no-recap`을 쓴다. 문항 범위 게이트와 웹 자료의 등록/raw-only/없음 구분은 그대로 적용한다.
