# Bio-interactive Note Links Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 스킬의 저장 후 정리노트 연결 절차를 추가하고 기존 43개 자료를 관련 설명에 연결한다.

**Architecture:** `resolve.cjs`는 HTML 후보 경로도 반환한다. `link-notes.cjs`는 검토된 연결 명세를 받아 원문 구간만 수정한다. 의미적 연결은 작성자가 노트·자료를 읽고 명세에 기록하며 도구는 위치·파일·중복을 검증한다.

**Tech Stack:** Node.js >=20, CommonJS, node:test, fs/path 기본 라이브러리, 기존 HTML.

**Spec:** `docs/superpowers/specs/2026-10-14-bio-interactive-note-links-design.md`

## Global Constraints

- 상대 경로, `target="_blank" rel="noopener noreferrer"`, `(새 탭)` 표시 문구 없음.
- 기존 본문, 스타일, 위젯, 스크립트와 인터렉티브 파일 보존.
- 누락·모호한 연결만 건너뛰고 이유 보고. 생성 성공은 유지.
- Node.js 20 이상, CommonJS, 기본 라이브러리만 사용.
- 실제 NFC/NFD 경로 보존. 재실행 중복 방지. 노트별 한 번 저장.
- 커밋·푸시 실행하지 않음.

## Review Focus

- 한글·공백·`+`·`#` 파일명: URL 인코딩 후 실제 파일로 연결되는지 검사.
- 동일 자료의 다른 절과 이미 존재하는 링크: 절별 중복만 방지하고 기존 링크도 새 탭 속성을 보장.
- 중첩 HTML, 주석·스크립트의 가짜 태그: 삽입 구간 외 바이트 보존.
- 없는 노트·절·자료와 중복 ID: 원본 유지하고 연결별 이유 반환.
- 여러 자료·재실행: 노트별 모든 연결 반영, 두 번째 실행 변경 없음.

---

### Task 1: 연결 도구와 HTML 탐색

**Files:**
- Create: `.agents/skills/bio-interactive/scripts/link-notes.cjs`
- Create: `.agents/skills/bio-interactive/tests/link-notes.test.cjs`
- Modify: `.agents/skills/bio-interactive/scripts/resolve.cjs`
- Modify: `.agents/skills/bio-interactive/tests/resolve.test.cjs`

**Interfaces:**
- Consumes: `{note, links:[{sectionId, html, label, before, after, anchorId?}], dryRun?}`. 모든 파일은 실제 절대 경로. `before/after`는 링크 앞뒤의 일반 텍스트.
- Produces: `linkNotes(input) -> {note, changed, results:[{sectionId, html, status, reason?}]}`; status는 added/updated/unchanged/skipped.
- Produces: `resolve({repo,arg}).noteHtml -> string[]`.

- [x] Step 1: 임시 폴더 fixture로 실패 테스트 작성. 핵심 검증:
```js
const result = linkNotes({note, links:[{sectionId:'pcr',html,label:'PCR 모형',before:'세 단계를 ',after:'에서 살펴보세요.'}]});
assert.equal(result.changed, true);
assert.match(fs.readFileSync(note,'utf8'), /target="_blank" rel="noopener noreferrer"/);
assert.equal(linkNotes({note,links}).changed, false);
```
추가 케이스: 누락 파일·절, 중복 ID, NFC/NFD, `+`/`#` 파일명, 기존 링크, 여러 절, 중첩 태그·가짜 스크립트 태그, dryRun.
- [x] Step 2: `node --test .agents/skills/bio-interactive/tests/link-notes.test.cjs`를 실행하여 모듈 없음 실패 확인. resolve 테스트에 HTML 후보 실제 경로 반환 검증을 넣고 실패 확인.
- [x] Step 3: 태그 스캐너로 원문 offsets·부모 관계를 수집한다. 주석과 script/style 내용은 건너뛴다. 고유 절 안 첫 `.layer.formal` 뒤(없으면 `.layer.eli5` 또는 제목 뒤)에 다음 구조를 삽입한다:
```html
<p class="interactive-note" data-bio-interactive="relative-url">안내 <a href="relative-url" target="_blank" rel="noopener noreferrer">자료 제목</a>에서 확인해 보세요. <span>(새 탭)</span></p>
```
텍스트/속성 escape, 경로의 각 세그먼트 encodeURIComponent, 노트 자기 링크 제외. 동일 절의 목적지 링크 존재 시 속성만 보정. 노트 누락 NOTE_MISSING, 자료 누락 TARGET_MISSING, 절 누락 SECTION_MISSING, 중복 절 SECTION_AMBIGUOUS를 반환. 전체 문자열 편집 후 한 번 write.
resolve 반환값에 `noteHtml: exists ? list(folder).filter(d=>d.isFile() && /^정리노트_.*\\.html$/.test(nfc(d.name))).map(d=>path.join(folder,d.name)) : []` 추가.
- [x] Step 4: 위 두 테스트 파일 실행, 모두 PASS.

### Task 2: 스킬 계약과 연결 명세

**Files:**
- Modify: `.agents/skills/bio-interactive/SKILL.md`
- Modify: `.agents/skills/bio-interactive/references/topic-selection.md`
- Create: `.agents/skills/bio-interactive/references/note-links.md`
- Modify: `.agents/skills/bio-interactive/tests/skill.test.cjs`

