"""Derive and validate the complete source-qualified question universe."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from coverage_model import file_digest

def _expand_numbers(text: str) -> list[int]:
    values = []
    for token in re.split(r"[·,\s]+", text.strip()):
        if not token:
            continue
        match = re.fullmatch(r"(\d+)[–—~\-](\d+)", token)
        if match:
            start, end = map(int, match.groups())
            values.extend(range(start, end + 1))
        elif token.isdigit():
            values.append(int(token))
    return values

def _qualified_ids(text: str) -> list[str]:
    result = []
    for match in re.finditer(r"(\d+강)\s+([0-9][0-9\s,·–—~\-]*)", text):
        source, numbers = match.groups()
        result.extend(f"{source}:{number}" for number in _expand_numbers(numbers))
    return result

def extract_question_scope(markdown: str) -> dict[str, dict]:
    questions = {}
    appendix = markdown.split("## 부록. 문항 ↔ 개념 매핑", 1)
    if len(appendix) == 2:
        for source, number in re.findall(r"^\|\s*(\d+강)\s*\|\s*(\d+)\s*\|", appendix[1], re.M):
            ident = f"{source}:{int(number)}"
            questions[ident] = {"id": ident, "status": "included", "source_locator": "문항 매핑표"}
    review = re.search(r"## ⏪ 지난 회차 복습.*?(?=\n## )", markdown, re.S)
    if review:
        for line in review.group(0).splitlines():
            if "관련 문항" in line:
                for ident in _qualified_ids(line.split("관련 문항", 1)[1].lstrip(":： ")):
                    questions[ident] = {"id": ident, "status": "review", "source_locator": "지난 회차 복습"}
    for line in markdown.splitlines():
        if line.lstrip().startswith("> 보류:"):
            reason = "정리노트의 후속 범위 보류: " + line.split("보류:", 1)[1].strip()
            for ident in _qualified_ids(line.split("보류:", 1)[1]):
                questions[ident] = {
                    "id": ident, "status": "deferred",
                    "source_locator": "보류 목록", "reason": reason,
                }
    return questions

def apply_overrides(base: dict[str, dict], overrides: list[dict]) -> tuple[dict[str, dict], list[str]]:
    final = {ident: dict(item) for ident, item in base.items()}
    errors, seen = [], set()
    for override in overrides:
        if not isinstance(override, dict):
            errors.append("override must be an object")
            continue
        ident = override.get("id")
        if ident in seen:
            errors.append(f"duplicate override: {ident}")
        seen.add(ident)
        if ident not in final:
            errors.append(f"override references unknown question: {ident}")
            continue
        if override.get("from") != final[ident]["status"]:
            errors.append(f"override source status mismatch: {ident}")
            continue
        if override.get("to") not in {"included", "review", "deferred"}:
            errors.append(f"invalid override target: {ident}")
            continue
        evidence = override.get("evidence")
        valid_evidence = isinstance(evidence, dict) and all(
            isinstance(evidence.get(key), str) and evidence[key].strip()
            for key in ("source_path", "page", "quote")
        )
        if not isinstance(override.get("reason"), str) or not override["reason"].strip() or not valid_evidence:
            errors.append(f"override lacks evidence: {ident}")
            continue
        final[ident].update(
            status=override["to"],
            override_reason=override["reason"],
            override_evidence=evidence,
        )
    return final, errors

def scope_digest(lock: dict) -> str:
    payload = {key: value for key, value in lock.items() if key != "scope_sha256"}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def _as_map(items: object) -> tuple[dict[str, dict], list[str]]:
    if not isinstance(items, list):
        return {}, ["question collection must be a list"]
    result, errors = {}, []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("invalid scoped question")
            continue
        if item["id"] in result:
            errors.append(f"duplicate scoped question: {item['id']}")
        result[item["id"]] = item
    return result, errors

def validate_scope_lock(lock: object, note_path: Path, *, lock_path: Path | None = None) -> list[str]:
    if not isinstance(lock, dict) or lock.get("schema_version") not in (1, 2):
        return ["invalid question scope lock"]
    errors = []
    source = lock.get("source")
    try:
        digest = file_digest(note_path)
        if not isinstance(source, dict) or source.get("sha256") != digest:
            errors.append("question scope source hash mismatch")
        extracted = extract_question_scope(note_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        return [f"cannot read scope source: {error}"]
    if lock['schema_version'] == 2:
        if lock_path is None:
            return ['scope v2 requires lock_path']
        try:
            from repo_bootstrap import enable_repo_imports
            root = enable_repo_imports()
            from scripts.question_bank.scope import load_web_scope, file_hash
            web_source = lock['web_scope']
            if (not isinstance(web_source, dict)
                    or not isinstance(web_source.get('path'), str)
                    or Path(web_source['path']).is_absolute()):
                raise ValueError('web scope lock path must be relative')
            manifest = (lock_path.parent / web_source['path']).resolve()
            if file_hash(manifest) != lock['web_scope']['sha256']:
                errors.append('web scope source hash mismatch')
            entries, _ = load_web_scope(manifest, root)
            paths = list(dict.fromkeys(Path(e['bank_path']) for e in entries))
            import os
            expected_banks = [{'path': os.path.relpath(p, lock_path.parent.resolve()), 'sha256': file_hash(p)} for p in paths]
            if lock.get('banks') != expected_banks:
                errors.append('question scope bank sources mismatch')
            for entry in entries:
                if entry['id'] in extracted:
                    errors.append('question id collision: ' + entry['id'])
                extracted[entry['id']] = {k: v for k, v in entry.items() if k != 'bank_path'}
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            return errors + [f'cannot load web scope: {error}']
    base, base_errors = _as_map(lock.get("base_questions"))
    final, final_errors = _as_map(lock.get("questions"))
    errors.extend(base_errors + final_errors)
    if base != extracted:
        errors.append("question scope base does not match source")
    applied, override_errors = apply_overrides(base, lock.get("overrides", []))
    errors.extend(override_errors)
    final_matches = set(final) == set(applied) and all(
        final[ident].get("status") == item.get("status")
        and final[ident].get("source_locator") == item.get("source_locator")
        and (lock['schema_version'] == 1 or all(final[ident].get(k) == v for k, v in item.items()))
        for ident, item in applied.items()
    )
    if not final_matches:
        errors.append("question scope final set does not match overrides")
    if lock.get("scope_sha256") != scope_digest(lock):
        errors.append("question scope hash mismatch")
    return errors

def validate_scope_audit(lock: dict) -> list[str]:
    """Require source-grounded format and knowledge needs before completion."""
    errors = []
    for item in lock.get("questions", []):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        ident = item["id"]
        if item.get("status") == "deferred":
            reason = item.get("override_reason") or item.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"scope deferred reason missing: {ident}")
            continue
        if item.get("audit_status") != "confirmed":
            errors.append(f"scope question audit pending: {ident}")
            continue
        if item.get("format") not in {"multiple_choice", "short_answer"}:
            errors.append(f"scope question format missing: {ident}")
        if (
            item.get("format") == "multiple_choice"
            and (type(item.get("option_count")) is not int or item["option_count"] < 2)
        ):
            errors.append(f"scope question option count missing: {ident}")
        if item.get("grading") not in {"single", "ambiguous", "rubric"}:
            errors.append(f"scope question grading missing: {ident}")
        requirements = item.get("requirements")
        if not isinstance(requirements, list) or not requirements:
            errors.append(f"scope question requirements missing: {ident}")
        evidence = item.get("source_evidence")
        if not isinstance(evidence, dict) or any(
            not isinstance(evidence.get(key), str) or not evidence[key].strip()
            for key in ("source_path", "page", "quote")
        ):
            errors.append(f"scope question evidence missing: {ident}")
    return errors

def validate_question_coverage(
    data: dict, scope: dict[str, dict], allow_missing: bool = False
) -> list[str]:
    declared = {
        item.get("id"): item
        for item in data.get("inventory", {}).get("questions", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    missing, unexpected = set(scope) - set(declared), set(declared) - set(scope)
    errors = []
    if (missing and not allow_missing) or unexpected:
        errors.append(f"question universe mismatch: {len(missing)} missing, {len(unexpected)} unexpected")
        if not allow_missing:
            errors.extend(f"missing question: {ident}" for ident in sorted(missing))
        errors.extend(f"unexpected question: {ident}" for ident in sorted(unexpected))
    for ident in sorted(set(scope) & set(declared)):
        if declared[ident].get("status") != scope[ident].get("status"):
            errors.append(f"question scope status mismatch: {ident}")
        for field in ("format", "grading", "option_count"):
            if field in scope[ident] and declared[ident].get(field) != scope[ident].get(field):
                errors.append(f"question {field} mismatch: {ident}")
        if "requirements" in scope[ident] and set(declared[ident].get("requirements", [])) != set(scope[ident]["requirements"]):
            errors.append(f"question requirements mismatch: {ident}")
    return errors
