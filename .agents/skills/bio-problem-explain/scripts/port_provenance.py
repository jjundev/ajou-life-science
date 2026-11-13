"""Regenerate assets/port-provenance.json against the pinned ds-problem-explain source (maintenance only)."""
import argparse, hashlib, json, subprocess
import os
from pathlib import Path
from bio_web_assets import REPO as BIO_REPO, SHARED_DIR

SKILL = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/jjundev/ajou-jagual.git'
COMMIT = 'd631a5a573a32c9406b139e319bc9c7c2d328098'
SOURCE = '/Users/hyunjun_macbook_pro/Documents/Univ/자구알'
SOURCE_SKILL = '.agents/skills/ds-problem-explain'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_git(source):
    result = subprocess.run(['git', '-C', str(source), 'rev-parse', '--git-dir'], capture_output=True)
    if result.returncode != 0:
        raise SystemExit(f'git 저장소가 아니거나 경로가 잘못됐어요: {source}')


def source_bytes(source, relative):
    result = subprocess.run(['git', '-C', str(source), 'show', f'{COMMIT}:{SOURCE_SKILL}/{relative}'], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def build(source):
    check_git(source)
    files = []
    bundle = BIO_REPO / SHARED_DIR
    paths = sorted(SKILL.rglob('*')) + sorted(bundle.rglob('*'))
    for path in paths:
        if not path.is_file():
            continue
        relative = Path(os.path.relpath(path, SKILL)).as_posix()
        upstream = ('assets/vendor/' + path.relative_to(bundle).as_posix()
                    if path.is_relative_to(bundle) else relative)
        if '__pycache__' in path.parts or relative == 'assets/port-provenance.json':
            continue
        destination = path.read_bytes()
        original = source_bytes(source, upstream)
        if original is None:
            source_path, source_hash, reason = None, None, 'local addition'
        else:
            source_path, source_hash = upstream, sha(original)
            reason = 'unchanged pinned copy' if source_hash == sha(destination) else 'biology course adaptation'
        files.append({'source_path': source_path, 'source_sha256': source_hash, 'destination': relative,
                      'destination_sha256': sha(destination), 'change_reason': reason})
    return {'source_repository': REPO, 'source_commit': COMMIT, 'files': files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=SOURCE, help='ajou-jagual git checkout')
    args = parser.parse_args()
    out = SKILL / 'assets/port-provenance.json'
    out.write_text(json.dumps(build(Path(args.source)), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
