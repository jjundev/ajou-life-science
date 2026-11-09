# 생명과학 학습만화 스킬 검증 — 2026-11-09

## 변경 범위

`bio-review-comic` 스킬, Python 표준 라이브러리 기반 제작 도구, 기존 정리노트에서 파생한 템플릿/CSS, 테스트, Claude 검색용 심볼릭 링크를 추가했다. 기존 정리노트·다른 스킬·문제은행 소스는 수정하지 않았다. 작업 브랜치는 `codex/bio-review-comic`; 커밋·푸시는 수행하지 않았다.

## 통과한 검증

- `python3 /Users/hyunjun_macbook_pro/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/bio-review-comic`: Skill is valid.
- `python3 -m unittest discover -s .agents/skills/bio-review-comic/tests -v`: **16 tests, OK**. 추출/순서/범위, NFC/NFD, 근거 coverage, 원본 변경, 그림 재사용 지문, 검토 무효화, 보류, 발행 조건, 이전 버전의 유효 링크, 저장 실패 후 그림 보존과 인덱스 복구를 확인했다.
- `.venv-question-bank/bin/python .agents/skills/bio-review-comic/tests/browser_check.py --output tmp/bio-review-comic/browser-check`: **4종 화면 passed**, 페이지 오류 0. 1440×900과 375×812의 light/dark에서 3개 테스트 페이지(8컷 포함), 래스터 16개 로드, 긴 대사, 가로 넘침, 목차/키보드/페이지 이동, 요약, 서랍, 테마 유지, 원본 링크와 뒤로가기, 읽음 키 분리를 확인했다. 화면 캡처도 직접 확인했다.
- 실제 1105 HTML 추출: **17개 토픽, 15개 포함**, `s4-next`와 `s4-links` 제외. 콘티/그림 생성은 실행하지 않았다.
- 기존 정리노트 **17개 전체**에 추출기를 실행: **245개 포함 토픽**을 오류 없이 추출했다. 학습 내용의 의미 검토나 해당 245페이지의 만화 제작을 수행했다는 뜻은 아니다.
- Impeccable 변경 템플릿/CSS 기계 검사: `[]` (지적 없음). 원본 디자인 시스템을 그대로 상속했다.
- `git diff --check`: 통과.

브라우저의 이미지는 자동화 검사용 단색 PNG다. 실제 학습만화 일러스트 생성/생물학적 그림 검토를 수행한 결과로 보고하지 않는다. 실제 스킬 실행은 내장 이미지 도구로 생성한 모든 그림의 검토가 필요하다.

## 독립 적용·검토

스킬 없이 동일한 요청을 해석한 기준 실행은 실제 15페이지를 찾았지만, 요청에 없던 복기 질문/정답 토글과 표지 제거를 제안했다. 완성된 스킬을 받은 별도 적용 실행은 실제 CLI 추출을 수행하고, 원본 15페이지·보충/불확실성 보존·부분 완료·검토·원본 불변 조건에 맞는 절차를 도출했다.

독립 코드 검토에서 발견한 문제는 회귀 테스트의 실패를 확인한 뒤 수정했다.

1. 전 페이지 보류 결과의 발행 차단.
2. 더 깊은 버전 폴더로 옮긴 `previous.html`의 상대 그림/원본 링크 재기준화.
3. HTML 교체 후 메타데이터 저장 실패 시 이미 참조된 그림 버전 보존.
4. 같은 결과 재시도 시 `latest.json` 복구와 기존 버전 재사용.

## 기존 저장소 테스트의 실패

README에 기재된 저장소 명령을 기존 가상환경으로 실행했다.

`.venv-question-bank/bin/python -m unittest discover tests -v`

결과: **121 tests, failures=5, skipped=1**. 아래 5개는 모두 변경하지 않은 `tests/test_migrate_review_assets.py`의 `old_review_html()` 사전조건 `html.count(NEW_COMMENT) == 1`에서 실패한다. 현재 상호작용 스크립트와 옛 주석을 기대하는 테스트 픽스처의 불일치다.

- `test_apply_layout_and_links`
- `test_dry_run_changes_nothing`
- `test_migrate_is_idempotent`
- `test_name_clash_stops`
- `test_review_install_error_moves_nothing`

일반 `pytest -q`도 별도로 시도했으나 기존 `tests/test_question_bank_model.py`의 `question_bank_fixture` import 오류로 수집 중단됐다. 이번 스킬은 위 모듈이나 기존 테스트 설정을 수정하지 않는다.

세부 실행 로그와 스크린샷은 저장소의 무시된 `tmp/bio-review-comic/` 및 실행 중 `/tmp/bio-comic-*.log`에 있다. 장기 검증 기록은 이 문서다.
