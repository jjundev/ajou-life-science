# 생명과학 예습노트 스킬 (`bio-preview-note`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 다음 생명과학 수업의 강의노트 범위로, 수업 중 옆에 띄워 둘 짧은 예습노트 HTML(+MD)을 만드는 `bio-preview-note` 스킬을 만든다.

**Architecture:** 새 스킬 `.agents/skills/bio-preview-note/`의 스크립트는 `_review.py`로 `bio-review-pack/scripts`를 import 경로에 넣고, 복습 스킬의 검사기(`check_common`, `check_note`), manifest 헬퍼, 조립 도우미, `html2md`를 재사용한다. 예습 전용 로직(수업일·시작 쪽 고르기, manifest 계약, 분량·쪽 태그·기출 배지 검사)은 머신러닝기초 저장소의 `ml-preview-note` 스크립트를 생명과학 자료 구조(장·쪽·날짜)에 맞게 옮긴다. 템플릿은 `bio-review-pack`의 `note-template.html`을 심링크로 공유한다.

**Tech Stack:** Python 3 표준 라이브러리(스킬 스크립트), `unittest`, PyMuPDF(`fitz`, SKILL.md 스니펫에서만), KaTeX CDN(템플릿에 이미 있음).

**Spec:** `docs/superpowers/specs/2026-09-29-bio-preview-note-design.md`

## Global Constraints

- 스킬 원본은 `.agents/skills/bio-preview-note/`, 진입점은 심링크 `.claude/skills/bio-preview-note` → `../../.agents/skills/bio-preview-note`.
- 스크립트는 표준 라이브러리만 쓴다(`fitz`는 SKILL.md의 heredoc 스니펫에서만).
- 산출물 이름: `예습노트/<MMDD>/예습노트_<MMDD>_<slug>.html`, 같은 이름 `.md`, `figures_<MMDD>/`.
- 쪽 태그 형식: `4장 p3`, 범위는 en dash `4장 p3–p4`.
- 분량: 토픽 본문 600자 이하, 쉽게 말하면 2문장 이하, 들을 때 포인트 2항목 이하, 720×900에서 한 화면.
- 교과서 보충 배지 글자는 `교과서 보충`, 기출 배지는 `<span class="badge exam">기출</span>`.
- 그림: 강의노트·교과서가 그림으로 설명하는 개념(manifest 토픽 `figure_ref`)이면 쉽게 말하면 레이어에 인라인 SVG 1개. 교과서 그림은 그대로 넣지 않고(`<img>` 금지) 참고 PNG `RUN/work/textbook-figs/<토픽id>.png`(PyMuPDF, dpi 150, 저장소·산출물에 넣지 않음)를 보고 구조를 따라 다시 그린다. figcaption에 출처("교과서 그림 4.3을 단순하게 다시 그렸어요"). 색은 `fig-*` 클래스만. 그림이 있는 토픽은 글 300자 안팎, 720×900 한 화면.
- 파일명·폴더명은 NFC로 비교한다(macOS NFD 이름도 찾는다).
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 스킬 테스트: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests` / 복습 스킬: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests` (시작 기준선 78 OK) / 저장소: `.venv-question-bank/bin/python -m unittest discover tests` (시작 기준선 60 OK, skipped=1).
- 모든 명령은 저장소 루트 `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학`에서 실행한다.

## Review Focus

- NFD 이름의 `복습노트/`·`예습노트/` 폴더와 파일 — pick·backup이 NFC 이름처럼 찾아야 한다 (Task 6 `test_nfd_names`, `test_nfd_notes_dir_backed_up`).
- 기간 폴더 정리노트(`정리노트_0923-0924_…`) — "가장 최근"은 범위 **끝** 날짜로 판단해야 한다 (Task 6 `test_range_note_uses_end_date`).
- 오늘 수업 STT가 이미 있을 때 인자 없이 실행 — 다음 화·목으로 넘어가야 한다(끝난 수업을 예습하지 않음) (Task 6 `test_default_date_skips_class_with_stt`).
- manifest에 하이픈 `-`로 쓴 쪽 범위(`4장 p2-3`) — 검증에서 막아야 한다(태그 비교가 조용히 실패하지 않게) (Task 2 `test_slides_format`).
- 쪽 태그가 없는 옛 정리노트가 가장 최근일 때 — 무엇이 없는지 말하고 멈춰야 한다 (Task 6 `test_note_without_tags`).

---

## File Structure

```
.agents/skills/bio-review-pack/
  assets/note-template.html          (수정: {{BRAND}} 슬롯, .layer.listen·.badge.exam CSS)
  scripts/assemble.py                (수정: BRAND 값 "정리노트")
  tests/test_template.py             (새로)
.agents/skills/bio-preview-note/
  SKILL.md                           절차 0~9
  references/content-rules.md        작성자 브리프·마크업·분량 규칙
  references/manifest-guide.md       manifest 계약
  references/review-prompt.md        리뷰어 지시문
  references/browser-check.md        브라우저 검증
  assets/note-template.html  ->  ../../bio-review-pack/assets/note-template.html
  scripts/_review.py                 bio-review-pack/scripts를 sys.path에 넣음
  scripts/preview_manifest.py        manifest 로더·검증기
  scripts/preview_assemble.py        manifest + 섹션 조각 → HTML
  scripts/preview_check.py           예습노트 검사기
  scripts/preview_md.py              HTML → MD
  scripts/preview_files.py           pick / backup
  tests/_preview_util.py
  tests/fixtures/mini-run/{manifest.json, sections/s0.html, s1.html, s2.html}
  tests/test_preview_{manifest,template,assemble,check,md,files,skill_files}.py
.claude/skills/bio-preview-note  ->  ../../.agents/skills/bio-preview-note
```

---

### Task 1: 공유 템플릿에 BRAND 슬롯과 예습 레이어 스타일 추가

**Files:**
- Modify: `.agents/skills/bio-review-pack/assets/note-template.html:86-93,325`
- Modify: `.agents/skills/bio-review-pack/scripts/assemble.py:62-73` (`build_note`의 슬롯 딕셔너리)
- Create: `.agents/skills/bio-review-pack/tests/test_template.py`
- Modify: `.agents/skills/bio-review-pack/tests/test_assemble.py` (브랜드 테스트 추가)

**Interfaces:**
- Produces: 템플릿 슬롯 집합 `{"BRAND","DESCRIPTION","FOOTER","PAGE_TITLE","RANGE","SCRIPTS","SECTIONS","SUBTITLE","TITLE","TOC"}`, CSS 선택자 `.layer.listen`, `.layer.listen .layer-title`, `.badge.exam`. 복습 정리노트의 brand 글자는 계속 `정리노트`.

- [ ] **Step 1: 실패하는 테스트 작성**

`.agents/skills/bio-review-pack/tests/test_template.py`:
```python
"""정리노트 템플릿이 예습 스킬(bio-preview-note)과 공유하는 슬롯·스타일을 지킨다."""

import re
import unittest

from _util import SKILL

TEMPLATE = SKILL / "assets" / "note-template.html"
SLOTS = {"BRAND", "DESCRIPTION", "FOOTER", "PAGE_TITLE", "RANGE", "SCRIPTS", "SECTIONS", "SUBTITLE", "TITLE", "TOC"}


class TestNoteTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")

    def test_slots(self):
        self.assertEqual(set(re.findall(r"\{\{([A-Z_]+)\}\}", self.text)), SLOTS)

    def test_brand_is_slot(self):
        self.assertIn('<strong class="brand">{{BRAND}}</strong>', self.text)

    def test_preview_styles(self):
        for sel in (".layer.listen", ".layer.listen .layer-title", ".badge.exam"):
            with self.subTest(sel=sel):
                self.assertIn(sel, self.text)


if __name__ == "__main__":
    unittest.main()
```

`.agents/skills/bio-review-pack/tests/test_assemble.py`의 `test_sections_toc_and_titles` 바로 아래에 추가:
```python
    def test_note_brand(self):
        self.assertIn('<strong class="brand">정리노트</strong>', self.note_html)
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p "test_template.py" -v`
Expected: FAIL — `test_slots`(BRAND 없음), `test_brand_is_slot`, `test_preview_styles` 실패. (`test_note_brand`는 지금 통과한다. 템플릿이 글자를 박아 두고 있어서다. 조립기가 슬롯을 채우는지는 Step 4에서 확인한다.)

- [ ] **Step 3: 템플릿과 조립기 수정**

`note-template.html` 86행:
```css
    .layer.prof, .layer.warn, .layer.listen { font-size: var(--fs-sub); line-height: 1.7; }
```
89행:
```css
    .layer.warn, .layer.listen { background: var(--surface); border-top: 0; border-radius: var(--radius); padding: var(--s4); }
```
90행(`.layer.warn .layer-title …`) 바로 아래에 추가:
```css
    .layer.listen .layer-title { color: var(--accent-ink); font-size: var(--fs-body); }
```
93행(`.badge.supp { color: var(--supp); }`) 바로 아래에 추가:
```css
    .badge.exam { color: var(--warn); margin-right: var(--s1); }
```
325행:
```html
      <strong class="brand">{{BRAND}}</strong>
```
`--s1`이 없으면 `grep -n -- "--s1" note-template.html`로 확인하고, 없을 때는 `margin-right: 4px;`로 쓴다.

`assemble.py`의 `build_note` 슬롯 딕셔너리에서 `"PAGE_TITLE"` 다음 줄에 추가:
```python
        "BRAND": "정리노트",
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `Ran 82 tests … OK` (기존 78 + 템플릿 3 + 브랜드 1)

Run: `.venv-question-bank/bin/python -m unittest discover tests`
Expected: `Ran 60 tests … OK (skipped=1)`

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-review-pack/assets/note-template.html .agents/skills/bio-review-pack/scripts/assemble.py .agents/skills/bio-review-pack/tests/test_template.py .agents/skills/bio-review-pack/tests/test_assemble.py
git commit -m "feat(skills): add brand slot and listen styles to note template

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: 스킬 뼈대와 manifest 검증기

**Files:**
- Create: `.agents/skills/bio-preview-note/scripts/_review.py`
- Create: `.agents/skills/bio-preview-note/scripts/preview_manifest.py`
- Create: `.agents/skills/bio-preview-note/tests/_preview_util.py`
- Create: `.agents/skills/bio-preview-note/tests/fixtures/mini-run/manifest.json`
- Test: `.agents/skills/bio-preview-note/tests/test_preview_manifest.py`

**Interfaces:**
- Consumes: `bio-review-pack/scripts/manifest.py`의 `ManifestError`, `_need(obj, key, typ, where, errors) -> bool`, `_objects(items, where, errors)`(`(i, obj)` 반복자), `_strings(items, where, errors) -> None`.
- Produces: `preview_manifest.validate(m: dict) -> list[str]`, `load(path) -> dict`(오류 시 `ManifestError`), `note_name(m) -> "예습노트_<range>_<slug>.html"`, `fig_dir_name(range_: str) -> "figures_<range>"`, `main(argv) -> int`. manifest 키: `course, range, chapters, slug, pdfs, note_title, note_subtitle, footer_note, sections, links`; 토픽 키: `id, title, slides, required_terms, layers, supp`, 선택 `exam_terms`(문자열 목록), 선택 `figure_ref`(문자열, 예: `"그림 4.3"`). 테스트 공용 `_preview_util`의 `TESTS, SKILL, SCRIPTS, FIXTURES, MINI_RUN, REPO, REVIEW_SKILL`.

- [ ] **Step 1: 테스트 공용 모듈과 픽스처 manifest 작성**

`tests/_preview_util.py`:
```python
"""예습 스킬 테스트 공통 경로."""

from __future__ import annotations

