# 웹과제 문제은행 통합 최종 리뷰

기준 branch는 `codex/web-question-bank`, Task 8 시작 base는 `1be8126`이다. 이번 단계는 기존 MMDD 노트·가이드, bank JSON, raw 캡처, SVG를 다시 만들거나 수정하지 않고 앞으로 생성할 노트의 내용 규칙과 두 canonical skill 계약을 연결했다.

## 전달 범위

- 문제은행 원본·preview·4 SVG는 기존 Task 1–4 산출물을 그대로 사용한다. 1장 bank는 17문항·82보기이고, 모든 `official_answer`는 null이라 공식 답은 확보되지 않았다.
- `정리노트/CLAUDE.md`는 JSON을 신규 원본의 유일한 원천으로 두고, 모든 보기 감사, 그림 선행 설명, 보충 출처 구분, 분류 경계와 조건 보존, 별도의 정확한 다섯 열 WEB 매핑표를 규정한다. PDF-only 단일/다중 출처 숫자 표와 기존 unmarked HTML은 호환 경로를 유지한다.
- `.agents/skills/summary-note/SKILL.md`가 단일 절차 원천이다. 등록 bank, raw-only, 웹 자료 없음의 세 상태를 구별하고 `validate --complete`, 전체 ID 분류, 생성 변형 분리, 정리 뒤 freshness 재검증, 장 종료 점검을 연결한다.
- `.claude/skills/summary-note/SKILL.md`는 canonical resource 링크만 가진 얇은 진입점이다. resource 링크는 canonical skill 기준, shell/data 경로는 저장소 루트 기준이다.
- study-note-eli5는 scope v1 fallback과 v2 혼합 범위, guide-module-relative `META.web_scope`, 최종 활성 ID와 같은 `WEB_BINDINGS`, requirement→authored `FACTS`, 자동 bank import, 공식 키와 분석 대안의 구별을 문서화한다.

## 드라이런 1 — 1장 등록 bank

입력은 `웹과제/1장/questions.json`과 그 requirement가 가리키는 `정리노트/0901.md`, `0903.md`, `0908.md`, `0910.md`, `강의노트/1장 생명분자와 세포.pdf`다. 선택 범위는 절차 검증용 Q2/Q4/Q9/Q17이며 나머지 13문항은 이 드라이런에서 검토하지 않았으므로 pass나 deferred로 표시하지 않았다. 실제 새 노트나 가이드는 만들지 않았다.

실행:

```bash
.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/1장/questions.json' --complete
.venv-question-bank/bin/python - <<'PY'
# Q2/Q4/Q9/Q17의 requirements, evidence locator, exam figure를 읽기 전용으로 출력
PY
```

결과는 `Valid: 17 questions (complete)`였다. 제안된 선행 가르침은 다음과 같다.

| 문항 | 필요한 근거 | 참조 절 | 그림 위치 |
|---|---|---|---|
| Q2 | 내막계 구성원과 분비 경로에 참여하는 리보솜의 구별 | `0908.md` §5-2, §4 | 없음 |
| Q4 | 세포내공생 근거, 내막계 경계, 미토콘드리아·엽록체 이중막 | `0908.md` §5-3/§5-2/§4, `0910.md` 복습/§1-1, 강의노트 1장 p.5–6 | 없음; wording issue와 공식 답 미확보를 먼저 공개 |
| Q9 | 단당·이당·다당, 아미노산·펩타이드, 뉴클레오타이드, 중성지질·인지질 구별 | `0903.md` §3-2/§3-3/§5-1, `0908.md` §2, 강의노트 1장 p.3–4 | exam `q09`를 질문의 보기 앞, explained `q09`를 solution 안에만 |
| Q17 | 원핵/진핵 경계, 3영역과 계의 수준, 식물 세포벽 셀룰로오스 | `0908.md` §4, `0901.md` §2-2, `0910.md` §1-2, 강의노트 1장 p.5 | 없음 |

위 표는 bank requirements와 실제 evidence만 세었다. option diagnostic이나 해설에만 있는 문장은 본문 근거로 승격하지 않았다. 남은 일은 실제 새 회차에서 17개 전체 ID를 정확한 다섯 열 매핑표에 분류하고, Q4의 공식 채점 여부를 확인하거나 분석 답/불확실성 표시를 유지하는 것이다.

## 드라이런 2 — 2장 no-bank fallback

확인한 웹 경로는 `웹과제/2장/questions.json`과 `웹과제/2장/raw/`이며 둘 다 없다. 따라서 raw-only가 아니라 **같은 장의 등록/미등록 웹 자료 없음**으로 판정했다. fallback 입력은 `STT/0915 생명.md`, `강의노트/2장 세포호흡과 광합성.pdf`, `23, 24 소스/2강 합본.pdf`다.

