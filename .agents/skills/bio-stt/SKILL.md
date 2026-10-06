---
name: bio-stt
description: Use when transcribing biology lecture audio or video recordings (.m4a, .mp3, .wav) into a verbatim transcript under STT/<MMDD> 생명.md with domain-specific terminology guidance for ajou-life-science, or when invoking /bio-stt.
---

# Bio STT (생명과학 강의 음성 전사)

생명과학 강의 녹음 음성을 Gemini 네이티브 멀티모달(`view_file`)로 축어적(verbatim) 전사하고, 당일 진도(강의 슬라이드·예습노트·교과서)의 생명과학 고유명사 및 발음 교정 지침을 프롬프트에 주입하여 전문용어 오인식을 최소화한 마스터 전사본을 `STT/<MMDD> 생명.md`로 산출한다.

---

## 🧠 핵심 원칙

1. **도메인 특화 어휘 주입 (Context-Aware Prior)**:
   - 파일명에서 날짜(`MMDD`)를 자동 추출하고, 당일 진도 단원의 슬라이드 텍스트 및 교재 부록에서 핵심 생물학 고유명사를 추출해 서브에이전트 프롬프트에 힌트로 주입한다.
   - 발음이 뭉개지거나 일상 단어로 들리기 쉬운 어휘(예: *이수체*, *역위*, *비분리*, *클라인펠터 증후군*, *헬리케이스*, *리가아제* 등)는 생명과학 표준 용어로 전사한다.
2. **저장소 표준 경로 및 산출물 보존**:
   - 최종 마스터 전사본은 항상 `STT/<MMDD> 생명.md`로 생성한다.
   - 포맷은 기존 전사본 규격과 일치하게 `# <MMDD> 생명 전체 오디오 전사본` 및 `## Part 01`, `## Part 02` 헤더 아래 문단 단위 클린 텍스트로 저장한다.
3. **네이티브 멀티모달 전사 (외부 Whisper 절대 금지)**:
   - Whisper, mlx-whisper, faster-whisper 등 외부/로컬 모델을 절대 설치하거나 사용하지 않는다.
   - 오디오를 1fps 블랙 비디오 래퍼(`color=c=black:s=320x240:r=1`)가 포함된 MP4로 변환한 뒤, Gemini의 `view_file` 기능으로 직접 듣고 전사한다.
4. **10분 세그먼트 및 병렬 서브에이전트**:
   - 10분이 넘는 긴 음성은 10분(600초) 단위로 분할하여 `self` 서브에이전트를 병렬 기동한다.
5. **복습팩 파이프라인 자동 연결**:
   - 전사 완료 후 `/bio-review-pack <MMDD>` 실행을 안내하여 예습 → 수업 STT → 복습팩 생성이 매끄럽게 연결되도록 한다.

---

## 🛠️ 실행 절차

### 0. 인자 확인 및 날짜·단원 컨텍스트 추출

오디오 파일명에서 날짜(`MMDD`)와 단원(Chapter) 정보를 추출하고, 프롬프트 주입용 용어 목록을 생성한다.

```bash
REPO="$(git rev-parse --show-toplevel)"
python3 "$REPO/.agents/skills/bio-stt/scripts/infer_context.py" "<AUDIO_PATH>" --repo "$REPO" --json > "/tmp/bio_stt_context.json"
```

- 파일명에 날짜가 명시되어 있지 않은 경우 에러가 발생하므로, 사용자가 `--date MMDD`를 지정해야 한다.
- 콘솔에 파싱된 날짜, 단원명, 추출된 용어 수가 표시된다.

### 1. 오디오 전처리 (10분 분할 및 MP4 래핑)

임시 작업 폴더(`STT/_temp_<MMDD>/`)를 생성하고 10분 단위 분할 및 MP4 변환을 수행한다.

```bash
REPO="$(git rev-parse --show-toplevel)"
DATE=$(python3 -c "import json; print(json.load(open('/tmp/bio_stt_context.json'))['date'])")
WORK_DIR="$REPO/STT/_temp_${DATE}"
mkdir -p "$WORK_DIR"

# 1) 10분 분할 (오디오만 분할)
ffmpeg -y -i "<AUDIO_PATH>" -vn -c:a libmp3lame -b:a 192k \
  -f segment -segment_time 600 -segment_start_number 1 -reset_timestamps 1 \
  "$WORK_DIR/${DATE}_생명_part%02d.mp3"

# 2) 1fps 블랙 MP4 래퍼 일괄 생성
for f in "$WORK_DIR"/*_part*.mp3; do
  (
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
    ffmpeg -y -f lavfi -i color=c=black:s=320x240:r=1 \
      -i "$f" -t "$dur" -c:v libx264 -c:a aac -b:a 128k "${f%.mp3}_temp.mp4" -loglevel error
  ) &
done
wait
```

