# 복습문제 해설 번호와 자동 스크롤 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습문제 선택지 아래 해설의 중복 선두 번호를 숨기고, 첫 답 선택 직후 내 선택과 정답 선지를 함께 볼 수 있게 한다.

**Architecture:** 기존 정적 HTML과 채점 모델을 유지한다. 공통 JavaScript가 해설 DOM을 선택지 아래로 옮길 때 표시 텍스트의 선두 번호만 제거하고, 답 선택 뒤 펼쳐진 카드의 실제 높이를 측정해 왼쪽 `.content`만 스크롤한다. 기존 Python 설치기를 재실행해 8개 HTML의 내장 스크립트를 갱신한다.

**Tech Stack:** Python 3 표준 라이브러리, vanilla JavaScript, Node 내장 test runner, Playwright 브라우저 검사. 새 패키지는 추가하지 않는다.

**Spec:** `docs/superpowers/specs/2026-09-29-bio-review-explanation-scroll-design.md` — 실행 전 함께 읽는다.

## Global Constraints

- 기존 복습문제 HTML 8개와 이후 생성본에 적용한다.
- 원본 문제·선지·해설 문장, 오른쪽 풀이 도움, Markdown, 채점 모델, localStorage 형식은 보존한다.
- 선지 번호는 펼친 해설의 선두에서만 제거한다. 해설 중간의 선지 참조는 남긴다.
- 자동 스크롤은 최초 답 선택 때만 실행한다. 복원·해설 재토글·다시 풀기에는 실행하지 않는다.
- 화면보다 긴 콘텐츠는 두 선지 버튼 표시를 우선하고, 버튼 둘도 안 들어가면 내 선택 버튼을 중앙에 둔다.
- 작업 전 `git status --short`로 기존 변경을 확인한다. 미추적 `tmp/`, `videos/`, 다른 계획 문서에는 손대지 않는다.
- Windows PowerShell에서 명령을 개별 실행한다. 아래 상대 경로는 저장소 루트 기준이다.

## Review Focus

1. `(1)`과 `A.`로 시작하는 해설, 중간에 `(2)`가 나오는 문장: 첫 식별자만 제거되고 본문 참조는 남아야 한다. Task 1의 Node 테스트.
2. 정답을 고른 카드가 펼쳐져 높이가 바뀌는 경우: 펼친 카드 자체를 기준으로 중앙에 둬야 한다. Task 2의 브라우저 테스트.
3. 내 선택과 정답 사이가 길어 한 화면에 모두 안 들어가는 경우: 두 버튼이 들어가면 함께 보여야 한다. Task 2의 브라우저 테스트.
4. 모바일처럼 버튼 둘도 한 화면에 들어가지 않는 경우: 내 선택 버튼이 보이는 위치로 간다. Task 2의 브라우저 테스트.
5. 저장 답 복원, 해설 재토글, 리셋: 스크롤이 다시 움직이지 않아야 한다. Task 2의 브라우저 테스트.

---

## 파일 구조와 책임

| 파일 | 변경 책임 |
|---|---|
| `.agents/skills/bio-review-pack/assets/review-interaction.js` | 선두 번호 제거, 실패 시 복원, 최초 답 선택의 스크롤 계산 |
| `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs` | 번호 제거의 순수 함수 검사 |
| `.agents/skills/bio-review-pack/tests/browser_check_review.py` | 실제 레이아웃·스크롤·복원 동작 검사 |
| `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929}/복습문제_*.html` | 설치기가 갱신하는 내장 공통 코드 |

`review_interaction.py`는 수정하지 않는다. 현재 `--write`는 공통 CSS/JS를 읽어 기존 8개 파일에 다시 설치하며, 설치할 때 기존 블록을 먼저 제거한다([설치 함수](../../../.agents/skills/bio-review-pack/scripts/review_interaction.py)).

### Task 1: 펼친 해설의 선두 번호 제거

**Files:** Modify `.agents/skills/bio-review-pack/assets/review-interaction.js`; Test `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs`.

**Interfaces:**
- Consumes: `diagnostic`은 기존 `ol.steps > li`, `o.id`는 채점 모델의 숫자 또는 대문자 식별자.
- Produces: `stripDiagnosticPrefix(text: string, id: string): string`; `module.exports`에 추가. DOM 수정 전에 원본 첫 텍스트 노드 값을 저장한다.

