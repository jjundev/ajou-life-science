# 문제해설 문제 패널 레이아웃 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 문제설명·문제해설 HTML에서 문제를 오른쪽 클릭형 패널로 옮기고 가운데를 해설 전용으로 만든 뒤, 기존 12팩을 조각 재저작 없이 재발행한다.

**Architecture:** 추출 단계가 원 복습문제의 `review-interaction-model` JSON에서 보기 모델(`ChoiceModel`)을 읽는다. 조립기는 문제를 article 안 `div.problem-pane`으로 감싸고 모델을 `script#explain-choice-model`로 심는다. 템플릿의 `setupExplain()`이 pane을 화면 폭에 따라 오른쪽 패널(문제 탭) 또는 article 맨 위 접힘 버튼으로 옮기고, 보기 클릭 시 판정 표시와 해설 이동을 처리한다. `rerender`는 발행된 조각·근거를 재사용해 다시 build하고, 입력 해시가 같으면 content·independent 검토를 이식한다.

**Tech Stack:** Python 3.10+ 표준 라이브러리(실행기), pytest(`uv run --with pytest`), Playwright(시스템 `python3`, 브라우저 수용 테스트), 인라인 CSS/JS 템플릿.

**Spec:** `docs/superpowers/specs/2026-10-13-problem-pane-layout-design.md`

## Global Constraints

- `SKILL` = `.agents/skills/bio-problem-explain` (저장소 루트 기준). 모든 명령은 저장소 루트에서 실행한다.
- 단위 테스트: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q` (현재 136 passed).
- 브라우저 수용: `python3 .agents/skills/bio-problem-explain/tests/browser_acceptance.py <비어 있는 scratchpad 폴더>`.
- SKILL 아래 파일을 하나라도 바꾸면 커밋 전에 `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py`로 `assets/port-provenance.json`을 재생성한다(`test_claude_link_and_provenance`가 전 파일 해시를 검사).
- 실행기는 표준 라이브러리만 쓴다. 산출 HTML은 외부 요청 0, 콘솔 오류 0, 문서 가로 넘침 0.
- 고정 문구: 탭 "문제"/"요약", 토글 라벨 "문제", 모바일 버튼 "문제 보기"(펼치면 "문제 접기"), 배지 "내 선택"/"정답"/"출제 의도상 답", 해제 버튼 "다시 고르기", 원문 요약 "기출 원문 보기"(forecast "원문·출처 정보 보기"), 부제 "왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요."
- 저장 키: 탭 `bio-problem-explain-tab`. 보기 선택은 저장하지 않는다(메모리만).
- 수치: `--panel-r-min: 360px`, wide 경계 1024px(`wideMq`), 강조 1.6초, 이동 시 대상 상단이 스크롤러 높이의 1/4 지점.
- 판정 문단 정규식(보기 id `ID`, 정규식 이스케이프): `^\(?ID(\)|\.|\s)`, 대상은 현재 article `[data-explanation="solve"]` 안의 `p, li`. 실패 시 solve의 `h4`.
- 원 복습문제·정리노트·`.pack/`·기출 PDF는 수정하지 않는다. 조각 저작 계약(일곱 구역, `sum[hidden]`)은 바꾸지 않는다.
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. 푸시하지 않는다.

## Review Focus

1. 보기 목록이 있지만 모델에 없는 카드(skipped·비객관식) → 정적 문제로 보이고 클릭 요소·콘솔 오류가 없다 (Task 4 `p1에 .review-choice 0개` 단언).
2. ambiguous 문항 → 정답 카드 배지가 "출제 의도상 답" (Task 4 fixture p4).
3. 판정 문단 라벨이 보기 id와 다른 조각(실측 1006 p3: `a 맞아요`) → solve 제목으로 이동하고 강조 (Task 4 fixture p4).
4. 보기를 고른 상태에서 창 폭이 1024 경계를 넘나듦 → pane이 패널↔article로 옮겨져도 선택 상태 유지 (Task 4 리사이즈 단언).
5. 발행 후 원 복습문제가 바뀐 팩을 rerender → 검토를 이식하지 않고 "입력 변경" 안내 (Task 5 `test_rerender_changed_source_keeps_reviews_unrun`).

---

### Task 1: 보기 모델 추출

**Files:**
- Modify: `SKILL/scripts/mpe_types.py` (Problem 끝에 필드, `ChoiceModel` 추가)
- Modify: `SKILL/scripts/mpe_source.py:170-192` (`load_source`)
- Modify: `SKILL/scripts/mpe_forecast.py:80-84`
- Modify: `SKILL/scripts/mpe_cli.py:29-44` (`extract` 경고)
- Modify: `SKILL/tests/helpers.py` (`choice_source_file`에 `model` 인자), `SKILL/tests/forecast_helpers.py` (`forecast_source_file`에 모델 스크립트)
- Test: `SKILL/tests/test_source.py`, `SKILL/tests/test_forecast_source.py`, `SKILL/tests/test_cli.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) class ChoiceModel: answer: str; mode: str; option_ids: tuple[str, ...]` in `mpe_types` (`mode` ∈ `'single'|'ambiguous'`).
  - `Problem.choice: ChoiceModel | None = None` (마지막 필드, 기본값 있음 → 기존 위치 인자 호출 유지).
  - `choice_models(html_text: str, statements: dict[str, str]) -> dict[str, ChoiceModel]` in `mpe_source`: 유효한 카드만 담는다.
  - `helpers.choice_source_file(repo, ..., model: dict | None = None)`: `model`이 있으면 `</section>` 뒤에 `<script id="review-interaction-model" type="application/json">{json}</script>`를 쓴다.

- [ ] **Step 1: 실패 테스트 작성** (`test_source.py`)

```python
def test_choice_model_read_from_review_model(tmp_path):
    model={'schema':1,'cards':{'p1':{'answer':'1','mode':'single','options':[{'id':'1','index':0,'diagnostic':0},{'id':'5','index':1,'diagnostic':1}],'version':'x'}}}
    pack=load_source(choice_source_file(tmp_path/'repo',model=model),tmp_path/'repo')
    assert pack.problems[0].choice==ChoiceModel('1','single',('1','5'))

