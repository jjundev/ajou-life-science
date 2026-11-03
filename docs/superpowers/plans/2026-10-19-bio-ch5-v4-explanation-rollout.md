# 5장 v4 전체 15문항 해설 개선 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 시범 P2·P3·P7의 결함 안내 표제를 정리하고 나머지 12문항에 판단 기준 중심의 해설을 적용해, 15문항·75선지의 새 검토를 통과한 경우에만 기존 v4 해설을 교체한다.

**Architecture:** 기존 `bio-problem-explain`의 extract → 조각 저작 → build/check → 네 검토 → publish를 재사용한다. 커밋된 시범 조각은 출발점으로만 쓰고, 전체 승인이나 옛 검토를 이식하지 않는다. 원 문제는 보존하며 해설 소유 파일만 백업 후 교체한다.

**Tech Stack:** Python 3.10+, 기존 해설 CLI·템플릿·로컬 KaTeX/Pretendard, PDF 렌더링 도구, Playwright.

**Spec:** `d82975f`의 `.agents/skills/bio-problem-explain/references/authoring.md`, `references/verification.md`와 `8127868`의 `docs/superpowers/reviews/2026-10-19-bio-ch5-v4-explanation-pilot.md`. 발행 계약은 기존 `docs/superpowers/specs/2026-10-13-bio-problem-explain-design.md`와 현재 `scripts/mpe_publish.py`를 따른다. 구역 구성은 최신 authoring이 우선한다.

## Global Constraints

- 이번 호출은 계획 작성만 한다. 실행 방식은 이전에 선택한 직접 구현을 유지하되, 사용자의 계획 검토를 받은 뒤 실행한다.
- 대상은 `웹과제예상/5장/복습문제_5장_웹과제예상_v4.html`의 p1~p15 전체, 각 A–E 총 75선지다. o1·o2는 제외한다. 다른 장·버전은 건드리지 않는다.
- 문제·보기·정답키·표·그림·순서·pack.json·blueprint.md를 수정하지 않는다. P2 DNA/U 표기와 P7 누락 전제의 문항 수정은 별도 작업이다.
- `understand → recall → solve → verify`는 필수이고 start/pitfall/retry는 별도 도움이 있을 때만 쓴다. recall의 제목은 **이 문제를 봤을 때 떠올릴 개념과 공식**이다.
- 모든 선지의 실제 주장 → 기준 적용 → 판정과 선택/제외를 연결한다. 진술의 참·거짓, 사례 적합성, 부정형 질문의 선택 여부를 구별한다.
- 지워도 기준 이해·선지 판정·오류 방지에 손실 없는 문장은 삭제·통합한다. 정의·이유·가정·출처·결함 공개는 필요한 만큼 남기며 분량 감소율을 강제하지 않는다.
- 표현 결함은 understand의 `<strong>문항 결함:</strong>`으로 공개한다. P2/P7의 조건·유보를 solve/verify/pitfall/sum에서도 유지한다. 조건부 답을 엄밀한 무조건적 유일 정답으로 만들지 않는다.
- 새 RUN의 `review.json` 네 검토를 전체 15문항에 대해 실제 수행한다. 시범의 scoped pass나 기존 validation.json을 승인으로 복사하지 않는다.
- 독립 재풀이자에게 정답키·카드 풀이·기존/새 해설·pack/blueprint·이 계획의 문항별 판정 예를 주지 않는다. 문제·보기·그림과 허용 수업 근거만 준다.
- 최초 검토 후 수정·재검토는 최대 2회다. 원본/문맥 변경은 새 RUN 재추출, 해설 변경은 새 build/check와 네 검토가 필요하다. 하나라도 fail/disputed/not_run이면 발행을 보류한다.
- 공통 스킬·생산 코드·템플릿·기존 시범 보존 폴더는 수정하지 않는다. 필요한 감사·검증 도우미만 새 RUN 안에 둔다.
- 계획 승인 후 실행 범위에는 **검토 통과 시 이 checkout의 기존 v4 해설 교체**가 포함된다. Git 병합·커밋·푸시는 별도 요청 없이는 하지 않는다. 이전 커밋 요청을 새 실행의 커밋 허가로 쓰지 않는다.

