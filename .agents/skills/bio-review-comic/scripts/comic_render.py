"""Render the inherited note shell and publish immutable local versions."""
from __future__ import annotations

from datetime import datetime, timezone
import html
import os
from pathlib import Path
import re
import shutil
import uuid
from urllib.parse import quote, unquote, urlsplit

from comic_browser_evidence import LINK_RECORD, preview_evidence, save_link_status
from comic_contract import CSS, TEMPLATE, assets_for, check, jobs_for, load, local, raster, read, state, validate_storyboard, write
from comic_source import digest, existing, nfc, parse


def esc(value):
    return html.escape(str(value), quote=True)


def relative(path, directory):
    return quote(os.path.relpath(path, directory).replace(os.sep, '/'), safe='/.-_')


def render(run, output, image_root=None):
    run, src, book = validate_storyboard(run)
    jobs = jobs_for(src, book)
    assets = assets_for(run, jobs)
    image_root = Path(image_root) if image_root else run
    output = Path(output)
    sections, titles, section_ids = {}, {}, {}
    topics = {t['id']: t for t in src['topics']}
    held = sum(p['status'] == 'held' for p in book['pages'])
    characters = {c['id']: c for c in book.get('characters', [])}
    for page in book['pages']:
        topic = topics[page['id']]
        section = topic['section']
        # Keep source section IDs when valid; the per-topic deep links are unchanged.
        section_ids.setdefault(section, f'comic-section-{len(section_ids) + 1}')
        titles[section] = topic['section_title']
        source_href = relative(Path(src['path']), output.parent) + '#' + quote(page['id'], safe='')
        back = f'<p class="comic-source"><a href="{esc(source_href)}" target="_self">원본 정리노트 보기</a></p>'
        title = f'<h3>{esc(page["title"])}</h3>'
        if page['status'] == 'held':
            content = f'<div class="layer warn"><span class="layer-title">이 페이지는 제작 보류 중이에요</span><p>{esc(page["reason"])}</p></div>'
            summary = '<div class="sum" hidden><p class="sum-lead">이 페이지는 아직 제작을 마치지 못했어요.</p></div>'
        else:
            evidence = {e['id']: e for e in topic['evidence']}

            def labels(refs):
                values = list(dict.fromkeys(evidence[r]['label'] for r in refs if evidence[r]['scope'] == 'supplement'))
                return ''.join(f'<span class="badge supp">{esc(value)}</span>' for value in values)

            panels = []
            for n, panel in enumerate(page['panels'], 1):
                asset = assets[f"{page['id']}/{n:02}"]
                image_href = relative(image_root / asset['file'], output.parent)
                dialogue = []
                for line in panel.get('dialogue', []):
                    speaker = line['speaker']
                    side = 'left' if page['narrative']['cast'].index(speaker) % 2 == 0 else 'right'
                    offscreen = speaker not in panel.get('characters', [])
                    dialogue.append(f'<p class="comic-dialogue comic-voice-{side}" data-speaker="{esc(speaker)}" data-offscreen="{str(offscreen).lower()}"><span class="comic-speaker">{esc(characters[speaker]["name"])}</span>{esc(line["text"])}</p>')
                balloons = '<div class="comic-balloon-layer">' + ''.join(dialogue) + '</div>' if dialogue else ''
                # A growing top row keeps readable speech clear of the lower 60% art.
                # Unlike fixed absolute coordinates this also works at 375px and zoom.
                space = f'<div class="comic-art-space" style="aspect-ratio:{asset["width"]} / {asset["height"] * 0.64:g}" aria-hidden="true"></div>' if dialogue else ''
                analogy = page['analogy']
                explanation = ''
                if n == analogy['panels'][0]:
                    pairs = ' · '.join(labels(m['evidence']) + esc(f"{m['familiar']} → {m['biology']}") for m in analogy['mapping'])
                    explanation += '<p class="comic-analogy"><strong>비유 연결</strong> ' + pairs + '</p>'
                if n == analogy['limit_panel']:
                    explanation += '<p class="comic-limit"><strong>여기까지의 비유예요</strong> ' + esc(analogy['limit']) + '</p>'
                panels.append(f'''<li class="comic-panel" data-panel="{n}">
<figure><div class="comic-scene">{balloons}<img src="{esc(image_href)}" alt="{esc(panel['alt'])}" width="{asset['width']}" height="{asset['height']}" loading="lazy" decoding="async">{space}</div>
<figcaption><span class="comic-number">{n}컷</span>{labels(panel['evidence'])}<p class="comic-caption">{esc(panel['caption'])}</p>{explanation}</figcaption></figure></li>''')
            content = '<p class="comic-question">' + esc(page['question']) + '</p><ol class="comic-strip" aria-label="순서대로 읽는 학습만화">' + ''.join(panels) + '</ol>'
            terms = ''.join(f'<dt>{esc(t["term"])}</dt><dd>{labels(t["evidence"])}{esc(t["text"])}</dd>' for t in page.get('terms', []))
            summary = f'<div class="sum" hidden>{labels(page["summary"]["evidence"])}<p class="sum-lead">{esc(page["summary"]["text"])}</p>'
            if terms:
                summary += f'<p class="panel-label">용어</p><dl class="terms">{terms}</dl>'
            summary += '</div>'
        article = f'<article class="topic" id="{esc(page["id"])}">{title}{content}{back}{summary}</article>'
        sections.setdefault(section, []).append(article)
    sections_html = '\n'.join(f'<section id="{section_ids[s]}"><h2>{esc(titles[s])}</h2>{"".join(items)}</section>' for s, items in sections.items())
    toc = ''.join(f'<a href="#{section_ids[s]}">{esc(titles[s])}</a>' for s in sections)
    count = len(book['pages'])
    status = f'{count - held}/{count}페이지 완료 · 일부 보류' if held else f'{count}페이지 · 페이지마다 4~8컷'
    if src.get('selection'):
        status = '선택 페이지 샘플 · ' + status
    values = {'PAGE_TITLE': esc(book['title']), 'DESCRIPTION': esc(f"{src['range']} 수업 학습만화. {status}"), 'BRAND': '학습만화', 'TITLE': esc(book['title']), 'SUBTITLE': esc(status + '. 그림과 대사를 따라 읽고 원본 정리노트에서 확인해요.'), 'TOC': toc, 'SECTIONS': sections_html, 'FOOTER': esc('일부 페이지 제작 보류' if held else '정리노트의 수업 내용을 바탕으로 만든 학습만화'), 'SCRIPTS': '', 'RANGE': esc(src['range'])}
    template = TEMPLATE.read_text(encoding='utf-8')
    slots = set(re.findall(r'\{\{([A-Z_]+)\}\}', template))
    if slots - values.keys():
        raise ValueError('알 수 없는 만화 템플릿 슬롯: ' + ', '.join(sorted(slots - values.keys())))
    text = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: values[m[1]], template)
    return text.replace('</head>', '<style id="comic-style">\n' + CSS.read_text(encoding='utf-8') + '\n</style>\n</head>')


