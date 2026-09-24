# 리뷰어 지시문

6단계에서 두 리뷰어를 한 메시지에서 병렬로 띄운다. 블라인드 리뷰어는 `lite`에서도 띄우고, 일반 리뷰어는 `lite`면 생략한다.

## 블라인드 풀이 검사

먼저 메인 에이전트가 복습문제에서 문제·보기·그림만 뽑은 사본을 만든다(`REVIEW`는 조립된 복습문제 HTML 절대 경로).
```bash
REVIEW=… OUT="$RUN/work/blind-<range>.md" python3 - <<'EOF'
import html, os, re
src = open(os.environ["REVIEW"], encoding="utf-8").read()
base = os.path.dirname(os.environ["REVIEW"])
cards = re.findall(r'<article class="card" id="(p\d+)"[^>]*>\s*<h3>(.*?)</h3>\s*<div class="problem">(.*?)</div>\s*<details', src, re.S)
def text(h):
    h = re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', lambda m: f"\n[그림: {os.path.join(base, m.group(1))}]\n", h)
    h = re.sub(r"</(p|li|figure)>|<br\s*/?>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
with open(os.environ["OUT"], "w", encoding="utf-8") as f:
    for pid, title, body in cards:
        f.write(f"## {pid}. {html.unescape(re.sub(r'<[^>]+>', '', title))}\n\n{text(body)}\n\n")
print(len(cards), "문항")
EOF
```
출력 문항 수가 manifest 문제 수와 다르면 카드 마크업 순서를 고친 뒤 다시 만든다.

---
생명과학 복습팩의 블라인드 풀이 검사를 한다. 파일은 수정하지 않는다.

- 열 수 있는 파일은 **두 개뿐**이다: 정리노트 `<RUN>/repo/복습노트/<range>/<정리노트 html>`, 문항 사본 `<RUN>/work/blind-<range>.md`(그 안의 `[그림: …]` 경로 이미지도 볼 수 있다). 복습문제 HTML, manifest, 요약, 교과서, 인터넷, 다른 파일은 열지 않는다. 자기 배경지식으로 풀지 말고 정리노트에 쓰인 내용만 근거로 삼는다.
- 문항마다 답을 고르고, 근거가 된 정리노트 토픽 id와 문장을 적는다. 정리노트만으로 판단할 수 없는 보기가 있으면 "근거 없음"으로 적고 무엇이 빠졌는지 쓴다.

출력 형식(이것만):
```
| 문항 | 내 답 | 근거 토픽 | 빠진 사실 |
|---|---|---|---|
| p1 | (2) | s1-centromere | |
| p4 | 근거 없음 | — | 보기 (3)의 방추사 부착 위치가 노트에 없음 |
```
---

메인 에이전트는 리뷰어 답을 manifest `answer`와 비교한다. 다르거나 "근거 없음"인 문항은 `anchor` 토픽의 섹션 작성자에게 빠진 사실을 가르치도록 되돌린다. 카드 풀이를 바꿔서 맞추지 않는다. 고친 뒤 사본을 다시 만들어 그 문항만 다시 검사한다.

## 일반 리뷰 (lite에서는 생략)

---
생명과학 복습팩 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/복습노트/<range>/<정리노트 html>`, `<…/복습문제 html>`
- 근거: `<RUN>/summaries/stt-*.md`, `<RUN>/slides.txt`, `<RUN>/manifest.json`, `<RUN>/question-audit.md`, `<RUN>/key-check.md`, `<RUN>/work/exam/*.png`, 웹과제 bank
- 규칙: `<SKILL>/references/content-rules.md`, `card-rules.md`, `problem-selection.md`

확인할 것:
1. **사실 오류**: 정의, 성립 조건, 과정의 위치·입력·출력, "항상/보통" 같은 한정어가 요약·강의노트·교재와 맞는가.
2. **누락**: 요약의 핵심 내용·강조 발언·`⚠️ 혼동 지점`·미룬 설명 중 노트에 없는 것.
3. **범위**: "예고만/안 다룸" 내용이 본문에 설명되어 있는가. 보충 레이어에 출처가 있는가.
4. **분류 경계**: 쉬운 설명이 조건을 지우거나, 과정 참여를 계의 구성원으로 쓰거나, 판별 용어를 없앴는가.
5. **ELI5 품질**: 쉽게 말하면 레이어가 전문용어 없이 1~3문장인가, 그림이 개념을 실제로 보여 주는가.
6. **문항**: 문제·보기가 원문(PNG, bank)과 글자까지 같은가, 모든 보기에 진단이 있는가, 정답이 `key-check.md`와 맞는가(직접 다시 판단), 답안지 오류를 공개했는가, `question-audit.md`의 합계가 합본·bank 전체와 맞는가.
7. **표현**: 표 첫 열이 한 글자씩 줄바꿈되거나 빈 칸이 있는 표, 잘린 문장, 원문자.

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
