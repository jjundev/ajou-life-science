"""Storyboard, source, image, and review invariants; no semantic-review claims."""
from __future__ import annotations

import json
from pathlib import Path
import struct

from comic_source import compact, digest, existing

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / 'assets' / 'comic-template.html'
CSS = SKILL / 'assets' / 'comic.css'


def read(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'JSON 읽기 실패: {path}: {exc}') from exc


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fingerprint(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def local(run, relative):
    path = Path(run) / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(Path(run).resolve()):
        raise ValueError(f'실행 폴더 밖 파일: {relative}')
    return path


def raster(path):
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f'그림 파일 없음: {path}') from exc
    width = height = 0
    ext = ''
    if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) >= 33 and data[12:16] == b'IHDR':
        width, height = struct.unpack('>II', data[16:24]); ext = '.png'
    elif data.startswith(b'\xff\xd8'):
        i = 2
        while i + 4 <= len(data):
            if data[i] != 255:
                break
            marker = data[i + 1]; i += 2
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            size = int.from_bytes(data[i:i + 2], 'big')
            if size < 2 or i + size > len(data):
                break
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF) and size >= 7:
                height, width = struct.unpack('>HH', data[i + 3:i + 7]); ext = '.jpg'; break
            i += size
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        mode = data[12:16]
        if mode == b'VP8X' and len(data) >= 30:
            width = int.from_bytes(data[24:27], 'little') + 1
            height = int.from_bytes(data[27:30], 'little') + 1
        elif mode == b'VP8 ' and len(data) >= 30 and data[23:26] == b'\x9d\x01\x2a':
            width, height = (v & 0x3fff for v in struct.unpack('<HH', data[26:30]))
        elif mode == b'VP8L' and len(data) >= 25 and data[20] == 0x2f:
            bits = int.from_bytes(data[21:25], 'little')
            width, height = (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
        ext = '.webp'
    if min(width, height) < 256 or not ext:
        raise ValueError(f'유효한 PNG/JPEG/WebP 그림(짧은 변 256px 이상)이 아닙니다: {path}')
    return {'sha256': digest(data), 'width': width, 'height': height, 'extension': ext}


def load(run):
    run = Path(run).resolve()
    src, book = read(run / 'source.json'), read(run / 'storyboard.json')
    try:
        path = existing(src['path'])
    except ValueError as exc:
        raise ValueError('원본 정리노트 없음. 이전 결과를 보존하고 원본 경로를 확인하세요.') from exc
    if digest(path.read_bytes()) != src['sha256']:
        raise ValueError('원본 정리노트 변경: 새 RUN으로 extract --reuse 이전RUN을 실행하세요.')
    if book.get('schema_version') != 1 or book.get('source_sha256') != src['sha256']:
        raise ValueError('콘티와 원본 지문 불일치')
    snapshot = run / 'source.html'
    if not snapshot.is_file() or digest(snapshot.read_bytes()) != src['sha256']:
        raise ValueError('원본 스냅샷 변경 또는 누락')
    # Also binds extracted evidence/classification to the immutable original snapshot.
    from comic_source import inventory
    actual = inventory(path, src['repo'])
    if src != actual:
        raise ValueError('원본 근거 목록 변경: source.json을 편집하지 마세요.')
    return run, src, book


def validate_storyboard(run):
    run, src, book = load(run)
    if not compact(book.get('style', '')):
        raise ValueError('공통 그림 스타일 없음')
    expected = [t for t in src['topics'] if t['include']]
    pages = book.get('pages', [])
    if [p.get('id') for p in pages] != [t['id'] for t in expected]:
        raise ValueError('원본 페이지 순서·대응 누락 또는 중복')
    for page, topic in zip(pages, expected):
        pid = page['id']
        if page.get('source_topic_sha256') != topic['sha256']:
            raise ValueError(f'{pid}: 원본 페이지 변경')
        if page.get('status') == 'held':
            if not compact(page.get('reason', '')):
                raise ValueError(f'{pid}: 보류 이유 없음')
            continue
        if page.get('status') != 'ready':
            raise ValueError(f'{pid}: 콘티 작성 대기(draft). 완성하거나 이유와 함께 held로 표시하세요.')
        panels = page.get('panels', [])
        if not 4 <= len(panels) <= 8:
            raise ValueError(f'{pid}: 페이지마다 4~8컷 필요')
        if not compact(page.get('question', '')):
            raise ValueError(f'{pid}: 핵심 질문 없음')
        refs = {e['id'] for e in topic['evidence']}

        def validate_refs(item, label):
            values = item.get('evidence', [])
            if not isinstance(values, list) or not values or any(v not in refs for v in values):
                raise ValueError(f'{pid}: {label} 근거 없음 또는 알 수 없는 근거')

        summary = page.get('summary', {})
        if not compact(summary.get('text', '')):
            raise ValueError(f'{pid}: 페이지 요약 없음')
        validate_refs(summary, '요약')
        for term in page.get('terms', []):
            if not compact(term.get('term', '')) or not compact(term.get('text', '')):
                raise ValueError(f'{pid}: 용어 설명 비어 있음')
            validate_refs(term, '용어')
        for n, panel in enumerate(panels, 1):
            if any(not compact(panel.get(k, '')) for k in ('scene', 'caption', 'alt')):
                raise ValueError(f'{pid}/{n}: 장면·설명·대체 설명 필요')
            validate_refs(panel, f'{n}컷')
            for line in panel.get('dialogue', []):
                if not compact(line.get('speaker', '')) or not compact(line.get('text', '')):
                    raise ValueError(f'{pid}/{n}: 화자·대사 필요')
        coverage = page.get('coverage', [])
        if len(coverage) != len(refs) or {r.get('evidence') for r in coverage} != refs:
            raise ValueError(f'{pid}: 근거 coverage 누락·중복')
        for row in coverage:
            numbers = row.get('panels', [])
            if not numbers and not compact(row.get('reason', '')):
                raise ValueError(f'{pid}: 근거 생략 이유 없음')
            if any(type(n) is not int or not 1 <= n <= len(panels) or row['evidence'] not in panels[n - 1]['evidence'] for n in numbers):
                raise ValueError(f'{pid}: coverage와 실제 컷 근거 불일치')
    return run, src, book


def jobs_for(src, book):
    topics = {t['id']: t for t in src['topics']}
    jobs = []
    for page in book['pages']:
        if page['status'] != 'ready':
            continue
        evidence = {e['id']: e for e in topics[page['id']]['evidence']}
        for n, panel in enumerate(page['panels'], 1):
            facts = '\n'.join(f"- {evidence[r]['text']}" for r in panel['evidence'])
            prompt = '\n'.join([
                'Use case: illustration-story / scientific-educational',
                'Asset: one wordless panel of a Korean biology learning comic.',
                f"Shared style and continuity: {book['style']}",
                f"Page: {page['title']} | Learning question: {page['question']}",
                f"Panel {n}/{len(page['panels'])}: {panel['scene']}",
                f"Scientific meaning: {panel['caption']}",
                'Source facts; preserve scope, uncertainty, counts and directions:\n' + facts,
                'Composition: clearly readable landscape panel; warm light paper background; restrained blue accents.',
                'No text, letters, digits, labels, speech balloons, arrows with text, UI, or watermarks. Dialogue and precise notation are HTML.',
                'Show a concrete state or action. Preserve recurring subjects. No goal-directed evolution or intentional molecules.',
            ])
            jobs.append({'key': f"{page['id']}/{n:02}", 'page': page['id'], 'panel': n, 'prompt': prompt, 'prompt_sha256': digest(prompt)})
    return jobs


def assets_for(run, jobs, required=True):
    registry = read(run / 'images.json') if (run / 'images.json').exists() else {}
    found = {}
    for job in jobs:
        item = registry.get(job['key'])
        try:
            if not item or item.get('prompt_sha256') != job['prompt_sha256']:
                raise ValueError('그림 없음 또는 그림 프롬프트 변경으로 오래된 그림')
            info = raster(local(run, item['file']))
            if info['sha256'] != item.get('sha256'):
                raise ValueError('그림 파일 변경')
            found[job['key']] = {**item, **info}
        except ValueError as exc:
            if required:
                raise ValueError(f"{job['key']}: {exc}") from exc
    return found


def state(run):
    run, src, book = validate_storyboard(run)
    jobs = jobs_for(src, book)
    assets = assets_for(run, jobs)
    pages = {}
    for page in book['pages']:
        if page['status'] != 'ready':
            continue
        content = fingerprint({'page': page, 'style': book['style']})
        images = {j['key']: assets[j['key']]['sha256'] for j in jobs if j['page'] == page['id']}
        pages[page['id']] = {'content': content, 'visual': fingerprint({'content': content, 'images': images})}
    browser = fingerprint({'book': book, 'source': src['sha256'], 'images': assets, 'template': digest(TEMPLATE.read_bytes()), 'css': digest(CSS.read_bytes())})
    return {'pages': pages, 'browser': browser}


def check(run, phase='storyboard'):
    run, src, book = validate_storyboard(run)
    if phase not in ('storyboard', 'images', 'reviewed', 'browser'):
        raise ValueError(f'알 수 없는 검사 단계: {phase}')
    if phase != 'storyboard':
        assets_for(run, jobs_for(src, book))
    if phase in ('reviewed', 'browser'):
        expected = state(run)
        report = read(run / 'review.json') if (run / 'review.json').exists() else {}
        for pid, kinds in expected['pages'].items():
            for kind, fp in kinds.items():
                entry = report.get('pages', {}).get(pid, {}).get(kind, {})
                if entry.get('status') != 'passed' or entry.get('fingerprint') != fp or not entry.get('notes'):
                    raise ValueError(f'{pid}: {kind} 검토 없음 또는 변경 후 재검토 필요')
        if phase == 'browser':
            browser = report.get('browser', {})
            if browser.get('status') != 'passed' or browser.get('fingerprint') != expected['browser'] or not browser.get('notes'):
                raise ValueError('브라우저 검토 없음 또는 변경 후 재검토 필요')
            views = browser.get('views', [])
            expected_views = {(w, h, t) for w, h in ((1440, 900), (375, 812)) for t in ('light', 'dark')}
            if {(v.get('width'), v.get('height'), v.get('theme')) for v in views} != expected_views:
                raise ValueError('브라우저: 데스크톱·모바일 라이트·다크 4종 확인 필요')
            for view in views:
                raster(local(run, view.get('screenshot', '')))
    held = [{'id': p['id'], 'reason': p['reason']} for p in book['pages'] if p['status'] == 'held']
    return {'status': 'partial' if held else 'complete', 'phase': phase, 'total': len(book['pages']), 'ready': len(book['pages']) - len(held), 'held': held, 'excluded': [{'id': t['id'], 'reason': t['reason']} for t in src['topics'] if not t['include']]}
