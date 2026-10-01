# bio-review-pack 웹과제형 변형 연습 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 1~3장 웹과제 분석으로 얻은 출제 유형(쌍둥이·그림·상황 전이·ㄱㄴㄷ·용어 바꿔 쓰기)을 `bio-review-pack`의 partC 규칙에 넣고, 0910·0915·0917·0922·0929 팩을 새 규칙으로 다시 만든다.

**Architecture:** 코드가 아니라 스킬 규칙 문서를 바꾼다. 새 참조 파일 `references/webquiz-style.md`가 유형·할당을 정하고, `problem-selection.md` 6절·`card-rules.md`·`SKILL.md`가 그 파일을 따르게 한다. 규칙 문장은 새 테스트 파일 `tests/test_webquiz_rules.py`가 고정한다. 마지막 태스크는 스킬을 실제로 다시 실행하는 운영 작업이다.

**Tech Stack:** Markdown(스킬 규칙), Python 3 `unittest`(문서 규칙 테스트), 기존 `bio-review-pack` 파이프라인.

**Spec:** `docs/superpowers/specs/2026-10-01-bio-review-webquiz-variants-design.md`

## Global Constraints

- 스킬 원본 경로는 `.agents/skills/bio-review-pack/` (`.claude/skills/bio-review-pack`은 심볼릭 링크). 모든 수정은 원본 경로에서.
- partC 합계 **10~15개**, 토픽당 최대 3개. 못 채우면 만든 만큼 + 보고서 사유.
- 유형 최소: 쌍둥이 ≥2 · 그림 ≥2 · 상황 전이 ≥2 · ㄱㄴㄷ ≥1 · 용어 바꿔 쓰기 ≥2(겹쳐도 됨) · 부정형 약 1/3.
- 쌍둥이는 **발문만** 원문 그대로, 보기는 새로 쓴다.
- 보기 5개 기본(개념상 안 되면 4개), 변형 보기 번호는 `(1)~(n)` 유지.
- manifest 스키마(`scripts/manifest.py`), `assemble.py`, `check_html.py`, 채점 JS는 바꾸지 않는다.
- 규칙 문서에 원문자(①~⑳)를 쓰지 않는다(`test_no_circled_numbers_in_rules`). 새 참조 파일은 SKILL.md에서 `references/webquiz-style.md`로 언급해야 한다(`test_every_reference_is_used`).
- 학생용 HTML·MD에 STT 녹음 시각을 넣지 않는다(기존 규칙).
- 커밋 메시지 끝: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Review Focus

1. **포함된 기출이 없거나 모두 쓸 수 없는 범위:** 쌍둥이를 지어내지 않고 0개 + 사유. Task 1 테스트가 `webquiz-style.md` §4의 "만들 수 없으면 0개" 문장을 고정한다.
2. **같은 팩 partA에 이미 정답이 바뀐 웹과제 원문이 있음(0910·0915 재생성 시 2장 q1·q8·q10):** 그 기출은 쌍둥이 재료로 쓰지 않는다. Task 1 테스트가 §3 "피할 것"의 이 문장을 고정한다.
3. **쌍둥이 발문에 금지어가 있음:** 발문을 원문 그대로 쓰므로 금지어 검사에 걸린다. 그런 기출은 고르지 않는다. Task 1 테스트로 고정한다.
4. **좁은 범위에서 10개를 못 채움:** 범위 밖이나 같은 문제 반복으로 채우지 않는다. Task 1·2 테스트가 "못 채우면" 문장을 고정한다.
5. **재생성이 사용자 자료를 덮어씀:** `복습노트/0922/풀이기록/`과 커밋 72704c8의 손 수정(0922 P29 우성 유전병 보기)이 사라지면 안 된다. Task 4의 해시 대조와 재적용 단계가 지킨다.

---

## File map

- Create `.agents/skills/bio-review-pack/references/webquiz-style.md`: 웹과제 출제 유형과 partC 할당 기준(단일 책임).
- Create `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`: 위 파일과 관련 규칙 문장을 고정하는 테스트.
- Modify `.agents/skills/bio-review-pack/references/problem-selection.md:80-86` (6절).
- Modify `.agents/skills/bio-review-pack/references/card-rules.md:41` (변형 카드 규칙).
- Modify `.agents/skills/bio-review-pack/SKILL.md:93`, `:182`, `:192` (2단계 partC 줄, 9단계 보고서, 보고 뒤 안내).
- 재생성 산출물: `복습노트/0929/`, `0910/`, `0915/`, `0917/`, `0922/`의 정리노트·복습문제 html/md, `figures_<range>/`.

