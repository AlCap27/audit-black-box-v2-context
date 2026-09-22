import math
import unittest
from analyze import counts, point, inference


class AnalysisTests(unittest.TestCase):
    def test_counts_include_absent_vendors_and_unsupported_known_recommendation(self):
        rows=[{'assignment_id':'a','Y':['v0'],'Z':['v1'],'X':['v1']}]
        c=counts(rows,{'a':{'v0':'000','v1':'111'}},['v0','v1'])
        self.assertEqual(c['L'],[[1,0,0,0,1],[0,1,0,1,1]])

    def test_conditional_is_ratio_of_totals_not_average_ratios(self):
        # Level 1 has successes/exposures 1/1 and 0/9, hence 1/10, not 1/2.
        c=[[0,10,0,10,32],[1,10,1,10,32]]
        self.assertAlmostEqual(point(c)['C'],.1)
        self.assertIsNone(point([[0,0,0,0,16],[1,1,1,1,16]])['C'])

    def test_frozen_alpha_support_and_n(self):
        clusters=[{f:[[0,24,0,24,384],[24,48,24,48,384]] for f in 'SLT'} for _ in range(367)]
        r=inference(clusters)
        primary=next(x for x in r if (x['factor'],x['outcome'])==('L','Y'))
        radius=(3/8)*math.sqrt(math.log(2/.025)/(2*367))
        self.assertAlmostEqual(primary['estimate'],1/16)
        self.assertAlmostEqual(primary['interval'][0],1/16-radius)
        self.assertEqual(sum(x['alpha'] for x in r),.05)
        self.assertEqual(len(r),9)
        self.assertTrue(primary['reject_zero'])

    def test_no_retrieval_gives_unidentified_conditional(self):
        clusters=[{f:[[0,0,0,0,384],[0,0,0,0,384]] for f in 'SLT'} for _ in range(367)]
        r=inference(clusters)
        for test in r:
            self.assertFalse(test['reject_zero'])
            if test['outcome']=='C':
                self.assertIsNone(test['estimate']);self.assertEqual(test['interval'],(-1,1))


if __name__=='__main__': unittest.main()
