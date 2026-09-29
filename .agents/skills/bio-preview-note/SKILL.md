---
name: bio-preview-note
description: 생명과학 다음 수업의 강의노트 범위(직전 복습노트가 끝난 쪽부터)와 교과서로, 수업 중 옆에 띄워 둘 짧은 예습노트 HTML(+MD, 그림)을 만들어 예습노트/<날짜>/ 폴더에 저장한다. 문제는 만들지 않고, 기출·웹과제에 나온 용어는 들을 때 포인트에 "기출"로 표시한다. "예습노트", "생명 예습", "다음 수업 미리 보기", "0929 예습해줘"처럼 생명과학 수업 전 준비를 요청하거나 /bio-preview-note [MMDD] [lite]로 부를 때 사용한다.
---

# 생명과학 예습노트

강의노트와 교과서로 다음 수업 한 번의 예습노트를 만든다. 수업을 들으면서 옆에 띄워 두는 용도라 **짧게** 쓰고, 토픽 순서는 **강의노트 순서 그대로**다. 문제는 만들지 않는다. 양식은 `bio-review-pack` 정리노트와 같다(`assets/note-template.html`은 그 템플릿의 심링크). 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**산출물** (`예습노트/<MMDD>/`): `예습노트_<MMDD>_<slug>.html`, 같은 이름 `.md`, `figures_<MMDD>/`

**인자**: `[MMDD] [lite]`
- `MMDD`가 없으면 오늘(포함) 이후 STT가 없는 가장 가까운 화·목. 그 날짜 예습노트가 이미 있으면 멈추고 알린다. 날짜를 주면 다시 만든다.
- `lite`: 작성자와 6단계 리뷰어를 sonnet으로 돌린다. 리뷰는 생략하지 않는다(검사기가 못 잡는 사실 오류·문장 문제를 잡는 유일한 단계라서). 기계 검사와 브라우저 검사도 그대로 한다.

**진행 표시**: 단계마다 한 줄, `<단계 번호>/9`. 예: `3/9 작성 중: 섹션 3개 (병렬)`

**서브에이전트가 없는 환경(Codex 등)**: 병렬 작성자 대신 같은 브리프로 섹션을 차례로 직접 쓴다. 모델 지정은 Claude에서는 opus/sonnet 그대로, GPT 등에서는 opus→sol, sonnet→luna로 바꿔 읽는다(references의 모든 모델 지정에 적용).

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-preview-note`)의 절대 경로. `.claude/skills/bio-preview-note`는 이 폴더를 가리키는 심링크다. 원본 경로로 푼다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/preview-note/<MMDD>/` (scratchpad가 없으면 `/tmp/bio-preview-note/<MMDD>/`)
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. `$SKILL`, `$RUN`, `$REPO`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나 같은 Bash 호출 맨 앞에 세미콜론으로 먼저 설정한다(`SKILL=…; RUN=…; REPO=…; python3 "$SKILL/scripts/…" …`). `os.environ`으로 값을 읽는 파이썬 heredoc 스니펫(`REPO=… python3 - <<'EOF'`)만 앞에 붙이는 형식을 쓴다. `cd`는 쓰지 않는다.
- 장 번호 `N`은 `강의노트/N장 *.pdf`, `23, 24 소스/N강*합본.pdf`(파일명에 `+`가 섞여 있다), `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`(두 자리), `웹과제/N장/`에서 같은 수다.

## 절차

### 0. 준비
1. `REPO`에 `STT/`, `강의노트/`, `복습노트/`, `교과서/생명과학_기초와_응용_2판/`이 있는지 확인한다. 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. 수업일과 시작 쪽을 고른다.
   ```bash
   python3 "$SKILL/scripts/preview_files.py" pick --repo "$REPO" [--date MMDD]
   ```
   출력은 `MMDD<TAB>장<TAB>시작쪽<TAB>강의노트 PDF 경로`. 종료 코드가 1이면 표준에러 메시지를 그대로 보여 주고 멈춘다.
3. 실행 폴더를 만든다. 서브에이전트에게는 `RUN`, `RUN/repo`, `SKILL` 경로만 넘긴다.
   ```bash
   SKILL=…; RUN=…; REPO=…; rm -rf "${RUN:?}/sections" "${RUN:?}/work" && mkdir -p "$RUN"/{sections,work} && ln -sfn "$REPO" "$RUN/repo"
   ```
   에이전트는 `RUN` 밖에 쓰지 않는다. 임시 파일은 `RUN/work/`에만 둔다. `예습노트/`에는 메인 에이전트만 쓴다.

