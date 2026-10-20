# 최종 코드 재검토 — 2026-10-20

프로젝트 read-only 재검토. 이전 code-review.md의 P2 목차 앵커 문제는 수정되었다.

## 수정 검증

- mpe_contract.note_link_contract가 알려진 top/toc/contents/main/summary/questions/problems, panel-/tab-/tabpanel-, -links/-cheatsheet/-next 앵커를 필수 개념 링크로 세지 않도록 변경됨을 확인했다.
- 이전의 임시 `<nav id="panel-left-title">목차</nav>` 재현을 동일하게 실행했고 이번에는 build_explanation에서 명시적인 개념 앵커 누락 오류로 차단되었다.
- validate_fragment는 build·CLI check·publish 공통으로 호출되므로 알려진 탐색 앵커 검사는 세 경로에 적용된다. publish의 omission 별도 승인 게이트는 유지된다.
- 신규 7개 탐색 앵커 테스트와 기존 링크/명시생략/승인 테스트를 읽었다. `uv run --with pytest python -m pytest .agents/skills/bio-problem-explain/tests/test_note_links.py .agents/skills/bio-problem-explain/tests/test_contract.py -q`를 실제 실행하여 **56 passed in 0.28s** 확인했다.

## 범위와 지침의 정합성

현재 검사는 알려진 템플릿 UI/안내 앵커를 걸러내는 구조 검사이다. 모든 가능한 앵커 이름이나 관련 없는 실제 학습 절까지 자동 분류하는 검사는 아니다. authoring.md:81과 verification.md:3은 기계 검사의 형식·자원 검사와 content의 의미 판단 책임을 명확히 구분한다. authoring의 recall 예시는 실제 파일·앵커로 교체하라는 안내를 포함한다. 이 범위에서 지침과 구현은 일치하며 무한한 이름 패턴의 완전성을 주장하지 않는다.

## 결론

앞선 P2 발견 해결 확인. 현재 변경에서 추가 조치가 필요한 발견 없음. 이 재검토에서는 전체 suite·브라우저 검사를 실행하지 않았다. 실제 저작/별도 검토자의 판단을 대신하거나 모델 압박 테스트를 수행했다고 주장하지 않는다.
