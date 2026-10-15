"""Deterministic family matching; source mix is an auditable soft target."""
from collections import Counter,defaultdict
from exam_contract import Selection,validate_candidate,fingerprint,stem_fingerprint
TARGETS={('mcq','web','original'):20,('mcq','web','variant'):10,('mcq','past','original'):10,('mcq','new','generated'):15,('short','web','variant'):8,('short','past','any'):4,('short','new','generated'):8}

def bucket(c):return (c['format'],c['origin'],'any' if c['format']=='short' and c['origin']=='past' else c['mode'])

def allocate_quotas(scope):
 n=len(scope.chapters);base,rem=divmod(75,n)
 totals={ch:base+(i<rem) for i,ch in enumerate(scope.chapters)}
 mcq={ch:55*t//75 for ch,t in totals.items()}
 order=sorted(totals,key=lambda ch:(-(55*totals[ch]%75),ch))
 for ch in order[:55-sum(mcq.values())]:mcq[ch]+=1
 return {ch:dict(total=totals[ch],mcq=mcq[ch],short=totals[ch]-mcq[ch]) for ch in scope.chapters}

def select_candidates(candidates,scope,topics,*,previous=()):
 quotas=allocate_quotas(scope)
 previous_families={p['family_id'] for p in previous}
 previous_generated={stem_fingerprint(p) for p in previous if p['mode']=='generated'}
 valid=[c for c in candidates if not validate_candidate(c,scope,topics) and not (c['mode']=='generated' and stem_fingerprint(c) in previous_generated)]
 # Union semantic family and exact duplicate identities, including cross-origin copies.
 parent={c['family_id']:c['family_id'] for c in valid}
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 seen={}
 for c in sorted(valid,key=lambda c:c['id']):
  fp=fingerprint(c);f=find(c['family_id'])
  if fp in seen:parent[f]=find(seen[fp])
  else:seen[fp]=f
 generated_stems={}
 for c in sorted(valid,key=lambda c:c['id']):
  if c['mode']!='generated':continue
  stem=stem_fingerprint(c);family=find(c['family_id'])
  if stem in generated_stems:parent[family]=find(generated_stems[stem])
  else:generated_stems[stem]=family
 def rank(c):return tuple(-int(x) for x in c['priority'])+(c['family_id'] in previous_families,c['id'])
 pools=defaultdict(list)
 for c in sorted(valid,key=rank):pools[c['primary_chapter'],c['format']].append(c)
 slots=[(ch,fmt,i) for ch in scope.chapters for fmt in ('mcq','short') for i in range(quotas[ch][fmt])]
 assignment={};owners={};counts=Counter()
 def assign(slot,visited):
  pool=pools[slot[:2]]
  pool=sorted(pool,key=lambda c:(tuple(-int(x) for x in c['priority']),counts[bucket(c)]>=TARGETS.get(bucket(c),0),c['family_id'] in previous_families,c['id']))
  for c in pool:
   family=find(c['family_id'])
   if family in visited:continue
   visited.add(family);old=owners.get(family)
   if old is None or assign(old,visited):
    if slot in assignment:
     prev=assignment[slot];counts[bucket(prev)]-=1
     pf=find(prev['family_id'])
     if owners.get(pf)==slot:owners.pop(pf)
    assignment[slot]=c;owners[family]=slot;counts[bucket(c)]+=1;return True
  return False
 # Scarce pools first; augmenting paths free flexible families when required.
 for slot in sorted(slots,key=lambda s:(len({find(c['family_id']) for c in pools[s[:2]]})-quotas[s[0]][s[1]],s)):
  assign(slot,set())
 def score(counter):return sum(abs(counter[k]-v) for k,v in TARGETS.items())+sum(v for k,v in counter.items() if k not in TARGETS)
 # Improve source targets only when hard constraints remain satisfied.
 changed=True
 while changed:
  changed=False
  for slot,current in sorted(assignment.items()):
   for c in pools[slot[:2]]:
    family=find(c['family_id'])
    if family in owners and owners[family]!=slot:continue
    test=counts.copy();test[bucket(current)]-=1;test[bucket(c)]+=1
    if score(test)<score(counts):
     owners.pop(find(current['family_id']),None);owners[family]=slot;assignment[slot]=c;counts=test;changed=True;break
   if changed:break
 selected=tuple(assignment[s] for s in sorted(assignment,key=lambda s:(s[1]!='mcq',s[0],s[2])))
 shortages=[]
 for ch in scope.chapters:
  for fmt in ('mcq','short'):
   actual=sum(c['primary_chapter']==ch and c['format']==fmt for c in selected)
   if actual<quotas[ch][fmt]:shortages.append(dict(chapter=ch,format=fmt,missing=quotas[ch][fmt]-actual,reason='범위·검토·중복 제약을 통과한 독립 가족 부족'))
 deviations=[dict(format=k[0],origin=k[1],mode=k[2],target=v,actual=counts[k],reason='장/형식/가족 제약 우선, 적격 출처로 보완') for k,v in TARGETS.items() if counts[k]!=v]
 for c in selected:
  if c['family_id'] in previous_families:deviations.append(dict(candidate_id=c['id'],reason='이전 버전 가족 재사용'))
 return Selection(selected,quotas,tuple(shortages),tuple(deviations))

def selection_report(selection):
 import json
 return '# 선정 보고\n\n기본 배합은 생성 정책이며 실제 출제 확률이 아니다.\n\n'+json.dumps(dict(quotas=selection.quotas,shortages=selection.shortages,deviations=selection.deviations),ensure_ascii=False,indent=2)+'\n'
