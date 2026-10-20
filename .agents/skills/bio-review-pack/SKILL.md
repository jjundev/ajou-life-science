---
name: bio-review-pack
description: 생명과학 수업의 STT·강의노트·교과서와 23·24 기출·웹과제로 ELI5 정리노트 HTML과 객관식 복습문제 HTML(+MD, 그림)과 문제설명을 만들어 복습노트의 날짜별 폴더에 저장한다. "정리노트", "복습문제", "문제설명", "복습팩", "0922 강의 듣고 왔어", "0922~0924 정리해줘"처럼 생명과학 수업 정리를 요청하거나 /bio-review-pack [MMDD|MMDD-MMDD] [lite]로 부를 때 사용한다.
---

# 생명과학 복습팩

수업 녹음 전사(STT)와 강의노트, 교과서, 기출·웹과제로 한 기간의 복습팩을 만든다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**산출물** (`복습노트/<range>/`, 기간(range)마다 폴더 하나):
- 루트: `정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, `문제설명_<range>_<slug>.html`, `.pack/`
- `.assets/`(숨김 폴더): 같은 이름의 `.md`(정리노트·복습문제·문제설명), `figures_<range>/`, `figures_문제설명_<range>_<slug>/`, `자료_문제설명_<range>_<slug>/`, `풀이기록/`, (장이 끝난 범위면) `장마감_<range>_<N>장.md`
- `.assets/`는 숨김 폴더라 Glob·Grep 도구가 건너뛴다. 안의 파일은 `복습노트/<range>/.assets/…`처럼 경로를 글자 그대로 쓰고, 찾을 때는 Bash의 `ls`·`find`나 Python `pathlib`를 쓴다.

**인자**: `[MMDD | MMDD-MMDD] [lite] [augment]`
- `lite`: 작성자·요약 에이전트를 sonnet으로 하고, 6단계의 일반 리뷰를 생략한다. 블라인드 풀이 검사, 기계 검사, 브라우저 검사는 그대로 한다. 문제설명 저작·독립 검산·실자료 검토·브라우저 검증은 생략하지 않는다.
- `augment`: 이미 만든 팩에 웹과제 원문(partA)과 새 변형(partC)을 덧붙인다. 0~9단계 대신 아래 **보강 모드**를 따른다. range가 꼭 있어야 한다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 5개 + 카드 23개 (병렬)`

**서브에이전트가 없는 환경(Codex 등)**: 병렬 에이전트 대신 같은 브리프로 요약·섹션·카드를 차례로 직접 쓴다. 6단계 블라인드 검사는 새 세션에서 블라인드 사본과 정리노트만 열어 수행한다. 모델 지정은 Claude에서는 opus/sonnet 그대로 따르고, GPT 등 다른 모델 환경에서는 opus→sol, sonnet→luna로 바꿔 읽는다(이 문서와 references의 모든 모델 지정에 적용).

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-review-pack`)의 절대 경로. `.claude/skills/bio-review-pack`은 이 폴더를 가리키는 심볼릭 링크다. 링크 경로가 아니라 원본 경로로 푼다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/review-pack/<range>/` (scratchpad가 없으면 `/tmp/bio-review-pack/<range>/`)
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 셸 명령의 `$SKILL`, `$RUN`, `$REPO`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 Bash 호출 맨 앞에 세미콜론으로 먼저 설정한다(`SKILL=…; RUN=…; REPO=…; python3 "$SKILL/scripts/…" …`). `RUN=… mkdir "$RUN"`처럼 같은 명령 앞에 붙이는 형식은 쓰지 않는다. 셸이 인자의 `"$RUN"`을 그 설정보다 먼저 펼쳐 빈 경로가 되기 때문이다. `os.environ`으로 값을 읽는 파이썬 heredoc 스니펫(`REPO=… python3 - <<'EOF'` 형식)만 앞에 붙이는 형식을 그대로 쓴다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.
- 장 번호 `N`은 `강의노트/N장 *.pdf`, `23, 24 소스/N강 합본.pdf`(파일명에 `+`가 섞여 있다), `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`(두 자리), `웹과제/N장/`에서 같은 수를 쓴다.

## 절차

