import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/study-note-eli5/scripts"
sys.path.insert(0, str(SCRIPTS))


def digest(value):
    return hashlib.sha256(value).hexdigest()


def case(base):
    note = "# 효소\n\n효소는 활성화에너지를 낮춘다.\n\n평형은 바꾸지 않는다.\n"
    quiz = "2강 6: 효소에 대한 설명 중 틀린 것은? 답: 비가역 반응을 가역 반응으로 만든다.\n"
    (base / "note.md").write_text(note, encoding="utf-8")
    (base / "quiz.txt").write_text(quiz, encoding="utf-8")
    inventory = {
        "main_source": "note",
        "sources": [
            {"id": "note", "path": "note.md", "role": "note", "sha256": digest(note.encode()), "read_status": "read"},
            {"id": "quiz", "path": "quiz.txt", "role": "quiz", "sha256": digest(quiz.encode()), "read_status": "read"},
        ],
        "blocks": [
            {"id": "b0", "start": 1, "end": 1, "kind": "metadata", "fact_ids": [], "reason": "단원 제목"},
            {"id": "b1", "start": 3, "end": 3, "kind": "teaching", "fact_ids": ["f1"], "reason": ""},
            {"id": "b2", "start": 5, "end": 5, "kind": "teaching", "fact_ids": ["f2"], "reason": ""},
        ],
        "facts": [
            {"id": "f1", "block_id": "b1", "statement": "효소는 활성화에너지를 낮춘다.", "qualifiers": [], "concept_id": "enzyme", "scope": "teaching", "evidence": {"source_id": "note", "locator": "3행", "quote": "효소는 활성화에너지를 낮춘다."}},
            {"id": "f2", "block_id": "b2", "statement": "평형은 바꾸지 않는다.", "qualifiers": ["속도와 평형 구분"], "concept_id": "enzyme", "scope": "teaching", "evidence": {"source_id": "note", "locator": "5행", "quote": "평형은 바꾸지 않는다."}},
        ],
        "concepts": [{"id": "enzyme", "title": "효소", "prerequisites": [], "prior_note": ""}],
        "questions": [{"id": "2강:6", "source_id": "quiz", "locator": "1행", "status": "included", "fact_ids": ["f2"], "reason": ""}],
    }
    data = {"schema_version": 1, "inventory": inventory,
            "inventory_sha256": digest(json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
            "mappings": [{"fact_id": "f1", "target_ids": ["fact-barrier"]}, {"fact_id": "f2", "target_ids": ["fact-balance"]}],
            "review": {"status": "pending"}}
    return data


HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>효소</title></head>
<body>
<section id="concept-enzyme" data-concept="enzyme" data-role="teaching">
<h2>효소: 반응을 시작하는 문턱</h2>
<p id="fact-barrier">효소는 활성화에너지를 낮춥니다.</p>
<p id="fact-balance">반응물과 생성물의 에너지 차이나 평형은 바꾸지 않습니다.</p>
<div data-role="recall" data-generated="true"><p>학습용 생성 질문: 효소가 바꾸는 것과 바꾸지 않는 것을 말해 보세요.</p>
<details><summary>설명 확인</summary><p data-part="model-answer">활성화에너지를 낮추지만 평형은 바꾸지 않습니다.</p></details></div>
</section>
<article data-question-id="2강:6" data-status="included"><h3>원본 문항 2강 6</h3>
<p data-part="prompt">효소에 대한 설명 중 틀린 것은?</p><details data-role="solution"><summary>정답과 근거</summary>
<p data-part="answer">비가역 반응을 가역 반응으로 만든다.</p><p data-part="reason">효소는 평형을 바꾸지 않습니다.</p>
<p data-part="trap">속도 변화와 평형 변화를 혼동하지 마세요.</p><a data-remedy="confusion" href="#concept-enzyme">개념 비교 복습</a>
</details></article></body></html>"""


def reviewed(data, html):
    data["review"] = {
        "status": "complete", "artifact_sha256": digest(html.encode()),
        "inventory_sha256": data["inventory_sha256"], "inventory_change_reason": "",
        "source_audit": {"status": "pass", "notes": "fixture 구간과 사실을 대조했다."},
        "fact_checks": [
            {"fact_id": "f1", "status": "pass", "evidence": "fact-barrier에 활성화에너지 감소가 있다."},
            {"fact_id": "f2", "status": "pass", "evidence": "fact-balance에 평형 불변이 있다."},
        ],
        "reverse_audit": {"status": "pass", "notes": "근거 없는 추가 주장이 없다."},
        "visual_audit": {"status": "pass", "notes": "fixture는 화면 검토용 가상 기록이다."},
        "conflicts": [],
    }
    return data