def validate_output(path):
    path = Path(path)
    root = parse(path.read_text(encoding='utf-8'))
    for node in root.walk():
        if node.tag not in ('img', 'a'):
            continue
        href = node.attrs.get('src' if node.tag == 'img' else 'href', '')
        url = urlsplit(href)
        if url.scheme or url.netloc:
            raise ValueError(f'생성 본문의 외부 링크·그림 미지원: {href}')
        target = path.parent / unquote(url.path) if url.path else path
        if not target.is_file():
            raise ValueError(f'생성 HTML 연결 파일 없음: {href}')
        if node.tag == 'img':
            raster(target)
        if node.tag == 'a' and url.fragment:
            ids = {n.attrs.get('id') for n in parse(target.read_text(encoding='utf-8')).walk()}
            if unquote(url.fragment) not in ids:
                raise ValueError(f'생성 HTML 연결 주제 없음: {href}')


def build(run):
    run = Path(run).resolve()
    output = run / 'preview.html'
    text = render(run, output)
    temp = output.with_suffix('.html.tmp')
    temp.write_text(text, encoding='utf-8')
    os.replace(temp, output)
    validate_output(output)
    return output


def archive_html(text, original_directory, archive_directory):
    """Preserve usable relative resources when moving a previous HTML deeper."""
    def rebase(match):
        attribute, delimiter, raw = match.groups()
        value = html.unescape(raw)
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path:
            return match[0]
        target = Path(original_directory) / unquote(url.path)
        value = relative(target, archive_directory)
        if url.query:
            value += '?' + url.query
        if url.fragment:
            value += '#' + url.fragment
        return attribute + '=' + delimiter + esc(value) + delimiter
    return re.sub(r'''\b(href|src)=(['"])(.*?)\2''', rebase, text)


