# 문제 패널 붙이기·띄우기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 문제해설 페이지의 문제 패널을 왼쪽에 붙이기·오른쪽에 붙이기·띄우기(옮기고 크기 조절하는 창) 중 하나로 두게 하고, 1008 팩으로 사용자 확인을 받은 뒤 나머지 팩을 재발행한다.

**Architecture:** `#panel-prob` 한 요소를 그대로 두고 `.layout[data-prob-dock="left|right|float"]`에 따라 CSS가 grid 칸 2/4 또는 `position: fixed`로 배치한다. `panels-ui` 스크립트에 방식 저장·전환(`setDock`), 띄운 창 배치(`placeFloat`), 상단 바 버튼 자리(`placeToggle`), 머리 끌기(옮기기·떼기·붙이기 미리보기)를 더한다. 템플릿은 payload_hash 밖이라 발행은 `mpe_cli.py rerender`로 content·independent를 재사용하고 source_visual·browser만 재검토한다.

**Tech Stack:** 단일 HTML 템플릿(CSS·바닐라 JS), Python pytest, Playwright(Chromium).

**Spec:** `docs/superpowers/specs/2026-10-13-problem-panel-dock-float-design.md`

## Global Constraints

- 원본 복습문제·정리노트·`.pack/`·기출 PDF는 수정하지 않는다.
- 렌더러(`scripts/mpe_render.py`)·조각 계약·payload_hash는 바꾸지 않는다. 바뀌는 코드는 `assets/note-template.html`(과 테스트·문서)뿐.
- 푸시하지 않는다. 커밋 메시지 끝: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 스킬 변경 뒤 `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py`로 provenance 재생성. 스킬 디렉터리에 `.pytest_cache`를 남기지 않는다(`-p no:cacheprovider`). 두 테스트 묶음(`bio-problem-explain`, `bio-review-pack`)은 따로 실행한다(함께 돌리면 모듈 충돌).
- worktree를 `--force`로 지우지 않는다.
- 저장 키: 패널 `od-panels:explain:v2`(바꾸지 않음), 너비 `…:v2:w`, 새 키 `od-panels:explain:v2:prob` = `{dock: 'left'|'right'|'float', x, y, w, h}`. 값이 없거나 `dock`이 세 값이 아니거나 JSON이 깨졌으면 `dock: 'left'`.
- 수치: 띄운 창 기본 `w = 420`, `h = min(560, round(0.7 * innerHeight))`, `x = clientWidth − w − 24`, `y = 상단 바 bottom + 16`; 최소 280×200; 끌어 붙이기 `SNAP = 32`(px, 화면 왼쪽·오른쪽 끝에서); 떼기 문턱 `UNDOCK = 24`(px); 키보드 이동·크기 16px / Shift 64px; 띄운 창 `z-index: 30`, `border-radius: 12px`.
- 문구(aria-label): 방식 그룹 `문제 패널 위치`, 버튼 `왼쪽에 붙이기`·`오른쪽에 붙이기`·`띄우기`, 이동 버튼 `문제 창 이동. 화살표로 이동`, 모서리 `문제 창 크기 조절. 화살표로 조절`.
- 1024 미만·인쇄·`html:not(.js)`: 지금 규칙 그대로(문제 패널·버튼 숨김).
- 진행 순서(사용자 지정): Task 2에서 1008만 재발행하고 **멈춰서 사용자 확인을 받는다.** Task 3·4는 사용자 피드백 뒤에만.

## Review Focus

- 큰 화면에서 저장된 띄운 창(x=1500)으로 1100 화면에 재방문 → 창이 화면 안·상단 바 아래로 들어와 있다(Task 1 `float-clamp` 블록).
- 띄운 상태에서 900으로 줄였다 1280으로 복귀 → 900에선 인라인 '문제 보기', 복귀하면 다시 띄운 창(같은 위치)(Task 1 `float-cross` 블록).
- 오른쪽에 붙이고 목차·요약까지 연 1024 → 목차가 먼저 비켜서고 문서 가로 넘침 0, 본문 ≥ 320px(Task 1 `right-crowded` 블록).
- 저장값 `{"dock":"top"}`·깨진 JSON → 왼쪽에 붙음, 콘솔 오류 0(Task 1 `bad-pref` 블록).
- 붙인 패널 머리의 탭을 클릭 → 떨어지지 않고 탭만 바뀐다(Task 1 `tab-no-drag` 블록).

