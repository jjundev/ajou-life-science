# Study Note ELI5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 원본 사실과 문항의 누락을 추적하고, 이해·회상·문제 적용을 지원하는 생명과학 ELI5 생성 스킬을 만든다.

**Architecture:** 생성 전에 원본 구간·학습 사실·문항의 inventory를 확정하고, 생성 후 HTML 위치와 검토 근거를 coverage JSON에 기록한다. Python 표준 라이브러리 검증기는 원본/HTML/검토 기록의 정합성을 확인하고 의미 판단은 작성자의 근거 있는 대조 검토로 남긴다. HTML은 JSON을 불러오지 않는 독립 학습 자료다.

**Tech Stack:** 기존 Python 3, `unittest`, `hashlib`, `json`, `html.parser`, `pathlib`; UTF-8 HTML/CSS/inline SVG, 작은 vanilla JavaScript. 계획 작성 환경의 Python은 3.14.6이며 신규 패키지·빌드 시스템을 요구하지 않는다.

**Spec:** `docs/superpowers/specs/2026-09-10-study-note-eli5-design.md` — 실행자는 계획과 설계 모두 읽는다.

## Global Constraints

- 원본 전체 보존. 문제에 직접 나오지 않는 개념도 설명한다.
- 전체 길이 제한 없음. 카드와 분량을 늘려 조건·예외·수치·방향을 보존한다.
- UTF-8, 오프라인 단일 HTML, inline CSS/SVG. 외부 CDN·네트워크 요청·빌드 도구 없음.
- 정리노트 MD와 원본 퀴즈 HTML은 원천 자료이고 ELI5는 파생 학습 가이드다.
- 원본과 답지의 충돌은 조용히 고치지 않는다. 원문 주장·판단 근거·처리 결과를 표시한다.
- 범위 밖 내용은 설명·풀이로 당겨오지 않는다. 보류 사유와 필요한 후속 학습을 표시한다.
- 필수 사실은 개념 설명에 존재해야 한다. 정답 해설에만 있는 사실은 설명 완료로 세지 않는다.
- 중요한 조건은 기본 화면에 표시한다. 정답과 추가 예시는 접을 수 있으며 인쇄 시 펼친다.
- 문항 식별자는 출처와 번호를 묶는다. 생성 질문은 원본 문항과 구분한다.
- 원본과 생성물 변경 시 이전 검토 기록을 재사용하지 않는다.
- 일괄 재생성, 자동 알림, 학습 계정·성적 저장, 자유서술 자동 채점은 이번 범위 밖이다.

추가 실행 제약: 이번 요청은 계획 저장까지다. 코드·스킬·학습 HTML 변경과 커밋은 후속 실행 요청 이후 진행한다. 기존 dirty 변경을 보존하고 현재 staged 상태를 먼저 확인한다. 아래 커밋 단계는 명시적으로 커밋이 승인됐을 때만 수행한다. 승인 없으면 변경을 unstaged로 두고 해당 체크박스는 미실행으로 기록한다. `git add .`와 broad staging을 금지한다.

---

## 0. 현재 상태와 실행 전 확인

- 실제 스킬은 `.agents/skills/study-note-eli5/`에 있다. `.claude/skills/study-note-eli5/`는 존재하지 않는다. `SKILL.md:32`의 명령 경로를 고쳐야 한다.
- `scripts/verify_guide.py:24-44`는 HTML 문자열과 `.qnum`만 검사한다. 주 노트를 읽지 않고 원문 보존·의미 검토·외부 의존성을 검사하지 않는다.
- `assets/base-template.html:20`은 검증기가 기대하는 `.qnum`조차 제공하지 않는다. 신규 계약은 class 정규식 대신 `data-*`와 HTML 파서를 사용한다.
- `정리노트/CLAUDE.md:49-67`은 원천 MD/HTML 분업과 오프라인 제약을 정한다. 파생 ELI5의 예외·역할을 명시적으로 추가한다.
- `tests/test_note_0910.py:8`의 현재 본강 문항은 2강 30개다. 복습 문항과 보류 문항은 별도로 원문 대조한다. 이 값은 실행 시 재확인한다.
- 작업 폴더에는 `.agent/` 삭제, `.agents/` 미추적, 노트·퀴즈·테스트·CLAUDE 수정이 있다. 이를 스킬 정리나 계획 구현의 결과로 오인하지 않는다.

실행 시작 때 읽을 파일:

```bash
git status --short
git diff --cached --stat
git diff -- 정리노트/CLAUDE.md tests/test_note_0910.py
cat .agents/skills/study-note-eli5/SKILL.md
cat 정리노트/CLAUDE.md
python3 --version
python3 -m unittest discover -s tests -p 'test_note_*.py' -v
```

원천 노트 테스트의 초기 결과를 기록해 Task 6의 결과와 비교한다. 사용자가 실행 방식을 선택한 뒤에만 실행용 스킬을 적용한다. 격리 작업공간이 필요하면 `using-git-worktrees` 절차를 따른다. 현재 미커밋 자료가 기본 브랜치에 없을 수 있으므로 실제 스킬과 현재 0910 자료를 확인하지 못하는 worktree에서 오래된 자료로 진행하지 않는다.

## 1. 파일 구조와 책임

| 작업 | 파일 | 책임 |
|---|---|---|
| 1 | Create `.agents/skills/study-note-eli5/references/coverage-contract.md` | JSON·HTML·검토 상태의 단일 계약 |
| 1 | Create `.agents/skills/study-note-eli5/scripts/coverage_model.py` | inventory, 해시, 원본 범위·스키마 검증 |
| 1 | Create `tests/study_guide_fixture.py` | 외부 자료와 무관한 최소 검증 fixture |
| 1 | Create `tests/test_study_guide_model.py` | 원본·범위·스키마 실패 사례 |
| 2 | Create `.agents/skills/study-note-eli5/scripts/guide_html.py` | HTML 파싱, 사실·문항·회상 연결 검증 |
| 2 | Create `tests/test_study_guide_html.py` | DOM 연결·범위·보류 실패 사례 |
| 3 | Modify `.agents/skills/study-note-eli5/scripts/verify_guide.py:1-57` | CLI·오류 출력·기존 형식 구분·최종 검토 게이트 |
| 3 | Create `tests/test_study_guide_cli.py` | CLI 종료 코드와 stale review |
| 4 | Modify `.agents/skills/study-note-eli5/assets/base-template.html:1-25` | 실제 개념 예제, 회상·해설·복습·인쇄 동작 |
| 4 | Create `tests/test_study_guide_template.py` | 템플릿의 학습 흐름 연결 |
| 5 | Modify `.agents/skills/study-note-eli5/SKILL.md:10-38` | 작업 순서·실패 처리·완료 보고 |
| 5 | Modify `정리노트/CLAUDE.md:49-67,114-124` | 원천과 파생 가이드의 역할 |
| 6 | Create `정리노트/0910-eli5-audited.html` | 한 회차 실사용 파일; 기존 파일 보존 |
| 6 | Create `정리노트/0910-eli5-audited.coverage.json` | 해당 파일의 inventory·mapping·검토 근거 |
| 6 | Create `docs/superpowers/reviews/2026-09-10-study-note-eli5-pilot.md` | 의미·시각 검토와 실제 명령 결과 |

테스트는 기존 저장소처럼 `unittest`를 사용한다. `tests/test_note_MMDD.py`는 원천 노트 테스트이며 신규 파생 가이드 계약을 억지로 넣지 않는다.

## 2. 데이터 계약 — 작업 사이에 바꾸지 않을 인터페이스

### coverage JSON v1

최상위 필드: `schema_version: 1`, `inventory`, `inventory_sha256`, `mappings`, `review`.

`inventory`는 생성 전에 확정한다. 해시는 `json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")`의 SHA-256이다. 수정 시 이유를 `review.inventory_change_reason`에 남기고 review를 pending으로 되돌린다. 이것은 변경 감지이며 변조 방지 시스템이 아니다.

