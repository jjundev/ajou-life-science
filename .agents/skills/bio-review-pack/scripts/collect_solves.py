"""다운로드 폴더의 풀이기록 JSON을 복습노트/<날짜>/풀이기록/ 으로 옮긴다."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[3]


def owner_folder(root: Path, document_id: str, range_: str) -> Path | None:
    """document_id(HTML 파일명)가 들어 있는 복습노트 하위 폴더. 여러 곳이면 range와 같은 이름을 우선."""
    found = sorted(p.parent for p in root.glob('*/' + document_id))
    if len(found) > 1:
        found = [p for p in found if p.name == range_] or found
    return found[0] if len(found) == 1 else None


def collect(downloads: Path, root: Path, dry_run: bool = False) -> list[tuple[Path, Path | None, str, str]]:
    """(원본, 대상, 상태, 이유) 목록. 상태는 moved / would-move / skipped."""
    results = []
    if not downloads.is_dir():
        return results
    for src in sorted(downloads.glob('*_풀이기록_*.json')):
        try:
            data = json.loads(src.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('documentId'), str):
                raise ValueError('풀이기록 형식이 아님')
        except (OSError, ValueError) as exc:
            results.append((src, None, 'skipped', str(exc)))
            continue
        folder = owner_folder(root, data['documentId'], str(data.get('range', '')))
        if folder is None:
            results.append((src, None, 'skipped', '해당 복습문제 폴더를 하나로 정할 수 없음'))
            continue
        dst = folder / '풀이기록' / src.name
        if dst.exists():
            results.append((src, dst, 'skipped', '같은 이름 파일이 이미 있음'))
            continue
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))
        results.append((src, dst, 'would-move' if dry_run else 'moved', ''))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--downloads', type=Path, default=Path.home() / 'Downloads', help='JSON이 내려받아진 폴더')
    ap.add_argument('--root', type=Path, default=REPO / '복습노트')
    ap.add_argument('--dry-run', action='store_true', help='옮기지 않고 결과만 보여준다')
    args = ap.parse_args()
    results = collect(args.downloads, args.root, args.dry_run)
    for src, dst, status, reason in results:
        print(f'{status}: {src.name}' + (f' -> {dst.relative_to(args.root.parent)}' if dst and status != 'skipped' else '')
              + (f' ({reason})' if reason else ''))
    if not results:
        print(f'옮길 풀이기록 JSON이 없어요: {args.downloads}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
