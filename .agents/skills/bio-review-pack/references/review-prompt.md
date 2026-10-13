# 리뷰어 지시문

6단계에서 두 리뷰어를 한 메시지에서 병렬로 띄운다. 블라인드 리뷰어는 `lite`에서도 띄우고, 일반 리뷰어는 `lite`면 생략한다.

## 블라인드 풀이 검사

먼저 메인 에이전트가 복습문제에서 문제·보기·그림만 뽑은 사본을 만든다(`REVIEW`는 조립된 복습문제 HTML 절대 경로). 기출 그림(`<img>`)은 PNG 경로를, 웹과제 인라인 `<svg>`는 `OUT`과 같은 폴더의 `blind-figs/<pid>-<n>.svg` 파일로 저장한 경로를 `[그림: …]` 줄로 남긴다. `OUT`의 `$RUN`은 같은 명령 앞에 붙인 `RUN=…`로는 펼쳐지지 않으므로, 같은 Bash 호출 맨 앞에 `RUN=…;`로 먼저 설정하거나 `OUT`에 절대 경로를 직접 쓴다.
```bash
REVIEW=… OUT="$RUN/work/blind-<range>.md" IDS="" python3 - <<'EOF'
import html, os, re
src = open(os.environ["REVIEW"], encoding="utf-8").read()
base = os.path.dirname(os.environ["REVIEW"])
cards = re.findall(r'<article class="card" id="(p\d+)"[^>]*>\s*<h3>(.*?)</h3>\s*<div class="problem">(.*?)</div>\s*<details', src, re.S)
ids = {i for i in os.environ.get("IDS", "").split(",") if i}
if ids:  # 보강 모드: 새 카드만
    cards = [c for c in cards if c[0] in ids]
figs = os.path.join(os.path.dirname(os.path.abspath(os.environ["OUT"])), "blind-figs")
def text(pid, h):
    n = 0
    def svg(m):  # 웹과제 인라인 SVG → blind-figs/<pid>-<n>.svg
        nonlocal n
        n += 1
        os.makedirs(figs, exist_ok=True)
        path = os.path.join(figs, f"{pid}-{n}.svg")
        s = m.group(0)
        if "xmlns=" not in s.split(">", 1)[0]:
            s = s.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        open(path, "w", encoding="utf-8").write(s)
        return f"\n[그림: {path}]\n"
    h = re.sub(r"<svg\b.*?</svg>", svg, h, flags=re.S)
    h = re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', lambda m: f"\n[그림: {os.path.join(base, m.group(1))}]\n", h)
    h = re.sub(r"</(p|li|figure)>|<br\s*/?>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
with open(os.environ["OUT"], "w", encoding="utf-8") as f:
    for pid, title, body in cards:
        f.write(f"## {pid}. {html.unescape(re.sub(r'<[^>]+>', '', title))}\n\n{text(pid, body)}\n\n")
print(len(cards), "문항")
EOF
```
출력 문항 수가 manifest 문제 수와 다르면 카드 마크업 순서를 고친 뒤 다시 만든다. 보강 모드에서는 `IDS`에 새 카드 id만 넣는다(출력 문항 수 = 새 카드 수).

---
생명과학 복습팩의 블라인드 풀이 검사를 한다. 파일은 수정하지 않는다.

- 열 수 있는 파일은 **두 개뿐**이다: 정리노트 `<RUN>/repo/복습노트/<range>/<정리노트 html>`, 문항 사본 `<RUN>/work/blind-<range>.md`(그 안의 `[그림: …]` 줄이 가리키는 그림 파일 — 기출 PNG와 `<RUN>/work/blind-figs/`의 웹과제 SVG — 도 볼 수 있다). 복습문제 HTML, manifest, 요약, 교과서, 인터넷, 다른 파일은 열지 않는다. 자기 배경지식으로 풀지 말고 정리노트에 쓰인 내용만 근거로 삼는다.
- 수준 판정 기준: 1 정의·관계·도식을 직접 식별, 2 한 가지 원리 적용·짧은 추론, 3 여러 조건·원리 연결·추가 조건부 계산. 그림·부정형·보기 개수 자체로 높이지 않는다. 기본은 1~2, 심화는 3이다.
- 문항마다 최소 풀이 단계와 수준을 독립 판정한다. 설계의 예상 수준은 보여 주지 않는다. 이 검사는 lite와 보강의 새 문항에도 적용한다.
- 문항마다 답을 고르고, 근거가 된 정리노트 토픽 id와 문장을 적는다. 정리노트만으로 판단할 수 없는 보기가 있으면 "근거 없음"으로 적고 무엇이 빠졌는지 쓴다.
- 보기 진단에 `+낯선참`으로 설계된 보기(교과서에만 있는 참인 진술)는 정리노트에 근거가 없어도 정상이다. 정답 보기의 근거만 판정하고, 그 보기 때문에 "근거 없음"으로 적지 않는다(메인 에이전트가 해당 카드 id를 알려 준다).

