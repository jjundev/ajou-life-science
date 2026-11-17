"""Extract → agent-authored fragments → build/check → reviewed publication."""
import argparse
from dataclasses import asdict, fields, replace
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
from mpe_contract import initial_reviews, payload_hash, validate_fragment
from mpe_source import inside, load_source, resolve_sources, sha256
from mpe_render import build_explanation, check_artifacts, artifact_hashes, dump, names
from mpe_publish import publish_explanation
from mpe_shared import SIDE, migrate_md, moves
from mpe_types import Artifacts, ExplainError

def serialized(pack):
    value = asdict(pack)
    value['path'] = str(pack.path)
    # JSON normalizes tuples to lists; compare canonical serialization on import.
    return json.loads(json.dumps(value, ensure_ascii=False))

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def extract(repo, target, run):
    repo = Path(repo).resolve()
    run = Path(run).absolute()
    if run.exists() and (run.is_symlink() or not run.is_dir() or any(run.iterdir())):
        raise ExplainError('RUN은 비어 있어야 해요')
    sources = resolve_sources(repo, target)
    run.mkdir(parents=True, exist_ok=True)
    buckets = []
    failed = False
    for source in sources:
        try:
            pack = load_source(source, repo)
            name = f'{pack.profile}-{pack.range}-{pack.slug}'
            folder = run / name
            folder.mkdir()
            (folder / 'explanations').mkdir()
            (folder / 'evidence').mkdir()
            dump(folder / 'source.json', serialized(pack))
            for p in pack.problems:
                if p.choice is None and re.search(r'class="[^"]*\bchoices\b', p.conditions_html):
                    print(f'{p.id}: 보기 모델 없음/불일치 — 정적 표시', file=sys.stderr)
            buckets.append(name)
            print('extract:', folder / 'source.json')
        except ExplainError as exc:
            failed = True
            print(f'{source}: {exc}', file=sys.stderr)
    dump(run / 'run.json', {'version': 1, 'repo': str(repo), 'targets': buckets})
    return int(failed)

def load_run(run, errors=None):
    run = Path(run).absolute()
    index = read_json(inside(run / 'run.json', run))
    repo = Path(index['repo'])
    if not repo.is_absolute() or not repo.is_dir():
        raise ExplainError('저장소 절대 경로 필요')
    items = []
    if not isinstance(index['targets'], list) or not index['targets']:
        raise ExplainError('추출 대상 없음')
    for name in index['targets']:
        try:
            folder = inside(run / name, run)
            value = read_json(inside(folder / 'source.json', run))
            source = Path(value['path'])
            if not source.is_absolute():
                raise ExplainError('추출 입력은 절대 경로여야 해요')
            pack = load_source(inside(source, repo), repo)
            if value != serialized(pack):
                raise ExplainError('추출 데이터 또는 원본 변경: extract부터 다시 실행하세요')
            items.append({'pack': pack, 'folder': folder, 'repo': repo, 'run': run})
        except (ExplainError, OSError, ValueError, KeyError, TypeError) as exc:
            if errors is None:
                raise
            errors.append(f'{name}: {exc}')
    return items

def load_fragments(item):
    folder = item['folder']
    actual = {p.stem for p in (folder / 'explanations').glob('*.html')}
    if actual != {p.id for p in item['pack'].problems}:
        raise ExplainError('모든 문항의 explanations/pN.html을 먼저 저작하세요')
    return {p.id: inside(folder / 'explanations' / f'{p.id}.html', item['run']).read_text(encoding='utf-8') for p in item['pack'].problems}

def load_artifacts(item):
    value = read_json(inside(item['folder'] / 'stage.json', item['run']))
    stage = inside(item['folder'] / value['stage'], item['run'])
    paths = [inside(stage / value[key], stage) for key in ('html', 'md', 'manifest')]
    manifest = read_json(paths[2])
    files = tuple(inside(stage / name, stage) for name in manifest['files']) + (paths[2],)
    return Artifacts(*paths, files)

