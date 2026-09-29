from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,os,shutil,subprocess,time,wave
from .cache import digest,file_hash,cache_valid,atomic_json

def command(args,cwd=None,timeout=300):
    return subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',
       timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)

def probe_media(path):
    r=command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path])
    if r.returncode: raise ValueError('ffprobe failed: '+str(path))
    return json.loads(r.stdout)

def frames_ok(path,frames):
    try:
        s=next(s for s in probe_media(path)['streams'] if s['codec_type']=='video')
        return int(s['nb_frames'])==frames and int(s['width'])==1920 and int(s['height'])==1080
    except (ValueError,KeyError,StopIteration,OSError): return False

def choose_backend(probes):
    valid=[p for p in probes if p['ok']]
    if not valid: raise RuntimeError('No working video encoder')
    return min(valid,key=lambda p:p['seconds']/p['workers'])

def probe_backends(run):
    dest=Path(run)/'work/probes'; dest.mkdir(parents=True,exist_ok=True)
    versions={k:command([k,'-version']).stdout.splitlines()[0] for k in ('ffmpeg','ffprobe')}
    candidates=[]
    for encoder in ('libx264','h264_nvenc'):
        path=dest/(encoder+'.mp4'); start=time.monotonic()
        args=['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=black:s=1920x1080:r=30','-frames:v','60','-an','-c:v',encoder]
        args+=['-preset','veryfast'] if encoder=='libx264' else ['-preset','p5']
        r=command(args+['-pix_fmt','yuv420p',path],timeout=60)
        ok=r.returncode==0 and frames_ok(path,60) and command(['ffmpeg','-v','error','-i',path,'-f','null','-']).returncode==0
        candidates.append({'encoder':encoder,'ok':ok,'seconds':time.monotonic()-start,'workers':1,
          'capture_gpu':False,'decode_gpu':False,'tool_versions':versions})
    # Measure a two-worker NVENC encode only when VRAM headroom is observed.
    gpu=command(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits']) if shutil.which('nvidia-smi') else None
    nv=next(p for p in candidates if p['encoder']=='h264_nvenc')
    if nv['ok'] and gpu and gpu.returncode==0 and int(gpu.stdout.splitlines()[0])>=2048 and (os.cpu_count() or 1)>=4:
        def trial(i):
            p=dest/f'parallel-{i}.mp4'
            r=command(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=black:s=1920x1080:r=30',
              '-frames:v','60','-an','-c:v','h264_nvenc','-preset','p5',p])
            return r.returncode==0 and frames_ok(p,60)
        start=time.monotonic()
        with ThreadPoolExecutor(max_workers=2) as pool: ok=all(pool.map(trial,range(2)))
        candidates.append(dict(nv,ok=ok,seconds=time.monotonic()-start,workers=2))
    result=dict(choose_backend(candidates))
    atomic_json(Path(run)/'verification/backend-probes.json',{'probes':candidates,'chosen':result})
    return result

def render_parts(parts,run,backend):
    run=Path(run); dest=run/'renders/parts'; dest.mkdir(parents=True,exist_ok=True)
    entry=Path(backend['hyperframes_entry']).resolve()
    if not entry.is_file(): raise ValueError('HyperFrames Node entry is missing')
    versions=dict(backend.get('tool_versions',{}))
    version=command(['node',entry,'--version'])
    if version.returncode: raise RuntimeError('HyperFrames unavailable')
    versions['hyperframes']=version.stdout.strip()
    dependencies={p.relative_to(run).as_posix():file_hash(p) for p in run.rglob('*')
                  if p.is_file() and p.suffix in ('.html','.css','.js','.svg','.png','.jpg','.woff2') and 'renders' not in p.relative_to(run).parts and 'verification' not in p.relative_to(run).parts}
    def render(part):
        out=dest/(part['id']+'.mp4'); receipt=out.with_suffix('.json')
        key=digest({'part':part,'dependencies':dependencies,'backend':backend,'versions':versions})
        if receipt.exists():
            old=json.loads(receipt.read_text(encoding='utf-8'))
            if cache_valid(out,old,key) and frames_ok(out,part['frames']): return out
        pending=out.with_name(out.stem+'.pending.mp4')
        args=['node',entry,'render','--composition',part['entry'],'--quality','delivery','--workers','1','--output',str(pending)]
        if backend['encoder']=='h264_nvenc': args+=['--gpu']
        if backend.get('capture_gpu'): args+=['--browser-gpu']
        r=command(args,run,timeout=3600)
        out.with_suffix('.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        if r.returncode or not frames_ok(pending,part['frames']): raise RuntimeError('scene render failed: '+part['id'])
        os.replace(pending,out)
        atomic_json(receipt,{'key':key,'output_sha256':file_hash(out),'frames':part['frames']})
        return out
    with ThreadPoolExecutor(max_workers=max(1,min(backend.get('workers',1),len(parts)))) as pool:
        return list(pool.map(render,parts))

def mux(parts,audio,timeline,destination):
    destination=Path(destination); run=destination.parent; work=run/'work/mux'; work.mkdir(parents=True,exist_ok=True)
    sources=[Path(p).resolve() for p in parts]
    if destination.resolve() in sources: raise ValueError('refusing to overwrite source')
    lines=[]
    for i,p in enumerate(sources):
        target=work/f'part-{i:04d}.mp4'
        r=command(['ffmpeg','-y','-v','error','-i',p,'-map','0:v:0','-an','-c:v','copy',target])
        if r.returncode: raise RuntimeError('video-only extraction failed')
        lines.append("file '"+target.name+"'")
    (work/'concat.txt').write_text('\n'.join(lines),encoding='utf-8')
    pcm=bytearray(timeline['total_samples']*2); voices={a['id']:a for a in audio}
    for seg in timeline['segments']:
        rec=voices[seg['id']]; path=run/rec['path']
        with wave.open(str(path),'rb') as f:
            if (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())!=(1,2,24000,rec['samples']):
                raise ValueError('audio format/length changed')
            raw=f.readframes(f.getnframes())
        start=seg['start_sample']*2
        if start+len(raw)>len(pcm): raise ValueError('audio exceeds timeline')
        pcm[start:start+len(raw)]=raw
    mixed=work/'narration.wav'
    with wave.open(str(mixed),'wb') as f:
        f.setparams((1,2,24000,0,'NONE','not compressed')); f.writeframes(pcm)
    pending=destination.with_name(destination.stem+'.pending.mp4')
    r=command(['ffmpeg','-y','-v','error','-f','concat','-safe','1','-i',work/'concat.txt','-i',mixed,
      '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',pending])
    if r.returncode or not frames_ok(pending,timeline['total_frames']): raise RuntimeError('mux failed')
    decode=command(['ffmpeg','-v','error','-i',pending,'-f','null','-'],timeout=1800)
    if decode.returncode: raise RuntimeError('final decode failed')
    os.replace(pending,destination)
