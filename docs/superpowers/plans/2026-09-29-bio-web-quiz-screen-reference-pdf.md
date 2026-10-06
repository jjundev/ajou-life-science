# 2·3장 웹과제 화면용 판별표 PDF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 태블릿·노트북에서 각 장의 판별 근거를 빠르게 찾을 수 있는 2쪽 PDF를 생성한다.

**Architecture:** 콘텐츠를 장별 3개 구역의 불변 데이터로 두고, ReportLab 캔버스가 16:10 가로 페이지 두 장에 배치한다. PDF 텍스트·페이지 크기·페이지 수는 자동 검증하고, Poppler 이미지 렌더링으로 시각 검수한다.

**Tech Stack:** Python 3, ReportLab, pypdf 또는 PyMuPDF, Poppler `pdftoppm`, Windows 맑은 고딕 TTF.

**Spec:** `docs/superpowers/specs/2026-09-29-bio-web-quiz-screen-reference-design.md`

## Global Constraints

- 결과 PDF: `output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf`.
- 화면용 16:10 가로 페이지 1152 × 720 pt, 정확히 2쪽, 각 장 1쪽.
- 본문 글자 15pt 이상. 정보를 더 넣기 위해 글자를 줄이지 않는다.
- 정답 번호·문항 전문·출제 확률·4장 유전은 넣지 않는다.
- 생성 전 PDF skill의 artifact-operation 명령을 정확히 한 번 실행한다.
- 기존 원천 자료와 `tmp/`의 기존 비추적 파일은 수정하거나 삭제하지 않는다.

## Review Focus

1. **한글 글꼴을 찾지 못함:** 명확한 오류로 멈춰야 하며 빈 글리프 PDF를 만들면 안 된다. Task 2에서 글꼴 경로 부재 테스트.
2. **한글·기호가 PDF 추출에서 빠짐:** 핵심 용어가 텍스트로 남아야 한다. Task 2의 추출 테스트.
3. **본문이 페이지 밖으로 넘침:** 생성이 실패해야 한다. Task 2의 높이 제한 테스트.
4. **4장 내용이 섞임:** 3장 페이지에 멘델·분리의 법칙이 없어야 한다. Task 1의 범위 테스트.
5. **2쪽 중복 또는 누락:** 2장 다음 3장 순서로 정확히 두 장이어야 한다. Task 2의 페이지 테스트.

---

## File map

- Create `scripts/web_quiz_reference_content.py`: 장별 제목과 3개 구역의 검토된 원고. PDF 배치 코드를 포함하지 않는다.
- Create `scripts/build_web_quiz_reference_pdf.py`: 글꼴 등록, 구역·도식 배치, PDF 생성과 넘침 검사.
- Create `tests/test_web_quiz_reference_pdf.py`: 내용 범위, PDF 구조, 글꼴·넘침·추출 검사.
- Create `output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf`: 최종 결과물.

### Task 1: 장별 판별 원고 확정

**Files:**
- Create: `scripts/web_quiz_reference_content.py`
- Create: `tests/test_web_quiz_reference_pdf.py`

**Interfaces:**
- Consumes: 앞의 spec과 2·3장 강의노트·복습노트.
- Produces: `PAGES: tuple[Page, Page]`; `Page(chapter: int, title: str, columns: tuple[Column, Column, Column])`; `Column(title: str, entries: tuple[Entry, ...])`; `Entry(label: str, text: str)`.

- [ ] **Step 1: 실패하는 내용 테스트 작성**

