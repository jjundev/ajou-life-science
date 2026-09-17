"""Locate shared repository code for direct absolute-path skill entrypoints."""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]


def enable_repo_imports() -> Path:
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return REPO_ROOT
