"""Page-scoped work packets and verdicts for the current comic workflow."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from urllib.parse import unquote, urlsplit

from comic_contract import (CSS, REVIEW_VERSION, SKILL, TEMPLATE, assets_for, atomic_write,
                            fingerprint, jobs_for, local, raster, read, validate_storyboard,
                            write_atomic)
from comic_reviews import (criteria_digest, dependencies, page_review_inputs, preserve_report,
                           review_data, write_review)
from comic_source import digest, existing, parse


def reference_index(run):
    if run is None:
        return {}, {}
    run = Path(run)
    indexes = []
    for filename in ('art-references.json', 'art-reference-fallback.json'):
        path = run / filename
        indexes.append({key: {**item, 'path': str(local(run, item['file']))}
                        for key, item in read(path).items()} if path.exists() else {})
    return tuple(indexes)


def art_jobs(src, book, page, archived=None, fallback=None):
    archived, fallback = archived or {}, fallback or {}
    jobs = []
    cast = {c['id']: c for c in book['characters']}
    file_hashes = {}
    for panel_number, panel in enumerate(page['panels'], 1):
        visible = [cast[c] for c in panel['characters']]
        style_ref = panel.get('style_reference', 'flat-people' if visible else 'flat-objects')
        if style_ref not in ('flat-people', 'flat-objects', 'flat-process', 'flat-structure'):
            raise ValueError(f'{page["id"]}/{panel_number}: 알 수 없는 그림체 참조')
        style_path = SKILL / 'assets' / 'style' / (style_ref + '.png')
        references = [{'kind': 'style', 'id': f'style:{style_ref}', 'path': str(style_path)}]
        supplied = panel.get('art_references', [])
        if not isinstance(supplied, list):
            raise ValueError('art_references는 목록이어야 합니다.')
        for ref in supplied:
            if not isinstance(ref, dict) or ref.get('kind') not in ('structure', 'continuity') or not isinstance(ref.get('path'), str):
                raise ValueError('그림 참조에는 kind(structure/continuity)와 저장소 상대 path가 필요합니다.')
            path = local(Path(src['repo']), ref['path'])
            references.append({'kind': ref['kind'], 'id': f'{ref["kind"]}:{ref["path"]}', 'path': str(path)})
        for reference in references:
            identity = reference['id']
            pinned = archived.get(identity)
            if pinned is None:
                try:
                    reference['path'] = str(existing(reference['path']))
                except ValueError:
                    pinned = fallback.get(identity)
                    if pinned is None:
                        raise
            if pinned:
                reference['path'] = pinned['path']
            name = reference['path']
            if name not in file_hashes:
                file_hashes[name] = digest(Path(name).read_bytes())
            reference['sha256'] = file_hashes[name]
            if pinned and reference['sha256'] != pinned['sha256']:
                raise ValueError('보관된 그림 참조 파일 지문 불일치')
        people = ' | '.join(f"{c['id']}: {c['appearance']}" for c in visible)
        prompt = '\n'.join([
            'Wordless educational biology comic panel.',
            'Shared visual style: ' + book['style'],
            'Visible characters (only these): ' + people if people else 'Object-only: no people, faces, hands, or personification.',
            'Scene: ' + panel['scene'],
            'Use style references for appearance only, structure references for anatomy, and continuity references for recurring appearance.',
            'Landscape, warm paper and restrained blue. Leave upper 40% quiet; keep essential objects and action within the lower 60%.',
            'No rendered text, labels, numbers, speech balloons, borders, extra diagrams, UI, or watermarks.',
        ])
        identity = {'prompt': prompt, 'references': [{k: r[k] for k in ('kind', 'sha256')} for r in references]}
        jobs.append({'key': f'{page["id"]}/{panel_number:02}', 'page': page['id'], 'panel': panel_number,
                     'prompt': prompt, 'references': references, 'prompt_sha256': fingerprint(identity)})
    return jobs


def input_fingerprints(src, book, page, jobs, assets, criteria, *, frozen=None):
    frozen_topics, frozen_files = frozen if frozen is not None else (None, None)
    files = {key: value['sha256'] for key, value in frozen_files.items()} if frozen_files is not None else None
    content = page_review_inputs(src, book, page, {}, criteria, saved_files=files)
    content.pop('images')
    if frozen_topics is None:
        content['figures'] = {tid: {href: digest(path.read_bytes()) for href, path in figures.items()}
                              for tid, (_, figures) in source_topics(src, page).items() if figures}
    else:
        content['figures'] = {tid: {href: ref['sha256'] for href, ref in topic['figures'].items()}
                              for tid, topic in frozen_topics.items() if topic['figures']}
    content['storyboard'] = fingerprint({
        'page': {**page, 'panels': [{k: v for k, v in panel.items() if k not in ('style_reference', 'art_references')}
                                   for panel in page['panels']]},
        'speakers': [{k: c[k] for k in ('id', 'name', 'role', 'voice')} for c in book['characters']
                     if c['id'] in page['narrative']['cast']],
    })
    checks = {'content': fingerprint(content)}
    if jobs and all(job['key'] in assets for job in jobs):
        art = {j['key']: {'prompt': j['prompt_sha256'], 'image': assets[j['key']]['sha256']} for j in jobs}
        art_sources = {key: content[key] for key in ('source', 'related', 'files', 'figures')}
        checks['art'] = fingerprint({'criteria': criteria, 'source': art_sources, 'art': art})
        checks['composition'] = fingerprint({'content': checks['content'], 'art': checks['art'],
                                             'template': digest(TEMPLATE.read_bytes()), 'css': digest(CSS.read_bytes())})
    return checks


def page_state(run, pid, *, read_assets=True, ready_only=True):
    run, src, book = validate_storyboard(run, page_id=pid, allow_draft=not ready_only)
    if src.get('review_version') != REVIEW_VERSION:
        raise ValueError('페이지별 작업은 새 검토 계약의 RUN이 필요합니다.')
    page = next(p for p in book['pages'] if p['id'] == pid)
    if page['status'] != 'ready':
        if ready_only:
            raise ValueError(f'{pid}: 콘티가 준비되지 않았습니다.')
        return run, src, book, page, [], {}, {}
    jobs = jobs_for(src, book, pid, run=run)
    assets = assets_for(run, jobs, required=False) if read_assets else {}
    checks = input_fingerprints(src, book, page, jobs, assets, criteria_digest())
    return run, src, book, page, jobs, assets, checks


def stage_verdict(run, row, kind, expected, pid):
    if row.get('fingerprint') != expected or not expected:
        return None
    origin = row['origin']
    sha = origin['sha256']
    path = f'review-evidence/{sha}.json'
    if origin['report'] != path:
        raise ValueError('검토 증거 경로 불일치')
    raw = local(run, path).read_bytes()
    if digest(raw) != sha:
        raise ValueError('검토 증거 지문 불일치')
    evidence = json.loads(raw)
    snapshot, report = evidence['snapshot'], evidence['report']
    if (snapshot['page_id'] != pid or snapshot['id'] != report['task']
            or snapshot['id'] != fingerprint({k: v for k, v in snapshot.items() if k != 'id'})
            or snapshot['checks'].get(kind) != expected or snapshot['attempt_ns'] != row['attempt_ns']
            or report['checks'][kind]['status'] != row['status']):
        raise ValueError('검토 증거와 기록 불일치')
    return row['status']


def require_reviews(run, pid, rows, checks):
    for kind, expected in checks.items():
        if stage_verdict(run, rows.get(kind, {}).get(expected, {}), kind, expected, pid) != 'passed':
            labels = {'content': '내용', 'art': '그림', 'composition': '합성 화면'}
            raise ValueError(f'{pid}: 현재 {labels[kind]} 검토 통과 기록이 필요합니다.')


def copy_resource(root, path):
    raw = path.read_bytes()
    sha = digest(raw)
    name = f'resources/{sha}{path.suffix.lower()}'
    dest = local(root, name)
    dest.parent.mkdir(exist_ok=True)
    if not dest.exists():
        atomic_write(dest, raw)
    return {'file': name, 'sha256': sha}


def preserve_art_references(version, jobs):
    index = {}
    for job in jobs:
        for ref in job['references']:
            if ref['id'] not in index:
                frozen = copy_resource(version, Path(ref['path']))
                if frozen['sha256'] != ref['sha256']:
                    raise ValueError('발행 준비 중 그림 참조가 바뀌었습니다.')
                index[ref['id']] = frozen
    write_atomic(version / 'art-references.json', index)


def copy_art_reference_fallback(previous, run):
    archived, fallback = reference_index(previous)
    index = {}
    for identity, ref in (archived or fallback).items():
        frozen = copy_resource(run, Path(ref['path']))
        if frozen['sha256'] != ref['sha256']:
            raise ValueError('이전 그림 참조 파일 지문 불일치')
        index[identity] = frozen
    if index:
        write_atomic(run / 'art-reference-fallback.json', index)


def source_topics(src, page):
    related, _ = dependencies(page)
    topics = {topic['id']: topic['body_html'] for topic in src['topics']}
    ids = topics.keys() if related == 'all' else {page['id'], *related}
    note = Path(src['path'])
    repo = Path(src['repo'])
    result = {}
    for tid, html in topics.items():
        if tid not in ids:
            continue
        figures = {}
        for node in parse(html).walk():
            href = node.attrs.get('src', '') if node.tag == 'img' else ''
            url = urlsplit(href)
            if url.path and not (url.scheme or url.netloc):
                path = existing(Path(os.path.abspath(note.parent / unquote(url.path))))
                if not path.is_relative_to(repo):
                    raise ValueError(f'저장소 밖 원본 그림: {href}')
                figures[href] = path
        result[tid] = html, figures
    return result


def frozen_sources(src, page, root):
    _, files = dependencies(page)
    result = {tid: {'html': html, 'figures': {href: copy_resource(root, path) for href, path in figures.items()}}
              for tid, (html, figures) in source_topics(src, page).items()}
    repo = Path(src['repo'])
    return result, {name: copy_resource(root, existing(local(repo, name))) for name in files}


def freeze_references(directory, job):
    refs = []
    for ref in job['references']:
        frozen = copy_resource(directory, Path(ref['path']))
        if frozen['sha256'] != ref['sha256']:
            raise ValueError('그림 참조가 배정 중 변경됐습니다.')
        refs.append({'kind': ref['kind'], **frozen})
    return refs


def prepare_page(run, pid, stage, *, redo=False, panels=None):
    if stage not in ('content', 'generate', 'review') or ((redo or panels) and stage != 'generate'):
        raise ValueError('유효하지 않은 작업 단계·재생성 옵션')
    started = time.time_ns()
    run, src, book, page, jobs, assets, checks = page_state(run, pid, read_assets=stage != 'content')
    rows = review_data(run)['pages'].get(pid, {})
    if stage == 'content':
        selected_checks = {'content': checks['content']}
    else:
        require_reviews(run, pid, rows, {'content': checks['content']})
        if stage == 'review' and 'art' not in checks:
            raise ValueError(f'{pid}: 등록 그림을 모두 준비해야 합니다.')
        selected_checks = {kind: checks[kind] for kind in ('art', 'composition')
                           if stage == 'review' and stage_verdict(run, rows.get(kind, {}).get(checks[kind], {}), kind, checks[kind], pid) != 'passed'}
    if panels and set(panels) - {job['panel'] for job in jobs}:
        raise ValueError(f'{pid}: 대상 컷 번호 없음')
    pending = [j for j in jobs if (not panels or j['panel'] in panels) and (redo or j['key'] not in assets)]
    if (stage == 'generate' and not pending) or (stage == 'review' and not selected_checks):
        return {'page': pid, 'stage': stage, 'pending': 0, 'status': 'current'}

    task_root = run / 'tasks'
    task_root.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='.prepare-', dir=task_root))
    try:
        task = {'page_id': pid, 'stage': stage, 'attempt_ns': started, 'prepared_ns': 0,
                'checks': selected_checks, 'panels': list(range(1, len(page['panels']) + 1))}
        if stage == 'generate':
            registered = read(run / 'images.json')
            task['jobs'] = [{**job, 'references': freeze_references(directory, job),
                             'replaces_registered_art': job['key'] in registered} for job in pending]
        else:
            task['page'] = page
            task['characters'] = [c for c in book['characters'] if c['id'] in page['narrative']['cast']]
            if stage == 'content' or 'art' in selected_checks:
                task['sources'], task['additional_sources'] = frozen_sources(src, page, directory)
                frozen = (task['sources'], task['additional_sources'])
                frozen_checks = input_fingerprints(src, book, page, jobs, assets, criteria_digest(), frozen=frozen)
                if frozen_checks['content'] != checks['content']:
                    raise ValueError('원본 또는 검토 기준이 배정 중 변경됐습니다.')
                topic = next(t for t in src['topics'] if t['id'] == pid)
                task['evidence'] = {e['id']: {'text': e['text'], 'scope': e['scope']} for e in topic['evidence']}
            if stage == 'review':
                if 'art' in selected_checks:
                    task['art_references'] = {job['key']: freeze_references(directory, job) for job in jobs}
                task['art'] = {}
                for key, asset in assets.items():
                    dest = copy_path(directory, asset['file'])
                    shutil.copy2(local(run, asset['file']), dest)
                    if digest(dest.read_bytes()) != asset['sha256']:
                        raise ValueError('등록 그림이 검토 판본을 만드는 동안 바뀌었습니다.')
                    task['art'][key] = {'file': asset['file'], 'sha256': asset['sha256']}
            from comic_render import render
            view = directory / 'preview.html'
            view.write_text(render(run, view, image_root=directory,
                                   page_context=(src, book, page, assets), planned=stage == 'content'),
                            encoding='utf-8')
            task['preview'] = {'file': view.name, 'sha256': digest(view.read_bytes())}
        task['prepared_ns'] = time.time_ns()
        task['id'] = fingerprint(task)
        write_atomic(directory / 'task.json', task)
        destination = task_root / task['id']
        os.rename(directory, destination)
        return {'page': pid, 'stage': stage, 'file': str(destination / 'task.json'), 'pending': len(pending) if stage == 'generate' else len(selected_checks),
                'input_chars': len((destination / 'task.json').read_text(encoding='utf-8')), 'status': 'prepared'}
    finally:
        if directory.exists():
            shutil.rmtree(directory)


def copy_path(directory, name):
    path = local(directory, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def assignment(run, report_path, stages):
    run = Path(run).resolve()
    report = read(Path(report_path))
    task_id = report.get('task')
    if not isinstance(task_id, str) or not re.fullmatch(r'[0-9a-f]{64}', task_id):
        raise ValueError('유효한 배정 판본 지문(task)이 필요합니다.')
    directory = run / 'tasks' / task_id
    task = read(directory / 'task.json')
    if task.get('id') != task_id or fingerprint({k: v for k, v in task.items() if k != 'id'}) != task_id or task['stage'] not in stages:
        raise ValueError('배정 판본 지문 또는 단계 불일치')
    resources = list(task.get('additional_sources', {}).values()) + list(task.get('art', {}).values())
    for topic in task.get('sources', {}).values():
        resources.extend(topic['figures'].values())
    resources.extend(ref for refs in task.get('art_references', {}).values() for ref in refs)
    for job in task.get('jobs', []):
        resources.extend(job['references'])
    if 'preview' in task:
        resources.append(task['preview'])
    if any(digest(local(directory, r['file']).read_bytes()) != r['sha256'] for r in resources):
        raise ValueError('배정 판본의 파일 지문 불일치')
    return run, directory, task, report


def finish_task(directory, report):
    worker_seconds = report.get('elapsed_seconds')
    if worker_seconds is not None and (type(worker_seconds) not in (int, float)
                                       or not math.isfinite(worker_seconds) or worker_seconds < 0):
        raise ValueError('elapsed_seconds는 0 이상의 실제 작업 시간입니다.')
    path = directory / 'result.json'
    if path.exists():
        previous = read(path)
        if previous['report'] != report:
            raise ValueError('이미 종료된 배정입니다. 수정 작업은 다시 배정하세요.')
        return
    write_atomic(path, {'received_ns': time.time_ns(), 'report': report})


def record_page_review(run, report_path):
    run, directory, task, report = assignment(run, report_path, ('content', 'review'))
    judgments = report.get('checks')
    if not isinstance(judgments, dict) or judgments.keys() != task['checks'].keys():
        raise ValueError('보고서 검토 항목과 배정 판본 불일치')
    for verdict in judgments.values():
        if not isinstance(verdict, dict):
            raise ValueError('검토 판정은 객체여야 합니다.')
        notes = verdict.get('notes')
        if (verdict.get('status') not in ('passed', 'failed') or not isinstance(notes, list) or not notes
                or any(not isinstance(n, str) or not n.strip() for n in notes)
                or verdict.get('checked_panels') != task['panels']):
            raise ValueError('실제로 확인한 모든 컷과 판정 근거가 필요합니다.')
    finish_task(directory, report)
    pid = task['page_id']
    data = review_data(run)
    rows = data['pages'].setdefault(pid, {})
    recorded = []
    raw = (json.dumps({'snapshot': task, 'report': report}, ensure_ascii=False) + '\n').encode()
    for kind, verdict in judgments.items():
        expected = task['checks'][kind]
        history = rows.setdefault(kind, {})
        if history.get(expected, {}).get('attempt_ns', -1) > task['attempt_ns']:
            continue
        history[expected] = {'origin': preserve_report(run, raw), 'fingerprint': expected,
                             'attempt_ns': task['attempt_ns'], 'status': verdict['status']}
        recorded.append(kind)
    if recorded:
        write_review(run, data)
    try:
        *_, checks = page_state(run, pid, read_assets=task['stage'] != 'content', ready_only=False)
    except (OSError, ValueError):
        checks = {}
    active = [kind for kind in recorded if checks.get(kind) == task['checks'][kind]]
    return {'page': pid, 'recorded': active, 'status': 'recorded' if active else 'stale'}


def register_generation(run, report_path):
    run, directory, task, report = assignment(run, report_path, ('generate',))
    rows = report.get('images')
    calls = report.get('image_calls')
    if not isinstance(rows, list) or type(calls) is not int or calls < len(rows):
        raise ValueError('이미지 결과 목록과 실제 이미지 호출 수가 필요합니다.')
    calls_by_panel = report.get('calls_by_panel')
    if calls_by_panel is not None:
        valid_panels = {str(job['panel']) for job in task['jobs']}
        if (not isinstance(calls_by_panel, dict) or set(calls_by_panel) - valid_panels
                or any(type(count) is not int or count < 1 for count in calls_by_panel.values())
                or sum(calls_by_panel.values()) != calls):
            raise ValueError('컷별 이미지 호출 수와 실제 호출 합계 불일치')
    pid = task['page_id']
    assigned = {job['panel']: job for job in task['jobs']}
    seen, verified = set(), []
    for row in rows:
        if not isinstance(row, dict) or type(row.get('panel')) is not int:
            raise ValueError('생성 결과의 컷 번호가 필요합니다.')
        panel = row['panel']
        job = assigned.get(panel)
        if panel in seen or not job or row.get('prompt_sha256') != job['prompt_sha256']:
            raise ValueError(f'{pid}/{panel}: 배정 생성 지문 불일치')
        if calls_by_panel is not None and str(panel) not in calls_by_panel:
            raise ValueError(f'{pid}/{panel}: 생성 호출 기록 없음')
        seen.add(panel)
        image = Path(row['image'])
        info = raster(image)
        if row.get('sha256') != info['sha256']:
            raise ValueError(f'{pid}/{panel}: 생성 결과 파일 지문 불일치')
        verified.append((job, image, info))
    finish_task(directory, report)
    run, _, _, _, current_jobs, _, checks = page_state(run, pid, read_assets=False)
    current = {job['panel']: job for job in current_jobs}
    data = read(run / 'images.json')
    for job, _, _ in verified:
        panel = job['panel']
        if current.get(panel, {}).get('prompt_sha256') != job['prompt_sha256']:
            raise ValueError(f'{pid}/{panel}: 현재 생성 지문 불일치')
        if data.get(job['key'], {}).get('attempt_ns', -1) > task['attempt_ns']:
            raise ValueError(f'{pid}/{panel}: 더 최근 그림이 등록돼 있습니다.')
    require_reviews(run, pid, review_data(run)['pages'].get(pid, {}), {'content': checks['content']})
    for job, image, info in verified:
        name = f'images/{pid}/{job["panel"]:02}-{info["sha256"]}{info["extension"]}'
        contents = image.read_bytes()
        if digest(contents) != info['sha256']:
            raise ValueError('등록 중 그림 파일이 바뀌었습니다.')
        atomic_write(copy_path(run, name), contents)
        data[job['key']] = {'file': name, 'sha256': info['sha256'], 'prompt_sha256': job['prompt_sha256'],
                            'attempt_ns': task['attempt_ns']}
    write_atomic(run / 'images.json', data)
    return {'page': pid, 'registered': len(verified), 'failed': sorted(set(assigned) - seen)}


def inherit_page_reviews(run, src, book, old, old_src, *, dry_run):
    data = review_data(run)
    old_records = review_data(old)['pages'] if old_src.get('review_version') == REVIEW_VERSION else {}
    result = {}
    for page in book['pages']:
        pid = page['id']
        if page['status'] != 'ready':
            result[pid] = {'status': page['status']}
            continue
        jobs = jobs_for(src, book, pid, run=run)
        checks = input_fingerprints(src, book, page, jobs, assets_for(run, jobs, required=False), criteria_digest())
        current = data['pages'].setdefault(pid, {})
        eligible = []
        for kind, expected in checks.items():
            before = old_records.get(pid, {}).get(kind, {}).get(expected, {})
            history = current.setdefault(kind, {})
            if (expected in history
                    or stage_verdict(old, before, kind, expected, pid) != 'passed'):
                continue
            eligible.append(kind)
            if not dry_run:
                previous = local(old, before['origin']['report']).read_bytes()
                history[expected] = {**before, 'origin': preserve_report(run, previous)}
        result[pid] = {'status': ('eligible' if dry_run else 'inherited') if eligible else 'needs_review',
                       'checks': eligible}
    if not dry_run:
        write_review(run, data)
    return {'dry_run': dry_run, 'pages': result}


def run_stats(run):
    root = Path(run).resolve()
    tasks = []
    for path in sorted((root / 'tasks').glob('*/task.json')):
        raw = path.read_text(encoding='utf-8')
        task = json.loads(raw)
        result = path.with_name('result.json')
        row = {'page': task['page_id'], 'stage': task['stage'], 'task': task['id'],
               'input_chars': len(raw), 'prompt_chars': sum(len(j['prompt']) for j in task.get('jobs', [])),
               'prepare_seconds': (task['prepared_ns'] - task['attempt_ns']) / 1e9}
        if result.exists():
            data = read(result)
            report = data['report']
            elapsed = report.get('elapsed_seconds')
            turnaround = (data['received_ns'] - task['prepared_ns']) / 1e9
            row.update(turnaround_seconds=turnaround, worker_seconds=elapsed,
                       dispatch_and_collection_seconds=max(0, turnaround - elapsed) if elapsed is not None else None,
                       received_ns=data['received_ns'])
            if task['stage'] == 'generate':
                calls = report['image_calls']
                by_panel = report.get('calls_by_panel')
                jobs = task['jobs']
                if by_panel is not None:
                    regenerated = sum(by_panel.get(str(job['panel']), 0) for job in jobs if job.get('replaces_registered_art', False))
                elif all(job.get('replaces_registered_art', False) for job in jobs):
                    regenerated = calls
                elif not any(job.get('replaces_registered_art', False) for job in jobs):
                    regenerated = 0
                else:
                    regenerated = None
                row.update(image_calls=calls, regeneration_calls=regenerated,
                           new_image_calls=calls - regenerated if regenerated is not None else None)
        tasks.append(row | {'prepared_ns': task['prepared_ns']})
    starts = [t['prepared_ns'] for t in tasks]
    ends = [t['received_ns'] for t in tasks if 'received_ns' in t]
    stages = {}
    for stage in ('content', 'generate', 'review'):
        group = [t for t in tasks if t['stage'] == stage]
        measured = [t['worker_seconds'] for t in group if t.get('worker_seconds') is not None]
        stages[stage] = {'tasks': len(group), 'completed': sum('received_ns' in t for t in group),
                         'input_chars': sum(t['input_chars'] for t in group),
                         'image_calls': sum(t.get('image_calls', 0) for t in group),
                         'prepare_seconds': sum(t['prepare_seconds'] for t in group),
                         'timed_tasks': len(measured), 'worker_seconds': sum(measured) if measured else None}
    generations = [t for t in tasks if 'image_calls' in t]
    known = all(t['regeneration_calls'] is not None for t in generations)
    return {'input_chars': sum(t['input_chars'] for t in tasks), 'image_calls': sum(t['image_calls'] for t in generations),
            'new_image_calls': sum(t['new_image_calls'] for t in generations) if known else None,
            'regeneration_calls': sum(t['regeneration_calls'] for t in generations) if known else None,
            'task_window_seconds': (max(ends) - min(starts)) / 1e9 if ends else None,
            'stages': stages, 'tasks': tasks}