### 0. 준비
1. `REPO`에 `STT/`, `강의노트/`, `23, 24 소스/`, `교과서/생명과학_기초와_응용_2판/`이 모두 있는지 확인한다. 하나라도 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다. 형제 스킬 `bio-problem-explain/SKILL.md`와 `bio-problem-explain/scripts/mpe_cli.py`(`.agents/skills/` 아래 원본 경로)도 있는지 확인한다. 없으면 경로와 오류를 보고하고 멈춘다.
2. STT 날짜와 마지막으로 정리한 날짜를 NFC로 읽는다. `복습노트/*/정리노트_<range>_*.html`의 끝 날짜를 본다.
```bash
REPO=… python3 - <<'EOF'
import os, re, unicodedata as u
repo = os.environ["REPO"]
def ls(*parts):
    d = os.path.join(repo, *parts)
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
stt = sorted(m.group(1) for n in ls("STT") if (m := re.fullmatch(r"(\d{4})[ _]생명\.md", n)))
done = []
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
1. 이번 STT가 다룰 장을 정한다. 직전 노트(가장 최근 `복습노트/*/.assets/정리노트_*.md`)의 마지막 장과 끊긴 지점, STT 앞부분을 본다. 확실하지 않으면 다음 장까지 넣는다. **먼저** 그 장들의 강의노트 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다. 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
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
4. `references/note-feedback.md`대로 이번 장의 `웹과제/<N>장/note-feedback.md`를 읽고 실제 문항별 판별 기준을 확인한다. bank 미등록·partA 제외여도 본문 피드백을 건너뛰지 않는다. 자료가 없으면 미작성 상태를 보고한다. 출제 관찰·문항별 판별 기준·개인 미확인 가설을 구분하고 기존 영어 병기와 명칭 회상 연습도 따로 확인한다.

### 2. manifest
- 요약들의 슬라이드 대조표, 용어 목록, 혼동 지점으로 `RUN/manifest.json`을 쓴다. 규칙은 `references/manifest-guide.md`에 있다.
- 문항 감사와 선별은 `references/problem-selection.md`를 따른다.
  - 장의 모든 문항 분류는 `RUN/question-audit.md`, 정답 대조는 `RUN/key-check.md`, 문항별 원문 위치는 `RUN/problem-pages.txt`에 적는다.
  - 포함 문항은 **전부** manifest `problems`에 넣는다.
  - 변형 연습(partC)은 `references/problem-selection.md` 6절과 `references/webquiz-style.md`의 유형 할당으로 설계해 포함 문항 뒤에 넣는다(`RUN/variants.md`).
- 본문 피드백은 `references/note-feedback.md`대로 `RUN/note-feedback-audit.md`에 **카드 포함 여부와 독립적으로** 모든 ID의 범위·토픽·계획 레이어를 적는다. 판별 용어는 관련 토픽에, 추가 사실은 출처 있는 supp에 연결한다. 이전 수업 링크·미학습·불확실도 행을 남긴다.
- 검증: `python3 "$SKILL/scripts/manifest.py" "$RUN/manifest.json"` 결과가 `OK`여야 한다.

설계표의 기본/심화 목표와 실개수를 `review_intro`에 짧게 적는다(예: “변형 연습은 기본 8개·심화 2개예요.”). 기존 카드 번호와 part 순서는 유지하고 난이도 배지는 추가하지 않는다. 보강에서는 기존 partC와 새 변형을 합쳐 실개수를 집계하되, 기존 문항을 배합 때문에 고치거나 제거하지 않는다. 새 문항 블라인드 검사만으로 기존 미검토 난이도가 검증됐다고 쓰지 않는다.

### 3. 작성
- 섹션마다 작성자 1명을 띄운다. 브리프는 `references/content-rules.md`, 위젯 규칙은 `references/widget-rules.md`에 있다.
- 작성자 브리프에 `references/content-rules.md`의 「어려운 개념에 한정한 동기·인과 설명」 기준을 반영한다. 해당 토픽만 필요성·원리·시작 조건을 연결하고 단순 토픽의 과잉 설명은 피한다. 재료의 준비 상태와 선택 주체가 혼동되는 토픽에서는 선행 준비, 생성·선택·운반·연결의 구분, 각 짝맞춤의 담당 주체도 확인한다. 그중 어려운 실험·기술 개념은 직접 측정값·해석·궁극적인 질문까지 연결하며, 절차 설명만으로 목적 설명을 대신하지 않는다. 작성자 자기 검사에는 이 기준을 포함하며 `lite`에서도 수행한다.
- 섹션 작성자에게 `RUN/note-feedback-audit.md` 중 해당 토픽의 행과 원천 피드백·근거를 전달한다. 포함 문항 목록에 없어도 필요한 판별 기준을 가르친다. 명칭·대상·조건·결과·인접 사례가 필요한 토픽만 공통 규칙에 따라 연결한다. 영어 병기 존재만으로 다른 명칭에서의 회상을 충족했다고 세지 않으며, lite에서도 실제 본문 문장으로 의미를 검토한다. 작성 후 실제 본문 문장·토픽·적용 상태를 표에 채운다(`references/note-feedback.md`).
- 카드 작성자는 카드 10개당 1명이다(`p1`–`p10`, `p11`–`p20`, …). 브리프는 `references/card-rules.md`에 있다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 opus, `lite`이면 sonnet이다.
- 브리프의 `<…>` 자리는 실제 값으로 채운다: 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 섹션 작성자에게 필요한 교과서 쪽(`<쪽>`), manifest `links` 중 그 섹션 토픽에 속한 것(`<이 섹션의 links 목록>`), `question-audit.md`에서 anchor가 그 섹션 토픽인 포함 문항과 필요한 개념(`<이 섹션 토픽이 받쳐야 할 문항>`), 카드 작성자가 맡은 id(`<담당 카드 id>`).
- 위젯은 팩 전체에 0~2개다. 병렬 작성자끼리는 서로를 모르므로 **메인 에이전트가 띄우기 전에** 위젯을 둘 토픽(0~2개)을 정하고, 그 토픽의 섹션 작성자 브리프에만 `<위젯>` 자리에 "토픽 `<토픽 id>`에 위젯 1개: <무엇을 움직이면 무엇이 보이는지>"를 적는다. 나머지 작성자의 `<위젯>` 자리에는 "위젯 없음"이라고 적는다. 정한 토픽과 이유는 보고서 "스킬이 정한 사항"에 적는다.

### 4. 조립
- **처음 조립할 때만**: `복습노트/<range>/`(그 안의 `.assets/`, 또는 `복습노트/` 바로 아래)에 이번 `range`의 산출물(`정리노트_<range>_*`, `복습문제_<range>_*`의 `.html`·`.md`, `장마감_<range>_*.md`, `figures_<range>/`, `문제설명_<range>_*`, `figures_문제설명_<range>_*/`, `자료_문제설명_<range>_*/`)이 하나라도 있으면 먼저 백업한다. 다시 조립할 때(5~8단계에서 돌아온 경우)는 백업하지 않는다. 이미 스킬이 만든 초안이 백업에 섞이기 때문이다.
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
    return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_", f"장마감_{r}_", f"문제설명_{r}_", f"figures_문제설명_{r}_", f"자료_문제설명_{r}_")) or n in (f"figures_{r}", ".pack")
def listdir_nfc(d):  # NFD 폴더명도 찾는다
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
day = listdir_nfc(notes).get(r)
srcs = [day, day and os.path.join(day, ".assets"), notes]  # 날짜 폴더, 그 안의 .assets, 예전 형식(바로 아래)
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
조립기는 `RUN/figures/`의 카드 그림을 `복습노트/<range>/.assets/figures_<range>/`로 복사한다. 카드의 `<img src>`는 `.assets/figures_<range>/pN.png`다.
조립기는 `RUN`의 `manifest.json`·`question-audit.md`·`key-check.md`·`variants.md`·`problem-pages.txt`를 `복습노트/<range>/.pack/`에 복사하고 `.pack/log.md`에 실행 한 줄을 더한다. `.pack/`은 git으로 추적한다(금지어 목록과 감사표를 다음 보강에서 다시 쓴다). 내부 기록이라 STT 시각이 있어도 된다.
full 조립에서는 `RUN/note-feedback-audit.md`가 있으면 `.pack/`에 함께 복사한다. 검토 후 최종 표를 저장하고 마지막 조립을 다시 수행하여 실제 적용·보류 결과를 보존한다.

### 5. 기계 검사
객관식은 `references/content-rules.md`의 보기·해설 식별자 규칙을 따른다. 조립 시 채점 모델이 자동 내장되며 연결 오류는 카드 원본에서 해결한다. 아래 검사기는 내장 채점 데이터와 원본의 일치도 검사한다. 브라우저 검증 때 정답·오답 선택, 내 선택·정답만 자동 펼침, 모든 보기별 해설의 개별 접기·펼치기, 다시 풀기와 선택 복원을 함께 확인한다. 선택·푼 기록은 `sessionStorage`라 새로고침·뒤로가기엔 남고 새 탭에서 다시 열면 초기화돼야 한다(`localStorage` 사용 금지). 마지막 문제 화면의 **JSON 내보내기** 버튼(폴더 선택창 저장, 취소·거부 처리)과 화면을 벗어날 때의 스냅샷 갱신, 풀이 패널의 **애매함으로 표시** 토글(JSON `unsure`)도 함께 확인한다. 이 토글은 정답을 고른 뒤에만 보이고 오답·출제 모호 문항에서는 숨겨져야 한다.

```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$REPO/복습노트/<range>/<정리노트>.html" --review "$REPO/복습노트/<range>/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다. `broken-image`는 그 카드 작성자다.
- `stt-time`은 학생용 HTML에 STT 녹음 시각이 남은 경우다. 해당 문장을 자연스럽게 고치고 다시 검사한다. 내부 요약의 시각은 보존한다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰
- 카드 검사와 별도로 `references/review-prompt.md`의 **본문 피드백 검토 (항상, lite 포함)**를 수행한다. `RUN/note-feedback-audit.md`의 전체 ID를 본문 문장과 대조하고, 누락은 섹션을 고쳐 재조립·재검사한다. 완료 후 최종 감사표를 `.pack/`에 저장한다. 원본 채점 미확인은 그대로 유지한다.
- 브리프는 `references/review-prompt.md`에 있다. 두 리뷰어를 한 메시지에서 병렬로 띄운다.
  - **블라인드 풀이 검사**(항상, `lite` 포함): `references/review-prompt.md`의 "블라인드 풀이 검사" 스니펫으로 `RUN/work/blind-<range>.md`를 만든 뒤 리뷰어 1명에게 정리노트와 이 사본만 준다.
  - **일반 리뷰**(`lite`면 생략): 리뷰어 1명.
