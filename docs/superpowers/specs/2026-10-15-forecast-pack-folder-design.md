# 웹과제예상 장 폴더의 부속 파일을 `.pack/`으로 모으기

## Intent
`웹과제예상/<N>장/` 맨 위에는 열어 볼 HTML(`복습문제_<N>장_웹과제예상_v<K>.html`, `문제해설_<N>장_웹과제예상_v<K>.html`)과 숨김 폴더 `.pack/`만 둔다. 나머지(`src/v<K>/`, `문제해설_….md`, `figures_문제해설_…/`, `자료_문제해설_…/`)는 모두 `.pack/` 안으로 옮긴다. 이 폴더를 쓰는 두 스킬(bio-webquiz-forecast, bio-problem-explain forecast 프로필)이 새 위치를 쓰고, 기존 4장(v1–v4)·5장(v1–v2)을 이전해 깨진 상대 링크 0개·두 스킬 테스트 통과면 완료다. 복습노트 `.assets` 이전(`2026-10-13-review-assets-folder-design.md`)과 같은 방식이다.
Classification: bounded — 생성 흐름은 그대로이고 경로만 바뀐다. 경로 규칙(`assets_path.py`)과 이전 스크립트 선례(`scripts/migrate_review_assets.py`)가 이미 있다.

## Behavior when done
- 탐색기에서 `웹과제예상/5장/`을 열면 HTML 4개만 보인다(`.pack/`은 숨김).
- 문제해설 HTML의 KaTeX·Pretendard·그림이 `.pack/자료_…/vendor`, `.pack/figures_…/`로 그대로 뜬다.
- `.pack/문제해설_….md`의 그림 링크와 `../../../복습노트/…` 링크가 열린다.
- `/bio-webquiz-forecast 5`는 `.pack/v3/`를 만들고, `복습문제_5장_웹과제예상_v3.html`은 장 폴더 맨 위에 생긴다. 해설 부속 파일도 `.pack/`에 생긴다.
- `--init`의 다음 버전 계산은 `.pack/v*`를 본다. 그림·자료 폴더가 섞여 있어도 번호가 틀어지지 않는다.

## Not in this round
- `웹과제예상/커닝페이퍼/` — 요청 경로(`N장/`) 밖.
- `복습노트/` `.assets` — 이미 끝남.
- homework 프로필 출력 — 다른 폴더.
- `mpe_cli.py rerender`가 `.pack/` 접두어를 무시하게 하는 일 — rerender는 review 전용 흐름이다.
- `docs/superpowers/*` 과거 문서 — 역사 기록.

## Implementation spec
- 경로 규칙(`bio-review-pack/scripts/assets_path.py`, problem-explain vendor 사본): 상수 `PACK = ".pack"`을 추가한다. `moves`·`relocate`·`rebase_md`·`migrate_md`에 `side: str = SIDE` 인자를 추가한다. 기본값이 그대로라 review 동작은 바뀌지 않는다. vendor 해시(`assets/port-provenance.json`)를 갱신한다.
- bio-webquiz-forecast: `build.py`에 상수 `PACK`을 둔다. `load_pack`은 `src.parent.name == PACK`을 검사하고, `next_version`·`init_version`은 `<장>/.pack/v<K>`를 쓴다. 출력은 그대로 `src.parents[1]`이다. `check.py`는 `.pack/v<K>`를 읽는다. SKILL.md·references의 `src/v<K>`를 `.pack/v<K>`로 바꾼다.
- bio-problem-explain forecast: `names()`는 `.pack/figures_…`, `.pack/자료_…`를 돌려준다. `build_explanation`과 `check_artifacts`의 review 분기를 프로필→부속 폴더 표(`review: .assets`, `forecast: .pack`)로 일반화한다. MD는 `.pack/`에 쓰고 `rebase_md(…, PACK)`를 한 번 적용한다. `mpe_forecast.py`는 `.pack/v<K>`에서 pack.json·blueprint.md를 읽는다. SKILL.md 43·62·98행을 고친다.
- 이전 스크립트 `scripts/migrate_forecast_pack.py`: 기본 dry-run, 여러 번 돌려도 결과가 같다. `src/v<K>`는 `.pack/v<K>`로, 그 밖의 비 HTML 항목은 `.pack/<이름>`으로 옮긴다. 루트 HTML의 상대 `src`/`href`에 `relocate(…, PACK)`를, 옮긴 MD에 `migrate_md(…, PACK)`를 적용한다. `자료_…/manifest.json`·`validation.json`에서는 `src\v<K>` 경로를 `.pack\v<K>`로 바꾸고, `files`·`artifact_hashes` 키를 옮기고, 바뀐 파일의 해시를 다시 계산한다. 파일은 바이트 그대로 읽고 써서 CRLF를 지킨다. `--check`는 깨진 링크와 루트에 남은 항목을 센다.
- 숨김 폴더 주의: ripgrep(Glob/Grep)과 Python `glob('*')`은 dot 폴더를 건너뛴다. 문서와 코드에는 `.pack`을 글자 그대로 쓴 경로만 적는다.

## Decisions
### Confident
| # | Decision | Answer | Rationale |
|---|---|---|---|
| 1 | 예전 위치(`src/`)도 읽을지 | 아니오, 한 번에 전부 이전 | `.assets` 결정 #1과 같음 |
| 2 | 버전 소스 위치 | `.pack/v<K>/` (`src` 단계 제거) | `.pack` 자체가 소스 폴더. `build.py:36` 검사 한 줄 |
| 3 | 해설 부속 파일 배치 | `.pack/` 바로 아래, 이름 그대로 | review의 `names()` 접두어 방식(`mpe_render.py:25`) |
| 4 | 경로 규칙 코드 | `assets_path.py`에 `side` 인자 + vendor 사본 | 순수 함수 재사용(`mpe_shared.py:10`) |
| 5 | 기존 MD | 재생성 없이 `migrate_md`로 링크만 수정 | `.assets` 결정 #6과 같음 |
| 6 | 해설 manifest·validation | 경로·키·해시를 다시 씀 | 절대 경로 `src\v<K>`와 HTML·MD 해시가 들어 있음 |
| 7 | `--init` 번호 계산 | `VERSION_RE.fullmatch` 유지(`build.py:73`, `check.py:48`)하고 테스트로 고정 | `.pack/`에 figures·자료 폴더가 섞임 |
| 8 | 커닝페이퍼 | 범위 밖 | 요청 경로 |

### Confirmed by default
| # | Decision | Answer |
|---|---|---|
| A | 숨김 폴더 구성 | `.pack/` 하나(버전 소스와 해설 부속 파일 모두) |
