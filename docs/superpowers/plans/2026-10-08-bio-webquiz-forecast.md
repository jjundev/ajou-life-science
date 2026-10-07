# bio-webquiz-forecast 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 장마다 웹과제 예상 세트(개요 2 + 기출 재출제 5 + 새 문제 10)를 버전(v1, v2 …)으로 쌓아 만드는 스킬 `bio-webquiz-forecast`를 만들고, 2026-10-07에 만든 4장 세트를 그 v1으로 옮긴다.

**Architecture:** 스킬은 문서(SKILL.md·references)와 스크립트 4개로 이뤄진다. `cards.py`는 카드 HTML 파서, `exam_pool.py`는 복습팩에서 `기출 <N>강 M` 카드를 모으는 기출 풀, `build.py`는 bio-review-pack `assemble.build_review`로 HTML을 조립하고 버전을 매긴다, `check.py`는 세트 규칙 전체를 검사한다. 카드 내용은 실행 때 에이전트가 쓰고, 스크립트는 구조·버전·중복·기출 원문 대조만 책임진다.

**Tech Stack:** Python 3 stdlib(`unittest`, `re`, `json`, `pathlib`, `tempfile`), bio-review-pack 스크립트(`assemble`, `manifest`, `review_interaction`, `check_html`).

**Spec:** `docs/superpowers/specs/2026-10-08-bio-webquiz-forecast-design.md` (결정 #0–#22). 이 계획의 값은 모두 그 표에서 왔다.

## Global Constraints

- **작업 공간:** `main` 작업 트리에는 사용자가 진행 중인 staged 변경(`웹과제/커닝페이퍼` → `웹과제예상/커닝페이퍼` 이동)이 있다. 건드리지 않는다. superpowers:using-git-worktrees로 `.worktrees/bio-webquiz-forecast`에 새 브랜치 `feat/bio-webquiz-forecast`를 **`feat/ch4-webquiz-forecast`에서** 만든다(4장 세트와 빌드 스크립트가 그 브랜치에만 있다). 계획 파일과 spec 파일은 `main` 작업 트리에만 있으므로 워크트리로 복사해 첫 커밋으로 넣는다:
  ```bash
  cp "<main>/docs/superpowers/specs/2026-10-08-bio-webquiz-forecast-design.md" docs/superpowers/specs/
  cp "<main>/docs/superpowers/plans/2026-10-08-bio-webquiz-forecast.md" docs/superpowers/plans/
  git add docs/superpowers && git commit -m "docs: add bio-webquiz-forecast spec and plan"
  ```
- 스킬 경로: `.agents/skills/bio-webquiz-forecast/`. `.claude/skills/bio-webquiz-forecast`는 `../../.agents/skills/bio-webquiz-forecast`를 가리키는 심볼릭 링크.
- bio-review-pack 폴더(`.agents/skills/bio-review-pack/`)의 파일은 **고치지 않는다.** 스크립트는 `Path(__file__).resolve().parents[2] / "bio-review-pack" / "scripts"`를 `sys.path`에 넣어 import한다.
- 산출물: `웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html`, 원본 `웹과제예상/<N>장/src/v<K>/{pack.json, cards/*.html, blueprint.md}`.
- HTML 치환 3개는 각각 정확히 1회여야 하며 아니면 오류: 정리노트 링크(`href="<note_name>"` → `href="<note_href>"`), `data-range="<N>장"` → `data-range="<N>장-v<K>"`, `</head>` 앞 `<style id="forecast-overrides">.review-export-bar { display: none !important; }</style>`.
- 세트 구성(비 legacy): partA o1·o2(보기 없음), partB p1–p5 기출(기출그대로 2 · 기출쌍둥이 2 · 기출숫자 1), partC p6–p15 새 문제. 채점 문항 15개, 정답 A~E 각 3개.
- 카드 제목: `PN. [예상] …`(새 문제), `PN. [기출 예상] …`(기출그대로), `PN. [기출 변형] …`(쌍둥이·숫자).
- 출력 파일은 LF(`newline="\n"`), UTF-8.
- 테스트 실행: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -t .agents/skills/bio-webquiz-forecast/tests -v` (저장소 루트에서).
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **같은 버전을 다시 만들어 이전 세트를 덮어씀** — `--init`이 이미 있는 `src/v<K>`를 만나면 멈춰야 한다. → Task 3 `test_init_refuses_existing`.
2. **v1과 v2의 푼 기록이 섞임** — 두 버전 모두 카드 id가 p1…p15이므로 `data-range`가 버전마다 달라야 한다. → Task 3 `test_render_substitutions`.
3. **"기출 그대로"인데 보기 하나가 살짝 바뀜** — 학생은 원문 그대로라고 믿고 외운다. 발문·보기 집합이 원문과 정규화 비교로 같아야 한다. → Task 4 `test_exam_verbatim_mismatch`.
4. **쌍둥이 정답이 원문 정답과 같은 문장** — 그러면 쌍둥이가 아니다. → Task 4 `test_exam_twin_same_answer`.
5. **세트 사이 같은 기출 번호·같은 발문 반복** — "여러 세트"의 가치가 사라진다. legacy v1의 `used_exam_sources`까지 포함해 막아야 한다. → Task 4 `test_exam_reuse_across_versions`, `test_stem_dup_across_versions`.

---

### Task 1: 스킬 뼈대 + 카드 파서 `cards.py` + 테스트 도구

**Files:**
- Create: `.agents/skills/bio-webquiz-forecast/scripts/cards.py`
- Create: `.agents/skills/bio-webquiz-forecast/tests/_util.py`
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_cards.py`

**Interfaces:**
- Produces:
  - `cards.norm(s: str) -> str` — 공백·문장부호 제거(한글·영숫자만 남김).
  - `cards.text(html: str) -> str` — 태그 제거, 공백 하나로.
  - `cards.parse_cards(html: str) -> dict[str, dict]` — 키는 카드 id. 값 dict 키: `id`, `source`(data-source), `types`(list[str]), `title`(h3 텍스트), `stem`(problem 첫 `<p>` 텍스트, 없으면 `""`), `options`(list[str], 라벨 제거), `answer_index`(int|None, 0부터), `answer_label`(str|None, 원문 라벨 `"2"` 또는 `"B"`), `diagnoses`(list[tuple[str,str]] 예: `[("A","틀려요"),…]`), `body`(카드 안쪽 HTML).
  - `_util.py`: `SKILL`, `SCRIPTS`, `card_html(i, answer, *, types="계산", kind="예상", stem=None, options=None) -> str`, `overview_html(cid="o1") -> str`, `make_repo(tmp: Path) -> Path`(노트 파일 생성 후 repo 경로 반환), `make_set(repo, chapter, version, cards: dict[str,str], pack_extra: dict|None=None) -> Path`(src 폴더 반환), `exam_card_html(source, stem, options, answer_no) -> str`, `write_pool(repo, cards_html: list[str])`.

- [ ] **Step 1: 테스트 도구 `_util.py` 작성**

```python
"""스킬 테스트 공통 도구. 임시 저장소에 작은 세트를 만든다."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

NOTE_REL = "복습노트/0000/정리노트_0000_T.html"
LINK = f"../../{NOTE_REL}#s1-t"


def card_html(i: int, answer: str, *, types: str = "계산", kind: str = "예상",
              stem: str | None = None, options: list[str] | None = None) -> str:
    options = options or [f"보기 {i}{c}" for c in "ABCDE"]
    stem = stem or f"문제 {i}번 발문이다?"
    neg = "부정형" in types.split()
    diag = "".join(
        f"<li>{c}. {'맞아요' if ((c != answer) if neg else (c == answer)) else '틀려요'}. 이유 {c}예요.</li>"
        for c in "ABCDE")
    choices = "".join(f"<li>{c}. {t}</li>" for c, t in zip("ABCDE", options))
    return (f'<article class="card" id="p{i}" data-source="예상 9장 {i}" data-types="{types}">\n'
            f'  <h3>P{i}. [{kind}] 제목 {i}</h3>\n'
            f'  <div class="problem"><p>{stem}</p>\n    <ul class="choices">{choices}</ul></div>\n'
            f'  <details class="original"><summary>원문 정보 보기</summary>예상 문제예요.</details>\n'
            f'  <details class="hint"><summary>힌트 보기</summary>힌트예요.</details>\n'
            f'  <details class="solution"><summary>풀이 보기</summary>\n'
            f'    <ol class="steps">{diag}<li>수업과의 연결: 노트와 이어져요(<a href="{LINK}">정리노트</a>).</li></ol>\n'
            f'    <p class="answer">정답: {answer}</p>\n  </details>\n</article>\n')


def overview_html(cid: str = "o1") -> str:
    return (f'<article class="card" id="{cid}" data-source="예상 9장 개요">\n  <h3>개요</h3>\n'
            f'  <div class="problem"><p>개요 내용이에요.</p></div>\n</article>\n')


def make_repo(tmp: Path) -> Path:
    note = tmp / NOTE_REL
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text('<!DOCTYPE html><html lang="ko"><body><a id="s1-t"></a></body></html>', encoding="utf-8")
    return tmp


def make_set(repo: Path, chapter: int, version: int, cards: dict[str, str],
             pack_extra: dict | None = None) -> Path:
    src = repo / "웹과제예상" / f"{chapter}장" / "src" / f"v{version}"
    (src / "cards").mkdir(parents=True, exist_ok=True)
    for cid, html in cards.items():
        (src / "cards" / f"{cid}.html").write_text(html, encoding="utf-8")
    graded = [c for c in cards if c.startswith("p")]
    pack = {
        "course": "생명과학", "chapter": chapter, "version": version,
        "note_href": f"../../{NOTE_REL}",
        "review_title": f"{chapter}장 웹과제 예상 v{version}", "review_intro": "소개예요.",
        "footer_review": "근거예요.",
        "parts": [{"id": "partA", "title": "A. 개요", "short": "개요"},
                  {"id": "partC", "title": "C. 새 문제", "short": "새 문제"}],
        "problems": [{"id": c, "part": "partA" if c.startswith("o") else "partC"} for c in cards],
        "answer_key": {c: "" for c in graded},
        "forbidden": ["금지어"], "types_required": {}, "exam_sources": {}, "legacy": True,
        "used_exam_sources": [],
    }
    for c in graded:
        pack["answer_key"][c] = re.search(r"정답: ([A-E])", cards[c]).group(1)
    pack.update(pack_extra or {})
    (src / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return src


def exam_card_html(source: str, stem: str, options: list[str], answer_no: int, cid: str = "p1") -> str:
    lis = "".join(f"<li>({n}) {t}</li>" for n, t in enumerate(options, 1))
    return (f'<article class="card" id="{cid}" data-source="{source}">\n<h3>P1. 기출</h3>\n'
            f'<div class="problem"><p>{stem}</p><ul class="choices">{lis}</ul></div>\n'
            f'<details class="solution"><summary>풀이 보기</summary><ol class="steps"></ol>'
            f'<p class="answer">정답: ({answer_no})</p></details></article>\n')


def write_pool(repo: Path, cards_html: list[str]) -> Path:
    f = repo / "복습노트" / "0000" / "복습문제_0000_T.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("<html><body>" + "".join(cards_html) + "</body></html>", encoding="utf-8")
    return f
```

- [ ] **Step 2: 실패하는 테스트 `test_cards.py` 작성**

```python
import unittest

from _util import card_html, exam_card_html, overview_html
import cards


class TestCards(unittest.TestCase):
    def test_norm_and_text(self):
        self.assertEqual(cards.norm(" A형, B형 (가)! "), "A형B형가")
        self.assertEqual(cards.text("<p>가 <b>나</b></p>\n<p>다</p>"), "가 나 다")

    def test_parse_forecast_card(self):
        c = cards.parse_cards(card_html(3, "C", types="부정형 계산"))["p3"]
        self.assertEqual(c["types"], ["부정형", "계산"])
        self.assertEqual(c["title"], "P3. [예상] 제목 3")
        self.assertEqual(c["stem"], "문제 3번 발문이다?")
        self.assertEqual(c["options"], [f"보기 3{x}" for x in "ABCDE"])
        self.assertEqual((c["answer_index"], c["answer_label"]), (2, "C"))
        self.assertEqual([d for d, _ in c["diagnoses"]], list("ABCDE"))
        self.assertEqual(dict(c["diagnoses"])["C"], "틀려요")

    def test_parse_exam_card(self):
        c = cards.parse_cards(exam_card_html("기출 9강 1", "기출 발문?", ["가", "나", "다", "라", "마"], 2))["p1"]
        self.assertEqual(c["source"], "기출 9강 1")
        self.assertEqual(c["options"], ["가", "나", "다", "라", "마"])
        self.assertEqual((c["answer_index"], c["answer_label"]), (1, "2"))

    def test_overview_has_no_options(self):
        c = cards.parse_cards(overview_html())["o1"]
        self.assertEqual((c["options"], c["answer_index"]), ([], None))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 실패 확인**

Run: `python -m unittest discover -s .agents/skills/bio-webquiz-forecast/tests -t .agents/skills/bio-webquiz-forecast/tests -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'cards'`

- [ ] **Step 4: `cards.py` 작성**

```python
"""예상 세트·복습팩 카드 HTML 파서 (표준 라이브러리만)."""
from __future__ import annotations

import re

CARD_RE = re.compile(r'<article class="card" id="([^"]+)"([^>]*)>(.*?)</article>', re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
LABEL_RE = re.compile(r"^\s*(?:\((\d+)\)|([A-E])\.)\s*")
ANSWER_RE = re.compile(r'<p class="answer">\s*정답:\s*(?:\((\d+)\)|([A-E]))\s*</p>')
DIAG_RE = re.compile(r"<li>([A-E])\. (맞아요|틀려요)")


def text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def norm(s: str) -> str:
    return re.sub(r"[\W_]+", "", s)


def _options(body: str) -> list[str]:
    m = re.search(r'<ul class="choices">(.*?)</ul>', body, re.S)
    if not m:
        return []
    return [LABEL_RE.sub("", text(li), count=1) for li in re.findall(r"<li>(.*?)</li>", m.group(1), re.S)]


def parse_cards(html: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for cid, raw_attrs, body in CARD_RE.findall(html):
        attrs = dict(ATTR_RE.findall(raw_attrs))
        stem = re.search(r'<div class="problem">\s*<p>(.*?)</p>', body, re.S)
        title = re.search(r"<h3>(.*?)</h3>", body, re.S)
        ans = ANSWER_RE.search(body)
        options = _options(body)
        index = label = None
        if ans:
            label = ans.group(1) or ans.group(2)
            index = int(ans.group(1)) - 1 if ans.group(1) else "ABCDE".index(ans.group(2))
        out[cid] = dict(id=cid, source=attrs.get("data-source", ""), types=attrs.get("data-types", "").split(),
                        title=text(title.group(1)) if title else "", stem=text(stem.group(1)) if stem else "",
                        options=options, answer_index=index, answer_label=label,
                        diagnoses=DIAG_RE.findall(body), body=body)
    return out
```

- [ ] **Step 5: 통과 확인**

Run: 위 테스트 명령
Expected: 4 tests OK

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast
git commit -m "feat(bio-webquiz-forecast): add card parser and test helpers"
```

---

### Task 2: 기출 풀 `exam_pool.py` + 블라인드 사본 `blind.py`

**Files:**
- Create: `.agents/skills/bio-webquiz-forecast/scripts/exam_pool.py`
- Create: `.agents/skills/bio-webquiz-forecast/scripts/blind.py`
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_exam_pool.py`

**Interfaces:**
- Consumes: `cards.parse_cards`, `cards.norm`; `_util.make_repo`, `exam_card_html`, `write_pool`, `card_html`, `overview_html`.
- Produces:
  - `exam_pool.load_pool(repo: Path, chapter: int) -> dict[str, dict]` — 키 `"기출 <N>강 M"`, 값은 `parse_cards` dict + `file`(str, 저장소 기준 경로). 정답 없는 카드는 뺀다. 같은 번호가 여러 팩에 있으면 경로 정렬 순 첫 것.
  - CLI `exam_pool.py <repo> <N>` → JSON 배열 `[{"source","stem","options","answer","file"}]`를 stdout으로(번호 순).
  - `blind.blind_markdown(html: str) -> str` — 채점 카드마다 `## <title>\n\n<stem>\n\n` + (ㄱㄴㄷ 진술 `<ul>`이 있으면 그 항목 줄) + `- A. …` 보기 줄. 정답·힌트·풀이·원문 정보는 넣지 않는다.
  - CLI `blind.py <html> <out.md>`.

- [ ] **Step 1: 실패하는 테스트**

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _util import SCRIPTS, card_html, exam_card_html, make_repo, write_pool
import blind
import exam_pool


class TestExamPool(unittest.TestCase):
    def test_load_pool_filters_chapter_and_answerless(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [
                exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 2, "p1"),
                exam_card_html("기출 8강 1", "다른 장?", list("가나다라마"), 1, "p2"),
                exam_card_html("기출 9강 2", "발문 2?", list("가나다라마"), 3, "p3").replace("정답: (3)", "정답 없음"),
            ])
            pool = exam_pool.load_pool(repo, 9)
            self.assertEqual(list(pool), ["기출 9강 1"])
            self.assertEqual(pool["기출 9강 1"]["options"][pool["기출 9강 1"]["answer_index"]], "나")

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 2)])
            out = subprocess.run([sys.executable, str(SCRIPTS / "exam_pool.py"), str(repo), "9"],
                                 capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertEqual(json.loads(out)[0]["answer"], "나")

    def test_blind_hides_answers(self):
        md = blind.blind_markdown(card_html(1, "B", stem="무엇일까?"))
        self.assertIn("## P1. [예상] 제목 1", md)
        self.assertIn("무엇일까?", md)
        self.assertIn("- B. 보기 1B", md)
        for leaked in ("정답", "맞아요", "틀려요", "힌트"):
            self.assertNotIn(leaked, md)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: 테스트 명령
Expected: ERROR — `No module named 'blind'`(또는 `exam_pool`)

- [ ] **Step 3: `exam_pool.py` 작성**

```python
#!/usr/bin/env python3
"""복습팩 복습문제 HTML에서 '기출 <N>강 M' 카드를 모은다.
CLI: exam_pool.py <repo> <N>  → JSON 배열(stdout)
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402


def _num(source: str) -> int:
    return int(source.rsplit(" ", 1)[1])


def load_pool(repo: Path | str, chapter: int) -> dict[str, dict]:
    repo = Path(repo)
    pat = re.compile(rf"기출 {chapter}강 \d+")
    pool: dict[str, dict] = {}
    for f in sorted(repo.glob("복습노트/*/복습문제_*.html")):
        for c in cards.parse_cards(f.read_text(encoding="utf-8")).values():
            if pat.fullmatch(c["source"]) and c["answer_index"] is not None and c["source"] not in pool:
                pool[c["source"]] = dict(c, file=f.relative_to(repo).as_posix())
    return dict(sorted(pool.items(), key=lambda kv: _num(kv[0])))


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("사용법: exam_pool.py <repo> <N>", file=sys.stderr)
        return 2
    pool = load_pool(args[0], int(args[1]))
    rows = [dict(source=s, stem=c["stem"], options=c["options"], answer=c["options"][c["answer_index"]],
                 file=c["file"]) for s, c in pool.items()]
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: `blind.py` 작성**

```python
#!/usr/bin/env python3
"""예상 세트 HTML → 정답·풀이를 뺀 블라인드 풀이용 Markdown.
CLI: blind.py <html> <out.md>
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402


def blind_markdown(html: str) -> str:
    parts = []
    for c in cards.parse_cards(html).values():
        if not c["options"]:
            continue
        lines = [f"## {c['title']}", "", c["stem"], ""]
        problem = re.search(r'<div class="problem">(.*?)<ul class="choices">', c["body"], re.S)
        if problem:
            for ul in re.findall(r"<ul>(.*?)</ul>", problem.group(1), re.S):
                lines += [cards.text(li) for li in re.findall(r"<li>(.*?)</li>", ul, re.S)] + [""]
        lines += [f"- {l}. {t}" for l, t in zip("ABCDE", c["options"])] + [""]
        parts.append("\n".join(lines))
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("사용법: blind.py <html> <out.md>", file=sys.stderr)
        return 2
    Path(args[1]).write_text(blind_markdown(Path(args[0]).read_text(encoding="utf-8")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 통과 확인**

Run: 테스트 명령
Expected: 7 tests OK (cards 4 + exam_pool 3)

- [ ] **Step 6: 실제 저장소 풀 확인**

Run: `python .agents/skills/bio-webquiz-forecast/scripts/exam_pool.py . 4 | python -c "import json,sys; d=json.load(sys.stdin); print(len(d), d[0]['source'])"`
Expected: 첫 숫자가 40 이상(0922·0929 팩의 `기출 4강` 카드 23+28개에서 중복 제외), 두 번째가 `기출 4강 1` 같은 번호. 0이면 경로나 파서가 틀린 것이니 고친다.

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast
git commit -m "feat(bio-webquiz-forecast): add exam pool and blind copy tools"
```

---

### Task 3: 조립·버전 `build.py`

**Files:**
- Create: `.agents/skills/bio-webquiz-forecast/scripts/build.py`
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_build.py`

**Interfaces:**
- Consumes: bio-review-pack `assemble.build_review`, `assemble.AssembleError`, `manifest.note_name`, `manifest.review_name`; `_util.make_repo`, `make_set`, `card_html`, `overview_html`.
- Produces:
  - `build.BuildError(Exception)`
  - `build.load_pack(src: Path) -> dict` — `pack.json`을 읽고 `range`=`"<chapter>장"`, `slug`=`"웹과제예상_v<version>"`을 채워 돌려준다. 폴더가 `.../<chapter>장/src/v<version>`이 아니면 `BuildError`.
  - `build.render(src: Path | str) -> tuple[str, str]` — (파일명, HTML).
  - `build.build(src) -> Path` — `src.parents[1]`(= `웹과제예상/<N>장`)에 쓴다.
  - `build.next_version(chapter_dir: Path) -> int`
  - `build.init_version(repo: Path, chapter: int) -> Path` — `웹과제예상/<N>장/src/v<K>/cards/`를 새로 만들고 src 경로 반환. 이미 있으면 `BuildError`.
  - CLI: `build.py <src>` | `build.py --next <repo> <N>` | `build.py --init <repo> <N>`.
  - 상수 `OVERRIDE_STYLE`.

- [ ] **Step 1: 실패하는 테스트**

```python
import tempfile
import unittest
from pathlib import Path

from _util import card_html, make_repo, make_set, overview_html
import build


def five():
    cards = {"o1": overview_html()}
    cards.update({f"p{i}": card_html(i, "ABCDE"[i - 1]) for i in range(1, 6)})
    return cards


class TestBuild(unittest.TestCase):
    def test_render_substitutions(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 2, five())
            name, html = build.render(src)
            self.assertEqual(name, "복습문제_9장_웹과제예상_v2.html")
            self.assertEqual(html.count('data-range="9장-v2"'), 1)
            self.assertNotIn('data-range="9장"', html)
            self.assertEqual(html.count('href="../../복습노트/0000/정리노트_0000_T.html"'), 1)  # 상단 링크만(카드 링크는 #s1-t)
            self.assertEqual(html.count(build.OVERRIDE_STYLE), 1)
            self.assertIn('"documentId": "복습문제_9장_웹과제예상_v2.html"', html)

    def test_build_writes_to_chapter_dir(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            out = build.build(make_set(repo, 9, 1, five()))
            self.assertEqual(out, repo.resolve() / "웹과제예상" / "9장" / "복습문제_9장_웹과제예상_v1.html")
            self.assertNotIn(b"\r\n", out.read_bytes())

    def test_folder_must_match_pack(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_set(make_repo(Path(t)), 9, 1, five(), {"version": 3})
            with self.assertRaises(build.BuildError):
                build.render(src)

    def test_next_version(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "웹과제예상" / "9장"
            self.assertEqual(build.next_version(d), 1)
            (d / "src" / "v1").mkdir(parents=True)
            (d / "복습문제_9장_웹과제예상_v3.html").write_text("x", encoding="utf-8")
            self.assertEqual(build.next_version(d), 4)

    def test_init_refuses_existing(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            src = build.init_version(repo, 9)
            self.assertEqual(src, repo / "웹과제예상" / "9장" / "src" / "v1")
            self.assertTrue((src / "cards").is_dir())
            self.assertEqual(build.init_version(repo, 9).name, "v2")
            (repo / "웹과제예상" / "9장" / "src" / "v3").mkdir()
            with self.assertRaises(build.BuildError):
                build.init_version(repo, 9, version=3)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: 테스트 명령
Expected: ERROR — `No module named 'build'`

- [ ] **Step 3: `build.py` 작성**

```python
#!/usr/bin/env python3
"""웹과제 예상 세트(src/v<K>) → 복습문제 형식 HTML, 그리고 버전 관리.

조립은 bio-review-pack assemble.build_review를 그대로 쓴다. 치환 3개(정리노트 링크, data-range, 내보내기 숨김)는
각각 정확히 1회여야 한다.
CLI:
  build.py <src>              src/v<K> → 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html
  build.py --next <repo> <N>  다음 버전 번호 출력
  build.py --init <repo> <N>  다음 버전 폴더(src/v<K>/cards) 생성 후 경로 출력
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

REVIEW_PACK = Path(__file__).resolve().parents[2] / "bio-review-pack" / "scripts"
sys.path.insert(0, str(REVIEW_PACK))
import assemble  # noqa: E402
import manifest as manifest_mod  # noqa: E402

OVERRIDE_STYLE = '<style id="forecast-overrides">.review-export-bar { display: none !important; }</style>'
VERSION_RE = re.compile(r"v(\d+)")
HTML_VERSION_RE = re.compile(r"_v(\d+)\.html$")


class BuildError(RuntimeError):
    pass


def load_pack(src: Path | str) -> dict:
    src = Path(src)
    m = json.loads((src / "pack.json").read_text(encoding="utf-8"))
    n, k = m["chapter"], m["version"]
    if src.name != f"v{k}" or src.parent.name != "src" or src.parent.parent.name != f"{n}장":
        raise BuildError(f"폴더({src})가 pack.json(chapter={n}, version={k})과 맞지 않음")
    m["range"], m["slug"] = f"{n}장", f"웹과제예상_v{k}"
    return m


def _once(html: str, old: str, new: str) -> str:
    if html.count(old) != 1:
        raise BuildError(f"치환 대상이 정확히 1개가 아님({html.count(old)}개): {old}")
    return html.replace(old, new)


def render(src: Path | str) -> tuple[str, str]:
    src = Path(src)
    m = load_pack(src)
    try:
        html = assemble.build_review(m, src)
    except (assemble.AssembleError, ValueError) as e:
        raise BuildError(str(e)) from e
    html = _once(html, f'href="{manifest_mod.note_name(m)}"', f'href="{m["note_href"]}"')
    html = _once(html, f'data-range="{m["range"]}"', f'data-range="{m["range"]}-v{m["version"]}"')
    html = _once(html, "</head>", OVERRIDE_STYLE + "\n</head>")
    return manifest_mod.review_name(m), html


def build(src: Path | str) -> Path:
    src = Path(src).resolve()
    name, html = render(src)
    out = src.parents[1] / name
    out.write_text(html, encoding="utf-8", newline="\n")
    return out


def next_version(chapter_dir: Path | str) -> int:
    d = Path(chapter_dir)
    nums = [0]
    if (d / "src").is_dir():
        nums += [int(m.group(1)) for p in (d / "src").iterdir() if (m := VERSION_RE.fullmatch(p.name))]
    if d.is_dir():
        nums += [int(m.group(1)) for p in d.iterdir() if (m := HTML_VERSION_RE.search(p.name))]
    return max(nums) + 1


def init_version(repo: Path | str, chapter: int, version: int | None = None) -> Path:
    d = Path(repo) / "웹과제예상" / f"{chapter}장"
    k = version or next_version(d)
    src = d / "src" / f"v{k}"
    if src.exists():
        raise BuildError(f"이미 있는 버전: {src}")
    (src / "cards").mkdir(parents=True)
    return src


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if len(args) == 3 and args[0] == "--next":
            print(next_version(Path(args[1]) / "웹과제예상" / f"{args[2]}장"))
        elif len(args) == 3 and args[0] == "--init":
            print(init_version(args[1], int(args[2])))
        elif len(args) == 1:
            print(build(args[0]))
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except BuildError as e:
        print(f"빌드 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: 테스트 명령
Expected: 12 tests OK

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast
git commit -m "feat(bio-webquiz-forecast): add versioned builder"
```

---

### Task 4: 세트 검사기 `check.py`

**Files:**
- Create: `.agents/skills/bio-webquiz-forecast/scripts/check.py`
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_check.py`

**Interfaces:**
- Consumes: `build.render`, `build.load_pack`; `cards.parse_cards`, `cards.norm`, `cards.text`; `exam_pool.load_pool`; bio-review-pack `check_html.check_file`.
- Produces:
  - `check.check(html: Path | str) -> list[str]` — 문제마다 `"[코드] 위치: 내용"` 한 줄. 빈 목록이면 통과. `html`은 `웹과제예상/<N>장/복습문제_…_v<K>.html`이고, src는 `html.parent / "src" / f"v{K}"`, repo는 `html.parents[2]`.
  - 코드 목록: `checker`, `stale`, `answer-key`, `answer-spread`, `structure`, `diagnosis`, `types`, `figure`, `wording`, `open-details`, `exam-count`, `exam-missing`, `exam-verbatim`, `exam-twin`, `exam-reuse`, `stem-dup`, `webquiz-copy`.
  - CLI `check.py <html>` — 문제를 출력하고 있으면 종료 코드 1, 없으면 `OK`와 0.
- pack.json 필드(이 Task가 읽는 것): `answer_key`(dict), `forbidden`(list), `types_required`(dict), `exam_sources`(dict: `pid` → `{"source": "기출 N강 M", "mode": "기출그대로"|"기출쌍둥이"|"기출숫자"}`), `legacy`(bool), `used_exam_sources`(list).

- [ ] **Step 1: 실패하는 테스트**

```python
import json
import tempfile
import unittest
from pathlib import Path

from _util import card_html, exam_card_html, make_repo, make_set, overview_html, write_pool
import build
import check

ANSWERS = "ABCDE"


def base_cards(**over):
    cards = {"o1": overview_html()}
    cards.update({f"p{i}": card_html(i, ANSWERS[i - 1]) for i in range(1, 6)})
    cards.update(over)
    return cards


def codes(problems):
    return {p.split("]")[0].lstrip("[") for p in problems}


class TestCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def built(self, version=1, cards=None, extra=None):
        return build.build(make_set(self.repo, 9, version, cards or base_cards(), extra))

    def test_clean_set_passes(self):
        self.assertEqual(check.check(self.built()), [])

    def test_stale(self):
        out = self.built()
        (out.parent / "src" / "v1" / "cards" / "p1.html").write_text(
            card_html(1, "A", stem="바뀐 발문?"), encoding="utf-8")
        self.assertIn("stale", codes(check.check(out)))

    def test_answer_spread(self):
        cards = base_cards(p2=card_html(2, "A"))
        self.assertIn("answer-spread", codes(check.check(self.built(cards=cards))))

    def test_negative_double_wrong(self):
        bad = card_html(1, "A", types="부정형").replace("<li>B. 맞아요", "<li>B. 틀려요")
        self.assertIn("diagnosis", codes(check.check(self.built(cards=base_cards(p1=bad)))))

    def test_forbidden_word(self):
        cards = base_cards(p1=card_html(1, "A", stem="금지어가 든 발문?"))
        self.assertIn("wording", codes(check.check(self.built(cards=cards))))

    def test_types_required(self):
        out = self.built(extra={"types_required": {"그림": 1}})
        self.assertIn("types", codes(check.check(out)))

    def test_stem_dup_across_versions(self):
        self.built(version=1)
        self.assertIn("stem-dup", codes(check.check(self.built(version=2))))

    def exam_extra(self, mode, p1):
        write_pool(self.repo, [exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2)])
        extra = {"legacy": False, "exam_sources": {"p1": {"source": "기출 9강 7", "mode": mode}},
                 "exam_counts": {mode: 1}}
        return self.built(cards=base_cards(p1=p1), extra=extra)

    def test_exam_verbatim_ok(self):
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        self.assertEqual(check.check(self.exam_extra("기출그대로", p1)), [])

    def test_exam_verbatim_mismatch(self):
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "바"])
        self.assertIn("exam-verbatim", codes(check.check(self.exam_extra("기출그대로", p1))))

    def test_exam_twin_same_answer(self):
        p1 = card_html(1, "A", kind="기출 변형", stem="기출 발문?", options=["나", "x", "y", "z", "w"])
        self.assertIn("exam-twin", codes(check.check(self.exam_extra("기출쌍둥이", p1))))

    def test_exam_reuse_across_versions(self):
        write_pool(self.repo, [exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2)])
        self.built(version=1, extra={"used_exam_sources": ["기출 9강 7"]})
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        cards = base_cards(p1=p1, **{f"p{i}": card_html(i, ANSWERS[i - 1], stem=f"v2 발문 {i}?") for i in range(2, 6)})
        out = self.built(version=2, cards=cards, extra={
            "legacy": False, "exam_sources": {"p1": {"source": "기출 9강 7", "mode": "기출그대로"}},
            "exam_counts": {"기출그대로": 1}})
        self.assertIn("exam-reuse", codes(check.check(out)))

    def test_webquiz_copy(self):
        q = self.repo / "웹과제" / "9장" / "questions.json"
        q.parent.mkdir(parents=True)
        q.write_text(json.dumps([{"original": {"content": [{"type": "text", "text": "문제 3번 발문이다?"}]}}],
                                ensure_ascii=False), encoding="utf-8")
        self.assertIn("webquiz-copy", codes(check.check(self.built())))


if __name__ == "__main__":
    unittest.main()
```

참고: 비 legacy 세트의 실제 기출 문항 수는 `{"기출그대로": 2, "기출쌍둥이": 2, "기출숫자": 1}`이다. 테스트 세트는 5문항뿐이라 `pack.json`의 `exam_counts`로 기대값을 덮어쓴다. `check.py`는 `exam_counts`가 없으면 위 기본값을 쓴다.

- [ ] **Step 2: 실패 확인**

Run: 테스트 명령
Expected: ERROR — `No module named 'check'`

- [ ] **Step 3: `check.py` 작성**

```python
#!/usr/bin/env python3
"""웹과제 예상 세트 검사기. CLI: check.py <웹과제예상/<N>장/복습문제_…_v<K>.html>"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402  (bio-review-pack 경로도 여기서 추가된다)
import cards  # noqa: E402
import check_html  # noqa: E402
import exam_pool  # noqa: E402

DEFAULT_EXAM_COUNTS = {"기출그대로": 2, "기출쌍둥이": 2, "기출숫자": 1}
TITLE_KIND = {"기출그대로": "기출 예상", "기출쌍둥이": "기출 변형", "기출숫자": "기출 변형"}
FIG_CLASSES = {"fig-ink", "fig-accent", "fig-dot", "fig-text", "fig-muted"}
HELP_PHRASES = ("답을 선택하면", "여기를 눌러", "다른 보기도 눌러")
NOTE_LINK_RE = re.compile(r'href="\.\./\.\./복습노트/\d{4}/정리노트_[^"#]+\.html#s\d+-[a-z0-9-]+"')


def _webquiz_stems(repo: Path, chapter: int) -> set[str]:
    f = repo / "웹과제" / f"{chapter}장" / "questions.json"
    if not f.is_file():
        return set()
    data = json.loads(f.read_text(encoding="utf-8"))
    qs = data["questions"] if isinstance(data, dict) else data
    out = set()
    for q in qs:
        texts = [c["text"] for c in q.get("original", {}).get("content", []) if c.get("type") == "text"]
        if texts:
            out.add(cards.norm(texts[0]))
    return out


def _earlier(src: Path, version: int) -> tuple[set[str], set[str]]:
    """이전 버전들의 (발문 정규화 집합, 사용한 기출 번호 집합)."""
    stems, sources = set(), set()
    for d in src.parent.iterdir():
        m = re.fullmatch(r"v(\d+)", d.name)
        if not m or int(m.group(1)) >= version or not (d / "pack.json").is_file():
            continue
        pack = json.loads((d / "pack.json").read_text(encoding="utf-8"))
        sources |= {e["source"] for e in pack.get("exam_sources", {}).values()}
        sources |= set(pack.get("used_exam_sources", []))
        for f in (d / "cards").glob("p*.html"):
            for c in cards.parse_cards(f.read_text(encoding="utf-8")).values():
                if c["stem"]:
                    stems.add(cards.norm(c["stem"]))
    return stems, sources


def check(html_path: Path | str) -> list[str]:
    html_path = Path(html_path).resolve()
    m = re.search(r"_v(\d+)\.html$", html_path.name)
    if not m:
        return [f"[checker] {html_path.name}: 파일명에 _v<K>가 없음"]
    src = html_path.parent / "src" / f"v{m.group(1)}"
    repo = html_path.parents[2]
    pack = build.load_pack(src)
    source = html_path.read_text(encoding="utf-8")
    probs = [f"[checker] {p}" for p in check_html.check_file(html_path)]

    name, fresh = build.render(src)
    if name != html_path.name or fresh != source:
        probs.append(f"[stale] {html_path.name}: src로 다시 빌드한 결과와 다름")

    parsed = cards.parse_cards(source)
    graded = {cid: c for cid, c in parsed.items() if c["options"]}
    key = pack["answer_key"]
    for cid, c in graded.items():
        got = "ABCDE"[c["answer_index"]] if c["answer_index"] is not None else None
        if key.get(cid) != got:
            probs.append(f"[answer-key] {cid}: 카드 {got}, answer_key {key.get(cid)}")
    if set(key) != set(graded):
        probs.append(f"[answer-key] 세트: answer_key 카드 {sorted(key)} ≠ 채점 카드 {sorted(graded)}")
    if graded and len(graded) % 5 == 0:
        spread = Counter(key.get(cid) for cid in graded)
        if any(spread[l] != len(graded) // 5 for l in "ABCDE"):
            probs.append(f"[answer-spread] 세트: {dict(spread)}")

    exams = pack.get("exam_sources", {})
    for cid, c in graded.items():
        kind = TITLE_KIND.get(exams.get(cid, {}).get("mode"), "예상")
        if not c["title"].startswith(f"{cid.upper()}. [{kind}]"):
            probs.append(f"[structure] {cid}: 제목은 '{cid.upper()}. [{kind}]'로 시작해야 함")
        order = re.findall(r'<h3>|<div class="problem">|<details class="(?:original|hint|solution)">', c["body"])
        if order != ["<h3>", '<div class="problem">', '<details class="original">',
                     '<details class="hint">', '<details class="solution">']:
            probs.append(f"[structure] {cid}: 순서 {order}")
        if "수업과의 연결" not in c["body"] or not NOTE_LINK_RE.search(c["body"]):
            probs.append(f"[structure] {cid}: 수업과의 연결 줄 또는 정리노트 앵커 링크 없음")
        labels = [l for l, _ in c["diagnoses"]]
        if labels != list("ABCDE"[:len(c["options"])]):
            probs.append(f"[diagnosis] {cid}: 보기 진단 {labels}")
        verdict = "틀려요" if "부정형" in c["types"] else "맞아요"
        hits = [l for l, v in c["diagnoses"] if v == verdict]
        if hits != [key.get(cid)]:
            probs.append(f"[diagnosis] {cid}: '{verdict}'인 보기 {hits} (정답 {key.get(cid)} 하나여야 함)")

    counts = Counter(t for c in graded.values() for t in c["types"])
    for t, n in pack.get("types_required", {}).items():
        if counts[t] < n:
            probs.append(f"[types] 세트: {t} {counts[t]}개 < {n}")

    for svg in re.findall(r"<svg\b(?![^>]*aria-hidden).*?</svg>", "".join(c["body"] for c in parsed.values()), re.S):
        bad = []
        if 'role="img"' not in svg:
            bad.append("role=img 없음")
        if re.search(r"#[0-9a-fA-F]{3,6}\b|\s(?:fill|stroke)=\"", svg):
            bad.append("직접 색 지정")
        vb = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) ', svg)
        if not vb or float(vb.group(1)) > 360:
            bad.append("viewBox 너비 > 360")
        if set(re.findall(r'class="([^"]+)"', svg)) - FIG_CLASSES:
            bad.append("fig-* 밖 클래스")
        if bad:
            probs.append(f"[figure] svg: {', '.join(bad)}")

    all_text = " ".join(cards.text(c["body"]) for c in parsed.values())
    for w in list(pack.get("forbidden", [])) + list(HELP_PHRASES):
        if w in all_text:
            probs.append(f"[wording] 세트: '{w}'")
    if re.search(r"[①-⑳]", all_text):
        probs.append("[wording] 세트: 원문자 ①~⑳")
    if re.search(r"<details[^>]*\sopen[\s>=]", source):
        probs.append("[open-details] 세트: 펼친 details 있음")

    earlier_stems, earlier_sources = _earlier(src, pack["version"])
    if not pack.get("legacy"):
        want = pack.get("exam_counts", DEFAULT_EXAM_COUNTS)
        got = Counter(e["mode"] for e in exams.values())
        if dict(got) != want:
            probs.append(f"[exam-count] 세트: {dict(got)} ≠ {want}")
        pool = exam_pool.load_pool(repo, pack["chapter"])
        for cid, e in exams.items():
            c, orig = graded.get(cid), pool.get(e["source"])
            if c is None or orig is None:
                probs.append(f"[exam-missing] {cid}: 카드 또는 원문 {e['source']} 없음")
                continue
            if e["source"] in earlier_sources:
                probs.append(f"[exam-reuse] {cid}: {e['source']}는 이전 버전에서 썼음")
            same_stem = cards.norm(c["stem"]) == cards.norm(orig["stem"])
            keyed = cards.norm(c["options"][c["answer_index"]])
            orig_answer = cards.norm(orig["options"][orig["answer_index"]])
            if e["mode"] == "기출그대로":
                if not same_stem or sorted(map(cards.norm, c["options"])) != sorted(map(cards.norm, orig["options"])) \
                        or keyed != orig_answer:
                    probs.append(f"[exam-verbatim] {cid}: 발문·보기·정답이 {e['source']} 원문과 다름")
            elif e["mode"] == "기출쌍둥이":
                if not same_stem or keyed == orig_answer:
                    probs.append(f"[exam-twin] {cid}: 발문이 원문과 같고 정답 문장은 원문 정답과 달라야 함")
    exam_ids = set(exams)
    quiz = _webquiz_stems(repo, pack["chapter"])
    for cid, c in graded.items():
        if cid in exam_ids:
            continue
        s = cards.norm(c["stem"])
        if s in earlier_stems:
            probs.append(f"[stem-dup] {cid}: 이전 버전과 같은 발문")
        if s in quiz:
            probs.append(f"[webquiz-copy] {cid}: 실제 웹과제 발문과 같음")
    return probs


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    sys.stdout.reconfigure(encoding="utf-8")
    if len(args) != 1:
        print("사용법: check.py <html>", file=sys.stderr)
        return 2
    try:
        probs = check(args[0])
    except (build.BuildError, KeyError, FileNotFoundError) as e:
        print(f"[checker] 검사 실패: {e}")
        return 1
    print("\n".join(probs) if probs else "OK")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: 테스트 명령
Expected: 24 tests OK (cards 4 + exam_pool 3 + build 5 + check 12). 깨진 fixture 테스트가 다른 코드로 실패하면, 그 코드의 단언이 아니라 검사기 로직을 확인한다.

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast
git commit -m "feat(bio-webquiz-forecast): add set checker"
```

---

### Task 5: SKILL.md · references · 심볼릭 링크

**Files:**
- Create: `.agents/skills/bio-webquiz-forecast/SKILL.md`
- Create: `.agents/skills/bio-webquiz-forecast/references/forecast-rules.md`
- Create: `.agents/skills/bio-webquiz-forecast/references/question-blueprint.md`
- Create: `.agents/skills/bio-webquiz-forecast/references/card-brief.md`
- Create: `.agents/skills/bio-webquiz-forecast/references/blind-brief.md`
- Create: `.claude/skills/bio-webquiz-forecast` (symlink)
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_skill_files.py`

**Interfaces:**
- Consumes: 스크립트 CLI 4개(Task 2–4)의 정확한 사용법.

- [ ] **Step 1: 실패하는 테스트**

```python
import re
import unittest

from _util import SKILL


class TestSkillFiles(unittest.TestCase):
    def setUp(self):
        self.md = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.md)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "bio-webquiz-forecast")
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"`((?:references|scripts)/[\w.-]+)`", self.md))
        refs |= set(re.findall(r"\$SKILL/((?:references|scripts)/[\w.-]+)", self.md))
        self.assertGreaterEqual(len(refs), 8)
        for r in sorted(refs):
            self.assertTrue((SKILL / r).exists(), r)

    def test_briefs_point_to_existing_files(self):
        for name in ("card-brief.md", "blind-brief.md"):
            text = (SKILL / "references" / name).read_text(encoding="utf-8")
            for r in re.findall(r"\{SKILL\}/((?:references|scripts)/[\w.-]+)", text):
                self.assertTrue((SKILL / r).exists(), f"{name}: {r}")

    def test_claude_symlink(self):
        link = SKILL.parents[2] / ".claude" / "skills" / "bio-webquiz-forecast"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), SKILL.resolve())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: 테스트 명령
