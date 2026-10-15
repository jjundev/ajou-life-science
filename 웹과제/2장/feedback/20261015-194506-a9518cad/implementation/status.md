# 2장 웹과제 자료 보완 — 최종 발행 완료

2026-10-15. 격리 worktree에서 검토한 변경을 사용자 요청에 따라 main에 반영했다. 원문 bank/raw/intake·카드/정답모델·사용자 풀이기록과 다른 작업은 보존했다. 아래에 main 통합 검증을 기록한다.

## 결과

- q14/p33: 포도당 유래 전자→NAD⁺ 방향 수정. 분석 D·C 표현 유보·공식 답 미확인을 본문/검산/요약에 유지.
- q16: ATP 합성효소 회귀 차단 결과에 전자전달 유지 조건 명시.
- 전체 16문항 피드백 입력 및 8+8개 본문 감사 연결.
- 추가 오류 5문항: 0910 p17 자발적 반응 조건(연결 노트 포함), p19/p43 FADH₂의 복합체 II 유입, 0915 p6 원자수와 반응 방향 구별, p32 검산 논리 수정.
- 공통 문제설명 템플릿: 1024px에서 목차·문제 기본 동시 열림. 저장된 사용자 설정과 모바일 동작 보존.

## 확인한 검증

- 전체 테스트 178/178, 실제 브라우저 회귀 RED→GREEN.
- 별도 정답 비공개 독립 검산 53+40문항, 원천/내용 검토 93/93.
- 1280×900/375×812 × light/dark 372문항 뷰 및 1024 기본 패널 재검증. 합성 브라우저 6조건·상호작용 검사 통과.
- 최종 증거 패키징 전후 HTML·그림·vendor·설명 조각 바이트 동일. 패키징 후 372뷰 재확인.
- 발행 경로의 1024px 실제 렌더 추가 확인. 현재 참조 SHA256 및 발행 artifact hashes 전부 일치.
- bank --complete 16문항·git diff --check 통과.

## 발행 파일

- 0910: [문제설명](/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0910/문제설명_0910_Cells_and_Cellular_Respiration.html) · [정리노트](/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0910/정리노트_0910_Cells_and_Cellular_Respiration.html)
- 0915: [문제설명](/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0915/문제설명_0915_Cellular_Respiration_and_Photosynthesis.html) · [정리노트](/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/복습노트/0915/정리노트_0915_Cellular_Respiration_and_Photosynthesis.html)

## 검토 기록

[최종 후속 리뷰](final-review-followup.md) · [93문항 판정과 원천 해시](source-content-followup.md). 최초 보류 상황은 [별도 역사 기록](initial-hold-status.md)으로 보존한다. 현재 네 검토는 두 발행 자료 폴더 validation.json에서 모두 pass이며 실제 reviewer/evidence·현재 해시에 결합되어 있다.

## 남은 경미한 항목

- full 조립에 따른 두 노트 목차 제목 일부 잘림. 앵커·본문 손실은 없으며 비차단 가독성 항목으로 남겼다.
- 과거 variants의 보기4개 메타데이터와 보존 카드 보기5개 차이. 정답·실제 보기 내용은 검토했으며 이번 회귀가 아니다.

## 판단과 범위

동일한 p17 오류가 연결 노트에도 있어 그 한 문장을 함께 고쳤다. 원문·정답 모델은 바꾸지 않고 인쇄 표현과 과학적 조건을 구별했다. 공식 웹과제 정답·출제자의 C 의도·개인 숙달은 미확인이다. 실제 사용자 브라우저 저장내용은 조사하지 않았고, 테스트용 context와 원파일 해시로 보존을 확인했다. 신규 프로덕션 코드는 템플릿 한 줄이며 실제 동작 회귀 테스트와 파생본 provenance 기록을 함께 갱신했다. 원본 source commit/hash는 그대로다. 복구를 위해 WORK 백업·실행 기록은 유지한다.


## main 통합 검증

main 기준으로 기존 rerender 어댑터를 실행해 입력·참조 경로와 manifest를 재결합했다. 문항·그림 payload 및 렌더링 HTML은 검토된 worktree와 바이트 동일하다. 내용·독립 검산의 유효한 입력 동일성을 어댑터가 확인했고, 원천 파일의 main 경로 해시를 대조했으며 화면은 실제 main 경로에서 새로 검증했다. 1280/1024/375 × light/dark 558문항 뷰, 테스트178개 통과. 두 팩의 네 게이트 및 발행 artifact/reference SHA256은 main 현재 파일에 일치한다. 1장 미추적 작업은 스테이징 범위에서 제외했다. 이번 커밋·푸시 결과는 Git 기록으로 확인한다.