def publication_paths(src):
    note = existing(src['path'])
    suffix = nfc(note.name).removeprefix('정리노트_')
    filename = '학습만화_' + suffix
    if src.get('selection'):
        filename = Path(filename).stem + '_샘플_' + src['selection'][0] + '.html'
    root = note.parent / '.assets' / ('자료_' + Path(filename).stem)
    normalized = [p for p in note.parent.iterdir() if nfc(p.name) == filename]
    if len(normalized) > 1:
        raise ValueError('발행 대상 NFC/NFD 이름 중복')
    return note, normalized[0] if normalized else note.parent / filename, root


def new_version(root):
    return root / 'versions' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])


def reusable_publication(record, output, src, assets):
    try:
        version = Path(record['version'])
        if Path(record['html']) != output or digest(output.read_bytes()) != record['html_sha256']:
            return False
        for asset in assets.values():
            if raster(local(version, asset['file']))['sha256'] != asset['sha256']:
                return False
        if src.get('review_version'):
            check(version, 'reviewed')
        if src.get('browser_gate_version'):
            archived = version / 'checks' / 'automatic-preview' / 'report.json'
            if digest(archived.read_bytes()) != record.get('preview_report_sha256'):
                return False
            for view in read(archived)['views']:
                if digest(local(archived.parent, view['screenshot']).read_bytes()) != view['screenshot_sha256']:
                    return False
        validate_output(output)
    except (ValueError, OSError, KeyError, TypeError):
        return False
    return True


