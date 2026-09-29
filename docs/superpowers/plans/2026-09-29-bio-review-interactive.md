# 복습문제 선택·채점 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 기존 복습문제와 앞으로 생성하는 복습문제에서 보기 클릭 즉시 채점하고 모든 보기 아래에 해설을 표시한다.

**Architecture:** 정적 HTML을 원본으로 유지하고, Python 빌드 단계에서 보기·정답·해설의 연결 정보를 검증해 JSON으로 내장한다. 독립된 작은 JavaScript 모듈이 기존 DOM을 점진적으로 확장하고 기존 화면 관리 코드와 이벤트로 연동한다. 기존 8개 HTML과 향후 assemble 경로가 동일한 설치 함수를 사용한다.

**Tech Stack:** Python 표준 라이브러리, 기존 unittest, vanilla JavaScript/CSS, Node 내장 test runner, 실제 브라우저 QA. 새 런타임 패키지 없음.

**Spec:** `docs/superpowers/specs/2026-09-29-bio-review-interactive-design.md` — 구현 전 반드시 함께 읽는다.

## Global Constraints

- 기존 문제·보기·정답·해설·출처·그림·수식 내용을 보존한다.
- 해설의 ‘맞아요/틀려요’ 문구로 정답을 추론하지 않는다.
- 별도의 서버 API나 프런트엔드 프레임워크를 추가하지 않는다.
- 생성 HTML은 기능에 필요한 CSS와 JavaScript를 내장한다.
- 기존 Markdown의 정적 문제·풀이 읽기 기능을 유지한다.
- 타이머·무작위 출제·별도 오답노트·주관식 자동 채점은 제외한다.
- 시작 시 git status를 확인하고 기존 미추적 `tmp/`와 다른 계획 문서를 이번 변경에 포함하지 않는다.
- PowerShell에서 각 명령을 별도로 실행한다. 아래 경로는 저장소 루트 기준이다.
- 격리가 필요하면 실행 시 using-git-worktrees와 앱의 worktree 도구를 사용한다. 계획 작성 시에는 worktree를 만들지 않는다.

## Review Focus

1. ‘틀린 것’ 문항과 A~E/숫자 보기: 문장 참·거짓 대신 명시 정답으로 채점한다. Task 1·2 테스트로 고정한다.
2. 모호한 기출과 잘못된 인쇄 답: 분석된 기존 정답은 보존하되 모호한 문항은 단정 채점하지 않는다. Task 1·2·5에서 검증한다.
3. 손상된 localStorage, 저장 차단, 동일 날짜의 다른 파일, 수정된 문제: 화면은 동작하고 잘못된 기록이 복원되지 않는다. Task 2·3에서 검증한다.
4. 오른쪽 패널로 이동한 풀이, 그림·수식·중복 id: 현재 문제의 원본 노드만 이동하고 중복 복제하지 않는다. Task 3·5에서 검증한다.
5. JavaScript 꺼짐, 해설 매핑 누락, 재실행, Markdown/인쇄: 원래 읽기 기능이 보존되고 마이그레이션이 누적되지 않는다. Task 1·4·5에서 검증한다.

---

## 파일 책임과 변경 범위

| 파일 | 책임 |
|---|---|
| `.agents/skills/bio-review-pack/scripts/review_interaction.py` (신규) | 카드 분석, 해설 연결 검증, 버전 해시, CSS/JS/JSON 내장, 기존 파일 갱신 CLI |
| `.agents/skills/bio-review-pack/assets/review-interaction.js` (신규) | 정오답 판정, 저장, DOM 상호작용, 완료 이벤트 |
| `.agents/skills/bio-review-pack/assets/review-interaction.css` (신규) | 보기 버튼·선택·정답·해설·인쇄 표현 |
| `.agents/skills/bio-review-pack/assets/review-template.html` | 기존 푼 문제 상태와 제출·초기화 연결 |
| `.agents/skills/bio-review-pack/scripts/assemble.py` | build_review의 최종 HTML에 기능 내장 |
| `.agents/skills/bio-review-pack/scripts/check_html.py` | 내장 모델 오류를 기존 검사 결과에 포함 |
| `.agents/skills/bio-review-pack/references/interactive-overrides.json` (신규) | 파일명/문항 id별로 사람이 확인한 해설 위치와 모호성 사유 |
| `.agents/skills/bio-review-pack/tests/test_review_interaction.py` (신규) | 매핑·주입·원본 보존·멱등성·실제 문항 검사 |
| `.agents/skills/bio-review-pack/tests/test_review_interaction.cjs` (신규) | 실제 런타임의 채점·저장 순수 함수 검사 |
| `.agents/skills/bio-review-pack/tests/test_assemble.py` | 새 생성 경로와 비객관식 호환성 |
| `.agents/skills/bio-review-pack/tests/test_check_html.py` | 잘못된 연결 검출 |
| `.agents/skills/bio-review-pack/references/content-rules.md` | 새 카드의 명시적 보기·해설 연결 규약 |
| `.agents/skills/bio-review-pack/references/browser-check.md` | 클릭·복원·접근성·인쇄 확인 절차 |
| `.agents/skills/bio-review-pack/SKILL.md` | 작성 후 데이터 및 인터랙션 검사 단계 연결 |
| `docs/superpowers/reviews/2026-09-29-bio-review-interactive.md` (신규) | 실제 8개 파일 검사 결과와 브라우저 QA 증거 |

