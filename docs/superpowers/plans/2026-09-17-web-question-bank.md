# Web Question Bank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 1장 웹과제 17문항과 SVG 4개를 검증 가능한 원본으로 저장하고 앞으로 생성하는 정리노트/ELI5에 연결한다.

**Architecture:** JSON은 원문·관찰·분석을 분리한 편집 원본이고 SVG는 문제용/해설용으로 나눈다. 생성 시 HTML에 삽입하여 오프라인 단일 파일 사용을 유지한다. 기존 문제 형식을 보존하는 어댑터와 source-bound scope v2를 추가하고 기존 scope v1은 변경 없이 지원한다.

**Tech Stack:** Python 3.10+, unittest, jsonschema>=4.18,<5, HTML/CSS/JavaScript, XML ElementTree, SVG. 이미지 원본은 PNG이며 그림 재작성은 SVG 코드로 한다.

**Spec:** `docs/superpowers/specs/2026-09-17-web-question-bank-design.md` — 실행자는 이 설계와 계획을 모두 읽는다. 문항 내용 근거는 `docs/2026-09-17-1장-웹과제-분석과-노트-개선안.md`이며 전사는 raw 화면으로 다시 확인한다.

## Global Constraints

- 원본 스크린샷은 변경하지 않는다. Q1–Q17, 82보기, Q6의 a–d 조건문과 원문 순서를 보존한다.
- 문제용 SVG 2개와 해설용 SVG 2개를 웹과제/1장/image에 저장한다.
- 캡처 선택, 공식 답, 분석 답을 별도 저장한다. 현재 공식 답은 null이며 캡처는 pre_submission이다.
- 문제용 그림·대체 설명·파일명에 원문에 없던 정답 힌트를 넣지 않는다.
- JSON과 SVG는 편집 원본이며 HTML에는 생성 시 삽입한다. 브라우저 외부 요청·CDN은 사용하지 않는다.
- 기존 회차 MD/HTML/ELI5를 재생성하거나 본문 수정하지 않는다. 새로운 생성부터 적용한다.
- 기존 1강:18 형식의 ID와 q1-18 형식 링크, 기존 scope v1 검증은 유지한다.
- 회차 본문은 실제 STT 진도를 따른다. 보충에는 실제 출처를 표시한다.
- 모든 보기의 선택 적합성·근거를 감사한다. 자동 검사는 의미 정확성이나 학습자의 이해를 증명하지 않는다.
- 새 웹과제는 같은 장의 직접 근거, 다른 장의 웹과제는 출제 형태의 참고로만 사용한다.
- 사용자의 기존 변경·미추적 파일을 포함하여 일괄 stage하거나 덮어쓰지 않는다. 커밋은 실행 작업별 명시 경로만 사용한다.
- 구현 언어는 Python 3.10 이상과 표준 HTML/CSS/JavaScript/SVG다. JSON Schema 검증 의존성은 jsonschema>=4.18,<5 하나다.

---

## 실행 전 상태와 명령 규칙

계획 작성 시 checkout에는 0903 STT의 삭제/다른 이름 파일, 0915 ELI5의 미추적 파일, 웹과제 raw, 앞선 분석 보고서가 있었다. 이것들은 이번 계획 작성으로 발생한 변경이 아니다. 실행 시 `git status --short`를 다시 확인하고 해당 자료를 보존한다.

모든 경로와 명령은 저장소 루트 기준이다. 현재 루트의 실제 Unicode 이름은 `pwd`로 확인한다. source 데이터가 미추적이므로 실행을 위한 worktree를 만들면 raw 19장을 명시적으로 복사하고 바이트 해시를 비교해야 한다. 별도 worktree는 실행 시 using-git-worktrees 절차로 결정하며 계획 작성 단계에서는 만들지 않는다.

단계는 2–5분의 한 행동으로 나눴다. 전사와 그림은 문항/그림 단위로 쪼갠다. 체크박스를 실행 증거 없이 체크하지 않는다. 커밋 명령은 실행 단계용이며 이 계획 저장 요청이 구현·push·merge 승인은 아니다.

## 파일 책임과 인터페이스

| 파일 | 책임 |
|---|---|
| `웹과제/question-bank.schema.json` | 설계의 v1 JSON Schema; 구조 규칙의 유일 원천 |
| `requirements-question-bank.txt` | Python 검증기 의존성 한 줄 |
| `scripts/question_bank/__init__.py` | package marker |
| `scripts/question_bank/model.py` | load, schema/관계 검증, 원본/검토 해시 |
| `scripts/question_bank/svg.py` | SVG allowlist 검증, 내부 ID 재명명 |
| `scripts/question_bank/render.py` | preview 및 SVG template 생성 |
| `scripts/question_bank/note.py` | bank→기존 QUIZ 호환 데이터/HTML 생성 |
| `scripts/question_bank/scope.py` | web-scope 입력 검증·전체 문항 분류 |
| `scripts/question_bank/guide.py` | WEB_BINDINGS와 bank→ELI5 Q 데이터 변환 |
| `scripts/question_bank/__main__.py` | validate/preview/note CLI |
| `tests/question_bank_fixture.py` | 실제 원문과 구별된 테스트 전용 입력 |
| `tests/test_question_bank_model.py` | 잘못된 스키마·참조·검토/파일 변경 검출 |
| `tests/test_question_bank_svg.py` | SVG 의미 표지/임베딩 계약 |
| `tests/test_question_bank_ch1.py` | 실제 17문항/19스크린샷/82보기 회귀 |
| `tests/test_question_bank_render.py` | 정답 비노출·문자 escape·미리보기 |
| `tests/test_question_bank_note.py` | 보기 ID→인덱스 변환·노트 렌더 |
| `tests/test_question_bank_scope.py` | 명세 누락·중복·혼합 scope/해시 |
| `tests/test_question_bank_guide.py` | bank→가이드/기존 ID 호환 |
| `tests/test_summary_note_entrypoint.py` | 공유 스킬 진입점 연결 |
| `웹과제/1장/questions.json`, `image/*.svg`, `preview.html` | 실제 자료 원본과 검토용 결과 |
| `정리노트/_template.html`, `scripts/new_note_test.py` | 신규 웹문항 선택 확장; 과거 산출물 보존 |
| `.agents/skills/study-note-eli5/scripts/{question_scope,build_question_scope,build_guide,guide_kit,verify_guide}.py` | scope v2/웹 provenance/그림 연결 |
| `정리노트/CLAUDE.md`, summary-note 2개 진입점, ELI5 SKILL/coverage-contract | 내용 규칙·생성 절차·데이터 계약 동기화 |
| `docs/superpowers/reviews/2026-09-17-web-question-bank.md` | 실제 수행한 검증 증거와 한계 |

공통 공개 API (모든 경로 인수는 pathlib.Path, 아래는 실행 코드가 아닌 시그니처 표):