실행:

```bash
test ! -e '웹과제/2장/questions.json' && test ! -d '웹과제/2장/raw'
rg -n -m 8 '세포호흡|해당과정|시트르산|전자전달|광합성' 'STT/0915 생명.md'
pdftotext -layout '강의노트/2장 세포호흡과 광합성.pdf' - | sed -n '1,35p'
pdfinfo '23, 24 소스/2강 합본.pdf' | rg 'Pages|Title'
```

STT에서 전자전달계·시트르산 회로·해당과정이 확인됐고 강의노트는 2장 2.1의 에너지·효소로 시작한다. 이 드라이런은 기존 PDF 감사 경로가 실제 파일로 열리는지만 확인했다. 1장 Q1–Q17을 2장 문항 집합에 넣지 않았고, 분류 경계·조건 변경·그림 판독이라는 출제 형태만 재사용 대상으로 남겼다. 실제 2강 PDF 전체 보기 감사, STT의 정확한 시작/끝 범위, 생성 변형의 풀이 평가는 새 2장 회차 작업 전까지 pending이다.

## Fix round 1 — 생성 절차 실행 검증

첫 리뷰에서 bank-only `question_bank note` 예시가 같은 회차의 PDF 문항을
잃을 수 있고, web generator를 host `python3`로 실행하면 jsonschema가 없으며,
다섯 열 표의 범위와 thin-entrypoint guard가 부정확하다는 점이 확인됐다.
수정 뒤 canonical skill은 bank-only CLI를 명시적으로 제한하고
`references/mixed-source-note.md`의 실행 가능한 두 절차로 연결한다.

실제 혼합 절차는 다음 명령으로 문서의 첫 bash block을 그대로 실행했다.

```bash
sed -n '/^```bash$/,/^```$/p' \
  .agents/skills/summary-note/references/mixed-source-note.md | sed '1d;$d' | zsh
```

결과: 명시적으로 작성한 임시 `legacy-quiz.json` 1개와 real 1장 bank의
`export_note_items` 1개를 `render_note`에 함께 전달했다. 출력은
`legacy=1 web_active=1 web_total=17 ids=2강:6,web-20260917-ch01:q02`였고,
`--quiz "2강:6" --web-scope …`로 생성한 **13 tests가 모두 통과**했다.
legacy 문항 수/ID, 활성 web qid 1회, WEB 표의 원본 17 ID가 함께 검증됐다.

진짜 no-bank 2장 fallback은 같은 문서의 두 번째 bash block을 실행했다.

```bash
awk '/^## PDF-only/{section=1} section && /^```bash$/{block=1; next} \
  block && /^```$/{exit} block{print}' \
  .agents/skills/summary-note/references/mixed-source-note.md | zsh
```

현재 `_template.html`의 strict JSON marker에 PDF-only authored QUIZ 1개를
넣고, 표준 `python3 scripts/new_note_test.py 0998 --quiz 6`으로 생성한
**10 tests가 모두 통과**했다. 결과는 `pdf_only=1 ids=6 marker_json=true`였고
단일 출처 숫자 표를 유지했다. 이는 절차 표본이며 완성된 2장 노트나 전체
문항 감사가 아니다. web 명령은 모두 `.venv-question-bank/bin/python`을
사용하고, venv가 없을 때만 만드는 조건부 setup을 canonical skill에 뒀다.

entrypoint test는 실제 옛 heading `## 3. 문항 감사`를 검사한다. canonical
링크 뒤에 과거 절차를 다시 붙인 합성 회귀가 해당 guard에서 실패하는 것도
검증한다.

Fix round의 fresh full suite는 다음 명령을 정확히 한 번 실행했다.

```bash
.venv-question-bank/bin/python -m unittest discover -s tests -v \
  > /tmp/task8-fix1-full.txt 2>&1
```

결과는 **206 tests, OK, skipped=1** (7.270s)이다. 같은 시점의 real bank
`validate --complete`는 17문항 complete였고, bank·preview·SVG 4개의
SHA256은 base `5da5fa5`와 같으며 해당 경로 diff도 없다. 보호 artifact는
**30/30 matched**, summary-note `quick_validate.py`와 `git diff --check`도
통과했다.

## 검증과 증거의 구분

