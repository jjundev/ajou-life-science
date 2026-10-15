# 문제에서 검토된 해설로

문제 `check --final` 성공 후 기존 `.agents/skills/bio-problem-explain/SKILL.md`를 읽고 명시 HTML을 입력으로 사용한다.

```sh
python3 EXPLAIN/scripts/mpe_cli.py extract --repo REPO --target ABS_시험예상문제_HTML --run NEW_EXPLAIN_RUN
```

exam adapter는 p1~p75와 20개 short_answer 모델을 전달한다. all/최신은 기존 복습노트만 선택한다. range/version/manifest/카드/정답/검토가 불일치하면 거부한다. pack/blueprint/scope/policy/candidates/manifest/question-review와 present 근거를 context_hashes에 묶고 missing→present도 재확인한다.

기존 understand/recall/start/solve/verify/pitfall/retry 조각을 작성하고 단답형 canonical/accepted/대소문자·단위 판정을 설명한다. build/check 후 source_visual/content/independent/browser 네 해설 검토를 실제 수행하고 publish한다. 해설 이름은 `문제해설_<범위>_시험예상_vK.html`, 부속 MD·그림·자료는 `.pack/vK/` 안이다. 단순 HTML 존재는 완료가 아니다. status는 실제 manifest/validation/검토/산출 해시와 현재 질문 근거를 검사한다.

최초 검토 이후 오류가 있으면 문제 RUN의 `exam_cli.py repair --run RUN --reason ...`를 먼저 기록한다. repair-history와 run.repairs_used를 같이 보존한다. 두 단계 합계 최대2회이며 새 해설 RUN은 이 예산을 초기화하지 않는다.

- 문제 오류: RUN의 candidates/scope/policy를 수정하고 select/build로 새 버전을 예약한다. 같은 RUN이 소유한 수정 전 초안들은 과거 신규 출제 이력에서 제외하여 재선정 시 거짓 부족을 막는다. 이전 버전은 보존한다. build/check → 문제 네 검토 → 새 EXPLAIN_RUN extract부터 진행. 완료된 버전은 덮어쓰지 않는다.
- 해설만 오류: 기존 조각을 수정 → 해설 build/check → 네 해설 검토를 모두 다시 수행 → publish. 오래된 review를 재사용하지 않는다.
- 두 번 후 미해결: 더 반복하지 않고 partial/unverified로 보고한다. 검증된 문제를 보존한다.

최종 `status --run RUN --explanation ABS_HTML`이 complete일 때 두 결과를 전달한다. partial은 문제만 검증됨, unverified는 질문 검증도 미완료다. repair-history 삭제/수동 예산 초기화는 금지한다.
