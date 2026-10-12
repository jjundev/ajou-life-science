---
name: ds-problem-explain
description: 자구알의 기존 복습문제 HTML로 문제 단서, 떠올릴 개념과 공식, 첫 줄, 단계별 이유, 완성 답과 검산을 펼친 문제설명 HTML·MD를 만든다. 문제해설, 입문 풀이 설명 또는 /ds-problem-explain [날짜|기간|HTML경로]에 사용한다. 복습팩 생성과 과제·실습 PDF 추출에는 사용하지 않는다.
---

# 자구알 문제풀이 입문 설명

이론을 읽었지만 풀이 경험이 부족한 학생에게 문제의 단서 → 개념·공식 → 실제 첫 줄 → 단계별 이유 → 완성 답 → 검산을 보여 준다. 기존 복습문제 HTML을 입력으로 사용하며 머신러닝기초 문제설명 템플릿과 로컬 KaTeX/Pretendard를 그대로 사용한다.

## 대상과 보존

- `0917`: 해당 날짜. `0914-0917`: 양끝을 포함한 기간의 팩을 각각 처리한다.
- 저장소 내부 HTML 경로: 해당 복습문제 파일을 명시한다.
- 인자 없음: 파일명 날짜 기준 최신 복습문제 팩.

여러 slug 또는 통합/개별 팩이 겹치면 후보를 보여 주고 경로를 명시하게 한다. 최신 또는 명시한 팩이 0문항이면 **문항 없음**과 비어 있지 않은 후보를 안내하고 중단한다. 이전 날짜로 자동 이동하지 않는다. 과제·실습 PDF와 과제 카드는 이번 스킬의 입력이 아니다. 새로운 문제를 출제하지 않는다.

원 HTML·MD·PDF·그림·은행·정리노트를 수정하지 않는다. `.problem` 전체의 코드·수치·연산 순서와 기출 원문을 보존한다. 참고 풀이·답은 독립 검산을 대신하지 않는다. 질문 소문항과 연산 목록을 구별하며, 질문 경계가 모호하면 추출을 보류한다. 소문항을 임의로 합치지 않는다.

## 실행

저장소 루트에서 Python 3.10 이상을 사용한다. 실행기는 표준 라이브러리만 필요하다. 설치만으로 실제 수업 산출물을 만들지 않는다.

1. 고유 RUN을 정하고 추출한다.

   ```sh
   python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py extract --repo . --target 0917 --run tmp/ds-problem-explain/0917-first
   ```

2. 대상 디렉터리의 `source.json`을 읽는다. 문항 ID·전체 문제·소문항·원문·그림·참고 풀이를 확인한다. 원 기출/문제은행(`from_the_past/기출/문제은행.json`), 강의록(`자료구조_강의록_2026/`), 관련 정리노트를 필요한 범위에서 실제로 읽고 원 페이지와 대조한다. STT는 필요한 경우 보조로 사용한다. 수업 밖 보충은 표시한다. `source.json`을 수동 수정하면 재추출 검사가 거부한다.
3. [저작 규칙](references/authoring.md)을 읽고 `explanations/pN.html`을 작성한다. 일곱 직계 구역 `understand → recall → start → solve → verify → pitfall → retry`, 모든 소문항의 solve/verify 표지, 펼친 답과 우측 요약이 필요하다. recall은 문제의 어떤 단서에서 개념을 떠올렸는지, 정의·규칙·기호·조건·선택 이유를 연결한다. CLI는 설명을 자동 저작하지 않는다.
4. 독립 추적·시뮬레이션·컴파일 실행·논증으로 답을 확인하고 `evidence/`에 근거를 보관한다. C는 정의된 동작과 입력 가정을 먼저 확인한다. 원문 오타·UB·비종료·은행 충돌은 몰래 수정하거나 정상 답으로 승인하지 않고 disputed로 남긴다.
5. 조립과 기계 검사를 실행한다. build는 새 stage를 만들고 검토 상태를 모두 `not_run`으로 초기화한다.

   ```sh
   python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py build --run tmp/ds-problem-explain/0917-first
   python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py check --run tmp/ds-problem-explain/0917-first
   ```

6. [검토 기록](references/verification.md)을 읽고 실제 source_visual/content/independent/browser 결과를 `review.json`에 기록한다. 사용한 참조 파일의 절대 path와 SHA-256을 references에 기록한다. 구조 통과를 정답 검증으로 기록하지 않는다. 로컬 브라우저에서 1280×900/375×812, light/dark의 모든 문항·목차·이전/다음·요약·수식·그림·코드·상태 표를 확인한다. 콘솔·KaTeX 오류·누락 자원·외부 요청·문서 가로 넘침은 0이어야 한다. 코드 블록 내부 스크롤은 허용한다. stage의 원 문제/개념 링크는 최종 발행 디렉터리 기준이므로 실제 원 파일과 anchor도 대조한다. 템플릿 결함은 근거를 보고하며 임의로 템플릿을 수정하지 않는다.
7. 실제 검토가 모두 pass이고 현재 해시가 일치하면 사용자 호출 범위에서 추가 확인 없이 발행한다. 미검토·변경·실패·disputed는 해당 팩의 발행을 막는다.

   ```sh
   python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py publish --run tmp/ds-problem-explain/0917-first
   ```

설명 소유 파일만 백업·교체하며 실패하면 복구한다. 다중 파일 교체는 OS 원자적 transaction이 아니다. 팩별 성공·보류 이유, HTML·MD와 백업 경로를 보고한다. 유용하면 HTML을 Codex 패널로 연다. 커밋·푸시는 별도 사용자 요청이 있을 때만 수행한다.

## 산출 위치

입력과 같은 날짜 폴더에 `문제설명_<range>_<slug>.html/.md`, `figures_문제설명_<range>_<slug>/`, `자료_문제설명_<range>_<slug>/`를 저장한다. 자료 폴더에는 생성 기록·검토·설명 조각·검산·로컬 자원이 들어간다. 정리노트 링크를 자동 삽입하지 않는다. 읽음 상태 범위는 `ds-problem-explain-review-<range>-<slug>`다.

원본 고정 커밋과 바이트 해시는 [이식 기록](assets/port-provenance.json)에 있다. 실행 중 머신러닝기초 checkout이나 ds-review-pack을 참조하지 않는다.
