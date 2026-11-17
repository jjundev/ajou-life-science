import re,sys,html
f=sys.argv[1]; ids=sys.argv[2:]
s=open(f).read()
# find section elements with ids
for a in ids:
    m=re.search(r'<(section|div|article|h[1-6])[^>]*id="%s"[^>]*>'%re.escape(a),s)
    if not m: print('##',a,'NOT FOUND');continue
    tag=m.group(1); start=m.start()
    # take until next <section id="s.. or next element with id matching sN- pattern at same prefix level
    nxt=re.search(r'<(section|div|article)[^>]*id="s\d+(-[a-z0-9-]+)?"',s[m.end():])
    cand=[mm for mm in re.finditer(r'id="(s\d+-[a-z-]+|s\d+)"',s[m.end():]) if not mm.group(1).startswith(a+'-')]
    end=m.end()+cand[0].start() if cand else len(s)
    t=s[start:end]
    t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<svg.*?</svg>','[svg]',t,flags=re.S)
    t=re.sub(r'<(p|li|h\d|tr|div)[^>]*>','\n',t); t=re.sub(r'<[^>]+>','',t); t=html.unescape(t)
    t=re.sub(r'\n\s*\n+','\n',t)
    print('##',a,'\n',t.strip()[:6000],'\n')