갱신할 HTML은 아래 8개로 한정한다. Markdown은 원문 변경이 필요하지 않으면 수정하지 않는다.

```text
복습노트/0901/복습문제_0901_Biomolecules_and_Cells.html
복습노트/0903/복습문제_0903_Biomolecules_and_Cells.html
복습노트/0908/복습문제_0908_Biomolecules_and_Cells.html
복습노트/0910/복습문제_0910_Cells_and_Cellular_Respiration.html
복습노트/0915/복습문제_0915_Cellular_Respiration_and_Photosynthesis.html
복습노트/0917/복습문제_0917_Cell_Division.html
복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.html
복습노트/0929/복습문제_0929_Heredity.html
```

## 데이터 계약

Python `build_model(source: str, document_id: str, overrides: dict | None = None) -> dict`는 다음 구조를 반환한다. `index`는 `.choices` 직계 li의 0-based 위치, `diagnostic`은 해당 카드의 `details.solution ol.steps` 직계 li의 0-based 위치이다.

```json
{
  "schema": 1,
  "documentId": "복습문제_0101_Mini_Test.html",
  "cards": {
    "p1": {
      "version": "sha256 hex digest",
      "answer": "2",
      "mode": "single",
      "notice": "",
      "options": [
        {"id": "1", "index": 0, "diagnostic": 0},
        {"id": "2", "index": 1, "diagnostic": 1}
      ]
    }
  },
  "skipped": [],
  "errors": []
}
```

- `mode`는 `single` 또는 `ambiguous`. `ambiguous`는 사람이 확인한 `notice`가 필수다.
- `skipped`는 보기가 없는 카드 id 배열. `errors`는 `{cardId, reason}` 배열. 오류 카드는 `cards`에 넣지 않는다.
- overrides 구조: `{documentId: {cardId: {"mode":"ambiguous", "notice":"원문에 있는 모호성 설명", "diagnostics":{"1":0,"2":1}}}}`. `diagnostics`는 해설의 표준 접두사로 매핑할 수 없을 때만 사용한다. 모든 위치와 일대일 대응을 재검증한다.
- 향후 작성 카드는 보기 li에 `data-choice="1"`, 해설 li에 `data-explains="1"`을 넣는다. `article`에 `data-grade-mode="ambiguous"`와 `data-grade-notice`로 모호성을 명시할 수 있다.
- 정답은 `.answer`의 `정답: (2)` 또는 `정답: B`에서 엄격하게 읽는다. 숫자는 괄호 없이 정규화한다. 새 모호성 속성이 없고 의심 문구가 있으면 검토 오류로 내보내고 추정 채점하지 않는다.
- 버전은 해당 카드의 문제·정답·풀이 원본과 최종 연결 정보를 SHA-256으로 계산한다. 질문만 같아도 정답이나 해설 수정 시 무효화된다.

### Task 1: 실제 카드에서 채점 모델 추출·검증

**Files:** 신규 `scripts/review_interaction.py`, 신규 `tests/test_review_interaction.py`, 신규 `references/interactive-overrides.json` (모두 위 스킬 폴더 기준).

**Interfaces:**
- Consumes: 기존 `.problem .choices`, `details.solution ol.steps`, `.answer`.
- Produces: `build_model(source, document_id, overrides=None)`와 `validate_model(source: str, model: dict) -> list[dict]`.
- Produces: CLI `review_interaction.py --root 복습노트 --audit`; JSON으로 파일별 총 카드 수, 객관식 수, skipped, errors를 출력한다. 미해결 오류가 있으면 종료 코드 1.