def test_choice_model_ambiguous_mode(tmp_path):
    model={'schema':1,'cards':{'p1':{'answer':'5','mode':'ambiguous','options':[{'id':'1','index':0},{'id':'5','index':1}]}}}
    assert load_source(choice_source_file(tmp_path/'repo',model=model),tmp_path/'repo').problems[0].choice.mode=='ambiguous'

@pytest.mark.parametrize('options,answer',[
    ([{'id':'1','index':0}],'1'),                                  # 옵션 수 ≠ li 수
    ([{'id':'1','index':0},{'id':'5','index':1}],'3'),             # answer 없음
    ([{'id':'1','index':0},{'id':'5','index':0}],'1')])            # index 중복
def test_choice_model_mismatch_is_none(tmp_path,options,answer):
    model={'schema':1,'cards':{'p1':{'answer':answer,'mode':'single','options':options}}}
    assert load_source(choice_source_file(tmp_path/'repo',model=model),tmp_path/'repo').problems[0].choice is None

def test_choice_model_absent_is_none(tmp_path):
    assert load_source(choice_source_file(tmp_path/'repo'),tmp_path/'repo').problems[0].choice is None
```

`test_forecast_source.py`: `forecast_source_file`가 p1–p15에 `{'answer': key, 'mode':'single','options':[{'id':L,'index':i} for i,L in enumerate('ABCDE')]}` 모델을 쓰게 하고, `test_forecast_choice_model_letters`에서 `pack.problems[0].choice.option_ids==('A','B','C','D','E')`와 `answer==key['p1']`를 단언. o1·o2는 문항에 없으므로 모델에 있어도 무시된다.

`test_cli.py`: `test_extract_warns_static_choices` — 모델 없는 `choice_source_file`로 extract → returncode 0, stderr에 `p1: 보기 모델 없음/불일치 — 정적 표시`.

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_source.py .agents/skills/bio-problem-explain/tests/test_forecast_source.py .agents/skills/bio-problem-explain/tests/test_cli.py -q`
Expected: FAIL (`ImportError: ChoiceModel`, `choice_source_file() got an unexpected keyword argument 'model'`)

