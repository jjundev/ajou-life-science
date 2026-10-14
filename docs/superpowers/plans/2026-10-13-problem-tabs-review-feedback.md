# 문제해설 원문 탭 + 복습노트 보기 반응 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 문제해설 오른쪽 패널을 [문제 | 원문 | 요약] 탭으로 바꾸고, 보기 클릭 반응을 복습노트와 같게 맞춘 뒤 기존 12팩을 재발행한다.

**Architecture:** 렌더러 출력은 그대로 두고 `assets/note-template.html`의 `setupExplain()`만 바꾼다. 넓은 화면에서 JS가 각 pane의 `details.original`을 새 `#tabpanel-original`로 옮기고, 보기 판정·알림·스크롤은 `bio-review-pack/assets/review-interaction.{js,css}`에서 복사한 코드로 처리한다. 템플릿은 payload_hash 밖이므로 `mpe_cli.py rerender`로 재발행한다.

**Tech Stack:** 인라인 CSS/JS 템플릿, pytest(`uv run --with pytest`), Playwright(시스템 `python3`).

**Spec:** `docs/superpowers/specs/2026-10-13-problem-tabs-review-feedback-design.md`

## Global Constraints

- `SKILL` = `.agents/skills/bio-problem-explain`. `REVIEW` = `.agents/skills/bio-review-pack/assets`. 모든 명령은 저장소 루트에서.
- 단위: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q` (현재 156 passed).
- 브라우저: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py <비어 있는 scratchpad 폴더>` (1280/1024/375 × light/dark, 6 runs).
- SKILL 아래 파일을 바꾸면 커밋 전에 `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py` 실행.
- 렌더러(`mpe_render.py`)·조각 저작 계약·payload_hash는 바꾸지 않는다. 원 복습문제·정리노트·`.pack/`·기출 PDF 수정 금지.
- 고정 문구: 탭 `문제`/`원문`/`요약`; 알림 `정답이에요`/`다시 확인해요`(1100ms, ambiguous는 없음); 상태 `정답이에요.`/`정답이 아니에요. 보기별 이유를 확인해 보세요.`/`단일 정답 판정 주의`; 배지 `내 선택`/`정답`/`정답 아님`/`출제 의도상 답`(구분자 ` · `); 버튼 `다시 풀기`.
- `data-result` 값: `correct`, `intended`, `selected`, `uncertain`, `''`.
- 탭 저장 키 `bio-problem-explain-tab`, 값 `problem`|`original`|`summary`. 보기 선택은 메모리만.
- 해설 판정 문단 이동(`jump`)은 `wideMq.matches`일 때만. 강조 1.6초.
- 작업은 worktree `.worktrees/problem-tabs`(브랜치 `feat/problem-tabs-feedback`)에서. 커밋 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. 푸시 금지.

## Review Focus

1. 원문 탭을 고른 채 원문 없는 문항 → 문제 탭이 보이고, 원문 있는 문항으로 돌아가면 원문 탭 복귀 (Task 1 p4/p3 단언).
2. 원문 탭을 연 상태에서 창이 1024 아래로 줄었다 다시 커짐 → 원문이 pane 안 접힘 ↔ 탭 펼침으로 오가며 중복·유실 없음 (Task 1 리사이즈 단언).
3. 보기가 스크롤러보다 아래에 있을 때 클릭 → 내 선택·정답 묶음이 스크롤러 가운데로 (Task 2 spacer 단언, 1280 패널·375 본문).
4. 판정 후 다른 보기 클릭 → 판정 불변 (Task 2 잠금 단언).
5. 다시 풀기 직후 1.1초 안에 남은 알림 → 즉시 사라짐 (Task 2 reset 단언).

---

### Task 1: 원문 탭

**Files:**
- Modify: `SKILL/assets/note-template.html` — 패널 마크업(약 431–445행), CSS(약 291–294행), `setupExplain()`(약 708–950행)
- Modify: `SKILL/tests/helpers.py` — `choice_card(id_, number, count, original=True)`, `acceptance_pack`에서 `choice_card('p4',4,3,original=False)`
- Modify: `SKILL/tests/browser_acceptance.py`
- Modify: `SKILL/SKILL.md:75`, `SKILL/references/verification.md:10`