- [ ] **Step 1: 실패하는 순수 함수 테스트 작성**

`test_review_interaction.cjs` 끝에 추가한다.

```js
test('펼친 해설의 선두 식별자만 제거', () => {
  assert.equal(api.stripDiagnosticPrefix('(1) 틀려요. 보기 (2)는 맞아요.', '1'),
    '틀려요. 보기 (2)는 맞아요.');
  assert.equal(api.stripDiagnosticPrefix(' A. 맞아요.', 'A'), '맞아요.');
  assert.equal(api.stripDiagnosticPrefix('(2) 다른 보기', '1'), '(2) 다른 보기');
  assert.equal(api.stripDiagnosticPrefix('번호 없는 해설', '1'), '번호 없는 해설');
});
```

- [ ] **Step 2: 실패 확인**

Run: `node .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Expected: 새 테스트가 `api.stripDiagnosticPrefix is not a function`으로 실패.

- [ ] **Step 3: 최소 구현**

`grade` 앞에 함수를 두고, 해설 이동 직전의 첫 텍스트 노드만 바꾼다. 현재 `positions` 보관 바로 뒤에 `const diagnosticTexts = [];`를 두고, 기존 `const diagnostic = diagnostics[o.diagnostic];` 다음에 아래 조각을 넣는다.

```js
function stripDiagnosticPrefix(text, id) {
  const match = text.match(/^\s*(?:\((\d+)\)|([A-Z])[.)])\s*/);
  return match && (match[1] || match[2]) === id ? text.slice(match[0].length) : text;
}

const first = diagnostic.firstChild;
if (first && first.nodeType === 3) {
  diagnosticTexts.push({node:first, text:first.textContent});
  first.textContent = stripDiagnosticPrefix(first.textContent, o.id);
}
```

기존 `catch`에서 원본 노드를 제자리에 돌리기 전에 `diagnosticTexts.forEach(p => { p.node.textContent = p.text; });`를 실행한다. 함수는 기존 `api`에도 넣는다. 이렇게 하면 런타임 초기화가 중간에 실패해도 원본 정적 해설이 복원된다.

- [ ] **Step 4: 통과 확인**

Run: `node .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Expected: 모든 Node 테스트 PASS.

- [ ] **Step 5: 커밋**

Run: `git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Run: `git commit -m "fix: remove repeated review explanation labels"`

### Task 2: 답 선택 뒤 두 선지를 배치하는 스크롤

**Files:** Modify `.agents/skills/bio-review-pack/assets/review-interaction.js`; Test `.agents/skills/bio-review-pack/tests/browser_check_review.py`.

**Interfaces:**
- Consumes: Task 1의 `controls`(`{id, button, ...}`), 기존 `choices[o.index]`, `selected`, `data.answer`.
- Produces: `scrollAnswerIntoView(scroller: Element, selectedLi: Element, answerLi: Element, selectedButton: Element, answerButton: Element): void`. 첫 답 클릭의 `paint()` 뒤 한 번 호출한다.

- [ ] **Step 1: 실제 브라우저에서 실패하는 테스트 작성**

`browser_check_review.py`에 아래 테스트를 추가한다. `element.evaluate('(e)=>e.click()')`를 사용해 Playwright의 클릭 전 자동 스크롤과 구현 스크롤을 구분한다.

```python
    def test_answer_scroll_and_diagnostic_labels(self):
        card = self.open('0910', 'p8')
        self.page.locator('.content').evaluate('(e) => { e.scrollTop = 0; }')
        card.locator('.review-choice').nth(0).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        state = self.page.evaluate('''() => {
          const sc = document.querySelector('.content');
          const card = document.querySelector('#p8');
          const buttons = [0, 1].map(i => card.querySelectorAll('.review-choice')[i].getBoundingClientRect());
          const viewport = sc.getBoundingClientRect();
          return {scroll:sc.scrollTop, visible:buttons.every(b =>
            b.top >= viewport.top && b.bottom <= viewport.bottom),
            text:card.querySelector('.review-diagnostic:not([hidden])').textContent.trim()};
        }''')
        self.assertGreater(state['scroll'], 0)
        self.assertTrue(state['visible'])
        self.assertFalse(state['text'].startswith('(1)'))

    def test_correct_answer_center_and_no_retoggle_scroll(self):
        card = self.open('0910', 'p8')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        center_gap = self.page.evaluate('''() => {
          const sc=document.querySelector('.content').getBoundingClientRect();
          const li=document.querySelector('#p8 .choices > li:nth-child(2)').getBoundingClientRect();
          return Math.abs((li.top+li.bottom-sc.top-sc.bottom)/2);
        }''')
        self.assertLess(center_gap, 24)
        self.page.locator('.content').evaluate('(e) => { e.scrollTop = 0; }')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        self.assertEqual(self.page.locator('.content').evaluate('(e) => e.scrollTop'), 0)
