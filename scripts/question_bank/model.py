"""Load and validate the version 1 web assessment question-bank contract."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "웹과제/question-bank.schema.json"


def canonical_digest(value: object) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def resolve_local(base: Path, relative: str) -> Path:
    base = base.resolve()
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError("absolute path not allowed: " + relative)

    result = base
    for component in candidate.parts:
        if component == "..":
            result = result.parent.resolve()
            if not result.is_relative_to(base):
                raise ValueError("path outside root: " + relative)
            continue
        matches: list[Path] = []
        if result.is_dir():
            normalized = unicodedata.normalize("NFC", component)
            try:
                matches = [
                    entry
                    for entry in result.iterdir()
                    if unicodedata.normalize("NFC", entry.name) == normalized
                ]
            except OSError:
                matches = []
        if len(matches) > 1:
            raise ValueError("ambiguous normalized path component: " + component)
        result = matches[0] if matches else result / component
        result = result.resolve()
        if not result.is_relative_to(base):
            raise ValueError("path outside root: " + relative)
    return result


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _without_review(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "review"}


def _sources_by_id(bank: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {source["id"]: source for source in bank["sources"]}


def _assets_by_id(bank: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {asset["id"]: asset for asset in bank["assets"]}


def asset_payload(
    bank: dict[str, Any], asset: dict[str, Any], base: Path
) -> dict[str, Any]:
    sources = _sources_by_id(bank)
    source_hashes = {
        source_id: _file_digest(resolve_local(base, sources[source_id]["path"]))
        for source_id in asset["source_ids"]
    }
    return {
        "asset": _without_review(asset),
        "source_sha256": source_hashes,
        "exam_sha256": _file_digest(resolve_local(base, asset["exam"]["path"])),
        "explained_sha256": _file_digest(
            resolve_local(base, asset["explained"]["path"])
        ),
    }


def question_payload(
    bank: dict[str, Any],
    question: dict[str, Any],
    base: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = REPO_ROOT if repo_root is None else repo_root
    sources = _sources_by_id(bank)
    assets = _assets_by_id(bank)
    source_hashes = {
        source_id: _file_digest(resolve_local(base, sources[source_id]["path"]))
        for source_id in question["source_ids"]
    }
    figure_ids = [
        block["asset_id"]
        for block in question["original"]["content"]
        if block["type"] == "figure"
    ]
    asset_hashes = {
        asset_id: {
            "exam": _file_digest(
                resolve_local(base, assets[asset_id]["exam"]["path"])
            ),
            "explained": _file_digest(
                resolve_local(base, assets[asset_id]["explained"]["path"])
            ),
        }
        for asset_id in figure_ids
    }
    evidence_paths = {
        evidence["path"]
        for requirement in question["analysis"]["requirements"]
        for evidence in requirement["evidence"]
    }
    evidence_hashes = {
        path: _file_digest(resolve_local(repo_root, path))
        for path in sorted(evidence_paths)
    }
    return {
        "question": _without_review(question),
        "source_sha256": source_hashes,
        "asset_sha256": asset_hashes,
        "evidence_sha256": evidence_hashes,
    }


def _schema_errors(bank: object) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(bank), key=lambda error: str(error.absolute_path))
    return [
        "/" + "/".join(map(str, error.absolute_path)) + ": " + error.message
        for error in errors
    ]


def _duplicates(values: list[Any]) -> set[Any]:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _checked_file(
    errors: list[str],
    root: Path,
    relative: str,
    label: str,
    expected_hash: str | None = None,
    required_directory: str | None = None,
) -> Path | None:
    try:
        path = resolve_local(root, relative)
        required_root = (
            resolve_local(root, required_directory)
            if required_directory is not None
            else None
        )
    except ValueError as error:
        errors.append(f"{label}: {error}")
        return None
    if required_root is not None:
        if not path.is_relative_to(required_root):
            errors.append(f"{label} must be under {required_directory}/: {relative}")
            return None
    if not path.is_file():
        errors.append(f"{label} file missing: {relative}")
        return None
    if expected_hash is not None and _file_digest(path) != expected_hash:
        errors.append(f"{label} hash mismatch: {relative}")
    return path


def _review_errors(
    review: dict[str, Any],
    payload: dict[str, Any] | None,
    label: str,
    complete: bool,
) -> list[str]:
    errors: list[str] = []
    status = review["status"]
    if status == "verified":
        if review["payload_sha256"] is None:
            errors.append(f"{label} verified review requires payload_sha256")
        elif payload is not None and review["payload_sha256"] != canonical_digest(payload):
            errors.append(f"{label} review hash mismatch")
        if review["notes"] is None:
            errors.append(f"{label} verified review requires notes")
    if complete and status != "verified":
        errors.append(f"{label} review is {status}; complete requires verified")
    return errors


def validate_bank(
    bank: dict[str, Any],
    base: Path,
    *,
    complete: bool = False,
    repo_root: Path | None = None,
) -> list[str]:
    schema_errors = _schema_errors(bank)
    if schema_errors:
        return schema_errors

    base = base.resolve()
    repo_root = REPO_ROOT if repo_root is None else repo_root.resolve()
    errors: list[str] = []
    sources = bank["sources"]
    assets = bank["assets"]
    questions = bank["questions"]

    source_ids = [source["id"] for source in sources]
    asset_ids = [asset["id"] for asset in assets]
    question_ids = [question["id"] for question in questions]
    question_numbers = [question["number"] for question in questions]
    for duplicate in sorted(_duplicates(source_ids)):
        errors.append(f"duplicate source id: {duplicate}")
    for duplicate in sorted(_duplicates(asset_ids)):
        errors.append(f"duplicate asset id: {duplicate}")
    for duplicate in sorted(_duplicates(question_ids)):
        errors.append(f"duplicate question id: {duplicate}")
    for duplicate in sorted(_duplicates(question_numbers)):
        errors.append(f"duplicate question number: {duplicate}")

    expected_numbers = set(range(1, bank["assessment"]["expected_question_count"] + 1))
    if set(question_numbers) != expected_numbers:
        errors.append(
            "question numbers must equal 1..expected_question_count: "
            f"got {sorted(set(question_numbers))}"
        )

    source_by_id = _sources_by_id(bank)
    asset_by_id = _assets_by_id(bank)
    known_source_ids = set(source_by_id)
    known_asset_ids = set(asset_by_id)
    referenced_source_ids: set[str] = set()

    for source_id in bank["assessment"]["evidence_source_ids"]:
        referenced_source_ids.add(source_id)
        if source_id not in known_source_ids:
            errors.append(f"unknown assessment source id: {source_id}")

    valid_source_files: set[str] = set()
    for source in sources:
        if _checked_file(
            errors,
            base,
            source["path"],
            f"source {source['id']}",
            source["sha256"],
            "raw",
        ) is not None:
            valid_source_files.add(source["id"])

    valid_asset_files: set[str] = set()
    for asset in assets:
        label = f"asset {asset['id']}"
        for source_id in asset["source_ids"]:
            referenced_source_ids.add(source_id)
            if source_id not in known_source_ids:
                errors.append(f"{label} has unknown source id: {source_id}")
        exam = _checked_file(
            errors,
            base,
            asset["exam"]["path"],
            f"{label} exam",
            asset["exam"]["sha256"],
            "image",
        )
        explained = _checked_file(
            errors,
            base,
            asset["explained"]["path"],
            f"{label} explained",
            asset["explained"]["sha256"],
            "image",
        )
        if exam is not None and explained is not None:
            valid_asset_files.add(asset["id"])

        payload = None
        if (
            set(asset["source_ids"]) <= valid_source_files
            and asset["id"] in valid_asset_files
        ):
            payload = asset_payload(bank, asset, base)
        errors.extend(_review_errors(asset["review"], payload, label, complete))

    assessment_id = bank["assessment"]["id"]
    for question in questions:
        label = f"question {question['id']}"
        expected_id = f"{assessment_id}:q{question['number']:02d}"
        if question["id"] != expected_id:
            errors.append(f"{label} id must be {expected_id}")

        for source_id in question["source_ids"]:
            referenced_source_ids.add(source_id)
            if source_id not in known_source_ids:
                errors.append(f"{label} has unknown question source id: {source_id}")

        option_ids = [option["id"] for option in question["original"]["options"]]
        for duplicate in sorted(_duplicates(option_ids)):
            errors.append(f"{label} has duplicate option id: {duplicate}")
        known_option_ids = set(option_ids)

        statement_ids = [
            statement["id"]
            for block in question["original"]["content"]
            if block["type"] == "statements"
            for statement in block["items"]
        ]
        for duplicate in sorted(_duplicates(statement_ids)):
            errors.append(f"{label} has duplicate statement id: {duplicate}")

        figure_ids = [
            block["asset_id"]
            for block in question["original"]["content"]
            if block["type"] == "figure"
        ]
        for asset_id in figure_ids:
            if asset_id not in known_asset_ids:
                errors.append(f"{label} has unknown figure asset id: {asset_id}")
                continue
            missing_asset_sources = set(asset_by_id[asset_id]["source_ids"]) - set(
                question["source_ids"]
            )
            if missing_asset_sources:
                errors.append(
                    f"{label} asset source_ids must be included in question source_ids: "
                    f"{sorted(missing_asset_sources)}"
                )

        observations = question["observations"]
        selected_option_id = observations["selected_option_id"]
        if selected_option_id is not None and selected_option_id not in known_option_ids:
            errors.append(f"{label} selected_option_id is not an option: {selected_option_id}")
        selected_source_id = observations["selected_source_id"]
        if selected_source_id is not None and selected_source_id not in question["source_ids"]:
            errors.append(
                f"{label} selected_source_id must be in question source_ids: "
                f"{selected_source_id}"
            )
        official_answer = observations["official_answer"]
        if official_answer is not None:
            for option_id in official_answer["option_ids"]:
                if option_id not in known_option_ids:
                    errors.append(f"{label} official answer has unknown option: {option_id}")
            for source_id in official_answer["source_ids"]:
                referenced_source_ids.add(source_id)
                if source_id not in known_source_ids:
                    errors.append(f"{label} official answer has unknown source: {source_id}")

        analysis = question["analysis"]
        answer_option_id = analysis["answer_option_id"]
        if answer_option_id is not None and answer_option_id not in known_option_ids:
            errors.append(f"{label} answer_option_id is not an option: {answer_option_id}")
        if analysis["answer_status"] == "unresolved":
            if answer_option_id is not None or analysis["grading"] != "unresolved":
                errors.append(f"{label} unresolved answer must have null option and unresolved grading")
            if analysis["also_accept"]:
                errors.append(f"{label} unresolved answer requires empty also_accept")
            if complete:
                errors.append(f"{label} unresolved answer blocks complete validation")
        elif answer_option_id is None or analysis["grading"] == "unresolved":
            errors.append(f"{label} reasoned answer requires an option and resolved grading")

        also_accept = set(analysis["also_accept"])
        unknown_alternates = also_accept - known_option_ids
        if unknown_alternates:
            errors.append(f"{label} also_accept has unknown options: {sorted(unknown_alternates)}")
        if answer_option_id in also_accept:
            errors.append(f"{label} answer_option_id cannot also appear in also_accept")
        if analysis["grading"] == "single" and also_accept:
            errors.append(f"{label} single grading requires empty also_accept")
        if analysis["grading"] == "ambiguous" and not any(
            issue["kind"] in {"wording", "source-conflict"}
            for issue in analysis["issues"]
        ):
            errors.append(f"{label} ambiguous grading requires an explanatory issue")

        requirement_ids = [item["id"] for item in analysis["requirements"]]
        for duplicate in sorted(_duplicates(requirement_ids)):
            errors.append(f"{label} has duplicate requirement id: {duplicate}")
        known_requirement_ids = set(requirement_ids)
        evidence_files_valid = True
        for requirement in analysis["requirements"]:
            for evidence in requirement["evidence"]:
                if _checked_file(
                    errors,
                    repo_root,
                    evidence["path"],
                    f"{label} evidence",
                ) is None:
                    evidence_files_valid = False

        diagnostic_ids = set(analysis["option_diagnostics"])
        if diagnostic_ids != known_option_ids:
            errors.append(
                f"{label} diagnostic ids must exactly match option ids: "
                f"got {sorted(diagnostic_ids)}"
            )
        intended_answers = (
            set()
            if analysis["answer_status"] == "unresolved"
            else ({answer_option_id} | also_accept)
        )
        for option_id, diagnostic in analysis["option_diagnostics"].items():
            unknown_requirements = set(diagnostic["requirement_ids"]) - known_requirement_ids
            if unknown_requirements:
                errors.append(
                    f"{label} diagnostic {option_id} has unknown requirement ids: "
                    f"{sorted(unknown_requirements)}"
                )
            expected_is_answer = None if analysis["answer_status"] == "unresolved" else option_id in intended_answers
            if diagnostic["is_answer"] is not expected_is_answer:
                errors.append(
                    f"{label} diagnostic {option_id} is_answer must be {expected_is_answer}"
                )

        for issue in analysis["issues"]:
            for source_id in issue["source_ids"]:
                referenced_source_ids.add(source_id)
                if source_id not in known_source_ids:
                    errors.append(f"{label} issue has unknown source id: {source_id}")
        if question["review"]["status"] == "verified" and any(
            issue["kind"] in {"unreadable", "figure-incomplete"}
            for issue in analysis["issues"]
        ):
            errors.append(f"{label} cannot be verified with blocking issues")

        payload = None
        if (
            set(question["source_ids"]) <= valid_source_files
            and set(figure_ids) <= valid_asset_files
            and evidence_files_valid
        ):
            payload = question_payload(
                bank, question, base, repo_root=repo_root
            )
        errors.extend(_review_errors(question["review"], payload, label, complete))

    for source_id in sorted(known_source_ids - referenced_source_ids):
        errors.append(f"source id is never referenced: {source_id}")

    return errors


def load_bank(
    path: Path,
    *,
    complete: bool = False,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    path = Path(path)
    try:
        bank = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load question bank {path}: {error}") from error
    errors = validate_bank(
        bank, path.parent, complete=complete, repo_root=repo_root
    )
    if errors:
        raise ValueError(f"invalid question bank {path}:\n" + "\n".join(errors))
    return bank
