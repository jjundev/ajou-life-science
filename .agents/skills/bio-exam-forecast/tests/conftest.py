import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
from exam_fixtures import make_repo, make_candidates
@pytest.fixture
def repo(tmp_path): return make_repo(tmp_path/'repo')
@pytest.fixture
def topics(repo):
    import json
    return {x['id']:x for x in json.loads((repo/'scope.json').read_text())['topics']}
@pytest.fixture
def six_chapter_candidates(repo): return make_candidates(repo)