| 위치 | 필수 필드와 값 |
|---|---|
| inventory | `main_source`(source id), `sources`, `blocks`, `facts`, `concepts`, `questions`(모두 배열) |
| source | `id`, `path`(manifest 기준 상대 경로), `role`: `note/quiz/reference`, `sha256`, `read_status`: `read/unread/missing` |
| block | `id`, `start`, `end`(주 MD의 1-based inclusive 줄), `kind`: `teaching/review/supplement/boundary/metadata`, `fact_ids`, `reason` |
| fact | `id`, `block_id`, `statement`, `qualifiers`(문자열 배열), `concept_id`(boundary면 빈 문자열), `scope`: `teaching/review/supplement/deferred`, `evidence` |
| evidence | `source_id`, `locator`(절·문항·페이지 등 사람이 찾을 위치), `quote`(짧은 원문 발췌) |
| concept | `id`, `title`, `prerequisites`(다른 concept id 배열), `prior_note`(없으면 빈 문자열) |
| question | `id`(예: `2강:14`), `source_id`, `locator`, `status`: `included/review/deferred`, `fact_ids`, `reason`(deferred 필수) |
| mapping | `fact_id`, `target_ids`(HTML id 배열) |
| review | `status`: `pending/complete`, `artifact_sha256`, `inventory_sha256`, `inventory_change_reason`, `source_audit`, `fact_checks`, `reverse_audit`, `visual_audit`, `conflicts` |
| source_audit | `status`: `pending/pass`, `notes`(목록이 원본을 충실히 분해했는지 확인한 근거) |
| fact_check | `fact_id`, `status`: `pending/pass`, `evidence`(어떤 문장·조건을 대조했는지) |
| reverse_audit | `status`: `pending/pass`, `notes`(추가·과장·모순을 검토한 근거) |
| visual_audit | `status`: `pending/pass`, `notes`(desktop/mobile/print 실제 점검 결과) |
| conflict | `id`, `status`: `open/resolved`, `source_claim`, `resolution`, `evidence`, `target_id` |

경로는 manifest 파일의 부모를 기준으로 resolve한다. `../` 자체를 금지하지 않는다. 실제 파일이 존재하고 해시가 맞는지 확인한다. `main_source`는 정확히 하나의 `role=note`를 가리키고 UTF-8 MD여야 한다. PDF 참고 자료는 bytes 해시만 계산하고 페이지·정답 색상 검토는 해당 PDF 스킬로 수행한다. 무관한 PDF까지 자동으로 전수 렌더링하지 않는다.

### HTML 계약

```html
<section id="concept-enzyme" data-concept="enzyme" data-role="teaching">
  <h2>효소: 반응을 시작하는 문턱</h2>
  <p id="fact-barrier">효소는 활성화에너지를 낮춥니다.</p>
  <p id="fact-balance">반응물과 생성물의 에너지 차이나 평형은 바꾸지 않습니다.</p>
  <div data-role="recall" data-generated="true">
    <p>학습용 생성 질문: 효소가 바꾸는 것과 바꾸지 않는 것을 말해 보세요.</p>
    <details><summary>설명 확인</summary><p data-part="model-answer">활성화에너지를 낮추지만 평형은 바꾸지 않습니다.</p></details>
  </div>
</section>
<article data-question-id="2강:6" data-status="included">
  <h3>원본 문항 2강 6</h3>
  <p data-part="prompt">효소에 대한 설명 중 틀린 것은?</p>
  <details data-role="solution"><summary>정답과 근거</summary>
    <p data-part="answer">비가역 반응을 가역 반응으로 만든다.</p>
    <p data-part="reason">효소는 평형을 바꾸지 않습니다.</p>
    <p data-part="trap">속도 변화와 평형 변화를 혼동하지 마세요.</p>
    <a data-remedy="confusion" href="#concept-enzyme">개념 비교 복습</a>
  </details>
</article>
<article data-question-id="2강:3" data-status="deferred">
  <p data-part="deferred-reason">발효는 이번 회차 범위 밖입니다. 후속 강의에서 공부합니다.</p>
</article>
```

- 사실 target은 `data-role=teaching` 내부의 보이는 설명이어야 한다. deferred 사실은 `data-role=boundary` 내부여야 한다. `details`, `script`, `style`, `template`, `hidden`, `aria-hidden=true` 내부는 필수 설명 target으로 인정하지 않는다.
- 각 concept에는 `data-role=recall`이 1~3개 있어야 한다. 생성 표시, 질문 텍스트, 닫힌 details 안의 model-answer가 필요하다. 원본 문항 수에는 포함하지 않는다.
- `included/review` 문항은 prompt·answer·reason·trap·관련 concept 링크가 필요하다. 선택지가 없는 문제의 trap은 흔한 오해로 작성하며 가짜 보기를 추가하지 않는다.
- deferred 문항은 사유가 필요하고 answer/reason/solution을 포함하지 않는다. included/review와 같은 정확한 ID 집합 안에서 상태를 검사한다.
- 정답·모범답은 닫힌 details 아래에 둔다. `data-remedy`는 `term/confusion/process/condition` 중 하나이고 해당 concept로 이동한다. 모든 문항에 네 종류를 억지로 달지 않는다.
- SVG 설명은 inline으로 포함하며 핵심 사실은 SVG만이 아니라 짧은 한국어 본문도 갖춘다. CSS 때문에 실제로 안 보이는 경우는 시각 검토로 확인한다.

### CLI 계약

```bash
python3 .agents/skills/study-note-eli5/scripts/verify_guide.py 정리노트/0910-eli5-audited.html --coverage 정리노트/0910-eli5-audited.coverage.json --phase structure
python3 .agents/skills/study-note-eli5/scripts/verify_guide.py 정리노트/0910-eli5-audited.html --coverage 정리노트/0910-eli5-audited.coverage.json --phase complete
```

`--phase` 기본값은 complete. structure는 연결과 inventory만 확인하고 `STRUCTURE PASS; semantic review not certified`를 출력한다. complete는 review의 기록과 해시까지 확인하며 `PASS: structure + recorded review; semantic accuracy is not machine-proven`을 출력한다. 오류는 `FAIL`과 항목별 이유, 종료 1. argparse 입력 오류는 2. coverage 없는 구형 `--questions`/`--marker` 호출은 기존 검사만 하되 `LEGACY STRUCTURE ONLY`로 표시한다. `--coverage`와 구형 인수의 혼용은 argparse 오류로 처리한다. coverage 없이 명시적인 `--phase`를 주면 오류다.

## Task 1: 원본 inventory와 스키마 검증

**Files:** Create `references/coverage-contract.md`, `scripts/coverage_model.py`(스킬 폴더 기준), `tests/study_guide_fixture.py`, `tests/test_study_guide_model.py`.

**Interfaces:**
- Consumes: 위 JSON v1 계약; manifest 상대 경로.
- Produces: `inventory_digest(inventory: dict) -> str`, `file_digest(path: Path) -> str`, `validate_inventory(data: dict, base: Path) -> list[str]`.
- malformed JSON 형태도 traceback 대신 오류 배열을 반환한다. 파일 I/O 오류는 경로와 원인을 오류에 넣는다.

- [ ] **Step 1: 계약 문서와 최소 fixture를 작성한다.** 계약 문서는 §2를 단일 기준으로 옮긴다. 테스트 helper의 실제 내용:

```python
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/study-note-eli5/scripts"
sys.path.insert(0, str(SCRIPTS))

def digest(value):
    return hashlib.sha256(value).hexdigest()

def case(base):
    note = "# 효소\n\n효소는 활성화에너지를 낮춘다.\n\n평형은 바꾸지 않는다.\n"
    quiz = "2강 6: 효소에 대한 설명 중 틀린 것은? 답: 비가역 반응을 가역 반응으로 만든다.\n"
    (base / "note.md").write_text(note, encoding="utf-8")
    (base / "quiz.txt").write_text(quiz, encoding="utf-8")
    inventory = {
        "main_source": "note",
        "sources": [
            {"id": "note", "path": "note.md", "role": "note", "sha256": digest(note.encode()), "read_status": "read"},
            {"id": "quiz", "path": "quiz.txt", "role": "quiz", "sha256": digest(quiz.encode()), "read_status": "read"},
        ],
        "blocks": [
            {"id": "b0", "start": 1, "end": 1, "kind": "metadata", "fact_ids": [], "reason": "단원 제목"},
            {"id": "b1", "start": 3, "end": 3, "kind": "teaching", "fact_ids": ["f1"], "reason": ""},
            {"id": "b2", "start": 5, "end": 5, "kind": "teaching", "fact_ids": ["f2"], "reason": ""},
        ],
        "facts": [
            {"id": "f1", "block_id": "b1", "statement": "효소는 활성화에너지를 낮춘다.", "qualifiers": [], "concept_id": "enzyme", "scope": "teaching", "evidence": {"source_id": "note", "locator": "3행", "quote": "효소는 활성화에너지를 낮춘다."}},
            {"id": "f2", "block_id": "b2", "statement": "평형은 바꾸지 않는다.", "qualifiers": ["속도와 평형 구분"], "concept_id": "enzyme", "scope": "teaching", "evidence": {"source_id": "note", "locator": "5행", "quote": "평형은 바꾸지 않는다."}},
        ],
        "concepts": [{"id": "enzyme", "title": "효소", "prerequisites": [], "prior_note": ""}],
        "questions": [{"id": "2강:6", "source_id": "quiz", "locator": "1행", "status": "included", "fact_ids": ["f2"], "reason": ""}],
    }
    data = {"schema_version": 1, "inventory": inventory,
            "inventory_sha256": digest(json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
            "mappings": [{"fact_id": "f1", "target_ids": ["fact-barrier"]}, {"fact_id": "f2", "target_ids": ["fact-balance"]}],
            "review": {"status": "pending"}}
    return data
```

- [ ] **Step 2: 실패 테스트를 작성한다.** `tests/test_study_guide_model.py`:

```python
import tempfile
import unittest
from pathlib import Path
from study_guide_fixture import case
from coverage_model import inventory_digest, validate_inventory

class InventoryTests(unittest.TestCase):
    def test_source_fact_without_a_question_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            self.assertEqual(validate_inventory(data, base), [])
            data["inventory"]["blocks"].pop(1)
            data["inventory_sha256"] = inventory_digest(data["inventory"])
            self.assertIn("uncovered source line: 3", validate_inventory(data, base))

    def test_changed_source_invalidates_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            (base / "note.md").write_text("다른 내용", encoding="utf-8")
            self.assertIn("source hash mismatch: note", validate_inventory(data, base))

    def test_malformed_input_is_an_error_list(self):
        with tempfile.TemporaryDirectory() as directory:
            for data in ([], {}, {"schema_version": 2}, {"schema_version": 1, "inventory": None}):
                with self.subTest(data=data):
                    self.assertTrue(validate_inventory(data, Path(directory)))
```

- [ ] **Step 3: 테스트를 실행해 미구현 실패를 확인한다.**

```bash
python3 -m unittest discover -s tests -p 'test_study_guide_model.py' -v
```

Expected: `coverage_model` import 실패. 원천 노트 테스트 실패를 이 작업의 red로 사용하지 않는다.

- [ ] **Step 4: 해시와 범위 검증을 구현한다.** 아래 알고리즘을 `coverage_model.py`에 넣고, 계약 표의 필드별 타입을 먼저 검사한다.

```python
import hashlib
import json
from collections import Counter
from pathlib import Path

def inventory_digest(inventory: dict) -> str:
    value = json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def line_errors(lines: list[str], blocks: list[dict]) -> list[str]:
    errors = []
    covered = Counter()
    for block in blocks:
        start, end = block["start"], block["end"]
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            errors.append(f"invalid source range: {block['id']}")
            continue
        covered.update(range(start, end + 1))
    for number, line in enumerate(lines, 1):
        if line.strip() and covered[number] == 0:
            errors.append(f"uncovered source line: {number}")
        if covered[number] > 1:
            errors.append(f"overlapping source line: {number}")
    return errors
```

`validate_inventory`의 구현 순서는 다음처럼 고정한다. 각각 독립적인 짧은 구현 단계로 작업한다.

```python
def validate_inventory(data: dict, base: Path) -> list[str]:
    errors = shape_errors(data)
    if errors:
        return errors
    inventory = data["inventory"]
    errors.extend(reference_errors(inventory))
    if data["inventory_sha256"] != inventory_digest(inventory):
        errors.append("inventory hash mismatch")
    for source in inventory["sources"]:
        path = (base / source["path"]).resolve()
        if source["read_status"] != "read":
            errors.append(f"source not read: {source['id']}")
        try:
            if file_digest(path) != source["sha256"]:
                errors.append(f"source hash mismatch: {source['id']}")
            if source["id"] == inventory["main_source"]:
                lines = path.read_text(encoding="utf-8").splitlines()
                errors.extend(line_errors(lines, inventory["blocks"]))
        except (OSError, UnicodeError) as error:
            errors.append(f"cannot read source {source['id']}: {error}")
    return errors
```

이 단계에서 사용하는 내부 함수도 같은 파일에 정의한다:

- `shape_errors(data: object) -> list[str]`: §2의 필수 키, object/list/string/int 타입, enum을 검사한다. start/end에 bool을 허용하지 않는다. 빈 id/path/statement/locator/quote는 실패다. 배열에 dict가 아닌 값이 있으면 실패한다. mappings/review는 존재와 바깥 타입을 확인하고 상세 검사는 후속 작업에서 수행한다.
- `reference_errors(inventory: dict) -> list[str]`: source/block/fact/concept/question 각각의 id 중복, main_source 존재·role, block↔fact 양방향 대응, metadata의 빈 fact_ids와 비어 있지 않은 reason, 나머지 block의 비어 있지 않은 fact_ids를 확인한다. block.kind와 fact.scope는 teaching→teaching, review→review, supplement→supplement, boundary→deferred로 대응한다. concept/prerequisite 참조와 순환, question.source의 role=quiz와 fact 참조를 검사한다. included/review question에는 deferred가 아닌 fact가 하나 이상 있어야 한다. deferred question은 비어 있지 않은 reason이 필수다. fact.evidence의 source는 존재해야 한다.

주 노트 fact의 quote가 해당 block의 실제 텍스트에 포함되는지는 `validate_inventory`에서 파일을 읽은 직후 확인한다. `reference_errors`에는 파일 내용이나 경로를 추가로 전달하지 않는다. 참고 자료에서 얻은 보충 설명의 연결은 source_audit에서 별도로 판단한다.

- [ ] **Step 5: 경계 사례를 실행 가능한 테스트로 추가한다.** 다음을 같은 클래스에 추가하고, 변경한 inventory digest를 다시 계산해 구조 오류 자체를 검증한다.

```python
    def test_rejects_broken_inventory_links(self):
        changes = [
            lambda i: i["facts"].append(dict(i["facts"][0])),
            lambda i: i["blocks"][1].update(start=0),
            lambda i: i["blocks"][1].update(start=1),
            lambda i: i["facts"][0].update(concept_id="missing"),
            lambda i: i["concepts"][0].update(prerequisites=["enzyme"]),
            lambda i: i["sources"][1].update(read_status="unread"),
            lambda i: i["blocks"][0].update(reason=""),
            lambda i: i["questions"][0].update(source_id="note"),
        ]
        for change in changes:
            with tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                data = case(base)
                change(data["inventory"])
                data["inventory_sha256"] = inventory_digest(data["inventory"])
                self.assertTrue(validate_inventory(data, base))
```

