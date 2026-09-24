# bio-review-pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 생명과학 저장소의 `summary-note`·`study-note-eli5` 두 스킬을 머신러닝기초 `ml-review-pack`을 옮긴 단일 스킬 `bio-review-pack`으로 대체한다.

**Architecture:** ML 스킬의 스크립트 4개·템플릿 2개·테스트를 `.agents/skills/bio-review-pack/`(정본)에 복사하고, 과목 전용 부분(references 문서, 문제 선별·객관식 카드 규칙, 경로)을 새로 쓴다. 스크립트는 세 곳만 고친다(과목명 제목, 카드 그림 복사·검사, MD 그림 변환). `.claude/skills/bio-review-pack/SKILL.md`는 정본을 가리키는 진입점이다. 마지막에 옛 스킬과 그 전용 테스트를 지운다.

**Tech Stack:** Python 3 표준 라이브러리(스킬 스크립트), `unittest`, PyMuPDF(`fitz`, 스킬 문서의 스니펫에서만), KaTeX CDN(템플릿에 이미 포함).

**Spec:** `docs/superpowers/specs/2026-09-24-bio-review-pack-design.md`

## Global Constraints

- 원본 ML 스킬 경로: `ML=/Users/hyunjun_macbook_pro/Documents/Univ/머신러닝기초/.claude/skills/ml-review-pack` (읽기만 한다. 절대 수정하지 않는다).
- 새 스킬 정본: `.agents/skills/bio-review-pack/` · 진입점: `.claude/skills/bio-review-pack/SKILL.md`.
- 템플릿 두 개는 ML 것과 바이트 단위로 같아야 한다(`cmp`로 확인). `assets/backup-*` 폴더는 복사하지 않는다.
- 스킬 스크립트는 표준 라이브러리만 쓴다.
- 산출물 파일명: `정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, 같은 이름 `.md`, `figures_<range>/` (`복습노트/<range>/` 안).
- 교수님: 이영만 교수님. 과목명 문자열: `생명과학`.
- 보충 배지 글자: `보충 · 수업에서 다루지 않았어요`.
- 스킬 산출물 어디에도 원문자(①~⑳)를 쓰지 않는다. 기출 보기 번호는 `(1)`~`(5)`, 웹과제 보기는 bank의 `A.`~`E.`.
- 스킬 테스트 명령: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
- 저장소 테스트 명령: `.venv-question-bank/bin/python -m unittest discover tests` (시작 기준선: 225 tests OK, skipped=1)
- 명령은 모두 저장소 루트(`/Users/hyunjun_macbook_pro/Documents/Univ/생명과학`)에서 실행한다.
- `git add .`·디렉터리 통째 add 금지(새로 만든 스킬 폴더 자체는 예외), `*.zip` add 금지. 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Task 1: ML 스킬 복사와 기준선 테스트

**Files:**
- Create: `.agents/skills/bio-review-pack/assets/note-template.html`, `.agents/skills/bio-review-pack/assets/review-template.html` (ML 복사)
- Create: `.agents/skills/bio-review-pack/scripts/{manifest,assemble,check_html,html2md}.py` (ML 복사)
- Create: `.agents/skills/bio-review-pack/tests/{_util,test_assemble,test_check_html,test_html2md,test_manifest}.py` (ML 복사)
- Create: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/` (ML 복사)
- Modify: `.agents/skills/bio-review-pack/tests/test_manifest.py` (회귀 fixture 테스트 제거)
- Modify: `.agents/skills/bio-review-pack/tests/_util.py` (경로 주석)

**Interfaces:**
- Produces: `manifest.load/validate/note_name/review_name/fig_dir_name`, `assemble.assemble(run_dir, out_dir) -> (note_path, review_path)`, `check_html.check_pack/check_common/parse_html`, `html2md.convert_pack/check_md` — ML과 같은 시그니처.

- [ ] **Step 1: 작업 트리 확인**

Run: `git status --short`
커밋하지 않은 사용자 변경(0917 노트, 0915·0917 eli5, STT 등)이 보이면 여기서 멈추고 사용자에게 먼저 커밋할지 묻는다. 사용자 파일을 직접 커밋하지 않는다. 깨끗해지면 브랜치를 만든다:

```bash
git switch -c feat/bio-review-pack
```

- [ ] **Step 2: 파일 복사**

```bash
ML=/Users/hyunjun_macbook_pro/Documents/Univ/머신러닝기초/.claude/skills/ml-review-pack
SK=.agents/skills/bio-review-pack
mkdir -p "$SK/assets" "$SK/scripts" "$SK/references" "$SK/tests/fixtures"
cp "$ML/assets/note-template.html" "$ML/assets/review-template.html" "$SK/assets/"
cp "$ML/scripts/manifest.py" "$ML/scripts/assemble.py" "$ML/scripts/check_html.py" "$ML/scripts/html2md.py" "$SK/scripts/"
cp "$ML/tests/_util.py" "$ML/tests/test_assemble.py" "$ML/tests/test_check_html.py" "$ML/tests/test_html2md.py" "$ML/tests/test_manifest.py" "$SK/tests/"
cp -R "$ML/tests/fixtures/mini-run" "$SK/tests/fixtures/"
cmp "$ML/assets/note-template.html" "$SK/assets/note-template.html" && cmp "$ML/assets/review-template.html" "$SK/assets/review-template.html" && echo TEMPLATES-IDENTICAL
```
Expected: `TEMPLATES-IDENTICAL`. `test_regression_0909_0916.py`, `test_skill_files.py`, `fixtures/manifest-0909-0916.json`은 복사하지 않는다(`test_skill_files.py`는 Task 5에서 새로 만든다).

- [ ] **Step 3: ML 전용 테스트 제거**

`.agents/skills/bio-review-pack/tests/test_manifest.py`에서 아래 메서드를 지운다:

```python
    def test_regression_manifest_is_valid(self):
        manifest.load(FIXTURES / "manifest-0909-0916.json")

```
그리고 import 줄 `from _util import FIXTURES, MINI_RUN`을 `from _util import MINI_RUN`으로 바꾼다.

`.agents/skills/bio-review-pack/tests/_util.py`에서
`REPO = SKILL.parents[2]  # <repo>/.claude/skills/ml-review-pack`을
`REPO = SKILL.parents[2]  # <repo>/.agents/skills/bio-review-pack`로 바꾼다.

- [ ] **Step 4: 테스트 실행**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK` (실패 0)

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-review-pack
git commit -m "feat(bio-review-pack): copy ml-review-pack scripts, templates and tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: 생명과학 fixture, 과목 제목, 카드 그림 복사·검사

**Files:**
- Modify: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/manifest.json`
- Modify: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/sections/s1.html`
- Create: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/cards/p2.html`
- Create: `.agents/skills/bio-review-pack/tests/fixtures/mini-run/figures/p2.png`
- Modify: `.agents/skills/bio-review-pack/scripts/assemble.py`
- Modify: `.agents/skills/bio-review-pack/scripts/check_html.py`
- Test: `.agents/skills/bio-review-pack/tests/test_assemble.py`, `.agents/skills/bio-review-pack/tests/test_check_html.py`

**Interfaces:**
- Consumes: Task 1 스크립트.
- Produces: `assemble.copy_figures(run_dir: Path, out_dir: Path, range_: str) -> int` (복사한 파일 수). `assemble.assemble()`이 두 HTML을 쓴 뒤 호출한다. `check_html.Doc.img_srcs: list[str]`, Problem 코드 `broken-image`. `check_html.SUPP_LABEL == "보충 · 수업에서 다루지 않았어요"`.

- [ ] **Step 1: fixture를 생명과학용으로 바꾸기**

`tests/fixtures/mini-run/manifest.json`에서:
- `"course": "머신러닝기초"` → `"course": "생명과학"`
- `"review_title": "복습문제 1선 — 테스트"` → `"review_title": "복습문제 2선 — 테스트"`
- `"parts"` 배열을 다음으로 바꾼다:
```json
 "parts": [{"id": "partA", "title": "A. 교과서 예제", "short": "A 교과서 예제"}, {"id": "partB", "title": "B. 기출", "short": "B 기출"}],
```
- `"problems"` 배열의 p1 뒤에 항목을 하나 더한다(쉼표 주의):
```json
  {"id": "p2", "part": "partB", "source": "기출 3강 7", "variant": false, "anchor": "s1-var", "level": 1, "date": "0101", "terms": ["정답: (2)", "자매염색분체"], "answer": "(2)"}
```

`tests/fixtures/mini-run/sections/s1.html`에서
`<span class="badge supp">보충 · 수업에서 유도하진 않았어요</span>`를
`<span class="badge supp">보충 · 수업에서 다루지 않았어요</span>`로 바꾼다.

`tests/fixtures/mini-run/cards/p2.html` 새로 만들기:
```html
      <article class="card" id="p2" data-source="기출 3강 7">
        <h3>P2. 동원체의 뜻</h3>
        <div class="problem"><p>동원체는 (     ) 지역이에요.</p>
          <figure class="figure"><img src="figures_0101-0102/p2.png" alt="중기 염색체 그림"></figure>
          <ul class="choices"><li>(1) 핵이 위치하는</li><li>(2) 자매염색분체가 서로 부착되어 있는</li><li>(3) 중기 염색체가 정렬되는</li></ul></div>
        <details class="original"><summary>원문 정보 보기</summary>기출 3강 합본 7번 (PDF 1쪽)</details>
        <details class="hint"><summary>힌트 보기</summary>두 자매염색분체가 어디서 붙어 있는지 떠올려 보세요.</details>
        <details class="solution"><summary>풀이 보기</summary><ol class="steps"><li>(1) 틀려요. 핵은 세포 안의 소기관이에요.</li><li>(2) 맞아요. 자매염색분체는 동원체에서 붙어 있어요.</li><li>(3) 틀려요. 염색체가 정렬되는 곳은 중기판이에요.</li></ol><p class="answer">정답: (2)</p></details>
      </article>
```

1×1 PNG fixture 만들기:
```bash
python3 - <<'EOF'
import os, struct, zlib
def chunk(t, d):
    return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")) + chunk(b"IEND", b""))
d = ".agents/skills/bio-review-pack/tests/fixtures/mini-run/figures"
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "p2.png"), "wb").write(png)
print("ok")
EOF
```

- [ ] **Step 2: 실패하는 테스트 쓰기**

`tests/test_assemble.py`에서:
- `self.assertIn("<title>머신러닝기초 정리노트 0101-0102</title>", self.note_html)`를 아래 두 줄로 바꾼다:
```python
        self.assertIn("<title>생명과학 정리노트 0101-0102</title>", self.note_html)
        self.assertIn("<title>생명과학 복습문제 0101-0102</title>", self.review_html)
```
- `test_review_parts` 본문 끝에 추가:
```python
        self.assertIn('<section id="partB"><h2>B. 기출</h2>', self.review_html)
```
- `test_review_parts` 바로 뒤에 새 테스트 추가:
```python
    def test_card_figures_copied(self):
        # 카드 원문 그림(RUN/figures/)은 산출물 figures_<range>/ 로 복사된다.
        self.assertEqual((self.tmp / "figures_0101-0102" / "p2.png").read_bytes(),
                         (MINI_RUN / "figures" / "p2.png").read_bytes())
```

`tests/test_check_html.py`에서:
- `external_codes` 도우미의 반환을 external만 보도록 바꾼다(로컬 그림 검사가 섞이지 않게):
```python
    def external_codes(self, head: str, body: str = "") -> list[str]:
        src = f'<html lang="ko"><head>{head}</head><body>{body}</body></html>'
        return [p.code for p in check_html.check_common(check_html.parse_html(src), src, Path("x.html")) if p.code == "external"]
```
- `test_widget_without_static` 바로 뒤에 새 테스트 추가:
```python
    def test_local_image_must_exist(self):
        with tempfile.TemporaryDirectory() as d:
            src = '<html lang="ko"><body><img src="figures_x/a.png" alt=""><img src="data:image/png;base64,AA" alt=""></body></html>'
            path = Path(d) / "x.html"
            codes = [p.code for p in check_html.check_common(check_html.parse_html(src), src, path)]
            self.assertEqual(codes, ["broken-image"])
            (Path(d) / "figures_x").mkdir()
            (Path(d) / "figures_x" / "a.png").write_bytes(b"x")
            codes = [p.code for p in check_html.check_common(check_html.parse_html(src), src, path)]
            self.assertEqual(codes, [])
```
- `test_missing_supp_badge`의 edit 대상 문자열을 바꾼다:
```python
        self.edit("sections/s1.html", '<span class="badge supp">보충 · 수업에서 다루지 않았어요</span>', "")
```

