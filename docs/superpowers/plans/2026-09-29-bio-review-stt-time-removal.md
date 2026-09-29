# Biology Review STT Time Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 학생용 복습팩의 STT 녹음 시각을 모두 지우고 새 팩에서 재발하면 검사로 막는다.

**Architecture:** 기존 복습팩의 HTML을 진실 원본으로 삼아 문장 단위로 정리하고 MD를 다시 생성한다. 장마감 MD는 별도로 정리한다. 작성 브리프에서 시각 요구를 없애고, `check_html.py`가 표시 텍스트를 검사해 생성 단계에서 실패하게 한다.

**Tech Stack:** Python 표준 라이브러리, `unittest`, 정적 HTML/Markdown, PowerShell.

**Spec:** `docs/superpowers/specs/2026-09-29-bio-review-stt-time-design.md`

## Global Constraints

- `STT/`와 내부 요약·문항 감사·정답 대조 파일의 근거 시각은 보존한다.
- `MMDD 수업`, 강의노트·교재 쪽수, 기출·웹과제 출처, 실제 생물학 학습 내용의 시간 표현은 보존한다.
- 학생용 HTML·MD·장마감 MD의 문장은 STT 시각 제거 후에도 자연스러워야 한다.
- 다른 사용자의 미추적 파일(`tmp/`, `videos/`, 기존 `docs/superpowers/` 파일)을 수정하거나 커밋하지 않는다.
- 출력 파일명과 토픽·카드 id, 링크 대상, 그림 폴더 구조는 보존한다.

## Review Focus

1. `(0910 22:05, 강의노트 2장 p3)`처럼 한 괄호에 시각과 출처가 함께 있으면 시각만 빠지고 출처는 남아야 한다. Task 1의 혼합 출처 테스트와 Task 3의 diff 검토로 확인한다.
2. `0910 22:05–22:22에서`처럼 조사와 붙은 표기는 문장이 자연스럽게 바뀌어야 한다. Task 3의 대표 문장 검토와 전체 diff 검토로 확인한다.
3. 파트 시각 `(P03 04:12)` 및 날짜 없는 `14:37`도 빠져야 한다. Task 1의 각 형식 테스트와 Task 3의 잔여 후보 검색으로 확인한다.
4. 실제 수업 내용의 시간 `24시간`, 날짜 배지 `0910 수업`, `p14`를 오탐으로 지우지 않아야 한다. Task 1의 음성 테스트와 Task 3의 diff 검토로 확인한다.
5. HTML은 깨끗하지만 재생성된 MD나 장마감 MD에 시각이 남는 경우도 막아야 한다. Task 3의 MD 검색·변환 검사로 확인한다.

---

## File map

- `.agents/skills/bio-review-pack/scripts/check_html.py`: HTML 표시 텍스트 검사 및 오류 위치 보고.
- `.agents/skills/bio-review-pack/tests/test_check_html.py`: 검사기 회귀 테스트.
- `.agents/skills/bio-review-pack/tests/fixtures/mini-run/sections/s1.html`: 기존 테스트 픽스처에서 의도하지 않은 시각 제거.
- `.agents/skills/bio-review-pack/references/content-rules.md`: 정리노트 작성 지침.
- `.agents/skills/bio-review-pack/references/card-rules.md`: 복습문제 작성 지침.
- `.agents/skills/bio-review-pack/SKILL.md`: 기계 검사와 MD 변환 뒤 잔여 시각 확인 지침.
- `복습노트/*/정리노트_*.html`, `복습문제_*.html`: 기존 학생용 문장.
- 같은 폴더의 대응 `.md` 및 `장마감_*.md`: Markdown 산출물.

### Task 1: 표시 텍스트 검사기와 회귀 테스트

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/check_html.py:38-175,235-260`
- Modify: `.agents/skills/bio-review-pack/tests/test_check_html.py:1-165`
- Modify: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/sections/s1.html:4,22`

**Interfaces:**
- Consumes: `Doc.body_text` from `parse_html(source)`.
- Produces: `stt_time_problems(text: str, where: str) -> list[Problem]`; `check_common` includes those problems with code `stt-time`.

