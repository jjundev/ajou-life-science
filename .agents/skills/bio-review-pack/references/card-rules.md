# 문제 카드 규칙

## 작성자 브리프 (메인 에이전트가 카드 10개당 1명, 병렬, model: opus / lite: sonnet)

---
생명과학 복습문제 카드 `<담당 카드 id>`를 쓴다.

- 읽기: `<SKILL>/references/card-rules.md`(이 파일 전체), `<SKILL>/references/problem-selection.md`의 원칙과 4절, `problem-selection.md` 6절(변형 연습 카드를 맡았을 때)
- 계약: `<RUN>/manifest.json`의 `problems` 중 담당 카드 — id, `source`, `anchor`, `level`, `date`, `terms`, `answer`를 그대로 따른다.
- 금지어: `<forbidden 목록>` — 카드 어디에도 쓰지 않는다. "다음 시간에 배울 …" 같은 예고도 쓰지 않는다.
- 근거: 원문 위치 `<RUN>/problem-pages.txt`(기출 PNG는 `<RUN>/work/exam/`), 웹과제 bank `<RUN>/repo/웹과제/<N>장/questions.json`, 정답 대조 `<RUN>/key-check.md`, 변형 설계 `<RUN>/variants.md`, 정리노트 토픽 제목은 manifest.
- 출력: `<RUN>/cards/<pid>.html` 문제마다 한 파일, 기출 그림은 `<RUN>/figures/<pid>.png`(웹과제 SVG 그림은 파일로 만들지 않고 카드에 인라인). 다른 곳에 쓰지 않는다.
- 임시·보조 파일은 `<RUN>/work/` 아래에만 둔다. 저장소와 `<RUN>` 밖(scratchpad 루트, `/tmp` 등)에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 연다.
- 확인용으로 브라우저 탭을 열었으면 보고 전에 모두 닫는다(메인 에이전트의 브라우저 검사가 탭 수 제한에 걸린다).
- 자기 검사: 카드별 `terms`가 글자 그대로 있는지, `정답:` 줄이 `answer`와 같은지, 모든 보기에 진단이 있는지, 원문 문항이면 문제와 보기가 원문과 글자까지 같은지(줄바꿈 흔적만 고친다), 변형이면 `RUN/variants.md`의 혼동 묶음을 겨냥하는지, 원문자(①~⑳)와 금지어와 STT 녹음 시각이 하나도 없는지, 기출 그림이면 `<img src>`가 `.assets/figures_<range>/<pid>.png`이고 그 파일을 `<RUN>/figures/`에 만들었는지, 웹과제 그림이면 SVG가 인라인이고 모든 `id`에 `<pid>-` 접두어가 붙었으며 `explained` SVG가 풀이 밖에 없는지, 변형 연습 그림(인라인 SVG)도 모든 `id`와 그 id를 가리키는 `aria-labelledby`·`url(#…)`에 `<pid>-` 접두어가 붙었는지. 어긋나면 고치지 말고 보고에 적는다.
- 보고: 카드별 한 줄(출처, 정답, 답안지 오류 여부), 풀이에 정리노트에 없는 사실이 필요했던 곳.
---