- 블라인드 리뷰어의 답이 manifest `answer`와 다르거나 "근거 없음"이면, `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다.
  - 변형 연습(partC)을 못 풀었으면 먼저 변형 자체를 본다. 정답이 하나가 아니거나 범위 밖이면 카드 작성자에게 고치게 하거나 manifest·`variants.md`에서 뺀다. 변형이 멀쩡할 때만 위처럼 섹션 작성자에게 되돌린다. 변형을 빼도 번호를 다시 매기지 않고 빈 번호로 둔다(추가 때처럼 `question-audit.md`가 아닌 `variants.md`에 사유를 적는다). 마지막 변형까지 빠지면 manifest `parts`에서 `partC`를 지우고 `review_intro`·`footer_review`의 변형 문구도 지운다.
- 독립 수준·최소 풀이 단계를 설계표와 대조한다. 원문 분류는 재검토하고 생성 변형은 수정/교체하거나 목표 차이를 보고한다(`references/review-prompt.md`). lite에서도 수행하며 기존 최대 2회 한도에 포함한다.
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
- `OK`가 나와야 한다. MD와 SVG 그림은 `복습노트/<range>/.assets/`에 쓰이고, MD 안 링크는 `.assets/` 기준이다.
- 변환한 두 MD(`복습노트/<range>/.assets/`)와 `.assets/장마감_<range>_*.md`에서 `HH:MM` 형태의 후보를 검색한다. STT 녹음 위치는 삭제하고, 실제 학습 내용의 시간 표현이라면 문맥을 확인해 유지한다.
- 누락이 나오면 대부분 HTML 조각의 마크업 문제다(수식이 `svg`나 `.controls` 안에 있는 경우 등). 조각을 고치고 4단계부터 다시 한다.

### 8b. 문제설명
8단계가 `OK`이고 5~8단계에 미해결이 없을 때만 한다. 미해결이 있으면 실행하지 않고 "복습팩 생성됨 / 문제설명 보류"와 이유를 보고한다.
- 최종 복습문제 HTML의 절대 경로(ABS_REVIEW)로 `references/problem-explain.md`를 실행한다. 형제 `bio-problem-explain`의 "실행" 1~7단계를 따르며 `lite`에서도 네 검토를 생략하지 않는다.
- 실패하면 검증된 복습팩과 이전 문제설명을 보존하고 다음 팩을 계속한다.
- 기존 range를 전체 재생성(augment 아님)했는데 8b가 보류·실패하면 보고서의 미해결에 "기존 문제설명 파일은 이전 카드 기준(stale)"이라고 적는다.

### 9. 보고
이번 범위에서 장이 끝났으면 아래 **장 마감** 검토를 먼저 하고, 보고서의 `장 마감` 줄에 그 요약을 적는다. 다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료  (문제설명 보류면 제목을 "복습팩 생성됨 / 문제설명 보류"로 바꾼다)
- 파일: 복습노트/<range>/… (html 3, `.pack/`) · 복습노트/<range>/.assets/… (md 3, figures_<range>/ N개)
- 범위: 배운 쪽 … / 예고만: … / 끊긴 지점: "…"
- 난이도: 변형 기본(수준 1~2) N · 심화(수준 3) N · 목표와 실제 유형 수·난이도 차이 및 이유
- 문항: 포함 N (웹과제 w, 기출 x) · 변형 v (쌍둥이 t · 그림 g · 상황 s · ㄱㄴㄷ k · 부정형 n · 용어 r · 낯선참 u · 장섞기 c) · 이전 팩 N · 보류 N · 범위 밖 N — 분류표 RUN/question-audit.md, 변형 RUN/variants.md. 표 해석은 별도 집계. 목표보다 부족한 유형은 사유를 한 줄씩(의무 최소 0인 선택 유형은 0개 자체가 미해결은 아님)
- 보류·범위 밖 문항: 번호와 사유를 한 줄씩(보고서만 읽어도 분류를 알 수 있게; RUN은 세션이 끝나면 사라질 수 있다)
- 답안지 오류: 기출 3강 12 (인쇄 (2) → 판단 (3)) … (없으면 "없음")
- 블라인드 검사: N/N 풀림 (고친 토픽: …)
- 본문 피드백: 대상 N · 본문 반영 N · 기존 설명 충분 N · 이전 노트 연결 N · 미학습 보류 N · 판독/근거 불확실 N — .pack/note-feedback-audit.md (피드백 미작성은 별도 보고)
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유
- 장 마감: N장 — 보류 재분류 요약 (장이 끝나지 않았으면 "해당 없음")
- 문제설명: 발행/보류 · N문항 · HTML·MD · EXPLAIN_RUN · 백업 · 네 검토 결과 · 보류 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add review pack <range>"
```