- [x] **Step 1: 실패 테스트 추가.** unittest 파일에 다음 fixture와 사례를 추가한다.

```python
import unittest
from _util import SKILL
from review_interaction import build_model

CARD = '''<article class="card" id="p1"><div class="problem">
<p>틀린 것을 고르시오.</p><ul class="choices">
<li>(1) 옳은 설명</li><li>(2) 틀린 설명</li></ul></div>
<details class="solution"><summary>풀이 보기</summary><ol class="steps">
<li>(1) 맞는 설명이므로 답이 아니에요.</li>
<li>(2) 틀린 설명이므로 답이에요.</li>
<li>수업과의 연결: 분류</li></ol><p class="answer">정답: (2)</p>
</details></article>'''

class TestModel(unittest.TestCase):
    def test_negative_question(self):
        model = build_model(CARD, 'test.html')
        self.assertEqual(model['errors'], [])
        self.assertEqual(model['cards']['p1']['answer'], '2')
        self.assertEqual([o['diagnostic'] for o in model['cards']['p1']['options']], [0, 1])

    def test_letter_choices(self):
        model = build_model(CARD.replace('(1)', 'A.').replace('(2)', 'B.').replace('정답: B.', '정답: B'), 'test.html')
        self.assertEqual(model['cards']['p1']['answer'], 'B')

    def test_missing_diagnostic_fails_closed(self):
        source = CARD.replace('<li>(2) 틀린 설명이므로 답이에요.</li>', '')
        model = build_model(source, 'test.html')
        self.assertNotIn('p1', model['cards'])
        self.assertEqual(model['errors'][0]['cardId'], 'p1')

    def test_no_choices_stays_static(self):
        model = build_model('<article class="card" id="p1"><p>빈칸</p></article>', 'test.html')
        self.assertEqual(model['skipped'], ['p1'])

    def test_corrected_answer_invalidates_record(self):
        a = build_model(CARD, 'test.html')['cards']['p1']['version']
        b = build_model(CARD.replace('정답: (2)', '정답: (1)'), 'test.html')['cards']['p1']['version']
        self.assertNotEqual(a, b)

    def test_ambiguous_notice_required(self):
        override = {'test.html': {'p1': {'mode': 'ambiguous', 'notice': '두 해석이 가능해요.'}}}
        card = build_model(CARD, 'test.html', override)['cards']['p1']
        self.assertEqual(card['mode'], 'ambiguous')
        self.assertEqual(card['notice'], '두 해석이 가능해요.')
```

- [x] **Step 2: 실패 확인.** `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_review_interaction.py -v` → 모듈 없음으로 실패해야 한다.
- [x] **Step 3: 파서와 순수 모델 구현.** 기존 html2md.Builder의 Node 탐색을 활용하되 원본 직렬화에 쓰지 않는다. choices와 steps의 직계 li만 대상으로 한다. 명시 속성을 우선하고 없으면 아래 접두사로 연결한다. 정답 없음/중복 보기 id/누락 또는 중복 해설/범위 밖 override/정답이 보기에 없음은 카드 오류로 반환한다. 원문 정답과 manifest 답을 혼동하지 않는다.

```python
import hashlib
import json
import re

LABEL = re.compile(r'^\s*(?:\((\d+)\)|([A-Z])[.)])\s*')
ANSWER = re.compile(r'^\s*정답:\s*(?:\((\d+)\)|([A-Z]))\s*$')

def content_version(card_source, mapping):
    payload = card_source + json.dumps(mapping, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()
```

수업 연결 li는 접두사가 없으므로 매핑에서 제외한다. ‘인쇄된 답’, ‘모호’, ‘모두 가능’, ‘단일 정답’ 등 경고 후보는 자동 확정하지 않고 --audit에서 수동 검토 대상으로 출력한다. 단순히 인쇄 답과 분석 답이 다른 문항은 기존 분석 답을 보존하며 반드시 ambiguous로 만들 필요는 없다.