- [ ] **Step 6: 같은 테스트 명령으로 PASS를 확인하고 독립 변경 묶음을 검토한다.** 계약이 기존 디자인과 달라진 경우 계약과 후속 인터페이스를 함께 수정한다. 승인된 경우에만 아래 정확한 경로로 커밋한다.

```bash
git add -- .agents/skills/study-note-eli5/references/coverage-contract.md .agents/skills/study-note-eli5/scripts/coverage_model.py tests/study_guide_fixture.py tests/test_study_guide_model.py
git commit -m "feat: validate study guide source inventory"
```

## Task 2: 실제 설명·문항·회상 DOM 검증

**Files:** Create `.agents/skills/study-note-eli5/scripts/guide_html.py`, `tests/test_study_guide_html.py`; extend `tests/study_guide_fixture.py`.

**Interfaces:**
- Consumes: `inventory`와 `mappings`의 v1 데이터.
- Produces: `parse_guide(html: str) -> GuideParser`, `validate_html(html: str, data: dict) -> list[str]`.
- Internal: `Node`(tag, attrs, parent, text, children), `GuideParser`(nodes, ids, errors), `descendants(node: Node) -> list[Node]`, `text_of(node: Node) -> str`, `ancestor_has(node: Node, key: str, value: str) -> bool`.

- [ ] **Step 1: fixture에 §2의 효소 concept와 included 문항을 `HTML` 상수로 복사한다.** deferred 예제는 기본 fixture에 포함하지 않는다. 문자열을 `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>효소</title></head><body>`와 `</body></html>`로 감싼다. 이 상수는 템플릿의 외형을 테스트하지 않고 계약만 테스트한다.

- [ ] **Step 2: 다음 실패 테스트를 작성한다.**

```python
import tempfile
import unittest
from pathlib import Path
from study_guide_fixture import case, HTML
from guide_html import validate_html

class HtmlTests(unittest.TestCase):
    def test_valid_links(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(validate_html(HTML, case(Path(directory))), [])

    def test_fact_id_in_answer_is_not_teaching(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            html = HTML.replace('id="fact-barrier"', 'id="other"')
            html = html.replace('data-part="answer"', 'data-part="answer" id="fact-barrier"')
            self.assertIn("fact target is not visible teaching: f1/fact-barrier", validate_html(html, data))

    def test_empty_explanation_and_duplicate_question_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            empty = HTML.replace("효소는 활성화에너지를 낮춥니다.", "")
            self.assertTrue(validate_html(empty, data))
            duplicate = HTML.replace("</body>", '<article data-question-id="2강:6"></article></body>')
            self.assertIn("duplicate question: 2강:6", validate_html(duplicate, data))

    def test_generated_recall_is_not_an_original_question(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            html = HTML.replace('data-role="recall"', 'data-role="recall" data-question-id="2강:99"')
            self.assertTrue(validate_html(html, data))
```

- [ ] **Step 3: `python3 -m unittest discover -s tests -p 'test_study_guide_html.py' -v`로 import 실패를 확인한다.**

- [ ] **Step 4: 작은 HTML 트리 파서를 구현한다.** Python `HTMLParser(convert_charrefs=True)`를 사용하며 JavaScript를 실행하지 않는다. Node는 아래 구조로 시작한다.

```python
from dataclasses import dataclass, field
from html.parser import HTMLParser

@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    parent: "Node | None" = None
    text: list[str] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)

def descendants(node: Node) -> list[Node]:
    return [child for direct in node.children for child in [direct, *descendants(direct)]]

def text_of(node: Node) -> str:
    if node.tag in {"script", "style", "template"}:
        return ""
    return " ".join([*node.text, *(text_of(child) for child in node.children)]).strip()

def ancestor_has(node: Node, key: str, value: str) -> bool:
    current = node
    while current is not None:
        if current.attrs.get(key) == value:
            return True
        current = current.parent
    return False
```

`GuideParser`는 루트 노드와 stack을 유지한다. starttag에서 parent/children을 연결하고 nodes에 추가한다. id가 기존 ids에 있으면 에러를 기록한다. `area/base/br/col/embed/hr/img/input/link/meta/param/source/track/wbr`는 stack에 넣지 않는다. `handle_startendtag`는 SVG self-closing까지 처리한다. endtag가 stack top과 다르면 broken nesting 오류를 남기고 해당 tag까지 회복한다. 종료 시 미닫힌 stack도 오류다. HTMLParser는 브라우저 CSS 엔진이 아니므로 화면 통과 판정은 여기서 하지 않는다.

- [ ] **Step 5: `validate_html`을 아래 검증 순서로 구현한다.** 호출 전 Task 1의 검증을 통과한 data를 사용하되 public 함수는 잘못된 외형에 오류를 반환한다.

```python
def validate_html(html: str, data: dict) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("inventory"), dict) or not isinstance(data.get("mappings"), list):
        return ["invalid coverage shape for HTML validation"]
    guide = parse_guide(html)
    errors = list(guide.errors)
    if not html.lstrip().lower().startswith("<!doctype html>"):
        errors.append("missing HTML doctype")
    errors.extend(mapping_errors(guide, data))
    errors.extend(question_errors(guide, data["inventory"]))
    errors.extend(learning_errors(guide, data["inventory"]))
    errors.extend(resource_errors(guide, html))
    return errors
```

같은 파일에 아래 내부 함수를 구현한다. 첫 인수는 `GuideParser`, 두 번째 인수는 명시한 dict 또는 str이며 반환값은 모두 `list[str]`다:

- `mapping_errors(guide: GuideParser, data: dict)`: fact와 mapping의 id 집합이 완전히 같고 각 fact가 한 번만 mapping돼야 한다. target_ids는 비어 있지 않고 중복 없는 문자열 배열이다. 각 target의 존재·본문·teaching 또는 boundary 부모를 확인한다. deferred가 아닌 fact는 concept_id와 target 조상의 data-concept도 같아야 한다. details/solution/hidden/script/style/template/aria-hidden 아래 target은 실패다. 주석에 있는 id는 인정하지 않는다.
- `question_errors(guide: GuideParser, inventory: dict)`: `[data-question-id]`의 집합·개수와 inventory.questions가 같고 status도 같아야 한다. included/review는 prompt/answer/reason/trap 각각의 비어 있지 않은 본문, 닫힌 details[data-role=solution] 아래 answer, fact_ids에 연결된 모든 concept로의 실제 href를 요구한다. deferred는 deferred-reason만 요구하며 answer/reason/solution은 금지한다. 생성 recall에 question-id가 있으면 실패다.
- `learning_errors(guide: GuideParser, inventory: dict)`: concept id 집합·개수 일치, prerequisite concept로의 실제 내부 링크, concept당 recall 1~3개를 확인한다. recall의 data-generated=true, 질문, 닫힌 details 안 model-answer를 확인한다. data-remedy의 enum과 href의 실제 concept를 확인한다.
- `resource_errors(guide: GuideParser, html: str)`: script[src], link[rel=stylesheet], img, iframe/object/embed/audio/video, CSS @import/url(...), fetch/XMLHttpRequest/WebSocket/sendBeacon을 실패 처리한다. href는 `#id`나 원본 자료 상대 링크를 허용하고, 일반 외부 인용 링크는 실행 시 네트워크 의존성으로 세지 않는다. SVG의 표준 xmlns는 허용한다. 보수적인 패턴 검사이며 실행 안전을 증명하는 장치가 아니다.

- [ ] **Step 6: 상태와 숨겨진 설명에 대한 회귀 테스트를 추가한다.**

