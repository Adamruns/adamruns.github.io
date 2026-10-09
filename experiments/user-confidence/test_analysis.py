import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import report


class MeasurementTests(unittest.TestCase):
    def runs(self, treatment, control):
        return [dict(instance_id=f'issue-{i}',repetition=rep,condition=arm,solved=values[i],evaluated=True)
                for arm,values in [('confident-wrong',treatment),('tentative-wrong',control)]
                for i in range(20) for rep in (1,2)]

    def test_effect_and_cluster_randomization(self):
        # Two repeated attempts per issue do not become independent samples.
        rows=self.runs([True]*2+[False]*18,[False]*20)
        result=report.contrast(rows,'confident-wrong','tentative-wrong')
        self.assertEqual(result['difference_pp'],10)
        self.assertEqual(result['exact_task_sign_flip_p'],0.5)
        self.assertEqual(result['treatment_only_pass'],4)
        self.assertEqual(result['same_outcome'],36)
        self.assertFalse(result['bootstrap_degenerate'])

    def test_identical_effects_flag_degenerate_interval(self):
        result=report.contrast(self.runs([True]*20,[True]*20),'confident-wrong','tentative-wrong')
        self.assertTrue(result['bootstrap_degenerate'])
        self.assertEqual(result['cluster_bootstrap_95_pp'],[0,0])
        self.assertEqual(result['exact_task_sign_flip_p'],1)

    def test_partial_schedule_does_not_get_final_contrast(self):
        rows=self.runs([True]*20,[False]*20)
        self.assertIsNone(report.contrast(rows[:-1],'confident-wrong','tentative-wrong'))

    def test_timeout_can_leave_correct_patch_and_cached_tokens_are_subset(self):
        manifest={'schedule':[{}]*160,'tasks':[{}]*20,'protocol':{'model':'test','reasoning_effort':'medium'}}
        row=dict(instance_id='a',condition='no-diagnosis',repetition=1,status='timeout',elapsed_seconds=300,
                 acceptance={'all_pass':True},usage={'input_tokens':1000,'cached_input_tokens':700,'output_tokens':20})
        result=report.analyze(manifest,[row]);arm=result['arms']['no-diagnosis']
        self.assertEqual(arm['solved'],1)
        self.assertEqual(arm['timeouts'],1)
        self.assertEqual(arm['mean_seconds'],300)
        self.assertEqual(arm['input_tokens'],1000)
        self.assertEqual(result['status'],'incomplete')
        self.assertEqual(result['contrasts'],{})


if __name__=='__main__':unittest.main()
