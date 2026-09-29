import tempfile,unittest,json
from pathlib import Path
from _util import ROOT,minimal_manifest
from lib.theme import snapshot_theme
from lib.timing import build_timeline
from lib.composition import assemble

class CompositionTest(unittest.TestCase):
    def test_composition_and_invalid_target(self):
        with tempfile.TemporaryDirectory() as d:
            run=Path(d); m=minimal_manifest()
            theme=snapshot_theme(ROOT/'.agents/skills/bio-review-pack',run)
            p=run/'source/scene-fragments'; p.mkdir()
            (p/'scene-atp.html').write_text('<section class="topic"><h3 id="scene-atp-count">32 ATP</h3></section>',encoding='utf-8')
            motions=[{'target':'#scene-atp-count','segment_id':'seg-atp','kind':'count','from':{'textContent':0},'to':{'textContent':32},'duration_s':1}]
            (p/'scene-atp.motion.json').write_text(json.dumps(motions))
            t=build_timeline(m,[{'id':'seg-atp','samples':24000,'rate':24000,'path':'assets/voice/test.wav'}])
            parts=assemble(m,t,theme,run)
            page=(run/parts[0]['entry']).read_text(encoding='utf-8')
            self.assertIn('data-theme="dark"',page); self.assertIn('scene-atp-count',page)
            self.assertNotIn('class="clip video-caption"',page)
            self.assertIn('id="audio-seg-atp"',(run/'index.html').read_text(encoding='utf-8'))
            self.assertEqual(parts[0]['frames'],78)
            motions[0]['target']='#missing'
            (p/'scene-atp.motion.json').write_text(json.dumps(motions))
            with self.assertRaises(ValueError): assemble(m,t,theme,run)
    def test_rejects_executable_fragment(self):
        from lib.composition import validate_fragment
        for fragment in ('<img src="https://example.com/x">','<svg onload="alert(1)"></svg>','<script>bad()</script>'):
            with self.assertRaises(ValueError): validate_fragment(fragment,'scene-x')
