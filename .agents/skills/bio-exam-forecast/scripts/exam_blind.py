"""Export question DOM and visual assets without keys, models or provenance."""
import shutil
from pathlib import Path
from urllib.parse import unquote
from exam_check import check_set,locate
from exam_contract import ExamError
from exam_dom import parse,outer
from exam_sources import sha

def write_blind(html,output):
 html=Path(html).resolve();output=Path(output).resolve()
 errors=check_set(html)
 if errors:raise ExamError('\n'.join(errors))
 if output==html or output.exists():raise ExamError('새 blind 출력 경로 필요')
 root=parse(html.read_text(encoding='utf-8'));cards=list(root.find_all(lambda n:n.tag=='article' and 'card' in n.classes))
 output.parent.mkdir(parents=True,exist_ok=True)
 allowed={'problem','exam-input'}
 for card in cards:
  card.attrs={k:v for k,v in card.attrs.items() if k in ('id','class')}
  card.children=[n for n in card.children if not isinstance(n,str) and (n.tag=='h3' or allowed.intersection(n.classes))]
  for n in card.find_all(lambda n:True):
   n.attrs={k:v for k,v in n.attrs.items() if not k.startswith('data-') and not k.startswith('on')}
   if n.tag=='img':
    source=(html.parent/unquote(n.attrs['src'])).resolve();assets=output.parent/(output.stem+'_assets');assets.mkdir(exist_ok=True)
    target=assets/(sha(source)[:16]+source.suffix);shutil.copyfile(source,target);n.attrs['src']=target.relative_to(output.parent).as_posix()
 styles='body{max-width:1000px;margin:auto;padding:18px;font-family:sans-serif}.card{border:1px solid #aaa;margin:15px 0;padding:20px}img,svg{max-width:100%;height:auto}input[type=text]{width:90%;padding:12px}label{display:block;padding:8px}'
 output.write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+styles+'</style><title>독립 풀이용 시험</title><main>'+''.join(outer(c) for c in cards)+'</main></html>',encoding='utf-8')
 return output
