# 시험 풀이기록 JSON v1

`schema: "bio-exam-attempt"`, `schemaVersion: 1`은 시험 전용 기록이다. 기존 복습문제의 `schema: 1`과 호환된다고 간주하지 않는다. 서버 전송·파일 자동 수집·가져오기는 제공하지 않는다.

- `documentId`: 생성된 시험 HTML 파일명.
- `range`, `examVersion`: 장 범위와 표시 버전.
- `questionSetHash`: `pack.json`의 `problems`를 `ensure_ascii=False, sort_keys=True, separators=(',', ':')`로 직렬화한 UTF-8 바이트의 SHA-256. 표시 버전만 바뀌고 문항 데이터가 동일하면 같은 해시다.
- `attemptId`: 제출 시 생성되는 응시 식별자. 재내보내기 시 유지한다.
- `submittedAt`, `exportedAt`: ISO 8601 UTC 시각. 제출 시각은 고정하고 내보내기 시각만 갱신한다.
- `summary`: 전체 `total`, `answered`, `unanswered`; `mcq`의 `total`, `correct`, `incorrect`, `unanswered`; `short`의 `total`, `matched`, `pending`, `unanswered`.
- `cards`: 문항 순서대로 `id`, `format`(`mcq`/`short`), `selected`, `answer`, `result`를 담는 배열.
- `selected`: 객관식 보기 ID 또는 단답형 입력 원문. 공백만 입력하거나 미응답이면 `null`이다.
- `answer`: 기존 문항의 정답 객체를 보존한다. 객관식은 `kind`, `option_id`; 단답형은 `kind`, `canonical`, `accepted`, `case_sensitive`다.
- `result`: 객관식 `correct`/`incorrect`/`unanswered`, 단답형 `matched`/`pending`/`unanswered`. `pending`을 오답으로 바꾸거나 단답형 전체 점수를 산정하지 않는다.

화면과 JSON은 같은 제출 스냅샷을 사용한다. 제출 후 입력은 잠그고, 확인을 거친 다시 풀기에서만 스냅샷을 폐기한다. 결과는 새로고침 후 복원하지 않으며 이를 결과 화면에 안내한다. 내보내기는 UTF-8 JSON Blob 다운로드로 동작하고 실패해도 응시 기록을 유지한다.