Expected: ERROR/FAIL — `SKILL.md` 없음

- [ ] **Step 3: `SKILL.md` 작성**

````markdown
---
name: bio-webquiz-forecast
description: 생명과학 다음 웹과제(장별 퀴즈)를 예상해 복습문제 형식의 예상 세트 HTML을 만든다. "4장 웹과제 예상해줘", "웹과제 예상문제 만들어줘", "예상문제 한 세트 더", /bio-webquiz-forecast N [lite]처럼 장 번호와 함께 요청할 때 쓴다. 부를 때마다 웹과제예상/<N>장/에 v1, v2 … 새 세트가 쌓인다. 정리노트·복습문제(복습팩)·커닝페이퍼를 만드는 요청에는 쓰지 않는다.
---

# 생명과학 웹과제 예상 세트

장 하나의 다음 예상 세트를 `웹과제예상/<N>장/`에 만든다. 세트는 개요 2장(o1·o2), 기출 재출제 예상 5문항(p1–p5), 새 문제 예상 10문항(p6–p15)이고 정답은 A~E 각 3개다. 중간에 묻지 않고 끝날 때 한 번만 보고한다. 커밋은 제안만 한다.

**인자**: `<N> [lite]`. `lite`면 카드 작성자를 sonnet으로 쓴다. 블라인드 풀이는 lite여도 opus다.