def build(item, fragments):
    folder = item['folder']
    stage = folder / 'stage' / uuid.uuid4().hex
    artifacts = build_explanation(item['pack'], fragments, stage, item['repo'])
    # Evidence is copied before binding the artifact hashes; review approval comes later.
    evidence = inside(folder / 'evidence', item['run'])
    if evidence.is_dir():
        for source in evidence.rglob('*'):
            inside(source, item['run'])
            if source.is_file():
                dest = artifacts.manifest.parent / 'evidence' / source.relative_to(evidence)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
    manifest = read_json(artifacts.manifest)
    files = tuple(sorted(p for p in stage.rglob('*') if p.is_file() and p != artifacts.manifest))
    manifest['files'] = {p.relative_to(stage).as_posix(): sha256(p) for p in files}
    dump(artifacts.manifest, manifest)
    artifacts = Artifacts(artifacts.html, artifacts.md, artifacts.manifest, files + (artifacts.manifest,))
    dump(folder / 'stage.json', {'stage': stage.relative_to(folder).as_posix(),
                               'html': artifacts.html.name, 'md': artifacts.md.relative_to(stage).as_posix(),
                               'manifest': artifacts.manifest.relative_to(stage).as_posix()})
    review = initial_reviews(item['pack'], fragments)
    review['artifact_hashes'] = artifact_hashes(artifacts)
    dump(folder / 'review.json', review)
    print('build:', artifacts.html)

REVIEW_KINDS = ('source_visual', 'content', 'independent', 'browser')
REVIEW_STATUSES = ('pass', 'fail', 'disputed', 'not_run')

def current_review(item, fragments):
    review = read_json(inside(item['folder'] / 'review.json', item['run']))
    if review.get('input_hash') != payload_hash(item['pack'], fragments):
        raise ExplainError('설명 조각 또는 원본 변경: build부터 다시 실행하세요')
    return review

def review_status(item):
    """review.json을 통째로 읽지 않도록 검토별 상태와 통과하지 못한 항목만 한 줄씩 낸다."""
    review = read_json(inside(item['folder'] / 'review.json', item['run']))
    lines = []
    for kind in REVIEW_KINDS:
        part = review.get(kind) or {}
        items = part.get('items') if isinstance(part.get('items'), dict) else {}
        bad = sorted(k for k, v in items.items() if not isinstance(v, dict) or v.get('status') != 'pass')
        line = f"{kind}: {part.get('status', 'not_run')}"
        if items:
            line += f" (항목 {len(items) - len(bad)}/{len(items)} pass)"
        if bad:
            line += ' — ' + ', '.join(bad[:12]) + (f' 외 {len(bad) - 12}건' if len(bad) > 12 else '')
        lines.append(line)
    return lines

def card_answer(problem):
    if problem.choice:
        return problem.choice.answer
    if problem.short_answer:
        return problem.short_answer.canonical
    return problem.reference_answer

def _plain(answer):
    return re.sub(r'[\s()`.]', '', str(answer)).lower()

def compare_answers(item, path):
    """독립 검산자의 답(TSV: 문항 id, 답)을 카드 정답과 대조한다. 검산자는 정답을 보지 않으므로 대조는 컨트롤러가 여기서 한다."""
    got = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.split('\t')]
        if len(cells) >= 2 and cells[0] and not cells[0].startswith('#'):
            got[cells[0].split(':', 1)[0]] = cells[1]
    problems = item['pack'].problems
    missing = [p.id for p in problems if p.id not in got]
    wrong = [f"{p.id} ({p.source}): 검산 {got[p.id]} / 카드 {card_answer(p)}" for p in problems
             if p.id in got and _plain(got[p.id]) != _plain(card_answer(p))]
    lines = [f"독립 검산 대조: {len(problems) - len(missing) - len(wrong)}/{len(problems)} 일치 · 불일치 {len(wrong)} · 답 없음 {len(missing)}"]
    lines += wrong
    if missing:
        lines.append('답 없음: ' + ', '.join(missing))
    return lines, bool(wrong or missing)