```

같은 파일에 화면 높이별 대체 경로 테스트를 추가한다. 작은 화면의 선택·정답 버튼이 실제로 한 화면에 들어가는지는 측정값으로 판정한다.

```python
    def test_small_viewport_fallback(self):
        for height in (480, 240):
            with self.subTest(height=height):
                ctx = self.browser.new_context(viewport={'width': 375, 'height': height})
                page = ctx.new_page()
                try:
                    page.goto(self.url('0910', 'p8'))
                    page.locator('#p8 .review-choice').nth(4).evaluate('(e) => e.click()')
                    page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                    state = page.evaluate('''() => {
                      const sc=document.querySelector('.content').getBoundingClientRect();
                      const b=document.querySelectorAll('#p8 .review-choice');
                      const a=b[4].getBoundingClientRect(), z=b[1].getBoundingClientRect();
                      const fits=Math.max(a.bottom,z.bottom)-Math.min(a.top,z.top) <= sc.height-32;
                      const visible=r => r.top >= sc.top-2 && r.bottom <= sc.bottom+2;
                      return {fits, both:visible(a)&&visible(z), selected:visible(a)};
                    }''')
                    self.assertTrue(state['both'] if state['fits'] else state['selected'])
                finally:
                    ctx.close()
```

저장 답 복원 검사는 아래 독립 테스트로 추가한다. 해설 재토글은 위 `test_correct_answer_center_and_no_retoggle_scroll`이 검사한다.

```python
    def test_restored_answer_does_not_scroll(self):
        card = self.open('0910', 'p8')
        card.locator('.review-choice').nth(1).evaluate('(e) => e.click()')
        self.page.reload()
        expect(card.locator('.review-choice').nth(1)).to_have_attribute('data-selected', 'true')
        self.page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        self.assertEqual(self.page.locator('.content').evaluate('(e) => e.scrollTop'), 0)
```

- [ ] **Step 2: 실패 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py`
Expected: 새 스크롤·번호 테스트가 실패. 브라우저 설치 오류는 테스트 실패와 구분해 환경을 확인한다.

- [ ] **Step 3: 최소 구현**

공통 JS의 `mount` 안에 아래 함수를 추가하고 첫 답 클릭의 `paint();` 직후, `emit(...)` 직전에 호출한다. `choiceById`는 `controls`와 `options`의 동일한 순서를 이용해 찾는다.

```js
function scrollAnswerIntoView(scroller, selectedLi, answerLi, selectedButton, answerButton) {
  if (!scroller || !selectedLi.getClientRects().length) return;
  const viewport = scroller.getBoundingClientRect();
  const height = scroller.clientHeight;
  const margin = 16;
  const span = (a, b) => {
    const x = a.getBoundingClientRect(), y = b.getBoundingClientRect();
    return {top: Math.min(x.top, y.top), bottom: Math.max(x.bottom, y.bottom)};
  };
  let target = span(selectedLi, answerLi);
  if (target.bottom - target.top > height - 2 * margin)
    target = span(selectedButton, answerButton);
  if (target.bottom - target.top > height - 2 * margin)
    target = span(selectedButton, selectedButton);
  scroller.scrollTop += (target.top + target.bottom - viewport.top - viewport.bottom) / 2;
}

const selectedOption = options.find(o => o.id === selected);
const answerOption = options.find(o => o.id === data.answer);
const selectedControl = controls.find(c => c.id === selected);
const answerControl = controls.find(c => c.id === data.answer);
win.requestAnimationFrame(() => {
  if (!card.isConnected || !card.getClientRects().length) return;
  scrollAnswerIntoView(root.querySelector('.content'),
    choices[selectedOption.index], choices[answerOption.index],
    selectedControl.button, answerControl.button);
});
```