- [ ] **Step 3: 구현**

- `choice_models`: 정규식으로 스크립트 본문을 찾아 `json.loads`(실패·부재 → `{}`). 카드마다 `statements[id]`를 `parse`해 최상위 `ul.choices, ol.choices`(첫 번째)의 직계 `li` 수를 센다. 조건: 옵션 수 = li 수, `answer` ∈ ids, `sorted(index) == list(range(n))`, ids 중복 없음, `mode` ∈ {single, ambiguous}. 통과하면 index 순서로 `option_ids`.
- `load_source`·`load_forecast_source`: 문항 생성 후 `dataclasses.replace(p, choice=models.get(p.id))`.
- `extract`: `pack` 로드 뒤 `p.choice is None`이고 `'choices'`가 `p.conditions_html`에 class로 있으면 stderr로 위 경고. 반환 코드는 바꾸지 않는다.

- [ ] **Step 4: 통과 확인**

Run: 전체 단위 테스트 명령. Expected: 모두 PASS (`test_cli_round_trip…`은 실제 0917 원본 모델로 `choice`가 채워진 채 round-trip).

- [ ] **Step 5: provenance 재생성 후 커밋**

```bash
python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py
git add .agents/skills/bio-problem-explain
git commit -m "feat(bio-problem-explain): read choice model from review cards"
```

---

### Task 2: 문제 pane과 보기 모델 조립

**Files:**
- Modify: `SKILL/scripts/mpe_render.py:148-175` (`build_explanation`)
- Test: `SKILL/tests/test_render.py`

**Interfaces:**
- Consumes: `Problem.choice: ChoiceModel | None` (Task 1).
- Produces (Task 3·4 JS가 의존하는 DOM):
  - 문항마다 `article.topic#pN > div.problem-pane[data-problem-for="pN"]`, 그 안에 `div.layer.formal[data-source-problem="pN"]`(h4 없음, `data-source-field` 그대로), 원문이 있으면 `details.original[data-original-problem="pN"] > summary`(문구는 Global Constraints).
  - `<script type="application/json" id="explain-choice-model">{"pN":{"answer":…,"mode":…,"options":[…ids…]}}</script>` — `choice`가 있는 문항만, 키 `options`는 `option_ids` 리스트.

- [ ] **Step 1: 실패 테스트 작성**

```python
def test_problem_pane_wraps_statement_and_original(tmp_path):
    pack,fragments=make(tmp_path);result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    doc=parse(result.html.read_text())
    panes=list(doc.find_all(lambda n:'problem-pane' in n.classes))
    assert [n.attrs['data-problem-for'] for n in panes]==['p1']
    assert len(list(panes[0].find_all(lambda n:n.attrs.get('data-source-problem')=='p1')))==1
    original=[n for n in panes[0].find_all(lambda n:n.tag=='details')]
    assert len(original)==1 and 'original' in original[0].classes and '기출 원문 보기' in original[0].text()
    assert '주어진 조건</h4>' not in result.html.read_text()

def test_choice_model_json_embedded_and_escaped(tmp_path):
    pack,fragments=make(tmp_path)
    pack=replace(pack,problems=(replace(pack.problems[0],choice=ChoiceModel('</script>','single',('</script>','2'))),))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    text=result.html.read_text()
    m=re.search(r'<script type="application/json" id="explain-choice-model">(.*?)</script>',text,re.S)
    assert json.loads(m[1])=={'p1':{'answer':'</script>','mode':'single','options':['</script>','2']}}
    assert '<\\/script>' in m[1]

def test_problem_without_choice_absent_from_model(tmp_path):
    pack,fragments=make(tmp_path);text=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo').html.read_text()
    assert re.search(r'id="explain-choice-model">\{\}</script>',text)
```

