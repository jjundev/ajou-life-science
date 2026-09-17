# Mixed PDF and web note recipe

Use this only after both the legacy PDF item and the registered web bank have
passed their source audits. It is a temporary procedure sample, not a complete
chapter guide. Run the whole block from the repository root in one shell.

The temporary `legacy-quiz.json` is the explicitly authored legacy QUIZ data.
`export_note_items` supplies the active bank item, and `render_note` writes one
JSON-compatible marker block containing both sources. The example keeps one
audited 2강 item and one active real-bank item; the other real-bank IDs remain
visible as deferred rows in the separate WEB table.

```bash
MIXED_DIR="$(mktemp -d)"
export MIXED_DIR
export NOTE_SOURCE_ROOT="$PWD"

.venv-question-bank/bin/python - <<'PY'
import hashlib
import json
import os
from pathlib import Path

from scripts.question_bank.model import load_bank
from scripts.question_bank.note import export_note_items, render_note
from scripts.question_bank.render import figure_templates
from scripts.question_bank.scope import load_web_scope, reference_href

root = Path(os.environ["NOTE_SOURCE_ROOT"]).resolve()
tmp = Path(os.environ["MIXED_DIR"]).resolve()
note_root = tmp / "repo" / "정리노트"
test_root = tmp / "repo" / "tests"
note_root.mkdir(parents=True)
test_root.mkdir(parents=True)

bank_path = root / "웹과제/1장/questions.json"
bank = load_bank(bank_path, complete=True, repo_root=root)
bank_id = bank["assessment"]["id"]
scope_rows = []
for question in bank["questions"]:
    active = question["number"] == 2
    scope_rows.append({
        "id": question["id"],
        "status": "included" if active else "deferred",
        "reason": "혼합 드라이런의 직접 범위" if active else "절차 표본 밖",
        "prerequisite": None if active else "실제 회차 범위와 근거 검토",
        "refs": ([{"path": "정리노트/0908.md",
                   "section": "§4 원핵세포와 진핵세포"}] if active else []),
    })
scope = {
    "schema_version": 1,
    "banks": [{
        "path": os.path.relpath(bank_path, tmp),
        "sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
        "questions": scope_rows,
    }],
}
scope_path = tmp / "scope.json"
scope_path.write_text(json.dumps(scope, ensure_ascii=False, indent=2), encoding="utf-8")

legacy = [{
    "n": 6,
    "src": "2강",
    "q": "효소에 대한 설명 중 틀린 것은?",
    "opts": ["비가역 반응을 가역 반응으로 만든다.", "활성화에너지를 낮춘다."],
    "answer": 0,
    "why": "효소는 활성화에너지를 낮추지만 반응의 평형은 바꾸지 않는다.",
    "trap": {"1": "활성화에너지를 낮추는 것은 효소의 올바른 기능이다."},
    "keyNote": "2강 합본 Q6 감사를 반영한 임시 authored legacy payload",
    "ref": "§1 효소",
}]
legacy_path = tmp / "legacy-quiz.json"
legacy_path.write_text(json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8")

entries, banks = load_web_scope(scope_path, root)
web_items = export_note_items(banks[bank_id], entries)
for item in web_items:
    for ref in item["refs"]:
        ref["href"] = reference_href(ref, root, note_root)
items = json.loads(legacy_path.read_text(encoding="utf-8")) + web_items
html = render_note(
    (root / "정리노트/_template.html").read_text(encoding="utf-8"),
    {"date": "0999", "title": "혼합 출처 절차 드라이런"},
    items,
    figure_templates(banks[bank_id], bank_path.parent),
)
(note_root / "0999.html").write_text(html, encoding="utf-8")

web_rows = []
for row in entries:
    section = row["refs"][0]["section"] if row["refs"] else ""
    summary = "내막계 구성원과 리보솜 구별" if row["id"].endswith(":q02") else "절차 표본 밖"
    web_rows.append(f'| {row["bank_id"]} | {row["id"]} | {summary} | {section} | {row["status"]} |')
markdown = """# 혼합 출처 절차 드라이런

[0999.html](0999.html)

## ⏱ 30초 요약

효소는 활성화에너지를 낮추지만 평형을 바꾸지 않는다.

### §1 효소

효소는 활성화에너지를 낮춘다.

## ✂️ 여기서 강의가 끊겼습니다

다음 회차 범위는 이 절차 표본에 포함하지 않는다.

## 부록. 문항 ↔ 개념 매핑

| 출처 | 문항 번호 | 질문 요약 | 절 | 상태 |
|---|---:|---|---|---|
| 2강 | 6 | 효소의 잘못된 설명 | §1 효소 | included |

## WEB 문항 매핑

| 출처 | 문항 ID | 질문 요약 | 절 | 상태 |
|---|---|---|---|---|
""" + "\n".join(web_rows) + "\n"
(note_root / "0999.md").write_text(markdown, encoding="utf-8")
print(f"legacy=1 web_active={len(web_items)} web_total={len(entries)} ids=" +
      ",".join(item.get("qid", f'{item["src"]}:{item["n"]}') for item in items))
PY

.venv-question-bank/bin/python scripts/new_note_test.py 0999 \
  --quiz "2강:6" \
  --web-scope "$MIXED_DIR/scope.json" \
  --no-recap \
  --out "$MIXED_DIR/repo/tests/test_note_0999.py"

NOTE_REPO_ROOT="$MIXED_DIR/repo" \
WEB_SCOPE_REPO_ROOT="$PWD" \
.venv-question-bank/bin/python "$MIXED_DIR/repo/tests/test_note_0999.py" -v
```

