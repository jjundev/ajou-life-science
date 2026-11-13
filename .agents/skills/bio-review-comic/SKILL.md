---
name: bio-review-comic
description: '생명과학 정리노트 HTML을 바탕으로 강의 차수별 학습만화·복습만화·4~8컷 만화를 요청하거나 /bio-review-comic 날짜 또는 HTML경로로 호출할 때 사용한다. 기존 학습만화를 정리노트에 연결하는 요청에도 사용한다. 정리노트·복습문제·영상 생성 요청에는 사용하지 않는다.'
---

# 생명과학 페이지별 학습만화

기존 정리노트의 **학습·지난 수업 복습·전체 요약 페이지마다 4~8컷**을 만든다. 학생이 애매하게 이해할 수 있는 관계를 **익숙한 비유와 캐릭터의 설명·대화**로 명확히 한다. 비유의 대응·한계를 밝히고 실제 생물 구조·조건을 보존한다. 기본은 학생＋안내자 두 명, 간단한 주제는 한 명 설명형이다. 표지·미학습 예고·자료 링크는 만화 대상에서 제외한다. 결과는 원본 순서의 페이지, 목차, 우측 요약, 이전·다음 버튼을 가진 HTML이다. 그림이 부족한 페이지는 이유와 함께 보류하며 완성으로 세지 않는다.

**입력:** `MMDD`, 기존 `MMDD-MMDD` 폴더명, 또는 정리노트 HTML 경로. 날짜 생략·주제만·`all`은 자동 추정하지 않고 사용법과 실제 후보를 안내한다. 범위 폴더명은 날짜 사이의 모든 폴더를 일괄 실행하는 명령이 아니다.

**산출물:** 원본 폴더의 `학습만화_<원본의 날짜·주제>.html` 하나와 `.assets/자료_학습만화_<날짜·주제>/`의 그림·콘티·근거·검토·이전 버전. 새 퀴즈·정답 토글·영상·음성·PDF는 만들지 않는다. 만화 제작에서 원본 노트에 추가하는 것은 관련 설명 뒤 안내와 같은 탭 링크다. 원본 교정도 요청받으면 [원본 교정 후 재개](references/source-correction.md)를 따른다. 다른 스킬 수정·커밋·푸시는 별도 요청 범위다.

## 준비와 경로