def sync_evidence(item, fragments):
    """Copy evidence written after build into the current stage and rebind hashes; reviews stay as recorded.

    Only files under the stage's evidence folder may change. Any other stage change means the
    rendered output differs from what was reviewed, so the caller must build and review again.
    """
    review = current_review(item, fragments)
    artifacts = load_artifacts(item)
    stage = artifacts.html.parent
    evidence_rel = (artifacts.manifest.parent / 'evidence').relative_to(stage).as_posix() + '/'
    manifest_rel = artifacts.manifest.relative_to(stage).as_posix()
    recorded = review.get('artifact_hashes')
    if not isinstance(recorded, dict):
        raise ExplainError('review.json에 artifact_hashes 없음: build부터 다시 실행하세요')
    fixed = lambda rel: rel != manifest_rel and not rel.startswith(evidence_rel)
    now = {p.relative_to(stage).as_posix(): sha256(p) for p in stage.rglob('*') if p.is_file()}
    changed = sorted(rel for rel in set(recorded) | set(now) if fixed(rel) and recorded.get(rel) != now.get(rel))
    if changed:
        raise ExplainError('evidence 밖 stage 파일이 build 이후 바뀜: build와 검토를 다시 하세요: ' + ', '.join(changed[:5]))
    target = stage / evidence_rel
    if target.exists():
        shutil.rmtree(target)
    source = inside(item['folder'] / 'evidence', item['run'])
    for path in source.rglob('*') if source.is_dir() else ():
        inside(path, item['run'])
        if path.is_file():
            dest = target / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    manifest = read_json(artifacts.manifest)
    files = sorted(p for p in stage.rglob('*') if p.is_file() and p != artifacts.manifest)
    manifest['files'] = {p.relative_to(stage).as_posix(): sha256(p) for p in files}
    dump(artifacts.manifest, manifest)
    review['artifact_hashes'] = artifact_hashes(load_artifacts(item))
    dump(item['folder'] / 'review.json', review)
    print(f'sync-evidence: evidence {sum(1 for p in target.rglob("*") if p.is_file()) if target.is_dir() else 0}개 반영, 검토 기록 유지')

def _entry_errors(entry, label):
    if not isinstance(entry, dict):
        return [f'{label}: 객체가 아님']
    errors = []
    if entry.get('status') not in REVIEW_STATUSES:
        errors.append(f'{label}: status는 {"/".join(REVIEW_STATUSES)} 중 하나')
    if any(not isinstance(entry.get(k), str) for k in ('reviewer', 'evidence')):
        errors.append(f'{label}: reviewer·evidence 문자열 필요')
    return errors

def review_merge(item, fragments, kind, part, add_references=()):
    """Replace one review kind (and optionally add reference hashes) without rewriting the rest by hand."""
    review = current_review(item, fragments)
    if kind is not None:
        if kind not in REVIEW_KINDS:
            raise ExplainError(f'검토 종류는 {", ".join(REVIEW_KINDS)} 중 하나')
        value = part.get(kind, part) if isinstance(part, dict) else part
        errors = _entry_errors(value, kind)
        if kind in ('content', 'independent') and not errors:
            expected = set(review[kind]['items'])
            items = value.get('items')
            if not isinstance(items, dict) or set(items) != expected:
                errors.append(f'{kind}: items 키는 {sorted(expected)}와 같아야 해요')
            else:
                for key, entry in items.items():
                    errors += _entry_errors(entry, f'{kind}.{key}')
            if kind == 'content' and 'note_link_exceptions' not in value:
                value = {**value, 'note_link_exceptions': review['content'].get('note_link_exceptions', {})}
        if errors:
            raise ExplainError(' / '.join(errors))
        review[kind] = value
    references = [r for r in review.get('references', []) if isinstance(r, dict)]
    for path in add_references:
        path = inside(Path(path).resolve(), item['repo'])
        if not path.is_file():
            raise ExplainError(f'참조 자료 없음: {path}')
        references = [r for r in references if Path(r.get('path', '')) != path]
        references.append({'path': str(path), 'sha256': sha256(path)})
    review['references'] = references
    dump(item['folder'] / 'review.json', review)
    print(f'review-merge: {kind or "references"} 기록' + (f', 참조 {len(add_references)}개' if add_references else ''))

