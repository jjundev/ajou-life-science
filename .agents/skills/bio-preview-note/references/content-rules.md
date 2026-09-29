# 예습노트 섹션 작성 규칙

## 작성자 브리프 (메인 에이전트가 섹션마다 1명, 병렬, model: opus / lite: sonnet, GPT이면 sol / lite: luna)

---
생명과학 예습노트의 섹션 `<sid>`(`<섹션 title>`)를 쓴다. 학생이 **수업을 들으면서 옆에 띄워 보는** 노트다. 짧게 쓴다.

- 읽기: `<SKILL>/references/content-rules.md`(이 파일 전체)
- 계약: `<RUN>/manifest.json`의 섹션 `<sid>` — 토픽 id·제목·`slides`·`required_terms`·`exam_terms`·`layers`·`supp`를 정확히 따른다.
- 링크: 이 섹션 토픽의 `links` `<이 섹션의 links 목록>`을 그 토픽 안에 `<a href="…">`로 넣는다. `href`는 글자 그대로.
- 근거: `<RUN>/slides.txt`(`=== N장 pK ===` 구획), 필요하면 교과서 `<RUN>/repo/교과서/생명과학_기초와_응용_2판/<0N장_…pdf>` <쪽> (스캔본이라 텍스트가 없다. `<RUN>/work/textbook-pages/pNN.png`를 Read 도구로 보고, 작으면 그 쪽만 dpi 140 PNG를 `<RUN>/work/`에 렌더링해 읽는다)
- 그림: <그림 토픽 id → figure_ref, 참고 PNG `<RUN>/work/textbook-figs/<토픽id>.png` 목록, 없으면 "그림 토픽 없음">. 참고 PNG를 Read 도구로 보고 아래 "교과서 그림 따라 그리기"대로 SVG를 그린다. PNG를 복사하거나 `<img>`로 넣지 않는다.
- 출력: `<RUN>/sections/<sid>.html` **한 파일만**. `<section>`/`<h2>`는 쓰지 않는다(조립기가 감싼다). 임시 파일은 `<RUN>/work/`에만.
- 자기 검사(끝내기 전): `required_terms`가 문자 그대로 있는지, 쪽 태그가 manifest `slides`와 글자 그대로 같은지(범위는 en dash `–`), 토픽 본문 600자 이하(공백·그림 제외), 쉽게 말하면 2문장 이하이고 전문용어가 없는지, 들을 때 포인트 2항목 이하이고 "~하실 거예요" 같은 예측이 없는지, `exam_terms`가 있는 토픽만 기출 배지가 있고 그 용어가 같은 항목에 있는지, 그림 방향·레이블이 강의노트와 맞는지, `figure_ref` 토픽은 쉽게 말하면 레이어에 SVG 1개가 있고 figcaption에 `figure_ref` 글자와 "다시 그렸어요"가 있는지, 단계 순서·배치·화살표 방향·표지 이름이 참고 PNG와 같은지, 이모지 없음, `layers`가 빈 목록이 아닌 토픽마다 맨 끝에 `<div class="sum" hidden>`.
- 보고: 파일 경로, 토픽별 한 줄, 강의노트에 있었지만 뺀 것과 이유.
---

## 범위
- 강의노트에 있는 내용만 설명한다. 강의노트에 없는 설명(교과서의 예시·배경)은 `supp`가 `true`인 토픽의 보충 레이어에만 쓴다.
- 교수님 말씀이나 수업 중 강조는 아직 모르므로 **추측해서 쓰지 않는다**.

## 토픽 마크업 (이 순서)
```html
<article class="topic" id="…"><h3>…</h3><div class="tags"><span class="tag slide">4장 p3–p4</span></div>
  <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">한 문장 비유</p> …그림(figure_ref 토픽은 SVG 1개)… </div>
  <div class="layer formal"><span class="layer-title">정확히 말하면</span> …정의 목록 / 단계 / 비교표… </div>
  <div class="layer listen"><span class="layer-title">들을 때 포인트</span><ul><li>…</li></ul></div>   ← manifest layers에 listen이 있을 때만
  <div class="layer supp"><span class="badge supp">교과서 보충</span> … </div>                              ← manifest supp=true만
  <div class="sum" hidden>…페이지 요약…</div>                                                          ← layers가 빈 목록이 아닌 토픽만, 맨 끝
</article>
```
- 레이어 제목과 배지 글자는 위와 글자 그대로 쓴다. `layer prof`, `layer warn`은 쓰지 않는다(검사 실패).
- 쪽 태그 span 안에는 manifest `slides` 글자만 쓴다(검사기가 정확히 비교한다). `slides`가 빈 문자열인 토픽은 `<div class="tags">`를 생략한다. 날짜 태그(`tag date`)는 쓰지 않는다(아직 듣지 않은 수업이라서).
- 토픽은 그것만 읽어도 이해되게 쓰고, 앞 토픽은 `<a href="#토픽id">토픽 제목</a>`으로 잇는다.
- "미리 알아둘 것"(`s0`) 토픽: 이 범위를 따라가려면 필요한 선수 개념 하나. 이전 정리노트 링크를 건다.
- "한눈에 보기"(마지막 섹션): `-cheatsheet`는 표(`<div class="table-wrap"><table>`), `-links`는 `<ul><li><a>`.

