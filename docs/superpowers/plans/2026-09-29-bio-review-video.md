# Bio Review Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 완성된 생명과학 복습팩을 전체 내용과 HTML 템플릿 디자인을 보존하는 한국어 Aoede 복습 영상으로 만드는 저장소 전용 스킬을 구현한다.

**Architecture:** 에이전트가 출처 대응·대본·도식·의미 검토를 담당하고, 작은 Python 모듈이 입력 계약·템플릿 스냅샷·Vertex TTS·시간표·캐시·렌더·검증을 담당한다. HyperFrames 장면 렌더와 FFmpeg 결합을 사용하며 음성 교체는 별도 경로로 둔다. 실행별 immutable 입력 스냅샷과 원자적 상태 저장으로 실패한 부분만 재개한다.

**Tech Stack:** Python 3.11 이상/표준 라이브러리, unittest, HTML/CSS/SVG, 로컬 Pretendard 1.3.9, GSAP, HyperFrames CLI, FFmpeg/ffprobe, Vertex AI Express REST. HyperFrames 0.8.91은 기존 성공 버전이며 실행 환경에서 지원 명령을 확인하고 사용 버전을 기록한다. Node 브라우저 검사 도구는 현재 HyperFrames 설치에 맞춰 사용한다.

**Spec:** [2026-09-29-bio-review-video-design.md](../specs/2026-09-29-bio-review-video-design.md). 사용자가 제공한 grill 설계와 템플릿 보존 요구를 함께 보존했다. 실행자는 두 문서를 먼저 읽는다.

## Global Constraints

- “수업을 이미 들은 학생을 위한 복습 영상”이며 생명과학 저장소 전용이다.
- “전체 개념 보존, 반복만 통합”; “미연결 학습 내용이 남으면 완료 처리하지 않습니다.”
- “화면 디자인도 생명과학의 reviewpack 스킬 템플렛 html을 유지”한다.
- 디자인 원본은 `.agents/skills/bio-review-pack/assets/note-template.html`과 `review-template.html`이다. 기존 파일을 수정하지 않는다.
- 템플릿 CSS와 의미별 클래스·글꼴·강조·구분선을 재사용한다. `data-theme="dark"`, Pretendard 1.3.9, 1920×1080, 30fps를 기본값으로 고정한다.
- “기본 공급자: Vertex AI Express”, `gemini-2.5-flash-tts`, Aoede. 승인한 한국어 지시문을 재사용한다.
- “실제 음성 길이로 확정”; 임의로 영상 길이를 제한하지 않는다.
- 자동 완주, `--review`에서만 중간 검토. 실행당 기본 $2는 로컬 API 예산이며 클라우드 청구 보장이 아니다.
- 인증은 환경변수 또는 명시한 `.env` 경로. 키·인증 헤더·원본 예외 본문을 저장하지 않는다.
- “파일 존재나 프레임 수만 같다고 재사용하지 않습니다.”
- “Windows 전역 GPU 설정 변경은 기본 동작에 넣지 않습니다.”
- “완성 MP4를 재생하는 미리보기의 통과를 편집 소스 전체의 검증 통과로 대체하지 않습니다.”
- 원본 영상·복습팩·기존 0915 제작물은 읽기 전용. 결과는 `복습영상/<범위>/<실행ID>/`에 둔다.
- 자동 테스트는 fake API/로컬 PCM을 사용하며 실제 API 요청은 하지 않는다.
- 이번 요청은 **계획 작성**이다. 아래 체크박스와 커밋 명령은 향후 실행 단계이며 지금 실행하지 않는다. 커밋 전 저장소 지침과 사용자 권한을 확인하고 변경 파일만 stage한다.

## Review Focus

1. 한국어 NFC/NFD 경로·공백·작은따옴표 및 중복 날짜 폴더: 실제 경로를 보존하고 모호한 입력은 후보와 함께 중단한다. Task 1, 7의 테스트로 고정한다.
2. HTML/MD의 숫자 충돌 및 토픽 ID만 연결한 허위 coverage: 출처 대조/항목별 의미 검토가 끝나기 전 유료 작업·완료 표시를 차단한다. Task 2.
3. 템플릿 변경과 OS 라이트모드: 이전 실행은 스냅샷을 유지하고 새 실행은 현 템플릿에서 생성하며 다크모드/컴포넌트 형태를 보존한다. Task 3, 8.
4. 응답 수신 여부가 불명확한 타임아웃·병렬 예산 경쟁·중단 후 재개: 미확정 비용을 보수적으로 예약하고 성공 캐시는 보존한다. Task 4, 5.
5. 재타이밍의 0프레임 구간·매우 긴 새 음성·손상된 중간 파일: 해당 장면 재렌더 또는 구체적 중단으로 처리하며 이전 영상과 latest를 보호한다. Task 6, 7, 8.

---

## 실행 전 맥락과 파일 지도

이 작업은 입력→음성→시간표→화면→출력의 단일 파이프라인이다. 서로 독립된 제품으로 분리하면 manifest와 재개 규약을 중복시키므로 하나의 계획으로 진행한다. Task 1–9는 순차 의존성이 있다. 테스트 가능한 경계에서만 작업을 나눴다.

기존 참고 파일:

| 파일 | 읽을 내용 / 이관하지 않을 부분 |
|---|---|
| `.agents/skills/bio-review-pack/SKILL.md` | 폴더·날짜 규칙, 기존 노트 제작 역할 |
| `.agents/skills/bio-review-pack/assets/note-template.html` | 전체 CSS, `.topic`, `.layer`, `.figure`, 배지, 표, 수식 |
| `.agents/skills/bio-review-pack/assets/review-template.html` | 문제와 해설의 실제 클래스; 구현 시 selector를 이 파일에서 확인 |
| `.agents/skills/bio-review-pack/tests/test_template.py` | unittest 관례와 템플릿 슬롯 |
| `videos/0915-biology-review/generate_aoede.py` | payload/PCM/백오프; ROOT·날짜·과거 durationRatio 의존 제거 |
| `videos/0915-biology-review/build_video.py` | paused timeline·자막·장면 구조; 자체 색상 CSS를 템플릿 대신 복사하지 않음 |
| `videos/0915-biology-review/prepare_render_parts.py`, `render_parts.py` | 장면 렌더·PCM 조립; 고정 26장면/4worker/프레임만 보는 캐시 제거 |
| `videos/0915-biology-review/replace_with_aoede.py` | 구간 setpts·원본 보존; source hash 없는 fingerprint 제거 |
| `videos/0915-biology-review/aoede/VIDEO-QA.md` | 실제 MP4 검사와 wrapper 검사 구분 |

새 파일은 모두 `.agents/skills/bio-review-video/` 아래에 둔다. 아래 경로에서 `S`는 이 디렉터리를 뜻한다. 실제 구현 및 커밋 시에는 전체 저장소 상대 경로로 펼친다.

