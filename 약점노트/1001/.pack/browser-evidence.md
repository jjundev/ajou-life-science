# 약점팩 실제 브라우저 검토

검토자 root. browser-results.json과 extra-browser-results.json의 실제 결과. note12화면(표지 포함), review13화면을 1280×900/375×812 light/dark 네 조합에서 검사. 토픽 8개·요약·재확인·링크를 직접 렌더링해 확인. 각 카드12개에서 오답 두 해설·정답 한 해설, 재시도, Enter/Space, 같은 탭 새로고침 복원, 새 탭 초기화, unsure 토글·JSON 반영 확인. 마지막 화면에만 export 버튼, 실제 JSON 다운로드 파일에서 cards12/unsure 확인. 사용자의 풀이기록 폴더에는 쓰지 않음.

날짜1001 폴더 및 상위 약점노트 폴더를 선택한 mock에서 .assets/풀이기록으로 해석함. 취소와 관계없는 폴더는 저장하지 않고 각각 취소·위치 안내를 표시. 실제 OS 폴더 선택창의 사용자 조작은 테스트하지 않고 File System Access API 경계 mock으로 경로계산·쓰기 호출을 확인. 현재 팩은 v1이어서 별도 v2 폴더는 만들지 않음. print media와 비JS에서도 정적 풀이12개 보존. 테마 버튼과 이전/다음 동작 확인. 모든 화면 가로넘침0·깨진그림0·KaTeX오류0·pageerror0. CDN Pretendard/KaTeX는 기존 허용 계약이며 외부요청0 또는 오프라인 보장이라고 주장하지 않음.

직접 본 화면: 정리노트 PC light와 모바일 dark 전체 접촉판, 복습문제 PC light·모바일 dark 전체, 노트 하단 PC dark·모바일 light, 기존 p29/p30 그림. 노트 하단에 자료충돌·정정 경로·단위 경계가 남고 표·요약·링크가 읽힘. 그림의 H/L은 본문에 각각 15N/14N으로 정의. 전체 화면의 상하 내용을 확인해 숨겨진 경고 누락 없음.