- [x] **Step 4: 8개 날짜 audit 실행.** `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --audit`. 출력의 모든 오류와 모호성 후보를 실제 풀이와 대조해 overrides에 기록한다. 기존 HTML/MD의 학습 내용은 아직 수정하지 않는다. 보기별 해설 자체가 없는 경우에는 현재 강의노트·교과서 근거를 확인해서 원문 해설 보완이 필요한 문항으로 기록하고 Task 5에서 처리한다.
- [x] **Step 5: 테스트 통과 후 커밋.** 위 unittest 명령 PASS 확인. `git add .agents/skills/bio-review-pack/scripts/review_interaction.py .agents/skills/bio-review-pack/tests/test_review_interaction.py .agents/skills/bio-review-pack/references/interactive-overrides.json` 후 `git commit -m "feat: validate review choice and explanation mappings"`.

### Task 2: 채점·저장 규칙을 실제 런타임에 구현

**Files:** 신규 `assets/review-interaction.js`, 신규 `tests/test_review_interaction.cjs`.

**Interfaces:**
- Consumes: Task 1의 card model.
- Produces: `grade(card, selected) -> 'correct'|'incorrect'|'ambiguous'|null`, `storageKey(documentId, cardId) -> string`, `readAttempt(storage, key, card) -> string|null`, `writeAttempt(storage, key, card, selected) -> void`.
- 저장 값: `{version: card.version, selected: string}`. selected=null은 removeItem. CommonJS 테스트용 exports와 브라우저 전역 `ReviewInteraction`에 동일한 함수를 제공한다.

