# 복습문제 채점 효과와 선택지 강조 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습문제에서 최초 답 선택 때 짧은 정오답 효과를 보여주고, 선택 보기와 정답 보기의 테두리를 분명하게 표시한다.

**Architecture:** 복습팩 생성 원본의 CSS와 JavaScript에 표시 동작을 추가한다. 기존 `grade()` 결과와 `paint()`의 상태 속성을 사용하고, 배포 스크립트로 같은 자산을 기존 8개 HTML에 다시 내장한다. 채점 모델과 저장 형식은 바꾸지 않는다.

**Tech Stack:** HTML, CSS 애니메이션, 바닐라 JavaScript, Python unittest, Playwright Chromium.

**Spec:** `docs/superpowers/specs/2026-09-29-bio-review-answer-feedback-design.md`

## Global Constraints

- 기존 복습문제 HTML 8개와 앞으로 생성하는 복습문제 HTML에 적용한다.
- 기존 문제, 정답, 해설, 점수 기록, 보기별 해설 접기·펼치기는 유지한다.
- 효과는 첫 답 선택에서만 재생한다. 저장 답 복원과 제출 후 보기별 해설 접기·펼치기에서는 재생하지 않는다.
- 모호한 문항에 이진 정오답 효과를 재생하지 않고 기존 `단일 정답 판정 주의`를 유지한다.
- `prefers-reduced-motion: reduce`에서 움직임을 없애고 정적 문구를 표시한다.
- 인쇄에서 효과와 강조 테두리를 숨긴다. JavaScript가 실패하거나 꺼져도 정적 문제와 풀이를 읽을 수 있어야 한다.
- 서버, 외부 애니메이션 라이브러리, 소리, 점수 화면을 추가하지 않는다.
- 원본 체크아웃의 수정 중인 0910 HTML을 덮어쓰지 않는다. 이 계획은 `codex/review-answer-feedback` 워크트리에서만 실행한다.

## Review Focus

1. 연속으로 두 문항에 답하기: 첫 효과의 타이머가 두 번째 효과를 조기 제거하지 않아야 한다. Task 2의 `test_feedback_replaces_previous_answer`로 확인한다.
2. 답을 고른 직후 다시 풀기: 이전 효과와 강조가 남지 않아야 한다. Task 2의 `test_feedback_reset_and_restore`로 확인한다.
3. 모호 문항에서 출제 의도상 답과 다른 보기 선택: 오답 색이나 틀림 효과로 단정하지 않아야 한다. Task 1과 2의 모호 문항 검사로 확인한다.
4. 동작 줄이기·좁은 화면: 위치가 뷰포트 안에 있고 움직임이 없어야 한다. Task 2의 `test_feedback_reduced_motion_and_mobile`로 확인한다.
5. 기존 HTML 8개와 새 생성물의 차이: 전부 같은 CSS/JS를 내장하고 문제 콘텐츠를 유지해야 한다. Task 3의 설치 멱등성·모델 검증으로 확인한다.

---

## File map

- `.agents/skills/bio-review-pack/assets/review-interaction.css`: 선택지 상태별 테두리와 화면 상단 효과의 유일한 스타일 원본.
- `.agents/skills/bio-review-pack/assets/review-interaction.js`: 채점 상태 속성과 효과의 생성·종료를 담당하는 유일한 런타임 원본.
- `.agents/skills/bio-review-pack/tests/browser_check_review.py`: 실제 화면 상태와 동작을 검사한다.
- `.agents/skills/bio-review-pack/tests/test_review_interaction.py`: 내장 자산과 설치 멱등성을 검사한다.
- `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929}/복습문제_*.html`: 배포 스크립트가 갱신하는 산출물. 문항 본문과 JSON 모델은 변경하지 않는다.

## Task 1: 선택 보기와 정답 보기의 상태별 테두리

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.css:14-15,26-33`
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js:143-164`
- Test: `.agents/skills/bio-review-pack/tests/browser_check_review.py`

**Interfaces:**
- Consumes: `grade(card, selected)`의 `correct | incorrect | ambiguous | null`; 기존 `data-selected`와 `data-result`.
- Produces: 보기 버튼의 `data-result="correct|selected|intended|uncertain|"`; Task 2는 이 속성을 바꾸지 않고 사용한다.

