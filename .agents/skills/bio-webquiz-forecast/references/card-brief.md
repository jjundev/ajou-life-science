# 카드 작성자 브리프

---
생명과학 <N>장 웹과제 예상 세트 v<K>의 카드 `<담당 카드 id>`를 쓴다.

- 읽기: `{SKILL}/references/card-brief.md`(이 파일 전체), `{SKILL}/references/question-blueprint.md`, `.agents/skills/bio-review-pack/references/card-rules.md`의 "마크업" 절.
- 계약: `<SRC>/blueprint.md`의 담당 행(정답·유형·토픽·혼동·기출 출처·노트 앵커)과 `<SRC>/pack.json`의 `forbidden`.
- 근거: 정리노트 MD(`<노트 경로들>`), 기출 원문 `<RUN>/pool.json`.
- 출력: `<SRC>/cards/<pid>.html` 카드마다 한 파일. 다른 곳에 쓰지 않는다.
- 자기 검사: `python {SKILL}/scripts/build.py <SRC>`가 성공하고 `python {SKILL}/scripts/check.py <HTML>`에 담당 카드 id 줄이 없을 때까지 고친다(다른 작성자 카드의 문제는 무시).
- 보고: 카드별 한 줄(정답, 유형, 기출 출처), 노트에 없는 사실이 필요했던 곳.
---

## 마크업
```html
<article class="card" id="pN" data-source="예상 <N>장 N" data-types="부정형 계산">
  <h3>PN. [예상] 한 줄 제목</h3>
  <div class="problem"><p>발문</p>
    <figure class="figure"><svg viewBox="0 0 340 200" role="img" aria-label="…">…</svg></figure>   ← 그림 문항만
    <ul><li>ㄱ. …</li><li>ㄴ. …</li><li>ㄷ. …</li></ul>                                          ← ㄱㄴㄷ 문항만
    <ul class="choices"><li>A. …</li><li>B. …</li><li>C. …</li><li>D. …</li><li>E. …</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>…</details>
  <details class="hint"><summary>힌트 보기</summary>…</details>
  <details class="solution"><summary>풀이 보기</summary>
    <ol class="steps">
      <li>A. 맞아요/틀려요. 이유 한 문장.</li> … E까지
      <li>수업과의 연결: …(<a href="../../복습노트/<날짜>/정리노트_<날짜>_<slug>.html#<앵커>">정리노트 "토픽 제목"</a>).</li>
    </ol>
    <p class="answer">정답: X</p>
  </details>
</article>
```
- 제목: 새 문제 `PN. [예상]`, 기출그대로 `PN. [기출 예상]`, 기출쌍둥이·기출숫자 `PN. [기출 변형]`.
- `data-source`: 새 문제 `예상 <N>장 N`, 기출 카드는 `기출 <N>강 M 예상`.
- 부정형("옳지 않은 것") 카드는 정답 보기만 `틀려요`, 나머지 넷은 `맞아요`. 그 밖의 카드는 정답만 `맞아요`. ㄱㄴㄷ 카드는 진술 판정 줄(`<li>ㄱ. 맞아요. …</li>`)을 먼저 쓰고 A~E 진단을 쓴다.
- 기출그대로: 발문·보기 문장은 pool의 원문 그대로(줄바꿈 흔적만 고침), 보기 순서만 blueprint 정답 글자에 맞게 섞는다. 원문 정보: "기출 <N>강 합본 M번을 보기 순서만 바꿔 실은 예상 문제예요."
- 기출쌍둥이: 발문은 원문 그대로, 보기는 새로 써서 원문 정답과 다른 문장이 정답이 되게 한다. 풀이 마지막 단계 앞에 "원문 정답과 달라진 점: …" 한 줄.
- 기출숫자: 원문의 숫자·조건만 바꾸고 보기를 다시 계산한다.
- SVG: 클래스 `fig-ink`, `fig-accent`, `fig-dot`, `fig-text`, `fig-muted`만, 직접 색 금지, `viewBox` 너비 ≤ 360, `id`는 `pN-` 접두어.
- 쓰지 않는 것: `forbidden` 용어, 원문자 ①~⑳, 사용법 안내("답을 선택하면" 등), 모호성 문구(`모호`, `모두 가능`, `답이 하나`, `해석에 따라`, `복수 정답`), STT 녹음 시각. 생식세포의 성별처럼 발문에 없는 조건을 보기에서 가정하지 않는다.