출력 형식(이것만):
```
| 문항 | 내 답 | 근거 토픽 | 빠진 사실 | 최소 풀이 단계 | 수준 |
|---|---|---|---|---|---|
| p1 | (2) | s1-centromere | | 위치 확인 → 기능 판별 | 2 |
| p4 | 근거 없음 | — | 보기 (3)의 방추사 부착 위치가 노트에 없음 | 판정 불가 | 판정 불가 |
```
---

메인 에이전트는 리뷰어 답을 manifest `answer`와 비교한다. 다르거나 "근거 없음"인 문항은 `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다. 고친 뒤 사본을 다시 만들어 그 문항만 다시 검사한다.

메인은 독립 수준을 manifest `level` 및 partC `variants.md`와 대조한다. 불일치하면 풀이 단계를 확인해 분류를 재검토한다. 원문은 난이도 배합 때문에 수정하지 않는다. 생성 변형은 범위·유일 정답을 확인한 뒤 수정/교체하거나 배합 차이를 보고한다. 기본/심화 실개수는 partC만 따로 센다. 기존 최대 2회 검사 한도 안에서 재검사하며, 판정 불가나 남은 차이는 미해결로 보고한다.

## 일반 리뷰 (lite에서는 생략)

---
생명과학 복습팩 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/복습노트/<range>/<정리노트 html>`, `<…/복습문제 html>`
- 근거: `<RUN>/summaries/stt-*.md`, `<RUN>/slides.txt`, `<RUN>/manifest.json`, `<RUN>/question-audit.md`, `<RUN>/key-check.md`, `<RUN>/variants.md`, `<RUN>/work/exam/*.png`, 웹과제 bank
- 규칙: `<SKILL>/references/content-rules.md`, `card-rules.md`, `problem-selection.md`

확인할 것:
1. **사실 오류**: 정의, 성립 조건, 과정의 위치·입력·출력, "항상/보통" 같은 한정어가 요약·강의노트·교재와 맞는가.
2. **누락**: 요약의 핵심 내용·강조 발언·`⚠️ 혼동 지점`·미룬 설명 중 노트에 없는 것.
3. **범위**: "예고만/안 다룸" 내용이 본문에 설명되어 있는가. 보충 레이어에 출처가 있는가.
4. **분류 경계**: 쉬운 설명이 조건을 지우거나, 과정 참여를 계의 구성원으로 쓰거나, 판별 용어를 없앴는가. 치트시트(30초 요약)는 본문과 따로 읽어도 조건·분류 경계가 살아 있는가.
5. **ELI5 품질**: 쉽게 말하면 레이어가 전문용어 없이 1~3문장인가, 그림이 개념을 실제로 보여 주는가.
6. **문항**: 문제·보기가 원문(PNG, bank)과 글자까지 같은가, 모든 보기에 진단이 있는가, 원문 문항의 정답이 `key-check.md`와 맞는가(직접 다시 판단), 답안지 오류를 공개했는가, `question-audit.md`의 합계가 합본·bank 전체와 맞는가. 변형 연습(partC)은 원문이 아니라고 표시했는가, 이번 범위 안인가, 정답이 하나이고 `variants.md`의 의도한 정답과 맞는가(직접 다시 판단), 원문 문장을 그대로 재사용하지 않았는가.
7. **표현**: 표 첫 열이 한 글자씩 줄바꿈되거나 빈 칸이 있는 표, 잘린 문장, 원문자.
8. **어려운 개념의 이해 공백과 과잉 설명**: `content-rules.md`의 선별 기준에 해당하는 토픽에서 필요한 상황·해결하는 문제·작동 원리가 연결되는가. 최초 유입 같은 시작 조건이나 숨은 조건 때문에 인과가 끊기지 않는가. 보충 사실의 배지·출처는 정확한가. 단순 정의·명칭·목록이나 이미 충분히 설명한 토픽에 불필요한 동기 문단을 붙이지 않았는가. 생물의 의도나 근거 없는 진화 목적론으로 설명하지 않았는가.

출력 형식(이것만):
```
## Critical
- [s2-checkpoint] 문제 → 고칠 내용
## Important
- [p3] …
## Minor
- …
```
각 항목은 토픽/카드 id로 시작한다. 없으면 "없음".
---