- [ ] **Step 1: 실패하는 브라우저 테스트 추가**

`TestReviewBrowser`에 아래 헬퍼와 메서드를 넣는다. 1·2번 작업에서는 실제 HTML을 아직 갱신하지 않으므로, 브라우저 응답에 현재 원본 자산을 내장해 검사한다. 파일에는 쓰지 않는다. 파일 상단에 `import review_interaction as ri`를 추가한다.

```python
def open_current_assets(self, date='0929', card='p1'):
    path = next((REPO / '복습노트' / date).glob('복습문제*.html'))
    url = self.url(date, card).split('#', 1)[0]
    source = ri.install(path.read_text(encoding='utf-8'), path.name)
    self.page.route(url, lambda route: route.fulfill(body=source, content_type='text/html'))
    return self.open(date, card)

def test_answer_borders_distinguish_correct_selected_and_ambiguous(self):
    card = self.open_current_assets('0929', 'p1')  # 정답 2번
    buttons = card.locator('.review-choice')
    buttons.nth(0).click()
    self.assertEqual(buttons.nth(0).get_attribute('data-result'), 'selected')
    self.assertEqual(buttons.nth(1).get_attribute('data-result'), 'correct')
    self.assertEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '3px')
    self.assertEqual(buttons.nth(1).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '3px')
    self.assertNotEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopColor'),
                        buttons.nth(1).evaluate('(e) => getComputedStyle(e).borderTopColor'))
    card.locator('.review-reset').click()
    self.assertEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopWidth'), '1px')
    card = self.open_current_assets('0929', 'p11')  # 모호 문항, 출제 의도상 답 3번
    buttons = card.locator('.review-choice')
    buttons.nth(0).click()
    self.assertEqual(buttons.nth(0).get_attribute('data-result'), 'uncertain')
    self.assertEqual(buttons.nth(2).get_attribute('data-result'), 'intended')
    self.assertNotEqual(buttons.nth(0).evaluate('(e) => getComputedStyle(e).borderTopColor'),
                        buttons.nth(2).evaluate('(e) => getComputedStyle(e).borderTopColor'))
```

- [ ] **Step 2: 실패 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py TestReviewBrowser.test_answer_borders_distinguish_correct_selected_and_ambiguous`

Expected: `1px` 테두리 검사 또는 `uncertain` 속성 검사에서 실패한다.

- [ ] **Step 3: 최소 구현**

`paint()`에서 기존 `data.result` 삼항식의 모호한 선택 분기만 바꾼다. `correct`와 `intended` 판정 순서는 유지한다.

```javascript
c.button.dataset.result = !answered ? '' : c.id === data.answer
  ? (data.mode === 'ambiguous' ? 'intended' : 'correct')
  : c.id === selected ? (data.mode === 'ambiguous' ? 'uncertain' : 'selected') : '';
```

기존 CSS의 1px 강조와 안쪽 선을 아래 규칙으로 교체한다. 글자 라벨은 그대로 둔다.

```css
.review-choice[data-result="correct"],
.review-choice[data-result="intended"] { border:3px solid var(--accent); }
.review-choice[data-result="selected"] { border:3px solid var(--danger); }
.review-choice[data-result="uncertain"] { border:3px solid var(--ink-2); }
@media print {
  .review-choice { border:0 !important; box-shadow:none !important; padding:0; }
}
```

테두리 규칙은 기존 `@media print` 안에 합치고, 중복된 `.review-choice` 인쇄 규칙은 하나만 남긴다. 정답을 고르면 `data-result="correct"`와 `data-selected="true"`가 같은 버튼에 남아 파란 테두리 하나로 표시된다.

- [ ] **Step 4: 통과 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py TestReviewBrowser.test_answer_borders_distinguish_correct_selected_and_ambiguous`

Expected: PASS. 이어서 `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_review_interaction.py -v`도 PASS.

- [ ] **Step 5: 커밋**

```powershell
git add .agents/skills/bio-review-pack/assets/review-interaction.css .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/browser_check_review.py
git commit -m "feat(review): distinguish selected and correct answer borders"
```

## Task 2: 화면 중앙 상단의 일회성 채점 효과

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.css`
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js:43-54,170-205`
- Test: `.agents/skills/bio-review-pack/tests/browser_check_review.py`

