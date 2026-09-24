---
name: bio-review-pack
description: 생명과학 수업의 STT·강의노트·교과서와 23·24 기출·웹과제로 ELI5 정리노트 HTML과 객관식 복습문제 HTML(+MD, 그림)을 만들어 복습노트/<날짜>/ 폴더에 저장한다. "정리노트", "복습문제", "복습팩", "0922 강의 듣고 왔어", "0922~0924 정리해줘"처럼 생명과학 수업 정리를 요청하거나 /bio-review-pack [MMDD|MMDD-MMDD] [lite]로 부를 때 사용한다.
---

# 생명과학 복습팩

수업 녹음 전사(STT)와 강의노트, 교과서, 기출·웹과제로 한 기간의 복습팩을 만든다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**산출물** (`복습노트/<range>/`, 기간(range)마다 폴더 하나):
`정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, 같은 이름의 `.md` 두 개, `figures_<range>/`

**인자**: `[MMDD | MMDD-MMDD] [lite]`
- `lite`: 작성자·요약 에이전트를 sonnet으로 하고, 6단계의 일반 리뷰를 생략한다. 블라인드 풀이 검사, 기계 검사, 브라우저 검사는 그대로 한다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 5개 + 카드 23개 (병렬)`

**서브에이전트가 없는 환경(Codex 등)**: 병렬 에이전트 대신 같은 브리프로 요약·섹션·카드를 차례로 직접 쓴다. 6단계 블라인드 검사는 새 세션에서 블라인드 사본과 정리노트만 열어 수행한다. 모델 지정(opus/sonnet)은 Claude에서만 따른다.

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-review-pack`)의 절대 경로. `.claude/skills/bio-review-pack/SKILL.md`는 이 파일을 가리키는 진입점일 뿐이다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/review-pack/<range>/` (scratchpad가 없으면 `/tmp/bio-review-pack/<range>/`)
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 셸 명령의 `$SKILL`, `$RUN`, `$REPO`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 Bash 호출 맨 앞에 세미콜론으로 먼저 설정한다(`SKILL=…; RUN=…; REPO=…; python3 "$SKILL/scripts/…" …`). `RUN=… mkdir "$RUN"`처럼 같은 명령 앞에 붙이는 형식은 쓰지 않는다. 셸이 인자의 `"$RUN"`을 그 설정보다 먼저 펼쳐 빈 경로가 되기 때문이다. `os.environ`으로 값을 읽는 파이썬 heredoc 스니펫(`REPO=… python3 - <<'EOF'` 형식)만 앞에 붙이는 형식을 그대로 쓴다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.
- 장 번호 `N`은 `강의노트/N장 *.pdf`, `23, 24 소스/N강 합본.pdf`(파일명에 `+`가 섞여 있다), `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`(두 자리), `웹과제/N장/`에서 같은 수를 쓴다.

## 절차

### 0. 준비
1. `REPO`에 `STT/`, `강의노트/`, `23, 24 소스/`, `교과서/생명과학_기초와_응용_2판/`이 모두 있는지 확인한다. 하나라도 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. STT 날짜와 마지막으로 정리한 날짜를 NFC로 읽는다. 예전 형식 `정리노트/MMDD.md`와 새 형식 `복습노트/*/정리노트_<range>_*.html`(끝 날짜)를 모두 본다.
```bash
REPO=… python3 - <<'EOF'
import os, re, unicodedata as u
repo = os.environ["REPO"]
def ls(*parts):
    d = os.path.join(repo, *parts)
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
stt = sorted(m.group(1) for n in ls("STT") if (m := re.fullmatch(r"(\d{4})[ _]생명\.md", n)))
done = [m.group(1) for n in ls("정리노트") if (m := re.fullmatch(r"(\d{4})\.md", n))]
for folder in ls("복습노트").values():
    if os.path.isdir(folder):
        for n in os.listdir(folder):
            if (m := re.match(r"정리노트_(?:\d{4}-)?(\d{4})_", u.normalize("NFC", n))):
                done.append(m.group(1))
last = max(done, default="0000")
print("STT:", *stt)
print("마지막 정리:", last)
print("다음:", *[d for d in stt if d > last])
EOF
```
3. 기간을 정한다.
   - 인자가 있으면 그 기간을 쓴다.
   - 인자가 없으면 위 출력의 `다음:` 날짜를 모두 쓴다.
   - 해당 STT가 하나도 없으면 사용 가능한 날짜(`STT:`)를 보여 주고 멈춘다.
   - `range`는 첫 STT 날짜 하나이거나 `첫-끝` 형식이다.
