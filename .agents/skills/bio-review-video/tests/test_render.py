import tempfile,unittest,subprocess,json,shutil
from pathlib import Path
from _util import pcm
from lib.render import choose_backend,mux,probe_backends
from lib.cache import file_hash

class RenderTest(unittest.TestCase):
    def test_cpu_fallback(self):
        b=choose_backend([{'encoder':'h264_nvenc','ok':False,'seconds':0,'workers':1},
                          {'encoder':'libx264','ok':True,'seconds':2,'workers':1}])
        self.assertEqual(b['encoder'],'libx264')
    def test_probe_duration_not_part_of_render_key(self):
        from lib.render import stable_backend
        a={'encoder':'h264_nvenc','seconds':1,'workers':1,'ok':True}
        b=dict(a,seconds=2,workers=2)
        self.assertEqual(stable_backend(a),stable_backend(b))
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg required')
    def test_mux_korean_quote_path_and_decode(self):
        with tempfile.TemporaryDirectory(prefix="생명 O'Brien ") as d:
            run=Path(d); video=run/'original.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=1920x1080:r=30',
              '-frames:v','60','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',str(video)],check=True)
            before=file_hash(video); pcm(run/'voice.wav',48000)
            t={'rate':24000,'total_samples':48000,'total_frames':60,'segments':[{'id':'s','start_sample':0,'end_sample':48000}]}
            mux([video],[{'id':'s','path':'voice.wav','samples':48000}],t,run/'review.mp4')
            subprocess.run(['ffmpeg','-v','error','-i',str(run/'review.mp4'),'-f','null','-'],check=True)
            self.assertEqual(before,file_hash(video))
            data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(run/'review.mp4')]))
            self.assertEqual(sum(s['codec_type']=='audio' for s in data['streams']),1)