`test_legacy_statement_rendered_once`의 `assert not list(...details...)`는 "`details`는 `details.original` 하나뿐"으로 바꾸고, `생명과학 복습 0917 문제설명` 옆에 새 부제 문구 단언을 추가한다. forecast 렌더 테스트(`test_forecast_pipeline.py`)에 summary가 "원문·출처 정보 보기"인지 단언을 추가한다.

- [ ] **Step 2: 실패 확인** — `…/tests/test_render.py -q` → FAIL(`problem-pane` 없음).

- [ ] **Step 3: 구현** — `reading`을 pane으로 감싸고 원문을 `details`로, `values['SCRIPTS']`에 모델 스크립트(`json.dumps(..., ensure_ascii=False).replace('</', '<\\/')`), `SUBTITLE` 교체. `resources(...)`는 pane 전체 문자열에 그대로 적용한다. `check_artifacts`는 바꾸지 않는다.

- [ ] **Step 4: 통과 확인** — 전체 단위 테스트 PASS. MD에 문제 텍스트가 해설보다 앞에 있는지 `test_legacy…`의 `md.index('printf') < md.index('이 문제를 봤을 때')`로 단언 추가 후 PASS.

- [ ] **Step 5: provenance 재생성 후 커밋** — `feat(bio-problem-explain): wrap problem in pane and embed choice model`

---

### Task 3: 오른쪽 패널 탭과 pane 배치

**Files:**
- Modify: `SKILL/assets/note-template.html` — body `data-panels`(:353), 오른쪽 패널 마크업(:386-397), 패널 기본값 `docked()`(:460-463), `--panel-r-min`(:215), 토글 라벨(:359), `setupNote`(:654-682)를 `setupExplain`으로 교체, CSS 추가
- Modify: `SKILL/tests/helpers.py` (`acceptance_pack`에 p3·p4 보기 카드와 모델 추가)
- Modify: `SKILL/tests/browser_acceptance.py`
- Modify: `SKILL/references/verification.md` (browser 항목), `SKILL/SKILL.md` (실행 6단계에 레이아웃 한 문단)

**Interfaces:**
- Consumes: Task 2의 `div.problem-pane[data-problem-for]`, `.sum` 조각, `od:screen` 이벤트(`detail.screen`).
- Produces (Task 4가 사용):
  - 오른쪽 패널: `div.panel-tabs[role=tablist] > button[role=tab][data-tab="problem"|"summary"]`, `div.probs[role=tabpanel]`, `div.sums[role=tabpanel]`.
  - 좁은 화면: article 메타 뒤 `button.problem-toggle[aria-expanded][aria-controls]` + 바로 다음 형제로 pane(`hidden` 토글).
  - 함수 `mountPanes()`(wideMq 변경과 초기화 때 호출), 전역 아닌 클로저 안 `curId`(현재 문항 id).
- `acceptance_pack` 추가 문항(Task 4에서도 사용):
  - p3: `<ul class="choices">` `(1)`~`(5)` 다섯 항목, 모델 `{'answer':'3','mode':'single'}`, 조각 solve는 `(1) 틀려요…`~`(5) 틀려요…`, 마지막 `따라서 답은 (3)이에요.`; understand에 긴 문단 8개(스크롤 발생용).
  - p4: `(1)`~`(3)` 세 항목, 모델 `{'answer':'2','mode':'ambiguous'}`, solve 문단은 `a 맞아요…`, `b 틀려요…`, `c 틀려요…`(라벨 불일치).
  - 모델 스크립트는 원본 `</section>` 뒤. p1·p2는 모델에 넣지 않는다.