```text
.agents/skills/bio-review-video/
  SKILL.md                         # 에이전트 실행 지침과 사용자 명령
  agents/openai.yaml               # 스킬 표시 정보
  references/
    sources-and-coverage.md         # 출처·충돌·의미 대응 검토
    narration-and-motion.md         # 한국어 대본, 템플릿, 결정적 동작
    voice-and-budget.md             # 인증·비용·429·음성 변경
    rendering-and-verification.md   # GPU·소스/결과 QA·보고
  assets/
    defaults.json                  # 비밀 없는 설정; 디자인 값을 복제하지 않음
    vertex-direction.txt           # 승인된 Aoede 지시문
    video-layout.css               # 영상 전용 배치/글자 크기 어댑터
  scripts/
    video.py                       # CLI dispatch, 단계 실행/재개
    lib/
      __init__.py
      sources.py                   # 범위·실제 파일·asset 경로 발견
      manifest.py                  # schema·출처·coverage·충돌 gate
      theme.py                     # 원본 HTML/CSS 스냅샷·렌더용 셸
      cache.py                     # 정규화 해시·파일 검증·원자적 쓰기
      state.py                     # 실행 lock·단계 DAG·복구
      budget.py                    # 비용 예약/정산 ledger
      vertex_tts.py                # REST adapter·PCM·재시도
      timing.py                    # PCM 샘플 기준 시간표·SRT·chapters
      composition.py               # 에이전트 장면 조각→HyperFrames 조립
      render.py                    # GPU 실측·장면 렌더·최종 mux
      revoice.py                   # 기존 구간 retime/부분 재렌더 결정
      verify.py                    # 분리된 QA와 latest 승격
  tests/
    _util.py                       # sys.path·최소 manifest·PCM fixture
    test_sources.py
    test_manifest.py
    test_theme.py
    test_state.py
    test_tts.py
    test_timing.py
    test_composition.py
    test_render.py
    test_revoice.py
    test_verify.py
    test_cli.py
    browser_check.mjs              # 실제 CSS·폰트·bbox·seek 검사
```

`review-dark.json`을 독립 수동 팔레트로 두지 않는다. 동일 목적의 `source/theme.json`을 실행 시 템플릿에서 생성한다. 색상 원본이 둘이 되는 것을 막기 위한 파일 구조 조정이다.

실행 산출물:

```text
복습영상/<range>/<run-id>/
  review.mp4, narration.srt, chapters.txt
  run.json, manifest.json
  source/inputs.json, source/coverage.md, source/conflicts.json
  source/templates/note-template.html, review-template.html
  source/theme.json, source/template.css, source/review-template.css
  source/script.md, source/scene-fragments/, source/compositions/
  source/index.html, source/retime-manifest.json
  assets/fonts/, assets/vendor/, assets/voice/
  renders/, verification/, work/, cost-ledger.json
```

`복습영상/<range>/latest.json`은 검증된 run-id/상대 MP4 경로/hash만 가진다. 작업용 대용량 캐시와 비밀 파일은 커밋하지 않는다. 새 스킬 테스트는 저장소 내 unittest 관례를 따른다.

## Task 1: 한국어 입력과 범위 발견 계약

**Files:** Create `S/scripts/lib/__init__.py`, `S/scripts/lib/sources.py`, `S/tests/_util.py`, `S/tests/test_sources.py`.

**Interfaces:**
- `discover(repo: Path, selector: str) -> dict`: `{range: str, files: list[dict], missing_optional: list[str]}`.
- 각 file: `{id: str, kind: str, path: str, sha256: str}`. path는 실제 절대 경로, id는 `src-` + 상대 경로 SHA256 앞 16자리.
- `asset_path(root: Path, relative: str) -> Path`: 루트 안의 존재하는 로컬 그림만 허용한다.
- `SourceError(ValueError)`는 missing/ambiguous/invalid-date/unsafe-asset 이유와 비밀 없는 후보를 전달한다.

- [ ] **Step 1: 테스트 지원 파일과 실패 테스트 작성.** `_util.py`는 아래 경로 설정과 `pcm(path, samples)`를 제공한다. 나머지 테스트는 여기서 `ROOT`, `SKILL`을 import한다.

```python
from pathlib import Path
import sys, wave
SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
sys.path.insert(0, str(SKILL / 'scripts'))

def pcm(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        out.writeframes(b'\x10\x00' * samples)
    return path
```

```python
import tempfile, unittest
from pathlib import Path
from _util import ROOT
from lib.sources import discover, SourceError, asset_path

class SourcesTest(unittest.TestCase):
    def test_korean_space_quote_and_invalid_date(self):
        with tempfile.TemporaryDirectory(prefix="생명 O'Brien ") as d:
            root = Path(d)
            folder = root / '복습노트' / '0915'
            folder.mkdir(parents=True)
            (folder / '정리노트_0915_호흡.html').write_text('<p>ATP</p>', encoding='utf-8')
            result = discover(root, '0915')
            self.assertEqual(result['range'], '0915')
            self.assertEqual(len(result['files']), 1)
            self.assertTrue(Path(result['files'][0]['path']).is_file())
            with self.assertRaises(SourceError): discover(root, '0931')
            with self.assertRaises(SourceError): asset_path(folder, '../outside.svg')
```

- [ ] **Step 2: 실패 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_sources.py -v` → 아직 모듈이 없어 FAIL.
- [ ] **Step 3: 발견 알고리즘 구현.** MMDD는 `datetime.strptime(value, '%m%d')`, 역방향 범위는 오류. NFC는 비교에만 사용하고 실제 Path를 유지한다. 정확한 범위 폴더가 있으면 그것 하나, 없으면 범위 안의 날짜 폴더를 정렬해 합친다. 기간 폴더 중복/부분 겹침은 자동 중복 합치기 대신 후보를 보고한다. 같은 논리 이름의 NFC/NFD 파일 두 개도 모호성 오류다. 지정 폴더는 파일명 range가 일치해야 한다. HTML 또는 MD 하나는 필수이며 문제/장마감 누락은 `missing_optional`에 기록한다. 외부 URL 그림은 내려받지 않고 unresolved asset로 기록한다.

```python
def asset_path(root, relative):
    base = root.resolve()
    result = (base / relative).resolve()
    if not result.is_relative_to(base) or not result.is_file():
        raise SourceError('unsafe-asset: ' + relative)
    return result
