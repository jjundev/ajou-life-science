# 문항 감사와 선별 (메인 에이전트)

## 원칙
- 문항은 **23·24 기출 합본**(`23, 24 소스/N강 합본.pdf`, 파일명에 `+`가 섞여 있다)과 **웹과제 bank**(`웹과제/N장/questions.json`)에서만 가져온다. 자작·변형 금지.
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
- 그 장 `웹과제/N장/questions.json`이 있으면 검증한다(저장소 루트에서):
  ```bash
  .venv-question-bank/bin/python -m scripts.question_bank validate '웹과제/N장/questions.json' --complete
  ```
  전용 venv가 없으면 `python3 -m venv --system-site-packages .venv-question-bank && .venv-question-bank/bin/python -m pip install 'jsonschema>=4.18,<5'`로 만든다. 검증이 실패해도 멈추지 않는다. 실패한 필드와 source를 보고서 "미해결"에 적고 문항은 그대로 쓴다.
- `questions.json`은 없고 `웹과제/N장/raw/` 캡처만 있으면 **등록되지 않은 자료**다. 보고서에 그렇게 적는다("웹 자료 없음"이라고 쓰지 않는다). 이 경우 partA는 없다.
- 목록 보기:
  ```bash
  python3 - <<'EOF'
  import json
  b = json.load(open("<REPO>/웹과제/N장/questions.json", encoding="utf-8"))
  for q in b["questions"]:
      text = " ".join(c.get("text", f"[{c['type']}]") for c in q["original"]["content"])
      print(q["id"], q["number"], q["analysis"]["answer_option_id"], q["observations"].get("official_answer"), text[:60])
  EOF
  ```
- 카드에는 `original.content`(문제), `original.options`(보기, id가 `A`~`E`), `analysis.answer_option_id`(분석 정답), `analysis.option_diagnostics`(보기별 설명)를 쓴다. `observations.official_answer`가 있고 분석 정답과 다르면 `key-check.md`에 적고 카드에 공개한다.
- `RUN/figures/`에는 PNG만 둔다(기출 그림 자르기, `card-rules.md`). `html2md.py`가 변환할 때 `figures_<range>/`의 SVG 파일을 모두 지우고 다시 내보내므로, SVG 파일은 `RUN/figures/`에 복사하지 않는다.
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
| 웹과제 1장 | q03 | 공유결합 | s2-bond | 이전 팩 | 정리노트/0903.md 매핑표 포함 |
```
상태는 넷 중 하나다.
- **포함**: 풀이에 필요한 개념을 모두 이번 범위나 이전 수업에서 배웠고, 그중 하나 이상이 이번 범위에서 배운 것이며, 이전 팩에 아직 포함되지 않았다.
- **이전 팩**: 이미 이전 팩에 포함되었다. 확인 위치: 새 형식 `복습노트/*/복습문제_*.html`의 `data-source`, 예전 형식 `정리노트/MMDD.md`의 `## 부록. 문항 ↔ 개념 매핑` 표(상태 "포함")와 WEB 문항 매핑 표(상태 included/review).
- **보류**: 필요한 개념 중 아직 배우지 않은 것이 있다. 사유에 무엇을 언제 배우면 풀 수 있는지 적는다.
- **범위 밖**: 이번 장과 무관하거나 수업에서 다루지 않기로 한 내용이다. 근거(STT 타임스탬프나 강의계획서)를 적는다.

포함 문항마다 `problem-pages.txt`에 `p<N> 기출 3강 12 → work/exam/3강-p3.png`처럼 원문 위치를 적는다.

## 4. 정답 대조 → `RUN/key-check.md`
- 기출은 인쇄된 답(빨간 표시)을 PNG에서 읽고, 모든 보기를 독립적으로 판단해 대조한다. **답안지를 그대로 믿지 않는다.** 1강 합본은 40문항 중 3개(2, 30, 38번)가 틀려 있었다.
- 판단이 어긋나면 manifest `answer`는 **옳다고 판단한 쪽**으로 두고 `key-check.md`에 `기출 3강 12: 인쇄 (2) → 판단 (3), 근거: …`를 적는다. 카드 풀이에서 공개한다. 조용히 고치지 않는다.
- 보기가 없는 빈칸 문항은 보기를 만들지 않고 빈칸 그대로 카드에 싣는다. 정답은 낱말이다.
- 모든 포함 문항의 정답이 manifest `answer`와 카드 `정답:` 줄에 같게 들어간다.

## 5. 난이도 (`level`)
1 개념 확인(정의·이름) · 2 판별·비교(보기마다 경계 판단) · 3 그림 판독이나 여러 개념 결합.
