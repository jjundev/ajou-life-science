# 실행 데이터 계약 v2

## 파일과 원본 지문

- `source.html`: 추출 당시 원본 바이트 스냅샷. 편집 금지.
- `source.json`: 원본 경로, `sha256`(스냅샷 실제 바이트), `content_sha256`(검증된 만화 참조 블록만 제외한 원본), 토픽·근거·포함/제외 목록. 새 추출에는 `review_version: 1`이 기록된다. 편집 금지.
- `selection`: 기본 `[]`(전체 포함 페이지). 명시적 `extract --page ID` 샘플만 `[ID]`. 범위 밖은 보류가 아니라 제작 범위 제외다.
- `storyboard.json`: 작성할 콘티. 원본과 동일한 `source_sha256`, `schema_version: 2`.
- `prompts.json`, `images.json`: 프롬프트와 실제 등록 이미지 지문. `reusable`은 실제 검토를 대신하지 않는다.
- `review.json`, `review-evidence/`, `checks/`: 내용·그림·브라우저 판정, 최초 독립 검토 보고서, 화면 증거. 새 계약의 페이지 기록은 `inputs`와 `origin`(`kind`, `report`, `sha256`)을 포함한다. 이전 계약의 발행 버전은 기존 기록 형식으로 확인할 수 있다.
- `preview.html`, `publication.json`: 미리보기와 발행 결과.
- `note-links-result.json`: 원본 연결 결과. 실패해도 발행한 만화를 삭제하지 않는다.
- `browser_gate_version: 1`: 새 추출의 발행 조건. RUN의 `browser-preview.json`은 미리보기 보고서 경로와 지문을 기록한다. 발행 시 보고서와 4종 화면을 버전의 `checks/automatic-preview/`에 보존한다. 필드가 없는 RUN은 기존 발행 계약을 적용한다.
- `link-verification.json`: 발행 버전의 연결 상태. 최종 보고서와 화면 증거는 해당 버전의 `checks/published/`에 보존한다.

v1 실행은 직접 수정·발행하지 않고 새 RUN에서 `extract --reuse 이전RUN`으로 전환한다. v1 콘티는 새 필수 정보가 없어 자동으로 ready가 되지 않는다. 기존 발행자료는 그대로 보존한다.

## 콘티 공통

`title`, `style`, `pages` 외에 `characters`를 둔다.

```json
{"characters":[
  {"id":"student","name":"학생","role":"질문과 자기수정","appearance":"노란 후드, 검은 단발","voice":"구체적인 질문"},
  {"id":"guide","name":"안내자","role":"관계와 한계 설명","appearance":"남색 조끼, 둥근 안경","voice":"차분한 설명"}
]}
```

한 차수 안에서 외형·역할·말투를 유지한다. 실제 이미지의 캐릭터 외형도 이 정의와 대조한다.

## 페이지

원본 포함 토픽마다 같은 `id`, `source_topic_sha256`, 원본 순서의 페이지 하나를 둔다.

- `status`: `draft`(검사 실패), `ready`(콘티 준비), `held`(보류). 보류에는 `reason` 필수. ready는 검토·그림 완료가 아니다.
- `title`, `question`: 페이지 제목과 핵심 질문.
- `clarification`: `confusion`(혼동할 수 있는 관계), `understanding`(도달할 이해), `evidence`(원본 ID 목록).
- `analogy`: 아래 필드 전부 필요. 익숙한 장면 자체는 설명 도구이며, 원본에 없는 과학적 주장을 근거처럼 만들지 않는다.
  - `familiar`: 익숙한 상황.
  - `mapping`: `[{familiar, biology, evidence}]` 비유 대상과 생물학적 관계의 대응.
  - `limit`: 비유가 설명하지 못하는 부분과 잘못된 추론 방지.
  - `panels`: 비유를 설명하는 1부터 시작하는 컷 번호 목록.
  - `limit_panel`: 한계를 독자에게 보여 주는 컷 번호. 조립기는 해당 컷에 한계를 표시한다.
- `narrative`: `{mode: "explanation"|"dialogue", cast: [캐릭터ID]}`. 설명형은 한 명, 대화형은 두 명 이상. 전원이 페이지에서 발언해야 한다. cast는 화자 목록이며 그림 출연 의무가 아니다.
- `summary`: `{text,evidence}`. 핵심 관계·조건을 독립적으로 이해할 수 있게 작성.
- `source_dependencies`: `{topics: [다른 원본 토픽 ID] 또는 "all", files: [저장소 루트 기준 상대 경로]}`. 요약·용어·대사·그림의 실제 근거를 적는다. 다른 토픽을 쓰지 않으면 `topics: []`, 별도 파일이 없으면 `files: []`를 명시한다. 필드 자체가 없으면 관련 토픽 범위를 확인할 수 없어 원본 전체를 비교한다. 파일은 읽은 바이트로 확인한다.
- `terms`: `[{term,text,evidence}]`, 필요 없으면 `[]`.
- `panels`: 4~8개. 각 컷에 `scene`, `caption`, `alt`, `evidence`, `characters`, `dialogue`.
  - `characters`: 그림에 실제 보이는 캐릭터 ID 목록. 사물 중심·확대·관찰 컷은 `[]`로 쓴다. 페이지 전체가 `[]`여도 된다. 이 경우 사람·얼굴·손·의인화한 사물을 생성하지 않는다.
  - `dialogue`: `[{speaker: 캐릭터ID, text: 대사}]`. 세부 관찰 컷은 `[]` 가능하나 페이지의 핵심 추론은 대사로 전달한다.
  - 화자는 페이지 cast에 등록되어야 한다. 그림 밖에서 말하는 등록 화자는 허용한다. 말풍선은 컷 내부 위쪽에서 DOM 순서대로 읽고 cast 순서에 따른 좌우 위치와 이름으로 구별한다. 화면 밖 화자의 꼬리는 컷 가장자리를 향하며 사물이 말하는 것처럼 연결하지 않는다.
- `coverage`: 원본 근거마다 정확히 한 번 `{evidence: ID, panels: [컷번호], reason: ""}`. 생략은 빈 panels와 구체적 reason. 독자에게 표시하는 비유 대응의 근거는 생략 처리할 수 없다. 대응별 보충 배지를 표시한다. 컷의 evidence와 실제 대응해야 한다.
- `note_link`: `{before,label,after,anchor_id?}`. 일반 텍스트를 이스케이프해 관련 설명 뒤에 한 문장을 삽입한다. `anchor_id`는 원본 토픽 안의 기존 닫힌 컨테이너 ID만 지정한다. 원본에 새 ID를 만들지 않는다.

독자에게 근거 ID·제작 해시·검토 이력을 노출하지 않는다. 범위·가설·보충 표시는 유지한다.

## 검사 단계

| 단계 | 기계적으로 검사하는 것 | 별도 판단 |
|---|---|---|
| storyboard | 지문·페이지 대응·4~8컷·근거·비유 필드·출연 목록/등록 화자 발언 | 비유의 타당성, 대화가 이해를 이끄는지 |
| images | 위 + 실제 래스터·파일/프롬프트 지문 | 이미지 디코딩·정확성·일관성 |
| reviewed | 위 + 현재 내용/그림 지문의 실제 검토 기록 | 실제 검토 수행 여부 |
| browser | 위 + 4종 화면 증거·현재 브라우저 지문 | 읽기·이동·원본 왕복 |

기계 검사를 의미 검토로 보고하지 않는다. `partial`은 페이지 보류가 있다는 뜻이다. 만화 완료와 정리노트 연결 결과도 구분한다.
