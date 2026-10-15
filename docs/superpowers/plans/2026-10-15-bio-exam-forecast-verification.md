# 시험 예상문제 스킬 구현 검증

검증일: 2026-10-16. 구현은 managed worktree `bio-exam-forecast`의 detached HEAD 39f8bb3 위 미커밋 변경이다. 원래 checkout의 기존 untracked 계획/피드백을 수정하지 않았다. 실제 수업 시험 세트는 생성하지 않았다.

## 결과

- 새 bio-exam-forecast suite: **52 passed** (합성 75문항, 55+20 형식, 범위, 자료 변경, 배정/중복, 브라우저, CLI, 해설 발행).
- bio-problem-explain suite: **187 passed**, 기존 날짜형/all/최신/forecast 회귀 포함.
- bio-webquiz-forecast suite: **49 passed**.
- 저장소 tests: **120 passed, 1 skipped, 43 subtests passed**. skip은 tests/test_generated_files.py:13의 기존 분할 PDF 미생성 항목이다. PyMuPDF의 Swig 타입 DeprecationWarning 5개가 있다.
- 합계 **408 passed**. 각 suite는 별도 pytest 프로세스로 실행했다.
- skill-creator quick_validate: Skill is valid. git diff --check 및 신규 텍스트 whitespace 검사 성공.
- 브라우저: 문제·해설 각 1280x900/375x812 × light/dark. 제출 전 숨김·제출/초기화·단답 허용답/자기채점·JS off·인쇄 숨김·수식/SVG/표/래스터·외부 요청 및 가로 overflow 검사. 별도 desktop/mobile 스크린샷을 직접 확인했다.

실행 환경: `/tmp/bio-forecast-test-env/bin/python`, pytest/jsonschema/playwright/PyYAML/PyMuPDF. 일반 root tests는 `PYTHONPATH=tests:.`로 실행했다. 원본 데이터와 고정 vendor는 변경하지 않았다.

## 최종 독립 검토와 수정

직접 구현 후 fresh reviewer(gpt-6-astra)가 read-only 검토했다. Critical 0, Important 3, Minor 0. 세 Important를 모두 실패 테스트로 재현한 뒤 한 번의 수정 패스에서 해결하고 전체 suite를 다시 실행했다. 수정 후 별도 재검토를 수행했다고 주장하지 않는다.

1. RUN 후보를 고쳐 select/build해도 이전 src가 렌더되는 문제: 재선정 후 새 버전 예약으로 수정. 이전 HTML 보존과 새 풀이 반영을 검증했다.
2. 현재 RUN의 버전을 과거 생성 이력에 포함해 거짓 부족을 내는 문제: 같은 RUN 소유 버전들을 과거 신규 출제 이력에서 제외. 정확히 75개 후보로 반복 수정/재선정 가능함을 검증했다.
3. 같은 생성 발문에 보기만 바꾸어 두 문제를 선정하는 문제: 현재 후보의 generated stem도 충돌 가족으로 합치고 pack에서도 재검사. 부족을 숨기지 않는지 검증했다.

실제 학술 정확성/공식 답/경향의 실제 적용과 시험 적중률/학습 효과는 합성 설치 테스트로 판단하지 않았다. 실제 스킬 호출에서 75문항에 대한 source_visual/content_scope_style/independent/browser 및 해설 네 검토가 필요하다. 보류한 Minor는 없다.

## 구현 판단과 비용

- 커밋은 계획의 별도 요청 조건에 따라 보류했다. 커밋이 작업 기록을 보존하지 않으므로 ignored 실행 ledger도 유지한다. 비용: 통합 전에 변경 파일을 별도로 확인해야 한다.
- 출처 배합은 family-slot augmenting matching 후 국소 개선하는 soft 목표다. 장/형식/가족·범위가 우선이며 차이를 보고한다. 비용: 전역 최적화로 달성 가능한 배합이라도 편차가 남을 수 있다.
- 기존 해설 adaptation provenance의 현재 destination 해시 중 11개가 구현 전부터 오래된 상태였다. 원래 checkout 및 CRLF 재구성도 대조했다. 현재 수정된 adaptation destination 해시를 갱신하고 새 파일을 등록했으며, 역사적 source 해시와 unchanged pinned vendor는 보존했다. 비용: 이전 adapted destination snapshot의 식별값 대신 현재 adaptation을 기록한다.
- 커밋이 승인되지 않았으므로 commit-range package 대신 tracked diff+명시한 untracked 소유 파일로 최종 검토했다. 비용: 새 파일 누락 위험이 있어 검토 범위를 전부 나열했다.
- 재선정/수정은 새 버전을 만들고 같은 RUN 소유 초안들을 과거 신규 출제 이력에서 제외한다. 비용: 초안 버전 폴더가 늘어나며 별도 신규 출제는 새 RUN을 사용해야 한다.
- 독립 검토자가 합성 자료로 판단할 수 없는 실제 학술·출제 성능은 미검증으로 유지했다. 비용: 실제 세트 생성 시 별도 의미 검토가 필요하며 설치 성공으로 대체할 수 없다.

## 보관 위치와 사용

정본은 `.agents/skills/bio-exam-forecast/SKILL.md`, `.claude/skills/bio-exam-forecast`는 정본 링크다. 현재 구현은 위 managed worktree에만 있다. 이 checkout에서 `/bio-exam-forecast 1장~6장`으로 실제 출제 작업을 시작할 수 있다. 원래 checkout 통합·커밋·푸시는 수행하지 않았다.