## Review Focus

1. 부정형과 메타 보기: P1의 ‘모두 맞다’는 다른 보기의 판정 결과로 평가하고, P4는 분자의 역할과 ‘참여하지 않는 것’ 선택을 구별한다 — Task 2의 R1.
2. 방향·번호·도형: P5의 실제 염기서열, P6의 화살표/말단, P9의 9번째 염기/종결코돈을 그대로 대입해 이유를 검증한다 — Task 2의 R2.
3. 결정 가능한 범위: P7의 가닥 수, P10의 유전자형, P13/P15의 수업 모형을 자료 이상으로 확정하지 않는다 — Task 2의 R3.
4. 부분 승인 재사용과 오래된 해시: 시범 세 문항도 새 전체 검토에 포함하며, 승인 뒤 조각·자료·산출물 변경은 발행 거부로 이어져야 한다 — Task 3의 R4와 기존 gate 회귀 테스트.
5. 실제 화면과 교체 실패: 좁은 패널의 짧은 식, 모바일 원문 영역, 상대 링크, 그림 확대를 확인하고 실패 시 기존 해설과 원 문제를 보존한다 — Task 3의 R5와 Task 4의 발행/복구 검증.

---

## File Structure and Interfaces

실행 시 실제 checkout의 절대 경로를 `REPO`로 기록한다. 현재 계획 작성 checkout은 `/Users/hyunjun_macbook_pro/.codex/worktrees/ef62/생명과학`, 브랜치는 `codex/bio-ch5-explanation-pilot`, 기준 HEAD는 `8127868`이다. 새 checkout이면 그 커밋을 포함하는지 확인한다. native 작업 폴더는 upstream 기준으로 만들어질 수 있으므로 HEAD를 추정하지 않는다.

|경로/기호|역할|
|---|---|
|`SKILL = REPO/.agents/skills/bio-problem-explain`|기존 CLI와 저작/검토 규격, 읽기 전용|
|`SOURCE = REPO/웹과제예상/5장/복습문제_5장_웹과제예상_v4.html`|15문항 원본, 읽기 전용|
|`PILOT = REPO/docs/superpowers/reviews/2026-10-19-bio-ch5-v4-explanation-pilot`|커밋된 시범 조각·근거, 읽기 전용|
|`PUBLISHED = REPO/웹과제예상/5장/.pack/자료_문제해설_5장_웹과제예상_v4`|기존 발행 조각·검토, 읽기 전용 출발점|
|`RUN = REPO/tmp/bio-ch5-v4-explanation-rollout-<고유값>`|빈 고유 RUN, 기존 시범 RUN 재사용 금지|
|`RUN/rollout-state.json`|원본/문맥·참조·시범 보존 해시, 기존 발행 파일 목록과 백업 위치|
|`FOLDER = mpe_cli.load_run(RUN)[0]['folder']`|추출 결과. 이름을 추측하지 않음|
|`FOLDER/explanations/p1.html`~`p15.html`|15문항의 최종 저작 조각|
|`FOLDER/evidence/option-audit.md`|75선지의 실제 주장·기준·판정·근거 쪽과 삭제/유지 이유|
|`FOLDER/evidence/independent-full.md`|정답 비공개 재풀이와 조건/해석 충돌 기록|
|`RUN/check_authoring.py`|이 RUN 전용 구조·범위·표제 검사. `--phase pilot` / `--phase full`|
|`RUN/rollout-progress.json`|attempt, active_run, history, verified_snapshot. 새 RUN이 필요해도 수정 횟수 유지|
|`FOLDER/stage/<build ID>/`, `FOLDER/review.json`|새 조립 결과와 전체 검토, CLI가 생성|
|`RUN/preview.py`, `RUN/browser-result.json`, `RUN/screenshots/`|일회성 경로 매핑과 실제 화면 증거|
|`RUN/pre-publish/`, `FOLDER/backups/`|교체 전 소유 파일 스냅샷과 기존 publisher의 백업|
|`docs/superpowers/reviews/2026-10-19-bio-ch5-v4-explanation-rollout.md`|전체 결과·발행/보류·보존 검사·남은 문항 결함 보고서|

