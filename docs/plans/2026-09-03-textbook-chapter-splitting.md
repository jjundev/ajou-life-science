# 생명과학 교재 장별 분할 (Textbook Chapter Splitting) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `교과서/생명과학_기초와_응용_2판.pdf` (총 522쪽)를 1장부터 19장 및 앞부속/부록 단위(총 23개 파일)로 완벽하고 무손실(lossless)하게 분할하여 `교과서/장별/` 디렉토리에 생성한다.

**Architecture:** PyMuPDF(`fitz`)를 활용하여 원본 이미지와 렌더링 품질을 그대로 유지하며 고속으로 페이지 슬라이스를 추출한다. 사전 검증된 522쪽 전체 커버리지 매핑(단 1쪽의 누락 및 중복 없는 전수 매핑)을 기반으로 스크립트를 구성하고, 단위 테스트(`unittest`)를 통해 페이지 연속성 및 파일 무결성을 보증한다.

**Tech Stack:** Python 3.14, PyMuPDF (`fitz`), `unittest`, `tempfile`

## Global Constraints

- 원본 교재 파일: `교과서/생명과학_기초와_응용_2판.pdf` (522쪽) 보존 (수정/삭제 절대 금지)
- 분할 대상: 앞부속(1~9), 1~19장(10~471), 부록 3종(472~522) 전수 포함 (총 23개 분할 PDF)
- 분할 저장 디렉토리: `교과서/장별/`
- 전체 분할 페이지 합산이 원본 페이지 수(522쪽)와 정확히 일치해야 함 (연속성 및 배타성 만족)
- macOS 샌드박스 호환을 위해 git 명령 시 `GIT_CONFIG_GLOBAL=/dev/null` 적용
- 대용량 분할 PDF 파일의 실수 커밋 방지를 위해 `교과서/장별/`을 `.gitignore`에 등록

---

## Chapter & Page Mapping Specification

| 구분 | 파일명 | 시작(PDF) | 끝(PDF) | 쪽수 | 내용 요약 |
|---|---|---|---|---|---|
| 앞부속 | `00_앞부속_표지_차례.pdf` | 1 | 9 | 9 | 표지, 머리말, 주요차례, 세부차례 |
| 1장 | `01장_생물분자와_세포.pdf` | 10 | 37 | 28 | CHAPTER 1 생물분자와 세포, 응용이슈 1 |
| 2장 | `02장_세포호흡과_광합성.pdf` | 38 | 61 | 24 | CHAPTER 2 세포호흡과 광합성 |
| 3장 | `03장_세포분열.pdf` | 62 | 79 | 18 | CHAPTER 3 세포분열 |
| 4장 | `04장_유전.pdf` | 80 | 99 | 20 | 단원 2 유전학, CHAPTER 4 유전 |
| 5장 | `05장_DNA_복제와_유전자의_발현.pdf` | 100 | 125 | 26 | CHAPTER 5 DNA 복제와 유전자의 발현 |
| 6장 | `06장_DNA_기술과_유전체학.pdf` | 126 | 145 | 20 | CHAPTER 6 DNA 기술과 유전체학, 응용이슈 2 |
| 7장 | `07장_진화_사상과_소진화.pdf` | 146 | 163 | 18 | 단원 3 진화와 생물다양성, CHAPTER 7 |
| 8장 | `08장_종분화와_대진화.pdf` | 164 | 183 | 20 | CHAPTER 8 종분화와 대진화 |
| 9장 | `09장_생물다양성_원핵생물과_진핵생물.pdf` | 184 | 215 | 32 | CHAPTER 9 생물다양성: 원핵생물과 진핵생물 |
| 10장 | `10장_식물체의_구조_수송_및_영양.pdf` | 216 | 245 | 30 | 단원 4 식물의 구조와 기능, CHAPTER 10 |
| 11장 | `11장_식물의_생식_및_발달.pdf` | 246 | 267 | 22 | CHAPTER 11 식물의 생식 및 발달, 응용이슈 3 |
| 12장 | `12장_신경계_감각계_근육계.pdf` | 268 | 295 | 28 | 단원 5 동물의 구조와 기능, CHAPTER 12 |
| 13장 | `13장_호흡계와_순환계.pdf` | 296 | 317 | 22 | CHAPTER 13 호흡계와 순환계 |
| 14장 | `14장_면역체계.pdf` | 318 | 337 | 20 | CHAPTER 14 면역체계, 생활 속 이슈 1 |
| 15장 | `15장_동물_영양_배설_내분비.pdf` | 338 | 367 | 30 | CHAPTER 15 동물 영양, 배설, 내분비, 생활 속 이슈 2 |
| 16장 | `16장_동물의_생식과_발생.pdf` | 368 | 387 | 20 | CHAPTER 16 동물의 생식과 발생 |
| 17장 | `17장_개체군과_군집.pdf` | 388 | 419 | 32 | 단원 6 생태학과 행동학, CHAPTER 17 |
| 18장 | `18장_생태계와_기후_변화.pdf` | 420 | 447 | 28 | CHAPTER 18 생태계와 기후 변화, 응용이슈 5 |
| 19장 | `19장_동물행동.pdf` | 448 | 471 | 24 | CHAPTER 19 동물행동 |
| 부록1 | `부록_해답.pdf` | 472 | 477 | 6 | ANSWER (A-1 ~ A-6) |
| 부록2 | `부록_용어풀이.pdf` | 478 | 506 | 29 | GLOSSARY (G-1 ~ G-29) |
| 부록3 | `부록_찾아보기.pdf` | 507 | 522 | 16 | INDEX (I-1 ~ I-16) |