- [ ] **Step 3: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: FAIL — `test_sections_toc_and_titles`(제목), `test_card_figures_copied`(파일 없음), `test_local_image_must_exist`(broken-image 없음), `test_mini_pack_passes`·`test_missing_supp_badge`(missing-supp) 등.

- [ ] **Step 4: assemble.py 구현**

`scripts/assemble.py`:
- 모듈 docstring의 `실행 폴더 구조:` 목록 끝(`RUN/cards/<problem-id>.html ...` 줄 다음)에 한 줄 추가:
```
  RUN/figures/*                    (카드 원문 그림 등, out/figures_<range>/ 로 복사)
```
- import 블록에 `import shutil`을 `import re` 다음 줄에 추가.
- `build_note`의 `"PAGE_TITLE": esc(f"머신러닝기초 정리노트 {m['range']}"),`를 `"PAGE_TITLE": esc(f"{m['course']} 정리노트 {m['range']}"),`로.
- `build_review`의 `"PAGE_TITLE": esc(f"머신러닝기초 복습문제 {m['range']}"),`를 `"PAGE_TITLE": esc(f"{m['course']} 복습문제 {m['range']}"),`로.
- `def assemble(` 바로 위에 추가:
```python
def copy_figures(run_dir: Path, out_dir: Path, range_: str) -> int:
    """RUN/figures/ 의 파일을 out/figures_<range>/ 로 복사하고 개수를 돌려준다."""
    src = run_dir / "figures"
    if not src.is_dir():
        return 0
    dst = out_dir / manifest_mod.fig_dir_name(range_)
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src.iterdir()):
        if f.is_file():
            shutil.copy2(f, dst / f.name)
            count += 1
    return count
```
- `assemble()` 안의 `review_path.write_text(review_html, encoding="utf-8")` 다음 줄에 추가:
```python
    copy_figures(run_dir, out_dir, m["range"])
```

- [ ] **Step 5: check_html.py 구현**

`scripts/check_html.py`:
- `SUPP_LABEL = "보충 · 수업에서 유도하진 않았어요"` → `SUPP_LABEL = "보충 · 수업에서 다루지 않았어요"`
- `Doc` dataclass의 `hrefs: list[str] = field(default_factory=list)` 다음 줄에 추가:
```python
    img_srcs: list[str] = field(default_factory=list)
```
- `_Parser.handle_starttag`의 `# 원격 리소스:` 주석 바로 위에 추가:
```python
        src = a.get("src", "")
        if tag == "img" and src and not is_remote(src) and not src.startswith("data:"):
            self.doc.img_srcs.append(src)
```
- `check_common`의 `out += [Problem("broken-link", ...)]` 줄 다음에 추가:
```python
    out += [Problem("broken-image", name, s) for s in doc.img_srcs if not (Path(path).parent / unquote(s)).exists()]
```
- 모듈 docstring의 `- 공통 검사:` 줄 끝 `위젯 정적 대체물`을 `위젯 정적 대체물, 로컬 그림 파일`로 바꾼다.

- [ ] **Step 6: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK`

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-review-pack/scripts/assemble.py .agents/skills/bio-review-pack/scripts/check_html.py .agents/skills/bio-review-pack/tests
git commit -m "feat(bio-review-pack): course title, card figure copy and image check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: html2md가 카드 그림(`<img>`)을 MD로 옮기기

**Files:**
- Modify: `.agents/skills/bio-review-pack/scripts/html2md.py` (`inline()`, `figure` 분기)
- Test: `.agents/skills/bio-review-pack/tests/test_html2md.py`

**Interfaces:**
- Consumes: Task 2 fixture(`cards/p2.html`, `figures/p2.png`)와 `assemble.copy_figures`.
- Produces: MD에 `![<alt>](<src>)` 줄. `convert_pack`/`check_md` 시그니처 변화 없음.

- [ ] **Step 1: 실패하는 테스트 쓰기**

`tests/test_html2md.py`의 `TestHtml2Md` 클래스, `test_outputs_and_check_pass` 바로 뒤에 추가:
```python
    def test_card_image_kept_in_markdown(self):
        review_md = Path(self.review_md).read_text(encoding="utf-8")
        self.assertIn("![중기 염색체 그림](figures_0101-0102/p2.png)", review_md)
        self.assertIn("자매염색분체가 서로 부착되어 있는", review_md)
        self.assertEqual(html2md.check_md(self.review, self.review_md), [])
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_html2md.py`
Expected: FAIL — `![중기 염색체 그림](...)`가 MD에 없음.

- [ ] **Step 3: 구현**

`scripts/html2md.py`의 `inline()`에서 `if t == "a":` 분기 바로 위에 추가:
```python
    if t == "img":
        alt = node.attrs.get("alt", "그림").replace("[", "(").replace("]", ")")
        return f"![{alt}]({node.attrs.get('src', '')})"
```

`block(node, ctx)` 함수의 `if t == "figure":` 분기를 다음으로 바꾼다:
```python
    if t == "figure":
        svg = next(node.find_all(lambda n: n.tag == "svg"), None)
        img = None if svg else next(node.find_all(lambda n: n.tag == "img"), None)
        cap = next(node.find_all(lambda n: n.tag == "figcaption"), None)
        alt = (svg.attrs.get("aria-label", "그림") if svg else "그림").replace("[", "(").replace("]", ")")
        if svg:
            lines = [f"![{alt}]({export_svg(svg, ctx)})"]
        elif img:
            lines = [inline(img, ctx)]
        else:
            lines = []
        if cap:
            lines += ["", "*" + "".join(inline(c, ctx) for c in cap.children).strip() + "*"]
        return lines
```
모듈 docstring의 `- 인라인 SVG 그림은 ...` 줄 다음에 한 줄 추가:
```
- <img>(카드 원문 그림)는 같은 상대 경로의 ![alt](src)로 옮긴다.
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK`

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/bio-review-pack/scripts/html2md.py .agents/skills/bio-review-pack/tests/test_html2md.py
git commit -m "feat(bio-review-pack): keep card images in markdown export

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: references 문서 8개

**Files:**
- Create: `.agents/skills/bio-review-pack/references/widget-rules.md` (ML 복사 + 예시 한 줄)
- Create: `.agents/skills/bio-review-pack/references/browser-check.md` (ML 복사 + 그림 검사)
- Create: `.agents/skills/bio-review-pack/references/stt-summary-prompt.md`
- Create: `.agents/skills/bio-review-pack/references/manifest-guide.md`
- Create: `.agents/skills/bio-review-pack/references/content-rules.md`
- Create: `.agents/skills/bio-review-pack/references/problem-selection.md`
- Create: `.agents/skills/bio-review-pack/references/card-rules.md`
- Create: `.agents/skills/bio-review-pack/references/review-prompt.md`

**Interfaces:**
- Consumes: Task 2의 보충 배지 글자, `RUN/figures/` 규약, 카드 마크업.
- Produces: SKILL.md(Task 5)가 가리키는 파일 8개와 그 안의 브리프 자리표시자 `<RUN>`, `<SKILL>`, `<sid>`, `<forbidden 목록>`, `<preview_topic>`, `<쪽>`, `<위젯>`, `<이 섹션의 links 목록>`, `<이 섹션 토픽이 받쳐야 할 문항>`, `<담당 카드 id>`, `<range>`. 실행 산출 파일 `RUN/question-audit.md`, `RUN/key-check.md`, `RUN/problem-pages.txt`, `RUN/work/exam/<N>강-p<k>.png`, `RUN/figures/p<N>.png`, `RUN/work/blind-<range>.md`.

- [ ] **Step 1: widget-rules.md, browser-check.md 복사 후 수정**

```bash
ML=/Users/hyunjun_macbook_pro/Documents/Univ/머신러닝기초/.claude/skills/ml-review-pack
cp "$ML/references/widget-rules.md" "$ML/references/browser-check.md" .agents/skills/bio-review-pack/references/
```
`widget-rules.md`에서
`- 팩 전체에 0~2개. "슬라이더를 움직이면 개념이 보이는" 경우만(예: λ와 과적합, prior 강도와 MAP).`를
`- 팩 전체에 0~2개. "슬라이더를 움직이면 개념이 보이는" 경우만(예: 세포주기 단계별 DNA 양, 기질 농도와 효소 반응 속도).`로 바꾼다.

`browser-check.md`의 `## 복습문제` 절 스크립트에서 `hScroll: await overflowScreens(),` 줄 바로 위에 한 줄 추가:
```js
  brokenImgs: Array.from(document.querySelectorAll('article.card img')).filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.getAttribute('src')),
```
그리고 그 아래 `통과:` 문장의 `` `katexErrors: 0`, `hScroll: []`. ``을 `` `katexErrors: 0`, `brokenImgs: []`, `hScroll: []`. ``로 바꾼다.

- [ ] **Step 2: stt-summary-prompt.md 쓰기**

`.agents/skills/bio-review-pack/references/stt-summary-prompt.md`:
````markdown
# STT 요약 에이전트 지시문

메인 에이전트는 날짜마다 아래 브리프로 에이전트 1명을 띄운다(병렬, model: opus / lite: sonnet).

---
생명과학(이영만 교수님) <MMDD> 수업 녹음 전사를 정밀 요약한다.

- 입력(읽기 전용): `<RUN>/repo/STT/<MMDD 생명.md>` — **처음부터 끝까지 전부** 읽는다. 건너뛰지 않는다.
- 대조 자료: `<RUN>/repo/강의노트/<N장 *.pdf>` 텍스트(메인이 추출해 `<RUN>/slides.txt`에 둠, 쪽마다 `=== N장 pK ===`)
- 출력: `<RUN>/summaries/stt-<MMDD>.md` 한 파일만 쓴다. 다른 곳에는 쓰지 않는다(임시 파일은 아래 규칙).
- 임시·보조 파일은 `<RUN>/work/` 아래에만 둔다. 저장소(`STT/`, `강의노트/`, `교과서/`, `23, 24 소스/`, `웹과제/`, `복습노트/`)와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 복사하거나 이름을 바꾸지 말고 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 그 경로로 연다.

출력 형식:
1. `# <MMDD> 생명과학 강의 개요 (이영만 교수, <YYYY-MM-DD>)`
2. **총평**: 녹음 길이, 이번 수업이 다룬 강의노트 장과 쪽 범위(예: "3장 p12–20"), **시작하지 않은** 쪽, 흐름 한 줄.
3. `## 0. 지난 수업 복습`: 교수님이 도입부에서 앞 수업을 다시 짚었으면 요점 3~5줄과 타임스탬프. 없으면 "없음".
4. 흐름 순서대로 `## N. 제목 (Part PP MM:SS–MM:SS)` 절. 각 절에:
   - **핵심 내용**: 정의와 성립 조건, 인과(왜 그렇게 되는가), 과정이면 위치·입력·출력. 강의노트에 없는 설명은 `[강의노트 외]` 표시.
   - **비유와 일화**: 개념을 싣는 비유만. 순수 잡담(출석, 자리, 공지 등)은 쓰지 않는다.
   - **학생과의 대화**: 학생 이름은 "한 학생".
   - 강조 발언: 원문 인용 + `(MM:SS)`. "중요", "시험", "꼭", "외워" 같은 표현이 붙은 발언은 모두.
   - `⚠️ 혼동 지점:` 교수님이 반복했거나, 학생에게 되물었거나, "헷갈린다"고 말한 곳. 무엇과 무엇이 헷갈리는지 한 줄씩, 빠짐없이.
   - "나중에 할게요", "교재 보세요"처럼 미룬 설명은 `🕳️ 미룬 설명:`으로 표시.
