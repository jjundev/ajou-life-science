# 5장 v4 대표 3문항 해설 시범 적용 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** P2·P3·P7의 해설을 새 공통 지침으로 시범 재작성하고, 판단 기준의 명확성·선지와 근거의 대응·불필요한 반복을 전후 비교한다.

**Architecture:** 기존 `bio-problem-explain`의 extract/build/check를 재사용한다. forecast 입력은 15문항 전체를 유지하고, 별도 RUN에서 세 문항의 설명 조각만 교체한다. 기존 발행 파일을 바꾸지 않는 시범본과 비교 보고서로 끝내며, 정식 재발행은 별도 작업이다.

**Tech Stack:** Python 3.10+, 기존 해설 CLI·로컬 템플릿/KaTeX/Pretendard, Playwright 또는 사용 가능한 로컬 브라우저, PDF 렌더링 도구.

**Spec:** 커밋 `d82975f`의 `.agents/skills/bio-problem-explain/references/authoring.md`, `references/verification.md`를 공통 내용 규격으로 사용한다. 이 계획의 Global Constraints가 이번 3문항 시범 범위를 정한다. 기존 전체 해설 설계는 `docs/superpowers/specs/2026-10-13-bio-problem-explain-design.md`이며, 구역 구성은 최신 공통 지침이 우선한다.

## Global Constraints

- 이번 호출은 **계획 작성만** 한다. 아래 단계는 사용자가 실행 방식을 선택한 다음 수행한다.
- 대상은 `웹과제예상/5장/복습문제_5장_웹과제예상_v4.html`의 P2·P3·P7이다. 문제·보기·수치·순서·정답키를 고치거나 새 문제를 출제하지 않는다.
- 기존 `웹과제예상/5장/` 전체와 읽은 수업 근거의 바이트를 보존한다. 원래 문제해설 HTML·MD·그림·자료·검토 기록도 덮어쓰지 않는다.
- `understand → recall → solve → verify`는 필수이며, start/pitfall/retry는 별도의 도움이 있을 때만 쓴다. 문항 결함·인쇄 정답 오류의 기존 공개·대처 규칙은 유지한다.
- P2·P3·P7의 모든 A–E, 총 15선지를 검토한다. 정답뿐 아니라 선택·제외의 판단 과정을 설명한다.
- 나머지 12개 조각은 복사한 바이트 그대로 둔다. 전체 15문항을 담은 시범 HTML이 만들어져도 새로 검토한 범위는 세 문항뿐이다.
- `publish`·`rerender`는 실행하지 않는다. `source.json`·SourcePack·manifest의 문항 집합을 3개로 줄이거나 기존 검토를 이식하지 않는다.
- source_visual/content/independent/browser의 실제 시범 검토를 모두 한다. 정답·기존 풀이·새 해설을 독립 재풀이자에게 제공하지 않는다.
- 조각 수정 시 build/check 및 시범 검토를 다시 한다. 최초 검토 후 수정·재검토는 최대 2회이고, 미해결이면 실패/보류로 보고한다.
- 분량 감소율이나 구역 수를 성과 기준으로 강제하지 않는다. 학생의 실제 숙달이나 학습 효과도 추정하지 않는다.
- 생산 코드·템플릿·공통 스킬·기존 문구 비교 테스트의 별도 실패는 이번 시범에서 수정하지 않는다.
- 커밋·푸시는 이번 실행에 별도로 포함해 달라는 요청이 있을 때만 한다. 이전 작업에 대한 커밋 허가는 이 계획으로 이어지지 않는다.

## Review Focus

1. **선지와 근거 불일치:** P3의 A/C/E에 서로 다른 주장을 설명하는 근거가 붙은 현재 상태를 재현하고, 수정 후 각 원문 주장과 일치하는지 검토한다 — Task 1 기준선, Task 2의 R2.
2. **필요조건의 역방향 확정:** P7에서 염기 비율이 같은 시료의 가닥 수까지 확정하는 문장이 본문·요약에 남지 않게 한다 — Task 2의 R3 및 Task 3 독립 재풀이.
3. **용어의 뜻과 답 적합성 혼동:** P2에서 ‘모호성’과 ‘비모호성’을 뒤집거나, 보편성의 올바른 정의 자체를 틀린 사실로 표현하지 않는다 — Task 2의 R1.
4. **부분 검토를 전체 승인으로 바꾸는 오류:** 12개 미수정 조각과 기존 발행 파일의 보존, 전체 review의 미승인을 검사한다 — Task 2 보존 검사, Task 3 범위 검사.
5. **stage의 상대 링크와 화면 오류:** 최종 발행 위치를 기준으로 작성된 원 문제·노트 링크를 임시 stage 경로에서 잘못 검사하지 않는다 — Task 3의 로컬 경로 매핑 및 4개 화면 조합.