- [ ] **Step 1: 브라우저 수용 테스트에 실패 단언 추가** (각 viewport·theme 루프 안)

```python
page.goto(url+'#p3',wait_until='networkidle')
if width>=1024:
    assert page.locator('#panel-right .probs [data-problem-for="p3"]').is_visible()
    assert page.locator('#p3 > [data-problem-for]').count()==0
    assert page.locator('#panel-right [role=tab][data-tab="problem"]').get_attribute('aria-selected')=='true'
    page.locator('#panel-right [data-tab="summary"]').click()
    assert page.locator('#panel-right .sums .summary-group').first.is_visible()
    page.locator('#panel-right [data-tab="problem"]').click()
else:
    toggle=page.locator('#p3 .problem-toggle')
    assert toggle.get_attribute('aria-expanded')=='false' and not page.locator('#p3 [data-problem-for="p3"]').is_visible()
    toggle.click();assert page.locator('#p3 [data-problem-for="p3"]').is_visible() and toggle.inner_text()=='문제 접기'
assert page.locator('#p3 [data-explanation="understand"]').is_visible()
```

viewport 목록에 `(1024,768)`을 추가한다(1024는 wide). 기존 `#panel-right .summary-group` 단언은 요약 탭 클릭 뒤로 옮긴다. 기존 375 흐름의 `#toggle-right`(서랍)는 요약 서랍을 연다.

- [ ] **Step 2: 실패 확인** — `python3 …/browser_acceptance.py <scratch>/acc-t3` → AssertionError(`.probs` 없음).

- [ ] **Step 3: 템플릿 구현**

- `data-panels="explain"`, `PREF`는 자연히 `od-panels:explain`. `docked()`는 `kind==='explain'`일 때 `{ left: pref.left ?? roomyMq.matches, right: pref.right ?? true }`.
- 패널 머리: 제목 h2를 visually-hidden "문제와 요약"으로 두고 탭 두 개, `#sum-for`·`#sum-empty`는 요약 탭 패널 안으로.
- `setupExplain()`: `setupNote`의 `.sum` 이동과 읽음 표시 로직을 그대로 포함. pane을 `{id: node}` 맵으로 모으고 `mountPanes()`가 `wideMq.matches`면 `.probs`에 append(현재 id만 보임), 아니면 각 article의 `.panel-meta` 뒤에 토글 버튼+pane(기본 `hidden`, 문항별 펼침 상태는 메모리 유지). 탭 상태 `store.get('bio-problem-explain-tab','problem')`. `od:screen`에서 현재 pane만 보이게 하고 패널 스크롤 0.
- `if (kind === 'explain') setupExplain();` 기존 `note` 분기는 제거.
- CSS: 탭(밑줄형, 높이 `var(--tap)`), `.problem-toggle`(`.solved-btn`과 같은 외곽), pane 안 그림 `max-width:100%`.

- [ ] **Step 4: 통과 확인** — 수용 테스트 PASS(모든 viewport·theme, 콘솔·외부 요청·넘침 0). 단위 테스트 PASS.

- [ ] **Step 5: 문서** — verification.md `browser` 항목에 "1280·1024에서 오른쪽 문제 탭이 기본으로 보이고 요약 탭 전환이 되는지, 375에서 '문제 보기' 토글이 해설 위에 있는지" 추가. SKILL.md 6단계에 "문제는 넓은 화면에서 오른쪽 문제 탭, 좁은 화면에서 해설 위 접힘 버튼으로 표시된다" 한 문장.

- [ ] **Step 6: provenance 재생성 후 커밋** — `feat(bio-problem-explain): move problem into right panel tab`

---

### Task 4: 클릭형 보기, 해설 이동, 그림 확대

**Files:**
- Modify: `SKILL/assets/note-template.html` (`setupExplain` 안 보기 로직, CSS 인라인 복사)
- Modify: `SKILL/tests/browser_acceptance.py`
- Modify: `SKILL/references/authoring.md` (보기 판정 절), `SKILL/references/verification.md` (browser 항목)

