# 검토 기록과 발행

기계 검사는 구역·소문항·수식 보존·자원·파일 해시를 검사해요. 의미와 답이 맞다는 판단은 하지 않아요. build가 만든 `review.json`은 전부 `not_run`이에요. 실제 확인을 수행한 에이전트만 기록을 갱신해요. 기출 합본 PDF·웹과제·교과서의 문항 쪽과 대조하고, 카드의 원 답안을 독립 검산의 결과로 간주하지 않아요.

JSON의 `input_hash`는 현재 원본과 설명 조각에 묶여요. build 출력의 `artifact_hashes`도 그대로 검토 대상이에요. 조각·원본·렌더링 파일을 바꿨다면 다시 build하고 검토해요. 예전 검토 보고서는 통과하지 않아요.

- `source_visual`: 문항 조건·보기·그림·소문항을 원자료의 실제 쪽과 대조. 기출 문항은 `23, 24 소스/N강 합본.pdf`의 해당 쪽, 웹과제 문항은 `웹과제/N장/questions.json`의 해당 항목, 교과서 그림·표를 옮긴 문항은 `교과서/생명과학_기초와_응용_2판/0N장_*.pdf`의 해당 쪽. `data-source="생성 변형 …"` 카드는 `.pack/variants.md`에서 같은 id 행(근거 토픽, 형태 열의 교재 쪽)과 그 근거 토픽의 정리노트 절, 교재 쪽이 적혀 있으면 그 교과서 쪽과 대조. reviewer와 evidence에 자료/쪽/대조 결과.
- `content`: 상위 status/reviewer/evidence 및 items의 모든 `pN:a` 또는 `pN:main`. recall의 문제 단서와 개념 연결·용어와 기호의 뜻·적용 조건·선택 이유·소문항별 누락 여부, 첫 줄·보기별 판정과 근거·ㄱㄴㄷ 진술별 판정·부정형 질문 방향·모든 답·검산·충돌 여부 확인. recall은 정의/판단 기준만 필요한 문항도 허용하지만 제목만으로는 충분하지 않아요. start와 긴 설명을 복제하지 않았는지, 요약의 핵심 개념이 본문과 일치하는지 확인해요.
- `independent`: 같은 모든 items, method=`exact|symbolic|numerical|proof|qualitative`, conclusion과 evidence. 저작 에이전트와 다른, **정답을 보지 않은** 별도 에이전트가 문항(지문·보기·그림)과 정리노트·교과서·강의노트만으로 다시 풀어 카드 정답과 일치해야 해요. 이 에이전트에게 카드의 정답·풀이·설명 조각을 주지 않아요. method는 주로 `qualitative`, 유전 교배 비율 같은 계산은 `exact`예요. 컨트롤러는 재풀이 답을 카드 정답과 `.pack/key-check.md`의 인쇄·판단 답에 대조하고, 하나라도 다르면 disputed로 둬요(충돌). 카드 정답이 이 답들과 모두 같고 문항 표현만 결함이면 disputed가 아니라 설명에서 결함을 공개한 것으로 보고, content 검토에서 공개가 정확한지 확인해요. key-check.md(또는 question-audit.md)가 없는 팩은 카드 정답과 `.pack/variants.md`의 `의도한 정답과 이유` 열에 대조하고 evidence에 "key-check 없음"을 기록해요. 파일이 없다는 것만으로는 disputed가 아니에요. 재풀이 기록(`evidence/independent-<range>.md` 등)과 자료 쪽을 구체적으로 기록. 단, 카드 정답이 기출 인쇄 정답과만 다르고 교과서·강의노트 근거와 독립 재풀이(있으면 key-check 판단 답)가 모두 카드 정답과 같으면 인쇄 정답 오류로 보고 disputed로 두지 않아요. 이때 설명의 `<strong>인쇄 정답 오류:</strong>` 공개와 근거 쪽을 content에서 확인하고, evidence에 인쇄 정답·카드 정답·근거를 함께 기록해요.
- `browser`: 1280×900 및 375×812, light/dark. 모든 문항의 목차·이전/다음·요약·수식·표·그림·링크를 확인. 콘솔·KaTeX 오류·누락 자원·문서 가로 넘침은 0. 짧은 인라인 수식의 스크롤 컨테이너와 수식 영역의 보이는 스크롤바는 0. 구역 24px·제목 아래 12px·소문항 16px 간격, 행렬 잘림과 겹침을 실제 렌더링으로 확인. 긴 수식은 의미 단위 줄바꿈을 우선하고, 더 나눌 수 없는 긴 수식만 안내와 함께 스크롤바 없는 국소 이동을 허용. 외부 요청 없이 로컬 자원으로 렌더링. 1280·1024에서 오른쪽 문제 탭이 기본으로 보이고 요약 탭 전환이 되는지, 375에서 '문제 보기' 토글이 해설 위에 있는지 확인.

