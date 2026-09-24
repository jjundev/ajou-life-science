# Web Quiz Screenshot Extraction Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 웹과제 스크린샷을 기존 검증 가능한 문제은행 양식으로 등록하는 재사용 스킬을 만든다.

**Architecture:** `.agents/skills/web-quiz-extract/SKILL.md`가 수집 인벤토리부터 원문·그림·근거 검토, complete 검증과 미리보기까지 순서와 완료 조건을 정한다. `.claude/skills/web-quiz-extract`는 동일 정본을 가리킨다. 기존 JSON schema, Python validator/renderer, `bio-review-pack`은 그대로 사용한다.

**Tech Stack:** Markdown skill, Git symlink, Python 3.10+, `jsonschema>=4.18,<5`, 기존 `scripts.question_bank` CLI, SVG.

**Spec:** `docs/superpowers/specs/2026-09-25-web-quiz-extract-design.md`

## Global Constraints

- 새 스킬 정본: `.agents/skills/web-quiz-extract/SKILL.md`; Claude 진입점: `.claude/skills/web-quiz-extract` 심볼릭 링크.
- 모델 호출을 켠다. 설명은 웹과제 종료 스크린샷 등록 요청에만 반응하도록 간결하게 쓴다. `disable-model-invocation: true`를 넣지 않는다.
- 저장 형식은 `웹과제/question-bank.schema.json` 버전 1이다. schema, `scripts/question_bank/`, `bio-review-pack`, 기존 `웹과제/1장/`은 수정하지 않는다.
- 한 평가의 대상 경로는 `웹과제/N장/questions.json`; 기존 파일을 자동 덮어쓰거나 병합하지 않는다.
- 원본은 `raw/`에 바이트·실제 파일명을 유지한다. NFC는 조회 비교에만 사용한다. 같은 이름·다른 바이트는 충돌이다.
- 지원 문항은 기존 단일 선택형, 그림은 기존 안전한 SVG만이다. unsupported 자료나 빠진 원본을 complete로 등록하지 않는다.
- 캡처 선택, 공식 답, 분석 답은 별도 필드다. 공식 답의 직접 화면 근거가 없으면 `null`이다.
- 근거가 부족하면 필수 `analysis.requirements`를 가짜로 채우지 않는다. 이때 raw와 `intake.md`는 남기되 `questions.json`을 새로 게시하지 않는다.
- 검토 해시는 실제 파일에서 `canonical_digest(question_payload(...))`, `canonical_digest(asset_payload(...))`로 계산하며, 원문/근거 시각 대조를 마친 뒤에만 `verified`를 쓴다.
- 테스트는 frontmatter/link 확인과 실제 1장 raw의 읽기 전용 행동 드라이런이다. 마커·제목을 복제하는 테스트를 새로 쓰지 않는다.

---

## File map

| File | Responsibility |
|---|---|
| `.agents/skills/web-quiz-extract/SKILL.md` | 자동 발견 설명, 입력, 단계별 완료 조건과 기존 validator 호출 |
| `.claude/skills/web-quiz-extract` | `.agents` 정본을 가리키는 심볼릭 링크 |

변경하지 않는 참조: `웹과제/question-bank.schema.json`, `scripts/question_bank/model.py`, `scripts/question_bank/svg.py`, `scripts/question_bank/__main__.py`, `.agents/skills/bio-review-pack/references/problem-selection.md`.

### Task 1: 스크린샷 등록 스킬과 단일 진입점

**Files:**
- Create: `.agents/skills/web-quiz-extract/SKILL.md`
- Create: `.claude/skills/web-quiz-extract` (symlink)

**Interfaces:**
- Consumes: schema v1; `model.load_bank`, `model.canonical_digest`, `model.question_payload`, `model.asset_payload`; `python -m scripts.question_bank validate/preview`.
- Produces: 자동 발견 가능한 `web-quiz-extract` 스킬. 호출 시 대상 평가의 `raw/`, `questions.json`, 선택적 `image/*.svg`, `preview.html`을 만든다. 등록 불가 때는 `raw/`와 `intake.md`로 누락을 밝힌다.

- [ ] **Step 1: 기준선과 스킬 위치 확인**

Run from repository root:

```bash
git status --short
git ls-files 웹과제/question-bank.schema.json scripts/question_bank/model.py .agents/skills/bio-review-pack/SKILL.md
ls -ld .claude/skills/bio-review-pack
.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/1장/questions.json' --complete
```

Expected: 기존 사용자 변경을 기록한다. `bio-review-pack`의 Claude 경로는 `.agents`를 가리키는 링크다. 1장 bank는 `Valid: 17 questions (complete)`다. 기존 사용자 변경은 건드리지 않는다.

- [ ] **Step 2: 다음 내용으로 정본 SKILL.md 작성**