**Interfaces:**
- Consumes: Task 1 linkNotes 명세, resolve.noteHtml, save 결과 html.
- Produces: 작성자용 브리프와 `RUN/note-links.json` CLI 입력 계약.

- [x] Step 1: skill.test.cjs에 `noteHtml`, `scripts/link-notes.cjs`, `references/note-links.md`, `### 8. 정리노트 연결`, `### 9. 보고`와 브리프 연결 필드 검증을 추가.
- [x] Step 2: `node --test .agents/skills/bio-interactive/tests/skill.test.cjs` 실행, 새 계약 누락으로 FAIL 확인.
- [x] Step 3: 금지 범위를 링크 안내 외의 본문 수정으로 좁힌다. 새 탭·중복·실패 보고·기존 자료 연결 전용 요청을 명시한다. references에 실제 CLI 예제를 작성한다:
```json
{"notes":[{"note":"/absolute/정리노트.html","links":[{"sectionId":"s0-pcr-cycle","html":"/absolute/인터렉티브_01_PCR.html","label":"PCR 모형","before":"세 단계를 ","after":"에서 순서대로 살펴보세요."}]}]}
```
실행: `node "$SKILL/scripts/link-notes.cjs" "$RUN/note-links.json"`. 생성 없이 링크만 연결할 때는 기존 노트·자료의 설명을 읽고 같은 명세로 실행한다.
- [x] Step 4: skill 테스트 PASS 확인.

### Task 3: 기존 자료 전체 연결과 최종 검증

**Files:**
- Create: `docs/superpowers/plans/2026-10-14-bio-interactive-note-links-manifest.json`
- Modify: `복습노트/0901,0903,0908,0910,0915,0917,0922,0929,1001,1006,1008,1013/정리노트_*.html`

**Interfaces:**
- Consumes: Task 1 CLI와 Task 2 작성 계약.
- Produces: 모든 기존 자료를 포함하는 검토된 연결 명세와 수정된 노트.

- [x] Step 1: 각 노트 article.topic와 자료 TOPIC/MODES/STEPS 설명을 읽는다. 자료당 한 개 이상 적절한 절을 선정하고 관찰 포인트 문장을 작성한다.
- [x] Step 2: 명세 dryRun으로 경로·절 확인. 예:
```js
for (const entry of manifest.notes) assert.ok(!linkNotes({...entry,dryRun:true}).results.some(r=>r.status==='skipped'));
```
- [x] Step 3: CLI 실행 후 두 번째 실행에서 모든 노트 changed=false 확인. 정리노트별 diff에서 추가 문장/링크만 수정되었는지 확인.
- [x] Step 4: `node --test .agents/skills/bio-interactive/tests/*.test.cjs`, `git diff --check` 실행. 링크를 URL decode하여 실제 대상 존재와 43개 자료 커버리지 확인. 대표 노트를 브라우저에서 열어 링크 클릭의 새 탭과 원래 노트 유지 확인.

## 실행 기록

- Ruling: 사용자가 승인한 설계대로 수정과 전체 연결을 명시적으로 요청했으므로 계획 저장 후 재승인 없이 직접 실행한다.
- Ruling: 사용자에게 보이는 로컬 정리노트를 갱신하는 작업이므로 현재 워크스페이스에서 변경한다. 초기 git status는 깨끗하며 커밋은 하지 않는다.
- Ruling: 스킬의 기존 테스트 방식(node:test)을 유지하여 연결 도구의 실제 실패/통과와 문서 계약 검증을 진행한다.

- Task 1: complete — 연결 도구/resolve 구현, 실패→통과 확인.
- Task 2: complete — 스킬 계약·브리프·연결 참고문서 수정, 문서 계약 테스트 통과.
- Task 3: complete — 12개 노트, 43개 자료, 71개 문맥 링크. 누락 0, 재실행 변경 0. 생성 안내를 제거한 본문은 HEAD와 동일(플랫폼 줄바꿈 정규화 비교).
- Ruling: 기존 테스트의 Windows 경로/CRLF 가정 실패를 확인하여 테스트 비교와 실제 NFD fixture 경로 참조만 보완했다.
- 최종 검토: 새 탭 속성 보정에서 다른 속성의 인용 문자열과 값 없는/중복 속성을 처리하는 문제 2건을 발견했다. 회귀 테스트 실패→수정→통과 후 별도 검토자가 해결을 확인했다. 남은 actionable finding 없음.
- 브라우저: PCR 설명 뒤 안내·링크 표시와 대상 자료의 정상 로드, 원래 노트 유지, 콘솔 오류 0 확인. target=_blank 및 noopener/noreferrer DOM 검사 완료. 앱 내 브라우저에서 링크 클릭에 의한 새 탭 생성은 관찰되지 않아, 실제 새 탭 생성 검증은 제한된다. 대상은 별도 탭을 직접 열어 정상 로드를 확인했다.

- 2026-10-14 사용자 추가 요청: 안내의 `(새 탭)` 표시를 기존 71개 링크와 생성 도구에서 제거했다. `_blank`와 rel 속성은 유지한다.
