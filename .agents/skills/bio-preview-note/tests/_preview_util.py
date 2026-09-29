"""예습 스킬 테스트 공통 경로."""

from __future__ import annotations

from pathlib import Path
import sys

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = TESTS / "fixtures"
MINI_RUN = FIXTURES / "mini-run"
REPO = SKILL.parents[2]  # <repo>/.agents/skills/bio-preview-note
REVIEW_SKILL = SKILL.parent / "bio-review-pack"
sys.path.insert(0, str(SCRIPTS))
