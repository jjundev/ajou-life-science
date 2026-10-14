# 문제·원문 패널 왼쪽 분리 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 문제해설 페이지의 문제·원문을 목차 오른쪽·본문 왼쪽의 독립 패널로 옮기고, 오른쪽 패널은 요약만 남긴 뒤 12개 팩을 재발행한다.

**Architecture:** 템플릿의 기존 docked 패널 시스템(`sync`/`toggle`/`WIDTH` 리사이즈)에 세 번째 side `prob`를 더한다. `setupExplain`은 탭 DOM을 `panels.prob`에서 찾고 탭을 [문제 | 원문] 둘로 줄인다. 템플릿은 payload_hash 밖이라 발행은 `mpe_cli.py rerender`로 content·independent를 재사용하고 source_visual·browser만 재검토한다.

**Tech Stack:** 단일 HTML 템플릿(CSS·바닐라 JS), Python pytest, Playwright(Chromium).

**Spec:** `docs/superpowers/specs/2026-10-13-left-problem-panel-design.md`

## Global Constraints

- 원본 복습문제·정리노트·`.pack/`·기출 PDF는 수정하지 않는다.
- 렌더러(`scripts/mpe_render.py`)·조각 계약·payload_hash는 바꾸지 않는다. 바뀌는 코드는 `assets/note-template.html`뿐.
- 푸시하지 않는다. 커밋 메시지 끝: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 스킬 변경 뒤 `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py`로 provenance 재생성. 스킬 디렉터리에 `.pytest_cache`를 남기지 않는다(`-p no:cacheprovider`).
- 저장 키: 패널 `od-panels:explain:v2`(너비는 `od-panels:explain:v2:w`), 탭 `bio-problem-explain-tab` 그대로.
- 첫 방문 기본: `{left: matchMedia('(min-width: 1280px)').matches, prob: true, right: false}`.
- 너비: 문제 패널 자동 `clamp(360px, calc(100vw - var(--l) - var(--r) - var(--measure) - var(--scrollbar)), 720px)`, 요약 패널 자동 `clamp(300px, 22vw, 380px)`; 드래그 범위 `prob {min: 320, max: 720}`.
- 문구: 새 버튼 `문제`, 오른쪽 버튼 항상 `요약`, 오른쪽 패널 제목 항상 `페이지 요약`(보임).
- 1024 미만: `#panel-prob`·`#toggle-prob` 숨김, 인라인 '문제 보기' 동작 그대로.
- `setupReview`·`revealCurrent`(review kind 전용, `note-template.html:716-763`)는 건드리지 않는다.

## Review Focus

- 예전 저장값 `od-panels:explain = {"right": true}`를 가진 재방문자 → 요약이 열리지 않고 문제 패널이 열린다(Task 1 Step 1 `legacy` 블록).
- 저장된 탭이 `'summary'`인 재방문자 → 문제 탭이 선택된다(같은 블록).
- 1024에서 목차·문제·요약을 모두 연 상태 → 문서 가로 넘침 0, 본문 폭 ≥ 320px(Task 1 Step 1 `crowded` 블록).
- 1280에서 문제 패널을 닫고 900으로 줄였다 되돌림 → 900에서 인라인 '문제 보기'가 생기고, 1280 복귀 시 문제 패널은 여전히 닫혀 있다(`cross` 블록).
- 목차가 열린 채 문제 패널 핸들을 Shift+→ 20회 → 본문 폭 ≥ 380px로 남는다(`grow` 블록).

---

### Task 1: 템플릿에 왼쪽 문제 패널 추가

**Files:**
- Modify: `.agents/skills/bio-problem-explain/assets/note-template.html` (CSS `216`, `234-239`, `387-427`; 마크업 `456-508`; JS `550-690`, `770-860`, `1095-1110`)
- Modify: `.agents/skills/bio-problem-explain/SKILL.md:75`, `references/authoring.md:32`, `references/verification.md:10`
- Modify: `.agents/skills/bio-problem-explain/port-provenance.json` (재생성)
- Test: `.agents/skills/bio-problem-explain/tests/test_render.py`, `tests/browser_acceptance.py`

**Interfaces:**
- Consumes: 없음
- Produces: DOM 계약 — `#toggle-prob`, `#panel-prob` 안 `#tab-problem`·`#tab-original`·`#tabpanel-problem .probs`·`#tabpanel-original .orig-tab`·`.panel-resize[data-side="prob"]`; `#panel-right` 안 `#panel-right-title`·`.sum-tab .sums`; `.layout[data-prob="open|closed"]`. Task 2의 검토 스크립트가 이 선택자를 쓴다.

