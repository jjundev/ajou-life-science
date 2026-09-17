# 웹과제 문제 원본과 정리노트 통합 설계

상태: 2026-09-17 대화의 grill-yourself 설계에서 구현 계획으로 전환. #8(그림 4개), #9(신규 노트부터 적용)는 사용자의 writing-plans 요청에 따라 추천값으로 기본 확정했다. 실행 승인은 아직 아니다.

## 목적과 범위

1장 raw 스크린샷 19장에서 17문항·82보기를 원문 그대로 JSON에 기록하고, Q9·Q14를 문제용 및 해설용 SVG 총 4개로 재작성한다. 정리노트와 ELI5 생성 과정은 이 원본을 참조하되 기존 노트/ID/링크를 보존한다. 문항 저장, SVG, 노트 연결은 하나의 순차 파이프라인이다.

## Global Constraints

- 원본 스크린샷은 변경하지 않는다. Q1–Q17, 82보기, Q6의 a–d 조건문과 원문 순서를 보존한다.
- 문제용 SVG 2개와 해설용 SVG 2개를 웹과제/1장/image에 저장한다.
- 캡처 선택, 공식 답, 분석 답을 별도 저장한다. 현재 공식 답은 null이며 캡처는 pre_submission이다.
- 문제용 그림·대체 설명·파일명에 원문에 없던 정답 힌트를 넣지 않는다.
- JSON과 SVG는 편집 원본이며 HTML에는 생성 시 삽입한다. 브라우저 외부 요청·CDN은 사용하지 않는다.
- 기존 회차 MD/HTML/ELI5를 재생성하거나 본문 수정하지 않는다. 새로운 생성부터 적용한다.
- 기존 1강:18 형식의 ID와 q1-18 형식 링크, 기존 scope v1 검증은 유지한다.
- 회차 본문은 실제 STT 진도를 따른다. 보충에는 실제 출처를 표시한다.
- 모든 보기의 선택 적합성·근거를 감사한다. 자동 검사는 의미 정확성이나 학습자의 이해를 증명하지 않는다.
- 새 웹과제는 같은 장의 직접 근거, 다른 장의 웹과제는 출제 형태의 참고로만 사용한다.
- 사용자의 기존 변경·미추적 파일을 포함하여 일괄 stage하거나 덮어쓰지 않는다. 커밋은 실행 작업별 명시 경로만 사용한다.
- 구현 언어는 Python 3.10 이상과 표준 HTML/CSS/JavaScript/SVG다. JSON Schema 검증 의존성은 jsonschema>=4.18,<5 하나다.

## 산출물

`웹과제/question-bank.schema.json`, `웹과제/1장/questions.json`, `웹과제/1장/preview.html`, `웹과제/1장/image/q09.svg`, `q09.explained.svg`, `q14.svg`, `q14.explained.svg`.

자료 출처: `docs/2026-09-17-1장-웹과제-분석과-노트-개선안.md`. 이 분석은 전사 원본이 아니므로 각 문구와 그림은 raw를 다시 보고 입력한다. Q9의 두 화면은 12.11.48/12.11.51, Q14는 12.12.32/12.12.35다. Q6/Q12/Q15는 4보기, 나머지는 5보기다.

## 데이터 계약 v1

모든 객체는 아래에 정의한 키만 허용한다. 문자열은 비어 있지 않아야 한다(명시적 예외만 허용). 경로는 파일 시스템의 실제 Unicode 파일명을 보존하며 JSON 경로 구분자는 `/`다. NFC 정규화는 조회 비교에만 쓰고 원본 이름을 rename하지 않는다.

### 루트

- `schema_version`: 정수 1.
- `assessment`: `{id,title,chapter,date,expected_question_count,time_limit_seconds,max_points,evidence_source_ids}`. id는 `web-20260917-ch01`, chapter는 양의 정수, date는 YYYY-MM-DD, 문항 수는 17, 시간은 660, 배점은 17. 일반 스키마에서 시간/배점은 null 허용. 실제 값에는 화면 근거 ID를 붙인다.
- `sources`: `{id,path,sha256,width,height}` 배열. path는 bank 파일 디렉터리 기준 `raw/…png`, width/height는 양의 정수, 해시는 lowercase SHA256 64자리. 한 화면이 여러 문항에 연결될 수도 있으며 모든 source는 한 번 이상 참조되어야 한다.
- `assets`: `{id,exam,explained,source_ids,review}` 배열. exam/explained는 `{path,sha256,alt}`. path는 `image/` 안의 SVG, alt는 각 버전의 대체 설명. review는 아래 검토 객체.
- `questions`: 아래 문항 배열. id와 number는 서로 유일하고 1부터 expected_question_count까지 빠짐없이 존재한다.

### 문항