**Interfaces:**
- Consumes: `script#explain-choice-model`(Task 2), `.probs`/`problem-toggle`/`mountPanes()`/`curId`(Task 3), fixture p3·p4(Task 3).
- Produces: `button.review-choice[data-choice-id][data-result=""|"correct"|"incorrect"|"intended"][aria-pressed]`, `span.review-badge`, `p.review-status[aria-live=polite]`, `button.review-reset`("다시 고르기"), 대상 요소 `.is-target`, 그림 시트 `dialog.sheet.figure-sheet`.

- [ ] **Step 1: 실패 단언 추가** (Task 3 블록 뒤, 넓은 화면은 패널, 좁은 화면은 토글을 연 뒤의 pane을 `pane`으로)

```python
pane=page.locator('[data-problem-for="p3"]')
assert pane.locator('.review-choice').count()==5
assert pane.locator('.review-badge:visible').count()==0                       # 클릭 전 정답 숨김
pane.locator('.review-choice[data-choice-id="5"]').click();page.wait_for_timeout(100)
assert pane.locator('[data-choice-id="5"]').get_attribute('data-result')=='incorrect'
assert pane.locator('[data-choice-id="3"]').get_attribute('data-result')=='correct'
assert '정답' in pane.locator('[data-choice-id="3"] .review-badge').inner_text()
target=page.locator('#p3 [data-explanation="solve"] p.is-target')
assert target.count()==1 and target.inner_text().startswith('(5)')
assert target.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
page.set_viewport_size({'width':900 if width>=1024 else 1280,'height':height});page.wait_for_timeout(150)
assert page.locator('[data-problem-for="p3"] [data-choice-id="5"]').get_attribute('data-result')=='incorrect'
page.set_viewport_size({'width':width,'height':height})
page.locator('[data-problem-for="p3"] .review-reset').click()
assert page.locator('[data-problem-for="p3"] [data-result="correct"]').count()==0
page.goto(url+'#p4');  # 좁은 화면이면 토글을 연다
p4=page.locator('[data-problem-for="p4"]');p4.locator('[data-choice-id="1"]').click()
assert '출제 의도상 답' in p4.locator('[data-choice-id="2"] .review-badge').inner_text()
assert page.locator('#p4 [data-explanation="solve"] h4.is-target').count()==1
page.goto(url+'#p1');assert page.locator('[data-problem-for="p1"] .review-choice').count()==0
```

넓은 화면에서 p2의 패널 그림을 클릭하면 `dialog.figure-sheet[open] img`가 보이고 Escape로 닫히는 단언을 추가한다(fixture p2의 `그림.png`를 문제 쪽에도 넣는다).

- [ ] **Step 2: 실패 확인** — 수용 테스트 → AssertionError(`.review-choice` 0개).

- [ ] **Step 3: 구현**

- 모델을 `JSON.parse`(실패 시 `{}`). 모델이 있는 pane마다 첫 `.choices` 직계 li 수가 `options.length`와 같을 때만 li 자식 노드를 `button.review-choice` 안으로 옮기고 배지 span을 붙인다. 아니면 건너뛴다.
- 클릭: 메모리 `Map(id → 선택 id)` 갱신 후 `paint(id)`가 data-result·배지·상태 문장(정답 "정답이에요." / 오답 "정답이 아니에요. 해설에서 판정 이유를 확인해요." / ambiguous "출제 의도상 답을 표시했어요.")·리셋 표시를 칠한다. `mountPanes()`는 노드를 옮기기만 하므로 상태가 남는다.
- 이동: Global Constraints의 정규식으로 대상 찾기 → `.content` 스크롤러에 `scrollTop += rect.top - scrollerRect.top - scroller.clientHeight/4` → `is-target` 1600ms 후 제거. reduced-motion이면 transition 없음.
- 그림: pane 안 `img` 클릭 → 한 번 만든 `dialog.sheet.figure-sheet`에 같은 `src`·`alt`로 `showModal()`. 바깥 클릭·Escape로 닫힘.
- CSS: `bio-review-pack/assets/review-interaction.css`에서 `.review-choice`, `[data-result]` 상태, `.review-badge`, `.review-status`, `.review-reset` 규칙을 그대로 복사(색 토큰은 템플릿 토큰과 이미 같은 이름). `.is-target { outline: 2px solid var(--accent); outline-offset: 4px; border-radius: var(--radius); }`.

