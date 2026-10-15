# 5장 커닝페이퍼 재생성 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습팩 검토가 완료된 뒤 실제 5장 웹과제와 명칭·판별 기준을 반영한 커닝페이퍼 HTML·PDF를 만든다.

**Architecture:** 기존 bio-cheatsheet full 생성 흐름으로 별도 RUN/out 후보를 만든다. 새 자료와 실제 원자료를 연결하고 자동 검사·전체 PDF 시각 검사·별도 사실 리뷰를 수행한다. refresh는 사용하지 않는다.

**Tech Stack:** 기존 spec.json·구역 HTML·build/check/stale Python CLI, Chrome PDF, PDF 쪽 렌더링.

**Spec:** `docs/superpowers/specs/2026-10-15-bio-ch5-existing-materials-design.md`.

## Global Constraints

- 선행 계획 `2026-10-15-bio-ch5-review-pack-backfill.md`의 최종 상태 READY가 필요하다. NOT_READY면 시트를 만들지 않는다.
- Native 방식 유지. 생산 코드·스킬·템플릿·spec 스키마는 변경하지 않는다.
- 기본 산출물 4개만 대상이며 웹과제당일 등 응시 기록은 보존한다. 원문/예상 v1~v4/풀이기록도 보존한다.
- ① 시험장 체크·② 용어 바꿔 부르기가 맨 앞, 구역 10~16개, ③부터 함정 1~3개와 출처, 고정 쪽 수 없음.
- 선택 표시는 공식 답이 아니다. 개인 가설·확정 취약점·확인하지 않은 시간 제한을 시트 사실로 쓰지 않는다.
- 찾기-점검은 기출 정확히 5행, 서로 다른 구역, 부정형·그림 각각 하나 이상. 시간 칸은 학생이 측정하므로 채우지 않는다.
- 커밋·main 병합·push·워크트리 정리는 별도 지시가 없으면 수행하지 않는다. 이후 이 순차 계획 구현을 지시하면 검증된 기본 시트 교체도 포함되므로 중복 승인을 묻지 않는다. 후보만 요청한 경우에는 RUN/out에 남긴다.

## Review Focus

1. 설명 갱신이 실패한 팩을 원천으로 쓰는 경우: READY 검사로 시작 전 차단(Task 1).
2. ②를 바꾸면서 refresh로 실행하는 경우: full 생성만 사용(Task 1).
3. 본문 밖 범위·가설·불명확한 시험 시간을 사실로 쓰는 경우: 문장별 원자료 대조(Task 1·2).
4. 자동 검사 통과하지만 작은 글자·표/화살표 겹침·빈 쪽 발생: 모든 PDF 쪽 렌더링 확인(Task 2).
5. 기존 찾기-점검에 사용자 측정값이 있는 경우: 원본 보존, 후보와 별도 대조(Task 2).

## File Structure / Interfaces

- 입력: 선행 검토 보고서, 현재 1001·1006·1008 노트/문제 MD, 장마감, 실제 bank/피드백·강의노트·교재·panic-patterns.
- 생성 후보: 고유 RUN의 `sources/manifest.md`, `spec.json`, `sections/NN.html`, `out/{cheatsheet_5장.html,cheatsheet_5장.pdf,spec.json,찾기-점검.md}`, `work/`의 시각·검토 증거.
- 승인된 교체 대상: `웹과제예상/커닝페이퍼/5장/`의 같은 4개 기본 파일.
- 최종 기록: `docs/superpowers/reviews/2026-10-15-bio-ch5-cheatsheet-rebuild.md`.
- 각 셸 호출에서 REPO(현재 worktree), CS=`$REPO/.agents/skills/bio-cheatsheet`, RUN(새 scratch 절대 경로)를 다시 설정한다.

### Task 1: 최신 자료로 구역 작성

**Files:** RUN/sources/manifest.md, spec.json, sections/NN.html. 기존 출력 수정 없음.

**Interfaces:** Consumes 선행 READY·현재 입력 파일 path/SHA256. Produces 기존 형식 spec와 10~16개 구역 조각. source manifest는 각 명칭·구별 단서·함정의 실제 원천 위치를 연결한다.

