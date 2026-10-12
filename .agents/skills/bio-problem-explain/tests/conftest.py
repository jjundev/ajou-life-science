import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import pytest

@pytest.fixture(autouse=True)
def synthetic_repo(request, tmp_path):
    # Tests never depend on or write real coursework; source adapter has a separate read-only probe.
    from helpers import source_file
    if hasattr(request.module, 'ROOT'):
        repo=tmp_path/'fixtures'
        source_file(repo)
        request.module.ROOT=repo
