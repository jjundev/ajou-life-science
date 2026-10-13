import json, shutil, subprocess, sys
from pathlib import Path
from mpe_source import sha256

S=Path(__file__).resolve().parents[1]

def test_install_has_no_ml_runtime_dependency(tmp_path):
    copied=tmp_path/'skill';shutil.copytree(S,copied,ignore=shutil.ignore_patterns('__pycache__'))
    result=subprocess.run([sys.executable,str(copied/'scripts/mpe_cli.py'),'--help'],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert 'extract' in result.stdout and 'publish' in result.stdout

def test_claude_link_and_provenance():
    repo=S.parents[2];link=repo/'.claude/skills/bio-problem-explain'
    assert link.is_symlink() and link.resolve()==S.resolve()
    data=json.loads((S/'assets/port-provenance.json').read_text())
    assert data['source_commit']=='d631a5a573a32c9406b139e319bc9c7c2d328098'
    for entry in data['files']:
        assert sha256(S/entry['destination'])==entry['destination_sha256']
        if entry['destination'].startswith('assets/') and entry['source_path'] and entry['change_reason']=='unchanged pinned copy':
            assert entry['source_sha256']==entry['destination_sha256']

import re

DOCS=[S/'SKILL.md',*sorted((S/'references').glob('*.md'))]
SECTIONS=('understand','recall','start','solve','verify','pitfall','retry')

def test_frontmatter():
    text=(S/'SKILL.md').read_text(encoding='utf-8')
    match=re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n',text)
    assert match
    name,description=match[1],match[2]
    assert name=='bio-problem-explain'
    for word in ('생명과학','문제설명','/bio-problem-explain'):
        assert word in description
    assert len(description)<=1024
    if ': ' in description:
        assert description.startswith('"') and description.endswith('"')

def test_no_ds_leftovers():
    pattern=re.compile(r'자료구조|자구알|강의록|from_the_past|printf|C 코드|ds-problem-explain|ds-review-pack|Codex 패널')
    for path in DOCS:
        found=pattern.findall(path.read_text(encoding='utf-8'))
        assert not found,(path.name,found)

def test_bio_sources_named():
    text=(S/'SKILL.md').read_text(encoding='utf-8')
    for needle in ('강의노트/','교과서/생명과학_기초와_응용_2판/','23, 24 소스/','웹과제/','.pack/key-check.md','all'):
        assert needle in text,needle

def test_authoring_bio_rules():
    text=(S/'references/authoring.md').read_text(encoding='utf-8')
    rows=re.findall(r'^\| (\w+) \|',text,re.M)
    assert [r for r in rows if r in SECTIONS]==list(SECTIONS)
    for needle in ('보기','ㄱㄴㄷ','부정형','disputed'):
        assert needle in text,needle

def test_independent_definition():
    text=(S/'references/verification.md').read_text(encoding='utf-8')
    for needle in ('정답을 보지 않은','key-check.md'):
        assert needle in text,needle

def test_printed_key_error_rule():
    for name in ('SKILL.md','references/authoring.md','references/verification.md'):
        text=(S/name).read_text(encoding='utf-8')
        assert '인쇄 정답 오류' in text,name
    text=(S/'references/authoring.md').read_text(encoding='utf-8')
    assert '<strong>인쇄 정답 오류:</strong>' in text

def test_referenced_files_exist():
    text=(S/'SKILL.md').read_text(encoding='utf-8')
    refs=set(re.findall(r'((?:references/[\w.-]+\.md)|(?:scripts/[\w.-]+\.py)|(?:assets/[\w.-]+\.json))',text))
    assert refs
    for ref in refs:
        assert (S/ref).is_file(),ref
