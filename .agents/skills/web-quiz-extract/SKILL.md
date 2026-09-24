---
name: web-quiz-extract
description: 웹과제 완료 후 제공된 문제 스크린샷을 생명과학 저장소의 검증 가능한 웹과제 문제은행으로 등록할 때 사용한다. 이미 등록된 문제은행으로 복습팩을 만드는 요청에는 사용하지 않는다.
---

# 웹과제 스크린샷 등록

이 스킬은 `웹과제/N장/raw/`의 화면을 `questions.json`과 필요한 `image/` SVG로 등록한다. 필드 정의는 저장소 루트의 `웹과제/question-bank.schema.json`을 따른다. `REPO`는 저장소 루트이며 아래 검증 명령은 `REPO`에서 실행한다.

## 1. 평가와 원본 인벤토리

사용자가 지정한 장 번호와 화면에서 확인되는 날짜·평가명·전체 문항 수를 기록한다. 입력 이미지가 `raw/` 밖에 있으면 바이트와 실제 파일명을 유지해 복사한다. 기존 `raw/` 파일은 다시 만들지 않는다. 동일 이름에 다른 바이트가 있거나 기존 `questions.json`이 있으면 덮어쓰지 않고 충돌을 보고한다. NFD 파일명은 보존하고 NFC는 검색할 때만 사용한다.

각 화면의 실제 파일명, SHA256, 픽셀 크기, 문항 번호, 보기 개수, 전후 화면과의 연결, 제출 전/후 여부를 `웹과제/N장/intake.md`의 인벤토리에 적는다. 중복 화면도 버리지 않고 연결한다. 전체 문항 수와 각 번호의 발문·모든 보기를 화면으로 확인했는지 대조한다. 날짜, 장 번호, 전체 문항 수, 각 문항의 필수 배점 중 하나라도 확인할 수 없으면 부족한 정보와 화면을 보고하고 `questions.json`을 새로 게시하지 않는다. 시간 제한·총점만 보이지 않으면 스키마의 `null`을 사용한다.

## 2. 원문 전사와 관찰 분리

각 문항의 발문, 조건문과 소문항, 그림 순서, 보기 기호·문구·순서·배점을 원본과 다시 비교한다. OCR은 초안 보조로만 사용한다. 하나의 문항을 여러 화면에서 읽었다면 모든 원본 source ID를 연결한다. `selected_option_id`는 캡처의 선택 표시, `official_answer`는 결과 화면이 직접 증명한 공식 답, `analysis.answer_option_id`는 별도 판단이다. 선택 표시를 공식 답으로 복사하지 않는다. 공식 답 화면이 없으면 `official_answer: null`이다.

현재 저장 형식은 단일 선택형과 안전한 SVG 그림만 지원한다. 다중 선택형, 단답형, 충실하게 SVG로 옮길 수 없는 사진이나 읽을 수 없는 그림을 발견하면 문항 번호·원본 파일을 `intake.md`에 적고 이 평가의 `questions.json`을 새로 게시하지 않는다. 그림이 없다면 `assets: []`이다. 그림이 있으면 `image/qNN.svg`에는 원문만, `image/qNN.explained.svg`에는 풀이용 내용을 넣는다. 둘 다 원본과 시각 대조하고 `scripts.question_bank.svg.validate_svg`를 통과시킨다. 문제용 SVG의 텍스트·대체 설명에 원본에 없는 답 힌트를 넣지 않는다.

## 3. 답과 필요 지식의 근거

같은 장의 실제 강의노트·STT·교과서 파일에서 정확한 쪽·절·시간과 인용문을 확인한다. 모든 보기의 선택 적합성을 `analysis.option_diagnostics`에, 필요한 지식을 `analysis.requirements`에 그 근거로 작성한다. 표현이 모호하면 `analysis.issues`와 채점 상태를 공개한다. 근거 파일이 없거나 보기를 판단할 수 없으면 빈 근거·가짜 인용·그럴듯한 정답으로 스키마를 채우지 않는다. `raw/`와 `intake.md`에 미해결 항목을 남기고 `questions.json`을 새로 게시하지 않는다.

## 4. 검토 해시, 검증, 미리보기

화면별 원문·모든 보기·캡처 관찰, 그림, 분석 근거를 다시 대조한다. 번호 집합은 `1..expected_question_count`와 같아야 하고 raw source는 모두 참조되어야 한다. 검토가 끝난 문항·그림에만 `review.status=verified`를 쓰고 검토 기록을 남긴다. 저장할 `payload_sha256`는 현재 파일에 대해 `scripts.question_bank.model`의 `canonical_digest(question_payload(bank, question, bank_dir))` 또는 `canonical_digest(asset_payload(bank, asset, bank_dir))`로 계산한다. 검토 없이 해시만 갱신하지 않는다.

저장소 루트에서 `.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/N장/questions.json' --complete`를 실행한다. venv가 없다면 `.agents/skills/bio-review-pack/references/problem-selection.md` 2절의 환경 설정을 따른다. 성공한 뒤 `.venv-question-bank/bin/python -m scripts.question_bank preview '웹과제/N장/questions.json' --output '웹과제/N장/preview.html'`을 실행한다. 실제 브라우저에서 데스크톱과 375px 너비로 문제·보기·SVG·출처 링크와 정답 공개 위치를 본다. complete 검증 실패나 시각 대조 미완료를 성공으로 보고하지 않는다.

끝에 원본 화면 수·문항 수·보기 수·그림 수, 생성 파일, 검증 결과, 공식 답 확인 여부와 미해결 항목을 구분해 보고한다. `bio-review-pack`은 같은 장의 `questions.json`에 대해 `--complete`가 성공해야 문제를 사용한다.
