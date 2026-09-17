"""Read an independently authored scope without shrinking its source universe."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

from .model import load_bank, resolve_local


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_bank_path(manifest: Path, relative: str, repo_root: Path) -> Path:
    """Bank paths use manifest.parent, permitting ../ within the repository."""
    if not _text(relative) or Path(relative).is_absolute():
        raise ValueError('bank path must be relative')
    # Normalize the lexical base first, then use the shared Unicode/symlink guard.
    relative_to_root = os.path.relpath(os.path.normpath(manifest.parent / relative), repo_root)
    return resolve_local(repo_root, relative_to_root)


def section_names(markdown: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$', markdown, re.M)}


def section_anchor(section: str) -> str:
    """GitHub-style heading fragment used by relative Markdown links."""
    return re.sub(r'[^\w\- ]', '', section.lower()).replace(' ', '-')


def reference_href(ref: dict, repo_root: Path, output_dir: Path) -> str:
    path = resolve_local(repo_root, ref['path'])
    relative = Path(os.path.relpath(path, output_dir.resolve())).as_posix()
    return quote(relative, safe='/.-_') + '#' + quote(section_anchor(ref['section']))


def assert_same_ids(expected: set[str], actual: list[str]) -> None:
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError(f'question universe mismatch: missing={sorted(expected-set(actual))}, '
                         f'extra={sorted(set(actual)-expected)}')


def load_web_scope(path: Path, repo_root: Path) -> tuple[list[dict], dict[str, dict]]:
    path, repo_root = Path(path).resolve(), Path(repo_root).resolve()
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'banks'}
            or type(manifest['schema_version']) is not int or manifest['schema_version'] != 1
            or not isinstance(manifest['banks'], list) or not manifest['banks']):
        raise ValueError('invalid web scope manifest')
    entries, banks = [], {}
    for row in manifest['banks']:
        if not isinstance(row, dict) or set(row) != {'path', 'sha256', 'questions'}:
            raise ValueError('invalid web scope bank entry')
        bank_path = resolve_bank_path(path, row['path'], repo_root)
        if file_hash(bank_path) != row['sha256']:
            raise ValueError('web scope bank hash mismatch: ' + str(bank_path))
        # Universe checks precede complete-review checks, including an empty list.
        bank = load_bank(bank_path, repo_root=repo_root)
        questions = row['questions']
        if not isinstance(questions, list) or any(
                not isinstance(e, dict) or not _text(e.get('id')) for e in questions):
            raise ValueError('invalid web scope questions')
        assert_same_ids({q['id'] for q in bank['questions']}, [e['id'] for e in questions])
        bank_id = bank['assessment']['id']
        if bank_id in banks:
            raise ValueError('duplicate bank id: ' + bank_id)
        for entry in questions:
            if set(entry) != {'id', 'status', 'reason', 'prerequisite', 'refs'}:
                raise ValueError('invalid scope question fields: ' + entry['id'])
            status = entry['status']
            if status not in ('included', 'review', 'deferred'):
                raise ValueError('invalid scope status: ' + str(status))
            for field in ('reason', 'prerequisite'):
                if entry[field] is not None and not _text(entry[field]):
                    raise ValueError('invalid scope ' + field + ': ' + entry['id'])
                if status == 'deferred' and not _text(entry[field]):
                    raise ValueError('deferred requires ' + field + ': ' + entry['id'])
            refs = entry['refs']
            if not isinstance(refs, list) or (status != 'deferred' and not refs):
                raise ValueError('active scope question requires refs: ' + entry['id'])
            for ref in refs:
                if not isinstance(ref, dict) or set(ref) != {'path', 'section'} or not all(_text(v) for v in ref.values()):
                    raise ValueError('invalid scope ref: ' + entry['id'])
                source = resolve_local(repo_root, ref['path'])
                if ref['section'] not in section_names(source.read_text(encoding='utf-8')):
                    raise ValueError('scope reference section missing: ' + ref['section'])
            entries.append(dict(deepcopy(entry), bank_id=bank_id, bank_path=str(bank_path)))
        banks[bank_id] = load_bank(bank_path, complete=True, repo_root=repo_root)
    return entries, banks


def protect_paths(output: Path, inputs: list[Path]) -> None:
    for path in inputs:
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError('output cannot overwrite an input file: ' + str(output))