---

## File Structure and Interfaces

경로는 저장소 루트 기준이다. 실행 시 `REPO`는 실제 checkout의 절대 경로로 정한다. 여러 셸 호출 사이에 변수가 유지된다고 가정하지 말고 아래 변수 값을 실행 기록에 절대 경로로 남겨 다시 사용한다.

| 기호/파일 | 역할 |
|---|---|
| `SKILL = REPO/.agents/skills/bio-problem-explain` | 읽기 전용 공통 해설기 |
| `SOURCE = REPO/웹과제예상/5장/복습문제_5장_웹과제예상_v4.html` | 15문항과 버전 문맥을 추출할 입력 |
| `PUBLISHED = REPO/웹과제예상/5장/.pack/자료_문제해설_5장_웹과제예상_v4` | 기존 조각·검토 기록, 읽기 전용 |
| `RUN = REPO/tmp/bio-ch5-v4-explanation-pilot-<고유값>` | 비어 있는 고유 작업 폴더. `tmp/`는 이미 gitignore 대상 |
| `RUN/pilot-state.json` | 기준선 해시·시범 ID·변경 조각 검사 입력 |
| `FOLDER = load_run(RUN)[0]['folder']` | extract가 정한 실제 하위 경로. 이름을 추측하지 않는다 |
| `FOLDER/explanations/p2.html`, `p3.html`, `p7.html` | 시범에서 수정할 유일한 설명 조각 |
| `FOLDER/evidence/source-audit.md` | 선지별 문제점·근거 자료/쪽·해시·공개할 결함 |
| `FOLDER/stage/<build ID>/` | 기존 CLI가 만든 15문항 시범 HTML·MD·로컬 자원 |
| `RUN/pilot-review.json` | 세 문항에 한정된 네 검토와 검토한 산출물 해시 |
| `RUN/screenshots/` | 데스크톱/모바일, light/dark 확인 이미지 |
| `docs/superpowers/reviews/2026-10-19-bio-ch5-v4-explanation-pilot.md` | 실행 시 새로 작성할 비교 보고서. 이미 있으면 덮어쓰지 말고 고유 접미사를 붙인다 |

새 생산 코드나 스키마를 만들지 않는다. 필요한 보존 검사·미리보기 도우미는 RUN 안의 일회성 도구로 둔다. 이번 계획 문서 외의 파일은 계획 단계에서 만들지 않는다.

## Task 1: 기준선과 세 문항의 근거를 고정하기

**Files:** 읽기 `SOURCE`, `PUBLISHED/fragments/p1.html`~`p15.html`, `.pack/v4/pack.json`, `.pack/v4/blueprint.md`; 생성 `RUN/pilot-state.json`, `FOLDER/evidence/source-audit.md`.

**Interfaces:** `mpe_cli.load_run(run) -> list[dict]`의 단일 item과 그 `pack: SourcePack`을 소비한다. 다음 단계에 `pilot-state.json`의 `selected_ids`, `protected_hashes`, `fragment_hashes`와 원문을 대조한 근거 기록을 제공한다. `protected_hashes`는 기존 5장 폴더의 모든 파일 및 실제 읽은 수업 근거의 저장소 상대 경로→SHA-256, `fragment_hashes`는 p1~p15→기존 조각 바이트의 SHA-256이다.

- [ ] **Step 1: 시작 상태와 읽기 전용 보호 목록을 기록한다.**

`git status --short`, HEAD, 공통 규칙 버전을 기록한다. 고유 RUN을 만들고 기존 5장 폴더 전체의 파일 집합·해시와 15개 조각의 해시를 `pilot-state.json`에 저장한다. `selected_ids`는 `['p2', 'p3', 'p7']`로 고정한다. 이번 조사에서 입력 HTML의 SHA-256은 `8296aacece14bd005ffd91020ebc28621bd8f9ab3bda3b0cea433187e9d0adc4`였다. 실행 시 다르면 이 계획의 기준선을 그대로 재사용하지 않고 차이를 조사한다.

- [ ] **Step 2: 기존 CLI로 전체 입력을 추출하고 기존 조각 15개를 복사한다.**

```sh
python3 "$SKILL/scripts/mpe_cli.py" extract --repo "$REPO" --target "$SOURCE" --run "$RUN"
```