```

- [ ] **Step 4: 날짜 범위·중복을 테스트에 추가.** 위 테스트에서 `0917` 폴더와 노트도 만들고 `discover(root, '0915-0917')`의 file 수가 2인지 검사한다. `unicodedata.normalize('NFD', '정리노트_0915_호흡.html')`를 두 번째 파일명으로 만든 경우 SourceError를 검사한다. 동일 명령 PASS 및 0915 실제 입력 read-only 목록 확인.
- [ ] **Step 5: 작업 단위 커밋.** `git add .agents/skills/bio-review-video/scripts/lib .agents/skills/bio-review-video/tests` 후 `git commit -m "feat: resolve biology review video sources"`. 후속 Task에서도 커밋에는 해당 Task 변경만 포함한다.

## Task 2: manifest와 전체 내용 coverage gate

**Files:** Create `S/scripts/lib/manifest.py`, `S/tests/test_manifest.py`, `S/references/sources-and-coverage.md`; Extend `S/tests/_util.py` with `minimal_manifest()`.

**Interfaces:** `validate_manifest(m: dict) -> list[str]`, `require_ready(m: dict) -> None` (오류 시 `ManifestError`), `coverage_rows(m: dict) -> list[dict]`. `discover`의 file 목록을 sources로 사용한다.

JSON v1 계약:

```json
{
  "schema_version": 1, "range": "0915",
  "sources": [{"id":"src-note","kind":"note-html","path":"note.html","sha256":"fixture"}],
  "topics": [{"id":"t-atp","requirements":[{"id":"r-atp","claim":"수업 기준 32 ATP","source_id":"src-note","locator":"#respiration","kind":"number","required":true}]}],
  "scenes": [{"id":"scene-atp","topic_ids":["t-atp"],"question_ids":[],"template_kind":"note","visual":"ATP 수량 표시","motion":"32까지 수량 증가"}],
  "segments": [{"id":"seg-atp","scene_id":"scene-atp","text":"수업 기준으로 32 ATP입니다.","caption":"수업 기준 32 ATP","requirement_ids":["r-atp"],"source_ids":["src-note"]}],
  "questions": [], "notices": [], "conflicts": [],
  "coverage_reviews": [{"requirement_id":"r-atp","segment_ids":["seg-atp"],"status":"passed","reason":"발화가 수업 기준과 수치를 모두 보존"}],
  "exclusions": []
}
```

`questions` 항목은 `{id, source_id, locator, requirement_ids}`. 문항 전문을 낭독할 필요는 없지만 판별점마다 requirement가 있어야 한다. `notices`는 `{id, text, period_label, source_id}`. `conflicts`는 `{id, source_ids, description, status, resolution, evidence}`이며 resolved만 gate 통과. exclusions는 비학습 내용만 `{source_id, locator, reason}`으로 기록한다. 필수 requirement 제외는 허용하지 않는다.

- [ ] **Step 1: fixture와 실패 테스트 작성.** 위 JSON을 `_util.minimal_manifest()`의 새 dict 반환값으로 넣는다.

```python
import unittest
from _util import minimal_manifest
from lib.manifest import validate_manifest

class ManifestTest(unittest.TestCase):
    def test_link_and_semantic_review_are_both_required(self):
        m = minimal_manifest()
        self.assertEqual(validate_manifest(m), [])
        m['segments'][0]['requirement_ids'] = []
        self.assertIn('uncovered:r-atp', validate_manifest(m))
        m = minimal_manifest()
        m['coverage_reviews'][0]['status'] = 'pending'
        self.assertIn('unreviewed:r-atp', validate_manifest(m))

    def test_conflicting_numbers_block_paid_work(self):
        m = minimal_manifest()
        m['conflicts'] = [{'id':'c1','source_ids':['src-note'],
          'description':'HTML 32 / MD 30 ATP','status':'open','resolution':'','evidence':''}]
        self.assertIn('conflict:c1', validate_manifest(m))
```

- [ ] **Step 2: 실행하여 FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_manifest.py -v`.
- [ ] **Step 3: schema/coverage 검사 구현.** 배열·문자열 타입, 중복 ID, 참조 무결성, 빈 대본/자막/동작 의도, source locator, required bool, question requirement를 검사한다. review는 실제 연결 segment들을 가리켜야 한다. `passed` 문자열만 자동 생성하지 않는다. 에이전트가 claim과 원문·발화를 대조한 이유를 기록해야 한다.

```python
linked = {rid for s in m['segments'] for rid in s['requirement_ids']}
reviewed = {r['requirement_id'] for r in m['coverage_reviews']
            if r['status'] == 'passed' and r['reason'].strip() and r['segment_ids']}
for topic in m['topics']:
    for req in topic['requirements']:
        if req['required'] and req['id'] not in linked:
            errors.append('uncovered:' + req['id'])
        if req['required'] and req['id'] not in reviewed:
            errors.append('unreviewed:' + req['id'])
```

- [ ] **Step 4: 출처 규칙 문서 작성 및 PASS.** HTML/MD 숫자 차이, 보충/오개념, 모든 문제 판별점, 과거 공지의 처리 예시를 이 계약으로 설명한다. 파서는 항목 발견을 돕지만 의미 동일성을 증명하지 못한다는 점을 명시한다. `require_ready`를 향후 TTS와 publish 양쪽에서 호출한다. 같은 unittest 명령 PASS.
- [ ] **Step 5: 커밋.** `git add .agents/skills/bio-review-video` → `git commit -m "feat: enforce review video coverage contract"`.

## Task 3: 복습팩 HTML을 보존하는 영상 디자인 어댑터

**Files:** Create `S/scripts/lib/theme.py`, `S/assets/video-layout.css`, `S/tests/test_theme.py`.

**Interfaces:** `snapshot_theme(pack: Path, run: Path) -> dict`, `scene_shell(fragment: str, kind: str, theme: dict) -> str`. theme에는 templates `{note/review: {path, sha256, css_path}}`, font asset hashes, layout hash, dark computed tokens를 기록한다. `kind`는 note/review만 허용한다.

- [ ] **Step 1: 원본 보존과 재개 테스트 작성.**

```python
import tempfile, unittest, hashlib
from pathlib import Path
from _util import ROOT
from lib.theme import snapshot_theme, scene_shell

class ThemeTest(unittest.TestCase):
    def test_original_templates_and_dark_shell(self):
        pack = ROOT / '.agents/skills/bio-review-pack'
        original = (pack / 'assets/note-template.html').read_bytes()
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            theme = snapshot_theme(pack, run)
            saved = run / 'source/templates/note-template.html'
            self.assertEqual(saved.read_bytes(), original)
            self.assertEqual(theme['templates']['note']['sha256'], hashlib.sha256(original).hexdigest())
            page = scene_shell('<section class="topic"><div class="layer warn">주의</div></section>', 'note', theme)
            self.assertIn('data-theme="dark"', page)
            self.assertIn('class="layer warn"', page)
            self.assertNotIn('localStorage', page)
            self.assertEqual((pack / 'assets/note-template.html').read_bytes(), original)
```

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_theme.py -v`.
- [ ] **Step 3: 스냅샷과 CSS 이식 구현.** HTMLParser로 각 style의 원문을 추출해 그대로 저장한다. `note`와 `review` CSS를 섞지 않는다. `source/templates`가 이미 있으면 recorded hash를 확인하고 재개 시 원본 변경으로 덮어쓰지 않는다. 새 run만 새 템플릿을 가져온다. selector 누락은 조용한 fallback 대신 명확한 호환성 오류로 보고한다. 스타일 뒤에 아래 레이아웃만 덧붙인다.

```css
html[data-theme="dark"], body { width:1920px; height:1080px; margin:0; overflow:hidden; }
.video-scene { position:relative; width:1920px; height:1080px; padding:64px 96px 204px; }
.video-scene main { max-width:none; padding:0; }
.video-scene .topic { margin:0; padding-top:24px; }
.video-scene .hero h1 { font-size:60px; }
.video-scene .topic h3 { font-size:48px; }
.video-scene .layer { font-size:32px; }
.video-scene .layer-title { font-size:34px; }
.video-scene .layer.eli5 .lead { font-size:38px; }
.video-scene .figure svg { max-width:none; max-height:570px; }
.video-caption { position:absolute; left:96px; right:96px; top:908px; bottom:36px;
  border-top:1px solid var(--line); color:var(--ink); font:400 39px/1.5 var(--font);
  display:flex; align-items:center; justify-content:center; text-align:center; }
