import unittest
from _util import ROOT
from lib.revoice import plan_revoice

class RevoiceTest(unittest.TestCase):
    def test_extreme_zero_and_hash(self):
        old={'fps':30,'windows':[{'id':'a-1','scene_id':'a','first_frame':0,'last_frame':30}]}
        for finish in (0,90):
            new={'fps':30,'windows':[{'id':'a-1','scene_id':'a','first_frame':0,'last_frame':finish}]}
            self.assertEqual(plan_revoice(old,new,'hash',{'a'})[0]['mode'],'rerender')
        a=plan_revoice(old,old,'a',{'a'}); b=plan_revoice(old,old,'b',{'a'})
        self.assertNotEqual(a[0]['key'],b[0]['key'])
    def test_mismatch_and_overlap(self):
        old={'fps':30,'windows':[{'id':'a','scene_id':'a','first_frame':0,'last_frame':30}]}
        with self.assertRaises(ValueError): plan_revoice(old,{'fps':30,'windows':[]},'a',{'a'})
