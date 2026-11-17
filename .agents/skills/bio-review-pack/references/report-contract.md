# 보고 계약 (모든 서브에이전트와 메인 에이전트)

메인 에이전트의 컨텍스트는 실행 순서를 정하는 데만 쓴다. 서브에이전트의 **산출물은 파일**이고, 메인에 돌려주는 보고는 그 파일이 어디 있고 통과했는지 알리는 **영수증**이다. 상세(통과한 행, 근거 인용, 표)는 파일에만 둔다. 검증 단계를 줄이는 규칙이 아니다. 결과가 돌아오는 형태만 바꾼다.

## 서브에이전트: 영수증 형식

보고 본문은 아래 형식만 쓴다. 최대 12줄이다. 표·인용·근거 문장·통과한 항목 목록은 넣지 않는다.
```
결과: 완료 | 결함 있음 | 막힘
파일: <쓴 파일 경로들, 쉼표로>
수: <통과 N · 결함 N 처럼 세어 낸 값>
결함: <id> — <한 줄> (최대 8줄, 넘으면 "외 N건"과 파일 경로)
막힘: <쓰지 못한 파일·읽지 못한 자료와 이유> (없으면 줄을 뺀다)
```
- `결함` 줄에는 메인이 다음 행동을 정하는 데 필요한 id와 한 줄만 적는다. 고칠 내용 전체는 아래 `findings` 파일에 있다.
- 브리프가 따로 요구한 값(총평 3줄 등)이 있으면 그것만 더한다.

## 서브에이전트: 상세 기록 파일

상세 기록은 `<RUN>/work/reports/` 아래 TSV로 쓴다. 한 줄이 한 행이고 칸은 탭으로 나눈다. 칸 안에는 탭과 줄바꿈을 쓰지 않는다. `#`으로 시작하는 줄은 머리글이다.

| 파일 | 쓰는 쪽 | 칸 |
|---|---|---|
| `rows-<sid>.tsv` | 섹션 작성자 | 토픽 id · 본문의 핵심 주장 · 대응하는 요약 문장 · 판정·생략 이유 |
| `feedback-<sid>.tsv` | 섹션 작성자 | 피드백 ID · 실제 토픽 id · 본문 문장 · 적용 상태(본문 반영 / 기존 설명 충분 / 이전 노트 연결 / 미학습 보류 / 판독·근거 불확실) |
| `notes-<이름>.tsv` | 작성자(섹션·카드·감사) | id · 메모(넣지 않은 것과 이유, 못 가르친 사실, 카드별 한 줄 등) |
| `blind.tsv` | 블라인드 리뷰어 | 문항 · 내 답 · 근거 토픽 · 빠진 사실 · 최소 풀이 단계 · 수준 |
| `findings-<이름>.tsv` | 모든 검토자 | 심각도 · id · 문제 · 고칠 내용 |
| `fixed-<담당>.tsv` | 수정한 작성자 | id · 한 일(또는 반영하지 않은 이유) |

- `findings`의 심각도는 `critical`, `important`, `minor-easy`(한두 문장만 고치면 되는 사소한 것), `minor` 중 하나다. id는 토픽 id(`s2-checkpoint`), 섹션 id(`s2`), 카드 id(`p3`) 중 하나로 시작한다. `고칠 내용`은 담당 작성자가 다른 자료 없이 고칠 수 있을 만큼 구체적으로 쓴다.
- 각자 자기 이름이 붙은 파일만 쓴다. 병렬 작성자가 같은 파일을 덮어쓰지 않는다. 수정 라운드에서는 자기 `rows-<sid>.tsv`·`feedback-<sid>.tsv`를 **통째로 다시 쓴다**(바뀐 행만 보고하지 않는다).
- **쓰는 방법:** Write 도구는 서브에이전트가 `summary-audit-s0.md`처럼 보고서로 보이는 이름의 `.md`를 쓰는 것을 거부한다("Subagents should return findings as text"). 같은 폴더의 `.tsv`·`.txt`·`.html`·`.json`과 Bash 쓰기는 허용된다(2026-11-17 확인). 그래서 상세 기록은 위 이름의 `.tsv`로 쓰고, Write가 거부되면 고쳐 쓰려 하지 말고 곧바로 Bash로 쓴다.
  ```bash
  python3 - <<'EOF'
  rows = [("s1-mean", "평균은 합을 개수로 나눈다", "평균은 합을 개수로 나눈 값이에요", "반영")]
  open("<RUN>/work/reports/rows-s1.tsv", "w", encoding="utf-8").write("".join("\t".join(r) + "\n" for r in rows))
  EOF
  ```
  Bash로도 쓰지 못할 때만 영수증의 `막힘`에 적고 그 표를 보고 본문에 싣는다.

## 메인 에이전트

- 영수증만 읽는다. 상세 파일을 통째로 열지 않는다. 집계·대조·배분은 `scripts/pack_run.py`가 하고 메인은 그 출력 몇 줄만 본다.
  | 명령 | 하는 일 |
  |---|---|
  | `pack_run.py merge-problems --run RUN` | 문항 감사자의 `work/problems.json`을 manifest에 넣는다 |
  | `pack_run.py audit-merge --run RUN` | `rows-*.tsv` → `RUN/summary-audit.md`. 누락·수정 필요 행을 `findings-audit.tsv`로 낸다 |
  | `pack_run.py feedback-merge --run RUN` | `feedback-*.tsv` → `RUN/note-feedback-audit.md`의 「작성 후 적용 상태」 절 |
  | `pack_run.py blind-check --run RUN` | `blind.tsv`를 manifest `answer`·`level`과 대조 → `RUN/blind-results.md`, `findings-blind.tsv` |
  | `pack_run.py fixes --run RUN` | 모든 `findings-*.tsv`를 담당 작성자별 `RUN/work/fixes/<담당>.txt`로 나눈다 |
  | `pack_run.py status --run RUN` | 9단계 보고서에 쓸 집계 |
- 수정 요청은 내용을 옮겨 적지 않는다. 담당 작성자에게 "`<RUN>/work/fixes/<담당>.txt`를 읽고 모두 고친 뒤 영수증만 보고" 한 줄을 보낸다. 담당은 섹션 id(`s2`) 또는 카드 묶음(`cards-p1`, `cards-p11`, …)이다.
- 한 항목을 직접 확인해야 하면 id로 그 줄만 찾는다(`grep -n "s3-imaging" <파일>`). JSON·감사표·로그를 `cat`으로 통째로 출력하지 않는다. 필요한 키만 `python3 -c`로 뽑는다.
- 서브에이전트의 표를 메인이 파일에 다시 옮겨 쓰지 않는다. 영수증에 `막힘`이 있으면 그 에이전트에게 Bash로 다시 쓰게 한다.
- `work/reports/`는 full 조립 때 `.pack/reports/`로 복사되어 검토 수행 기록으로 남는다. 기록 파일을 고친 뒤에는 마지막 조립을 다시 한다.