extract는 빈 RUN만 허용하므로 Step 1의 상태 JSON은 우선 RUN 밖의 임시 파일에 쓰고, extract 성공 후 `RUN/pilot-state.json`으로 넣는다. `load_run(RUN)`으로 FOLDER를 찾고 `PUBLISHED/fragments/`의 15개 조각을 바이트 그대로 `FOLDER/explanations/`에 복사한다. `source.json`은 편집하지 않는다. 예상: forecast profile, p1~p15 정확히 15개, 대상 세 문항의 답 키는 각각 B/D/B.

- [ ] **Step 3: 현재 해설에서 실패하는 의미 검토를 기록한다.**

| ID | 선택 이유 및 기준선에서 확인할 실패 | 새 해설에서 확인할 사항 |
|---|---|---|
| P2 | ‘모호성’ 보기 설명이 ‘번역되지 않는다’라는 비모호성 설명으로 되어 있음. 첫 줄·요약 등 반복도 있음 | 각 용어의 구별 기준, 지문과의 대응, 정의의 참·거짓과 사례 적합성 구분 |
| P3 | A는 리보솜, C는 상보적 염기, E는 두 주형 가닥을 말하지만 해설은 각각 주형 가닥·위치·오카자키 절편을 설명함 | A–E를 원문의 실제 주장과 일대일로 연결 |
| P7 | A=T/G=C의 성립에서 이중가닥을 확정하거나 단일가닥이면 반드시 비율이 다르다고 단정하는 문장 | 조건의 방향과 판별 한계, 정답 판단에 쓰이지 않는 확정·배경 설명 제거 |

이 표는 현재 파일에서 관찰한 실패이며, 학술적 판단의 최종 근거는 Step 4에서 확인한다. 단순히 ‘기존 답 글자가 맞다’는 이유로 실패를 통과 처리하지 않는다.

- [ ] **Step 4: 해당 선지들의 수업 근거를 실제로 확인한다.**

`강의노트/5장 DNA 복제와 유전자의 발현.pdf`, `교과서/생명과학_기초와_응용_2판/05장_DNA_복제와_유전자의_발현.pdf`, `23, 24 소스/5강 합본.pdf`, `복습노트/1006/정리노트_1006_Transcription_Translation_and_Lac_Operon.html`, `복습노트/1001/정리노트_1001_Chromosome_Changes_and_DNA_Replication.html`에서 필요한 범위만 읽는다. 한글 파일명은 `rg --files`로 발견한 실제 경로를 사용한다. PDF의 해당 쪽은 렌더링으로 확인한다.

`source-audit.md`에 15선지 각각의 실제 주장·판단 기준·자료/쪽·판독 상태를 기록한다. P2의 DNA 표현과 U 포함 코돈 등 원문 문제 가능성, P3에서 생물 범위를 임의로 진핵으로 한정하는 문제, P7에서 시료 구성을 해석할 전제도 확인한다. 원문에 조건을 끼워 넣지 말고 필요한 가정·결함은 해설에서 공개한다. 자료를 못 찾거나 답이 충돌하면 보류 이유를 남긴다.

## Task 2: 세 조각만 재작성하고 선지별로 비교하기

**Files:** 수정 `FOLDER/explanations/p2.html`, `p3.html`, `p7.html`; 추가 기록 `FOLDER/evidence/source-audit.md`. 저장소의 발행 파일은 수정하지 않는다.

**Interfaces:** Task 1의 원문·근거·해시를 소비한다. `mpe_cli.load_fragments(item) -> dict[str, str]`로 읽을 수 있는 15개 조각 중 정확히 세 개만 변경된 상태와, R1~R3의 선지별 검토 결과를 제공한다.

- [ ] **Step 1: 재작성 전에 변경 범위 검사의 RED를 확인한다.**

SKILL/scripts를 import 경로에 넣고 아래 검사를 실행한다. 복사 직후에는 `changed == set()`이므로 ‘세 문항이 바뀌었음’ 검사가 실패해야 한다. 보호 파일 검사와 문항 집합 검사는 이때부터 통과해야 한다.

```python
import hashlib
import json
from pathlib import Path
from mpe_cli import load_run, load_fragments
from mpe_contract import validate_fragment

state = json.loads((RUN / 'pilot-state.json').read_text())
item, = load_run(RUN)
fragments = load_fragments(item)
digest = lambda data: hashlib.sha256(data).hexdigest()
assert set(fragments) == {f'p{i}' for i in range(1, 16)}
changed = {key for key in fragments
           if digest((item['folder'] / 'explanations' / f'{key}.html').read_bytes())
           != state['fragment_hashes'][key]}
for problem in item['pack'].problems:
    assert validate_fragment(problem, fragments[problem.id]) == []
for relative, expected in state['protected_hashes'].items():
    assert digest((REPO / relative).read_bytes()) == expected, relative
assert changed == {'p2', 'p3', 'p7'}, changed
```

