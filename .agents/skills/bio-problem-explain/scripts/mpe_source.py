"""Select saved sources without guessing, then preserve their raw questions."""
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from mpe_types import ExplainError, Problem, SourcePack
from mpe_shared import HOMEWORK, REVIEW, Node, ReviewPdfError, read_cards, normalize_cards, parse

def nfc(value):
    return unicodedata.normalize('NFC', str(value))

def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inside(path: Path, repo: Path) -> Path:
    path = Path(path).absolute()
    try:
        path.resolve().relative_to(repo.resolve())
    except ValueError as exc:
        raise ExplainError(f'저장소 밖 경로: {path}') from exc
    # Symlinks in the resource path are refused, except the repository's own root.
    current = path
    while current != repo.absolute() and current != current.parent:
        if current.is_symlink():
            raise ExplainError(f'심볼릭 링크 입력 금지: {current}')
        current = current.parent
    return path

def existing_path(path: Path) -> Path:
    """Resolve encoded/Unicode-normalized paths component by component."""
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        candidate = current / part
        if candidate.exists():
            current = candidate
        elif current.is_dir():
            matches = [p for p in current.iterdir() if nfc(p.name) == nfc(part)]
            if len(matches) != 1:
                raise ExplainError(f'경로 없음 또는 모호함: {path}')
            current = matches[0]
        else:
            raise ExplainError(f'경로 없음: {path}')
    return current

def date_key(value):
    try:
        datetime.strptime('2000' + value, '%Y%m%d')
    except ValueError as exc:
        raise ExplainError(f'잘못된 날짜: {value}') from exc
    return value

def resolve_sources(repo: Path, target: str | None) -> tuple[Path, ...]:
    repo = repo.resolve()
    if target and target.lower().endswith('.html'):
        path = Path(target)
        path = path if path.is_absolute() else repo / path
        path = inside(path, repo)
        if not path.is_file():
            try:
                path = inside(existing_path(path), repo)
            except ExplainError as exc:
                raise ExplainError(f'대상 없음: {path}') from exc
        return (path,)
    candidates = []
    for path in repo.rglob('*.html'):
        rel = nfc(path.relative_to(repo))
        if rel.split('\\')[0].split('/')[0] not in ('복습노트',):
            continue
        for profile in (REVIEW,):
            match = re.fullmatch(profile.filename_re, nfc(path.name))
            if match:
                candidates.append((profile.name, match[1], path))
    if target and re.fullmatch(r'(?:과제|hw)\s*[1-9]\d*', target, re.I):
        raise ExplainError('과제 입력 미지원: 기존 복습문제 HTML을 선택하세요.')
    else:
        reviews = [(value, path) for kind, value, path in candidates if kind == 'review']
        if target is None:
            latest = max((value.split('-')[-1] for value, _ in reviews), default='')
            latest_candidates = [(value, path) for value, path in reviews if value.split('-')[-1] == latest]
            ranges = {value for value, _ in latest_candidates}
            if len(ranges) > 1:
                raise ExplainError('여러 후보 (최신 날짜의 통합/개별):\n' + '\n'.join(str(p) for _, p in latest_candidates))
            target = next(iter(ranges), '')
        if not re.fullmatch(r'\d{4}(?:-\d{4})?', target):
            raise ExplainError('대상 없음 또는 잘못된 대상: ' + target)
        bounds = target.split('-')
        for date in bounds:
            date_key(date)
        if len(bounds) == 2 and bounds[0] > bounds[1]:
            raise ExplainError('날짜 범위 순서 오류')
        found = [path for value, path in reviews if value == target]
        if len(bounds) == 2:
            individual = [path for value, path in reviews if '-' not in value and bounds[0] <= value <= bounds[1]]
            if found and individual:
                raise ExplainError('여러 후보 (통합/개별):\n' + '\n'.join(map(str, found + individual)))
            if not found:
                found = individual
    if not found:
        raise ExplainError('대상 없음: ' + str(target))
    by_range = {}
    for path in found:
        match = re.fullmatch((HOMEWORK if nfc(path.name).startswith('과제') else REVIEW).filename_re, nfc(path.name))
        by_range.setdefault(match[1], []).append(path)
    if any(len(group) > 1 for group in by_range.values()):
        raise ExplainError('여러 후보: HTML 경로를 명시하세요.\n' + '\n'.join(map(str, found)))
    return tuple(inside(path, repo) for path in sorted(found, key=lambda p: nfc(p.name)))