def import_blind(item, fragments, ledger_path):
    """Carry the forecast step-7 blind solve into the independent review when nothing changed since."""
    pack = item['pack']
    if pack.profile != 'forecast':
        raise ExplainError('import-blind는 웹과제 예상(forecast)에만 쓸 수 있어요')
    review = current_review(item, fragments)
    match = re.search(r'_v(\d+)\.html$', pack.path.name)
    src = pack.path.parent / '.pack' / f'v{match.group(1)}'
    ledger_path = Path(ledger_path).resolve()
    ledger = read_json(ledger_path)
    if ledger.get('version') != 1 or Path(ledger.get('src', '')).resolve() != src.resolve():
        raise ExplainError(f'ledger가 이 세트({src})의 기록이 아니에요')
    key = read_json(src / 'pack.json')['answer_key']
    if set(key) != {p.id for p in pack.problems}:
        raise ExplainError('answer_key와 해설 문항 집합이 달라요')
    errors, rows, items = [], [], {}
    for p in pack.problems:
        entry = ledger['cards'].get(p.id)
        card = src / 'cards' / f'{p.id}.html'
        if p.subparts != ('main',):
            errors.append(f'{p.id}: 소문항이 있는 문항은 승계하지 않아요')
            continue
        if entry is None:
            errors.append(f'{p.id}: 블라인드 기록 없음')
            continue
        if entry.get('sha256') != sha256(card):
            errors.append(f'{p.id}: 블라인드 이후 카드 변경')
        if entry.get('answer') != key[p.id] or (p.choice is not None and p.choice.answer != key[p.id]):
            errors.append(f'{p.id}: 블라인드 답 {entry.get("answer") or "없음"} ≠ answer_key {key[p.id]}')
        if entry.get('objection'):
            errors.append(f'{p.id}: 이의 — {entry["objection"]}')
        types = re.search(r'data-types="([^"]*)"', card.read_text(encoding='utf-8'))
        method = 'exact' if types and '계산' in types.group(1).split() else 'qualitative'
        reviewer = f'웹과제 예상 7단계 블라인드 리뷰어(정답 비공개, {entry.get("round")}회차)'
        items[f'{p.id}:main'] = {
            'status': 'pass', 'reviewer': reviewer, 'evidence': f'evidence/independent-blind.md#{p.id}',
            'method': method,
            'conclusion': f'정답을 보지 않은 블라인드 답 {entry.get("answer")} = answer_key {key[p.id]}, 이의 없음'}
        rows.append(f'| <a id="{p.id}"></a>{p.id} | {entry.get("answer")} | {key[p.id]} | {entry.get("round")} | '
                    f'{entry.get("basis", "")} | {entry.get("steps", "")} | {entry.get("level", "")} | `{entry.get("sha256", "")[:12]}` |')
    if errors:
        raise ExplainError('블라인드 승계 거부(별도 독립 검산자가 다시 풀어야 해요): ' + ' / '.join(errors))
    evidence = inside(item['folder'] / 'evidence', item['run'])
    evidence.mkdir(exist_ok=True)
    shutil.copy2(ledger_path, evidence / 'blind-ledger.json')
    answer_files = sorted({ledger['cards'][p.id].get('answers_file', '') for p in pack.problems} - {''})
    for index, name in enumerate(answer_files, 1):
        if Path(name).is_file():
            shutil.copy2(name, evidence / f'blind-answers-{index}.md')
    (evidence / 'independent-blind.md').write_text(
        '# 독립 검산: 웹과제 예상 7단계 블라인드 풀이 승계\n\n'
        '정답·풀이를 지운 사본(blind.py)으로 별도 리뷰어가 정리노트만 근거로 풀었다. '
        '카드 해시가 블라인드 당시와 같고, 답이 answer_key와 같으며, 이의가 없는 경우에만 승계했다.\n\n'
        '| 카드 | 블라인드 답 | answer_key | 회차 | 근거 | 최소 풀이 단계 | 수준 | 카드 SHA-256 |\n'
        '|---|---|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    review['independent'] = {'status': 'pass', 'reviewer': '웹과제 예상 7단계 블라인드 리뷰어(정답 비공개)',
                             'evidence': f'evidence/independent-blind.md: {len(items)}/{len(items)} 일치, 이의 0, 카드 해시 일치',
                             'items': items}
    references = [r for r in review.get('references', []) if isinstance(r, dict)]
    cards = {str((src / 'cards' / f'{p.id}.html').resolve()) for p in pack.problems}
    references = [r for r in references if r.get('path') not in cards]
    references += [{'path': path, 'sha256': sha256(Path(path))} for path in sorted(cards)]
    review['references'] = references
    dump(item['folder'] / 'review.json', review)
    print(f'import-blind: independent {len(items)}문항 승계')
    sync_evidence(item, fragments)