- [ ] **Step 0: worktree 준비**

```bash
git worktree add .worktrees/left-problem-panel -b feat/left-problem-panel main
```
이후 모든 경로는 이 worktree 기준.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_render.py`에 추가:

```python
def test_problem_panel_left_of_content():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    bar=t[t.index('<header class="topbar">'):t.index('</header>')]
    assert bar.index('id="toggle-left"')<bar.index('id="toggle-prob"')<bar.index('class="brand"')<bar.index('id="toggle-right"')
    assert t.index('id="panel-left"')<t.index('id="panel-prob"')<t.index('<div class="content">')<t.index('id="panel-right"')
    right=t[t.index('id="panel-right"'):]
    assert 'id="tab-problem"' not in right and 'id="tab-summary"' not in t
    prob=t[t.index('id="panel-prob"'):t.index('<div class="content">')]
    assert 'id="tab-original"' in prob and 'data-side="prob"' in prob
    assert "'od-panels:' + kind + ':v2'" in t or "od-panels:explain:v2" in t
```

`tests/browser_acceptance.py` 갱신(기존 압축 스타일 유지):
- 넓은 화면 블록(`if width>=1024:`, 현재 41-63행): `#panel-right .probs` → `#panel-prob .probs`, `#panel-right [role=tab]…` → `#panel-prob [role=tab]…`. 요약 탭 클릭 두 줄을 다음으로 교체:
  ```python
  assert page.locator('#panel-right').is_hidden() and page.locator('#toggle-prob').get_attribute('aria-expanded')=='true'
  L,P,C=[page.locator(s).bounding_box() for s in ('#panel-left','#panel-prob','.content')]
  assert P['x']+P['width']<=C['x']+1 and (not page.locator('#panel-left').is_visible() or L['x']+L['width']<=P['x']+1)
  assert page.locator('#panel-right-title').inner_text()=='페이지 요약' and page.locator('#toggle-right').inner_text()=='요약'
  ```
  ArrowRight 순환 단언(59-62행)은 `original → problem`(두 탭)으로: `ArrowRight` 한 번 뒤 `#tab-problem` 선택.
- 좁은 화면 블록: `assert page.locator('#toggle-prob').is_hidden() and page.locator('#panel-prob').is_hidden()` 추가.
- 인쇄 뒤 단언(152행)·`#panel-right .probs` 모든 사용처 → `#panel-prob .probs`.
- 요약 확인(153행): 조건 없이 `page.locator('#toggle-right').click()` 후 `#panel-right .summary-group` 단언, 닫기는 넓은 화면에서 `#toggle-right` 재클릭.
- 1280·light 페이지에서만 실행하는 Review Focus 블록을 루프 끝(`page.close()` 직전)에 추가:
  ```python
  if (width,theme)==(1280,'light'):
   # cross
   page.locator('#toggle-prob').click();assert page.locator('#panel-prob').is_hidden()
   page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
   assert page.locator('#p2 .problem-toggle').count()==1 and page.locator('#toggle-prob').is_hidden()
   page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
   assert page.locator('#panel-prob').is_hidden();page.locator('#toggle-prob').click()
   # grow
   if page.locator('#toggle-left').get_attribute('aria-expanded')=='false':page.locator('#toggle-left').click()
   h=page.locator('#panel-prob .panel-resize');h.focus()
   for _ in range(20):h.press('Shift+ArrowRight')
   assert page.locator('.content').bounding_box()['width']>=380;h.press('Home')
   # crowded
   page.set_viewport_size({'width':1024,'height':768});page.wait_for_timeout(150)
   if page.locator('#panel-right').is_hidden():page.locator('#toggle-right').click()
   page.wait_for_timeout(250)
   assert all(page.locator(s).is_visible() for s in ('#panel-left','#panel-prob','#panel-right'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth') and page.locator('.content').bounding_box()['width']>=320
   # legacy
   page.evaluate("localStorage.clear();localStorage.setItem('od-panels:explain','{\"right\":true}');localStorage.setItem('bio-problem-explain-tab','\"summary\"')")
   page.set_viewport_size({'width':1280,'height':height});page.goto(url+'#p3');page.wait_for_timeout(150)
   assert page.locator('#panel-right').is_hidden() and page.locator('#panel-prob').is_visible()
   assert page.locator('#tab-problem').get_attribute('aria-selected')=='true'
  ```
  (페이지는 이미 각 조합마다 새 컨텍스트라 localStorage가 비어 있는 첫 방문에서 시작한다.)

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_render.py::test_problem_panel_left_of_content -q -p no:cacheprovider`
Expected: FAIL (`toggle-prob` 없음, ValueError substring not found)

Run: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py "$(mktemp -d)/acc"`
Expected: FAIL — `#panel-prob .probs` 단언에서 AssertionError