테스트 실행 명령(저장소 루트에서):

```bash
python3 -m pytest .agents/skills/bio-review-pack/tests -q
```

`pytest`가 없으면 `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p 'test_*.py'`.

---

### Task 1: 웹과제 출제 유형 참조 파일

**Files:**
- Create: `.agents/skills/bio-review-pack/references/webquiz-style.md`
- Create: `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`
- Modify: `.agents/skills/bio-review-pack/SKILL.md:93`

**Interfaces:**
- Consumes: 없음
- Produces: 파일 `references/webquiz-style.md`의 절 제목 `## 1. 출처`, `## 2. 수치`, `## 3. 유형`, `## 4. 할당`, `## 5. 갱신`과 유형 제목 `### 쌍둥이`, `### 그림`, `### 상황 전이`, `### ㄱㄴㄷ`, `### 용어 바꿔 쓰기`. Task 2·3이 이 이름(`webquiz-style.md §4`, 유형 이름)을 문장에서 가리킨다. 테스트 도우미 `section(text, heading) -> str`를 Task 2·3 테스트가 재사용한다.

- [ ] **Step 1: 실패하는 테스트 쓰기**

`.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`:

```python
"""웹과제형 변형 연습 규칙(webquiz-style.md와 관련 규칙 문장)을 고정한다."""

import re
import unittest

from _util import SKILL

REFS = SKILL / "references"
TYPES = ("쌍둥이", "그림", "상황 전이", "ㄱㄴㄷ", "용어 바꿔 쓰기")


def read(path):
    return path.read_text(encoding="utf-8")


def section(text, heading):
    """`heading` 줄부터 같은 수준 이상의 다음 제목 전까지."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading)
    rest = text[start + len(heading):]
    m = re.search(rf"\n#{{1,{level}}} ", rest)
    return heading + (rest[: m.start()] if m else rest)


class TestWebquizStyle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(REFS / "webquiz-style.md")

    def test_sections(self):
        for h in ("## 1. 출처", "## 2. 수치", "## 3. 유형", "## 4. 할당", "## 5. 갱신"):
            with self.subTest(h=h):
                self.assertIn(f"\n{h}\n", self.text)

    def test_types_have_four_parts(self):
        body = section(self.text, "## 3. 유형")
        for t in TYPES:
            with self.subTest(t=t):
                part = section(body, f"### {t}")
                for label in ("정의:", "실제 예:", "만드는 법:", "피할 것:"):
                    self.assertIn(label, part)

    def test_evidence_numbers(self):
        body = section(self.text, "## 2. 수치")
        for s in ("46", "70%", "33%", "17%"):
            with self.subTest(s=s):
                self.assertIn(s, body)

    def test_twin_guards(self):
        twin = section(section(self.text, "## 3. 유형"), "### 쌍둥이")
        self.assertIn("발문은 글자 그대로", twin)
        self.assertIn("보기 5개는 새로 쓴다", twin)
        self.assertIn("금지어", twin)
        self.assertIn("같은 팩 partA", twin)

    def test_quota(self):
        q = section(self.text, "## 4. 할당")
        for s in ("10~15개", "토픽당 최대 3개", "쌍둥이 2", "그림 2", "상황 전이 2", "ㄱㄴㄷ 1",
                  "용어 바꿔 쓰기 2", "약 1/3", "보기는 5개", "만들 수 없으면 0개", "못 채우면"):
            with self.subTest(s=s):
                self.assertIn(s, q)

    def test_update_is_proposal_only(self):
        u = section(self.text, "## 5. 갱신")
        self.assertIn("webquiz-style.md 갱신 제안", u)
        self.assertIn("이 파일은 고치지 않는다", u)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q`
Expected: FAIL — `FileNotFoundError: ... webquiz-style.md`

- [ ] **Step 3: 참조 파일 쓰기**

`.agents/skills/bio-review-pack/references/webquiz-style.md` (전문):

