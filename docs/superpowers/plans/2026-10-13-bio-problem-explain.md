# bio-problem-explain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 생명과학 복습문제 HTML로 문항별 입문 문제설명 HTML/MD를 만드는 `bio-problem-explain` 스킬을 이식하고, `bio-review-pack`이 이를 호출하게 하며, 기존 11개 팩에 문제설명을 백필한다.

**Architecture:** 자구알 `ds-problem-explain`(ajou-jagual `d631a5a`)을 통째로 복사해 생명과학 문자열·소문항 판별·`all` 대상만 고친다. 결정적 실행기(extract → build → check → publish)는 그대로 두고, 저작·독립 검산·실검토는 에이전트가 SKILL.md/references 규칙대로 수행한다. bio-review-pack은 문서(SKILL.md, references)만 바뀐다.

**Tech Stack:** Python 3.10+ 표준 라이브러리(실행기), pytest(이식 스킬 테스트, `uv run --with pytest`), unittest(bio-review-pack 테스트), 로컬 http.server + 내장 브라우저(실검토).

**Spec:** `docs/superpowers/specs/2026-10-13-bio-problem-explain-design.md`

## Global Constraints

- 원본: `/Users/hyunjun_macbook_pro/Documents/Univ/자구알/.agents/skills/ds-problem-explain`, 커밋 `d631a5a573a32c9406b139e319bc9c7c2d328098`, 저장소 `https://github.com/jjundev/ajou-jagual.git`.
- 실행 중 자구알·머신러닝기초 checkout을 참조하지 않는다(복사본만으로 동작).
- `assets/note-template.html`, `assets/template-provenance.json`, `assets/vendor/**`는 바이트 그대로 복사한다.
- 산출 파일명: `문제설명_<range>_<slug>.html/.md`, `figures_문제설명_<range>_<slug>/`, `자료_문제설명_<range>_<slug>/`.
- 제목 `생명과학 복습 {range} 문제설명`, 읽음 상태 키 `bio-problem-explain-{profile}-{range}-{slug}`.
- 원 복습문제·정리노트·MD·그림·`.pack/`·`풀이기록/`은 수정하지 않는다. 정리노트·복습문제에 링크를 넣지 않는다.
- 발행 게이트: `source_visual`/`content`/`independent`/`browser` 네 검토가 실제 수행으로 `pass`일 때만 publish. `lite`에서도 생략하지 않는다.
- 저작 에이전트: 문항 10개당 1명, opus(`lite`면 sonnet; 비-Claude는 sol/luna).
- 백필 순서: 1008 → 1006 → 1001 → 0929 → 0922 → 0917 → 0915 → 0910 → 0908 → 0903 → 0901, 전체 문항(partC 포함).
- 커밋은 이 계획의 커밋 단계에서만, 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. 푸시하지 않는다.

## Review Focus

1. macOS NFD 파일명/폴더명의 팩 → `all`과 날짜 대상 모두 찾아야 한다 (Task 2 `test_all_finds_nfd_pack`).
2. 보기 안의 "설명하/구하/?"와 ㄱㄴㄷ 진술 목록 → 소문항 오탐 없이 `main` (Task 2 `test_choices_never_subparts`, `test_giyeok_statements_single`).
3. 팩 폴더에 남은 백업 사본(같은 range의 복습문제 HTML 2개) → `all`이 조용히 하나를 고르지 않고 "여러 후보"로 멈춘다 (Task 2 `test_all_rejects_duplicate_range`).
4. 문제설명 재발행(augment 후 재생성) → 기존 설명만 백업·교체, `풀이기록/`·복습문제·정리노트 바이트 불변 (Task 1 `test_republish_preserves_pack_files`).
5. 카드 그림(`figures_<range>/…png`)이 있는 문항 → 문제설명 페이지에서 그림이 로드된다 (Task 5 브라우저 검토 항목, Task 1 기존 `acceptance_pack` 그림 테스트 유지).

---

### Task 1: 스킬 이식과 생명과학 식별자