- [ ] **Step 3: 마크업·CSS 구현** (`note-template.html`)

스펙 Implementation spec의 마크업·CSS 항목 그대로. 결정이 필요한 점만:
- `#toggle-prob` 아이콘: 목차 아이콘과 같은 구조, `.strip`을 `x="9" width="6"`, 구분선 `M9 4v16 M15 4v16`.
- `:root`(216행)에 `--panel-p-min: 360px; --panel-p-max: 720px; --panel-r: clamp(300px, 22vw, 380px);` 추가, `--panel-r-min/max`는 제거.
- ≥1024: `.layout { --r: var(--panel-r-user, var(--panel-r)); } .layout[data-right="closed"] { --r: 0px; }`, `.panel-right { width: var(--r) }`, `.panel-prob { width: var(--panel-p-user, clamp(var(--panel-p-min), calc(100vw - var(--l) - var(--r) - var(--measure) - var(--scrollbar)), var(--panel-p-max))) }`, `.panel-prob .panel-resize { right: 0 }`과 `::after { right: 0 }`, `.layout[data-prob="closed"] .panel-prob { display: none }`.
- <1024: `.panel-prob, #toggle-prob { display: none }`. no-JS 줄(423행)에 `html:not(.js) .panel-prob`·`#toggle-prob` 추가.

- [ ] **Step 4: JS 구현** (`note-template.html`)

- `panels`/`toggles`에 `prob`(`#panel-prob`/`#toggle-prob`), `PREF = 'od-panels:' + kind + ':v2'`.
- `docked()` explain 분기: `{ left: pref.left ?? roomyMq.matches, prob: pref.prob ?? true, right: pref.right ?? false }`; 다른 kind는 `prob: false`.
- `sync()`: `['left','prob','right']` 순회, `prob`는 `open = wide && d.prob`이고 drawer 속성(`is-open`, `role=dialog`)을 붙이지 않는다.
- `toggles.prob` 클릭 → `toggle('prob')`(넓은 화면 경로만 탄다).
- `WIDTH.prob = { min: 320, max: 720, prop: '--panel-p-user' }`; `applyWidths`는 세 side 순회.
- `maxFor(side)`: 열린(`layout.dataset[s]==='open'`) 다른 패널들의 `getBoundingClientRect().width` 합을 `innerWidth`에서 빼고 400을 더 뺀 값과 `WIDTH[side].max` 중 작은 값, `WIDTH[side].min` 이상.
- 핸들 방향: `const dir = side === 'right' ? -1 : 1;`.
- `setupExplain`: `probs`·`origTab`·`origBtn`·`tabList`·`tabs`는 `panels.prob`에서; `box`·`sumTab`·`sub`·`empty`는 `panels.right`; 탭 목록 `['problem','original']`, 저장값이 그 밖이면 `'problem'`; `showTab`에서 `sumTab.hidden` 줄 제거; `mountPanes`에서 `tabList.hidden`·`title`·`label` 줄 제거하고 `showTab(tab, false)`; 키보드 순서 `['problem'].concat(origs[curId] ? ['original'] : [])`; `od:screen`에서 `panels.prob`와 `panels.right`의 `.panel-inner` 둘 다 `scrollTop = 0`; 마크업에서 제목을 '페이지 요약', 라벨을 '요약'으로 고정.
- 보기 클릭·판정 이동 코드에서 `panels.right`로 문제 패널을 가리키던 곳이 있으면 `panels.prob`로(`grep -n "panels.right" note-template.html`로 explain 구간 770행 이후만 확인).

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q -p no:cacheprovider`
Expected: 176 passed

Run: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py "$(mktemp -d)/acc"`
Expected: JSON 6개(1280/1024/375 × light/dark), 각 `console_errors: []`, 종료 코드 0

- [ ] **Step 6: 문서 갱신·provenance 재생성**