5. `## 끊긴 지점`: 마지막 발언 원문과 타임스탬프, 개념 중간에서 끊겼는지, 다음 시간 예고 항목.
6. `## 슬라이드 대조표`: | 쪽 | 다룸/일부/예고만/안 다룸 | 근거 타임스탬프 |
7. `## 용어 목록`: 수업에서 실제로 쓴 용어를 `한국어(영어)` 형태로(정리노트 required_terms 후보). 화학식·반응식은 쓴 그대로.
8. `## 말실수 정정`: STT 오인식(비슷한 소리의 생물 용어 등) 또는 교수님 말실수와 올바른 형태.

타임스탬프가 파트마다 00:00부터 다시 시작하면 `(P03 04:12)`처럼 파트 번호를 붙인다.

보고: 파일 경로와 총평 3줄만 돌려준다.
---
````

- [ ] **Step 3: manifest-guide.md 쓰기**

`.agents/skills/bio-review-pack/references/manifest-guide.md`:
````markdown
# manifest.json 작성 규칙 (메인 에이전트)

manifest는 이번 팩의 계약이다. 작성자, 검사기, 조립기가 모두 이 파일을 기준으로 삼는다.
정본 예시: `tests/fixtures/mini-run/manifest.json`.
작성 후 반드시 `python3 <SKILL>/scripts/manifest.py <RUN>/manifest.json` → `OK`.

## 최상위
| 키 | 값 |
|---|---|
| `course` | `"생명과학"` (페이지 `<title>`에 쓰인다) |
| `range` | `"0922"` 또는 `"0922-0924"` (첫 STT–마지막 STT 날짜) |
| `slug` | 이번 범위 대표 장 제목의 영문 밑줄 형태, 예: `"Cell_Division"`, `"Mendelian_Genetics"`. 두 장에 걸치면 뒤쪽 장 |
| `note_title` | `"<주제> — 5살도 이해하는 정리노트"` |
| `note_subtitle` | `"이영만 교수님 생명과학 · 0922 수업 (3장 세포분열)"` 형식 |
| `review_title` | `"복습문제 N선 — <range 물결표기> 수업 범위"` |
| `review_intro` | 인라인 HTML만(`<b>`, `<i>`, `<code>`, `<a>`). 템플릿이 `<p>`로 감싸므로 블록 태그는 쓰지 않는다. 문제 구성(웹과제 몇 개, 기출 몇 개)과 "먼저 풀어 보고, 막히면 힌트를 열어 보세요"처럼 "~해요" 체 한 문장 안내(이모지 없이) |
| `footer_note` | HTML 허용. `출처: 이영만 교수님 강의노트(N장) · 수업 녹음 전사(MMDD…) · 『생명과학: 기초와 응용』 2판 N장.` |
| `footer_review` | HTML 허용. `출처: 2023·2024 생명과학 기출(N강 합본) · 웹과제(N장). 정답은 인쇄된 답안지와 독립 판단을 대조했고, 어긋난 곳은 풀이에 밝혔습니다.` (웹과제나 기출이 없으면 그 부분을 뺀다) |
| `sessions` | 날짜별 `{date, stt, summary, slides}`. `slides`는 `"3장 p12–20"` 형식 |

## sections / topics
- 섹션 id는 `s0`, `s1`, … 순서. 마지막 섹션은 항상 "요약 · 예고"이며 토픽 `s<N>-cheatsheet`, `s<N>-next`, `s<N>-links`를 둔다.
- 요약의 `## 0. 지난 수업 복습`이 "없음"이 아니면 `s0`의 첫 토픽을 `s0-recap`(`layers: ["formal"]`)으로 두고 이전 팩 링크를 `links`에 넣는다.
- 섹션은 **개념 순서(강의노트 쪽 순서)** 로 묶는다. 날짜는 토픽 태그로만 드러낸다.
- 두 장에 걸친 수업은 장 경계에서 섹션을 나누고 섹션 `title` 앞에 장을 적는다(예: `"3. [4장] 멘델의 유전 법칙"`).
- 토픽 id는 `s<n>-<kebab>`(영문 소문자). 토픽 하나 = 강의노트 1~3쪽 또는 칠판 설명 하나.
- `short`는 상단 목차 글자(예: `"2 세포주기"`), `title`은 `"2. 세포주기와 확인점"`.
- `layers`: 개념 토픽은 `["eli5", "formal", "prof"]`. 요약에 그 토픽의 `⚠️ 혼동 지점`이나 강조 발언이 있으면 `"warn"`을 더한다. 교수님 발언이 없으면 `prof`를 빼되 이유를 보고서 "스킬이 정한 사항"에 적는다. 요약·예고 섹션 토픽은 `[]`.
- `supp`: STT에 없지만 포함 문항을 풀려면 필요한 사실(강의노트·교재·외부 출처)을 싣는 토픽만 `true`. 요약의 `🕳️ 미룬 설명`을 보충으로 싣는 토픽도 `true`.
- `required_terms`: 토픽당 3~9개. 요약의 **용어 목록과 강조 발언**에서 고른다.
  - 작성자가 **글자 그대로** 쓸 문자열이다(예: `"자매염색분체(sister chromatid)"`, `"G1기"`).
  - 교수님 비유의 핵심 단어를 최소 하나 넣어 교수님 말씀(prof) 레이어 누락을 잡는다.
  - 포함 문항의 판별 용어(보기에서 정답과 오답을 가르는 말)를 anchor 토픽에 넣는다.
- `preview_topic`: `s<N>-next`.
- `forbidden_outside_preview`: 슬라이드 대조표에서 "예고만/안 다룸"인 쪽의 핵심 용어 3~8개. 본문에 나오면 검사 실패. 생명과학은 장 안의 용어가 서로 겹치므로, 이번 수업에서 **한 번도** 말하지 않은 용어만 고른다(예: 오늘 "감수분열"을 이름만 말했다면 금지어로 넣지 않는다).

## parts / problems
- `parts`: `partA`(`{"id": "partA", "title": "A. 웹과제", "short": "A 웹과제"}`), `partB`(`{"id": "partB", "title": "B. 기출", "short": "B 기출"}`). 포함 문항이 0개인 part는 뺀다.
- 문제 선별은 `references/problem-selection.md`. 범위 안의 문항은 **전부** 넣는다(개수 상한 없음).
- 문제 `id`: `p1`, `p2`, … 빈 번호 없이 순서대로(partA 먼저, 각 part 안에서는 원문 번호 순). 카드 파일명 `cards/<id>.html`이 된다. `part`: 위 `parts`의 id.
- `source`: 웹과제는 `"웹과제 <장>장 q<두 자리 번호>"`(예: `"웹과제 1장 q01"`), 기출은 `"기출 <장>강 <번호>"`(예: `"기출 3강 12"`). 정확히 이 형식.
- `variant`: 항상 `false`(문항을 바꾸지 않는다).
- `anchor`: 풀이가 기대는 정리노트 토픽 id. `level`: 1 개념 확인 / 2 판별·비교 / 3 그림 판독·복합. `date`: 관련 수업 날짜.
- `answer`: 판단한 정답의 보기 기호. 기출은 `"(3)"`, 웹과제는 `"C"`, 보기 없는 빈칸 문항은 정답 낱말.
- `terms`: 카드에 반드시 나올 문자열. 첫 항목은 `"정답: <answer>"`(예: `"정답: (3)"`), 다음은 정답 보기의 핵심 용어 1~2개. **모두 빈 문자열이 아닌 문자열**이다. `required_terms`, `forbidden_outside_preview`도 같다(`manifest.py`가 검사).

## links
- `href`는 작성자가 `<a href="…">`에 **글자 그대로** 넣을 값이다(검사기가 해당 `topic` 안의 링크와 정확히 비교한다).
- `{"topic": "s<N>-links", "href": "복습문제_<range>_<slug>.html"}`는 항상. 파일명은 `manifest.py`의 `review_name`이 만드는 것과 정확히 같아야 한다.
- 이전 복습팩과 이어지면 `../<이전 range>/정리노트_<이전 range>_<slug>.html#<토픽>`. 예전 형식 노트와 이어지면 `../../정리노트/MMDD.html`(퀴즈)·`../../정리노트/MMDD.md`(본문). 토픽은 기본 `s<N>-links`, `s0-recap`이 있으면 그 링크는 `s0-recap`에 건다.
````

- [ ] **Step 4: content-rules.md 쓰기**

`.agents/skills/bio-review-pack/references/content-rules.md`:
````markdown
# 섹션 작성 규칙

## 작성자 브리프 (메인 에이전트가 섹션마다 1명, 병렬, model: opus / lite: sonnet)

---
생명과학 정리노트의 섹션 `<sid>`(`<섹션 title>`)를 쓴다.

- 읽기: `<SKILL>/references/content-rules.md`(이 파일 전체), 위젯이 있으면 `<SKILL>/references/widget-rules.md`
- 위젯: <위젯> (메인 에이전트가 정한 것만 만든다. "위젯 없음"이면 이 섹션에는 위젯을 넣지 않는다)
- 계약: `<RUN>/manifest.json`의 섹션 `<sid>` — 토픽 id·제목·`required_terms`·`layers`·`supp`가 정확히 여기 적힌 대로여야 한다.
- 링크: manifest `links` 중 `topic`이 이 섹션에 있는 항목 `<이 섹션의 links 목록>`을 모두 그 토픽 안에 `<a href="…">`로 넣는다. `href`는 글자 그대로 복사(`%20` 포함). 복습문제 링크만은 `{{REVIEW_HREF}}`로 써도 된다.
- 받쳐야 할 문항: <이 섹션 토픽이 받쳐야 할 문항> — `<RUN>/question-audit.md`에서 anchor가 이 섹션 토픽인 포함 문항과 풀이에 필요한 개념이다. 복습문제를 보지 않고 이 섹션만 읽어도 그 문항을 풀 수 있게, 필요한 사실(보기를 가르는 기준 포함)을 본문이나 보충 레이어에 먼저 가르친다. 문항 번호와 정답은 쓰지 않는다.
- 근거: `<RUN>/summaries/stt-*.md`(해당 날짜), `<RUN>/slides.txt`, 교과서 `<RUN>/repo/교과서/생명과학_기초와_응용_2판/` <쪽> (스캔본이다. PyMuPDF로 필요한 쪽만 dpi 140 PNG를 `<RUN>/work/`에 렌더링해 눈으로 읽는다)
- 출력: `<RUN>/sections/<sid>.html` **한 파일만**. `<section>`/`<h2>`는 쓰지 않는다(조립기가 감싼다). 임시 파일은 아래 규칙.
- 임시·보조 파일은 `<RUN>/work/` 아래에만 둔다. 저장소(`STT/`, `강의노트/`, `교과서/`, `23, 24 소스/`, `웹과제/`, `복습노트/`)와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 복사하거나 이름을 바꾸지 말고 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 그 경로로 연다.
- 자기 검사(끝내기 전): 토픽별로 `required_terms`가 모두 글자 그대로 들어갔는지, `$` 짝, `links` 항목이 해당 토픽 안에 있는지, 금지어 `<forbidden 목록>`이 없는지. 금지어는 예고 토픽 `<preview_topic>` 안에서만 허용된다(이 토픽에는 예고 제목을 빠뜨리지 말고 쓴다). eli5 레이어마다 문장 수(figcaption 포함)가 3 이하이고 전문용어가 없는지. warn 레이어가 요약의 `⚠️ 혼동 지점`을 모두 담았는지. supp 레이어마다 `출처:` 줄이 있는지. 조각 어디에도 이모지와 원문자(①~⑳)가 없는지. `layers`가 빈 목록이 아닌 토픽마다 마지막에 `<div class="sum" hidden>`이 있는지. 그림 설명이 SVG 클래스의 실제 모양(채움/윤곽)과 맞는지.
- 보고: 파일 경로, 토픽별 한 줄, 요약에 있었지만 넣지 않은 것과 이유, 받쳐야 할 문항 중 가르치지 못한 사실.
---