```

이 CSS에 배경/강조색/새 shadow/gradient를 추가하지 않는다. 주의·보충·교수님 블록의 고유 템플릿 스타일은 보존한다. 기존 template의 더 구체적인 글자 크기는 실제 화면 QA 후 영상 전용 선택자로 확대한다. 레이어를 통째로 카드 UI로 바꾸지 않는다. template의 scripts/localStorage/웹 내비게이션은 제외하고, 학습용 widget 상태는 장면 조각에서 재현한다. 수식은 로컬 KaTeX 0.16.11 자산을 고정하고 준비 완료 후 렌더한다.

- [ ] **Step 4: 변경된 원본과 기존 실행 분리 테스트.** 임시 pack에 두 HTML을 복사해 첫 snapshot 후 accent 한 값을 변경한다. 같은 run의 hash는 같고 새 run의 hash는 다름을 검사한다. `snapshot_theme` 중 기존 파일이 손상되면 실패해야 한다. 기존 Pretendard 로컬 파일은 출처/라이선스를 확인해 run에 복사하며 없는 굵기는 실제 사용 전 확보한다. 시스템 fallback font로 검증 통과하지 않는다. unittest PASS. 실제 computed style 비교는 Task 8에서 추가한다.

```python
def test_template_changes_only_affect_new_runs(self):
    import shutil
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); pack = root/'pack'
        shutil.copytree(ROOT/'.agents/skills/bio-review-pack/assets', pack/'assets')
        first = snapshot_theme(pack, root/'old')
        src = pack/'assets/note-template.html'
        src.write_text(src.read_text(encoding='utf-8').replace('#3182f6', '#3388ff'), encoding='utf-8')
        resumed = snapshot_theme(pack, root/'old')
        fresh = snapshot_theme(pack, root/'new')
        self.assertEqual(first['templates']['note']['sha256'], resumed['templates']['note']['sha256'])
        self.assertNotEqual(first['templates']['note']['sha256'], fresh['templates']['note']['sha256'])
```
- [ ] **Step 5: 커밋.** `git add .agents/skills/bio-review-video` → `git commit -m "feat: preserve review pack HTML design in video scenes"`.

## Task 4: 원자적 상태·해시 캐시·비용 예약

**Files:** Create `S/scripts/lib/cache.py`, `state.py`, `budget.py`, `S/tests/test_state.py`, `S/assets/defaults.json`.

**Interfaces:**
- `digest(value: dict) -> str`, `file_hash(path: Path) -> str`, `atomic_json(path: Path, value: dict) -> None`.
- `cache_valid(output: Path, receipt: dict, expected_key: str) -> bool`: 입력 key와 output hash 모두 검사.
- `RunStore(run: Path)`의 `lock()` context manager, `load() -> dict`, `save(state: dict) -> None`, `invalidate(stage: str) -> None`.
- `Budget(path: Path, limit_usd: Decimal)`의 `reserve(request_id: str, upper_usd: Decimal) -> bool`, `settle(request_id: str, actual_usd: Decimal | None) -> None`, `remaining() -> Decimal`.

단계 DAG: `inputs → coverage → script → voice → timing → composition → render → verify → publish`. revoice는 coverage/script 검증 후 voice/timing/revoice/render/verify/publish. 각 단계 status는 pending/running/passed/failed/blocked, input_hash/output_hashes/errors를 갖는다. `--review`에서는 script 이후 `awaiting_review`로 종료하고 명시적 승인 기록을 받은 재개만 voice로 간다.

- [ ] **Step 1: 캐시/예산 실패 테스트 작성.**

```python
import tempfile, unittest
from decimal import Decimal
from pathlib import Path
from _util import ROOT
from lib.cache import digest, file_hash, cache_valid
from lib.budget import Budget

class StateTest(unittest.TestCase):
    def test_same_frames_different_content_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'part.mp4'; out.write_bytes(b'old')
            key = digest({'frames':90,'caption':'32 ATP'})
            receipt = {'key':key,'output_sha256':file_hash(out)}
            self.assertTrue(cache_valid(out, receipt, key))
            self.assertFalse(cache_valid(out, receipt, digest({'frames':90,'caption':'30 ATP'})))
            out.write_bytes(b'corrupt')
            self.assertFalse(cache_valid(out, receipt, key))

    def test_unknown_charge_is_not_refunded(self):
        with tempfile.TemporaryDirectory() as d:
            b = Budget(Path(d)/'ledger.json', Decimal('2'))
            self.assertTrue(b.reserve('request-1', Decimal('1.2')))
            b.settle('request-1', None)
            self.assertFalse(b.reserve('request-2', Decimal('0.9')))
```

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_state.py -v`.
- [ ] **Step 3: 원자적 쓰기·실행 lock 구현.** `tempfile.NamedTemporaryFile(dir=path.parent, delete=False)`에 UTF-8 JSON 쓰기→flush→fsync→`os.replace`. canonical JSON은 `sort_keys=True`, `separators=(',', ':')`, `ensure_ascii=False`, `allow_nan=False`를 사용한다. 한 run은 파일 배타 lock으로 단일 writer를 유지하고 같은 프로세스의 병렬 예약은 threading.Lock으로 직렬화한다. Windows에서 숨김 프로세스 사용, stale lock은 PID 생존 확인 없이 삭제하지 않는다. source 변경 시 최초 영향 단계부터만 invalidation한다.

```python
import hashlib, json
def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()
```

- [ ] **Step 4: 비용 ledger와 기본 설정 구현.** Decimal 문자열로 금액을 저장한다. 요청 전 추정 상한을 예약하고 실제 usage가 있으면 정산한다. 불확실한 timeout/전송된 실패 요청은 예약액을 유지한다. retry는 새 request-id로 재예약한다. 가격표에는 모델·단가·검증 날짜·근거를 기록하며 가격/응답 최대 토큰을 모르면 paid request를 시작하지 않는다. 실제 공급자 과금과 차이 가능성을 보고한다. 샘플/ASR도 동일 ledger를 사용한다.

```json
{"schema_version":1,"provider":"vertex-ai-express","model":"gemini-2.5-flash-tts","voice":"Aoede","language":"ko-KR","budget_usd":"2.00","width":1920,"height":1080,"fps":30,"sample_rate":24000,"tts_concurrency":2,"max_attempts":4,"revoice_speed_min":0.8,"revoice_speed_max":1.25}
```

- [ ] **Step 5: 재개/경쟁 테스트 후 커밋.** 2개 thread가 각각 $1.2를 예약할 때 하나만 True임을 검사한다. 중간 save 실패를 주입해 이전 run.json이 유효함을 검사한다. running 단계가 재시작되면 산출물 hash 검증 뒤 passed 또는 pending으로 복구하는지 검사한다. 테스트 PASS 후 `git add .agents/skills/bio-review-video` → `git commit -m "feat: add resumable video state and API budget ledger"`.

```python
def test_parallel_reservations_do_not_overspend(self):
    from concurrent.futures import ThreadPoolExecutor
    with tempfile.TemporaryDirectory() as d:
        b = Budget(Path(d)/'ledger.json', Decimal('2'))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda i:b.reserve(str(i), Decimal('1.2')), range(2)))
        self.assertEqual(sorted(results), [False, True])

def test_interrupted_atomic_write_preserves_previous_state(self):
    import json
    from unittest.mock import patch
    from lib.cache import atomic_json
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)/'run.json'
        atomic_json(path, {'stage':'voice','status':'passed'})
        with patch('lib.cache.os.replace', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError): atomic_json(path, {'stage':'render','status':'running'})
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['stage'], 'voice')
```

