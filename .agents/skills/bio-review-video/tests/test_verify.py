import tempfile,unittest
from pathlib import Path
from _util import minimal_manifest
from lib.verify import verify_run,publish_latest

class VerifyTest(unittest.TestCase):
    def test_wrapper_pass_cannot_replace_source_check(self):
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)/'0915'/'run-1'; run.mkdir(parents=True)
            reports={k:{'status':'passed','evidence':[],'errors':[]} for k in ('content','audio','visual','media','sync')}
            reports['source']={'status':'unverified','evidence':['wrapper passed'],'errors':[]}
            result=verify_run(run,minimal_manifest(),reports)
            self.assertFalse(result['complete'])
            with self.assertRaises(ValueError): publish_latest(run,result)
            self.assertFalse((run.parent/'latest.json').exists())
    def test_failed_run_preserves_latest(self):
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)/'r'; run.mkdir(); latest=run.parent/'latest.json'
            latest.write_text('previous')
            with self.assertRaises(ValueError): publish_latest(run,{'complete':False})
            self.assertEqual(latest.read_text(),'previous')
    def test_forged_complete_cannot_publish(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): publish_latest(Path(d),{'complete':True})