**Interfaces:**
- Consumes: `grade(data, selected)`의 `correct | incorrect | ambiguous`와 Task 1의 버튼 상태.
- Produces: 문서당 한 개의 `[data-review-feedback]` 영역. `showFeedback(result)`는 `correct | incorrect`를 받고, `clearFeedback()`은 활성 효과와 타이머를 제거한다. 영역은 `aria-hidden="true"`이며 채점 알림은 기존 `.review-status[role=status]`가 담당한다.

- [ ] **Step 1: 실패하는 브라우저 테스트 추가**

`TestReviewBrowser`에 다음 세 메서드를 추가한다. 타이머 검사는 `expect(...).to_have_count()`의 자동 대기를 이용한다.

```python
def test_feedback_once_for_first_answer_only(self):
    card = self.open_current_assets('0929', 'p1')
    card.locator('.review-choice').nth(1).click()
    feedback = self.page.locator('[data-review-feedback]')
    expect(feedback).to_have_attribute('data-result', 'correct')
    expect(feedback).to_contain_text('정답이에요')
    self.assertEqual(feedback.get_attribute('aria-hidden'), 'true')
    card.locator('.review-choice').nth(0).click()  # 해설만 펼침
    expect(feedback).to_have_attribute('data-result', 'correct')
    expect(feedback).to_have_count(0, timeout=2500)
    card = self.open_current_assets('0929', 'p11')
    card.locator('.review-choice').first.click()
    expect(self.page.locator('[data-review-feedback]')).to_have_count(0)

def test_feedback_replaces_previous_answer(self):
    card = self.open_current_assets('0929', 'p1')
    card.locator('.review-choice').first.click()
    expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'incorrect')
    self.page.wait_for_timeout(500)
    card = self.open_current_assets('0929', 'p2')
    card.locator('.review-choice').nth(4).click()  # p2의 정답 5번
    expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'correct')
    self.page.wait_for_timeout(650)
    expect(self.page.locator('[data-review-feedback]')).to_have_attribute('data-result', 'correct')
    expect(self.page.locator('[data-review-feedback]')).to_have_count(0, timeout=2500)

def test_feedback_reset_and_restore(self):
    card = self.open_current_assets('0929', 'p1')
    card.locator('.review-choice').first.click()
    expect(self.page.locator('[data-review-feedback]')).to_have_count(1)
    card.locator('.review-reset').click()
    expect(self.page.locator('[data-review-feedback]')).to_have_count(0)
    card.locator('.review-choice').nth(1).click()
    self.page.reload()
    expect(card.locator('.review-choice').nth(1)).to_have_attribute('data-selected', 'true')
    expect(self.page.locator('[data-review-feedback]')).to_have_count(0)
```

