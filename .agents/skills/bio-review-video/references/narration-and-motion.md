# 대본과 화면

디자인 원본은 sibling bio-review-pack/assets의 note-template.html과 review-template.html이다. 이 파일을 수정하지 않는다. snapshot_theme로 HTML/CSS를 보존하고 data-theme=dark를 강제한다. 별도 팔레트나 새로운 카드 디자인을 만들지 않는다. 영상용 크기/배치만 assets/video-layout.css로 조절한다.

manifest.scenes의 template_kind는 note/review다. source/scene-fragments/<scene-id>.html은 해당 템플릿의 topic/layer/tag/badge/figure/문제 클래스를 재사용한다. 긴 본문은 여러 장면으로 분리한다. inline style/script/event/외부 URL은 금지한다. SVG와 이미지는 run 내부 assets에 둔다. 모든 ID는 <scene-id>-로 시작한다.

같은 이름의 .motion.json은 target(#ID), segment_id, kind(reveal/move/count/highlight/path), from/to(GSAP property 객체), duration_s 배열이다. 이동·축적·수량 변화처럼 학습 의미가 있는 움직임을 넣는다. path는 미리 계산한 SVG strokeDashoffset/dasharray 또는 x/y 좌표로 표현한다. 시간 기반 random/interval은 쓰지 않는다.

원고는 용어와 수치를 보존하고 자막은 핵심 문장으로 줄인다. TTS 실제 PCM 샘플 수가 확정된 후 timing.py가 시간을 만든다. 자막은 하단 908px부터, 본문은 위 영역에 배치한다. 단어별 타임스탬프를 지어내지 않는다. 학생용 SRT는 전체 발화, 화면에는 핵심 자막이다.

stage_assets에는 fonts/Pretendard-{Regular,SemiBold,Bold}.woff2와 vendor/gsap.min.js가 있는 로컬 asset 폴더를 넘긴다. 기존 복습영상/0915/20260929-legacy/assets를 재사용할 수 있으며 출처/라이선스도 보존한다. 수식이 있으면 local vendor/katex에 katex.min.js, katex.min.css, auto-render.min.js와 fonts를 제공한다. 누락을 네트워크 fallback으로 감추지 않는다.
