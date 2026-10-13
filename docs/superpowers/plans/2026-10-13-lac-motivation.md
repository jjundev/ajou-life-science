# lac Motivation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 1006 lac 오페론의 필요성과 최초 유입 원리를 설명하고, 어려운 개념에만 적용하는 동기 설명 규칙을 생명과학 정리노트 스킬에 반영한다.

**Architecture:** 기존 s5-operon 토픽의 설명 레이어를 보강하고 기저 발현은 출처를 표시한 supp 레이어로 넣는다. 앞으로의 생성에는 bio-review-pack의 작성·검토 지침을 적용한다. HTML이 MD의 원본이며 새 프로그램이나 manifest 필드는 만들지 않는다.

**Tech Stack:** HTML, Markdown, JSON, 기존 Python manifest/check_html/html2md 도구, 브라우저 검증.

**Spec:** `docs/superpowers/specs/2026-10-13-lac-motivation-design.md`

## Global Constraints
- 포도당이 없는 설명 조건을 유지한다. OFF를 생산량 0으로 오해하지 않게 한다.
- 기저 발현은 확인한 1006 STT에 없으므로 출처가 있는 보충으로 구분한다. 교수님 말씀으로 넣지 않는다.
- 단순 용어, 명칭, 목록에는 추가하지 않는다. 이미 충분한 설명은 반복하지 않는다.
- 생물학의 필요성은 기능과 효과로 설명하고 의도적 설계나 근거 없는 진화 이야기를 쓰지 않는다.
- 출처를 확인할 수 없으면 단정하지 않는다.
- 다른 날짜 노트, 복습문제, 문제설명, 별도 인터랙티브 자료는 수정하지 않는다.
- .agents/skills/bio-review-pack이 원본이다. .claude/skills/bio-review-pack은 심볼릭 링크이므로 따로 수정하지 않는다.
- 기존 eli5의 전문용어 없는 1~3문장 규칙과 레이어 순서를 지킨다. 자세한 설명은 formal/supp에 둔다.
- 기존 미추적 problem-tabs-review-feedback 계획·설계 파일은 그대로 둔다. 실행 시 상태를 다시 확인한다.
- 실행 환경의 Python 의존성은 기존 도구 import로 확인한다. 실패하면 사용 가능한 환경을 찾고 새 의존성은 임의로 추가하지 않는다.
- 커밋·푸시는 별도 사용자 요청이 있을 때만 수행한다.

## Review Focus
1. OFF를 완전한 생산 중단으로 읽는 경우: 기저 발현과 최초 유입 설명을 찾을 수 있어야 한다. Task 1의 내용 검토로 확인한다.
2. 젖당과 알로락토스를 혼동하는 경우: 억제자 결합 물질과 구조 변화가 정확해야 한다. Task 1의 사실 대조로 확인한다.
3. 보충을 수업 내용으로 오해하는 경우: 기저 발현의 배지·출처가 보이고 기존 교수님 인용은 보존되어야 한다. Task 1의 구조·브라우저 검토로 확인한다.
4. 단순 용어나 이미 충분한 토픽: 불필요한 동기 문단을 추가하지 않아야 한다. Task 2의 음성 사례 검토로 확인한다.
5. 모바일·다크모드·파생 MD: 보충을 읽을 수 있고 요약·위젯·출처 링크가 동작하며 관련 없는 파일이 바뀌지 않아야 한다. Task 1의 브라우저·변환·diff 검토로 확인한다.

---

## 파일 구조
- `복습노트/1006/정리노트_1006_Transcription_Translation_and_Lac_Operon.html`: 학습자가 읽는 원본, s5-operon 중심 수정.
- `복습노트/1006/.pack/manifest.json`: s5-operon의 supp=true 반영. topic id·layers·문항 목록은 유지.
- `복습노트/1006/.assets/정리노트_1006_Transcription_Translation_and_Lac_Operon.md`: 원본 HTML에서 재생성.
- `복습노트/1006/.pack/lac-motivation-update.md`: 이번 수정의 출처·검사 결과·한계. 과거 검증 보고서를 이번 변경의 증거로 재사용하지 않는다.
- `.agents/skills/bio-review-pack/SKILL.md`: 작성·검토 단계에서 새 기준 확인 연결.
- `.agents/skills/bio-review-pack/references/content-rules.md`: 선별 기준, 설명 순서, 보충 허용 조건.
- `.agents/skills/bio-review-pack/references/review-prompt.md`: 어려운 개념의 설명 공백과 과잉 설명 검사.

