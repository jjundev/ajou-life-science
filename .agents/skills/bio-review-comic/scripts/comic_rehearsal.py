"""Prepare and verify an exact publication candidate without touching live files."""
from dataclasses import dataclass
import json
from pathlib import Path
import re
from threading import Lock

from comic_browser import CHECKER, Inputs, browser_check
from comic_browser_evidence import LINK_RECORD, link_status, passing_views, preview_evidence, require_current_resources, save_link_status
from comic_contract import assets_for, atomic_write, check, jobs_for, load, local, read, state, write_atomic
from comic_links import apply_note_plan, plan_note_links, strip_links
from comic_render import new_version, publication_paths, render, reusable_publication, validate_output
from comic_source import digest, existing

MANIFEST = 'candidate.json'
REPORT = 'report.json'
VERSION_ID = re.compile(r'\d{8}T\d{6}-[0-9a-f]{8}')
RUN_FILES = ('source.json', 'source.html', 'storyboard.json', 'images.json', 'review.json', 'preview.html')


def file_hash(path):
    return digest(path.read_bytes()) if path.exists() else None


def run_hashes(run):
    return {name: digest((run / name).read_bytes()) for name in RUN_FILES}


def final_paths(src):
    repo = existing(src['repo'])
    note, comic, root = publication_paths(src)
    if any(not p.resolve().is_relative_to(repo) for p in (note, comic, root / 'versions')):
        raise ValueError('리허설 발행 대상은 저장소 안에 있어야 합니다.')
    if comic.is_symlink() or (root / 'versions').resolve() != root / 'versions':
        raise ValueError('리허설 발행 대상에 심볼릭 링크를 사용할 수 없습니다.')
    return repo, note, comic, root


def version_for(run, output, root, fingerprint, src, assets):
    path = run / 'publication.json'
    if path.is_file():
        record = read(path)
        version = Path(record['version'])
        if (record.get('fingerprint') == fingerprint and Path(record['html']) == output
                and version.parent == root / 'versions' and VERSION_ID.fullmatch(version.name)
                and version.is_dir() and not version.is_symlink()
                and reusable_publication(record, output, src, assets)
                and record['html_sha256'] == digest(render(run, output, image_root=version))):
            return version
    return new_version(root)


class ResourceSnapshot:
    """Materialize each live resource once; never serve bytes from the live tree."""
    def __init__(self, repo, tree):
        self.repo = repo
        self.tree = tree
        self.hashes = {}
        self.lock = Lock()

    def __call__(self, path):
        with self.lock:
            if path.exists():
                return
            relative = path.relative_to(self.tree).as_posix()
            source = local(self.repo, relative)
            if not source.is_file() or source.resolve().is_relative_to(self.tree.parent):
                raise ValueError('격리본에 복사할 로컬 자원 없음')
            raw = source.read_bytes()
            path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(path, raw)
            self.hashes[relative] = digest(raw)


def candidate_inputs(run, out, manifest, src, book, images):
    tree = local(out, 'tree')
    note, comic, version = (local(tree, manifest[name]) for name in ('note', 'comic', 'version'))
    assets = {key: local(version, item['file']) for key, item in images.items()}
    files = {name: run / name for name in RUN_FILES}
    files.update(note=note, comic=comic, checker=CHECKER, candidate=local(out, MANIFEST))
    note_link_error = None
    try:
        status = 'current' if digest(strip_links(note.read_bytes().decode('utf-8'))) == src['content_sha256'] else 'changed'
    except ValueError as exc:
        status, note_link_error = 'invalid_managed_links', str(exc)
    return Inputs(tree, version, comic, note, book['pages'], files, assets, status, note_link_error)