*(참고: 전체 오디오가 10분 이하인 단일 파일인 경우 분할 없이 단일 `_temp.mp4`로 래핑하여 직접 처리한다.)*

### 2. 도메인 가이드가 포함된 병렬 서브에이전트 전사

각 파트마다 `self` 서브에이전트를 띄워 병렬로 전사를 수행한다.

**서브에이전트 프롬프트 템플릿**:
```text
You are a verbatim STT transcription agent specialized in college Biology (생명과학).
Target video: <WORK_DIR>/<DATE>_생명_part01_temp.mp4
Output markdown: <WORK_DIR>/<DATE>_생명_part01.md

<PROMPT_GUIDE> (infer_context.py 의 prompt_guide 내용 삽입)

Instructions:
1. Call `view_file` on <WORK_DIR>/<DATE>_생명_part01_temp.mp4.
2. Transcribe ALL spoken words verbatim from start to finish. Do not skip, summarize, or omit anything.
3. Group 2~4 sentences per paragraph, separated by blank lines (\n\n). Do not output timestamps unless requested.
4. When technical terms sound ambiguous or muffled, bias towards the correct Korean/English biology terms provided above.
5. Save directly to <WORK_DIR>/<DATE>_생명_part01.md using `write_to_file` (Overwrite=True).
6. Strict Guardrails:
   - NEVER use, search for, or install Whisper or any external STT tools.
   - Rely solely on native `view_file`.
7. Report completion immediately when done.
```

### 3. 마스터 전사본 병합 및 자동 정리

전체 파트 전사가 완료되면 `merge_transcripts.py`를 실행하여 `STT/<DATE> 생명.md`로 병합하고 임시 파일을 정리한다.

```bash
REPO="$(git rev-parse --show-toplevel)"
python3 "$REPO/.agents/skills/bio-stt/scripts/merge_transcripts.py" \
  --dir "$WORK_DIR" \
  --prefix "${DATE}_생명" \
  --out "$REPO/STT/${DATE} 생명.md"
rm -rf "$WORK_DIR"
```

*(타임스탬프가 필요한 경우 `--timestamps` 옵션을 추가한다.)*

### 4. 완료 보고 및 후속 가이드 안내

전사 완료 후 사용자에게 결과를 보고하고, 다음 단계 복습팩 생성을 안내한다:
```text
✅ 생명과학 강의 전사 완료: STT/<DATE> 생명.md
- 대상 수업: <DATE> (<CHAPTER>장 <CHAPTER_TITLE>)
- 전문용어 힌트 적용 완료

👉 이 전사본으로 복습팩(정리노트 + 복습문제)을 생성하려면 다음 명령을 실행하세요:
/bio-review-pack <DATE>
```

---

## 🛡️ 안전 필터(Safety Filter) 복구 프로토콜

Gemini safety filter에 의해 특정 파트가 블록될 경우:
1. **Whisper 폴백 절대 금지**: Whisper 설치 시도 금지.
2. **해당 파트를 2~3분 단위 서브 청크로 분할**:
   ```bash
   ffmpeg -y -i "<FAILING_CHUNK>.mp3" -ss 0 -t 150 -c copy "<FAILING_CHUNK>_sub01.mp3"
   ffmpeg -y -i "<FAILING_CHUNK>.mp3" -ss 150 -t 150 -c copy "<FAILING_CHUNK>_sub02.mp3"
   ```
3. 각각 1fps 블랙 MP4로 감싸서 `view_file`로 전사 후 하나의 파트 파일로 합친다.

---

## ⚠️ 흔한 실수 및 주의사항

- **날짜 형식 누락**: 파일명에 날짜가 없는데 추측으로 임의의 날짜를 지정하지 말 것. 반드시 사용자에게 `--date MMDD`를 요청할 것.
- **용어집 오남용**: 교수님이 말하지도 않은 용어를 프롬프트에 있다고 임의로 지어내어 채워 넣지 말 것 (축어성 원칙 준수).
- **저장소 위치 이탈**: 마스터 전사본은 반드시 `STT/<MMDD> 생명.md`에 저장할 것 (루트나 다른 폴더에 저장 금지).