The first command must report `legacy=1 web_active=1 web_total=17` with IDs
`2강:6,web-20260917-ch01:q02`. The generated suite must pass 13 tests: the
legacy numeric mapping and QUIZ item remain present, the active web qid appears
once, and the WEB table accounts for all 17 original bank IDs.

## PDF-only current-template fallback sample

This separate sample checks a true no-bank chapter path with the current
strict JSON marker template. It uses standard `python3`, the legacy numeric
mapping format, and `--quiz` without importing the web-bank modules. It is a
procedure check, not a complete chapter-2 guide.

```bash
PDF_ONLY_DIR="$(mktemp -d)"
export PDF_ONLY_DIR
export NOTE_SOURCE_ROOT="$PWD"

python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["NOTE_SOURCE_ROOT"]).resolve()
tmp = Path(os.environ["PDF_ONLY_DIR"]).resolve()
note_root = tmp / "repo" / "정리노트"
test_root = tmp / "repo" / "tests"
note_root.mkdir(parents=True)
test_root.mkdir(parents=True)

legacy = [{
    "n": 6,
    "q": "효소에 대한 설명 중 틀린 것은?",
    "opts": ["비가역 반응을 가역 반응으로 만든다.", "활성화에너지를 낮춘다."],
    "answer": 0,
    "why": "효소는 활성화에너지를 낮추지만 반응의 평형은 바꾸지 않는다.",
    "trap": {"1": "활성화에너지를 낮추는 것은 효소의 올바른 기능이다."},
    "keyNote": "2강 합본 Q6 감사를 반영한 PDF-only 절차 표본",
    "ref": "§1 효소",
}]
template = (root / "정리노트/_template.html").read_text(encoding="utf-8")
start = "/* QUESTION-DATA-START */"
end = "/* QUESTION-DATA-END */"
payload = (start + "\nconst META = " +
           json.dumps({"date": "0998", "title": "PDF-only 절차 드라이런"}, ensure_ascii=False) +
           ";\nconst QUIZ = " + json.dumps(legacy, ensure_ascii=False) + ";\n")
html = template[:template.index(start)] + payload + template[template.index(end):]
(note_root / "0998.html").write_text(html, encoding="utf-8")
(note_root / "0998.md").write_text("""# PDF-only 절차 드라이런

[0998.html](0998.html)

## ⏱ 30초 요약

효소는 활성화에너지를 낮추지만 평형을 바꾸지 않는다.

### §1 효소

효소는 활성화에너지를 낮춘다.

## ✂️ 여기서 강의가 끊겼습니다

다음 회차 범위는 이 절차 표본에 포함하지 않는다.

## 부록. 문항 ↔ 개념 매핑

| 문항 번호 | 질문 요약 | 절 | 상태 |
|---:|---|---|---|
| 6 | 효소의 잘못된 설명 | §1 효소 | included |
""", encoding="utf-8")
print("pdf_only=1 ids=6 marker_json=true")
PY

python3 scripts/new_note_test.py 0998 \
  --quiz 6 \
  --no-recap \
  --out "$PDF_ONLY_DIR/repo/tests/test_note_0998.py"

NOTE_REPO_ROOT="$PDF_ONLY_DIR/repo" \
python3 "$PDF_ONLY_DIR/repo/tests/test_note_0998.py" -v
```

The first command must report `pdf_only=1 ids=6 marker_json=true`. The
generated suite must pass 10 tests against the current template and the
single-source numeric mapping, with no web scope or jsonschema dependency.