```markdown
# 웹과제 출제 유형 — partC 변형 설계 기준 (메인 에이전트)

partC(변형 연습)를 설계할 때 `problem-selection.md` 6절과 함께 읽는다. 웹과제는 장이 끝난 뒤에 응시하므로 이번 장의 bank는 팩을 만들 때 대개 없다. 그래서 지난 장 웹과제에서 본 출제 방식을 여기 모아 새 장의 변형에 옮긴다.

## 1. 출처

`웹과제/1장/`, `2장/`, `3장/questions.json` 46문항, 2026-10-01 집계. 화면의 선택 표시(`selected_option_id`)는 집계에 쓰지 않았다.

## 2. 수치

| 사실 | 1장 | 2장 | 3장 | 합계 |
|---|---|---|---|---|
| 문항 | 17 | 16 | 13 | 46 |
| 기출과 거의 같음(보기 순서만 바뀜) | 2 | 3 | 2 | 7 |
| 기출 발문 그대로 + 정답 보기 교체 | 0 | 3 | 0 | 3 |
| 기출 숫자·보기를 고쳐 씀 | 0 | 0 | 4 | 4 |
| 새 문항 | 15 | 10 | 7 | 32 (70%) |
| 부정형 발문 | 6 | 3 | 6 | 15 (33%) |
| 그림·모식도·사진 | 2 | 3 | 3 | 8 (17%) |
| ㄱㄴㄷ 합답형 | 1 | 0 | 1 | 2 |
| 오타·표기 문제 | 2 | 5 | 2 | 9 |

웹과제의 70%는 기출에 없는 새 문항이고, 보기는 대부분 5개다.

## 3. 유형

### 쌍둥이

- 정의: 기출 발문을 그대로 두고, 다른 보기가 정답이 되게 보기를 다시 쓴 문제(정답 바꾼 쌍둥이).
- 실제 예: 2장 q1은 기출 2강 9번 발문(광의존반응 동안 일어나지 않는 것)인데 정답이 "산소가 분해되어 물 방출"에서 "이산화탄소가 고정된다"로 바뀌었다. 2장 q8은 기출 2강 39번(효소에 대한 맞는 진술)에서 "여러 번 재사용"이 "고온에서 변성"으로, 2장 q10은 기출 2강 32번에서 "캘빈회로에서 생산된 산소"가 "광독립반응(암반응) 부산물로 산소"로 바뀌었다.
- 만드는 법: 이번 팩 partB에 포함된 기출 하나를 고른다. 발문은 글자 그대로 쓰고 보기 5개는 새로 쓴다. 원래 정답 보기의 개념은 발문 방향에 맞게 오답 쪽 진술로 남기고, 다른 오답 개념 하나를 정답 진술로 바꾼다.
- 피할 것: 원문 보기 문장 재사용. 발문에 금지어가 들어 있는 기출. 같은 팩 partA에 이미 정답이 바뀐 웹과제 원문(예: 0910·0915의 2장 q1·q8·q10)이 있는 기출은 그 원문이 쌍둥이 역할을 하므로 고르지 않는다.

### 그림

- 정의: 라벨을 가린 그림·모식도·그래프를 읽어야 풀리는 문제.
- 실제 예: 2장 q4 효소 유무 자유에너지 그래프(구간 I~IV 판별), 2장 q9 세포호흡 개요 모식도((가)(나)(다) 빈 라벨), 3장 q1 양파 뿌리 현미경 사진(단계 순서), 3장 q5 DNA 응축 모식도((가)(나)(다)와 히스톤).
- 만드는 법: 정리노트의 `fig-*` 클래스로 카드에 인라인 SVG를 그린다(`content-rules.md` SVG 그림 규칙). 이름 대신 (가)(나)(다), A~E, I~IV로 표지하고 모양·위치 단서로 판별하게 한다. 사진 판독은 모양 단서(염색체가 가운데 줄로 섬, 두 무리로 갈라짐)를 도식으로 옮긴다.
- 피할 것: 표지에 정답 이름 쓰기. 그림 없이도 풀리는 문제.

### 상황 전이

- 정의: 배운 원리를 새 생물·새 실험 조건·다른 숫자에 적용하는 문제.
- 실제 예: 2장 q2 지방이 탄수화물보다 ATP를 많이 내는 이유(산화 상태), 2장 q7 시금치 잎을 씹을 때 사실인 것, 2장 q16 전자전달은 두고 ATP 합성효소만 막을 때 pH 차이, 3장 q2 2n=8일 때 정자 종류 수.
- 만드는 법: 원인 하나만 바꾸고 결과를 묻는다. 수업에서 쓴 예와 다른 생물·숫자를 쓴다.
- 피할 것: 배우지 않은 사실이 있어야 풀리는 상황.

### ㄱㄴㄷ

- 정의: 진술 3개를 하나씩 판정하고 "옳은 것만을 모두 고른 것"을 고르는 합답형.
- 실제 예: 1장 q6 살아 있는 세포로 판단할 조건, 3장 q12 세포 주기 진술(ㄷ "M기에 방추사 단백질 합성"이 함정이고 실제로는 G2기).
- 만드는 법: 진술을 `ㄱ.`~`ㄷ.`로 싣고 보기 5개는 조합으로 쓴다. 진술 하나는 인접 단계·인접 개념과 바꿔 쓴 함정으로 둔다.
- 피할 것: 진술 하나가 다른 진술의 정답을 알려 주는 구성.

### 용어 바꿔 쓰기

- 정의: 노트와 다른 이름으로 같은 대상을 부르는 문제. 단독 유형이 아니라 다른 유형 문제 안에 섞는다.
- 실제 예: 2장 q1 "명반응(광의존반응)", 2장 q10 "광독립반응(암반응)", 1장 "전자전달사슬"·"뉴클레오티드".
- 만드는 법: 아래 대응표에서 노트에 덜 쓴 쪽 이름을 발문이나 보기에 쓰고, 풀이에 "같은 말"이라고 한 줄 밝힌다. 명반응 ↔ 광의존반응 · 암반응 ↔ 광독립반응 ↔ 캘빈회로 · 전자전달계 ↔ 전자전달사슬 · 뉴클레오타이드 ↔ 뉴클레오티드 · 유사분열 ↔ 체세포 분열 · 감수분열 ↔ 감수 분열.
- 피할 것: 이번 범위에서 한 번도 나오지 않은 이름(금지어 규칙과 충돌).

## 4. 할당

- 합계 10~15개. 토픽당 최대 3개.
- 최소: 쌍둥이 2, 그림 2, 상황 전이 2, ㄱㄴㄷ 1, 용어 바꿔 쓰기 2(다른 유형 문제와 겹쳐도 된다). 부정형 발문은 전체의 약 1/3.
- 남는 자리는 `problem-selection.md` 6절의 혼동 묶음 변형으로 채운다. 한 문제가 유형과 혼동 묶음을 함께 맡아도 된다.
- 만들 수 없으면 0개(또는 최소보다 적게)로 두고 보고서에 사유를 적는다. 예: 포함 기출이 없거나 모두 "피할 것"에 걸리면 쌍둥이 0, 그릴 구조가 없는 범위면 그림 0.
- 범위가 좁아 10개를 못 채우면 만든 만큼만 넣고 사유를 적는다. 범위 밖 내용이나 같은 문제 반복으로 채우지 않는다.
- 보기는 5개가 기본이다. 개념상 5개를 만들 수 없으면 4개.

## 5. 갱신

이 파일에 없는 장의 `웹과제/<N>장/questions.json`이 있으면 메인 에이전트가 그 장의 문항 수, 기출과 같은 문항·정답 교체 문항 수, 부정형·그림·ㄱㄴㄷ 수를 세고, 위에 없는 유형이 보이면 함께 적어 9단계 보고서에 "webquiz-style.md 갱신 제안"으로 낸다. 이 파일은 고치지 않는다.
```