### Task 1: 1006 lac 설명과 보충 출처 반영

**Files:** 위 파일 구조의 1006 HTML, manifest, MD, 변경 기록.

**Interfaces:**
- Consumes: s5-switch/s5-operon, STT/1006 생명.md, 기존 manifest의 sections[].topics[].supp:boolean.
- Produces: 동일한 토픽 id의 보강된 HTML 및 파생 MD. 기존 검사 CLI 입력 형식을 유지한다.

- [x] **Step 1: 현행 설명의 부족한 지점 확인**
  s5-operon만 읽고 필요성, 알로락토스의 결합 대상, 최초 젖당 유입, OFF의 의미 네 질문에 답한다. 예상: 최초 유입과 기저 발현 근거가 없다. 결과를 이번 변경 기록에 남긴다. 문구 일치만 검사하는 새 테스트는 만들지 않는다.

- [x] **Step 2: 보충 사실의 출처 확인**
  STT의 lac 부분과 해당 강의노트·교재 설명을 대조한다. 대화에서 확인한 연구 `https://pmc.ncbi.nlm.nih.gov/articles/PMC3722110/`의 원문에서 기저 발현, 소량의 permease/β-galactosidase, 알로락토스 생성에 관한 근거를 확인하고 자료명·링크를 기록한다. 수업 범위 밖 사실은 supp에만 둔다.

- [x] **Step 3: HTML과 manifest 수정**
  s5-operon formal에 에너지·재료 절약과 전사부터 억제하는 이유를 연결한다. 기존 구조 변화 설명을 유지한다. 새 supp 레이어에는 기저 발현 정의, 소량 LacY의 유입 역할, 소량 LacZ의 알로락토스 생성 역할, 단계별 과정, 실제 출처를 넣는다. 배지는 `보충 · 수업에서 다루지 않았어요`로 한다. manifest의 해당 supp를 true로 바꾼다. 위젯 옆 설명에서 OFF≠완전한 0임을 알려주되 위젯의 상태 모형은 바꾸지 않는다. 본문·요약·그림 캡션에 완전한 생산 중단을 단정하는 표현이 있는지 대조한다.

- [x] **Step 4: 기존 구조 검사 실행**
  저장소 루트에서 실행한다. 두 명령 모두 종료 코드 0과 `OK`가 통과 조건이다.
  ```bash
  python3 .agents/skills/bio-review-pack/scripts/manifest.py 복습노트/1006/.pack/manifest.json
  python3 .agents/skills/bio-review-pack/scripts/check_html.py --manifest 복습노트/1006/.pack/manifest.json --note 복습노트/1006/정리노트_1006_Transcription_Translation_and_Lac_Operon.html --review 복습노트/1006/복습문제_1006_Transcription_Translation_and_Lac_Operon.html
  ```

- [x] **Step 5: 파생 MD 재생성과 변경 범위 검사**
  html2md는 review도 재생성하고 SVG를 쓸 수 있다. 실행 전 대상 .assets 파일을 임시 경로에 백업하고 해시를 기록한다.
  ```bash
  python3 .agents/skills/bio-review-pack/scripts/html2md.py 복습노트/1006/정리노트_1006_Transcription_Translation_and_Lac_Operon.html 복습노트/1006/복습문제_1006_Transcription_Translation_and_Lac_Operon.html --check
  ```
  예상: 종료 코드 0, `OK`, 정리노트 MD에 보충 내용·출처 포함. 의도하지 않은 복습문제 MD/SVG 변경이 있으면 이번 실행의 백업과 비교해 이번 실행이 만든 차이만 복원한다. 기존 사용자 변경은 덮어쓰지 않는다.

- [x] **Step 6: 내용 및 브라우저 수용 검사**
  `.agents/skills/bio-review-pack/references/browser-check.md`를 따라 1280×900과 너비 375px, 밝은/다크 테마에서 s5-operon을 읽는다. .content 가로 넘침 없음, 출처 링크 연결, 요약 표시, 위젯 젖당 없음/있음 선택과 기존 readout 동작, 콘솔 오류 없음이 통과 조건이다. Step 1의 네 질문에 새 노트만으로 답한다. 기저 발현이 보충으로 보이는지와 억제자 구조 변화·포도당 조건을 확인한다. 실제 결과를 새 변경 기록에 남긴다.