- `SKILL`은 이 파일의 실제 폴더(심볼릭 링크는 원본으로 해석), `REPO`는 저장소 루트다.
- `RUN`은 **비어 있는 새 폴더**다. 기본은 `REPO/tmp/bio-review-comic/<인자>-<실행ID>/`; 작업은 발행 때 전용 `.assets`에 보존한다. 자동화 브라우저의 HTTP 서버는 `REPO`에서 열어 원본 링크도 접근하게 한다.
- Python 3.10+를 사용한다. `browser-check`에는 [Playwright와 Chromium](references/review.md#브라우저-확인)이 필요하며 나머지 명령은 표준 라이브러리로 실행한다. 셸 호출 사이 변수 상태를 가정하지 않고 모든 경로는 실제 절대 경로로 전달한다. 경로 검색은 스크립트가 NFC/NFD를 처리한다.
- 아래 명령의 `python3 "$SKILL/scripts/comic.py"`를 사용한다. 이미지 생성은 내장 `image_gen` 도구가 담당하며 CLI는 생성 API를 호출하지 않는다.

**연결만 요청한 경우:** 새 만화를 생성하지 않는다. 기존 발행자료의 RUN/버전 폴더를 찾아 [정리노트 연결](references/note-links.md)의 검사·연결·브라우저 왕복만 수행한다. v1 자료는 v2 새 실행·검토·발행으로 전환해야 한다.

## 1. 원본 추출

```bash
python3 "$SKILL/scripts/comic.py" extract --repo "$REPO" --target "1105" --run "$RUN"
```

`source.html`은 원본 스냅샷, `source.json`은 모든 토픽의 포함·제외 사유와 페이지별 근거, `storyboard.json`은 채울 콘티다. **`source.json`과 `source.html`은 편집하지 않는다.** 후보가 여러 개면 HTML 경로를 지정하고, 없으면 가능한 날짜를 안내한다. STT로 대체 생성하지 않는다.

원본의 `main article.topic` 하나가 만화 한 페이지다. 본문 전체·원본 그림·교수님 강조·주의·보충·요약을 읽는다. `source.json`의 텍스트 근거는 글의 목록이며 원본 그림 속 사실을 대신하지 않는다. 콘티 전에 원본의 핵심 주장과 도해의 방향·개수·비교 조건을 대조한다. 오류나 모순을 발견하면 [원본 교정 후 재개](references/source-correction.md)에 따라 기록하고 해당 페이지를 보류한다.

첫 진행 보고에 대상 전체/포함/제외 수와 예상 컷 수(포함 페이지 × 4~8)를 적고 계속한다. 사용자가 전체 제작을 요청했다면 임의로 대표 페이지만 골라 끝내지 않는다.

## 2. 콘티

[콘티 기준](references/storyboard.md)과 [데이터 계약](references/contract.md)을 읽고 `storyboard.json`을 채운다. 출력은 다음 순서다.

1. [공통 그림체](references/style.md)의 플랫 일러스트 스타일을 `style`에 넣고 인물·생물 구조·과정·비유 사물에 동일하게 적용한다. `characters`에는 반복 대상의 모양/색, 인물 ID·외형·역할·말투를 정한다. `--reuse`로 가져온 이전 그림체도 현재 기준으로 갱신한 뒤 프롬프트를 만든다.
2. 각 페이지의 혼동 지점·도달할 이해(`clarification`) → 비유 대응·한계(`analogy`) → 설명형/대화형과 cast(`narrative`) → 4~8컷의 관찰 대상·행동·대사 → 근거·우측 요약을 쓴다. 화자의 질문·설명·자기수정이 핵심 추론을 이끈다. **대화 참여와 그림 출연은 별개**다. 비유 장면은 관련 사물과 작동 관계에 집중하고 화자는 화면 밖에서 말할 수 있다. 인물의 표정·행동 자체가 이해를 도울 때만 해당 컷 `characters`에 넣는다. 모든 컷을 사물 중심으로 구성해도 된다.
3. `note_link`에는 그 페이지로 이동해 무엇을 구별할지 한 문장으로 적는다. 혼동을 설명하는 기존 블록 ID가 적절하면 anchor_id로 지정한다.
4. 원본 근거 **모든 항목**에 컷 번호 또는 생략 이유를 `coverage`로 남긴다. 조건·예외·오개념 판별 기준은 생략하지 않는다. 반복·주변 사례의 생략은 설명한다.
5. 페이지가 준비되면 `ready`, 해결 불가면 이유를 적고 `held`로 표시한다. 미완료 `draft`는 검사에서 실패한다.

다른 토픽의 주장을 다시 설명하는 페이지는 해당 토픽 ID를 `source_dependencies.topics`에 기록한다. 검토에 실제로 쓰는 별도 도해·위젯 등 로컬 파일도 `source_dependencies.files`에 기록한다. 전체 요약의 범위를 좁히기 어렵다면 `topics: "all"`을 쓴다.

```bash
python3 "$SKILL/scripts/comic.py" check --run "$RUN" --phase storyboard
python3 "$SKILL/scripts/comic.py" prompts --run "$RUN"
```

검사는 근거 존재·대응과 구조를 확인한다. 설명의 의미가 옳다는 판정은 4단계에서 별도로 한다.

## 3. 그림 생성과 등록

[이미지 제작](references/images.md)과 [에이전트 작업 계약](references/agents.md)을 읽는다. **페이지당 생성 에이전트 하나**에 해당 페이지의 4~8컷을 맡긴다. 이 스킬은 생성·독립 검토의 서브에이전트 위임을 요청한다. 대화 이력 없이 시작하고, 경로·페이지 ID·작업 계약을 전달한다. 메인은 콘티·배분·순차 등록·발행을 담당하며 생성 이미지와 상세 로그는 작업 에이전트의 컨텍스트에 둔다. 실제 동시 실행 한도에서 메인 슬롯을 제외한 만큼 생성자와 검토자를 배치한다.

생성자는 `prompts.json`의 작업별 `prompt`로 **내장 이미지 생성 도구를 컷마다 호출**한다. 각각 다른 장면을 한 프롬프트의 변형 옵션으로 대신하지 않는다. 앞서 만든 대상의 외형이 중요하면 실제 이전 컷을 참조 이미지로 제공한다. 원본 텍스트를 이미지에 새기지 않고 한국어·라벨·정확한 표기는 HTML로 표시한다.

- `reusable: true`인 그림은 프롬프트와 파일 지문이 맞으므로 재사용 후보이다. 실제 장면의 적합성은 내용/그림 검토에서 확인한다.
- 생성자는 실제 로컬 파일과 컷별 결과를 전용 결과 파일에 남기고 짧은 요약만 반환한다. 메인은 경로·컷 목록·현재 프롬프트 지문을 확인한 뒤 아래 `register-image`를 **순차 실행**한다. 공유 `images.json`은 생성자가 수정하지 않는다. 파일 경로를 지어내거나 비트맵 대신 SVG·도형·빈 이미지로 채우지 않는다.
- 위임 불가·생성 도구 사용 불가·아티팩트 저장 실패면 원인과 함께 해당 페이지를 `held`로 표시한다. 메인 생성으로 조용히 전환하거나 별도 유료 API/키를 자동으로 사용하지 않는다.

```bash
python3 "$SKILL/scripts/comic.py" register-image --run "$RUN" --page s0-miller --panel 1 --image "/실제/생성결과.png"
python3 "$SKILL/scripts/comic.py" check --run "$RUN" --phase images
python3 "$SKILL/scripts/comic.py" build --run "$RUN"
```

도구가 이미지를 인라인으로만 반환하면 지원되는 저장 경로를 확인한다. 파일을 확보할 수 없으면 해당 페이지 보류와 원인을 보고한다. 생성 실패 시 페이지당 수정 시도는 한 번으로 묶고, 계속 실패하면 다른 페이지를 진행한다.

## 4. 내용과 그림 검토

[검토 기준](references/review.md)을 읽는다. 재실행은 [이전 판정 대조](#재실행원본-변경)를 먼저 한다. 새 검토가 필요한 페이지에는 생성자와 다른 독립 검토 에이전트를 배정한다. 검토자는 원본·콘티의 내용과 **모든 실제 그림**의 구조·방향·개수·의미를 확인한다. 검토자도 대화 이력 없이 시작하며 생성자의 자기평가를 정답으로 전달하지 않는다. 관찰·판정은 전용 보고서에 남기고 메인에는 판정·수정할 컷·보고서 경로만 반환한다. 검토자 확보 불가 시 해당 페이지는 보류한다.

```bash
python3 "$SKILL/scripts/comic.py" fingerprints --run "$RUN" --page "$PAGE"
python3 "$SKILL/scripts/comic.py" record-review --run "$RUN" --report "$RUN/workers/$PAGE/review.json"
python3 "$SKILL/scripts/comic.py" check --run "$RUN" --phase reviewed
```

메인은 보고서의 실제 관찰과 독립 검토자 여부를 확인한 뒤 `record-review`를 순차 실행한다. CLI는 이미 수행된 검토를 확인하고 최초 보고서를 보존한다. 전체 이미지를 메인에서 다시 열지 않고, 검토자가 지적한 문제나 판정 충돌이 있는 컷을 확인한다. 대사만 바뀌어도 내용과 그림 검토 지문이 바뀐다. 장면·스타일·그림 의미가 달라져 프롬프트가 바뀐 그림은 현행 그림 검사를 따른다.

## 5. 브라우저

`browser-check --stage preview`로 **1440×900·375×812 각각 라이트·다크**에서 모든 준비 완료 페이지와 원본 이동·뒤로가기를 확인한다. `--out`은 비어 있는 증거 폴더다. 말풍선이 실제 그림의 핵심 사물을 가리는지, 화자와 읽는 순서가 자연스러운지는 직접 확인한다. 세부 검사와 기록 형식은 [검토 기준](references/review.md)을 따른다.

아래 첫 명령은 자동 검사 보고서와 `RUN/browser-preview.json`을 기록한다. 새 RUN의 `publish`는 현재 입력과 4종 증거가 일치할 때만 HTML을 교체한다. 자동 검사 결과와 직접 관찰을 확인한 뒤 현재 브라우저 지문, 4종 스크린샷 상대 경로와 확인 내용을 `review.json`에 기록한다. 변경 후 재검사는 비어 있는 다른 `--out` 폴더를 사용한다. 기존 RUN·발행본은 작성 당시 계약으로 읽는다.

```bash
python3 "$SKILL/scripts/comic.py" browser-check --run "$RUN" --stage preview --out "$RUN/checks/preview"
python3 "$SKILL/scripts/comic.py" check --run "$RUN" --phase browser
python3 "$SKILL/scripts/comic.py" publish --run "$RUN"
```

발행은 검증된 결과를 **로컬 파일**로 저장한다. 기존 HTML은 새 버전의 `previous.html`로 보존하고, 이미지·제작자료와 `review-evidence/`의 최초 독립 검토 보고서를 고유 버전 폴더에 둔다. `prompts.json`과 `workers/`의 작업 기록은 메인이 실제 `version` 폴더에 상대 경로를 유지해 추가 보존한다. 같은 결과를 재실행하면 중복 버전을 만들지 않는다. 발행 뒤 [정리노트 연결](references/note-links.md)대로 원본에 안내·링크를 자동 추가한다. 연결 실패는 발행 결과와 구분하고 `link-notes --run "$RUN"`으로 재시도한다. `publish --no-link`는 발행만 할 때 쓴다. 성공/보류 수는 `publish` 출력에 따른다. 전부 보류라면 빈 제작물을 발행하지 말고 원인과 실행 폴더만 보고한다.

발행과 연결 후에는 최종 정리노트의 안내 문맥을 읽고 별도 명령인 `browser-check --stage published`로 왕복을 확인한다. `link-status`가 `passed`일 때 연결 완료로 보고한다. 실패하면 발행본을 보존한 채 [원본 연결 복구](references/note-links.md#왕복-실패-복구)를 따른다. 의도적으로 `publish --no-link`를 썼으면 최종 검사에 `--comic-only`를 추가한다.

```bash
python3 "$SKILL/scripts/comic.py" browser-check --run "$RUN" --stage published --out "$RUN/checks/published"
python3 "$SKILL/scripts/comic.py" link-status --run "$RUN"
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN" --dry-run
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN"
```

**명시적 한 페이지 샘플:** 사용자가 일부만 요청했거나 스킬의 실제 제작 검증을 할 때 `extract --page 토픽ID`로 범위를 명시한다. 파일명에 `_샘플_토픽ID`를 붙이며 차수 전체 완료로 보고하지 않는다. 전체 요청을 임의의 샘플로 축소하지 않는다.

## 재실행·원본 변경

원본을 교정한 경우 [교정 검증](references/source-correction.md#3-검증과-재개)을 마치고 아래 명령으로 재개한다.

```bash
python3 "$SKILL/scripts/comic.py" extract --repo "$REPO" --target "1105" --run "$NEW_RUN" --reuse "$PREVIOUS_RUN"
python3 "$SKILL/scripts/comic.py" reuse-reviews --from "$PREVIOUS_RUN" --run "$NEW_RUN" --dry-run
python3 "$SKILL/scripts/comic.py" reuse-reviews --from "$PREVIOUS_RUN" --run "$NEW_RUN"
```

검증된 만화 참조 블록만 제외한 원본 내용이 달라지면 기존 RUN은 발행할 수 없다. 참조 블록은 근거·토픽 지문에서도 제외하고 실제 바이트 스냅샷은 보존한다. 관리 블록의 형식/지문이 손상되면 멈춘다. 일반 본문·그림·링크 변경은 무시하지 않는다. `extract --reuse`는 같은 토픽의 콘티와 프롬프트·파일 지문이 맞는 그림을 가져온다. `reuse-reviews`는 별도로 페이지별 판정을 대조한다. 이전 RUN 또는 발행 버전 폴더를 두 명령의 입력으로 쓸 수 있다. 검토와 브라우저 검사 진행은 [승계 결과 해석](references/review.md#이전-독립-검토-승계)을 따른다.

## 디자인 유지

`assets/comic-template.html`은 `bio-review-pack/assets/note-template.html`에서 파생했다. 원본 색상·서체·간격·좌우 패널·표지·페이지 이동을 유지하고 `comic.css`는 만화 본문만 확장한다. 테마 키는 공유하고 읽음 키는 `od-comic-read:`로 분리한다. 원본 요약을 무조건 복사하지 않고 만화의 핵심·조건·구분을 요약하되 원본 근거로 검토한다. 그림은 밝은 종이 배경을 유지하며 다크 모드에서 반전하지 않는다.

템플릿을 갱신할 때 `template-provenance.json`의 원본·지문을 확인하고, 최신 원본을 복사한 뒤 읽음 키만 분리한다. 새 퀴즈나 위젯을 추가하지 않는다. 파생본과 CSS 변경 후 테스트와 브라우저 검사를 다시 실행한다.

## 마지막 보고

- 상태: `완료 N/N페이지` 또는 `일부 완료 N/N페이지, 보류 ID와 이유`. 원본 충실성 검토와 기계 검사를 구별한다.
- 최종 HTML, 그림·제작자료 폴더, 원본 연결, 실행 폴더의 실제 경로.
- 혼동 지점·사용한 비유·한계·설명형/대화형. 정리노트 연결 added/updated/unchanged/skipped와 이유, 실패 시 재시도 방법.
- 포함·제외 페이지 수, 실제 컷 수, 재사용/신규 그림 수.
- 내용·그림 검토에서 고친 내용, 생략한 주변 내용, 남은 불확실성.
- 데스크톱·모바일 및 라이트·다크 확인 결과와 제약.

`status: partial`을 전체 완료로 보고하지 않는다. 구조·내용·그림·브라우저 검토가 모두 통과하고 보류가 없을 때만 차수 전체 완료다.
