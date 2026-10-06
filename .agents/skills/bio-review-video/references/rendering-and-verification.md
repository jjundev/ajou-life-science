# 렌더와 검증

Python 3.11+, Node, FFmpeg/ffprobe, 로컬 HyperFrames CLI Node entry가 필요하다. HyperFrames entry는 해당 설치의 bin/hyperframes.mjs다. CLI에 --hyperframes-entry로 절대 경로를 넘긴다. 렌더 버전은 기록하고 이전 run의 도구/템플릿을 몰래 갱신하지 않는다.

probe_backends는 실제 CPU/NVENC 60frame 영상과 전체 decode를 시험한다. 여유 VRAM이 있으면 2개 병렬도 실측한다. 브라우저 캡처 GPU는 NVENC와 별개다. 실제 render 로그가 확인되기 전 RTX browser capture로 보고하지 않는다. OS 전역 GPU 선호 설정은 변경하지 않는다.

검증:
1. content: 전체 원문 항목 발견과 발화/문항 판별점 의미 대응 검토.
2. audio: PCM hash/무음/클리핑/길이 검사 + 핵심 수치 직접 청취 또는 예산에 포함한 전사. 표본 검사 범위를 명시.
3. visual: tests/browser_check.mjs로 모든 장면/테마/자막 경계 검사(장면 안 고정 자막은 없으므로 captionCount는 0이어야 한다) 후 스크린샷을 직접 검토. 템플릿 컴포넌트와 크기 변경만 다른지 비교.
4. source: HyperFrames check를 실제 편집 소스에 실행. timeout은 unverified. MP4 wrapper로 대체 금지.
5. media: ffprobe, 전체 decode, 1920×1080/30fps/mono24k/프레임/스트림.
6. sync: PCM 샘플과 문단 경계, 마지막 audio/video 시간 오차.

verification/reviews.json의 content/audio/visual은 {status,evidence:[run 내부 경로],errors:[],input_hash} 형식이다. input_hash는 verify 모드가 출력하는 현재 review_fingerprint 값이다. 마지막 산출물이 정해진 뒤 검토하고 기록한다. 오래된 검토는 통과하지 않는다. content와 audio의 의미 검토를 기계 성공으로 자동 승인하지 않는다.

node tests/browser_check.mjs RUN PUPPETEER_PACKAGE_JSON CHROME_EXE는 로컬 설치한 puppeteer-core와 Chrome 실행 파일을 사용한다. 각 인자는 절대 경로다. 화면 대표 PNG는 verification/frames에 저장한다.

완료 보고는 검증한 항목과 미확인 항목을 구분한다. report.complete일 때만 latest.json을 갱신한다. 실패 시 이전 최신 결과를 유지한다. 사용자가 명시한 예산이 소진되면 성공한 문단을 보존하고 사용자에게 예산/실패 사유를 알린다. --resume은 처음 미완료 단계부터 다시 수행한다.

하드 자막본은 마스터 검증 후 만든다. 자막 위치·폰트는 SKILL.md의 "자막 (고정)" 설정을 따르고, 자막본의 대표 프레임에서 박스·본문과 겹치지 않는지 직접 확인한다.

**다크모드 고정.** 최종 영상은 항상 다크모드다. 렌더는 반드시 `render_parts`(장면별 `scene-NN.html`, `data-theme="dark"` 진입점)와 `mux`로 한다. 프로젝트 `index.html`을 `hyperframes render .`로 한 번에 렌더하면 서브 컴포지션 CSS 때문에 라이트로 나올 수 있으므로 쓰지 않는다. 코드가 이를 강제한다: `render_parts`는 `data-theme="dark"`가 아닌 진입점·`index.html`을 거부하고, `mux`·`verify_media`(`not-dark`)·`burn_subtitles`는 여러 시점의 좌상단 배경 밝기가 기준(80)을 넘으면 실패한다. 이 검사를 끄거나 우회하지 않는다.
