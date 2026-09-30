# Remove Review-Question Help Text Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete the useless guidance sentence "답을 선택하면 내 선택과 정답의 해설이 열려요. 다른 보기도 눌러 해설을 확인할 수 있어요." from every review-question HTML, and make the `bio-review-pack` skill unable to produce it again.

**Architecture:** The sentence is not authored per file. It is created at runtime by `assets/review-interaction.js` (`element('p','review-help', …)`), styled in `assets/review-interaction.css`, and both are inlined into each `복습문제_*.html` by `scripts/review_interaction.py install`. So the fix is: (1) remove the source (JS + CSS), (2) re-run `install` to refresh every embedded copy, (3) add tests and a written rule so the text/element cannot come back.

**Tech Stack:** Python 3 + unittest (`tests/*.py`), Node `node:test` (`tests/*.cjs`), Playwright browser check (`tests/browser_check_review.py`, optional).

**Spec:** none (direct user request: "복습문제 html에서 이 문구를 지우고, 스킬도 수정해서 재발을 방지하자. 쓸데없는 텍스트야.")

## Global Constraints

- Delete only the `review-help` paragraph. Keep `review-status` ("정답이에요." / "정답이 아니에요. 보기별 이유를 확인해 보세요." / "단일 정답 판정 주의"), `다시 풀기`, badges (`내 선택`, `정답`), and all disclosure behavior unchanged.
- Do not hand-edit the generated HTMLs; regenerate them with `review_interaction.py install` so `test_existing_packs_embed_current_interaction_assets` (install is idempotent) keeps passing.
- Skill root: `.agents/skills/bio-review-pack` (`.claude/skills/bio-review-pack` is a symlink to it — edit only the `.agents` path).
- Files affected by refresh: 8 tracked packs `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929}/복습문제_*.html` and 4 untracked copies in `복습노트/2장_3장_모음/복습문제_*.html`.

## Review Focus

- Card with a stored (restored) answer on reload: no help paragraph flashes or remains, and layout above `.choices` is just the status line. Pinned by browser check (Task 2).
- Enhancement failure fallback (`catch` block) still works after `help` is removed from the cleanup list — `[status, reset, notice]` must not reference an undefined `help`. Pinned by node test/`grep` in Task 1.
- Print CSS (`@media print`) no longer names `.review-help`; no orphan selector left. Pinned by Task 1 test.
- A future edit re-adding the sentence or a `review-help` class to any asset, reference, or generated HTML. Pinned by Task 2 guard test.
- `2장_3장_모음` copies (not covered by the existing 8-file test) still get refreshed. Pinned by Task 3 verification grep.

---

### Task 1: Remove the help text from the interaction assets

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.js` (lines 101, 145, 151, 172, 252)
- Modify: `.agents/skills/bio-review-pack/assets/review-interaction.css` (lines 19, 24, 81)
- Test: `.agents/skills/bio-review-pack/tests/test_review_interaction.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `review-interaction.js` / `.css` with no `help` variable, no `review-help` class, and no help sentence. `ReviewInteraction.mount` API is unchanged.

- [ ] **Step 1: Write the failing test**

Append to class `TestModel` in `tests/test_review_interaction.py` (before `test_safe_json` is fine):

```python
    def test_assets_have_no_help_text(self):
        for name in ('review-interaction.js', 'review-interaction.css'):
            text = (SKILL / 'assets' / name).read_text(encoding='utf-8')
            with self.subTest(asset=name):
                self.assertNotIn('review-help', text)
                self.assertNotIn('해설이 열려요', text)
                self.assertNotIn('다른 보기도 눌러', text)
```

