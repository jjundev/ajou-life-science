"""Behavioral contracts for the comic pipeline; test images are never lesson art."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import unicodedata
import zlib
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / 'comic.py'


def png(path):
    """A valid, visibly synthetic test raster, not generated comic content."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (b'\x00' + bytes((218, 231, 247)) * 640) * 400
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 640, 400, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
    return path


def source(repo):
    folder = repo / unicodedata.normalize('NFD', '복습노트') / '1105'
    folder.mkdir(parents=True)
    path = folder / unicodedata.normalize('NFD', '정리노트_1105_Test.html')
    path.write_text('''<!DOCTYPE html><html><head><title>생명 노트</title></head>
<body data-range="1105"><main><div class="hero"><h1>생명 노트</h1></div>
<section id="s0"><h2>생명의 재료</h2>
<article class="topic" id="s0-miller"><h3>유기물과 생명</h3>
<div class="layer eli5"><p>유기물이 검출되었어요.</p></div>
<div class="layer formal"><p>살아 있는 세포를 만든 것은 아니에요.</p></div>
<div class="layer supp" id="extra"><span class="badge supp">보충 · 수업에서 다루지 않았어요</span><p>반응에는 조건이 필요해요.</p></div>
<div class="sum" hidden><p class="sum-lead">재료와 세포는 달라요.</p></div></article>
<article class="topic" id="s0-recap"><h3>지난 수업 복습</h3><p>재료와 생명을 구별해요.</p></article>
</section><section id="s1"><h2>마무리</h2>
<article class="topic" id="s1-cheatsheet"><h3>시험 직전 한 장 요약</h3><table><tr><th>주제</th><th>핵심</th></tr><tr><td>실험</td><td>재료 검출</td></tr></table></article>
<article class="topic" id="s1-next"><h3>다음 시간 예고</h3><p>아직 배우지 않은 내용</p></article>
<article class="topic" id="s1-links"><h3>함께 보면 좋은 자료</h3><a href="other.html">자료</a></article>
</section></main></body></html>''', encoding='utf-8')
    return path


class ComicPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.exists():
            return
        spec = importlib.util.spec_from_file_location('bio_comic', SCRIPT)
        cls.api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.api)

    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'comic.py must implement the approved pipeline')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.note = source(self.repo)
        self.run = Path(self.tmp.name) / 'run'
        self.api.extract(self.repo, '1105', self.run)

    def read(self, name):
        return json.loads((self.run / name).read_text())

    def write(self, name, data):
        (self.run / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def ready(self, held=False):
        book, src = self.read('storyboard.json'), self.read('source.json')
        book['characters'] = [{'id': 'guide', 'name': '안내자', 'role': '관계 설명', 'appearance': '남색 조끼와 둥근 안경', 'voice': '짧고 정확한 설명'}, {'id': 'student', 'name': '학생', 'role': '질문과 자기수정', 'appearance': '노란 후드와 검은 단발', 'voice': '구체적인 질문'}]
        book['style'] = '생물의 실제 구조를 살린 절제된 학습만화. 같은 대상의 색과 모양 유지.'
        for index, page in enumerate(book['pages']):
            if held and index == 1:
                page.update(status='held', reason='그림 검토 보류')
                continue
            evidence = src['topics'][index]['evidence']
            refs = [e['id'] for e in evidence]
            page.update(clarification={'confusion': '재료 검출과 생명 생성의 혼동', 'understanding': '두 성과를 구별한다', 'evidence': refs}, analogy={'familiar': '부품과 완성품', 'mapping': [{'familiar': '부품', 'biology': '작은 유기물', 'evidence': refs}], 'limit': '생명은 사람이 조립하는 기계와 같지 않다', 'panels': [1], 'limit_panel': 4}, narrative={'mode': 'dialogue', 'cast': ['guide', 'student']}, note_link={'before': '재료와 완성품의 차이를 ', 'label': '재료와 생명 만화', 'after': '에서 비교해 보세요.'})
            page.update(status='ready', question='무엇이 검출되었을까?', summary={'text': '재료와 살아 있는 세포를 구별해요.', 'evidence': refs}, terms=[],
                        coverage=[{'evidence': ref, 'panels': [1], 'reason': ''} for ref in refs],
                        panels=[{'scene': f'실험의 관찰 상태 {n}', 'caption': '검출 결과를 확인해요.', 'characters': ['guide', 'student'], 'dialogue': [{'speaker': 'guide', 'text': '세포가 만들어진 것은 아니야.'}, {'speaker': 'student', 'text': '재료 검출과 구별해야겠네요.'}], 'alt': f'실험 결과를 비교하는 장면 {n}', 'evidence': refs} for n in range(1, 5)])
        self.write('storyboard.json', book)
        return book

    def images(self):
        art = png(Path(self.tmp.name) / 'fixture.png')
        for page in self.read('storyboard.json')['pages']:
            if page['status'] == 'ready':
                for n in range(1, len(page['panels']) + 1):
                    self.api.register_image(self.run, page['id'], n, art)

    def reviews(self, browser=True):
        fp = self.api.fingerprints(self.run)
        reports = {'pages': {pid: {kind: {'status': 'passed', 'fingerprint': value, 'notes': ['source and rendered panel checked']} for kind, value in data.items()} for pid, data in fp['pages'].items()}}
        if browser:
            png(self.run / 'checks' / 'fixture.png')
            reports['browser'] = {'status': 'passed', 'fingerprint': fp['browser'], 'notes': ['fixture browser evidence'], 'views': [{'width': w, 'height': h, 'theme': t, 'screenshot': 'checks/fixture.png'} for w, h in ((1440, 900), (375, 812)) for t in ('light', 'dark')]}
        self.write('review.json', reports)

    def test_inventory_covers_review_summary_and_excludes_future_and_links(self):
        src = self.read('source.json')
        self.assertEqual([(t['id'], t['include']) for t in src['topics']], [('s0-miller', True), ('s0-recap', True), ('s1-cheatsheet', True), ('s1-next', False), ('s1-links', False)])
        evidence = src['topics'][0]['evidence']
        self.assertEqual([e['text'] for e in evidence], ['유기물이 검출되었어요.', '살아 있는 세포를 만든 것은 아니에요.', '반응에는 조건이 필요해요.'])
        self.assertEqual(evidence[-1]['scope'], 'supplement')

    def test_explicit_nfc_path_resolves_nfd_and_ambiguity_does_not_choose(self):
        self.assertEqual(self.api.resolve(self.repo, unicodedata.normalize('NFC', str(self.note))), self.note.resolve())
        other = self.note.with_name('정리노트_1105_Other.html')
        other.write_text(self.note.read_text())
        with self.assertRaisesRegex(ValueError, '여러 후보'):
            self.api.resolve(self.repo, '1105')

    def test_unknown_nonlearning_page_is_not_silently_excluded(self):
        self.note.write_text(self.note.read_text().replace('id="s1-links"', 'id="s1-custom"').replace('함께 보면 좋은 자료', '새로운 분류'))
        with self.assertRaisesRegex(ValueError, '근거|본문'):
            self.api.extract(self.repo, '1105', self.run / 'unknown')

    def test_source_drift_blocks_check_and_missing_source_blocks_build(self):
        self.ready()
        self.note.write_text(self.note.read_text().replace('유기물이 검출', '세포가 검출'))
        with self.assertRaisesRegex(ValueError, '원본.*변경'):
            self.api.check(self.run, 'storyboard')
        self.note.unlink()
        with self.assertRaisesRegex(ValueError, '원본'):
            self.api.build(self.run)

    def test_panel_limit_and_complete_evidence_coverage(self):
        book = self.ready()
        book['pages'][0]['panels'] = book['pages'][0]['panels'][:3]
        self.write('storyboard.json', book)
        with self.assertRaisesRegex(ValueError, '4.*8'):
            self.api.check(self.run, 'storyboard')
        book = self.ready()
        book['pages'][0]['coverage'].pop()
        self.write('storyboard.json', book)
        with self.assertRaisesRegex(ValueError, '근거.*누락|coverage'):
            self.api.check(self.run, 'storyboard')

    def test_unknown_refs_and_unsupported_omissions_are_rejected(self):
        book = self.ready()
        book['pages'][0]['panels'][0]['evidence'] = ['invented']
        self.write('storyboard.json', book)
        with self.assertRaisesRegex(ValueError, '근거'):
            self.api.check(self.run, 'storyboard')
        book = self.ready()
        book['pages'][0]['coverage'][0] = {'evidence': book['pages'][0]['coverage'][0]['evidence'], 'panels': [], 'reason': ''}
        self.write('storyboard.json', book)
        with self.assertRaisesRegex(ValueError, '생략'):
            self.api.check(self.run, 'storyboard')

    def test_prompt_reuse_requires_exact_prompt_and_image_hash(self):
        self.ready(); self.images()
        self.assertTrue(all(j['reusable'] for j in self.api.prompts(self.run)['jobs']))
        book = self.read('storyboard.json'); book['pages'][0]['panels'][0]['scene'] += ' 다른 방향'
        self.write('storyboard.json', book)
        jobs = self.api.prompts(self.run)['jobs']
        self.assertFalse(jobs[0]['reusable']); self.assertTrue(jobs[1]['reusable'])
        with self.assertRaisesRegex(ValueError, '그림.*변경|그림.*오래'):
            self.api.check(self.run, 'images')

    def test_missing_and_invalid_rasters_cannot_publish(self):
        self.ready()
        with self.assertRaisesRegex(ValueError, '그림'):
            self.api.check(self.run, 'images')
        bad = Path(self.tmp.name) / 'bad.png'; bad.write_text('<svg/>')
        with self.assertRaisesRegex(ValueError, '이미지|그림|PNG'):
            self.api.register_image(self.run, 's0-miller', 1, bad)

    def test_build_escapes_text_preserves_supplement_and_source_links(self):
        book = self.ready(); book['pages'][0]['panels'][0]['caption'] = '<script>alert(1)</script>'
        self.write('storyboard.json', book); self.images()
        output = self.api.build(self.run)
        text = output.read_text()
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', text)
        self.assertIn('보충 · 수업에서 다루지 않았어요', text)
        self.assertIn('#s0-miller', text)
        self.assertIn('target="_self"', text)
        self.assertNotIn("'od-note-read:'", text)
        self.assertIn("'od-comic-read:'", text)

    def test_content_change_invalidates_reviews(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        self.assertEqual(self.api.check(self.run, 'reviewed')['status'], 'complete')
        book = self.read('storyboard.json'); book['pages'][0]['panels'][0]['dialogue'][0]['text'] += ' 새 설명'
        self.write('storyboard.json', book)
        self.images()
        with self.assertRaisesRegex(ValueError, '검토'):
            self.api.check(self.run, 'reviewed')

    def test_publish_requires_browser_review_and_preserves_previous_version(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews(browser=False)
        with self.assertRaisesRegex(ValueError, '브라우저'):
            self.api.publish(self.run)
        self.reviews(); result = self.api.publish(self.run)
        old_html = Path(result['html']).read_bytes()
        old_version = Path(result['version'])
        self.assertTrue(old_version.is_dir())
        result2 = self.api.publish(self.run)
        self.assertEqual(result['version'], result2['version'])
        self.assertEqual(Path(result2['html']).read_bytes(), old_html)
        self.assertIn('data-bio-comic', self.note.read_text())

    def test_held_pages_stay_visible_and_are_not_complete(self):
        self.ready(held=True); self.images()
        output = self.api.build(self.run)
        self.assertIn('그림 검토 보류', output.read_text())
        self.assertIn('id="s0-recap"', output.read_text())
        self.reviews()
        self.assertEqual(self.api.check(self.run, 'browser')['status'], 'partial')
        result = self.api.publish(self.run)
        self.assertEqual(result['status'], 'partial')
        self.assertIn('일부 보류', Path(result['html']).read_text())

    def test_extraction_is_non_destructive_and_reuses_only_unchanged_topics(self):
        self.ready(); self.images(); before = (self.run / 'storyboard.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '이미'):
            self.api.extract(self.repo, '1105', self.run)
        self.assertEqual((self.run / 'storyboard.json').read_bytes(), before)
        self.note.write_text(self.note.read_text().replace('재료와 생명을 구별', '재료와 세포를 비교'))
        newer = Path(self.tmp.name) / 'newer'
        self.api.extract(self.repo, '1105', newer, reuse=self.run)
        pages = json.loads((newer / 'storyboard.json').read_text())['pages']
        self.assertEqual([p['status'] for p in pages], ['ready', 'draft', 'ready'])

    def test_all_held_run_cannot_publish_empty_comic(self):
        book = self.ready()
        for page in book['pages']:
            page.update(status='held', reason='이미지 도구 사용 불가')
        self.write('storyboard.json', book)
        self.api.build(self.run); self.reviews()
        with self.assertRaisesRegex(ValueError, '모든|전부'):
            self.api.publish(self.run)

    def test_previous_html_keeps_working_image_and_original_links(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        first = self.api.publish(self.run)
        book = self.read('storyboard.json'); book['pages'][0]['panels'][0]['dialogue'][0]['text'] += ' 한 번 더 확인하자.'
        self.write('storyboard.json', book)
        self.images()
        self.api.build(self.run); self.reviews()
        second = self.api.publish(self.run)
        self.assertNotEqual(first['version'], second['version'])
        from comic_render import validate_output
        backup = Path(second['version']) / 'previous.html'
        self.assertTrue(backup.is_file())
        validate_output(backup)

    def test_metadata_failure_does_not_delete_published_images(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        import comic_render
        actual_write = comic_render.write
        def fail_latest(path, value):
            if Path(path).name == 'latest.json':
                raise OSError('simulated metadata disk failure')
            return actual_write(path, value)
        with patch.object(comic_render, 'write', side_effect=fail_latest):
            with self.assertRaisesRegex(OSError, 'metadata'):
                self.api.publish(self.run)
        published = next(self.note.parent.glob('학습만화_*.html'))
        comic_render.validate_output(published)
        recovered = self.api.publish(self.run)
        latest = Path(recovered['version']).parent.parent / 'latest.json'
        self.assertTrue(latest.is_file(), 'A successful retry must restore the publication index')
        self.assertEqual(json.loads(latest.read_text())['version'], recovered['version'])

    def test_clarification_analogy_and_speaker_contract(self):
        for field in ('clarification', 'analogy', 'narrative'):
            with self.subTest(field=field):
                book = self.ready(); del book['pages'][0][field]
                self.write('storyboard.json', book)
                with self.assertRaises(ValueError): self.api.check(self.run, 'storyboard')
        for mutation in ('unknown', 'no_dialogue', 'only_one', 'limit'):
            with self.subTest(mutation=mutation):
                book = self.ready(); page = book['pages'][0]
                if mutation == 'unknown': page['panels'][0]['dialogue'][0]['speaker'] = 'ghost'
                elif mutation == 'no_dialogue':
                    for panel in page['panels']: panel['dialogue'] = []
                elif mutation == 'only_one':
                    for panel in page['panels']: panel['dialogue'] = panel['dialogue'][:1]
                else: page['analogy']['limit'] = ''
                self.write('storyboard.json', book)
                with self.assertRaises(ValueError): self.api.check(self.run, 'storyboard')

    def test_character_and_dialogue_change_invalidates_image_prompt(self):
        self.ready(); self.images()
        book = self.read('storyboard.json'); book['characters'][0]['appearance'] += ' 빨간 가방'
        self.write('storyboard.json', book)
        self.assertFalse(self.api.prompts(self.run)['jobs'][0]['reusable'])
        self.images(); book['pages'][0]['panels'][0]['dialogue'][0]['text'] += ' 새 의미'
        self.write('storyboard.json', book)
        self.assertFalse(self.api.prompts(self.run)['jobs'][0]['reusable'])

    def test_object_only_page_keeps_registered_offscreen_conversation(self):
        book = self.ready()
        for page in book['pages']:
            for panel in page['panels']:
                panel['characters'] = []
                panel['scene'] = '책상 위 부품과 완성품만 확대한다. 사람은 화면 밖에 있다.'
        self.write('storyboard.json', book)
        self.assertEqual(self.api.check(self.run, 'storyboard')['status'], 'complete')
        self.assertIn('No humans, faces, hands', self.api.prompts(self.run)['jobs'][0]['prompt'])

    def test_dialogue_is_inside_scene_before_art_and_outside_caption(self):
        self.ready(); self.images()
        from comic_source import parse
        root = parse(self.api.build(self.run).read_text())
        scenes = [n for n in root.walk() if 'comic-scene' in n.classes]
        self.assertEqual(len(scenes), 12)
        for scene in scenes:
            nodes = list(scene.walk())
            balloons = [n for n in nodes if 'comic-dialogue' in n.classes]
            self.assertEqual(len(balloons), 2)
            self.assertLess(nodes.index(balloons[0]), next(i for i, n in enumerate(nodes) if n.tag == 'img'))
        for caption in [n for n in root.walk() if n.tag == 'figcaption']:
            self.assertFalse(any('comic-dialogue' in n.classes for n in caption.walk()))

    def test_links_dry_run_preserve_bytes_and_do_not_change_evidence(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        before = self.note.read_bytes(); inventory = self.read('source.json')
        result = self.api.publish(self.run, link_notes=False)
        self.assertEqual(self.note.read_bytes(), before)
        dry = self.api.link_notes(self.run, dry_run=True)
        self.assertTrue(dry['changed']); self.assertEqual(self.note.read_bytes(), before)
        linked = self.api.link_notes(self.run)
        self.assertTrue(linked['changed'])
        from comic_links import strip_links
        self.assertEqual(strip_links(self.note.read_text()).encode(), before)
        self.assertEqual(self.api.check(self.run, 'browser')['status'], 'complete')
        self.assertFalse(self.api.link_notes(self.run)['changed'])
        newer = Path(self.tmp.name) / 'linked-new'
        self.api.extract(self.repo, '1105', newer)
        extracted = json.loads((newer / 'source.json').read_text())
        self.assertEqual(extracted['content_sha256'], inventory['content_sha256'])
        self.assertEqual(extracted['topics'], inventory['topics'])
        # Actual prose changes remain blocked even after linking.
        self.note.write_text(self.note.read_text().replace('유기물이 검출', '세포가 검출'))
        with self.assertRaisesRegex(ValueError, '원본.*변경'):
            self.api.link_notes(self.run)

    def test_links_exact_fragments_and_held_pages(self):
        self.ready(held=True); self.images(); self.api.build(self.run); self.reviews()
        result = self.api.publish(self.run)
        note = self.note.read_text()
        self.assertIn('#s0-miller', note); self.assertIn('#s1-cheatsheet', note)
        self.assertNotIn('#s0-recap', note)
        self.assertEqual(note.count('data-bio-comic='), 2)
        self.assertEqual([x['status'] for x in result['note_links']['results']], ['added', 'skipped', 'added'])

    def test_missing_anchor_does_not_insert_in_wrong_place(self):
        book = self.ready(); book['pages'][0]['note_link']['anchor_id'] = 'absent'
        self.write('storyboard.json', book); self.images(); self.api.build(self.run); self.reviews()
        result = self.api.publish(self.run)
        self.assertEqual(result['note_links']['results'][0]['reason'], 'ANCHOR_MISSING')
        self.assertNotIn('#s0-miller', self.note.read_text())
        self.assertIn('#s1-cheatsheet', self.note.read_text())

    def test_managed_block_tampering_is_not_ignored(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews(); self.api.publish(self.run)
        self.note.write_text(self.note.read_text().replace('에서 비교해 보세요.', '다른 사실로 바뀌었어요.'))
        with self.assertRaises(ValueError): self.api.check(self.run, 'storyboard')

    def test_explicit_single_page_scope_and_v1_reuse(self):
        run = Path(self.tmp.name) / 'sample'
        self.api.extract(self.repo, '1105', run, page='s0-miller')
        src = json.loads((run / 'source.json').read_text())
        self.assertEqual([t['id'] for t in src['topics'] if t['include']], ['s0-miller'])
        self.assertEqual(src['selection'], ['s0-miller'])
        old = self.read('storyboard.json'); old['schema_version'] = 1
        self.write('storyboard.json', old)
        new = Path(self.tmp.name) / 'v2'
        self.api.extract(self.repo, '1105', new, reuse=self.run)
        self.assertEqual(json.loads((new / 'storyboard.json').read_text())['schema_version'], 2)

    def test_one_character_explanation_and_silent_detail_panel(self):
        book = self.ready()
        for page in book['pages']:
            page['narrative'] = {'mode': 'explanation', 'cast': ['guide']}
            for panel in page['panels']:
                panel['characters'] = ['guide']; panel['dialogue'] = panel['dialogue'][:1]
            page['panels'][2]['characters'] = []; page['panels'][2]['dialogue'] = []
        self.write('storyboard.json', book)
        self.assertEqual(self.api.check(self.run, 'storyboard')['ready'], 3)

    def test_crlf_note_bytes_and_user_links_are_preserved(self):
        raw = self.note.read_bytes().replace(b'\n', b'\r\n')
        raw = raw.replace(b'</h3>', b'</h3><a title="a target=original" rel="bookmark" target="_blank" href="manual.html">manual</a>', 1)
        self.note.write_bytes(raw)
        self.run = Path(self.tmp.name) / 'crlf'
        self.api.extract(self.repo, '1105', self.run)
        self.ready(); self.images(); self.api.build(self.run); self.reviews(); self.api.publish(self.run)
        from comic_links import strip_links
        self.assertEqual(strip_links(self.note.read_bytes().decode()).encode(), raw)
        self.assertFalse(self.api.link_notes(self.run)['changed'])

    def test_hidden_anchor_is_skipped(self):
        self.note.write_text(self.note.read_text().replace('<div class="sum" hidden>', '<div id="hidden-summary" class="sum" hidden>', 1))
        self.run = Path(self.tmp.name) / 'hidden'
        self.api.extract(self.repo, '1105', self.run)
        book = self.ready(); book['pages'][0]['note_link']['anchor_id'] = 'hidden-summary'
        self.write('storyboard.json', book); self.images(); self.api.build(self.run); self.reviews()
        result = self.api.publish(self.run)
        self.assertEqual(result['note_links']['results'][0].get('reason'), 'ANCHOR_INVALID')

    def test_link_write_failure_keeps_published_comic_and_retries(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        import comic_links
        actual = comic_links.os.replace
        def fail_note(src, dest):
            if Path(dest).resolve() == self.note.resolve(): raise OSError('note write denied')
            return actual(src, dest)
        with patch.object(comic_links.os, 'replace', side_effect=fail_note):
            result = self.api.publish(self.run)
        self.assertTrue(Path(result['html']).is_file())
        self.assertEqual(result['note_links']['status'], 'failed')
        self.assertTrue(self.api.link_notes(self.run)['changed'])
        self.assertFalse(self.api.link_notes(self.run)['changed'])

    def test_archived_version_supports_link_only(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        result = self.api.publish(self.run, link_notes=False)
        linked = self.api.link_notes(Path(result['version']))
        self.assertTrue(linked['changed'])
        self.assertFalse(self.api.link_notes(Path(result['version']))['changed'])

    def test_link_only_rejects_missing_or_changed_published_art(self):
        self.ready(); self.images(); self.api.build(self.run); self.reviews()
        result = self.api.publish(self.run, link_notes=False)
        art = Path(result['version']) / 'images' / 's0-miller' / '01.png'
        art.unlink()
        before = self.note.read_bytes()
        with self.assertRaises(ValueError): self.api.link_notes(self.run)
        self.assertEqual(self.note.read_bytes(), before)

    def test_analogy_supplement_cannot_be_omitted_or_lose_badge(self):
        book = self.ready(); page = book['pages'][0]
        supplementary = page['panels'][0]['evidence'][-1]
        page['analogy']['mapping'] = [{'familiar': '작동 조건', 'biology': '반응 조건', 'evidence': [supplementary]}]
        for panel in page['panels']: panel['evidence'] = panel['evidence'][:-1]
        page['coverage'][-1] = {'evidence': supplementary, 'panels': [], 'reason': '주변 설명 생략'}
        self.write('storyboard.json', book)
        with self.assertRaises(ValueError): self.api.check(self.run, 'storyboard')
        page['panels'][2]['evidence'].append(supplementary)
        page['coverage'][-1] = {'evidence': supplementary, 'panels': [3], 'reason': ''}
        self.write('storyboard.json', book); self.images()
        text = self.api.build(self.run).read_text()
        analogy = text.split('class="comic-analogy"', 1)[1].split('</p>', 1)[0]
        self.assertIn('badge supp', analogy)


if __name__ == '__main__':
    unittest.main()