## 범위
- 본문(eli5·formal·prof·warn)에는 이번 STT에서 **한 번이라도 언급된** 개념만 쓴다. 강의노트는 목차 뼈대일 뿐이고 STT가 주 자료다. 다음 수업 내용을 당겨오지 않는다.
- 슬라이드 대조표에서 "예고만/안 다룸"인 내용은 `s<N>-next`에 이름만 쓴다. 끊긴 지점은 여기에 교수님 마지막 발언 인용과 `(MMDD MM:SS)`로 적는다.
- STT에 없지만 포함 문항을 풀려면 필요한 사실은 supp 레이어에 쓰고 실제 출처를 밝힌다(`출처: 강의노트 3장 p14`, `출처: 교재 3장 p.68`, 외부 자료면 자료명). 수업에서 생략했다는 사실을 "시험에 안 나온다"로 바꾸지 않는다.
- 수업에서 말한 모든 개념, 교수님 비유와 강조 발언을 빠짐없이 싣는다. 잡담은 "이 비유를 지우면 개념 이해가 나빠지는가"로 판별해 버린다.
- STT 오인식과 말실수는 올바른 형태로 쓴다.
- 쉬운 설명에서도 성립 조건과 분류 경계를 지킨다. 어떤 경로·과정에 참여한다는 것을 그 계(系)의 구성원이라고 쓰지 않는다. 시험에서 판별에 쓰는 원래 용어는 쉬운 말과 함께 남긴다.

## 토픽 마크업 (이 순서)
```html
<article class="topic" id="…"><h3>…</h3><div class="tags"><span class="tag date">MMDD 수업</span><span class="tag slide">3장 p12</span></div>
  <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">한 문장 비유</p> …그림… </div>
  <div class="layer formal"><span class="layer-title">정확히 말하면</span> …정의·성립 조건·인과·과정(ol.steps)… </div>
  <div class="layer prof"><span class="layer-title">교수님 말씀</span> …비유·일화, 원문은 blockquote… </div>
  <div class="layer warn"><span class="layer-title">꼭 기억해요</span> …헷갈리는 짝과 바른 구분, 원문 인용 + (MMDD MM:SS)… </div>   ← layers에 warn이 있을 때만
  <div class="layer supp"><span class="badge supp">보충 · 수업에서 다루지 않았어요</span><p>…</p><p>출처: 교재 3장 p.68</p></div>   ← manifest supp=true만
  <div class="sum" hidden>…페이지 요약(아래)…</div>                                                    ← layers가 빈 목록이 아닌 토픽만, 맨 끝
</article>
```
- 레이어 제목과 배지 글자는 위와 글자 그대로 쓴다. 이모지, 장식 기호(★, ↗, → 같은 화살표 아이콘), "아래를 보세요" 같은 안내 문장은 쓰지 않는다.
- warn 레이어는 오개념 방어가 목적이다. 요약의 `⚠️ 혼동 지점`마다 "무엇을 무엇으로 착각하기 쉬운지"와 "바른 구분"을 한 쌍으로 쓴다.
- `s0-recap` 토픽(지난 수업 복습)은 formal 레이어에 요점 3~5줄과 이전 팩 링크만 둔다.
- 템플릿이 토픽 하나를 한 화면에 보여 준다. 토픽은 그것만 읽어도 이해되게 쓰고, 앞 토픽에 기대는 말 대신 `<a href="#토픽id">토픽 제목</a>`으로 잇는다.
- 요약·예고 섹션: 치트시트는 표(`<div class="table-wrap"><table>`)로, 행마다 "주제 | 시험 직전 한 줄"이며 성립 조건과 분류 경계를 한 줄 안에 보존한다. 예고는 `<ul>`, 링크는 `<ul><li><a>`.

## 페이지 요약 (`.sum`)
화면 오른쪽 "페이지 요약" 패널에 그 토픽의 핵심만 보여 준다. 템플릿이 토픽의 **직계 자식** `.sum`을 패널로 옮기므로 토픽 안 맨 끝에, 레이어 밖에 둔다. `hidden`은 꼭 붙인다.
```html
<div class="sum" hidden>
  <p class="sum-lead">토픽 핵심 한 문장("~해요" 체)</p>
  <p class="panel-label">핵심 식</p>
  <ul class="eq-list"><li><span class="eq-name">식 이름</span>$$…$$</li></ul>
  <p class="panel-label">용어</p>
  <dl class="terms"><dt>용어(영어)</dt><dd>한 줄 뜻</dd></dl>
</div>
```
- 새 내용을 쓰지 않는다. 본문에 이미 나온 식·용어를 같은 표기로 1~3개씩 고른다.
- 식이 없는 토픽(생명과학은 대부분)은 "핵심 식" 줄과 `eq-list`를 뺀다. 용어가 없으면 "용어" 줄과 `dl`을 뺀다. `sum-lead`는 항상 쓴다.
- `layers`가 `[]`인 토픽에는 두지 않는다.

## 문체
- 쉽게 말하면(eli5): 초등학생이 이해할 1~3문장(figcaption 포함) + 그림. 전문용어 없이. 토스처럼 짧고 다정한 "~해요" 체.
- 정확히 말하면(formal): 정의와 성립 조건, 인과, 과정(위치·입력·출력)을 빠짐없이 정확하게. "~해요" 체.
- 교수님 말씀(prof)/꼭 기억해요(warn): 원문 인용은 15단어 안팎으로 줄이고 `(0922 26:00)`처럼 출처.
- UI 글은 한국어, 전문용어는 영어 병기(예: 자매염색분체(sister chromatid)). 한 문장에 한 가지만 말하고 군더더기 수식어는 뺀다.

## 수식과 기호
- 반응식·화학식을 식으로 보여야 할 때만 `$…$`/`$$…$$`(예: `$$\mathrm{C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O}$$`). 문장 속 화학식은 H₂O처럼 유니코드 아래첨자를 써도 된다. 본문에 리터럴 `$` 금지.
- TeX 안에 `<`, `>`, `&` 금지 → `\lt`, `\gt`.
- 원문자(①~⑳)는 어디에도 쓰지 않는다. 목록 번호가 필요하면 `(1) (2) (3)`.

## SVG 그림
- 개념 토픽마다 eli5 레이어에 그림 1개 이상(구조도, 과정 흐름도, 단계 비교 등).
- `<figure class="figure"><svg id="fig-<kebab>" viewBox="…" role="img" aria-label="한국어 설명">…</svg><figcaption>…</figcaption></figure>`
- 색은 클래스로만: `fig-ink`, `fig-accent`, `fig-danger`, `fig-dot`, `fig-text`, `fig-muted`. 하드코딩 색 금지(다크모드).
- 채움과 윤곽: `fig-ink`, `fig-accent`, `fig-danger`는 선만 그린다(`fill:none`). 속이 칠해진 도형은 `fig-dot`뿐이다. 글·figcaption·`aria-label`에서 "색칠된", "채워진"은 `fig-dot` 도형에만 쓰고, 선만 있는 도형은 "테두리", "선"으로 부른다.
- 글자 12~14px, SVG `<text>`에 `$` 금지.
- id는 페이지 전체에서 유일해야 한다(`fig-` + 토픽 고유 단어).
- 문항이 교재·기출 그림을 판독하게 하면, 그 그림의 구조(표지 이름, 위치 관계)를 같은 이름으로 먼저 그려 가르친다.
````

- [ ] **Step 5: problem-selection.md 쓰기**

`.agents/skills/bio-review-pack/references/problem-selection.md`:
````markdown
# 문항 감사와 선별 (메인 에이전트)

## 원칙
- 문항은 **23·24 기출 합본**(`23, 24 소스/N강 합본.pdf`, 파일명에 `+`가 섞여 있다)과 **웹과제 bank**(`웹과제/N장/questions.json`)에서만 가져온다. 자작·변형 금지.
- 범위 안의 문항은 **전부** 넣는다. 개수 상한은 없다.
- 이번 수업이 다룬 장의 모든 문항을 하나도 빼지 않고 분류한다. 합계가 합본 전체 문항 수와 bank 전체 ID 수와 같아야 한다.

## 1. 자료 준비 (요약 에이전트가 도는 동안)
합본을 쪽마다 dpi 170 PNG로 렌더링한다. 텍스트 추출은 2단 조판이 섞이고 **빨간 글씨 정답 표시가 사라진다.** 반드시 이미지로 읽는다.
```bash
REPO=… RUN=… CH="3" python3 - <<'EOF'
import fitz, os, unicodedata as u
repo, run = os.environ["REPO"], os.environ["RUN"]
src = os.path.join(repo, "23, 24 소스")
os.makedirs(os.path.join(run, "work", "exam"), exist_ok=True)
for ch in os.environ["CH"].split():
    hit = [n for n in os.listdir(src) if u.normalize("NFC", n).startswith(f"{ch}강") and n.endswith(".pdf")]
    if not hit:
        print(f"{ch}강 합본 없음"); continue
    doc = fitz.open(os.path.join(src, hit[0]))
    for i, page in enumerate(doc, 1):
        path = os.path.join(run, "work", "exam", f"{ch}강-p{i}.png")
        page.get_pixmap(dpi=170).save(path); print(path)
EOF
```
`CH`는 공백으로 구분한 장 번호들이다.

## 2. 웹과제 bank
- 그 장 `웹과제/N장/questions.json`이 있으면 검증한다(저장소 루트에서):
  ```bash
  .venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/N장/questions.json' --complete
  ```
  전용 venv가 없으면 `python3 -m venv --system-site-packages .venv-question-bank && .venv-question-bank/bin/python -m pip install 'jsonschema>=4.18,<5'`로 만든다. 검증이 실패해도 멈추지 않는다. 실패한 필드와 source를 보고서 "미해결"에 적고 문항은 그대로 쓴다.
- `questions.json`은 없고 `웹과제/N장/raw/` 캡처만 있으면 **등록되지 않은 자료**다. 보고서에 그렇게 적는다("웹 자료 없음"이라고 쓰지 않는다). 이 경우 partA는 없다.
- 목록 보기:
  ```bash
  python3 - <<'EOF'
  import json
  b = json.load(open("<REPO>/웹과제/N장/questions.json", encoding="utf-8"))
  for q in b["questions"]:
      text = " ".join(c.get("text", f"[{c['type']}]") for c in q["original"]["content"])
      print(q["id"], q["number"], q["analysis"]["answer_option_id"], q["observations"].get("official_answer"), text[:60])
  EOF
  ```
- 카드에는 `original.content`(문제), `original.options`(보기, id가 `A`~`E`), `analysis.answer_option_id`(분석 정답), `analysis.option_diagnostics`(보기별 설명)를 쓴다. `observations.official_answer`가 있고 분석 정답과 다르면 `key-check.md`에 적고 카드에 공개한다.
- 문항 `content`에 그림 항목이 있으면 bank의 `assets` 경로에서 원본 파일을 찾아 `RUN/figures/p<N>.<확장자>`로 복사한다.

## 3. 문항 감사 → `RUN/question-audit.md`
장의 모든 문항을 한 줄씩 적는다.
```markdown
| 출처 | 번호 | 질문 요약 | 필요한 개념(토픽 id) | 상태 | 사유 |
|---|---|---|---|---|---|
| 기출 3강 | 12 | 동원체의 뜻 | s1-chromosome | 포함 | |
| 기출 3강 | 21 | 감수분열 교차 | — | 범위 밖 | 다음 수업 예고만(0922 49:10) |
| 웹과제 1장 | q03 | 공유결합 | s2-bond | 이전 팩 | 정리노트/0903.md 매핑표 포함 |
```
상태는 넷 중 하나다.
- **포함**: 풀이에 필요한 개념을 모두 이번 범위나 이전 수업에서 배웠고, 그중 하나 이상이 이번 범위에서 배운 것이며, 이전 팩에 아직 포함되지 않았다.
- **이전 팩**: 이미 이전 팩에 포함되었다. 확인 위치: 새 형식 `복습노트/*/복습문제_*.html`의 `data-source`, 예전 형식 `정리노트/MMDD.md`의 `## 부록. 문항 ↔ 개념 매핑` 표(상태 "포함")와 WEB 문항 매핑 표(상태 included/review).
- **보류**: 필요한 개념 중 아직 배우지 않은 것이 있다. 사유에 무엇을 언제 배우면 풀 수 있는지 적는다.
- **범위 밖**: 이번 장과 무관하거나 수업에서 다루지 않기로 한 내용이다. 근거(STT 타임스탬프나 강의계획서)를 적는다.