```text
# model.py
def canonical_digest(value: object) -> str
def resolve_local(base: Path, relative: str) -> Path
def question_payload(bank: dict, question: dict, base: Path, *, repo_root: Path | None = None) -> dict
def asset_payload(bank: dict, asset: dict, base: Path) -> dict
def validate_bank(bank: dict, base: Path, *, complete: bool = False, repo_root: Path | None = None) -> list[str]
def load_bank(path: Path, *, complete: bool = False, repo_root: Path | None = None) -> dict

# svg.py
def validate_svg(text: str) -> list[str]
def inline_svg(text: str, prefix: str, alt: str) -> str

# render.py
def figure_templates(bank: dict, base: Path) -> str
def render_preview(bank: dict, base: Path) -> str

# scope.py
def load_web_scope(path: Path, repo_root: Path) -> tuple[list[dict], dict[str, dict]]

# note.py
def export_note_items(bank: dict, entries: list[dict]) -> list[dict]
def render_note(template: str, meta: dict, items: list[dict], figures: str) -> str

# guide.py
def bank_to_guide(bank: dict, bindings: dict, base: Path, entries: list[dict]) -> tuple[list[dict], dict, str]
```

위 목록은 함수 시그니처 계약이다. 각 작업의 구현 단계에서 함수 본체를 작성한다.

load_bank는 오류를 ValueError로 전달한다. CLI는 이를 잡아 stderr에 출력하고 exit 1을 반환한다. 성공은 exit 0이다. validate/preview는 draft를 읽을 수 있고 note/guide는 complete 입력을 요구한다. 파일이 없으면 정확한 경로를 포함한 오류를 반환하며 자동 생성하지 않는다.

## Task 1: 문제 스키마와 검증 모델

**Files:** Create `requirements-question-bank.txt`, `웹과제/question-bank.schema.json`, `scripts/question_bank/__init__.py`, `scripts/question_bank/model.py`, `tests/question_bank_fixture.py`, `tests/test_question_bank_model.py`; Modify `.gitignore` (전용 venv 경로 한 줄만).

**Interfaces:** Consumes design v1 contract. Produces model API and fixture `make_bank(base: Path) -> tuple[Path, dict]`; fixture writes one raw file, evidence.md, questions.json and returns the path plus dict. Review starts pending.

- [ ] **Step 1: 실행 환경과 초기 테스트 상태 기록**

```bash
git status --short
python3 -m unittest discover -s tests -v
```

기존 실패는 테스트 이름과 출력을 기록하고 이번 수정 대상으로 자동 추가하지 않는다. 계획 작성 시 system/bundled Python 모두 jsonschema가 설치되지 않았다.

- [ ] **Step 2: 전용 실행 환경 준비**

requirements-question-bank.txt에 `jsonschema>=4.18,<5`, .gitignore에 `.venv-question-bank/`를 추가한다.

```bash
python3 -m venv .venv-question-bank
.venv-question-bank/bin/python -m pip install -r requirements-question-bank.txt
```

이후 명령에서는 전용 환경의 Python 경로를 직접 사용한다.

- [ ] **Step 3: 재사용할 최소 fixture 작성**

```python
import hashlib
import json
from pathlib import Path

def make_bank(base: Path) -> tuple[Path, dict]:
    (base / "raw").mkdir(parents=True, exist_ok=True)
    raw = base / "raw" / "fixture.txt"
    raw.write_text("fixture source: 1 question", encoding="utf-8")
    (base / "evidence.md").write_text("DNA는 유전 정보를 저장한다.", encoding="utf-8")
    bank = {
        "schema_version": 1,
        "assessment": {"id":"web-test-ch01", "title":"테스트 전용", "chapter":1,
            "date":"2026-09-17", "expected_question_count":1,
            "time_limit_seconds":None, "max_points":1, "evidence_source_ids":["s1"]},
        "sources":[{"id":"s1", "path":"raw/fixture.txt",
            "sha256":hashlib.sha256(raw.read_bytes()).hexdigest(), "width":1,"height":1}],
        "assets":[],
        "questions":[{
            "id":"web-test-ch01:q01", "number":1, "points":1, "source_ids":["s1"],
            "original":{"format":"single_choice", "content":[{"type":"text","text":"유전 정보 저장 물질은?"}],
                "options":[{"id":"A","text":"DNA"},{"id":"B","text":"지방"}]},
            "observations":{"phase":"pre_submission","selected_option_id":"B",
                "selected_source_id":"s1","official_answer":None},
            "analysis":{"answer_option_id":"A","answer_status":"reasoned","grading":"single",
                "also_accept":[],"reason":"DNA가 유전 정보를 저장한다.",
                "concept_ids":["dna"],"skills":["statement-evaluation"],
                "requirements":[{"id":"r1","statement":"DNA는 유전 정보를 저장한다.",
                    "evidence":[{"path":"evidence.md","locator":"1","quote":"DNA는 유전 정보를 저장한다."}]}],
                "option_diagnostics":{
                    "A":{"is_answer":True,"explanation":"유전 정보 저장에 해당한다.","requirement_ids":["r1"]},
                    "B":{"is_answer":False,"explanation":"지방은 이 질문의 답이 아니다.","requirement_ids":["r1"]}},
                "issues":[]},
            "review":{"status":"pending","payload_sha256":None,"notes":None}
        }]
    }
    path = base / "questions.json"
    path.write_text(json.dumps(bank, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return path, bank
```

fixture는 바이트 참조 검증용 텍스트를 사용한다. 실제 PNG 치수는 Task 3에서 별도로 확인하므로 이 fixture를 이미지 검토 증거로 쓰지 않는다. evidence 경로는 repo_root 기준이며 fixture에서는 base를 전달한다. validate_bank와 load_bank는 모두 선택 인수 repo_root를 지원하고 기본값은 저장소 루트다.

- [ ] **Step 4: 참조 관계 오류를 잡는 실패 테스트 작성**

```python
import copy
import tempfile
import unittest
from pathlib import Path
from question_bank_fixture import make_bank
from scripts.question_bank.model import validate_bank

class BankModelTests(unittest.TestCase):
    def test_selected_is_not_the_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            self.assertEqual(validate_bank(bank, base, repo_root=base), [])
            q = bank["questions"][0]
            self.assertEqual(q["observations"]["selected_option_id"], "B")
            self.assertEqual(q["analysis"]["answer_option_id"], "A")
            bad = copy.deepcopy(bank)
            bad["questions"][0]["analysis"]["answer_option_id"] = "Z"
            self.assertTrue(validate_bank(bad, base, repo_root=base))

    def test_missing_diagnostic_and_changed_source_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            del bank["questions"][0]["analysis"]["option_diagnostics"]["B"]
            self.assertTrue(validate_bank(bank, base, repo_root=base))
            (base / "raw/fixture.txt").write_text("changed", encoding="utf-8")
            self.assertTrue(any("hash" in e for e in validate_bank(bank, base, repo_root=base)))
```

Run `.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_model.py' -v`; Expected missing module/function failure.

- [ ] **Step 5: 스키마와 모델 구현**

Draft 2020-12 스키마에 설계의 객체를 $defs로 정의한다. additionalProperties:false, 필수 키, content oneOf, enum/null 제약을 적용한다. ID 사이의 참조는 Python에서 검증한다. 아래는 스키마 읽기와 공통 함수의 구현 핵심이다.

```python
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "웹과제/question-bank.schema.json"

def canonical_digest(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def resolve_local(base: Path, relative: str) -> Path:
    if Path(relative).is_absolute():
        raise ValueError("absolute path not allowed: " + relative)
    result = (base / relative).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError("path outside root: " + relative)
    return result

def schema_errors(bank: dict) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    return ["/" + "/".join(map(str, e.absolute_path)) + ": " + e.message
            for e in sorted(validator.iter_errors(bank), key=lambda e: str(e.absolute_path))]
```