실행 폴더 경로(`RUN`)도 적는다. 수정이 필요하면 조각을 고쳐 4단계부터 다시 돌리면 된다. 커밋 제안 전에 `git status`로 `*.zip`이 섞이지 않았는지 확인한다.

`references/webquiz-style.md` 1절에 없는 장의 `웹과제/<N>장/questions.json`이 있으면 그 파일 5절대로 세어 보고서 끝에 "webquiz-style.md 갱신 제안"을 적는다. 같은 range의 팩을 다시 만들면 기존 카드 번호를 유지한다(새 문항은 기존 최대 번호 다음부터). `references/interactive-overrides.json`의 애매함 공지와 `복습노트/<range>/.assets/풀이기록/`이 카드 id로 문항을 가리키기 때문이다. 번호가 바뀌었다면 overrides 키를 새 번호에 맞게 고치고, 예전 풀이기록은 git 기록의 예전 HTML 기준이라고 보고서에 적는다. 끝나면 `.assets/풀이기록/`이 그대로인지 확인한다.

**장 마감** (이번 범위에서 한 장이 끝났을 때만 — 요약의 끊긴 지점이 장 끝이거나 다음 장으로 넘어갔을 때):
그 장을 다룬 모든 회차(`복습노트/*/`)를 모아 다음을 검토하고 `복습노트/<range>/.assets/장마감_<range>_<N>장.md`에 쓴다. 보고서에는 요약만 싣는다.
1. 회차별 범위와 절 연결: 어느 회차가 그 장의 어느 쪽을 다뤘는지, 빠진 쪽이 없는지.
2. 필수 그림과 시험 판별 용어가 노트에 모두 있는지.
3. 그 장의 **남은 보류 문항 전부**를 다시 분류한다: `시험 범위 확인됨 / 보충 학습 권장 / 제외 근거 있음 / 범위 불명`. 사유와 근거(강의계획서, 수업 발언 요지)를 함께 적되 학생용 장 마감 파일에 STT 녹음 시각은 넣지 않는다. 내부 감사 기록에는 타임스탬프를 남겨 대조한다. 생략을 곧바로 시험 제외로 바꾸지 않는다.
4. 시험 범위가 확인됐는지, 불명인지.
5. 변형 연습의 풀이 점검 결과(블라인드 검사에서 틀렸거나 근거 없던 변형).
6. `웹과제/<N>장/note-feedback.md`의 전체 ID를 회차별 `.pack/note-feedback-audit.md`와 대조해 실제 문항의 판별 기준이 어디서 설명되는지, 남은 보류가 무엇인지 확인한다. 등록 여부와 별개이며 카드 검사 수로 대신하지 않는다.