## Task 5: Vertex Aoede 문단 음성과 재시도

**Files:** Create `S/scripts/lib/vertex_tts.py`, `S/assets/vertex-direction.txt`, `S/tests/test_tts.py`, `S/references/voice-and-budget.md`.

**Interfaces:** `make_payload(text: str, config: dict, direction: str) -> dict`; `synthesize(items: list[dict], run: Path, config: dict, budget: Budget, transport, sleep) -> list[dict]`. transport는 `(payload: dict) -> dict`, HTTP 오류는 `VertexError(status: int | None)`로 정제한다. 반환 audio record `{id,path,samples,rate,key,sha256,usage}`. credentials loader `load_key(env_file: Path | None) -> str`는 env 우선이며 명시 경로 밖 `.env` 탐색 금지.

- [ ] **Step 1: 실제 네트워크 없는 테스트 작성.**

```python
import base64, tempfile, unittest
from pathlib import Path
from decimal import Decimal
from _util import ROOT
from lib.vertex_tts import synthesize, VertexError
from lib.budget import Budget

class TtsTest(unittest.TestCase):
    def test_retry_and_resume_do_not_repeat_success(self):
        calls = []
        def fake(payload):
            calls.append(payload)
            if len(calls) == 1: raise VertexError(429)
            return {'candidates':[{'finishReason':'STOP','content':{'parts':[{
                'inlineData':{'mimeType':'audio/L16;rate=24000',
                             'data':base64.b64encode(b'\x10\x00'*24000).decode()}}]}}],
                'usageMetadata':{'promptTokenCount':10,'candidatesTokenCount':25}}
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            cfg = {'model':'gemini-2.5-flash-tts','voice':'Aoede','language':'ko-KR',
                   'direction':'원고만 읽으세요.','pronunciation':{},'max_output_tokens':2048,
                   'max_attempts':4,'tts_concurrency':1,
                   'price':{'input_per_million':'1','output_per_million':'20','request_upper_usd':'0.10'}}
            b = Budget(run/'cost-ledger.json', Decimal('2'))
            items = [{'id':'seg-1','text':'ATP가 만들어집니다.'}]
            first = synthesize(items, run, cfg, b, fake, lambda _: None)
            second = synthesize(items, run, cfg, b, fake, lambda _: None)
            self.assertEqual(len(calls), 2)
            self.assertEqual(first[0]['sha256'], second[0]['sha256'])
            self.assertEqual(first[0]['samples'], 24000)
```

테스트 단가는 fake 값이며 운영 가격으로 복사하지 않는다. 실제 단가는 구현 시 공식 Vertex 가격으로 검증해 기록한다.

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_tts.py -v`.
- [ ] **Step 3: payload와 승인 말투 이관.** endpoint는 `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent`, `x-goog-api-key` header다. 요청 파일/CLI 인자에 키를 넣지 않는다.

```python
def make_payload(text, config, direction):
    return {'contents':[{'role':'user','parts':[{'text':direction+'\n\n원고:\n'+text}]}],
        'generationConfig':{'responseModalities':['AUDIO'],
          'maxOutputTokens':config['max_output_tokens'],
          'speechConfig':{'languageCode':'ko-KR',
            'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':config['voice']}}}}}
```

`vertex-direction.txt`의 내용:

```text
한국어 생명과학 복습 영상의 내레이터입니다. 이미 수업을 들은 대학생에게 설명하듯 차분하고 명료하며 자연스럽게 말하세요. 기계적으로 끊지 말고 의미 단위로 호흡하세요. 지나치게 느리지 않은 보통 속도입니다. 강조는 절제하고 배경음이나 효과음을 넣지 마세요. 다음 원고만 빠짐없이 읽고 안내 문장은 읽지 마세요.
```

- [ ] **Step 4: PCM 검증/재시도 구현.** 정규화 발음 적용 후 hash에 원문·규칙·모델·voice·direction·전체 generationConfig 포함. STOP 아닌 종료, 빈/홀수 바이트 PCM, 잘못된 base64/MIME/샘플률/채널은 실패. WAV는 실제 header로 검증, PCM16 mono 24k로 저장한다. 길이는 실측하고 0915의 2–75초 규칙을 일반 실패 규칙으로 복사하지 않는다. 긴 발화는 script 단계에서 의미 단위로 나누고 truncation은 정상 캐시로 저장하지 않는다. 429/500/502/503/504/timeout만 최대 4회, 대기 5/10/20초(+제한된 jitter), 연속 429면 동시성을 1까지 줄인다. 401/403/404는 즉시 구체적인 인증/모델 오류로 정지한다. ledger 예약 실패는 `blocked:budget`로 종료한다.
- [ ] **Step 5: 보안과 손상 테스트 후 커밋.** fake transport의 예외에 `SECRET_TEST_VALUE`를 넣고 저장 로그·run.json에 그 문자열이 없음을 검사한다. MIME 오류·부분 응답은 WAV receipt가 생기지 않아야 한다. 목소리 변경으로 cache miss, 기존 성공 WAV는 유지되는지 확인한다. unittest PASS 후 `git add .agents/skills/bio-review-video` → `git commit -m "feat: synthesize cached Vertex Aoede narration"`.

## Task 6: 샘플 기준 시간표와 템플릿 장면 조립

**Files:** Create `S/scripts/lib/timing.py`, `composition.py`, `S/tests/test_timing.py`, `test_composition.py`, `S/references/narration-and-motion.md`.

**Interfaces:** `build_timeline(m: dict, audio: list[dict], fps: int = 30) -> dict`; `write_subtitles(timeline: dict, run: Path) -> None`; `assemble(m: dict, timeline: dict, theme: dict, run: Path) -> list[dict]`. timeline은 rate/fps/total_samples/total_frames, scenes `{id,start_sample,end_sample,first_frame,last_frame}`, segments `{id,scene_id,start_sample,end_sample,caption,text}`를 가진다. 렌더 parts는 `{id,entry,frames,key}`. 에이전트는 `source/scene-fragments/<scene-id>.html`과 `<scene-id>.motion.json`을 작성한다.

- [ ] **Step 1: 누적 반올림·빈 구간 실패 테스트 작성.**

```python
import unittest
from _util import minimal_manifest
from lib.timing import build_timeline