---

### Task 1: 템플릿에 붙이기·띄우기 추가

**Files:**
- Modify: `.agents/skills/bio-problem-explain/assets/note-template.html` (CSS `234-239`, `386-427`; 마크업 `461-500`; JS `panels-ui` `564-720`, 수식 ResizeObserver `1326-1328`)
- Modify: `.agents/skills/bio-problem-explain/SKILL.md:75`, `references/authoring.md:32`, `references/verification.md:10`
- Modify: `.agents/skills/bio-problem-explain/port-provenance.json` (재생성)
- Test: `.agents/skills/bio-problem-explain/tests/test_render.py`, `tests/browser_acceptance.py`

**Interfaces:**
- Consumes: 기존 `panels`, `toggles`, `SIDES`, `WIDTH`, `store`, `PREF`, `last`, `sync()`, `fit()`, `maxFor()`, `applyWidths()` (`note-template.html:564-720`).
- Produces (Task 2 검토 스크립트가 쓰는 DOM 계약):
  - `.layout[data-prob-dock="left|right|float"]` (마크업 기본 `left`)
  - `#panel-prob .prob-dock[role=group]` 안 `button[data-dock="left|right|float"][aria-pressed]`
  - `#panel-prob .float-move`(button), `#panel-prob .float-resize`(`role=button`, `tabindex=0`) — 띄웠을 때만 보임
  - `.layout .dock-preview` (끌기 중에만 보임, 그 밖엔 `hidden`)
  - `#toggle-prob[data-dock]` — 오른쪽에 붙이면 `#toggle-right` 바로 앞, 그 밖엔 `#toggle-left` 바로 뒤
  - JS(스크립트 내부): `setDock(dock: 'left'|'right'|'float'): void`, `placeFloat(): void`, `placeToggle(): void`, `dockPreview(side: 'left'|'right'|null): void`, `probPref(): {dock,x,y,w,h}`

- [ ] **Step 0: worktree 준비**

```bash
git worktree add .worktrees/problem-dock-float -b feat/problem-dock-float main
```
이후 모든 경로는 이 worktree 기준.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_render.py`에 추가:

```python
def test_problem_panel_dock_controls():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    assert '<div class="layout" data-left="open" data-prob="open" data-right="closed" data-prob-dock="left">' in t
    prob=t[t.index('id="panel-prob"'):t.index('<div class="content">')]
    group=prob[prob.index('class="prob-dock"'):]
    assert 'role="group"' in group and 'aria-label="문제 패널 위치"' in group
    assert [d for d in ('left','right','float') if f'data-dock="{d}"' in group]==['left','right','float']
    assert group.index('data-dock="left"')<group.index('data-dock="right"')<group.index('data-dock="float"')
    assert 'class="float-move"' in prob and 'class="float-resize"' in prob and 'aria-label="문제 창 이동. 화살표로 이동"' in prob
    assert 'class="dock-preview"' in t and "PREF + ':prob'" in t