# Page code (CSS, executable scripts) is layout; JSON data scripts such as the answer model are content.
CODE_RE = re.compile(r'<style\b[^>]*>.*?</style>|<script\b(?![^>]*application/json)[^>]*>.*?</script>', re.S | re.I)
# The .assets migration prefixed relative src/href values in date-folder HTML; the targets are the same files.
SIDE_URL_RE = re.compile(r'(\b(?:src|href)=["\']?)(?:\./)*(?:' + re.escape(SIDE) + '/)?', re.I)

def unside(text):
    """Drop a leading ./ and .assets/ from relative src/href values."""
    return SIDE_URL_RE.sub(r'\1', text)

def same_problems(old, new):
    """Problems equal up to .assets-prefixed URLs."""
    fix = lambda v: unside(v) if isinstance(v, str) else tuple(map(fix, v)) if isinstance(v, tuple) else v
    norm = lambda p: replace(p, **{f.name: fix(getattr(p, f.name)) for f in fields(p)})
    return tuple(map(norm, old)) == tuple(map(norm, new))

def git_blob(path, digest):
    """Bytes of the committed version of path whose SHA-256 is digest, or None. path may since be deleted."""
    git = lambda *args: subprocess.run(['git', *args], cwd=path.parent, capture_output=True, check=True).stdout
    try:
        commits = git('log', '--format=%H', '--', path.name).decode().split()
    except (OSError, subprocess.CalledProcessError):
        return None
    for commit in commits:
        try:
            data = git('show', f'{commit}:./{path.name}')
        except (OSError, subprocess.CalledProcessError):
            continue  # the commit that deleted or moved the file
        if hashlib.sha256(data).hexdigest() == digest:
            return data
    return None

def published_source(pack, digest):
    """The review source as it was when published, loaded from its git blob."""
    data = git_blob(pack.path, digest) if pack.profile == 'review' else None
    if data is None:
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / pack.path.parent.name / pack.path.name
            path.parent.mkdir()
            path.write_bytes(data)
            return load_source(path, Path(tmp))
    except (OSError, ExplainError):
        return None

