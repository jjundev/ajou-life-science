# 학습만화 v2 구현·실제 제작 검증

## 구현

- 필수 혼동/도달 이해, 비유 대응·한계, 설명형/대화형, 캐릭터 ID·외형·역할·말투·컷별 출연/대사 계약.
- 이미지 프롬프트에 해당 정보 반영. 대사·인물 변경 시 프롬프트/그림 재사용 및 검토 무효화.
- 발행 후 원본 관련 설명에 같은 탭·정확한 토픽 해시 링크 추가. dry-run, 관리 블록 멱등 갱신, 연결만 재실행.
- 원본 스냅샷 실제 바이트 지문과 관리 참조를 제외한 내용 지문을 구분. 참조는 근거로 추출하지 않으며 본문/도해 변경·손상된 관리 블록은 차단.
- 명시적 단일 페이지 샘플 범위와 파일명. 전체 제작을 임의 축소하지 않음.

## 테스트·독립 검토

- 새 요구의 실패를 먼저 확인: `/tmp/bio-comic-v2-red.log`.
- 최종 스킬 테스트: `python3 -m unittest discover -s .agents/skills/bio-review-comic/tests -v` — 30개 통과.
- 1440×900·375×812 각각 light/dark, 합성 래스터16개를 사용하는3페이지 UI 테스트 통과. 목차·이전/다음·키보드·요약·서랍·테마·정확한 해시·같은 탭 원본 왕복, 오류0·가로 넘침 없음.
- `quick_validate.py` 통과, `git diff --check` 통과.
- Python3.12 이전 f-string 문법으로도 모든 파이프라인 파일 AST 분석 통과(`/usr/bin/python3`). 실제 런타임 검증은3.14 환경이며3.10 인터프리터 실행은 별도 수행하지 않음.
- 별도 검토자 comic_v2_review가 버전 폴더 연결 실패·발행 이미지 누락·f-string 호환성·비유 보충 표시 누락을 재현. 회귀 검사와 구현으로 수정.
- 비유에서 실제 표시한 근거는 coverage에서 생략할 수 없고, 대응별 보충 배지를 표시.

## 실제 만화 제작

- 원본: `복습노트/1105/정리노트_1105_Origin_of_Life_and_Prokaryotes.html`의 `s3-structure`.
- 결과: `복습노트/1105/학습만화_1105_Origin_of_Life_and_Prokaryotes_샘플_s3-structure.html`.
- 학생＋안내자의6컷 대화. USB 정보와 컴퓨터의 복사 장치를 바이러스의 숙주 의존성에 대응. 마지막 컷에 비유의 한계.
- 내장 image_gen으로 실제6이미지 생성. 코드/도형/단색 테스트 래스터를 제작물로 사용하지 않음.
- 초기 스타일 초안의 불필요한 말풍선은 채택하지 않음.5컷의 세균 내부 큰 파란 덩어리가 핵으로 오인될 수 있어 내장 편집 도구로 제거하고 실제 수정 결과 확인.
- 실제6이미지, 원본 도해·본문·주의, 모든 대사/조건을 직접 검토. 독립 검토자도 같은 자료와6실제 그림을 대조하여 중대한 문제 없음으로 보고.
- 원본17토픽 중1개를 명시적으로 선택한 샘플.14학습 페이지는 범위 밖,2개는 예고·자료 안내. 차수 전체 제작 완료를 의미하지 않음.
- 실제 샘플의4종 브라우저 검사 통과. 각 이미지 디코딩, 대사 넘침, 요약·테마·목차·키보드, 원본→만화 해당 페이지→원본 링크/뒤로가기 확인. 콘솔 오류0.
- 새로 진입 직후 이미지 디코딩 전 캡처한 최초 화면은 사용하지 않고 디코딩 대기 후 다시 캡처하여 실제 그림이 표시된4화면을 직접 확인.
- 원본의 안내 블록을 제거하면 스냅샷과 바이트 단위 동일. 원래 RUN 및 발행 버전 폴더에서 연결 재실행 모두 changed:false.
- 근거/콘티/프롬프트/검토·최종 왕복 기록/실제 그림/화면은 결과와 같은 이름의 `.assets/자료_학습만화_…_샘플_s3-structure/versions/20261109T081728-5141b227/`에 보존.

## 기존 저장소 테스트 실패

`.venv-question-bank/bin/python -m unittest discover tests -v`: 121개 중5실패·1skip. 모두 기존 `tests/test_migrate_review_assets.py`의 `old_review_html()` 안 `html.count(NEW_COMMENT) == 1` 공통 fixture assertion에서 실패한다. 이번 변경 대상이 아니며 이전 구현 검증에서도 같은 실패가 기록되어 있다.

- `test_apply_layout_and_links`
- `test_dry_run_changes_nothing`
- `test_migrate_is_idempotent`
- `test_name_clash_stops`
- `test_review_install_error_moves_nothing`

전체 로그: `/tmp/bio-comic-v2-repository-tests.log`. 스킬 로그: `/tmp/bio-comic-v2-tests.log`, `/tmp/bio-comic-v2-browser.log`. 원본에 대한 충실성 검토와 학습 효과의 실사용 측정은 구분한다. 학생의 이해도 실험을 수행한 것은 아니다.
