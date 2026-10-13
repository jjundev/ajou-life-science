# 복습노트 날짜 폴더의 부속 파일을 `.assets/`로 모으기

## Intent
`복습노트/<range>/` 맨 위에는 `.pack/`과 열어 볼 HTML(정리노트·복습문제·문제설명·인터렉티브)만 둔다. 나머지(`.md`, `figures_*`, `자료_*`, `풀이기록/`, `장마감_*.md`)는 모두 숨김 폴더 `.assets/` 하나로 옮긴다. 이 폴더를 쓰거나 읽는 모든 스킬이 새 위치를 쓰고, 기존 12개 날짜 폴더(0901–1013)를 이전해 깨진 상대 링크가 0개면 완료다.
Classification: bounded — 기존 생성·읽기 흐름의 경로만 바뀐다.

## Behavior when done
- Finder에서 `복습노트/1001/`을 열면 HTML만 보인다(`.pack/`, `.assets/`는 숨김).
- HTML의 그림·문제설명 vendor(KaTeX, Pretendard)는 `.assets/…` 경로로 그대로 뜬다.
- 복습문제의 풀이기록 내보내기는 `<range>/.assets/풀이기록/`에 저장된다. 날짜 폴더·`복습노트`·`.assets`·`풀이기록` 중 무엇을 골라도 같은 곳에 저장된다.
- `.assets/` 안의 MD에서 형제 MD, `../<html>`, `../../<다른 날짜>/…`, `figures_…/` 링크가 모두 열린다.
- cheatsheet·preview-note·webquiz-forecast·review-coach·stt·interactive·review-video가 새 위치에서 정리노트 MD·장마감·풀이기록을 찾는다.

## Not in this round
- `예습노트/` — 요청 범위 밖. html2md 공용 함수(`Ctx`, `convert`) 기본 동작은 바꾸지 않는다.
- 웹과제예상 forecast·homework 프로필 출력(bio-problem-explain) — 다른 폴더.
- 하위 이름 변경(`.assets/자료_인터렉티브_…` 그대로) — 결정 B.
- `docs/superpowers/*` 과거 문서, `복습영상/*/selection.json` 옛 경로 — 역사 기록.
- `.DS_Store` — gitignore 대상.

## Implementation spec
- 이름 규칙: 부속 폴더는 고정 이름 `.assets`. 하위 이름은 지금과 같다. 각 스킬은 상수 `.assets` 하나로 처리한다.
- 경로 변환 순수 함수(`bio-review-pack/scripts/assets_path.py`, bio-problem-explain에 vendor 복사):
  - `relocate(url, moved)`: 날짜 폴더 기준 상대 URL의 첫 조각이 옮긴 이름이면 `.assets/`를 붙인다.
  - `rebase_md(text)`: 날짜 폴더 기준으로 쓰인 MD 링크를 `.assets/` 기준으로 바꾼다(`.assets/x` → `x`, 그 밖의 상대 경로 → `../x`).
  - 생성기는 MD를 "날짜 폴더 기준"으로 만든 뒤 `rebase_md`로 한 번 바꾼다. 이전 스크립트는 기존 MD에 `relocate` 후 `rebase_md`를 적용한다.
- bio-review-pack: 카드 그림 `src`는 `.assets/figures_<range>/pN.png`. 조립기는 그림을 `.assets/figures_<range>/`로 복사. `convert_pack`은 MD와 SVG를 `.assets/`에 쓴다. `collect_solves.py`와 `review-interaction.js`의 `resolveExportDir`는 `.assets/풀이기록`을 쓴다. SKILL.md의 산출물·glob·백업·장마감 경로를 고친다.
- bio-problem-explain(review 프로필만): `figures_문제설명_…`, `자료_문제설명_…`, MD를 `.assets/` 아래에 둔다. HTML의 VENDOR는 `.assets/자료_문제설명_…/vendor`.
- bio-interactive: `자료_인터렉티브_NN_…`는 `.assets/` 아래. 정리노트 MD는 `.assets/`에서 읽는다. 번호는 루트 HTML과 `.assets/` 폴더를 함께 본다.
- 읽는 쪽: SKILL.md·references의 경로 문자열, `bio-stt/scripts/infer_context.py`의 장마감 탐색.
- 숨김 폴더 주의: Claude Code Glob/Grep(ripgrep)은 숨김 폴더를 기본으로 건너뛴다. 문서에는 `.assets`를 글자 그대로 쓴 경로만 적는다. Python `glob.glob('*')`도 dot 항목을 건너뛰므로 `.assets`를 명시한다.
- 이전 스크립트 `scripts/migrate_review_assets.py`: `--dry-run` 기본, 여러 번 돌려도 같은 결과. `git mv`로 옮기고, HTML의 상대 `src`/`href`와 인터렉티브 생성 주석을 `relocate`하고, 복습문제 HTML에 박힌 `resolveExportDir` 블록을 asset 본문으로 바꾸고, MD는 다시 만들지 않고 `rebase_md(relocate(...))`로 링크만 고친다. `--check`는 깨진 상대 링크를 센다.

## Decisions
### Confident
| # | Decision | Answer | Rationale |
|---|---|---|---|
| 1 | 예전 위치도 읽을지 | 아니오, 한 번에 전부 이전 | 이중 경로가 쓸모없음 |
| 2 | `.pack/` 위치 | 루트 그대로 | 요청; `augment.py:139`, `assemble.py:147` 무변경 |
| 3 | 풀이기록·장마감 | `.assets/`로 | 요청("나머지 전부") |
| 4 | 경로 규칙 위치 | 스킬마다 상수 + review-pack의 순수 함수 모듈(problem-explain은 vendor 복사) | 스킬 자급 구조, vendor 선례(`mpe_shared.py:5`) |
| 5 | MD 링크 | 날짜 폴더 기준으로 만든 뒤 `rebase_md` | `html2md.py:168 fix_href`는 형제 링크만 다룸 |
| 6 | 기존 MD | 재생성하지 않고 링크만 수정 | 손본 MD 보존(`bio-review-pack/SKILL.md:178`) |
| 7 | 기존 복습문제 HTML의 JS | `resolveExportDir` 블록만 교체 | 12개 HTML 모두 같은 689자 블록 인라인 |
| 8 | forecast·예습노트 | 범위 밖 | 요청 범위 |
| 9 | bio-review-video | 코드 무변경 | `lib/sources.py:58` `rglob` |
| 10 | 숨김 폴더 탐색 | 문서에 `.assets` 명시 경로만 | ripgrep이 숨김 폴더를 건너뜀 |

### Confirmed by user
| # | Decision | Answer |
|---|---|---|
| A | 부속 폴더 이름 | `.assets` (".(영어)" 형식 요청, 단어는 Claude 선택) |
| B | 하위 이름 | 그대로 |
