"""Carry forward independent page reviews with their original evidence."""
from __future__ import annotations

import json
from pathlib import Path

from comic_contract import REVIEW_VERSION, SKILL, assets_for, atomic_write, fingerprint, jobs_for, local, page_content, read, validate_storyboard
from comic_source import digest, existing


def criteria_digest(version=REVIEW_VERSION):
    if version == 1:
        # Version 1 verdicts were issued under the criteria shipped with that contract.
        return '8b38d8a23b3a58f087d408372347e698c8b42d2c262b9033b6f6e121d99babce'
    refs = SKILL / 'references'
    review = (refs / 'review.md').read_text(encoding='utf-8').split('\n## 브라우저 확인\n', 1)[0]
    agents = (refs / 'agents.md').read_text(encoding='utf-8').split('\n## 독립 검토자에게 전달할 작업\n', 1)[-1]
    styles = SKILL / 'assets' / 'style'
    return fingerprint({'review': review, 'reviewer': agents, 'style': digest((refs / 'style.md').read_bytes()),
                        'references': {p.name: digest(p.read_bytes()) for p in styles.glob('*.png')}})


def dependencies(page):
    spec = page.get('source_dependencies', {'topics': 'all', 'files': []})
    if not isinstance(spec, dict):
        raise ValueError('source_dependencies는 객체여야 합니다.')
    topics, files = spec.get('topics'), spec.get('files')
    if ((topics != 'all' and not isinstance(topics, list)) or not isinstance(files, list)
            or any(not isinstance(item, str) or not item for item in files)
            or (topics != 'all' and any(not isinstance(item, str) or not item for item in topics))):
        raise ValueError('source_dependencies에는 topics(토픽 ID 목록 또는 all)와 files(저장소 상대 경로 목록)가 필요합니다.')
    return topics, sorted(set(files))


def related_sources(src, page):
    topics, _ = dependencies(page)
    if topics == 'all':
        return {'all': src['content_sha256']}
    index = {t['id']: t['sha256'] for t in src['topics']}
    unknown = set(topics) - index.keys()
    if unknown:
        raise ValueError(f'알 수 없는 관련 토픽: {", ".join(sorted(unknown))}')
    return {tid: index[tid] for tid in sorted(set(topics) - {page['id']})}


def page_review_inputs(src, book, page, images, criteria, *, saved_files=None):
    _, filenames = dependencies(page)
    files = {}
    for name in filenames:
        if saved_files is not None:
            files[name] = saved_files[name]
        else:
            try:
                repo = Path(src['repo']).resolve()
                path = existing(local(repo, name))
                files[name] = digest(path.read_bytes())
            except (ValueError, OSError) as exc:
                raise ValueError(f'{page["id"]}: 원본 근거 파일을 읽을 수 없음: {name}') from exc
    return {'source': page['source_topic_sha256'], 'related': related_sources(src, page),
            'files': files, 'criteria': criteria, 'storyboard': page_content(book, page), 'images': images}


def review_fingerprints(inputs):
    content = fingerprint({key: value for key, value in inputs.items() if key != 'images'})
    return {'content': content, 'visual': fingerprint({'content': content, 'images': inputs['images']})}


def validate_worker(pid, report, inputs):
    if not isinstance(report, dict):
        raise ValueError(f'{pid}: 독립 검토 보고서는 JSON 객체여야 합니다.')
    panels = report.get('checked_panels')
    expected = list(range(1, len(inputs['images']) + 1))
    if (report.get('page') != pid or not isinstance(panels, list)
            or any(type(n) is not int for n in panels) or sorted(panels) != expected):
        raise ValueError(f'{pid}: 독립 검토 보고서의 페이지·컷 목록 불일치')
    if report.get('issues') != []:
        raise ValueError(f'{pid}: 독립 검토 보고서에 해결할 문제가 남아 있음')
    for kind, fp in review_fingerprints(inputs).items():
        entry = report.get(kind, {})
        if not isinstance(entry, dict):
            raise ValueError(f'{pid}: 독립 {kind} 검토 형식 오류')
        notes = entry.get('notes')
        if (entry.get('status') != 'passed' or entry.get('fingerprint') != fp
                or not isinstance(notes, list) or not notes
                or any(not isinstance(note, str) or not note.strip() for note in notes)):
            raise ValueError(f'{pid}: 독립 {kind} 검토 기록 또는 현재 입력 지문 불일치')


