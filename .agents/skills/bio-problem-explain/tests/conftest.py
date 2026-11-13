import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import pytest

@pytest.fixture(autouse=True)
def synthetic_repo(request, tmp_path):
    # Tests never depend on or write real coursework; source adapter has a separate read-only probe.
    from helpers import install_shared_assets, source_file
    if request.module.__name__ not in {'test_source', 'test_forecast_source'}:
        install_shared_assets(tmp_path / 'repo')
    if hasattr(request.module, 'ROOT'):
        repo=tmp_path/'fixtures'
        install_shared_assets(repo)
        source_file(repo)
        request.module.ROOT=repo
