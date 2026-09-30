# 복습문제 풀이 기록 JSON 내보내기 설계

## 의도
복습문제 HTML에서 "다음" 등으로 문제 화면을 벗어나는 순간 그 문제의 풀이 기록(고른 답·정오·시각)을 탭 세션 스냅샷에 갱신하고, 마지막 문제 화면에서 **JSON 내보내기** 버튼으로 전체 기록을 폴더에 `.json`으로 저장한다. 학습자 본인이 나중에 확인하는 용도이며, 다시 불러오는 기능은 없다.

분류: bounded — `od:answer`, 페이저(`pager-ui`), `body.at-end`가 이미 있어서 그 위에 얹는다.

## 확정된 결정
- 저장 위치: 내보낼 때마다 폴더 선택창(`showDirectoryPicker`). 브라우저는 Chrome이며, 미지원·거부(SecurityError) 시 다운로드 폴더로 내려받는다. 선택창을 취소하면 아무것도 저장하지 않는다.
- 기록 범위: 안 푼 문제도 `selected: null`로 전체 포함.
- 용도: 확인용. 다시 열면 초기화(직전 결정 `sessionStorage` 유지), 불러오기 없음.
- 갱신 시점: 문제 화면을 벗어나는 모든 이동(다음·이전·목차·방향키·스와이프·뒤로가기)에서 갱신한다. 마지막 문제에는 "다음"이 없으므로 내보내기 클릭 시 전체를 한 번 더 갱신한다.
- 문제당 최종 상태 한 건만 남기고 이력은 남기지 않는다.
- 스냅샷 키: `sessionStorage`의 `od-review-export:v1:<documentId>`. 저장소가 막히면 메모리 값으로 내보낸다.
- 파일 이름: `<복습문제 파일명(확장자 제외)>_풀이기록_<YYYYMMDD-HHmm(로컬)>.json`.

## JSON 스키마 (`schema: 1`)
```json
{
  "schema": 1, "documentId": "복습문제_0929_Heredity.html", "range": "0929",
  "exportedAt": "2026-09-30T05:03:11.000Z",
  "summary": {"total": 34, "answered": 20, "unanswered": 14, "correct": 14, "incorrect": 5, "ambiguous": 1},
  "skipped": [],
  "cards": [
    {"id": "p1", "title": "…", "selected": "3", "answer": "2", "result": "incorrect", "updatedAt": "2026-09-30T05:01:00.000Z"}
  ]
}
```
- `cards`는 문서(DOM) 순서. `selected`·`updatedAt`은 안 푼 문제에서 `null`.
- `result`는 `correct | incorrect | ambiguous | null`.
- `skipped`는 보기가 없어 채점 대상이 아닌 카드 id 목록.

## 이번 범위 밖
- 이전 JSON 불러오기, 정리노트 읽음 기록 내보내기, 정답·해설 본문 포함, 기기 간 동기화