포함 문항마다 `problem-pages.txt`에 `p<N> 기출 3강 12 → work/exam/3강-p3.png`처럼 원문 위치를 적는다.

## 4. 정답 대조 → `RUN/key-check.md`
- 기출은 인쇄된 답(빨간 표시)을 PNG에서 읽고, 모든 보기를 독립적으로 판단해 대조한다. **답안지를 그대로 믿지 않는다.** 1강 합본은 40문항 중 3개(2, 30, 38번)가 틀려 있었다.
- 판단이 어긋나면 manifest `answer`는 **옳다고 판단한 쪽**으로 두고 `key-check.md`에 `기출 3강 12: 인쇄 (2) → 판단 (3), 근거: …`를 적는다. 카드 풀이에서 공개한다. 조용히 고치지 않는다.
- 보기가 없는 빈칸 문항은 보기를 만들지 않고 빈칸 그대로 카드에 싣는다. 정답은 낱말이다.
- 모든 포함 문항의 정답이 manifest `answer`와 카드 `정답:` 줄에 같게 들어간다.

## 5. 난이도 (`level`)
1 개념 확인(정의·이름) · 2 판별·비교(보기마다 경계 판단) · 3 그림 판독이나 여러 개념 결합.
````

- [ ] **Step 6: card-rules.md 쓰기**

`.agents/skills/bio-review-pack/references/card-rules.md`:
````markdown
# 문제 카드 규칙

## 작성자 브리프 (메인 에이전트가 카드 10개당 1명, 병렬, model: opus / lite: sonnet)

---
생명과학 복습문제 카드 `<담당 카드 id>`를 쓴다.

- 읽기: `<SKILL>/references/card-rules.md`(이 파일 전체), `<SKILL>/references/problem-selection.md`의 원칙과 4절
- 계약: `<RUN>/manifest.json`의 `problems` 중 담당 카드 — id, `source`, `anchor`, `level`, `date`, `terms`, `answer`를 그대로 따른다.
- 금지어: `<forbidden 목록>` — 카드 어디에도 쓰지 않는다. "다음 시간에 배울 …" 같은 예고도 쓰지 않는다.
- 근거: 원문 위치 `<RUN>/problem-pages.txt`(기출 PNG는 `<RUN>/work/exam/`), 웹과제 bank `<RUN>/repo/웹과제/<N>장/questions.json`, 정답 대조 `<RUN>/key-check.md`, 정리노트 토픽 제목은 manifest.
- 출력: `<RUN>/cards/<pid>.html` 문제마다 한 파일, 그림은 `<RUN>/figures/<pid>.png`. 다른 곳에 쓰지 않는다.
- 임시·보조 파일은 `<RUN>/work/` 아래에만 둔다. 저장소와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 연다.
- 자기 검사: 카드별 `terms`가 글자 그대로 있는지, `정답:` 줄이 `answer`와 같은지, 모든 보기에 진단이 있는지, 문제와 보기가 원문과 글자까지 같은지(줄바꿈 흔적만 고친다), 원문자(①~⑳)와 금지어가 하나도 없는지, `<img src>`가 `figures_<range>/<pid>.png`이고 그 파일을 `<RUN>/figures/`에 만들었는지. 어긋나면 고치지 말고 보고에 적는다.
- 보고: 카드별 한 줄(출처, 정답, 답안지 오류 여부), 풀이에 정리노트에 없는 사실이 필요했던 곳.
---

## 마크업
```html
<article class="card" id="pN" data-source="기출 3강 12">
  <h3>PN. 한 줄 제목</h3>
  <div class="problem"><p>…문제 원문…</p>
    <figure class="figure"><img src="figures_<range>/pN.png" alt="한국어 그림 설명"></figure>   ← 그림 문항만
    <ul class="choices"><li>(1) …</li><li>(2) …</li></ul></div>
  <details class="original"><summary>원문 정보 보기</summary>기출 3강 합본 12번 (PDF 3쪽)</details>
  <details class="hint"><summary>힌트 보기</summary>…한두 문장…</details>
  <details class="solution"><summary>풀이 보기</summary>
    <ol class="steps"><li>(1) 틀려요. …</li><li>(2) 맞아요. …</li></ol>
    <p class="answer">정답: (2)</p>
    <p>인쇄된 답안지에는 (3)으로 표시되어 있지만 오류로 판단해요. …</p>   ← key-check.md에 있을 때만
  </details>
</article>
```
- 구조와 순서는 위와 같다: `<h3>` → `div.problem` → `details.original` → `details.hint` → `details.solution`. 블라인드 사본 스크립트가 이 순서에 기댄다.
- `data-source`는 manifest `source`와 글자까지 같다.
- 보기 번호: 기출은 `(1)`~`(5)`(원문 ①~⑤을 옮긴 것), 웹과제는 bank 보기 id 그대로 `A.`~`E.`. 원문 순서를 바꾸지 않는다.
- 원문 정보 보기: 출처, 문항 번호, PDF 쪽만 쓴다(웹과제는 `웹과제 1장 q01 (스크린샷 s01)`). 인쇄된 답은 여기에 쓰지 않는다.
- 풀이: **모든 보기**에 "맞아요/틀려요 + 이유 한 문장"을 쓴다. 웹과제는 `option_diagnostics`를 "~해요" 체로 다듬는다. 보기 없는 빈칸 문항은 채우는 이유를 한두 단계로 쓴다.
- 풀이 마지막 단계에 "수업과의 연결"을 한 줄로 쓴다(어느 수업의 어떤 말과 이어지는지).
- 답안지 오류와 공식 답 불일치는 `정답:` 줄 다음 문단에서 반드시 공개한다.
- 난이도·날짜 배지, 이모지, 장식 기호, 원문자는 쓰지 않는다. 문제 원문을 뺀 문장은 "~해요" 체로 쓴다.
- 템플릿이 카드 하나를 한 화면에 보여 준다. 카드는 다른 카드 없이도 풀 수 있게 쓴다.

## 그림 자르기 (기출)
PNG(dpi 170)에서 그림 영역의 픽셀 좌표를 확인한 뒤 PDF 좌표(pt = px × 72 / 170)로 바꿔 원본 PDF에서 바로 잘라낸다.
```bash
REPO=… RUN=… python3 - <<'EOF'
import fitz, os, unicodedata as u
src = os.path.join(os.environ["REPO"], "23, 24 소스")
name = next(n for n in os.listdir(src) if u.normalize("NFC", n).startswith("3강") and n.endswith(".pdf"))
page = fitz.open(os.path.join(src, name))[2]                  # 0부터 센다: PDF 3쪽
rect = fitz.Rect(40, 300, 300, 520)                            # pt 단위. 쪽 전체 크기는 page.rect
page.get_pixmap(dpi=170, clip=rect).save(os.path.join(os.environ["RUN"], "figures", "p7.png"))
EOF
```
보기에 답이 인쇄된 빨간 표시가 그림 안에 들어가지 않게 자른다. 들어가면 영역을 줄인다.
````

- [ ] **Step 7: review-prompt.md 쓰기**

`.agents/skills/bio-review-pack/references/review-prompt.md`:
````markdown
# 리뷰어 지시문

6단계에서 두 리뷰어를 한 메시지에서 병렬로 띄운다. 블라인드 리뷰어는 `lite`에서도 띄우고, 일반 리뷰어는 `lite`면 생략한다.

## 블라인드 풀이 검사

먼저 메인 에이전트가 복습문제에서 문제·보기·그림만 뽑은 사본을 만든다(`REVIEW`는 조립된 복습문제 HTML 절대 경로).
```bash
REVIEW=… OUT="$RUN/work/blind-<range>.md" python3 - <<'EOF'
import html, os, re
src = open(os.environ["REVIEW"], encoding="utf-8").read()
base = os.path.dirname(os.environ["REVIEW"])
cards = re.findall(r'<article class="card" id="(p\d+)"[^>]*>\s*<h3>(.*?)</h3>\s*<div class="problem">(.*?)</div>\s*<details', src, re.S)
def text(h):
    h = re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', lambda m: f"\n[그림: {os.path.join(base, m.group(1))}]\n", h)
    h = re.sub(r"</(p|li|figure)>|<br\s*/?>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
with open(os.environ["OUT"], "w", encoding="utf-8") as f:
    for pid, title, body in cards:
        f.write(f"## {pid}. {html.unescape(re.sub(r'<[^>]+>', '', title))}\n\n{text(body)}\n\n")
print(len(cards), "문항")
EOF
```
출력 문항 수가 manifest 문제 수와 다르면 카드 마크업 순서를 고친 뒤 다시 만든다.

---
생명과학 복습팩의 블라인드 풀이 검사를 한다. 파일은 수정하지 않는다.

- 열 수 있는 파일은 **두 개뿐**이다: 정리노트 `<RUN>/repo/복습노트/<range>/<정리노트 html>`, 문항 사본 `<RUN>/work/blind-<range>.md`(그 안의 `[그림: …]` 경로 이미지도 볼 수 있다). 복습문제 HTML, manifest, 요약, 교과서, 인터넷, 다른 파일은 열지 않는다. 자기 배경지식으로 풀지 말고 정리노트에 쓰인 내용만 근거로 삼는다.
- 문항마다 답을 고르고, 근거가 된 정리노트 토픽 id와 문장을 적는다. 정리노트만으로 판단할 수 없는 보기가 있으면 "근거 없음"으로 적고 무엇이 빠졌는지 쓴다.

출력 형식(이것만):
```
| 문항 | 내 답 | 근거 토픽 | 빠진 사실 |
|---|---|---|---|
| p1 | (2) | s1-centromere | |
| p4 | 근거 없음 | — | 보기 (3)의 방추사 부착 위치가 노트에 없음 |
```
---

메인 에이전트는 리뷰어 답을 manifest `answer`와 비교한다. 다르거나 "근거 없음"인 문항은 `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다. 고친 뒤 사본을 다시 만들어 그 문항만 다시 검사한다.

## 일반 리뷰 (lite에서는 생략)

---
생명과학 복습팩 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/복습노트/<range>/<정리노트 html>`, `<…/복습문제 html>`
- 근거: `<RUN>/summaries/stt-*.md`, `<RUN>/slides.txt`, `<RUN>/manifest.json`, `<RUN>/question-audit.md`, `<RUN>/key-check.md`, `<RUN>/work/exam/*.png`, 웹과제 bank
- 규칙: `<SKILL>/references/content-rules.md`, `card-rules.md`, `problem-selection.md`

확인할 것:
1. **사실 오류**: 정의, 성립 조건, 과정의 위치·입력·출력, "항상/보통" 같은 한정어가 요약·강의노트·교재와 맞는가.
2. **누락**: 요약의 핵심 내용·강조 발언·`⚠️ 혼동 지점`·미룬 설명 중 노트에 없는 것.
3. **범위**: "예고만/안 다룸" 내용이 본문에 설명되어 있는가. 보충 레이어에 출처가 있는가.
4. **분류 경계**: 쉬운 설명이 조건을 지우거나, 과정 참여를 계의 구성원으로 쓰거나, 판별 용어를 없앴는가.
5. **ELI5 품질**: 쉽게 말하면 레이어가 전문용어 없이 1~3문장인가, 그림이 개념을 실제로 보여 주는가.
6. **문항**: 문제·보기가 원문(PNG, bank)과 글자까지 같은가, 모든 보기에 진단이 있는가, 정답이 `key-check.md`와 맞는가(직접 다시 판단), 답안지 오류를 공개했는가, `question-audit.md`의 합계가 합본·bank 전체와 맞는가.
7. **표현**: 표 첫 열이 한 글자씩 줄바꿈되거나 빈 칸이 있는 표, 잘린 문장, 원문자.

