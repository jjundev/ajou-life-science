# 문제 검토와 불변성

`check`는 구조를, `check --final`은 현재 입력에 묶인 검토 완료를 검사한다. 구조 성공을 학술 검증으로 보고하지 않는다. question-review.json은 build 시 모두 not_run이다. 현재 input_hash는 pack/blueprint/scope/policy/candidates/manifest/report/75 cards/HTML/vendor/assets에 묶인다. 원본 근거는 별도 freshness로 검사한다. MD 수정·삭제·부재 파일 신규 등장 시 이전 pass로 진행하지 않는다.

네 검토 모두 status=pass, reviewer, 구체적 evidence, items의 p1~p75 각각 비어 있지 않은 근거가 필요하다.

- source_visual: 발문·수치·조건·보기 순서·원본 그림/PDF 페이지, 분석/공식 답 구별. PDF는 필요한 실제 페이지를 렌더해 읽는다.
- content_scope_style: 모든 보기의 required_chapters, included topic, 최신 policy-notes/style_basis의 실제 적용, 난이도·오답의 타당성, 중복 개념 과집중·문항 간 답 노출.
- independent: 별도 검토자가 blind HTML과 학습 근거로 처음부터 다시 푼 답/판단. 원 정답·해설·pack/blueprint/style_basis/출처는 제공하지 않는다. SVG·표·래스터 그림은 그대로 둔다. 다시 푼 결과와 제작자의 답을 컨트롤러가 대조한다.
- browser: 1280x900/375x812, light/dark. 75문항 모두 접근 가능, 보기·표·그림·수식/단답 입력 표시, 제출 전 답/출처 hidden, JS off와 print에서도 hidden, 제출 후 모든 답 공개, 낯선 단답 자기채점, 빈 답 미응답, reset 초기화. 키보드 사용·가로 overflow·콘솔/자원 실패·외부 요청도 확인한다.

blind 명령은 새 출력 폴더로 실행한다. 문제용 그림만 복사하고 해설용 그림·허용답·hint·script·데이터 모델·출처를 제외한다. blind 자체의 75문항·20단답·그림/표 보존을 실제로 확인한다.

초안 변경/rebuild는 네 검토를 초기화한다. 네 검토가 완료된 버전은 새 버전을 사용한다. 해시만 바꿔 이전 승인을 살리지 않는다. 최대 2회 수정 예산은 explanation-handoff를 따른다. 합성 테스트의 TEST ONLY 검토는 실제 시험 문제 검토로 사용하지 않는다.