## 분량 (검사기가 센다)
- 토픽 본문 **600자 이하**: 레이어 안 글자만 센다. 공백, `$…$` 수식, 그림, 레이어 제목, 배지, 태그, 요약 패널은 빼고 센다.
- **한 화면**: 토픽 하나가 720×900 창에서 스크롤 없이 보여야 한다(브라우저 검사). 표·목록·그림이 많으면 600자 안이어도 넘친다. 그림이 있는 토픽은 글을 300자 안팎으로 줄인다.
- **쉽게 말하면**: 2문장 이하("."·"?"·"!" 뒤 공백으로 나눈다), 전문용어 없이 일상 비유로. manifest `figure_ref`가 있는 토픽(강의노트나 교과서가 그림으로 설명하는 개념)은 이 레이어에 인라인 SVG 1개를 넣는다. 다른 토픽은 그림 없이 쓴다(넣더라도 1개까지, 검사기가 센다).
- **정확히 말하면**: 강의노트의 정의와 과정을 쓴다. 형식은 내용에 맞춰 하나를 고른다.
  - 용어 정의: `<dl><dt>불완전우성(incomplete dominance)</dt><dd>한 줄 뜻</dd></dl>`
  - 과정: `<ol><li>단계</li></ol>` (5단계 이하)
  - 헷갈리는 두 개념: 비교표 `<div class="table-wrap"><table>` (3행 이하)
  - 비율·수치는 본문 글자로(예: 9:3:3:1). TeX는 식이 꼭 필요할 때만 `$…$`.
- **들을 때 포인트**: 2항목 이하. 학생이 수업 중에 **할 일**을 쓴다: "~가 나오면 ~를 확인해 보세요", "~와 비교해 보세요". 교수님이 무엇을 말할지 예측하지 않는다("설명하실 거예요", "강조하실 거예요"는 검사 실패).
- **기출 배지**: manifest 토픽에 `exam_terms`가 있을 때만, 들을 때 포인트의 한 항목을 `<li><span class="badge exam">기출</span> …</li>`로 시작하고 그 항목에 `exam_terms` 용어를 **모두 글자 그대로** 쓴다. 예: `<li><span class="badge exam">기출</span> 독립의 법칙이 나오면 정의를 그대로 받아 적어 두세요.</li>`. `exam_terms`가 없는 토픽에는 배지를 쓰지 않는다(검사 실패).
- 문체: "~해요" 체, 한 문장에 한 가지, 군더더기 수식어 없이. 전문용어는 처음 한 번 영어 병기(예: 양성잡종(dihybrid)).

## 페이지 요약 (`.sum`)
```html
<div class="sum" hidden>
  <p class="sum-lead">토픽 핵심 한 문장("~해요" 체)</p>
  <p class="panel-label">용어</p>
  <dl class="terms"><dt>용어(영어)</dt><dd>한 줄 뜻</dd></dl>
</div>
```
- 본문에 이미 나온 용어를 같은 표기로 1~2개. 용어가 없으면 "용어" 줄과 `dl`을 뺀다.

## 수식
- `$…$`, `$$…$$`만. 본문에 리터럴 `$` 금지. TeX 안 `<`, `>`, `&` 금지(`\lt`, `\gt`).

## SVG 그림
- `<figure class="figure"><svg id="fig-<kebab>" viewBox="…" role="img" aria-label="한국어 설명">…</svg><figcaption>…</figcaption></figure>`
- 색은 클래스로만: `fig-ink`, `fig-accent`, `fig-danger`(선만), `fig-dot`(채움), `fig-text`, `fig-muted`(글자). 하드코딩 색 금지.
- 글자 12~14px, SVG `<text>`에 `$` 금지. id는 페이지 전체에서 유일.
- `<text>`에는 `fig-text`·`fig-muted`만 쓴다. 선과 글을 짝지으려면 figcaption에 "파란 선(…)"처럼 적는다.
- 순서가 있는 그림(분열 단계, 세대)은 왼쪽→오른쪽으로 그리고, 단계 이름이 강의노트와 같은지 확인한다.

### 교과서 그림 따라 그리기 (`figure_ref` 토픽)
- 교과서 그림을 **그대로 넣지 않고**, 참고 PNG를 보고 **구조만** 따라 SVG로 단순하게 다시 그린다. 따를 것: 단계 순서, 배치(위아래·좌우), 화살표 방향, 표지 이름.
- 표지 이름은 교과서·강의노트와 **같은 용어**로 쓴다(예: "전기 I", "상동염색체"). 새 이름을 만들지 않는다.
- 세부 장식(질감, 그림자, 입체 표현, 배경 사진, 번호가 없는 부가 설명)은 뺀다. 도형은 사각형·원·선·화살표로 충분하다.
- 가로로 넓게(viewBox 가로:세로 4:1 안팎) 그린다. 교과서 그림이 세로로 길면 단계를 가로 한 줄로 펼친다.
- figcaption에 한 문장 설명과 출처를 쓴다: "… 교과서 그림 4.3을 단순하게 다시 그렸어요." 강의노트 그림이면 "강의노트 4장 p3 그림을 단순하게 다시 그렸어요." `figure_ref` 글자가 그대로 들어가야 한다.
- 색은 위의 `fig-*` 클래스만 쓴다(교과서 색을 옮기지 않는다). 그래야 다크모드에서도 보인다.
- 그림이 있는 토픽은 글을 300자 안팎으로 줄여 720×900 한 화면에 맞춘다.
- 그림은 가로로 넓게(viewBox 가로:세로 4:1 안팎) 그려 한 화면 높이를 아낀다.
- 위젯(`class="widget"`)은 만들지 않는다.