### Task 2: 어려운 개념에 한정하는 작성·리뷰 기준 반영

**Files:** SKILL.md, references/content-rules.md, references/review-prompt.md.

**Interfaces:**
- Consumes: Task 1의 실제 lac 사례, 현재 범위·supp·eli5 계약.
- Produces: 작성자와 리뷰어가 같은 선별 기준을 사용하는 자연어 규칙. 새 CLI·JSON 필드·템플릿 레이어는 없다.

- [x] **Step 1: 현행 규칙의 공백 확인**
  사용자 지적·이중 부정·다단계 인과·시작 조건·숨은 조건의 선별 기준과, 문항 풀이 외 이해 공백을 메우는 supp 허용 문구가 있는지 읽는다. 예상: 명시적 선별 기준과 이해 보충 허용 규칙이 부족하다.

- [x] **Step 2: content-rules.md에 작성 계약 추가**
  범위 규칙 뒤에 어려운 개념의 선별 기준을 추가한다. 사용자 지적은 적용 신호이고 구조적 어려움은 정의만으로 인과가 연결되지 않을 때 적용한다. 필요 상황, 해결 문제, 핵심 원리, 작은 사례, 오해 조건을 기존 레이어 안에 짧게 통합한다. 고정 문단 수나 모든 토픽 적용을 강제하지 않는다. 기존 문항 필요 사실의 supp 허용에 이해의 인과적 공백을 메우는 사실도 추가하고 실제 출처·기존 배지 계약을 유지한다.

- [x] **Step 3: SKILL.md와 review-prompt.md 연결**
  SKILL.md의 작성 단계에서 새 기준을 작성자 브리프와 자기 검사에 반영한다. lite에서도 작성자 자기 검사는 적용한다. review-prompt.md 일반 리뷰에는 해당 토픽의 필요성·인과·시작 조건 누락과 단순 토픽에 붙인 불필요한 설명을 확인하도록 추가한다. lite의 기존 일반 리뷰 생략 정책은 유지한다.

- [x] **Step 4: 대표 사례로 규칙 수용 검사**
  각 사례에 대해 적용 여부와 이유를 새 변경 기록에 남긴다. 아래 다섯 기대 결과와 일치해야 한다.
  - lac 억제자: 적용. 필요성, 억제 해제, 최초 유입 설명을 연결한다.
  - 사용자가 어려움을 지적한 인과 개념: 적용. 사용자가 막힌 지점을 보완한다.
  - 코돈의 명칭·단순 정의: 별도 동기 문단을 추가하지 않는다.
  - 이미 필요성이 충분한 s5-switch: 반복 문단을 추가하지 않는다.
  - 출처 없는 수업 밖 기작: 단정해 삽입하지 않는다. 근거 확인 또는 설명 한계를 기록한다.
  규칙만으로 생물의 의도·근거 없는 진화 목적론을 유도하지 않는지 함께 읽는다. 문자열 존재만 확인하는 새 테스트는 추가하지 않는다.

- [x] **Step 5: 최종 변경 검사와 인계**
  ```bash
  git diff --check
  git diff --stat
  git status --short
  ```
  예상: whitespace 오류 없음, 변경 파일은 위 파일 구조에 한정. Task 1의 출처·실행 결과·브라우저 결과와 Task 2 사례 판정을 보고한다. 이미 성공한 구조 검사는 HTML/manifest를 다시 바꾼 경우에만 재실행한다. 커밋 요청이 있을 때만 지정 파일을 stage하고 staged diff를 검토한 뒤 커밋한다.

## 계획 자체 검토
- 설계의 필요성·인과·기저 발현·출처 구분은 Task 1에 포함했다.
- 적용/제외 기준, 목적론 방지, 보충 허용, lite 작성 검사 연결은 Task 2에 포함했다.
- Review Focus 다섯 조건은 각 작업의 명시적인 내용·브라우저·사례 검사에 연결했다.
- 자연어·산출물 보완 작업이므로 구현을 복제하는 테스트 대신 기존 검증기와 학습자 관점의 수용 검사를 사용한다.
- 계획 작성 시 제품 파일은 수정하지 않는다. 실행 방법 선택 후 구현한다.