---

## User Review Required

> [!IMPORTANT]
> - **출력 위치 및 명명 규칙**: `교과서/장별/` 디렉토리에 장 번호와 제목을 병기한 파일명(`01장_생물분자와_세포.pdf`, `부록_해답.pdf` 등 총 23개)으로 분할 저장합니다.
> - **원본 파일 무손실 유지**: 원본 `교과서/생명과학_기초와_응용_2판.pdf`는 수정/삭제 없이 안전하게 보존됩니다.

---

## Proposed Changes

### Scripts & Automation

#### [NEW] [`scripts/__init__.py`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/scripts/__init__.py)
#### [NEW] [`scripts/split_textbook.py`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/scripts/split_textbook.py)
- PyMuPDF 기반 장별 분할 스크립트.
- 메타데이터 정의 및 검증 기능(`validate_metadata`), PDF 슬라이싱(`split_pdf`) 제공.

### Tests

#### [NEW] [`tests/__init__.py`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/tests/__init__.py)
#### [NEW] [`tests/test_split_textbook.py`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/tests/test_split_textbook.py)
- 메타데이터 522쪽 완결성 및 임시 디렉토리를 활용한 분할 로직 단위 테스트.

#### [NEW] [`tests/test_generated_files.py`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/tests/test_generated_files.py)
- 분할 완료 후 23개 파일의 실제 페이지 수 및 렌더링 무결성 전수 검증 테스트.

### Repository Configuration & Documentation

#### [MODIFY] [`.gitignore`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.gitignore)
- 대용량 바이너리 보호를 위해 `교과서/장별/` 및 Python 캐시(`__pycache__/`) 등록.

#### [MODIFY] [`README.md`](file:///Users/hyunjun_macbook_pro/Documents/Univ/생명과학/README.md)
- `교과서/장별/` 디렉토리 구성 및 장별 인덱스 표 추가.

---

## Tasks

### Task 1: 환경 준비 및 분할 엔진 스크립트 작성 (TDD)

**Files:**
- Create: `scripts/__init__.py`, `scripts/split_textbook.py`
- Create: `tests/__init__.py`, `tests/test_split_textbook.py`

**Interfaces:**
- Consumes: `fitz` (PyMuPDF)
- Produces: 
  - `CHAPTERS`: `list[dict]` containing `{"id": str, "title": str, "start": int, "end": int, "filename": str}`
  - `validate_metadata(chapters: list[dict], total_pages: int) -> bool`
  - `split_pdf(src_path: str, out_dir: str, chapters: list[dict]) -> list[str]`

- [ ] **Step 1: 실패하는 단위 테스트 작성**

`tests/__init__.py` 및 `tests/test_split_textbook.py` 작성:
```python
# tests/test_split_textbook.py
import unittest
import os
import tempfile
import fitz
from scripts.split_textbook import CHAPTERS, validate_metadata, split_pdf

class TestSplitTextbook(unittest.TestCase):
    def test_metadata_coverage(self):
        """총 522쪽이 1쪽부터 522쪽까지 누락 및 겹침 없이 연속되는지 검증"""
        self.assertEqual(len(CHAPTERS), 23)
        self.assertTrue(validate_metadata(CHAPTERS, total_pages=522))

    def test_split_pdf_execution(self):
        """임시 디렉토리에서 PDF(4쪽) 분할 동작 및 무결성 검증"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = os.path.join(temp_dir, "test_src.pdf")
            temp_out = os.path.join(temp_dir, "test_out_dir")
            
            doc = fitz.open()
            for _ in range(4):
                doc.new_page()
            doc.save(temp_src)
            doc.close()

            dummy_meta = [
                {"id": "part1", "title": "Part 1", "start": 1, "end": 2, "filename": "p1.pdf"},
                {"id": "part2", "title": "Part 2", "start": 3, "end": 4, "filename": "p2.pdf"}
            ]
            
            res = split_pdf(temp_src, temp_out, dummy_meta)
            self.assertEqual(len(res), 2)
            
            doc1 = fitz.open(os.path.join(temp_out, "p1.pdf"))
            self.assertEqual(len(doc1), 2)
            doc1.close()
            
            doc2 = fitz.open(os.path.join(temp_out, "p2.pdf"))
            self.assertEqual(len(doc2), 2)
            doc2.close()

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python3 -m unittest tests/test_split_textbook.py`  
Expected: FAIL (`ModuleNotFoundError: No module named 'scripts'`)

