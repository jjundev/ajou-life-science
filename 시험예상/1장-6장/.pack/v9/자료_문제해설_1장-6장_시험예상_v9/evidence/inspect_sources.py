from pathlib import Path
import pymupdf
import sys

root = Path(__file__).resolve().parents[4]
ch = int(sys.argv[1])
terms = sys.argv[2:]
files = list((root / '강의노트').glob(f'{ch}장*.pdf')) + list((root / '교과서/생명과학_기초와_응용_2판').glob(f'{ch:02d}장*.pdf'))
for path in files:
    doc = pymupdf.open(path)
    print('\nFILE', path.relative_to(root), 'PAGES', len(doc))
    for i, page in enumerate(doc):
        text = ' '.join(page.get_text().split())
        hits = [term for term in terms if term.lower() in text.lower()]
        if hits:
            print('PAGE', i + 1, 'HITS', ', '.join(hits), 'TEXT', text[:1400])
