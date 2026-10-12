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
        if entry['destination'].startswith('assets/') and entry['source_path']:
            assert entry['source_sha256']==entry['destination_sha256']
