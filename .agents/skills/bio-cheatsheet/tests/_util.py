"""스킬 테스트 공통 경로."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = TESTS / "fixtures"
MINI = FIXTURES / "mini"
TEMPLATE = SKILL / "assets" / "cheatsheet-template.html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HAS_CHROME = Path(CHROME).exists()
HAS_POPPLER = bool(shutil.which("pdfinfo") and shutil.which("pdffonts"))
sys.path.insert(0, str(SCRIPTS))
