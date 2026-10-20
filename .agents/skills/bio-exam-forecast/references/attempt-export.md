# 시험 응시 기록과 복기 프롬프트

제출 때 만드는 응시 기록(`schema: "bio-exam-attempt"`, `schemaVersion: 1`)은 결과 화면·채점표·복기 프롬프트가 함께 쓰는 내부 스냅샷이다. 파일로 내보내지 않으며 서버 전송·파일 자동 수집·가져오기도 제공하지 않는다.

- `documentId`: 생성된 시험 HTML 파일명.
- `range`, `examVersion`: 장 범위와 표시 버전.
- `questionSetHash`: `pack.json`의 `problems`를 `ensure_ascii=False, sort_keys=True, separators=(',', ':')`로 직렬화한 UTF-8 바이트의 SHA-256. 표시 버전만 바뀌고 문항 데이터가 동일하면 같은 해시다.
- `attemptId`, `submittedAt`: 제출 시 생성되는 응시 식별자와 ISO 8601 UTC 제출 시각.
- `summary`: 전체 `total`, `answered`, `unanswered`; `mcq`의 `total`, `correct`, `incorrect`, `unanswered`; `short`의 `total`, `matched`, `pending`, `unanswered`.
- `cards`: 문항 순서대로 `id`, `format`(`mcq`/`short`), `selected`, `answer`, `result`를 담는 배열.
- `selected`: 객관식 보기 ID 또는 단답형 입력 원문. 공백만 입력하거나 미응답이면 `null`이다.
- `answer`: 기존 문항의 정답 객체를 보존한다. 객관식은 `kind`, `option_id`; 단답형은 `kind`, `canonical`, `accepted`, `case_sensitive`다.
- `result`: 객관식 `correct`/`incorrect`/`unanswered`, 단답형 `matched`/`pending`/`unanswered`. `pending`을 오답으로 바꾸거나 단답형 전체 점수를 산정하지 않는다.

결과 화면의 **복기 프롬프트 복사**는 이 기록과, KaTeX 렌더 전에 캡처한 문항 원문(제목·문제·보기·풀이 단계)으로 `docs/superpowers/specs/2026-10-20-review-prompt-export-design.md` 형식의 프롬프트를 만든다. `matched`는 맞힌 문항으로, `pending`은 `자기채점 대기` 묶음으로 넣고 단답형은 정답과 허용답을 함께 적는다. 클립보드 복사가 막히면 프롬프트가 선택된 직접 복사 대화상자를 연다.

제출 후 입력은 잠그고, 확인을 거친 다시 풀기에서만 기록을 폐기한다. 결과는 새로고침 후 복원하지 않으며 이를 결과 화면에 안내한다.