- 자동 검증: entrypoint RED→GREEN, 세 skill에 대한 `quick_validate.py`, 전체 unittest, bank `validate --complete`, `git diff --check`, protected artifact hash audit.
- 실제 source 확인: 1장 verified requirement/evidence graph과 2장 STT·강의노트·과거 PDF의 존재/내용 시작을 읽었다. synthetic draft를 source review나 complete 가이드로 부르지 않는다.
- 브라우저 증거: Task 7의 실제 Chrome/Playwright 증거를 유지한다. 1200px와 375px에서 `scrollWidth`가 viewport와 같고, 18 cards, Q9/Q14 exam/explained 분리, blind copy 해설 제거, console/network 오류 0이었다. Task 8은 HTML/SVG 엔진과 산출물을 바꾸지 않아 브라우저를 재실행하지 않았다.
- 의미/시각 경계: 자동 검증은 82개 보기의 생물학적 정확성, 학습자의 이해, 새 회차 guide의 blind solvability를 증명하지 않는다. 새 complete ELI5마다 source/reverse/blind/desktop/mobile/print/SVG 검토를 다시 해야 한다.
- 알려진 skip: 전체 suite의 optional split-textbook test 1개는 생성된 chapter PDF 부재로 계속 skip된다.

## 보호 경계

기존 30개 MMDD MD/HTML/ELI5 및 archive artifact는 `protected-artifact-hashes.json`과 대조한다. 신규 note/guide, bank/raw/SVG 수정은 이 작업에 포함하지 않는다. 현재 ELI5 adapter의 복수 공식 키 미지원, own-prompt exam figure 예외, deferred web-bank empty-facts 예외는 명시된 좁은 경계이며 legacy 규칙을 넓히지 않는다.

## Chronological rulings

아래는 workspace `progress.md`의 Ruling 행을 순서와 문구 그대로 보존한 기록이다.

- Ruling: Use an isolated worktree as already included in the approved execution workflow; no implementation on main — preserves user changes — costs an explicit integration step if the user wants main updated.
- Ruling: META.web_scope resolves relative to guide.py, matching META.note and the implementation plan; stored lock paths are rebased relative to the lock — resolves spec/plan path-base inconsistency — wrong choice would require updating only new guide manifests.
- Ruling: Transformation helpers require a verified input object while file boundaries call load_bank(complete=True); synthetic fixture tests are not source-review evidence — preserves pure adapters and honest validation — callers bypassing loaders are unsupported.
- Ruling: Missing raw image media enforcement in synthetic model fixtures is permitted; actual chapter tests verify PNG IHDR and original counts — avoids making fixture bytes impersonate an image — unsupported future source media need explicit review.
- Ruling: The dedicated venv inherits existing system site-packages while jsonschema stays installed in that venv — baseline PDF tests require pre-existing fitz — reproduction elsewhere still requires the repository existing PDF dependencies.
- Ruling: Bank-origin ambiguous questions may have no established alternative answer when a visible wording issue is preserved; legacy ambiguous-question rules remain unchanged — aligns the explicit bank spec with Q4 and prevents invented accepted answers — cost is a separate bank-origin validation branch and clearer uncertainty labeling.
- Ruling: Standard note QUIZ validation compares active included/review IDs, while the source scope separately accounts for all bank IDs including deferred — resolves the plan's full-set wording against its active-only exporter — costs users needing all questions a separate all-chapter preview, already provided.
- Ruling: load_web_scope returns a runtime-only resolved bank_path on each classified entry, alongside bank_id — downstream renderers need each bank's base directory while bank JSON stays schema-pure — costs a small documented runtime field and no stored-format change.
- Ruling: Wire new_note_test --web-scope and note CLI in Task6 with the scope loader; Task5 supplies renderer/export and marker-aware quiz parsing — removes the plan's Task5→Task6 dependency cycle without temporary stubs — costs only the order of intermediate commits.
- Ruling: Preserve pre-existing artifact bytes and legacy behavior; newly generated standalone test scripts may contain the additive standard-library marker parser — reconciles the plan's literal output wording with new mixed-format testing while the spec forbids rewriting old artifacts — cost is a diff if someone explicitly regenerates an old test script.
- Ruling: validate_scope_lock gains optional keyword lock_path, required for v2; v1 keeps its two-argument API — v2 cannot resolve lock-relative files without knowing lock location — costs an additive keyword at new verifier call sites.
- Ruling: CLI web-scope arguments resolve from invocation cwd to absolute paths; direct build_lock relative values resolve from note.parent; guide META resolves from guide.py before calling build_lock — preserves normal CLI behavior and existing module-relative META convention — costs explicit path resolution at boundaries.
- Ruling: Task6 includes one .app grid-template-columns:minmax(0,1fr) template rule — real17-question375px smoke found implicit grid width720px, absent in Task5's2-question sample — cost is a narrowly tested shared-template layout change; existing MMDD artifacts remain untouched.
- Ruling: Validated bank-origin figure evidence may be visible inside its own matching question prompt; actual teaching facts remain teaching-only and legacy figure rules unchanged — raw exam figures belong in prompts rather than falsely classified teaching — cost is a narrow ownership/visibility branch in guide_html.
- Ruling: Validated bank-origin deferred items may have empty fact_ids with explicit reason and later_prerequisite; active and legacy requirements unchanged — bindings intentionally cover active knowledge only, so future facts must not be invented — cost is a narrow deferred-bank branch in coverage_model.
- Ruling: Current ELI5 adapter explicitly rejects multiple official keys rather than truncating them; bank storage/preview still preserve the full array, and analysis accepted alternatives remain supported — legacy Q printed-key representation is scalar and the real17 records all have null official keys — cost is an adapter extension if a future official multi-key record must be exported.

