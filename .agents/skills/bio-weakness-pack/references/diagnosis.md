# 공부 기록과 해당 차시 자료를 함께 읽기

SSTT는 정리노트만 읽은 기록이 아니다. 학습자는 해당 차시의 **정리노트·복습문제·문제설명 HTML을 함께 보며 공부하고 녹음**했다. 문제를 읽거나 해설을 따라 말한 발언도 있으므로, 세 자료를 읽기 전에 발언만으로 오개념·독립 풀이·자발적 자기교정을 확정하지 않는다.

## 차시 확정과 전체 읽기

1. 선택한 SSTT를 파일 전체·숫자 순서로 읽고 공부 시작 안내, 문항 표현, 내용으로 원래 차시 폴더를 확인한다. 파일명 날짜는 첫 후보이며, 공부 날짜와 자료 차시가 다를 수 있다. 다른 차시를 다룬 파일은 실제 자료에 각각 연결한다. 끝의 다음 회차 안내만으로 그 회차를 포함하지 않는다.
2. `python3 CLI study --repo REPO --folder 복습노트/차시`의 출력을 JSON으로 보관한다. `files`에는 note/review/explanation 경로·SHA-256·학습 항목 ID·보기·해설 구역이 있다. 이 명령은 **목록만 만들며 읽기 완료를 판정하지 않는다.**
3. 해당 차시의 세 HTML에서 아래 학습 내용을 **전체** 읽는다. HTML에서 학습 내용을 항목별로 추출·분할해 읽어도 되지만, 검색에 걸린 토픽·문항만 읽거나 Markdown 사본만 확인하고 HTML 전체를 읽었다고 기록하지 않는다.

| role | 자료 | 필수 범위 |
|---|---|---|
| note | 정리노트 | 모든 토픽·요약·표·주의·보충·그림과 설명 |
| review | 복습문제 | 모든 문항의 지문·보기·그림·원문 정보·힌트·정답·풀이 |
| explanation | 문제설명 | 모든 문항의 문제 읽기·판단 기준·보기별 판정·검산·추가 확인 |

접힌 details와 숨겨진 다른 화면의 내용도 포함한다. CSS·JavaScript 전체를 학습 내용으로 읽을 필요는 없다. SVG·문항 그림의 시각적 관계가 판단에 필요하면 실제로 렌더링해 본다. 읽은 항목, 내용 확인 결과와 그림 검토를 RUN 내부 근거 파일에 기록한다. 같은 근거 파일을 역할별로 참조해도 되지만 각 자료를 확인한 내용이 드러나야 한다.

폴더에 같은 종류의 파일이 여러 개면 자동 최신 선택·무조건 합치기를 하지 않는다. 의도한 자료 세트를 확인해 `study --note 경로 --review 경로 --explanation 경로`로 명시한다. 명시 파일도 해당 차시 폴더 안에 있어야 한다. 같은 세트가 아닌 파일을 섞으면 `suite_mismatch`로 표시되며 확정 문항 연결에 사용할 수 없다. 차시 후보 자체가 불명확하면 `unresolved_sessions`에 보류 이유를 기록하고 그 입력의 발언을 다른 차시의 약점으로 사용하지 않는다.

세 자료가 없거나 일부 누락되면 `missing`을 보존하고, 읽을 수 있는 자료는 전체 읽는다. 누락된 자료가 필요한 문항 판정은 보류한다. 강의자료·교재로 확인 가능한 개념 자체의 보완은 `concept` 연결과 보류 이유로 구분할 수 있다. 모든 자료가 없거나 진단할 근거가 없으면 해당 날짜 팩 생성을 보류한다.

## 자료의 역할과 원래 문항 연결

- SSTT: 학습 신호의 주된 근거. 나중의 정정까지 읽고 최초 발언·정정·망설임을 구분한다.
- 차시 HTML 3종: 어떤 설명·문제·보기·해설을 보며 말했는지 해석하는 문맥. 자료가 존재한다는 것만으로 특정 문항을 실제 풀었다고 단정하지 않는다.
- 강의자료·교재: 정확성 검증. 기존 해설도 오류가 있을 수 있다. 필요한 교재 쪽은 렌더링해 확인하고 PDF 쪽과 인쇄 쪽을 구분한다. 자료 충돌·문항 모호성은 학습자 약점과 분리한다.
- 실제 기출·웹과제 원문: 차시 문제의 출처를 특정할 수 있을 때 추가 대조한다. 기존 생성 문제의 정답과 공식 채점 정답을 구별한다. 최종 제출 답을 녹음만으로 추정하지 않는다.

약점의 `source_context`에는 원래 차시를 지정하고 다음 상태를 사용한다.

| match | 의미 | 필드 |
|---|---|---|
| confirmed | 고유한 발문·보기·번호로 원래 문항 확인 | problem, 관련 choices, note_topics, explanation_sections |
| candidate | 비슷한 문항이 여러 개여서 미확정 | candidates, reason; 확정 problem은 넣지 않음 |
| concept | 특정 문항에 연결되지 않는 개념 발언 | note_topics, reason; 확정 problem은 넣지 않음 |

`source_context.problem`은 **기존 복습문제 ID**, 약점의 `problems`는 **새 약점팩 문제 ID**다. 두 번호가 같아야 하는 것이 아니다. 확정 연결은 원래 복습문제와 문제설명 모두에 있는 ID만 사용한다. choices·note_topics·explanation_sections는 목록으로 명시하고 관련 해설 구역을 하나 이상 연결한다. 정리노트가 있으면 관련 토픽도 연결한다. 특정 보기를 언급하지 않은 발언은 choices를 빈 목록으로 명시할 수 있다. 불일치 목록 `review_only`·`explanation_only`를 보고 해당 문항의 판정을 보류하고, 정상 대응되는 다른 문항까지 자동 폐기하지 않는다. 개념·후보 연결을 확정 오답으로 표현하지 않는다.

