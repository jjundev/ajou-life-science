"""0910 ELI5 guide data — entry point for build_guide.py.

Rebuild:  python3 .agents/skills/study-note-eli5/scripts/build_guide.py 정리노트/eli5/src/0910/guide.py
"""
import guide_kit as kit
from facts_a import SOURCES, CONCEPTS, BLOCKS, FACTS_A
from facts_b import FACTS_B

kit.TITLES.update({c: t for c, t, _ in CONCEPTS})
kit.BADGES["rev"] = "0908 복습"

from questions_a import QUESTIONS_A  # noqa: E402
from questions_b import QUESTIONS_B, DEFERRED_REASONS  # noqa: E402
from sections_a import SECTIONS_A  # noqa: E402
from sections_b import SECTIONS_B  # noqa: E402
from sections_c import SECTIONS_C, BOUNDARY  # noqa: E402

FACTS = FACTS_A + FACTS_B
QUESTIONS = QUESTIONS_A + QUESTIONS_B
SECTIONS = SECTIONS_A + SECTIONS_B + SECTIONS_C  # SECTIONS[0] = 30초 지도, then the scope table


def _deferred_facts(ident):
    if ident.startswith("1강"):
        return ["d1", "d4"]  # 막수송: §1-4 경고 + 보류 줄
    if ident == "2강:13":
        return ["d3"]  # 원문 레이아웃 근거로 재분류, 광합성 후속 범위
    return ["d5", "d3"]  # 발효·광합성: 보류 줄 + 강의 끊김


DEFERRED = {i: (reason, later, _deferred_facts(i)) for i, (reason, later) in DEFERRED_REASONS.items()}

META = dict(
    note="../../../0910.md",
    overrides="../../meta/0910-eli5.question-scope-overrides.json",
    output_stem="0910-eli5",
    prior_notes={"review-cell": "0908"},
    title="0910 생명과학 ELI5 · 세포호흡 학습 가이드",
    quiz_sources={
        "1강": dict(source_id="quiz1", path="../23, 24 소스/1강 합본.pdf", label="1강 합본"),
        "2강": dict(source_id="quiz2", path="../23, 24 소스/2강 합본.pdf", label="2강 합본"),
    },
    groups=[("review", "복습 문항 — 1강(0908 내용)"), ("chloroplast", "엽록체·식물세포"), ("atp", "ATP"),
            ("enzyme", "효소"), ("redox", "산화환원"), ("glycolysis", "해당과정·ATP 장부"),
            ("krebs", "시트르산 회로"), ("oxphos", "전자전달계·산화적 인산화")],
    header_html=('<header><small>ELI5 학습 가이드 · 0910 생명과학 · 원천: 0910.md + 원문 문제지</small>\n'
                 '<h1>1장 마무리와 2장 세포호흡 — 그림으로 이해하고 원본 문제로 확인하기</h1>\n'
                 '<p>포함 {inc}문항 · 복습 {rev}문항 · 보류 {deferred}문항 = {total}문항. 개념 절을 먼저 읽고, 회상 질문을 풀고, '
                 '<a href="#questions">원본 문제</a>로 넘어가세요. 정답은 모두 접혀 있습니다(인쇄하면 펼쳐집니다).</p></header>'),
    scope_notes_html=('<p>문항 문장과 보기는 <b>원문 PDF(23, 24 소스 1강·2강 합본)</b>를 이미지로 대조해 옮겼습니다. '
                      '동반 퀴즈 <code>0910.html</code>에는 보기를 줄이거나 바꾼 문항(2강 1·6·8·10·11·14·15·23·29·35·38·43·44)과 '
                      '원문에 없는 13번이 있어, 이 가이드는 원문을 따르고 차이를 각 해설에 공개합니다.\n'
                      "<b>2강 13번</b>은 매핑표에서 '포함'이었지만, 원문에서는 광합성 반응식 그림이 13번 자리로 보여 근거와 함께 "
                      "'보류'로 바꿨습니다(ID는 유지). 1강의 나머지 문항은 이번 회차 추적 대상이 아닙니다.</p>"),
    routine_html='''<section class="card" id="study-routine"><p class="kicker">다음 공부</p><h2>틀린 문제는 이렇게 복습합니다</h2>
<ul><li><b>용어</b>를 몰랐다 → 해설의 링크로 개념 절에 가서 굵은 글씨 정의를 소리 내어 읽습니다.</li>
<li><b>개념을 혼동</b>했다(리보솜/리소좀, NAD+/NADH, 전자전달계/ATP 합성효소) → 개념 절의 ⚠️ 상자와 비교 문장을 봅니다.</li>
<li><b>과정·방향</b>이 헷갈렸다(ATP→ADP, H+ 이동, 전자 이동) → 그림의 화살표를 손으로 따라 그립니다.</li>
<li><b>조건·단위</b>를 놓쳤다(포도당 1개당 vs 아세틸-CoA 1개당, 산소 유무, '완전히 산화') → 표의 기준 열을 다시 봅니다.</li></ul>
<p>맞혔더라도 이유를 한 문장으로 설명하지 못했다면 복습 대상입니다. 오늘은 그림과 설명을 읽고, <b>다음 공부를 시작할 때</b> 설명을 가린 채 회상 질문부터 답해 보세요. <b>주간 복습</b>에서는 여러 절의 문제를 섞어서 풉니다.</p></section>''',
    footer=("한 줄 암기: 포도당의 전자는 NADH·FADH2를 타고 산소로 내려가며, 그 에너지는 H+ 댐을 거쳐 ATP 합성효소에서 "
            "ATP가 된다. 효소는 이 모든 반응의 턱을 낮출 뿐 도착점은 바꾸지 않는다."),
)