def carried_references(references, old_repo, repo):
    """Rebase reference paths onto this checkout; accept files changed only in page code or by the .assets move."""
    carried, notes = [], []
    text = lambda data: data.decode('utf-8', 'replace')
    strip = lambda data: unside(CODE_RE.sub('', text(data)))
    for reference in references:
        path = Path(reference['path'])
        if path.is_relative_to(old_repo):
            path = repo / path.relative_to(old_repo)
        reference = {**reference, 'path': str(path)}
        side = path.parent / SIDE / path.name
        if not path.exists() and moves(path.name) and side.is_file():
            # A date-folder side file moved into .assets/; the move rewrote a moved MD's links once.
            old = git_blob(path, reference['sha256'])
            moved = old is not None and (migrate_md(text(old)) if path.suffix == '.md' else text(old)) == text(side.read_bytes())
            if moved:
                reference = {**reference, 'path': str(side), 'sha256': sha256(side)}
                notes.append(f'참조 자료는 {SIDE}/로 옮겨졌을 뿐이에요: {path.name}')
            else:
                notes.append(f'참조 자료 변경: 검토를 다시 하세요: {SIDE}/{path.name}')
        elif not path.is_file():
            notes.append(f'참조 자료 없음: 검토를 다시 하세요: {path.name}')
        elif sha256(path) != reference['sha256']:
            old = git_blob(path, reference['sha256'])
            if old is not None and strip(old) == strip(path.read_bytes()):
                reference['sha256'] = sha256(path)
                notes.append(f'참조 자료는 스타일·스크립트·자산 경로만 바뀌었어요: {path.name}')
            else:
                notes.append(f'참조 자료 변경: 검토를 다시 하세요: {path.name}')
        carried.append(reference)
    return carried, notes