네 검토 source_visual·content·independent·browser는 `lite`에서도 모두 실제로 수행해요. 각 단계와 items는 status=`pass`, 비어 있지 않은 reviewer/evidence여야 발행돼요. `not_run`, `fail`, `disputed`는 발행을 보류해요. numerical은 유한한 tolerance>0, 0<=residual<=tolerance도 필요해요. proof에 숫자 예제 확인만 있는 evidence는 수동 검토에서 승인하면 안 돼요.

```json
{
  "status": "pass",
  "reviewer": "독립 검산 에이전트(정답 비공개)",
  "evidence": "evidence/independent-1008.md: 정리노트·교과서 05장 p.NN으로 다시 푼 답 (5), 카드 정답·key-check.md 판단 답과 일치",
  "method": "qualitative",
  "conclusion": "보기 (1)~(4)는 교과서 설명과 일치하고 (5)만 틀려 답 (5)"
}
```

사용한 근거 파일은 대상 작업 디렉터리의 `evidence/` 아래 보관해요. `references`에는 읽은 저장소 내부 자료의 절대 path와 SHA-256을 기록해요. 발행 직전 재확인돼요. `artifact_hashes`에는 manifest를 포함한 현재 stage 파일의 상대경로→SHA-256을 기록해요. build가 넣은 값을 승인 전 점검하며 임의로 오래된 검토에 새 해시만 덮어씌우지 않아요.

답 충돌·조건 모호함·원문 미확인은 해당 팩을 disputed로 표시하고 이유를 보고해요. 다른 독립 팩은 통과하면 발행할 수 있어요. 기존 파일은 변경하지 않고 설명 소유 파일만 백업 후 교체하며 실패 시 복구해요.

## forecast 예상문제

명시 경로의 예상문제는 p1–p15 전체를 다루고 o1·o2 개요는 제외해요. 해당 버전 src/v<K>/pack.json과 blueprint.md의 기출 출처·모드·노트 앵커를 확인해요. key-check.md/variants.md 대신 이 근거를 사용해요. 원문 그대로인 문항만 원문 답과 직접 대조하고, 변형 문항은 바뀐 조건·숫자·보기 순서로 실제 재풀이해요. 새 예상문항을 실제 기출로 표현하지 않아요. original이 새 예상문항의 출처 안내이면 기출 원문이라고 주장하지 않아요.

독립 검산은 별도 에이전트가 정답을 보지 않은 문항 사본으로 수행해요. 설계표의 정답·pack.json 정답키·o1/o2 정답·카드 풀이·해설을 제공하지 않아요. 컨트롤러가 재풀이 결과와 pack.json/blueprint.md를 대조하고 자료의 path/SHA-256을 references에 기록해요. 오류가 남으면 disputed/fail로 두고 [연결 계약](../../bio-webquiz-forecast/references/explanation-handoff.md)에 따라 수정 후 다시 검토해요. 해설만 수정하면 build/check 및 네 검토, 문제/문맥 변경이면 새 RUN 재추출부터 수행해요. 최초 이후 최대 2회 수정·재검토를 넘기면 발행을 보류해요. 상태나 해시만 바꿔 승인하지 않아요.