장 마감 파일은 새 장 요약 노트가 아니다. 본문을 복제하지 않고 원천 노트의 토픽으로 링크한다.

## 보강 모드

웹과제 bank는 그 장 응시 뒤에 생긴다. 이미 만든 팩을 다시 만들면 카드 번호가 바뀌어 `references/interactive-overrides.json`(카드 id 키)과 `복습노트/<range>/.assets/풀이기록/`이 엉뚱한 문항에 붙는다. 그래서 보강은 **기존 카드 번호를 그대로 두고** 복습문제만 다시 쓴다. 정리노트 HTML·MD와 `.assets/풀이기록/`은 건드리지 않는다. `RUN` 경로 약속은 위와 같다(`<scratchpad>/review-pack/<range>-augment/`).
새 문항별 피드백을 읽어도 이 모드에서는 본문 적용 완료로 세지 않는다. 기존 `.pack/note-feedback-audit.md`를 보존하고, 본문 변경이 필요하면 전체 재생성(augment 아님) 대상으로 보고한다.

**A1. 추출**
```bash
SKILL=…; REPO=…; RUN=…; python3 "$SKILL/scripts/augment.py" extract "$REPO/복습노트/<range>" "$RUN"
```
- 기존 카드를 `RUN/cards/pN.html`로, manifest를 `RUN/manifest.json`으로 꺼내고 다음 id를 출력한다.
- manifest는 `복습노트/<range>/.pack/manifest.json`을 쓴다. 없으면 HTML에서 복원한다(출력에 "금지어 미복원"). 복원했거나 `.pack/log.md`에 "금지어 미복원"이 있으면 A2에서 금지어를 다시 정한다.
- `.pack` manifest와 HTML 카드가 다르다고 멈추면, 누가 HTML을 손으로 고친 것이다. 차이를 보고하고 멈춘다.
- `경고:`로 "HTML이 .pack manifest로 다시 조립한 결과와 다름"이 나오면 카드 밖(제목·안내·꼬리말)을 손으로 고친 것이다. A3이 manifest 값으로 덮으므로, 살릴 수정이면 `RUN/manifest.json`에 옮겨 적는다. 같은 종류 HTML이 둘 이상이라고 멈추면 백업 사본을 팩 폴더 밖으로 옮긴다.