```python
from scripts.web_quiz_reference_content import PAGES

def test_content_is_only_chapters_two_and_three():
    assert tuple(page.chapter for page in PAGES) == (2, 3)
    assert all(len(page.columns) == 3 for page in PAGES)
    text = " ".join(entry.label + entry.text for page in PAGES
                    for column in page.columns for entry in column.entries)
    for term in ("광계Ⅱ", "NADP⁺", "상동염색체", "자매염색분체", "X/2"):
        assert term in text
    for excluded in ("멘델", "분리의 법칙", "정답 ①"):
        assert excluded not in text
```

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest tests/test_web_quiz_reference_pdf.py::test_content_is_only_chapters_two_and_three -q`

Expected: `ModuleNotFoundError` for `scripts.web_quiz_reference_content`.

- [ ] **Step 3: 콘텐츠 모듈 작성**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    label: str
    text: str

@dataclass(frozen=True)
class Column:
    title: str
    entries: tuple[Entry, ...]

@dataclass(frozen=True)
class Page:
    chapter: int
    title: str
    columns: tuple[Column, Column, Column]

PAGES = (
    Page(2, "2장  세포호흡 · 광합성", (
        Column("세포호흡", (
            Entry("장소", "해당과정=세포질 / 피루브산 산화·시트르산 회로=미토콘드리아 기질 / 전자전달계·ATP 합성효소=내막"),
            Entry("해당과정", "포도당 1개 → 피루브산 2개, 순 2 ATP·2 NADH. CO₂는 아직 나오지 않음"),
            Entry("CO₂", "피루브산 산화에서 처음 발생. 산소는 전자전달계의 마지막에서 사용"),
            Entry("ATP 수지", "완전 산화: 32 = 기질 수준 4(해당 2+회로 2) + 산화적 28"),
            Entry("전자", "NADH·FADH₂ → 전자전달계 → O₂(최종 수용체) → H₂O"),
            Entry("H⁺", "전자전달계가 기질→막간공간으로 퍼냄; ATP 합성효소를 거쳐 기질로 돌아오며 ATP 합성"),
        )),
        Column("발효 · 광의존반응", (
            Entry("산소 없음", "전자전달계 정지 → NAD⁺ 재생 불가 → 해당과정도 지속 불가"),
            Entry("발효", "NADH를 산화해 NAD⁺ 재생. ATP는 해당과정의 2개뿐"),
            Entry("발효 종류", "젖산: 피루브산이 전자 받음 / 알코올: CO₂ 이탈 뒤 아세트알데하이드가 받음"),
            Entry("명반응 장소", "틸라코이드 막; 물이 광계Ⅱ에서 분해되어 O₂가 나옴"),
            Entry("전자 순서", "H₂O → 광계Ⅱ → 전자전달계 → 광계Ⅰ → NADP⁺ → NADPH"),
            Entry("H⁺ 방향", "틸라코이드 안에 쌓임 → 스트로마로 나오며 ATP 합성"),
        )),
        Column("캘빈 회로 · 함정", (
            Entry("두 반응", "명반응이 ATP·NADPH 생산 → 캘빈 회로가 CO₂·ATP·NADPH 사용"),
            Entry("캘빈 장소", "스트로마. 탄소 고정 → 환원 → RuBP 재생"),
            Entry("회전 수", "CO₂ 1개/회전; 포도당 1개에 CO₂ 6개가 필요"),
            Entry("산소 기원", "광합성 O₂는 H₂O에서 나옴. 캘빈 회로는 O₂를 만들지 않음"),
            Entry("효소", "활성화에너지↓, 기질 특이성, 반응 뒤 재사용"),
            Entry("스펙트럼", "흡수=파장별 흡광도 / 작용=파장별 실제 광합성량"),
        )),
    )),
    Page(3, "3장  세포분열", (
        Column("염색체 · 세포주기", (
            Entry("자매염색분체", "S기 복제로 생긴 한 염색체의 두 사본; 동원체로 붙음"),
            Entry("상동염색체", "모계·부계에서 하나씩 온 쌍; 같은 자리의 대립유전자는 다를 수 있음"),
            Entry("중심체/동원체", "중심체에서 방추사(미세소관)가 뻗음 / 동원체는 염색체에서 붙는 부위"),
            Entry("세포주기", "G₁ 성장 → S DNA 복제 → G₂ 준비 → M 분열. G₁·S·G₂=간기"),
            Entry("G₀", "G₁에서 나와 분열을 멈춘 상태"),
            Entry("확인점", "DNA 복제·손상, 방추사 부착 등을 검사한 뒤 다음 단계로 진행"),
        )),
        Column("무엇이 분리되나", (
            Entry("유사분열", "전기 응축·핵막 소실 → 중기 중앙 배열 → 후기 자매염색분체 분리 → 말기 핵막 재형성"),
            Entry("결과", "유사분열: 2n 세포 2개 / 감수분열: n 세포 4개"),
            Entry("감수 전기Ⅰ", "상동염색체 접합 → 4분체 형성, 비자매염색분체 사이 교차"),
            Entry("감수 후기Ⅰ", "상동염색체 분리 → 이미 n; 각 염색체의 자매염색분체는 여전히 붙음"),
            Entry("감수 후기Ⅱ", "자매염색분체 분리; Ⅰ과 Ⅱ 사이 DNA 복제 없음"),
            Entry("세포질 분열", "동물=분열홈 / 식물=세포판"),
        )),
        Column("계산 · 암 판별", (
            Entry("DNA 양", "G₂를 X라 하면 말기Ⅰ 뒤·중기Ⅱ=X/2, 말기Ⅱ 뒤=X/4"),
            Entry("조합 수", "상동염색체 n쌍의 무작위 분배=2ⁿ. 2n=4면 n=2 → 4가지"),
            Entry("유전 다양성", "전기Ⅰ 교차 + 상동염색체 무작위 분배 + 무작위 수정"),
            Entry("접촉 저해", "이웃 세포와 닿으면 분열 중단: 정상세포의 성질, 암세포는 상실"),
            Entry("전이", "악성 종양 세포가 다른 부위로 퍼지는 과정"),
            Entry("조절", "사이클린·CDK=주기 진행 / 발암 유전자=과도한 촉진 / 종양 억제 유전자=억제·수선"),
        )),
    )),
)
```