발행으로 변경할 수 있는 경로는 아래 네 소유 경로뿐이다. 그 외 기존 장 파일은 파일 집합과 바이트를 보존한다. 별도 보고서·새 RUN은 이 보호 목록 밖이다.

1. `웹과제예상/5장/문제해설_5장_웹과제예상_v4.html`
2. `웹과제예상/5장/.pack/문제해설_5장_웹과제예상_v4.md`
3. `웹과제예상/5장/.pack/figures_문제해설_5장_웹과제예상_v4/`
4. `웹과제예상/5장/.pack/자료_문제해설_5장_웹과제예상_v4/`

### Task 1: 새 입력 고정과 시범 세 문항의 표제 정리

**Files:** 생성 `RUN/rollout-state.json`, `RUN/check_authoring.py`, `RUN/rollout-progress.json`; 수정 새 `FOLDER/explanations/p2.html`, `p7.html`. 원 발행물·PILOT는 수정하지 않는다.

**Interfaces:** `mpe_cli.extract(repo, target, run) -> int`, `load_run(run) -> list[dict]`, `load_fragments(item) -> dict[str, str]`, `mpe_contract.validate_fragment(problem, text) -> list[str]`를 소비한다. 다음 Task에 원본과 동일한 SourcePack, 15개 초안 조각, 보호 해시와 phase 검사기를 제공한다. 검사기는 `/tmp` 전역 context 파일에 의존하지 않고 RUN의 `run.json`에서 REPO를 읽는다.

- [ ] **Step 1: 기준선·보호 파일과 기존 발행 스냅샷을 기록한다.**

Run: `git status --short --branch`, `git log -2 --oneline` 및 SHA-256 대조. SOURCE의 계획 시점 해시는 `8296aacece14bd005ffd91020ebc28621bd8f9ab3bda3b0cea433187e9d0adc4`, pack.json은 `37eb572150b4b5617f9b483754c907a5c8efdff9483adfcecc0c5a09465d180b`, blueprint.md는 `7dd1609671b23d46c93d22ca77cc8138f5576bd676faf827ba1dc8fc948f8e1e`다. 달라졌으면 차이를 조사하고 이전 계획의 판정을 그대로 재사용하지 않는다. 빈 RUN 제약 때문에 상태 JSON은 extract 뒤 넣는다. 원 발행 소유 경로의 파일 집합·바이트를 `RUN/pre-publish/`에 복사하고, 나머지 장 파일과 PILOT의 파일/심볼릭 링크 상태를 보호한다. 실제 읽은 수업 파일도 보호 목록에 추가한다.

extract 전에 쓰는 상태 JSON과 발행 스냅샷은 **RUN 밖의 임시 폴더**에 둔다. RUN 자체는 만들지 않거나 완전히 비워 두고, Step 2의 extract 성공 뒤 각각 `RUN/rollout-state.json`, `RUN/pre-publish/`로 옮긴다.

Expected: 초기 자료는 동일하며 보호 범위와 복구 스냅샷이 RUN 밖에 기록돼 있다. 이 단계는 원본 수정이나 새 source.json 조작을 하지 않는다.

- [ ] **Step 2: 전체를 추출하고 15개 조각의 출발점을 복사한다.**

Run: `python3 "$SKILL/scripts/mpe_cli.py" extract --repo "$REPO" --target "$SOURCE" --run "$RUN"`.
extract가 성공한 뒤 Step 1의 상태/스냅샷을 RUN으로 옮긴다. 기존 PUBLISHED/fragments에서 15개를 복사하고, p2/p3/p7만 PILOT/explanations의 커밋된 시범 조각으로 교체한다.

Expected: forecast profile, p1~p15, 75선지, 각 subparts=`('main',)`. 이전 review/validation은 새 review로 복사하지 않는다.