- [ ] **Step 4: SKILL.md에서 참조하기**

`.agents/skills/bio-review-pack/SKILL.md:93`의 줄

```
  - 변형 연습(partC)은 `references/problem-selection.md` 6절로 설계해 포함 문항 뒤에 넣는다(`RUN/variants.md`).
```

을 다음으로 바꾼다.

```
  - 변형 연습(partC)은 `references/problem-selection.md` 6절과 `references/webquiz-style.md`의 유형 할당으로 설계해 포함 문항 뒤에 넣는다(`RUN/variants.md`).
```

- [ ] **Step 5: 통과 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py .agents/skills/bio-review-pack/tests/test_skill_files.py -q`
Expected: 모두 PASS (`test_every_reference_is_used`, `test_no_circled_numbers_in_rules` 포함)

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-review-pack/references/webquiz-style.md .agents/skills/bio-review-pack/tests/test_webquiz_rules.py .agents/skills/bio-review-pack/SKILL.md
git commit -m "feat(bio-review-pack): add webquiz style reference for partC variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: partC 선별·카드 규칙을 유형 할당에 맞추기

**Files:**
- Modify: `.agents/skills/bio-review-pack/references/problem-selection.md:82-86`
- Modify: `.agents/skills/bio-review-pack/references/card-rules.md:41`
- Test: `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`

**Interfaces:**
- Consumes: Task 1의 `webquiz-style.md` 절·유형 이름, 테스트 도우미 `read`, `section`, 상수 `REFS`.
- Produces: `RUN/variants.md` 헤더 `| id | 혼동 묶음 | 웹과제 유형 | 형태 | 근거 토픽 | 문제 요지 | 의도한 정답과 이유 | 오답 보기의 의도 |`. Task 3의 보고서 줄이 이 `웹과제 유형` 열을 센다. 유형 값: `쌍둥이`, `그림`, `상황`, `ㄱㄴㄷ`, `없음`, 덧붙임 `+부정형`, `+용어`.

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_webquiz_rules.py`의 `if __name__ == "__main__":` 위에 추가:

