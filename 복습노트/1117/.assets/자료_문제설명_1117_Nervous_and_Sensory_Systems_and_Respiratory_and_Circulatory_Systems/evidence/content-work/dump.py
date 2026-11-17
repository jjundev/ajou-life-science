import json,re,sys,html
T=sys.argv[1]
d=json.load(open(T+'/source.json'))
def strip(s,keep=True):
    s=re.sub(r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>',r'[\2](\1)',s,flags=re.S)
    s=re.sub(r'<strong>(.*?)</strong>',r'**\1**',s,flags=re.S)
    s=re.sub(r'<div[^>]*data-explanation="([^"]*)"[^>]*>',r'\n=== \1 ===\n',s)
    s=re.sub(r'<div[^>]*data-subpart="([^"]*)"[^>]*>',r'[sub \1]',s)
    s=re.sub(r'<div class="sum"[^>]*>',r'\n=== SUM ===\n',s)
    s=re.sub(r'<(p|li|h4|tr)[^>]*>',r'\n',s)
    s=re.sub(r'<(td|th)[^>]*>',r' | ',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=re.sub(r'\n\s*\n+','\n',s)
    return s.strip()
for p in d['problems']:
    out=[f"##### {p['id']} {p['title']} | {p['source']} | ans={p['choice'] and p['choice']['answer']}"]
    out.append(strip(p['conditions_html']))
    if p['ask_html']: out.append('ASK: '+strip(p['ask_html']))
    if p['figures_html']: out.append('FIG: '+str(len(p['figures_html'])))
    ex=open(f"{T}/explanations/{p['id']}.html").read()
    out.append('--- EXPLANATION ---')
    out.append(strip(ex))
    open(f"{T}/evidence/content-work/{p['id']}.txt",'w').write('\n'.join(out)+'\n')
print('ok')