**Interfaces:**
- Produces (DOM): `#tab-original[role=tab][data-tab="original"][aria-controls="tabpanel-original"]`(문제·요약 탭 사이), `div.orig-tab#tabpanel-original[role=tabpanel][aria-labelledby="tab-original"]`(`.probs`와 `.sum-tab` 사이). 넓은 화면에서 원문은 `#tabpanel-original > details.original[data-original-problem=ID][open]`.
- Produces (JS, `setupExplain` 내부): `origs: {[id]: HTMLDetailsElement}`, `showTab(name, save)`가 세 탭을 처리.

- [ ] **Step 1: 브라우저 테스트 수정(실패 먼저)**

`helpers.choice_card`에 `original=True` 인자를 추가하고 False면 `details.original`을 빼며, `acceptance_pack`의 p4를 `original=False`로 만든다. `browser_acceptance.py`의 넓은 화면 분기(요약 탭 클릭 뒤 `[data-tab="problem"]` 클릭 직후)에 다음을 넣는다.

```python
    assert page.locator('#tab-original').is_visible()
    page.locator('#tab-original').click()
    orig=page.locator('#tabpanel-original details.original[data-original-problem="p3"][open]')
    assert orig.is_visible() and '합성 원문 3' in orig.inner_text()
    assert orig.locator('summary').is_hidden() and page.locator('#tabpanel-problem').is_hidden()
    assert page.locator('[data-problem-for="p3"] details.original').count()==0
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#p3 [data-problem-for="p3"] details.original:not([open])').count()==1
    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
    assert page.locator('details.original[data-original-problem="p3"]').count()==1 and orig.is_visible()
    page.goto(url+'#p4');page.wait_for_timeout(100)
    assert page.locator('#tab-original').is_hidden()
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true' and page.locator('[data-problem-for="p4"]').is_visible()
    page.goto(url+'#p3');page.wait_for_timeout(100)
    assert page.locator('#tab-original').get_attribute('aria-selected')=='true'
    page.locator('#tab-original').focus();page.keyboard.press('ArrowRight')
    assert page.locator('#tab-summary').get_attribute('aria-selected')=='true'
    page.keyboard.press('ArrowRight')
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true'
```

좁은 화면 분기(토글 클릭 단언 뒤)에 추가:

```python
    assert page.locator('#p3 [data-problem-for="p3"] details.original:not([open])').count()==1
    assert page.locator('#tab-original').is_hidden()
```

인쇄 단언 블록(`emulate_media(media='print')` 뒤)에 추가:

```python
   assert page.locator('#p3 > [data-problem-for="p3"] details.original[open]').is_visible()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 SKILL/tests/browser_acceptance.py <scratch>/a1`
Expected: FAIL — `#tab-original` 없음(`is_visible` False에서 AssertionError).

- [ ] **Step 3: 템플릿 구현**

- 마크업: Interfaces의 탭(`hidden`, `tabindex="-1"`, `aria-selected="false"`)과 탭 패널(`hidden`) 추가. sr-only 제목 `문제와 요약` → 넓은 화면 `문제, 원문, 요약`(`mountPanes`의 `title.textContent`도 같게).
- CSS: `.probs, .sum-tab` 규칙에 `.orig-tab` 추가. `.orig-tab details.original { margin-top: 0; padding-top: 0; border-top: 0; }`, `.orig-tab details.original > summary { display: none; }`.
- `setupExplain()`:
  - topics 순회에서 `pane.querySelector(':scope > details.original')`이 있으면 `origs[t.id]`에 담는다.
  - 저장값 해석: `['problem','original','summary'].includes(saved) ? saved : 'problem'`.
  - `effective(name)` = `name === 'original' && !origs[curId] ? 'problem' : name`. `showTab(name, save)`는 `#tab-original.hidden = !origs[curId]`, 세 탭의 `aria-selected`/`tabIndex`, `probs`/`origTab`/`sumTab`의 `hidden`을 `effective(name)` 기준으로 정하고, `save`면 `tab = name` 후 저장.
  - `mountPanes()` 넓은 화면: 원문마다 `open = true`, `origTab.appendChild`, `hidden = id !== curId`. 좁은 화면: `open = false`, `hidden = false`, `panes[id].appendChild(orig)`.
  - 키보드: ←/→가 보이는 탭 목록(`problem`, 원문 있으면 `original`, `summary`)에서 `effective(tab)`의 이웃으로 순환하고 그 탭에 포커스.
  - `od:screen`: 넓은 화면이면 원문 `hidden`을 `curId` 기준으로 갱신하고 `showTab(tab, false)`.
  - `mountForPrint()`: 원문을 `panes[id]` 끝에 넣고 `open = true`, `hidden = false`. `afterprint`는 기존대로 `mountPanes()`.