- [ ] **Step 3: phase pilot의 표제 검사를 작성하고 RED를 확인한다.**

검사기는 보호 해시·파일 집합과 15개 조각의 구조를 먼저 검사한 다음, p2와 p7의 understand에 정확한 결함 표제가 있는지 검사한다.

```python
from mpe_shared import parse
for pid in ('p2', 'p7'):
    root = parse(fragments[pid])
    section, = list(root.find_all(lambda n: n.attrs.get('data-explanation') == 'understand'))
    assert any(n.text() == '문항 결함:' for n in section.find_all(lambda n: n.tag == 'strong')), pid
```

Run: `python3 "$RUN/check_authoring.py" --run "$RUN" --phase pilot`.
Expected: 보호/구조 PASS, p2/p7의 기존 표제 차이로 해당 assertion FAIL.

- [ ] **Step 4: 새 조각에서 표제만 통일하고 GREEN으로 만든다.**

p2 understand의 `원문 표현 주의:`, p7 understand의 `판정의 전제:`를 `문항 결함:`으로 바꾼다. P7은 그 전제가 원문에 명시되지 않았음을 첫 안내 문장에 분명히 쓴다. p3은 실제 근거 오류가 추가로 발견되지 않는 한 시범 바이트를 유지한다. P2의 RNA 해석, P7의 조건부 B와 I/III 가닥 수 미확정은 유지한다.

Run: Step 3과 같은 명령. Expected: PASS, PILOT 및 기존 발행물 해시 변화 0. task 완료 시 이 결과를 실행 ledger에 기록하며 자동 커밋하지 않는다.

### Task 2: 나머지 12문항의 판단 기준과 75선지 대응 완성

**Files:** 수정 새 `FOLDER/explanations/p1.html`, `p4.html`, `p5.html`, `p6.html`, `p8.html`~`p15.html`; 생성 `FOLDER/evidence/option-audit.md`; 확장 `RUN/check_authoring.py`의 phase full.

**Interfaces:** Task 1의 15개 조각·보호 목록을 소비한다. full 검사는 `load_fragments`와 `validate_fragment`의 구조 결과 및 75선지 감사 범위를 검증한다. 의미 검토는 도구로 입증되지 않으므로 감사표를 실제 자료와 대조해 별도로 판정한다.

- [ ] **Step 1: 읽을 근거를 찾고 기존 12문항의 의미 검토 RED를 기록한다.**

강의노트 5장, 교과서 05장, 기출 5강 합본, 복습노트 1001/1006/1008의 필요한 절을 실제로 읽는다. `rg --files`로 한글 실제 경로를 발견한다. PDF 해당 쪽은 렌더링으로 확인하며 교과서의 PDF 쪽과 인쇄 쪽을 구별한다. 기존 해설의 p.117/118/121 같은 숫자를 검증 없이 복제하지 않는다.

감사표의 열은 `문항 | 선지 | 실제 주장 | 적용 기준 | 적용 결과와 선택/제외 | 근거 파일/쪽 | 검토 상태`다. 75개 키 `(p1,A)`~`(p15,E)`가 정확히 하나씩 있어야 한다. 초기 상태는 `pending`으로 만들고, 현재 P1 B와 P5 E 등 확인된 불일치를 `fail`로 기록한다. Task 1의 세 문항도 새 전체 검토 범위에 포함한다.

Run: `python3 "$RUN/check_authoring.py" --run "$RUN" --phase full`.
Expected: 보호·구조·감사 범위 PASS, pending/fail이 남아 전체 의미 완료 조건 FAIL. 단순 키워드 검사를 의미 PASS로 대체하지 않는다.

- [ ] **Step 2: 아래 기준으로 12문항을 저작하고 선지마다 실제 적용을 쓴다.**

