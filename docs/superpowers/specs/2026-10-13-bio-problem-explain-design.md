# bio-problem-explain 스킬과 복습팩 연동 설계

## Intent
자구알 `ds-problem-explain`(ajou-jagual 커밋 `d631a5a573a32c9406b139e319bc9c7c2d328098`)을 생명과학 저장소로 이식해 `bio-problem-explain` 스킬을 만든다. 기존 `복습노트/<range>/복습문제_<range>_<slug>.html`을 입력으로, 문항마다 일곱 구역(understand·recall·start·solve·verify·pitfall·retry)을 펼친 `문제설명_<range>_<slug>.html/.md`를 같은 날짜 폴더에 발행한다. `bio-review-pack`은 MD 변환 뒤(8b)와 보강 모드(A5b)에서 이 스킬을 호출하고, 이미 생성된 11개 팩도 같은 절차로 백필한다.
Classification: architectural — 새 스킬·실행기·산출물.

## Behavior when done
- `/bio-problem-explain [MMDD | MMDD-MMDD | all | HTML경로]`(인자 없음 = 최신) → `문제설명_*.html/.md`, `figures_문제설명_*/`, `자료_문제설명_*/`.
- `/bio-review-pack <range>`가 복습팩 뒤 문제설명까지 만든다. 실패 시 검증된 복습팩은 유지하고 "복습팩 생성됨 / 문제설명 보류"와 이유를 보고한다.
- `augment` 후 해당 팩의 문제설명을 전체 재생성한다.
- 독립 검산 미통과·자료 충돌(disputed)이면 해당 팩 발행을 보류한다.

## Not in this round
- bio-review-coach·video·cheatsheet 연동, 정리노트/복습문제에 링크 삽입, 일부 카드 증분 설명, 자동 커밋.

## Approach
A. ds-problem-explain을 vendor·assets·tests까지 복사·수정하고 `assets/port-provenance.json`에 원본 커밋·해시를 고정한다(자구알이 머신러닝기초에서 이식한 방식). 실측: 수정 없는 추출기가 11팩 중 10팩(360문항)을 `main` 소문항으로 추출했다.

## Implementation spec
- 새 `.agents/skills/bio-problem-explain/` + `.claude/skills/bio-problem-explain -> ../../.agents/skills/bio-problem-explain`.
- `mpe_render.py`: 제목 `생명과학 복습 {range} 문제설명`, 읽음 상태 키 `bio-problem-explain-{profile}-{range}-{slug}`.
- `mpe_source.subparts`: `ul/ol.choices`·`.options` 보기 목록은 소문항 판별에서 제외(0915 p17 보기 (5)의 "설명하"가 오탐). 명시적 `.part`/`(a)` 표지만 소문항.
- `mpe_source.resolve_sources`: `all` 대상 추가(모든 팩, 끝 날짜 내림차순).
- `references/authoring.md`(생명과학판): solve는 보기별 판정, verify는 다른 경로로 정답 재확인, ㄱㄴㄷ형은 진술별 판정, 부정형은 understand에 질문 방향 명시, C 코드 절 → "답안지·기출·웹과제 충돌 시 disputed".
- `references/verification.md`: independent = 카드 정답을 보지 않은 별도 에이전트가 정리노트·교과서·강의노트만으로 다시 풀어 일치 + `.pack/key-check.md` 대조.
- 참조 자료: `강의노트/N장*.pdf`, `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`, `23, 24 소스/N강 합본.pdf`, `웹과제/N장/questions.json`, 정리노트, `.pack/key-check.md`·`question-audit.md`; STT는 보조.
- 저작: 문항 10개당 에이전트 1명 병렬(opus, lite면 sonnet); 독립 검산은 별도 에이전트.
- 템플릿·KaTeX·Pretendard 바이트 고정.
- bio-review-pack: 0단계 형제 스킬 존재 확인, 8b 문제설명, A5b, 보고서 `문제설명:` 줄, 오류 표 행, 4단계 백업 대상에 `문제설명_<range>_`·`figures_문제설명_<range>_`·`자료_문제설명_<range>_`, `references/problem-explain.md` 신규.

## Decisions
| # | Decision | Answer |
|---|---|---|
| 0 | 접근 | A 복사·수정 + provenance |
| 1 | 입력 | 기존 복습문제 카드 |
| 2 | 소문항 | 보기 목록 제외, 기본 `main` |
| 3 | 일곱 구역 | 유지, solve=보기별 판정 |
| 4 | 독립 검산 | 정답 숨긴 별도 에이전트 재풀이 + key-check 대조 |
| 5 | 호출 위치 | 8단계 MD 뒤, 9단계 보고 앞 |
| 6 | 실패 | 복습팩 유지, 설명만 보류, 다른 팩 계속 |
| 7 | 템플릿 | 머신러닝기초 템플릿 바이트 고정 |
| 8 | 파일명 충돌 | 없음(다른 스킬 glob은 `복습문제_*`/`정리노트_*` 고정) |
| 9 | 링크 삽입 | 안 함 |
| N1 | augment 후 | 팩 전체 재생성 [confirmed] |
| N2 | 백필 | 11팩 전체, 최신(1008)→0901 [confirmed] |
| N3 | 대상 문항 | 전체(기출·웹과제·partC) [confirmed] |
