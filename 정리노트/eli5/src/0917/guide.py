"""0917 complete ELI5 guide data. Rebuild with build_guide.py."""
import guide_kit as kit
from facts import SOURCES, CONCEPTS, BLOCKS, FACTS
from questions import QUESTIONS, DEFERRED
from sections import SECTIONS, BOUNDARY


kit.TITLES.update({c: title for c, title, _ in CONCEPTS})

META = dict(
    note="../../../0917.md",
    overrides="../../meta/0917-eli5.question-scope-overrides.json",
    output_stem="0917-eli5",
    title="0917 생명과학 ELI5 · 염색체, 세포주기와 암",
    quiz_sources={"3강": dict(source_id="quiz3", path="../23, 24 소스/3강 합본.pdf", label="3강 합본 원문")},
    groups=[("chromosome", "염색체 관계"), ("division", "2n·n과 분리 대상"), ("cycle", "세포주기와 확인점"), ("control", "세포주기 조절"), ("tumor", "암과 전이")],
    header_html=("<style>@media(max-width:600px){{.fig{{overflow-x:auto;-webkit-overflow-scrolling:touch}}.fig svg{{min-width:560px;max-width:none;margin-left:0}}}}@media print{{.q>.qid{{break-after:avoid-page}}.q>.qid+[data-part=\"prompt\"]{{break-before:avoid-page}}}}</style>"
                 "<header><small>ELI5 학습 가이드 · 0917 생명과학 · 원천: 0917 실강 + 3강 원문 문제지</small>"
                 "<h1>염색체부터 암까지 — 무엇이 복제되고, 무엇이 멈추는가</h1>"
                 "<p>포함 {inc}문항 · 복습 {rev}문항 · 보류 {deferred}문항 = {total}문항. 관계 그림 → 작동 원리 → 원문 문제 순서로 공부하세요. 정답은 접혀 있으며 인쇄 시 펼쳐집니다.</p></header>"),
    scope_notes_html=("<p>3강 합본 40문항을 원본 PDF 네 쪽과 대조했습니다. 0917 실강에서 직접 다룬 염색체 관계·배수성·세포주기·암 조절 23문항을 활성화했고, "
                      "교수님이 다음 시간에 비교하겠다고 한 단계별 유사·감수분열·재조합·DNA량 문항 17개는 ID를 유지해 보류했습니다. "
                      "3강 30번은 강의의 단순화와 현대 생물학의 더 세분된 S기 점검 개념 차이를 해설에 공개했습니다.</p>"),
    footer="한 줄 암기: 복제 사본은 자매염색분체, 부모 유래 한 쌍은 상동염색체다. G1-S-G2-M을 확인점이 지키고, 가속 유전자와 브레이크 유전자의 고장이 쌓이면 암이 된다.",
)