- [x] **Step 1: 실제 모듈을 가져오는 실패 테스트 작성.**

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../assets/review-interaction.js');
const card = {version:'v1', mode:'single', answer:'2', options:[{id:'1'},{id:'2'}]};
test('정답 표기를 기준으로 채점한다', () => {
  assert.equal(api.grade(card,'1'),'incorrect');
  assert.equal(api.grade(card,'2'),'correct');
  assert.equal(api.grade(card,'X'),null);
  assert.equal(api.grade({...card,mode:'ambiguous'},'1'),'ambiguous');
});
test('손상·구버전·없는 보기는 복원하지 않는다', () => {
  for (const raw of ['{', 'null', '[]', '{"version":"old","selected":"2"}', '{"version":"v1","selected":"X"}']) {
    assert.equal(api.readAttempt({getItem:()=>raw}, 'k', card),null);
  }
});
test('저장 차단이 풀이를 막지 않는다', () => {
  const storage = {getItem(){throw Error('blocked')},setItem(){throw Error('blocked')},removeItem(){throw Error('blocked')}};
  assert.equal(api.readAttempt(storage,'k',card),null);
  assert.doesNotThrow(()=>api.writeAttempt(storage,'k',card,'2'));
  assert.doesNotThrow(()=>api.writeAttempt(storage,'k',card,null));
});
test('동일 문항 id라도 파일이 다르면 분리한다', () => {
  assert.notEqual(api.storageKey('a.html','p1'),api.storageKey('b.html','p1'));
});
test('선택 기록과 초기화', () => {
  const data = new Map();
  const storage = {getItem:k=>data.get(k),setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)};
  api.writeAttempt(storage,'k',card,'2');
  assert.equal(api.readAttempt(storage,'k',card),'2');
  api.writeAttempt(storage,'k',card,null);
  assert.equal(api.readAttempt(storage,'k',card),null);
});
```

- [x] **Step 2: 실패 확인.** `node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs` → 모듈 없음.
- [x] **Step 3: 함수 구현.** document/window를 모듈 로드 시 무조건 참조하지 않는다. 브라우저 localStorage 속성 자체 접근도 try/catch로 감싼다.

```javascript
function grade(card, selected) {
  if (!card.options.some(o => o.id === selected)) return null;
  if (card.mode === 'ambiguous') return 'ambiguous';
  return selected === card.answer ? 'correct' : 'incorrect';
}
function storageKey(documentId, cardId) {
  return 'od-review-attempt:v1:' + encodeURIComponent(documentId) + ':' + encodeURIComponent(cardId);
}
function readAttempt(storage, key, card) {
  try {
    const value = JSON.parse(storage.getItem(key));
    return value && value.version === card.version && grade(card, value.selected) !== null ? value.selected : null;
  } catch { return null; }
}
function writeAttempt(storage, key, card, selected) {
  try {
    if (selected === null) storage.removeItem(key);
    else storage.setItem(key, JSON.stringify({version:card.version, selected}));
  } catch {}
}
```

- [x] **Step 4: 같은 Node 명령 PASS 확인.** 테스트 함수와 브라우저 함수가 같은 구현을 사용함을 확인한다.
- [x] **Step 5: 커밋.** `git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/tests/test_review_interaction.cjs` 후 `git commit -m "feat: add review grading and persistent attempts"`.

### Task 3: 클릭·보기별 해설 UI와 기존 패널 연결

**Files:** 수정 `assets/review-interaction.js`, 신규 `assets/review-interaction.css`, 수정 `assets/review-template.html:596-639`.

**Interfaces:**
- Consumes: `mount(root: Document, model: dict, storage: Storage|null) -> void`를 JS 공개 API에 추가한다. 호출은 DOMContentLoaded 이후 한 번이다.
- Produces: `document`에 `od:answer` CustomEvent, detail `{id: string, selected: string|null, result: string|null, restored: boolean}`.
- DOM 계약: `.review-choice` 버튼, `.review-diagnostic` 해설, `.review-status[role=status]`, `.review-reset` 버튼, 활성 카드 `.review-ready`.

- [x] **Step 1: 실제 브라우저의 실패 시나리오 기록.** mini-run을 임시 디렉터리에 assemble하고 로컬 HTTP로 연다. p2에서 보기 클릭이 안 되는 현재 상태를 확인한다. 자동 브라우저 도구가 있으면 해당 도구의 문서를 읽고 사용한다. QA에서 native 버튼 역할로 보기 (1)을 클릭하고 결과·모든 해설 수를 검사할 것이다.
- [x] **Step 2: mount 구현.** model의 모든 DOM 위치·개수·정답을 먼저 검증하고 성공한 카드만 변경한다. setupReview가 이미 details를 옮기므로 `card`에서 다시 찾지 말고, 기존 코드가 생성한 aid에 `data-card-id`를 붙여 찾는다. 카드 내부 solution도 fallback으로 허용한다.

```javascript
const aid = document.createElement('div');
aid.className = 'aid';
aid.dataset.cardId = card.id;
// 기존 setupReview의 g 생성부에서 위 dataset을 설정한다.
```

각 원래 보기 li 안에 button을 만들고 기존 childNodes를 이동한다. 각 대응 해설 li는 div.review-diagnostic으로 감싸기보다 원본 li 노드를 그대로 유지해 별도의 ol.review-diagnostics 한 개를 해당 보기 li 아래에 삽입한다. ol의 목록 표시는 CSS로 숨긴다. 이 방식으로 그림·링크·수식·id가 복제되지 않는다. `<button>` 내부에 다른 버튼/링크가 있는 보기나 블록 표가 있는 보기는 전용 선택 버튼을 문장 앞에 두고 aria-describedby로 원문을 연결한다.

```javascript
function announce(id, selected, result, restored = false) {
  document.dispatchEvent(new CustomEvent('od:answer', {
    detail: {id, selected, result, restored}
  }));
}
```

첫 클릭에서 선택을 고정하고 전체 버튼에 aria-disabled=true를 적용한다. 이벤트 핸들러도 재선택을 차단한다. 결과는 role=status로 알리고 해설을 모두 표시한다. ‘정답/정답 아님’은 문제의 답 여부를 뜻하며 원문 내용의 참·거짓 문구는 그대로 보존한다. ambiguous는 ‘단일 정답 판정 주의’와 notice, ‘출제 의도상 답’만 표시한다.

- [x] **Step 3: 숨김·초기화·인쇄 스타일 구현.** 검증에 성공한 카드에만 클래스를 붙여 초기 해설을 숨긴다. 원본 solution은 CSS의 전역 `.js`만으로 숨기지 않는다. 초기화 시 원래 solution도 닫고 수업 연결 및 이의사항을 다시 숨긴다. 제출 후 잔여 solution을 ‘추가 해설’로 열어 둔다. 초기화 후 첫 선택 버튼으로 포커스를 옮긴다.

```css
.review-choice { width:100%; text-align:left; font:inherit; color:inherit; background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:12px; cursor:pointer; }
.review-choice:focus-visible { outline:3px solid var(--accent); outline-offset:3px; }
.review-diagnostics { list-style:none; padding:0; margin:8px 0 16px; }
.review-diagnostic { color:var(--ink-2); }
.review-status { margin-block:12px; }
.review-reset { min-height:44px; }
@media print {
  .review-reset, .review-status { display:none; }
  .review-diagnostic[hidden] { display:list-item !important; }
  .review-choice { border:0; padding:0; }
}
```

인쇄 때 추가 해설도 숨겨지지 않도록 print 규칙에서 solution의 hidden을 해제하고, 기존 details 인쇄 규칙과 함께 확인한다. 화면에 표시하는 문구는 모두 한국어로 쓴다.

- [x] **Step 4: 기존 상태 이벤트 연결.** setupReview에 listener를 추가한다. 클릭 시 solved.add(id), 다시 풀기 시 solved.delete(id), 저장·paintBtn·markToc를 호출한다. 이전 수동 완료 표시는 모델 초기화만으로 제거하지 않는다. restored=true도 완료 상태를 복원한다. 선택 기록이 있는 문항에서 수동 표시 해제를 누르면 선택 기록은 유지하고 완료 표시만 바꾸며, 다음 제출/재도전에서 다시 동기화한다.

```javascript
document.addEventListener('od:answer', ({detail}) => {
  if (!cards.some(c => c.id === detail.id)) return;
  if (detail.selected === null) solved.delete(detail.id);
  else solved.add(detail.id);
  store.set(KEY, Array.from(solved));
  if (curId) paintBtn();
  markToc(solved, cards.length, '푼 문제');
});
```

- [x] **Step 5: 브라우저 확인.** p2의 (1) 선택 → ‘정답이 아니에요’, 정답 (2), 모든 3개 해설 표시; 다른 보기 클릭 → 변경 없음; 다시 풀기 → 해설 숨김·선택 없음·완료 수 감소; (2) 선택 → ‘정답이에요’; 새로고침 → (2) 복원. Tab/Enter/Space, 화면 이동 후 재진입, 390px 너비와 다크모드도 확인한다. 브라우저 콘솔 오류 0, 중복 id 0을 확인한다.
- [x] **Step 6: Node 테스트 재실행 후 커밋.** `git add .agents/skills/bio-review-pack/assets/review-interaction.js .agents/skills/bio-review-pack/assets/review-interaction.css .agents/skills/bio-review-pack/assets/review-template.html` 후 `git commit -m "feat: show explanations when a review choice is selected"`.

### Task 4: 동일 설치 함수를 신규 생성과 기존 HTML에 연결

**Files:** 수정 `scripts/review_interaction.py`, `scripts/assemble.py:79-100`, `scripts/check_html.py:307-319`, `tests/test_review_interaction.py`, `tests/test_assemble.py`, `tests/test_check_html.py`.

**Interfaces:**
- Produces: `install(source: str, document_id: str, overrides: dict | None = None, strict: bool = True) -> str`.
- 내장 영역: `<!-- review-interaction:start -->`와 `<!-- review-interaction:end -->` 사이의 style, JSON script, runtime script, 초기화 script. 본문 끝에 넣는다.
- strict=True에서 errors가 있으면 ValueError로 중단. strict=False는 오류 카드만 정적 유지. 새 생성과 최종 배포는 strict=True.
- CLI에 `--write` 추가. 8개 결과를 메모리에서 모두 검증한 뒤 쓰며, 출력 외 영역과 그림은 변경하지 않는다. --audit는 읽기 전용이다.

- [x] **Step 1: 실패 테스트 추가.** 다음 테스트를 기존 TestModel에 추가한다.

```python
def test_install_is_idempotent_and_keeps_content(self):
    from review_interaction import install
    source = '<html><body>' + CARD + '</body></html>'
    output = install(source, 'test.html')
    self.assertEqual(install(output, 'test.html'), output)
    self.assertIn(CARD, output)
    self.assertEqual(output.count('id="review-interaction-model"'), 1)