### 1. 범위 파악
1. 시작 쪽부터 최대 5쪽(장이 끝나면 다음 장 앞쪽까지)을 쪽 번호와 함께 `RUN/slides.txt`로 뽑는다. 줄여서 4쪽 이하로 맞추는 것은 3에서 한다.
   ```bash
   REPO=… RUN=… CH=<장> START=<시작쪽> python3 - <<'EOF'
   import fitz, os, unicodedata as u
   repo, run = os.environ["REPO"], os.environ["RUN"]
   ch, start = int(os.environ["CH"]), int(os.environ["START"])
   d = os.path.join(repo, "강의노트")
   pdfs = {}
   for n in os.listdir(d):
       name = u.normalize("NFC", n)
       head = name.split("장", 1)[0]
       if name.endswith(".pdf") and head.isdigit():
           pdfs[int(head)] = os.path.join(d, n)
   nxt = [c for c in sorted(pdfs) if c > ch]
   out = []
   for c, first in [(ch, start)] + ([(nxt[0], 1)] if nxt else []):
       doc = fitz.open(pdfs[c])
       print(f"{c}장: {len(doc)}쪽")
       for i in range(first, len(doc) + 1):
           if len(out) >= 5:
               break
           out.append(f"=== {c}장 p{i} ===\n{doc[i - 1].get_text()}")
   open(os.path.join(run, "slides.txt"), "w", encoding="utf-8").write("\n".join(out))
   print(len(out), "쪽:", *[o.splitlines()[0] for o in out])
   EOF
   ```
   추출에 실패하면 PDF를 Read 도구로 직접 읽고 보고서에 적는다.
2. 가장 최근 정리노트 MD에서 끊긴 지점을 읽는다(`pick`이 고른 정리노트와 같은 폴더의 `.md`).
   ```bash
   grep -n "끊긴 지점" "<REPO>/복습노트/<폴더>/정리노트_<range>_<slug>.md"
   ```
   시작 쪽 안에서 이미 배운 절(소제목)은 범위에서 뺀다. 끊긴 지점이 장 끝이면 다음 장부터 시작한다.
3. 범위를 정한다: 끊긴 지점 다음 절부터 **절 경계에서** 끊어 **최대 4쪽**(서로 다른 쪽 수 기준). 강의계획서 진도(5주 4·5장, 6주 5장 …)와 크게 어긋나면 보고서에 적는다.
4. 범위의 절을 개념 단위(소절 `4.1.2`나 `n` 항목 1~2개)로 묶어 토픽 후보를 만든다.
5. 기출·웹과제 용어를 찾는다. `TERMS`는 토픽 후보의 핵심 용어(한국어, `|`로 구분)다.
   ```bash
   REPO=… CH="4" TERMS="양성잡종|독립의 법칙|불완전우성" python3 - <<'EOF'
   import fitz, json, os, unicodedata as u
   repo, terms = os.environ["REPO"], os.environ["TERMS"].split("|")
   texts = {}
   src = os.path.join(repo, "23, 24 소스")
   for ch in os.environ["CH"].split():
       for n in os.listdir(src):
           name = u.normalize("NFC", n)
           if name.endswith(".pdf") and name.split("강", 1)[0] == ch:
               texts[name] = "".join(p.get_text() for p in fitz.open(os.path.join(src, n)))
       bank = os.path.join(repo, "웹과제", f"{ch}장", "questions.json")
       if os.path.exists(bank):
           texts[f"웹과제/{ch}장"] = json.dumps(json.load(open(bank, encoding="utf-8")), ensure_ascii=False)
   print("자료:", *texts or ["없음"])
   for t in terms:
       print(t, "→", ", ".join(k for k, v in texts.items() if t in v) or "없음")
   EOF
   ```
   합본 텍스트는 2단 조판이 섞이고 정답 표시가 사라지지만, 용어가 있는지만 보므로 텍스트로 충분하다. 결과는 manifest `exam_terms`에 쓴다.