|ID|이번 저작에서 반드시 확인할 내용|
|---|---|
|P1|부정형 방향을 굵게 명시. 교정/후속 수선/잔여 돌연변이를 구별. B ‘모두 맞다’는 다른 보기 판정 뒤 평가하며 ‘일반 사실이 맞다’로 독립 승인하지 않음. 메타 보기 적용 범위의 해석이 충돌하면 기록하고 보류|
|P4|번역에 직접 쓰이는 주형·운반체·재료·리보솜과 전사 효소를 구별. 분자 명칭에 무조건 ‘틀려요’를 붙이지 않고 질문의 제외 대상임을 설명. 소단위체 자체가 펩타이드 결합을 촉매한다고 확대하지 않음|
|P5|주형의 3′/5′, RNA의 U, 위치별 상보성을 실제 10개 염기에 대입. E `CUUAGGCCAU`는 정답 서열의 단순 역순이라고 쓰지 않음. 정답 `AUGGCCUAAG`의 실제 역순은 `GAAUCCGGUA`임을 검사해 잘못된 오답 진단 제거|
|P6|그림의 분기점 진행 화살표, (가)/(나)/(다), 각 말단과 실제 합성 방향을 화면에서 짝지음. 주형을 읽는 방향/새 가닥 합성/분기점 이동을 분리|
|P8|표지 (가)~(라)를 DNA 서열인지 단백질인지, 결합 상대와 기능이 무엇인지로 판정. 진핵 개시를 RNA 중합효소의 단독 직접 결합으로 일반화하지 않음|
|P9|1~3,4~6,7~9번 염기 경계와 9번 치환을 직접 표시. 종결코돈은 아미노산 수에서 제외. 주어진 암호화 부위에서 정상 5개·변이 2개를 재계산|
|P10|표의 +/+와 -/-부터 판독. 억제자-작동자와 중합효소-프로모터 구별. 표현형만으로 유일 유전자형을 확정하지 않으며 II의 원인을 두 가지로만 제한하지 않음. 억제자 구조 변화와 완전 분해를 구별|
|P11|캡/꼬리의 첨가 위치·구조·기능과 번역되는 암호화 부위를 구별. 사용하지 않는 꼬리 길이 수치 등은 제거하되 E의 핵 밖 이동 기능은 근거 확인|
|P12|주형 수·프라이머·기질·신생 가닥 방향·산물을 같은 항목으로 비교. 프라이머 불필요를 다른 개시 인자도 불필요하다는 뜻으로 확대하지 않음. 일반 문항을 진핵 핵 가공으로 한정하지 않음|
|P13|아세틸화→전하/접근성의 인과와 탈아세틸화 구별. DNA 메틸화·유전성은 이 문항/수업 모형의 근거와 범위를 유지하고 항상/유일이라는 결론을 검증 없이 일반화하지 않음|
|P14|표지·분해 장치·기질·산물·재사용 분자를 구별. 아미노산 개수 같은 판정에 쓰이지 않는 배경 수치 제거. 단백질 분해와 RNA 분해를 구별|
|P15|분자 길이·표적 종류·결합 서열·조절 수준과 상보성을 대조. 수업의 부분/높은 상보성 비교를 제시하되 부분 결합이면 mRNA 분해가 절대 없다고 단정하지 않음|

각 문항에서 삭제·통합한 문장과 필요해서 유지한 설명을 하나 이상 기록한다. 기존 문장이 이미 기준을 충족하면 유지하고, 변경 개수를 채우기 위해 고치지 않는다. start는 실제 서열 정렬/계산 첫 조작이 필요할 때만, retry는 설명을 가리고 적용할 과제가 있을 때만 둔다.

- [ ] **Step 3: R1–R3와 full 검사를 GREEN으로 만든다.**

R1: P1의 다른 보기 → 메타 보기 → 부정형 답 선택 순서, P4의 역할과 제외 대상을 자료/원문에 대조해 설명할 수 있다.
R2: P5는 방향이 붙은 위치별 서열 표로 모든 후보를 검증하고, P6은 실제 SVG 표지/화살표, P9는 실제 염기 번호와 종결 전 코돈 수로 검증한다. `assert 'AUGGCCUAAG'[::-1] == 'GAAUCCGGUA'`로 P5의 기존 단순 역순 설명을 반증한 기록을 남긴다.
R3: P7은 비율 동률로 구조 확정 금지, P10은 가능한 원인과 확정 원인 구별, P13/P15는 자료가 허용하는 범위만 말한다. understand/solve/verify/sum의 조건이 서로 같아야 한다.