```

`tests/browser_acceptance.py`의 `(1280,'light')` 블록 끝(`legacy` 뒤, `assert not logs,logs` 앞)에 추가(기존 압축 스타일):

```python
    box=lambda s:page.locator(s).bounding_box()
    def drag(a,b,steps=8):page.mouse.move(*a);page.mouse.down();page.mouse.move(*b,steps=steps);page.mouse.up();page.wait_for_timeout(150)
    def headgap():T,G=box('#panel-prob .panel-tabs'),box('#panel-prob .prob-dock');return ((T['x']+T['width']+G['x'])/2,T['y']+T['height']/2)
    page.evaluate('localStorage.clear()');page.goto(url+'#p3');page.reload();page.wait_for_timeout(150)
    assert page.locator('#panel-prob [data-dock="left"]').get_attribute('aria-pressed')=='true'
    # tab-no-drag: clicking a tab in the docked head does not undock
    page.locator('#tab-original').click();assert page.locator('.layout').get_attribute('data-prob-dock')=='left';page.locator('#tab-problem').click()
    # right: content | prob | summary, toggle sits before 요약, both open independently
    page.locator('#panel-prob [data-dock="right"]').click();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='right' and page.locator('#panel-prob [data-dock="right"]').get_attribute('aria-pressed')=='true'
    assert box('#panel-prob')['x']>=box('.content')['x']+box('.content')['width']-1
    assert page.evaluate("document.getElementById('toggle-prob').nextElementSibling.id")=='toggle-right'
    page.locator('#toggle-right').click();page.wait_for_timeout(250)
    assert box('#panel-prob')['x']+box('#panel-prob')['width']<=box('#panel-right')['x']+1
    page.locator('#toggle-prob').click();assert page.locator('#panel-prob').is_hidden() and page.locator('#panel-right').is_visible()
    page.locator('#toggle-prob').click();page.wait_for_timeout(150);assert page.locator('.layout').get_attribute('data-prob-dock')=='right'
    w0=box('#panel-prob')['width'];h=page.locator('#panel-prob .panel-resize');h.focus();h.press('ArrowLeft');assert box('#panel-prob')['width']>w0;h.press('Home')
    # right-crowded: at 1024 the TOC steps aside first
    page.set_viewport_size({'width':1024,'height':768});page.wait_for_timeout(250)
    assert page.locator('#panel-prob').is_visible() and page.locator('#panel-right').is_visible() and page.locator('#panel-left').is_hidden()
    assert page.evaluate('document.querySelector(".layout").scrollWidth<=innerWidth') and box('.content')['width']>=320
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(250);page.locator('#toggle-right').click();page.wait_for_timeout(250)
    # float: fixed card, content grows, default geometry under the top bar
    cw=box('.content')['width'];page.locator('#panel-prob [data-dock="float"]').click();page.wait_for_timeout(150)
    assert page.locator('#panel-prob').evaluate('e=>getComputedStyle(e).position')=='fixed' and box('.content')['width']>cw
    F=box('#panel-prob');top=box('.topbar');assert abs(F['width']-420)<=1 and F['y']>=top['y']+top['height']
    assert page.evaluate("document.getElementById('toggle-prob').previousElementSibling.id")=='toggle-left'
    # move by the grip, resize by the corner, both clamp
    M=box('#panel-prob .float-move');drag((M['x']+M['width']/2,M['y']+M['height']/2),(M['x']+M['width']/2-200,M['y']+M['height']/2+100))
    F2=box('#panel-prob');assert abs(F2['x']-(F['x']-200))<=1 and abs(F2['y']-(F['y']+100))<=1
    R=box('#panel-prob .float-resize');drag((R['x']+R['width']/2,R['y']+R['height']/2),(R['x']-600,R['y']-600))
    F3=box('#panel-prob');assert abs(F3['width']-280)<=1 and abs(F3['height']-200)<=1
    page.locator('#panel-prob .float-move').focus();page.keyboard.press('ArrowRight');assert abs(box('#panel-prob')['x']-(F3['x']+16))<=1
    # choice click still marks inside the floating panel
    page.locator('[data-problem-for="p3"] .review-choice[data-choice-id="5"]').click();page.wait_for_timeout(100)
    assert page.locator('[data-problem-for="p3"] [data-choice-id="5"]').get_attribute('data-result')
    # reload keeps float + geometry
    F4=box('#panel-prob');page.reload();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='float' and abs(box('#panel-prob')['x']-F4['x'])<=1
    # float-cross: narrow screen hides it, coming back restores it
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#panel-prob').is_hidden() and page.locator('#p3 .problem-toggle').count()==1
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
    assert page.locator('#panel-prob').is_visible() and abs(box('#panel-prob')['x']-F4['x'])<=1
    # snap: dragging to the right edge shows the preview, dropping docks right
    M=box('#panel-prob .float-move');page.mouse.move(M['x']+5,M['y']+5);page.mouse.down();page.mouse.move(1270,M['y']+5,steps=8)
    assert page.locator('.dock-preview').is_visible();page.mouse.up();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='right' and page.locator('.dock-preview').is_hidden()
    # undock: dragging the docked head's empty gap 24px+ makes it float under the pointer
    g=headgap();drag(g,(640,400))
    assert page.locator('.layout').get_attribute('data-prob-dock')=='float';F5=box('#panel-prob')
    assert F5['x']<=640<=F5['x']+F5['width'] and F5['y']<=400<=F5['y']+F5['height']
    # float-clamp: a saved position from a bigger screen comes back inside
    page.evaluate("localStorage.setItem('od-panels:explain:v2:prob',JSON.stringify({dock:'float',x:1500,y:-50,w:420,h:500}))")
    page.set_viewport_size({'width':1100,'height':height});page.reload();page.wait_for_timeout(150)
    F6=box('#panel-prob');top=box('.topbar');assert F6['x']>=0 and F6['x']+F6['width']<=1100 and F6['y']>=top['y']+top['height']
    # bad-pref: unknown dock or broken JSON falls back to left
    for v in ['{"dock":"top"}','{broken']:
     page.evaluate(f"localStorage.setItem('od-panels:explain:v2:prob',{json.dumps(v)})");page.reload();page.wait_for_timeout(150)
     assert page.locator('.layout').get_attribute('data-prob-dock')=='left'
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_render.py::test_problem_panel_dock_controls -q -p no:cacheprovider`
Expected: FAIL (`data-prob-dock="left"` 문자열 없음)

Run: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py "$(mktemp -d)/acc"`
Expected: FAIL — `[data-dock="left"]` 대기 시간 초과 또는 `aria-pressed` 단언 AssertionError

