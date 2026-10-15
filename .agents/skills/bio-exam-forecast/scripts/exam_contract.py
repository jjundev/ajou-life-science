"""Validated boundaries for mixed-format, strictly scoped exam packs."""
from dataclasses import dataclass
from html.parser import HTMLParser
import hashlib
import html
import json
import re
import unicodedata

class ExamError(ValueError):
    pass

@dataclass(frozen=True)
class Scope:
    chapters: tuple[int, ...]
    @property
    def label(self):
        return f'{self.chapters[0]}장' if len(self.chapters)==1 else f'{self.chapters[0]}장-{self.chapters[-1]}장'

@dataclass(frozen=True)
class Selection:
    problems: tuple[dict, ...]
    quotas: dict[int, dict[str, int]]
    shortages: tuple[dict, ...]
    deviations: tuple[dict, ...]

def parse_scope(text):
    text=unicodedata.normalize('NFC',text)
    m=re.fullmatch(r'\s*([1-9]\d*)\s*장?\s*(?:[~～-]\s*([1-9]\d*)\s*장?\s*)?',text)
    if not m: raise ExamError('단일 장 또는 연속 범위를 입력하세요: 1장~6장')
    a,b=int(m[1]),int(m[2] or m[1])
    if b<a: raise ExamError('역순 범위')
    return Scope(tuple(range(a,b+1)))

def normalize_short(value, *, case_sensitive=True):
    value=unicodedata.normalize('NFC',value).strip()
    return value if case_sensitive else value.casefold()

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def payload(c):
    return digest({k:c.get(k) for k in ('problem_html','options','answer')})

class _Options(HTMLParser):
    def __init__(self,markup):
        super().__init__(); self.count=0;self.level=0;self.stack=[];self.items=[];self.in_item=False;self.active=False;self.feed(markup)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('script','iframe','object','embed','style','input','form','details') or any(k.startswith('on') or k in ('hidden','data-correct') for k in attrs):self.active=True
        if any(re.match(r'\s*(?:[a-z]+:|//)',v,re.I) for k,v in attrs.items() if k in ('href','src','xlink:href') and not v.startswith('#')):self.active=True
        if tag in ('ul','ol'):
            self.stack.append(self.level)
            if 'choices' in attrs.get('class','').split(): self.level+=1
        if tag=='li' and self.level:
            self.count+=1;self.items.append('');self.in_item=True
    def handle_data(self,value):
        if self.in_item:self.items[-1]+=value
    def handle_endtag(self,tag):
        if tag=='li':self.in_item=False
        if tag in ('ul','ol') and self.stack: self.level=self.stack.pop()