출력 형식(이것만):
```
## Critical
- [s2-checkpoint] 문제 → 고칠 내용
## Important
- [p3] …
## Minor
- …
```
각 항목은 토픽/카드 id로 시작한다. 없으면 "없음".
---
````

- [ ] **Step 8: ML 흔적 검사**

Run:
```bash
grep -n -E "MML|머신러닝|정방철|머러기|Mathematics_for|answers\.py|Lecture" .agents/skills/bio-review-pack/references/*.md
```
Expected: 출력 없음(종료 코드 1).

Run: `ls .agents/skills/bio-review-pack/references | wc -l`
Expected: `8`

- [ ] **Step 9: 커밋**

```bash
git add .agents/skills/bio-review-pack/references
git commit -m "docs(bio-review-pack): add biology briefs and rules

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 정본 SKILL.md, 스킬 파일 테스트, .claude 진입점

**Files:**
- Create: `.agents/skills/bio-review-pack/SKILL.md`
- Create: `.agents/skills/bio-review-pack/tests/test_skill_files.py`
- Create: `.claude/skills/bio-review-pack/SKILL.md`
- Create: `tests/test_bio_review_pack_entrypoint.py`

**Interfaces:**
- Consumes: Task 4 references 8개, scripts 4개.
- Produces: SKILL.md의 `### 0.`~`### 9.` 절, 0단계 기간 판정 스니펫(첫 줄 `REPO=… python3 - <<'EOF'`), 4단계 백업 스니펫(첫 줄 `RANGE=<range> REPO=… RUN=… python3 - <<'EOF'`). 진입점이 가리키는 상대 경로 `../../../.agents/skills/bio-review-pack/SKILL.md`.

- [ ] **Step 1: 실패하는 스킬 파일 테스트 쓰기**

