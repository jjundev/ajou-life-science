from pathlib import Path
from lxml import html
import hashlib, json, re, datetime

work=Path(__file__).resolve().parent.parent
path=work/'evidence'/'content-full.json'
report=json.loads(path.read_text(encoding='utf-8'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def plain(node): return re.sub(r'\s+',' ',node.text_content()).strip()

stage_path=work/'stage'/'문제해설_1장-6장_시험예상.html'
stage=html.fromstring(stage_path.read_text(encoding='utf-8'))
baseline=html.fromstring((work/'baseline.html').read_text(encoding='utf-8'))
mismatches=[]
checks={'reference_files':0,'fragment_files':0,'unchanged_73_fragments':0,'built_sections':0,'source_questions':0,'final_p38_p74':0}

if sha(stage_path)!=report['stage_sha256']:
    mismatches.append({'stage_hash':{'recorded':report['stage_sha256'],'actual':sha(stage_path)}})
for name,record in report['references'].items():
    p=Path(name)
    if not p.is_file() or sha(p)!=record['sha256']:
        mismatches.append({'reference':name,'recorded':record['sha256'],'actual':sha(p) if p.is_file() else None})
    checks['reference_files']+=1

for item in report['items']:
    pid=item['id']; frag_path=Path(item['fragment_path'])
    if not frag_path.is_file() or sha(frag_path)!=item['fragment_sha256']:
        mismatches.append({'fragment':pid,'recorded':item['fragment_sha256'],'actual':sha(frag_path) if frag_path.is_file() else None})
    checks['fragment_files']+=1
    if pid not in ('p38','p74') and sha(frag_path)==item['fragment_sha256']:
        checks['unchanged_73_fragments']+=1
    frag=html.fragments_fromstring(frag_path.read_text(encoding='utf-8'))
    fsections={x.get('data-explanation'):plain(x) for x in frag if x.get('data-explanation')}
    built=stage.get_element_by_id(pid)
    bsections={x.get('data-explanation'):plain(x) for x in built.xpath('./*[@data-explanation]')}
    if fsections!=bsections:
        mismatches.append({'assembled_sections':pid})
    checks['built_sections']+=1
    original=baseline.get_element_by_id(pid).xpath('.//*[@data-source-field="conditions"]')[0]
    current=built.xpath('.//*[@data-source-field="conditions"]')[0]
    if html.tostring(original,encoding='unicode')!=html.tostring(current,encoding='unicode'):
        mismatches.append({'source_question':pid})
    checks['source_questions']+=1
    for note in item['note_links']:
        p=Path(note['absolute_path'])
        if sha(p)!=note['sha256']:
            mismatches.append({'note':pid,'path':str(p)})
        doc=html.fromstring(p.read_text(encoding='utf-8'))
        if not doc.xpath(f'//*[@id="{note["anchor"]}"]'):
            mismatches.append({'note_anchor':pid,'path':str(p),'anchor':note['anchor']})

p38=stage.get_element_by_id('p38')
p38_source=plain(p38.xpath('.//*[@data-source-field="conditions"]')[0])
p38_d=next(plain(p) for p in p38.xpath('./*[@data-explanation="solve"]//p') if plain(p).startswith('D.'))
p38_ok=all(s in p38_source for s in ['DNA 중합효소는 RNA 중합효소보다 교정 기능이 떨어져 돌연변이율이 더 높다']) and all(s in p38_d for s in ['돌연변이율이 더 높다','RNA에 생긴 전사 오류','RNA 중합효소에도 제한적인 교정 기전']) and bool(p38.xpath('.//a[@href="https://www.ncbi.nlm.nih.gov/books/NBK26887/"]')) and '전사 오류가 DNA 돌연변이' not in p38_d
if not p38_ok: mismatches.append({'final_semantics':'p38'})
checks['final_p38_p74']+=1
p74=stage.get_element_by_id('p74')
p74_recall=plain(p74.xpath('./*[@data-explanation="recall"]')[0])
p74_solve=plain(p74.xpath('./*[@data-explanation="solve"]')[0])
p74_note=p74.xpath('./*[@data-explanation="recall"]//a[contains(@href,"#s5-restriction")]')
p74_ok=bool(p74_note) and all(s in p74_recall for s in ['인식서열과 방어 기능','메틸화','강의노트 6장 1쪽']) and '메틸화' in p74_solve
if not p74_ok: mismatches.append({'final_semantics':'p74'})
checks['final_p38_p74']+=1

audit={'status':'pass' if not mismatches else 'fail','audited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'stage_sha256':sha(stage_path),'checks':checks,'p38_final_content_confirmed':p38_ok,'p74_final_content_confirmed':p74_ok,
       'mismatches':mismatches,'official_gate':'source-manifest freshness block remains; this is content reference binding only'}
audit_path=work/'evidence'/'content-binding-audit.json'
audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report['reference_binding_audit']={'path':str(audit_path),'sha256':sha(audit_path),'status':audit['status'],'stage_sha256':audit['stage_sha256'],'checks':checks}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False,indent=2))
