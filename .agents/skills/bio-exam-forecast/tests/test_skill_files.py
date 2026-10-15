"""Check discoverability and packaged dependency paths, not prose keywords."""
from pathlib import Path
import re
from exam_fixtures import ROOT

def test_skill_registered_and_dependencies_resolve():
 skill=ROOT/'.agents/skills/bio-exam-forecast';link=ROOT/'.claude/skills/bio-exam-forecast'
 assert (skill/'SKILL.md').is_file() and link.is_symlink() and link.resolve()==skill.resolve()
 text=(skill/'SKILL.md').read_text()
 for ref in re.findall(r'\]\(([^)]+)\)',text):
  if not ref.startswith(('http:','https:','#')):assert (skill/ref).exists(),ref