`.agents/skills/bio-review-pack/tests/test_skill_files.py`:
````python
"""SKILL.md 형식과, 본문이 가리키는 파일이 모두 있는지, 스니펫이 실제로 도는지 확인한다."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _util import SKILL

SKILL_MD = SKILL / "SKILL.md"


def snippet(first_line: str) -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(r"```bash\n" + re.escape(first_line) + r"\n(.*?)\nEOF\n```", text, re.S)
    assert m, f"SKILL.md 스니펫을 찾지 못함: {first_line}"
    return m.group(1)


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "bio-review-pack")
        self.assertIn("정리노트", m.group(2))
        self.assertIn("복습문제", m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 12)
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

    def test_no_ml_leftovers(self):
        pattern = re.compile(r"MML|머신러닝|정방철|머러기|Mathematics_for|answers\.py")
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            with self.subTest(file=path.name):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))

    def test_no_circled_numbers_in_rules(self):
        # 원문자는 "쓰지 않는다"를 설명하는 ①~⑳ 범위 표기에서만 허용한다.
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8").replace("①~⑳", "").replace("①~⑤", "")
            with self.subTest(file=path.name):
                self.assertIsNone(re.search(r"[①-⑳]", text))


class TestRangeSnippet(unittest.TestCase):
    """SKILL.md 0단계 기간 판정 스니펫을 임시 저장소에서 실제로 실행한다."""

    @classmethod
    def setUpClass(cls):
        cls.code = snippet("REPO=… python3 - <<'EOF'")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "STT").mkdir()
        for name in ("0903_생명.md", "0917 생명.md", unicodedata.normalize("NFD", "0922 생명.md"), "0924 생명.md", "메모.md"):
            (self.repo / "STT" / name).write_text("x", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_snippet(self):
        env = dict(os.environ, REPO=str(self.repo))
        r = subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_nothing_done_yet(self):
        self.assertIn("다음: 0903 0917 0922 0924", self.run_snippet())

    def test_legacy_note_counts_as_done(self):
        (self.repo / "정리노트").mkdir()
        (self.repo / "정리노트" / "0917.md").write_text("x", encoding="utf-8")
        (self.repo / "정리노트" / "0903.md").write_text("x", encoding="utf-8")
        self.assertIn("다음: 0922 0924", self.run_snippet())

    def test_new_pack_range_end_counts_as_done(self):
        (self.repo / "정리노트").mkdir()
        (self.repo / "정리노트" / "0917.md").write_text("x", encoding="utf-8")
        pack = self.repo / "복습노트" / unicodedata.normalize("NFD", "0922-0924")
        pack.mkdir(parents=True)
        (pack / unicodedata.normalize("NFD", "정리노트_0922-0924_Cell_Division.html")).write_text("x", encoding="utf-8")
        out = self.run_snippet()
        self.assertIn("마지막 정리: 0924", out)
        self.assertRegex(out, r"다음:\s*$")


class TestBackupSnippet(unittest.TestCase):
    """SKILL.md 4단계 백업 스니펫(python 부분)을 임시 폴더에서 실제로 실행한다."""

    @classmethod
    def setUpClass(cls):
        cls.code = snippet("RANGE=<range> REPO=… RUN=… python3 - <<'EOF'")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.notes = self.tmp / "repo" / "복습노트"
        self.notes.mkdir(parents=True)
        self.run_dir = self.tmp / "run"
        self.run_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def backup(self, range_):
        env = dict(os.environ, RANGE=range_, REPO=str(self.tmp / "repo"), RUN=str(self.run_dir))
        return subprocess.run([sys.executable, "-"], input=self.code, env=env, capture_output=True, text=True)

    def backups(self):
        return sorted(p for p in self.run_dir.iterdir() if p.name.startswith("previous-"))

    def test_nothing_to_back_up(self):
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업할 기존 팩 없음", r.stdout)
        self.assertEqual(self.backups(), [])

    def test_backs_up_dated_folder_layout(self):
        pack = self.notes / "0922"
        (pack / "figures_0922").mkdir(parents=True)
        (pack / "figures_0922" / "p2.png").write_bytes(b"x")
        (pack / "정리노트_0922_A.html").write_text("n", encoding="utf-8")
        (pack / unicodedata.normalize("NFD", "복습문제_0922_A.md")).write_text("r", encoding="utf-8")
        (self.notes / "0924").mkdir()
        (self.notes / "0924" / "정리노트_0924_B.html").write_text("other", encoding="utf-8")
        r = self.backup("0922")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 3항목(파일 3개)", r.stdout)
        (d,) = self.backups()
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
        self.assertEqual(names, ["figures_0922", "복습문제_0922_A.md", "정리노트_0922_A.html"])

    def test_bad_range_fails_loudly(self):
        (self.notes / "정리노트_0922_A.html").write_text("n", encoding="utf-8")
        for bad in ("", "<range>", "922"):
            with self.subTest(bad=bad):
                r = self.backup(bad)
                self.assertEqual(r.returncode, 1)
                self.assertIn("백업 중단", r.stderr)
        self.assertEqual(self.backups(), [])


if __name__ == "__main__":
    unittest.main()
````

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_skill_files.py`
Expected: ERROR — `SKILL.md` 없음(FileNotFoundError).

- [ ] **Step 3: 정본 SKILL.md 쓰기**

`.agents/skills/bio-review-pack/SKILL.md`:
````markdown
---
name: bio-review-pack
description: 생명과학 수업의 STT·강의노트·교과서와 23·24 기출·웹과제로 ELI5 정리노트 HTML과 객관식 복습문제 HTML(+MD, 그림)을 만들어 복습노트/<날짜>/ 폴더에 저장한다. "정리노트", "복습문제", "복습팩", "0922 강의 듣고 왔어", "0922~0924 정리해줘"처럼 생명과학 수업 정리를 요청하거나 /bio-review-pack [MMDD|MMDD-MMDD] [lite]로 부를 때 사용한다.
---

# 생명과학 복습팩

수업 녹음 전사(STT)와 강의노트, 교과서, 기출·웹과제로 한 기간의 복습팩을 만든다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**산출물** (`복습노트/<range>/`, 수업 날짜마다 폴더 하나):
`정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, 같은 이름의 `.md` 두 개, `figures_<range>/`

**인자**: `[MMDD | MMDD-MMDD] [lite]`
- `lite`: 작성자·요약 에이전트를 sonnet으로 하고, 6단계의 일반 리뷰를 생략한다. 블라인드 풀이 검사, 기계 검사, 브라우저 검사는 그대로 한다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 5개 + 카드 23개 (병렬)`

**서브에이전트가 없는 환경(Codex 등)**: 병렬 에이전트 대신 같은 브리프로 요약·섹션·카드를 차례로 직접 쓴다. 6단계 블라인드 검사는 새 세션에서 블라인드 사본과 정리노트만 열어 수행한다. 모델 지정(opus/sonnet)은 Claude에서만 따른다.

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/bio-review-pack`)의 절대 경로. `.claude/skills/bio-review-pack/SKILL.md`는 이 파일을 가리키는 진입점일 뿐이다.
- `REPO` = 저장소 루트
- `RUN` = `<scratchpad>/review-pack/<range>/` (scratchpad가 없으면 `/tmp/bio-review-pack/<range>/`)
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 명령의 `$SKILL`, `$RUN`, `$REPO`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 명령 앞에 `SKILL=… RUN=… REPO=…`를 붙여 설정한다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.
- 장 번호 `N`은 `강의노트/N장 *.pdf`, `23, 24 소스/N강 합본.pdf`(파일명에 `+`가 섞여 있다), `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`(두 자리), `웹과제/N장/`에서 같은 수를 쓴다.

## 절차

### 0. 준비
1. `REPO`에 `STT/`, `강의노트/`, `23, 24 소스/`, `교과서/생명과학_기초와_응용_2판/`이 모두 있는지 확인한다. 하나라도 없으면 "생명과학 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. STT 날짜와 마지막으로 정리한 날짜를 NFC로 읽는다. 예전 형식 `정리노트/MMDD.md`와 새 형식 `복습노트/*/정리노트_<range>_*.html`(끝 날짜)를 모두 본다.
```bash
REPO=… python3 - <<'EOF'
import os, re, unicodedata as u
repo = os.environ["REPO"]
def ls(*parts):
    d = os.path.join(repo, *parts)
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
stt = sorted(m.group(1) for n in ls("STT") if (m := re.fullmatch(r"(\d{4})[ _]생명\.md", n)))
done = [m.group(1) for n in ls("정리노트") if (m := re.fullmatch(r"(\d{4})\.md", n))]
for folder in ls("복습노트").values():
    if os.path.isdir(folder):
        for n in os.listdir(folder):
            if (m := re.match(r"정리노트_(?:\d{4}-)?(\d{4})_", u.normalize("NFC", n))):
                done.append(m.group(1))
last = max(done, default="0000")
print("STT:", *stt)
print("마지막 정리:", last)
print("다음:", *[d for d in stt if d > last])
EOF
```
3. 기간을 정한다.
   - 인자가 있으면 그 기간을 쓴다.
   - 인자가 없으면 위 출력의 `다음:` 날짜를 모두 쓴다.
   - 해당 STT가 하나도 없으면 사용 가능한 날짜(`STT:`)를 보여 주고 멈춘다.
   - `range`는 첫 STT 날짜 하나이거나 `첫-끝` 형식이다.
4. 실행 폴더를 만든다. 서브에이전트에게는 `RUN`, `RUN/repo`, `SKILL` 경로만 넘긴다.
   ```bash
   mkdir -p "$RUN"/{summaries,sections,cards,figures,work} && ln -sfn "$REPO" "$RUN/repo"
   ```
   에이전트는 `RUN` 밖에 쓰지 않는다. 임시·보조 파일은 `RUN/work/`에만 둔다. 저장소(`STT/`, `강의노트/`, `교과서/`, `23, 24 소스/`, `웹과제/`)에는 아무도 쓰지 않고, `복습노트/`에는 메인 에이전트만 쓴다.

### 1. 범위 파악
1. 이번 STT가 다룰 장을 정한다. 직전 노트(가장 최근 `복습노트/*/정리노트_*.md` 또는 `정리노트/MMDD.md`)의 마지막 장과 끊긴 지점, STT 앞부분을 본다. 확실하지 않으면 다음 장까지 넣는다. **먼저** 그 장들의 강의노트 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다. 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
   ```bash
   REPO=… RUN=… CH="3" python3 - <<'EOF'
   import fitz, os, unicodedata as u
   repo, run = os.environ["REPO"], os.environ["RUN"]
   d = os.path.join(repo, "강의노트")
   out = []
   for n in sorted(os.listdir(d)):
       name = u.normalize("NFC", n)
       ch = name.split("장", 1)[0]
       if name.endswith(".pdf") and ch in os.environ["CH"].split():
           for i, page in enumerate(fitz.open(os.path.join(d, n)), 1):
               out.append(f"=== {ch}장 p{i} ===\n{page.get_text()}")
   open(os.path.join(run, "slides.txt"), "w", encoding="utf-8").write("\n".join(out))
   print(len(out), "쪽")
   EOF
   ```
   추출에 실패하면 STT만으로 진행하고 보고서에 적는다(브리프의 `slides.txt` 줄은 "없음"으로 바꿔 넘긴다).
2. 그다음 STT 날짜마다 요약 에이전트 1명을 **병렬로** 띄운다. 브리프는 `references/stt-summary-prompt.md`에 있다.
   - `<N장 *.pdf>`: 그 날짜가 다룬 강의노트 파일 이름. 확실하지 않으면 1의 장을 모두 적는다.
   - `<MMDD 생명.md>`: 0단계에서 찾은 실제 STT 파일 이름(`0903_생명.md`처럼 밑줄인 것도 있다).
   - `<YYYY-MM-DD>`: 연도는 이번 학기 연도(오늘 날짜 기준), 월·일은 `<MMDD>`.
3. 에이전트가 도는 동안 메인 에이전트는 `references/problem-selection.md`의 1절(기출 합본 렌더링)과 2절(웹과제 bank 확인·검증)을 한다.

### 2. manifest
- 요약들의 슬라이드 대조표, 용어 목록, 혼동 지점으로 `RUN/manifest.json`을 쓴다. 규칙은 `references/manifest-guide.md`에 있다.
- 문항 감사와 선별은 `references/problem-selection.md`를 따른다.
  - 장의 모든 문항 분류는 `RUN/question-audit.md`, 정답 대조는 `RUN/key-check.md`, 문항별 원문 위치는 `RUN/problem-pages.txt`에 적는다.
  - 포함 문항은 **전부** manifest `problems`에 넣는다.
- 검증: `python3 "$SKILL/scripts/manifest.py" "$RUN/manifest.json"` 결과가 `OK`여야 한다.

### 3. 작성
- 섹션마다 작성자 1명을 띄운다. 브리프는 `references/content-rules.md`, 위젯 규칙은 `references/widget-rules.md`에 있다.
- 카드 작성자는 카드 10개당 1명이다(`p1`–`p10`, `p11`–`p20`, …). 브리프는 `references/card-rules.md`에 있다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 opus, `lite`이면 sonnet이다.
- 브리프의 `<…>` 자리는 실제 값으로 채운다: 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 섹션 작성자에게 필요한 교과서 쪽(`<쪽>`), manifest `links` 중 그 섹션 토픽에 속한 것(`<이 섹션의 links 목록>`), `question-audit.md`에서 anchor가 그 섹션 토픽인 포함 문항과 필요한 개념(`<이 섹션 토픽이 받쳐야 할 문항>`), 카드 작성자가 맡은 id(`<담당 카드 id>`).
- 위젯은 팩 전체에 0~2개다. 병렬 작성자끼리는 서로를 모르므로 **메인 에이전트가 띄우기 전에** 위젯을 둘 토픽(0~2개)을 정하고, 그 토픽의 섹션 작성자 브리프에만 `<위젯>` 자리에 "토픽 `<토픽 id>`에 위젯 1개: <무엇을 움직이면 무엇이 보이는지>"를 적는다. 나머지 작성자의 `<위젯>` 자리에는 "위젯 없음"이라고 적는다. 정한 토픽과 이유는 보고서 "스킬이 정한 사항"에 적는다.

### 4. 조립
- **처음 조립할 때만**: `복습노트/<range>/`(또는 `복습노트/` 바로 아래)에 이번 `range`의 산출물(`정리노트_<range>_*`, `복습문제_<range>_*`의 `.html`·`.md`, `figures_<range>/`)이 하나라도 있으면 먼저 백업한다. 다시 조립할 때(5~8단계에서 돌아온 경우)는 백업하지 않는다. 이미 스킬이 만든 초안이 백업에 섞이기 때문이다.
  - `RANGE`, `REPO`, `RUN`을 모두 실제 값으로 바꿔 한 명령으로 실행한다. 파일명은 NFC로 비교하므로 NFD 파일명도 잡힌다.
  - 백업은 매번 새 폴더 `RUN/previous-<시각>-<임의>/`에 만든다(이전 백업을 덮어쓰지 않음). `RANGE`가 형식에 안 맞거나, 대상이 있는데 복사된 파일 수가 다르면 종료 코드 1로 멈춘다. 이때는 조립하지 말고 원인을 고친다.
```bash
RANGE=<range> REPO=… RUN=… python3 - <<'EOF'
import os, re, shutil, sys, tempfile, time, unicodedata as u
r, run = os.environ["RANGE"], os.environ["RUN"]
notes = os.path.join(os.environ["REPO"], "복습노트")
if not re.fullmatch(r"\d{4}(-\d{4})?", r) or not os.path.isdir(run):
    sys.exit(f"백업 중단: RANGE={r!r} 또는 RUN={run!r} 잘못됨")
def want(n):
    n = u.normalize("NFC", n)
    return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_")) or n == f"figures_{r}"
def listdir_nfc(d):  # NFD 폴더명도 찾는다
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
srcs = [listdir_nfc(notes).get(r), notes]  # 날짜 폴더, 예전 형식(바로 아래)
hits = sorted({n: p for d in srcs if d and os.path.isdir(d) for n, p in listdir_nfc(d).items() if want(n)}.items())
if not hits:
    print("백업할 기존 팩 없음"); sys.exit(0)
def count(p):
    return sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 1
dst = tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run)  # 항상 새 폴더
for n, a in hits:
    b = os.path.join(dst, n)
    shutil.copytree(a, b) if os.path.isdir(a) else shutil.copy2(a, b)
want_n, got_n = sum(count(a) for _, a in hits), count(dst)
if got_n != want_n:
    sys.exit(f"백업 실패: 파일 {want_n}개 중 {got_n}개만 복사됨 → {dst}")
print(f"백업 {len(hits)}항목(파일 {got_n}개): {dst}", *(a for _, a in hits), sep="\n")
EOF
```
```bash
python3 "$SKILL/scripts/assemble.py" --run "$RUN" --out "$REPO/복습노트/<range>"
```
조립기는 `RUN/figures/`의 카드 그림을 `복습노트/<range>/figures_<range>/`로 복사한다.

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$REPO/복습노트/<range>/<정리노트>.html" --review "$REPO/복습노트/<range>/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다. `broken-image`는 그 카드 작성자다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰
- 브리프는 `references/review-prompt.md`에 있다. 두 리뷰어를 한 메시지에서 병렬로 띄운다.
  - **블라인드 풀이 검사**(항상, `lite` 포함): 문서의 스니펫으로 `RUN/work/blind-<range>.md`를 만든 뒤 리뷰어 1명에게 정리노트와 이 사본만 준다.
  - **일반 리뷰**(`lite`면 생략): 리뷰어 1명.
- 블라인드 리뷰어의 답이 manifest `answer`와 다르거나 "근거 없음"이면, `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다.
- 일반 리뷰의 Critical과 Important는 모두, Minor는 쉬운 것만 고친다.
- 담당 작성자별로 **한 번에 모아서** 수정을 요청한다. 수정은 한 번만 한다.
- 수정 후 4~5단계를 다시 하고, 블라인드 사본을 다시 만들어 틀렸던 문항만 다시 검사한다. 반영하지 않은 항목은 보고서에 적는다.

### 7. 브라우저 검증
- `references/browser-check.md`대로 한다.
  - http.server를 빈 포트에 띄운다.
  - 확인: KaTeX 오류 0, 남은 `$` 없음, 카드 그림 로드, 375px에서 가로 스크롤 없음, 다크모드, 위젯, 링크, 콘솔 오류
- 결함은 5단계와 같은 방식으로 작성자에게 되돌린다. 이것도 최대 2회 규칙에 포함된다.
- 끝나면 서버를 종료한다.

### 8. MD 변환
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --check
```
- `OK`가 나와야 한다.
- 누락이 나오면 대부분 HTML 조각의 마크업 문제다(수식이 `svg`나 `.controls` 안에 있는 경우 등). 조각을 고치고 4단계부터 다시 한다.

### 9. 보고
다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료
- 파일: 복습노트/<range>/… (html 2, md 2, figures_<range>/ N개)
- 범위: 배운 쪽 … / 예고만: … / 끊긴 지점: "…" (MMDD MM:SS)
- 문항: 포함 N (웹과제 a, 기출 b) · 이전 팩 N · 보류 N · 범위 밖 N — 분류표 RUN/question-audit.md
- 답안지 오류: 기출 3강 12 (인쇄 (2) → 판단 (3)) … (없으면 "없음")
- 블라인드 검사: N/N 풀림 (고친 토픽: …)
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add review pack <range>"
```
실행 폴더 경로(`RUN`)도 적는다. 수정이 필요하면 조각을 고쳐 4단계부터 다시 돌리면 된다. 커밋 제안 전에 `git status`로 `*.zip`이 섞이지 않았는지 확인한다.

## 오류 처리
| 상황 | 동작 |
|---|---|
| 저장소가 아님 | 알리고 멈춤 |
| 기간에 해당하는 STT 없음 | 사용 가능한 날짜를 보여 주고 멈춤 |
| 강의노트 텍스트 추출 실패 | STT만으로 진행하고 보고서에 표시 |
| 그 장의 기출 합본 없음 | partB를 빼고 진행, 보고서에 표시 |
| 웹과제 `questions.json` 없이 `raw/` 캡처만 있음 | "등록되지 않은 웹과제 자료"로 보고하고 partA를 뺀다("웹 자료 없음"이라고 쓰지 않는다) |
| 웹과제 bank 검증 실패 | 멈추지 않고 문항은 쓰되, 실패한 필드와 source를 "미해결"에 적음 |
| 포트 사용 중 | 다른 빈 포트 사용 |
| 같은 range의 팩이 이미 있음 | 4단계 첫 조립 전에 기존 html·md·`figures_<range>/`를 새 폴더 `RUN/previous-<시각>-<임의>/`에 복사하고(다시 조립할 때는 복사하지 않음) 백업 경로를 보고서에 적음. 백업 명령이 실패하면 조립하지 않고 원인을 고친다 |
| 검사 2회 실패 | 멈추지 않고 나머지 단계를 끝낸 뒤 "미해결"로 보고 |
````

- [ ] **Step 4: 스킬 테스트 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK`

- [ ] **Step 5: 실패하는 진입점 테스트 쓰기**

`tests/test_bio_review_pack_entrypoint.py`:
```python
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / ".agents/skills/bio-review-pack/SKILL.md"
ENTRY = ROOT / ".claude/skills/bio-review-pack/SKILL.md"
TARGET = "../../../.agents/skills/bio-review-pack/SKILL.md"


def frontmatter(text):
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
    return m.groups() if m else None


class BioReviewPackEntrypointTests(unittest.TestCase):
    def test_entry_has_same_frontmatter_as_canonical(self):
        entry = frontmatter(ENTRY.read_text(encoding="utf-8"))
        self.assertIsNotNone(entry)
        self.assertEqual(entry, frontmatter(CANON.read_text(encoding="utf-8")))

    def test_entry_points_to_canonical(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertIn(TARGET, text)
        self.assertEqual((ENTRY.parent / TARGET).resolve(), CANON.resolve())

    def test_entry_does_not_duplicate_procedure(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 20)
        self.assertNotRegex(text, r"\n### \d\. ")


if __name__ == "__main__":
    unittest.main()
```

Run: `python3 -m unittest tests.test_bio_review_pack_entrypoint -v`
Expected: ERROR — `.claude/skills/bio-review-pack/SKILL.md` 없음.

- [ ] **Step 6: 진입점 쓰기**

Step 3의 정본 frontmatter 두 줄(`name`, `description`)을 글자 그대로 복사해 `.claude/skills/bio-review-pack/SKILL.md`를 만든다:
```markdown
---
name: bio-review-pack
description: 생명과학 수업의 STT·강의노트·교과서와 23·24 기출·웹과제로 ELI5 정리노트 HTML과 객관식 복습문제 HTML(+MD, 그림)을 만들어 복습노트/<날짜>/ 폴더에 저장한다. "정리노트", "복습문제", "복습팩", "0922 강의 듣고 왔어", "0922~0924 정리해줘"처럼 생명과학 수업 정리를 요청하거나 /bio-review-pack [MMDD|MMDD-MMDD] [lite]로 부를 때 사용한다.
---

# 생명과학 복습팩

Read and follow [the canonical skill](../../../.agents/skills/bio-review-pack/SKILL.md) completely before acting.
`SKILL` in that file means the canonical directory `.agents/skills/bio-review-pack`; resolve every script, asset, and reference path from there.
Do not maintain a second procedure here.
```

- [ ] **Step 7: 통과 확인**

Run: `python3 -m unittest tests.test_bio_review_pack_entrypoint -v && python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: 둘 다 `OK`

- [ ] **Step 8: 커밋**

```bash
git add .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/tests/test_skill_files.py .claude/skills/bio-review-pack/SKILL.md tests/test_bio_review_pack_entrypoint.py
git commit -m "feat(bio-review-pack): add canonical skill procedure and claude entrypoint

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: 옛 스킬과 전용 테스트 제거, 규칙 문서 포인터 갱신

**Files:**
- Delete: `.agents/skills/study-note-eli5/`, `.agents/skills/summary-note/`, `.claude/skills/study-note-eli5/`, `.claude/skills/summary-note/`
- Delete: `tests/test_claude_study_note_eli5.py`, `tests/test_summary_note_entrypoint.py`, `tests/test_study_guide_blind.py`, `tests/test_study_guide_build.py`, `tests/test_study_guide_cli.py`, `tests/test_study_guide_external.py`, `tests/test_study_guide_html.py`, `tests/test_study_guide_model.py`, `tests/test_study_guide_scope.py`, `tests/test_study_guide_template.py`, `tests/study_guide_fixture.py`, `tests/test_eli5_0917_source.py`, `tests/test_question_bank_guide.py`, `tests/fixtures/study_guide/`
- Delete: `scripts/question_bank/guide.py` (ELI5 어댑터, 유일한 사용처가 삭제되는 `build_guide.py`)
- Modify: `tests/test_question_bank_scope.py:18-22`, `:127-152`, `:168-200`
- Modify: `정리노트/CLAUDE.md` (맨 위 안내, ELI5 절 72-73행, §12 156행)
- Modify: `tests/test_bio_review_pack_entrypoint.py` (규칙 문서 포인터 테스트 추가)

**Interfaces:**
- Consumes: Task 5 진입점 테스트 파일.
- Produces: 저장소 테스트 전체가 옛 스킬 없이 통과.

- [ ] **Step 1: 실패하는 테스트 쓰기**

`tests/test_bio_review_pack_entrypoint.py`의 클래스 끝(`test_entry_does_not_duplicate_procedure` 다음)에 추가:
```python
    def test_rules_point_to_new_skill_only(self):
        rules = (ROOT / "정리노트/CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/bio-review-pack/SKILL.md", rules)
        self.assertNotIn(".agents/skills/summary-note/SKILL.md", rules)
        self.assertNotIn(".agents/skills/study-note-eli5/SKILL.md", rules)

    def test_old_skills_removed(self):
        for name in ("summary-note", "study-note-eli5"):
            for base in (".agents/skills", ".claude/skills"):
                with self.subTest(path=f"{base}/{name}"):
                    self.assertFalse((ROOT / base / name).exists())
```

Run: `python3 -m unittest tests.test_bio_review_pack_entrypoint -v`
Expected: FAIL 2개(`test_rules_point_to_new_skill_only`, `test_old_skills_removed`).

- [ ] **Step 2: 옛 스킬·테스트·어댑터 삭제**

```bash
git rm -r -q .agents/skills/study-note-eli5 .agents/skills/summary-note .claude/skills/study-note-eli5 .claude/skills/summary-note
git rm -q tests/test_claude_study_note_eli5.py tests/test_summary_note_entrypoint.py \
  tests/test_study_guide_blind.py tests/test_study_guide_build.py tests/test_study_guide_cli.py \
  tests/test_study_guide_external.py tests/test_study_guide_html.py tests/test_study_guide_model.py \
  tests/test_study_guide_scope.py tests/test_study_guide_template.py tests/study_guide_fixture.py \
  tests/test_eli5_0917_source.py tests/test_question_bank_guide.py scripts/question_bank/guide.py
git rm -r -q tests/fixtures/study_guide
grep -rn -E "study-note-eli5|summary-note|study_guide_fixture|question_bank\.guide|bank_to_guide" scripts tests .agents/skills .claude || echo CLEAN
```
Expected: `CLEAN`이 아니면 `tests/test_question_bank_scope.py`만 나와야 한다(다음 단계에서 고친다). 다른 파일이 나오면 멈추고 그 참조를 보고한다.

- [ ] **Step 3: test_question_bank_scope.py에서 ELI5 스크립트 의존 제거**

18~22행:
```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / '.agents/skills/study-note-eli5/scripts'
sys.path.insert(0, str(SCRIPTS))
from build_question_scope import build_lock
from question_scope import validate_scope_lock, scope_digest
```
를 다음 한 줄로 바꾼다:
```python
ROOT = Path(__file__).resolve().parents[1]
```

`test_v2_rebases_sources_and_detects_forged_universe_and_source_changes` 메서드 전체(`def test_v2_rebases...`부터 `self.assertTrue(validate_scope_lock(json.loads(out.read_text()), note, lock_path=out))`까지)를 지운다. 바로 아래 `rebase_fixture` staticmethod는 남긴다.

`test_absolute_script_from_temp_cwd_and_legacy_without_jsonschema` 메서드 전체를 다음으로 바꾼다:
```python
    def test_new_note_test_from_temp_cwd_accepts_absolute_web_scope(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.superpowers') as tmp, tempfile.TemporaryDirectory() as cwd:
            root = Path(tmp)
            _, _, scope, _ = fixture(root)
            self.rebase_fixture(root, scope)
            generated = root / 'test_note_0999.py'
            p = subprocess.run([sys.executable, str(ROOT / 'scripts/new_note_test.py'), '0999',
                                '--web-scope', str(scope), '--out', str(generated)],
                               cwd=cwd, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn('WEB_SCOPE =', generated.read_text())
```

Run: `.venv-question-bank/bin/python -m unittest tests.test_question_bank_scope -v`
Expected: `OK`

- [ ] **Step 4: 정리노트/CLAUDE.md 포인터 갱신**

1행 `# 정리노트 작성 규칙` 바로 아래(빈 줄 다음)에 문단 추가:
```markdown
> 새 회차 복습팩은 `/bio-review-pack` 스킬(정본 `.agents/skills/bio-review-pack/SKILL.md`)이 `복습노트/<range>/`에 만든다. 이 문서는 기존 `정리노트/MMDD.md`·`MMDD.html`·`eli5/` 산출물을 고칠 때의 규칙으로 남긴다.
```

ELI5 절의 두 줄
```
생성 절차는 .agents/skills/study-note-eli5/SKILL.md, coverage 데이터 계약은
해당 스킬의 references/coverage-contract.md를 따른다.
```
을 다음으로 바꾼다(같은 줄에 이어지는 ` 원본 정답·설명과`는 그대로 둔다):
```
생성 스킬 study-note-eli5는 2026-09-24에 bio-review-pack으로 대체되어 삭제되었다. 기존 ELI5 산출물은 git 이력의 그 스킬 규칙을 기준으로 읽는다.
```

§12의 문장
```
절차는 `/summary-note MMDD` 스킬의 canonical 파일 `../.agents/skills/summary-note/SKILL.md`가 맡는다. `.claude/skills/summary-note/SKILL.md`는 그 파일을 가리키는 얇은 진입점만 둔다. **규칙이 바뀌면 이 파일을, 절차가 바뀌면 canonical SKILL.md를** 고친다. 둘에 같은 내용을 쓰지 않는다.
```
을 다음으로 바꾼다:
```
새 회차 절차는 `/bio-review-pack` 스킬(정본 `../.agents/skills/bio-review-pack/SKILL.md`, 진입점 `.claude/skills/bio-review-pack/SKILL.md`)이 맡는다. 옛 `summary-note` 스킬은 2026-09-24에 삭제되었고, 아래 생성기 사용법은 기존 회차를 고칠 때만 쓴다.
```

- [ ] **Step 5: 전체 테스트**

Run: `.venv-question-bank/bin/python -m unittest discover tests 2>&1 | tail -3`
Expected: `OK` (삭제된 테스트만큼 수가 줄어든다. 실패·오류 0)

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK`

- [ ] **Step 6: 커밋**

```bash
git add tests/test_question_bank_scope.py tests/test_bio_review_pack_entrypoint.py 정리노트/CLAUDE.md
git status --short   # 삭제(D)와 위 세 파일만 staged인지, zip이 없는지 확인
git commit -m "refactor: replace summary-note and study-note-eli5 with bio-review-pack

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 실제 회차(0922)로 끝까지 실행

**Files:**
- Create (산출물, 커밋하지 않음): `복습노트/0922/정리노트_0922_<slug>.html`, `.md`, `복습노트/0922/복습문제_0922_<slug>.html`, `.md`, `복습노트/0922/figures_0922/`
- Modify (필요할 때만): `.agents/skills/bio-review-pack/SKILL.md`, `.agents/skills/bio-review-pack/references/*.md`

**Interfaces:**
- Consumes: Task 1~6 전부.
- Produces: 사용자에게 보여 줄 9단계 보고서, 발견한 절차 결함의 수정 커밋.

- [ ] **Step 1: 스킬 실행**

`.agents/skills/bio-review-pack/SKILL.md`를 처음부터 읽고 인자 `0922`로 0~9단계를 그대로 수행한다. 0단계 기간 판정 출력의 `마지막 정리:`가 `0917`, `다음:`에 `0922`가 있는지 먼저 확인한다.

- [ ] **Step 2: 산출물 검증**

```bash
SKILL=.agents/skills/bio-review-pack
ls 복습노트/0922
python3 "$SKILL/scripts/check_html.py" --manifest "<RUN>/manifest.json" --note 복습노트/0922/정리노트_0922_*.html --review 복습노트/0922/복습문제_0922_*.html
python3 "$SKILL/scripts/html2md.py" 복습노트/0922/정리노트_0922_*.html 복습노트/0922/복습문제_0922_*.html --check
grep -c -E "[①-⑳]" 복습노트/0922/*.html 복습노트/0922/*.md
```
Expected: 파일 4개와 `figures_0922/`, `OK`, `OK`, 각 파일 `0`. `<RUN>`은 1단계에서 정한 실제 경로다.

또 확인: `RUN/question-audit.md`의 3강 합계가 합본 전체 문항 수(40)와 같다. 블라인드 검사가 모든 포함 문항을 맞혔다.

- [ ] **Step 3: 절차 결함 반영**

실행 중 SKILL.md나 references의 지시가 모호하거나 틀려서 되돌아간 곳이 있으면 해당 문서를 고치고 스킬 테스트를 다시 돌린다:
Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests`
Expected: `OK`
고친 게 있으면 그 파일만 커밋한다:
```bash
git add .agents/skills/bio-review-pack/SKILL.md .agents/skills/bio-review-pack/references
git commit -m "docs(bio-review-pack): clarify steps found in first 0922 run

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: 보고**

9단계 형식의 보고서를 사용자에게 보여 준다. `복습노트/0922/` 산출물은 커밋하지 않고 커밋 명령만 제안한다. 브랜치 `feat/bio-review-pack`의 병합은 사용자가 정한다.
