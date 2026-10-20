from pathlib import Path
from lxml import html
from urllib.parse import unquote
import json, re, hashlib, sys

repo = Path(__file__).resolve().parents[4]
work = Path(__file__).resolve().parent.parent
baseline = html.fromstring((work / 'baseline.html').read_text(encoding='utf-8'))

def txt(node):
    return re.sub(r'\s+', ' ', node.text_content()).strip() if node is not None else ''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records=[]
for n in range(1,76):
    article = baseline.get_element_by_id(f'p{n}')
    qnode = article.xpath('.//*[@data-source-field="conditions"]')[0]
    q = [txt(x) for x in qnode.xpath('./p')]
    choices = [txt(x) for x in qnode.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," choices ")]/li')]
    fragment_path = work/'fragments'/f'p{n}.html'
    frag = html.fragments_fromstring(fragment_path.read_text(encoding='utf-8'))
    sections = {x.get('data-explanation'): x for x in frag if x.get('data-explanation')}
    summary = next((x for x in frag if x.get('class')=='sum'), None)
    note_links=[]
    for a in sections['recall'].xpath('.//a[@href]'):
        href = unquote(a.get('href'))
        pathstr, sep, anchor = href.partition('#')
        path = (repo/'시험예상'/'1장-6장'/pathstr).resolve()
        title = body = error = ''
        if path.is_file():
            doc = html.fromstring(path.read_text(encoding='utf-8'))
            found = doc.xpath(f'//*[@id="{anchor}"]') if anchor else []
            if found:
                node = found[0]
                title = txt(node.xpath('./h2|./h3|./h4')[0]) if node.xpath('./h2|./h3|./h4') else txt(node)[:100]
                body = txt(node)
            else: error='anchor_missing'
        else: error='file_missing'
        note_links.append({'href':href,'text':txt(a),'path':str(path),'sha256':sha(path) if path.is_file() else None,'anchor':anchor,'title':title,'body':body,'error':error})
    rec={'id':f'p{n}','title':txt(article.xpath('./h3')[0]),'question':q,'choices':choices,
         'sections':{k:[txt(p) for p in v.xpath('.//p')] for k,v in sections.items()},
         'sections_present':list(sections),'summary':txt(summary),'note_links':note_links,
         'fragment_sha256':sha(fragment_path)}
    records.append(rec)

if len(sys.argv)>1 and sys.argv[1]=='answers':
    for n in range(56,76):
        article=baseline.get_element_by_id(f'p{n}')
        ref=article.xpath(f'.//*[@data-short-answer="p{n}"]')
        print(f'p{n}:',txt(ref[0]) if ref else 'MISSING')
elif len(sys.argv)>1 and sys.argv[1]=='diff':
    from difflib import SequenceMatcher
    for n in range(1,76):
        article=baseline.get_element_by_id(f'p{n}')
        old={x.get('data-explanation'):txt(x) for x in article.xpath('./*[@data-explanation]')}
        frag=html.fragments_fromstring((work/'fragments'/f'p{n}.html').read_text(encoding='utf-8'))
        new={x.get('data-explanation'):txt(x) for x in frag if x.get('data-explanation')}
        changes=[]
        for key in ('understand','recall','start','solve','verify','pitfall','retry'):
            if old.get(key)!=new.get(key):
                ratio=SequenceMatcher(None,old.get(key,''),new.get(key,'')).ratio()
                changes.append(f'{key}:{ratio:.2f}')
        print(f'p{n}: '+', '.join(changes))
elif len(sys.argv)>1 and sys.argv[1]=='findnote':
    needle=sys.argv[2]
    for path in repo.glob('복습노트/**/정리노트_*.html'):
        if needle not in path.read_text(encoding='utf-8'): continue
        doc=html.fromstring(path.read_text(encoding='utf-8'))
        for node in doc.xpath('//*[@id]'):
            if needle in txt(node) and not any(needle in txt(child) for child in node.xpath('./*[@id]')):
                print(path.relative_to(repo),node.get('id'),txt(node)[:160])
elif len(sys.argv)>1 and sys.argv[1]=='extra':
    for n in map(int, sys.argv[2:]):
        qnode=baseline.get_element_by_id(f'p{n}').xpath('.//*[@data-source-field="conditions"]')[0]
        for child in qnode:
            if child.tag not in ('p','ul','ol'):
                print(n,child.tag,txt(child))
elif len(sys.argv)>1 and sys.argv[1]=='json':
    print(json.dumps(records,ensure_ascii=False,indent=2))
else:
    start=int(sys.argv[1]) if len(sys.argv)>1 else 1
    end=int(sys.argv[2]) if len(sys.argv)>2 else 75
    for r in records[start-1:end]:
        print(f"\n{r['id']} {r['title']} Q {' '.join(r['question'])}")
        for i,c in enumerate(r['choices']): print(f'{chr(65+i)}. {c}')
        for k in ['understand','recall','start','solve','verify','pitfall','retry']:
            if k in r['sections']: print(f"{k.upper()}: {' / '.join(r['sections'][k])}")
        print(f"SUM: {r['summary']}")
        for l in r['note_links']: print(f"NOTE: {l['text']} | {l['title']} | {l['body'][:320]} | {l['error']}")