def _publish_comic(run, candidate=None):
    run = Path(run).resolve()
    result = check(run, 'browser')
    if not result['ready']:
        raise ValueError('모든 페이지가 보류 상태라 발행할 학습만화가 없습니다.')
    _, src, book = load(run)
    preview = run / 'preview.html'
    if not preview.exists() or preview.read_text(encoding='utf-8') != render(run, preview):
        raise ValueError('브라우저 확인 대상 preview.html이 없거나 변경됨. build 후 재확인하세요.')
    current = state(run)['browser']
    record = read(run / 'publication.json') if (run / 'publication.json').exists() else {}
    _, output, root = publication_paths(src)
    assets = assets_for(run, jobs_for(src, book))
    if (record.get('fingerprint') == current and (candidate is None or candidate.matches(record))
            and reusable_publication(record, output, src, assets)):
        version = Path(record['version'])
        if candidate is not None:
            candidate.recheck()
            candidate.archive(version)
            record = {**record, 'rehearsal_report_sha256': candidate.report_sha256}
            write(run / 'publication.json', record)
        # The HTML may have committed before a transient index-write failure.
        write(version / 'publication.json', record)
        write(root / 'latest.json', record)
        return record
    evidence = preview_evidence(run) if src.get('browser_gate_version') else None
    if candidate is not None and evidence is not None:
        candidate.check_preview(evidence)
    version = candidate.version if candidate is not None else new_version(root)
    version.mkdir(parents=True, exist_ok=False)
    committed = False
    try:
        if evidence is not None:
            checks = version / 'checks' / 'automatic-preview'
            checks.mkdir(parents=True)
            for name, raw in evidence.items():
                (checks / name).write_bytes(raw)
        for name in ('source.json', 'source.html', 'storyboard.json', 'images.json', 'review.json'):
            shutil.copy2(run / name, version / name)
        review = read(run / 'review.json')
        if src.get('review_version'):
            for page in book['pages']:
                if page['status'] == 'ready':
                    relative_name = review['pages'][page['id']]['origin']['report']
                    dest = local(version, relative_name)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(local(run, relative_name), dest)
        for view in review['browser']['views']:
            relative_name = view['screenshot']
            dest = local(version, relative_name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local(run, relative_name), dest)
        for key, asset in assets.items():
            dest = local(version, asset['file'])
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate.images[key] if candidate else local(run, asset['file']), dest)
            if candidate and raster(dest)['sha256'] != asset['sha256']:
                raise ValueError(f'리허설 그림 변경: {key}')
        raw = candidate.comic_bytes if candidate else render(run, output, image_root=version).encode('utf-8')
        if candidate is not None:
            candidate.archive(version)
        if output.exists():
            (version / 'previous.html').write_text(archive_html(output.read_text(encoding='utf-8'), output.parent, version), encoding='utf-8')
        temporary = output.with_name('.' + output.name + '.' + uuid.uuid4().hex + '.tmp')
        try:
            temporary.write_bytes(raw)
            validate_output(temporary)
            # Recheck source/reviews after staging, before the one atomic replacement.
            check(run, 'browser')
            if evidence is not None and preview_evidence(run) != evidence:
                raise ValueError('발행 준비 중 미리보기 증거 변경: 다시 발행하세요.')
            if src.get('review_version'):
                check(version, 'reviewed')
            if candidate is not None:
                candidate.recheck()
            os.replace(temporary, output)
            committed = True
        finally:
            if temporary.exists():
                temporary.unlink()
        record = {**result, 'html': str(output), 'version': str(version), 'fingerprint': current, 'html_sha256': digest(output.read_bytes())}
        if evidence is not None:
            record['preview_report_sha256'] = digest(evidence['report.json'])
        if candidate is not None:
            record['rehearsal_report_sha256'] = candidate.report_sha256
        write(run / 'publication.json', record)
        write(version / 'publication.json', record)
        write(root / 'latest.json', record)
        return record
    except Exception:
        # After replacement this version is referenced by the actual public HTML.
        if not committed:
            shutil.rmtree(version)
        raise


def publish(run, link_notes=True, *, rehearsal=None):
    """Publication commits first; contextual linking is independently retryable."""
    candidate = None
    if rehearsal is not None:
        if not link_notes:
            raise ValueError('--rehearsal은 원본 연결을 포함한 발행에만 사용하세요.')
        from comic_rehearsal import load_rehearsal
        candidate = load_rehearsal(run, rehearsal)
    result = _publish_comic(run, candidate)
    version = Path(result['version'])
    if (result.get('preview_report_sha256') or candidate) and not (version / LINK_RECORD).exists():
        save_link_status(version, 'pending' if link_notes else 'skipped', stage='insertion')
    if link_notes:
        from comic_links import link_notes as connect
        try:
            linked = candidate.apply_note(version) if candidate else connect(run)
        except (ValueError, OSError, KeyError) as exc:
            linked = {'status': 'failed', 'error': str(exc), 'retry': 'link-notes --run RUN'}
            if candidate is not None:
                save_link_status(version, 'failed', stage='insertion', error=str(exc))
        result = {**result, 'note_links': linked}
        # Keep evidence of linking beside the archived production inputs.
        write(version / 'note-links-result.json', linked)
    if (version / LINK_RECORD).is_file():
        from comic_browser_evidence import link_status
        result = {**result, 'link_verification': link_status(version)}
    return result