- [ ] **Step 3: 마크업·CSS 구현** (`note-template.html`)

- `.layout`에 `data-prob-dock="left"`(속성 순서는 Step 1의 문자열 그대로).
- `#panel-prob`의 `.panel-head`: 맨 앞 `button.float-move`(그립 아이콘), 탭 리스트, 끝에 `div.prob-dock[role=group][aria-label="문제 패널 위치"]`(버튼 3개, `margin-left: auto`로 탭과의 사이에 빈 띠를 만든다). 패널 마지막 자식 `div.float-resize`. `.layout` 안 끝에 `<div class="dock-preview" hidden></div>`.
- `.layout { grid-template-columns: auto auto minmax(320px, 1fr) auto auto }`, `.panel-right { grid-column: 5 }`, `[data-prob-dock="right"] .panel-prob { grid-column: 4; border-right: 0; border-left: 1px solid var(--line) }`, 오른쪽일 때 `.panel-prob .panel-resize`·`::after`는 `left: 0; right: auto`.
- ≥1024 `[data-prob-dock="float"] .panel-prob`: `position: fixed; left: var(--fx); top: var(--fy); width: var(--fw); height: var(--fh); z-index: 30; border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 12px 32px rgb(0 0 0 / .18)`, 머리 `cursor: grab`, `.panel-resize` 숨김. `.float-move`·`.float-resize`는 띄웠을 때만 보임(모서리 16×16, `cursor: nwse-resize`).
- `.dock-preview`: `position: fixed; z-index: 29; top: 상단 바 높이; bottom: 0; width: min(400px, 40vw); background: color-mix(in srgb, var(--accent) 18%, transparent); border: 2px solid var(--accent)`, `[data-side="left"]`이면 `left: 0`, `"right"`면 `right: 0`.
- `.prob-dock button[aria-pressed="true"]`는 강조색. `#toggle-prob[data-dock="right"] .strip`은 띠를 네 번째 칸(`x="15"`와 같은 자리)으로 옮기는 CSS(`transform`), 그 밖엔 지금 아이콘.
- 좁은 화면·인쇄·no-JS 규칙은 손대지 않는다(`.panel-prob` 숨김이 그대로 이 요소들을 숨긴다).

