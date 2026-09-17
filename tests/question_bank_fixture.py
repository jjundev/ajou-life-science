import hashlib
import json
from pathlib import Path


def make_bank(base: Path) -> tuple[Path, dict]:
    (base / "raw").mkdir(parents=True, exist_ok=True)
    raw = base / "raw" / "fixture.txt"
    raw.write_text("fixture source: 1 question", encoding="utf-8")
    (base / "evidence.md").write_text(
        "DNA는 유전 정보를 저장한다.", encoding="utf-8"
    )
    bank = {
        "schema_version": 1,
        "assessment": {
            "id": "web-test-ch01",
            "title": "테스트 전용",
            "chapter": 1,
            "date": "2026-09-17",
            "expected_question_count": 1,
            "time_limit_seconds": None,
            "max_points": 1,
            "evidence_source_ids": ["s1"],
        },
        "sources": [
            {
                "id": "s1",
                "path": "raw/fixture.txt",
                "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                "width": 1,
                "height": 1,
            }
        ],
        "assets": [],
        "questions": [
            {
                "id": "web-test-ch01:q01",
                "number": 1,
                "points": 1,
                "source_ids": ["s1"],
                "original": {
                    "format": "single_choice",
                    "content": [
                        {"type": "text", "text": "유전 정보 저장 물질은?"}
                    ],
                    "options": [
                        {"id": "A", "text": "DNA"},
                        {"id": "B", "text": "지방"},
                    ],
                },
                "observations": {
                    "phase": "pre_submission",
                    "selected_option_id": "B",
                    "selected_source_id": "s1",
                    "official_answer": None,
                },
                "analysis": {
                    "answer_option_id": "A",
                    "answer_status": "reasoned",
                    "grading": "single",
                    "also_accept": [],
                    "reason": "DNA가 유전 정보를 저장한다.",
                    "concept_ids": ["dna"],
                    "skills": ["statement-evaluation"],
                    "requirements": [
                        {
                            "id": "r1",
                            "statement": "DNA는 유전 정보를 저장한다.",
                            "evidence": [
                                {
                                    "path": "evidence.md",
                                    "locator": "1",
                                    "quote": "DNA는 유전 정보를 저장한다.",
                                }
                            ],
                        }
                    ],
                    "option_diagnostics": {
                        "A": {
                            "is_answer": True,
                            "explanation": "유전 정보 저장에 해당한다.",
                            "requirement_ids": ["r1"],
                        },
                        "B": {
                            "is_answer": False,
                            "explanation": "지방은 이 질문의 답이 아니다.",
                            "requirement_ids": ["r1"],
                        },
                    },
                    "issues": [],
                },
                "review": {
                    "status": "pending",
                    "payload_sha256": None,
                    "notes": None,
                },
            }
        ],
    }
    path = base / "questions.json"
    path.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path, bank
