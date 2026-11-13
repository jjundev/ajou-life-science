#!/usr/bin/env python3
"""Local comic pipeline. Image generation and semantic review are agent tasks."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import shutil
import sys

from comic_contract import BROWSER_GATE_VERSION, REVIEW_VERSION, assets_for, check, jobs_for, local, raster, read, state, validate_storyboard, write
from comic_render import build, publish
from comic_reviews import page_fingerprints, record_review, reuse_reviews
from comic_links import link_notes
from comic_source import digest, inventory, resolve


def extract(repo, target, run, reuse=None, page=None):
    repo, run = Path(repo).resolve(), Path(run).resolve()
    if run.exists() and any(run.iterdir()):
        raise ValueError('실행 폴더에 이미 파일이 있습니다. 새 RUN을 사용하세요.')
    path = resolve(repo, target)
    src = inventory(path, repo, selection=[page] if page else None, review_version=REVIEW_VERSION,
                    browser_gate_version=BROWSER_GATE_VERSION)
    if run == path.parent or path.is_relative_to(run):
        raise ValueError('RUN은 원본 정리노트 폴더와 분리하세요.')
    book = {'schema_version': 2, 'characters': [], 'source_sha256': src['sha256'], 'title': f"생명과학 {src['range']} 학습만화", 'style': '생물 구조를 살린 학습만화. 밝은 종이색 배경과 절제된 파란 강조. 같은 대상의 모양·색 유지.', 'pages': []}
    for topic in src['topics']:
        if topic['include']:
            book['pages'].append({'id': topic['id'], 'title': topic['title'], 'source_topic_sha256': topic['sha256'], 'status': 'draft', 'question': '', 'summary': {'text': '', 'evidence': []}, 'terms': [], 'panels': [], 'coverage': [], 'clarification': {}, 'analogy': {}, 'narrative': {}, 'note_link': {}})
    run.mkdir(parents=True, exist_ok=True)
    write(run / 'source.json', src)
    shutil.copy2(path, run / 'source.html')
    write(run / 'images.json', {})
    write(run / 'review.json', {'pages': {}})
    if reuse:
        old = Path(reuse).resolve()
        if old == run:
            raise ValueError('이전 실행과 새 RUN은 달라야 합니다.')
        previous_src, previous = read(old / 'source.json'), read(old / 'storyboard.json')
        if Path(previous_src['path']).resolve() != path:
            raise ValueError('재사용 대상 원본 정리노트가 다릅니다.')
        book['style'] = previous['style']
        book['characters'] = previous.get('characters', [])
        prior = {p['id']: p for p in previous['pages']} if previous.get('schema_version') == 2 else {}
        for i, page in enumerate(book['pages']):
            found = prior.get(page['id'])
            if found and found.get('source_topic_sha256') == page['source_topic_sha256']:
                book['pages'][i] = copy.deepcopy(found)
        old_assets = read(old / 'images.json')
        new_assets = {}
        for job in jobs_for(src, book):
            item = old_assets.get(job['key'])
            if not item or item.get('prompt_sha256') != job['prompt_sha256']:
                continue
            try:
                if raster(local(old, item['file']))['sha256'] != item['sha256']:
                    continue
                dest = local(run, item['file'])
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local(old, item['file']), dest)
                new_assets[job['key']] = item
            except ValueError:
                continue
        write(run / 'images.json', new_assets)
    write(run / 'storyboard.json', book)
    return {'source': str(path), 'run': str(run), 'total': len(src['topics']), 'included': len(book['pages']), 'excluded': [{'id': t['id'], 'reason': t['reason']} for t in src['topics'] if not t['include']]}


def prompts(run):
    run, src, book = validate_storyboard(run)
    jobs = jobs_for(src, book)
    reusable = assets_for(run, jobs, required=False)
    for job in jobs:
        job['reusable'] = job['key'] in reusable
        job['output'] = str(run / 'images' / job['page'] / f"{job['panel']:02}.png")
    result = {'jobs': jobs, 'count': len(jobs), 'pending': sum(not j['reusable'] for j in jobs)}
    write(run / 'prompts.json', result)
    return result


def register_image(run, page, panel, image):
    run, src, book = validate_storyboard(run)
    job = next((j for j in jobs_for(src, book) if j['page'] == page and j['panel'] == panel), None)
    if not job:
        raise ValueError('대상 컷 없음')
    info = raster(image)
    filename = f'images/{page}/{panel:02}{info["extension"]}'
    dest = local(run, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if Path(image).resolve() != dest.resolve():
        shutil.copy2(image, dest)
    registry = read(run / 'images.json')
    registry[job['key']] = {'file': filename, 'sha256': info['sha256'], 'prompt_sha256': job['prompt_sha256']}
    write(run / 'images.json', registry)
    return {**registry[job['key']], 'page': page, 'panel': panel}


def fingerprints(run, page=None):
    return page_fingerprints(run, page) if page else state(Path(run).resolve())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    ext = commands.add_parser('extract', help='원본 페이지·근거를 추출하고 빈 콘티 생성')
    ext.add_argument('--repo', required=True, type=Path)
    ext.add_argument('--target', required=True)
    ext.add_argument('--run', required=True, type=Path)
    ext.add_argument('--reuse', type=Path)
    ext.add_argument('--page', help='명시적으로 한 토픽만 제작하는 샘플 범위')
    for name in ('prompts', 'build', 'fingerprints', 'publish', 'check', 'link-notes', 'link-status'):
        cmd = commands.add_parser(name)
        cmd.add_argument('--run', required=True, type=Path)
        if name == 'link-notes':
            cmd.add_argument('--dry-run', action='store_true')
            cmd.add_argument('--repair-fragments', action='store_true', help='발행본에 연결된 관리 링크의 토픽 해시만 복구')
        if name == 'publish':
            mode = cmd.add_mutually_exclusive_group()
            mode.add_argument('--no-link', action='store_true', help='만화만 발행; 이후 link-notes로 연결')
            mode.add_argument('--rehearsal', type=Path, help='통과한 리허설 후보 그대로 발행')
        if name == 'check':
            cmd.add_argument('--phase', choices=('storyboard', 'images', 'reviewed', 'browser'), default='storyboard')
        if name == 'fingerprints':
            cmd.add_argument('--page', help='다른 페이지의 제작을 기다리지 않고 한 페이지의 검토 지문 확인')
    reuse = commands.add_parser('reuse-reviews', help='이전 독립 검토의 페이지별 승계 여부 확인 및 적용')
    reuse.add_argument('--run', required=True, type=Path)
    reuse.add_argument('--from', required=True, dest='previous', type=Path)
    reuse.add_argument('--dry-run', action='store_true')
    record = commands.add_parser('record-review', help='독립 검토자의 통과 보고서를 검증하고 보존')
    record.add_argument('--run', required=True, type=Path)
    record.add_argument('--report', required=True, type=Path)
    browser = commands.add_parser('browser-check', help='실제 브라우저에서 4종 화면과 원본 링크 확인')
    browser.add_argument('--run', required=True, type=Path)
    browser.add_argument('--stage', required=True, choices=('preview', 'published'))
    browser.add_argument('--out', required=True, type=Path)
    browser.add_argument('--comic-only', action='store_true', help='연결 없이 발행한 만화의 역방향 링크 검사 생략')
    rehearsal = commands.add_parser('rehearse', help='격리본에서 최종 경로와 원본 왕복 검사')
    rehearsal.add_argument('--run', required=True, type=Path)
    rehearsal.add_argument('--out', required=True, type=Path)
    register = commands.add_parser('register-image', help='이미지 도구가 반환한 실제 로컬 파일 등록')
    register.add_argument('--run', required=True, type=Path)
    register.add_argument('--page', required=True)
    register.add_argument('--panel', required=True, type=int)
    register.add_argument('--image', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'extract':
            result = extract(args.repo, args.target, args.run, reuse=args.reuse, page=args.page)
        elif args.command == 'prompts':
            result = prompts(args.run)
            result = {k: v for k, v in result.items() if k != 'jobs'} | {'file': str(args.run / 'prompts.json')}
        elif args.command == 'register-image':
            result = register_image(args.run, args.page, args.panel, args.image)
        elif args.command == 'build':
            result = {'preview': str(build(args.run)), **check(args.run, 'images')}
        elif args.command == 'check':
            result = check(args.run, args.phase)
        elif args.command == 'link-notes':
            result = link_notes(args.run, dry_run=args.dry_run, repair_fragments=args.repair_fragments)
        elif args.command == 'link-status':
            from comic_browser_evidence import link_status
            result = link_status(args.run)
        elif args.command == 'fingerprints':
            result = fingerprints(args.run, args.page)
        elif args.command == 'reuse-reviews':
            result = reuse_reviews(args.run, args.previous, dry_run=args.dry_run)
        elif args.command == 'record-review':
            result = record_review(args.run, args.report)
        elif args.command == 'browser-check':
            from comic_browser import browser_check
            result = browser_check(args.run, args.stage, args.out, comic_only=args.comic_only)
        elif args.command == 'rehearse':
            from comic_rehearsal import rehearse
            result = rehearse(args.run, args.out)
        else:
            result = publish(args.run, link_notes=not args.no_link, rehearsal=args.rehearsal)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command in ('browser-check', 'rehearse') and result['status'] != 'passed')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        import json
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