class TimingTest(unittest.TestCase):
    def test_many_short_segments_have_no_rounding_drift(self):
        m = minimal_manifest()
        proto = m['segments'][0]
        m['segments'] = [dict(proto, id=f'seg-{i}') for i in range(1000)]
        audio = [{'id':s['id'],'samples':1001,'rate':24000} for s in m['segments']]
        t = build_timeline(m, audio)
        self.assertEqual(t['total_frames'], (t['total_samples']*30+23999)//24000)
        self.assertEqual(t['segments'][1]['start_sample']-t['segments'][0]['start_sample'], 1001+7200)
        self.assertEqual(sum(x['last_frame']-x['first_frame'] for x in t['scenes']), t['total_frames'])
```

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_timing.py -v`.
- [ ] **Step 3: 정수 시간표 구현.** 장면 도입 13200샘플(0.55s), 문단 뒤 7200샘플(0.3s), 장면 끝 18000샘플(0.75s)을 기본값으로 쓴다. 시작/종료는 누적 정수 sample이고 frame 변환은 전역 좌표에서만 한다. 마지막 frame만 ceil. SRT는 실제 음성 구간만, 화면 핵심 자막은 문단 pause까지 유지 가능하다. 음성 총 길이와 chapter 시작을 동일 시간표에서 도출한다.

```python
def frame_at(sample, rate=24000, fps=30):
    return (sample * fps * 2 + rate) // (2 * rate)

def end_frame(sample, rate=24000, fps=30):
    return (sample * fps + rate - 1) // rate
```

- [ ] **Step 4: HyperFrames 조립 계약 구현.** 구현 시 `hyperframes`, `hyperframes-core`, `hyperframes-animation` 스킬을 읽는다. 레지스트리가 필요한 도식은 해당 검색 지침을 따른다. fragment는 템플릿 클래스/semantic SVG를 사용하고 scripts/events/외부 URL을 허용하지 않는다. motion JSON은 `{target,segment_id,kind,from,to,duration_s}` 배열; kind는 reveal/move/count/highlight/path. 실제 selector가 존재해야 하며 모두 segment 시간에 상대적으로 실행한다. 아래처럼 paused timeline에 한 번 연결한다.

```javascript
const tl = gsap.timeline({paused:true});
tl.fromTo('#atp-count', {textContent:0},
  {textContent:32,duration:1,snap:{textContent:1},ease:'none'}, 0.55);
window.__timelines['scene-atp'] = tl;
```

조립기는 scene별 `data-composition-id`, 실제 duration, 1920×1080, root 하위 clip/track를 작성한다. 장면/음성/핵심 자막 각각 별도 트랙. local CSS/fonts/vendor를 stage하고 네트워크 없이 로드되게 한다. raw 사용자 문장은 HTML escape하고 경로는 허용된 로컬 asset만 사용한다. 임의 setInterval/random/wall-clock 애니메이션을 허용하지 않는다.
- [ ] **Step 5: 조립 테스트 및 커밋.** 최소 fixture에 `<h3 id="atp-count">32</h3>` fragment와 위 count motion을 넣어 assemble하고 HTML에 `data-theme="dark"`, `data-composition-id="scene-atp"`, 실제 duration이 있는지 검사한다. 존재하지 않는 target, 빈 audio, 0샘플, 자막 미매핑은 ValueError를 검사한다. 두 unittest 파일 PASS 후 `git add .agents/skills/bio-review-video` → `git commit -m "feat: build sample accurate review video compositions"`.

## Task 7: GPU 장면 렌더와 화면을 보존하는 revoice

**Files:** Create `S/scripts/lib/render.py`, `revoice.py`, `S/tests/test_render.py`, `test_revoice.py`.

**Interfaces:** `choose_backend(probes: list[dict]) -> dict`; `render_parts(parts: list[dict], run: Path, backend: dict) -> list[Path]`; `mux(parts: list[Path], audio: list[dict], timeline: dict, destination: Path) -> None`; `retime_input(timeline: dict) -> dict`; `plan_revoice(old: dict, new: dict, source_hash: str, unchanged_scenes: set[str]) -> list[dict]`. 반환 windows는 `{scene_id,source_first_frame,source_last_frame,first_frame,last_frame,mode,key}`이며 mode는 retime/rerender다. backend는 `{encoder,capture_gpu,decode_gpu,workers,tool_versions}`다. `retime_input`은 Task 6 timeline의 장면/문단 경계를 intro·각 문단(pause 포함)·tail로 분할해 `{fps,windows:[{id,scene_id,first_frame,last_frame}]}`을 반환한다. `plan_revoice`에는 이 변환값을 넣는다. 테스트의 단일 window는 이 계약의 최소 사례이며 실제 사용 시에는 안정적인 window ID로 두 입력을 대응시킨다.

- [ ] **Step 1: CPU fallback/revoice 경계 실패 테스트 작성.**

```python
import unittest
from _util import ROOT
from lib.render import choose_backend
from lib.revoice import plan_revoice

class RenderTest(unittest.TestCase):
    def test_broken_nvenc_uses_measured_cpu(self):
        b = choose_backend([
          {'encoder':'h264_nvenc','ok':False,'seconds':0,'workers':1,'capture_gpu':False,'decode_gpu':False,'tool_versions':{}},
          {'encoder':'libx264','ok':True,'seconds':2,'workers':1,'capture_gpu':False,'decode_gpu':False,'tool_versions':{}}])
        self.assertEqual(b['encoder'], 'libx264')

    def test_extreme_revoice_requires_scene_render(self):
        old = {'fps':30,'windows':[{'id':'a-seg-1','scene_id':'a','first_frame':0,'last_frame':30}]}
        new = {'fps':30,'windows':[{'id':'a-seg-1','scene_id':'a','first_frame':0,'last_frame':90}]}
        w = plan_revoice(old, new, 'original-sha256', {'a'})
        self.assertEqual(w[0]['mode'], 'rerender')
```

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_render.py -v`.
- [ ] **Step 3: probe와 renderer 구현.** CPU와 NVENC로 각각 2초·60프레임 테스트를 실행하고 ffprobe와 전체 decode로 성공을 확인한다. 브라우저 캡처 GPU와 인코더 GPU는 별도로 판정한다. HyperFrames의 GPU 플래그만으로 RTX를 사용했다고 기록하지 않는다. 성공한 경로에서 worker 1개부터 실측하고 메모리 부족·timeout·속도 저하가 있으면 늘리지 않는다. 최대 worker 수는 CPU/RAM/VRAM과 실측 결과로 제한한다. FFmpeg는 인자 배열과 `shell=False`로 호출한다. 다음은 probe 호출의 핵심 코드다.

```python
cmd = ['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=black:s=1920x1080:r=30',
       '-frames:v','60','-an','-c:v',encoder,'-pix_fmt','yuv420p',str(probe_path)]
```

GPU 선호 판단은 실제 결과를 사용한다. HyperFrames CLI는 설치된 Node entry를 직접 실행해 Windows `.cmd` 인자 재해석을 피한다. CLI version/help를 기록하고 `--gpu --browser-gpu --workers 1`은 지원되는 GPU 경로에서만 전달한다. cache key는 part HTML·CSS·font·SVG·vendor의 transitive hashes, template hash, timeline, backend 설정과 버전을 포함한다. 잘린 MP4는 hash/probe/decode 실패로 다시 렌더한다.

- [ ] **Step 4: mux와 revoice 구현.** 비디오만 concat하고 모든 문단 PCM을 전역 start_sample에 배치해 최종 AAC를 한 번만 만든다. concat 파일에는 controlled basename(`part-0001.mp4`)만 사용해 입력 경로의 작은따옴표 문제를 없앤다. 예산·시간표·원본을 수정하지 않는다. 임시 final을 전체 검사한 뒤 목적 파일로 교체한다.

```python
speed = (window['source_last_frame'] - window['source_first_frame']) / max(1, window['last_frame'] - window['first_frame'])
needs_render = (window['scene_id'] not in unchanged_scenes or
                not 0.8 <= speed <= 1.25 or window['last_frame'] <= window['first_frame'])
```

retime은 source의 video만 `-an`, `setpts`/fps/명시 frame count로 생성하며 source hash를 key에 넣는다. old/new windows는 문단 ID와 intro/pause/tail로 정렬하고 누락/역순/겹침은 오류다. 0frame은 무작정 1frame으로 늘리지 않고 해당 장면 재조립한다. revoice용 기존 소스가 없으면 rerender가 필요한 이유를 보고하고 원본을 유지한다. speed 임계값은 보수적인 기본값이며 임계값 안이어도 화면 가독성 검사를 통과해야 한다.
- [ ] **Step 5: 실제 작은 영상 테스트 후 커밋.** 테스트 임시 폴더 이름을 `생명 O'Brien`으로 사용하고 PCM + 60frame color fixture를 CPU 렌더/mux/전체 decode한다. 원본 SHA256 전후 일치와 출력 audio stream 1개를 검사한다. source hash만 바뀌면 window key가 바뀌는 테스트도 추가한다. test_render/test_revoice PASS; GPU가 있으면 같은 tiny test를 NVENC로 실행하며 없으면 명시적 skip. `git add .agents/skills/bio-review-video` → `git commit -m "feat: render review videos and preserve visuals during revoice"`.

```python
def test_source_hash_is_part_of_revoice_cache(self):
    t = {'fps':30,'windows':[{'id':'a-seg-1','scene_id':'a','first_frame':0,'last_frame':30}]}
    left = plan_revoice(t, t, 'source-a', {'a'})
    right = plan_revoice(t, t, 'source-b', {'a'})
    self.assertNotEqual(left[0]['key'], right[0]['key'])

def test_zero_frame_window_requires_scene_rerender(self):
    old = {'fps':30,'windows':[{'id':'a-seg-1','scene_id':'a','first_frame':0,'last_frame':30}]}
    new = {'fps':30,'windows':[{'id':'a-seg-1','scene_id':'a','first_frame':0,'last_frame':0}]}
    self.assertEqual(plan_revoice(old, new, 'source-a', {'a'})[0]['mode'], 'rerender')
```

## Task 8: 템플릿 비교·편집 소스·최종 파일을 분리해 검증

**Files:** Create `S/scripts/lib/verify.py`, `S/tests/test_verify.py`, `S/tests/browser_check.mjs`, `S/references/rendering-and-verification.md`.

**Interfaces:** `verify_media(path: Path, expected: dict) -> dict`, `verify_run(run: Path, m: dict, reports: dict) -> dict`, `publish_latest(run: Path, report: dict) -> None`. report `{content,audio,visual,source,media,sync,complete}`; 각 영역 `{status:passed|failed|unverified,evidence:list[str],errors:list[str]}`. complete는 모두 passed일 때만 True.

- [ ] **Step 1: wrapper만 성공한 경우와 latest 보호 테스트 작성.**

```python
import tempfile, unittest
from pathlib import Path
from _util import minimal_manifest
from lib.verify import verify_run, publish_latest

class VerifyTest(unittest.TestCase):
    def test_wrapper_pass_does_not_pass_source(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)/'0915'/'run-1'; run.mkdir(parents=True)
            reports = {k:{'status':'passed','evidence':[],'errors':[]}
                       for k in ('content','audio','visual','media','sync')}
            reports['source'] = {'status':'unverified','evidence':['wrapper passed'],'errors':[]}
            report = verify_run(run, minimal_manifest(), reports)
            self.assertFalse(report['complete'])
            with self.assertRaises(ValueError): publish_latest(run, report)
            self.assertFalse((run.parent/'latest.json').exists())
```

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_verify.py -v`.
- [ ] **Step 3: 실제 미디어 검사 구현.** ffprobe의 1920×1080,30fps,frame 수,mono24k audio, duration차를 검사한다. audio/video 끝 차이는 1frame+AAC 1packet(1024/24000s) 이내. ffmpeg 전체 decode의 exit0과 stderr를 저장한다. PCM 무음/클리핑/길이 outlier는 segment별 기록한다. 숫자·약어가 있는 대표 문단은 예산 내 전사로 점검하고 API 미사용이면 직접 청취 증거를 남긴다. 둘 다 없으면 audio semantic 검증은 unverified다. 5개 표본으로 전체 낭독 검증을 주장하지 않는다.

```python
passed = all(reports.get(k, {}).get('status') == 'passed'
             for k in ('content','audio','visual','source','media','sync'))
result = dict(reports, complete=passed)
```

- [ ] **Step 4: 템플릿/browser 비교 구현.** 원본 note/review fixture와 generated scene에 같은 텍스트·layer·tag·figure·표를 넣고 브라우저에서 dark/light OS 조건 모두 검사한다. 아래 JS 연산을 browser_check.mjs에서 페이지 context로 실행해 JSON evidence를 저장한다.

```javascript
await document.fonts.ready;
const rootStyle = getComputedStyle(document.documentElement);
const keys = ['--bg','--surface','--ink','--ink-2','--line','--accent','--accent-ink','--warn','--prof','--supp','--danger'];
const tokens = Object.fromEntries(keys.map(k => [k, rootStyle.getPropertyValue(k).trim()]));
const caption = document.querySelector('.video-caption');
const box = caption?.getBoundingClientRect();
const evidence = {tokens, fontReady:document.fonts.check('32px Pretendard'),
  captionFits:!caption || (caption.scrollHeight <= caption.clientHeight && box.bottom <= 1080)};
```

브라우저 실행 API는 설치된 HyperFrames 지원 snapshot/check 또는 실제 설치된 Playwright로 연결하고 dependency version을 고정한다. 토큰만 같다고 visual passed를 자동 확정하지 않는다. 원본과 영상의 같은 semantic 컴포넌트를 나란히 촬영하여 글꼴 위계·선·배지·주의·보충 색/모양을 비교한다. 글자 크기/넓이는 영상 어댑터의 허용된 차이다. 각 장면 도입/중간/끝과 자막 전환 직전·직후를 seek해 잘림·겹침·글자 최소크기·수식 준비·동작을 확인한다. 상호작용 위젯은 기본/변화/결론 상태를 각각 확인한다. 랜덤 seek 순서에서도 동일 frame이 나와야 한다. 기대 bbox 예외는 source/QA에 명시하며 본문-자막 겹침은 허용하지 않는다.
- [ ] **Step 5: source check와 latest 승격 검증.** 실제 생성한 편집 composition 전부에 HyperFrames check를 적용한다. wrapper check는 별도 evidence로만 저장한다. 하나라도 timeout이면 source=unverified. media decoder 오류/기존 latest 있음/long caption 실패의 경우 기존 latest bytes가 유지되는 테스트를 추가한다. 통과 시 atomic_json으로 latest 갱신한다. unittest PASS 후 `git add .agents/skills/bio-review-video` → `git commit -m "feat: gate video publishing on source and output verification"`.

## Task 9: 사용자 스킬·CLI와 비용 없는 전체 회귀 실행

**Files:** Create `S/SKILL.md`, `S/agents/openai.yaml`, `S/scripts/video.py`, `S/tests/test_cli.py`; Finalize `S/references/*.md` and `S/assets/defaults.json`.

**Interfaces:** `main(argv: list[str] | None = None) -> int`. 사용자 slash 인자는 스킬이 CLI stage 명령으로 번역한다. CLI는 `prepare`, `check`, `tts`, `assemble`, `render`, `verify`, `resume`, `revoice` subcommand를 제공한다. 모든 명령은 `--repo`/`--run` 중 필요한 절대 경로를 받는다. prepare는 selector, `--review`, `--env-file`을 받는다. 비밀 파일 경로는 저장해도 값은 저장하지 않는다. API 작업은 transport dependency를 테스트에서만 fake로 교체한다.

에이전트가 대본과 도식을 작성해야 하므로 CLI가 노트만 받아 모든 콘텐츠를 스스로 창작한다고 설명하지 않는다. 스킬은 prepare 결과를 읽고 manifest/scene fragments를 만든 뒤 반복 가능한 stage 명령을 순서대로 호출한다. resume은 최초 미완료 단계와 필요한 수동 콘텐츠 작업을 반환하고 스킬이 그 단계부터 이어간다.

- [ ] **Step 1: CLI 실패 테스트 작성.**

```python
import tempfile, unittest
from pathlib import Path
from _util import ROOT
from video import main

class CliTest(unittest.TestCase):
    def test_prepare_is_free_and_bad_range_is_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            notes = repo/'복습노트'/'0915'; notes.mkdir(parents=True)
            (notes/'정리노트_0915_test.md').write_text('수업 기준 32 ATP', encoding='utf-8')
            self.assertEqual(main(['prepare','--repo',str(repo),'0915']), 0)
            self.assertNotEqual(main(['prepare','--repo',str(repo),'0931']), 0)
```

prepare는 source 발견/run 생성까지만 하므로 테스트 repo에 템플릿이 없어도 되며, theme 단계에서는 실제 pack을 요구한다. 테스트 중 env API 키가 있어도 prepare는 네트워크를 호출하면 실패하도록 urllib mock을 사용한다.

- [ ] **Step 2: FAIL 확인.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -p test_cli.py -v`.
- [ ] **Step 3: CLI wiring과 스킬 본문 구현.** argparse subparser로 위 명령을 dispatch하고 제어 flow에 `require_ready`, RunStore, Budget을 연결한다. 입력이 잘못되면 exit2, 처리 실패 exit1, 정상/명시적 review 대기 exit0. 출력은 stage/state/run 경로/다음 필요한 작업의 JSON을 제공한다. 기본 auto 실행은 새 질문 없이 정해진 작업을 진행하고 인증/내용 충돌/예산 같은 실제 장애만 구체적으로 보고한다.

`SKILL.md` frontmatter와 핵심 절차:

```yaml
---
name: bio-review-video
description: 완성된 생명과학 복습노트를 review-pack HTML 템플릿의 다크모드 디자인과 한국어 Aoede 음성을 사용하는 복습 영상으로 만든다. 복습 영상 제작·영상 복습·기존 영상의 목소리 교체 요청 또는 /bio-review-video 호출에 사용한다. 일반 정리노트 작성은 bio-review-pack을 사용한다.
---
```

본문은 입력/coverage/대본/음성/실측/장면/렌더/QA/전달의 9단계로 적고 각 단계에 해당 CLI 명령과 reference를 연결한다. 시작 시 HyperFrames entry skill을 읽고 프로젝트 workflow를 정하되, 이미 승인된 dark template/Aoede/auto 선호를 다시 묻지 않는다. voice 변경에만 sample을 제시한다. HTML template source of truth와 과거 생성물 보존을 맨 앞에 둔다.

```yaml
interface:
  display_name: "생명과학 복습 영상"
  short_description: "복습팩의 화면 디자인과 전체 내용을 유지하는 한국어 영상"
  default_prompt: "Use $bio-review-video to turn the selected biology review notes into a complete review video."
```

- [ ] **Step 4: 전체 회귀 실행.** `python -m unittest discover -s .agents/skills/bio-review-video/tests -v`를 실행한다. 2장면/3문단 fixture, 로컬 PCM, note/review 템플릿, CPU 1080p MP4로 prepare→검증→latest까지 수행한다. 중간 TTS429, render 실패, 긴 자막 실패를 각각 주입하고 성공 캐시 유지 및 latest 보호를 확인한다. 기존 0915는 실제 source discovery/coverage 시범 검토만 하고 full 재생성이나 유료 TTS를 실행하지 않는다. 기존 template 원본 hash 전후 비교 및 `python -m unittest discover -s .agents/skills/bio-review-pack/tests -p test_template.py -v`도 실행한다.
- [ ] **Step 5: 사용 안내와 최종 커밋.** `references/rendering-and-verification.md`에 실제 설치 필요 조건, 테스트 실행 명령, GPU/CPU 경로, source/최종 media의 검증 범위, $2 예산 중단 재개 절차를 기록한다. paid request에 필요한 가격표가 없으면 운영 준비 상태를 별도 미확인으로 보고한다. fixture 통과를 새 강의 전체 영상 품질 보증으로 과장하지 않는다. `git add .agents/skills/bio-review-video` → `git commit -m "feat: expose biology review video skill and end to end workflow"`.

## 검토와 완료 체크리스트

| 설계 요구 | 구현/검증 위치 |
|---|---|
| 전용 스킬·호출·자동/검토 모드 | Task 1, 4, 9 |
| 모든 내용·문항·HTML/MD 충돌·과거 안내 | Task 2 |
| review-pack HTML 템플릿·다크모드·Pretendard 보존 | Task 3, 6, 8 |
| Aoede/Vertex/비밀·비용·429 | Task 4, 5 |
| 실측 길이·의미 동작·자막 | Task 6 |
| 해시 캐시·원자 저장·재개 | Task 4–7 |
| RTX 실측/CPU 대체/전역 설정 미변경 | Task 7 |
| 원본 보존 revoice·부분 재렌더 | Task 7 |
| 모든 장면·소스/최종 파일 분리 QA | Task 8 |
| MP4/SRT/chapters/latest·회귀 fixture | Task 8, 9 |

계획 자체의 점검: schema field와 함수 명칭을 Task 간 대조하고, 요구 사항마다 위 소유 Task를 배정했다. Review Focus의 다섯 조건은 각 소유 Task에 실패 테스트/실행 절차를 넣었다. 기존 코드에 유료 예산·다크 템플릿 자동 연동이 이미 구현되어 있다고 가정하지 않는다. 라이브 API/실제 렌더 성능/새 코드 테스트는 아직 실행하지 않았으며 구현 단계의 검증 항목이다.

## 실행 방식 인계

추천은 **Native**: 같은 manifest·시간표·캐시 인터페이스를 공유하는 9개 작업이므로 한 구현자가 순차적으로 작업하고 마지막에 새 리뷰어가 전체를 검토하는 방식이 효율적이다. **Subagent-driven**을 선택하면 Task별 새 구현자와 리뷰어가 각 경계를 검토하고 마지막에 전체 검토를 한다. 사용자가 계획과 실행 방식을 확인하기 전 구현을 시작하지 않는다. 이는 writing-plans의 Execution Handoff 요구다.