오직 `selected = c.id; ... paint();`가 실행되는 첫 답 클릭 분기에 이 호출을 둔다. 저장 답의 `paint()`와 이미 답한 뒤의 `paintDisclosure()` 경로에는 두지 않는다. 애니메이션과 경쟁하지 않도록 즉시 위치를 설정한다.

브라우저 테스트는 배포 HTML에 내장된 공통 JS를 실행하므로, 구현 직후 아래 명령으로 8개 HTML을 갱신한 다음 테스트를 실행한다. 갱신된 HTML은 Task 3에서 범위와 멱등성을 확인하고 커밋한다.

Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write`

- [ ] **Step 4: 통과 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py`
Expected: 새 테스트와 기존 브라우저 테스트 PASS. 정답 카드가 문서 끝에 가까워 중앙 배치가 스크롤 경계로 제한되면 테스트 문항을 중앙 배치가 가능한 카드로 바꾸고, 끝 경계는 별도 단언으로 확인한다.

- [ ] **Step 5: 커밋**

Run: `git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/browser_check_review.py`
Run: `git commit -m "feat: scroll selected and answer choices into view"`

### Task 3: 기존 8개 HTML 갱신 및 회귀 확인

**Files:** Modify `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929}/복습문제_*.html`; Test existing `.agents/skills/bio-review-pack/tests/test_review_interaction.py` and `browser_check_review.py`.

**Interfaces:**
- Consumes: Task 1·2에서 갱신한 공통 JS와 기존 `review_interaction.py install()`.
- Produces: 각 HTML 안에 동일한 최신 `review-interaction` 블록. 원본 카드와 내장 모델은 그대로 유지한다.

- [ ] **Step 1: 갱신 전 범위 확인**

Run: `git status --short`
Run: `rg --files 복습노트 -g '복습문제_*.html'`
Expected: 대상 HTML 8개. 기존 미추적 파일은 보존한다.

- [ ] **Step 2: 설치기 실행**

Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write`
Expected: 각 파일에 `errors: []`. Task 2에서 이미 갱신했다면 추가 변경이 없어야 한다. 이 명령은 카드 원문을 재작성하지 않고 내장 블록을 교체한다.

- [ ] **Step 3: 회귀 검사**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_review_interaction.py`
Run: `node .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py`
Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --audit`
Expected: 모두 통과하고 모델 오류 0개.

- [ ] **Step 4: 멱등성과 변경 범위 확인**

Run: `git diff --stat`
Run: `git diff --check`
Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write`
Run: `git diff --stat`
Expected: 두 번째 설치에서 추가 변경이 없고, 변경 파일은 위의 공통 JS·테스트·HTML 8개·이 계획과 스펙뿐이다. 원본 문제 문구와 모델 JSON에는 차이가 없어야 한다.

- [ ] **Step 5: 커밋**

Run: `git add 복습노트/0901/복습문제_*.html 복습노트/0903/복습문제_*.html 복습노트/0908/복습문제_*.html 복습노트/0910/복습문제_*.html 복습노트/0915/복습문제_*.html 복습노트/0917/복습문제_*.html 복습노트/0922/복습문제_*.html 복습노트/0929/복습문제_*.html docs/superpowers/specs/2026-09-29-bio-review-explanation-scroll-design.md docs/superpowers/plans/2026-09-29-bio-review-explanation-scroll.md`
Run: `git commit -m "chore: update existing review question pages"`

## Self-review

- Spec의 번호 표시, 정답·오답 스크롤, 화면 높이 한계, 최초 답 선택만 적용, 기존·향후 문서 범위를 Task 1–3에 연결했다.
- 함수명 `stripDiagnosticPrefix`와 `scrollAnswerIntoView`, 카드·버튼 인자는 모든 단계에서 동일하다.
- Review Focus 1–5는 Task 1·2의 테스트에 대응한다.
- 실행 단계는 기존 미추적 작업을 건드리지 않는다.