- [ ] **Step 3: `scripts/__init__.py` 및 `scripts/split_textbook.py` 구현**

```python
# scripts/split_textbook.py
import os
import argparse
import fitz

CHAPTERS = [
    {"id": "00", "title": "앞부속", "start": 1, "end": 9, "filename": "00_앞부속_표지_차례.pdf"},
    {"id": "01", "title": "생물분자와 세포", "start": 10, "end": 37, "filename": "01장_생물분자와_세포.pdf"},
    {"id": "02", "title": "세포호흡과 광합성", "start": 38, "end": 61, "filename": "02장_세포호흡과_광합성.pdf"},
    {"id": "03", "title": "세포분열", "start": 62, "end": 79, "filename": "03장_세포분열.pdf"},
    {"id": "04", "title": "유전", "start": 80, "end": 99, "filename": "04장_유전.pdf"},
    {"id": "05", "title": "DNA 복제와 유전자의 발현", "start": 100, "end": 125, "filename": "05장_DNA_복제와_유전자의_발현.pdf"},
    {"id": "06", "title": "DNA 기술과 유전체학", "start": 126, "end": 145, "filename": "06장_DNA_기술과_유전체학.pdf"},
    {"id": "07", "title": "진화 사상과 소진화", "start": 146, "end": 163, "filename": "07장_진화_사상과_소진화.pdf"},
    {"id": "08", "title": "종분화와 대진화", "start": 164, "end": 183, "filename": "08장_종분화와_대진화.pdf"},
    {"id": "09", "title": "생물다양성: 원핵생물과 진핵생물", "start": 184, "end": 215, "filename": "09장_생물다양성_원핵생물과_진핵생물.pdf"},
    {"id": "10", "title": "식물체의 구조, 수송 및 영양", "start": 216, "end": 245, "filename": "10장_식물체의_구조_수송_및_영양.pdf"},
    {"id": "11", "title": "식물의 생식 및 발달", "start": 246, "end": 267, "filename": "11장_식물의_생식_및_발달.pdf"},
    {"id": "12", "title": "신경계, 감각계, 근육계", "start": 268, "end": 295, "filename": "12장_신경계_감각계_근육계.pdf"},
    {"id": "13", "title": "호흡계와 순환계", "start": 296, "end": 317, "filename": "13장_호흡계와_순환계.pdf"},
    {"id": "14", "title": "면역체계", "start": 318, "end": 337, "filename": "14장_면역체계.pdf"},
    {"id": "15", "title": "동물 영양, 배설, 내분비", "start": 338, "end": 367, "filename": "15장_동물_영양_배설_내분비.pdf"},
    {"id": "16", "title": "동물의 생식과 발생", "start": 368, "end": 387, "filename": "16장_동물의_생식과_발생.pdf"},
    {"id": "17", "title": "개체군과 군집", "start": 388, "end": 419, "filename": "17장_개체군과_군집.pdf"},
    {"id": "18", "title": "생태계와 기후 변화", "start": 420, "end": 447, "filename": "18장_생태계와_기후_변화.pdf"},
    {"id": "19", "title": "동물행동", "start": 448, "end": 471, "filename": "19장_동물행동.pdf"},
    {"id": "A1", "title": "해답", "start": 472, "end": 477, "filename": "부록_해답.pdf"},
    {"id": "A2", "title": "용어풀이", "start": 478, "end": 506, "filename": "부록_용어풀이.pdf"},
    {"id": "A3", "title": "찾아보기", "start": 507, "end": 522, "filename": "부록_찾아보기.pdf"},
]

def validate_metadata(chapters: list[dict], total_pages: int = 522) -> bool:
    if not chapters:
        return False
    if chapters[0]["start"] != 1:
        return False
    for i in range(len(chapters) - 1):
        if chapters[i]["end"] + 1 != chapters[i + 1]["start"]:
            return False
    if chapters[-1]["end"] != total_pages:
        return False
    return True

def split_pdf(src_path: str, out_dir: str, chapters: list[dict]) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    src_doc = fitz.open(src_path)
    output_paths = []
    try:
        for item in chapters:
            start_idx = item["start"] - 1
            end_idx = item["end"] - 1
            out_path = os.path.join(out_dir, item["filename"])
            
            new_doc = fitz.open()
            new_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx)
            new_doc.save(out_path, garbage=3, deflate=True)
            new_doc.close()
            output_paths.append(out_path)
    finally:
        src_doc.close()
    return output_paths

def main():
    parser = argparse.ArgumentParser(description="생명과학 교재 PDF 장별 분할")
    parser.add_argument("--src", default="교과서/생명과학_기초와_응용_2판.pdf", help="원본 PDF 경로")
    parser.add_argument("--out", default="교과서/장별", help="출력 디렉토리")
    args = parser.parse_args()

    assert validate_metadata(CHAPTERS, 522), "메타데이터 검증 실패"
    print(f"분할 시작: {args.src} -> {args.out}")
    paths = split_pdf(args.src, args.out, CHAPTERS)
    print(f"성공적으로 {len(paths)}개 파일 분할 완료.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python3 -m unittest tests/test_split_textbook.py -v`  