- [ ] **Step 4: 내용 테스트와 원천 대조**

Run: `python -m pytest tests/test_web_quiz_reference_pdf.py::test_content_is_only_chapters_two_and_three -q`

Expected: PASS. 이어서 각 Entry를 spec의 출처와 비교하여 과도한 단정이나 4장 내용이 없는지 수동 확인한다. 특히 발효·ATP 수지·감수분열 DNA 양을 확인한다.

- [ ] **Step 5: 커밋**

```powershell
git add scripts/web_quiz_reference_content.py tests/test_web_quiz_reference_pdf.py docs/superpowers/specs/2026-09-29-bio-web-quiz-screen-reference-design.md docs/superpowers/plans/2026-09-29-bio-web-quiz-screen-reference-pdf.md
git commit -m "docs: define screen reference content for biology web quiz"
```

### Task 2: 화면용 PDF 배치와 검증

**Files:**
- Create: `scripts/build_web_quiz_reference_pdf.py`
- Modify: `tests/test_web_quiz_reference_pdf.py`
- Create: `output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf`

**Interfaces:**
- Consumes: `PAGES`, `Page`, `Column`, `Entry` from Task 1.
- Produces: `build_pdf(output_path: Path, font_path: Path = Path(r"C:\Windows\Fonts\malgun.ttf")) -> None`.

- [ ] **Step 1: PDF 구조·실패 조건 테스트 작성**