- `SKILL.md:75`: "문제는 넓은 화면에서 오른쪽 [문제 | 원문 | 요약] 탭(원문 탭은 원문이 있는 문항만)" → "문제는 넓은 화면에서 목차 오른쪽·본문 왼쪽의 문제 패널 [문제 | 원문] 탭(원문 탭은 원문이 있는 문항만), 요약은 오른쪽 요약 패널".
- `references/authoring.md:32`: "오른쪽 문제 패널에서" → "왼쪽 문제 패널에서".
- `references/verification.md:10`: "1280·1024에서 오른쪽 문제 탭이 기본으로 보이고 원문·요약 탭 전환이 되는지(원문 없는 문항은 원문 탭 숨김)" → "1280·1024에서 본문 왼쪽 문제 패널이 기본으로 열리고 목차와 동시에 열리는지, 원문 탭 전환(원문 없는 문항은 원문 탭 숨김)과 오른쪽 요약 패널 열기가 되는지".
- Run: `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py && find .agents/skills/bio-problem-explain -name .pytest_cache`
  Expected: 재생성 성공, `find` 출력 없음. 이어서 Step 5의 pytest 다시 → 176 passed.

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): move problem and original into a left panel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: 12개 팩 재발행

**Files:**
- Modify: `복습노트/<range>/문제설명_*.html`(12개)와 그 manifest·validation 파일(rerender가 쓰는 것만)
- Create: 각 팩 `.assets/` 아래 `*rerender4*` 증거 파일
- 검토 스크립트(커밋하지 않음): `<scratchpad>/republish4.sh`, `<scratchpad>/review_pack4.py`

**Interfaces:**
- Consumes: Task 1의 DOM 계약(`#panel-prob .probs [data-problem-for]`, `#panel-prob [data-tab="original"]`, `#toggle-right`·`#panel-right .sum-tab`, `#toggle-prob`).
- Produces: 없음(최종 발행물).

대상 범위: `0901 0903 0908 0910 0915 0917 0922 0929 1001 1006 1008 1013`.

- [ ] **Step 1: 검토 스크립트 복사·수정**

`<scratchpad>` = `/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ-----/63c50112-4e4e-4dcb-b50f-5a7b1f6e808a/scratchpad`.
- `republish3.sh` → `republish4.sh`: `rr3`→`rr4`, `rerender3`→`rerender4`, `review_pack3.py`→`review_pack4.py`; source_visual evidence 문구 "오른쪽 문제 패널" → "왼쪽 문제 패널", browser 문구에 "목차·문제 패널 동시 열림, 오른쪽 요약 패널" 추가, "요약 탭·서랍" → "요약 패널·서랍".
- `review_pack3.py` → `review_pack4.py`: `#panel-right .probs` → `#panel-prob .probs`, 문제 패널 넘침 검사 `#panel-right .panel-inner` → `#panel-prob .panel-inner`, 패널 스크린샷 대상 `#panel-prob`, 요약 탭 클릭(159-161행)을 "`#toggle-right` 클릭 → `#panel-right .sum-tab` 보임 → 다시 클릭"으로, 넓은 화면에서 `#panel-prob` 박스가 `.content` 왼쪽에 있는지 검사 추가(`bad.append('prob not left')`), 증거 파일명 `rerender4`.

- [ ] **Step 2: 한 팩으로 시험**

Run: `bash <scratchpad>/republish4.sh 1013 2>&1 | tee <scratchpad>/rr4-1013.log`
Expected: `rerender:` 줄에 `content·independent 재사용`, review_pack 마지막 줄 JSON에 `"n_failures": 0`, 끝의 `check` 출력이 통과(`ok`/발행 가능 상태), `reviews merged` 출력.

- [ ] **Step 3: 나머지 11개 팩**

Run: `for r in 0901 0903 0908 0910 0915 0917 0922 0929 1001 1006 1008; do echo "== $r"; bash <scratchpad>/republish4.sh $r > <scratchpad>/rr4-$r.log 2>&1; echo "exit $?"; done`
Expected: 모두 `exit 0`, 각 로그 `"n_failures": 0`. CDN 타임아웃·`ERR_CONNECTION_RESET`으로 실패한 팩은 한 번 재실행(그 외 실패는 원인 확인).

- [ ] **Step 4: 발행**

각 팩을 지난 회차(12a659f)와 같은 `mpe_cli.py publish --run <scratchpad>/rr4/<range>` 절차로 발행.
Expected: 12개 모두 발행 성공. `git status --short`에 12개 문제설명 html·manifest·validation과 `*rerender4*` 증거만 보이고, `복습문제_*`·`정리노트*`·`.pack/`·PDF 변경 0.

- [ ] **Step 5: 발행물 확인·전체 테스트**

Run: `grep -L 'id="panel-prob"' 복습노트/*/문제설명_*.html`
Expected: 출력 없음

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q -p no:cacheprovider` → 176 passed; `uv run --with pytest python -m pytest .agents/skills/bio-review-pack/tests -q -p no:cacheprovider` → 191 passed.

- [ ] **Step 6: 커밋**

```bash
git add 복습노트
git commit -m "docs(notes): republish problem explanations with left problem panel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
