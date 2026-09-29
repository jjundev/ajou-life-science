from pathlib import Path
from decimal import Decimal
import json,threading
from .cache import atomic_json,file_lock

_locks={}; _guard=threading.Lock()

class Budget:
    def __init__(self,path,limit_usd):
        self.path=Path(path); self.limit=Decimal(str(limit_usd))
        if not self.limit.is_finite() or self.limit<0: raise ValueError('invalid budget')
        with _guard: self.lock=_locks.setdefault(str(self.path.resolve()),threading.RLock())
    def _load(self):
        return json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {'requests':{}}
    def _used(self,data):
        return sum((Decimal(r.get('actual') or r['reserved']) for r in data['requests'].values()),Decimal(0))
    def remaining(self):
        with self.lock: return max(Decimal(0),self.limit-self._used(self._load()))
    def reserve(self,request_id,upper_usd):
        value=Decimal(str(upper_usd))
        if not value.is_finite() or value<=0: raise ValueError('invalid request bound')
        with self.lock, file_lock(self.path.with_suffix('.lock')):
            data=self._load()
            if request_id in data['requests']: raise ValueError('duplicate request ID')
            if self._used(data)+value>self.limit: return False
            data['requests'][request_id]={'reserved':str(value),'actual':None,'status':'reserved'}
            atomic_json(self.path,data); return True
    def settle(self,request_id,actual_usd):
        with self.lock, file_lock(self.path.with_suffix('.lock')):
            data=self._load(); row=data['requests'][request_id]
            if actual_usd is not None:
                cost=Decimal(str(actual_usd))
                if not cost.is_finite() or cost<0: raise ValueError('invalid actual cost')
                row['actual']=str(cost)
            row['status']='unknown' if actual_usd is None else 'settled'
            atomic_json(self.path,data)