Run: `python3 "$RUN/check_authoring.py" --run "$RUN" --phase full`.
Expected: 15조각 구조와 보호 파일 PASS, 감사 키 75개 일치, 실제 검토된 행에 pending/fail/disputed 0일 때만 GREEN이다. 해석·답 충돌이 남으면 이 task를 통과했다고 기록하지 않는다. Task 3의 독립 검토로 충돌을 확인하고 수정 예산 안에서 재검토하되, 끝내 해소되지 않으면 Task 4의 발행 단계는 건너뛰고 보류 보고만 한다. task 완료 근거를 ledger에 남기며 자동 커밋하지 않는다.

### Task 3: 전체 조립과 네 검토를 현재 해시에 결속

**Files:** 생성 새 stage, `FOLDER/review.json`, `FOLDER/evidence/independent-full.md`, RUN의 preview/browser 결과·화면·수정 이력.

**Interfaces:** `mpe_cli.build(item, fragments)`, `load_artifacts(item) -> Artifacts`, `mpe_render.check_artifacts(pack, artifacts) -> list[str]`, `artifact_hashes(artifacts) -> dict[str,str]`, `mpe_contract.validate_reviews(pack, fragments, reviews) -> list[str]`를 소비한다. 다음 Task에 현재 해시와 결속된 15개 `pN:main`의 content/independent 검토 및 네 상위 pass를 제공하거나, 발행 보류 사유를 제공한다.

- [ ] **Step 1: build/check를 실행하고 미검토 발행 거부를 검증한다.**

Run: `python3 "$SKILL/scripts/mpe_cli.py" build --run "$RUN"`와 `check --run "$RUN"`.
Expected: machine PASS, 새 review의 네 status는 모두 not_run, content/independent items는 각각 p1:main~p15:main이다. `validate_reviews(...)`는 실제 검토 pass 누락으로 오류를 반환해야 한다. 실자료의 미승인 publish를 테스트 목적으로 실행하지 않는다.

- [ ] **Step 2: 전체 source_visual/content/independent를 수행한다.**

source_visual은 15문항의 지문·선지·수치·표·그림을 실제 원자료/수업 근거에 대조한다. content는 75선지 감사와 R1–R3, 불필요한 문장, 부정형·결함 공개·요약 일관성을 검토한다. independent는 새 별도 문맥에 15문항 원문만 제공해 재풀이하며, 컨트롤러가 현재 정답키와 비교한다. 계산 P5/P9는 `exact`, 원리 판정은 `qualitative`로 기록한다. 정상 문항은 불필요한 가정을 추가하지 않는다.

Expected: 모든 항목에 실제 reviewer/evidence/method/conclusion이 있거나, 실패/해석 충돌이 명시된다. P2/P7은 공개된 조건부 판단과 독립 풀이가 일치할 때만 해당 공개 규칙으로 통과시킨다. 다른 충돌은 정답에 이유를 맞추어 통과시키지 않는다.

- [ ] **Step 3: R5의 실제 화면·상대 링크를 검토한다.**

커밋된 PILOT/preview.py의 경로 매핑을 참고하되 새 stage를 사용한다. 127.0.0.1에서 `/웹과제예상/5장/` 아래는 stage를 우선하고 나머지는 REPO 원자료로 연결한다. URL 디코딩·정규화와 내부 경로 검사를 유지하며 기존 파일은 이동하지 않는다. 경로와 결과를 새 RUN에서 독립적으로 찾고, 옛 context.json의 절대 RUN 경로를 재사용하지 않는다.

