"""Validate banks and create static offline previews."""
from __future__ import annotations

import argparse
from pathlib import Path
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
    args = parser.parse_args(argv)
    try:
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