- `id`: `${assessment.id}:q${number padded to 2 digits}`; number는 양의 정수, `points`는 0 이상의 수.
- `source_ids`: 문구/보기/그림을 복원하는 source ID 배열.
- `original`: `{format,content,options}`; format은 현재 `single_choice`만 지원한다. 미지원 형식은 조용히 변환하지 않고 오류.
- `content`: 순서 있는 블록 배열. text `{type:"text",text}`, statements `{type:"statements",items:[{id,text}]}`, figure `{type:"figure",asset_id}` 중 하나. Q6의 a/b/c/d는 statements이며 선택지는 여전히 A–D 단일 선택이다.
- `options`: `{id,text}` 배열, id는 A–Z 중 한 문자이고 원래 표시 순서를 유지한다. 최소 2개. 같은 문구라도 ID는 다르므로 자동 중복 제거 금지.
- `observations`: `{phase,selected_option_id,selected_source_id,official_answer}`. phase는 pre_submission/post_submission/unknown. 선택은 null 또는 존재하는 보기 ID. official_answer는 null 또는 `{option_ids,source_ids}`. 공식 답의 증거 없이 selected 값을 복사하는 코드 금지.
- `analysis`: `{answer_option_id,answer_status,grading,also_accept,reason,concept_ids,skills,requirements,option_diagnostics,issues}`.
- answer_status는 reasoned/unresolved; unresolved이면 답은 null. grading은 single/ambiguous/unresolved; ambiguous는 설명 issue를 요구하지만 가능한 다른 정답이 입증되지 않았다면 also_accept는 빈 배열일 수 있다. single에서는 also_accept가 빈 배열이다.
- skills는 figure-identification / classification-boundary / condition-change / statement-evaluation / scenario-transfer / structure-to-function 중 배열.
- requirements는 `{id,statement,evidence}` 배열. id는 문항 안에서 유일. evidence는 `{path,locator,quote}` 배열; path는 저장소 루트 기준이며 locator는 MD 절/PDF 쪽/STT 시각, quote는 확인한 짧은 근거 문장이다. 요구 지식과 가이드의 fact ID는 서로 다른 이름공간이다.
- option_diagnostics는 보기 ID를 키로 하는 객체. 값 `{is_answer,explanation,requirement_ids}`. is_answer는 bool이며 intended/also_accept에 맞춘다. 정답으로 부적합하다는 것과 보기 문장 자체가 거짓이라는 것은 구분해서 explanation에 쓴다. unresolved는 is_answer=null 허용.
- issues는 `{kind,description,source_ids}` 배열; kind는 wording/source-conflict/unreadable/figure-incomplete. Q4/Q16 표현 문제를 보존한다.
- `review`: `{status,payload_sha256,notes}`; status는 pending/needs_review/verified. pending에서 payload_sha256와 notes는 null 허용. verified는 실제 비교 기록과 현재 payload 해시를 요구한다. unreadable/figure-incomplete가 남으면 verified 불가. wording은 설명과 함께 verified 가능하다.

### 검토 해시와 상태

`canonical_digest(value)`는 UTF-8, ensure_ascii=False, sort_keys=True, separators=(",",":")로 JSON 직렬화한 SHA256이다.

문항 payload는 review를 뺀 문항 객체 + 해당 source들의 실제 SHA256 + 참조 asset의 exam/explained 실제 SHA256 및 requirements.evidence 파일의 실제 SHA256이다. Asset payload는 review를 뺀 asset 객체 + source 실제 해시 + 두 SVG 실제 해시다. review 기록이 자기 자신을 해시하지 않는다. 내용/그림/분석 변경 시 과거 verified는 stale 오류다. 검증기는 검토 상태를 자동 verified로 올리지 않는다.

draft 검증도 스키마·ID·참조·해시·보기 수·파일 존재를 검사한다. complete는 추가로 전체 review verified와 stale 없음이 필요하다. unresolved 답은 보존과 미리보기는 가능하지만 자동 채점용 내보내기는 거부한다.

## SVG 계약

SVG는 외부 이미지나 JavaScript 없이 작성한다. 허용 태그는 svg/g/path/line/polyline/polygon/circle/ellipse/rect/text/tspan/title/desc. viewBox 필수. 속성은 id/viewBox/xmlns/role/aria-label/aria-labelledby 및 좌표·글꼴·칠/선·transform 속성의 명시 allowlist. script/style/foreignObject/image/use, on* 속성, href, url(), 외부 리소스는 거부한다. 숫자/전하의 의미를 바꾸는 자동 cleanup은 하지 않는다.

렌더링 시 SVG 내부 id와 aria-labelledby를 호출 지점별 prefix로 바꿔 중복을 피한다. 문제용은 원문 표지만 유지하며 annotated 명칭은 해설 `<details>` 안에만 삽입한다. 그림 검토는 데스크톱과 375px 화면에서 수행하고 전하·첨자·결합·꼬리·잘림을 원본과 비교한다.

## 노트/ELI5 연결