(`SKILL` is already imported from `_util` at the top of that file.)

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p "test_review_interaction.py" -k test_assets_have_no_help_text -v`
Expected: FAIL (`'review-help' unexpectedly found in …`).

- [ ] **Step 3: Edit the JS**

In `assets/review-interaction.js`:

1. Line 101: `let status, reset, help, notice;` → `let status, reset, notice;`
2. Delete line 145 entirely:
   ```js
           help = element('p', 'review-help', '답을 선택하면 내 선택과 정답의 해설이 열려요. 다른 보기도 눌러 해설을 확인할 수 있어요.');
   ```
3. Line 151: `card.querySelector('.choices').before(help, status);` → `card.querySelector('.choices').before(status);`
4. Delete line 172: `          help.hidden = answered;`
5. Line 252: `for (const el of [status, reset, help, notice]) if (el) el.remove();` → `for (const el of [status, reset, notice]) if (el) el.remove();`

- [ ] **Step 4: Edit the CSS**

In `assets/review-interaction.css`:

1. Line 19: `.review-help[hidden], .review-reset[hidden], .review-diagnostics[hidden] { display:none; }` → `.review-reset[hidden], .review-diagnostics[hidden] { display:none; }`
2. Delete line 24: `.review-help { color:var(--ink-2); font-size:var(--fs-small); }`
3. Line 81: `.review-reset, .review-status, .review-help, .review-choice-label { display:none !important; }` → `.review-reset, .review-status, .review-choice-label { display:none !important; }`

- [ ] **Step 5: Run the tests**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p "test_review_interaction.py" -v`
Expected: `test_assets_have_no_help_text` PASS. **`test_existing_packs_embed_current_interaction_assets` will now FAIL** — the generated HTMLs still embed the old assets; Task 3 fixes that. Also run `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs` → PASS (it only loads the module; confirms no syntax error).

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/assets/review-interaction.css .agents/skills/bio-review-pack/tests/test_review_interaction.py
git commit -m "fix: remove useless help sentence from review interaction assets"
```

(Do not push a broken intermediate state; Tasks 1–3 may be squashed into one branch before merging.)

---

### Task 2: Prevent recurrence in the skill (rule + guard tests)

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/card-rules.md` (append a rule)
- Modify: `.agents/skills/bio-review-pack/references/browser-check.md:66-68` (add a check line)
- Modify: `.agents/skills/bio-review-pack/tests/test_review_interaction.py` (guard over generated packs)
- Modify: `.agents/skills/bio-review-pack/tests/browser_check_review.py` (assert no help element)

**Interfaces:**
- Consumes: Task 1's cleaned assets.
- Produces: a written rule plus tests that fail if the sentence/class reappears in assets or any generated `복습문제_*.html`.

- [ ] **Step 1: Write the failing guard test**

Append to `TestModel` in `tests/test_review_interaction.py`:

```python
    def test_generated_packs_have_no_help_text(self):
        files = sorted((REPO / '복습노트').glob('**/복습문제_*.html'))
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            text = path.read_text(encoding='utf-8')
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertNotIn('review-help', text)
                self.assertNotIn('해설이 열려요', text)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p "test_review_interaction.py" -k test_generated_packs_have_no_help_text -v`
Expected: FAIL for all 12 files (passes after Task 3).

- [ ] **Step 3: Add the written rule**

Append to `references/card-rules.md`:

```markdown

## 화면에 넣지 않는 안내 문구

- 문항 카드에 “답을 선택하면 …해설이 열려요”, “다른 보기도 눌러 …”, “여기를 눌러 …” 같은 **사용법·조작 안내 문장을 넣지 않는다.** 보기 버튼과 판정 문구(`review-status`), `내 선택`·`정답` 배지만으로 충분하다.
- `assets/review-interaction.js`·`.css`에 안내용 `<p>`(예: `review-help`)를 다시 추가하지 않는다. 새 상호작용을 만들 때도 화면에는 결과(판정·배지)만 보이고 설명 문장은 만들지 않는다.
- `tests/test_review_interaction.py`의 `test_assets_have_no_help_text`, `test_generated_packs_have_no_help_text`가 이 규칙을 강제한다.
```

- [ ] **Step 4: Add the browser-check line**

In `references/browser-check.md`, after the line beginning `- 보기 선택 전 해설이 숨겨지고,` insert:

```markdown
- 선택 전·후 어느 때도 “해설이 열려요” 같은 사용법 안내 문장(`.review-help`)이 카드에 없어야 한다.
```

In `tests/browser_check_review.py`, next to the existing first-card assertions (around line 141–144, where `card.locator('.review-status')` is first checked), add:

```python
        expect(card.locator('.review-help')).to_have_count(0)
```