```python
    def test_hidden_and_out_of_scope_answers_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            for attr in ('hidden', 'aria-hidden="true"'):
                html = HTML.replace('id="fact-barrier"', f'id="fact-barrier" {attr}')
                self.assertTrue(validate_html(html, data))
            data["inventory"]["questions"][0].update(status="deferred", reason="후속 강의")
            html = HTML.replace('data-status="included"', 'data-status="deferred"')
            self.assertTrue(validate_html(html, data))

    def test_source_qualified_question_ids_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            data = case(Path(directory))
            item = dict(data["inventory"]["questions"][0], id="1강:6", status="review")
            data["inventory"]["questions"].append(item)
            article = HTML[HTML.index('<article'):HTML.index('</article>') + len('</article>')]
            second = article.replace('2강:6', '1강:6').replace('data-status="included"', 'data-status="review"')
            self.assertEqual(validate_html(HTML.replace('</body>', second + '</body>'), data), [])
```

- [ ] **Step 7: HTML 테스트 PASS와 Task 1 회귀 PASS를 확인한다.** 승인된 경우에만 정확한 파일을 커밋한다.

```bash
python3 -m unittest discover -s tests -p 'test_study_guide_*.py' -v
git add -- .agents/skills/study-note-eli5/scripts/guide_html.py tests/test_study_guide_html.py tests/study_guide_fixture.py
git commit -m "feat: verify teaching and quiz coverage in HTML"
```

## Task 3: CLI와 버전이 묶인 검토 게이트

**Files:** Modify `.agents/skills/study-note-eli5/scripts/verify_guide.py`; Create `tests/test_study_guide_cli.py`; Extend `tests/study_guide_fixture.py`.

**Interfaces:**
- Consumes: `validate_inventory(data, base)`, `file_digest(path)`, `validate_html(html, data)`.
- Produces: `validate_review(data: dict, artifact: Path) -> list[str]`, `main(argv: list[str] | None = None) -> int`.
- CLI는 read-only다. JSON을 수정하거나 임의로 review를 pass로 만들지 않는다.

- [ ] **Step 1: fixture helper를 확장한다.**

```python
def reviewed(data, html):
    data["review"] = {
        "status": "complete", "artifact_sha256": digest(html.encode()),
        "inventory_sha256": data["inventory_sha256"], "inventory_change_reason": "",
        "source_audit": {"status": "pass", "notes": "fixture의 3개 구간과 2개 사실을 대조했다."},
        "fact_checks": [
            {"fact_id": "f1", "status": "pass", "evidence": "fact-barrier에 활성화에너지 감소가 있다."},
            {"fact_id": "f2", "status": "pass", "evidence": "fact-balance에 평형 불변이 있다."},
        ],
        "reverse_audit": {"status": "pass", "notes": "fixture에 근거 없는 추가 주장이 없다."},
        "visual_audit": {"status": "pass", "notes": "단위 테스트용 가상 기록; 실제 화면 검증 결과가 아니다."},
        "conflicts": [],
    }
    return data
```

- [ ] **Step 2: 종료 코드와 review 무효화 테스트를 작성한다.**

```python
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from study_guide_fixture import case, HTML, reviewed
from verify_guide import main, validate_review

class CliTests(unittest.TestCase):
    def test_structure_does_not_certify_pending_review(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = case(base)
            artifact, manifest = base / "guide.html", base / "guide.coverage.json"
            artifact.write_text(HTML, encoding="utf-8")
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = main([str(artifact), "--coverage", str(manifest), "--phase", "structure"])
            self.assertEqual(rc, 0)
            self.assertIn("semantic review not certified", output.getvalue())
            self.assertTrue(validate_review(data, artifact))

    def test_html_edit_invalidates_review(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = reviewed(case(base), HTML)
            artifact = base / "guide.html"
            artifact.write_text(HTML, encoding="utf-8")
            self.assertEqual(validate_review(data, artifact), [])
            artifact.write_text(HTML.replace("평형은 바꾸지 않습니다.", "평형을 바꿉니다."), encoding="utf-8")
            self.assertIn("review artifact hash mismatch", validate_review(data, artifact))

    def test_open_conflict_blocks_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = reviewed(case(base), HTML)
            artifact = base / "guide.html"
            artifact.write_text(HTML, encoding="utf-8")
            data["review"]["conflicts"] = [{"id": "c1", "status": "open", "source_claim": "원문 주장", "resolution": "", "evidence": "", "target_id": ""}]
            self.assertIn("open conflict: c1", validate_review(data, artifact))
```

- [ ] **Step 3: `python3 -m unittest discover -s tests -p 'test_study_guide_cli.py' -v`로 아직 없는 main(argv)/validate_review 실패를 확인한다.**

- [ ] **Step 4: 완료 검토를 구현한다.**

```python
def validate_review(data: dict, artifact: Path) -> list[str]:
    review = data.get("review", {})
    if not isinstance(review, dict) or review.get("status") != "complete":
        return ["review not complete"]
    errors = []
    if review.get("artifact_sha256") != file_digest(artifact):
        errors.append("review artifact hash mismatch")
    if review.get("inventory_sha256") != data["inventory_sha256"]:
        errors.append("review inventory hash mismatch")
    for key in ("source_audit", "reverse_audit", "visual_audit"):
        audit = review.get(key, {})
        notes = audit.get("notes") if isinstance(audit, dict) else None
        if not isinstance(audit, dict) or audit.get("status") != "pass" or not isinstance(notes, str) or not notes.strip():
            errors.append(f"review incomplete: {key}")
    errors.extend(fact_review_errors(data))
    errors.extend(conflict_review_errors(data, artifact))
    return errors
```

같은 파일에 `fact_review_errors(data: dict) -> list[str]`와 `conflict_review_errors(data: dict, artifact: Path) -> list[str]`를 정의한다. 전자는 fact_checks의 타입, id 집합 완전 일치·중복 금지, status=pass, 비어 있지 않은 evidence를 확인한다. 후자는 conflicts 배열·id 중복 금지를 확인하고 open이면 `open conflict: ID`를 반환한다. resolved이면 source_claim/resolution/evidence/target_id가 비어 있지 않은 문자열이어야 하고 실제 HTML target과 본문이 있어야 한다. None이나 dict를 문자열로 바꿔 검토 근거로 통과시키지 않는다. review.inventory_change_reason은 문자열 필수지만 최초 생성은 빈 값을 허용한다.

- [ ] **Step 5: CLI를 §2의 계약대로 연결한다.** 주 경로의 코드:

```python
def run_coverage(artifact: Path, manifest: Path, phase: str) -> list[str]:
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        html = artifact.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [f"cannot load inputs: {error}"]
    errors = validate_inventory(data, manifest.parent)
    if errors:
        return errors
    errors = validate_html(html, data)
    if phase == "complete":
        errors.extend(validate_review(data, artifact))
    return errors
```

`main`은 argparse로 artifact/coverage/phase/questions/marker를 해석한다. phase의 parser 기본값을 None으로 해 coverage 없이 명시한 phase를 감지하고, coverage 경로에만 complete를 채운다. 기존 검사는 `legacy_errors(artifact: Path, questions: str | None, markers: list[str]) -> list[str]`로 옮긴다. 현재 doctype/종료 태그/1000문자/marker/qnum 검사를 유지하며 기존 HTML을 자동 변환하지 않는다. 출력 문구와 종료 코드는 §2를 따른다.

- [ ] **Step 6: CLI의 실제 입출력 사례를 추가한다.**

```python
    def test_missing_or_bad_json_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            artifact, manifest = base / "guide.html", base / "bad.json"
            artifact.write_text(HTML, encoding="utf-8")
            for content in ("{", "[]", '{"schema_version": 2}'):
                manifest.write_text(content, encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([str(artifact), "--coverage", str(manifest)]), 1)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(artifact), "--coverage", str(base / "missing.json")]), 1)

    def test_legacy_pass_is_labeled_structure_only(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "old.html"
            artifact.write_text('<!doctype html><html><body>30초 문항별 범위 <b class="qnum">6</b>' + '설명 ' * 400 + '</body></html>', encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(artifact), "--questions", "6"]), 0)
            self.assertIn("LEGACY STRUCTURE ONLY", output.getvalue())
```