- [ ] **Step 1: Write the failing tests.** Add table-driven cases in `TestPrimitives`. Use `check_html.stt_time_problems(text, "x.html")` for `"(0910 22:05–22:22)"`, `"0910 22:05–22:22에서"`, `"(P03 04:12)"`, `"14:37에 생략"`, `"(0910 22:05, 강의노트 2장 p3)"`. Assert one `stt-time` for each. Assert `[]` for `"0910 수업"`, `"강의노트 2장 p14"`, `"24시간 뒤"`, `"교재 p.68"`. Add a `check_common` test with `<script>const t="0910 22:05"</script><p>0910 수업</p>` and assert no `stt-time`.

```python
for value in ("(0910 22:05–22:22)", "0910 22:05–22:22에서", "(P03 04:12)", "14:37에 생략", "(0910 22:05, 강의노트 2장 p3)"):
    with self.subTest(value=value):
        self.assertEqual([p.code for p in check_html.stt_time_problems(value, "x.html")], ["stt-time"])
for value in ("0910 수업", "강의노트 2장 p14", "24시간 뒤", "교재 p.68"):
    self.assertEqual(check_html.stt_time_problems(value, "x.html"), [])
```

- [ ] **Step 2: Run the focused test and confirm red.** Run `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_check_html.py -v` from the repo root. Expected: `AttributeError` for the missing helper.
- [ ] **Step 3: Implement the minimal checker.** Match clock shaped tokens with `(?<!\d)(?:[01]?\d|2[0-3]|[3-9]\d):[0-5]\d(?!\d)`; the `[3-9]\d` arm covers STT recordings longer than an hour, such as `63:04`. Return one `Problem("stt-time", where, context)` per containing line, with a short context snippet and its line number. Scan `doc.body_text`, which already omits script/style content, in `check_common`. Keep display times as a reviewable failure; do not auto-delete in the checker.

```python
STT_CLOCK_RE = re.compile(r"(?<!\d)(?:[01]?\d|2[0-3]|[3-9]\d):[0-5]\d(?!\d)")

def stt_time_problems(text: str, where: str) -> list[Problem]:
    return [Problem("stt-time", where, f"line {n}: {line.strip()[:120]}")
            for n, line in enumerate(text.splitlines(), 1) if STT_CLOCK_RE.search(line)]
```

- [ ] **Step 4: Remove `(0101 01:00)` and `(0101 02:00)` from the two mini-run fixture quotes; update `test_missing_layer`'s exact old string.** Run the focused suite again. Expected: PASS.
- [ ] **Step 5: Run `python -m unittest discover -s .agents/skills/bio-review-pack/tests -v`.** Fix only failures caused by the new rule; preserve unrelated behavior. Commit Task 1 files with `git add` on these exact paths and `git commit -m "test(notes): reject STT times in review HTML"`.