검증 순서는 스키마 오류 즉시 반환 → source/id/number 중복 → 1부터 expected까지의 집합 → assessment/source 참조 → 실제 source 해시 → asset 경로/실제 해시 → 문항의 source/figure/option/diagnostic/requirement 참조 → evidence 파일 → review다. raw와 image는 bank 디렉터리 밖을 참조하지 못한다. evidence는 repo_root 기준이다. selected_source_id는 해당 question.source_ids에 있어야 한다.

question_payload와 asset_payload는 설계에 명시한 의존 파일의 바이트를 다시 읽어 dict를 반환한다. question_payload의 evidence 파일은 repo_root 기준으로 읽으며 validate_bank가 같은 repo_root를 전달한다. 저장된 해시만 신뢰하지 않는다. verified 해시 불일치는 draft에서도 오류다. complete에서는 pending/needs_review도 오류다. load_bank는 JSONDecodeError/OSError를 경로가 포함된 ValueError로 변환하며 입력을 수정하지 않는다.

- [ ] **Step 6: 추가 반례와 통과 확인**

같은 테스트 파일에 미지원 스키마, 중복 qid/source, 문항 누락, source 누락, 미등록 figure, 경로 이탈, selected_source 불일치, unresolved 상태, 검토 해시 불일치 반례를 추가한다. 테스트 형태는 다음과 같다.

```python
def test_unknown_version(self):
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        _, bank = make_bank(base)
        bank["schema_version"] = 2
        self.assertTrue(validate_bank(bank, base, repo_root=base))
```

Run `.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_model.py' -v`; Expected all PASS.

- [ ] **Step 7: 해당 작업 파일만 커밋**

```bash
git add requirements-question-bank.txt .gitignore 웹과제/question-bank.schema.json scripts/question_bank/__init__.py scripts/question_bank/model.py tests/question_bank_fixture.py tests/test_question_bank_model.py
git commit -m "feat: define verified web question bank contract"
```

## Task 2: SVG 검증과 실제 문제용·해설용 그림 4개

**Files:** Modify `scripts/question_bank/model.py` (asset SVG 검증 연결); Create `scripts/question_bank/svg.py`, `tests/test_question_bank_svg.py`, `웹과제/1장/image/q09.svg`, `q09.explained.svg`, `q14.svg`, `q14.explained.svg`.

**Interfaces:** Consumes original screenshots and model.resolve_local. Produces validate_svg/inline_svg and four SVG artifacts. Prefixing must not change chemistry or text.

- [ ] **Step 1: 실패 테스트 작성**

```python
import unittest
from scripts.question_bank.svg import validate_svg, inline_svg

class SvgTests(unittest.TestCase):
    def test_external_and_script_content_rejected(self):
        self.assertTrue(validate_svg('<svg viewBox="0 0 10 10"><script>alert(1)</script></svg>'))
        self.assertTrue(validate_svg('<svg viewBox="0 0 10 10"><image href="x.png"/></svg>'))

    def test_internal_label_ids_are_prefixed(self):
        text = '<svg viewBox="0 0 10 10" aria-labelledby="title"><title id="title">분자 구조</title></svg>'
        result = inline_svg(text, "q09-exam", "분자 구조")
        self.assertIn('id="q09-exam-title"', result)
        self.assertIn('aria-labelledby="q09-exam-title"', result)
```

Run `.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_svg.py' -v`; Expected import failure.

- [ ] **Step 2: XML allowlist 구현**

```python
import xml.etree.ElementTree as ET

TAGS = {"svg","g","path","line","polyline","polygon","circle","ellipse","rect","text","tspan","title","desc"}
ATTRS = {"id","viewBox","xmlns","role","aria-label","aria-labelledby","x","y","x1","y1","x2","y2",
         "cx","cy","r","rx","ry","width","height","d","points","dx","dy","fill","fill-opacity",
         "stroke","stroke-width","stroke-linecap","stroke-linejoin","stroke-dasharray","stroke-opacity",
         "font-size","font-family","font-weight","text-anchor","dominant-baseline","baseline-shift","transform","opacity"}

def validate_svg(text: str) -> list[str]:
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        return ["SVG declarations forbidden"]
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        return ["invalid SVG: " + str(error)]
    errors = []
    if root.tag.rsplit("}", 1)[-1] != "svg" or "viewBox" not in root.attrib:
        errors.append("SVG root/viewBox required")
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] not in TAGS:
            errors.append("forbidden SVG tag: " + node.tag)
        for key, value in node.attrib.items():
            if key not in ATTRS or "url(" in value.lower():
                errors.append("forbidden SVG attribute: " + key)
    return errors
```

inline_svg는 validate_svg를 먼저 호출하고 실패하면 ValueError를 발생시킨다. ElementTree namespace를 등록하고 모든 id와 aria-labelledby 토큰을 같은 prefix로 변환한다. prefix는 assessment.id, asset.id, exam/explained를 하이픈으로 연결한다. root의 role=img, aria-label=alt를 설정해 직렬화한다. 원본 id 중복, 미등록 참조, 잘못된 viewBox(유한수 4개, 폭·높이 양수)를 추가로 거부한다.

- [ ] **Step 3: Q9 문제용 그림 재작성**

raw 12.11.48을 읽는다. 왼쪽 중심 C에는 H3N+, COO−, H, CH3가 연결되고 오른쪽 같은 중심 골격에는 CH2–CH2–S–CH3가 연결된다. 원본의 좌우·결합 순서·전하·음영을 보존한다. 문제용 title/alt는 두 분자의 구조식으로 쓰고 아미노산이나 정답 C를 넣지 않는다. SVG 기본 형식은 아래와 같다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" role="img" aria-label="두 분자의 구조식">
  <title>두 분자의 구조식</title>
  <g fill="#172033" stroke="none" font-family="Arial, sans-serif" font-size="26">
    <text x="180" y="220">C</text>
  </g>
</svg>
```

위 root/text 스타일에 원본의 각 원자를 text/tspan, 결합을 line/path로 추가한다. 첨자와 전하는 별도 tspan으로 표현하고 desc에는 원문의 구조 정보를 읽는 순서로 기록한다. 완성 후 model.validate_bank의 asset 검사에 validate_svg를 연결한다.

- [ ] **Step 4: Q9해설 그림**

문제용 구조를 유지하면서 공통 골격·아미노기·카복실기·R기·아미노산→단백질 설명을 추가한다. 전하를 중성형으로 바꾸지 않는다.

- [ ] **Step 5: Q14문제 그림**

raw 12.12.32/12.12.35를 함께 읽는다. 콜린–인산–글리세롤, 지방산 두 개, 한쪽의 이중결합과 꺾임, 원본의 친수성·소수성 표지를 유지한다. 원본에 없던 정답 표시나 판별 화살표는 넣지 않는다.

- [ ] **Step 6: Q14해설 그림**

같은 구조에 친수성 머리·소수성 꼬리와 항상 포화지방산인 것은 아니라는 설명을 추가한다. 라벨이 결합이나 꼬리를 가리지 않도록 배치한다.

- [ ] **Step 7: 원본 비교·375px 화면 검토·테스트**

각 SVG를 열어 전하·결합·꼬리·잘림·문자를 확인한다. 네 파일 각각 validate_svg의 결과가 빈 배열인지 검사한다.

```python
from pathlib import Path
from scripts.question_bank.svg import validate_svg
for path in Path("웹과제/1장/image").glob("*.svg"):
    assert not validate_svg(path.read_text(encoding="utf-8")), path
