# Harden ajou-bb Skill with Integrity Checks and Troubleshooting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md` with download integrity verification rules (rejecting 77KB dummy HTML shells), direct `course_id` resolution, and sandbox/EPERM troubleshooting.

**Architecture:** Augment `Workflow 2` in `SKILL.md` with an explicit post-download integrity verification criterion (inspecting magic bytes and rejecting HTML login redirects), update Command Routing to support exact Blackboard `course_id` arguments, and expand Troubleshooting with real-world failure modes encountered in Blackboard Learn Ultra.

**Tech Stack:** Markdown, YAML Frontmatter, OpenCLI (`opencli ajou-bb`), Blackboard Learn Ultra REST API.

## Global Constraints

- Target file: `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`
- Keep file lean, concise, and structured (under 140 lines).
- Maintain all existing workflows, Korean anchors, and D-Day reporting formats.
- Retain model-invoked status (do not set `disable-model-invocation: true`).

---

### Task 1: Update `SKILL.md` with Integrity Check and Troubleshooting

**Files:**
- Modify: `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`

**Interfaces:**
- Consumes: Existing structure of `SKILL.md`.
- Produces: Hardened `SKILL.md` with integrity verification gate in Workflow 2, direct course ID routing guidance, and expanded troubleshooting entries.

- [ ] **Step 1: Read existing SKILL.md to ensure clean line bounds**

Run: `view_file` on `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md` lines 1 to 118.

- [ ] **Step 2: Atomically update SKILL.md**

Write the complete updated content to `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`:

```markdown
---
name: ajou-bb
description: >
  아주대학교 Blackboard Learn Ultra (아주대 블랙보드, 아주Bb) LMS automation.
  MUST USE when the user asks to check pending assignments or due dates,
  download lecture notes, read unread announcements, inspect course grades,
  or analyze class student demographics via blackboard.
---

# ajou-bb — 아주대학교 Blackboard Ultra LMS 도우미

## 🛡️ Ground Rules
1. **Adapter First**: 모든 Blackboard 조작은 로컬 `opencli ajou-bb <subcommand>`를 최우선 호출합니다.
2. **Inspect-then-Act**: 강의자료는 `contents`로 구조를 먼저 열람하고, 다운로드 대상이 확정된 후 `download`를 실행합니다.
3. **Privacy Masking**: 학생 식별 번호(학번), 이메일, 토큰 등 PII는 명시적 요청이 없는 한 마스킹 상태를 유지합니다.
4. **Standard Storage**: 다운로드 파일은 사용자가 별도 지정하지 않는 한 프로젝트 루트의 `./강의노트/<과목명>/`에 자동 분류 저장합니다.
5. **Structured Briefing**: 브리핑 보고서는 D-Day 그룹핑(`🚨 D-3 이내 긴급`, `📅 이번 주 마감`, `📌 이후`) 테이블과 체크리스트로 출력합니다.

---

## 📋 Command Routing Reference

| 영역 | 서브커맨드 | 핵심 옵션 | 사용 목적 |
|---|---|---|---|
| **세션 확인** | `status` | `--include-sensitive` | 로그인 세션 상태 및 학생 프로필 검증 |
| **일정/스트림** | `calendar`, `stream` | `--days 7`, `--category due_soon` | 다가오는 마감일, 시험, LMS 실시간 업데이트 |
| **수강 과목** | `courses` | `--term <YYYY-학기>` (생략 시 현재 학기) | 활성 수강 과목 및 학수번호/과목ID 확인 |
| **과제/시험** | `assignments <과목>` | `--pending`, `--submitted` | 과제 제출 여부, 마감 기한, 배점 확인 |
| **강의 자료** | `contents <과목>`, `download <과목>` | `--depth 2`, `--query "<단어>"`, `--all` | 강의실 폴더/문서 탐색 및 로컬 다운로드 (`<과목>`은 과목명, 학수번호, 또는 고유 `course_id` 지원) |
| **공지/성적** | `announcements <과목>`, `grades [과목]` | `--unread`, `--term <YYYY-학기>` | 미확인 공지 본문 파싱, 항목별 성적/비중 |
| **학습 분석** | `analytics <과목>` | `--term <YYYY-학기>` | LTI 대시보드 연동 수강생 학년/학점/전공 분석 |

---

## 🚀 Core Workflows

### Workflow 1: 통합 학습 브리핑 (Exhaustive Sweep)
학생이 "오늘 과제 뭐 있어?", "이번 주 마감 브리핑해줘", "블랙보드 현황 요약" 등을 요청할 때 실행합니다.

1. **실행 시퀀스**:
   - `opencli ajou-bb calendar --days 7 -f yaml`
   - `opencli ajou-bb stream --category due_soon --limit 10 -f yaml`
   - `opencli ajou-bb courses -f yaml` 로 활성 과목 목록 확보.
2. **과목별 전수 검사 (Loop completion criterion)**:
   - `courses`에서 반환된 **모든 활성 수강 과목**에 대해 빠짐없이 `opencli ajou-bb assignments "<과목명>" --pending -f yaml`을 실행해야 합니다.
   - ⚠️ **조기 종료(Premature completion) 방지**: 1~2개 과목만 조회하고 보고서 생성을 시작하는 것을 엄격히 금지합니다. 모든 과목의 응답을 수합하기 전까지는 합성을 시작하지 마십시오.
3. **결과 합성 및 보고 기준 (Synthesis Criterion)**:
   - 수합된 모든 과제 및 일정을 반드시 아래 3개 필수 섹션과 마크다운 테이블 및 체크리스트 서식으로 출력합니다:

#### 🚨 D-3 이내 긴급
| 과목명 | 과제/시험명 | 마감 일시 | 남은 시간 |
|---|---|---|---|
| <과목명> | <과제명> | YYYY-MM-DD HH:mm | D-N (XX시간 남음) |

- [ ] [과목명] 과제 제출 완료하기

#### 📅 이번 주 마감
| 과목명 | 과제/시험명 | 마감 일시 | 남은 시간 |
|---|---|---|---|
| <과목명> | <과제명> | YYYY-MM-DD HH:mm | D-N |

- [ ] [과목명] 과제 진행 및 검토

#### 📌 이후
- **향후 마감 과제**: D-7 초과 마감 일정 요약
- **주요 공지 요약**: 최근 7일 내 주요 과목별 미확인 공지 핵심 1줄 요약

---

### Workflow 2: 스마트 강의자료 탐색 및 다운로드 (Inspect-then-Act)
학생이 "강의자료 확인해줘", "자료 다운로드해줘" 등을 요청할 때 실행합니다.

1. **Step 1 (Inspect)**:
   - `opencli ajou-bb contents "<과목명>" --depth 3 -f yaml` 실행.
   - 폴더 트리 및 파일 목록을 사용자에게 제시하고 다운로드할 대상 확인.
2. **Step 2 (Act - 다운로드 게이트)**:
   - 사용자가 다운로드 대상을 명시하거나 일괄 다운로드를 지시한 경우에만 실행:
     * 특정 주차/키워드: `opencli ajou-bb download "<과목명>" --query "<키워드>" --out ./강의노트/<과목명>/ -f yaml`
     * 전체 다운로드: `opencli ajou-bb download "<과목명>" --all --out ./강의노트/<과목명>/ -f yaml`
3. **Completion & Integrity Criterion**:
   - 다운로드 완료 후 파일명, 용량, 저장 위치(`destination_path`), 결과 상태(`downloaded`/`skipped`)를 테이블로 안내.
   - ⚠️ **무결성 사후 검증(Integrity Check)**: 다운로드된 파일들이 모두 동일한 크기(예: 77KB 내외)이거나 HTML 로그인/리디렉션 쉘(`<HTML`)이 아닌지 확인. 실제 문서 매직 바이트(HWP 5.x, PDF, ZIP 등) 및 정상 용량을 검증한 뒤 보고서를 마무리합니다.

---

### Workflow 3: LTI 학습분석차트 심층 진단 (Learning Analytics)
학생이 "학습분석차트 봐줘", "수강생 통계 어때?", "학점 분포 알려줘" 등을 요청할 때 실행합니다.

1. **실행 시퀀스**:
   - `opencli ajou-bb analytics "<과목명>" -f yaml` 실행.
2. **Synthesis Criterion**:
   - 다음 4가지 영역을 반드시 포함하여 분석 브리핑을 완성:
     * **수강생 구성**: 총 수강 인원, 학년별 비율, 전공 분포
     * **직전 학점(GPA) 분포**: 4.0 초과 / 3.5~4.0 / 3.0~3.5 / 3.0 이하 비율
     * **선이수 과목 Top 5**: 주요 선이수 과목 순위 및 이수율
     * **💡 학습 대비 전략**: 수강생 학년 및 선이수 구성을 바탕으로 한 구체적 학업 조언

---

### Workflow 4: 미확인 공지 & 성적 관리 (Announcements & Grades)
학생이 "새 공지 있어?", "성적 확인해줘" 등을 요청할 때 실행합니다.

1. **실행 시퀀스**:
   - 미확인 공지: `opencli ajou-bb announcements "<과목명>" --unread -f yaml`
   - 성적 조회: `opencli ajou-bb grades "<과목명>" -f yaml`
2. **Synthesis Criterion**:
   - 공지: 제목, 작성일시, 본문 핵심 요약
   - 성적: 항목별 배점, 내 득점, 반영 비중(%), 교수자 피드백을 표로 정리

---

## 💡 Troubleshooting
- **세션 검증 (`Session Check`)**:
  - `opencli ajou-bb status`로 세션 유효성을 확인합니다.
- **인증 만료 (`AuthRequiredError`, Exit Code 77)**:
  - Chrome 브라우저에서 `https://eclass2.ajou.ac.kr` 로그인 여부 확인을 사용자에게 안내합니다.