def rerender(repo, target, run):
    """Rebuild published packs with the current template from their published fragments and evidence."""
    if extract(repo, target, run):
        return 1
    failed = False
    for item in load_run(run):
        try:
            pack, folder = item['pack'], item['folder']
            data = pack.path.parent / names(pack)[2]
            published = data / 'fragments'
            if not published.is_dir() or {p.stem for p in published.glob('*.html')} != {p.id for p in pack.problems}:
                raise ExplainError('발행된 조각 없음/불일치: 정상 저작 절차를 쓰세요')
            for p in pack.problems:
                shutil.copy2(inside(published / f'{p.id}.html', item['repo']), folder / 'explanations' / f'{p.id}.html')
            if (data / 'evidence').is_dir():
                shutil.copytree(inside(data / 'evidence', item['repo']), folder / 'evidence', dirs_exist_ok=True)
            fragments = load_fragments(item)
            build(item, fragments)
            stored = data / 'validation.json'
            stored = read_json(inside(stored, item['repo'])) if stored.is_file() else {}
            manifest = read_json(inside(data / 'manifest.json', item['repo'])) if stored else {}
            # The payload hash covers source and fragments, not the template, so content reviews stay valid.
            same = stored.get('input_hash') == payload_hash(pack, fragments)
            note = ''
            if not same and stored.get('input_hash'):
                # A source edited only outside its cards (e.g. page CSS) or by the .assets move keeps the same problems.
                digest = manifest.get('source_sha256', '')
                old = published_source(pack, digest)
                same = (old is not None and same_problems(old.problems, pack.problems)
                        and payload_hash(replace(pack, sha256=digest), fragments) == stored['input_hash'])
                note = '원본 파일은 바뀌었지만 문항 내용은 같아요: ' if same else ''
            if same:
                review = read_json(folder / 'review.json')
                for key in ('content', 'independent'):
                    review[key] = stored[key]
                review['references'], notes = carried_references(stored['references'], Path(manifest['repo']), item['repo'])
                dump(folder / 'review.json', review)
                for line in notes:
                    print('rerender:', line)
                print(f'rerender: {note}content·independent 재사용, source_visual·browser 재검토 필요')
            else:
                print('rerender: 입력 변경: 네 검토 모두 다시 필요')
        except (ExplainError, OSError, ValueError, KeyError, TypeError) as exc:
            failed = True
            print(f'{folder.name}: {exc}', file=sys.stderr)
    return int(failed)

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    extraction = commands.add_parser('extract')
    extraction.add_argument('--repo', type=Path, required=True)
    extraction.add_argument('--target')
    extraction.add_argument('--run', type=Path, required=True)
    rerendering = commands.add_parser('rerender')
    rerendering.add_argument('--repo', type=Path, required=True)
    rerendering.add_argument('--target', required=True)
    rerendering.add_argument('--run', type=Path, required=True)
    for name in ('build', 'check', 'publish', 'sync-evidence'):
        commands.add_parser(name).add_argument('--run', type=Path, required=True)
    merging = commands.add_parser('review-merge')
    merging.add_argument('--run', type=Path, required=True)
    merging.add_argument('--kind', choices=REVIEW_KINDS)
    merging.add_argument('--from', dest='part', type=Path, help='해당 검토 객체 JSON(또는 {kind: 객체})')
    merging.add_argument('--add-reference', action='append', default=[], type=Path,
                         help='읽은 참조 자료(절대 경로·SHA-256을 references에 기록, 반복 가능)')
    blinding = commands.add_parser('import-blind')
    blinding.add_argument('--run', type=Path, required=True)
    blinding.add_argument('--ledger', type=Path, required=True)
    commands.add_parser('review-status').add_argument('--run', type=Path, required=True)
    comparing = commands.add_parser('compare-answers')
    comparing.add_argument('--run', type=Path, required=True)
    comparing.add_argument('--from', dest='answers', type=Path, required=True, help='독립 검산 답 TSV(문항 id<TAB>답)')
    browsing = commands.add_parser('browser')
    browsing.add_argument('--run', type=Path, required=True)
    browsing.add_argument('--shots', action='store_true', help='뷰포트·테마별 스크린샷 저장')
    args = parser.parse_args(argv)
    if args.command == 'review-merge' and (args.kind is None) != (args.part is None):
        parser.error('--kind와 --from은 함께 써요')
    if args.command == 'review-merge' and args.kind is None and not args.add_reference:
        parser.error('--kind/--from 또는 --add-reference가 필요해요')
    try:
        if args.command == 'extract':
            return extract(args.repo, args.target, args.run)
        if args.command == 'rerender':
            return rerender(args.repo, args.target, args.run)
        load_errors = []
        items = load_run(args.run, errors=load_errors)
        failed = bool(load_errors)
        for error in load_errors:
            print(error, file=sys.stderr)
        for item in items:
            try:
                if args.command == 'review-status':
                    print(*review_status(item), sep='\n')
                    continue
                if args.command == 'compare-answers':
                    lines, bad = compare_answers(item, args.answers)
                    print(*lines, sep='\n')
                    failed = failed or bad
                    continue
                fragments = load_fragments(item)
                if args.command == 'build':
                    build(item, fragments)
                elif args.command == 'sync-evidence':
                    sync_evidence(item, fragments)
                elif args.command == 'review-merge':
                    part = read_json(args.part) if args.part else None
                    review_merge(item, fragments, args.kind, part, args.add_reference)
                elif args.command == 'import-blind':
                    import_blind(item, fragments, args.ledger)
                elif args.command == 'browser':
                    from mpe_browser import run_browser
                    if run_browser(item, shots=args.shots):
                        failed = True
                else:
                    artifacts = load_artifacts(item)
                    if args.command == 'check':
                        errors = check_artifacts(item['pack'], artifacts)
                        errors += [e for p in item['pack'].problems for e in validate_fragment(p, fragments[p.id])]
                        if read_json(artifacts.manifest).get('input_hash') != payload_hash(item['pack'], fragments):
                            errors.append('설명 조각 변경: build부터 다시 실행하세요')
                        dump(item['folder'] / 'machine.json', {'status': 'fail' if errors else 'pass', 'errors': errors,
                                                              'artifact_hashes': artifact_hashes(artifacts)})
                        if errors:
                            raise ExplainError(' / '.join(errors))
                        print('check: machine PASS (수학·화면 검토는 별도)', artifacts.html)
                    else:
                        review = read_json(inside(item['folder'] / 'review.json', item['run']))
                        published = publish_explanation(item['pack'], artifacts, fragments, review,
                                                        item['pack'].path.parent, item['folder'] / 'backups')
                        print('publish:', published[0], 'backup:', item['folder'] / 'backups')
            except (ExplainError, OSError, ValueError, KeyError, TypeError) as exc:
                failed = True
                print(f'{item["folder"].name}: {exc}', file=sys.stderr)
        return int(failed)
    except (ExplainError, OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