- [ ] **Step 4: 통과 확인** — 수용 테스트 PASS(1280/1024/375 × light/dark), 단위 테스트 PASS.

- [ ] **Step 5: 문서** — authoring.md 보기 판정 절에 "판정 문단은 보기 라벨(`(n)`, `A`, `ㄱ`)로 시작해요. 오른쪽 문제 패널에서 보기를 누르면 이 문단으로 이동해요." 추가. verification.md `browser`에 "오답 하나·정답 하나를 눌러 판정 문단으로 이동하는지, 그림 확대" 추가.

- [ ] **Step 6: provenance 재생성 후 커밋** — `feat(bio-problem-explain): clickable choices jump to verdicts`

---

### Task 5: rerender 명령

**Files:**
- Modify: `SKILL/scripts/mpe_cli.py` (서브커맨드, `rerender` 함수)
- Modify: `SKILL/SKILL.md` (실행 절 끝에 "레이아웃만 바뀐 기존 발행분 재발행" 절)
- Test: `SKILL/tests/test_cli.py`

**Interfaces:**
- Consumes: `extract(repo, target, run) -> int`, `load_run(run)`, `build(item, fragments)`, `mpe_render.names(pack) -> (stem, fig_name, data_name)`, `payload_hash(pack, fragments)`.
- Produces: `rerender(repo: Path, target: str, run: Path) -> int` (0 성공, 1 실패) and CLI `rerender --repo --target --run`.

- [ ] **Step 1: 실패 테스트 작성** (`test_cli.py`; fixture는 기존 `test_cli_round_trip…`처럼 extract → 조각 작성 → build → `approved()` → publish로 한 번 발행한 저장소)

```python
def test_rerender_reuses_content_reviews(tmp_path):
    repo,source=published_pack(tmp_path)              # 이 파일에 추가하는 헬퍼
    result=call('rerender','--repo',repo,'--target',source,'--run',tmp_path/'run2')
    assert result.returncode==0,result.stderr
    folder=next(p for p in (tmp_path/'run2').iterdir() if p.is_dir())
    review=json.loads((folder/'review.json').read_text())
    assert review['content']['status']=='pass' and review['independent']['status']=='pass'
    assert review['source_visual']['status']=='not_run' and review['browser']['status']=='not_run'
    assert {p.name for p in (folder/'explanations').glob('*.html')}=={'p1.html'}
    assert (folder/'evidence').is_dir() and any((folder/'evidence').iterdir())
    assert 'source_visual·browser 재검토 필요' in result.stdout

def test_rerender_changed_source_keeps_reviews_unrun(tmp_path):
    repo,source=published_pack(tmp_path)
    source.write_text(source.read_text().replace('함수 결과를 구해요.','함수 결과를 다시 구해요.'))
    result=call('rerender','--repo',repo,'--target',source,'--run',tmp_path/'run2')
    folder=next(p for p in (tmp_path/'run2').iterdir() if p.is_dir())
    review=json.loads((folder/'review.json').read_text())
    assert review['content']['status']=='not_run'
    assert '입력 변경: 네 검토 모두 다시 필요' in result.stdout

def test_rerender_without_published_fragments_fails(tmp_path):
    repo=tmp_path/'repo';source=source_file(repo)
    result=call('rerender','--repo',repo,'--target',source,'--run',tmp_path/'run')
    assert result.returncode==1 and '발행된 조각 없음' in result.stderr
```