Use the exact frontmatter and essential workflow below. The executor may shorten prose if it preserves each stage's checkable gate and behavior. Do not duplicate the full schema or current 1장 data.

````markdown
---
name: web-quiz-extract
description: 웹과제 완료 후 제공된 문제 스크린샷을 생명과학 저장소의 검증 가능한 웹과제 문제은행으로 등록할 때 사용한다. 이미 등록된 문제은행으로 복습팩을 만드는 요청에는 사용하지 않는다.
---

# 웹과제 스크린샷 등록

이 스킬은 `웹과제/N장/raw/`의 화면을 `questions.json`과 필요한 `image/` SVG로 등록한다. 스키마는 저장소 루트 `웹과제/question-bank.schema.json`이 유일한 필드 정의다. `REPO`는 저장소 루트이며, 검증 명령은 `REPO`에서 실행한다.

## 1. 평가와 원본 인벤토리

사용자가 지정한 장 번호와 화면에서 확인되는 날짜·평가명·문항 총수를 기록한다. 사용자 입력 이미지가 `raw/` 밖에 있으면 바이트·실제 파일명을 유지해 복사한다. 기존 `raw/` 파일은 다시 만들지 않는다. 동일 이름에 다른 바이트가 있거나 기존 `questions.json`이 있으면 덮어쓰지 않고 충돌을 보고한다. NFD 이름은 보존하고 NFC는 검색할 때만 사용한다.

각 화면의 실제 파일명, SHA256, 픽셀 크기, 문항 번호, 보기 개수, 전후 화면과의 연결, 제출 전/후 여부를 `웹과제/N장/intake.md`의 인벤토리에 적는다. 화면 중복은 버리지 않고 연결한다. 평가 전체 문항 수와 각 번호의 발문·모든 보기를 화면으로 확인했는지 대조한다. 날짜, 장, 총 문항 수, 각 문항의 필수 배점 중 하나라도 확인할 수 없으면 부족한 정보와 화면을 보고하고 `questions.json`을 새로 게시하지 않는다. 시간 제한·총점만 안 보이는 경우에는 스키마의 `null`을 사용한다.

## 2. 원문 전사와 관찰 분리

각 문항의 발문, 조건문과 소문항, 그림 순서, 보기 기호·문구·순서·배점을 원본과 다시 비교한다. OCR은 초안 보조로만 사용한다. 하나의 문항을 여러 화면에서 읽었다면 모든 원본 source ID를 연결한다. `selected_option_id`는 캡처의 선택 표시, `official_answer`는 결과 화면이 직접 증명한 공식 답, `analysis.answer_option_id`는 별도 판단이다. 선택 표시를 공식 답으로 복사하지 않는다. 공식 답 화면이 없으면 `official_answer: null`이다.

현재 저장 형식은 단일 선택형과 안전한 SVG 그림만 지원한다. 다중 선택형, 단답형, 충실하게 SVG로 옮길 수 없는 사진이나 읽을 수 없는 그림을 발견하면 문항 번호·원본 파일을 `intake.md`에 적고 이 평가의 `questions.json`을 새로 게시하지 않는다. 그림이 없다면 `assets: []`이다. 그림이 있으면 `image/qNN.svg`에는 원문만, `image/qNN.explained.svg`에는 풀이용 내용을 넣는다. 둘 다 원본과 시각 대조하고 `scripts.question_bank.svg.validate_svg`를 통과시킨다. 문제용 SVG의 텍스트·대체 설명에 원본에 없는 답 힌트를 넣지 않는다.

## 3. 답과 필요 지식의 근거

같은 장의 실제 강의노트·STT·교과서 파일에서 정확한 쪽/절/시간과 인용문을 확인한다. 모든 보기의 선택 적합성과 문항의 `analysis.requirements`를 그 근거로 작성한다. 표현이 모호하면 issue와 채점 상태를 공개한다. 근거 파일이 없거나 보기를 판단할 수 없으면 빈 근거·가짜 인용·그럴듯한 정답으로 schema를 채우지 않는다. raw와 `intake.md`에 미해결 항목을 남기고 `questions.json`을 새로 게시하지 않는다.

## 4. 검토 해시, 검증, 미리보기

화면별 원문·모든 보기·캡처 관찰, 그림, 분석 근거를 다시 대조한다. 번호 집합은 `1..expected_question_count`와 같아야 하고 raw source는 모두 참조되어야 한다. 검토가 끝난 문항/그림에만 `review.status=verified`를 쓰고 검토 기록을 남긴다. 저장할 `payload_sha256`는 현재 파일에 대해 `scripts.question_bank.model`의 `canonical_digest(question_payload(bank, question, bank_dir))` 또는 `canonical_digest(asset_payload(bank, asset, bank_dir))`로 계산한다. 검토 없이 해시만 갱신하지 않는다.

