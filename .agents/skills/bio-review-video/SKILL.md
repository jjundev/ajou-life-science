---
name: bio-review-video
description: 완성된 생명과학 복습노트를 읽고 애니메이션이 이해에 도움이 되는 부분을 추출해 주제별 복습 영상을 만든다. review-pack 다크모드와 한국어 Aoede 음성을 사용한다. 복습 영상 제작·영상 복습·기존 영상의 목소리 교체 요청 또는 /bio-review-video 호출에 사용한다. 일반 정리노트 작성은 bio-review-pack을 사용한다.
---

# 생명과학 복습 영상

수업을 이미 들은 학생을 위한 **주제별 애니메이션 복습 영상**이다. 기본 흐름은 **복습노트 전체 읽기 → 영상이 필요한 부분 추출 → 독립 주제로 묶기 → 주제별 제작**이다. 선정한 주제가 두 개면 영상도 두 개 만든다. 전체 내용을 읽어주는 통합 영상은 사용자가 명시적으로 요청할 때만 만든다.

**bio-review-pack HTML 템플릿을 화면 디자인 원본으로 유지**한다. 색상만 비슷한 별도 UI로 바꾸지 않는다. 기본은 다크모드(항상 고정, 라이트 렌더 금지)·Pretendard·Vertex AI Aoede·1920×1080 30fps·자동 완주·비용 상한 없음이다. 주제별 길이는 약 1–3분을 목표로 설명에 맞춘다. 길이에 맞추려고 필요한 내용을 누락하거나 모든 영상을 90초로 고정하지 않는다. 사용자 지정 범위·길이가 우선한다. 단가 확인 없이 제작하며 요청별 사용량 기록은 유지한다. 예산은 사용자가 원할 때만 config.budget_usd로 설정하며 여러 영상이 같은 요청의 예산·ledger를 공유한다.

SKILL은 이 파일의 폴더, REPO는 생명과학 저장소, RUN은 실행 결과 폴더다. 아래 명령의 python SKILL/scripts/video.py와 경로는 실제 절대 경로로 펼친다. 원자료로 노트를 만드는 일은 bio-review-pack에 맡긴다. 기존 노트·템플릿·영상은 수정하지 않는다.

인자: MMDD, MMDD-MMDD, 노트 폴더, --review, --resume, --revoice --voice NAME. 일반 노트 요청에는 적용하지 않는다.

## 절차

1. **읽기·선정·준비.** HyperFrames entry skill을 읽고 승인된 의도/디자인/음성으로 workflow를 정한다. 선호를 다시 묻지 않는다. [선정·여러 영상](references/selection-and-batches.md)을 읽고 복습노트 HTML/MD·복습문제·장마감 문서를 대조한다. 에이전트가 전체 개념 목록, 선정/비선정 이유와 주제 묶음을 selection.json에 작성한다. plan-check --repo REPO RANGE --selection PLAN을 통과시킨 뒤 prepare-set --repo REPO RANGE --selection PLAN을 실행한다. 반환 BATCH와 영상별 RUN을 이후 명령에 쓴다. --review 요청이면 prepare-set에도 붙인다. 재개는 resume-set --batch BATCH가 알려주는 영상별 첫 미완료 단계부터 이어간다. 명시적인 전체 복습·기존 영상 재개·목소리 교체는 기존 prepare/resume/--from-run 경로를 유지한다.
2. **선정 기록·내용 범위.** [출처·coverage](references/sources-and-coverage.md)를 읽는다. BATCH의 전체 선정 기록과 각 RUN의 영상 범위를 구분한다. 해당 영상의 주개념과 필요한 선수 개념을 모두 manifest.json에 등록하고 발화문에 연결한다. 원자료의 claim·수치·조건을 바꾸지 않는다. source/coverage.md에 의미 대조를 남긴다. 전체 복습 요청일 때는 기존대로 원문 전체 학습 내용을 포함한다.
3. **대본·장면.** [대본·화면](references/narration-and-motion.md)을 읽는다. manifest.segments에 전체 발화와 핵심 자막, scenes에 의미 있는 동작을 설계한다. HTML fragment와 motion JSON을 source/scene-fragments에 작성한다. check --run RUN을 통과시킨다. --review일 때만 여기서 사용자 검토를 받고 승인 후 tts --approve-review로 계속한다.
4. **음성.** [음성·예산](references/voice-and-budget.md)을 읽고 비밀 없는 운영 config를 준비한다. 기본 제작에는 단가 조회나 확인이 필요 없다. tts --run RUN --config CONFIG --env-file ENV_FILE로 문단별 생성한다. 키를 출력하지 않는다. 환경변수를 쓰면 --env-file은 생략한다. 모델/공급자를 자동 대체하지 않는다.
5. **실측·화면.** assemble --run RUN --pack REPO/.agents/skills/bio-review-pack --assets-from LOCAL_ASSETS를 실행한다. LOCAL_ASSETS는 fonts/와 vendor/를 가진다. 화면은 note-template.html/review-template.html의 스냅샷 CSS와 의미별 클래스를 재사용하고 영상 배치만 덧붙인다. 내용이 많으면 장면을 나눈다.
6. **렌더.** render --run RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN을 실행한다. 실제 CPU/NVENC를 시험하고 장면을 렌더한 뒤 PCM을 한 번에 결합한다. 전역 GPU 설정을 바꾸지 않는다. 브라우저 GPU와 인코더 GPU 이용을 구분한다.
7. **검증.** [렌더·검증](references/rendering-and-verification.md)을 따른다. 모든 장면을 브라우저 검사하고 대표 이미지를 직접 확인한다. 내용/음성/화면 검토를 verification/reviews.json에 현재 input_hash와 증거로 기록한다. verify --run RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN으로 실제 편집 소스와 최종 파일을 검사한다. 검토 전 verify는 fingerprint와 미확인 항목을 제공한다. 실패하면 원인을 고치고 영향 단계부터 반복한다.
8. **묶음 전달.** 각 RUN 검증이 끝나면 publish-set --batch BATCH를 실행한다. 선정한 영상 모두가 현재 지문으로 검증되어야 전체 완료와 latest가 갱신된다. 일부 실패 시 성공한 영상·음성은 보존하고 실패한 단계만 재개한다. 이어서 아래 "자막" 절대로 모든 영상에 하드 자막을 굽고 자막본만 남긴다. 최종 영상들, 각 영상의 narration.srt·chapters.txt와 제작자료 폴더를 절대 경로로 전달하고 실제 검증 범위를 구분한다. 전체 복습·목소리 교체의 단일 결과도 아래 형식으로 정리한다.