**경로 약속**
- `SKILL`은 이 폴더 `.agents/skills/bio-webquiz-forecast`의 절대 경로, `REPO`는 저장소 루트, `RUN`은 `<scratchpad>/webquiz-forecast/<N>장-v<K>/`(작업 메모·블라인드 사본).
- 셸 상태는 호출 사이에 이어지지 않으므로 명령마다 절대 경로를 쓴다.

## 절차

### 1. 버전 잡기
`python "$SKILL/scripts/build.py" --init "$REPO" <N>` → 새 `웹과제예상/<N>장/src/v<K>/`가 생긴다. 이 명령만 버전 폴더를 만든다. 기존 버전은 고치지 않는다(덮어쓰기 금지). `REPO`에 `복습노트/`가 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다. `복습노트/*/정리노트_*.md` 중 N장을 다룬 파일이 없으면 "N장 정리노트가 없어 예상할 근거가 없습니다"라고 알리고 멈춘다(만든 빈 폴더는 지운다).

### 2. 원천 모으기
- 출제 패턴: `.agents/skills/bio-review-pack/references/webquiz-style.md`, 이전 장 `웹과제/*/questions.json`.
- 이 장 범위: `복습노트/*/장마감_*_<N>장.md`(있으면), 그 장을 다룬 정리노트 MD, STT(`STT/*.md`)의 "시험"·"중요" 발언.
- 기출 풀: `python "$SKILL/scripts/exam_pool.py" "$REPO" <N> > "$RUN/pool.json"`.
- 이전 세트: `웹과제예상/<N>장/src/v*/blueprint.md`와 `pack.json`(쓴 기출 번호·주제).
- 실제 웹과제가 이미 있으면(`웹과제/<N>장/questions.json`) 그 발문은 피하고, 실제 경향을 개요에 반영한다.