from pathlib import Path
import sys

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = TESTS / "fixtures"
MINI_RUN = FIXTURES / "mini-run"
REPO = SKILL.parents[2]  # <repo>/.agents/skills/bio-preview-note
REVIEW_SKILL = SKILL.parent / "bio-review-pack"
sys.path.insert(0, str(SCRIPTS))
```

`tests/fixtures/mini-run/manifest.json`:
```json
{
 "course": "생명과학",
 "range": "0101",
 "chapters": ["4"],
 "slug": "Mini_Preview",
 "pdfs": ["강의노트/4장 유전.pdf"],
 "note_title": "Mini — 수업 전에 보는 예습노트",
 "note_subtitle": "테스트용 · 4장 예습",
 "footer_note": "출처: 테스트 픽스처",
 "sections": [
  {"id": "s0", "title": "0. 미리 알아둘 것", "short": "0 미리", "topics": [
   {"id": "s0-meiosis", "title": "감수분열 다시 보기", "slides": "", "required_terms": ["상동염색체"], "layers": ["eli5", "formal"], "supp": false}
  ]},
  {"id": "s1", "title": "1. 멘델의 법칙 이어서", "short": "1 멘델", "topics": [
   {"id": "s1-dihybrid", "title": "양성잡종 교배", "slides": "4장 p2–p3", "required_terms": ["양성잡종", "9:3:3:1", "독립의 법칙"], "exam_terms": ["독립의 법칙"], "figure_ref": "그림 4.3", "layers": ["eli5", "formal", "listen"], "supp": false},
   {"id": "s1-incomplete", "title": "불완전우성", "slides": "4장 p3", "required_terms": ["불완전우성", "이형접합자"], "layers": ["eli5", "formal"], "supp": true}
  ]},
  {"id": "s2", "title": "2. 한눈에 보기", "short": "2 한눈에", "topics": [
   {"id": "s2-cheatsheet", "title": "치트시트", "slides": "", "required_terms": ["불완전우성"], "layers": [], "supp": false},
   {"id": "s2-links", "title": "함께 보면 좋은 자료", "slides": "", "required_terms": [], "layers": [], "supp": false}
  ]}
 ],
 "links": [{"topic": "s2-links", "href": "#s1-dihybrid"}]
}
```

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/test_preview_manifest.py`:
```python
import copy
import io
import json
from contextlib import redirect_stdout
import unittest

from _preview_util import MINI_RUN

import preview_manifest as pm

BASE = json.loads((MINI_RUN / "manifest.json").read_text(encoding="utf-8"))


def errors_with(mutate):
    m = copy.deepcopy(BASE)
    mutate(m)
    return pm.validate(m)


def topic(m, s, t):
    return m["sections"][s]["topics"][t]


class TestPreviewManifest(unittest.TestCase):
    def test_fixture_valid(self):
        self.assertEqual(pm.validate(BASE), [])
        self.assertEqual(pm.load(MINI_RUN / "manifest.json")["range"], "0101")

    def test_names(self):
        self.assertEqual(pm.note_name(BASE), "예습노트_0101_Mini_Preview.html")
        self.assertEqual(pm.fig_dir_name("0101"), "figures_0101")

    def test_missing_top_level_key(self):
        errs = errors_with(lambda m: m.pop("pdfs"))
        self.assertTrue(any("manifest.pdfs" in e for e in errs), errs)

    def test_bad_range(self):
        for bad in ("929", "0929-1001", "L04"):
            with self.subTest(range=bad):
                errs = errors_with(lambda m: m.update(range=bad))
                self.assertTrue(any("manifest.range" in e for e in errs), errs)

    def test_bad_chapters(self):
        for bad in ([], ["4장"], [4]):
            with self.subTest(chapters=bad):
                errs = errors_with(lambda m: m.update(chapters=bad))
                self.assertTrue(any("manifest.chapters" in e for e in errs), errs)

    def test_bad_pdfs(self):
        for bad in ([], ["4장 유전.pdf"]):
            with self.subTest(pdfs=bad):
                errs = errors_with(lambda m: m.update(pdfs=bad))
                self.assertTrue(any("manifest.pdfs" in e for e in errs), errs)

    def test_stt_layer_rejected(self):
        errs = errors_with(lambda m: topic(m, 1, 0)["layers"].append("prof"))
        self.assertTrue(any("알 수 없는 레이어" in e for e in errs), errs)

    def test_concept_topic_needs_eli5_and_formal(self):
        errs = errors_with(lambda m: topic(m, 1, 1).update(layers=["eli5", "listen"]))
        self.assertTrue(any("eli5와 formal" in e for e in errs), errs)

    def test_slides_format(self):
        for bad in ("4장 p2-3", "4장 p2–3", "p2", "4장", "s2", "4 p2", ""):
            with self.subTest(slides=bad):
                errs = errors_with(lambda m: topic(m, 1, 0).update(slides=bad))
                self.assertTrue(any(".slides" in e for e in errs), errs)

    def test_slides_ok(self):
        for good in ("4장 p3", "12장 p1–p6"):
            with self.subTest(slides=good):
                self.assertEqual(errors_with(lambda m: topic(m, 1, 0).update(slides=good)), [])

    def test_s0_topic_may_omit_slides(self):
        self.assertEqual(errors_with(lambda m: topic(m, 0, 0).update(slides="")), [])
        errs = errors_with(lambda m: topic(m, 0, 0).update(slides="p2"))
        self.assertTrue(any(".slides" in e for e in errs), errs)

    def test_exam_terms_must_be_required_terms(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(exam_terms=["멘델"]))
        self.assertTrue(any("exam_terms" in e and "required_terms" in e for e in errs), errs)

    def test_exam_terms_need_listen(self):
        errs = errors_with(lambda m: topic(m, 1, 1).update(exam_terms=["불완전우성"]))
        self.assertTrue(any("exam_terms" in e and "listen" in e for e in errs), errs)

    def test_exam_terms_type(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(exam_terms="독립의 법칙"))
        self.assertTrue(any("exam_terms" in e for e in errs), errs)

    def test_exam_terms_optional(self):
        self.assertEqual(errors_with(lambda m: topic(m, 1, 0).pop("exam_terms")), [])

    def test_figure_ref_type(self):
        for bad in ("", "  ", ["그림 4.3"], 4.3):
            with self.subTest(figure_ref=bad):
                errs = errors_with(lambda m: topic(m, 1, 0).update(figure_ref=bad))
                self.assertTrue(any("figure_ref" in e for e in errs), errs)

    def test_figure_ref_needs_eli5(self):
        errs = errors_with(lambda m: topic(m, 2, 0).update(figure_ref="그림 4.3"))
        self.assertTrue(any("figure_ref" in e and "eli5" in e for e in errs), errs)

    def test_section_ids_in_order(self):
        errs = errors_with(lambda m: m["sections"][0].update(id="s9"))
        self.assertTrue(any("s0이어야 함" in e for e in errs), errs)

    def test_topic_id_prefix(self):
        errs = errors_with(lambda m: topic(m, 1, 0).update(id="s0-dihybrid"))
        self.assertTrue(any("s1-로 시작" in e for e in errs), errs)

    def test_last_section_needs_cheatsheet_and_links(self):
        errs = errors_with(lambda m: m["sections"][2]["topics"].pop(0))
        self.assertTrue(any("s2-cheatsheet" in e for e in errs), errs)

    def test_single_section_rejected(self):
        errs = errors_with(lambda m: m.update(sections=m["sections"][:1]))
        self.assertTrue(any("2개 이상" in e for e in errs), errs)

    def test_supp_on_summary_topic_rejected(self):
        errs = errors_with(lambda m: topic(m, 2, 0).update(supp=True))
        self.assertTrue(any(".supp" in e for e in errs), errs)

    def test_link_to_unknown_topic(self):
        errs = errors_with(lambda m: m["links"].append({"topic": "s7-x", "href": "#a"}))
        self.assertTrue(any("없는 토픽" in e for e in errs), errs)

    def test_cli_ok(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pm.main([str(MINI_RUN / "manifest.json")])
        self.assertEqual((code, out.getvalue().strip()), (0, "OK"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_manifest.py"`
Expected: FAIL — `ModuleNotFoundError: No module named 'preview_manifest'`

- [ ] **Step 4: 구현**

`scripts/_review.py`:
```python
"""bio-review-pack의 scripts/를 import 경로에 넣는다. 양식·검사 로직을 복습 스킬과 공유하기 위해서다."""

from pathlib import Path
import sys

REVIEW_SCRIPTS = Path(__file__).resolve().parents[2] / "bio-review-pack" / "scripts"
if not REVIEW_SCRIPTS.is_dir():
    raise ImportError(f"bio-review-pack 스킬 없음: {REVIEW_SCRIPTS}")
if str(REVIEW_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS))
```

`scripts/preview_manifest.py`:
```python
#!/usr/bin/env python3
"""
생명과학 예습노트 manifest.json 로더·검증기 (표준 라이브러리만 사용).

manifest는 한 번의 실행(수업일 하나)에 대한 계약이다. preview_assemble.py와 preview_check.py가 읽는다.
CLI: preview_manifest.py RUN/manifest.json   (검증만, 오류가 있으면 목록 출력 후 종료 코드 1)
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401  (bio-review-pack/scripts를 import 경로에 넣는다)
from manifest import ManifestError, _need, _objects, _strings  # noqa: E402  (복습 스킬 공용 도우미)

LAYER_NAMES = {"eli5", "formal", "listen"}
CONCEPT_LAYERS = {"eli5", "formal"}
TOP_LEVEL_TYPES = {
    "course": str, "range": str, "chapters": list, "slug": str, "pdfs": list,
    "note_title": str, "note_subtitle": str, "footer_note": str,
    "sections": list, "links": list,
}
RANGE_RE = re.compile(r"\d{4}")
CHAPTER_RE = re.compile(r"\d{1,2}")
SLUG_RE = re.compile(r"[A-Za-z0-9_]+")
ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
SLIDES_RE = re.compile(r"\d{1,2}장 p\d+(–p\d+)?")  # 범위는 en dash(–)
PDF_PREFIX = "강의노트/"


def _check_exam_terms(t: dict, tw: str, errors: list[str]) -> None:
    if "exam_terms" not in t:
        return
    exam = t["exam_terms"]
    if not isinstance(exam, list) or not all(isinstance(x, str) and x for x in exam):
        errors.append(f"{tw}.exam_terms: 빈 문자열이 아닌 문자열 목록이어야 함")
        return
    missing = [x for x in exam if x not in t["required_terms"]]
    if missing:
        errors.append(f"{tw}.exam_terms: required_terms에 없는 용어 {missing}")
    if exam and "listen" not in t["layers"]:
        errors.append(f"{tw}.exam_terms: listen 레이어가 있는 토픽에만 쓸 수 있음")


def _check_figure_ref(t: dict, tw: str, errors: list[str]) -> None:
    """figure_ref: 이 토픽이 따라 그릴 교과서·강의노트 그림(예: "그림 4.3"). 있으면 eli5에 SVG 1개가 필요하다."""
    if "figure_ref" not in t:
        return
    ref = t["figure_ref"]
    if not isinstance(ref, str) or not ref.strip():
        errors.append(f"{tw}.figure_ref: 빈 문자열이 아닌 문자열이어야 함(예: \"그림 4.3\")")
        return
    if "eli5" not in t["layers"]:
        errors.append(f"{tw}.figure_ref: eli5 레이어가 있는 토픽에만 쓸 수 있음")


def validate(m: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(m, dict):
        return ["manifest: JSON 객체 필요"]
    for key, typ in TOP_LEVEL_TYPES.items():
        _need(m, key, typ, "manifest", errors)
    if errors:
        return errors
    if not RANGE_RE.fullmatch(m["range"]):
        errors.append(f"manifest.range: 네 자리 수업 날짜(MMDD)여야 함: {m['range']}")
    if not SLUG_RE.fullmatch(m["slug"]):
        errors.append(f"manifest.slug: 영문·숫자·밑줄만: {m['slug']}")
    if not m["chapters"] or not all(isinstance(c, str) and CHAPTER_RE.fullmatch(c) for c in m["chapters"]):
        errors.append(f"manifest.chapters: 장 번호 문자열 목록이어야 함(예: [\"4\"]): {m['chapters']}")
    if not m["pdfs"] or not all(isinstance(p, str) and p.startswith(PDF_PREFIX) for p in m["pdfs"]):
        errors.append(f"manifest.pdfs: '{PDF_PREFIX}'로 시작하는 경로 목록이어야 함: {m['pdfs']}")
    if len(m["sections"]) < 2:
        errors.append("sections: '미리 알아둘 것'과 '한눈에 보기'를 포함해 2개 이상 필요")

    seen: set[str] = set()
    topic_ids: set[str] = set()

    def new_id(value: str, where: str) -> None:
        if not ID_RE.fullmatch(value):
            errors.append(f"{where}: id 형식 오류: {value}")
        if value in seen:
            errors.append(f"{where}: 중복 id: {value}")
        seen.add(value)

    for i, sec in _objects(m["sections"], "sections", errors):
        where = f"sections[{i}]"
        if not all([_need(sec, "id", str, where, errors), _need(sec, "title", str, where, errors),
                    _need(sec, "short", str, where, errors), _need(sec, "topics", list, where, errors)]):
            continue
        new_id(sec["id"], where)
        if sec["id"] != f"s{i}":
            errors.append(f"{where}.id: s{i}이어야 함: {sec['id']}")
        for j, t in _objects(sec["topics"], f"{where}.topics", errors):
            tw = f"{where}.topics[{j}]"
            ok = all([_need(t, "id", str, tw, errors), _need(t, "title", str, tw, errors),
                      _need(t, "slides", str, tw, errors), _need(t, "required_terms", list, tw, errors),
                      _need(t, "layers", list, tw, errors), _need(t, "supp", bool, tw, errors)])
            if not ok:
                continue
            new_id(t["id"], tw)
            topic_ids.add(t["id"])
            if not t["id"].startswith(f"{sec['id']}-"):
                errors.append(f"{tw}.id: {sec['id']}-로 시작해야 함: {t['id']}")
            _strings(t["required_terms"], f"{tw}.required_terms", errors)
            if not all(isinstance(x, str) for x in t["layers"]):
                errors.append(f"{tw}.layers: 문자열 목록이어야 함")
                continue
            unknown = set(t["layers"]) - LAYER_NAMES
            if unknown:
                errors.append(f"{tw}.layers: 알 수 없는 레이어 {sorted(unknown)}")
            if t["layers"]:
                if not CONCEPT_LAYERS <= set(t["layers"]):
                    errors.append(f"{tw}.layers: 개념 토픽은 eli5와 formal 필요")
                # s0(미리 알아둘 것)은 강의노트 쪽이 아니라 선수 개념이라 빈 문자열을 허용한다
                if not SLIDES_RE.fullmatch(t["slides"]) and not (sec["id"] == "s0" and t["slides"] == ""):
                    errors.append(f"{tw}.slides: '4장 p3' 또는 '4장 p3–p4'(en dash) 형식이어야 함(s0만 빈 문자열 허용): {t['slides']!r}")
            elif t["supp"]:
                errors.append(f"{tw}.supp: 레이어가 없는 토픽은 false여야 함")
            _check_exam_terms(t, tw, errors)
            _check_figure_ref(t, tw, errors)

    last = m["sections"][-1] if m["sections"] else None
    if isinstance(last, dict) and isinstance(last.get("id"), str) and isinstance(last.get("topics"), list):
        ids = {t.get("id") for t in last["topics"] if isinstance(t, dict)}
        for suffix in ("cheatsheet", "links"):
            if f"{last['id']}-{suffix}" not in ids:
                errors.append(f"sections[-1]: 토픽 {last['id']}-{suffix} 필요")

    for i, link in _objects(m["links"], "links", errors):
        where = f"links[{i}]"
        if _need(link, "topic", str, where, errors) and link["topic"] not in topic_ids:
            errors.append(f"{where}.topic: 없는 토픽: {link['topic']}")
        _need(link, "href", str, where, errors)
    return errors


def load(path: Path | str) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ManifestError(f"{path}: 파일을 읽을 수 없음: {e}") from e
    try:
        m = json.loads(text)
    except json.JSONDecodeError as e:
        raise ManifestError(f"{path}: JSON 형식 오류: {e}") from e
    errors = validate(m)
    if errors:
        raise ManifestError("\n".join(errors))
    return m


def note_name(m: dict) -> str:
    return f"예습노트_{m['range']}_{m['slug']}.html"


def fig_dir_name(range_: str) -> str:
    return f"figures_{range_}"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("사용법: preview_manifest.py RUN/manifest.json", file=sys.stderr)
        return 2
    try:
        load(argv[0])
    except ManifestError as e:
        print(e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_manifest.py" -v`