```

SVG unittest를 다시 실행해 PASS를 확인한다. 실제 브라우저 뷰포트 375px을 사용하고 창 크기만 줄여 모바일 검증으로 보고하지 않는다.

- [ ] **Step 8: commit**

```bash
git add scripts/question_bank/model.py scripts/question_bank/svg.py tests/test_question_bank_svg.py 웹과제/1장/image/q09.svg 웹과제/1장/image/q09.explained.svg 웹과제/1장/image/q14.svg 웹과제/1장/image/q14.explained.svg
git commit -m "feat: reconstruct chapter one question figures"
```

## Task 3: 실제 17문항을 원본에서 등록

**Files:** Create `웹과제/1장/questions.json`, `tests/test_question_bank_ch1.py`; raw는 읽기 전용이다.

**Interfaces:** Consumes model APIs, four reviewed SVGs. Produces complete-valid bank, fixed source IDs s01–s19 ordered by filename timestamp.

- [ ] **Step 1: 실제 데이터에 대한 실패 테스트 작성**

```python
import unittest
import unicodedata
from pathlib import Path
from scripts.question_bank.model import load_bank

class ChapterOneTests(unittest.TestCase):
    def test_all_original_questions_and_options(self):
        folder = next(p for p in Path("웹과제").iterdir()
                      if unicodedata.normalize("NFC", p.name) == "1장")
        bank = load_bank(folder / "questions.json", complete=True)
        self.assertEqual(len(bank["sources"]), 19)
        self.assertEqual([q["number"] for q in bank["questions"]], list(range(1,18)))
        self.assertEqual(sum(len(q["original"]["options"]) for q in bank["questions"]), 82)
        self.assertEqual([q["number"] for q in bank["questions"]
                          if len(q["original"]["options"]) == 4], [6,12,15])
        self.assertTrue(all(q["observations"]["official_answer"] is None for q in bank["questions"]))
        self.assertEqual(len(bank["assets"]), 2)
```

Run `.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_ch1.py' -v`; Expected missing bank.

- [ ] **Step 2: source 목록과 시험 메타데이터 작성**

19장의 SHA256와 PNG IHDR 폭·높이를 읽는다. 순서는 mtime이 아니라 파일명 시각으로 정한다. s01–s19와 assessment의 화면 근거를 기록한다. 기존 폴더가 NFD이면 그대로 사용하고 같은 모양의 NFC 폴더를 따로 만들지 않는다.

```python
import hashlib
import struct
from pathlib import Path
sources = []
for i, path in enumerate(sorted(Path("웹과제/1장/raw").glob("*.png")), 1):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    sources.append(dict(id=f"s{i:02}", path="raw/"+path.name,
                        sha256=hashlib.sha256(data).hexdigest(), width=width, height=height))
```

- [ ] **Step 3: Q1 원문·선택·분석·보기 근거 입력**
- [ ] **Step 4: Q2 원문·선택·분석·보기 근거 입력**
- [ ] **Step 5: Q3 원문·선택·분석·보기 근거 입력**
- [ ] **Step 6: Q4 원문·선택·분석·보기 근거 입력**
- [ ] **Step 7: Q5 원문·선택·분석·보기 근거 입력**
- [ ] **Step 8: Q6 원문·선택·분석·보기 근거 입력; a–d statements 보존**
- [ ] **Step 9: Q7 원문·선택·분석·보기 근거 입력**
- [ ] **Step 10: Q8 원문·선택·분석·보기 근거 입력**
- [ ] **Step 11: Q9 원문·선택·분석·보기 근거 입력; s09/s10과 그림 연결**
- [ ] **Step 12: Q10 원문·선택·분석·보기 근거 입력**
- [ ] **Step 13: Q11 원문·선택·분석·보기 근거 입력**
- [ ] **Step 14: Q12 원문·선택·분석·보기 근거 입력**
- [ ] **Step 15: Q13 원문·선택·분석·보기 근거 입력**
- [ ] **Step 16: Q14 원문·선택·분석·보기 근거 입력; s15/s16과 그림 연결**
- [ ] **Step 17: Q15 원문·선택·분석·보기 근거 입력**
- [ ] **Step 18: Q16 원문·선택·분석·보기 근거 입력**
- [ ] **Step 19: Q17 원문·선택·분석·보기 근거 입력**

문항마다 original → observations → analysis → requirements/evidence → diagnostics 순서로 작성한다. 원문의 띄어쓰기·오기는 보존하고 해석은 issues에 쓴다. 분석 문서의 축약문을 original에 대신 넣지 않는다. 답은 선택 표시가 아니라 강의 자료에서 재확인한다.

앞선 분석의 검산값이며 공식 정답은 아니다.

```python
selected = ["A","A","B","B","E","B","B","D","D","E","E","C","D","B","C","B","E"]
reasoned = ["A","E","B","C","E","B","B","D","C","E","E","C","D","B","C","B","D"]
```

위 배열을 정답 추론의 근거로 쓰지 않는다. 차이가 생기면 원본과 근거를 확인해 issues에 설명한다. Q4와 Q16은 wording issue를 기록한다.

- [ ] **Step 20: 82개 보기와 그림 4개를 대조하고 검토 기록 작성**

확인한 대상과 항목을 review.notes에 구체적으로 적는다. payload_sha256는 실제 모델 함수로 계산한다. 검토를 마친 항목만 verified로 바꾼다. Q9/Q14 source_ids는 발문·그림·보기의 두 화면을 포함한다.

- [ ] **Step 21: complete 검증과 반례 확인**

ch1 unittest를 실행한다. 입력 복제본에서 Q17 삭제, Q9 그림 참조 누락, Q6 a–d 누락, 공식 답에 근거 없는 값 추가를 검사한다. Q6 진술 네 개는 1장 전용 검사이며 전체 스키마에 고정하지 않는다.

- [ ] **Step 22: 커밋 (raw는 목록에 있는 19개만 포함)**

```python
import json
import subprocess
from pathlib import Path
bank_path = next(Path("웹과제").glob("*/questions.json"))
bank = json.loads(bank_path.read_text(encoding="utf-8"))
paths = [str(bank_path), "tests/test_question_bank_ch1.py"]
paths += [str(bank_path.parent / s["path"]) for s in bank["sources"]]
subprocess.run(["git","add","--",*paths], check=True)
```

```bash
git diff --cached --stat
git commit -m "feat: archive chapter one web quiz with provenance"
```

## Task 4: 오프라인 원문 미리보기와 CLI

**Files:** Create `scripts/question_bank/render.py`, `scripts/question_bank/__main__.py`, `tests/test_question_bank_render.py`; Generate `웹과제/1장/preview.html`.

**Interfaces:** Consumes load_bank/inline_svg. Produces figure_templates/render_preview and CLI `python -m scripts.question_bank validate BANK [--complete]`, `preview BANK --output FILE`.

- [ ] **Step 1: 미리보기 실패 테스트 작성**

