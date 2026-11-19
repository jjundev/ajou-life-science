# 1119 정리노트 추론 보강 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 1119 정리노트의 빠진 추론 전제를 보완하고, 이후 생성한 정리노트에서 같은 공백을 기존 본문 감사로 발견한다.

**Architecture:** 1119 HTML의 기존 본문·그림·요약을 고치고 그 HTML에서 정리노트 Markdown과 SVG를 다시 만든다. `bio-review-pack`의 기존 인과 설명 규칙과 6단계 본문 감사에 선별 기준과 대표 질문을 추가한다. 현재의 검수 보고 형식과 수정 요청 배분을 재사용한다.

**Tech Stack:** HTML, 인라인 SVG, Markdown, Python 3의 기존 변환·검사 도구, 브라우저.

**Spec:** [이 문서의 설계 기준](#설계-기준)에 직전 채팅에서 정한 범위와 완료 판정을 보존했다.

## Global Constraints

- 적용 범위는 1119 정리노트와 이후 `bio-review-pack` 생성분이다. 기존 토픽 ID, 화면 구조, 1119 복습문제·문제설명 및 별도 인터랙티브의 동작을 보존한다.
- 조건과 첫 적용은 펼쳐진 본문에, 변수 변경 연습은 이미 연결된 인터랙티브에 둔다.
- 근거가 되는 표·그림·문장 옆에 필요한 전제를 넣는다. 단순 정의와 이미 충분한 설명에는 별도 설명을 요구하지 않는다.
- 수업 범위, 출처가 있는 보충, 기존 ELI5의 전문용어 없는 1~3문장 규칙을 적용한다. SVG와 캡션도 이 범위를 따른다.
- 검수 결과의 네 필드는 `심각도 · id · 문제 · 고칠 내용`이다. 심각도와 검수 반복 한도는 기존 6단계 규칙을 따른다.

## Review Focus

1. 같은 포화도와 같은 분압을 혼동하는 독자가 각각 다른 축을 고정할 수 있다. Task 1의 산소 곡선 판정으로 확인한다.
2. 이완 직후 반월판막 폐쇄와 충전 시작 사이에 두 판막이 닫히는 구간을 찾을 수 있다. Task 1의 판막 판정으로 확인한다.
3. 좁은 화면과 Markdown에서도 측정 범위가 읽히고 1117 및 인터랙티브 링크가 열린다. Task 1의 변환·브라우저 검사로 확인한다.
4. 연결된 선행 토픽만으로 풀리는 예는 기존 근거로 통과하고, 인터랙티브를 열어야 전제를 알 수 있는 예는 위치를 지정해 보완한다. Task 2의 표본 감사로 확인한다.
5. 단순 정의의 설명 길이와 작성자에게 전달되는 TSV 필드가 보존된다. Task 2의 대조 표본과 수정 요청 배분 검사로 확인한다.

---

## 설계 기준

독자가 공기 흐름·기체 확산·혈액 흐름에서 비교해야 하는 값을 구별하고, 같은 원리로 인접한 상태를 판단할 수 있어야 한다. 핵심 네 곳은 흉막·산소 해리곡선·CO₂ 운반·심장 판막이다. 기도, 호흡량, 호흡 조절, 순환과 혈액 성분, 심장 전도, 모세혈관에서 발견된 공백은 해당 위치만 보강한다. 생성 스킬은 비교 대상 전환, 관측값 해석, 상태 전환에 실제로 필요한 전제를 확인한다. 검수자는 본문과 그림에서 답의 근거를 짚고, 빠진 경우 기존 본문 감사 결함으로 전달한다.

## 파일 구조

- 1119 원본: `복습노트/1119/정리노트_1119_Respiratory_and_Circulatory_Systems.html`.
- 함께 갱신: `복습노트/1119/.assets/정리노트_1119_Respiratory_and_Circulatory_Systems.md`, `복습노트/1119/.assets/figures_1119/fig-s0-airway.svg`, `복습노트/1119/.assets/figures_1119/fig-s0-volumes.svg`, `복습노트/1119/.pack/summary-audit.md`.
- 출처를 확인해 새 보충을 추가한 경우: 해당 토픽의 `복습노트/1119/.pack/manifest.json`에 `supp: true`를 반영하고 본문의 보충과 대응 요약을 함께 갱신한다.
- 생성 규칙: `.agents/skills/bio-review-pack/references/content-rules.md`의 작성자 브리프와 `어려운 개념에 한정한 동기·인과 설명`.
- 검수 절차: `.agents/skills/bio-review-pack/references/review-prompt.md`의 `본문 감사 리뷰` 및 `본문 밀도 검토`, `.agents/skills/bio-review-pack/SKILL.md`의 6단계 진입점.

### Task 1. 1119 본문에 추론 전제와 적용 사례 반영

**Files:** 위 1119 원본, 함께 갱신할 파일과 조건에 해당하는 manifest. 근거는 `STT/1119 생명.md`, 13장 강의노트·교재, 1119의 기존 인터랙티브다.

**Interfaces:** 현재 토픽 ID와 `#o2-pressure`, `#o2-neutral`, `#o2-acid` 조작을 사용한다. `.sum`은 같은 토픽의 복습을, `summary-audit.md`는 `토픽 | 본문의 핵심 주장 | 대응하는 요약 문장 | 판정·생략 이유`를 담는다. 갱신 전후 `s1-carbon`은 Task 2의 검수 예시다.

- [x] **기준선 기록.** 아래 구조 검사를 실행해 `OK`를 확인한다. 아래 표의 질문을 수정 전 본문·그림에 적용해 답의 근거가 있는 곳과 빠진 곳을 작업 메모에 적는다. CO₂ 항목은 반응 방향 표와 “얘가 빠져나가니까”라는 인용까지 도달하지만, 본문에는 혈액 CO₂가 폐포로 빠져나가 *줄어드는 것이 원인*이라는 연결이 명시되지 않는다. 이미 본문 규칙으로 풀리는 항목은 ‘풀이 시범 보강’으로 기록한다.

  ```bash
  skill=.agents/skills/bio-review-pack
  pack=복습노트/1119
  note="$pack/정리노트_1119_Respiratory_and_Circulatory_Systems.html"
  review="$pack/복습문제_1119_Respiratory_and_Circulatory_Systems.html"
  python3 -B "$skill/scripts/check_html.py" --manifest "$pack/.pack/manifest.json" --note "$note" --review "$review"
  ```

- [x] **핵심 네 토픽을 수정.** 표의 위치와 판정 기준을 사용한다. 설명 문체는 기존 `~해요` 체를 따른다.

  | 토픽 ID와 삽입 위치 | 수정 후 질문과 판정 기준 |
  |---|---|
  | `s0-ventilation`, 기흉 사슬과 들숨·날숨 표 사이 | “폐를 펴는 압력차와 공기를 움직이는 압력차에는 각각 어떤 두 압력이 들어가나요?” 폐포압–흉막강압, 대기압–폐포압을 각각 설명한다. 가슴 공간 증가 → 폐 팽창 → 폐포압이 대기압 아래로 잠시 하강 → 공기 유입이 드러난다. |
  | `s1-oxygen`, 기존 위젯 읽기 설명 아래 | “같은 30 mmHg에서 50%와 32%를 읽었을 때 방출 차이를 어떻게 산출하나요?” 같은 양의 Hb가 같은 포화도로 들어왔을 때 18%p에 해당하는 결합 자리가 더 비었음을 설명한다. “포화도 50%에서 왜 오른쪽 이동인가요?”는 pH 7.4의 30 mmHg와 pH 7.2의 40 mmHg를 비교한다. 수치를 개념 모형으로 표시한다. |
  | `s1-carbon`, 조직·폐 반응표 바로 뒤 | “폐에서는 무엇이 먼저 줄어 CO₂가 다시 만들어지나요?” 혈액의 CO₂가 먼저 폐포로 확산해 줄어듦 → HCO₃⁻와 H⁺로부터 CO₂ 재형성 → 새 CO₂도 폐포로 이동을 설명한다. 조직 쪽 CO₂ 공급과 효소의 기존 역할은 표·문장을 이용한다. 근거는 전사 325–329행이다. |
  | `s3-cycle`, 판막 표 바로 뒤 | “심방압 < 심실압 < 동맥압일 때 두 판막과 혈류는 어떤 상태인가요?” 두 판막이 닫혀 심실로 들어오거나 나가는 혈류가 없다. “이완 초기에 언제 충전이 시작되나요?”는 반월판막이 닫힌 뒤 심실압이 심방압 아래로 내려가 방실판막이 열릴 때라고 설명한다. |

- [x] **나머지 공백의 위치를 수정.** `s0-airway`의 인라인 `fig-s0-airway`는 ‘끈끈한 층이 붙잡아요 → 작은 솔이 목 쪽으로 밀어요 → 기침하거나 삼켜요’ 순서와 이에 맞는 대체 설명으로 수정한다. `s0-volumes`의 `fig-s0-volumes`는 1회 호흡량·폐활량을 두 선 사이 괄호로, 잔기량을 최대 날숨 선 아래 음영으로 표시한다. 축 기준이나 캡션으로 이 범위를 식별할 수 있게 하고 본문에서 평소 날숨 뒤와 최대 날숨 뒤를 구분한다.
- [x] **호흡 조절과 순환 설명 연결.** `s1-control`에서는 감지 위치를 기체·pH 설명에도 표시하고 `CO₂ 배출 증가 → 자극 완화`로 닫는다. `s2-circuits` 첫 formal 문장은 폐에서 혈액에 실은 산소를 전신에 보내려면 심장과 혈관이 필요하다는 전사 331–333행으로 연결한다. `s2-blood`는 일정 혈액 부피에서 적혈구가 차지하는 몫과 산소 운반 능력의 관계를 가능성으로 설명한다. `s3-pacemaker`에서는 방실결절 지연과 `#s3-cycle`의 심실 채우기를 연결한다. P파·QRS 명칭은 강의자료 또는 교재에서 직접 확인한 경우에만 해당 파형과 의미를 출처가 있는 보충에 담는다. 새 보충에는 고유 id, 대응 `.sum-supp`, 동일 배지 메타데이터와 출처를 넣는다.
- [x] **유량의 조건과 요약 반영.** `s3-vessels`의 10 mL/s 예시 전에 정상 상태에서 중간에 혈액이 계속 쌓이지 않으므로 한 순환 경로의 각 단계 전체를 지나는 평균 유량을 같게 놓을 수 있다고 설명한다. 한 모세혈관의 유량과 가지 전체의 합을 구별한다. `s4-cheatsheet`는 공기 흐름의 대기압–폐포압, 기체 확산의 각 기체 분압, 혈액 흐름의 펌프가 만드는 혈압차를 함께 보여 준다. 바뀐 `.sum`의 대응 문장을 `summary-audit.md`의 해당 토픽 행과 맞춘다.
- [x] **Markdown과 SVG 재생성.** 임시 디렉터리에 `복습노트/1119/`를 복사해 1119 HTML과 `.assets/`를 담고, 같은 임시 `복습노트/` 아래의 `1117`은 실제 상대 경로 관계가 유지되도록 연결한다. 작업 트리의 스크립트에서 `python3 -B <절대경로>/html2md.py <임시 1119 정리노트 HTML> <임시 1119 복습문제 HTML> --check`를 실행한다. `OK`를 확인하고 정리노트 Markdown 및 그 Markdown이 참조하는 변경된 정리노트 SVG만 반영한다. 현행 HTML로 이 임시 변환 절차를 실행한 기준선은 `OK`였다.
- [x] **본문과 변환물 검증.** 핵심 네 질문을 다시 답하고 답마다 수정된 HTML의 토픽과 실제 근거를 적는다. `s0-volumes`에서 평소 날숨 선과 최대 날숨 선을 구별할 수 있는지, `s3-vessels`에서 10 ÷ 2 = 5 cm/s와 10 ÷ 10 = 1 cm/s를 같은 총유량 조건으로 읽는지 확인한다. Markdown에서 핵심 네 사례, SVG 두 개, 네 인터랙티브 링크, 1117 링크를 확인한다. 첫 단계의 구조 검사와 `git diff --check`의 통과를 확인한다.
- [x] **브라우저 검증.** 기존 `references/browser-check.md`를 따라 1280px와 375px, 밝은·어두운 테마에서 수정한 그림의 글자·화살표·음영과 요약을 확인한다. `#o2-pressure`의 30·40·95 mmHg에서 두 읽기값이 각각 `50%/32%`, `68%/50%`, `96%/91%`인지 확인한다. `a`가 연결하는 기존 인터랙티브 네 파일과 1117 앵커가 열린다. 최종 diff를 정리노트 산출물과 대조한다.

### Task 2. 기존 생성·감사 절차에 추론 확인 추가

**Files:** `.agents/skills/bio-review-pack/references/content-rules.md:39`, `.agents/skills/bio-review-pack/references/review-prompt.md:64`, `.agents/skills/bio-review-pack/SKILL.md:194`.

**Interfaces:** `findings-body.tsv`는 `심각도<TAB>id<TAB>문제<TAB>고칠 내용`이다. `pack_run.py fixes --run RUN`은 토픽 ID로 담당 섹션을 찾고 `RUN/work/fixes/<sid>.txt`에 요청을 쓴다. 이 태스크 검증에는 Task 1의 CO₂ 수정 전·후 본문을 예시로 쓰며 별도 노트 생성 없이 판정할 수 있다.

- [x] **검수 표본을 준비.** 원래 본문의 `s1-carbon`, 적용 후 본문의 `s1-carbon`, 정확한 선행 토픽 링크를 따라 답할 수 있는 모형 사례, 인터랙티브에서만 전제가 드러나는 모형 사례, 단순 용어 정의를 준비한다. 기록 항목은 `대표 질문 · 실제 근거 또는 빠진 전제 · 판정`이다. 기대 판정은 각각 `수정 필요`, `통과`, `통과`, `수정 필요`, `적용 대상 아님`이다.
- [x] **작성 기준을 추가.** 기존 어려운 개념 절에 비교 대상 전환·관측값 해석·상태 전환의 선별 기준을 넣는다. 해당 결론에 필요한 비교 대상·고정 조건·중간 상태 중 빠진 것만 원래 표·그림·문장 옆에 쓴다. 독자가 필요한 근거를 직접 연결된 선행 토픽에서 찾을 수 있으면 그 링크를 쓴다. 작성자 브리프의 자가 검사는 이 절을 가리킨다.
- [x] **본문 감사 기준을 추가.** 기존 리뷰어가 선별된 토픽에서 질문 하나에 먼저 답한다. 이때 펼쳐진 해당 본문·그림과 직접 연결된 선행 토픽을 읽고 근거를 짚는다. 이후 근거 자료에서 빠진 전제를 보완할 수 있는지 확인한다. 빠진 경우 `문제` 칸에 질문과 빠진 전제, `고칠 내용` 칸에 최소 보강 위치와 내용을 쓴다. 6단계 진입점과 기존 수정 후 재검토 문장에 같은 질문으로 재확인하는 절차를 반영한다.
- [x] **표본을 다시 판정.** 다섯 표본이 기대한 결과를 내는지 확인한다. 특히 답을 직접 써 주지 않아도 주어진 규칙으로 유도 가능한 예는 통과해야 한다. 원래 `s1-carbon`의 결함 행이 기존 네 칸으로 표현되고, 수정 후에는 그 결함이 사라지는지 확인한다.
- [x] **기존 배분 계약 검증.** 임시 RUN에서 1119의 `.pack/manifest.json`을 사용해 `work/reports/findings-body.tsv`에 `critical` / `s1-carbon` / `폐에서 무엇이 먼저 줄어드는가. 혈액 CO₂ 감소가 명시되지 않음` / `반응표 뒤에 폐포로의 CO₂ 확산과 역반응을 연결`을 탭으로 한 행 쓴다. `python3 -B .agents/skills/bio-review-pack/scripts/pack_run.py fixes --run <임시 RUN>` 실행 후 `work/fixes/s1.txt`에 두 텍스트가 보이고 `unapplied.tsv`에 해당 ID가 없는지 확인한다.
- [x] **기존 테스트를 실행.** 아래 두 모음이 각각 `OK`를 출력하고 `git diff --check`를 통과하는지 확인한다. 계획 작성 시 기준선은 각각 16개와 23개 테스트 통과였다.

  ```bash
  python3 -B -m unittest discover -s .agents/skills/bio-review-pack/tests -p 'test_pack_run.py'
  python3 -B -m unittest discover -s .agents/skills/bio-review-pack/tests -p 'test_skill_files.py'
  git diff --check
  ```

태스크별 검증 결과와 수정 범위를 확인해 독립적으로 검토할 수 있게 한다. 실행에서 커밋을 요청받은 경우 1119 정리노트 변경과 스킬 변경을 각각 `docs: clarify reasoning in the 1119 biology note`, `docs: verify reader reasoning in biology review packs`로 커밋한다.