def verified_report(run, pid, entry, inputs):
    if not isinstance(entry, dict):
        raise ValueError(f'{pid}: 검토 기록 형식 오류')
    origin = entry.get('origin', {})
    if (entry.get('inputs') != inputs or not isinstance(origin, dict)
            or origin.get('kind') not in ('independent', 'inherited')):
        raise ValueError(f'{pid}: 검토 입력 또는 최초 보고서 출처 없음')
    filename = f'review-evidence/{origin.get("sha256")}.json'
    if origin.get('report') != filename:
        raise ValueError(f'{pid}: 최초 독립 검토 보고서 경로 불일치')
    try:
        raw = local(run, filename).read_bytes()
    except OSError as exc:
        raise ValueError(f'{pid}: 최초 독립 검토 보고서 없음') from exc
    if digest(raw) != origin['sha256']:
        raise ValueError(f'{pid}: 최초 독립 검토 보고서 지문 불일치')
    report = json.loads(raw)
    validate_worker(pid, report, inputs)
    if any(entry.get(kind) != report[kind] for kind in ('content', 'visual')):
        raise ValueError(f'{pid}: 최초 독립 검토 판정과 현재 기록 불일치')
    return raw


def review_data(run):
    path = run / 'review.json'
    return read(path) if path.exists() else {'pages': {}}