def validate_candidate(c, scope, topics):
    errors=[]
    def need(ok,msg):
        if not ok: errors.append(f'{c.get("id","?")}: {msg}')
    for key in ('id','family_id','selection_reason','problem_html'):
        need(isinstance(c.get(key),str) and bool(c[key].strip()),key+' required')
    fmt=c.get('format'); need(fmt in ('mcq','short'),'format')
    need(c.get('origin') in ('web','past','new'),'origin')
    need(c.get('mode') in ('original','variant','generated'),'mode')
    need(c.get('primary_chapter') in scope.chapters,'primary chapter outside scope')
    required=c.get('required_chapters',[])
    need(isinstance(required,list) and bool(required) and all(type(x) is int and x in scope.chapters for x in required),'required chapters outside scope')
    need(c.get('primary_chapter') in required,'primary chapter not required')
    tids=c.get('topic_ids',[])
    need(bool(tids) and all(t in topics and topics[t].get('scope_status')=='included' and topics[t].get('chapter') in required for t in tids),'topic outside included scope')
    need(type(c.get('level')) is int and c['level'] in (1,2,3),'level')
    need(isinstance(c.get('priority'),list) and len(c['priority'])==5 and all(type(v) is bool for v in c['priority']),'priority')
    need(isinstance(c.get('types'),list) and bool(c['types']) and all(isinstance(t,str) and t.strip() for t in c['types']),'types')
    options=c.get('options',[]); answer=c.get('answer',{})
    parsed=_Options(c.get('problem_html',''))
    need(not parsed.active,'active or answer markup in question')
    if fmt=='mcq':
        ids=[o.get('id') for o in options if isinstance(o,dict)]
        need(len(options) in (4,5) and len(ids)==len(options) and all(isinstance(x,str) and x for x in ids) and len(set(ids))==len(ids),'options')
        need(all(isinstance(o.get('text'),str) and o['text'].strip() for o in options),'empty option')
        need(parsed.count==len(options),'problem option/model count')
        def option_text(value):
            value=re.sub(r'<[^>]+>','',value)
            value=re.sub(r'^\s*(?:[A-E][.)]|\([1-5]\))\s*','',html.unescape(value))
            return re.sub(r'\s+',' ',value).strip()
        need([option_text(x) for x in parsed.items]==[option_text(o.get('text','')) for o in options],'problem option/model text')
        need(answer.get('kind')=='choice' and answer.get('option_id') in ids,'choice answer')
    elif fmt=='short':
        need(options==[] and _Options(c.get('problem_html','')).count==0,'short options')
        need(answer.get('kind')=='short' and isinstance(answer.get('canonical'),str) and answer['canonical'].strip(),'short canonical')
        accepted=answer.get('accepted')
        need(isinstance(accepted,list) and bool(accepted) and all(isinstance(x,str) and x.strip() for x in accepted),'short accepted')
        need(type(answer.get('case_sensitive')) is bool,'case_sensitive')
    steps=c.get('solution_steps',[])
    need(isinstance(steps,list) and bool(steps) and all(isinstance(x,str) and x.strip() for x in steps),'solution steps')
    need(type(c.get('minimum_steps')) is int and c['minimum_steps']>0,'minimum_steps')
    for field in ('source_refs','style_basis'):
        refs=c.get(field,[])
        need(isinstance(refs,list) and bool(refs),field)
        for ref in refs:
            keys=('path','sha256','locator')+ (('criterion','application') if field=='style_basis' else ('role',))
            need(isinstance(ref,dict) and all(isinstance(ref.get(k),str) and ref[k].strip() for k in keys),field+' evidence')
    for field in ('scope','key','source','style','family'):
        r=c.get('review',{}).get(field,{})
        need(r.get('status')=='pass' and bool(r.get('evidence','').strip()),'unreviewed '+field)
    if c.get('mode')=='original': need(c.get('original_payload_sha256')==payload(c),'original payload mismatch')
    else: need(bool(c.get('transformation','').strip()),'transformation')
    return errors

def fingerprint(c):
    # Order-insensitive choices detect copied questions even when options are shuffled.
    value=unicodedata.normalize('NFC',re.sub(r'\s+',' ',re.sub(r'<ul class="choices">.*?</ul>','',c['problem_html'],flags=re.S))).strip()
    return digest([value,sorted(o['text'].strip() for o in c['options'])])

def validate_pack(pack):
    errors=[]
    try:
        scope=Scope(tuple(pack['scope']));problems=pack['problems']
        if pack.get('schema_version')!=1 or pack.get('profile')!='exam' or pack.get('range')!=scope.label: errors.append('pack identity')
        if not scope.chapters or scope.chapters!=tuple(range(scope.chapters[0],scope.chapters[-1]+1)) or scope.chapters[0]<1: errors.append('pack scope')
        if type(pack.get('version')) is not int or pack['version']<1: errors.append('version')
        if len(problems)!=75 or [p['id'] for p in problems]!=[f'p{i}' for i in range(1,76)]: errors.append('75 ordered unique ids required')
        if [p['format'] for p in problems]!=['mcq']*55+['short']*20: errors.append('55+20 formats required')
        if len({p['family_id'] for p in problems})!=len(problems): errors.append('duplicate family')
        if len({fingerprint(p) for p in problems})!=len(problems): errors.append('duplicate payload')
        generated=[stem_fingerprint(p) for p in problems if p['mode']=='generated']
        if len(generated)!=len(set(generated)):errors.append('duplicate generated stem')
        topics={t['id']:t for t in pack['scope_data']['topics']}
        for p in problems: errors.extend(validate_candidate(p,scope,topics))
    except (KeyError,TypeError,IndexError,ValueError) as exc: errors.append('invalid pack: '+str(exc))
    return errors

def stem_fingerprint(c):
    return digest(unicodedata.normalize('NFC',re.sub(r'\s+',' ',re.sub(r'<(?:ul|ol) class="choices">.*?</(?:ul|ol)>','',c['problem_html'],flags=re.S))).strip())