추가로 coverage와 questions를 혼용한 경우, coverage 없이 phase를 명시한 경우를 검사한다. 실행 가능한 테스트 코드는 다음과 같다.

```python
    def test_rejects_mixed_cli_modes(self):
        for argv in (["guide.html", "--coverage", "guide.json", "--questions", "6"],
                     ["guide.html", "--phase", "complete"]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    main(argv)
            self.assertEqual(caught.exception.code, 2)

    def test_missing_or_stale_review_evidence_fails(self):
        changes = [
            lambda r: r.update(fact_checks=[]),
            lambda r: r["fact_checks"].append(dict(r["fact_checks"][0])),
            lambda r: r["fact_checks"][0].update(evidence=""),
            lambda r: r.update(inventory_sha256="0" * 64),
            lambda r: r.update(conflicts=[{"id": "c1", "status": "resolved", "source_claim": "원문", "resolution": "정정", "evidence": "대조 근거", "target_id": "missing"}]),
        ]
        for change in changes:
            with tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                data = reviewed(case(base), HTML)
                artifact = base / "guide.html"
                artifact.write_text(HTML, encoding="utf-8")
                change(data["review"])
                self.assertTrue(validate_review(data, artifact))
```

- [ ] **Step 7: 신규 테스트 전체를 실행하고 승인된 경우 커밋한다.**

```bash
python3 -m unittest discover -s tests -p 'test_study_guide_*.py' -v
git add -- .agents/skills/study-note-eli5/scripts/verify_guide.py tests/test_study_guide_cli.py tests/study_guide_fixture.py
git commit -m "feat: gate guide completion on current review evidence"
```

## Task 4: 이해·회상·적용 템플릿

**Files:** Modify `.agents/skills/study-note-eli5/assets/base-template.html`; Create `tests/test_study_guide_template.py`.

**Interfaces:**
- Consumes: HTML data-* 계약, `validate_html`.
- Produces: 복사해 내용을 교체할 수 있는 효소 1단원 예제. fixture의 f1/f2 및 2강:6을 실제로 포함하고 미완성 토큰은 남기지 않는다.
- UI: 읽기/회상/원본 문제/복습 안내. 앱 저장소·계정·성적 추적 없음.

- [ ] **Step 1: 템플릿이 현재 계약을 만족하지 못함을 확인할 테스트를 만든다.**

```python
import tempfile
import unittest
from pathlib import Path
from study_guide_fixture import case, ROOT
from guide_html import validate_html

class TemplateTests(unittest.TestCase):
    def test_template_teaches_before_asking(self):
        html = (ROOT / ".agents/skills/study-note-eli5/assets/base-template.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(validate_html(html, case(Path(directory))), [])
        for marker in ('id="study-map"', 'id="study-routine"', 'id="scope-boundary"'):
            self.assertIn(marker, html)
        self.assertLess(html.index('id="fact-balance"'), html.index('data-question-id="2강:6"'))
        self.assertIn("beforeprint", html)
        self.assertIn("afterprint", html)
```

- [ ] **Step 2: `python3 -m unittest discover -s tests -p 'test_study_guide_template.py' -v`로 현재 템플릿의 실패를 확인한다.**

- [ ] **Step 3: 기본 visual language를 유지해 완성된 효소 예제를 작성한다.** 다음 카피·구성을 사용한다.

| 위치 | 실제 내용 |
|---|---|
| header | `효소: 반응을 시작하는 문턱` / `비유로 이해하고, 정확한 용어로 설명해 봅시다.` |
| study-map | `활성화에너지 → 효소의 역할 → 바뀌지 않는 평형 → 스스로 설명하기 → 원본 문제` |
| 비유 | `언덕을 넘는 길을 더 낮게 만들면 같은 출발점에서 같은 도착점으로 가기 쉬워집니다.` |
| 정확한 설명 | §2의 fact-barrier/fact-balance 본문을 사용 |
| 비유의 한계 | `효소가 열이나 ATP를 공급한다는 뜻은 아닙니다. 여기서 낮아지는 것은 활성화에너지입니다.` |
| recall | `효소가 바꾸는 것과 바꾸지 않는 것을 말해 보세요.` / 모범 설명은 닫힌 details |
| 원본 문제 | §2 문항 예제. fixture로부터 만든 데모 문항임을 표기; 실제 PDF 원문이라고 주장하지 않음 |
| scope-boundary | `이 예제의 범위는 효소의 활성화에너지와 평형입니다. 실제 가이드는 지정 노트 전체를 다룹니다.` |
| study-routine | `처음에는 그림과 설명을 읽고, 다음 공부를 시작할 때는 설명을 가리고 떠올려 보세요. 주간 복습에서는 여러 단원의 문제를 섞어 풀어 보세요.` |

inline SVG는 출발·도착 높이가 같은 두 경로와 서로 다른 봉우리를 보여준다. 라벨은 `반응물`, `생성물`, `효소 없음`, `효소 있음`, `활성화에너지`다. `viewBox="0 0 600 240"`, 반응물 (40,180), 생성물 (550,180), 높은 경로 `M40 180 Q290 -80 550 180`, 낮은 경로 `M40 180 Q290 60 550 180`를 사용한다. 특정 반응의 에너지 수치를 나타내는 그림이 아닌 개념 모식도라고 캡션을 단다.

- [ ] **Step 4: 답 숨김과 인쇄 복원을 구현한다.** 실제 CSS/JS:

```html
<style>
svg { max-width: 100%; height: auto; }
.flow { flex-wrap: wrap; }
a:focus-visible, summary:focus-visible { outline: 3px solid #356ae6; outline-offset: 3px; }
@media print {
  body { background: white; color: black; }
  .wrap { max-width: none; padding: 0; }
  .grid, .compare { display: block; }
  .card { break-inside: auto; box-shadow: none; }
  svg, .answer { break-inside: avoid; }
  details > :not(summary) { display: block !important; }
}
</style>
<script>
let printState = null;
window.addEventListener('beforeprint', () => {
  if (printState !== null) return;
  printState = [...document.querySelectorAll('details')].map(el => [el, el.open]);
  printState.forEach(([el]) => { el.open = true; });
});
window.addEventListener('afterprint', () => {
  if (printState === null) return;
  printState.forEach(([el, wasOpen]) => { el.open = wasOpen; });
  printState = null;
});
</script>
```

- [ ] **Step 5: 테스트 PASS 후 실제 브라우저에서 확인한다.** desktop 1280px와 mobile 390px에서 SVG 라벨·본문 잘림·가로 넘침을 확인한다. keyboard로 summary 열고 닫기, 오답 복습 anchor 이동, 닫힌 상태에서 인쇄 미리보기의 답 표시, 인쇄 취소 후 원래 접힘 상태 복원을 확인한다. UI 도구 사용 전 해당 도구의 지침을 읽는다. 정적 검사 결과로 이 항목을 대신하지 않는다.

- [ ] **Step 6: 승인된 경우에만 커밋한다.**

```bash
git add -- .agents/skills/study-note-eli5/assets/base-template.html tests/test_study_guide_template.py
git commit -m "feat: add recall and review flow to study guide template"
```

## Task 5: 스킬 절차와 원천/파생 규칙 동기화

**Files:** Modify `.agents/skills/study-note-eli5/SKILL.md:10-38`, `정리노트/CLAUDE.md:49-67,114-124`.

**Interfaces:**
- Consumes: `references/coverage-contract.md`, CLI 두 phase, template data-* 계약.
- Produces: 작성자가 별도 대화 맥락 없이 실행 가능한 절차와 최종 보고 기준.

