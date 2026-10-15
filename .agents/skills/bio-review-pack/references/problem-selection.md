# 문항 감사와 선별 (메인 에이전트)

## 원칙
- 문항은 **23·24 기출 합본**(`23, 24 소스/N강 합본.pdf`, 파일명에 `+`가 섞여 있다)과 **웹과제 bank**(`웹과제/N장/questions.json`)에서만 가져온다. 원문 문항(partA·partB)은 자작·변형 금지. 원문과 구별된 생성 변형은 partC에만 둔다(6절).
- 범위 안의 문항은 **전부** 넣는다. 개수 상한은 없다.
- 이번 수업이 다룬 장의 모든 문항을 하나도 빼지 않고 분류한다. 합계가 합본 전체 문항 수와 bank 전체 ID 수와 같아야 한다.

## 1. 자료 준비 (요약 에이전트가 도는 동안)
합본을 쪽마다 dpi 170 PNG로 렌더링한다. 텍스트 추출은 2단 조판이 섞이고 **빨간 글씨 정답 표시가 사라진다.** 반드시 이미지로 읽는다.
```bash
REPO=… RUN=… CH="3" python3 - <<'EOF'
import fitz, os, unicodedata as u
repo, run = os.environ["REPO"], os.environ["RUN"]
src = os.path.join(repo, "23, 24 소스")
os.makedirs(os.path.join(run, "work", "exam"), exist_ok=True)
for ch in os.environ["CH"].split():
    hit = [n for n in os.listdir(src) if u.normalize("NFC", n).startswith(f"{ch}강") and n.endswith(".pdf")]
    if not hit:
        print(f"{ch}강 합본 없음"); continue
    doc = fitz.open(os.path.join(src, hit[0]))
    for i, page in enumerate(doc, 1):
        path = os.path.join(run, "work", "exam", f"{ch}강-p{i}.png")
        page.get_pixmap(dpi=170).save(path); print(path)
EOF
```
`CH`는 공백으로 구분한 장 번호들이다.

## 2. 웹과제 bank
- 그 장 `웹과제/N장/questions.json`이 있으면 검증한다(작업 폴더를 `REPO`로 두고 실행한다 — 상대 경로 venv와 `-m scripts.question_bank`가 이를 전제한다. Bash 도구의 작업 폴더가 REPO가 아니면 `cd "$REPO" && …`를 이 명령에서만 허용한다):
  ```bash
  .venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/N장/questions.json' --complete
  ```
  전용 venv가 없으면 `python3 -m venv --system-site-packages .venv-question-bank && .venv-question-bank/bin/python -m pip install 'jsonschema>=4.18,<5'`로 만든다. 검증이 실패해도 멈추지 않는다. 실패한 필드와 source를 보고서 "미해결"에 적고 문항은 그대로 쓴다.
- `questions.json`은 없고 `웹과제/N장/raw/` 캡처만 있으면 **등록되지 않은 자료**다. 보고서에 그렇게 적는다("웹 자료 없음"이라고 쓰지 않는다). 이 경우 partA는 없다.
- partA 제외는 본문 피드백 제외가 아니다. `웹과제/N장/note-feedback.md`가 있으면 `references/note-feedback.md`대로 실제 문항의 판별 기준을 범위·토픽에 연결한다. 공식 답 미확인과 정본 미등록 상태는 유지한다.
- 목록 보기(`CH`는 장 번호 하나):
```bash
REPO=… CH="1" python3 - <<'EOF'
import json, os
path = os.path.join(os.environ["REPO"], "웹과제", f'{os.environ["CH"]}장', "questions.json")
b = json.load(open(path, encoding="utf-8"))
for q in b["questions"]:
    text = " ".join(c.get("text", f"[{c['type']}]") for c in q["original"]["content"])
    print(q["id"], q["number"], q["analysis"]["answer_option_id"], q["observations"].get("official_answer"), text[:60])
EOF
```
- 카드에는 `original.content`(문제), `original.options`(보기, id가 `A`~`E`), `analysis.answer_option_id`(분석 정답), `analysis.option_diagnostics`(보기별 설명)를 쓴다. `observations.official_answer`가 있고 분석 정답과 다르면 `key-check.md`에 적고 카드에 공개한다.
- `observations.selected_option_id`는 응시 화면에서 고른 보기일 뿐 정답이 아니다. 정답이나 풀이 근거로 쓰지 않는다.
- `RUN/figures/`에는 PNG만 둔다(기출 그림 자르기, `card-rules.md`). `html2md.py`가 변환할 때 `.assets/figures_<range>/`의 SVG 파일을 모두 지우고 다시 내보내므로, SVG 파일은 `RUN/figures/`에 복사하지 않는다.
- 웹과제 그림은 SVG다. 문항 `content`의 `{"type": "figure", "asset_id": "q09"}` 항목은 bank `assets`에서 같은 `id`를 찾는다. `exam.path` SVG(bank 폴더 기준 경로, 예: `image/q09.svg`) 원문을 카드 `div.problem` 안 `<figure class="figure">`에 인라인으로 넣고 루트 `<svg>`의 `aria-label`에 `exam.alt`를 쓴다.
- `explained.path` SVG는 해설이 들어 있으므로 풀이(`details.solution`) 안에만 넣는다(`aria-label`은 `explained.alt`). 문제·힌트·원문 정보에는 넣지 않는다.
- 인라인 SVG의 `id`가 페이지에서 겹치지 않게 모든 `id`에 `<pid>-` 접두어를 붙이고, 그 id를 가리키는 `aria-labelledby`, `url(#…)`, `href="#…"`도 같이 바꾼다. 루트 `<svg>`에는 `id="<pid>-exam"`(풀이용은 `id="<pid>-explained"`)을 준다. MD 변환 때 이 id가 그림 파일 이름이 된다.

