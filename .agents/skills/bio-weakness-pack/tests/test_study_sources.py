"""Behavioral checks for reading a lesson's three study documents."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/weakness_pack.py'


class StudySourceTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('study_wp', SCRIPT)
        self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name).resolve();self.repo=root/'repo';self.repo.mkdir()
        self.run=root/'run';self.run.mkdir();(self.run/'reading.md').write_text('세 자료의 전체 항목과 그림을 확인한 결과')
        (self.repo/'SSTT').mkdir();(self.repo/'SSTT/0910 공부.md').write_text('0910 자료를 공부한다\n해설을 읽고 고쳤다\n')
        self.folder=self.repo/'복습노트/0910';self.folder.mkdir(parents=True)
        self.note=self.folder/'정리노트_0910_Test.html'
        self.note.write_text('<article class="topic" id="s0-cell"><h3>세포</h3><p>핵과 DNA</p></article><article class="topic" id="s1-next">요약</article>')
        self.review=self.folder/'복습문제_0910_Test.html'
        self.review.write_text('<article class="card" id="p1"><div class="problem"><ul class="choices"><li data-choice="1">DNA</li><li data-choice="2">핵</li></ul></div><details class="hint" hidden>힌트</details><details class="solution">풀이</details></article>')
        self.explain=self.folder/'문제설명_0910_Test.html'
        self.explain.write_text('<article class="topic" id="p1"><div data-explanation="recall">기준</div><div data-explanation="solve">판정</div></article>')
        self.plan=dict(repo=str(self.repo),inputs=[self.m.fingerprint(self.repo,self.repo/'SSTT/0910 공부.md')])
        self.manifest=dict(sections=[dict(topics=[dict(id='s0-new')])],problems=[dict(id='p1',anchor='s0-new')])

    def diagnosis(self):
        inventory=self.m.study_inventory(self.repo,self.folder)
        inventory.update(input_paths=[self.plan['inputs'][0]['path']],match_evidence='발언 첫 줄의 0910 자료와 세포 문제 표현 대조',reading={role:dict(items=entry['items'],evidence='reading.md') for role,entry in inventory['files'].items()})
        context=dict(pack=inventory['folder'],match='confirmed',problem='p1',choices=['1'],note_topics=['s0-cell'],explanation_sections=['recall','solve'])
        return dict(schema=2,study_packs=[inventory],weaknesses=[dict(id='w1',status='study_corrected',source_context=context,correction=dict(origin='solution',evidence=[dict(path='SSTT/0910 공부.md',line_start=2,line_end=2,quote='해설을 읽고 고쳤다')]))])

    def test_inventory_includes_all_units_choices_and_explanation_sections(self):
        inv=self.m.study_inventory(self.repo,self.folder)
        self.assertEqual(inv['files']['note']['items'],['s0-cell','s1-next'])
        self.assertEqual(inv['files']['review']['choices']['p1'],['1','2'])
        self.assertEqual(inv['files']['explanation']['sections']['p1'],['recall','solve'])
        self.assertEqual(inv['missing'],[])

    def test_ambiguous_lesson_files_require_explicit_selection(self):
        other=self.folder/'정리노트_0910_Another.html';other.write_bytes(self.note.read_bytes())
        with self.assertRaisesRegex(ValueError,'여러 후보'):self.m.study_inventory(self.repo,self.folder)
        inv=self.m.study_inventory(self.repo,self.folder,{'note':self.note})
        self.assertEqual(inv['files']['note']['path'],self.note.relative_to(self.repo).as_posix())

    def test_hash_inventory_without_full_reading_record_is_rejected(self):
        data=self.diagnosis();data['study_packs'][0]['reading']['note']['items']=['s0-cell']
        with self.assertRaisesRegex(ValueError,'전체 읽기'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)
        data=self.diagnosis();del data['study_packs'][0]['reading']
        with self.assertRaisesRegex(ValueError,'전체 읽기'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_all_three_documents_and_original_problem_link_are_accepted(self):
        self.m.validate_study_sources(self.plan,self.run,self.diagnosis(),self.manifest)

    def test_changed_study_html_invalidates_record(self):
        data=self.diagnosis();self.review.write_text(self.review.read_text()+'<p>추가</p>')
        with self.assertRaisesRegex(ValueError,'변경'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_missing_explanation_is_reported_and_confirmed_link_is_blocked(self):
        self.explain.unlink();data=self.diagnosis()
        self.assertEqual(data['study_packs'][0]['missing'],['explanation'])
        with self.assertRaisesRegex(ValueError,'문항|문제설명'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)
        data['weaknesses'][0]['source_context']=dict(pack=data['study_packs'][0]['folder'],match='concept',note_topics=['s0-cell'],reason='해설 파일 누락으로 원문 문제 판정은 보류, 개념만 보완')
        self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_original_and_generated_problem_ids_are_separate(self):
        data=self.diagnosis();data['weaknesses'][0]['source_context']['problem']='p99'
        with self.assertRaisesRegex(ValueError,'문항'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_invalid_topic_choice_or_section_is_rejected(self):
        for key,value in [('note_topics',['s9-nope']),('choices',['9']),('explanation_sections',['nonexistent'])]:
            data=self.diagnosis();data['weaknesses'][0]['source_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_solution_or_unknown_correction_is_not_independent_self_correction(self):
        data=self.diagnosis();data['weaknesses'][0]['status']='self_corrected'
        with self.assertRaisesRegex(ValueError,'자기교정'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)
        data['weaknesses'][0]['correction']['origin']='unknown'
        with self.assertRaisesRegex(ValueError,'자기교정'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)
        data['weaknesses'][0]['status']='study_corrected';self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_mismatched_problem_sets_are_listed_without_guessing(self):
        self.explain.write_text(self.explain.read_text().replace('id="p1"','id="p2"'))
        data=self.diagnosis();self.assertEqual(data['study_packs'][0]['review_only'],['p1'])
        with self.assertRaisesRegex(ValueError,'문항'):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_confirmed_link_requires_explicit_topic_choice_and_explanation_fields(self):
        for key in ['choices','note_topics','explanation_sections']:
            data=self.diagnosis();del data['weaknesses'][0]['source_context'][key]
            with self.subTest(key=key),self.assertRaises(ValueError):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)
        data=self.diagnosis();data['weaknesses'][0]['source_context']['explanation_sections']=[]
        with self.assertRaises(ValueError):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_correction_cannot_come_from_unresolved_or_other_lesson_input(self):
        other=self.repo/'SSTT/0910 공부 2.md';other.write_text('다른 차시의 정정')
        self.plan['inputs'].append(self.m.fingerprint(self.repo,other))
        data=self.diagnosis();data['unresolved_sessions']=[dict(path='SSTT/0910 공부 2.md',reason='차시 미확정')]
        data['weaknesses'][0]['correction']['evidence']=[dict(path='SSTT/0910 공부 2.md',line_start=1,line_end=1,quote='다른 차시의 정정')]
        with self.assertRaises(ValueError):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)

    def test_source_context_cannot_use_unselected_sstt(self):
        data=self.diagnosis();data['study_packs'][0]['input_paths']=['SSTT/0922 공부.md']
        with self.assertRaises(ValueError):self.m.validate_study_sources(self.plan,self.run,data,self.manifest)


if __name__=='__main__':unittest.main()