4. 실행 폴더를 만든다. 서브에이전트에게는 `RUN`, `RUN/repo`, `SKILL` 경로만 넘긴다.
   ```bash
   mkdir -p "$RUN"/{summaries,sections,cards,figures,work} && ln -sfn "$REPO" "$RUN/repo"
   ```
   에이전트는 `RUN` 밖에 쓰지 않는다. 임시·보조 파일은 `RUN/work/`에만 둔다. 저장소(`STT/`, `강의노트/`, `교과서/`, `23, 24 소스/`, `웹과제/`)에는 아무도 쓰지 않고, `복습노트/`에는 메인 에이전트만 쓴다.

### 1. 범위 파악
1. 이번 STT가 다룰 장을 정한다. 직전 노트(가장 최근 `복습노트/*/정리노트_*.md` 또는 `정리노트/MMDD.md`)의 마지막 장과 끊긴 지점, STT 앞부분을 본다. 확실하지 않으면 다음 장까지 넣는다. **먼저** 그 장들의 강의노트 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다. 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
```bash
REPO=… RUN=… CH="3" python3 - <<'EOF'
import fitz, os, unicodedata as u
repo, run = os.environ["REPO"], os.environ["RUN"]
d = os.path.join(repo, "강의노트")
out = []
for n in sorted(os.listdir(d)):
    name = u.normalize("NFC", n)
    ch = name.split("장", 1)[0]
    if name.endswith(".pdf") and ch in os.environ["CH"].split():
        for i, page in enumerate(fitz.open(os.path.join(d, n)), 1):
            out.append(f"=== {ch}장 p{i} ===\n{page.get_text()}")
open(os.path.join(run, "slides.txt"), "w", encoding="utf-8").write("\n".join(out))
print(len(out), "쪽")
EOF
```
   추출에 실패하면 STT만으로 진행하고 보고서에 적는다(브리프의 `slides.txt` 줄은 "없음"으로 바꿔 넘긴다).
2. 그다음 STT 날짜마다 요약 에이전트 1명을 **병렬로** 띄운다. 브리프는 `references/stt-summary-prompt.md`에 있다.
   - `<N장 *.pdf>`: 그 날짜가 다룬 강의노트 파일 이름. 확실하지 않으면 1의 장을 모두 적는다.
   - `<MMDD 생명.md>`: 0단계에서 찾은 실제 STT 파일 이름(`0903_생명.md`처럼 밑줄인 것도 있다).
   - `<YYYY-MM-DD>`: 연도는 이번 학기 연도(오늘 날짜 기준), 월·일은 `<MMDD>`.
3. 에이전트가 도는 동안 메인 에이전트는 `references/problem-selection.md`의 1절(기출 합본 렌더링)과 2절(웹과제 bank 확인·검증)을 한다.

### 2. manifest
- 요약들의 슬라이드 대조표, 용어 목록, 혼동 지점으로 `RUN/manifest.json`을 쓴다. 규칙은 `references/manifest-guide.md`에 있다.
- 문항 감사와 선별은 `references/problem-selection.md`를 따른다.
  - 장의 모든 문항 분류는 `RUN/question-audit.md`, 정답 대조는 `RUN/key-check.md`, 문항별 원문 위치는 `RUN/problem-pages.txt`에 적는다.
  - 포함 문항은 **전부** manifest `problems`에 넣는다.
  - 변형 연습(partC)은 `references/problem-selection.md` 6절로 설계해 포함 문항 뒤에 넣는다(`RUN/variants.md`).
- 검증: `python3 "$SKILL/scripts/manifest.py" "$RUN/manifest.json"` 결과가 `OK`여야 한다.

### 3. 작성
- 섹션마다 작성자 1명을 띄운다. 브리프는 `references/content-rules.md`, 위젯 규칙은 `references/widget-rules.md`에 있다.
- 카드 작성자는 카드 10개당 1명이다(`p1`–`p10`, `p11`–`p20`, …). 브리프는 `references/card-rules.md`에 있다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 opus, `lite`이면 sonnet이다.
- 브리프의 `<…>` 자리는 실제 값으로 채운다: 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 섹션 작성자에게 필요한 교과서 쪽(`<쪽>`), manifest `links` 중 그 섹션 토픽에 속한 것(`<이 섹션의 links 목록>`), `question-audit.md`에서 anchor가 그 섹션 토픽인 포함 문항과 필요한 개념(`<이 섹션 토픽이 받쳐야 할 문항>`), 카드 작성자가 맡은 id(`<담당 카드 id>`).
- 위젯은 팩 전체에 0~2개다. 병렬 작성자끼리는 서로를 모르므로 **메인 에이전트가 띄우기 전에** 위젯을 둘 토픽(0~2개)을 정하고, 그 토픽의 섹션 작성자 브리프에만 `<위젯>` 자리에 "토픽 `<토픽 id>`에 위젯 1개: <무엇을 움직이면 무엇이 보이는지>"를 적는다. 나머지 작성자의 `<위젯>` 자리에는 "위젯 없음"이라고 적는다. 정한 토픽과 이유는 보고서 "스킬이 정한 사항"에 적는다.

