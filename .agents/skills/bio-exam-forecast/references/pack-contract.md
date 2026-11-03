# 데이터 계약

scripts/exam_contract.py가 기계 계약을 검사한다. `parse_scope`는 단일 장/연속 범위를 Scope(chapters tuple, label)로 만든다. `Selection`은 problems/quotas/shortages/deviations를 가진다. shortage가 있으면 build 금지다.

`scope.json`: chapters, topics. topic은 id/chapter/title/evidence/scope_status(included|excluded|uncertain)/reason. evidence는 path(repo-relative POSIX), sha256, locator, role. 토픽을 모든 보기·조건과 실제로 대조하며 included만 선정한다.

후보의 필수 필드:

- id, family_id, format(mcq|short), origin(web|past|new), mode(original|variant|generated).
- primary_chapter, required_chapters, topic_ids, level(1..3), priority(다섯 순위의 bool 배열).
- types(열린 문자열 배열), selection_reason, problem_html(전체 조건/그림/보기), options(순서대로 id/text; 단답형은 빈 배열).
- answer: 객관식 `{kind:"choice",option_id:"B"}`. 단답형 `{kind:"short",canonical:"Aa",accepted:["Aa","명시 동의어"],case_sensitive:true}`.
- rejected_answers의 text/reason, solution_steps의 비어 있지 않은 HTML 단계, minimum_steps(실제 추론 수).
- source_refs(path/sha256/locator/role), style_basis(path/sha256/locator/criterion/application).
- transformation(변형/생성 설명), original_payload_sha256(원문이면 `payload(candidate)`, 그 외 null).
- review의 scope/key/source/style/family 각각 status/pass와 evidence. collector 초안은 not_run이며 의미 판단을 마치기 전 선정하지 않는다.

`concept_summary`는 문항별 짧은 일반 텍스트 제목이다. 후보에 작성하면 pack에 보존하고, 생략하면 포함 토픽 제목으로 채운다. 새 발행본은 [확정 양식](exam-ui.md)에 따라 적절한 개념 요약과 답 노출 여부를 검토한다. 제목은 HTML 이스케이프해 `pN. 개념 요약`으로 표시하며, 문제·정답·풀이 데이터와 구분한다.

문제 HTML은 정답·힌트·풀이·모델을 포함하지 않는다. 객관식은 4~5보기 ul.choices의 순서/텍스트와 options가 같아야 한다. 그림 src는 저장소 상대 경로다. HTML은 수동 저작이며 실행 코드/외부 URL/이벤트 속성을 넣지 않는다.

`pack.json`: schema_version=1, profile=exam, scope, range, version, counts(55/20), targets(생성 정책), policy_summary, scope_data, source_manifest, problems. problems는 p1..p55(mcq), p56..p75(short), 원래 id는 candidate_id. scope/pack/blueprint/candidates/cards/HTML이 서로 일치해야 한다.

새 build는 같은 pack에서 연습형·시험형 문제판을 생성한다. `presentations.json`은 두 파일의 이름·SHA-256·공통 문제 집합과 원본 해시를 기록하며 문제 검토와 해설 문맥에 함께 묶인다. [두 풀이형 계약](dual-html.md)을 따른다. 문항 수나 출제 이력은 두 배로 세지 않는다.

policy_summary는 type_targets[{chapter,type,target,reason,source_ref}], difficulty_targets[{chapter,basic,advanced,reason,source_ref}], reason을 가진다. 불명확한 target은 null/이유를 쓴다. 코드가 경향 본문을 통계로 해석하지 않는다.

source-manifest는 sources[{path,role,status:present|missing,sha256:null 또는 digest}],warnings. 실제 사용한 PDF·원본 이미지·그림·근거도 등록한다. prepare 후 에이전트가 추가한 근거는 build에서 현재 해시와 대조한다.

단답형 정규화는 NFC+양끝 공백 제거뿐이다. case_sensitive=false일 때만 casefold. 내부 공백/단위/분수/소수는 동치화하지 않는다. 허용하려면 accepted에 직접 적는다. 빈 답은 미응답이며 낯선 답은 자기채점 대기다.

새로 생성하는 두 문제판의 객관식은 `option_explanations`(보기 ID → 검토된 설명 HTML)를 모든 보기에 제공한다. 일반 `solution_steps`와 구분하며 연습형 생성기가 누락·빈 설명을 거부한다. 기존 발행 단일 HTML의 정답·문항 계약은 유지한다.