def rehearse(run, out):
    run, out = Path(run).resolve(), Path(out).resolve()
    result = check(run, 'browser')
    if not result['ready']:
        raise ValueError('모든 페이지가 보류 상태라 리허설할 학습만화가 없습니다.')
    _, src, book = load(run)
    repo, note, comic, root = final_paths(src)
    if out.is_relative_to(note.parent):
        raise ValueError('리허설 --out은 실제 발행 폴더 밖에 두세요.')
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError('리허설 증거는 비어 있는 --out 폴더에 저장하세요.')
    evidence = preview_evidence(run) if src.get('browser_gate_version') else None
    preview = run / 'preview.html'
    if preview.read_bytes() != render(run, preview).encode('utf-8'):
        raise ValueError('preview.html 변경: build 후 다시 확인하세요.')
    fingerprint = state(run)['browser']
    images = assets_for(run, jobs_for(src, book, run=run))
    version = version_for(run, comic, root, fingerprint, src, images)
    raw_note, old_comic = note.read_bytes(), file_hash(comic)
    raw_comic = render(run, comic, image_root=version).encode('utf-8')
    candidate_note, links = plan_note_links(raw_note, note, comic, raw_comic, book['pages'])
    manifest = {
        'schema_version': 1, 'run': str(run), 'fingerprint': fingerprint,
        'run_hashes': run_hashes(run), 'old_note_sha256': digest(raw_note), 'old_comic_sha256': old_comic,
        'note': note.relative_to(repo).as_posix(), 'comic': comic.relative_to(repo).as_posix(),
        'version': version.relative_to(repo).as_posix(), 'link_plan': links,
        'preview_report_sha256': digest(evidence[REPORT]) if evidence is not None else None,
    }
    write_atomic(out / MANIFEST, manifest)
    tree = local(out, 'tree')
    snapshot = ResourceSnapshot(repo, tree)
    for name, raw in (('note', candidate_note), ('comic', raw_comic)):
        path = local(tree, manifest[name])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    inputs = candidate_inputs(run, out, manifest, src, book, images)
    for key, path in inputs.images.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(local(run, images[key]['file']).read_bytes())

    def checked_inputs():
        if inputs.source_status == 'changed':
            raise ValueError('리허설 원본 후보의 본문 변경')
        validate_output(inputs.comic)
        for key, path in inputs.images.items():
            if file_hash(path) != images[key]['sha256']:
                raise ValueError(f'리허설 준비 중 그림 변경: {key}')
        return inputs

    report = browser_check(run, 'rehearsal', out, load_candidate=checked_inputs, snapshot_resource=snapshot)
    report['link_plan'] = links
    if links['status'] != 'complete':
        report['failures'].append({'check': 'link_plan', 'expected': '준비 완료 토픽의 안내 삽입',
                                   'actual': [row for row in links['results']
                                              if row.get('reason') and row['reason'] != 'PAGE_HELD']})
    try:
        if (file_hash(note) != manifest['old_note_sha256'] or file_hash(comic) != old_comic
                or run_hashes(run) != manifest['run_hashes'] or state(run)['browser'] != fingerprint):
            raise ValueError('리허설 중 발행 입력 변경')
        require_current_resources(repo, report['local_resources'])
    except (ValueError, OSError) as exc:
        report['failures'].append({'check': 'candidate_inputs', 'expected': '리허설 입력 유지', 'actual': str(exc)})
    if report['failures']:
        report['status'] = 'failed'
    write_atomic(out / REPORT, report)
    return report


@dataclass
class Rehearsal:
    run: Path
    repo: Path
    note: Path
    output: Path
    version: Path
    manifest: dict
    report_sha256: str
    resources: dict
    evidence: dict
    original_note: bytes
    note_bytes: bytes
    comic_bytes: bytes
    images: dict

    def matches(self, record):
        return (record.get('version') == str(self.version) and record.get('html') == str(self.output)
                and record.get('html_sha256') == digest(self.comic_bytes))

    def archive(self, version):
        directory = version / 'checks' / 'rehearsal' / self.report_sha256
        directory.mkdir(parents=True, exist_ok=True)
        for name, raw in self.evidence.items():
            atomic_write(local(directory, name), raw)

    def recheck(self):
        _, src, _ = load(self.run)
        repo, note, comic, root = final_paths(src)
        if (repo, note, comic, root / 'versions') != (self.repo, self.note, self.output, self.version.parent):
            raise ValueError('리허설 후 발행 경로 변경: 다시 리허설하세요.')
        if note.read_bytes() != self.original_note:
            raise ValueError('리허설 후 원본 변경: 다시 리허설하세요.')
        current = file_hash(comic)
        if current != self.manifest['old_comic_sha256']:
            record = read(self.run / 'publication.json') if (self.run / 'publication.json').is_file() else {}
            if not self.matches(record) or current != digest(self.comic_bytes):
                raise ValueError('리허설 후 기존 발행 HTML 변경: 다시 리허설하세요.')
        if run_hashes(self.run) != self.manifest['run_hashes'] or state(self.run)['browser'] != self.manifest['fingerprint']:
            raise ValueError('리허설 후 RUN 입력 변경: 다시 리허설하세요.')
        require_current_resources(repo, self.resources)

    def check_preview(self, evidence):
        if digest(evidence[REPORT]) != self.manifest['preview_report_sha256']:
            raise ValueError('리허설 후 미리보기 증거 변경: 다시 리허설하세요.')

    def apply_note(self, version):
        if file_hash(self.output) != digest(self.comic_bytes):
            raise ValueError('연결 직전 발행 HTML 변경')
        apply_note_plan(self.note, self.original_note, self.note_bytes, version=version)
        if read(version / LINK_RECORD)['status'] != 'pending' and link_status(version)['status'] != 'passed':
            save_link_status(version, 'pending', stage='insertion')
        result = self.manifest['link_plan']
        return {**result, 'changed': self.original_note != self.note_bytes, 'dry_run': False}