6. 교과서 쪽을 찾는다. 교과서 PDF는 **스캔본이라 텍스트가 없다**(`get_text()`가 빈 문자열). 장 PDF 전체를 작은 PNG로 렌더링해 눈으로 훑는다.
   ```bash
   REPO=… RUN=… CH=04 python3 - <<'EOF'
   import fitz, os, unicodedata as u
   def find(d, name):  # NFD 폴더명도 찾는다
       return next(os.path.join(d, n) for n in os.listdir(d) if u.normalize("NFC", n) == name)
   book = find(find(os.environ["REPO"], "교과서"), "생명과학_기초와_응용_2판")
   f = next(os.path.join(book, n) for n in sorted(os.listdir(book))
            if u.normalize("NFC", n).startswith(os.environ["CH"] + "장_") and n.endswith(".pdf"))
   out = os.path.join(os.environ["RUN"], "work", "textbook-pages")
   os.makedirs(out, exist_ok=True)
   for i, page in enumerate(fitz.open(f), 1):
       page.get_pixmap(dpi=50).save(os.path.join(out, f"p{i:02d}.png"))
   print(f)
   print(out, len(os.listdir(out)), "쪽")
   EOF
   ```
   Read 도구로 `RUN/work/textbook-pages/pNN.png`를 보고, 범위의 절 제목이 있는 쪽(링크 `#page=N`의 N = 파일 번호)과 그 절의 그림(`그림 4.3` 같은 번호)이 있는 쪽을 적는다. 글자가 작아 안 읽히는 쪽만 dpi 140으로 다시 렌더링한다.
7. 참고 그림을 준비한다. 토픽 후보 중 강의노트나 교과서가 **그림으로 설명하는** 개념(분열 단계, 교배 결과, 구조도 등)을 고르고, 6에서 찾은 그림 쪽을 쓴다.
   토픽마다 쪽 하나를 골라 참고 PNG로 렌더링한다. 이 PNG는 작성자와 리뷰어가 보는 **참고용**이다. 저장소나 산출물(`예습노트/`)에 넣지 않는다.
   ```bash
   RUN=… PDF="<교과서 장 PDF 절대 경로>" FIGS="s1-dihybrid=12 s2-meiosis=15" python3 - <<'EOF'
   import fitz, os
   out = os.path.join(os.environ["RUN"], "work", "textbook-figs")
   os.makedirs(out, exist_ok=True)
   doc = fitz.open(os.environ["PDF"])
   for pair in os.environ["FIGS"].split():
       tid, page = pair.split("=")
       path = os.path.join(out, f"{tid}.png")
       doc[int(page) - 1].get_pixmap(dpi=150).save(path)
       print(path)
   EOF
   ```
   그림 번호(예: `그림 4.3`)는 manifest 토픽의 `figure_ref`에 쓴다. 교과서에 대응 그림이 없고 강의노트 쪽에 그림이 있으면 `PDF`를 강의노트로 바꿔 렌더링하고 `figure_ref`를 `"강의노트 4장 p3 그림"`으로 쓴다. 둘 다 없으면 `figure_ref`를 쓰지 않는다.
8. 이전 정리노트(`복습노트/*/정리노트_*.md`)에서 이 범위가 기대는 선수 개념을 하나 찾는다("미리 알아둘 것"과 링크에 쓴다).

### 2. manifest
- `RUN/manifest.json`을 쓴다. 규칙은 `references/manifest-guide.md`.
- 검증: `python3 "$SKILL/scripts/preview_manifest.py" "$RUN/manifest.json"` → `OK`

### 3. 작성
- 섹션마다 작성자 1명을 **한 메시지에서 병렬로** 띄운다. 브리프는 `references/content-rules.md`.
- 모델은 opus, `lite`이면 sonnet. 리뷰어도 같은 규칙이다.
- 브리프의 `<…>` 자리에 실제 경로, 섹션 id·제목, 그 섹션 토픽의 `links` 목록, 교과서 파일과 쪽 번호, 그 섹션의 그림 토픽(`figure_ref`와 참고 PNG `RUN/work/textbook-figs/<토픽id>.png`)을 채운다. 그림 토픽이 없으면 "그림 토픽 없음"이라고 적는다.

### 4. 조립
- **처음 조립할 때만** 기존 예습노트를 백업한다(다시 조립할 때는 하지 않는다. 스킬이 만든 초안이 백업에 섞이기 때문이다).
  ```bash
  python3 "$SKILL/scripts/preview_files.py" backup --repo "$REPO" --date <MMDD> --run "$RUN"
  ```
  종료 코드가 1이면 조립하지 말고 원인을 고친다.
