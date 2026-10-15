# 2장 자료 보완 실행 기록 — 2026-10-15

상태: 노트 조건 보완·16문항 본문 연결 완료. q14 해설은 수정 초안을 조립했으나 두 팩의 최종 발행은 보류했다. 기존 발행 해설은 교체하지 않았다. 커밋·푸시 없음.

## 적용한 내용

- 0910 #s5-atp-synthase: H⁺ 회귀 차단의 결과에 전자전달에 의한 H⁺ 수송 유지 조건 명시.
- 웹과제/2장/note-feedback.md: q01–q16 판별 기준·근거·원문 쟁점·공식 답 미확인·개인 가설 구별.
- 0910/0915 .pack/note-feedback-audit.md: 각 8개, 소유 ID 합집합 16개·중복 0. 기존 설명 충분 여부를 실제 문장으로 기록.
- 0915 장 마감: 과거 웹과제 부재 기록을 보존하고 날짜를 붙여 현재 감사 경로 추가.
- 새 해설 RUN의 0915 p33: 포도당 유래 전자를 NAD⁺가 받는 방향으로 수정. 분석 D·C의 압축 표현 가능성·공식 답 미확인을 understand/solve/verify/pitfall/sum에 일관되게 공개. 원문·정답 모델은 보존.

## 완료한 검증

- bank --complete: 16문항, exit 0.
- 무변경 full 복원 비교: 두 팩 토픽·카드 article 바이트 동일, 위젯 코드 보존.
- 최종 노트 실제 토픽 변경: 0910의 지정 토픽 1개, 0915 토픽 내용 변경 0.
- 두 복습문제 HTML 바이트 동일. bank/raw/intake·풀이기록·인터렉티브 파일 보존.
- check_html·html2md --check, 해설 build/check 모두 통과.
- 53+40문항을 정답 비공개 별도 검산자가 다시 풀이. 표현 결함은 일반 단일정답과 구별하여 대조.
- 브라우저 1280×900/375×812, light/dark 총 372개 문항 표시 확인. 콘솔·누락 자원·외부 요청·문서 가로 넘침 0.
- 노트 위젯·풀이 선택·다시 풀기·새로고침 복원·새 탭 초기화·애매함 토글·JSON 내보내기·취소 확인. 사용자 기록은 건드리지 않고 새 브라우저 context 사용.
- 최종 발행 위치 기준 해설 내부 링크 143개 파일·anchor 존재 확인. 모바일 p33 요약·원문 C 실제 표시 확인.

## 확정된 발행 보류 사유

기존 다른 해설을 그대로 보존하는 계획 범위와 모든 항목의 내용 검토 통과 요구를 함께 적용하면 아래 기존 오류를 승인으로 덮을 수 없다. 전항목 원천 대조로 아래 내용 오류 5문항을 확정했다. source_visual은 93/93 통과, content는 88통과/5실패다.

| 대상 | 현재 표현의 문제 | 최소 후속 수정안 |
|---|---|---|
| 0910 p17 solve | 앞에서는 자발적 반응을 설명하지만 결론에서 “신체의 모든 화학반응”으로 제한을 제거 | 문항 표현의 결함을 공개하고 자발적 반응과 활성화 에너지 장벽을 구분하여 결론·검산·요약에 유지. 서술 답의 원문 자체는 보존. |
| 0910 p19 recall/start/sum 및 p43 start | NADH·FADH₂의 전자를 모두 복합체 I·III·IV를 거치는 흐름으로 묶음 | NADH는 I→CoQ→III→IV, FADH₂는 II→CoQ→III→IV로 유입 경로를 구분. 참고 교재 p41 그림2.13. 정답4 보존. |
| 0915 p6 verify | 원자 수가 맞는 식은 (1)뿐이라고 하지만, 역반응 (5)도 원자 수 보존 | 원자 수 검산과 반응 방향을 함께 써야 (1)을 고른다고 한정. 정답1 보존. |
| 0915 p32 verify | NADP⁺가 빛을 흡수/물을 분해한다는 가정에서 NADP⁺ 부재 때 산소 발생을 결론내어 논리 방향 역전 | 잘못된 반사실 조건문을 제거하고 광계2의 물 분해와 NADP⁺의 최종 전자수용을 경로로 대조. 정답D 보존. |
| 공통 문제설명 템플릿 1024px | 기본 상태에서 목차가 닫혀 검증 지침의 목차·문제 기본 동시 열림 조건 불충족 | 1024px 기본 목차 상태 규칙을 별도 승인 범위에서 검토·수정하고 템플릿 브라우저 회귀 검사. |

이 추가 수정은 현재 범위(다른 설명 조각·스킬 코드 보존)에 포함하지 않았다. q14 초안은 정본 발행물로 표시하지 않는다. 기계 검사와 일부 화면 통과는 전체 발행 승인을 뜻하지 않는다.

## 검토할 파일

- [14번 수정이 들어간 미발행 초안](/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/.superpowers/sdd/2026-10-15-bio-ch2-feedback-materials/explain/0915/review-0915-Cellular_Respiration_and_Photosynthesis/stage/9809f320b9f1444db7c1a95e674670bd/문제설명_0915_Cellular_Respiration_and_Photosynthesis.html)
- [16번 조건 보완 정리노트](/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/복습노트/0910/정리노트_0910_Cells_and_Cellular_Respiration.html)
- [16문항 입력 피드백](/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/웹과제/2장/note-feedback.md)
- [현재 계획과 단계 상태](/Users/hyunjun_macbook_pro/.codex/worktrees/bio-ch2-feedback/생명과학/docs/superpowers/plans/2026-10-15-bio-ch2-feedback-materials.md)

격리된 managed worktree에서 진행했으며 main checkout의 tracked 변경은 없다. WORK 백업·검토 기록은 미커밋 상태이므로 보존한다.

## 최종 판정·남은 범위

[최종 리뷰](final-review.md), [93문항 판정·읽은 원자료·해시](source-content-review.md), review-0910.json 및 review-0915.json을 보존한다. 두 팩의 source_visual pass, content fail, browser fail이며 0910 p17은 독립 검산의 자발적 반응 한정과 현재 완성 답의 모든 반응이 달라 disputed로 보수적으로 기록했다. q14 공식 답 부재 자체를 disputed로 처리하지 않았다. 기존 발행 해설과 그 자료는 전혀 덮지 않았다.

Minor 보류: 두 노트 목차 제목의 잘린 표시(full 조립 metadata 영향), 과거 variants의 보기4개 설계와 보존 카드 보기5개의 차이. 후자는 이번 회귀가 아니며 정답모델은 일치한다.

범위 판단: 기존 검사·원자료 대조로 검증하고 신규 프로덕션 코드/테스트는 추가하지 않았다. 지정한 다른 해설·스킬 보존 범위를 지킨 결과 q14를 현재 정본으로 발행하지 못하는 비용이 남는다. 공식 채점/개인 숙달은 미확인으로 유지하며 사용자 실제 브라우저 기록은 조사하지 않았다. 브라우저 372뷰는 메인 실행의 신규 검증이며 최종 리뷰어가 중복 실행한 것은 아니다.