```python
import tempfile
import unittest
from pathlib import Path
from question_bank_fixture import make_bank
from scripts.question_bank.render import render_preview

class PreviewTests(unittest.TestCase):
    def test_original_order_and_observation_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            html = render_preview(bank, base)
            self.assertIn('data-question-id="web-test-ch01:q01"', html)
            self.assertIn('data-role="observations"', html)
            self.assertIn('data-role="solution"', html)
            self.assertNotIn("fetch(", html)
            self.assertNotIn('checked', html)
```

Run render unittest; Expected import failure.

- [ ] **Step 2: 순수 렌더러 구현**

text/statements/options는 html.escape, figure는 검증된 SVG로 삽입한다. 각 article은 prompt/options 다음에 observations details와 solution details를 둔다. 질문·출처·주의점과 미검토 상태를 표시한다. 82개 진단은 solution 안에 둔다. 스크립트 없는 정적 HTML로 만들고 max-width:960px, SVG width:100%;height:auto를 적용한다.

```python
from html import escape

def render_options(options: list[dict]) -> str:
    return '<ol class="options">' + ''.join(
        '<li data-option-id="'+escape(o["id"], quote=True)+'"><b>'+escape(o["id"])
        +'</b> '+escape(o["text"])+ '</li>' for o in options) + '</ol>'
```

figure_templates는 figure-web-20260917-ch01-q09-exam 같은 출처 포함 ID의 template과 해설용 template을 반환한다. selected는 검토용 preview의 관찰 기록에서만 표시한다.

- [ ] **Step 3: argparse CLI 구현**

validate는 load_bank, preview는 load_bank → render_preview → write_text를 호출한다. 실패는 stderr와 exit 1, 잘못된 CLI 인수는 argparse의 exit 2다. preview도 깨진 스키마·참조는 거부한다. 기존 출력과 같으면 수정하지 않고, 다르면 --force가 없을 때 거부한다. 입력 파일을 출력으로 지정할 수 없다.

- [ ] **Step 4: 표시와 문자 escape 검증**

fixture의 text를 <img src=x onerror=alert(1)>로 바꿔 실행 요소가 아니라 이스케이프된 문자로 나타나는지 검사한다. HTMLParser로 관찰/해설이 details 아래에 있는지 확인한다.

```bash
.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_render.py' -v
.venv-question-bank/bin/python -m scripts.question_bank validate 웹과제/1장/questions.json --complete
.venv-question-bank/bin/python -m scripts.question_bank preview 웹과제/1장/questions.json --output 웹과제/1장/preview.html
```

브라우저에서 17문항·Q6·Q9·Q14와 닫힌 해설 상태를 확인한다. 375px에서 보기와 전하가 읽히는지 확인하고 원본 파일 링크도 연다.

- [ ] **Step 5: commit**

```bash
git add scripts/question_bank/render.py scripts/question_bank/__main__.py tests/test_question_bank_render.py 웹과제/1장/preview.html
git commit -m "feat: render source-faithful offline quiz preview"
```

## Task 5: 신규 노트의 QUIZ 출력과 template 확장

**Files:** Create `scripts/question_bank/note.py`, `tests/test_question_bank_note.py`; Modify `정리노트/_template.html:359–377,510–609`, `scripts/new_note_test.py:21,54–65,172–185`, CLI.

**Interfaces:** export_note_items(bank,entries) accepts entries `{id,status,reason,prerequisite,refs}` defined in Spec. It exports only included/review, and rejects unresolved or pending bank. render_note takes the existing template/meta and returns full HTML. CLI `note --scope SCOPE --meta META --output FILE` uses Task 6 load_web_scope; this command is wired in Task 6 after that API exists.

- [ ] **Step 1: 답 인덱스 변환과 선택 기록 비혼입 테스트**

```python
import tempfile
import unittest
from pathlib import Path
from question_bank_fixture import make_bank
from scripts.question_bank.model import canonical_digest, question_payload
from scripts.question_bank.note import export_note_items

class NoteExportTests(unittest.TestCase):
    def test_option_id_conversion_does_not_use_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            q = bank["questions"][0]
            q["review"] = {"status":"verified", "notes":"synthetic fixture only",
                "payload_sha256":canonical_digest(question_payload(bank,q,base,repo_root=base))}
            entries = [{"id":q["id"],"status":"included","reason":"이번 범위",
                "prerequisite":None,"refs":[{"path":"evidence.md","section":"DNA"}]}]
            result = export_note_items(bank, entries)[0]
            self.assertEqual(result["answer"], 0)
            self.assertEqual(result["qid"], q["id"])
            self.assertNotIn("observations", result)
            self.assertEqual(len(result["diagnostics"]), 2)
```

Run note unittest; Expected import failure.

- [ ] **Step 2: 구조 변환 구현**

보기 배열 순서에서 답 인덱스를 계산한다. src=assessment.id, qid=전체 ID, q=첫 text, content=원문 블록, opts=보기 문장 배열, why=reason, diagnostics=전체 진단, trap=오답 진단, keyNote=주의점과 미공식 설명, ref=첫 참조 절, refs=전체 참조다. 그림 ID는 출처 ID까지 포함해 충돌을 방지한다. 관찰 기록은 내보내지 않는다. export_note_items는 verified 상태를 검사하며 CLI가 앞서 complete 검증한 bank를 전달한다. 기존 문항과 합칠 때 qid로 비교하고 번호만으로 제거하지 않는다.

```python
def script_json(value: object) -> str:
    import json
    text = json.dumps(value, ensure_ascii=False)
    for old, new in [("&", "\\u0026"),("<", "\\u003c"),(">", "\\u003e"),
                     ("\u2028", "\\u2028"),("\u2029", "\\u2029")]:
        text = text.replace(old,new)
    return text
```

기존 script 내부의 META/QUIZ 선언 앞뒤에 `/* QUESTION-DATA-START */`와 `/* QUESTION-DATA-END */` JavaScript 주석을 한 쌍 추가한다. render_note는 정확히 한 쌍인지 확인해 그 부분만 바꾼다. script_json으로 직렬화한 값을 const META와 const QUIZ 선언으로 출력한다. SVG template은 body 끝에 삽입한다. refs의 repo 경로를 링크로 변환하는 작업은 CLI가 수행해 render_note에 넘긴다. 정적 렌더 함수는 파일 시스템 위치를 추측하지 않는다.

- [ ] **Step 3: 기존 runtime의 선택적 확장**

buildCard는 content가 있으면 text/statements를 DOM으로 만들고 figure template을 clone한다. 레거시 항목은 기존 q를 표시한다. reveal은 diagnostics가 있으면 전체 설명을 쓰고 없으면 why/trap을 사용한다. 새로운 answerLabel은 분석 기준이며 결과 화면에도 공식 채점과 구별해 표시한다. refs는 생성 위치 기준의 실제 링크로 만들고 기존 ref 문자열 표시는 유지한다.

```javascript
function appendFigure(parent, id) {
  const template = document.getElementById("figure-" + id);
  if (!(template instanceof HTMLTemplateElement)) throw new Error("Missing figure: " + id);
  parent.append(template.content.cloneNode(true));
}
```

explainedFigureIds는 reveal 후 feedback에만 삽입한다. 캡처 선택을 초기 답으로 쓰지 않는다. intended 답과 also_accept를 정답 판정에 반영하고 해석상 주의점을 표시한다. note용 also_accept는 0-based다. isRight는 새 필드가 없는 기존 항목에서 기존 결과를 유지한다.

