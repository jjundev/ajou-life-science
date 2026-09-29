# 출처와 전체 내용

HTML/MD, 모든 복습문항과 장마감 문서를 읽는다. HTML과 MD가 모두 있으면 핵심 개념·수치·조건을 대조한다. 숫자가 다르면 conflicts에 출처와 차이를 기록하고 근거로 해결하기 전 TTS를 실행하지 않는다.

manifest schema v1의 실제 예시는 tests/_util.py의 minimal_manifest()다. topics.requirements에 학습 개념·수치·보충·오개념·문항 판별점을 각각 넣고 source_id와 locator를 남긴다. 반복 설명은 통합하되 각 requirement를 segment에 연결한다. questions에는 모든 문항 ID와 판별점 requirement_ids를 기록하고 scenes.question_ids로 연결한다.

coverage_reviews는 claim과 발화문을 직접 대조한 뒤 작성한다. ID 연결이나 문자열 포함만으로 passed를 쓰지 않는다. 필수 학습 내용은 exclusions로 제외할 수 없다. 원문 전체에서 발견한 항목이 manifest에 모두 들어갔는지 별도로 검토하고 source/coverage.md에 근거를 남긴다. 기계 검사는 항목 발견 자체와 의미 동일성을 증명하지 못한다.

지난 시험 공지/예고는 notices에 period_label을 기록하고 “당시 수업 안내”로 표시한다. 비학습 반복/내비게이션만 exclusions에 이유와 출처를 남긴다.