def test_script_closing_text_is_safe(self):
    from review_interaction import install
    override = {'test.html': {'p1': {'mode':'ambiguous','notice':'</script><script>alert(1)</script>'}}}
    output = install('<body>' + CARD + '</body>', 'test.html', override)
    self.assertNotIn('"notice": "</script>', output)
    self.assertIn('\\u003c/script>', output)
```

assemble 테스트에는 `self.assertIn('id="review-interaction-model"', self.review_html)`와 `self.assertNotIn('id="review-interaction-model"', self.note_html)`를 추가한다. checker 테스트는 설치된 모델의 answer를 존재하지 않는 X로 바꾼 source에서 검사 오류가 발생하도록 작성한다.

- [x] **Step 2: Python 스킬 테스트 실행, 새 기대값 실패 확인.** `python -m unittest discover -s .agents/skills/bio-review-pack/tests -v`.
- [x] **Step 3: 설치 구현.** source의 기존 marker 영역만 제거하고 다시 설치한다. JSON은 아래처럼 `<`를 escape하고 application/json으로 내장한다. assemble의 split_scripts가 JSON을 옮기거나 제거하지 않도록 build_review의 fill 완료 후 install을 호출한다. 문서 id는 manifest_mod.review_name(m)이다.

```python
payload = json.dumps(model, ensure_ascii=False, sort_keys=True).replace('<', '\\u003c')
model_script = '<script id="review-interaction-model" type="application/json">' + payload + '</script>'
```

runtime은 DOMContentLoaded를 기다려 기존 setupReview 초기화 뒤 mount한다. JSON parse 또는 mount의 카드별 오류는 해당 카드의 원래 풀이를 유지한다. 노드를 이동하기 전에 전체 참조를 확보하고, 실패하면 원래 위치로 복원할 수 있도록 부모와 nextSibling을 보관한다. model Script의 내용만 parse하고 eval하지 않는다. 기존 HTML에는 setupReview의 aid.dataset와 완료 listener도 명시적으로 패치한다. 이미 패치되어 있으면 건너뛰고, 대상 함수 구조가 예상과 다르면 파일명과 오류를 출력해 중단한다. 광범위한 HTML 재직렬화나 minify는 하지 않는다.

- [x] **Step 4: 검사기에 연결.** check_file와 check_pack 경로 모두 내장 모델이 있으면 validate_model을 실행한다. 구버전 정적 HTML은 기존 검사 그대로 통과한다. 모델 속 위치·정답·버전·문항 집합이 실제 HTML과 일치하는지 비교한다. 모델에 없는 객관식은 새 인터랙티브 파일에서 오류로 보고한다.
- [x] **Step 5: Python·Node 테스트 PASS 확인 후 커밋.** `git add .agents/skills/bio-review-pack/scripts/review_interaction.py .agents/skills/bio-review-pack/scripts/assemble.py .agents/skills/bio-review-pack/scripts/check_html.py .agents/skills/bio-review-pack/tests/test_review_interaction.py .agents/skills/bio-review-pack/tests/test_assemble.py .agents/skills/bio-review-pack/tests/test_check_html.py` 후 `git commit -m "feat: embed interactive reviews in generated and existing packs"`.

### Task 5: 8개 기존 팩 갱신·내용 보존·생성 규칙 문서화

**Files:** 위 8개 HTML, 필요 시 해설을 보완한 날짜의 복습문제 Markdown, `references/interactive-overrides.json`, `references/content-rules.md`, `references/browser-check.md`, `SKILL.md`, `tests/test_review_interaction.py`, 신규 검증 보고서.

**Interfaces:** Consumes Task 4 CLI/install 및 check_html. Produces 객관식 errors=0인 8개 팩, 실제 브라우저 검증 보고서.

- [x] **Step 1: 실제 팩의 모델 검사 테스트 추가.**

```python
def test_all_existing_review_cards_have_verified_mapping(self):
    import json
    from _util import REPO
    overrides = json.loads((SKILL / 'references/interactive-overrides.json').read_text(encoding='utf-8'))
    files = sorted((REPO / '복습노트').glob('*/복습문제_*.html'))
    self.assertGreaterEqual(len(files), 8)
    for path in files:
        with self.subTest(file=path.name):
            model = build_model(path.read_text(encoding='utf-8'), path.name, overrides)
            self.assertEqual(model['errors'], [])
            for card in model['cards'].values():
                self.assertEqual(len({o['diagnostic'] for o in card['options']}), len(card['options']))