새 노트는 `정리노트/meta/MMDD.web-scope.json`을 입력 명세로 쓴다. 형태 `{schema_version:1,banks:[{path,sha256,questions:[{id,status,reason,prerequisite,refs}]}]}`. bank path는 이 명세 파일 기준 상대 경로, sha256는 bank 파일 전체 해시다. 각 bank의 전체 문항 ID가 questions에 정확히 한 번씩 포함되어야 한다. 경로의 ../는 저장소 안의 파일에 한해 허용한다. status는 included/review/deferred이며 deferred는 reason과 prerequisite 필수. refs는 `{path,section}` 배열(저장소 기준 경로); included/review는 최소 하나 필요하다. 본문/복습/보충에 가르칠 근거는 refs로 연결하고 원문은 복제하지 않는다.

명세에 넣는 bank는 현재 장에 직접 관련된 것만이다. 다른 장 자료는 출제 형태에 관한 스킬 지침으로 사용하고 원문 문항 집합에는 합치지 않는다. 해당 장에 bank가 없으면 기존 PDF 흐름이 그대로 작동한다.

노트용 export는 `n,src,q,opts,answer,why,trap,keyNote,ref`의 기존 필드를 유지하면서 `qid,content,diagnostics,answerLabel,refs,examFigureIds,explainedFigureIds,also_accept`를 추가한다. 답 인덱스는 여기서만 0-based로 바꾸고 ELI5 Q에는 1-based로 바꾼다. also_accept도 해당 출력의 인덱스 기준을 따른다. observations는 학생용 출력에 넣지 않는다. reviewed analysis를 다시 수작업으로 옮겨 적지 않는다.

JSON/SVG 삽입 시 `<`, `>`, `&`, U+2028/U+2029를 script-safe escape한다. 동적 텍스트는 textContent/HTML escape를 쓴다. SVG는 allowlist 통과 후 template을 clone하여 표시한다. refs는 실제 링크로 만든다. 신규 문항은 정답 판정에도 `분석 기준`을 표시하고 공식 답인 것처럼 표현하지 않는다.

ELI5는 기존 scope v1을 그대로 지원한다. web_scope가 있을 때만 scope v2를 만든다. v2에는 원래 note source와 웹 scope 명세의 해시·bank의 해시·해석된 모든 base_questions가 들어간다. validate_scope_lock은 다시 source를 읽어 같은 집합을 계산한다. missing/extra/중복·다른 source ID 충돌은 실패한다. scope v2도 기존 overrides의 증거 규칙과 완전성 검사를 적용한다. 명세 경로 기준은 note.parent이며 lock 저장 위치와 무관하게 상대 경로를 재계산한다.

Q의 요구 facts와 bank requirements 연결은 guide 모듈의 `WEB_BINDINGS`로 명시한다: `{qid:{group,status,requirement_facts:{requirement_id:[fact_id]}}}`. active 원문 모두의 requirements가 가르치는 fact로 연결되어야 한다. deferred는 기존 DEFERRED로 합친다. 웹 문항·해설·보기·답·그림은 bank에서 자동 생성한다. provenance의 locator는 `스크린샷 파일명 · 문제 9`이며 가짜 PDF p번호를 만들지 않는다.

## 스킬 변경

summary-note는 STT/강의노트 범위→해당 장 bank 발견→기출 PDF와 bank 모든 보기 감사→노트 작성→해설 없는 풀이 검토 순서를 따른다. 기존 범위표 게이트는 유지하되 이미 승인한 범위를 재승인 요구하지 않는다. 내용 규칙은 CLAUDE.md, 절차는 .agents 스킬 한 곳에 둔다. .claude 스킬은 이를 읽는 얇은 진입점으로 바꾼다.

고정 함정 8개 규칙을 없애고 중요 개념별 혼동 관계 확인으로 바꾼다. 요약에서도 구성원과 기능 경로를 구분한다. 개념별 원문 필요 지식은 전부, 변형 문제는 혼동 묶음당 1–2개를 기본으로 한다. 생성 문제는 실제 원문 수에 포함하지 않고 별도 표시한다. 장이 끝날 때 여러 회차의 관련 절·그림·보류를 한 번 더 검토한다. 보충은 STT에 없음/강의노트 있음/교재 근거/외부 참고를 실제 근거대로 구별한다.

## 완료와 제외

완료는 bank complete 검증, SVG 4개 원본 대조, preview 17문항 표시, 혼합 출처 테스트, 기존 회귀 테스트, 새 스킬 드라이런 보고를 요구한다. 가이드 complete에는 별도의 기존 semantic/visual/blind review도 필요하다. smoke/draft 성공을 complete 가이드 성공으로 보고하지 않는다.

제외: LMS 수집, 과거 문제 일괄 변환, 기존 1장 노트 재생성, 새 학습 앱/시간 제한 모의/성적 관리, push/merge 자동 수행.