**Files:**
- Create: `.agents/skills/bio-problem-explain/` (자구알 `ds-problem-explain`에서 `__pycache__` 제외 전체 복사)
- Create: `.claude/skills/bio-problem-explain` (심볼릭 링크 → `../../.agents/skills/bio-problem-explain`)
- Create: `.agents/skills/bio-problem-explain/scripts/port_provenance.py`
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_render.py:150,156`
- Modify: `.agents/skills/bio-problem-explain/assets/port-provenance.json` (재생성)
- Test: `.agents/skills/bio-problem-explain/tests/test_render.py`, `test_skill_files.py`, `test_publish.py`, `tests/test_bio_review_pack_entrypoint.py`

**Interfaces:**
- Produces: `python3 .agents/skills/bio-problem-explain/scripts/mpe_cli.py {extract --repo R --target T --run RUN | build --run RUN | check --run RUN | publish --run RUN}` (자구알과 동일).
- Produces: `python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py` — `assets/port-provenance.json`을 다시 쓴다. 형식: `{"source_repository", "source_commit", "files": [{"source_path", "source_sha256", "destination", "destination_sha256", "change_reason"}]}`. `source_path`는 원본 스킬 기준 상대경로(원본에 없는 파일은 `null`), `source_sha256`은 `git -C <자구알> show d631a5a:<path>` 바이트의 해시, `change_reason`은 해시가 같으면 `"unchanged pinned copy"`, 다르면 `"biology course adaptation"`, 원본 없으면 `"local addition"`. `__pycache__`와 `port-provenance.json` 자신은 제외. 원본 저장소 경로는 `--source` 인자(기본값 위 Global Constraints 경로)로 받는다.

- [ ] **Step 1: 복사·링크**

```bash
cp -R /Users/hyunjun_macbook_pro/Documents/Univ/자구알/.agents/skills/ds-problem-explain /Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.agents/skills/bio-problem-explain
find /Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.agents/skills/bio-problem-explain -name __pycache__ -prune -exec rm -r {} +
ln -s ../../.agents/skills/bio-problem-explain /Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.claude/skills/bio-problem-explain
```

- [ ] **Step 2: 실패하는 테스트로 바꾸기**
  - `test_render.py::test_legacy_statement_rendered_once`: `'bio-problem-explain-review-0917-Recursion' in text`, `'생명과학 복습 0917 문제설명' in text`, `'자료구조' not in text`.
  - `test_skill_files.py::test_claude_link_and_provenance`: 링크 `.claude/skills/bio-problem-explain`, `data['source_commit']=='d631a5a573a32c9406b139e319bc9c7c2d328098'`, 모든 `files` 항목의 `destination_sha256`이 현재 파일 해시와 같고, `assets/` 항목은 `source_sha256==destination_sha256`. `local_overrides` 분기는 제거.
  - `test_publish.py::test_republish_preserves_pack_files`(신규): 같은 팩 폴더에 `정리노트_0917_Recursion.html`, `풀이기록/x.json`을 만든 뒤 publish를 두 번 실행(두 번째는 조각 문구 변경 후 build) → 복습문제·정리노트·`풀이기록/x.json` 바이트 불변, 두 번째 publish의 backup 폴더에 첫 번째 `문제설명_0917_Recursion.html`이 있다. 기존 `test_publish.py`의 publish 헬퍼 호출 방식을 따른다.
  - `tests/test_bio_review_pack_entrypoint.py::test_problem_explain_entry`(신규): `os.readlink(ROOT/".claude/skills/bio-problem-explain") == "../../.agents/skills/bio-problem-explain"`, `(ENTRY/"SKILL.md").is_file()`.

- [ ] **Step 3: 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q`
Expected: `test_legacy_statement_rendered_once`, `test_claude_link_and_provenance` FAIL.

- [ ] **Step 4: 구현**
  - `mpe_render.py:150` 제목 → `f'생명과학 {"과제" if pack.profile == "homework" else "복습"} {pack.range} 문제설명'`; `:156` 키 접두 → `bio-problem-explain-`.
  - `port_provenance.py` 작성 후 실행. 과제(HOMEWORK) 분기는 그대로 둔다(이식 차이 최소화; 입력은 `과제 입력 미지원`으로 이미 거부됨).

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q && python3 -m unittest tests.test_bio_review_pack_entrypoint`
Expected: 전부 PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/bio-problem-explain .claude/skills/bio-problem-explain tests/test_bio_review_pack_entrypoint.py
git commit -m "feat(bio-problem-explain): port problem explanation runner from ds"
```

