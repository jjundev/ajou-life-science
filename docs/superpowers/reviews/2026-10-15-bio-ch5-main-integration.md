# 5장 작업 main 통합 검증

2026-10-15. main e39d656 위에 codex/bio-ch5-feedback-skills의 5e353ba·5baa497을 병합한다. main의 1장 표현 전환 규칙과 5장 명칭·단위 규칙을 모두 유지했고, problem-selection 충돌은 두 문단을 합쳤다. PE port-provenance는 원본 고정 커밋/원본 해시를 유지하고 병합된 authoring·verification의 목적지 해시만 갱신했다.

전체 회귀 검사에서 발견한 1006·1008 안내문 생성 변형 수12→13을 manifest/HTML/MD에 동기화했다. 1008은 기본11·심화2로 맞췄다. 기존/새91카드의 원문·보기·정답·번호는 작업 브랜치와 바이트 단위로 동일하다.

워크트리 정리 뒤에도 검증 가능하도록 3팩의 문제설명은 main 경로에서 새로 추출·조립·검사·발행했다. 원 문항 객체와 모든 카드·설명 조각이 기존 검토 입력과 같고, 렌더된 설명 HTML/MD의 SHA256도 동일함을 확인했다. 참조 경로는 같은 내용 해시의 main 파일로 옮겼다. 실제 독립풀이/내용/시각 검토 증거는 그대로 보존하고, 현재 입력과의 동일성 검증을 evidence/integration-identity.json에 추가했다. 과거의 검토를 달라진 문항에 적용한 것이 아니다.

검증 결과: bio-review-pack196테스트·230하위검사, bio-webquiz-forecast45테스트, bio-problem-explain177테스트, bio-cheatsheet49테스트·3하위검사 통과. 합계467테스트·233하위검사. 처음 기본 Python에는 pytest가 없어 import 오류가 났고 기존 /tmp/bio-forecast-test-env의 pytest 런타임으로 각각 별도 프로세스에서 전체를 재실행했다. 3팩 check_html 및 현재 참조 해시 검증 통과, 5장 bank complete17문항 검증 통과. 생성기·화면 템플릿의 실행 코드는 변경하지 않았다. 커닝페이퍼4쪽·14구역은 브랜치에서 검증된 파일과 동일하다. git diff --check 통과.

main의 미추적 1장 계획·feedback 파일은 그대로 보존했다. 병합 대상과 겹치던 미추적 5장 계획/설계 2파일은 충돌 전에 외부로 옮겨 원문 해시를 확인했다(계획은 들어오는 커밋과 내용이 달랐고 설계는 같았다). 기존 실행 증거3,498파일도 외부 백업 후 전 파일 SHA256 일치를 확인했다. 이 작업 외 다른 워크트리는 정리하지 않는다.

외부 백업: /Users/hyunjun_macbook_pro/.codex/worktree-backups/bio-ch5-integration-20261015-193339