- 문서: SKILL.md:75의 "문제는 넓은 화면에서 오른쪽 문제 탭, …" 문장을 "문제는 넓은 화면에서 오른쪽 [문제 | 원문 | 요약] 탭(원문 탭은 원문이 있는 문항만), 좁은 화면에서 해설 위 접힘 버튼으로 표시된다."로. verification.md:10의 "1280·1024에서 오른쪽 문제 탭이 기본으로 보이고 요약 탭 전환이 되는지"를 "1280·1024에서 오른쪽 문제 탭이 기본으로 보이고 원문·요약 탭 전환이 되는지(원문 없는 문항은 원문 탭 숨김)"로.

- [ ] **Step 4: 통과 확인**

Run: `python3 SKILL/tests/browser_acceptance.py <scratch>/a2` → Expected: 6 runs 통과, 콘솔 오류 0.
Run: `python3 SKILL/scripts/port_provenance.py && uv run --with pytest python -m pytest SKILL/tests -q` → Expected: `156 passed`.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): move original problem into its own panel tab"
```

### Task 2: 복습노트 보기 반응 이식

**Files:**
- Modify: `SKILL/assets/note-template.html` — 보기 CSS(약 306–331행), `setupExplain()`의 보기 블록(`paint`/`jump`/버튼 생성, 약 783–855행)
- Modify: `SKILL/tests/test_render.py`, `SKILL/tests/browser_acceptance.py`
- Modify: `SKILL/references/verification.md:10`

**Interfaces:**
- Consumes: Task 1의 `showTab`·`mountPanes` (변경 없음).
- Produces (DOM): 배지 클래스 `review-choice-label`(기존 `review-badge` 대체), `p.review-status[role=status][aria-live=polite][data-result]`는 `.choices` 앞, `button.review-reset` 텍스트 `다시 풀기`는 `.choices` 뒤, 알림 `body > div.review-feedback[data-review-feedback][data-result][aria-hidden=true]` 안에 `.review-feedback-icon`, `.review-feedback-text`.
- Produces (JS): `scrollAnswerIntoView(scroller, selectedLi, answerLi, selectedButton, answerButton)` (REVIEW 원본과 동일), `showFeedback(result, id)`, `clearFeedback(owner = null)`.

- [ ] **Step 1: 드리프트 단위 테스트 작성** (`test_render.py`)

```python
REVIEW=Path(__file__).resolve().parents[2]/'bio-review-pack/assets'
squash=lambda s:re.sub(r'\s+','',s)

