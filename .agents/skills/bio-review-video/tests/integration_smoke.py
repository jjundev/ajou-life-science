"""Explicit local integration harness; never calls a paid API."""
import argparse,json
from pathlib import Path
from _util import ROOT,minimal_manifest,pcm
from lib.cache import atomic_json,file_hash
from lib.theme import snapshot_theme
from lib.composition import stage_assets,assemble
from lib.timing import build_timeline,write_subtitles
from lib.render import probe_backends,render_parts,mux
from lib.verify import verify_media,verify_audio,check_sources

def main():
    p=argparse.ArgumentParser(); p.add_argument('--run',required=True); p.add_argument('--assets',required=True)
    p.add_argument('--hyperframes-entry',required=True); args=p.parse_args()
    run=Path(args.run).resolve(); run.mkdir(parents=True,exist_ok=True)
    m=minimal_manifest()
    m['scenes'].append(dict(m['scenes'][0],id='scene-review',template_kind='review',visual='발효 복습'))
    m['segments'].append(dict(m['segments'][0],id='seg-atp-2',text='전자 전달을 복습합니다.',caption='전자 전달 과정'))
    m['segments'].append(dict(m['segments'][0],id='seg-review',scene_id='scene-review',text='발효는 NAD+를 재생합니다.',caption='발효 → NAD⁺ 재생'))
    atomic_json(run/'manifest.json',m)
    fragment=run/'source/scene-fragments'; fragment.mkdir(parents=True,exist_ok=True)
    for scene in m['scenes']:
        sid=scene['id']
        body=('<section class="topic"><h3>'+scene['visual']+'</h3><div class="tags"><span class="tag">생명과학 · 복습</span></div>'
          '<div class="layer eli5"><strong class="layer-title">쉽게 말하면</strong><p class="lead" id="'+sid+'-number">32 ATP</p></div>'
          '<div class="layer warn"><strong class="layer-title">꼭 기억해요</strong><p>수업의 기준과 조건을 함께 기억합니다.</p></div>'
          '<div class="layer supp"><span class="badge supp">보충</span><p>반복 설명은 통합하고 학습 내용은 보존합니다.</p></div></section>')
        (fragment/(sid+'.html')).write_text(body,encoding='utf-8')
        seg=next(s for s in m['segments'] if s['scene_id']==sid)
        atomic_json(fragment/(sid+'.motion.json'),[{'target':'#'+sid+'-number','segment_id':seg['id'],'kind':'count','from':{'textContent':0},'to':{'textContent':32},'duration_s':.6}])
    audio=[]
    for s in m['segments']:
        path=pcm(run/'assets/voice'/(s['id']+'.wav'))
        audio.append({'id':s['id'],'path':path.relative_to(run).as_posix(),'samples':24000,'rate':24000,'sha256':file_hash(path)})
    atomic_json(run/'source/audio.json',{'voices':audio})
    t=build_timeline(m,audio); atomic_json(run/'source/timeline.json',t); write_subtitles(t,run)
    theme=snapshot_theme(ROOT/'.agents/skills/bio-review-pack',run); stage_assets(Path(args.assets),run)
    parts=assemble(m,t,theme,run)
    backend=probe_backends(run); backend['hyperframes_entry']=args.hyperframes_entry
    rendered=render_parts(parts,run,backend); mux(rendered,audio,t,run/'review.mp4')
    media=verify_media(run/'review.mp4',t); sound=verify_audio(run,audio,t)
    atomic_json(run/'verification/media.json',media); atomic_json(run/'verification/audio.json',sound)
    source=check_sources(run,args.hyperframes_entry,timeout=180)
    atomic_json(run/'verification/source.json',source)
    print(json.dumps({'media':media['status'],'audio':sound['status'],'source':source,'backend':backend},ensure_ascii=False,indent=2))
    return 0 if media['status']==sound['status']==source['status']=='passed' else 1
if __name__=='__main__': raise SystemExit(main())