## Final review finding and fix

The final whole-branch review found one P2 freshness gap: a verified question
payload hashed `question.source_ids`, but permitted official-answer and issue
evidence could reference other registered sources. Updating one of those files
and its stored source hash therefore left the old question review digest valid.

The model now derives one evidence-source union from the question's original
sources, selected source, official-answer sources, and issue sources. That same
union drives payload byte hashes, source reference accounting, and payload
eligibility. Unknown or missing references remain ordinary validation errors;
they do not reach payload construction or raise a traceback. Regression tests
cover official-only and issue-only byte changes with refreshed stored source
hashes, and both invalidate the prior verified review digest.

The real 1장 bank has the same union as its existing `question.source_ids` for
all 17 questions. Complete validation still reports `Valid: 17 questions
(complete)`, while `questions.json`, `preview.html`, and the four SVG artifacts
remain byte-identical with hashes `c8c140…`, `d65322…`, `bcd017…`, `eea53e…`,
`ad94ed…`, and `2a7ce9…`.

## Forward-test clarifications

The independent preparation-only forward test correctly selected the
registered-bank path for chapter 1 and the no-web/PDF-only path for chapter 2.
It produced no note or guide. It also exposed instruction gaps now clarified in
the canonical files:

- a web-enabled ELI5 scope/build/blind-copy/verify flow uses
  `.venv-question-bank/bin/python`; plain `python3` is limited to the no-bank
  legacy v1 path;
- a chapter bank is shared evidence rather than the property of one dated note;
  each requested MMDD gets its own full-ID classification, and its date/scope
  comes from the user request and actual STT rather than bank metadata;
- legacy unmarked read compatibility does not authorize rewriting old
  artifacts; an explicit update that combines a bank uses the current template
  and strict JSON marker contract;
- the established step-4 range gate keeps its cited number, with step 3 now
  explicitly marked as having no separate action.

Future note work still needs source resolution for damaged chapter-2 question
13 before treating its reconstructed wording as complete, and an explicit
session date plus actual STT or confirmed absence before creating a 0917 note.
Those are future-note prerequisites; no existing note was edited here. The
forward test is preparation evidence, not a generated-full-guide or independent
complete-guide pass.

## Final verification

- TDD RED: the two new source-mutation tests failed because no review mismatch
  was produced; the unknown-reference guard already returned validation errors.
- Focused GREEN: model **27 tests OK**, scope **11 tests OK**, ELI5 entrypoint
  **3 tests OK**, and summary-note entrypoint **4 tests OK**.
- Both canonical skills passed `quick_validate.py`.
- Real-bank complete validation: **17 questions complete**.
- Final full suite, executed once after the fixes: **212 tests, OK, skipped=1**
  in 7.309s. The existing optional split-textbook test remains the only skip.
- The full-suite log was written to
  `/tmp/web-question-bank-final-fix-full-tests.txt`; a surrounding zsh status
  capture used the reserved variable name `status` after the suite finished and
  returned shell exit 1. The test log itself ends in `OK (skipped=1)` and was
  inspected directly without rerunning the suite.

## 최종 재검토 및 전달 상태

`1b2638e`의 최종 수정 범위를 독립 재검토한 결과, 증거 해시 P2는 ADDRESSED, 명세 준수와 품질은 모두 PASS이며 새 결함은 없었다.

최종 담당자 검증: `.venv-question-bank/bin/python -m unittest discover -s tests`는 212 tests, OK (skipped=1), exit 0이었다. 선택적 split-textbook 검사 1개는 기존 입력 부재로 제외됐다. 실제 bank complete 검증 17문항, 기존 노트·가이드 30/30 해시 일치, raw 19/19 main 원본과 바이트 일치, `git diff --check`와 작업 트리는 깨끗했다.

구현은 `codex/web-question-bank`에 완료됐고 main은 원래 `acc50fa`에 유지했다. 병합·푸시는 실행하지 않았다. 자동 검증, 실제 브라우저 검증, 독립 원문 검토, 스킬 준비 점검은 각각의 근거이며, 새 회차 완성 노트나 학습자 이해도 검사를 수행한 것으로 해석하지 않는다.
