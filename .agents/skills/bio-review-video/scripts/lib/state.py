from pathlib import Path
import json
from .cache import atomic_json,file_lock,file_hash

STAGES=('inputs','coverage','script','voice','timing','composition','render','verify','publish')

class RunStore:
    def __init__(self,run): self.run=Path(run)
    def lock(self): return file_lock(self.run/'work/run.lock')
    def load(self):
        p=self.run/'run.json'
        return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'schema_version':1,'stages':{}}
    def save(self,state): atomic_json(self.run/'run.json',state)
    def invalidate(self,stage):
        state=self.load()
        for name in STAGES[STAGES.index(stage):]:
            state.setdefault('stages',{})[name]={'status':'pending'}
        self.save(state)
    def recover(self):
        state=self.load()
        for name in STAGES:
            item=state.setdefault('stages',{}).get(name,{})
            if item.get('status') not in ('passed','running'): continue
            outputs=item.get('output_hashes',{})
            valid=bool(outputs)
            for relative,h in outputs.items():
                p=self.run/relative
                valid=valid and p.is_file() and file_hash(p)==h
            if not valid:
                self.invalidate(name); return name
            item['status']='passed'
        self.save(state)
        return next((s for s in STAGES if state['stages'].get(s,{}).get('status')!='passed'),None)