`RUN`과 `REPO`는 실제 절대 경로의 `Path` 값이다. 위 검사는 보호 파일·구조 검사를 먼저 수행하고 `assert changed == ...`를 마지막에 배치해, 복사 직후의 예상 실패가 보존 검사 실행을 막지 않게 한다. 기존 5장 폴더의 현재 파일 집합도 기록 당시와 비교해 추가·삭제를 검출한다.

- [ ] **Step 2: 최신 authoring.md로 P2·P3·P7을 다시 쓴다.**

recall에서 학생이 확인할 판단 기준과 필요한 개념을 설명하고, solve에서 각 선지의 실제 표현에 적용한다. 불필요한 반복을 덜어내고, 남긴 선택 구역에는 독립적인 역할이 있어야 한다. P7의 기준과 한계는 understand/recall/solve/verify/sum에서 일관되게 유지한다. 원 문제의 참고 풀이에 오류가 있어도 그대로 복제하지 않으며, 원문 자체는 고치지 않는다.

- [ ] **Step 3: 위 범위·구조 검사와 아래 의미 수용 검사를 GREEN으로 만든다.**

| 사례 | 입력 | 합격 기준 |
|---|---|---|
| R1 | P2의 A–E와 해설 | 코돈과 아미노산의 대응 방향, 생물 사이 비교 유무로 판단할 수 있고 C의 뜻을 반대로 설명하지 않는다. A의 정의 자체가 옳아도 이 사례에 부적합함을 구별한다. D/E도 자료에서 확인한 의미와 사례의 관계를 설명한다 |
| R2 | P3의 A–E와 해설 | A는 리보솜과 전사/번역, B는 프라이머, C는 A에 대응하는 RNA 염기, D는 합성 방향, E는 한 전사 산물의 주형 선택을 다룬다. 다른 선지의 근거로 대체하지 않는다 |
| R3 | P7의 표·A–E·본문·요약 | 비율의 일치만으로 I/III의 가닥 수를 확정하지 않는다. II에 대한 결론은 실제 수치와 확인한 전제에서 도출한다. 다른 선지도 핵산 종류·당·서열 상보성 등 실제 주장에 필요한 기준으로 판정한다 |

의미 검사는 키워드 유무가 아니라 자료와 15선지의 대응표로 판정한다. 각 문장에서 삭제에 따른 이해·판정의 손실을 확인한다. 문항마다 삭제·통합한 예와 필요해서 남긴 설명을 하나씩 기록한다. 글자 수는 참고값이며 짧다는 이유만으로 합격시키지 않는다.

## Task 3: 시범본 조립·네 검토·전후 비교 보고

**Files:** 생성 `FOLDER/stage/<build ID>/`, `RUN/pilot-review.json`, `RUN/screenshots/`, 위 비교 보고서. 생산 코드와 기존 발행 파일은 수정하지 않는다.

**Interfaces:** Task 2의 15개 조각을 소비한다. `mpe_cli.load_artifacts(item) -> Artifacts`로 얻는 시범본과 `selected_ids=['p2','p3','p7']`, 현재 input/artifact hashes에 묶인 네 시범 검토 결과를 제공한다. 전체 15문항 승인과 구별한다.

- [ ] **Step 1: 기존 build/check를 실행한다.**

```sh
python3 "$SKILL/scripts/mpe_cli.py" build --run "$RUN"
python3 "$SKILL/scripts/mpe_cli.py" check --run "$RUN"
```

예상: machine PASS, 전체 15문항을 포함한 HTML/MD가 생성되고 새 해설 3개와 미수정 해설 12개를 포함한다. `load_artifacts`로 최종 stage의 절대 경로를 기록한다. 조립된 HTML을 직접 패치하지 않는다.

- [ ] **Step 2: 세 문항의 source_visual/content/independent 검토를 실제로 수행한다.**

source_visual은 원문·표·해당 PDF의 실제 화면을 대조하고, content는 Task 2의 R1~R3와 불필요한 문장 검사를 수행한다. 독립 재풀이자에게는 세 문항의 지문·보기·그림과 교과서/강의노트/정리노트만 준다. 기존·새 정답과 해설, pack/blueprint 정답 정보는 제공하지 않는다. 컨트롤러가 독립 답과 해당 버전 정답키를 대조한다. 충돌·근거 미확인은 실패/보류로 남기고 답에 맞춰 이유를 만들지 않는다.

