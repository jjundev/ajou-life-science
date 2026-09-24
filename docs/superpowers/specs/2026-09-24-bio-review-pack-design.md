# 생명과학 복습팩 스킬 (`bio-review-pack`) 설계

작성일: 2026-09-24 · 근거 대화: `/grill-yourself` 설계 + 확인 라운드

## 의도

생명과학 저장소의 두 스킬 `summary-note`(STT → `정리노트/MMDD.md`+`.html`+테스트)와
`study-note-eli5`(노트+퀴즈 → `정리노트/eli5/MMDD-eli5.html`)를 하나의 스킬
`bio-review-pack`으로 대체한다. 머신러닝기초 저장소의
`.claude/skills/ml-review-pack` 파이프라인(manifest 계약 → 섹션·카드 병렬 작성 →
조립 → 기계 검사 → 리뷰 → 브라우저 검증 → MD 변환 → 보고)을 옮기고, HTML
템플릿 두 개(`note-template.html`, `review-template.html`)는 CSS·JS를 바꾸지 않고
그대로 복사한다. `/bio-review-pack 0922`를 부르면 `복습노트/0922/`에 정리노트
HTML·MD, 복습문제 HTML·MD, `figures_0922/`가 생기고 자동 검사와 블라인드 풀이
검사를 통과하면 완료다.

분류: architectural — 기존 흐름 두 개를 걷어내고 다른 저장소의 파이프라인을 새
스킬로 옮긴다.

## 완성 후 동작

- `/bio-review-pack [MMDD|MMDD-MMDD] [lite]` 또는 "0922 정리해줘", "0922 강의 듣고
  왔어". 인자가 없으면 가장 최근 산출물(새 형식 `복습노트/*/정리노트_*`와 예전 형식
  `정리노트/MMDD.md` 모두) 다음 날짜의 STT 전부.
- 정리노트: ML과 같은 모양(토픽 1개 = 1화면, 쉽게 말하면/정확히 말하면/교수님 말씀/
  꼭 기억해요/보충 레이어, 오른쪽 페이지 요약 패널).
- 복습문제: 범위에 드는 웹과제·23·24 기출 객관식 **전부**. 카드마다 문제와 보기,
  원문 정보·힌트·풀이(정답, 보기별 진단, 답안지 오류 공개)는 접힘.
- 중간에 묻지 않고 마지막에 한 번 보고(문항 분류표 포함). 검사 2회 실패는 "미해결".
- 생명과학 저장소가 아니면 알리고 멈춘다.

## 이번에 안 하는 것

- 기존 `정리노트/0901~0917`·`eli5/`를 새 형식으로 다시 만들기.
- `ml-review-pack`을 두 과목 공용으로 일반화하기.
- 웹과제 bank의 scope 잠금·coverage JSON·ELI5 바인딩(bank는 읽기 전용 입력).
- KaTeX 제거.

## 접근

A안: `ml-review-pack`을 복사하고 과목 전용 부분(references, 문제 선별, 카드 규칙,
경로)만 다시 쓴다. 옛 스킬 두 개는 걷어낸다.

## 결정

| # | 결정 | 답 |
|---|---|---|
| 0 | 접근 | A |
| 1 | 위치·Codex | `.agents/skills/bio-review-pack/`이 정본, `.claude/skills/bio-review-pack/SKILL.md`는 진입점만. 서브에이전트가 없으면 같은 브리프로 차례대로 직접 작성 **[확정]** |
| 2 | 이름 | `bio-review-pack` |
| 3 | 산출물 위치 | `복습노트/<range>/` |
| 4 | 기본 range | 새 팩과 옛 `정리노트/MMDD.md` 모두 본 뒤 다음 날짜부터 |
| 5 | 정리 범위 | 옛 스킬 두 개와 그 전용 테스트 삭제, `scripts/question_bank`(ELI5 어댑터 `guide.py` 제외)·`new_note_test.py`·`test_note_*` 유지 **[확정]** |
| 6 | 문항 수 | 범위 안의 기출·웹과제 전부 **[확정]** |
| 7 | 템플릿 | CSS·JS 그대로. 객관식은 기존 `.problem`, `ol.steps`, `.answer`, `details` 클래스로 표현 |
| 8 | manifest 스키마 | 그대로(`variant: false`, `answer`는 보기 기호) |
| 9 | slug | 영문(`SLUG_RE`) |
| 10 | 과목명 | `assemble.py` `PAGE_TITLE`에 manifest `course` |
| 11 | 웹 bank | 읽기 전용, validate 실패는 보고만 |
| 12 | 승인 게이트 | 없음 **[확정]** |
| 13 | 답안지 오류 | 판단한 답을 정답으로, 풀이에 공개 |
| 14 | 블라인드 풀이 검사 | 6단계, `lite`에서도 실행 |
| 15 | 옛 규칙 흡수 | ⚠️→warn, 💡→prof, 📎→supp(+출처), ✂️→`s<N>-next`, ⏪→`s0-recap`, ⏱→cheatsheet |

## 스크립트 변경 (ML 대비)

- `assemble.py`: `PAGE_TITLE`에 `m['course']`; `RUN/figures/*`를 `figures_<range>/`로 복사.
- `check_html.py`: 보충 배지 `보충 · 수업에서 다루지 않았어요`; 로컬 `<img src>`가 없으면 `broken-image`.
- `html2md.py`: `<img>`를 `![alt](src)`로 옮김(그림 문항이 MD에서 사라지지 않게).
