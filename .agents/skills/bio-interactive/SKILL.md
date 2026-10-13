---
name: bio-interactive
description: '생명과학 복습노트 날짜(MMDD)나 주제로 DNA 3D 모형과 같은 디자인의 인터렉티브 HTML(인터렉티브_NN.html)을 만든다. "인터렉티브", "인터랙티브", "3D 모형", "움직이는 자료", /bio-interactive [MMDD|주제]에 사용한다. 정리노트·복습문제 생성(bio-review-pack)에는 사용하지 않는다.'
---

# 생명과학 인터렉티브 자료

날짜나 주제 하나로 「DNA 구조와 복제 3D」(`복습노트/1001/3D모형_1001_DNA_Structure_and_Replication.html`)와 같은 화면의 인터렉티브 자료를 만든다. 공통 셸 템플릿에 주제별 장면과 문구만 채우고, 검사·내용 검토·브라우저 확인을 통과한 것만 저장한다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**인자**: `[MMDD | 주제]`
- 날짜: 그날 수업에서 인터렉티브로 만들 주제를 스스로 골라 **2–4개** 만든다.
- 주제(예: `오페론`, `세포 호흡`): 그 주제 **1개**를 만든다.

**산출물** (`DEST` 폴더, 번호 `NN`은 두 자리):
- `인터렉티브_NN.html` — 브라우저에서 바로 여는 단독 파일
- `자료_인터렉티브_NN/` — 원본 `Main.dc.html`과 `canvas.json`(나중에 Design 캔버스로 올릴 때 쓰는 매니페스트)

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/8 작성 중: 주제 3개 (병렬)`

**서브에이전트가 없는 환경(Codex 등)**: 병렬 에이전트 대신 같은 브리프로 주제를 차례로 직접 쓰고, 5단계 내용 검토는 새 세션에서 한다. 모델 지정은 Claude에서는 그대로, 다른 모델 환경에서는 opus→sol로 바꿔 읽는다.

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-interactive`)의 절대 경로. `.claude/skills/bio-interactive`는 이 폴더를 가리키는 심볼릭 링크다. 링크 경로가 아니라 원본 경로로 푼다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/bio-interactive/<인자>/` (scratchpad가 없으면 `/tmp/bio-interactive/<인자>/`). 주제마다 `RUN/<n>/`(n = 1, 2, …).
- `DEST` = 1단계 `resolve.cjs` 출력의 `folder`
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. `$SKILL`, `$RUN`, `$REPO`, `$DEST`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나 같은 Bash 호출 맨 앞에 세미콜론으로 먼저 설정한다(`SKILL=…; RUN=…; node "$SKILL/scripts/check.cjs" …`). `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.
- 파일명은 macOS에서 NFD로 저장된다. 경로를 손으로 짓지 말고 `resolve.cjs`가 돌려준 경로를 쓴다.

**하지 않는 것**: 기준 결과물(`복습노트/1001/자료_3D모형_1001_DNA_Structure_and_Replication/`)과 정리노트·복습문제 수정, 기존 `인터렉티브_*`·`3D모형_*` 덮어쓰기, Design 캔버스 게시, 커밋.

## 절차

### 0. 준비
`REPO`에 `복습노트/`, `STT/`, `강의노트/`, `교과서/생명과학_기초와_응용_2판/`이 있는지 확인한다. 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다. `node -v`가 20 이상인지 확인한다.

### 1. 대상 풀기
```bash
SKILL=…; REPO=…; RUN=…; mkdir -p "$RUN" && node "$SKILL/scripts/resolve.cjs" "$REPO" "<인자>" | tee "$RUN/target.json"
```
- 인자 `MMDD-MMDD`는 그 이름의 범위 폴더가 있을 때만 날짜로 쓴다(없으면 `NO_TARGET`).
- 출력: `kind`(date|topic), `folder`(= `DEST`), `exists`, `date`, `notes`(정리노트 `.md`), `stt`, `existing`(같은 폴더 `인터렉티브_*`·`3D모형_*`와 `<title>`), `next`(다음 번호).
- 날짜가 `0922-0924` 같은 범위 폴더 안이면 그 폴더가 나온다. 폴더는 없고 STT만 있으면 `exists: false`로 새 폴더 자리가 나온다.
- 주제는 정리노트 본문(링크 글자 제외)에서 찾고, H2·H3 제목에 나온 폴더를 먼저, 그다음 가장 최근 폴더를 고른다. 어느 정리노트에도 없으면 `복습노트/주제별/`이 나온다(교과서·강의노트로 만든다).
- `{"error":"NO_TARGET"}` → 「대상 없음: <인자>의 복습노트 폴더와 STT가 없어요」라고 보고하고 멈춘다. `NO_ARG` → 사용법을 보여 주고 멈춘다.