```python
from pathlib import Path
import pytest
from pypdf import PdfReader
from scripts.build_web_quiz_reference_pdf import build_pdf

def test_pdf_is_two_ordered_screen_pages(tmp_path):
    target = tmp_path / "reference.pdf"
    build_pdf(target)
    reader = PdfReader(target)
    assert len(reader.pages) == 2
    assert all(abs(float(p.mediabox.width) - 1152) < 1 for p in reader.pages)
    assert all(abs(float(p.mediabox.height) - 720) < 1 for p in reader.pages)
    assert "2장" in reader.pages[0].extract_text()
    assert "3장" in reader.pages[1].extract_text()
    text = " ".join(p.extract_text() for p in reader.pages)
    for term in ("광계Ⅱ", "NADP⁺", "상동염색체", "자매염색분체", "X/2"):
        assert term in text

def test_missing_font_fails_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="Korean font"):
        build_pdf(tmp_path / "out.pdf", tmp_path / "missing.ttf")

def test_overflow_fails_instead_of_clipping(tmp_path, monkeypatch):
    from scripts import build_web_quiz_reference_pdf as render
    monkeypatch.setattr(render, "BODY_SIZE", 40)
    with pytest.raises(ValueError, match="overflow"):
        render.build_pdf(tmp_path / "out.pdf")

def test_long_unspaced_korean_word_wraps_within_column():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from scripts.build_web_quiz_reference_pdf import wrap_text, BODY_SIZE, COLUMN_W
    pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
    lines = wrap_text("상동염색체" * 20, COLUMN_W)
    assert len(lines) > 1
    assert all(pdfmetrics.stringWidth(line, "Malgun", BODY_SIZE) <= COLUMN_W for line in lines)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest tests/test_web_quiz_reference_pdf.py -q`

Expected: import failure for the renderer module.

- [ ] **Step 3: 최소 렌더러 구현**

Use ReportLab. The following is the complete first implementation of `scripts/build_web_quiz_reference_pdf.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdf_canvas

from scripts.web_quiz_reference_content import Column, Entry, PAGES

PAGE_W, PAGE_H = 1152, 720
MARGIN = 36
GAP = 18
BODY_SIZE = 16
BODY_LEADING = 21
COLUMN_W = (PAGE_W - 2 * MARGIN - 2 * GAP) / 3
INK = colors.HexColor("#14202B")
ACCENT = colors.HexColor("#176B70")

def wrap_text(value: str, width: float) -> list[str]:
    lines = []
    for raw in simpleSplit(value, "Malgun", BODY_SIZE, width):
        if pdfmetrics.stringWidth(raw, "Malgun", BODY_SIZE) <= width:
            lines.append(raw)
            continue
        part = ""
        for char in raw:
            candidate = part + char
            if part and pdfmetrics.stringWidth(candidate, "Malgun", BODY_SIZE) > width:
                lines.append(part)
                part = char
            else:
                part = candidate
        if part:
            lines.append(part)
    return lines

def draw_entry(c: pdf_canvas.Canvas, entry: Entry, x: float, top: float, width: float) -> float:
    c.setFillColor(ACCENT)
    c.setFont("Malgun", BODY_SIZE)
    c.drawString(x, top, entry.label)
    lines = wrap_text(entry.text, width)
    c.setFillColor(INK)
    for index, line in enumerate(lines):
        c.drawString(x, top - 25 - BODY_LEADING * index, line)
    return top - 25 - BODY_LEADING * len(lines) - 11

def draw_column(c: pdf_canvas.Canvas, column: Column, x: float, top: float) -> float:
    c.setFillColor(INK)
    c.setFont("Malgun", 21)
    c.drawString(x, top, column.title)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    c.line(x, top - 9, x + COLUMN_W, top - 9)
    cursor = top - 35
    for entry in column.entries:
        cursor = draw_entry(c, entry, x, cursor, COLUMN_W)
        if cursor < 55:
            raise ValueError(f"overflow: {column.title}")
    return cursor

def draw_chromosome_pair(c: pdf_canvas.Canvas) -> None:
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    for center_x in (880, 922):
        c.line(center_x - 10, 681, center_x + 10, 643)
        c.line(center_x + 10, 681, center_x - 10, 643)
    c.setFont("Malgun", 11)
    c.setFillColor(INK)
    c.drawString(951, 661, "한 X 안: 자매 / 두 X 사이: 상동")

def build_pdf(output_path: Path, font_path: Path = Path(r"C:\Windows\Fonts\malgun.ttf")) -> None:
    if not font_path.is_file():
        raise FileNotFoundError(f"Korean font missing: {font_path}")
    pdfmetrics.registerFont(TTFont("Malgun", str(font_path)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        c = pdf_canvas.Canvas(str(output_path), pagesize=(PAGE_W, PAGE_H))
        c.setTitle("생명과학 2·3장 웹과제 판별표")
        for page in PAGES:
            c.setFillColor(INK)
            c.setFont("Malgun", 30)
            c.drawString(MARGIN, 660, page.title)
            if page.chapter == 3:
                draw_chromosome_pair(c)
            for index, column in enumerate(page.columns):
                x = MARGIN + index * (COLUMN_W + GAP)
                draw_column(c, column, x, 604)
                if index < 2:
                    c.setStrokeColor(colors.HexColor("#C8D3D6"))
                    c.setLineWidth(0.6)
                    separator_x = x + COLUMN_W + GAP / 2
                    c.line(separator_x, 45, separator_x, 617)
            c.setFont("Malgun", 11)
            c.setFillColor(INK)
            c.drawString(MARGIN, 28, "10월 1일 웹과제 · 판별 근거 빠른 참조")
            c.showPage()
        c.save()
    except Exception:
        output_path.unlink(missing_ok=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build_pdf(args.output)
```

