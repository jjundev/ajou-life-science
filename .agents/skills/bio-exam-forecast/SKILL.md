---
name: bio-exam-forecast
description: 생명과학 중간·기말 시험 예상문제와 해설을 사용자 지정 장 범위에서 만들 때 사용한다. "1장~6장 시험 예상문제", "중간고사 모의시험", /bio-exam-forecast [장 범위]에 사용한다. 장별 웹과제 예상은 bio-webquiz-forecast, 수업 정리·복습문제는 bio-review-pack을 사용한다.
---

# 생명과학 시험 예상문제

입력 범위에서 객관식 55문항과 단답형 20문항, 검토된 문제 HTML과 해설 HTML을 만든다. 55+20은 사용자 가정이며 실제 시험의 확정 형식·적중률이 아니다. 장별 균등·출처 배합은 생성 정책이다. 웹과제 재출제 비율은 알려져 있지 않다.

`SKILL`은 이 파일의 실제 폴더, `REPO`는 저장소, `RUN`은 새 빈 임시 폴더다. Python 3.10+, 기존 `requirements-question-bank.txt`의 jsonschema가 필요하다. 실제 경로를 넣어 `python3 SKILL/scripts/exam_cli.py COMMAND ...`로 실행한다. CLI는 저작·의미 검토를 자동 수행하거나 pass를 만들지 않는다.

1. `prepare --repo REPO --scope '1장~6장' --run RUN`. 단일 장·연속 범위만 받는다. [계약](references/pack-contract.md)을 읽는다. 문제·모든 보기·그림을 판단하는 데 필요한 지식이 입력 범위에 속해야 한다. 이전 장도 범위 밖이면 필수 지식으로 쓰지 않는다.
2. **매 실행에 원본을 새로 읽는다**: [공통 출제 경향](../bio-review-pack/references/webquiz-style.md), [공통 노트 피드백](../bio-review-pack/references/note-feedback.md), 선택 범위의 `웹과제/N장/note-feedback.md`, `questions.json`, `intake.md`. 공통 MD는 필수, 장별 부재는 manifest의 missing 기록으로 남긴다. 실제 은행·파일 상태가 오래된 MD 서술과 다르면 현재 검증된 파일을 사용하고 불일치를 공개한다. 경향 본문을 여기 복제하지 않는다.
3. [저작 규칙](references/authoring.md)에 따라 강의노트·STT·교과서·기출을 읽고 `RUN/scope.json`의 포함 토픽/근거를 작성한다. 읽은 절·판별 기준·장별 적용/비적용을 `policy-notes.md`에 기록한다. 최신 MD에서 유형·난이도 목표를 정해 `policy-summary.json`에 기록한다. 불명확하면 target은 null과 이유를 둔다. 해시만 기록하고 실제 읽기를 대신하지 않는다. 새 유형을 고정 enum으로 제한하지 않는다.
4. 원문 초안과 범위 내 새 문제를 `candidates.json`에서 검토·저작한다. 문항별 `style_basis`에 경로·SHA·절·판별 기준·실제 적용을 연결한다. 미확인 정답·결함·불필요한 범위 확장은 제외한다. 응시 선택을 공식 답으로 간주하지 않는다. 원문 재사용은 조건·수치·보기 순서·그림을 그대로 보존하고 수정 시 variant로 표시한다. [선정](references/selection.md)에 따라 `select --run RUN`. 부족하면 같은 범위에서 추가 저작하거나 부족을 보고한다. 반복·빈 문제로 수를 채우지 않는다.
5. **생성 전에 [확정 화면·동작 양식](references/exam-ui.md)을 읽는다.** 사용자 확정 레퍼런스는 1장~6장 v9이며, 화면과 동작의 기준으로만 사용한다. 새 문제는 최신 원자료와 경향으로 저작한다. 문항별 `concept_summary`, 객관식 선택 후 자동 이동, 상단 `다시 풀기`, 마지막 문항의 `전체 제출`, 제출 후 결과·5열 채점표·복기 프롬프트 복사를 유지한다. `build --run RUN`, `check --run RUN`. 버전은 `시험예상/<범위>/.pack/vK/`에 예약된다. 원본·완성 버전은 덮어쓰지 않으며, 새 버전을 생성했다고 이전 버전을 자동 삭제하지 않는다.
6. [검토](references/verification.md)를 읽고 `blind --run RUN --out NEW/index.html`로 만든 **그림·표를 보존한 HTML**을 별도 독립 풀이자에게 준다. 정답키·풀이·출처·설계표·모델은 주지 않는다. 학습 근거는 제공한다. 작성자가 독립 검토를 자처하지 않는다. `source_visual/content_scope_style/independent/browser` 네 검토를 75문항 각각 실제 수행하고 현재 input_hash의 question-review.json에 근거를 적는다. 자동 검사는 학술·범위·경향·문항 간 답 노출 검토를 대신하지 않는다. `check --run RUN --final`.
7. [해설 인계](references/explanation-handoff.md)에 따라 `bio-problem-explain`을 **명시 문제 HTML 경로**로 실행한다. exam profile은 p1~p75와 20개 단답형의 정답·허용답을 보존한다. 기존 all/최신 자동 선택은 복습노트만 유지한다. 해설 네 검토와 발행 게이트도 통과한다.
8. 최초 검토 후 수정은 문제·해설 합계 최대 2회다. 수정 전 `repair --run RUN --reason '구체적 원인'`. 새 해설 RUN으로 예산을 초기화하지 않는다. 문제 변경은 문제 재검토+새 해설 추출, 해설 변경은 build/check+네 검토다. `status --run RUN --explanation ABS_HTML`로 현재 근거·검토·산출물을 확인한다. 둘 다 검증될 때 complete, 문제만 검증되면 partial로 보고하고 보존한다.

v9 양식 채택은 학술 검토 완료를 뜻하지 않는다. 새 문제·해설은 정해진 검토와 발행 게이트를 각각 통과해야 한다.

최종 보고: 두 HTML 링크와 검증 상태, 장별 형식 수, 출처 목표/실제 차이와 사유, 경향 반영, 이전 버전 중복, 공식 답 미확인·미해결. 입력 파일 변경·삭제·missing 파일 신규 등장은 검토를 무효화한다. 다음 실행은 최신 MD를 읽지만 기존 HTML이 자동 갱신되지는 않는다. 설치 검증은 합성 자료만 사용하며 실제 세트·커밋·푸시를 자동 추가하지 않는다.