## 3. 문항 감사 → `RUN/question-audit.md`
장의 모든 문항을 한 줄씩 적는다.
```markdown
| 출처 | 번호 | 질문 요약 | 필요한 개념(토픽 id) | 상태 | 사유 |
|---|---|---|---|---|---|
| 기출 3강 | 12 | 동원체의 뜻 | s1-chromosome | 포함 | |
| 기출 3강 | 21 | 감수분열 교차 | — | 범위 밖 | 다음 수업 예고만(0922 49:10) |
| 웹과제 1장 | q03 | 공유결합 | s2-bond | 이전 팩 | 복습노트/0903 복습문제에 포함 |
```
상태는 넷 중 하나다.
- **포함**: 풀이에 필요한 개념을 모두 이번 범위나 이전 수업에서 배웠고, 그중 하나 이상이 이번 범위에서 배운 것이며, 이전 팩에 아직 포함되지 않았다.
- **이전 팩**: 이미 이전 팩에 포함되었다. 확인 위치: `복습노트/*/복습문제_*.html`의 `data-source`.
- **보류**: 필요한 개념 중 아직 배우지 않은 것이 있다. 사유에 무엇을 언제 배우면 풀 수 있는지 적는다.
- **범위 밖**: 이번 장과 무관하거나 수업에서 다루지 않기로 한 내용이다. 근거(STT 타임스탬프나 강의계획서)를 적는다.

포함 문항마다 `problem-pages.txt`에 `p<N> 기출 3강 12 → work/exam/3강-p3.png`처럼 원문 위치를 적는다.

## 4. 정답 대조 → `RUN/key-check.md`
- 기출은 인쇄된 답(빨간 표시)을 PNG에서 읽고, 모든 보기를 독립적으로 판단해 대조한다. **답안지를 그대로 믿지 않는다.** 1강 합본은 40문항 중 3개(2, 30, 38번)가 틀려 있었다.
- 판단이 어긋나면 manifest `answer`는 **옳다고 판단한 쪽**으로 두고 `key-check.md`에 `기출 3강 12: 인쇄 (2) → 판단 (3), 근거: …`를 적는다. 카드 풀이에서 공개한다. 조용히 고치지 않는다.
- 보기 둘 이상이 성립하면 `key-check.md`에 `기출 3강 16: 모호 — 인쇄 (4) 유지, 보기 (5)도 성립 가능, 근거: …`처럼 적는다(카드 작성자가 이 줄을 보고 모호성을 공개한다).
- 보기가 없는 빈칸 문항은 보기를 만들지 않고 빈칸 그대로 카드에 싣는다. 정답은 낱말이다.
- 모든 포함 문항의 정답이 manifest `answer`와 카드 `정답:` 줄에 같게 들어간다.

## 5. 난이도 (`level`)
- 1: 정의·관계·도식을 직접 식별. 예: EFG→GFE 배열을 읽고 역위 판별.
- 2: 한 가지 원리를 적용하거나 짧은 추론 수행. 예: Ff×Ff의 환자 확률, 기본 가계도 추론.
- 3: 여러 조건·원리를 연결하거나 추가 조건부 계산 수행. 예: 정상 자녀의 보인자 확률 2/3.
- 그림 유무·부정형·보기 개수로 수준을 자동 상향하지 않는다. 필요한 최소 풀이 과정으로 분류한다. 수준 1~2는 기본, 수준 3은 심화다. 원문은 그대로 두고 level만 이 기준으로 분류한다.