## 자막 (고정)

화면 안에는 하단 고정 문구(`.video-caption`)를 넣지 않는다. 핵심 문장은 장면의 "꼭 기억해요" 박스로만 보여 준다. 자막은 렌더 후 **하드 자막**으로 굽는다. 검증(`verify`)과 `publish-set`은 자막 없는 마스터로 수행하고, 그 뒤 날짜 폴더에는 **자막본만 남긴다.** 자막본의 파일명에는 `_자막` 같은 접미사를 붙이지 않고 영상 제목 그대로(`<영상 제목>.mp4`) 둔다.

```text
python SKILL/scripts/video.py burn-subtitles --video "<제목>.mp4" --srt RUN/narration.srt --output "<제목>_자막.mp4"
```

`burn-subtitles`는 입력 파일을 덮어쓰지 않으므로 임시 이름(`_자막`)으로 만든다. 자막본 검사(`status: passed`)와 대표 프레임 확인이 끝나면 자막 없는 `<제목>.mp4`를 지우고 `<제목>_자막.mp4`를 `<제목>.mp4`로 바꾼다. 같은 이름의 파일이 이미 있으면 덮어쓰지 말고 멈춘다. 모든 영상을 바꾼 뒤 `복습영상/README.md`·`catalog.json`의 경로·크기·SHA256을 실제 남은 파일 기준으로 갱신한다.

설정은 `scripts/lib/subtitles.py`에 고정했으며 사용자가 바꾸라고 하지 않는 한 건드리지 않는다.

- 폰트 Pretendard Bold(`assets/fonts/Pretendard-Bold.ttf`, 영상 본문과 동일 서체). libass는 woff2를 읽지 못하므로 TTF를 쓴다. 맑은 고딕 등 시스템 폰트로 대체하지 않는다.
- 하단 중앙 한 줄, 흰 글씨·검은 테두리 2, FontSize 14, MarginV 22(1080p에서 하단 약 80px 위). 화면 하단의 박스·본문과 겹치지 않는다.
- narration.srt의 긴 문단 자막은 문장·쉼표 단위(한 줄 약 34자 이하)로 쪼개고 글자 수 비례로 시간을 나눈다. 실제 음성과 1~2초 어긋날 수 있으므로 대표 프레임과 재생으로 확인한다.
- 재인코딩은 libx264 crf 18, 오디오는 복사한다.
- 마스터를 지운 뒤에는 제작자료의 `review.mp4` 링크와 latest.json의 영상 해시가 남은 자막본과 맞지 않는다. 이는 의도된 상태이며 제작자료를 자막본에 맞춰 고치지 않는다. 자막본은 검증 지문의 대상이 아니다.
- 목소리 교체·재검증·자막 재굽기에 마스터가 필요하면 해당 RUN에서 `render`를 다시 실행해 마스터를 재생성한다(음성 캐시를 재사용하므로 TTS 유료 요청은 없다). 자막본을 `--source-run`이나 자막 재굽기 입력으로 쓰지 않는다(자막이 이중으로 들어간다).