def ancestors(node, root):
    node = node.parent
    while node is not root and node is not None:
        yield node
        node = node.parent

def operation_item(text):
    return bool(re.fullmatch(r'\s*\([a-z]\)\s*(?:push|pop|enqueue|dequeue|insert|delete|append|remove)\s*\([^)]*\)\s*[;.]?\s*', text, re.I))

def subparts(ask: str, original: str) -> tuple[str, ...]:
    # Explicit question labels are authoritative; unlabelled operation lists are not questions.
    if ask and original:
        actual = subparts(ask, '')
        original_parts = subparts(original, '')
        if original_parts != ('main',) and original_parts != actual:
            raise ExplainError('질문·원문 소문항 표지 불일치')
        return actual
    root = parse(ask or original)
    marked = [n for n in root.find_all(lambda n: 'part' in n.classes or (n.tag == 'p' and re.match(r'\s*\(([a-z])\)', n.text())))
              if not any('part' in a.classes or a.tag in ('li', 'pre', 'code') for a in ancestors(n, root))]
    labels = []
    for node in marked:
        match = re.match(r'\s*\(([a-z])\)', node.text())
        if not match: raise ExplainError('소문항 표지 모호함')
        labels.append(match[1])
    lists = [n for n in root.find_all(lambda n: n.tag in ('ol','ul'))
             if not any(a.tag in ('li','ol','ul') for a in ancestors(n,root))]
    for node in lists:
        items = [c for c in node.children if isinstance(c,Node) and c.tag=='li']
        matches = [re.match(r'\s*\(([a-z])\)', c.text()) for c in items]
        if any(matches):
            if not all(matches): raise ExplainError('소문항 표지 누락 또는 모호함')
            operations = [operation_item(c.text()) for c in items]
            if all(operations): continue
            if any(operations): raise ExplainError('질문과 연산 소문항 경계 모호함')
            found = [m[1] for m in matches]
            if labels and labels != found: raise ExplainError('소문항 표지 불일치')
            if not labels: labels = found
        elif len(items)>1 and any(re.search(r'구하|설명하|증명하|계산하|\?\s*$',c.text()) for c in items):
            raise ExplainError('소문항 질문 경계 모호함: (a)/(b) 표지를 확인하세요')
    if labels and len(labels)!=len(set(labels)): raise ExplainError('중복 소문항 표지')
    return tuple(labels) or ('main',)

def load_source(path: Path, repo: Path) -> SourcePack:
    path = inside(existing_path(Path(path)), Path(repo))
    if not re.fullmatch(REVIEW.filename_re,nfc(path.name)):
        raise ExplainError('복습문제 HTML만 지원해요: '+str(path))
    try:
        pack = read_cards(path, REVIEW)
        problems = tuple(Problem(c.id,int(c.id[1:]),c.title,c.source,c.original_html,
                                 c.statement_html,'',(),c.steps,c.answer_html,
                                 subparts(c.statement_html,c.original_html)) for c in pack.cards)
        return SourcePack('review',pack.range,pack.slug,path,sha256(path),problems)
    except (ReviewPdfError,OSError) as exc:
        if 'no review cards' in str(exc):
            candidates=[]
            for p in repo.rglob('*.html'):
                if re.fullmatch(REVIEW.filename_re,nfc(p.name)) and p!=path:
                    try: read_cards(p, REVIEW); candidates.append(str(p.relative_to(repo)))
                    except (ReviewPdfError,OSError): pass
            raise ExplainError('문항 없음: '+str(path)+'\n비어 있지 않은 후보(자동 이동 없음):\n'+'\n'.join(sorted(candidates))) from exc
        raise ExplainError(str(exc)) from exc