- [ ] **Step 1: SKILL.md의 Workflow를 아래 8단계로 교체한다.** 스킬 frontmatter/name을 유지하고 생물학 예시 외에 특정 날짜나 특정 문항 번호를 규칙으로 하드코딩하지 않는다.

```markdown
1. Read the target note completely and read its companion quiz. Record source paths, roles, hashes, read status, lecture scope, review questions, and deferred questions. Resolve relevant earlier-note prerequisites. Use original question sources when wording, choices, or answer keys are uncertain; never reconstruct missing choices by guesswork.
2. Read references/coverage-contract.md. Inventory every nonblank source range, then extract independently checkable facts with their conditions, quantities, units, directions, warnings, and evidence. Include facts without quiz questions. Audit the inventory against the original before generating HTML; record the inventory digest.
3. Arrange concepts for learning: whole map, analogy, accurate diagram and terminology, mechanism, conditions and exceptions, then 1–3 recall prompts per concept group. Keep essential facts visible in teaching sections. Identify where an analogy stops being accurate.
4. Create a self-contained UTF-8 HTML guide next to the note, using assets/base-template.html and the coverage contract. Use <stem>-eli5.html unless it already contains user work; in that case choose a new explicit filename. Record facts-to-teaching targets in <artifact-stem>.coverage.json. Do not load that JSON at runtime.
5. Add original-question cards keyed by source and number. Hide solutions initially; show answer, reason, plausible misunderstanding and a concept review link. Label generated recall questions separately. Deferred questions show only the reason and needed future lesson. Include first-study, next-study recall and weekly cumulative-review guidance without scheduling notifications.
6. Run the validator with --coverage and --phase structure. Repair missing source ranges, facts, concept links, question scope and malformed HTML. Do not delete inventory requirements to make validation pass.
7. Re-read the original to audit facts against the guide; then audit the guide for unsupported additions and distorted conditions. Record fact-specific evidence, source audit, reverse audit, visible conflicts and actual desktop/mobile/print checks. Mark unresolved cases pending. Bind completed review to the current HTML hash and inventory digest; any source or HTML change requires renewed review of affected content and updated records.
8. Run --phase complete. Report structure validation and recorded semantic/visual review separately. Link the HTML, state source scope, original/review/deferred question counts and any corrections. If evidence or checks are incomplete, deliver only as review-needed and name the unresolved items. Never equate machine success with proof of semantic completeness or student understanding.
```

Step 6/8 직후 실제 호출 예시는 날짜 대신 repo 내 대표 경로를 사용하되 현재 pilot 파일과 coverage 이름을 그대로 보여준다. 신규 가이드에서 구형 `--questions` 검사만 실행하는 절차는 삭제한다. executable 경로는 `.agents/skills/study-note-eli5/scripts/verify_guide.py`이다.

- [ ] **Step 2: CLAUDE §6 뒤에 다음 규칙을 추가한다.** 기존 MD/원본 HTML의 분업 표는 유지한다.

```markdown
### ELI5 파생 학습 가이드

`*-eli5*.html`은 원천 `MMDD.md`와 원본 퀴즈 `MMDD.html`에서 생성하는 파생 학습 자료다. 원천 두 파일 사이의 본문 중복 금지 규칙을 ELI5의 설명 생략 근거로 사용하지 않는다. ELI5는 원본의 전체 학습 내용을 쉬운 표현으로 재구성하며 정답 해설과 연결한다.

생성 절차는 `.agents/skills/study-note-eli5/SKILL.md`, 검증 데이터 계약은 해당 스킬의 `references/coverage-contract.md`를 따른다. 원본 정답·설명과 판단이 충돌하면 원문 주장과 근거를 표시하며 원천 파일을 자동 수정하지 않는다. 원천 변경 시 해당 가이드와 검토 기록을 재확인한다.

coverage JSON은 제작·검증용이며 브라우저에서 불러오지 않는다. 원천 노트 테스트는 원천 파일을 계속 검사하고 ELI5는 별도 검증기로 확인한다.
```

- [ ] **Step 3: 경로·규칙의 상충 여부를 확인한다.**

```bash
rg -n 'coverage|phase|source|recall|deferred|review|검증|파생' .agents/skills/study-note-eli5/SKILL.md .agents/skills/study-note-eli5/references/coverage-contract.md 정리노트/CLAUDE.md
rg -n '\.claude/skills/study-note-eli5|\.agent/skills/study-note-eli5' .agents/skills/study-note-eli5 정리노트/CLAUDE.md
python3 -m unittest discover -s tests -p 'test_study_guide_*.py' -v
```

두 번째 rg는 match 없음(exit 1)이 기대 결과다. 단순 문서 키워드 유무만을 검사하는 별도 테스트는 만들지 않는다.

- [ ] **Step 4: diff에서 기존 사용자의 CLAUDE 변경과 이번 추가를 구별해 검토한다.** 스킬 경로의 이동·삭제를 임의로 정리하지 않는다. 커밋 승인이 있어도 파일 전체에 타인 변경이 섞였으면 아래 `git add`를 바로 실행하지 말고 해당 파일은 인계 시 제외하거나 사용자 변경까지 포함할 권한을 먼저 확인한다.

```bash
git diff -- .agents/skills/study-note-eli5/SKILL.md 정리노트/CLAUDE.md
```

승인된 독립 변경만 있는 경우의 커밋:

```bash
git add -- .agents/skills/study-note-eli5/SKILL.md 정리노트/CLAUDE.md
git commit -m "docs: define complete study guide generation workflow"
```

## Task 6: 0910 회차 실사용 검증과 인계

**Files:** Create `정리노트/0910-eli5-audited.html`, `정리노트/0910-eli5-audited.coverage.json`, `docs/superpowers/reviews/2026-09-10-study-note-eli5-pilot.md`.

**Interfaces:**
- Consumes: 현재 원본 `정리노트/0910.md`, `0910.html`, 필요한 `0908` 복습 자료와 원문 문제지; 새 스킬/계약/CLI.
- Produces: 한 회차 전체 가이드와 실제 검증 기록. 테스트 fixture의 synthetic review를 실사용 기록으로 복사하지 않는다.

- [ ] **Step 1: 원본 전체와 질문 범위를 확인한다.** `0910.md`, `0910.html`을 끝까지 읽고 복습 `1강 7,8,11,17,30,35` 및 본강/보류 목록을 현 자료와 대조한다. 명시한 복습 질문은 이전 원본 문제를 읽고 review 상태로 포함한다. 현재 본강 예상 30개는 검증 참고값이며 자동 신뢰하지 않는다. 문항 표현/답이 의심되면 원문 PDF의 실제 보기와 색상 표시를 PDF 스킬로 확인한다. 읽을 수 없는 자료가 있으면 missing/unread와 사유를 기록하고 완료 게이트를 통과시키지 않는다.

- [ ] **Step 2: JSON inventory를 생성하고 먼저 원본 대조한다.** 엽록체·액포/세포벽·세포골격·막·ATP·효소·산화환원·해당과정·회로·전자전달계, 도입 복습, 요약 표, 그림, 경고, 범위 경계 모두 구간에 포함한다. 실제 사실 수를 세고 메타데이터 제외 사유를 읽어 과도한 제외가 없는지 점검한다. 질문에 없는 사실이 반드시 inventory에 남는지 확인한다.

해시는 Python으로 계산해 출력만 확인한다. 파일 수정은 apply_patch를 사용한다.

```bash
python3 -c 'import sys,json; from pathlib import Path; sys.path.insert(0,".agents/skills/study-note-eli5/scripts"); from coverage_model import inventory_digest; p=Path("정리노트/0910-eli5-audited.coverage.json"); print(inventory_digest(json.loads(p.read_text(encoding="utf-8"))["inventory"]))'
```