```

- [x] **Step 2: audit 예외 정리.** 전체 원문 해설을 확인해 부정형 질문, 기출 답 오류, 모호한 문항을 각각 분류한다. 알려진 0929의 ‘다면발현 예외’, ‘모두 맞다/역위’, ‘O형에 대해 공동우성’ 문항은 반드시 검토한다. 누락 해설은 로컬 교재·강의노트 근거로만 보완하고 해당 Markdown에도 같은 문장을 반영한다. 모든 객관식의 매핑이 완성되기 전 write를 실행하지 않는다.
- [x] **Step 3: 생성 규칙과 검증 절차 기록.** content-rules에 아래 카드 속성 예시와 일대일 해설 규칙을 추가한다. SKILL.md 검사 단계에서 매핑 오류를 해결한 뒤 브라우저 테스트하도록 연결한다.

```html
<ul class="choices">
  <li data-choice="1">(1) 핵</li>
  <li data-choice="2">(2) 동원체</li>
</ul>
<details class="solution"><summary>풀이 보기</summary>
  <ol class="steps">
    <li data-explains="1">(1) 핵은 염색체를 담는 소기관이어서 답이 아니에요.</li>
    <li data-explains="2">(2) 자매염색분체가 연결되는 부위이므로 답이에요.</li>
  </ol>
  <p class="answer">정답: (2)</p>