- [ ] **Step 4: 테스트 생성기 확장**

선택 인수 --web-scope PATH를 추가한다. 기존 --quiz 문법은 유지한다. 신규 문항은 원본 명세의 전체 qid와 HTML qid를 비교한다. 신규 MD 표는 출처/문항 ID/질문 요약/절/상태 열을 사용하고 기존 숫자 열은 바꾸지 않는다. new_note_test.render의 기존 매개변수 뒤에 web_scope=None을 추가하며 미지정 호출의 출력은 유지한다. 새 marker 블록에서는 JSONDecoder.raw_decode로 META/QUIZ 선언 값을 읽어 키와 문항 수를 검사한다. JSON의 따옴표 있는 키를 기존 n: 정규식으로 읽지 않는다. marker가 없는 과거 HTML은 기존 정규식 경로로 처리한다.

- [ ] **Step 5: PASS와 브라우저 동작 확인**

note unittest와 test_new_note_test.py를 실행한다. 임시 폴더의 Q9/Q14 HTML에서 미응답 상태의 해설 그림 비노출, 답 선택 뒤 전체 진단, 정오답 라벨, 기존 샘플 동작, console error 0을 확인한다. 기존 0903/0908 파일을 수정하지 않는다.

- [ ] **Step 6: commit**

```bash
git add scripts/question_bank/note.py tests/test_question_bank_note.py 정리노트/_template.html scripts/new_note_test.py tests/test_new_note_test.py
git commit -m "feat: embed question bank data in new study notes"
```

## Task 6: 원본에 연결된 web-scope와 혼합 scope v2

**Files:** Create `scripts/question_bank/scope.py`, `tests/test_question_bank_scope.py`; Modify ELI5 `question_scope.py:105–133`, `build_question_scope.py:23–57,main`, `verify_guide.py:134–186`, `scripts/new_note_test.py`, CLI.

**Interfaces:** load_web_scope returns `(entries, banks)` where entries are full manifest question dicts plus `bank_id`, banks maps assessment.id→loaded complete bank. Manifest.path base is manifest.parent, reference paths are repo_root. Add keyword-only `web_scope: Path | None = None` to existing build_lock; existing callers stay valid.

- [ ] **Step 1: 원본 문항을 명세에서 누락할 수 없는지 테스트**

```python
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from question_bank_fixture import make_bank
from scripts.question_bank.scope import load_web_scope

class WebScopeTests(unittest.TestCase):
    def test_manifest_cannot_drop_bank_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path, bank = make_bank(base)
            manifest = {"schema_version":1,"banks":[{"path":path.name,
                "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"questions":[]}]}
            target = base / "scope.json"
            target.write_text(json.dumps(manifest),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"question universe"):
                load_web_scope(target,base)
```

load_web_scope는 먼저 draft bank를 읽어 문항 집합을 대조한 뒤 complete 상태를 확인한다. 위 반례에서는 pending보다 question universe 오류가 먼저 나타난다.

- [ ] **Step 2: 명세 해석과 v2 기본 집합 구현**

```python
def assert_same_ids(expected: set[str], actual: list[str]) -> None:
    if len(actual) != len(set(actual)) or set(actual) != expected:
        missing, extra = expected-set(actual), set(actual)-expected
        raise ValueError(f"question universe mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
```

manifest의 ../bank 경로는 manifest.parent에서 해석한 뒤 repo_root 내부인지 확인한다. raw/image용 resolve_local(base)의 더 좁은 기준을 잘못 적용하지 않는다. bank 해시, 모든 ID의 분류, status/refs/reason/prerequisite를 검사하고 전체 ID를 base_questions에 합친다. 기존 노트에서 추출한 ID와 충돌하면 거부한다. bank 전체는 complete여야 한다. refs의 파일·절을 확인한다. 명세는 노트 생성 전에 만드는 입력이며 출력에서 역생성해 누락 문항 수를 줄이지 않는다.

v2에는 기존 note source 외에 web_scope의 경로/해시와 bank 경로/해시 배열을 저장한다. 저장 경로는 lock.parent 기준이다. 명세를 읽을 때의 bank 경로는 manifest.parent 기준으로 해석한다. scope_digest는 전체를 계산하며 v1 출력은 변경하지 않는다.

- [ ] **Step 3: 검증기와 CLI 연결**

build_question_scope에 --web-scope를 추가해 build_lock으로 전달한다. validate_scope_lock은 v2에서 명세와 bank를 다시 읽고 legacy 집합 + bank 전체 집합이 base_questions와 같은지 검사한다. 읽기/JSON 오류는 기존 FAIL 출력으로 처리하고 verify_guide 공개 시그니처는 유지한다.

note CLI와 new_note_test --web-scope를 연결한다. 최종 note CLI 문법은 note --scope SCOPE --meta META --output FILE이다. 명세에 포함된 모든 bank에서 items/templates를 모으며 일부만 출력하고 완전판이라고 표시하지 않는다. META JSON은 기존 template 키를 사용하고 date=MMDD, title=비어 있지 않은 문자열을 요구하며 나머지는 template 기본값을 사용한다.

- [ ] **Step 4: v1 회귀와 변조 테스트**

기존 test_study_guide_scope.py 전체를 실행한다. 추가 반례는 명세 ID 삭제·중복, 보류 이유 없음, 참조 절 없음, bank/raw 바이트 변경, 서로 다른 bank의 같은 번호다. 다른 출력 폴더로 다시 생성해 상대 경로가 올바른지도 확인한다. 사용자가 옮긴 파일을 추측으로 복구하지 않는다.

```bash
.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_scope.py' -v
.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_study_guide_scope.py' -v
```

- [ ] **Step 5: commit**

```bash
git add scripts/question_bank/scope.py scripts/question_bank/__main__.py scripts/new_note_test.py tests/test_question_bank_scope.py .agents/skills/study-note-eli5/scripts/question_scope.py .agents/skills/study-note-eli5/scripts/build_question_scope.py .agents/skills/study-note-eli5/scripts/verify_guide.py
git commit -m "feat: bind mixed question scopes to source banks"
```

## Task 7: ELI5에 원문·그림·근거 연결

**Files:** Create scripts/question_bank/guide.py, tests/test_question_bank_guide.py; Modify ELI5 guide_kit.py:20–33, build_guide.py:98–151,188–340, make_blind_copy.py의 필요한 해설 구분 처리.

**Interfaces:** bank_to_guide returns `(questions, deferred, figure_html)` in existing guide_kit.Q dictionary shape plus optional `content,source_evidence,locator,explained_figures`. Entries classify every bank qid; bindings exactly cover active qids, each requirement_facts entry maps to existing authored FACTS IDs. META.web_scope is relative to guide.py; load_web_scope path is resolved once before passing build_lock. WEB_BINDINGS contains all active bank requirements; manuscript original facts still live in FACTS/SECTIONS.

- [ ] **Step 1: 기존 링크와 새 링크의 충돌 테스트**

