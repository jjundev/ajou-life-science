import json,sys,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
records=json.loads(sys.argv[1])
manifest=r/'generated-files.json'
history=json.loads(manifest.read_text()) if manifest.exists() else []
for item in records:
    page,panel=item['key'].split('/')
    subprocess.run(['python3','.agents/skills/bio-review-comic/scripts/comic.py','register-image','--run',str(r),'--page',page,'--panel',panel,'--image',item['path']],check=True,stdout=subprocess.DEVNULL)
history.extend(records)
manifest.write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['python3','.agents/skills/bio-review-comic/scripts/comic.py','prompts','--run',str(r)],check=True,stdout=subprocess.DEVNULL)
j=json.loads((r/'prompts.json').read_text())
print(json.dumps({'registered':len(records),'valid':j['count']-j['pending'],'pending':j['pending']}))