</details>
```

- [x] **Step 4: 전체 갱신.** `python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --write`. 그 뒤 같은 명령을 다시 실행해 추가 diff가 없음을 확인한다. git diff에서 문제 본문·원문 그림·정답이 무관하게 변경되지 않았는지 확인한다. 예상 237카드는 최초 기준이며 동시 추가 문항이 있으면 새 수치를 보고하고 사용자 변경을 덮어쓰지 않는다.
- [x] **Step 5: 내용 보존과 자동 검사 실행.**

```powershell
python -m unittest discover -s .agents/skills/bio-review-pack/tests -v
node --test .agents/skills/bio-review-pack/tests/test_review_interaction.cjs
python .agents/skills/bio-review-pack/scripts/review_interaction.py --root 복습노트 --audit
Get-ChildItem -LiteralPath 복습노트 -Recurse -Filter '복습문제_*.html' | ForEach-Object { python .agents/skills/bio-review-pack/scripts/check_html.py $_.FullName; if ($LASTEXITCODE -ne 0) { throw "HTML 검사 실패: $($_.FullName)" } }
git diff --check
```

MD 보존 검사는 html2md.Builder로 설치 전후 card subtree의 텍스트·img src·svg id를 비교한다. 기능 설치는 article 밖 영역과 setupReview만 바꾸므로 각 article 문자열이 동일해야 한다. 승인된 해설 보완만 예외로 명시한다. html2md 변환 확인이 필요하면 임시 팩 복사본에서 기존 CLI의 --check를 실행한다. 원본 figure 디렉터리에는 변환 부작용을 만들지 않는다.

- [x] **Step 6: 실제 브라우저 QA.** 0903 A~E 문항, 0901 부정형 문항, 0929 모호한 문항, 그림·수식 문항, 보기가 없는 문항을 각각 확인한다. Task 3 전체 시나리오에 더해 저장 차단, 잘못된 JSON 저장, 다른 파일 동일 id, 문항 버전 변경, JavaScript 꺼짐, 인쇄 미리보기, 390px/1280px, 밝은/어두운 테마를 확인한다. 정답 선택/오답 선택 때 모든 보기 아래 해설이 보이는 화면을 증거로 남긴다. 기능이 검증되지 않은 환경은 통과라고 쓰지 않는다.
- [x] **Step 7: 결과 보고서 작성 및 커밋.** 8개 파일별 전체/객관식/정적/모호 문항 수, 테스트 명령과 결과, 브라우저 확인 환경, 해설 보완 목록을 검증 보고서에 기록한다. `git add`는 이 Task의 실제 변경 파일을 각각 지정하고 `git commit -m "feat: enable interactive practice across biology review packs"`로 저장한다. 다른 작업의 미추적 파일은 stage하지 않는다.

## 완료 기준과 인계

- 8개 HTML의 모든 객관식이 클릭 가능하며 보기별 해설 누락이 없다.
- 새 mini-run 생성 결과도 같은 인터랙션을 제공한다.
- 정답·오답·모호한 문항·재도전·복원·비JS·인쇄 검증 증거가 있다.
- 기존 학습 내용과 정적 Markdown이 보존되어 있다.
- 실행 방식: Native(사용자 승인). 데이터 계약, 기존 DOM, 생성기를 차례로 연결하는 5개 작업이므로 같은 구현자가 맥락을 유지하기 좋다. 최종 별도 리뷰 후 결과를 사용자에게 보고한다.

## 계획 자체 점검

- 범위·클릭·모든 해설·상태·접근성·모호성·정적 fallback·향후 생성 요구를 Task 1~5에 배치했다.
- 함수 이름과 모델 필드를 Task 사이에서 동일하게 사용했다.
- 다섯 Review Focus를 각각 자동 검사 또는 구체적인 실제 브라우저 시나리오에 배치했다.
- 코드 및 기존 학습 산출물은 계획 작성 단계에서 수정하지 않는다.