### 4. 조립
- **처음 조립할 때만**: `복습노트/<range>/`(또는 `복습노트/` 바로 아래)에 이번 `range`의 산출물(`정리노트_<range>_*`, `복습문제_<range>_*`의 `.html`·`.md`, `장마감_<range>_*.md`, `figures_<range>/`)이 하나라도 있으면 먼저 백업한다. 다시 조립할 때(5~8단계에서 돌아온 경우)는 백업하지 않는다. 이미 스킬이 만든 초안이 백업에 섞이기 때문이다.
  - `RANGE`, `REPO`, `RUN`을 모두 실제 값으로 바꿔 한 명령으로 실행한다. 파일명은 NFC로 비교하므로 NFD 파일명도 잡힌다.
  - 백업은 매번 새 폴더 `RUN/previous-<시각>-<임의>/`에 만든다(이전 백업을 덮어쓰지 않음). `RANGE`가 형식에 안 맞거나, 대상이 있는데 복사된 파일 수가 다르면 종료 코드 1로 멈춘다. 이때는 조립하지 말고 원인을 고친다.
```bash
RANGE=<range> REPO=… RUN=… python3 - <<'EOF'
import os, re, shutil, sys, tempfile, time, unicodedata as u
r, run = os.environ["RANGE"], os.environ["RUN"]
notes = os.path.join(os.environ["REPO"], "복습노트")
if not re.fullmatch(r"\d{4}(-\d{4})?", r) or not os.path.isdir(run):
    sys.exit(f"백업 중단: RANGE={r!r} 또는 RUN={run!r} 잘못됨")
def want(n):
    n = u.normalize("NFC", n)
    return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_", f"장마감_{r}_")) or n == f"figures_{r}"
def listdir_nfc(d):  # NFD 폴더명도 찾는다
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
srcs = [listdir_nfc(notes).get(r), notes]  # 날짜 폴더, 예전 형식(바로 아래)
hits = sorted({n: p for d in srcs if d and os.path.isdir(d) for n, p in listdir_nfc(d).items() if want(n)}.items())
if not hits:
    print("백업할 기존 팩 없음"); sys.exit(0)
def count(p):
    return sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 1
dst = tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run)  # 항상 새 폴더
for n, a in hits:
    b = os.path.join(dst, n)
    shutil.copytree(a, b) if os.path.isdir(a) else shutil.copy2(a, b)
want_n, got_n = sum(count(a) for _, a in hits), count(dst)
if got_n != want_n:
    sys.exit(f"백업 실패: 파일 {want_n}개 중 {got_n}개만 복사됨 → {dst}")
print(f"백업 {len(hits)}항목(파일 {got_n}개): {dst}", *(a for _, a in hits), sep="\n")
EOF
```
```bash
python3 "$SKILL/scripts/assemble.py" --run "$RUN" --out "$REPO/복습노트/<range>"
```
조립기는 `RUN/figures/`의 카드 그림을 `복습노트/<range>/figures_<range>/`로 복사한다.

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$REPO/복습노트/<range>/<정리노트>.html" --review "$REPO/복습노트/<range>/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다. `broken-image`는 그 카드 작성자다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰
- 브리프는 `references/review-prompt.md`에 있다. 두 리뷰어를 한 메시지에서 병렬로 띄운다.
  - **블라인드 풀이 검사**(항상, `lite` 포함): `references/review-prompt.md`의 "블라인드 풀이 검사" 스니펫으로 `RUN/work/blind-<range>.md`를 만든 뒤 리뷰어 1명에게 정리노트와 이 사본만 준다.
  - **일반 리뷰**(`lite`면 생략): 리뷰어 1명.