- [ ] **Step 4: JS 구현** (`panels-ui`)

- `probPref()`: `store.get(PREF + ':prob', {})`를 읽어 `dock`이 `left|right|float`가 아니면 `'left'`, 숫자가 아닌 x/y/w/h는 기본값(Global Constraints)으로 채워 돌려준다.
- `setDock(dock)`: `layout.dataset.probDock`, 버튼 `aria-pressed`, 저장, `last = 'prob'`, `sync()`.
- `placeToggle()`: `toggles.prob.dataset.dock = dock`; 오른쪽이면 `toggles.right.before(toggles.prob)`, 아니면 `toggles.left.after(toggles.prob)`. `sync()` 끝에서 부른다.
- `placeFloat()`: 영역 = 위 `topbar.getBoundingClientRect().bottom`, 오른쪽 `documentElement.clientWidth`, 아래 `documentElement.clientHeight`. 크기를 `[280, 영역]`·`[200, 영역]`으로 먼저 clamp한 뒤 위치를 clamp해 `--fx/--fy/--fw/--fh`(px)를 `panels.prob.style`에 쓴다. 저장값은 바꾸지 않는다(줄인 화면에서만 임시로 맞춤). `sync()`에서 넓은 화면·float·열림이면 부른다.
- `fit()`·`maxFor()`: float이면 `prob`를 폭 합계·숨김 순서에서 뺀다.
- 너비 손잡이 방향: `const dir = () => (side === 'right' || (side === 'prob' && layout.dataset.probDock === 'right')) ? -1 : 1;` — pointerdown·keydown 때마다 계산.
- 넓은 화면 float이면 `panels.prob`에 `role="dialog"`·`aria-labelledby="panel-prob-title"`(aria-modal 없음), 아니면 기존 규칙대로 지운다.
- 머리 끌기(`panels.prob.querySelector('.panel-head')` pointerdown, 넓은 화면·주 버튼, `e.target.closest('button:not(.float-move),[role=tab],a,input')`이면 무시):
  - 붙인 상태: 움직임이 `UNDOCK`(24px)을 넘으면 `x = clientX − w/2`, `y = clientY − 20`으로 저장하고 `setDock('float')` 뒤 아래 띄운 상태 끌기로 이어간다.
  - 띄운 상태: 시작점 기준 delta로 `--fx/--fy`를 clamp하며 옮기고, `clientX <= SNAP`이면 `dockPreview('left')`, `clientX >= clientWidth − SNAP`이면 `dockPreview('right')`, 아니면 `dockPreview(null)`.
  - 놓을 때: 미리보기가 있으면 `setDock(그쪽)`(x/y는 끌기 전 값 유지), 없으면 x/y 저장. `dockPreview(null)`.
- `.float-move` keydown: 화살표 16px / Shift 64px 이동 후 clamp·저장. `.float-resize` pointerdown: w/h 변경·clamp·저장. keydown: ←→는 w, ↑↓는 h를 16/64px.
- 수식 재배치 ResizeObserver(`1326-1328` 부근)에 `#panel-prob .panel-inner`도 observe.

- [ ] **Step 5: 테스트 통과 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q -p no:cacheprovider`
Expected: 177 passed

Run: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py "$(mktemp -d)/acc"`
Expected: JSON 6개(1280/1024/375 × light/dark), 각 `console_errors: []`, 종료 코드 0

- [ ] **Step 6: 문서·provenance**