def write_review(run, data):
    atomic_write(run / 'review.json', (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def preserve_report(run, raw):
    sha = digest(raw)
    filename = f'review-evidence/{sha}.json'
    path = local(run, filename)
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f'보존된 최초 검토 보고서 지문 불일치: {filename}')
    else:
        atomic_write(path, raw)
    return {'report': filename, 'sha256': sha}


def page_images(run, src, book):
    jobs = jobs_for(src, book, run=run)
    assets = assets_for(run, jobs, required=False)
    images, missing = {}, set()
    for job in jobs:
        pid, key = job['page'], job['key']
        if key not in assets:
            missing.add(pid)
        else:
            images.setdefault(pid, {})[key] = assets[key]['sha256']
    return images, missing


def current_page_review(run, pid):
    run, src, book = validate_storyboard(run, allow_draft=True)
    if not src.get('review_version'):
        raise ValueError('새 검토 계약으로 extract한 RUN이 필요합니다.')
    page = next((p for p in book['pages'] if p['id'] == pid and p['status'] == 'ready'), None)
    images, missing = page_images(run, src, book)
    if page is None or pid in missing:
        raise ValueError(f'{pid}: 현재 콘티와 등록 그림을 준비해야 합니다.')
    return run, page_review_inputs(src, book, page, images[pid], criteria_digest(src['review_version']))


def page_fingerprints(run, pid):
    if read(Path(run) / 'source.json').get('review_version') == REVIEW_VERSION:
        from comic_page import page_state
        _, _, _, _, _, _, checks = page_state(run, pid)
        return {'pages': {pid: checks}}
    _, inputs = current_page_review(run, pid)
    return {'pages': {pid: review_fingerprints(inputs)}, 'review_inputs': {pid: inputs}}


def record_review(run, worker_report):
    if read(Path(run) / 'source.json').get('review_version') == REVIEW_VERSION:
        from comic_page import record_page_review
        return record_page_review(run, worker_report)
    raw = Path(worker_report).read_bytes()
    report = json.loads(raw)
    if not isinstance(report, dict):
        raise ValueError('독립 검토 보고서는 JSON 객체여야 합니다.')
    pid = report.get('page')
    run, inputs = current_page_review(run, pid)
    validate_worker(pid, report, inputs)
    origin = preserve_report(run, raw) | {'kind': 'independent'}
    entry = {kind: report[kind] for kind in ('content', 'visual')} | {'inputs': inputs, 'origin': origin}
    data = review_data(run)
    data['pages'][pid] = entry
    write_review(run, data)
    return {'page': pid, 'origin': origin}


def compare_sources(previous, current, page, old_topics, new_topics):
    pid = page['id']
    reasons = []
    if pid not in old_topics:
        reasons.append('new_page')
    elif old_topics[pid] != new_topics[pid]:
        reasons.append('source_changed')
    topics, _ = dependencies(page)
    if topics == 'all':
        changed = sorted(t for t in (old_topics.keys() | new_topics.keys()) - {pid}
                         if old_topics.get(t) != new_topics.get(t))
        if changed or (not reasons and previous['content_sha256'] != current['content_sha256']):
            reasons.append('related_source_changed')
    else:
        changed = sorted(t for t in set(topics) - {pid} if old_topics.get(t) != new_topics.get(t))
        if changed:
            reasons.append('related_source_changed')
    return reasons, changed


def prior_review(run, src, book, page, images, entry, current):
    """Check the old snapshot/art using criteria and file hashes bound to the old report."""
    recorded = entry['inputs']
    previous = page_review_inputs(src, book, page, images, recorded['criteria'], saved_files=recorded['files'])
    raw = verified_report(run, page['id'], entry, previous)
    fields = {'criteria': 'criteria_changed', 'files': 'source_files_changed',
              'storyboard': 'storyboard_changed', 'images': 'images_changed',
              'source': 'source_changed', 'related': 'related_source_changed'}
    reasons = [reason for key, reason in fields.items() if previous[key] != current[key]]
    return raw, reasons


def reuse_reviews(run, previous, *, dry_run=False):
    run, src, book = validate_storyboard(run, allow_draft=True)
    if not src.get('review_version'):
        raise ValueError('새 검토 계약으로 extract한 RUN이 필요합니다.')
    old, old_src, old_book = validate_storyboard(previous, historical=True, allow_draft=True)
    if old == run or Path(old_src['path']).resolve() != Path(src['path']).resolve():
        raise ValueError('이전 실행과 새 RUN은 같은 정리노트의 서로 다른 폴더여야 합니다.')
    if src.get('review_version') == REVIEW_VERSION:
        from comic_page import inherit_page_reviews
        return inherit_page_reviews(run, src, book, old, old_src, dry_run=dry_run)
    data = review_data(run)
    old_data = review_data(old) if old_src.get('review_version') else {'pages': {}}
    images, missing = page_images(run, src, book)
    old_images, old_missing = page_images(old, old_src, old_book) if old_src.get('review_version') else ({}, set())
    old_topics = {t['id']: t['sha256'] for t in old_src['topics']}
    new_topics = {t['id']: t['sha256'] for t in src['topics']}
    old_pages = {p['id']: p for p in old_book['pages']}
    criteria = criteria_digest(src['review_version'])
    results = {}
    applied = False
    for page in book['pages']:
        pid = page['id']
        if page['status'] == 'held':
            results[pid] = {'status': 'held', 'reason': page['reason']}
            continue
        try:
            reasons, changed = compare_sources(old_src, src, page, old_topics, new_topics)
        except ValueError as exc:
            results[pid] = {'status': 'needs_review', 'reasons': ['source_dependencies_unavailable'], 'detail': str(exc)}
            continue
        result = results[pid] = {'status': 'needs_review', 'reasons': reasons, 'related_topics': changed}
        if page['status'] != 'ready' or pid in missing:
            reasons.append('storyboard_pending' if page['status'] != 'ready' else 'images_pending')
        else:
            try:
                current = page_review_inputs(src, book, page, images[pid], criteria)
            except ValueError as exc:
                reasons.append('source_dependencies_unavailable')
                result['detail'] = str(exc)
            else:
                current_entry = data['pages'].get(pid)
                if current_entry:
                    try:
                        verified_report(run, pid, current_entry, current)
                    except (ValueError, KeyError, TypeError, AttributeError):
                        pass
                    else:
                        result.update(status='already_reviewed', reasons=[], related_topics=[])
                        continue
        entry = old_data['pages'].get(pid)
        if not old_src.get('review_version'):
            reasons.append('legacy_review')
        elif not entry:
            reasons.append('prior_review_missing')
        elif pid in old_missing or old_pages.get(pid, {}).get('status') != 'ready':
            reasons.append('prior_inputs_unavailable')
        elif not reasons:
            try:
                raw, mismatch = prior_review(old, old_src, old_book, old_pages[pid], old_images[pid], entry, current)
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                reasons.append('prior_review_invalid')
                result['detail'] = str(exc)
            else:
                reasons.extend(mismatch)
                if not mismatch:
                    result['status'] = 'eligible' if dry_run else 'inherited'
                    if not dry_run:
                        origin = preserve_report(run, raw) | {'kind': 'inherited'}
                        data['pages'][pid] = entry | {'origin': origin}
                        applied = True
    if applied:
        write_review(run, data)
    return {'dry_run': dry_run, 'pages': results}