Expected: 24 tests OK. `_need`/`_objects`/`_strings` import가 실패하면 `grep -n "^def _" .agents/skills/bio-review-pack/scripts/manifest.py`로 이름을 확인한다(33·42·49행에 있다).

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-preview-note/scripts/_review.py .agents/skills/bio-preview-note/scripts/preview_manifest.py .agents/skills/bio-preview-note/tests/_preview_util.py .agents/skills/bio-preview-note/tests/fixtures/mini-run/manifest.json .agents/skills/bio-preview-note/tests/test_preview_manifest.py
git commit -m "feat(skills): add bio-preview-note manifest contract

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: 조립기와 공유 템플릿 심링크

**Files:**
- Create: `.agents/skills/bio-preview-note/assets/note-template.html` (심링크 → `../../bio-review-pack/assets/note-template.html`)
- Create: `.agents/skills/bio-preview-note/scripts/preview_assemble.py`
- Create: `.agents/skills/bio-preview-note/tests/fixtures/mini-run/sections/s0.html`, `s1.html`, `s2.html`
- Test: `.agents/skills/bio-preview-note/tests/test_preview_template.py`, `test_preview_assemble.py`

**Interfaces:**
- Consumes: `preview_manifest.load`, `note_name` (Task 2). `bio-review-pack/scripts/assemble.py`의 `AssembleError`, `esc(str) -> str`, `fill(template: str, values: dict) -> str`(빠진 슬롯이면 `AssembleError`), `split_scripts(fragment) -> (body, scripts)`. Task 1의 슬롯 집합.
- Produces: `preview_assemble.assemble(run_dir, out_dir) -> Path`(예습노트 HTML 경로; 조각이 없으면 `AssembleError`, 아무 파일도 쓰지 않음), `other_notes(path: Path, range_: str) -> list[str]`, `main(argv) -> int`, 상수 `BRAND = "예습노트"`. 픽스처 조각(Task 4, 5에서 재사용).

- [ ] **Step 1: 심링크와 픽스처 조각 만들기**

```bash
mkdir -p .agents/skills/bio-preview-note/assets .agents/skills/bio-preview-note/tests/fixtures/mini-run/sections
ln -s ../../bio-review-pack/assets/note-template.html .agents/skills/bio-preview-note/assets/note-template.html
```

`tests/fixtures/mini-run/sections/s0.html`:
```html
      <article class="topic" id="s0-meiosis"><h3>감수분열 다시 보기</h3>
        <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">감수분열은 짝을 이룬 염색체를 한 개씩 나눠 담는 과정이에요.</p></div>
        <div class="layer formal"><span class="layer-title">정확히 말하면</span><dl><dt>상동염색체</dt><dd>부모에게서 하나씩 받은 같은 모양의 염색체 한 쌍이에요.</dd></dl></div>
        <div class="sum" hidden>
          <p class="sum-lead">감수분열은 상동염색체를 나눠요.</p>
        </div>
      </article>
```

`tests/fixtures/mini-run/sections/s1.html`:
```html
      <article class="topic" id="s1-dihybrid"><h3>양성잡종 교배</h3><div class="tags"><span class="tag slide">4장 p2–p3</span></div>
        <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">두 가지 특징은 서로 상관없이 따로 물려받아요.</p>
          <figure class="figure"><svg id="fig-dihybrid" viewBox="0 0 160 40" role="img" aria-label="네 칸으로 나뉜 막대"><rect x="10" y="10" width="140" height="20" class="fig-ink"/></svg><figcaption>둘째 자식 세대는 네 가지 모습으로 나뉘어요. 교과서 그림 4.3을 단순하게 다시 그렸어요.</figcaption></figure>
        </div>
        <div class="layer formal"><span class="layer-title">정확히 말하면</span><p>양성잡종(dihybrid)을 교배하면 둘째 자식 세대의 표현형이 9:3:3:1로 나와요.</p><ul><li>독립의 법칙: 서로 다른 형질의 대립유전자는 따로 분리돼요.</li></ul></div>
        <div class="layer listen"><span class="layer-title">들을 때 포인트</span><ul><li><span class="badge exam">기출</span> 독립의 법칙이 나오면 정의를 그대로 받아 적어 두세요.</li></ul></div>
        <div class="sum" hidden>
          <p class="sum-lead">두 형질은 따로 유전돼요.</p>
          <p class="panel-label">용어</p>
          <dl class="terms"><dt>양성잡종(dihybrid)</dt><dd>두 형질이 모두 이형접합인 개체</dd></dl>
        </div>
      </article>
      <article class="topic" id="s1-incomplete"><h3>불완전우성</h3><div class="tags"><span class="tag slide">4장 p3</span></div>
        <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">빨강과 흰색을 섞으면 분홍이 나오는 경우예요.</p></div>
        <div class="layer formal"><span class="layer-title">정확히 말하면</span><p>불완전우성에서는 이형접합자의 표현형이 두 동형접합자의 중간이에요.</p></div>
        <div class="layer supp"><span class="badge supp">교과서 보충</span><p>금어초 꽃 색 예시는 교과서 4장에 있어요.</p></div>
        <div class="sum" hidden>
          <p class="sum-lead">불완전우성은 중간 표현형을 만들어요.</p>
        </div>
      </article>
```

`tests/fixtures/mini-run/sections/s2.html`:
```html
      <article class="topic" id="s2-cheatsheet"><h3>치트시트</h3>
        <div class="table-wrap"><table><tr><th>개념</th><th>한 줄</th></tr><tr><td>불완전우성</td><td>이형접합자가 중간 표현형</td></tr></table></div>
      </article>
      <article class="topic" id="s2-links"><h3>함께 보면 좋은 자료</h3>
        <ul><li><a href="#s1-dihybrid">양성잡종 다시 보기</a></li></ul>
      </article>
```

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/test_preview_template.py`:
```python
"""공유 템플릿(심링크)이 예습 조립기가 기대하는 모양인지 지킨다. 복습 쪽에서 템플릿을 바꾸면 여기서 먼저 깨진다."""

import os
import re
import unittest

from _preview_util import REVIEW_SKILL, SKILL

TEMPLATE = SKILL / "assets" / "note-template.html"
SLOTS = {"BRAND", "DESCRIPTION", "FOOTER", "PAGE_TITLE", "RANGE", "SCRIPTS", "SECTIONS", "SUBTITLE", "TITLE", "TOC"}


