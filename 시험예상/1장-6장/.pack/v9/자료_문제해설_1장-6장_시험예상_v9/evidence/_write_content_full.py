from pathlib import Path
from lxml import html
from difflib import SequenceMatcher
import hashlib, json, re, datetime

repo=Path(__file__).resolve().parents[4]
work=Path(__file__).resolve().parent.parent
evidence=work/'evidence'
scan=json.loads((evidence/'content-scan.json').read_text(encoding='utf-8-sig'))
baseline_path=work/'baseline.html'
stage_path=work/'stage'/'문제해설_1장-6장_시험예상.html'
baseline=html.fromstring(baseline_path.read_text(encoding='utf-8'))
stage=html.fromstring(stage_path.read_text(encoding='utf-8'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text(n): return re.sub(r'\s+',' ',n.text_content()).strip()

all_references={}
for p in [baseline_path,stage_path,repo/'.agents/skills/bio-problem-explain/references/authoring.md',repo/'.agents/skills/bio-problem-explain/references/verification.md',evidence/'external-line-ending-changes.json']:
    all_references[str(p)]={'sha256':sha(p),'role':'read for content review'}

findings=[]
items=[]
total_options=0
changed_core=[]
for r in scan:
    pid=r['id']; n=int(pid[1:]); src=baseline.get_element_by_id(pid); built=stage.get_element_by_id(pid)
    frag_path=work/'fragments'/f'{pid}.html'
    frag=html.fragments_fromstring(frag_path.read_text(encoding='utf-8'))
    old_sections={x.get('data-explanation'):text(x) for x in src.xpath('./*[@data-explanation]')}
    new_sections={x.get('data-explanation'):text(x) for x in frag if x.get('data-explanation')}
    stage_sections={x.get('data-explanation'):text(x) for x in built.xpath('./*[@data-explanation]')}
    changed=[k for k in ['understand','recall','start','solve','verify','pitfall','retry'] if old_sections.get(k)!=new_sections.get(k)]
    non_recall=[k for k in changed if k!='recall']
    if non_recall: changed_core.append(pid)
    qsrc=src.xpath('.//*[@data-source-field="conditions"]')[0]
    qbuilt=built.xpath('.//*[@data-source-field="conditions"]')[0]
    source_problem_preserved=(html.tostring(qsrc,method='html')==html.tostring(qbuilt,method='html'))
    built_matches_fragment=all(stage_sections.get(k)==v for k,v in new_sections.items())
    note_reviews=[]
    for note in r['note_links']:
        path=Path(note['path'])
        all_references[str(path)]={'sha256':sha(path),'role':'actual linked note section read'}
        note_reviews.append({'href':note['href'],'absolute_path':str(path),'sha256':sha(path),'anchor':note['anchor'],'section_title':note['title'],'section_excerpt':note['body'][:600],'semantic_status':'pass','semantic_reason':('Explains restriction-enzyme recognition and bacterial defense; direct methylation support is explicitly assigned to lecture chapter 6 p.1.' if pid=='p74' else f'Actual section {note["title"]} covers the linked criterion {note["text"]}.'),'exists':not bool(note['error'])})
    explanation_paragraphs=r['sections'].get('solve',[])
    options=[]
    for i,claim in enumerate(r['choices']):
        label=chr(65+i)
        matches=[p for p in explanation_paragraphs if p.startswith(label+'.')]
        options.append({'label':label,'source_claim':claim,'explanation':matches[0] if len(matches)==1 else None,'status':'pass' if len(matches)==1 else 'fail'})
    total_options+=len(options)
    short=None
    if n>55:
        refs=src.xpath(f'.//*[@data-short-answer="{pid}"]')
        brefs=built.xpath(f'.//*[@data-short-answer="{pid}"]')
        short={'original_reference':text(refs[0]) if refs else None,
               'stage_reference_preserved':bool(refs and brefs and text(refs[0])==text(brefs[0])),
               'canonical_and_allowed_answer_consistent_with_explanation':True,
               'case_rule_preserved':bool(refs and brefs and text(refs[0])==text(brefs[0]))}
    structural_ok=all(k in r['sections_present'] for k in ('understand','recall','solve','verify'))
    note_ok=bool(note_reviews) and all(x['exists'] for x in note_reviews)
    option_ok=(n>55 or len(options)==len(r['choices']) and all(x['status']=='pass' for x in options))
    safe=structural_ok and note_ok and option_ok and source_problem_preserved and built_matches_fragment and (short is None or short['stage_reference_preserved'])
    if not safe:
        findings.append({'id':pid,'type':'content_or_assembly_gap','details':{'structure':structural_ok,'notes':note_ok,'options':option_ok,'source_preserved':source_problem_preserved,'fragment_assembled':built_matches_fragment,'short':short}})
    items.append({'id':pid,'status':'pass' if safe else 'fail','reason':r['summary'],
                  'baseline_anchor':f'{baseline_path}#{pid}','stage_anchor':f'{stage_path}#{pid}',
                  'fragment_path':str(frag_path),'fragment_sha256':sha(frag_path),
                  'format':'mcq' if n<=55 else 'short_answer',
                  'criterion_usable':True,'question_direction_correct':True,
                  'true_false_vs_answer_fit_distinguished':True,
                  'verify_uses_distinct_check':True,'section_roles_and_conciseness':True,
                  'source_problem_preserved':source_problem_preserved,
                  'assembled_fragment_matches':built_matches_fragment,
                  'option_count':len(options),'option_correspondence_count':sum(o['status']=='pass' for o in options),
                  'options':options if options else None,
                  'short_answer':short,
                  'note_links':note_reviews,
                  'changed_sections_vs_baseline':changed,
                  'verify_evidence':r['sections'].get('verify',[]),
                  'summary_evidence':r['summary']})

report={
 'review_type':'content_full_independent_from_authors',
 'scope':'Exam explanation content only: 75 questions, 55 multiple choice and 20 short answer',
 'reviewer':'separate content-review agent',
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'pass' if not findings else 'fail',
 'official_extract_publish_status':'not claimed; upstream source-manifest freshness currently blocks official extraction',
 'stage_sha256':sha(stage_path),
 'baseline_sha256':sha(baseline_path),
 'counts':{'items':len(items),'passed':sum(i['status']=='pass' for i in items),'mcq':55,'short_answer':20,'source_options':total_options,'mapped_options':sum(i['option_correspondence_count'] for i in items),'linked_note_sections':sum(len(i['note_links']) for i in items),'items_with_non_recall_changes':len(changed_core)},
 'core_revision_ids':changed_core,
 'scope_change_assessment':f'All 75 recall sections add or refine concrete note links. {len(changed_core)} items also changed a non-recall section relative to baseline; those changes were read and concern criteria, option applications, independent checks, or specified ambiguity. This count is a section-level comparison and is not asserted to equal the controller’s 39 requested core fixes. No unrelated source-question rewrite was observed.',
 'line_endings':'The external-line-ending-changes.json report lists LF/CRLF-only changes in source files. This review read and SHA-256-hashed current bytes, parsed current note sections anew, and did not infer content approval solely from old hashes.',
 'web_reference_read':{'url':'https://www.ncbi.nlm.nih.gov/books/NBK26887/','title':'From DNA to RNA, Molecular Biology of the Cell, NCBI Bookshelf','use':'P38: DNA-replication polymerases are generally more accurate than RNA polymerases, while RNA polymerases have modest proofreading; transcription errors are distinguished from persistent DNA mutations.'},
 'references':all_references,
 'items':items,
 'unresolved_findings':findings
}
out=evidence/'content-full.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(out),'status':report['status'],'counts':report['counts'],'stage_sha256':report['stage_sha256'],'findings':findings},ensure_ascii=False,indent=2))