def load_rehearsal(run, out):
    run, out = Path(run).resolve(), Path(out).resolve()
    try:
        manifest_path, report_path = local(out, MANIFEST), local(out, REPORT)
        manifest_raw, report_raw = manifest_path.read_bytes(), report_path.read_bytes()
        manifest, report = json.loads(manifest_raw), json.loads(report_raw)
        if (manifest['schema_version'] != 1 or manifest['run'] != str(run) or report['run'] != str(run)
                or report['schema_version'] != 2 or report['stage'] != 'rehearsal' or report['link_mode'] != 'required'
                or report['note_to_comic'] != 'required' or report['status'] != 'passed' or report['failures']
                or report['source_status'] != 'current' or manifest['link_plan']['status'] != 'complete'
                or manifest['link_plan'] != report['link_plan']):
            raise ValueError('통과한 리허설 보고서 필요')
        _, src, book = load(run)
        repo, note, output, root = final_paths(src)
        version = local(repo, manifest['version'])
        if (manifest['note'] != note.relative_to(repo).as_posix()
                or manifest['comic'] != output.relative_to(repo).as_posix()
                or version.parent != root / 'versions' or not VERSION_ID.fullmatch(version.name)
                or version.is_symlink()):
            raise ValueError('리허설 발행 경로 불일치')
        images = assets_for(run, jobs_for(src, book, run=run))
        inputs = candidate_inputs(run, out, manifest, src, book, images)
        expected = report['input_hashes']
        if inputs.hashes() != expected or expected['files']['candidate'] != digest(manifest_raw):
            raise ValueError('리허설 검사 후보 또는 입력 변경')
        if expected['images'] != {key: item['sha256'] for key, item in images.items()}:
            raise ValueError('리허설 그림 지문 불일치')
        raw_note, raw_comic = inputs.note.read_bytes(), inputs.comic.read_bytes()
        if digest(raw_note) != expected['files']['note'] or digest(raw_comic) != expected['files']['comic']:
            raise ValueError('리허설 HTML 변경')
        if digest(strip_links(raw_note.decode('utf-8'))) != src['content_sha256']:
            raise ValueError('리허설 원본 본문 변경')
        resources = report['local_resources']
        require_current_resources(inputs.repo, resources)
        shots = passing_views(report, book['pages'], out)
        if shots.keys() & {MANIFEST, REPORT}:
            raise ValueError('리허설 증거 파일명 충돌')
        sha = digest(report_raw)
        evidence = shots | {MANIFEST: manifest_raw, REPORT: report_raw}
        original_note = note.read_bytes()
        archived = version / 'checks' / 'rehearsal' / sha / REPORT
        already_accepted = file_hash(archived) == sha and file_hash(output) == digest(raw_comic)
        if digest(original_note) != manifest['old_note_sha256']:
            if original_note != raw_note or not already_accepted:
                raise ValueError('리허설 후 원본 변경: 다시 리허설하세요.')
        candidate = Rehearsal(run, repo, note, output, version, manifest, sha, resources, evidence,
                              original_note, raw_note, raw_comic, inputs.images)
        candidate.recheck()
        if src.get('browser_gate_version') and not already_accepted:
            candidate.check_preview(preview_evidence(run))
        return candidate
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f'발행 리허설 증거 확인 실패: {exc}') from exc