**A2. 새 문항 정하기** (기존 절차 재사용)
- 장 bank를 `references/problem-selection.md` 2절로 검증하고 3절 감사표를 `RUN/question-audit.md`에 쓴다. "이전 팩" 판정에 **이 팩 자신의 기존 `data-source`도** 넣는다.
- 변형은 6절과 `references/webquiz-style.md`대로 `RUN/variants.md`에 설계한다. 쌍둥이 재료 판단의 "같은 팩 partA"는 기존 카드와 새 partA를 합친 집합이다.
- 금지어 미복원이면: 정리노트 예고 토픽(`preview_topic`) 본문의 용어 중 다른 토픽에 나오지 않는 것을 후보로 다시 정해 `RUN/manifest.json`에 넣고 보고서에 "금지어 재도출"이라고 적는다.
- 기존과 새 partC의 기본/심화 실개수·목표 차이를 `review_intro`와 A6 보고에 적는다. 원문과 기존 카드 번호를 유지하고, 부족한 목표를 맞추기 위해 범위 밖 문항을 만들지 않는다.
- 새 문항을 `RUN/manifest.json` `problems` 끝에 A1이 출력한 다음 id부터 붙이고, 카드 작성자(`references/card-rules.md` 브리프)가 `RUN/cards/<새 id>.html`을 쓴다. 기출 그림은 `RUN/figures/`.

