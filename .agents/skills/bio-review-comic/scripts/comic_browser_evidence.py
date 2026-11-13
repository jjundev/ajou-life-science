"""Persist browser evidence and check its applicability without launching Chromium."""
import json
from pathlib import Path

from comic_contract import atomic_write, local, raster, read, write_atomic
from comic_source import digest, existing

VIEWS = ((1440, 900, 'light'), (1440, 900, 'dark'), (375, 812, 'light'), (375, 812, 'dark'))
PREVIEW_RECORD = 'browser-preview.json'
LINK_RECORD = 'link-verification.json'


def ready_panels(pages):
    return {page['id']: len(page['panels']) for page in pages if page['status'] == 'ready'}


def require_current_resources(repo, resources):
    if not isinstance(resources, dict):
        raise ValueError('브라우저 로컬 자원 지문 누락')
    for name, sha in resources.items():
        if digest(local(repo, name).read_bytes()) != sha:
            raise ValueError(f'브라우저 검사 후 로컬 자원 변경: {name}')


def preview_evidence(run):
    from comic_browser import inputs_for
    try:
        pointer = read(run / PREVIEW_RECORD)
        path = Path(pointer['report'])
        raw = path.read_bytes()
        if digest(raw) != pointer['sha256']:
            raise ValueError('보고서 지문 불일치')
        report = json.loads(raw)
        inputs = inputs_for(run, 'preview')
        if (report['schema_version'] != 2 or report['stage'] != 'preview' or
                report['link_mode'] != 'history' or report['status'] != 'passed' or report['failures']):
            raise ValueError('통과한 미리보기 보고서 필요')
        if report['input_hashes'] != inputs.hashes() or report['run'] != str(run):
            raise ValueError('미리보기 보고서의 입력 변경')
        require_current_resources(inputs.repo, report['local_resources'])
        return passing_views(report, inputs.pages, path.parent) | {'report.json': raw}
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError(f'미리보기 자동 검사 증거 확인 실패: {exc}. browser-check --stage preview를 실행하세요.') from exc


def passing_views(report, pages, out):
    views = report['views']
    if len(views) != len(VIEWS) or {(v['width'], v['height'], v['theme']) for v in views} != set(VIEWS):
        raise ValueError('데스크톱·모바일 라이트·다크 4종 필요')
    ready = ready_panels(pages)
    held = [{'id': p['id'], 'reason': p['reason']} for p in pages if p['status'] == 'held']
    if report['held'] != held:
        raise ValueError('보류 목록 불일치')
    shots = {}
    for view in views:
        if (view['failures'] or view['panels_by_topic'] != ready or view['returned_topics'] != list(ready)
                or view['pages'] != len(ready) or view['panels'] != sum(ready.values())
                or view['link_round_trips'] != len(ready)):
            raise ValueError('토픽·컷·복귀 검사 누락 또는 실패')
        name = view['screenshot']
        shot = local(out, name)
        info = raster(shot)
        data = shot.read_bytes()
        if (Path(name).name != name or name in shots or digest(data) != view['screenshot_sha256'] or
                (info['width'], info['height']) != (view['width'], view['height'])):
            raise ValueError('브라우저 스크린샷 변경 또는 중복')
        shots[name] = data
    return shots


def save_link_status(version, status, *, stage, **detail):
    data = {'status': status, 'stage': stage, **detail}
    write_atomic(version / LINK_RECORD, data)
    return data


def preserve_published_report(version, path, report):
    raw = path.read_bytes()
    sha = digest(raw)
    destination = version / 'checks' / 'published' / sha
    destination.mkdir(parents=True, exist_ok=True)
    for view in report['views']:
        if name := view['screenshot']:
            data = local(path.parent, name).read_bytes()
            if digest(data) != view['screenshot_sha256']:
                raise ValueError('발행본 검사 스크린샷 지문 불일치')
            atomic_write(local(destination, name), data)
    atomic_write(destination / 'report.json', raw)
    return (destination / 'report.json').relative_to(version).as_posix(), sha


def link_status(run):
    from comic_browser import inputs_for

    record = read(Path(run) / 'publication.json')
    version = existing(record['version'])
    path = version / LINK_RECORD
    if not path.is_file():
        return {'status': 'unverified', 'stage': 'legacy'}
    status = read(path)
    if status['status'] == 'passed':
        try:
            inputs = inputs_for(Path(run).resolve(), 'published')
            if status['input_hashes'] != inputs.hashes() or inputs.note_link_error:
                raise ValueError('발행본 또는 원본 검사 입력 변경')
            require_current_resources(inputs.repo, status['local_resources'])
            evidence = local(version, status['report'])
            if digest(evidence.read_bytes()) != status['report_sha256']:
                raise ValueError('발행본 검사 보고서 변경')
            for view in read(evidence)['views']:
                if digest(local(evidence.parent, view['screenshot']).read_bytes()) != view['screenshot_sha256']:
                    raise ValueError('발행본 검사 스크린샷 변경')
        except (ValueError, OSError, KeyError, TypeError) as exc:
            return {**status, 'status': 'pending', 'reason': str(exc)}
    return status