- [ ] **Step 3: 한 개념 묶음씩 HTML과 mapping을 작성한다.** 아래 한 사이클을 각 concept에 적용한다. 각 사이클은 별도 체크 메모로 남긴다: 비유/그림/정확한 설명/조건 추가 → fact target 연결 → 생성 회상 1~3개 → 원본 문항·복습 링크 연결. 모든 사실의 설명을 먼저 제공하고 뒤에 문제를 배치한다. 범위 밖 막수송·발효·광합성은 현재 원본에서의 경계에 따라 보류한다. 원본에 이미 있는 ATP 사용 예처럼 부분 언급된 사실과 별도 과정의 전체 강의 범위를 구분한다.

사실 연결 예:

```html
<section id="concept-glycolysis" data-concept="glycolysis" data-role="teaching">
  <h2>해당과정: 포도당 하나를 둘로 나누기</h2>
  <p id="glycolysis-yield">포도당 하나당 ATP 2개를 먼저 쓰고 4개를 얻으므로 순생산은 2개입니다.</p>
  <p>숫자를 말할 때는 기준이 포도당 하나인지 함께 확인하세요.</p>
  <div data-role="recall" data-generated="true">
    <p>학습용 생성 질문: 총생산과 순생산이 다른 이유를 설명해 보세요.</p>
    <details><summary>설명 확인</summary><p data-part="model-answer">4개를 얻지만 먼저 2개를 사용했으므로 남는 것은 2개입니다.</p></details>
  </div>
</section>
```

- [ ] **Step 4: structure 검증을 실행해 모든 오류를 고친다.**

```bash
python3 .agents/skills/study-note-eli5/scripts/verify_guide.py 정리노트/0910-eli5-audited.html --coverage 정리노트/0910-eli5-audited.coverage.json --phase structure
```

Expected: exit 0와 STRUCTURE PASS. 원본 범위 문제를 해결하려고 문제 목록을 줄이지 않는다. 원본 오류는 conflicts에 공개한다.

- [ ] **Step 5: 양방향 의미 검토와 화면 검토를 수행한다.** 사실마다 원문 주장과 가이드 문장을 실제 대조해 fact_checks.evidence를 작성한다. 반드시 확인할 왜곡 유형: 효소 속도/평형, 온도 조건, 막/이중층 구분, 소기관의 구조·위치, 산화/환원 방향, ATP 총량/순량/기준 분자, H+ 이동 방향, 전자전달계/ATP 합성효소 역할. 같은 모델의 검토 기록은 독립적인 과학 검증이라고 부르지 않는다.

원본과 충돌하는 보기가 발견되면 재확인 근거와 visible conflict 카드를 만들며, 확정할 근거가 없으면 open 상태를 유지한다. 단순히 기존 정답 인덱스를 복사하지 않는다. 범위 밖 사실을 질문 근거로 추가하지 않는다.

desktop 1280px/mobile 390px/print에서 회상·정답 접힘, 방향 화살표와 라벨, 내부 링크, 페이지 자름, 인쇄 복원까지 확인한다. CSS 검사를 못 했으면 visual_audit를 pass로 기록하지 않는다.

- [ ] **Step 6: 최종 HTML 해시를 읽어 검토 버전을 고정하고 complete 검증을 실행한다.**

```bash
python3 -c 'import hashlib; from pathlib import Path; print(hashlib.sha256(Path("정리노트/0910-eli5-audited.html").read_bytes()).hexdigest())'
python3 .agents/skills/study-note-eli5/scripts/verify_guide.py 정리노트/0910-eli5-audited.html --coverage 정리노트/0910-eli5-audited.coverage.json --phase complete
python3 -m unittest discover -s tests -p 'test_study_guide_*.py' -v
python3 -m unittest discover -s tests -p 'test_note_*.py' -v
```

마지막 원천 노트 테스트는 실행 전부터 있었던 실패와 구분한다. 신규 코드와 무관한 실패를 무단 수정하지 않는다. complete가 실패하면 원인을 고치고 관련 검토를 다시 하거나, 미해결 사항과 함께 review-needed로 인계한다. 미해결 상태에서 목표 완료를 보고하지 않는다.

- [ ] **Step 7: 실제 검토 보고서를 기록한다.** 다음 제목 아래 각각 실제 값과 근거를 적는다.

```markdown
# 0910 ELI5 Pilot Review

## Inputs and scope
## Source blocks and fact coverage
## Included, review and deferred questions
## Source-to-guide and guide-to-source review
## Answer-key conflicts and resolutions
## Desktop, mobile and print observations
## Commands and actual exit codes
## Remaining limitations
```

- [ ] **Step 8: 인계 전 범위 제한 diff를 확인한다.**

```bash
git diff --check -- .agents/skills/study-note-eli5 tests/study_guide_fixture.py tests/test_study_guide_model.py tests/test_study_guide_html.py tests/test_study_guide_cli.py tests/test_study_guide_template.py 정리노트/CLAUDE.md 정리노트/0910-eli5-audited.html 정리노트/0910-eli5-audited.coverage.json docs/superpowers/reviews/2026-09-10-study-note-eli5-pilot.md
git status --short
```

미추적 파일은 git diff에 나오지 않으므로 파일 내용·검증 출력으로 별도 확인한다. 승인된 경우에만 새 pilot 세 파일을 정확히 지정해 커밋한다.

```bash
git add -- 정리노트/0910-eli5-audited.html 정리노트/0910-eli5-audited.coverage.json docs/superpowers/reviews/2026-09-10-study-note-eli5-pilot.md
git commit -m "test: validate complete 0910 study guide workflow"
```

인계: HTML의 절대 경로 링크, 실제 원본/복습/보류 문항 수, 원본 사실 수, 구조 검사 결과, 의미·시각 검토 결과, 답지 충돌·미해결 사항을 한국어로 간결하게 보고한다. 구조 검사 성공만으로 내용 완전성이나 학생의 시험 성과를 보장하지 않는다.

## 3. 계획 자체 검토

| 설계 요구 | 구현 작업 |
|---|---|
| 문제와 무관한 개념까지 전체 보존 | Task 1 원본 구간·사실, Task 6 원본 목록 대조 |
| 조건·수치·방향·예외 보존 | Task 1 qualifiers/evidence, Task 3 fact checks, Task 6 의미 검토 |
| 해설에만 존재하는 개념 방지 | Task 2 teaching target 검사 |
| 선행 지식과 복습 | Task 1 prerequisite 참조, Task 2 링크, Task 6 이전 문제 확인 |
| 회상·원본 문제·오답 복습 | Task 2 HTML 계약, Task 4 템플릿 |
| 답 숨김·인쇄·모바일 | Task 4 실제 UI 검증, Task 6 실사용 화면 검토 |
| 답지 충돌·범위 밖 보류 | Task 2 deferred, Task 3 conflict gate, Task 6 원본 확인 |
| 원본/HTML 변경 시 검토 갱신 | Task 1 source/inventory 해시, Task 3 review 해시 |
| 원천과 파생물 동기화 | Task 5 문서 역할과 스킬 절차 |
| 실제 사용 가능성 확인 | Task 6 한 회차 파일과 검토 보고서 |

자체 검토 시 각 코드 단계의 함수 이름·입출력 타입이 §2/Task Interfaces와 같은지 확인한다. 이 계획은 아직 코드를 실행한 결과가 아니다. 테스트 코드의 PASS 기대값과 실제 실행 결과를 혼동하지 않는다.

계획 작성 검토 결과: 설계 요구를 위 표의 6개 작업에 연결했다. Python 예제 16개는 AST 문법 검사를 통과했고, 코드 펜스 짝과 후행 공백을 확인했다. 구현·단위 테스트·화면 검증은 아직 실행하지 않았다. 데이터 의미 검증의 한계, 기존 자료의 dirty 상태, 원본 질문 원문 대조는 실행자가 확인할 항목으로 명시했다.