### 2. 주제 고르기
`references/topic-selection.md`대로 한다.
- 날짜: `notes`의 H2·H3와 「직접 해 보기」 블록으로 후보를 만들고 점수를 매긴다. `notes`가 비었으면 `stt`와 그 장의 `강의노트/N장 *.pdf`로 후보를 만든다. `existing` 제목과 겹치는 후보는 뺀다. 개수는 2–4개.
- 주제: 인자 그대로 1개. 정리노트에서 그 주제가 나온 절을 근거로 쓴다.
- 후보가 0개면 「후보 없음」과 이유를 보고하고 멈춘다.
- 주제마다 브리프를 `RUN/<n>/brief.md`에 쓴다(항목은 `references/topic-selection.md`).

### 3. 작성 (주제당 opus 에이전트 1명, 한 메시지에서 병렬)
먼저 주제마다 템플릿을 복사한다.
```bash
SKILL=…; RUN=…; for n in 1 2; do mkdir -p "$RUN/$n" && cp "$SKILL/assets/template.dc.html" "$RUN/$n/Main.dc.html"; done
```
각 작성자에게 넘길 것:
- 고칠 파일 `RUN/<n>/Main.dc.html`(이 파일만 고친다)과 브리프 `RUN/<n>/brief.md`
- 계약 `references/scene-api.md`, 디자인 규칙 `references/design.md`
- 품질 기준 예시 `references/example-dna.dc.html` — 장면을 실제 구조(개수·방향·비율)로 모델링하는 방식, 단계·꼭 기억해요·출처 문구의 밀도를 본다. 이 예시는 예전 형식(`tabS` 등)이라 셸 부분은 따라 하지 않는다.
- 근거 자료: `notes`, `stt`, 해당 장의 `강의노트/N장 *.pdf`, `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`
- 지시: 수업에서 다룬 내용만 쓰고, 교과서에서 보충한 것은 패널 문구에 「(교과서 보충)」으로 표시한다. 단순화한 것(개수·속도·위치)은 `__SOURCE__` 자리 출처 한 줄에 적는다. 끝내기 전에 `node "$SKILL/scripts/check.cjs" "$RUN/<n>/Main.dc.html"`이 `ok`를 내야 한다.
- 돌려받을 것: 제목, 모드·단계 목록, 단순화한 것, 확신 없는 사실.

### 4. 검사
```bash
SKILL=…; RUN=…; for n in 1 2; do echo "== $n"; node "$SKILL/scripts/check.cjs" "$RUN/$n/Main.dc.html"; done
```
모두 `ok`여야 한다. 오류(`SHELL_MISSING`, `HOLE_UNKNOWN`, `HOLE_SYNTAX`, `EVENT_UNSUPPORTED`, `HEX_IN_MARKUP`, `TOPIC_INVALID`, `RENDER_THROWS`, `DRAW_THROWS`, `SCENE_EMPTY`, `SCENE_NAN`, `TEMPLATE_LEFT`)는 출력 줄 그대로(예외 문장이 `—` 뒤에 붙어 있다) 그 작성자에게 한 번 돌려보내 고친다. 그래도 남으면 그 주제는 「보류」.

### 5. 내용 검토 (별도 opus 에이전트, 주제마다 1명, 병렬)
작성자가 아닌 새 에이전트에게 `Main.dc.html`, 브리프, 근거 자료를 주고 다음을 대조하게 한다.
- 패널 문구·단계·꼭 기억해요·출처가 정리노트·교과서와 맞는지(용어, 방향 5′→3′ 같은 사실, 효소·분자 이름)
- 장면 모델이 사실과 맞는지(개수, 순서, 방향, 상대 크기, 무엇이 무엇에 붙는지)
- 수업 밖 내용에 「(교과서 보충)」 표시가 있는지
Critical·Important는 그 작성자에게 한 번에 모아 돌려보내 고치고 4단계를 다시 한다. 수정은 한 번만 한다. 남으면 「보류」.