## 마크업
```html
<article class="card" id="pN" data-source="기출 3강 12">
  <h3>PN. 한 줄 제목</h3>
  <div class="problem"><p>…문제 원문…</p>
    <figure class="figure"><img src=".assets/figures_<range>/pN.png" alt="한국어 그림 설명"></figure>   ← 기출 그림 문항만
    <ul class="choices"><li>(1) …</li><li>(2) …</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>기출 3강 합본 12번 (PDF 3쪽)</details>
  <details class="hint" open><summary>힌트 보기</summary>…한두 문장…</details>
  <details class="solution"><summary>풀이 보기</summary>
    <ol class="steps"><li>(1) 틀려요. …</li><li>(2) 맞아요. …</li></ol>
    <p class="answer">정답: (2)</p>
    <p>인쇄된 답안지에는 (3)으로 표시되어 있지만 오류로 판단해요. …</p>   ← key-check.md에 있을 때만
  </details>
</article>
```
- 구조와 순서는 위와 같다: `<h3>` → `div.problem` → `details.original` → `details.hint` → `details.solution`. 블라인드 사본 스크립트가 이 순서에 기댄다.
- `data-source`는 manifest `source`와 글자까지 같다.
- 보기 번호: 기출은 `(1)`~`(5)`(원문 ①~⑤을 옮긴 것), 웹과제는 bank 보기 id 그대로 `A.`~`E.`, 변형 연습은 `(1)`~`(n)`. 원문 순서를 바꾸지 않는다.
- 웹과제 그림(SVG)은 `RUN/figures/`에 복사하지 않는다(`RUN/figures/`에는 기출 PNG만 둔다. `html2md.py`가 `.assets/figures_<range>/`의 SVG 파일을 지운다). bank `assets`의 `exam.path` SVG 원문을 `div.problem` 안 `<figure class="figure">`에 인라인으로 넣고 `aria-label`에 `exam.alt`를 쓴다. `explained.path` SVG는 해설이 들어 있으므로 `details.solution` 안에만 넣는다. 모든 `id`(와 그 id를 가리키는 `aria-labelledby`, `url(#…)`)에 `<pid>-` 접두어를 붙인다. 자세한 것은 `problem-selection.md` 2절.
- 웹과제 `statements` 항목(`{"type": "statements", "items": [{"id": "a", "text": "…"}, …]}`)은 문제 문단 다음에 `<ul>`로 싣고, 항목마다 bank id 그대로 `a.`~`d.` 라벨을 붙인다(`<li>a. …</li>`). 순서와 글자를 바꾸지 않는다.
- 원문 정보 보기: 출처, 문항 번호, PDF 쪽만 쓴다(웹과제는 `웹과제 1장 q01 (스크린샷 s01)`). 인쇄된 답은 여기에 쓰지 않는다.
- 변형 작성자는 `variants.md`의 수준과 최소 풀이 단계에 맞춘다. 인접 개념의 한 부분을 바꾼 오답을 우선하고, 숫자·생물·그림·발문 방향을 바꿔도 불필요한 추론 단계를 추가하지 않는다. 실제 필요한 단계가 설계와 다르면 메인에게 보고한다. 난이도 배지는 추가하지 않는다.
- 변형 연습(partC) 카드: `<h3>`를 `PN. [변형] 제목`으로 쓰고, 원문 정보 보기에는 "원문 기출이 아닌 생성 변형이에요. 다루는 혼동: …"과 근거 토픽을 쓴다. 문제·보기는 새로 쓰되 나머지 규칙(모든 보기 진단, 힌트, 풀이, `정답:` 줄, 수업과의 연결)은 같다.
- 쌍둥이 변형(`variants.md` 웹과제 유형 `쌍둥이`): 발문은 `형태` 칸의 원문 발문을 글자 그대로, 보기는 새로 쓴다. 원문 정보 보기에 "기출 N강 M번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: …"이라고 원문을 밝힌다. 풀이 마지막 단계("수업과의 연결" 앞)에 "원문 정답과 달라진 점: …" 한 줄을 쓴다.
- 낯선 참 진술(`variants.md` 표시 `+낯선참`): 그 보기 진단을 "맞아요. 수업 밖이지만 맞는 진술이에요(출처: 교재 N장 p.x). 확실히 틀린 보기를 먼저 찾아요."로 쓴다. 장 섞기(`+장섞기`): "수업과의 연결"에 앞선 팩 정리노트 토픽 링크(`../<range>/정리노트_<range>_<slug>.html#<토픽>`)를 붙인다.
- ㄱㄴㄷ 변형: 진술을 문제 문단 다음 `<ul>`에 `ㄱ.`~`ㄷ.` 라벨로 싣고, 보기 `(1)`~`(5)`는 조합(예: `(4) ㄱ, ㄴ`)으로 쓴다. 풀이는 진술마다 맞아요/틀려요를 먼저 쓰고 보기 진단으로 넘어간다.
- 풀이: **모든 보기**에 "맞아요/틀려요 + 이유 한 문장"을 쓴다. 웹과제는 `option_diagnostics`를 "~해요" 체로 다듬는다. 보기 없는 빈칸 문항은 채우는 이유를 한두 단계로 쓴다.
- 보기의 "항상", "늘", "반드시"는 반례를 찾아 판단하고, 풀이에 그 반례나 성립 조건을 적는다. 절대 표현이라서 틀렸다고만 쓰지 않는다.
- `key-check.md`가 모호하다고 적은 보기는 "맞아요/틀려요" 대신 "출제 의도로는 답이 아니지만 …"처럼 진단하고, `정답:` 줄 다음 문단에서 모호성을 공개한다.
- 풀이 마지막 단계에 "수업과의 연결"을 한 줄로 쓴다(어느 수업의 어떤 개념·강조 발언과 이어지는지). STT의 분:초, 시각 범위, 파트 번호는 학생용 문장에 쓰지 않는다.
- 답안지 오류와 공식 답 불일치는 `정답:` 줄 다음 문단에서 반드시 공개한다.
- 난이도·날짜 배지, 이모지, 장식 기호, 원문자는 쓰지 않는다. 문제 원문을 뺀 문장은 "~해요" 체로 쓴다.
- 템플릿이 카드 하나를 한 화면에 보여 준다. 카드는 다른 카드 없이도 풀 수 있게 쓴다.

## 그림 자르기 (기출)
PNG(dpi 170)에서 그림 영역의 픽셀 좌표를 확인한 뒤 PDF 좌표(pt = px × 72 / 170)로 바꿔 원본 PDF에서 바로 잘라낸다.
```bash
REPO=… RUN=… python3 - <<'EOF'
import fitz, os, unicodedata as u
src = os.path.join(os.environ["REPO"], "23, 24 소스")
name = next(n for n in os.listdir(src) if u.normalize("NFC", n).startswith("3강") and n.endswith(".pdf"))
page = fitz.open(os.path.join(src, name))[2]                  # 0부터 센다: PDF 3쪽
rect = fitz.Rect(40, 300, 300, 520)                            # pt 단위. 쪽 전체 크기는 page.rect
page.get_pixmap(dpi=170, clip=rect).save(os.path.join(os.environ["RUN"], "figures", "p7.png"))
EOF
```
보기에 답이 인쇄된 빨간 표시가 그림 안에 들어가지 않게 자른다. 들어가면 영역을 줄인다.

## 화면에 넣지 않는 안내 문구

- 문항 카드에 “답을 선택하면 …해설이 열려요”, “다른 보기도 눌러 …”, “여기를 눌러 …” 같은 **사용법·조작 안내 문장을 넣지 않는다.** 보기 버튼과 판정 문구(`review-status`), `내 선택`·`정답` 배지만으로 충분하다.
- `assets/review-interaction.js`·`.css`에 안내용 `<p>`(예: `review-help`)를 다시 추가하지 않는다. 새 상호작용을 만들 때도 화면에는 결과(판정·배지)만 보이고 설명 문장은 만들지 않는다.
- `tests/test_review_interaction.py`의 `test_assets_have_no_help_text`, `test_generated_packs_have_no_help_text`가 이 규칙을 강제한다.