```python
import unittest
from study_guide_fixture import ROOT
from build_guide import qanchor

class GuideBankTests(unittest.TestCase):
    def test_web_and_legacy_anchors_are_distinct(self):
        self.assertEqual(qanchor("1강:18"), "q1-18")
        self.assertNotEqual(qanchor("web-20260917-ch01:q18"), qanchor("1강:18"))
        self.assertNotEqual(qanchor("web-20260917-ch01:q09"), qanchor("web-20260918-ch01:q09"))
```

Run guide unittest; Expected current qanchor fails on non-digit prefix.

- [ ] **Step 2: 링크와 Q 변환 구현**

```python
def qanchor(ident: str) -> str:
    import re
    match = re.fullmatch(r"(\d+)강:(\d+)", ident)
    if match:
        return f"q{match[1]}-{match[2]}"
    return "qweb-" + ident.encode("utf-8").hex()
```

bank_to_guide는 보기 ID를 1-based로 변환한다. 공식 답이 없으면 key=None이며 analysis에서 ans/grading/also_accept/diag/reason/conflict를 가져온다. content 순서를 유지하고 statements도 표시한다. 모든 requirement에 binding이 있고 fact ID가 실제 FACTS에 존재하는지 검사한다. 각 requirement의 fact 배열을 합쳐 Q.reqs로 전달한다. observations는 출력하지 않는다.

source_evidence는 bank 경로, 스크린샷/문항 locator, 원문의 첫 text를 기록한다. 웹 문항은 화면에 locator를 사용하고 PDF p 접두사를 강제로 붙이지 않는다. 기존 PDF 표시는 유지한다. scope audit의 page 필드는 호환성을 위해 비어 있지 않은 locator 문자열로 쓰고 원문 전체는 content에 보존한다.

- [ ] **Step 3: build_guide 합류와 파일 해시 의존성**

META.web_scope가 있을 때만 명세를 읽고 각 bank에 해당하는 entries를 bank_to_guide의 네 번째 인수로 전달한다. 함수는 entries의 deferred를 reason/prerequisite와 함께 기존 DEFERRED 형식으로 바꾼다. bank_to_guide 결과를 기존 QUESTIONS/DEFERRED와 합친다. 원래 module 객체는 변형하지 않으며 중복은 오류다. 문제 그림은 prompt, 해설 그림은 solution 안에 삽입한다. inventory.sources에는 명세/bank/raw/두 SVG의 실제 해시를 등록한다. META.quiz_sources에는 bank 출처를 추가한다. build_lock 호출에 web_scope=resolved_path를 전달한다.

active_card는 웹 항목의 content를 렌더링하고 기존 Q는 기존 방식을 유지한다. 그림 id와 Q.fig를 연결해 diagram-required 검사를 유지한다. requirements/fact_targets와 보이는 학습 본문의 연결 검사를 약화하지 않는다.

- [ ] **Step 4: 통합 fixture와 해설 없는 사본 테스트**


다음 단위 통합 테스트로 원문 ID·정답 인덱스·요구 fact 변환을 우선 검증한다.

```python
import tempfile
from pathlib import Path
from question_bank_fixture import make_bank
from scripts.question_bank.model import canonical_digest, question_payload
from scripts.question_bank.guide import bank_to_guide

def test_bank_to_guide_preserves_identity_and_maps_requirements():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        _, bank = make_bank(base)
        q = bank["questions"][0]
        q["review"] = {"status":"verified","notes":"synthetic fixture only",
            "payload_sha256":canonical_digest(question_payload(bank,q,base,repo_root=base))}
        entries = [{"id":q["id"],"status":"included","reason":"이번 범위",
            "prerequisite":None,"refs":[{"path":"evidence.md","section":"DNA"}]}]
        bindings = {q["id"]:{"group":"dna","status":"included",
            "requirement_facts":{"r1":["fact-dna"]}}}
        questions, deferred, figure_html = bank_to_guide(bank,bindings,base,entries)
        assert questions[0]["id"] == q["id"]
        assert questions[0]["ans"] == 1
        assert questions[0]["key"] is None
        assert questions[0]["reqs"] == ["fact-dna"]
        assert deferred == {}
        assert figure_html == ""
```

이 함수를 unittest.TestCase의 메서드로 넣어 discover가 실제 실행하게 한다.

기존 BuildGuideTests의 NOTE/GUIDE fixture를 가져와 tmp에 만든다. 웹 fixture r1을 새 DNA fact에 연결하고 MD 사실 행, block, T 표시를 추가한다. 질문 해설에만 있는 문장은 학습 본문 근거로 인정하지 않는지도 검사한다.

추가 반례는 requirement binding 누락, 없는 fact ID, 문제 그림 누락, 해설 그림의 prompt 혼입, raw 변경 후 검토 해시 불일치다. HTMLParser로 blind copy에서 관찰·답·진단·해설 그림이 빠지고 문제 그림은 남는지 검사한다.

```bash
.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_question_bank_guide.py' -v
.venv-question-bank/bin/python -m unittest discover -s tests -p 'test_study_guide_*.py' -v
```

임시 폴더에서 웹+기존 문항 혼합 가이드를 draft 검증한다. 이를 complete 가이드로 보고하지 않는다. 이번은 생성 과정 연결 작업이므로 기존 노트 전체를 재생성하지 않는다.

- [ ] **Step 5: commit**

```bash
git add scripts/question_bank/guide.py tests/test_question_bank_guide.py .agents/skills/study-note-eli5/scripts/guide_kit.py .agents/skills/study-note-eli5/scripts/build_guide.py .agents/skills/study-note-eli5/scripts/make_blind_copy.py
git commit -m "feat: integrate verified web questions into study guides"
```

## Task 8: 스킬 업데이트와 새로운 생성 절차 검증

**Files:** Modify `정리노트/CLAUDE.md:23–43,49–91,114–148`, `.agents/skills/summary-note/SKILL.md`, `.claude/skills/summary-note/SKILL.md`, `.agents/skills/study-note-eli5/SKILL.md`, `.agents/skills/study-note-eli5/references/coverage-contract.md`; Create `tests/test_summary_note_entrypoint.py`, `docs/superpowers/reviews/2026-09-17-web-question-bank.md`.

**Interfaces:** Consumes bank/CLI/scope/guide APIs. Produces one canonical summary-note instruction flow and review report. Execute skill-creator/writing-great-skills guidance during this task; user has requested actual skill update at execution, not during planning.

- [ ] **Step 1: 스킬 복사본 불일치를 막는 테스트**

```python
import unittest
from pathlib import Path

class SummaryEntrypointTests(unittest.TestCase):
    def test_claude_delegates_to_canonical_skill(self):
        path = Path(".claude/skills/summary-note/SKILL.md")
        text = path.read_text(encoding="utf-8")
        target = "../../../.agents/skills/summary-note/SKILL.md"
        self.assertIn(target,text)
        self.assertTrue((path.parent/target).resolve().is_file())
        self.assertNotIn("## 3. 문항 감사",text)
```

Run entrypoint test; Expected FAIL for currently duplicated full skill.

- [ ] **Step 2: 규칙 문서 개정**

CLAUDE.md의 내용은 다음 문장을 기준으로 고친다.