- [ ] **Step 2: 실패 확인**

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py TestReviewBrowser.test_feedback_once_for_first_answer_only TestReviewBrowser.test_feedback_replaces_previous_answer TestReviewBrowser.test_feedback_reset_and_restore`

Expected: `[data-review-feedback]`를 찾지 못해 실패한다.

- [ ] **Step 3: 효과 런타임 구현**

`mount()`의 `element` 함수 바로 아래에 문서당 공유 효과와 타이머를 둔다. 초기 DOM에는 효과 영역이 없다. `win.setTimeout` 콜백은 현재 영역만 지운다.

```javascript
let feedback = null;
let feedbackTimer = null;
let feedbackOwner = null;
function clearFeedback(owner = null) {
  if (owner !== null && owner !== feedbackOwner) return;
  if (feedbackTimer !== null) win.clearTimeout(feedbackTimer);
  feedbackTimer = null;
  if (feedback) feedback.remove();
  feedback = null;
  feedbackOwner = null;
}
function showFeedback(result, id) {
  if (result !== 'correct' && result !== 'incorrect') return;
  clearFeedback();
  feedback = element('div', 'review-feedback');
  feedback.dataset.reviewFeedback = '';
  feedback.dataset.result = result;
  feedback.setAttribute('aria-hidden', 'true');
  feedback.append(
    element('span', 'review-feedback-icon', result === 'correct' ? '✦' : '✕'),
    element('span', 'review-feedback-text', result === 'correct' ? '정답이에요' : '다시 확인해요')
  );
  root.body.append(feedback);
  feedbackOwner = id;
  feedbackTimer = win.setTimeout(clearFeedback, 1100);
}
```

최초 답 선택 분기에서 `paint()`와 `emit()` 뒤에 다음 호출을 넣는다. 제출된 답의 보기 접기·펼치기 분기와 복원 경로에는 넣지 않는다. `reset` 클릭의 `selected = null` 직전에 효과를 정리한다.

```javascript
showFeedback(grade(data, selected), id);
// reset 클릭 처리 안에서:
clearFeedback(id);
```

- [ ] **Step 4: 효과 CSS 구현**

스타일 원본에 다음 규칙을 추가한다. 효과는 상단 바 아래에 고정하고 본문 클릭을 막지 않는다.

```css
.review-feedback {
  position:fixed; top:calc(env(safe-area-inset-top) + 72px); left:50%; z-index:100;
  transform:translateX(-50%); width:max-content; max-width:calc(100vw - 32px);
  display:flex; align-items:center; gap:12px; padding:10px 16px;
  border:2px solid var(--line); border-radius:12px; background:var(--bg);
  color:var(--ink); font-weight:700; pointer-events:none;
  animation:review-feedback-in 180ms ease-out both;
}
.review-feedback[data-result="correct"] { border-color:var(--accent); }
.review-feedback[data-result="incorrect"] { border-color:var(--danger); }
.review-feedback-icon { position:relative; font-size:26px; line-height:1; }
.review-feedback[data-result="correct"] .review-feedback-icon { color:var(--accent); }
.review-feedback[data-result="incorrect"] .review-feedback-icon {
  color:var(--danger); animation:review-shake 320ms ease-in-out;
}
.review-feedback[data-result="correct"] .review-feedback-icon::before,
.review-feedback[data-result="correct"] .review-feedback-icon::after {
  content:""; position:absolute; left:50%; top:50%; width:4px; height:4px;
  border-radius:50%; background:currentColor;
  box-shadow:0 -15px currentColor, 15px 0 currentColor, 0 15px currentColor, -15px 0 currentColor;
  animation:review-burst 650ms ease-out both;
}
.review-feedback[data-result="correct"] .review-feedback-icon::after {
  transform:rotate(45deg); animation-delay:80ms;
}
@keyframes review-feedback-in {
  from { opacity:0; translate:0 -8px; } to { opacity:1; translate:0 0; }
}
@keyframes review-shake {
  0%,100% { translate:0; } 25%,75% { translate:-5px; } 50% { translate:5px; }
}
@keyframes review-burst {
  from { opacity:1; scale:.45; } to { opacity:0; scale:1.4; }
}
@media (prefers-reduced-motion: reduce) {
  .review-feedback, .review-feedback::before, .review-feedback::after,
  .review-feedback-icon, .review-feedback-icon::before, .review-feedback-icon::after {
    animation:none !important;
  }
  .review-feedback-icon::before, .review-feedback-icon::after { display:none; }
}
@media print { .review-feedback { display:none !important; } }
```

- [ ] **Step 5: 모바일·동작 줄이기·인쇄 테스트 추가**

```python
def test_feedback_reduced_motion_and_mobile(self):
    self.page.set_viewport_size({'width': 320, 'height': 568})
    self.page.emulate_media(reduced_motion='reduce')
    card = self.open_current_assets('0929', 'p1')
    card.locator('.review-choice').nth(1).click()
    box = self.page.locator('[data-review-feedback]').bounding_box()
    self.assertGreaterEqual(box['x'], 0)
    self.assertLessEqual(box['x'] + box['width'], 320)
    self.assertEqual(self.page.locator('.review-feedback-icon').evaluate('(e) => getComputedStyle(e).animationName'), 'none')
    self.page.emulate_media(media='print', reduced_motion='reduce')
    self.assertEqual(self.page.locator('[data-review-feedback]').evaluate('(e) => getComputedStyle(e).display'), 'none')