- **과목명 모호성 (`Multiple courses found`)**:
  - `opencli ajou-bb courses`로 목록을 확인한 뒤, 충돌을 피하기 위해 학수번호(예: `BIO111`)나 고유 ID(예: `_118608_1`)를 지정하여 실행합니다.
- **더미 HTML 파일 다운로드 현상 (약 77KB 동일 크기)**:
  - Blackboard Ultra의 SPA 내부 라우팅 URL(`/ultra/redirect?...`) 직접 요청 또는 세션 쿠키 누락 시 웹 쉘 HTML이 반환되는 현상입니다.
  - REST 첨부파일 API(`/learn/api/public/v1/courses/<CID>/contents/<ID>/attachments`)를 통한 원본 첨부파일 다운로드 엔드포인트 및 확장자 매핑을 확인하십시오.
- **샌드박스 파일 접근 오류 (`EPERM`)**:
  - `opencli` 데몬 및 브라우저 프로필 소켓(`~/.opencli/`) 통신이 차단될 경우 `BypassSandbox: true` 권한으로 실행하십시오.
```

- [ ] **Step 3: Verify updated file content and formatting**

Run: `view_file` on `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`.
Expected: Around 124 lines (safely under the 140-line ceiling), well-formed markdown, all sections intact.

---

### Task 2: Quality and Integrity Verification

**Files:**
- Test / Verify: `/Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`

**Interfaces:**
- Consumes: Updated `SKILL.md`.
- Produces: Confirmed compliance with Antigravity skill guidelines, zero placeholders, and exact anchor validation.

- [ ] **Step 1: Check for required anchors and keywords**

Verify that the following critical terms are present in `SKILL.md`:
- `Completion & Integrity Criterion`
- `무결성 사후 검증(Integrity Check)`
- `더미 HTML 파일 다운로드 현상`
- `고유 ID(예: _118608_1)`
- `EPERM`
Expected: All terms match.

- [ ] **Step 2: Check for any placeholder text**

Scan `SKILL.md` for `TODO`, `TBD`, or incomplete sections.
Command: `grep -i -E "todo|tbd|placeholder" /Users/hyunjun_macbook_pro/.gemini/config/skills/ajou-bb/SKILL.md`
Expected: 0 matches (exit code 1).