1280×900/375×812 × light/dark의 4조합에서 15문항 모두를 검사한다. 각 A–E 클릭→판정/알림, 다시 풀기, 넓은 화면의 해당 해설 이동을 확인해 총 300회 선택을 검증한다. 목차·이전/다음·요약·데스크톱 원문 탭/모바일 출처 접기·문제 원본/정리노트 앵커를 실제로 연다. P6/P8 그림 확대·표지, P7/P10 표, P5/P9 방향/계산과 수식을 직접 본다. 1024 너비에서도 목차와 문제 기본 열림을 확인하고 패널 왼쪽/오른쪽/띄우기·이동/크기 제한을 대표 문항에서 검사한다.

Expected: 콘솔/KaTeX 오류·누락 자원·문서 가로 넘침 0. 짧은 식의 불필요한 math-row/스크롤 0, 빈 선택 구역 제목 0. 패널 전환과 글꼴 로딩이 끝난 뒤 이미지를 저장하고 직접 확인한다. 모바일 요약은 보이는 ‘닫기’로 닫으며, 같은 문서의 앵커 이동이 HTTP 응답 None일 수 있음을 오류로 오인하지 않는다. 서버는 종료한다.

- [ ] **Step 4: R4의 승인 무효화 회귀와 최종 상태를 확인한다.**

Run: `PYTHON -m pytest "$SKILL/tests" -q`. PYTHON은 실행 시 pytest/Playwright 사용 가능 여부를 확인한 격리 환경이다. 이전 테스트 수를 성공 판정에 하드코딩하지 않는다. 기존 `test_rebuild_resets_reviews_and_blocks_stale_pass`, `test_changed_forecast_context_requires_reextract`, `test_disputed_cannot_publish`, `test_replace_failure_rolls_back_pair`, `test_republish_preserves_pack_files`가 실행되어야 한다. 이 fixture 승인 생성기를 실자료 review 작성에 사용하지 않는다.

실제 자료는 `check_artifacts == []`, `validate_reviews == []`, review input_hash=`payload_hash(pack, fragments)`, artifact_hashes 현재 일치, references의 실제 path/SHA-256 일치를 모두 확인한다. review/evidence를 stage 안에서 사후 편집해 이미 묶인 산출 해시를 바꾸지 않는다. 새 근거가 필요하면 build부터 다시 수행한다.

Expected: 회귀 테스트 PASS와 전체 실검토 PASS가 각각 존재한다. 실패를 수정할 때 attempt를 올리고 build/check 및 네 검토를 반복한다. attempt=2 뒤 미해결이면 Task 4의 publish는 실행하지 않고 보류 보고서만 작성한다.

### Task 4: 검토된 해설만 백업·교체하고 결과 보고

**Files:** 위 네 발행 소유 경로, RUN의 교체 전/후 목록과 백업, 새 전체 결과 보고서. SOURCE·다른 버전·PILOT는 보존한다.

**Interfaces:** Task 3의 승인된 Artifacts/fragments/reviews와 Task 1의 원본/발행 백업을 소비한다. `mpe_publish.publish_explanation(pack, artifacts, fragments, reviews, destination, backup_dir)`는 목적지가 `pack.path.parent`일 때만 발행하며 CLI `publish --run`이 이를 호출한다. 성공 시 검토된 파일과 validation.json을 제공하고, 실패 시 기존 발행 상태를 보존/복구한 결과를 제공한다.

- [ ] **Step 1: 교체 직전 보호 상태와 승인 유효성을 다시 확인한다.**

원본·문맥·참조·기존 발행 파일이 기준선 이후 외부에서 달라지지 않았는지 확인하고, 백업의 파일 집합/해시가 교체 직전 소유 파일과 일치해야 한다. 다른 작업이 바꾼 파일이면 덮지 말고 차이를 조사한다. gate가 실제 pass가 아니면 이 단계에서 발행을 중단한다.

Expected: 보호 파일 변화 0, 백업 일치, Task 3 승인 해시 일치. 실제 파일에 강제 실패를 주입하지 않는다. 쓰기 실패 복구/잠금은 기존 fixture 회귀 테스트로 확인한다.

- [ ] **Step 2: 승인된 stage를 기존 CLI로 발행한다.**