## 정정과 학습량

| status | 관찰 | 반영 |
|---|---|---|
| uncorrected | 혼동 이후 명확한 정정이 확인되지 않음 | 구분 기준·작은 사례·적용 |
| study_corrected | 공부 중 정정했으나 해설 참고 또는 정정 경로 불명 | 정정 사실을 인정하고 짧게 재확인 |
| self_corrected | 스스로 추론해 고친 근거가 확인됨 | 독립 자기교정으로 구별하고 재확인 |
| hesitant_application | 원리는 말하지만 적용에서 망설임 | 기준을 실제 조건에 적용 |
| name_recall | 이름이 바로 떠오르지 않음 | 명칭과 현상의 양방향 회상 |

정정한 두 상태에는 `correction.origin`과 SSTT 인용 근거가 필요하다. `independent`는 명시적으로 스스로 추론한 근거가 있을 때만 `self_corrected`와 사용한다. `solution`은 해설 참고, `unknown`은 경로 미확인으로 `study_corrected`와 사용한다. “아 맞다”나 뒤에서 정답을 말한 사실만으로 independent로 분류하지 않는다. 정정 인용도 해당 차시에 연결된 SSTT 안에서 찾아야 하며 다른 차시·차시 미확정 입력의 정정을 가져오지 않는다. 기존 발행 자료의 self_corrected 기록을 소급 수정하지 않으며 새 진단부터 이 구분을 적용한다.

설명 후 성공·최초 독립 회상·장기 기억 확인을 혼동하지 않는다. 전사 오류인지 불명확한 신호는 excluded에 이유·확인 방법을 적는다. 말더듬·욕설·무응답·발음 오류 자체로 약점이나 숙련을 확정하지 않는다. 반복 혼동과 선행 개념·적용 어려움에 따라 보완량을 정하고 문제 수로 숙련을 점수화하지 않는다.

## diagnosis.json schema 2

`inputs`는 plan.json을 그대로 복사한다. `study_packs`의 기본 목록은 `study` 출력 그대로 복사하고 `input_paths`·`match_evidence`·`reading`을 추가한다. 역할별 `reading.items`는 그 HTML의 전체 items와 같아야 한다. 전체 읽기 근거 파일은 RUN 내부에 실제로 작성한다. 경로는 저장소 상대 NFC, 해시는 실제 SHA-256을 사용한다.

```json
{
  "schema": 2,
  "inputs": [{"path": "SSTT/0910 공부.md", "sha256": "실제 해시"}],
  "review_note_search": "실제로 확인한 차시와 연결 근거",
  "study_packs": [
    {
      "folder": "복습노트/0910",
      "files": "study 명령이 반환한 files 객체 그대로",
      "missing": [],
      "review_only": [],
      "explanation_only": [],
      "suite_mismatch": false,
      "input_paths": ["SSTT/0910 공부.md"],
      "match_evidence": "SSTT의 공부 안내·고유한 지문 표현과 자료를 대조한 결과",
      "reading": {
        "note": {"items": ["실제 전체 토픽 ID"], "evidence": "work/study-reading.md"},
        "review": {"items": ["실제 전체 문항 ID"], "evidence": "work/study-reading.md"},
        "explanation": {"items": ["실제 전체 문항 ID"], "evidence": "work/study-reading.md"}
      }
    }
  ],
  "references": [{"path": "강의노트/관련장.pdf", "sha256": "실제 해시", "role": "lecture", "locations": ["PDF p5"]}],
  "weaknesses": [
    {
      "id": "w1",
      "status": "study_corrected",
      "evidence": [{"path": "SSTT/0910 공부.md", "line_start": 10, "line_end": 18, "quote": "실제 원문 인용"}],
      "later_check": "뒤쪽 발언까지 확인한 결과와 위치",
      "correction": {"origin": "unknown", "evidence": [{"path": "SSTT/0910 공부.md", "line_start": 15, "line_end": 18, "quote": "정정한 실제 발언"}]},
      "source_context": {"pack": "복습노트/0910", "match": "confirmed", "problem": "p7", "choices": ["2"], "note_topics": ["실제 원래 토픽 ID"], "explanation_sections": ["recall", "solve"]},
      "criterion": "이 혼동을 해결하는 판단 기준",
      "topic": "s0-new-concept",
      "problems": ["p1"]
    }
  ],
  "unresolved_sessions": [],
  "excluded": [{"reason": "보류·미포함 이유와 확인 방법"}]
}
```

예시의 설명용 문자열을 실제 목록·원문으로 바꾼다. 파일을 찾거나 해시를 계산한 것을 실제 독해로 보고하지 않는다. 전체 읽기 근거 파일은 조립 때 새 약점팩의 `.pack/study-reading/`에 복사하며, 완료 때 근거 파일·진단 내용이 바뀌면 재조립·검토한다. 검사기는 누락·ID·해시·근거 파일의 존재를 확인할 뿐 독해나 학습자의 현재 이해를 증명하지 못한다.

원문 인용·줄·녹음 위치는 내부 기록에 보존한다. 학생용 본문에는 혼동·정정·해설 참고 여부를 자연스럽게 요약하고 욕설·말더듬·녹음 위치는 싣지 않는다. 모든 새 문항을 보완 약점과 연결한다.
