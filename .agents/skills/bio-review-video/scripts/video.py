"""Stage CLI: agents author content; helpers execute repeatable work."""
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import argparse,json,shutil,uuid,subprocess
from lib.sources import discover
from lib.manifest import require_ready,coverage_rows
from lib.cache import atomic_json,file_hash
from lib.state import RunStore,stage_fingerprint
from lib.budget import Budget
from lib.vertex_tts import load_key,live_transport,synthesize
from lib.theme import snapshot_theme
from lib.composition import stage_assets,assemble
from lib.timing import build_timeline,write_subtitles
from lib.render import probe_backends,render_parts,mux
from lib.revoice import retime_input,plan_revoice,render_revoice,picture_fingerprint
from lib.verify import verify_media,verify_audio,verify_sync,check_sources,review_fingerprint,verify_run,publish_latest

SKILL=Path(__file__).resolve().parents[1]
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def output(value): print(json.dumps(value,ensure_ascii=False,indent=2))
def finish(run,stage,paths):
    store=RunStore(run); state=store.load()
    previous=state.get('stages',{}).get(stage,{})
    if previous and previous.get('input_hash')!=stage_fingerprint(run,stage):
        store.invalidate(stage); state=store.load()
    state.setdefault('stages',{})[stage]={'status':'passed','input_hash':stage_fingerprint(run,stage),'output_hashes':{Path(p).relative_to(run).as_posix():file_hash(p) for p in paths}}
    store.save(state)
def config_for(args,run):
    config=read(SKILL/'assets/defaults.json')
    if (run/'config.json').exists(): config.update(read(run/'config.json'))
    if args.config: config.update(read(args.config))
    if args.voice: config['voice']=args.voice
    if args.env_file: config['env_file']=str(Path(args.env_file).resolve())
    allowed=set(read(SKILL/'assets/defaults.json'))|{'env_file','price','direction','hyperframes_entry'}
    if set(config)-allowed: raise ValueError('unknown config keys; never put credentials in config')
    config['direction']=(SKILL/'assets/vertex-direction.txt').read_text(encoding='utf-8').strip()
    return config
def parser():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('prepare'); q.add_argument('selector',nargs='?')
    q.add_argument('--repo',required=True); q.add_argument('--review',action='store_true'); q.add_argument('--from-run')
    for name in ('check','tts','assemble','render','verify','resume','revoice'):
        q=sub.add_parser(name); q.add_argument('--run',required=True)
        if name=='tts': q.add_argument('--approve-review',action='store_true')
        if name=='assemble': q.add_argument('--pack',required=True); q.add_argument('--assets-from')
        if name in ('render','verify','revoice'): q.add_argument('--hyperframes-entry')
        if name=='revoice': q.add_argument('--source-run',required=True)
    for q in sub.choices.values():
        q.add_argument('--config'); q.add_argument('--voice'); q.add_argument('--env-file')
    return p

