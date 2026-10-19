import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/weakness_pack.py'


class SelectionTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('weakness_pack', SCRIPT)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name).resolve() / 'repo'
        self.repo.mkdir()
        (self.repo / 'SSTT').mkdir()
        for name in ['0908 공부.md', '0910 공부 2.md', '0910 공부.md', '0922 공부.md']:
            (self.repo / 'SSTT' / name).write_text('학습자의 발언\n나중의 정정\n')

    def legacy(self, day='0908', inputs=None):
        out = self.repo / '약점노트' / day
        (out / '.pack').mkdir(parents=True)
        (out / '.assets/자료_문제설명_x').mkdir(parents=True)
        for kind in ['정리노트', '복습문제', '문제설명']:
            (out / f'{kind}_{day}_Legacy.html').write_text(kind)
            (out / '.assets' / f'{kind}_{day}_Legacy.md').write_text(kind)
        refs = inputs or [self.m.fingerprint(self.repo, self.repo / 'SSTT' / f'{day} 공부.md')]
        # Old absolute paths remain usable when a checkout moves.
        refs = [{**x, 'path': '/old/checkout/' + x['path']} for x in refs]
        (out / '.pack/source-manifest.json').write_text(json.dumps(refs))
        (out / '.assets/자료_문제설명_x/validation.json').write_text(json.dumps({k: {'status': 'pass'} for k in ['source_visual', 'content', 'independent', 'browser']}))
        return out

    def test_default_skips_existing_test_and_groups_numbered_files(self):
        self.legacy()
        plan = self.m.select(self.repo)
        self.assertEqual([x['date'] for x in plan['selected']], ['0910'])
        self.assertEqual([Path(x['path']).name for x in plan['selected'][0]['inputs']], ['0910 공부.md', '0910 공부 2.md'])

    def test_remaining_returns_separate_date_groups(self):
        self.legacy()
        self.assertEqual([x['date'] for x in self.m.select(self.repo, 'remaining')['selected']], ['0910', '0922'])

    def test_explicit_file_does_not_pull_other_same_day_file(self):
        plan = self.m.select(self.repo, 'SSTT/0910 공부 2.md')
        self.assertEqual(len(plan['selected'][0]['inputs']), 1)

    def test_changed_input_is_reported_without_silent_regeneration(self):
        self.legacy()
        (self.repo / 'SSTT/0908 공부.md').write_text('바뀐 발언')
        plan = self.m.select(self.repo)
        self.assertEqual(plan['catalog'][0]['status'], 'changed')
        self.assertEqual(plan['selected'][0]['date'], '0910')
        self.assertEqual(self.m.select(self.repo, '0908')['selected'], [])
        self.assertEqual(self.m.select(self.repo, '0908', regenerate=True)['selected'][0]['version'], 2)

    def test_new_file_in_completed_date_requires_group_regeneration(self):
        refs = [self.m.fingerprint(self.repo, self.repo/'SSTT/0910 공부.md')]
        self.legacy('0910', refs)
        self.assertEqual(self.m.select(self.repo, '0910')['catalog'][1]['status'], 'changed')

    def test_removed_file_changes_completed_date_group(self):
        refs = [self.m.fingerprint(self.repo, p) for p in (self.repo/'SSTT').glob('0910*.md')]
        self.legacy('0910', refs)
        (self.repo/'SSTT/0910 공부 2.md').unlink()
        self.assertEqual(self.m.select(self.repo, '0910')['catalog'][1]['status'], 'changed')

    def test_partial_pack_is_not_a_completed_record(self):
        out = self.legacy()
        next(out.glob('문제설명_*.html')).unlink()
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')

    def test_corrupt_ledger_is_incomplete_not_fresh(self):
        out = self.legacy()
        (out/'.pack/source-manifest.json').write_text('{broken')
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')
        self.assertEqual(self.m.select(self.repo)['selected'][0]['date'], '0910')

    def test_missing_ledger_is_incomplete_not_fresh(self):
        out = self.legacy()
        (out/'.pack/source-manifest.json').unlink()
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')

    def test_pack_review_requires_nonempty_local_evidence(self):
        run = self.repo.parent/'review-run';run.mkdir()
        path=run/'evidence.md';path.write_text('')
        item=dict(status='pass',reviewer='test',evidence='evidence.md')
        with self.assertRaisesRegex(ValueError, '비어'): self.m.review_evidence(run,item)
        path.write_text('확인한 항목과 결과')
        self.assertEqual(self.m.review_evidence(run,item),path)
        outside=self.repo/'outside.md';outside.write_text('outside')
        with self.assertRaises(ValueError): self.m.review_evidence(run,dict(item,evidence=str(outside)))

    def test_new_metadata_without_hashes_is_incomplete(self):
        out = self.legacy()
        self.m.write(out/'.pack/weakness-run.json', {'status': 'complete'})
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')

    def test_present_but_empty_metadata_is_not_legacy_completion(self):
        out = self.legacy()
        for value in [{}, [], None]:
            with self.subTest(value=value):
                self.m.write(out/'.pack/weakness-run.json', value)
                self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')

    def test_changed_markdown_invalidates_new_completed_record(self):
        out = self.legacy()
        files = list(out.glob('*.html')) + list((out/'.assets').glob('*.md'))
        import hashlib
        hashes = {p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        self.m.write(out/'.pack/weakness-run.json', {'status': 'complete','artifact_hashes':hashes})
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'complete')
        next((out/'.assets').glob('정리노트*.md')).write_text('modified')
        self.assertEqual(self.m.select(self.repo)['catalog'][0]['status'], 'incomplete')

    def test_versions_preserve_occupied_and_previous_paths(self):
        out = self.legacy()
        (out/'v2').mkdir()
        plan = self.m.select(self.repo, '0908', regenerate=True)['selected'][0]
        self.assertEqual(plan['output'], '약점노트/0908/v3')
        self.assertIn('_v3', plan['slug'])

    def test_prepare_freezes_inputs_and_normalizes_scratch_path(self):
        run = self.repo.parent/'scratch'
        p = self.m.prepare(self.repo, '0910', run)
        self.assertEqual(Path(p['run']), run.resolve())
        (self.repo/'SSTT/0910 공부.md').write_text('수정')
        with self.assertRaisesRegex(ValueError, '입력 변경'):
            self.m.load_plan(run)
        self.assertFalse((self.repo/'약점노트').exists())

    def test_invalid_or_outside_target_is_rejected(self):
        for target in ['1332', '../outside.md', 'SSTT/README.md']:
            with self.subTest(target=target), self.assertRaises(ValueError):
                self.m.select(self.repo, target)

    def test_prepare_will_not_reuse_run_or_implicitly_process_remaining(self):
        run = self.repo.parent/'scratch'
        self.m.prepare(self.repo, '0910', run)
        with self.assertRaises(ValueError): self.m.prepare(self.repo, '0922', run)
        with self.assertRaises(ValueError): self.m.prepare(self.repo, 'remaining', self.repo/'all')

    def test_added_same_day_record_invalidates_prepared_group(self):
        run = self.repo.parent/'scratch'
        self.m.prepare(self.repo, '0910', run)
        (self.repo/'SSTT/0910 공부 3.md').write_text('추가 기록')
        with self.assertRaisesRegex(ValueError, '입력 변경'):
            self.m.load_plan(run)

    def test_published_pass_flags_do_not_hide_changed_source(self):
        out = self.legacy()
        review = next(out.glob('복습문제_*.html'))
        report = next((out/'.assets').glob('*/validation.json'))
        (report.parent/'manifest.json').write_text(json.dumps({'source_sha256': 'old', 'input_hash': 'x'}))
        with self.assertRaisesRegex(ValueError, '입력|검토'):
            self.m.verify_explanation(self.repo, out, review.name)

    def test_real_assembler_makes_draft_and_preserves_solve_records(self):
        run = self.repo.parent/'assemble-run'
        plan = self.m.prepare(self.repo, '0910', run)
        fixture = Path(__file__).resolve().parents[2]/'bio-review-pack/tests/fixtures/mini-run/manifest.json'
        m = json.loads(fixture.read_text())
        m.update(range=plan['date'], slug=plan['slug'], forbidden_outside_preview=[], preview_topic='s1-next')
        m['sections'] = [
            dict(id='s0', title='세포', short='세포', topics=[dict(id='s0-cell', title='세포', required_terms=['세균'], layers=['eli5','formal','warn'], supp=False)]),
            dict(id='s1', title='요약', short='요약', topics=[dict(id='s1-next', title='다음 확인', required_terms=['재확인'], layers=[], supp=False), dict(id='s1-links', title='자료', required_terms=['복습문제'], layers=[], supp=False)])]
        m['parts'] = [dict(id='partC',title='맞춤 연습',short='연습')]
        m['problems'] = [dict(id='p1',part='partC',source='생성 변형 s0-cell',variant=True,anchor='s0-cell',level=1,date='0910',terms=['정답: (1)'],answer='(1)')]
        review_name = f'복습문제_0910_{plan["slug"]}.html'
        m['links'] = [dict(topic='s1-links', href=review_name)]
        self.m.write(run/'manifest.json',m)
        (run/'sections/s0.html').write_text('<article class="topic" id="s0-cell"><h3>세포</h3><div class="layer eli5">설명서가 있어요.</div><div class="layer formal">세균에는 DNA가 있어요.</div><div class="layer warn">핵과 DNA는 달라요.</div><div class="sum" hidden>세균에도 DNA가 있어요.</div></article>')
        (run/'sections/s1.html').write_text(f'<article class="topic" id="s1-next"><h3>재확인</h3></article><article class="topic" id="s1-links"><h3>자료</h3><a href="{review_name}">복습문제</a></article>')
        (run/'cards/p1.html').write_text('<article class="card" id="p1" data-source="생성 변형 s0-cell"><h3>P1. 세포</h3><div class="problem"><p>세균에 관한 옳은 설명은?</p><ul class="choices"><li data-choice="1">(1) DNA가 있다.</li><li data-choice="2">(2) DNA가 없다.</li></ul></div><details class="original"><summary>출처</summary>생성 문제</details><details class="hint"><summary>힌트</summary>유전물질</details><details class="solution"><summary>풀이</summary><ol class="steps"><li data-explains="1">(1) 맞아요. 세균에도 DNA가 있어요.</li><li data-explains="2">(2) 틀려요. 핵이 없어도 DNA가 있어요.</li></ol><p class="answer">정답: (1)</p></details></article>')
        ref = self.repo/'lecture.txt';ref.write_text('테스트용 근거')
        diagnosis = dict(schema=1, inputs=plan['inputs'], review_note_search='임시 저장소에는 기존 노트 없음', references=[dict(self.m.fingerprint(self.repo,ref),role='lecture',locations=['test'])], weaknesses=[dict(id='w1',status='self_corrected',evidence=[dict(path=plan['inputs'][0]['path'],line_start=1,line_end=2,quote='나중의 정정')],later_check='끝까지 확인',criterion='핵과 DNA 구별',topic='s0-cell',problems=['p1'])])
        source = self.repo/'복습노트/0910';source.mkdir(parents=True)
        for kind,body in [
            ('정리노트','<article class="topic" id="s0-original">핵과 DNA</article>'),
            ('복습문제','<article class="card" id="p77"><ul class="choices"><li data-choice="1">DNA</li></ul></article>'),
            ('문제설명','<article class="topic" id="p77"><div data-explanation="solve">설명</div></article>')]:
            (source/f'{kind}_0910_Source.html').write_text(body)
        inventory=self.m.study_inventory(self.repo,source)
        (run/'work/study-reading.md').write_text('임시 fixture의 세 자료 전체 항목을 확인한 기록')
        inventory.update(input_paths=[x['path'] for x in plan['inputs']],match_evidence='fixture의 0910 차시 연결',reading={role:dict(items=entry['items'],evidence='work/study-reading.md') for role,entry in inventory['files'].items()})
        diagnosis.update(schema=2,study_packs=[inventory],review_note_search='fixture의 복습노트/0910 HTML 3종')
        weakness=diagnosis['weaknesses'][0]
        weakness.update(status='study_corrected',correction=dict(origin='unknown',evidence=weakness['evidence']),source_context=dict(pack=inventory['folder'],match='confirmed',problem='p77',choices=['1'],note_topics=['s0-original'],explanation_sections=['solve']))
        self.m.write(run/'diagnosis.json', diagnosis)
        result = self.m.assemble(run)
        out = Path(result['output'])
        archived=self.m.read(out/'.pack/diagnosis.json')['study_packs'][0]['reading']
        self.assertTrue(all((out/row['archived_evidence']).is_file() for row in archived.values()))
        self.assertEqual(self.m.read(out/'.pack/weakness-run.json')['status'], 'draft')
        self.assertEqual(self.m.select(self.repo,'0910')['catalog'][1]['status'], 'incomplete')
        with self.assertRaisesRegex(ValueError, '미완료'): self.m.finish(run)
        before = Path(result['note']).read_bytes()
        (out/'.assets/풀이기록/record.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, '풀이기록'): self.m.assemble(run)
        self.assertEqual(Path(result['note']).read_bytes(), before)

    def test_export_adapter_routes_versioned_root_and_rejects_wrong_folder(self):
        source = (Path(__file__).resolve().parents[2]/'bio-review-pack/assets/review-interaction.js').read_text()
        adapted = self.m.adapt_export(source, '0910/v2', '복습문제_0910_Weakness_0910_v2.html')
        js = adapted + r'''
const api = module.exports;
const assert = require('node:assert/strict');
(async()=>{
 const seen=[];
 const leaf={name:'풀이기록'};
 const node=(name,next)=>({name,async getDirectoryHandle(key){seen.push(key);if(!(key in next)){const e=new Error();e.name='NotFoundError';throw e;}return next[key];}});
 const assets=node('.assets',{'풀이기록':leaf});
 const v2=node('v2',{'.assets':assets});v2.getFileHandle=async()=>({});
 const day=node('0910',{'v2':v2});
 const root=node('약점노트',{'0910':day});
 assert.equal(await api.resolveExportDir(root,'복습문제_0910_Weakness_0910_v2.html','0910'),leaf);
 assert.deepEqual(seen,['0910','v2','.assets','풀이기록']);
 const wrong={name:'other',async getFileHandle(){const e=new Error();e.name='NotFoundError';throw e;}};
 assert.equal(await api.resolveExportDir(wrong,'x','0910'),null);
 assert.equal(await api.resolveExportDir(v2,'복습문제_0910_Weakness_0910_v2.html','0910'),leaf);
})().catch(e=>{console.error(e);process.exit(1)});
'''
        result = subprocess.run(['node','--input-type=commonjs','-e',js],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__ == '__main__': unittest.main()