Expected: `Ran 2 tests in ... OK`

- [ ] **Step 5: 커밋**

```bash
GIT_CONFIG_GLOBAL=/dev/null git add scripts/ tests/
GIT_CONFIG_GLOBAL=/dev/null git commit -m "feat: add textbook splitting engine and metadata tests"
```

---

### Task 2: 실제 교재 PDF 분할 실행 및 파일 생성

**Files:**
- Run: `scripts/split_textbook.py`
- Output: `교과서/장별/*.pdf` (23개 파일 생성)

**Interfaces:**
- CLI 명령 실행: `python3 scripts/split_textbook.py`

- [ ] **Step 1: 분할 스크립트 실행**

Run: `python3 scripts/split_textbook.py --src "교과서/생명과학_기초와_응용_2판.pdf" --out "교과서/장별"`  
Expected: `성공적으로 23개 파일 분할 완료.`

- [ ] **Step 2: 생성된 파일 목록 및 크기 확인**

Run: `ls -lh "교과서/장별"`  
Expected: 23개 PDF 파일 모두 생성 확인

---

### Task 3: 무결성 검증, .gitignore 갱신 및 README 문서화

**Files:**
- Create: `tests/test_generated_files.py`
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- `test_generated_files.py`: 23개 분할 PDF의 실제 페이지 수가 메타데이터와 완벽히 일치하는지, 열람 및 파싱이 정상인지 검증

- [ ] **Step 1: 생성된 분할 파일 전수 검증 테스트 작성 및 실행**

```python
# tests/test_generated_files.py
import unittest
import os
import fitz
from scripts.split_textbook import CHAPTERS

class TestGeneratedFiles(unittest.TestCase):
    def test_all_files_exist_and_match_pages(self):
        out_dir = "교과서/장별"
        self.assertTrue(os.path.exists(out_dir))
        
        total_extracted_pages = 0
        for item in CHAPTERS:
            path = os.path.join(out_dir, item["filename"])
            self.assertTrue(os.path.exists(path), f"File missing: {path}")
            
            doc = fitz.open(path)
            expected_pages = item["end"] - item["start"] + 1
            self.assertEqual(len(doc), expected_pages, f"Page mismatch in {item['filename']}")
            total_extracted_pages += len(doc)
            doc.close()
            
        self.assertEqual(total_extracted_pages, 522)

if __name__ == "__main__":
    unittest.main()
```

Run: `python3 -m unittest tests/test_generated_files.py -v`  
Expected: `Ran 1 test in ... OK`

- [ ] **Step 2: .gitignore 업데이트**

`.gitignore`에 `교과서/장별/` 및 `__pycache__/`를 추가하여 대용량 분할 파일이 git 인덱스를 어지럽히지 않도록 방지.

```gitignore
교과서/장별/
__pycache__/
*.pyc
```

- [ ] **Step 3: README.md 업데이트**

`README.md`에 `교과서/장별/` 디렉토리 설명 및 1장~19장/부록 매핑 표를 추가한다.

- [ ] **Step 4: 테스트 및 스크립트, 문서 커밋**

```bash
GIT_CONFIG_GLOBAL=/dev/null git add .gitignore README.md tests/test_generated_files.py
GIT_CONFIG_GLOBAL=/dev/null git commit -m "docs: document split textbook chapters and add verification test"
```

---

## Verification Plan

### Automated Tests
- `python3 -m unittest tests/test_split_textbook.py -v`: 메타데이터 522쪽 연속성/배타성 및 분할 모의 테스트
- `python3 -m unittest tests/test_generated_files.py -v`: 분할 생성된 23개 PDF 파일 전수의 페이지 수, 존재 여부, 파싱 가능성 실시간 전수 검증

### Manual Verification
- 분할된 `교과서/장별/` 디렉토리 내 각 장의 첫 페이지와 마지막 페이지가 교재의 장 시작/종료와 정확히 일치하는지 확인