- 조립:
  ```bash
  python3 "$SKILL/scripts/preview_assemble.py" --run "$RUN" --out "$REPO/예습노트/<MMDD>"
  ```
  "다른 slug의 예습노트가 남아 있어요" 경고가 나오면 지우지 말고 보고서 "미해결"에 적는다.

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/preview_check.py" --manifest "$RUN/manifest.json" --note "$REPO/예습노트/<MMDD>/<예습노트>.html"
```
- `FAIL`이면 Problem의 `where`(토픽·섹션 id)로 담당 작성자를 찾아 문제 목록을 보낸다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- `topic-long`·`eli5-long`·`listen-long`은 "줄여 주세요"로 보낸다. 내용을 다른 토픽으로 옮기지 말고 덜 중요한 문장을 뺀다.
- `figure`·`figure-source`는 참고 PNG를 보고 SVG를 그리거나 figcaption 출처를 채우게 한다. `textbook-image`는 `<img>`를 지우고 SVG로 다시 그리게 한다.
- `exam-mark`는 manifest `exam_terms`와 들을 때 포인트를 맞추게 한다. 배지를 지우는 것으로 맞추지 않는다(1단계 5의 결과가 근거다).
- 고친 뒤 4단계(조립)부터 다시 한다. 최대 2회, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰 (`lite`면 sonnet)
- 리뷰어 1명. 브리프는 `references/review-prompt.md`. 참고 PNG 폴더(`RUN/work/textbook-figs/`)도 넘긴다.
- Critical·Important는 모두, Minor는 쉬운 것만 고친다. 작성자별로 한 번에 모아 한 번만 수정 요청한다. 수정 후 4~5단계를 다시 한다.

### 7. 브라우저 검증
- `references/browser-check.md`대로 한다(KaTeX 오류 0, 남은 `$` 없음, 720px·375px 가로 넘침 없음, 720×900에서 토픽 한 화면, 기출 배지 수, 다크모드, 콘솔 오류).
- 결함은 5단계와 같은 방식으로 되돌린다(최대 2회 규칙에 포함). 끝나면 서버를 종료한다.

### 8. MD 변환
```bash
python3 "$SKILL/scripts/preview_md.py" "$REPO/예습노트/<MMDD>/<예습노트>.html" --check
```
`OK`가 나와야 한다. 누락은 대부분 조각의 마크업 문제다. 조각을 고치고 4단계부터 다시 한다.

### 9. 보고
```
## 예습노트 <MMDD> 완료
- 파일: 예습노트/<MMDD>/… (html 1, md 1, figures_<MMDD>/ N개)
- 범위: <N장 pA–pB> (시작: 정리노트_<range> 끊긴 지점 "…"), 토픽 M개
- 기출 표시: 토픽 K개 (용어: …, 근거: 23·24 N강 합본 / 웹과제 N장)
- 그림: 토픽 F개 (따라 그린 그림: 그림 4.3, …) / 대응 그림을 못 찾은 개념: …
- 스킬이 정한 사항: slug, 섹션 구성, 범위 끝을 정한 이유(절 경계), 교과서 보충으로 넣은 것과 이유, 뺀 내용과 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 예습노트/<MMDD> && git commit -m "docs(notes): add preview note <MMDD>"
```
실행 폴더 경로(`RUN`)와 백업 경로(있으면)도 적는다.

## 오류 처리
| 상황 | 동작 |
|---|---|
| 저장소가 아님 | 알리고 멈춤 |
| 수업이 이미 끝남(STT 있음) / 예습노트가 이미 있음 / 정리노트·쪽 태그 없음 / 장 PDF 없음 | `pick` 메시지를 보여 주고 멈춤 |
| 강의노트 텍스트 추출 실패 | Read 도구로 PDF를 읽고 보고서에 표시 |
| 기출 합본·웹과제 bank가 없음 | `exam_terms` 없이 진행하고 보고서에 표시 |
| 그림으로 설명하는 개념인데 교과서·강의노트에서 대응 그림을 못 찾음 | `figure_ref` 없이 진행하고 보고서에 표시 |
| 포트 사용 중 | 다른 빈 포트 사용 |
| 백업 실패 | 조립하지 않고 원인을 고침 |
| 검사 2회 실패 | 멈추지 않고 나머지 단계를 끝낸 뒤 "미해결"로 보고 |