def main(argv=None):
    args=parser().parse_args(argv); run=None
    try:
        if args.command=='prepare':
            repo=Path(args.repo).resolve()
            if args.from_run:
                old=Path(args.from_run).resolve(); selected=read(old/'manifest.json')['range']; inputs=read(old/'source/inputs.json')
            else:
                if not args.selector: raise ValueError('selector is required')
                inputs=discover(repo,args.selector); selected=inputs['range']
            run=repo/'복습영상'/selected/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
            run.mkdir(parents=True)
            if args.from_run:
                for folder in ('source','assets'): shutil.copytree(old/folder,run/folder)
                shutil.copyfile(old/'manifest.json',run/'manifest.json')
                if (old/'config.json').exists(): shutil.copyfile(old/'config.json',run/'config.json')
            else:
                for rec in inputs['files']:
                    p=Path(rec['path']); target=run/'source/inputs'/(rec['id']+p.suffix)
                    target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,target)
                    rec['snapshot']=target.relative_to(run).as_posix()
            atomic_json(run/'source/inputs.json',inputs); atomic_json(run/'config.json',config_for(args,run))
            RunStore(run).save({'schema_version':1,'range':selected,'review':args.review,'source_run':str(old) if args.from_run else None,'stages':{}})
            finish(run,'inputs',[run/'source/inputs.json'])
            output({'run':str(run),'next':'author manifest, coverage and scene fragments','paid_requests':0}); return 0
        run=Path(args.run).resolve()
        with RunStore(run).lock():
            if args.command=='resume':
                if args.config or args.voice or args.env_file: atomic_json(run/'config.json',config_for(args,run))
                output({'run':str(run),'next':RunStore(run).recover(),'state':RunStore(run).load()}); return 0
            config=config_for(args,run); atomic_json(run/'config.json',config)
            RunStore(run).recover()
            required={'check':'inputs','tts':'script','assemble':'voice','render':'composition','revoice':'composition','verify':'render'}[args.command]
            if RunStore(run).load().get('stages',{}).get(required,{}).get('status')!='passed':
                raise ValueError('complete or refresh prerequisite stage: '+required)
            m=read(run/'manifest.json'); require_ready(m)
            if args.command=='check':
                atomic_json(run/'source/coverage.json',{'rows':coverage_rows(m)})
                finish(run,'coverage',[run/'manifest.json',run/'source/coverage.json']); finish(run,'script',[run/'manifest.json'])
                output({'status':'ready','rows':len(coverage_rows(m))}); return 0
            if args.command=='tts':
                state=RunStore(run).load()
                if state.get('review') and not state.get('review_approved'):
                    if not args.approve_review: output({'status':'awaiting_review','run':str(run)}); return 0
                    state['review_approved']=True; RunStore(run).save(state)
                key=load_key(config.get('env_file'))
                audio=synthesize(m['segments'],run,config,Budget(run/'cost-ledger.json',Decimal(config['budget_usd'])),live_transport(key,config['model']))
                finish(run,'voice',[run/'source/audio.json']+[run/a['path'] for a in audio])
                output({'status':'passed','paragraphs':len(audio)}); return 0
            audio=read(run/'source/audio.json')['voices']; timeline=build_timeline(m,audio)
            atomic_json(run/'source/timeline.json',timeline); write_subtitles(timeline,run)
            finish(run,'timing',[run/'source/timeline.json',run/'narration.srt',run/'chapters.txt'])
            if args.command=='assemble':
                theme=snapshot_theme(Path(args.pack),run)
                if args.assets_from: stage_assets(Path(args.assets_from),run)
                if not (run/'assets/fonts/fonts.css').is_file() or not (run/'assets/vendor/gsap.min.js').is_file():
                    raise ValueError('stage local fonts and GSAP with --assets-from')
                parts=assemble(m,timeline,theme,run)
                finish(run,'composition',[run/'index.html',run/'source/parts.json']+[run/p['entry'] for p in parts])
                output({'status':'passed','scenes':len(parts)}); return 0
            if args.command in ('render','revoice'):
                entry=args.hyperframes_entry or config.get('hyperframes_entry')
                if not entry: raise ValueError('--hyperframes-entry required')
                backend=probe_backends(run); backend['hyperframes_entry']=str(Path(entry).resolve())
                parts=read(run/'source/parts.json')['parts']
                if args.command=='render': rendered=render_parts(parts,run,backend)
                else:
                    old=Path(args.source_run).resolve(); source=old/'review.mp4'
                    if old==run: raise ValueError('revoice requires a separate run')
                    oldm=read(old/'manifest.json'); unchanged=set()
                    for s in m['scenes']:
                        sid=s['id']; oldscene=next((x for x in oldm['scenes'] if x['id']==sid),None)
                        paths=[Path('source/scene-fragments')/(sid+ext) for ext in ('.html','.motion.json')]
                        same_segments=[x for x in m['segments'] if x['scene_id']==sid]==[x for x in oldm['segments'] if x['scene_id']==sid]
                        same_theme=read(old/'source/theme.json')==read(run/'source/theme.json')
                        if s==oldscene and same_segments and same_theme and picture_fingerprint(old,sid)==picture_fingerprint(run,sid) and all((old/p).exists() and file_hash(old/p)==file_hash(run/p) for p in paths): unchanged.add(sid)
                    windows=plan_revoice(retime_input(read(old/'source/timeline.json')),retime_input(timeline),file_hash(source),unchanged)
                    needed={w['scene_id'] for w in windows if w['mode']=='rerender'}; selected=[p for p in parts if p['id'] in needed]
                    replacements={p['id']:v for p,v in zip(selected,render_parts(selected,run,backend))} if selected else {}
                    rendered=render_revoice(source,windows,run,backend,replacements)
                mux(rendered,audio,timeline,run/'review.mp4'); finish(run,'render',[run/'review.mp4'])
                output({'status':'passed','video':str(run/'review.mp4'),'backend':backend}); return 0
            if args.command=='verify':
                key=review_fingerprint(run,m)
                reports=read(run/'verification/reviews.json') if (run/'verification/reviews.json').exists() else {}
                media=verify_media(run/'review.mp4',timeline); sound=verify_audio(run,audio,timeline)
                atomic_json(run/'verification/media.json',media); atomic_json(run/'verification/audio.json',sound)
                reports['media']=dict(media,input_hash=key,evidence=['verification/media.json'])
                sync=verify_sync(run,audio,timeline); atomic_json(run/'verification/sync.json',sync)
                reports['sync']=dict(sync,input_hash=key,evidence=['verification/sync.json'])
                if sound['status']!='passed': reports['audio']=dict(sound,input_hash=key,evidence=['verification/audio.json'])
                if args.hyperframes_entry: reports['source']=dict(check_sources(run,args.hyperframes_entry),input_hash=key)
                result=verify_run(run,m,reports)
                if result['complete']:
                    publish_latest(run,result); finish(run,'verify',[run/'verification/report.json']); finish(run,'publish',[run/'review.mp4'])
                output({'status':'passed' if result['complete'] else 'unverified','input_hash':key,'report':str(run/'verification/report.json')})
                return 0 if result['complete'] else 1
    except (ValueError,RuntimeError,OSError,KeyError,subprocess.SubprocessError) as ex:
        reason='external tool timed out or failed' if isinstance(ex,subprocess.SubprocessError) else str(ex)
        if run and (run/'run.json').is_file() and args.command not in ('prepare','resume'):
            store=RunStore(run)
            try:
                with store.lock():
                    state=store.load()
                    stage={'check':'coverage','tts':'voice','assemble':'composition','render':'render','revoice':'render','verify':'verify'}[args.command]
                    state.setdefault('stages',{})[stage]={'status':'failed','errors':[reason]}; store.save(state)
            except RuntimeError:
                pass  # Another writer owns this run; never overwrite its state.
        output({'status':'failed','reason':reason,'run':str(run) if run else None}); return 1
    return 2
if __name__=='__main__': raise SystemExit(main())
