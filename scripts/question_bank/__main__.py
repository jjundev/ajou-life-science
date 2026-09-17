"""Validate banks and create static offline previews."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from .model import REPO_ROOT, load_bank, resolve_local
from .render import render_preview


def _protect_inputs(bank: dict, bank_path: Path, output: Path) -> None:
    inputs = [bank_path]
    inputs.extend(resolve_local(bank_path.parent, s['path']) for s in bank['sources'])
    inputs.extend(resolve_local(bank_path.parent, a[v]['path'])
                  for a in bank['assets'] for v in ('exam', 'explained'))
    inputs.extend(resolve_local(REPO_ROOT, e['path']) for q in bank['questions']
                  for r in q['analysis']['requirements'] for e in r['evidence'])
    for path in inputs:
        if output.resolve() == path.resolve() or (output.exists() and output.samefile(path)):
            raise ValueError('output cannot overwrite an input file: ' + str(output))


def _template_meta(template: str) -> dict:
    """Read the template's marked META value without executing JavaScript."""
    from .note import START, END
    start, end = template.index(START), template.index(END)
    block = template[start + len(START):end].lstrip()
    match = re.match(r'const\s+META\s*=\s*', block)
    if not match:
        raise ValueError('template question data has no META declaration')
    value, _ = json.JSONDecoder().raw_decode(block[match.end():])
    if not isinstance(value, dict):
        raise ValueError('template META must be an object')
    return value


def _render_note_command(args: argparse.Namespace) -> bytes:
    from .note import export_note_items, render_note
    from .render import figure_templates
    from .scope import load_web_scope, protect_paths, reference_href

    scope_path = args.scope.resolve()
    meta_path = args.meta.resolve()
    template_path = args.template.resolve()
    output = args.output.resolve()
    template = template_path.read_text(encoding='utf-8')
    supplied = json.loads(meta_path.read_text(encoding='utf-8'))
    if not isinstance(supplied, dict):
        raise ValueError('META input must be a JSON object')
    if not isinstance(supplied.get('date'), str) or not re.fullmatch(r'\d{4}', supplied['date']):
        raise ValueError('META date must be MMDD')
    if not isinstance(supplied.get('title'), str) or not supplied['title'].strip():
        raise ValueError('META title must be a nonempty string')
    allowed = {'date', 'title', 'chapter', 'range', 'note'}
    if set(supplied) - allowed:
        raise ValueError('unknown META fields: ' + ', '.join(sorted(set(supplied) - allowed)))
    meta = _template_meta(template)
    meta.update(supplied)

    entries, banks = load_web_scope(scope_path, REPO_ROOT)
    items, figures = [], []
    bank_paths = {}
    for entry in entries:
        bank_paths.setdefault(entry['bank_id'], Path(entry['bank_path']))
    for bank_id, bank in banks.items():
        bank_path = bank_paths[bank_id]
        _protect_inputs(bank, bank_path, output)
        selected = [entry for entry in entries if entry['bank_id'] == bank_id]
        exported = export_note_items(bank, selected)
        for item in exported:
            for ref in item['refs']:
                ref['href'] = reference_href(ref, REPO_ROOT, output.parent)
        items.extend(exported)
        figures.append(figure_templates(bank, bank_path.parent))
    ref_paths = [resolve_local(REPO_ROOT, ref['path'])
                 for entry in entries for ref in entry['refs']]
    protect_paths(output, [scope_path, meta_path, template_path, *ref_paths])
    deferred = sum(entry['status'] == 'deferred' for entry in entries)
    if deferred:
        suffix = f' 원본 문항 중 {deferred}개는 명세에 따라 보류되어 이 퀴즈에 포함되지 않습니다.'
        meta['note'] = (meta.get('note') or '') + suffix
    return render_note(template, meta, items, '\n'.join(figures)).encode('utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate and preview an offline question bank.')
    commands = parser.add_subparsers(dest='command', required=True)
    validate = commands.add_parser('validate', help='validate the bank and local references')
    validate.add_argument('bank', type=Path)
    validate.add_argument('--complete', action='store_true', help='require complete verified review')
    preview = commands.add_parser('preview', help='render a static review HTML file')
    preview.add_argument('bank', type=Path)
    preview.add_argument('--output', required=True, type=Path)
    preview.add_argument('--force', action='store_true', help='replace a differing output file')
    note = commands.add_parser('note', help='render a study-note quiz from a web scope')
    note.add_argument('--scope', required=True, type=Path)
    note.add_argument('--meta', required=True, type=Path)
    note.add_argument('--output', required=True, type=Path)
    note.add_argument('--template', type=Path, default=REPO_ROOT / '정리노트/_template.html')
    note.add_argument('--force', action='store_true', help='replace a differing output file')
    args = parser.parse_args(argv)
    try:
        if args.command == 'note':
            content = _render_note_command(args)
            output = args.output.resolve()
            if output.exists():
                if output.read_bytes() == content:
                    print('Unchanged: ' + str(output))
                    return 0
                if not args.force:
                    raise ValueError('output exists and differs; use --force: ' + str(output))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            print('Note: ' + str(output))
            return 0
        bank = load_bank(args.bank, complete=getattr(args, 'complete', False))
        if args.command == 'validate':
            print(f'Valid: {len(bank["questions"])} questions ({"complete" if args.complete else "draft"})')
            return 0
        output = args.output
        _protect_inputs(bank, args.bank, output)
        html = render_preview(bank, args.bank.parent, output_dir=output.parent)
        content = html.encode('utf-8')
        if output.exists():
            if output.read_bytes() == content:
                print('Unchanged: ' + str(output))
                return 0
            if not args.force:
                raise ValueError('output exists and differs; use --force: ' + str(output))
        output.write_bytes(content)
        print('Preview: ' + str(output))
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
