# 음성과 예산

Vertex AI Express / gemini-2.5-flash-tts / Aoede / ko-KR가 기본이다. assets/vertex-direction.txt의 승인 지시문을 사용한다. 다른 음성을 요청할 때만 짧은 동일 원고 샘플을 비교한다. 공급자나 모델을 자동 대체하지 않는다.

환경변수 GOOGLE_API_KEY 또는 GEMINI_API_KEY, 또는 명시적인 --env-file을 사용한다. 키를 대화·로그·설정 파일에 복사하지 않는다. 기존 프로젝트 .env를 자동 탐색하지 않는다.

운영 config.price에는 input_per_million, output_per_million(USD 문자열), verified_at(날짜), source(공식 Vertex 가격 근거)를 제공한다. 구현 테스트 단가는 운영 가격이 아니다. 실행 전에 현재 모델/오디오 과금 단위를 공식 문서와 대조한다. 단가가 없으면 요청하지 않는다. input payload UTF-8 byte 수와 max_output_tokens로 보수적인 요청 비용을 예약한다. samples, retry, ASR도 반드시 같은 Budget ledger를 사용한다.

예산 기본 $2는 로컬 요청 제한이다. 타임아웃 등 불확실한 요청은 예약액을 환불하지 않는다. 클라우드의 실제 청구 상한을 보장하지 않는다. 429/일시적 서버 오류만 최대 4회 재시도하며 반복 429는 다음 batch를 1개로 줄인다. 인증/모델 오류·잘린 음성은 성공 캐시로 저장하지 않는다.

--revoice는 기존 audio metadata/시간표/MP4를 입력으로 새 실행을 만든다. 새 음성 파일명에는 입력 hash를 포함하므로 이전 성공 음성을 덮어쓰지 않는다.