```python
class TestSelectionRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s6 = section(read(REFS / "problem-selection.md"), "## 6. 변형 연습")
        cls.cards = read(REFS / "card-rules.md")

    def test_section6_points_to_style(self):
        self.assertIn("`references/webquiz-style.md`", self.s6)
        self.assertIn("10~15개", self.s6)
        self.assertIn("못 채우면", self.s6)
        self.assertNotIn("3~8개", self.s6)

    def test_twin_exception_and_five_options(self):
        self.assertIn("쌍둥이는 발문만 원문 그대로", self.s6)
        self.assertIn("보기는 5개가 기본", self.s6)
        self.assertNotIn("보기 수는 원문 형식에 맞출 필요가 없다", self.s6)

    def test_variants_table_has_type_column(self):
        self.assertIn("| id | 혼동 묶음 | 웹과제 유형 | 형태 |", self.s6)
        for v in ("`쌍둥이`", "`그림`", "`상황`", "`ㄱㄴㄷ`", "`없음`", "`+부정형`", "`+용어`"):
            with self.subTest(v=v):
                self.assertIn(v, self.s6)

    def test_card_rules_for_twin_and_statements(self):
        self.assertIn("정답을 바꾼 생성 변형이에요", self.cards)
        self.assertIn("원문 정답과 달라진 점", self.cards)
        self.assertIn("`ㄱ.`~`ㄷ.`", self.cards)
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q`
Expected: `TestSelectionRules`의 4개 테스트 FAIL (예: `'10~15개' not found`)

- [ ] **Step 3: `problem-selection.md` 6절 고치기**

82행

```
- 대상: 요약의 `⚠️ 혼동 지점`과 포함 문항의 오답 진단에서 나온 **핵심 혼동 묶음**. 묶음마다 필요하면 1~2개, 고정 개수는 채우지 않는다. 합계 3~8개가 보통이다.
```

을

```
- 대상: 요약의 `⚠️ 혼동 지점`과 포함 문항의 오답 진단에서 나온 **핵심 혼동 묶음**, 그리고 `references/webquiz-style.md`의 웹과제 유형. 먼저 그 파일 4절의 유형 할당(쌍둥이·그림·상황 전이·ㄱㄴㄷ·용어 바꿔 쓰기)을 채우고, 남는 자리를 혼동 묶음으로 채운다. 합계 10~15개, 토픽당 최대 3개. 범위가 좁아 못 채우면 만든 만큼만 넣고 보고서에 사유를 적는다.
```

로 바꾼다.

84행

```
- 범위: 이번 범위와 이전 수업에서 배운 것만. 금지어를 쓰지 않는다. 원문 기출·웹과제 문장을 그대로 재사용하지 않는다.
```

을

```
- 범위: 이번 범위와 이전 수업에서 배운 것만. 금지어를 쓰지 않는다. 원문 기출·웹과제 문장을 그대로 재사용하지 않는다. 단, 쌍둥이는 발문만 원문 그대로 쓰고 보기는 새로 쓴다(`webquiz-style.md` 3절).
```

로 바꾼다.

85행

```
- 정답이 하나로 정해지게 만들고, 메인 에이전트가 manifest `answer`를 정한다. 보기 수는 원문 형식에 맞출 필요가 없다.
```

을

```
- 정답이 하나로 정해지게 만들고, 메인 에이전트가 manifest `answer`를 정한다. 보기는 5개가 기본이다(웹과제 형식). 개념상 5개를 만들 수 없으면 4개. 부정형 발문은 전체의 약 1/3.
```

로 바꾼다.

86행