### 6. 브라우저 확인
통과한 주제를 `RUN`에 빌드하고 `RUN`을 http.server로 띄워 내장 브라우저로 연다.
```bash
SKILL=…; RUN=…; for n in 1 2; do node "$SKILL/scripts/build.cjs" "$RUN/$n/Main.dc.html" "$RUN/$n/preview.html"; done
```
주제마다 1440×900과 375×812에서 각각 라이트·다크로 확인한다.
- 콘솔 오류 0, 375px에서 가로 스크롤 없음
- 모드 전환, 재생·일시정지·스크럽·속도(재생 모드), 단계 누르기
- 패널 열고 닫기(375px는 서랍, Escape로 닫힘), 넓은 화면 패널 너비 조절
- 회전 모드에서 끌어서 회전, 확대·축소·시점 처음으로
- 캔버스 라벨이 겹치거나 화면 밖으로 잘리지 않음, 다크에서 색이 묻히지 않음
고친 것이 있으면 4단계부터 다시 한다(한 번). 그래도 문제가 남으면 「보류」.

### 7. 저장
통과한 주제를 점수 순으로 `next`부터 번호를 붙여 저장한다. 덮어쓰지 않도록 `mkdir`(-p 없이)과 존재 검사로 막는다.
```bash
SKILL=…; RUN=…; DEST=…; NN=01; n=1; mkdir -p "$DEST" && [ ! -e "$DEST/인터렉티브_$NN.html" ] && mkdir "$DEST/자료_인터렉티브_$NN" && cp "$RUN/$n/Main.dc.html" "$DEST/자료_인터렉티브_$NN/Main.dc.html" && node "$SKILL/scripts/build.cjs" "$DEST/자료_인터렉티브_$NN/Main.dc.html" "$DEST/인터렉티브_$NN.html"
```
`build.cjs`가 `자료_인터렉티브_NN/canvas.json`도 함께 만든다. 저장한 `인터렉티브_NN.html`을 내장 브라우저로 한 번 열어 콘솔 오류가 없는지만 다시 본다.

### 8. 보고
```
## 인터렉티브 <인자> 완료
- 파일: <DEST 상대 경로>/인터렉티브_NN.html — <제목> (모드: …, 단계 N개)
- 고른 이유: <주제> <점수>점 (과정 +2, 공간 구조 +2, …) · 뺀 후보와 이유
- 보류: <주제> — <어느 단계에서 무엇 때문에> (없으면 "없음")
- 단순화·교과서 보충: …
- 검토에서 고친 것: …
- 실행 폴더: RUN 경로
- 커밋 제안: git add "<DEST>/인터렉티브_NN.html" "<DEST>/자료_인터렉티브_NN" && git commit -m "docs(notes): add <MMDD> interactives"
```

## 실패 처리
| 상황 | 처리 |
|---|---|
| `NO_TARGET` | 「대상 없음」 보고 후 멈춤 |
| 후보 0개 | 「후보 없음」과 이유 보고 후 멈춤 |
| 검사·내용 검토·브라우저 확인 실패(수정 1회 후에도) | 그 주제만 저장하지 않고 「보류」, 나머지는 계속 |
| 모든 주제 보류 | 파일 없이 보고만 |
| 번호 자리에 이미 파일이 있음 | 다음 빈 번호로 넘긴다(덮어쓰지 않음) |

## 템플릿 고치기
셸(패널·테마·재생 바·그리기)을 바꿔야 하면 `assets/template.dc.html`을 고치고 `references/scene-api.md`를 맞춘 뒤 테스트를 돌린다.
```bash
node --test .agents/skills/bio-interactive/tests/*.test.cjs
```
템플릿 자체를 미리 보려면 `RUN`에 빌드한다(`build.cjs`는 원본 폴더에 `canvas.json`이 없으면 만들므로 `assets`에 생기면 지운다).