> 문제 JSON은 원문·관찰 기록·분석의 유일 원천이고, 퀴즈 HTML은 생성 결과입니다. MD에는 정답과 보기별 해설을 넣지 않습니다. JSON과 SVG는 생성할 때 HTML 내부에 삽입하며 브라우저에서 외부 파일을 가져오지 않습니다.
>
> 모든 보기의 선택 적합성과 근거를 확인합니다. 필요한 사실이 해설에만 있으면 본문이나 출처가 표시된 보충에서 먼저 가르칩니다. 그림 판독 문항은 정답을 열기 전의 그림과 설명으로 풀 수 있어야 합니다.
>
> 30초 요약에도 성립 조건과 분류 경계를 유지합니다. 기능 경로에 참여하는 것을 그 계의 구성원으로 표시하지 않습니다. 쉬운 설명에도 시험 판별에 필요한 원래 용어를 남깁니다.
>
> STT에 없는 보충은 실제 출처에 따라 강의노트·교재·외부 참고로 구분합니다. 강의에서 생략했다는 사실을 시험 제외로 바꾸지 않습니다.

레거시 HTML-only 퀴즈는 현상 유지한다는 호환 예외를 명시한다. 신규 원본/engine/src/source graph만 업데이트한다. git 허용 목록에 명시적 이번 `웹과제/` bank/SVG/source와 `.agents/`를 추가하되 zip 금지와 광범위 add 금지를 유지한다.

- [ ] **Step 3: summary-note의 실제 절차 수정**

입력에 동일 장 questions.json 발견 및 `validate --complete`를 추가한다. 미검토 자료가 있으면 누락처럼 무시하지 않고 구체적 필드/source를 보고하여 검토 후 진행한다. 해당 장 자료가 없으면 기존 PDF 절차로 간다. 기존 범위 게이트 표에 `출처 ID / 판정 답의 종류 / 전체 보기 감사 / 그림 / 필요한 보충`을 추가한다.

고정 8개 함정 기준은 제거한다. 핵심 혼동 묶음마다 1–2개 생성 변형을 제안하고 실제 출제와 구별한다. 생성 문항은 별도 회상/변형 영역에 놓고 bank 원문 집합을 늘리거나 줄이지 않는다. 1장의 분류/그림 패턴을 2장에 적용할 때 내용 근거는 2장 STT/강의노트에서 찾는다.

장 종료 시 ①회차별 해당 절 ②필수 그림/용어 ③남은 보류 및 사유 ④시험 범위 확인/불명 ⑤비교/변형 풀이 점검 결과를 보고한다. 이번 구현에는 새 장 요약 artifact 자동 생성은 넣지 않는다. 기존 승인 범위에 이미 포함된 행동에는 다시 허가를 요구하지 않는다.

- [ ] **Step 4: 얇은 진입점과 ELI5 문서**

`.claude/skills/summary-note/SKILL.md`는 frontmatter를 유지한 뒤 다음 본문으로 바꾼다.

```markdown
# Summary Note

Read and follow [the canonical skill](../../../.agents/skills/summary-note/SKILL.md).
Resolve relative paths from the canonical skill directory. Do not maintain a second procedure here.
Content rules remain in the repository's 정리노트/CLAUDE.md.
```

ELI5 SKILL/coverage-contract에 META.web_scope, WEB_BINDINGS, scope v2의 원본 검증과 기존 v1 fallback, exam/explained 분리를 설명한다. web `page`는 locator compatibility field이며 실제 PDF쪽수가 아님을 설명한다. complete는 기존 blind/source/reverse/visual gates 모두 유지한다.

- [ ] **Step 5: 동작 드라이런**

읽기·tmp 출력만으로 아래 두 경우를 실행한다.

1. 1장: 실제 bank를 읽고 Q2/Q4/Q9/Q17의 필요 근거와 참조 절, 그림의 포함 위치를 제안한다. 해설에만 있는 지식을 본문으로 세지 않는다. 기존 0903/0908을 덮어쓰지 않는다.
2. 2장: 실제 2장 web bank가 없음을 확인하고 STT/강의노트+과거 PDF 경로로 진행한다. 1장 원문을 2장 문항 집합에 넣지 않고 분류 경계/조건 변경/그림 판독이라는 형태만 활용한다.

드라이런 보고에 input paths, chosen scope, excluded/deferred reasons, pending issues, executed commands와 실제 결과를 기록한다. 리뷰를 하지 않은 항목에 pass를 채우지 않는다.

- [ ] **Step 6: 전체 회귀 및 출처별 보고**

```bash
.venv-question-bank/bin/python -m unittest discover -s tests -v
.venv-question-bank/bin/python -m scripts.question_bank validate 웹과제/1장/questions.json --complete
git diff --check
git status --short
```

전체 테스트의 초기 실패와 새 실패를 구분한다. 새로운 실패는 해결하고, 기존 실패가 이번 변경에 영향 없는지 근거를 남긴다. 실제 브라우저 검증/의미 검토/자동 검증은 별도 항목으로 보고한다.

- [ ] **Step 7: 마지막 commit과 인계**

```bash
git add 정리노트/CLAUDE.md .agents/skills/summary-note/SKILL.md .claude/skills/summary-note/SKILL.md .agents/skills/study-note-eli5/SKILL.md .agents/skills/study-note-eli5/references/coverage-contract.md tests/test_summary_note_entrypoint.py docs/superpowers/reviews/2026-09-17-web-question-bank.md
git commit -m "feat: teach future notes from verified web quiz evidence"
```

최종 응답은 bank/preview/그림4개/스킬 변경을 링크하고 17문항·82보기·공식답 미확보를 명시한다. 기존 노트가 바뀌지 않은 사실을 검증한 뒤 보고한다. push/merge는 별도 사용자 요청이 있을 때 수행한다.

## Spec coverage/self-review map

| 설계 요구 | 구현/검증 작업 |
|---|---|
| 원문/관찰/분석 분리, ID, 82보기 | Task1,3,5 |
| 4 SVG와 문제용 정답 비노출 | Task2,4,5,7 |
| 원본·분석·그림 변경에 따른 stale 검토 | Task1,3,6,7 |
| 단일 HTML, escape, 실제 참조 링크 | Task4,5 |
| 기존 ID/scope/노트 보존 | Task5,6,7,8 |
| 독립 원본 집합에 따른 완전성 | Task1,3,6,7 |
| 실제 장 입력 없을 때 fallback | Task8 드라이런 |
| 모든 보기·혼동·변형·장 마감 | Task8 규칙/절차/드라이런 |
| 사용자 이해와 자동 검증 구별 | Task7 draft한계, Task8 보고 |

## 최종 인터페이스 정합성

- model.validate_bank/load_bank는 `repo_root: Path | None = None`를 지원한다. 기본 root는 저장소이며 fixture는 base를 넘긴다.
- scope.load_web_scope는 `(entries, banks)`를 반환한다. entries는 bank_id가 추가된 모든 문항 분류이며 banks는 assessment.id로 keyed된다.
- CLI 최종 문법: `validate BANK [--complete]`, `preview BANK --output FILE [--force]`, `note --scope SCOPE --meta META --output FILE [--force]`.
- note.export_note_items의 also_accept는 0-based, guide.Q의 also_accept는 1-based다. 원본 JSON은 항상 보기 문자 ID다.
- scope v2의 추가 경로는 lock.parent 기준, 원래 manifest의 bank 경로는 manifest.parent 기준, facts.evidence/refs는 repo_root 기준이다.
- 기존 노트는 어느 Task에서도 출력 대상으로 사용하지 않는다. smoke는 temp 디렉터리만 쓴다.
