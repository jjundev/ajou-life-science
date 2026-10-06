---
name: bio-review-video
description: 완성된 생명과학 복습노트를 review-pack HTML 템플릿의 다크모드 디자인과 한국어 Aoede 음성을 사용하는 복습 영상으로 만든다. 복습 영상 제작·영상 복습·기존 영상의 목소리 교체 요청 또는 /bio-review-video 호출에 사용한다. 일반 정리노트 작성은 bio-review-pack을 사용한다.
---

# 생명과학 복습 영상

수업을 이미 들은 학생이 전체 내용을 복습하는 영상이다. **bio-review-pack HTML 템플릿을 화면 디자인 원본으로 유지**한다. 색상만 비슷한 별도 UI로 바꾸지 않는다. 기본은 다크모드·Pretendard·Vertex AI Aoede·1920×1080 30fps·자동 완주·비용 상한 없음이다. 단가 확인 없이 제작하며 요청별 사용량 기록은 유지한다. 예산은 사용자가 원할 때만 config.budget_usd로 설정한다.

SKILL은 이 파일의 폴더, REPO는 생명과학 저장소, RUN은 실행 결과 폴더다. 아래 명령의 python SKILL/scripts/video.py와 경로는 실제 절대 경로로 펼친다. 원자료로 노트를 만드는 일은 bio-review-pack에 맡긴다. 기존 노트·템플릿·영상은 수정하지 않는다.

인자: MMDD, MMDD-MMDD, 노트 폴더, --review, --resume, --revoice --voice NAME. 일반 노트 요청에는 적용하지 않는다.

## 절차

1. **준비.** HyperFrames entry skill을 읽고 승인된 의도/디자인/음성으로 workflow를 정한다. 선호를 다시 묻지 않는다. prepare --repo REPO RANGE를 실행한다. 반환 RUN을 이후 명령에 쓴다. --review 요청이면 prepare에도 붙인다. 재개는 resume --run RUN의 첫 미완료 단계부터 이어간다.
2. **전체 내용.** [출처·coverage](references/sources-and-coverage.md)를 읽는다. source/inputs.json의 원문/스냅샷을 읽고 모든 개념·수치·보충·오개념·문항 판별점을 manifest.json에 작성한다. HTML/MD 충돌을 근거로 해결한다. source/coverage.md에 원문 전체 대조 기록을 남긴다.
3. **대본·장면.** [대본·화면](references/narration-and-motion.md)을 읽는다. manifest.segments에 전체 발화와 핵심 자막, scenes에 의미 있는 동작을 설계한다. HTML fragment와 motion JSON을 source/scene-fragments에 작성한다. check --run RUN을 통과시킨다. --review일 때만 여기서 사용자 검토를 받고 승인 후 tts --approve-review로 계속한다.
4. **음성.** [음성·예산](references/voice-and-budget.md)을 읽고 비밀 없는 운영 config를 준비한다. 기본 제작에는 단가 조회나 확인이 필요 없다. tts --run RUN --config CONFIG --env-file ENV_FILE로 문단별 생성한다. 키를 출력하지 않는다. 환경변수를 쓰면 --env-file은 생략한다. 모델/공급자를 자동 대체하지 않는다.
5. **실측·화면.** assemble --run RUN --pack REPO/.agents/skills/bio-review-pack --assets-from LOCAL_ASSETS를 실행한다. LOCAL_ASSETS는 fonts/와 vendor/를 가진다. 화면은 note-template.html/review-template.html의 스냅샷 CSS와 의미별 클래스를 재사용하고 영상 배치만 덧붙인다. 내용이 많으면 장면을 나눈다.
6. **렌더.** render --run RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN을 실행한다. 실제 CPU/NVENC를 시험하고 장면을 렌더한 뒤 PCM을 한 번에 결합한다. 전역 GPU 설정을 바꾸지 않는다. 브라우저 GPU와 인코더 GPU 이용을 구분한다.
7. **검증.** [렌더·검증](references/rendering-and-verification.md)을 따른다. 모든 장면을 브라우저 검사하고 대표 이미지를 직접 확인한다. 내용/음성/화면 검토를 verification/reviews.json에 현재 input_hash와 증거로 기록한다. verify --run RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN으로 실제 편집 소스와 최종 파일을 검사한다. 검토 전 verify는 fingerprint와 미확인 항목을 제공한다. 실패하면 원인을 고치고 영향 단계부터 반복한다.
8. **전달.** 검증 완료 시에만 latest가 갱신된다. 아래 고정 출력 형식으로 정리한 뒤 최종 영상, narration.srt, chapters.txt를 절대 경로로 전달하고 실제 검증 범위를 구분한다.

## 고정 출력 형식

사용자가 다른 형식을 요청하지 않는 한 `복습영상/<MMDD 또는 RANGE>/`에는 **제목을 붙인 최종 MP4 하나와 제작자료 폴더 하나**만 둔다. 영상 제목은 학습 내용을 알아볼 수 있는 자연스러운 한국어로 에이전트가 짓는다. 날짜·실행 ID만 있는 영상 이름을 최종 이름으로 쓰지 않는다.

```text
복습영상/<날짜>/
├── <영상 제목>.mp4
└── <주제>_제작자료/
    └── 자막·장면 시간표·대본·HTML·음성·원자료 스냅샷·검증·실행 메타데이터
```

`prepare`의 RUN은 작업용 위치다. 완료 후 최종 MP4는 날짜 폴더로 옮기고 나머지 RUN 파일은 제작자료 폴더로 묶는다. `latest.json`도 제작자료 안에 넣어 날짜 폴더에 별도 파일을 남기지 않는다. 재개에 필요한 `review.mp4`는 제작자료 안에서 최종 영상으로 연결하는 상대 심볼릭 링크로 유지할 수 있으며 실제 영상을 중복 저장하지 않는다.

정리 후 영상 해시가 검증한 파일과 같은지, 자막·소스·메타데이터의 경로가 유효한지 확인한다. 이동으로 검증 지문이나 경로가 바뀌면 해당 기록도 새 위치에 맞춘다. 같은 날짜를 다시 제작할 때 기존 결과는 제작자료 안의 이전 버전으로 보존하고 날짜 폴더에는 최신 영상 하나와 제작자료 폴더 하나를 유지한다.

## 목소리만 변경

prepare --repo REPO --from-run OLD_RUN --voice Charon으로 별도 RUN을 만든다. 새 run에서 tts → assemble을 수행한 뒤 revoice --run RUN --source-run OLD_RUN --hyperframes-entry LOCAL_HYPERFRAMES_BIN을 실행한다. 기존 문단 경계로 재타이밍하며 내용/그림/가독성이 바뀌면 해당 장면을 재렌더한다. 원본과 이전 버전을 보존한다. 음성 비교 샘플도 같은 예산 ledger를 사용한다.

## 구현 경계

스크립트는 콘텐츠를 창작하지 않는다. 에이전트가 manifest/장면을 작성하고 의미를 검토한다. ID 연결만으로 전체 내용 보존을 주장하지 않는다. MP4 wrapper 통과를 편집 소스 통과로 대체하지 않는다. 인증·예산·내용 충돌은 구체적으로 보고하고 성공 파일을 재사용한다.

개발 회귀 명령: python -m unittest discover -s SKILL/tests -v. fake API/로컬 PCM을 사용하며 실제 API 비용을 발생시키지 않는다.