(Use the same `card` variable already defined in that test method; if the method reads the card as another name, use that name. Run `grep -n "review-status" tests/browser_check_review.py | head -3` to find the spot.)

- [ ] **Step 5: Verify rule file mentions**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p "test_skill_files.py" -v`
Expected: PASS (confirms doc edits didn't break skill-file consistency checks). If it fails on a reference-file listing, fix the reported item.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/bio-review-pack/references/card-rules.md .agents/skills/bio-review-pack/references/browser-check.md .agents/skills/bio-review-pack/tests/test_review_interaction.py .agents/skills/bio-review-pack/tests/browser_check_review.py
git commit -m "test: guard against help sentence in review packs and document the rule"
```

---

### Task 3: Regenerate every review HTML

**Files:**
- Modify (regenerated): `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929}/복습문제_*.html`
- Modify (regenerated, untracked): `복습노트/2장_3장_모음/복습문제_{0910,0915,0917,0922}_*.html`

**Interfaces:**
- Consumes: Task 1 assets; `review_interaction.install(source, document_id)` (document_id = file name).
- Produces: HTMLs with no `review-help` / help sentence.

- [ ] **Step 1: Audit (no writes)**

Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --audit`
Expected: 8 JSON lines, each `"errors": []`, exit 0.

- [ ] **Step 2: Refresh the 8 dated packs**

Run: `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write`
Expected: same 8 lines, exit 0; `git status` shows the 8 `복습문제_*.html` modified.

- [ ] **Step 3: Refresh the 2장_3장_모음 copies**

The CLI globs `*/복습문제_*.html`, which does not match files directly inside `2장_3장_모음`, so use a one-off (PowerShell/Bash, from repo root):

```bash
python - <<'EOF'
import sys
sys.path.insert(0, '.agents/skills/bio-review-pack/scripts')
from pathlib import Path
import review_interaction as ri
for p in sorted(Path('복습노트/2장_3장_모음').glob('복습문제_*.html')):
    src = p.read_text(encoding='utf-8')
    out = ri.install(src, p.name)
    if out != src:
        p.write_text(out, encoding='utf-8')
    print(p.name, 'updated' if out != src else 'unchanged')
EOF
```
Expected: 4 lines, `updated`.

- [ ] **Step 4: Verify nothing remains**

Run: `grep -rlE "review-help|해설이 열려요|다른 보기도 눌러" 복습노트 .agents docs --include=*.html --include=*.js --include=*.css --include=*.md --include=*.py`
Expected: no output except this plan and `card-rules.md`/`test_review_interaction.py` (which quote the phrase as a rule/guard). The 12 HTMLs and both assets must not be listed.

- [ ] **Step 5: Run the full skill test suite**

Run: `python -m unittest discover -s .agents/skills/bio-review-pack/tests -v` and `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs`
Expected: all PASS, including `test_existing_packs_embed_current_interaction_assets`, `test_generated_packs_have_no_help_text`, `test_assets_have_no_help_text`.

- [ ] **Step 6: Optional browser regression**

If Playwright/Chromium is available: `python .agents/skills/bio-review-pack/tests/browser_check_review.py`
Expected: passes, including `.review-help` count 0. Otherwise open `복습노트/0929/복습문제_0929_Heredity.html` in the browser, confirm no sentence appears above the choices before answering, then click a choice and confirm the status line and 해설 still open.

- [ ] **Step 7: Commit**

```bash
git add 복습노트/0901 복습노트/0903 복습노트/0908 복습노트/0910 복습노트/0915 복습노트/0917 복습노트/0922 복습노트/0929
git commit -m "fix: remove help sentence from all review question HTMLs"
```

(`복습노트/2장_3장_모음/` is untracked; leave it uncommitted unless the user says otherwise.)

---

## Self-Review

- **Coverage:** Remove phrase from all review HTMLs → Task 3 (12 files, incl. untracked 모음). Skill fix → Task 1 (source) + Task 2 (rule, guards, browser check).
- **Placeholders:** none; every edit names exact lines/strings.
- **Consistency:** the only removed identifier is `help` (JS var) / `.review-help` (CSS); Task 1 lists all 5 JS and 3 CSS usages found by grep.