```

Run: `python .agents/skills/bio-review-pack/tests/browser_check_review.py TestReviewBrowser.test_feedback_reduced_motion_and_mobile`

Expected: PASS. 이어서 Step 1의 세 테스트와 기존 `test_wrong_reset_correct_restore`, `test_letter_negative_and_ambiguity`도 PASS.

- [ ] **Step 6: 커밋**

```powershell
git add .agents/skills/bio-review-pack/assets/review-interaction.css .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/browser_check_review.py
git commit -m "feat(review): show brief answer feedback"
```

## Task 3: 기존 8개 HTML 반영과 생성 경로 검증

**Files:**
- Modify: `복습노트/0901/복습문제_0901_Biomolecules_and_Cells.html`
- Modify: `복습노트/0903/복습문제_0903_Biomolecules_and_Cells.html`
- Modify: `복습노트/0908/복습문제_0908_Biomolecules_and_Cells.html`
- Modify: `복습노트/0910/복습문제_0910_Cells_and_Cellular_Respiration.html`
- Modify: `복습노트/0915/복습문제_0915_Cellular_Respiration_and_Photosynthesis.html`
- Modify: `복습노트/0917/복습문제_0917_Cell_Division.html`
- Modify: `복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.html`
- Modify: `복습노트/0929/복습문제_0929_Heredity.html`
- Test: `.agents/skills/bio-review-pack/tests/test_review_interaction.py`
- Test: `.agents/skills/bio-review-pack/tests/browser_check_review.py`

**Interfaces:**
- Consumes: Task 1~2에서 확정한 자산과 `review_interaction.install(source, document_id)`.
- Produces: 원본 자산과 동일한 내장 CSS/JS를 가진 HTML 8개. 모델 JSON 및 `review-interaction` 블록 밖의 내용은 그대로 둔다.

- [ ] **Step 1: 생성물 일치 테스트 추가**

`TestModel`에 아래 테스트를 추가한다. 현재 HTML에는 이전 CSS/JS가 들어 있어 첫 실행은 실패해야 한다.

```python
def test_existing_packs_embed_current_interaction_assets(self):
    files = sorted((REPO / '복습노트').glob('*/복습문제_*.html'))
    self.assertEqual(len(files), 8)
    for path in files:
        with self.subTest(file=path.name):
            source = path.read_text(encoding='utf-8')
            self.assertEqual(ri.install(source, path.name), source)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_review_interaction.py -v`

Expected: 새 `test_existing_packs_embed_current_interaction_assets`가 실패한다.

- [ ] **Step 3: 내장 자산 재설치**

```powershell
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --audit
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write
```

`--audit`의 `errors`가 모두 빈 배열일 때만 `--write`를 실행한다. `git diff -- 복습노트`를 보고 CSS/JS 블록만 달라졌는지 확인한다. 특히 0910 파일의 원본 체크아웃 수정 내용은 이 워크트리에 복사하지 않는다.

- [ ] **Step 4: 검증**

```powershell
python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_review_interaction.py -v
python .agents/skills/bio-review-pack/tests/browser_check_review.py
git diff --check
```

Expected: 테스트 전체 PASS, `git diff --check` 출력 없음. 브라우저 검사에서 스크린샷 경로 `.superpowers/sdd/bio-review-interactive`가 없다면 그 경로만 만든 뒤 다시 실행하고, 생성된 스크린샷은 커밋하지 않는다.

- [ ] **Step 5: 인쇄와 정적 접근 확인**

기존 `test_mobile_theme_print_and_figures`와 `test_static_and_no_javascript`가 PASS인지 확인한다. 브라우저 테스트가 사용한 스크린샷을 열어 320px 화면과 다크 테마에서 효과가 상단 바를 가리지 않는지 시각적으로 확인한다.

- [ ] **Step 6: 커밋**

```powershell
git add .agents/skills/bio-review-pack/tests/test_review_interaction.py 복습노트
git commit -m "chore(review): refresh answer feedback in existing packs"
```

## Final review

- [ ] `git status --short`로 계획·설계 이외의 미처리 변경을 확인한다.
- [ ] `git diff main...HEAD --stat`와 `git diff main...HEAD --check`로 범위와 공백 오류를 확인한다.
- [ ] 정답·오답·모호 문항의 브라우저 테스트 결과와 인쇄·모바일 확인 결과를 요약한다.
- [ ] 계획과 설계 문서를 기능 브랜치에 포함한다면 별도 문서 커밋으로 기록한다.