### Task 2: 객관식 소문항 판별과 `all` 대상

**Files:**
- Modify: `.agents/skills/bio-problem-explain/scripts/mpe_source.py` (`resolve_sources`, `subparts`)
- Modify: `.agents/skills/bio-problem-explain/tests/helpers.py` (`choice_source_file` 추가)
- Test: `.agents/skills/bio-problem-explain/tests/test_source.py`

**Interfaces:**
- Consumes: Task 1의 복사본.
- Produces: `resolve_sources(repo: Path, target: str | None) -> tuple[Path, ...]` — `target == 'all'`이면 `복습노트/` 아래 모든 복습문제 HTML을 끝 날짜 내림차순으로 반환, range당 HTML이 둘 이상이면 `ExplainError('여러 후보…')`, 0개면 `ExplainError('대상 없음: all')`. 그 밖의 대상은 기존 동작 유지.
- Produces: `subparts(ask: str, original: str) -> tuple[str, ...]` — class에 `choices` 또는 `options`가 있는 목록과 그 하위는 판별에서 제외.
- Produces (test helper): `choice_source_file(repo, date='0915', slug='Cellular_Respiration', choices=(...)) -> Path` — `<ul class="choices">` 보기 카드 1개짜리 복습문제 HTML.

- [ ] **Step 1: 실패하는 테스트 작성**
  - `test_choices_never_subparts`: `subparts('<p>옳은 설명은 무엇인가요?</p><ul class="choices"><li>(1) 전자가 흐른다.</li><li>(5) 이 현상을 설명하는 이론은 화학삼투설이다.</li></ul>', '') == ('main',)`; 같은 내용을 `ol class="choices"`로도.
  - `test_giyeok_statements_single`: `subparts('<p>옳은 것만 고른 것은?</p><ul><li>ㄱ. 값을 구하는 효소이다.</li><li>ㄴ. 설명하는 그림이다.</li></ul><ul class="choices"><li>(1) ㄱ</li><li>(2) ㄴ</li></ul>', '') == ('main',)` — ㄱㄴㄷ 목록이 `(a)` 표지 없이 질문형 동사를 가지면 현재 "모호함"으로 실패하므로, `ㄱ.`/`ㄴ.`/`ㄷ.`로 시작하는 항목만으로 된 목록도 제외 대상에 포함한다.
  - `test_choice_card_extracts`: `load_source(choice_source_file(tmp_path), tmp_path).problems[0].subparts == ('main',)`, 보기 HTML이 `conditions_html`에 보존.
  - `test_all_newest_first`: 0901·0922·1008 팩 생성 → `[p.parent.name for p in resolve_sources(tmp_path,'all')] == ['1008','0922','0901']`.
  - `test_all_finds_nfd_pack`: NFD 폴더명·파일명 팩 포함 시 `all` 결과에 포함.
  - `test_all_rejects_duplicate_range`: 같은 range에 slug 두 개 → `ExplainError` match `여러 후보`.
  - `test_all_empty`: 팩 없음 → `ExplainError` match `대상 없음`.
  - 기존 `test_invalid_target` 파라미터는 유지(`all`은 넣지 않음).

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_source.py -q`
Expected: 신규 7개 FAIL(소문항 테스트는 "소문항 질문 경계 모호함", `all`은 "잘못된 대상").

- [ ] **Step 3: 구현**
  - `subparts`의 `lists` 수집에서 `{'choices','options'} & set(n.classes)`인 목록과 그런 조상을 가진 목록, 모든 `li` 텍스트가 `^\s*[ㄱ-ㅎ]\.`인 목록을 건너뛴다. `marked` 수집에도 같은 조상 제외를 적용한다.
  - `resolve_sources`: `target == 'all'` 분기를 날짜 정규식 검사 전에 둔다. 기존 `by_range` 중복 검사를 재사용하고 정렬 키는 `(range의 끝 날짜, nfc(name))` 내림차순.

- [ ] **Step 4: 통과 확인 + 실데이터 탐침**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q`
Expected: 전부 PASS.

