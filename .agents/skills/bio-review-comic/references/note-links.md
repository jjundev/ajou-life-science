# 정리노트에서 만화로 연결

## 자동 연결과 연결만 재실행

`publish`는 검토를 통과한 실제 만화를 먼저 발행한 뒤 원본에 관련 안내를 연결한다. `--no-link`는 발행만 한다. 연결이 실패해도 만화는 남긴다.

```bash
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN" --dry-run
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN"
```

기존 만화 연결만 요청하면 발행 버전 폴더(또는 원래 RUN)를 사용한다. 그림을 새로 생성하지 않는다. v1 자료는 v2 새 실행·검토·발행 후 연결한다. 발행 파일이 변경되었거나 현재 콘티/검토와 다르면 연결하지 않는다.

## 위치와 안내

`note_link`의 before + 링크 label + after는 **무엇을 구별하고 이해할지** 말하는 한 문장이다. 대상은 원본 토픽 ID와 같은 만화 페이지다. 상대 경로를 URL 인코딩하고 `#토픽ID`, `target="_self"`를 쓴다.

기본 위치는 토픽 안 첫 `.layer.formal` 뒤, 없으면 `.layer.eli5` 뒤, 없으면 제목 뒤다. 혼동을 설명하는 블록이 더 적절하면 기존 고유 ID를 `anchor_id`로 지정한다. `div`, `figure`, `section`, 제목, 표, 목록, blockquote 같은 닫힌 HTML 블록만 가능하다. SVG 내부, p/span/a 안에는 삽입하지 않는다. 없는/중복된 블록·목적지 ID는 건너뛰고 이유를 보고한다.

관리 안내는 `data-bio-comic`와 payload 지문을 가진 주석 경계로 식별한다. 같은 원본 토픽에서 같은 발행 파일을 가리키는 관리 블록 하나를 찾아 필요한 문구와 해시를 갱신한다. 후보가 여러 개면 해당 토픽을 건너뛰고 `REFERENCE_AMBIGUOUS`를 보고한다. 손으로 작성한 기존 링크와 다른 발행 파일의 안내는 보존한다.

## 원본 보존과 재실행

관리 블록을 제거하면 삽입 전 원본 바이트가 그대로 남아야 한다. 저장은 임시 파일과 원자적 교체로 수행하며, 직전 원본 재검사로 작업 중 변경을 감지한다. `--dry-run`은 파일·결과 기록을 변경하지 않는다.

원본 지문에서는 **정해진 형식과 payload 지문이 맞는 만화 참조 블록만** 제외한다. 링크 안내가 새 근거로 추출되거나 원본 변경으로 잘못 판정되지 않는다. 본문·그림·일반 링크·스크립트 변경은 여전히 변경으로 처리한다. 관리 블록이 손상되면 무시하지 않고 멈춘다.

결과는 note, changed, dry_run, results(page/status/reason/href)다. status는 added/updated/unchanged/skipped. held 페이지는 PAGE_HELD로 새 연결을 건너뛴다. 연결 실패는 `link-notes`로 다시 시도하며 재실행 결과 `changed: false`를 확인한다. 잘못된 위치에 대체 삽입하지 않는다.

최종 노트에서 안내 문맥을 읽고 [`browser-check --stage published`](review.md#브라우저-확인)로 원본 안내 링크 → 만화의 해당 페이지 → 만화의 원본 링크를 같은 탭에서 확인한다. 만화의 성공/보류와 연결의 성공/누락/실패를 따로 보고한다.

## 왕복 실패 복구

발행 버전의 `link-verification.json`은 삽입이나 링크 수정 뒤 `pending`, 4종 왕복 통과 시 `passed`, 삽입이나 검사 실패 시 `failed`를 기록한다. `publish --no-link`는 `skipped`를 기록한다. `link-status`는 통과 뒤 원본·만화·그림·로컬 자원이나 증거가 달라졌으면 `pending`을 반환한다. 기록이 없는 이전 발행본은 `unverified`다. 최종 검사를 실행하면 이전 발행본에도 결과를 남길 수 있다.

삽입이 누락되면 일반 `link-notes`로 재시도한다. 이미 발행한 만화의 유효한 관리 링크에서 토픽 해시만 잘못됐으면 다음 순서로 복구한다.

```bash
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN_OR_VERSION" --repair-fragments --dry-run
python3 "$SKILL/scripts/comic.py" link-notes --run "$RUN_OR_VERSION" --repair-fragments
python3 "$SKILL/scripts/comic.py" browser-check --run "$RUN_OR_VERSION" --stage published --out "$NEW_CHECKS"
```

`--repair-fragments`는 발행 HTML과 그림의 지문을 확인한 뒤 같은 토픽에 있는 관리 블록 하나의 해시를 복구한다. 발행 후 원본 본문이 교정됐어도 관리 안내 문구와 원본 본문은 보존한다. 관리 블록 지문이 손상됐거나 후보가 모호하면 위치와 원인을 확인한 뒤 유효한 관리 블록으로 복구한다. 그림이나 발행 HTML의 지문이 맞지 않으면 발행본 상태부터 확인한다.