class TestSharedTemplate(unittest.TestCase):
    def test_relative_symlink_to_review_template(self):
        self.assertTrue(TEMPLATE.is_symlink())
        self.assertEqual(os.readlink(TEMPLATE), "../../bio-review-pack/assets/note-template.html")
        self.assertEqual(TEMPLATE.resolve(), (REVIEW_SKILL / "assets" / "note-template.html").resolve())

    def test_slots(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"\{\{([A-Z_]+)\}\}", text)), SLOTS)

    def test_layer_styles(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for sel in (".layer.eli5", ".layer.formal", ".layer.listen", ".badge.supp", ".badge.exam"):
            with self.subTest(sel=sel):
                self.assertIn(sel, text)


if __name__ == "__main__":
    unittest.main()
```

`tests/test_preview_assemble.py`:
```python
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import shutil
import tempfile
import unittest

from _preview_util import MINI_RUN

import preview_assemble as pa
from assemble import AssembleError  # preview_assemble이 복습 scripts 경로를 넣은 뒤라 import된다


class TestPreviewAssemble(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.note = pa.assemble(MINI_RUN, self.tmp / "out")
        self.html = self.note.read_text(encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_output_name(self):
        self.assertEqual(self.note.name, "예습노트_0101_Mini_Preview.html")

    def test_titles_brand_range(self):
        self.assertIn("<title>생명과학 예습노트 0101</title>", self.html)
        self.assertIn('<strong class="brand">예습노트</strong>', self.html)
        self.assertIn('data-range="0101"', self.html)
        self.assertIn("<h1>Mini — 수업 전에 보는 예습노트</h1>", self.html)

    def test_sections_and_toc(self):
        self.assertIn('<a href="#s0">0 미리</a><a href="#s1">1 멘델</a><a href="#s2">2 한눈에</a>', self.html)
        self.assertIn('<section id="s1"><h2>1. 멘델의 법칙 이어서</h2>', self.html)

    def test_no_slots_left(self):
        self.assertNotIn("{{", self.html)

    def test_missing_fragment_writes_nothing(self):
        run = self.tmp / "run"
        shutil.copytree(MINI_RUN, run)
        (run / "sections" / "s2.html").unlink()
        out = self.tmp / "out2"
        with self.assertRaises(AssembleError):
            pa.assemble(run, out)
        self.assertFalse(out.exists())

    def test_warns_about_other_slug(self):
        out = self.tmp / "warn"
        out.mkdir()
        (out / "예습노트_0101_Old_Slug.html").write_text("old", encoding="utf-8")
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = pa.main(["--run", str(MINI_RUN), "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertIn("예습노트_0101_Old_Slug.html", err.getvalue())
        self.assertTrue((out / "예습노트_0101_Old_Slug.html").exists())  # 지우지 않고 알리기만 한다

    def test_cli(self):
        with redirect_stdout(io.StringIO()):
            code = pa.main(["--run", str(MINI_RUN), "--out", str(self.tmp / "cli")])
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "cli" / "예습노트_0101_Mini_Preview.html").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_a*.py"`
Expected: FAIL — `No module named 'preview_assemble'`. (`test_preview_template.py`는 Task 1과 Step 1 덕분에 이미 통과해야 한다: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_template.py"` → OK)

- [ ] **Step 4: 구현**

`scripts/preview_assemble.py`:
```python
#!/usr/bin/env python3
"""
manifest + 섹션 조각 → 생명과학 예습노트 HTML 하나 (표준 라이브러리만 사용).

실행 폴더 구조:
  RUN/manifest.json
  RUN/sections/<section-id>.html   (섹션 안쪽: <article class="topic"> 들)
템플릿은 bio-review-pack과 공유한다(assets/note-template.html 심링크).
CLI: preview_assemble.py --run RUN --out 예습노트/<MMDD>
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401
from assemble import AssembleError, esc, fill, split_scripts  # noqa: E402  (복습 스킬 공용)
import preview_manifest as pm  # noqa: E402

ASSETS = Path(__file__).resolve().parent.parent / "assets"
BRAND = "예습노트"


def read_fragment(path: Path) -> str:
    if not path.exists():
        raise AssembleError(f"조각 파일 없음: {path}")
    return path.read_text(encoding="utf-8")


def build_note(m: dict, run_dir: Path) -> str:
    sections, scripts = [], []
    for sec in m["sections"]:
        body, found = split_scripts(read_fragment(run_dir / "sections" / f"{sec['id']}.html"))
        scripts += found
        sections.append(f'    <section id="{sec["id"]}"><h2>{esc(sec["title"])}</h2>\n{body.strip()}\n    </section>')
    return fill((ASSETS / "note-template.html").read_text(encoding="utf-8"), {
        "PAGE_TITLE": esc(f"{m['course']} 예습노트 {m['range']}"),
        "BRAND": BRAND,
        "DESCRIPTION": esc(m["note_subtitle"]),
        "TOC": "".join(f'<a href="#{s["id"]}">{esc(s["short"])}</a>' for s in m["sections"]),
        "TITLE": esc(m["note_title"]),
        "SUBTITLE": esc(m["note_subtitle"]),
        "SECTIONS": "\n".join(sections),
        "FOOTER": m["footer_note"],
        "SCRIPTS": "\n".join(f"  {s}" for s in scripts),
        "RANGE": m["range"],
    })


def assemble(run_dir: Path | str, out_dir: Path | str) -> Path:
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    m = pm.load(run_dir / "manifest.json")
    html = build_note(m, run_dir)  # 조각이 하나라도 없으면 여기서 멈춰 아무 파일도 만들지 않는다
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / pm.note_name(m)
    path.write_text(html, encoding="utf-8")
    return path


def other_notes(path: Path, range_: str) -> list[str]:
    """같은 폴더에 남은 다른 slug의 예습노트(slug를 바꿔 다시 만들었을 때)."""
    prefix = f"예습노트_{range_}_"
    return sorted(n for n in (unicodedata.normalize("NFC", e) for e in os.listdir(path.parent))
                  if n.startswith(prefix) and n.endswith(".html") and n != path.name)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        path = assemble(args.run, args.out)
        print(path)
        range_ = path.name.split("_")[1]
        for name in other_notes(path, range_):
            print(f"경고: 다른 slug의 예습노트가 남아 있어요(지우지 않음): {name}", file=sys.stderr)
    except (AssembleError, pm.ManifestError) as e:
        print(f"assemble 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -v`
Expected: manifest 24 + template 3 + assemble 7 = 34 tests OK. `data-range` 단언이 실패하면 `grep -n "RANGE" .agents/skills/bio-review-pack/assets/note-template.html`로 템플릿의 속성 이름을 확인해 테스트 문자열을 맞춘다.

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-preview-note/assets .agents/skills/bio-preview-note/scripts/preview_assemble.py .agents/skills/bio-preview-note/tests/fixtures/mini-run/sections .agents/skills/bio-preview-note/tests/test_preview_template.py .agents/skills/bio-preview-note/tests/test_preview_assemble.py
git commit -m "feat(skills): assemble bio preview notes from shared template

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: 예습노트 검사기 (분량·쪽 태그·기출 배지·그림)

**Files:**
- Create: `.agents/skills/bio-preview-note/scripts/preview_check.py`
- Test: `.agents/skills/bio-preview-note/tests/test_preview_check.py`

**Interfaces:**
- Consumes: `bio-review-pack/scripts/check_html.py`의 `VOID_TAGS`, `Problem(code, where, detail)`(속성 `.code`, `.where`), `check_common(doc, source, path)`, `check_file(path)`, `check_note(doc, m)`(`m["preview_topic"]`, `m["forbidden_outside_preview"]` 필요), `parse_html(source) -> Doc`(`doc.containers[id].child_classes`, `.text`, `doc.img_srcs`). Task 2 `preview_manifest.load`, Task 3 `preview_assemble.assemble`.
- Produces: `preview_check.check_preview(m: dict, note_path) -> list[Problem]`, `topic_stats(source) -> dict[str, TopicStats]`, `visible_chars(text) -> int`, `sentences(text) -> int`, `main(argv) -> int`(`OK` / `FAIL (n)`). 문제 코드: `slide-tag`, `missing-supp`, `stt-layer`, `topic-long`, `eli5-long`, `listen-predicts`, `listen-long`, `exam-mark`, `figure`, `figure-source`, `textbook-image` + 복습 검사기 코드. `TopicStats`에 `exam_badges`, `eli5_svgs`, `captions` 추가.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_preview_check.py`:
```python
from contextlib import redirect_stdout
import io
from pathlib import Path
import shutil
import tempfile
import unittest

from _preview_util import MINI_RUN

import preview_assemble as pa
import preview_check as pc
import preview_manifest as pm

LEAD = "두 가지 특징은 서로 상관없이 따로 물려받아요."
FIG_SVG = '<svg id="fig-dihybrid" viewBox="0 0 160 40" role="img" aria-label="네 칸으로 나뉜 막대"><rect x="10" y="10" width="140" height="20" class="fig-ink"/></svg>'
FIG_SOURCE = "교과서 그림 4.3을 단순하게 다시 그렸어요."
LISTEN = "독립의 법칙이 나오면 정의를 그대로 받아 적어 두세요."
BADGE = '<span class="badge exam">기출</span> '


class TestPreviewCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.run = self.tmp / "run"
        shutil.copytree(MINI_RUN, self.run)
        self.m = pm.load(self.run / "manifest.json")

    def tearDown(self):
        self._tmp.cleanup()

    def patch(self, sid, old, new):
        p = self.run / "sections" / f"{sid}.html"
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def problems(self):
        note = pa.assemble(self.run, self.tmp / "out")
        return pc.check_preview(self.m, note)

    def codes(self):
        return {(p.code, p.where) for p in self.problems()}

    def test_fixture_passes(self):
        self.assertEqual(self.problems(), [])

    def test_missing_required_term(self):
        self.patch("s1", "이형접합자의 표현형", "잡종의 표현형")
        self.assertIn(("missing-term", "s1-incomplete"), self.codes())

    def test_slide_tag(self):
        self.patch("s1", "4장 p2–p3", "4장 p2")
        self.assertIn(("slide-tag", "s1-dihybrid"), self.codes())

    def test_slide_tag_exact_match(self):
        self.patch("s1", "4장 p2–p3", "4장 p2–p31")
        self.assertIn(("slide-tag", "s1-dihybrid"), self.codes())

    def test_supp_label(self):
        self.patch("s1", "교과서 보충", "보충")
        self.assertIn(("missing-supp", "s1-incomplete"), self.codes())

    def test_stt_layer(self):
        self.patch("s1", '<div class="layer listen">',
                   '<div class="layer prof"><span class="layer-title">교수님 말씀</span><p>가</p></div><div class="layer listen">')
        self.assertIn(("stt-layer", "s1-dihybrid"), self.codes())

    def test_eli5_sentences(self):
        self.patch("s1", LEAD, LEAD + " 두 번째 문장이에요. 세 번째 문장이에요.")
        self.assertIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_figcaption_not_counted_as_sentence(self):
        self.patch("s1", LEAD, LEAD + " 두 번째 문장이에요.")
        self.assertNotIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_eli5_sentences_without_periods(self):
        self.patch("s1", f'<p class="lead">{LEAD}</p>', '<p class="lead">첫 문장이에요</p><p>둘째 문장이에요</p><p>셋째예요</p>')
        self.assertIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_inline_markup_does_not_split_sentence(self):
        self.patch("s1", LEAD, "비율은 9:<b>3</b>이에요. 둘째 문장이에요.")
        self.assertNotIn(("eli5-long", "s1-dihybrid"), self.codes())

    def test_listen_predicting_professor(self):
        self.patch("s1", LISTEN, "독립의 법칙을 강조하실 거예요.")
        self.assertIn(("listen-predicts", "s1-dihybrid"), self.codes())

    def test_listen_items(self):
        self.patch("s1", f"{LISTEN}</li>", f"{LISTEN}</li><li>나</li><li>다</li>")
        self.assertIn(("listen-long", "s1-dihybrid"), self.codes())

    def test_topic_too_long(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", "나눠 담는 과정이에요.</p><p>" + "가" * 700 + "</p>")
        self.assertIn(("topic-long", "s0-meiosis"), self.codes())

    def test_math_not_counted(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", "나눠 담는 과정이에요.</p><p>$$" + "x_n + " * 300 + "x$$</p>")
        self.assertNotIn(("topic-long", "s0-meiosis"), self.codes())

    def test_summary_panel_not_counted(self):
        self.patch("s0", '<p class="sum-lead">감수분열은 상동염색체를 나눠요.</p>', '<p class="sum-lead">' + "가" * 700 + "</p>")
        self.assertNotIn(("topic-long", "s0-meiosis"), self.codes())

    def test_exam_badge_missing(self):
        self.patch("s1", BADGE, "")
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_badge_without_exam_terms(self):
        self.m["sections"][1]["topics"][0]["exam_terms"] = []
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_badge_outside_listen_ignored_but_required_inside(self):
        self.patch("s1", BADGE, "")
        self.patch("s1", '<p class="lead">', '<p class="lead"><span class="badge exam">기출</span> ')
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_exam_term_must_appear_in_listen(self):
        self.patch("s1", LISTEN, "이 법칙이 나오면 정의를 그대로 받아 적어 두세요.")
        self.assertIn(("exam-mark", "s1-dihybrid"), self.codes())

    def test_figure_ref_needs_svg(self):
        self.patch("s1", FIG_SVG, "")
        self.assertIn(("figure", "s1-dihybrid"), self.codes())

    def test_figure_ref_on_topic_without_figure(self):
        self.m["sections"][1]["topics"][1]["figure_ref"] = "그림 4.5"
        self.assertIn(("figure", "s1-incomplete"), self.codes())

    def test_at_most_one_figure(self):
        self.patch("s1", "</figcaption></figure>",
                   '</figcaption></figure><figure class="figure"><svg id="fig-extra" viewBox="0 0 160 40" role="img" aria-label="추가"></svg></figure>')
        self.assertIn(("figure", "s1-dihybrid"), self.codes())

    def test_figure_source_in_caption(self):
        self.patch("s1", FIG_SOURCE, "")
        self.assertIn(("figure-source", "s1-dihybrid"), self.codes())

    def test_textbook_image_rejected(self):
        self.patch("s0", "나눠 담는 과정이에요.</p>", '나눠 담는 과정이에요.</p><img src="fig.png" alt="교과서 그림">')
        self.assertIn(("textbook-image", "예습노트_0101_Mini_Preview.html"), self.codes())

    def test_helpers(self):
        self.assertEqual(pc.visible_chars("가 나 $x^2$ $$y$$ 다"), 3)
        self.assertEqual(pc.sentences(" 하나예요. 둘이에요? 셋 "), 3)
        self.assertEqual(pc.sentences("값은 0.5예요."), 1)

    def test_badge_text_not_counted(self):
        stats = pc.topic_stats(
            '<article class="topic" id="t"><div class="layer listen"><ul><li><span class="badge exam">기출</span>가나</li></ul></div></article>')
        self.assertEqual(pc.visible_chars(stats["t"].text), 2)
        self.assertEqual(stats["t"].exam_badges, 1)

    def test_cli_missing_note(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pc.main(["--manifest", str(self.run / "manifest.json"), "--note", str(self.tmp / "none.html")])
        self.assertEqual(code, 1)
        self.assertIn("none.html", out.getvalue())

    def test_cli(self):
        note = pa.assemble(self.run, self.tmp / "out")
        with redirect_stdout(io.StringIO()):
            code = pc.main(["--manifest", str(self.run / "manifest.json"), "--note", str(note)])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_check.py"`
Expected: FAIL — `No module named 'preview_check'`

- [ ] **Step 3: 구현**

`scripts/preview_check.py`:
```python
#!/usr/bin/env python3
"""
생명과학 예습노트 HTML 검사기 (표준 라이브러리만 사용).

- 공통·계약 검사는 bio-review-pack의 check_common/check_note를 그대로 쓴다
  (예고 금지어는 없고, 보충 배지는 이 파일에서 "교과서 보충"으로 따로 검사한다).
- 예습 전용: 쪽 태그, 교과서 보충 배지, STT 레이어 금지, 분량(600자·eli5 2문장·listen 2항목), 기출 배지.
- 분량은 레이어 안 글자만 센다. 공백, TeX($…$, $$…$$), 그림(svg·figure), 레이어 제목, 배지, 태그, 요약 패널은 뺀다.
- 문장은 블록(p, li, br …) 경계와 "." "?" "!" 뒤 공백에서 나눈다. 인라인 태그(b, a, span)는 문장을 나누지 않는다.
- 쪽 태그는 .tag.slide 글자가 manifest slides와 정확히 같아야 한다("4장 p3"이 "4장 p31"에 통과하지 않게).
- 들을 때 포인트는 교수님 발언을 예측하지 않는다("~하실 거예요" 같은 문장은 listen-predicts).
- 기출 배지(<span class="badge exam">기출</span>)는 exam_terms가 있는 토픽의 들을 때 포인트에만, 그 용어와 함께 쓴다.
- 그림: 쉽게 말하면 레이어의 SVG는 1개까지. figure_ref가 있는 토픽은 SVG 1개와, figcaption에 figure_ref·"다시 그렸어요"(출처)가 필요하다.
  교과서 그림을 잘라 넣은 <img>는 어디에도 쓰지 않는다(textbook-image).
CLI: preview_check.py --manifest RUN/manifest.json --note NOTE.html
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401
from check_html import VOID_TAGS, Problem, check_common, check_file, check_note, parse_html  # noqa: E402
import preview_manifest as pm  # noqa: E402

SUPP_LABEL = "교과서 보충"
EXAM_LABEL = "기출"
FIG_SOURCE = "다시 그렸어요"
MAX_FIGURES = 1
STT_LAYERS = {"prof", "warn"}
MAX_CHARS = 600
MAX_ELI5_SENTENCES = 2
MAX_LISTEN_ITEMS = 2
LAYER_KINDS = ("eli5", "formal", "listen", "supp")
SKIP_TAGS = {"svg", "figure", "script", "style"}
SKIP_CLASSES = {"layer-title", "badge", "sum", "tags"}
BLOCK_TAGS = {"p", "div", "li", "ul", "ol", "br", "dl", "dt", "dd", "table", "tr", "td", "th", "blockquote", "h3", "h4"}
MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$]*\$", re.S)
# 교수님 발언 예측: "강조하실 거예요", "짚으실 거예요", "나올 거예요", "물어보실 수 있어요"
PREDICT_RE = re.compile(r"(?:실|주실|으실)\s*(?:거예요|겁니다|수\s*있어요)|나올\s*거예요")


@dataclass
class TopicStats:
    text: str = ""
    eli5: str = ""
    listen_items: int = 0
    listen: str = ""
    exam_badges: int = 0
    eli5_svgs: int = 0
    captions: str = ""
    slide_tags: list[str] = field(default_factory=list)


class _StatsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stats: dict[str, TopicStats] = {}
        # (tag, topic_id, layer_kind, skip, in_slide_tag)
        self.stack: list[tuple[str, str | None, str | None, bool, bool]] = []

    def _top(self) -> tuple[str | None, str | None, bool, bool]:
        return self.stack[-1][1:] if self.stack else (None, None, False, False)

    def _block_break(self, tag: str) -> None:
        topic, layer, skip, _ = self._top()
        if tag in BLOCK_TAGS and topic and layer == "eli5" and not skip:
            self.stats[topic].eli5 += "\n"  # 블록 경계 = 문장 경계(마침표가 없어도)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        cls = set(a.get("class", "").split())
        topic, layer, skip, in_slide = self._top()
        if tag == "article" and "topic" in cls and a.get("id"):
            topic, layer = a["id"], None
            self.stats[topic] = TopicStats()
        if topic and tag == "div" and "layer" in cls:
            layer = next((k for k in LAYER_KINDS if k in cls), "other")
        if topic and {"tag", "slide"} <= cls:
            in_slide = True
            self.stats[topic].slide_tags.append("")
        if topic and layer == "listen" and {"badge", "exam"} <= cls:
            self.stats[topic].exam_badges += 1
        if topic and layer == "eli5" and tag == "svg":
            self.stats[topic].eli5_svgs += 1
        skip = skip or tag in SKIP_TAGS or bool(cls & SKIP_CLASSES)
        if topic and layer == "listen" and tag == "li" and not skip:
            self.stats[topic].listen_items += 1
        if tag not in VOID_TAGS:
            self.stack.append((tag, topic, layer, skip, in_slide))
        self._block_break(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        self._block_break(tag)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        topic, layer, skip, in_slide = self._top()
        if topic and in_slide:
            self.stats[topic].slide_tags[-1] += data
        if topic and layer == "eli5" and any(e[0] == "figcaption" for e in self.stack):
            self.stats[topic].captions += data  # figure 안이라 본문 글자 수에서는 빠진다
        if topic and layer and not skip:
            st = self.stats[topic]
            st.text += data
            if layer == "eli5":
                st.eli5 += data
            if layer == "listen":
                st.listen += data


def topic_stats(source: str) -> dict[str, TopicStats]:
    parser = _StatsParser()
    parser.feed(source)
    parser.close()
    return parser.stats


def _strip_math(text: str, repl: str = "") -> str:
    return MATH_RE.sub(repl, text.replace("\\$", ""))  # TeX 안의 \$는 구분자가 아니다


def visible_chars(text: str) -> int:
    return len(re.sub(r"\s", "", _strip_math(text)))


def sentences(text: str) -> int:
    """블록 경계(줄바꿈)와 "." "?" "!" 뒤 공백에서 나눈 문장 수."""
    t = _strip_math(text, "X")
    return sum(len([p for p in re.split(r"(?<=[.?!])\s+", line.strip()) if p.strip()]) for line in t.split("\n"))


def contract_view(m: dict) -> dict:
    """복습 check_note에 넘길 사본: 예고 금지어 없음, 보충 배지는 여기서 따로 검사."""
    v = copy.deepcopy(m)
    for sec in v["sections"]:
        for t in sec["topics"]:
            t["supp"] = False
    v["preview_topic"] = v["sections"][-1]["topics"][-1]["id"]
    v["forbidden_outside_preview"] = []
    return v


def _exam_problems(t: dict, st: TopicStats) -> list[Problem]:
    exam = t.get("exam_terms", [])
    out: list[Problem] = []
    if exam and not st.exam_badges:
        out.append(Problem("exam-mark", t["id"], f"들을 때 포인트에 '{EXAM_LABEL}' 배지(<span class=\"badge exam\">) 필요"))
    if not exam and st.exam_badges:
        out.append(Problem("exam-mark", t["id"], "manifest exam_terms가 없는데 기출 배지가 있음"))
    out += [Problem("exam-mark", t["id"], f"들을 때 포인트에 기출 용어 '{term}' 없음") for term in exam if term not in st.listen]
    return out


def _figure_problems(t: dict, st: TopicStats) -> list[Problem]:
    ref = t.get("figure_ref")
    out: list[Problem] = []
    if st.eli5_svgs > MAX_FIGURES:
        out.append(Problem("figure", t["id"], f"쉽게 말하면 그림 {st.eli5_svgs}개 > {MAX_FIGURES}개"))
    if ref and not st.eli5_svgs:
        out.append(Problem("figure", t["id"], f"figure_ref '{ref}'인데 쉽게 말하면 레이어에 SVG 그림이 없음"))
    if ref and st.eli5_svgs and (ref not in st.captions or FIG_SOURCE not in st.captions):
        out.append(Problem("figure-source", t["id"], f"figcaption에 '{ref}'와 '{FIG_SOURCE}' 필요(예: \"교과서 {ref}을 단순하게 다시 그렸어요\")"))
    return out


def check_preview(m: dict, note_path: Path | str) -> list[Problem]:
    path = Path(note_path)
    source = path.read_text(encoding="utf-8")
    doc = parse_html(source)
    out = check_common(doc, source, path) + check_note(doc, contract_view(m))
    out += [Problem("textbook-image", path.name, f"<img src=\"{s}\">: 교과서 그림은 잘라 넣지 말고 SVG로 다시 그린다")
            for s in doc.img_srcs]
    stats = topic_stats(source)
    for sec in m["sections"]:
        for t in sec["topics"]:
            con = doc.containers.get(t["id"])
            if con is None or not t["layers"]:
                continue
            st = stats.get(t["id"], TopicStats())
            if t["slides"] and t["slides"] not in (s.strip() for s in st.slide_tags):
                out.append(Problem("slide-tag", t["id"], f"'{t['slides']}' 태그 없음 (있는 태그: {st.slide_tags})"))
            if t["supp"] and ("supp" not in con.child_classes or SUPP_LABEL not in con.text):
                out.append(Problem("missing-supp", t["id"], f"layer supp + '{SUPP_LABEL}' 필요"))
            stt = STT_LAYERS & con.child_classes
            if stt:
                out.append(Problem("stt-layer", t["id"], ", ".join(sorted(stt))))
            n = visible_chars(st.text)
            if n > MAX_CHARS:
                out.append(Problem("topic-long", t["id"], f"본문 {n}자 > {MAX_CHARS}자"))
            k = sentences(st.eli5)
            if k > MAX_ELI5_SENTENCES:
                out.append(Problem("eli5-long", t["id"], f"쉽게 말하면 {k}문장 > {MAX_ELI5_SENTENCES}문장"))
            if PREDICT_RE.search(_strip_math(st.listen)):
                out.append(Problem("listen-predicts", t["id"], "교수님 발언을 예측하는 문장(\"~하실 거예요\") 대신 \"~가 나오면 ~해 보세요\"로"))
            if st.listen_items > MAX_LISTEN_ITEMS:
                out.append(Problem("listen-long", t["id"], f"들을 때 포인트 {st.listen_items}개 > {MAX_LISTEN_ITEMS}개"))
            out += _exam_problems(t, st)
            out += _figure_problems(t, st)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--manifest")
    ap.add_argument("--note")
    args = ap.parse_args(argv)
    problems: list[Problem] = []
    if args.manifest:
        if not args.note:
            ap.error("--manifest에는 --note가 필요")
        if not Path(args.note).is_file():
            print(f"노트 파일 없음: {args.note}")
            return 1
        try:
            problems += check_preview(pm.load(args.manifest), args.note)
        except pm.ManifestError as e:
            print(f"manifest 오류: {e}")
            return 1
    for name in args.files:
        problems += check_file(name)
    for p in problems:
        print(p)
    print("OK" if not problems else f"FAIL ({len(problems)})")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_check.py" -v`
Expected: 28 tests OK.
`test_fixture_passes`가 실패하면 출력된 Problem을 본다. 흔한 원인은 두 가지다. (a) 복습 `check_note`의 `missing-sum`: 개념 토픽마다 `<div class="sum" hidden>`이 있어야 한다. (b) `missing-term`: 픽스처 글자와 manifest `required_terms`가 다르다. 검사기를 느슨하게 고치지 말고 픽스처 쪽을 고친다.

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-preview-note/scripts/preview_check.py .agents/skills/bio-preview-note/tests/test_preview_check.py
git commit -m "feat(skills): check bio preview note length, page tags, exam badges and figures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: MD 변환

**Files:**
- Create: `.agents/skills/bio-preview-note/scripts/preview_md.py`
- Test: `.agents/skills/bio-preview-note/tests/test_preview_md.py`

**Interfaces:**
- Consumes: `bio-review-pack/scripts/html2md.py`의 `nfc(s)`, `Ctx(link_map, fig_dir_abs, fig_dir_name, prefix="", registry=None)`(`.registry`는 내보낸 그림 이름 집합), `convert(path, out_path, ctx, intro: list[str])`, `check_md(html_path, md_path) -> list[str]`. Task 3 `preview_assemble.assemble`.
- Produces: `preview_md.convert_note(note_path) -> tuple[Path, int]`(MD 경로, 그림 수; 파일명이 `예습노트_<MMDD>_<slug>.html`이 아니면 `ValueError`), `main(argv) -> int`.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_preview_md.py`:
```python
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

from _preview_util import MINI_RUN

import preview_assemble as pa
import preview_md as pmd
import html2md  # preview_md가 복습 scripts 경로를 넣은 뒤


class TestPreviewMd(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.note = pa.assemble(MINI_RUN, self.tmp / "out")

    def tearDown(self):
        self._tmp.cleanup()

    def test_convert_and_check(self):
        md, figs = pmd.convert_note(self.note)
        self.assertEqual(md.name, "예습노트_0101_Mini_Preview.md")
        self.assertEqual(figs, 1)
        self.assertTrue((self.tmp / "out" / "figures_0101" / "fig-dihybrid.svg").exists())
        self.assertEqual(html2md.check_md(str(self.note), str(md)), [])
        text = md.read_text(encoding="utf-8")
        self.assertIn("**들을 때 포인트**", text)
        self.assertIn("**교과서 보충**", text)
        self.assertIn("**기출**", text)

    def test_orphan_svgs_removed(self):
        figs = self.tmp / "out" / "figures_0101"
        figs.mkdir()
        (figs / "old.svg").write_text("<svg/>", encoding="utf-8")
        pmd.convert_note(self.note)
        self.assertFalse((figs / "old.svg").exists())

    def test_bad_name(self):
        other = self.note.with_name("정리노트_0101_X.html")
        other.write_text(self.note.read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaises(ValueError):
            pmd.convert_note(other)

    def test_cli_check(self):
        with redirect_stdout(io.StringIO()):
            code = pmd.main([str(self.note), "--check"])
        self.assertEqual(code, 0)

    def test_cli_missing_note(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = pmd.main([str(self.tmp / "예습노트_0101_None.html")])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_md.py"`
Expected: FAIL — `No module named 'preview_md'`

- [ ] **Step 3: 구현**

`scripts/preview_md.py`:
```python
#!/usr/bin/env python3
"""
생명과학 예습노트 HTML → GitHub 마크다운 (표준 라이브러리만 사용).

bio-review-pack의 html2md 변환·검사 함수를 그대로 쓴다. 그림은 같은 폴더의 figures_<MMDD>/에 SVG로 내보낸다.
CLI:
  preview_md.py 예습노트_<MMDD>_<slug>.html            # 같은 폴더에 .md + figures_<MMDD>/
  preview_md.py 예습노트_<MMDD>_<slug>.html --check    # 변환 후 누락 검사(수식·앵커·그림·링크)
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402,F401
import html2md  # noqa: E402  (복습 스킬 공용)

NAME_RE = re.compile(r"예습노트_(\d{4})_([A-Za-z0-9_]+)\.html")


def convert_note(note_path: Path | str) -> tuple[Path, int]:
    src = Path(note_path).resolve()
    name = html2md.nfc(src.name)
    m = NAME_RE.fullmatch(name)
    if not m:
        raise ValueError(f"파일명 규칙 위반: {name}")
    fig_name = f"figures_{m.group(1)}"
    fig_abs = src.parent / fig_name
    fig_abs.mkdir(exist_ok=True)
    for entry in os.listdir(fig_abs):  # 다시 변환할 때 이전 실행의 고아 SVG를 남기지 않는다(.svg만, 이 폴더만)
        old = fig_abs / entry
        if entry.lower().endswith(".svg") and old.is_file() and not old.is_symlink():
            old.unlink()
    md_name = name[:-5] + ".md"
    ctx = html2md.Ctx([(name, md_name)], str(fig_abs), fig_name, prefix="note", registry=set())
    intro = [f"> `{name}`를 마크다운으로 옮겼어요. 그림은 `{fig_name}/` 폴더의 SVG예요. "
             "수식은 `$…$` / `$$…$$`라서 GitHub, Obsidian, Typora에서 보여요."]
    out = src.parent / md_name
    html2md.convert(str(src), str(out), ctx, intro)
    return out, len(ctx.registry)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("note")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if not Path(args.note).is_file():
        print(f"노트 파일 없음: {args.note}", file=sys.stderr)
        return 1
    try:
        out, figs = convert_note(args.note)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(out)
    print(f"figures: {figs}")
    if not args.check:
        return 0
    problems = html2md.check_md(str(Path(args.note).resolve()), str(out))
    for p in problems:
        print(f"{out.name}: {p}")
    print("OK" if not problems else f"FAIL ({len(problems)})")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_md.py" -v`
Expected: 5 tests OK. `figs`가 0이면 `html2md.export_svg`가 `ctx.registry`에 이름을 넣는지 확인한다(`grep -n "registry" .agents/skills/bio-review-pack/scripts/html2md.py`). 넣지 않으면 반환값을 `len(ctx.figs)`로 바꾼다.

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-preview-note/scripts/preview_md.py .agents/skills/bio-preview-note/tests/test_preview_md.py
git commit -m "feat(skills): convert bio preview notes to markdown

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: 수업일·시작 쪽 고르기와 백업 (`preview_files.py`)

**Files:**
- Create: `.agents/skills/bio-preview-note/scripts/preview_files.py`
- Test: `.agents/skills/bio-preview-note/tests/test_preview_files.py`

**Interfaces:**
- Consumes: 없음(표준 라이브러리만). 저장소 파일 규칙: `STT/<MMDD>[ _]생명.md`, `복습노트/<폴더>/정리노트_<MMDD 또는 MMDD-MMDD>_<slug>.html`(`<span class="tag slide">4장 p1–p2</span>`), `강의노트/<N>장 <제목>.pdf`.
- Produces: `PickError`, `normalize_date(arg) -> "MMDD"`, `stt_dates(repo) -> set[str]`, `next_class_date(today: datetime.date, done: set[str]) -> str`, `latest_review_note(repo) -> tuple[str, Path]`(끝 날짜, 경로), `last_page(note: Path) -> tuple[int, int]`, `chapter_pdf(repo, chapter: int) -> Path`, `has_note(repo, date) -> bool`, `pick(repo, date=None, today=None) -> tuple[str, int, int, Path]`, `backup(repo, date, run) -> Path | None`, `main(argv) -> int`. CLI `pick` 출력: `MMDD<TAB>장<TAB>시작쪽<TAB>PDF 절대 경로`.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_preview_files.py`:
```python
from contextlib import redirect_stderr, redirect_stdout
import datetime as dt
import io
from pathlib import Path
import tempfile
import unicodedata
import unittest

import _preview_util  # noqa: F401  (scripts 경로)
import preview_files as pf

TUE_0922 = dt.date(2026, 9, 22)
SAT_0926 = dt.date(2026, 9, 26)


def tags(*texts):
    return "".join(f'<span class="tag slide">{t}</span>' for t in texts)


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class RepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        for name in ("3장 세포분열.pdf", "4장 유전.pdf", "12장 신경계와 감각계.pdf", "notes.txt"):
            write(self.repo / "강의노트" / name, "%PDF")
        write(self.repo / "STT" / "0917 생명.md")
        write(self.repo / "STT" / "0922 생명.md")
        write(self.repo / "복습노트" / "0917" / "정리노트_0917_Cell_Division.html", tags("3장 p1", "3장 p2–p5"))
        write(self.repo / "복습노트" / "0922" / "정리노트_0922_Heredity.html", tags("3장 p5", "4장 p1–p2", "4장 p2"))
        write(self.repo / "복습노트" / "0922" / "복습문제_0922_Heredity.html", tags("9장 p9"))

    def tearDown(self):
        self._tmp.cleanup()


class TestPick(RepoCase):
    def test_start_from_latest_note(self):
        date, ch, page, pdf = pf.pick(self.repo, "0929")
        self.assertEqual((date, ch, page, unicodedata.normalize("NFC", pdf.name)), ("0929", 4, 2, "4장 유전.pdf"))

    def test_range_note_uses_end_date(self):
        write(self.repo / "복습노트" / "0923-0924" / "정리노트_0923-0924_More.html", tags("4장 p5"))
        self.assertEqual(pf.latest_review_note(self.repo)[0], "0924")
        self.assertEqual(pf.pick(self.repo, "0929")[2], 5)

    def test_range_tag_uses_end_page(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_X.html", tags("4장 p3–p6"))
        self.assertEqual(pf.pick(self.repo, "0929")[1:3], (4, 6))

    def test_two_digit_chapter(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_X.html", tags("12장 p1"))
        self.assertEqual(unicodedata.normalize("NFC", pf.pick(self.repo, "0929")[3].name), "12장 신경계와 감각계.pdf")

    def test_default_date_skips_class_with_stt(self):
        self.assertEqual(pf.next_class_date(TUE_0922, {"0922"}), "0924")
        self.assertEqual(pf.pick(self.repo, today=TUE_0922)[0], "0924")

    def test_default_date_from_weekend(self):
        self.assertEqual(pf.next_class_date(SAT_0926, set()), "0929")

    def test_default_existing_note_stops(self):
        write(self.repo / "예습노트" / "0929" / "예습노트_0929_X.html", "<html></html>")
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, today=SAT_0926)
        self.assertIn("이미", str(cm.exception))
        self.assertEqual(pf.pick(self.repo, "0929")[0], "0929")  # 날짜를 주면 다시 만들 수 있다

    def test_date_with_stt_stops(self):
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0922")
        self.assertIn("bio-review-pack", str(cm.exception))

    def test_bad_date(self):
        for bad in ("929", "1340", "0230x", "abcd", "0001"):
            with self.subTest(date=bad):
                with self.assertRaises(pf.PickError):
                    pf.pick(self.repo, bad)

    def test_no_review_notes(self):
        for p in (self.repo / "복습노트").rglob("*.html"):
            p.unlink()
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("직접", str(cm.exception))

    def test_note_without_tags(self):
        write(self.repo / "복습노트" / "0924" / "정리노트_0924_Old.html", "<p>태그 없음</p>")
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("쪽 태그", str(cm.exception))
        self.assertIn("정리노트_0924_Old.html", str(cm.exception))

    def test_missing_chapter_pdf(self):
        (self.repo / "강의노트" / "4장 유전.pdf").unlink()
        with self.assertRaises(pf.PickError) as cm:
            pf.pick(self.repo, "0929")
        self.assertIn("ajou-bb", str(cm.exception))

    def test_stt_underscore_name(self):
        write(self.repo / "STT" / "0929_생명.md")
        self.assertIn("0929", pf.stt_dates(self.repo))

    def test_nfd_names(self):
        repo = Path(self._tmp.name) / "nfd"
        write(repo / unicodedata.normalize("NFD", "강의노트") / unicodedata.normalize("NFD", "4장 유전.pdf"), "%PDF")
        write(repo / unicodedata.normalize("NFD", "복습노트") / "0922" / unicodedata.normalize("NFD", "정리노트_0922_X.html"), tags("4장 p2"))
        write(repo / unicodedata.normalize("NFD", "STT") / unicodedata.normalize("NFD", "0922 생명.md"))
        self.assertEqual(pf.pick(repo, today=TUE_0922)[:3], ("0924", 4, 2))

    def test_cli_pick(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = pf.main(["pick", "--repo", str(self.repo), "--date", "0929"])
        self.assertEqual(code, 0)
        date, ch, page, pdf = out.getvalue().strip().split("\t")
        self.assertEqual((date, ch, page, unicodedata.normalize("NFC", Path(pdf).name)), ("0929", "4", "2", "4장 유전.pdf"))

    def test_cli_error_exit_code(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = pf.main(["pick", "--repo", str(self.repo), "--date", "0922"])
        self.assertEqual(code, 1)
        self.assertIn("0922", err.getvalue())


class TestBackup(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        self.run = Path(self._tmp.name) / "run"
        self.run.mkdir(parents=True)
        self.dir = self.repo / "예습노트" / "0929"
        self.dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_nothing_to_back_up(self):
        self.assertIsNone(pf.backup(self.repo, "0929", self.run))
        self.assertIsNone(pf.backup(self.repo, "1001", self.run))  # 폴더 자체가 없음

    def test_copies_only_this_date(self):
        (self.dir / "예습노트_0929_A.html").write_text("a", encoding="utf-8")
        (self.dir / "예습노트_0929_A.md").write_text("a", encoding="utf-8")
        (self.dir / "figures_0929").mkdir()
        (self.dir / "figures_0929" / "f.svg").write_text("<svg/>", encoding="utf-8")
        (self.dir / "memo.txt").write_text("x", encoding="utf-8")
        dst = pf.backup(self.repo, "0929", self.run)
        self.assertTrue(dst.name.startswith("previous-"))
        self.assertEqual(sorted(p.name for p in dst.iterdir()), ["figures_0929", "예습노트_0929_A.html", "예습노트_0929_A.md"])
        self.assertTrue((dst / "figures_0929" / "f.svg").exists())

    def test_each_backup_new_folder(self):
        (self.dir / "예습노트_0929_A.html").write_text("a", encoding="utf-8")
        a, b = pf.backup(self.repo, "0929", self.run), pf.backup(self.repo, "0929", self.run)
        self.assertNotEqual(a, b)

    def test_bad_args(self):
        with self.assertRaises(pf.PickError):
            pf.backup(self.repo, "929", self.run)
        with self.assertRaises(pf.PickError):
            pf.backup(self.repo, "0929", self.run / "missing")

    def test_nfd_notes_dir_backed_up(self):
        nfd = self.repo.parent / "repo2" / unicodedata.normalize("NFD", "예습노트") / "0929"
        nfd.mkdir(parents=True)
        (nfd / unicodedata.normalize("NFD", "예습노트_0929_A.html")).write_text("a", encoding="utf-8")
        dst = pf.backup(self.repo.parent / "repo2", "0929", self.run)
        self.assertEqual([unicodedata.normalize("NFC", p.name) for p in dst.iterdir()], ["예습노트_0929_A.html"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_files.py"`
Expected: FAIL — `No module named 'preview_files'`

- [ ] **Step 3: 구현**

`scripts/preview_files.py`:
```python
#!/usr/bin/env python3
"""
예습노트 대상 수업일·시작 쪽 고르기와 기존 예습노트 백업 (표준 라이브러리만 사용).

- 대상 수업일: --date MMDD. 없으면 오늘(포함) 이후 STT가 없는 가장 가까운 화·목(강의계획서 "화D 목C").
- 대상 날짜의 STT가 이미 있으면(끝난 수업) 멈추고 bio-review-pack을 안내한다.
- 날짜 없이 골랐는데 그 날짜 예습노트가 이미 있으면 멈춘다(날짜를 주면 다시 만든다).
- 시작 쪽: 가장 최근 정리노트(범위의 끝 날짜 기준) HTML의 .tag.slide 중 가장 큰 (장, 쪽). 그 쪽을 포함한다.
- macOS NFD 폴더·파일명도 NFC로 비교해 찾는다.
CLI:
  preview_files.py pick --repo REPO [--date 0929]   → "0929<TAB>4<TAB>2<TAB>강의노트 PDF 절대 경로"
  preview_files.py backup --repo REPO --date 0929 --run RUN
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import unicodedata

LECTURES_DIR = "강의노트"
NOTES_DIR = "예습노트"
REVIEW_DIR = "복습노트"
STT_DIR = "STT"
CLASS_WEEKDAYS = {1, 3}  # 화(1)·목(3)
DATE_RE = re.compile(r"(\d{2})(\d{2})")
STT_RE = re.compile(r"(\d{4})[ _]생명\.md")
REVIEW_NOTE_RE = re.compile(r"정리노트_(?:\d{4}-)?(\d{4})_.+\.html")
TAG_RE = re.compile(r'class="tag slide">\s*(\d+)장 p(\d+)(?:–p?(\d+))?\s*<')
CHAPTER_PDF_RE = re.compile(r"(\d+)장 .+\.pdf")


class PickError(RuntimeError):
    pass


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def entries(d: Path | None) -> dict[str, Path]:
    """d 안의 항목을 NFC 이름 → 실제 경로로(NFD 이름 포함). d가 폴더가 아니면 빈 dict."""
    if d is None or not d.is_dir():
        return {}
    return {nfc(n): d / n for n in os.listdir(d)}


def child(parent: Path | None, name: str) -> Path | None:
    return entries(parent).get(name)


def normalize_date(arg: str) -> str:
    m = DATE_RE.fullmatch(arg.strip())
    if not m or not (1 <= int(m.group(1)) <= 12 and 1 <= int(m.group(2)) <= 31):
        raise PickError(f"날짜 형식이 아님: {arg!r} (예: 0929)")
    return m.group(0)


def stt_dates(repo) -> set[str]:
    return {m.group(1) for n in entries(child(Path(repo), STT_DIR)) if (m := STT_RE.fullmatch(n))}


def next_class_date(today: dt.date, done: set[str]) -> str:
    d = today
    for _ in range(366):
        mmdd = d.strftime("%m%d")
        if d.weekday() in CLASS_WEEKDAYS and mmdd not in done:
            return mmdd
        d += dt.timedelta(days=1)
    raise PickError("다음 수업일을 찾지 못했어요. --date로 날짜를 주세요.")


def latest_review_note(repo) -> tuple[str, Path]:
    best: tuple[str, Path] | None = None
    for folder in entries(child(Path(repo), REVIEW_DIR)).values():
        for name, path in entries(folder).items():
            m = REVIEW_NOTE_RE.fullmatch(name)
            if m and (best is None or m.group(1) > best[0]):
                best = (m.group(1), path)
    if best is None:
        raise PickError(f"{REVIEW_DIR}/에 정리노트가 없어요. 강의계획서 진도로 장과 쪽을 직접 고르세요.")
    return best


def last_page(note: Path) -> tuple[int, int]:
    found = [(int(ch), int(end or start)) for ch, start, end in TAG_RE.findall(note.read_text(encoding="utf-8"))]
    if not found:
        raise PickError(f"정리노트에 쪽 태그(예: '4장 p2')가 없어요: {nfc(note.name)}. 장과 쪽을 직접 고르세요.")
    return max(found)


def chapter_pdf(repo, chapter: int) -> Path:
    for name, path in entries(child(Path(repo), LECTURES_DIR)).items():
        m = CHAPTER_PDF_RE.fullmatch(name)
        if m and int(m.group(1)) == chapter:
            return path
    raise PickError(f"{LECTURES_DIR}/에 {chapter}장 PDF가 없어요. 새 강의노트가 올라왔는지 ajou-bb로 확인하세요.")


def has_note(repo, date: str) -> bool:
    notes = entries(child(child(Path(repo), NOTES_DIR), date))
    return any(n.startswith(f"예습노트_{date}_") and n.endswith(".html") for n in notes)


def pick(repo, date: str | None = None, today: dt.date | None = None) -> tuple[str, int, int, Path]:
    repo = Path(repo)
    done = stt_dates(repo)
    if date is not None:
        date = normalize_date(date)
    else:
        date = next_class_date(today or dt.date.today(), done)
        if has_note(repo, date):
            raise PickError(f"{date} 수업의 예습노트가 이미 있어요. 다시 만들려면 날짜를 인자로 주세요.")
    if date in done:
        raise PickError(f"{date} 수업은 이미 STT가 있어요(수업이 끝났어요). 복습은 /bio-review-pack {date}을 쓰세요.")
    _, note = latest_review_note(repo)
    chapter, page = last_page(note)
    return date, chapter, page, chapter_pdf(repo, chapter)


def _count(p: Path) -> int:
    return sum(len(files) for _, _, files in os.walk(p)) if p.is_dir() else 1


def backup(repo, date: str, run) -> Path | None:
    run = Path(run)
    try:
        date = normalize_date(date)
    except PickError as e:
        raise PickError(f"백업 중단: {e}") from e
    if not run.is_dir():
        raise PickError(f"백업 중단: run 폴더 없음: {run}")
    src = child(child(Path(repo), NOTES_DIR), date)
    hits = sorted((n, p) for n, p in entries(src).items() if n.startswith(f"예습노트_{date}_") or n == f"figures_{date}")
    if not hits:
        return None
    dst = Path(tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run))  # 항상 새 폴더
    for name, path in hits:
        if path.is_dir():
            shutil.copytree(path, dst / name)
        else:
            shutil.copy2(path, dst / name)
    want, got = sum(_count(p) for _, p in hits), _count(dst)
    if got != want:
        raise PickError(f"백업 실패: 파일 {want}개 중 {got}개만 복사됨 → {dst}")
    return dst


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pick")
    p.add_argument("--repo", required=True)
    p.add_argument("--date")
    b = sub.add_parser("backup")
    b.add_argument("--repo", required=True)
    b.add_argument("--date", required=True)
    b.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "pick":
            date, chapter, page, pdf = pick(args.repo, args.date)
            print(f"{date}\t{chapter}\t{page}\t{pdf}")
        else:
            dst = backup(args.repo, args.date, args.run)
            print(f"백업: {dst}" if dst else "백업할 기존 예습노트 없음")
    except PickError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_files.py" -v`
Expected: 21 tests OK.

- [ ] **Step 5: 실제 저장소로 확인 (쓰기 없음)**

Run: `python3 .agents/skills/bio-preview-note/scripts/preview_files.py pick --repo "$PWD" --date 1001`
Expected: `1001	4	2	/Users/…/생명과학/강의노트/4장 유전.pdf` (0922 정리노트의 마지막 태그가 `4장 p2`)

Run: `python3 .agents/skills/bio-preview-note/scripts/preview_files.py pick --repo "$PWD" --date 0922; echo "exit=$?"`
Expected: `0922 수업은 이미 STT가 있어요 … /bio-review-pack 0922…` 와 `exit=1`

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-preview-note/scripts/preview_files.py .agents/skills/bio-preview-note/tests/test_preview_files.py
git commit -m "feat(skills): pick next bio class date and start page for preview notes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: SKILL.md, references, 진입점 심링크

> **구현 중 변경(2026-09-29):** 교과서 PDF가 스캔본이라(텍스트 없음) 1단계 6·7의 글자 검색을 dpi 50 썸네일(`RUN/work/textbook-pages/`)을 눈으로 보는 방식으로 바꿨다. 0929 시험 실행 뒤 content-rules에 "높이 예산"을, 검사기에 `figure-size`(viewBox 폭 600 이하, 세로/가로 0.25 이하)를 더했다. 아래 SKILL.md·references 본문은 저장소의 실제 파일과 같다.

**Files:**
- Create: `.agents/skills/bio-preview-note/SKILL.md`
- Create: `.agents/skills/bio-preview-note/references/content-rules.md`, `manifest-guide.md`, `review-prompt.md`, `browser-check.md`
- Create: `.claude/skills/bio-preview-note` (심링크 → `../../.agents/skills/bio-preview-note`)
- Test: `.agents/skills/bio-preview-note/tests/test_preview_skill_files.py`

**Interfaces:**
- Consumes: Task 2~6의 CLI — `preview_files.py pick|backup`, `preview_manifest.py`, `preview_assemble.py --run --out`, `preview_check.py --manifest --note`, `preview_md.py NOTE --check`. manifest 키(Task 2), 마크업·문제 코드(Task 4).
- Produces: `/bio-preview-note [MMDD] [lite]` 스킬.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_preview_skill_files.py`:
```python
"""SKILL.md 형식과, 본문이 가리키는 파일이 모두 있는지 확인한다."""

import os
import re
import unittest

from _preview_util import REPO, SKILL

SKILL_MD = SKILL / "SKILL.md"


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "bio-preview-note")
        self.assertIn("예습노트", m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 9)
        for rel in sorted(refs):
            with self.subTest(rel=rel):
                self.assertTrue((SKILL / rel).exists(), rel)

    def test_every_reference_is_used(self):
        for path in sorted((SKILL / "references").glob("*.md")):
            with self.subTest(ref=path.name):
                self.assertIn(f"references/{path.name}", self.text)

    def test_steps_present(self):
        for n in range(10):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### {n}\. ")

    def test_claude_entry_symlink(self):
        link = REPO / ".claude" / "skills" / "bio-preview-note"
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), "../../.agents/skills/bio-preview-note")
        self.assertEqual(link.resolve(), SKILL.resolve())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -p "test_preview_skill_files.py"`
Expected: FAIL — `FileNotFoundError: … SKILL.md`

- [ ] **Step 3: 진입점 심링크**

```bash
ln -s ../../.agents/skills/bio-preview-note .claude/skills/bio-preview-note
```

- [ ] **Step 4: `SKILL.md` 작성**

`.agents/skills/bio-preview-note/SKILL.md`:
````markdown
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
- `figure`·`figure-source`는 참고 PNG를 보고 SVG를 그리거나 figcaption 출처를 채우게 한다. `figure-size`는 viewBox를 560×110~140으로 낮추게 한다(content-rules "높이 예산"). `textbook-image`는 `<img>`를 지우고 SVG로 다시 그리게 한다.
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
````

- [ ] **Step 5: `references/manifest-guide.md` 작성**

````markdown
# 예습노트 manifest.json 작성 규칙 (메인 에이전트)

manifest는 이번 예습노트의 계약이다. 작성자, 검사기, 조립기가 모두 이 파일을 기준으로 삼는다.
정본 예시: `tests/fixtures/mini-run/manifest.json`.
작성 후 반드시 `python3 <SKILL>/scripts/preview_manifest.py <RUN>/manifest.json` → `OK`.

## 최상위
| 키 | 값 |
|---|---|
| `course` | `"생명과학"` |
| `range` | 수업 날짜 `"0929"` (`pick` 출력 첫 칸) |
| `chapters` | 범위에 든 장 번호 문자열 목록, 예: `["4"]`, `["4", "5"]` |
| `slug` | 범위 주제의 영어, 밑줄 연결. 복습노트 관례를 따른다(예: `"Heredity"`, `"Heredity_and_DNA_Replication"`) |
| `pdfs` | 저장소 기준 강의노트 경로 목록, 예: `["강의노트/4장 유전.pdf"]` |
| `note_title` | `"<주제> — 수업 전에 보는 예습노트"` |
| `note_subtitle` | `"이영만 교수님 생명과학 · <MMDD> 수업 예습 (강의노트 4장 p2–p5)"` 형식 |
| `footer_note` | HTML 허용. `출처: 이영만 교수님 생명과학 강의노트 N장 · 박상규 외, <i>생명과학 기초와 응용</i> 2판 (2021) N장. 수업 전에 만든 노트라 수업 내용과 다를 수 있어요.` |
| `sections`, `links` | 아래 |

## sections / topics
- 섹션 id는 `s0`, `s1`, … 순서(검사기가 강제). `s0`은 "0. 미리 알아둘 것", 마지막 섹션은 "N. 한눈에 보기"이며 토픽 `s<N>-cheatsheet`, `s<N>-links`를 둔다.
- 가운데 섹션은 **강의노트 순서**대로, 절(`4.1`, `4.2`) 단위로 묶는다. 토픽 id는 `s<n>-<kebab>`(영문 소문자), 섹션 id로 시작.
- 토픽 하나 = 소절 1~2개. `slides`는 `"4장 p3"` 또는 `"4장 p3–p4"`(en dash, 양쪽에 `p`). 요약 섹션 토픽은 `""`. `s0` 토픽은 선수 개념이므로 기본 `""`.
- 토픽은 **장 경계**를 넘지 않는다. `slides`는 한 장 안의 쪽만 쓸 수 있다(`4장 p9–5장 p1`은 검증 실패). 범위가 다음 장으로 넘어가면 장이 바뀌는 곳에서 토픽(가능하면 섹션)을 나눈다.
- `short`는 상단 목차 글자(예: `"2 독립의 법칙"`), `title`은 `"2. 독립의 법칙과 양성잡종"`.
- `layers`
  - 개념 토픽: `["eli5", "formal", "listen"]`. 들을 거리가 없는 짧은 정의 토픽은 `["eli5", "formal"]`.
  - `s0` 토픽: `["eli5", "formal"]`.
  - 요약 섹션 토픽: `[]`.
- `supp`: 강의노트만으로는 이해되지 않아 교과서 설명을 덧붙이는 토픽만 `true`. 요약 토픽은 항상 `false`.
- `required_terms`: 토픽당 2~6개, **강의노트에 나오는** 핵심 용어를 글자 그대로(예: `"불완전우성"`, `"9:3:3:1"`). 빈 문자열 금지. 요약 토픽은 치트시트에 넣을 용어 몇 개 또는 `[]`.
- `figure_ref`(선택): 강의노트나 교과서가 그림으로 설명하는 개념이면 SKILL 1단계 7에서 찾은 그림 이름(예: `"그림 4.3"`, 교과서에 없으면 `"강의노트 4장 p3 그림"`). 이 토픽의 쉽게 말하면 레이어에는 인라인 SVG 1개가 들어가고 figcaption에 이 글자와 "다시 그렸어요"가 들어가야 한다(검사기가 본다). `eli5` 레이어가 있는 토픽에만 쓴다. 참고 PNG는 `RUN/work/textbook-figs/<토픽id>.png`.
- `exam_terms`(선택): SKILL 1단계 5에서 기출 합본이나 웹과제에 나온 `required_terms`만. `listen` 레이어가 있는 토픽에만 쓴다. 나온 것이 없으면 키를 빼거나 `[]`.

## links
- `href`는 작성자가 `<a href="…">`에 **글자 그대로** 넣을 값이다(검사기가 해당 토픽 안의 링크와 정확히 비교하고, 파일이 실제로 있는지도 본다). 출력 폴더가 `예습노트/<MMDD>/`라 저장소 파일은 `../../`로 시작한다.
- 교과서: `{"topic": "s<N>-links", "href": "../../교과서/생명과학_기초와_응용_2판/04장_유전.pdf#page=<쪽>"}` (SKILL 1단계 6의 숫자).
- 선수 개념: `s0` 토픽에 `../../복습노트/<폴더>/정리노트_<range>_<slug>.html#<토픽 id>`.
````

- [ ] **Step 6: `references/content-rules.md` 작성**

````markdown
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
- 자기 검사(끝내기 전): `required_terms`가 문자 그대로 있는지, 쪽 태그가 manifest `slides`와 글자 그대로 같은지(범위는 en dash `–`), 토픽 본문 600자 이하(공백·그림 제외), 쉽게 말하면 2문장 이하이고 전문용어가 없는지, 들을 때 포인트 2항목 이하이고 "~하실 거예요" 같은 예측이 없는지, `exam_terms`가 있는 토픽만 기출 배지가 있고 그 용어가 같은 항목에 있는지, 그림 방향·레이블이 강의노트와 맞는지, `figure_ref` 토픽은 쉽게 말하면 레이어에 SVG 1개가 있고 figcaption에 `figure_ref` 글자와 "다시 그렸어요"가 있는지, 단계 순서·배치·화살표 방향·표지 이름이 참고 PNG와 같은지, 아래 "높이 예산"의 항목별 한도(그림 viewBox 560×140 이하, 첫 줄 한 줄, 그림 토픽의 정의는 `<p><b>` 한 줄 형식)를 지켰는지, 이모지 없음, `layers`가 빈 목록이 아닌 토픽마다 맨 끝에 `<div class="sum" hidden>`.
- 보고: 파일 경로, 토픽별 한 줄, 강의노트에 있었지만 뺀 것과 이유.
---

## 범위
- 강의노트에 있는 내용만 설명한다. 강의노트에 없는 설명(교과서의 예시·배경)은 `supp`가 `true`인 토픽의 보충 레이어에만 쓴다.
- 교수님 말씀이나 수업 중 강조는 아직 모르므로 **추측해서 쓰지 않는다**.

## 토픽 마크업 (이 순서)
```html
<article class="topic" id="…"><h3>…</h3><div class="tags"><span class="tag slide">4장 p3–p4</span></div>
  <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">한 줄 비유(30자 안팎)</p> …그림(figure_ref 토픽은 SVG 1개)… </div>
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
- **한 화면**: 토픽 하나가 720×900 창에서 스크롤 없이 보여야 한다(브라우저 검사). 글자 수보다 **높이**가 먼저 찬다. 아래 "높이 예산"대로 쓴다.
- **쉽게 말하면**: 2문장 이하("."·"?"·"!" 뒤 공백으로 나눈다), 전문용어 없이 일상 비유로. manifest `figure_ref`가 있는 토픽(강의노트나 교과서가 그림으로 설명하는 개념)은 이 레이어에 인라인 SVG 1개를 넣는다. 다른 토픽은 그림 없이 쓴다(넣더라도 1개까지, 검사기가 센다).
- **정확히 말하면**: 강의노트의 정의와 과정을 쓴다. 형식은 내용에 맞춰 하나를 고른다.
  - 용어 정의: `<p><b>불완전우성(incomplete dominance)</b>: 한 줄 뜻</p>`. `<dl>`은 항목마다 두 줄을 차지하므로 그림이 없는 토픽에서 정의가 2개 이하일 때만 쓴다.
  - 과정: `<ol><li>단계</li></ol>` (5단계 이하)
  - 헷갈리는 두 개념: 비교표 `<div class="table-wrap"><table>` (3행 이하)
  - 비율·수치는 본문 글자로(예: 9:3:3:1). TeX는 식이 꼭 필요할 때만 `$…$`.
- **들을 때 포인트**: 2항목 이하. 학생이 수업 중에 **할 일**을 쓴다: "~가 나오면 ~를 확인해 보세요", "~와 비교해 보세요". 교수님이 무엇을 말할지 예측하지 않는다("설명하실 거예요", "강조하실 거예요"는 검사 실패).
- **기출 배지**: manifest 토픽에 `exam_terms`가 있을 때만, 들을 때 포인트의 한 항목을 `<li><span class="badge exam">기출</span> …</li>`로 시작하고 그 항목에 `exam_terms` 용어를 **모두 글자 그대로** 쓴다. 예: `<li><span class="badge exam">기출</span> 독립의 법칙이 나오면 정의를 그대로 받아 적어 두세요.</li>`. `exam_terms`가 없는 토픽에는 배지를 쓰지 않는다(검사 실패).
- 문체: "~해요" 체, 한 문장에 한 가지, 군더더기 수식어 없이. 전문용어는 처음 한 번 영어 병기(예: 양성잡종(dihybrid)).

## 높이 예산 (720×900 한 화면)
브라우저로 직접 잴 수 없는 작성자를 위한 기준이다(0929 실측, 템플릿 기본 글꼴). 화면에서 토픽이 쓸 수 있는 높이는 약 764px이고, 이전/다음 버튼과 여백을 빼면 **토픽 전체 650px 이하**가 안전하다.

| 부분 | 높이(약) | 한도 |
|---|---|---|
| 제목(h3) + 쪽 태그 | 70px | 고정 |
| 레이어 제목 | 레이어마다 27px | 고정 |
| 쉽게 말하면 첫 줄(lead) | 한 줄 33px, 두 줄 66px | **한 줄**(30자 안팎) |
| 그림(`figure`, figcaption 포함) | viewBox 560×140이면 약 164px | **130px 이하 목표**: viewBox 560×110~120, figcaption 한 줄 |
| 정확히 말하면 한 줄(`<p><b>용어</b>: 뜻</p>`) | 줄마다 35px | 그림 토픽은 3줄 이하 |
| `<dl>` 정의 한 항목 | 70px | 그림 토픽에서는 쓰지 않는다 |
| 들을 때 포인트 | 1항목 96px, 2항목 125px | 그림 토픽은 1항목(기출 배지 항목 우선) |

- 그림 토픽 예: 70 + 27×3 + 33 + 130 + 35×3 + 96 ≈ 515px, 여백을 더해도 650px 안이다.
- 검사기는 그림 크기만 본다: viewBox가 없거나, 폭이 600보다 넓거나(글자가 12px 아래로 줄어듦), 세로/가로가 0.25(560×140)보다 크면 `figure-size`로 실패한다. 토픽 전체 높이는 브라우저 검사(7단계)가 잰다.

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
- viewBox는 폭 560, 높이 110~140으로 가로로 넓게 그린다("높이 예산", 검사기 `figure-size`). 교과서 그림이 세로로 길면 단계를 가로 한 줄로 펼치고, 퍼넷 사각형처럼 칸이 많으면 칸 높이를 20~24로 줄인다.
- figcaption에 한 문장 설명과 출처를 쓴다: "… 교과서 그림 4.3을 단순하게 다시 그렸어요." 강의노트 그림이면 "강의노트 4장 p3 그림을 단순하게 다시 그렸어요." `figure_ref` 글자가 그대로 들어가야 한다.
- 색은 위의 `fig-*` 클래스만 쓴다(교과서 색을 옮기지 않는다). 그래야 다크모드에서도 보인다.
- 그림이 있는 토픽은 글을 300자 안팎으로 줄이고 "높이 예산"의 그림 토픽 한도를 지켜 720×900 한 화면에 맞춘다.
- 위젯(`class="widget"`)은 만들지 않는다.
````

- [ ] **Step 7: `references/review-prompt.md` 작성**

````markdown
# 리뷰어 지시문 (lite에서는 sonnet)

---
생명과학 예습노트 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/예습노트/<MMDD>/<예습노트 html>`
- 근거: `<RUN>/slides.txt`, `<RUN>/manifest.json`, 교과서 `<RUN>/repo/교과서/생명과학_기초와_응용_2판/<0N장_…pdf>`(스캔본: `<RUN>/work/textbook-pages/pNN.png`로 본다), 참고 그림 `<RUN>/work/textbook-figs/<토픽id>.png`
- 규칙: `<SKILL>/references/content-rules.md`

확인할 것:
1. **사실 오류**: 정의, 비율, 과정 순서, 조건이 강의노트·교과서와 맞는가.
2. **쪽 대응**: 토픽 태그의 쪽 번호가 실제 그 내용이 있는 쪽인가. 범위 안의 절 중 빠진 것이 있는가.
3. **범위**: 강의노트에 없는 설명이 "교과서 보충" 밖에 있는가. 교수님 발언을 지어낸 곳이 있는가.
4. **예습 효용**: 처음 듣는 학생이 수업 중에 이 토픽만 보고 강의노트를 따라갈 수 있는가. 쉽게 말하면이 전문용어 없이 2문장 이하인가. 들을 때 포인트가 구체적인 행동인가("잘 들으세요" 같은 빈말이나 교수님 발언 예측이 아닌가).
5. **기출 표시**: 기출 배지가 붙은 항목이 그 용어를 수업 중에 어떻게 챙길지 말해 주는가. 배지가 없어야 할 토픽에 "시험에 나와요" 같은 문장이 있는가.
6. **그림**: `figure_ref`가 있는 토픽마다 참고 PNG(Read 도구로 본다)와 SVG를 비교한다. 단계 순서, 배치, 화살표 방향, 표지 이름이 교과서 그림과 같은가. 표지 이름이 교과서·강의노트 용어와 글자까지 같은가. 교과서 그림에 없는 요소를 지어내지 않았는가. figcaption 출처가 맞는 그림 번호인가. SVG 좌표와 `<text>`를 직접 읽어 확인한다. 그림으로 설명하는 개념인데 `figure_ref`가 빠진 토픽도 적는다.
7. **문장·표현**: 꼬인 문장, 주어·서술어 불일치, 용어 표기 불일치, 잘린 문장, 빈 표 칸.

출력 형식(이것만):
```
## Critical
- [s2-dihybrid] 문제 → 고칠 내용
## Important
- …
## Minor
- …
```
각 항목은 토픽 id로 시작한다. 없으면 "없음".
---
````

- [ ] **Step 8: `references/browser-check.md` 작성**

````markdown
# 브라우저 검증 (메인 에이전트)

## 서버
file:// 미리보기에서는 스크립트가 돌지 않는다. 빈 포트로 서버를 띄운다. 셸 상태가 이어지지 않으므로 포트 번호를 먼저 출력하고 이후에는 그 숫자를 직접 쓴다.
1. 빈 포트: `python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1])"`
2. 서버: Bash 도구의 `run_in_background: true`로 `python3 -m http.server <port> --directory "<RUN>/repo"` (끝에 `&` 없이)
3. URL: `http://localhost:<port>/예습노트/<MMDD>/<파일명>` (한글 그대로)
4. 끝나면 그 백그라운드 작업을 멈추거나 `pkill -f "http.server <port>"`.

## 측정 전 준비
숨은 창에서는 `document.documentElement.clientWidth`가 0이 된다. 측정 전에 `resize_window`로 크기를 명시하고 `clientWidth > 0`을 확인한다. `.katex-mathml` 안 요소는 넘침 원인으로 치지 않는다.

## 화면별 측정 함수
템플릿은 한 번에 토픽 하나를 `.content` 안에 보여 준다. 아래 함수를 매 실행에 붙여 넣는다. `over`는 가로로 넘친 화면, `tall`은 세로 스크롤이 필요한 화면이다.
```js
async function measureScreens() {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const scroller = document.querySelector('.content') || document.documentElement;
  const screens = Array.from(document.querySelectorAll('main .screen'));
  const over = [], tall = [];
  for (const s of screens.length ? screens : [document.querySelector('main')]) {
    if (screens.length) { location.hash = s.id ? '#' + s.id : ''; await wait(150); }
    document.getAnimations().forEach((a) => a.finish());
    if (scroller.scrollWidth > scroller.clientWidth + 1 || document.documentElement.scrollWidth > window.innerWidth + 1) over.push(s.id || 'hero');
    if (s.matches('article.topic') && scroller.scrollHeight > scroller.clientHeight + 1) tall.push(s.id);
  }
  location.hash = '';
  await wait(150);
  return { over, tall };
}
```

## 반 화면(720×900, 수업 중 쓰는 크기)
`resize_window`(`width: 720`, `height: 900`) → 새로고침 → `clientWidth > 0` 확인 → `mcp__Claude_Browser__javascript_tool`:
```js
await new Promise((r) => setTimeout(r, 1500));
const textNodes = Array.from(document.querySelectorAll('main *, #panel-right *')).filter((e) => !['SCRIPT', 'STYLE'].includes(e.tagName) && !e.closest('[hidden]'));
({
  brand: document.querySelector('.brand').textContent,
  katexErrors: document.querySelectorAll('.katex-error').length,
  rawDollar: textNodes.some((e) => Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.textContent.includes('$'))),
  sumsInPanel: document.querySelectorAll('#panel-right .sum').length,
  sumsLeftInMain: document.querySelectorAll('main .sum').length,
  widgets: document.querySelectorAll('.widget').length,
  examBadges: document.querySelectorAll('main .layer.listen .badge.exam').length,
  ...(await measureScreens()),
})
```
통과: `brand: "예습노트"`, `katexErrors: 0`, `rawDollar: false`, `sumsInPanel`이 manifest에서 `layers`가 빈 목록이 아닌 토픽 수, `sumsLeftInMain: 0`, `widgets: 0`, `examBadges`가 `exam_terms`가 비어 있지 않은 토픽 수, `over: []`, `tall: []`. `tall`에 나온 토픽은 부분별 높이(h3, 태그, 각 레이어, figure, `dl`·`p.lead`)를 재서 content-rules "높이 예산"의 어느 한도를 넘었는지와 함께 작성자에게 되돌린다("lead 66px → 한 줄로", "dl 202px → `<p><b>` 형식으로" 처럼 줄일 곳과 목표 px를 적는다). `read_console_messages`에 오류가 없어야 한다.

개념 토픽 하나로 넘겨(`location.hash = '#<토픽 id>'`) 스크린샷을 찍고, 쪽 태그, "들을 때 포인트" 박스, 기출 배지가 보이는지 확인한다.

그림(`figure svg`)이 있는 토픽은 **모두** 넘겨서 스크린샷을 찍는다. 단계 순서와 레이블이 참고 PNG(`RUN/work/textbook-figs/<토픽id>.png`)·본문 설명과 맞는지 눈으로 확인한다. 틀리면 사실 오류라 되돌림 횟수와 관계없이 고친다.

## 모바일·다크
`resize_window`(`preset: "mobile"`, `colorScheme: "dark"`) → 새로고침 → `clientWidth > 0` 확인 → 위 스크립트 재실행(`over: []`만 통과 조건, 모바일의 `tall`은 참고만) → 스크린샷으로 그림 글자와 기출 배지가 보이는지 확인 → `#theme-toggle`을 눌러 배경색과 `aria-label`이 바뀌는지 확인한 뒤 `localStorage.removeItem('od-theme')`.

## 마무리
`resize_window`(`preset: "desktop"`, `colorScheme: "light"`)로 되돌리고 서버를 종료한다.
````

- [ ] **Step 9: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests -v`
Expected: 전체 OK (manifest 24 + template 3 + assemble 7 + check 28 + md 5 + files 21 + skill files 5 = 93).
`test_referenced_files_exist`가 9개 미만이라고 실패하면 SKILL.md가 `scripts/preview_files.py`, `scripts/preview_manifest.py`, `scripts/preview_assemble.py`, `scripts/preview_check.py`, `scripts/preview_md.py`, `assets/note-template.html`, `references/` 4개를 모두 경로로 언급하는지 본다.

- [ ] **Step 10: 커밋**

```bash
git add .agents/skills/bio-preview-note/SKILL.md .agents/skills/bio-preview-note/references .agents/skills/bio-preview-note/tests/test_preview_skill_files.py .claude/skills/bio-preview-note
git commit -m "feat(skills): add bio-preview-note skill instructions

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: 전체 회귀와 문서 정리

**Files:**
- Modify: `README.md` (디렉토리 구조에 `예습노트/` 한 줄)

**Interfaces:**
- Consumes: Task 1~7 전부.
- Produces: 통과한 세 테스트 묶음, README 안내.

- [ ] **Step 1: 세 테스트 묶음 실행**

Run: `python3 -m unittest discover -s .agents/skills/bio-preview-note/tests`
Expected: `Ran 93 tests … OK`

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `Ran 82 tests … OK`

Run: `.venv-question-bank/bin/python -m unittest discover tests`
Expected: `Ran 60 tests … OK (skipped=1)`

- [ ] **Step 2: 기존 복습노트가 새 템플릿에 영향받지 않는지 확인**

기존 `복습노트/*/정리노트_*.html`은 조립된 결과물이라 템플릿 변경의 영향을 받지 않는다. 확인만 한다:
Run: `git status --short 복습노트`
Expected: 출력 없음

- [ ] **Step 3: README에 한 줄 추가**

`README.md`의 `## 📁 디렉토리 구조` 목록에서 `- \`강의계획서/\`: 강의계획서 PDF` 줄 바로 아래에 추가:
```markdown
- `예습노트/`: 수업 전에 보는 예습노트(`/bio-preview-note [MMDD]`로 생성, 수업 날짜별 폴더)
```

- [ ] **Step 4: 커밋**

```bash
git add README.md
git commit -m "docs: mention preview notes folder in README

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 5: 실사용 인수 확인 (사용자와 함께, 커밋 없음)**

새 세션에서 `/bio-preview-note 1001 lite`를 한 번 돌려 `예습노트/1001/`이 만들어지고 5·7·8단계가 통과하는지 본다. 결과 커밋 여부는 사용자가 정한다. 이 단계는 모델 호출 비용이 드는 실제 실행이라 구현 작업에 포함하지 않고 제안만 한다.