Run (읽기 전용 탐침, scratchpad에만 씀):
```bash
P=<scratchpad>/probe-all; rm -rf "$P"; python3 .agents/skills/bio-problem-explain/scripts/mpe_cli.py extract --repo /Users/hyunjun_macbook_pro/Documents/Univ/생명과학 --target all --run "$P"
```
Expected: 종료 코드 0, `extract:` 줄 11개(0915 포함), `git status --short 복습노트` 출력 없음.

- [ ] **Step 5: provenance 재생성 후 Commit**

```bash
python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py
git add .agents/skills/bio-problem-explain
git commit -m "fix(bio-problem-explain): ignore choice lists in subparts and add all target"
```

### Task 3: 생명과학 저작·검토 규칙과 SKILL.md

**Files:**
- Modify: `.agents/skills/bio-problem-explain/SKILL.md` (전면 개정)
- Modify: `.agents/skills/bio-problem-explain/references/authoring.md` (전면 개정)
- Modify: `.agents/skills/bio-problem-explain/references/verification.md`
- Test: `.agents/skills/bio-problem-explain/tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 1·2의 CLI(`all` 포함).
- Produces: 스킬 호출 `/bio-problem-explain [MMDD | MMDD-MMDD | all | HTML경로]`, RUN 규약 `<scratchpad>/bio-problem-explain/<range>/`(scratchpad 없으면 `/tmp/bio-problem-explain/<range>/`). Task 4가 이 SKILL.md의 절 이름 "실행" 1~7단계를 참조한다.

- [ ] **Step 1: 실패하는 테스트 작성** (`test_skill_files.py`)
  - `test_frontmatter`: `yaml.safe_load` 없이 정규식 `---\nname: (.+)\ndescription: (.+)\n---\n`; name `bio-problem-explain`; description에 `생명과학`, `문제설명`, `/bio-problem-explain` 포함, 1024자 이하, 콜론+공백(`: `)이 있으면 큰따옴표로 감싸져 있음.
  - `test_no_ds_leftovers`: SKILL.md·references/*.md에 `자료구조|자구알|강의록|from_the_past|printf|C 코드|ds-problem-explain|ds-review-pack|Codex 패널` 없음.
  - `test_bio_sources_named`: SKILL.md에 `강의노트/`, `교과서/생명과학_기초와_응용_2판/`, `23, 24 소스/`, `웹과제/`, `.pack/key-check.md`, `all` 포함.
  - `test_authoring_bio_rules`: authoring.md에 일곱 `data-explanation` 이름이 표 순서대로 있고, `보기`, `ㄱㄴㄷ`, `부정형`, `disputed` 포함.
  - `test_independent_definition`: verification.md에 `정답을 보지 않은`, `key-check.md` 포함.
  - `test_referenced_files_exist`: SKILL.md가 가리키는 `references/*.md`, `scripts/*.py`, `assets/*.json`이 모두 존재.

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_skill_files.py -q`
Expected: 신규 테스트 FAIL.

- [ ] **Step 3: 문서 작성** — 자구알 원문의 구조·게이트 문장을 유지하고 아래만 바꾼다.
  - SKILL.md: 대상(MMDD·기간·`all`·경로·최신), 참조 자료 목록(Spec 그대로), 저작 병렬 규칙(문항 10개당 1명, opus/sonnet, 서브에이전트 없으면 차례로), 독립 검산 에이전트 분리, 백필 시 팩별 결과 표 보고, 산출 위치·읽음 상태 키(`bio-problem-explain-review-<range>-<slug>`), 이식 기록 링크. 경로 약속은 bio-review-pack의 "경로 약속" 문단 형식(절대 경로, `cd` 금지).
  - authoring.md: recall 예시를 생명과학(예: "H⁺가 ATP 합성효소를 거치지 않는다" → 화학삼투)으로 교체, solve는 보기마다 `<p>(n) 맞아요/틀려요 + 근거 개념</p>`, ㄱㄴㄷ형은 진술별 판정 후 조합, 부정형("틀린 것", "아닌 것")은 understand에서 질문 방향을 굵게, verify는 소거·교과서 쪽 대조·교배표 재계산 중 하나 이상. "C 코드와 원자료 충돌" 절 → "원자료 충돌": 답안지·기출 합본·웹과제·`.pack/key-check.md`가 다르면 disputed. 수식·여백 절은 그대로.
  - verification.md: `source_visual` 대조 대상 → 기출 합본 PDF 쪽·웹과제 questions.json·교과서 쪽. `independent` → 정답을 보지 않은 별도 에이전트가 정리노트·교과서·강의노트만으로 다시 풀어 일치, `method`는 주로 `qualitative`(유전 계산은 `exact`), `.pack/key-check.md`와 대조.

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests -q`
Expected: 전부 PASS.

- [ ] **Step 5: provenance 재생성 후 Commit**

```bash
python3 .agents/skills/bio-problem-explain/scripts/port_provenance.py
git add .agents/skills/bio-problem-explain
git commit -m "docs(bio-problem-explain): adapt authoring and review rules to biology"
```

### Task 4: bio-review-pack 연동

**Files:**
- Create: `.agents/skills/bio-review-pack/references/problem-explain.md`
- Modify: `.agents/skills/bio-review-pack/SKILL.md` (frontmatter description, 산출물, 0단계, 4단계 백업 스니펫 `want`, 8b 신설, 9단계 보고 형식, 보강 모드 A5b·A6, 오류 처리 표)
- Test: `.agents/skills/bio-review-pack/tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 3 SKILL.md의 "실행" 1~7단계, CLI 경로 `<REPO>/.agents/skills/bio-problem-explain/scripts/mpe_cli.py`.
- Produces: `references/problem-explain.md` — 자구알 `ds-review-pack/references/problem-explain.md`의 생명과학판(EXPLAIN_SKILL = SKILL의 형제 `bio-problem-explain` 원본 절대 경로, ABS_REVIEW = 최종 복습문제 HTML 절대 경로, EXPLAIN_RUN = `<scratchpad>/bio-problem-explain/<range>/`, 단계 1~7, 실패 시 "복습팩 생성됨 / 문제설명 보류").

- [ ] **Step 1: 실패하는 테스트 작성** (unittest, 기존 클래스에 추가)
  - `test_problem_explain_step`: 본문에 `### 8b. 문제설명`이 `### 8.`과 `### 9.` 사이에 있고 `references/problem-explain.md`를 가리킴.
  - `test_sibling_check_in_prepare`: 0단계 본문에 `bio-problem-explain/SKILL.md`와 `scripts/mpe_cli.py` 존재 확인 문장.
  - `test_augment_reexplains`: `## 보강 모드` 본문에 `**A5b.`와 `references/problem-explain.md`.
  - `test_report_has_explain_line`: 9단계 보고 블록에 `- 문제설명:`과 `복습팩 생성됨 / 문제설명 보류`.
  - `test_lite_keeps_explain_review`: `lite` 설명 줄에 `문제설명` 검토를 생략하지 않는다는 문구.
  - `TestBackupSnippet.test_backs_up_explanations`: 팩 폴더에 `문제설명_0922_X.html`, `figures_문제설명_0922_X/a.png`, `자료_문제설명_0922_X/manifest.json`, `풀이기록/y.json`을 만들고 백업 → 앞의 세 개는 백업에 있고 `풀이기록`은 없음.
  - `test_no_ml_leftovers`는 새 reference 파일에도 자동 적용됨(머신러닝 단어 쓰지 않기).

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests -p 'test_skill_files.py'`
Expected: 신규 6개 FAIL.

- [ ] **Step 3: 구현**
  - description에 `문제설명` 추가(따옴표 규칙 유지).
  - 산출물 줄: `문제설명_<range>_<slug>.html`, `.md` 세 개, 설명 소유 `figures_문제설명_*`·`자료_문제설명_*`.
  - `lite` 줄: "문제설명 저작·독립 검산·실자료 검토·브라우저 검증은 생략하지 않는다."
  - 0단계 1에 형제 스킬 확인을 추가(없으면 경로와 오류를 보고하고 멈춤).
  - 4단계 백업 스니펫 `want`의 prefix 튜플에 `f"문제설명_{r}_", f"figures_문제설명_{r}_", f"자료_문제설명_{r}_"` 추가. 오류 처리 표 "같은 range의 팩이 이미 있음" 행에도 반영.
  - `### 8b. 문제설명`: 8단계 OK 뒤 최종 복습문제 HTML 절대 경로로 `references/problem-explain.md` 실행. 5~8단계 미해결이 있으면 실행하지 않고 보류로 보고.
  - 9단계 보고 형식에 `- 문제설명: 발행/보류 · N문항 · HTML·MD · EXPLAIN_RUN · 백업 · 네 검토 결과 · 보류 이유` 줄과 제목 대체 문구, 커밋 제안은 기존 `git add 복습노트/<range>` 그대로(설명 파일 포함됨).
  - 보강 모드: `**A5b. 문제설명**` — A5 뒤 같은 절차로 팩 전체 재생성. A6 보고에 문제설명 줄.
  - 오류 처리 표에 "해설 저작·검산·검토·발행 실패 → 검증된 복습팩과 이전 해설 보존, '복습팩 생성됨 / 문제설명 보류' 보고, 다른 팩 계속" 행.

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s .agents/skills/bio-review-pack/tests && python3 -m unittest discover -s tests -p 'test_bio_review_pack_entrypoint.py'`
Expected: 전부 OK.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/bio-review-pack
git commit -m "feat(bio-review-pack): call bio-problem-explain after md conversion and augment"
```

### Task 5: 시범 발행 — 1008 팩

최신 팩이자 21문항으로 가장 작은 축에 속해 백필 순서의 첫 팩으로 실전 절차를 검증한다.

**Files:**
- Create: `복습노트/1008/문제설명_1008_Gene_Regulation_and_DNA_Cloning.html/.md`, `figures_문제설명_1008_…/`, `자료_문제설명_1008_…/`

**Interfaces:**
- Consumes: `/bio-problem-explain 1008` (Task 3 SKILL.md 절차 전체).

- [ ] **Step 1:** `/bio-problem-explain 1008`을 SKILL.md 1~7단계대로 실행한다(저작 에이전트 3명 병렬, 별도 독립 검산 에이전트).
- [ ] **Step 2: 검증**
  - `check` 출력 `PASS`, `review.json` 네 검토 `pass`.
  - 브라우저: 1280×900·375×812 × light/dark에서 콘솔 오류 0, KaTeX 오류 0, 외부 요청 0, `document.documentElement.scrollWidth <= innerWidth`, 21문항 목차·이전/다음·요약 동작, 카드 그림(있으면) 로드.
  - `git status --short 복습노트/1008` 출력에 새 문제설명 파일만 있음(복습문제·정리노트·`.pack` 변경 없음).
- [ ] **Step 3: Commit**

```bash
git add 복습노트/1008
git commit -m "docs(notes): add 1008 problem explanations"
```

### Task 6: 나머지 10개 팩 백필

**Files:**
- Create: `복습노트/{1006,1001,0929,0922,0917,0915,0910,0908,0903,0901}/문제설명_*` 및 소유 폴더

**Interfaces:**
- Consumes: Task 5와 같은 절차.

- [ ] **Step 1:** Global Constraints의 순서대로 팩마다 `/bio-problem-explain <MMDD>`를 실행한다. 팩마다 새 RUN. 보류된 팩은 이유를 기록하고 다음 팩으로 넘어간다.
- [ ] **Step 2: 팩마다 검증** — Task 5 Step 2와 같은 기준. 추가로 `git status --short 복습노트/0922/풀이기록 복습노트/0929/풀이기록` 출력 없음.
- [ ] **Step 3: 팩마다 Commit** — `git add 복습노트/<MMDD> && git commit -m "docs(notes): add <MMDD> problem explanations"` (보류된 팩은 커밋하지 않음).
- [ ] **Step 4: 최종 보고** — 팩 | 문항 수 | 발행/보류 | 보류 이유 | RUN 표 하나.