```
- `question-audit.md`의 원문 합계에 넣지 않는다. 변형 목록은 `RUN/variants.md`에 `| id | 혼동 묶음 | 형태 | 근거 토픽 | 문제 요지 | 의도한 정답과 이유 | 오답 보기의 의도 |`로 적는다. 메인 에이전트가 3단계(작성) 전에 채우고, 카드 작성자는 이 행에 맞춰 문제와 보기를 쓴다.
```

을

```
- `question-audit.md`의 원문 합계에 넣지 않는다. 변형 목록은 `RUN/variants.md`에 `| id | 혼동 묶음 | 웹과제 유형 | 형태 | 근거 토픽 | 문제 요지 | 의도한 정답과 이유 | 오답 보기의 의도 |`로 적는다. `웹과제 유형`은 `쌍둥이`, `그림`, `상황`, `ㄱㄴㄷ`, `없음` 중 하나에, 부정형 발문이면 `+부정형`, 용어 바꿔 쓰기면 `+용어`를 붙인다(예: `그림+부정형`). 쌍둥이는 `형태` 칸에 원문 출처(예: `기출 2강 9`)를 적는다. 메인 에이전트가 3단계(작성) 전에 채우고, 카드 작성자는 이 행에 맞춰 문제와 보기를 쓴다.
```

로 바꾼다.

- [ ] **Step 4: `card-rules.md` 41행 뒤에 두 줄 추가**

41행(`- 변형 연습(partC) 카드: …`) 바로 다음에 넣는다.

```
- 쌍둥이 변형(`variants.md` 웹과제 유형 `쌍둥이`): 발문은 `형태` 칸의 원문 발문을 글자 그대로, 보기는 새로 쓴다. 원문 정보 보기에 "기출 N강 M번 발문에 정답을 바꾼 생성 변형이에요. 다루는 혼동: …"이라고 원문을 밝힌다. 풀이 마지막 단계("수업과의 연결" 앞)에 "원문 정답과 달라진 점: …" 한 줄을 쓴다.
- ㄱㄴㄷ 변형: 진술을 문제 문단 다음 `<ul>`에 `ㄱ.`~`ㄷ.` 라벨로 싣고, 보기 `(1)`~`(5)`는 조합(예: `(4) ㄱ, ㄴ`)으로 쓴다. 풀이는 진술마다 맞아요/틀려요를 먼저 쓰고 보기 진단으로 넘어간다.
```

- [ ] **Step 5: 통과 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-review-pack/references/problem-selection.md .agents/skills/bio-review-pack/references/card-rules.md .agents/skills/bio-review-pack/tests/test_webquiz_rules.py
git commit -m "feat(bio-review-pack): quota partC by webquiz types (10-15 variants)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: 보고서에 유형 개수와 갱신 제안 넣기

**Files:**
- Modify: `.agents/skills/bio-review-pack/SKILL.md:182`, `:192`
- Test: `.agents/skills/bio-review-pack/tests/test_webquiz_rules.py`

**Interfaces:**
- Consumes: Task 2의 `variants.md` `웹과제 유형` 열 값, Task 1 §5 "webquiz-style.md 갱신 제안".
- Produces: 보고서 줄 형식 `변형 v (쌍둥이 a · 그림 b · 상황 c · ㄱㄴㄷ d · 부정형 e)`. Task 4가 이 줄로 결과를 확인한다.

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_webquiz_rules.py`의 `if __name__ == "__main__":` 위에 추가:

```python
class TestReportRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read(SKILL / "SKILL.md")
        # 9단계 안 코드 블록에 "## 복습팩 …" 줄이 있어 section()은 거기서 끊긴다. 다음 절 제목까지 직접 자른다.
        cls.report = cls.skill[cls.skill.index("### 9. 보고"):cls.skill.index("## 오류 처리")]

    def test_report_counts_types(self):
        self.assertIn("변형 v (쌍둥이 a · 그림 b · 상황 c · ㄱㄴㄷ d · 부정형 e)", self.report)
        self.assertIn("0개인 유형은 사유", self.report)

    def test_report_mentions_style_update(self):
        self.assertIn("webquiz-style.md 갱신 제안", self.report)
        self.assertIn("풀이기록", self.report)
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests/test_webquiz_rules.py -q`
Expected: `TestReportRules` 2개 FAIL

- [ ] **Step 3: SKILL.md 182행 고치기**

```
- 문항: 포함 N (웹과제 a, 기출 b) · 변형 v · 이전 팩 N · 보류 N · 범위 밖 N — 분류표 RUN/question-audit.md
```

을

```
- 문항: 포함 N (웹과제 a, 기출 b) · 변형 v (쌍둥이 a · 그림 b · 상황 c · ㄱㄴㄷ d · 부정형 e) · 이전 팩 N · 보류 N · 범위 밖 N — 분류표 RUN/question-audit.md, 변형 RUN/variants.md. 0개인 유형은 사유를 한 줄씩
```

로 바꾼다.

- [ ] **Step 4: SKILL.md 192행 뒤에 한 문단 추가**

192행(`실행 폴더 경로(\`RUN\`)도 적는다. …`) 바로 다음에 빈 줄 하나와 함께 넣는다.