## 영상이 필요한 부분과 분할 기준

- 이동·분리·결합·축적·방향·시간에 따른 변화가 이해의 핵심이며, 보여줄 구체적인 상태 변화와 해결할 오개념을 설명할 수 있는 부분을 선정한다.
- 단순 용어 정의·목록·비교표는 별도 영상으로 만들지 않는다. 선정 주제에 필요한 기초 개념은 그 영상의 선수 설명으로 포함한다.
- 독립된 학습 질문 하나를 영상 하나로 묶는다. DNA 복제의 역평행·프라이머·선도/지연 가닥·오카자키 절편·연결효소는 같은 기작이므로 함께 설명한다. 감수분열 비분리는 별도 주제다.
- 같은 내용을 여러 영상의 주제로 중복 선정하지 않는다. 공통 선수 개념은 필요한 영상에서 짧게 다시 설명할 수 있다.
- 선정 결과가 0개면 이유와 선정 기록만 전달하며 MP4·TTS를 억지로 생성하지 않는다. 1개면 하나, N개면 N개를 제작한다. 개수를 미리 채우지 않는다.
- `--review`일 때 전체 선정 목록과 모든 영상의 장면 구성을 묶어 한 번에 검토한다. 기본 자동 제작에서는 선정 목록·이유·예상 길이를 알리고 진행한다.

## 고정 출력 형식

사용자가 다른 형식을 요청하지 않는 한 `복습영상/<MMDD 또는 RANGE>/`에는 **하드 자막을 구운 제목 있는 최종 MP4 N개와 제작자료 폴더 하나**를 둔다. 자막 없는 마스터와 `_자막` 접미사 파일은 남기지 않는다. N은 선정한 독립 주제 수이며 0도 가능하다. 영상 제목은 학습 내용을 알아볼 수 있는 자연스러운 한국어로 에이전트가 짓는다. 날짜·실행 ID만 있는 영상 이름을 최종 이름으로 쓰지 않는다.

```text
복습영상/<날짜>/
├── <영상 제목 1>.mp4      # 하드 자막본, 접미사 없음
├── <영상 제목 2>.mp4
└── <날짜>_제작자료/
    ├── latest.json
    └── 실행/<실행ID>/
        ├── selection.json · batch.json · 원자료 스냅샷 · 공용 사용량 기록
        └── videos/<주제ID>/
            └── 자막·장면 시간표·대본·HTML·음성·검증·실행 메타데이터
```

`prepare-set`의 RUN은 처음부터 제작자료 안에 생성한다. `publish-set`이 영상 해시·검증 지문·증거 파일을 확인해 제목 있는 마스터 MP4를 날짜 폴더로 내보내고 RUN의 review.mp4는 상대 심볼릭 링크로 바꾼다. 그 뒤 "자막" 절의 순서로 마스터를 자막본으로 교체한다. 각 RUN을 옮겨 검증 지문을 바꾸거나 실제 최종 영상을 중복 저장하지 않는다. 기존 단일 실행은 정리 후 지문·경로를 다시 확인한다.

같은 날짜를 다시 제작할 때 기존 결과는 제작자료 안의 이전버전으로 보존하며 기존 review.mp4 링크도 이전 영상으로 연결한다. 날짜 폴더에는 이번에 선정한 영상 N개와 제작자료 폴더 하나를 유지한다. 파일명 충돌·선정 변경·검증 실패를 조용히 덮어쓰지 않는다. 명시적 커밋 요청이 있을 때만 해당 결과와 목록을 커밋하며 인증 파일은 제외한다.

## 목소리만 변경

prepare --repo REPO --from-run OLD_RUN --voice Charon으로 별도 RUN을 만든다. 원래 RUN의 마스터가 지워졌으면 먼저 OLD_RUN에서 render로 마스터를 재생성한다. 새 run에서 tts → assemble을 수행한 뒤 revoice --run RUN --source-run OLD_RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN을 실행한다. 기존 문단 경계로 재타이밍하며 내용/그림/가독성이 바뀌면 해당 장면을 재렌더한다. 원본 제작자료와 이전 버전을 보존하고, 최종 결과는 "자막" 절대로 자막본으로 교체한다. 음성 비교 샘플도 같은 예산 ledger를 사용한다.

## 구현 경계

스크립트는 콘텐츠를 창작하지 않는다. 에이전트가 manifest/장면을 작성하고 의미를 검토한다. ID 연결만으로 전체 내용 보존을 주장하지 않는다. MP4 wrapper 통과를 편집 소스 통과로 대체하지 않는다. 인증·예산·내용 충돌은 구체적으로 보고하고 성공 파일을 재사용한다.

개발 회귀 명령: python -m unittest discover -s SKILL/tests -v. fake API/로컬 PCM을 사용하며 실제 API 비용을 발생시키지 않는다.