**A3. 조립**
```bash
SKILL=…; REPO=…; RUN=…; python3 "$SKILL/scripts/augment.py" build "$REPO/복습노트/<range>" "$RUN"
```
- 기존 카드의 id·part·source·answer가 바뀌었거나 카드가 사라졌으면 아무것도 쓰지 않고 멈춘다. 카드 본문 수정은 허용한다.
- part 순서(A·B·C)로 정렬하고, 제목의 "N선"·안내의 문항 수·꼬리말의 `웹과제(N장)`을 맞춘다. `경고:` 줄이 나오면 그 문구를 `RUN/manifest.json`에서 직접 고치고 A3을 다시 한다(`base-ids.json`이 그대로라 다시 해도 된다).
- 복습문제 HTML만 쓰고 `.pack/`에 기록을 남긴다(`log.md`에 augment 한 줄).

**A4. 검사**
- `python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note … --review …` → `OK`. 복원 manifest라면 정리노트 쪽은 구조만 검사된다는 한계를 보고서에 적는다.
- 블라인드 검사: `references/review-prompt.md` 스니펫을 `IDS=<새 id 쉼표 목록>`과 함께 돌려 **새 카드만** 사본을 만들고 6단계 규칙대로 검사한다.
- 브라우저: `references/browser-check.md`대로, 새 카드 하나 이상과 기존 카드 하나를 연다.

**A5. MD 변환**
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --only review --check
```
- 복습문제 MD만 다시 쓴다. 정리노트 MD와 그 그림은 그대로다.

**A5b. 문제설명**
- A5 뒤 `references/problem-explain.md`를 같은 절차로 실행해 팩 전체(기존+새 카드)의 문제설명을 다시 만든다. 이전 문제설명은 백업되고, 실패하면 보존한다.

**A6. 보고**
- 문제설명 줄(발행/보류)도 넣는다.
- 9단계 형식에 `보강:`을 앞에 붙이고 `추가 pX–pY`를 더한다. `git status 복습노트/<range>/.assets/풀이기록`이 비어 있는지 확인해 적는다. 기존 카드 번호를 바꾸지 않았음을 확인하는 줄을 넣는다.
- 커밋 제안: `git add 복습노트/<range> && git commit -m "docs(notes): augment review pack <range> with <N>장 webquiz"`

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
| 같은 range의 팩이 이미 있음 | 4단계 첫 조립 전에 기존 html과 `.assets/`의 md·`장마감_<range>_*.md`·`figures_<range>/`를 새 폴더 `RUN/previous-<시각>-<임의>/`에 복사하고(다시 조립할 때는 복사하지 않음) 백업 경로를 보고서에 적음. 문제설명 파일(`문제설명_<range>_*`, `figures_문제설명_<range>_*`, `자료_문제설명_<range>_*`)도 같이 백업한다. 백업 명령이 실패하면 조립하지 않고 원인을 고친다 |
| 검사 2회 실패 | 멈추지 않고 나머지 단계를 끝낸 뒤 "미해결"로 보고 |
| 보강: `.pack` manifest와 HTML 카드 불일치 | 차이를 보고하고 멈춤(HTML을 덮어쓰지 않음) |
| 보강: 기존 카드 보호 검사 실패 | 쓰지 않고 멈춤, 바뀐 카드와 필드를 보고 |
| 문제설명 저작·검산·검토·발행 실패 | 검증된 복습팩과 이전 해설을 보존하고 "복습팩 생성됨 / 문제설명 보류"로 보고, 다른 팩은 계속; 기존 range를 전체 재생성했다면 미해결에 "기존 문제설명 파일은 이전 카드 기준(stale)"이라고 적음 |