### Task 2: 작성 규칙에서 시각 노출 제거

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/content-rules.md:17,23,37,77`
- Modify: `.agents/skills/bio-review-pack/references/card-rules.md:16,45`
- Modify: `.agents/skills/bio-review-pack/SKILL.md:142-151,165-173`

**Interfaces:**
- Consumes: STT summary timestamps for private evidence checking.
- Produces: section/card briefs that emit no STT clock time and a pre-report check that scans HTML and MD.

- [ ] **Step 1: Add the explicit authoring rule.** In `content-rules.md`, replace instructions to show `(MMDD MM:SS)` in next-topic, warn, and prof layers with: `STT의 시각·구간·파트 번호는 근거 확인에만 쓰고 학생용 HTML 문장과 인용에는 적지 않는다. 날짜 배지와 강의노트·교재 쪽수는 유지한다.` Add “시각 없음” to the self-check. In `card-rules.md`, specify `수업과의 연결` uses the concept or professor's point without STT time, and add this to card self-check. Preserve `stt-summary-prompt.md` unchanged.
- [ ] **Step 2: Extend the workflow gate.** In `SKILL.md` step 5, state that `stt-time` is a FAIL needing source-fragment correction. In step 8, after `html2md.py --check`, scan both generated MD and `장마감_*.md` for the same `HH:MM` shaped candidates; inspect each hit and remove STT location text before reporting. Note that an actual course-time example must be reviewed rather than silently dropped.
- [ ] **Step 3: Search the skill text.** Run `rg -n 'MM:SS|타임스탬프|[0-9]{4} [0-9]{1,2}:[0-9]{2}' .agents/skills/bio-review-pack -g '*.md'`. Expected: student-facing timestamp instructions absent from `content-rules.md` and `card-rules.md`; internal summary, audit, and reporting references may remain. Commit the three files with `git commit -m "docs(notes): keep STT times out of review packs"`.

### Task 3: 기존 복습팩 정리와 전체 검증

**Files:**
- Modify: `복습노트/*/정리노트_*.html`, `복습노트/*/복습문제_*.html` where STT clocks appear.
- Regenerate: matching `복습노트/*/정리노트_*.md`, `복습문제_*.md`.
- Modify: `복습노트/*/장마감_*.md` where STT clocks appear.

**Interfaces:**
- Consumes: `stt_time_problems` from Task 1 and `html2md.py NOTE REVIEW --check`.
- Produces: existing student-readable packs with no STT clock references.

- [ ] **Step 1: Record the baseline without editing.** Run `rg -n '[0-9]{1,2}:[0-9]{2}' 복습노트 -g '*.html' -g '*.md'` and list affected folders. Inspect examples of each shape: full parenthesized citation, mixed citation, inline `…에서`, bare time, range, `P03` time, and chapter-close table. Leave any non-STT learning times intact.
- [ ] **Step 2: Edit affected HTML text and chapter-close MD.** Remove STT clocks while keeping quotation text and real source names. For `(0910 22:05, 강의노트 2장 p3)`, retain `(강의노트 2장 p3)`. Change `0910 22:05–22:22에서 교수님이…` to `수업에서 교수님이…`; change a bare `14:37에 생략했다고` to `수업에서 생략했다고`. Do not alter tags, ids, `href`, `src`, scripts, formulas, or original problem/choice wording. Review every changed line with `git diff -- 복습노트` before regenerating MD.
- [ ] **Step 3: Regenerate each affected folder's MD from its two HTML files.** Use the exact matching paths returned by `Get-ChildItem 복습노트 -Recurse -Filter '정리노트_*.html'` and the `복습문제_*.html` in the same folder; execute `python .agents/skills/bio-review-pack/scripts/html2md.py <note-absolute-path> <review-absolute-path> --check` once per affected folder. Expected: `OK`. This conversion rewrites both MD files and can update generated SVG figures; inspect `git status --short` and keep only the converter's intended outputs.
- [ ] **Step 4: Verify all remaining candidates.** Run `rg -n '[0-9]{1,2}:[0-9]{2}' 복습노트 -g '*.html' -g '*.md'`. Resolve each remaining STT clock in source HTML or chapter-close MD, regenerate MD if HTML changed, and rerun until only confirmed learning-time content remains. Run `python .agents/skills/bio-review-pack/scripts/check_html.py <each-note-html> <each-review-html>` for all existing folders; pre-existing unrelated failures must be recorded separately, and `stt-time` must be zero. Run `git diff --check`.
- [ ] **Step 5: Inspect student prose and structural diff.** Specifically reread the former `0910 22:05–22:22에서` sentence, all lines containing `교수님`, `수업과의 연결`, and `끊긴 지점` that changed, plus mixed-source citations. Check that all HTML→MD links and figure references still resolve using each folder's `html2md.py --check` result. Commit only the changed `복습노트/` paths with `git commit -m "docs(notes): remove recording times from review packs"`.

## Self-review

- Spec coverage: historical HTML, derived MD, chapter-close MD, authoring rule, internal evidence preservation, recurrence check, and verification each map to Tasks 1–3.
- Placeholder scan: no pending implementation decisions or unspecified path patterns.
- Type consistency: Task 1 defines `stt_time_problems(text: str, where: str) -> list[Problem]`; Task 3 consumes its `stt-time` result through `check_html.py`.
- Review Focus: five risks above are exercised or inspected in the owning task.