Run: `python3 "$SKILL/scripts/mpe_cli.py" publish --run "$RUN"`.
Expected: 지정 네 소유 경로만 교체되고 `FOLDER/backups/`에 기존 파일이 보존된다. 원 문제·pack.json·blueprint.md·다른 버전·PILOT 변화 0. 조립 HTML 직접 패치나 수동 validation 승인 생성은 하지 않는다.

- [ ] **Step 3: 최종 발행 경로를 검증하고 필요하면 소유 범위만 복구한다.**

발행 파일을 검토 stage의 파일별 해시와 대조하고 validation.json의 전체 15항목·네 pass·현재 hash를 확인한다. 최종 위치에서 4개 화면 조합으로 15문항의 표시와 원 문제/노트 링크, 그림·표·요약을 다시 확인한다. 상태가 다르면 완료로 보고하지 않는다.

publisher 내부 쓰기 실패는 기존 rollback 결과를 검사한다. 발행 후 검증 실패라면 RUN/pre-publish 스냅샷의 기존 소유 파일을 복원하고, 이번 발행에서 새로 만든 소유 파일만 제거해 이전 파일 집합/해시로 되돌린다. 복원 전 현재 파일이 이번에 쓴 해시와 같은지 확인해 외부 변경을 덮지 않는다. 범위를 벗어난 삭제·원 문제 수정·git reset/clean은 금지한다. 복구 불가면 실제 상태와 경로를 보고한다.

Expected: 성공은 검토 stage와 발행본 일치 및 보호 검사 PASS, 실패는 이전 소유 상태의 복구 검사 PASS 또는 구체적인 미복구 상태 보고다.

- [ ] **Step 4: 전체 결과와 남은 문항 결함을 보고한다.**

새 보고서에 15문항 적용 여부·75선지 감사·기계/네 실검토 결과·독립 답 비교·attempt·발행/보류·원본 보존·stage와 최종 HTML/MD/백업의 실제 경로를 기록한다. P2/P7 문항 수정과 다른 학술적 충돌은 별도 목록에 둔다. 기존 시범 보고서나 그 보존 자료를 수정하지 않는다. 실제 학습 효과를 주장하지 않는다.

Expected: 전체 검토와 발행을 모두 통과했을 때만 ‘전체 해설 교체 완료’로 쓴다. 보류라면 통과한 stage/보존된 기존 HTML과 실패 이유를 구별해 링크한다. 새 보고서 경로가 이미 있으면 고유 접미사를 사용한다.

- [ ] **Step 5: Git 범위를 보고하고 자동 커밋하지 않는다.**

Run: `git diff --name-only`, `git status --short`와 보호 해시 검사.
Expected: 성공 시 변경은 네 해설 소유 경로·새 계획/보고서뿐이며, 실패 시 기존 발행 파일 변화도 0이어야 한다. tmp 전체를 stage하지 않는다. 검토된 생성 HTML의 기존 공백처럼 바이트 보존과 충돌하는 항목은 그대로 설명하고, whitespace 정리를 이유로 검토 뒤 산출물을 수정하지 않는다. 별도 커밋 요청이 있으면 그때 명시 경로만 커밋한다.

## Self-Review

- [x] 기준 명시·75선지 적용·불필요한 내용 삭제를 Task 2에, 시범 표제 유보를 Task 1에 연결했다.
- [x] 실제 15문항·75선지·main 소문항과 기존 함수/출력 경로를 읽기 전용으로 확인했다.
- [x] 다섯 Review Focus를 R1–R5·기존 승인 거부/복구 테스트·실제 화면 검사에 연결했다.
- [x] 새 생산 API 없이 RUN 전용 도우미만 사용하며 이전 시범 승인·전역 tmp context·fixture 승인을 실검토로 재사용하지 않는다.
- [x] 원 문제 변경 제외와 해설 교체 포함을 구별했고, 승인 실패 시 보존/복구 경로를 명시했다.
- [x] 직접 구현 방식을 유지하며 계획 검토 전 저작·검토 기록 생성·발행·커밋을 시작하지 않는다.