`published_pack`은 발행 전 `RUN/<item>/evidence/note.txt`를 하나 써서 발행 자료 폴더에 evidence가 남게 한다.

- [ ] **Step 2: 실패 확인** — `…/tests/test_cli.py -q` → FAIL(`invalid choice: 'rerender'`).

- [ ] **Step 3: 구현** — `extract` 실패 시 1 반환. 각 item: 발행 자료 폴더 `pack.path.parent / data_name`의 `fragments/*.html` 집합이 문항 id 집합과 다르면 stderr `발행된 조각 없음/불일치: 정상 저작 절차를 쓰세요` 후 실패. 같으면 `explanations/`로, `evidence/`는 `folder/evidence/`로 복사 → `build(item, fragments)` → 발행 `validation.json`의 `input_hash == payload_hash(pack, fragments)`면 `review.json`에 `references`·`content`·`independent`를 덮어쓰고 stdout `rerender: content·independent 재사용, source_visual·browser 재검토 필요`, 아니면 `rerender: 입력 변경: 네 검토 모두 다시 필요`.

- [ ] **Step 4: 통과 확인** — 단위 테스트 PASS.

- [ ] **Step 5: SKILL.md** — 절 추가: 레이아웃·템플릿만 바뀐 경우 팩마다 새 RUN으로 `rerender` → `check` → source_visual·browser 실제 검토 → `publish`. 입력이 바뀌었다고 나오면 1~7단계 전체. `all`이면 최신 → 0901 순으로 팩마다 반복하고 결과 표로 보고.

- [ ] **Step 6: provenance 재생성 후 커밋** — `feat(bio-problem-explain): add rerender for layout-only republish`

---

### Task 6: 기존 12팩 재발행

**Files:**
- Modify(발행 산출물): `복습노트/<range>/문제설명_<range>_<slug>.html/.md`, `figures_문제설명_*`, `자료_문제설명_*` — 1013, 1008, 1006, 1001, 0929, 0922, 0917, 0915, 0910, 0908, 0903, 0901

**Interfaces:**
- Consumes: Task 5 `rerender`, 기존 `check`/`publish`, verification.md의 source_visual·browser 기준(Task 3·4 갱신본).

- [ ] **Step 1: 팩마다 rerender·check** — `RUN=<scratchpad>/bio-problem-explain/rerender-<range>/`, `python3 SKILL/scripts/mpe_cli.py rerender --repo <REPO> --target <복습문제 절대경로> --run $RUN` 후 `check --run $RUN`. Expected: `content·independent 재사용` 출력과 `check: machine PASS`. "입력 변경"이 나온 팩은 이 Task에서 보류하고 결과 표에 기록한다(전체 재저작은 별도 요청).
- [ ] **Step 2: source_visual 검토** — stage HTML을 로컬 http 서버로 열고 문항마다 오른쪽 pane의 질문·보기·그림이 원 복습문제 카드와 같은지 확인. `evidence/source-visual-<range>.md`에 결과를 쓰고 `review.json`의 `source_visual`을 pass로 기록(reviewer·evidence 비어 있지 않게).
- [ ] **Step 3: browser 검토** — 1280×900·375×812, light/dark에서 verification.md `browser` 전 항목. 콘솔·외부 요청·넘침 0. `evidence/browser-<range>.md` 기록 후 pass.
- [ ] **Step 4: 발행** — `publish --run $RUN`. Expected: `publish:` 경로와 백업 경로 출력.
- [ ] **Step 5: 결과 표 보고** — range · slug · 문항 수 · 발행/보류 · 보류 이유 · HTML 경로.
- [ ] **Step 6: 커밋**

```bash
git add 복습노트/*/문제설명_* 복습노트/*/figures_문제설명_* 복습노트/*/자료_문제설명_*
git commit -m "docs(notes): republish problem explanations with problem panel"
```