저장소 루트에서 `.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/N장/questions.json' --complete`를 실행한다. venv가 없다면 기존 `bio-review-pack/references/problem-selection.md` 2절의 환경 설정을 따른다. 성공한 뒤 `.venv-question-bank/bin/python -m scripts.question_bank preview '웹과제/N장/questions.json' --output '웹과제/N장/preview.html'`을 실행한다. 실제 브라우저에서 데스크톱과 375px 너비로 문제·보기·SVG·출처 링크와 정답 공개 위치를 본다. complete 검증 실패나 시각 대조 미완료를 성공으로 보고하지 않는다.

끝에 원본 화면 수/문항 수/보기 수/그림 수, 생성 파일, 검증 결과, 공식 답 확인 여부와 미해결 항목을 구분해 보고한다. `bio-review-pack`은 같은 장의 `questions.json`에 대해 `--complete`가 성공해야 문제를 사용한다.
````

Completion criterion: description has a distinct extraction trigger and no `disable-model-invocation`; all four stages state observable stop conditions; schema field definitions are referenced, not recopied.

- [ ] **Step 3: Claude 링크 생성**

Run from repository root:

```bash
ln -s ../../.agents/skills/web-quiz-extract .claude/skills/web-quiz-extract
test "$(readlink .claude/skills/web-quiz-extract)" = '../../.agents/skills/web-quiz-extract'
test -f .claude/skills/web-quiz-extract/SKILL.md
```

Expected: both entrypoints read the same SKILL.md; no second copy of the instructions.

- [ ] **Step 4: 정적 검증과 실제 입력 드라이런**

Run:

```bash
python3 /Users/hyunjun_macbook_pro/.ai-skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/web-quiz-extract
.venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/1장/questions.json' --complete
git diff --check
```

Expected: 새 skill frontmatter가 valid이고, 기존 bank는 17문항 complete, diff check가 clean. 기존 `bio-review-pack` 자체는 현재 quick validator에서 description의 `<`/`>` 때문에 실패할 수 있으나 이 작업에서 그 스킬을 고치지 않는다.

Then perform an **independent read-only forward check** with this user-like prompt, without supplying the expected answer to its evaluator:

> `웹과제/1장/raw/`에 놓인 완료 스크린샷을 웹과제 양식으로 등록할 준비를 점검해줘. 실제 파일을 쓰지 말고 화면과 기존 양식을 읽어 문항·보기·그림의 대응과 검증 절차를 말해줘. 추가로 첫 화면과 마지막 화면만 전달됐다면 어디서 멈출지도 설명해줘.

The evaluator reads the new skill, original screenshots, schema, validator help and relevant learning sources; it does not read this plan, spec, prior analysis or existing `questions.json` answer fields. Review its observed reasoning afterward. Expected scope gate from independently known material: full input is 19 screenshots for 17 questions and 82 options with 2 figure questions; first+last-only cannot establish all 17 questions and cannot register complete. It must keep selected and official answers distinct. Save the evaluation report under a git-ignored scratch directory, not the project output tree. If no independent agent is available, run the same inspection directly with a fresh source-first pass and mark it as non-independent.

- [ ] **Step 5: 스킬 자가 검토 및 범위 커밋**

Read the skill once as a future user: can it start from attached images or `raw/`, avoid copying a selected answer into the official key, stop on incomplete/unsupported material, and find every command without knowing the prior chat? Check that the behavior test did not rely on reading the old answer bank. If it found a real gap, fix only the new skill and repeat the relevant validation. Do not add generic advice, duplicate schema definitions, or alter `bio-review-pack`.

Run:

```bash
git add .agents/skills/web-quiz-extract/SKILL.md .claude/skills/web-quiz-extract
git diff --cached --check
git diff --cached --stat
git commit -m 'feat(skills): add web quiz screenshot registration'
```

Expected: only the canonical skill and its symlink are committed; raw screenshots, prior bank files and unrelated user changes are unchanged.

---

## Self-review performed while writing this plan

- Spec coverage: input/raw preservation, full-question count, transcription, answer separation, SVG pair, learning evidence, review digest, complete validation, preview, error reporting, collision safety and unchanged consumers all map to Task 1 steps 2–5.
- Scope: one new skill and one symlink, one independently reviewable deliverable. No new OCR subsystem, validator feature, schema migration or change to existing artifacts.
- Interface check: `question_payload(bank, question, base)`, `asset_payload(bank, asset, base)` and `canonical_digest(value)` exist; the CLI accepts `validate BANK --complete` and `preview BANK --output FILE`. The symlink relative target matches the existing `bio-review-pack` entrypoint.
- Placeholder check: no unfinished implementation step. The `N장` strings inside the proposed skill are runtime parameters supplied from the user's chapter, not literal paths to execute unchanged.
