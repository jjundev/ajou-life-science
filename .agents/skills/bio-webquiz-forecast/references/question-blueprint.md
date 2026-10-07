# 설계표와 pack.json

## blueprint.md (src/v<K>/blueprint.md)
15행 표: `카드 | 정답 | 유형(data-types) | 토픽 | 겨냥 혼동 | 기출 출처 | 노트 앵커`. 아래에 "재출제 유력 기출 10"과 고른 이유를 한 줄씩 적는다.

## 고정 배치
- p1–p5 기출: p1·p2 `기출그대로`, p3·p4 `기출쌍둥이`, p5 `기출숫자`(계산·조건이 있는 기출이 없으면 `기출쌍둥이`로 바꾸고 `exam_counts`를 `{"기출그대로":2,"기출쌍둥이":3}`로 적는다).
- p6–p15 새 문제.
- 정답 A~E 각 3개. 기출그대로 카드는 원문 보기 순서를 섞어 정답 글자를 맞춘다.
- `types_required`: `{"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "장섞기": 1}`. 장에 계산 거리가 없으면 `계산`을 줄이고 blueprint에 이유를 쓴다.

## 유력 기출 고르는 규칙
1. o1의 ★★★·★★☆ 주제를 다루는 기출부터.
2. `pool.json`에 있는 기출만(답이 확정된 복습팩 카드).
3. 이전 버전 `pack.json`의 `exam_sources`와 `used_exam_sources`에 있는 번호는 p1–p5에 쓰지 않는다.

## v2 이후 차별화
- 이전 blueprint와 같은 (토픽, 겨냥 혼동, 발문 방향) 조합을 피한다. 이전 세트에서 덜 다룬 ★★★·★★☆ 토픽을 먼저 채운다.
- 같은 혼동을 다시 낼 때는 숫자·생물·그림·발문 방향(옳은 것 ↔ 옳지 않은 것) 중 둘 이상을 바꾼다.
- 발문은 이전 세트와 같으면 안 된다(check.py `stem-dup`).

## pack.json
```json
{
  "course": "생명과학", "chapter": 4, "version": 2,
  "note_href": "../../복습노트/<날짜>/정리노트_<날짜>_<slug>.html",
  "review_title": "4장 웹과제 예상 v2", "review_intro": "…", "footer_review": "근거: …",
  "parts": [
    {"id": "partA", "title": "A. 예상 개요", "short": "예상 개요"},
    {"id": "partB", "title": "B. 기출 재출제 예상", "short": "기출 5"},
    {"id": "partC", "title": "C. 새 문제 예상", "short": "새 문제 10"}
  ],
  "problems": [{"id": "o1", "part": "partA"}, {"id": "o2", "part": "partA"},
               {"id": "p1", "part": "partB"}, "… p5까지 partB", {"id": "p6", "part": "partC"}, "… p15까지 partC"],
  "answer_key": {"p1": "A", "…": "…"},
  "exam_sources": {"p1": {"source": "기출 4강 6", "mode": "기출그대로"}, "…": "…"},
  "types_required": {"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "장섞기": 1},
  "forbidden": ["다음 장 핵심어", "…"],
  "legacy": false, "used_exam_sources": []
}
```
`problems`의 `"…"` 자리는 실제 항목으로 모두 펼쳐 쓴다. `note_href`는 그 장을 처음 다룬 정리노트다. `forbidden`에는 다음 장 핵심어(예: 4장이면 `헬리케이스`, `오카자키`, `코돈`, `전사`, `번역`)와 수업에서 빠진 쪽의 용어를 넣는다.