```
`references/webquiz-style.md` 1절에 없는 장의 `웹과제/<N>장/questions.json`이 있으면 그 파일 5절대로 세어 보고서 끝에 "webquiz-style.md 갱신 제안"을 적는다. 같은 range의 팩을 다시 만들었으면 `복습노트/<range>/풀이기록/`이 그대로인지 확인하고, 카드 번호가 바뀌어 예전 풀이기록은 백업 폴더의 예전 HTML 기준이라고 적는다.
```

- [ ] **Step 5: 통과 확인**

Run: `python3 -m pytest .agents/skills/bio-review-pack/tests -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/tests/test_webquiz_rules.py
git commit -m "feat(bio-review-pack): report partC webquiz type counts

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: 0929 → 0910 → 0915 → 0917 → 0922 팩 다시 만들기

운영 태스크다. 새 규칙으로 `/bio-review-pack <range>`를 범위마다 한 번씩, **이 순서대로 하나씩** 실행한다(0929는 4장 웹과제 10/8 대비라 먼저, 나머지는 "이전 팩" 판정이 앞 팩의 `data-source`를 보기 때문에 시간순).

**Files:**
- Modify(재생성): `복습노트/<range>/정리노트_<range>_*.html|md`, `복습문제_<range>_*.html|md`, `figures_<range>/`
- 보존: `복습노트/0922/풀이기록/*.json`

**Interfaces:**
- Consumes: Task 1~3의 규칙, Task 3의 보고서 줄.
- Produces: 재생성된 팩 5개, 범위별 커밋 5개.

- [ ] **Step 1: 시작 전 보존 대상 기록**

```bash
shasum -a 256 복습노트/*/풀이기록/*.json > "$TMPDIR/solves-before.txt"; cat "$TMPDIR/solves-before.txt"
git show 72704c8 -- '복습노트/0922/*.md' > "$TMPDIR/fix-72704c8.diff"; wc -l "$TMPDIR/fix-72704c8.diff"
```

Expected: 풀이기록 JSON 해시 목록, diff 파일(우성 유전병 문항 "기출 4강 38"의 보기를 `Mm`/`MM` 표기로 고친 수정).

- [ ] **Step 2: 0929 다시 만들기**

`/bio-review-pack 0929` 실행. 끝난 보고서에서 확인:
- `변형 v (…)`의 v가 10~15이거나, 아니면 사유가 있다.
- 유형 최소(쌍둥이 2 · 그림 2 · 상황 2 · ㄱㄴㄷ 1)에 못 미치는 유형마다 사유가 있다.
- 블라인드 검사: 변형 포함 N/N 풀림, 미해결 없음.

- [ ] **Step 3: 0929 보존 확인과 커밋**

```bash
shasum -a 256 -c "$TMPDIR/solves-before.txt"
git status --short 복습노트/0929
git add 복습노트/0929/정리노트_0929_* 복습노트/0929/복습문제_0929_* 복습노트/0929/figures_0929
git commit -m "docs(notes): regenerate review pack 0929 with webquiz variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Expected: `shasum -c`가 모두 `OK`. `*.zip`이 섞여 있지 않다.

- [ ] **Step 4: 0910 다시 만들기 → 확인 → 커밋**

`/bio-review-pack 0910` 실행. Step 2의 확인 항목에 더해:
- `웹과제/2장/questions.json`의 문항이 partA에 들어갔는지 보고서의 `웹과제 a`로 확인(2장 문항은 0910·0915로 나뉠 수 있다).
- partA에 2장 q1·q8·q10이 있으면 그 원문 기출(2강 9·39·32번)로 쌍둥이를 만들지 않았는지 `RUN/variants.md`의 `형태` 칸으로 확인.

```bash
shasum -a 256 -c "$TMPDIR/solves-before.txt"
git add 복습노트/0910/정리노트_0910_* 복습노트/0910/복습문제_0910_* 복습노트/0910/장마감_0910_* 복습노트/0910/figures_0910
git commit -m "docs(notes): regenerate review pack 0910 with webquiz variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`장마감_0910_*`이 없으면 그 경로는 빼고 add한다.

- [ ] **Step 5: 0915 다시 만들기 → 확인 → 커밋**

`/bio-review-pack 0915` 실행. Step 4와 같은 확인(2장 partA·쌍둥이 회피). 그다음:

```bash
shasum -a 256 -c "$TMPDIR/solves-before.txt"
git add 복습노트/0915/정리노트_0915_* 복습노트/0915/복습문제_0915_* 복습노트/0915/장마감_0915_* 복습노트/0915/figures_0915
git commit -m "docs(notes): regenerate review pack 0915 with webquiz variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 6: 0917 다시 만들기 → 확인 → 커밋**

`/bio-review-pack 0917` 실행. Step 2 확인 항목 + `웹과제/3장/questions.json` 문항이 partA에 들어갔는지 확인. 그다음:

```bash
shasum -a 256 -c "$TMPDIR/solves-before.txt"
git add 복습노트/0917/정리노트_0917_* 복습노트/0917/복습문제_0917_* 복습노트/0917/figures_0917
git commit -m "docs(notes): regenerate review pack 0917 with webquiz variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: 0922 다시 만들기**

`/bio-review-pack 0922` 실행. Step 6 확인 항목에 더해:
- 4강 기출 포함 집합이 이전 0922와 같은지: 새 `복습문제_0922_*.html`의 `data-source="기출 4강 …"` 목록을 `git show HEAD:'복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.html'`의 목록과 비교한다.

```bash
diff <(git show HEAD:"복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.html" | grep -o 'data-source="기출 4강 [0-9]*"' | sort) <(grep -o 'data-source="기출 4강 [0-9]*"' 복습노트/0922/복습문제_0922_*.html | sed 's/^[^:]*://' | sort)
```

Expected: 출력 없음. 차이가 있으면 0929를 한 번 더 실행해야 하므로 보고서에 적고 Step 2~3을 반복한다.

- [ ] **Step 8: 72704c8 손 수정 다시 적용**

`$TMPDIR/fix-72704c8.diff`의 문항(기출 4강 38, 우성 유전병)을 새 0922 복습문제에서 찾는다. 보기가 원문 문장("대립유전자 중 하나의 유전자만 돌연변이 일 때" …)으로 돌아왔으면, 그 카드의 HTML 보기와 풀이를 diff의 `+` 쪽 문장(`두 대립유전자가 모두 정상일 때만` / `이형접합자(Mm)일 때만` / `돌연변이 동형접합자(MM)일 때만` / `이형접합자(Mm)와 돌연변이 동형접합자(MM)일 때`, 정답 (4))으로 고친다. 그다음 MD를 다시 만든다.

```bash
python3 .agents/skills/bio-review-pack/scripts/html2md.py 복습노트/0922/정리노트_0922_Cell_Division_and_Heredity.html 복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.html --check
grep -c "이형접합자(Mm)와 돌연변이 동형접합자(MM)일 때" 복습노트/0922/복습문제_0922_Cell_Division_and_Heredity.md
```

Expected: `OK`, 그리고 `1` 이상.

- [ ] **Step 9: 0922 보존 확인과 커밋**

```bash
shasum -a 256 -c "$TMPDIR/solves-before.txt"
git add 복습노트/0922/정리노트_0922_* 복습노트/0922/복습문제_0922_* 복습노트/0922/장마감_0922_* 복습노트/0922/figures_0922
git commit -m "docs(notes): regenerate review pack 0922 with webquiz variants

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`풀이기록/`은 add하지 않는다(사용자 자료, 아직 git에 없음). `장마감_0922_*`이 없으면 그 경로는 뺀다.

- [ ] **Step 10: 마무리 확인**

```bash
python3 -m pytest .agents/skills/bio-review-pack/tests -q
for r in 0910 0915 0917 0922 0929; do printf "%s: " $r; grep -c '\[변형\]' 복습노트/$r/복습문제_${r}_*.md; done
```

Expected: 테스트 모두 PASS. 범위마다 `[변형]` 카드 수가 10~15(못 미치면 그 범위 보고서에 사유가 있어야 한다).