### 3. 개요 카드 o1·o2
`references/forecast-rules.md`대로 메인 에이전트가 `src/v<K>/cards/o1.html`, `o2.html`을 쓴다. o2에는 재출제 유력 기출 10개(번호·핵심 한 줄·정답)를 넣는다.

### 4. 설계표
`references/question-blueprint.md`대로 `src/v<K>/blueprint.md`와 `pack.json`(`answer_key`, `exam_sources`, `types_required`, `forbidden` 포함)을 쓴다.

### 5. 카드 작성
`references/card-brief.md`의 브리프로 작성자 3명을 **한 메시지에서 병렬로** 띄운다: p1–p5(기출, 원문 대조), p6–p10, p11–p15. 모델 opus(lite면 sonnet).

### 6. 빌드와 검사
```bash
python "$SKILL/scripts/build.py" "$REPO/웹과제예상/<N>장/src/v<K>"
python "$SKILL/scripts/check.py" "$REPO/웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html"
```
`OK`가 나와야 한다. 문제 줄의 카드 id로 담당 작성자를 찾아 한 번에 모아 되돌린다(최대 2회). 남으면 "미해결"로 보고한다.

### 7. 블라인드 풀이
`python "$SKILL/scripts/blind.py" <html> "$RUN/blind.md"`로 사본을 만들고 `references/blind-brief.md`로 opus 리뷰어 1명을 띄운다. 리뷰어 답이 `answer_key`와 다르거나 "다른 보기도 답이 될 수 있음" 이의가 있으면 그 카드를 고치고 6단계부터 다시 한다. 목표: 15/15 일치, 이의 0.

