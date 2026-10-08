"""Checks for measurement errors; fabricated fixtures never enter website artifacts."""
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import bench, report

class AnalysisTests(unittest.TestCase):
    def build_fixture(self, root, no_test_success, with_test_success):
        manifest={'tasks':[{'instance_id':f'task-{i}','repo':'sympy/sympy','base_commit':'base','version':'1.12','problem_statement':'fixture','FAIL_TO_PASS':'[]','PASS_TO_PASS':'[]','fail_nodes':[],'pass_nodes':[],'mutants':[]} for i in range(20)]}
        (root/'manifest.json').write_text(json.dumps(manifest))
        for task in range(20):
            for condition,success in [('no-new-tests',no_test_success),('write-tests',with_test_success)]:
                for repetition in [1,2]:
                    rid=f'task-{task}--{condition}--{repetition}'
                    target=root/'runs'/rid;target.mkdir(parents=True)
                    (target/'result.json').write_text(json.dumps(dict(run_id=rid,instance_id=f'task-{task}',condition=condition,repetition=repetition,status='completed',elapsed_seconds=30,usage={'input_tokens':100,'cached_input_tokens':50,'output_tokens':10},acceptance={'all_pass':success})))

    def test_effect_clusters_tasks_and_keeps_cached_tokens_separate(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.build_fixture(root,False,True)
            with patch.object(report,'OUT',root/'public'),patch.object(report,'chart'),patch('builtins.print'):
                d=report.build(root)
            self.assertEqual(d['paired_difference_pp'],100)
            self.assertEqual(d['confidence_interval_pp'],[100,100])
            self.assertEqual(d['sign_flip_p'],2/(2**20))
            self.assertEqual(d['arms']['write-tests']['input_tokens'],4000)
            self.assertEqual(d['arms']['write-tests']['cached_input_tokens'],2000)
            self.assertLessEqual(len((root/'public/tweet.txt').read_text().strip()),280)

    def test_no_difference_is_not_equivalence_and_incomplete_gets_no_inference(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.build_fixture(root,True,True)
            with patch.object(report,'OUT',root/'public'),patch.object(report,'chart'),patch('builtins.print'):
                d=report.build(root)
                self.assertEqual(d['paired_difference_pp'],0)
                self.assertEqual(d['sign_flip_p'],1)
                self.assertTrue(d['bootstrap_degenerate'])
                self.assertIn('degenerate',d['statistical_note'])
                self.assertIn('no equivalence claim',d['statistical_note'])
                one=next((root/'runs').glob('*/result.json'))
                r=json.loads(one.read_text());r.pop('acceptance');r['status']='infrastructure-error';one.write_text(json.dumps(r))
                d=report.build(root)
            self.assertEqual(d['evaluated'],79)
            self.assertIsNone(d['paired_difference_pp'])
            self.assertIsNone(d['confidence_interval_pp'])
            self.assertEqual(d['status'],'incomplete')

    def test_timeout_patch_scored_but_never_called_completed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.build_fixture(root,False,True)
            one=root/'runs/task-0--write-tests--1/result.json';r=json.loads(one.read_text());r['status']='timeout';r['elapsed_seconds']=300;r['usage']={};one.write_text(json.dumps(r))
            with patch.object(report,'OUT',root/'public'),patch.object(report,'chart'),patch('builtins.print'):d=report.build(root)
            arm=d['arms']['write-tests']
            self.assertEqual(arm['solved'],40);self.assertEqual(arm['completed'],39)
            self.assertEqual(arm['timeouts'],1);self.assertEqual(arm['total_seconds'],1470)

if __name__=='__main__':unittest.main()