def test_choice_feedback_copied_from_review_pack():
    template=squash((Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text())
    css=(REVIEW/'review-interaction.css').read_text();js=(REVIEW/'review-interaction.js').read_text()
    slices=[css[css.index('.review-feedback {'):css.index('.review-feedback[data-result="saved"]')],
            css[css.index('.review-feedback-icon {'):css.index('.review-export-bar')],
            css[css.index('.review-choice[data-result="correct"]'):css.index('.review-choice-label[hidden]')],
            js[js.index('function scrollAnswerIntoView('):js.index('function grade(')]]
    for s in slices: assert squash(s) in template,'복습노트 상호작용과 어긋났어요: '+s.strip()[:40]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest python -m pytest SKILL/tests/test_render.py::test_choice_feedback_copied_from_review_pack -q`
Expected: FAIL — `복습노트 상호작용과 어긋났어요: .review-feedback {`.

- [ ] **Step 3: 브라우저 테스트 수정(실패 먼저)**

`browser_acceptance.py`의 p3/p4 보기 블록을 바꾼다. `.review-badge` → `.review-choice-label`. p3 오답 클릭 직전에 패딩을 넣어 스크롤이 실제로 일어나게 한다:

```python
   pane.evaluate("e=>{const l=e.querySelector('.choices');for(const w of ['before','after']){const d=document.createElement('div');d.className='test-spacer';d.style.height='1400px';l[w](d)}}")
   pane.locator('.review-choice[data-choice-id="5"]').click();page.wait_for_timeout(100)
   fb=page.locator('.review-feedback[data-result="incorrect"]')
   assert fb.is_visible() and fb.inner_text()=='다시 확인해요'
   assert pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='selected'
   assert pane.locator('[data-choice-id="3"]').get_attribute('data-result')=='correct'
   assert pane.locator('[data-choice-id="1"] .review-choice-label').inner_text()=='정답 아님'
   assert pane.locator('[data-choice-id="5"] .review-choice-label').inner_text()=='내 선택'
   assert pane.locator('.review-status').inner_text()=='정답이 아니에요. 보기별 이유를 확인해 보세요.'
   assert pane.locator('.review-status + .choices').count()==1
   centered=pane.evaluate("""e=>{const s=e.closest('.panel-inner')||document.querySelector('.content');
     const a=e.querySelector('[data-choice-id="5"]').closest('li').getBoundingClientRect(),b=e.querySelector('[data-choice-id="3"]').closest('li').getBoundingClientRect(),v=s.getBoundingClientRect();
     return Math.abs((Math.min(a.top,b.top)+Math.max(a.bottom,b.bottom))/2-(v.top+v.bottom)/2)<24}""")
   assert centered
   pane.locator('.review-choice[data-choice-id="4"]').click();page.wait_for_timeout(50)
   assert pane.locator('[data-choice-id="4"]').get_attribute('data-result')=='' and pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='selected'
   target=page.locator('#p3 [data-explanation="solve"] p.is-target')
   if width>=1024:
    assert target.count()==1 and target.inner_text().startswith('(5)')
    assert target.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
   else: assert target.count()==0
   page.wait_for_timeout(1700);assert target.count()==0 and fb.count()==0
```

리사이즈 단언의 `'incorrect'` → `'selected'`. 리셋 뒤에:

```python
   assert page.locator('[data-problem-for="p3"] .review-reset').inner_text()=='다시 풀기'
   page.locator('[data-problem-for="p3"] .review-choice[data-choice-id="5"]').click()
   page.locator('[data-problem-for="p3"] .review-reset').click()
   assert page.locator('.review-feedback').count()==0
   page.locator('[data-problem-for="p3"] .review-choice[data-choice-id="3"]').click();page.wait_for_timeout(50)
   assert page.locator('.review-feedback[data-result="correct"]').inner_text()=='정답이에요'
   assert page.locator('[data-problem-for="p3"] .review-status').inner_text()=='정답이에요.'
   page.locator('[data-problem-for="p3"] .review-reset').click()
   page.evaluate("document.querySelectorAll('.test-spacer').forEach(n=>n.remove())")
```

p4: `[data-choice-id="1"]` → `'uncertain'`, `[data-choice-id="2"] .review-choice-label`에 `출제 의도상 답`, 상태 `단일 정답 판정 주의`, `page.locator('.review-feedback').count()==0`, `h4.is-target` 개수는 넓은 화면 1·좁은 화면 0.

- [ ] **Step 4: 실패 확인**

Run: `python3 SKILL/tests/browser_acceptance.py <scratch>/b1`
Expected: FAIL — `.review-feedback` 없음.

- [ ] **Step 5: 템플릿 구현**

- CSS: REVIEW css의 세 구간(Step 1 slices와 같은 범위: `.review-feedback {`~`[data-result="incorrect"] { border-color…}`, `.review-feedback-icon {`~reduced-motion 블록 끝, `.review-choice[data-result="correct"]`~`.review-choice-label {…}`)을 그대로 붙인다. 기존 `[data-result="incorrect"]`, `[aria-pressed="true"][data-result=""]`, `.review-badge` 규칙은 지우고 `.review-choice-label[hidden], .review-reset[hidden] { display:none; }`. 위에 `/* bio-review-pack review-interaction.css에서 복사 — test_choice_feedback_copied_from_review_pack이 어긋남을 잡는다 */`.
- JS: `scrollAnswerIntoView`를 원본 그대로 붙이고, `showFeedback`/`clearFeedback`는 원본(`review-interaction.js` `mount` 안)을 `root`→`document`, `win`→`window`로 바꿔 옮긴다. 보기 블록은:
  - `picks: Map<id, choiceId>`. 클릭 시 `picks.has(id)`면 무시(잠금). 아니면 `picks.set` → `paint(id)` → `showFeedback(grade, id)`(`grade` = ambiguous면 `'ambiguous'`, 아니면 `correct`/`incorrect`) → `requestAnimationFrame` 안에서 pane이 보일 때 `scrollAnswerIntoView(panes[id].closest('.panel-inner') || scroller, 선택 li, 정답 li, 선택 버튼, 정답 버튼)` 후 `if (wideMq.matches) jump(id, cid)`.
  - `paint(id)`: 원본 `paint()`의 상태·`data-result`·배지·`aria-pressed`(미선택 `false`, 선택 뒤 제거) 규칙을 그대로. `status.dataset.result`도 설정.
  - 상태는 `list.before(status)`에 `role="status"`, 리셋은 `list.after(reset)`에 `다시 풀기`. 리셋: `clearFeedback(id)` → `picks.delete(id)` → `paint(id)` → 첫 보기 버튼 `focus()`.
- verification.md:10의 "문항마다 오답 하나·정답 하나를 눌러 판정 표시와 해설 판정 문단 이동을 확인하고"를 "문항마다 오답을 눌러 판정 표시·상단 알림·보기 스크롤과(넓은 화면) 해설 판정 문단 이동을, 다시 풀기 뒤 정답을 눌러 정답 표시를 확인하고"로.

- [ ] **Step 6: 통과 확인**

Run: `python3 SKILL/scripts/port_provenance.py && uv run --with pytest python -m pytest SKILL/tests -q` → Expected: `157 passed`.
Run: `python3 SKILL/tests/browser_acceptance.py <scratch>/b2` → Expected: 6 runs 통과.

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): match review-note choice feedback and scrolling"
```

### Task 3: 12팩 재발행

**Files:**
- Modify (scratch, 커밋 안 함): `<scratchpad>/review_pack.py`, `<scratchpad>/republish.sh`
- Modify (발행 결과): `복습노트/<날짜>/문제설명_*.html` 12개와 각 manifest·검증 파일, 새 근거 `evidence/*rerender2*`

**Interfaces:**
- Consumes: `python3 SKILL/scripts/mpe_cli.py rerender --repo --target --run` (메시지 `content·independent 재사용`이면 진행).

- [ ] **Step 1: 스크립트 수정**
  - 근거 파일명 `source-visual-rerender-`/`browser-rerender-`/`rerender-<range>-*.png` → `…-rerender2-…`(republish.sh의 `browser-rerender-{rng}.json`·evidence 문구 포함). 실행 폴더 `rr` → `rr2`.
  - source_visual 행의 `original` 판정: 원문이 있으면 `#tabpanel-original details.original[data-original-problem=ID]`가 1개이고, 해당 문항에서 `#tab-original` 클릭 시 보이는지; 없으면 `#tab-original` 숨김. 확인 뒤 `#tab-problem` 클릭.
  - browser 루프: 오답 기대값 single `selected`/ambiguous `uncertain`; 오답 클릭 → 판정 확인 → `.review-reset` 클릭 → 정답 클릭 → 판정 확인 → 리셋 순서(잠금 때문). 해설 이동 확인은 `width >= 1024`만, 375에서는 `is-target` 0개.
- [ ] **Step 2: 첫 팩(1013) 시험 실행**

Run: `bash <scratchpad>/republish.sh 1013`
Expected: `rerender: … content·independent 재사용 …`, review_pack JSON `n_failures: 0`, check 통과, publish 성공. 기존 `*-rerender-*` 근거가 그대로인지 `git status --short 복습노트/1013`으로 확인(수정 아님·추가만).
- [ ] **Step 3: 나머지 11팩** (1008 1006 1001 0929 0922 0917 0915 0910 0908 0903 0901) 같은 명령. 하나라도 `HOLD`나 실패면 그 팩은 멈추고 원인을 기록.
- [ ] **Step 4: 확인**

Run: `git status --short 복습노트 | grep -v '^??' | grep -v '문제설명_\|manifest\|validation'` → Expected: 출력 없음(원 복습문제·정리노트 무변경). 기존 증거 파일 수정 0.
- [ ] **Step 5: Commit**

```bash
git add 복습노트
git commit -m "docs(notes): republish problem explanations with original tab and review feedback"
```
