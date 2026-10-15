"""Synthetic exam inputs with TEST ONLY review approvals."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EXAM=ROOT/'.agents/skills/bio-exam-forecast'
# Tests share the production import contract; no helpers module collision.
sys.path.insert(0,str(EXAM/'scripts'))
spec=importlib.util.spec_from_file_location('_exam_test_fixtures',EXAM/'tests/exam_fixtures.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
import pytest
@pytest.fixture
def repo(tmp_path):return fixtures.make_repo(tmp_path/'repo')
@pytest.fixture
def approved_exam(repo):
 p=fixtures.make_pack(repo);fixtures.approve_questions(p);return p