- `SKILL.md:75`, `references/authoring.md:32`, `references/verification.md:10`: 문제 패널 설명에 "왼쪽·오른쪽에 붙이기·띄우기(머리 버튼, 끌어서 붙이기/떼기), 방식·위치는 `od-panels:explain:v2:prob`에 기억"을 한 문장씩 더한다(verification은 브라우저 확인 항목에 "세 방식 전환·띄운 창 이동/크기/화면 안 clamp").
- Run: `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py && find .agents/skills/bio-problem-explain -name .pytest_cache`
  Expected: 재생성 성공, `find` 출력 없음. Step 5의 pytest 다시 → 177 passed.

- [ ] **Step 7: 커밋**

```bash
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): dock the problem panel left or right, or float it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: 1008 재발행 후 사용자 확인 (여기서 멈춤)

**Files:**
- Modify: `복습노트/1008/문제설명_*.html`과 rerender가 쓰는 manifest·validation
- Create: `복습노트/1008/.assets/` 아래 `*rerender5*` 증거 파일
- Create(scratchpad, 커밋 안 함): `<scratchpad>/republish5.sh`, `<scratchpad>/review_pack5.py`

**Interfaces:**
- Consumes: Task 1의 DOM 계약 전부.
- Produces: `republish5.sh RANGE [TAG]` — 실행 디렉터리 `<scratchpad>/<TAG 기본 rr5>/<RANGE>`. Task 3·4가 같은 스크립트를 쓴다(고친 뒤 재발행은 새 TAG로).

`<scratchpad>` = `/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ-----/d8c23aa7-42ce-416f-9775-60e722a48f02/scratchpad`. 원본은 이전 세션 scratchpad(`…/63c50112-4e4e-4dcb-b50f-5a7b1f6e808a/scratchpad/republish4b.sh`, `review_pack4.py`).

- [ ] **Step 1: 스크립트 복사·수정**

- `republish4b.sh` → `republish5.sh`: `D`를 새 scratchpad로, `R=$D/${2:-rr5}/$RANGE`, `rerender4`→`rerender5`, `review_pack4.py`→`review_pack5.py`; source_visual 문구 "왼쪽 문제 패널" → "문제 패널(왼쪽 기본)", browser 문구에 "문제 패널 오른쪽 붙이기(본문|문제|요약)·띄우기(고정 위치 카드, 이동·크기 clamp)·왼쪽 복귀" 추가; reviewer 문구 `rerender5 문제 패널 붙이기·띄우기 검토`.
- `review_pack4.py` → `review_pack5.py`: 증거 파일명 `rerender5`. 1280 넓은 화면 검사(현재 `159-168`행 요약 패널 검사 뒤)에 추가:
  - `#panel-prob [data-dock="right"]` 클릭 → `#panel-prob` 박스 x ≥ `.content` 오른쪽 − 1, 아니면 `bad.append('prob not right')`; 요약 열어 `#panel-prob` 오른쪽 ≤ `#panel-right` x + 1, 아니면 `bad.append('right order')`; 요약 닫기.
  - `[data-dock="float"]` 클릭 → `position` `fixed`이고 상단 바 아래, 화면 안이 아니면 `bad.append('float')`; 현재 문항 패널(`#panel-prob .probs [data-problem-for]:visible`) 보임 확인; 문서 가로 넘침 0.
  - `[data-dock="left"]` 클릭으로 되돌리고 `localStorage.removeItem('od-panels:explain:v2:prob')`.
  - 이 상태에서 `rerender5-{range}-1280-float.png` 스크린샷 1장(띄운 상태에서) 추가.

- [ ] **Step 2: 1008 재발행**

Run (repo root = worktree): `bash <scratchpad>/republish5.sh 1008 2>&1 | tee <scratchpad>/rr5-1008.log`
Expected: `rerender:` 줄에 `content·independent 재사용`, review_pack 마지막 줄 JSON `"n_failures": 0`, `reviews merged`, `check` 통과, publish 성공. CDN 타임아웃·`ERR_CONNECTION_RESET`이면 한 번 재실행.

- [ ] **Step 3: 범위 확인**