## 6. 변형 연습(partC) — 원문과 구별된 생성 문제
이미 풀어 본 원문은 새 문제 대비력을 재는 데 쓸 수 없다. 그래서 아직 보지 않은 변형을 따로 둔다.
- 대상: 요약의 `⚠️ 혼동 지점`과 포함 문항의 오답 진단에서 나온 **핵심 혼동 묶음**, 그리고 `references/webquiz-style.md`의 웹과제 유형. 그 파일 4절로 장별 유형·기본/심화 목표를 먼저 정하고 혼동 묶음에 할당한다. ㄱㄴㄷ·장 섞기·낯선 참 진술은 선택 유형이며, 유형 개수를 채우기 위해 범위 밖 사실을 추가하지 않는다. 합계 10~15개, 토픽당 최대 3개. 범위가 좁아 못 채우면 만든 만큼만 넣고 보고서에 사유를 적는다.
- 형태(필요한 것만): 명칭 바꾸기, 참/거짓 뒤집기(틀린 보기를 고쳐 쓰게 하기), 사례·조건 바꾸기, 그림 표현 바꾸기(회전·표지 교체. 그림은 정리노트의 `fig-*` 클래스로 카드에 인라인 SVG로 그리고(`content-rules.md` SVG 그림 규칙), `RUN/figures/`에 파일로 두지 않는다), 역질문(기능→구조, 조건→분류). 분류 개념이면 포함되는 것과 제외되는 것을 함께 묻는다.
- 표현 전환을 선택한 행은 `variants.md`의 기존 `형태` 칸에 `원래 표현 → 새 표현 / 불변 판별 기준`을 적고, `최소 풀이 단계`에 그 기준을 적용하는 과정을 적는다. 명칭을 바꿀 때도 같은 대상임을 판단하는 기준을 남긴다. `형태` 칸의 쌍둥이 원문 출처·낯선 참 진술 교재 출처는 함께 유지한다. 원문을 그대로 다시 푸는 것만으로 새 표현 연습을 완료했다고 세지 않는다. 표현 전환을 선택하지 않은 행에는 이 기록을 요구하지 않는다.
- 예(1장 구조 판별): `원문 아미노산 구조 → 배치·곁사슬이 다른 구조 / 중앙 탄소의 아미노기·카복실기·H·R 연결`을 `형태`에, `네 연결기 확인 → 아미노산 → 단백질`을 `최소 풀이 단계`에 적는다. 새 아미노산 이름 암기를 요구하지 않으며, 이 예를 다른 장의 고정 문항으로 쓰지 않는다.
- 명칭 회상: `+용어`는 [공통 용어 바꿔 쓰기](webquiz-style.md)의 근거 있는 이름→현상·현상→이름 연결로 설계한다. `variants.md`의 기존 형태·근거 토픽·오답 의도 칸에 질문 방향과 구별할 단위/단계를 적는다. 모든 동의어를 문제에 병기해 답을 미리 알려 주지 않고 풀이에서 대응을 공개한다. 단위 진단은 이름·질문 방향을 유지하고 대상 하나만 바꾸는 등, 무엇 때문에 판별이 달라졌는지 알 수 있게 한다. 새 필드·유형을 추가하지 않는다.
- 범위: 이번 범위와 이전 수업에서 배운 것만. 금지어를 쓰지 않는다. 원문 기출·웹과제 문장을 그대로 재사용하지 않는다. 단, 쌍둥이는 발문만 원문 그대로 쓰고 보기는 새로 쓴다(`webquiz-style.md` 3절).
- 정답이 하나로 정해지게 만들고, 메인 에이전트가 manifest `answer`를 정한다. 보기는 5개가 기본이다(웹과제 형식). 개념상 5개를 만들 수 없으면 4개. 부정형 발문은 장별 근거에 맞추고, 근거가 부족하면 약 1/3을 참고한다.
- `question-audit.md`의 원문 합계에 넣지 않는다. 변형 목록은 `RUN/variants.md`에 `| id | 혼동 묶음 | 웹과제 유형 | 형태 | 근거 토픽 | 문제 요지 | 의도한 정답과 이유 | 오답 보기의 의도 | 수준 | 최소 풀이 단계 |`로 적는다. `수준`은 1~3, `최소 풀이 단계`는 답에 도달하는 짧은 과정(예: 부모 유전자형 → 자손 비율)이다. 유형에 `표`를 추가해 표 해석을 별도로 집계한다. `웹과제 유형`은 `쌍둥이`, `그림`, `상황`, `ㄱㄴㄷ`, `표`, `없음` 중 하나에, 부정형 발문이면 `+부정형`, 용어 바꿔 쓰기면 `+용어`, 낯선 참 진술이면 `+낯선참`, 장 섞기면 `+장섞기`를 붙인다(예: `그림+부정형+낯선참`). 낯선 참 진술은 `형태` 칸에 교과서 출처(예: `교재 3장 p.68`)를 적는다. 쌍둥이는 `형태` 칸에 원문 출처(예: `기출 2강 9`)를 적는다. 메인 에이전트가 3단계(작성) 전에 채우고, 카드 작성자는 이 행에 맞춰 문제와 보기를 쓴다.