The small chromosome diagram sits in the title band, so it does not consume column height. `wrap_text` splits an unspaced Korean token by glyph when needed.

- [ ] **Step 4: PDF 기술 테스트 실행**

Run: `python -m pytest tests/test_web_quiz_reference_pdf.py -q`

Expected: all tests PASS. If the normal content overflows, shorten low-priority entries in Task 1; keep `BODY_SIZE >= 15`.

- [ ] **Step 5: 실제 결과물 생성**

Before the first authoring command, run the PDF skill artifact-operation command exactly once for one PDF output. On this Windows host, use the discovered tool path. Then run:

```powershell
node 'C:\Users\Hyunjun\.codex\plugins\cache\openai-primary-runtime\pdf\26.909.12148\skills\pdf\container_tools\mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 1 --output-format pdf
python -m scripts.build_web_quiz_reference_pdf output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf
pdfinfo output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf
New-Item -ItemType Directory -Force 'tmp/pdfs' | Out-Null
pdftoppm -f 1 -l 2 -png -r 110 output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf tmp/pdfs/web_quiz_reference
```

Expected: `Pages: 2` and two PNGs. Open both PNGs at original resolution; verify headings, all 3 columns, X-pair diagram, arrows, subscripts, no clipping or overlap. If legibility is poor, revise layout/content and repeat the render once.

- [ ] **Step 6: 최종 확인과 커밋**

Run: `python -m pytest tests/test_web_quiz_reference_pdf.py -q` and `git status --short`.

Expected: tests PASS; only intended new/modified files are staged. Do not stage pre-existing `tmp/` files.

```powershell
git add scripts/build_web_quiz_reference_pdf.py scripts/web_quiz_reference_content.py tests/test_web_quiz_reference_pdf.py output/pdf/2026-10-01_생명과학_2-3장_웹과제_판별표.pdf
git commit -m "feat: add screen reference PDF for biology chapters 2 and 3"
```

## Self-review

- Spec coverage: two pages, screen ratio, three areas per page, chapter separation, core concepts, font size, source limits, text extraction, visual QA all assigned to Tasks 1–2.
- Review Focus coverage: all five conditions have Task 1 or Task 2 tests; the overflow test deliberately increases the font size.
- Type consistency: Task 2 imports the exact `PAGES`, `Page`, `Column`, and `Entry` interfaces defined in Task 1.
- Placeholder scan: no implementation steps are deferred. The renderer functions above define the exact geometry and failure condition; visual art is limited to one small X-pair diagram.