Run: `git status --short && grep -c 'data-prob-dock' 복습노트/1008/문제설명_*.html`
Expected: 1008 문제설명 html·manifest·validation과 `*rerender5*` 증거만 변경, `복습문제_*`·`정리노트*`·`.pack/`·PDF 변경 0; grep 1 이상.

- [ ] **Step 4: 커밋**

```bash
git add 복습노트/1008
git commit -m "docs(notes): republish 1008 problem explanation with dockable problem panel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 5: 사용자에게 넘기고 멈춤**

worktree 안 `복습노트/1008/문제설명_*.html`의 전체 경로와 확인할 것(세 방식 버튼, 오른쪽에서 문제·요약 동시 열기, 띄운 창 이동·크기, 가장자리로 끌어 붙이기, 붙인 패널 끌어 떼기, 다크 모드)을 알리고 **피드백을 기다린다.** Task 3은 피드백이 와야 시작한다.

---

### Task 3: 사용자 피드백 반영 (피드백 받은 뒤 채움)

**Files:** 피드백에 따라 `note-template.html`, `tests/browser_acceptance.py`(또는 `test_render.py`).

**Interfaces:**
- Consumes: Task 1의 함수·DOM 계약, Task 2의 `republish5.sh RANGE TAG`.
- Produces: 같은 DOM 계약(바꾸면 `review_pack5.py`도 함께 고친다).

- [ ] **Step 1:** 피드백 항목마다 그 동작을 재현하는 단언을 `browser_acceptance.py` 1280-light 블록(좁은 화면 문제면 375 블록)에 추가하고 FAIL 확인 → 템플릿 수정 → Task 1 Step 5 두 명령 통과(pytest 177 + 추가분, 브라우저 JSON 6개·오류 0).
- [ ] **Step 2:** provenance 재생성(Task 1 Step 6 명령), 커밋 `fix(bio-problem-explain): <피드백 요지>`.
- [ ] **Step 3:** 1008 재발행: `bash <scratchpad>/republish5.sh 1008 rr5b` (고칠 때마다 `rr5c`, `rr5d`…로 새 TAG). Expected는 Task 2 Step 2와 같다. 커밋 후 다시 사용자 확인. 사용자가 "됐다"고 할 때까지 반복.

---

### Task 4: 나머지 팩 재발행

**Files:**
- Modify: `복습노트/{0901,0903,0908,0910,0915,0917,0922,0929,1001,1013}/문제설명_*.html`과 manifest·validation
- Create: 각 팩 `.assets/` 아래 `*rerender5*` 증거

**Interfaces:**
- Consumes: `republish5.sh RANGE TAG`(새 TAG `rr5all`).

1006은 정리노트가 바뀌어 content 재검토가 필요하므로 이번에도 제외한다.

- [ ] **Step 1: 재발행**

Run: `for r in 0901 0903 0908 0910 0915 0917 0922 0929 1001 1013; do echo "== $r"; bash <scratchpad>/republish5.sh $r rr5all > <scratchpad>/rr5all-$r.log 2>&1; echo "exit $?"; done`
Expected: 모두 `exit 0`, 각 로그 `"n_failures": 0`. 네트워크 실패 팩은 한 번 재실행(그 외 실패는 원인 확인).

- [ ] **Step 2: 범위·계약 확인**

Run: `grep -L 'data-prob-dock' 복습노트/*/문제설명_*.html`
Expected: `복습노트/1006/…`만 출력.

Run: `git status --short`
Expected: 10개 팩의 문제설명 html·manifest·validation·`*rerender5*` 증거만. 원본 변경 0.

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q -p no:cacheprovider` → 177(+Task 3 추가분) passed; `uv run --with pytest python -m pytest .agents/skills/bio-review-pack/tests -q -p no:cacheprovider` → 191 passed.

- [ ] **Step 3: 커밋**

```bash
git add 복습노트
git commit -m "docs(notes): republish problem explanations with dockable problem panel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

이후 최종 리뷰 → superpowers:finishing-a-development-branch(사용자 지정대로 main에 로컬 병합, worktree·브랜치 정리).
