"""Pinned Pretendard and KaTeX assets shared by the biology HTML generators."""

import hashlib
import json
import os
import unicodedata
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[4]
SHARED_DIR = Path('복습노트/_shared/pretendard-1.3.9_katex-0.16.11')


def asset_url(repo: Path, html_dir: Path) -> str:
    relative = Path(os.path.relpath(repo / SHARED_DIR, html_dir)).as_posix()
    return quote(unicodedata.normalize('NFC', relative), safe='/')


def verified_files(repo: Path, directory: Path = SHARED_DIR) -> dict[str, str]:
    """Return the verified bytes as a mapping of repo-relative paths to hashes."""
    if directory.parent != SHARED_DIR.parent:
        raise ValueError(f'공용 자원 폴더 경로 오류: {directory}')
    bundle = repo / directory
    if not bundle.resolve().is_relative_to(repo.resolve()) or bundle.is_symlink():
        raise ValueError(f'공용 자원 폴더 경로 오류: {directory}')
    provenance = bundle / 'provenance.json'
    try:
        raw = provenance.read_bytes()
        pinned = json.loads(raw)['files']
        if not isinstance(pinned, dict) or not pinned:
            raise ValueError('files')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f'공용 자원 기록 누락 또는 손상: {provenance}') from exc

    files = {(directory / provenance.name).as_posix(): hashlib.sha256(raw).hexdigest()}
    for name, expected in sorted(pinned.items()):
        path = bundle / name
        relative = directory / name
        if not path.resolve().is_relative_to(bundle.resolve()) or not path.is_file():
            raise ValueError(f'공용 자원 누락 또는 잘못된 경로: {relative}')
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ValueError(f'공용 자원 읽기 실패: {relative}') from exc
        if actual != expected:
            raise ValueError(f'공용 자원 변경: {relative}')
        files[relative.as_posix()] = actual
    return files