### 8. 브라우저 확인
저장소 루트에서 `python -m http.server <빈 포트> --bind 127.0.0.1`을 띄우고 세트 HTML을 연다. 375px 가로 스크롤 없음, 콘솔 오류 0, 보기 클릭 채점, 다크 모드 그림을 확인한 뒤 서버를 끈다.

### 9. 보고
```
## 웹과제 예상 <N>장 v<K> 완료
- 파일: 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html (+ src/v<K>/)
- 구성: 개요 2 · 기출 5 (그대로 2 · 쌍둥이 2 · 숫자 1: 기출 <N>강 …) · 새 문제 10
- 정답 분포: A3 B3 C3 D3 E3 · 유형: 부정형 n · 계산 n · 그림 n · ㄱㄴㄷ n · 장섞기 n
- 이전 세트와 겹침: 기출 번호 0 · 발문 0
- 블라인드: 15/15 (고친 카드: …)
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 웹과제예상/<N>장 && git commit -m "feat(webquiz-forecast): add ch<N> forecast v<K>"
```
````

- [ ] **Step 4: `references/forecast-rules.md` 작성**

```markdown
# 개요 카드 규칙 (o1·o2)

## 근거
- 형식 수치(문항 수, 부정형·그림·ㄱㄴㄷ 비율, 기출 재사용 약 30%)는 `bio-review-pack/references/webquiz-style.md` 2절 표와 이전 장 `웹과제/*/questions.json`에서 센 값만 쓴다. 장이 늘면 다시 센다.
- 주제 가능성 별점: ★★★ = 기출에 2회 이상 나오고 정리노트 "시험 직전 한눈에"에 있는 주제, ★★☆ = 둘 중 하나, ★☆☆ = 교과서·노트에만 있는 주제.
- 응시 뒤(`웹과제/<N>장/questions.json`이 있을 때): o1 첫 줄에 "실제 웹과제 응시 후 만든 중간고사 대비 세트"라고 쓰고, 실제 문항 수·유형 수를 형식 수치로 쓴다.

## o1 — 형식과 주제 예상
`<article class="card" id="o1" data-source="예상 <N>장 개요">` 안에 `<h3>형식과 주제 예상</h3>`, `<div class="problem">`에 형식 목록(`<ul>`)과 주제표(`<div class="table-wrap"><table>`: 가능성·주제·예상 질문·함정)를 넣는다. 주제는 12~16행.

## o2 — 막판 체크
`id="o2"`, `<h3>막판 체크</h3>`. `<ol>`로 계산 유형·헷갈리는 짝·그림 판별 포인트를 쓰고, 이어서 `<p><b>재출제 유력 기출 10</b></p>`과 표(`<div class="table-wrap"><table>`: 기출 번호·핵심 한 줄·정답 보기 문장)를 넣는다. 10개는 `question-blueprint.md`의 유력 기출 고르는 규칙으로 고르고, 이번 세트 p1–p5에 쓴 기출을 포함한다. 이전 세트의 유력 목록과 겹쳐도 된다.

## 공통
- 보기(`ul.choices`)·`details`를 넣지 않는다(채점에서 빠지는 카드).
- 문장은 "~해요" 체. 모호성 문구(`모호`, `모두 가능`, `답이 하나`, `해석에 따라`)와 원문자 ①~⑳은 쓰지 않는다.
```

- [ ] **Step 5: `references/question-blueprint.md` 작성**

````markdown
# 설계표와 pack.json

## blueprint.md (src/v<K>/blueprint.md)
15행 표: `카드 | 정답 | 유형(data-types) | 토픽 | 겨냥 혼동 | 기출 출처 | 노트 앵커`. 아래에 "재출제 유력 기출 10"과 고른 이유를 한 줄씩 적는다.

## 고정 배치
- p1–p5 기출: p1·p2 `기출그대로`, p3·p4 `기출쌍둥이`, p5 `기출숫자`(계산·조건이 있는 기출이 없으면 `기출쌍둥이`로 바꾸고 `exam_counts`를 `{"기출그대로":2,"기출쌍둥이":3}`로 적는다).
- p6–p15 새 문제.
- 정답 A~E 각 3개. 기출그대로 카드는 원문 보기 순서를 섞어 정답 글자를 맞춘다.
- `types_required`: `{"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "장섞기": 1}`. 장에 계산 거리가 없으면 `계산`을 줄이고 blueprint에 이유를 쓴다.

## 유력 기출 고르는 규칙
1. o1의 ★★★·★★☆ 주제를 다루는 기출부터.
2. `pool.json`에 있는 기출만(답이 확정된 복습팩 카드).
3. 이전 버전 `pack.json`의 `exam_sources`와 `used_exam_sources`에 있는 번호는 p1–p5에 쓰지 않는다.

## v2 이후 차별화
- 이전 blueprint와 같은 (토픽, 겨냥 혼동, 발문 방향) 조합을 피한다. 이전 세트에서 덜 다룬 ★★★·★★☆ 토픽을 먼저 채운다.
- 같은 혼동을 다시 낼 때는 숫자·생물·그림·발문 방향(옳은 것 ↔ 옳지 않은 것) 중 둘 이상을 바꾼다.
- 발문은 이전 세트와 같으면 안 된다(check.py `stem-dup`).

## pack.json
```json
{
  "course": "생명과학", "chapter": 4, "version": 2,
  "note_href": "../../복습노트/<날짜>/정리노트_<날짜>_<slug>.html",
  "review_title": "4장 웹과제 예상 v2", "review_intro": "…", "footer_review": "근거: …",
  "parts": [
    {"id": "partA", "title": "A. 예상 개요", "short": "예상 개요"},
    {"id": "partB", "title": "B. 기출 재출제 예상", "short": "기출 5"},
    {"id": "partC", "title": "C. 새 문제 예상", "short": "새 문제 10"}
  ],
  "problems": [{"id": "o1", "part": "partA"}, {"id": "o2", "part": "partA"},
               {"id": "p1", "part": "partB"}, "… p5까지 partB", {"id": "p6", "part": "partC"}, "… p15까지 partC"],
  "answer_key": {"p1": "A", "…": "…"},
  "exam_sources": {"p1": {"source": "기출 4강 6", "mode": "기출그대로"}, "…": "…"},
  "types_required": {"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "장섞기": 1},
  "forbidden": ["다음 장 핵심어", "…"],
  "legacy": false, "used_exam_sources": []
}
```
`problems`의 `"…"` 자리는 실제 항목으로 모두 펼쳐 쓴다. `note_href`는 그 장을 처음 다룬 정리노트다. `forbidden`에는 다음 장 핵심어(예: 4장이면 `헬리케이스`, `오카자키`, `코돈`, `전사`, `번역`)와 수업에서 빠진 쪽의 용어를 넣는다.
````

- [ ] **Step 6: `references/card-brief.md` 작성**

````markdown
# 카드 작성자 브리프

---
생명과학 <N>장 웹과제 예상 세트 v<K>의 카드 `<담당 카드 id>`를 쓴다.

- 읽기: `{SKILL}/references/card-brief.md`(이 파일 전체), `{SKILL}/references/question-blueprint.md`, `.agents/skills/bio-review-pack/references/card-rules.md`의 "마크업" 절.
- 계약: `<SRC>/blueprint.md`의 담당 행(정답·유형·토픽·혼동·기출 출처·노트 앵커)과 `<SRC>/pack.json`의 `forbidden`.
- 근거: 정리노트 MD(`<노트 경로들>`), 기출 원문 `<RUN>/pool.json`.
- 출력: `<SRC>/cards/<pid>.html` 카드마다 한 파일. 다른 곳에 쓰지 않는다.
- 자기 검사: `python {SKILL}/scripts/build.py <SRC>`가 성공하고 `python {SKILL}/scripts/check.py <HTML>`에 담당 카드 id 줄이 없을 때까지 고친다(다른 작성자 카드의 문제는 무시).
- 보고: 카드별 한 줄(정답, 유형, 기출 출처), 노트에 없는 사실이 필요했던 곳.
---

## 마크업
```html
<article class="card" id="pN" data-source="예상 <N>장 N" data-types="부정형 계산">
  <h3>PN. [예상] 한 줄 제목</h3>
  <div class="problem"><p>발문</p>
    <figure class="figure"><svg viewBox="0 0 340 200" role="img" aria-label="…">…</svg></figure>   ← 그림 문항만
    <ul><li>ㄱ. …</li><li>ㄴ. …</li><li>ㄷ. …</li></ul>                                          ← ㄱㄴㄷ 문항만
    <ul class="choices"><li>A. …</li><li>B. …</li><li>C. …</li><li>D. …</li><li>E. …</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>…</details>
  <details class="hint"><summary>힌트 보기</summary>…</details>
  <details class="solution"><summary>풀이 보기</summary>
    <ol class="steps">
      <li>A. 맞아요/틀려요. 이유 한 문장.</li> … E까지
      <li>수업과의 연결: …(<a href="../../복습노트/<날짜>/정리노트_<날짜>_<slug>.html#<앵커>">정리노트 "토픽 제목"</a>).</li>
    </ol>
    <p class="answer">정답: X</p>
  </details>
</article>
```
- 제목: 새 문제 `PN. [예상]`, 기출그대로 `PN. [기출 예상]`, 기출쌍둥이·기출숫자 `PN. [기출 변형]`.
- `data-source`: 새 문제 `예상 <N>장 N`, 기출 카드는 `기출 <N>강 M 예상`.
- 부정형("옳지 않은 것") 카드는 정답 보기만 `틀려요`, 나머지 넷은 `맞아요`. 그 밖의 카드는 정답만 `맞아요`. ㄱㄴㄷ 카드는 진술 판정 줄(`<li>ㄱ. 맞아요. …</li>`)을 먼저 쓰고 A~E 진단을 쓴다.
- 기출그대로: 발문·보기 문장은 pool의 원문 그대로(줄바꿈 흔적만 고침), 보기 순서만 blueprint 정답 글자에 맞게 섞는다. 원문 정보: "기출 <N>강 합본 M번을 보기 순서만 바꿔 실은 예상 문제예요."
- 기출쌍둥이: 발문은 원문 그대로, 보기는 새로 써서 원문 정답과 다른 문장이 정답이 되게 한다. 풀이 마지막 단계 앞에 "원문 정답과 달라진 점: …" 한 줄.
- 기출숫자: 원문의 숫자·조건만 바꾸고 보기를 다시 계산한다.
- SVG: 클래스 `fig-ink`, `fig-accent`, `fig-dot`, `fig-text`, `fig-muted`만, 직접 색 금지, `viewBox` 너비 ≤ 360, `id`는 `pN-` 접두어.
- 쓰지 않는 것: `forbidden` 용어, 원문자 ①~⑳, 사용법 안내("답을 선택하면" 등), 모호성 문구(`모호`, `모두 가능`, `답이 하나`, `해석에 따라`, `복수 정답`), STT 녹음 시각. 생식세포의 성별처럼 발문에 없는 조건을 보기에서 가정하지 않는다.
````

- [ ] **Step 7: `references/blind-brief.md` 작성**

```markdown
# 블라인드 풀이 리뷰어 브리프 (opus)

---
생명과학 <N>장 웹과제 예상 세트의 블라인드 풀이를 한다.

- 읽기: `{SKILL}/references/blind-brief.md`(이 파일 전체), 문제 사본 `<RUN>/blind.md`, 정리노트 MD `<노트 경로들>`.
- 문제마다 정리노트 근거로 답을 하나 고른다. 정답·풀이 파일은 보지 않는다.
- 출력 `<RUN>/blind-answers.md`: `| 카드 | 고른 답 | 근거(노트 토픽) | 이의 |` 표.
  - `이의`에는 다른 보기도 답이 될 수 있는 이유, 발문에 없는 조건이 필요한 경우, 노트 밖 사실이 필요한 경우를 쓴다. 없으면 빈칸.
- 보고: 표 요약과 이의 목록.
---
```

- [ ] **Step 8: 심볼릭 링크**

Run: `cd .claude/skills && ln -s ../../.agents/skills/bio-webquiz-forecast bio-webquiz-forecast && cd ../..`
(Windows Git Bash에서 `ln -s`가 복사본을 만들면 `MSYS=winsymlinks:nativestrict ln -s …`로 다시 만든다. 기존 링크들이 `git ls-files -s .claude/skills`에서 모드 `120000`이므로 같은 모드여야 한다.)

- [ ] **Step 9: 통과 확인**

Run: 테스트 명령
Expected: 28 tests OK

- [ ] **Step 10: 커밋**

```bash
git add .agents/skills/bio-webquiz-forecast .claude/skills/bio-webquiz-forecast
git commit -m "feat(bio-webquiz-forecast): add skill docs, briefs and symlink"
```

---

### Task 6: 2026-10-07 4장 세트를 v1으로 이전

**Files:**
- Move: `웹과제예상/src/4장/` → `웹과제예상/4장/src/v1/`
- Delete: `웹과제예상/복습문제_4장_웹과제예상.html`, `scripts/build_webquiz_forecast.py`, `tests/test_webquiz_forecast_ch4.py`
- Modify: `웹과제예상/4장/src/v1/pack.json`, `웹과제예상/4장/src/v1/cards/*.html`(링크 깊이)
- Create (빌드): `웹과제예상/4장/복습문제_4장_웹과제예상_v1.html`
- Create: `웹과제예상/4장/src/v1/blueprint.md`
- Create: `.agents/skills/bio-webquiz-forecast/tests/test_repo_v1.py`

**Interfaces:**
- Consumes: `build.build`, `check.check`.

- [ ] **Step 1: 실패하는 테스트 `test_repo_v1.py`**

```python
import unittest

from _util import SKILL
import check

REPO = SKILL.parents[2]
V1 = REPO / "웹과제예상" / "4장" / "복습문제_4장_웹과제예상_v1.html"


class TestRepoV1(unittest.TestCase):
    def test_v1_passes_check(self):
        self.assertTrue(V1.is_file(), V1)
        self.assertEqual(check.check(V1), [])

    def test_old_layout_removed(self):
        for p in ("웹과제예상/복습문제_4장_웹과제예상.html", "웹과제예상/src/4장",
                  "scripts/build_webquiz_forecast.py", "tests/test_webquiz_forecast_ch4.py"):
            self.assertFalse((REPO / p).exists(), p)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: 테스트 명령
Expected: FAIL — `test_v1_passes_check`(파일 없음), `test_old_layout_removed`

- [ ] **Step 3: 파일 이동·삭제**

```bash
mkdir -p 웹과제예상/4장/src
git mv 웹과제예상/src/4장 웹과제예상/4장/src/v1
git rm -q 웹과제예상/복습문제_4장_웹과제예상.html scripts/build_webquiz_forecast.py tests/test_webquiz_forecast_ch4.py
sed -i 's#href="\.\./복습노트/#href="../../복습노트/#g' 웹과제예상/4장/src/v1/cards/*.html
```

- [ ] **Step 4: `pack.json` 교체**

`웹과제예상/4장/src/v1/pack.json` 전체를 아래로 바꾼다(`problems`는 기존 17항목 그대로):

```json
{
  "course": "생명과학",
  "chapter": 4,
  "version": 1,
  "note_href": "../../복습노트/0929/정리노트_0929_Heredity.html",
  "review_title": "4장 유전 웹과제 예상 v1",
  "review_intro": "2026-10-08(목) 4장 웹과제를 대비한 예상 개요 2장과 예상 모의문제 15개예요. 1~3장 웹과제 46문항의 출제 패턴과 4장 기출·정리노트로 추론했어요. 실제 문제가 아니에요.",
  "footer_review": "근거: webquiz-style.md(1~3장 웹과제 46문항 집계), 0929·1001 정리노트, 장마감_1001_4장.md",
  "parts": [
    {"id": "partA", "title": "A. 예상 개요", "short": "예상 개요"},
    {"id": "partB", "title": "B. 예상 모의문제", "short": "모의문제 15"}
  ],
  "problems": [
    {"id": "o1", "part": "partA"}, {"id": "o2", "part": "partA"},
    {"id": "p1", "part": "partB"}, {"id": "p2", "part": "partB"}, {"id": "p3", "part": "partB"},
    {"id": "p4", "part": "partB"}, {"id": "p5", "part": "partB"}, {"id": "p6", "part": "partB"},
    {"id": "p7", "part": "partB"}, {"id": "p8", "part": "partB"}, {"id": "p9", "part": "partB"},
    {"id": "p10", "part": "partB"}, {"id": "p11", "part": "partB"}, {"id": "p12", "part": "partB"},
    {"id": "p13", "part": "partB"}, {"id": "p14", "part": "partB"}, {"id": "p15", "part": "partB"}
  ],
  "answer_key": {"p1": "D", "p2": "B", "p3": "C", "p4": "E", "p5": "B", "p6": "C", "p7": "A", "p8": "C",
                 "p9": "E", "p10": "A", "p11": "D", "p12": "B", "p13": "E", "p14": "A", "p15": "D"},
  "forbidden": ["헬리케이스", "오카자키", "코돈", "전사", "번역", "유전상담"],
  "types_required": {"부정형": 5, "계산": 4, "그림": 2, "ㄱㄴㄷ": 1, "쌍둥이": 1, "장섞기": 1},
  "exam_sources": {},
  "legacy": true,
  "used_exam_sources": ["기출 4강 39", "기출 4강 32"]
}
```

- [ ] **Step 5: `blueprint.md` 작성** (`웹과제예상/4장/src/v1/blueprint.md`)

```markdown
# 4장 v1 설계표 (legacy — 기출 재출제 규칙 이전에 만든 세트)

| 카드 | 정답 | 유형 | 토픽 | 겨냥 혼동 | 기출 출처 | 노트 앵커 |
|---|---|---|---|---|---|---|
| p1 | D | 부정형 용어 | 유전 용어 | 같은 유전자 vs 같은 대립유전자 | - | 0929#s0-locus |
| p2 | B | 계산 | 양성잡종 | 9:3:3:1 각 칸 | - | 0929#s0-independent |
| p3 | C | 계산 상황전이 | 배우자 종류 | 동형접합 쌍까지 세기 | - | 0929#s0-independent |
| p4 | E | 계산 | 검정교배 | 교배 종류별 비 | - | 0929#s2-morgan |
| p5 | B | 계산 상황전이 | X 연관 열성 | 아들·딸·전체 확률 | - | 0929#s3-carrier |
| p6 | C | 부정형 성연관 | 성연관 정의 | 위치 vs 기능 | - | 0929#s3-carrier |
| p7 | A | 그림 구조변형 쌍둥이 | 구조 변형 | 전좌 vs 역위 | 기출 4강 39 기반 | 0929#s4-structural |
| p8 | C | 그림 ㄱㄴㄷ 비분리 장섞기 | 비분리 | 1분열 vs 2분열, 상동 vs 자매 | - | 1001#s1-nondisjunction |
| p9 | E | 부정형 염색체수 | 이수성·다배수성 | 하나 vs 세트 | - | 1001#s1-polyploidy |
| p10 | A | ABO 상황전이 | ABO | 복대립유전자 개수 | - | 0929#s1-abo |
| p11 | D | 부정형 우성관계 | 불완전·공동우성 | 중간 vs 둘 다 | - | 0929#s1-incomplete |
| p12 | B | 쌍둥이 용어 | 다면발현 | 다인자 vs 다면 방향 | 기출 4강 32 기반 | 0929#s1-many |
| p13 | E | 계산 연관 상황전이 | 재조합 빈도 | 식과 부모형 | - | 0929#s2-frequency |
| p14 | A | 부정형 연관 장섞기 | 연관·교차 | 자매 vs 비자매 | - | 0929#s2-morgan |
| p15 | D | 계산 상황전이 | 열성 질환 | 조건부 확률 2/3 | - | 1001#s2-recessive-disease |

v2부터는 `used_exam_sources`(기출 4강 39·32)를 p1–p5에 쓰지 않는다.
```

- [ ] **Step 6: 빌드와 검사**

```bash
python .agents/skills/bio-webquiz-forecast/scripts/build.py 웹과제예상/4장/src/v1
python .agents/skills/bio-webquiz-forecast/scripts/check.py 웹과제예상/4장/복습문제_4장_웹과제예상_v1.html
```
Expected: 빌드 경로 한 줄, 그다음 `OK`. 문제가 나오면:
- `structure … 제목`: v1 카드 제목은 `PN. [예상]`이므로 통과해야 한다. 나오면 링크 치환(Step 3)을 확인한다.
- `diagnosis`: v1 카드는 2026-10-07에 같은 규칙으로 검사했다. 부정형 카드의 `틀려요`가 정답 하나뿐인지(이번 규칙이 더 엄격함) 확인하고, 실제 내용 오류일 때만 카드를 고친다. 고치면 ledger에 Ruling으로 남긴다.

- [ ] **Step 7: 통과 확인**

Run: 테스트 명령
Expected: 30 tests OK

- [ ] **Step 8: 커밋**

```bash
git add -A 웹과제예상 scripts tests .agents/skills/bio-webquiz-forecast
git commit -m "feat(webquiz-forecast): move ch4 forecast to versioned v1 layout"
```

- [ ] **Step 9: 브라우저 확인(v1)**

저장소 루트에서 `python -m http.server 8767 --bind 127.0.0.1`(백그라운드)을 띄우고 `http://127.0.0.1:8767/웹과제예상/4장/복습문제_4장_웹과제예상_v1.html`을 연다(`mcp__Claude_Browser__preview_start`). `javascript_tool`:
```js
({ range: document.body.dataset.range, scroll: document.documentElement.scrollWidth, view: innerWidth,
   graded: Object.keys(JSON.parse(document.getElementById('review-interaction-model').textContent).cards).length,
   note: (await fetch(document.querySelector('a.top-link').href)).status })
```
Expected(모바일 프리셋): `range: "4장-v1"`, `scroll <= view`, `graded: 15`, `note: 200`. `read_console_messages` 오류 0. 끝나면 desktop 프리셋으로 되돌리고 서버를 끈다.