- [ ] **Step 1:** 선행 보고서 READY와 실제 입력 해시를 대조한다. 그 이후 노트가 바뀌었으면 영향 받은 선행 검토를 갱신하기 전 시작하지 않는다. 적용 스킬과 references/content-rules·section-brief·review-brief를 읽는다.
- [ ] **Step 2:** 기존 4개 파일과 응시 기록·사용자 찾기 측정값을 백업하고 해시를 기록한다. 이번 계획은 full 재생성이며 refresh를 호출하지 않는다.
- [ ] **Step 3:** 5장 토픽만 모아 source manifest를 작성한다. q03/q06/q09는 원인 확정 없이 판별 기준으로만 반영한다. ①은 실제 5장 출제 관찰, ②는 확인된 명칭 대응과 짧은 구별 단서로 작성한다. 원천이 없는 대응은 보류 기록으로 남긴다.
- [ ] **Step 4:** `python3 "$CS/scripts/stale.py" "$REPO" --basis` 출력으로 basis를 채운다. 현재 5장 피드백/등록이 반영됐는지 확인하고 수작업으로 최신 상태를 꾸미지 않는다. 5장 panic-patterns가 이미 있으므로 무관한 스킬 수정은 하지 않는다.
- [ ] **Step 5:** spec·구역 조각을 작성한다. 핵심 비교는 명칭↔현상, 전구체↔성숙 mRNA, 전사↔전사 후, DNA↔히스톤, 작동자↔억제자, 합성↔교정 방향이다. 각 구역의 원천·함정 출처를 확인한다. 모든 구역에 억지로 모든 비교를 넣지 않는다.

### Task 2: HTML·PDF 검토와 교체 인계

**Files:** RUN/out의 4개 후보, work/page-*.png·검토 증거, 최종 검토 보고서. 지시가 있으면 기본 시트 4개 교체.

**Interfaces:** Consumes Task 1 조각/spec. Produces 검토된 후보 또는 교체본과 정확한 published/candidate/withheld 상태. 후보를 기존 시트에 적용 완료했다고 보고하지 않는다.

- [ ] **Step 1:** `python3 "$CS/scripts/build.py" "$RUN/spec.json" "$RUN/sections" "$RUN/out"` 실행. `--no-pdf`를 사용하지 않는다.
- [ ] **Step 2:** `python3 "$CS/scripts/check.py" "$RUN/out/cheatsheet_5장.html" "$RUN/spec.json"` → 위반 0. 변형된 임시 spec에서 ② 누락·basis 누락이 검사로 발견되는지 확인하되 원본/생산 테스트는 고치지 않는다. 검사가 다루지 않는 원천 의미는 수동 리뷰에서 확인한다.
- [ ] **Step 3:** `pdftoppm -r 80 -png "$RUN/out/cheatsheet_5장.pdf" "$RUN/work/page"`로 모든 쪽을 보고 글자·표·화살표 겹침과 빈 쪽을 확인한다. HTML의 밝은/어두운 모드·목차·용어 검색도 실제 브라우저에서 확인한다.
- [ ] **Step 4:** 새 사실 리뷰어에게 source manifest와 원자료를 주고 구역별 내용·명칭·단위·단계·함정 출처를 대조하게 한다. 최대 2회 수정 후 다시 build/check/시각 확인/영향된 사실 리뷰를 한다. 실패 후보는 교체하지 않는다.
- [ ] **Step 5:** `spec.json`을 out에 복사하고 기출 5행의 `찾기-점검.md`를 작성한다. 기존 측정값이 있으면 원본을 보존하고 새 파일은 미측정 후보임을 명시한다. 5행·서로 다른 구역·부정형/그림·링크 유효성을 대조한다.
- [ ] **Step 6:** 이 계획 구현 지시에 따라 검토된 4개 기본 파일만 백업 후 교체한다. 후보만 요청받은 경우에만 RUN/out 경로를 제공한다. 사용자 측정값이 존재하는 찾기-점검은 원본을 별도로 보관해 새 표와 함께 제시한다. `stale.py "$REPO"` 결과를 보고하되 후보 상태이면 기본 시트의 stale 알림이 남는 것이 정상이다. 보호 원본/응시 기록/풀이기록 불변과 `git diff --check`를 확인한다.
- [ ] **Step 7:** 페이지 수·검토 결과·원천 미확인/제외 항목·현재 적용 상태·백업 위치를 최종 보고서에 기록한다. 10초 찾기나 숙달은 학생이 확인하기 전 완료로 주장하지 않는다.

## Plan Self-Review

선행 READY, full/refresh 경계, 근거 연결, 현재 basis, 전체 PDF 확인, 사용자 측정값 보존, 교체 권한의 구별을 각 작업에 반영했다. 새로운 생산 함수나 저장 필드는 없다. 독립 산출물로 복습팩 계획과 분리하되 순서는 고정했다.