- 블라인드 리뷰어의 답이 manifest `answer`와 다르거나 "근거 없음"이면, `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다.
- 일반 리뷰의 Critical과 Important는 모두, Minor는 쉬운 것만 고친다.
- 담당 작성자별로 **한 번에 모아서** 수정을 요청한다. 수정은 한 번만 한다.
- 수정 후 4~5단계를 다시 하고, 블라인드 사본을 다시 만들어 틀렸던 문항만 다시 검사한다. 반영하지 않은 항목은 보고서에 적는다.

### 7. 브라우저 검증
- `references/browser-check.md`대로 한다.
  - http.server를 빈 포트에 띄운다.
  - 확인: KaTeX 오류 0, 남은 `$` 없음, 카드 그림 로드, 375px에서 가로 스크롤 없음, 다크모드, 위젯, 링크, 콘솔 오류
- 결함은 5단계와 같은 방식으로 작성자에게 되돌린다. 이것도 최대 2회 규칙에 포함된다.
- 끝나면 서버를 종료한다.

### 8. MD 변환
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --check
```
- `OK`가 나와야 한다.
- 누락이 나오면 대부분 HTML 조각의 마크업 문제다(수식이 `svg`나 `.controls` 안에 있는 경우 등). 조각을 고치고 4단계부터 다시 한다.

### 9. 보고
다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료
- 파일: 복습노트/<range>/… (html 2, md 2, figures_<range>/ N개)
- 범위: 배운 쪽 … / 예고만: … / 끊긴 지점: "…" (MMDD MM:SS)
- 문항: 포함 N (웹과제 a, 기출 b) · 변형 v · 이전 팩 N · 보류 N · 범위 밖 N — 분류표 RUN/question-audit.md
- 보류·범위 밖 문항: 번호와 사유를 한 줄씩(보고서만 읽어도 분류를 알 수 있게; RUN은 세션이 끝나면 사라질 수 있다)
- 답안지 오류: 기출 3강 12 (인쇄 (2) → 판단 (3)) … (없으면 "없음")
- 블라인드 검사: N/N 풀림 (고친 토픽: …)
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add review pack <range>"
```

**장 마감** (이번 범위에서 한 장이 끝났을 때만 — 요약의 끊긴 지점이 장 끝이거나 다음 장으로 넘어갔을 때):
그 장을 다룬 모든 회차(새 팩 `복습노트/*/`와 예전 `정리노트/MMDD.md`)를 모아 다음을 검토하고 `복습노트/<range>/장마감_<range>_<N>장.md`에 쓴다. 보고서에는 요약만 싣는다.
1. 회차별 범위와 절 연결: 어느 회차가 그 장의 어느 쪽을 다뤘는지, 빠진 쪽이 없는지.
2. 필수 그림과 시험 판별 용어가 노트에 모두 있는지.
3. 그 장의 **남은 보류 문항 전부**를 다시 분류한다: `시험 범위 확인됨 / 보충 학습 권장 / 제외 근거 있음 / 범위 불명`. 사유와 근거(강의계획서, STT 타임스탬프)를 함께 적는다. 생략을 곧바로 시험 제외로 바꾸지 않는다.
4. 시험 범위가 확인됐는지, 불명인지.
5. 변형 연습의 풀이 점검 결과(블라인드 검사에서 틀렸거나 근거 없던 변형).

장 마감 파일은 새 장 요약 노트가 아니다. 본문을 복제하지 않고 원천 노트의 토픽으로 링크한다.

실행 폴더 경로(`RUN`)도 적는다. 수정이 필요하면 조각을 고쳐 4단계부터 다시 돌리면 된다. 커밋 제안 전에 `git status`로 `*.zip`이 섞이지 않았는지 확인한다.

## 오류 처리
| 상황 | 동작 |
|---|---|
| 저장소가 아님 | 알리고 멈춤 |
| 기간에 해당하는 STT 없음 | 사용 가능한 날짜를 보여 주고 멈춤 |
| 강의노트 텍스트 추출 실패 | STT만으로 진행하고 보고서에 표시 |
| 그 장의 기출 합본 없음 | partB를 빼고 진행, 보고서에 표시 |
| 웹과제 `questions.json` 없이 `raw/` 캡처만 있음 | "등록되지 않은 웹과제 자료"로 보고하고 partA를 뺀다("웹 자료 없음"이라고 쓰지 않는다) |
| 웹과제 bank 검증 실패 | 멈추지 않고 문항은 쓰되, 실패한 필드와 source를 "미해결"에 적음 |
| 포트 사용 중 | 다른 빈 포트 사용 |
| 같은 range의 팩이 이미 있음 | 4단계 첫 조립 전에 기존 html·md·`장마감_<range>_*.md`·`figures_<range>/`를 새 폴더 `RUN/previous-<시각>-<임의>/`에 복사하고(다시 조립할 때는 복사하지 않음) 백업 경로를 보고서에 적음. 백업 명령이 실패하면 조립하지 않고 원인을 고친다 |
| 검사 2회 실패 | 멈추지 않고 나머지 단계를 끝낸 뒤 "미해결"로 보고 |