- [ ] **Step 3: 최종 경로에 대응하는 로컬 미리보기로 browser 검토를 수행한다.**

stage의 링크는 최종 발행 위치를 전제한다(`mpe_render.py:142`). RUN 안에 일회성 HTTP 도우미를 두고 `127.0.0.1`에만 바인딩한다. URL `/웹과제예상/5장/` 아래에서 stage에 존재하는 파일만 stage를 우선하고, 나머지는 REPO의 실제 자료로 연결한다. URL을 디코딩·정규화한 뒤 stage/REPO 내부 파일인지 검사하고 밖으로 벗어난 요청은 거부한다. 기존 파일을 이동·덮어쓰지 않는다.

1280×900/375×812, light/dark의 4개 조합에서 P2/P3/P7을 확인한다. A–E의 클릭→해당 해설, 이전/다음, 문제/원문/요약, P7의 표, 수식, 원 문제/정리노트 링크와 anchor를 확인한다. console/KaTeX 오류·누락 자원·문서 가로 넘침은 0이어야 한다. 패널 애니메이션이 끝난 뒤 화면을 저장해 직접 확인하고, 생략한 구역의 빈 제목이 없는지도 본다. 종료 시 서버를 중지한다.

- [ ] **Step 4: 부분 검토 결과와 보존 상태를 고정한다.**

`RUN/pilot-review.json`에 세 ID, 네 검토의 status/reviewer/evidence, 실제 사용한 자료 path/SHA-256, 현재 input_hash와 artifact_hashes를 기록한다. 기존 validation.json은 수정하지 않는다. `FOLDER/review.json`의 전체 검토는 not_run으로 두고, 나머지 12개까지 pass로 바꾸거나 publish를 위해 해시를 바꿔 끼우지 않는다. 수정 시 build/check부터 다시 수행하며 최대 2회 재검토 기록을 남긴다.

Task 2의 보존 검사와 함께 기존 5장 폴더의 파일 추가·삭제 0, 12개 조각의 바이트 일치, 전체 review 미승인을 확인한다. 이번 검토가 묶인 stage의 `check_artifacts(pack, artifacts)`는 `[]`여야 한다. 보고서·추가 검토 결과는 stage 밖에 두어 검토 후 산출 해시를 바꾸지 않는다.

- [ ] **Step 5: 한국어 전후 비교 보고서를 작성한다.**

문항별로 `기존 설명의 문제 | 새 판단 기준 | 선지에 적용한 예 | 삭제·통합한 내용 | 필요한 설명을 남긴 이유 | 검토 결과`를 한 행씩 적는다. 15선지 감사표·시범 HTML/MD·화면 이미지·RUN의 실제 경로를 연결한다. 기계 검사와 내용/독립 재풀이/화면 검토의 결과를 구별하고, 미해결 사항·기존 HTML 바이트 보존·나머지 12문항 미검토를 밝힌다.

결론은 ‘세 문항에 새 기준 적용 확인 / 수정·보류 필요’로 쓰며 학생의 실제 학습 효과를 주장하지 않는다. 보고서에서 전체 적용·기존 HTML 교체·별도 문제 수정을 자동으로 시작하지 않는다.

- [ ] **Step 6: 요청이 있을 때만 결과를 커밋한다.**

커밋은 새 비교 보고서와 사용자가 보존을 지정한 시범 자료의 명시 경로만 포함한다. `tmp/` 전체나 `웹과제예상/5장/` 전체를 stage하지 않는다. 요청이 없으면 결과 경로와 권장 메시지 `docs(bio-explain): compare chapter 5 pilot explanations`만 보고한다.

## Self-Review

- [x] 목적·공통 기준·세 문항/15선지·불필요한 내용 삭제를 Task 1~3에 연결했다.
- [x] 새 생산 API 없이 기존 `load_run/load_fragments/load_artifacts` 계약과 전체 15문항 요구를 확인했다.
- [x] 세 문항만 발행하거나 기존 검토를 이식하지 않도록 명시했다.
- [x] 다섯 Review Focus를 기준선·의미 수용 검사·보존 검사·브라우저 검사에 연결했다.
- [x] 아직 확인하지 않은 학술 근거는 Task 1/3에서 실제 확인하며, 계획 단계에서 새로 검증했다고 주장하지 않는다.
