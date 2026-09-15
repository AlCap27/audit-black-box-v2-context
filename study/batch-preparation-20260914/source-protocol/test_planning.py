import unittest,math
import numpy as np
from scipy.stats import binom
from power_analysis import tpower,required_n,guaranteed_n
from bounded_inference import mean_interval,conditional_difference

class PlanningTests(unittest.TestCase):
    def test_t_null_and_tail(self):
        for n in [4,40,318]:self.assertAlmostEqual(tpower(n,0,.03,.025),.025,places=7)
        self.assertTrue(.999<tpower(40,.05,.028356543640780024,.025)<=1)
    def test_required_n_minimal(self):
        n=required_n(.05,.06,.025,.8)
        self.assertGreaterEqual(tpower(n,.05,.06,.025),.8)
        self.assertLess(tpower(n-1,.05,.06,.025),.8)
    def test_bound_power_algebra(self):
        for d in [.02,.05,.1]:
            n=guaranteed_n(d,.025,.8)
            r=.375*math.sqrt(math.log(2/.025)/(2*n))
            self.assertGreater(d,r)
            self.assertLessEqual(math.exp(-2*n*(d-r)**2/.375**2),.2)
    def test_exact_binomial_coverage(self):
        for n in [20,40,100]:
            for p in [.01,.2,.5,.9]:
                rejection=0
                for k in range(n+1):
                    lo,hi=mean_interval([(1,1)]*k+[(0,0)]*(n-k),0,1,.025)
                    if not lo<=p<=hi:rejection+=binom.pmf(k,n,p)
                self.assertLessEqual(rejection,.025+1e-12)
    def test_missing_and_no_overlap(self):
        observed=mean_interval([(0,0)]*40,-3/16,3/16,.025)
        missing=mean_interval([(-3/16,3/16)]*40,-3/16,3/16,.025)
        self.assertLessEqual(missing[0],observed[0]);self.assertGreaterEqual(missing[1],observed[1])
        self.assertEqual(conditional_difference([(0,0)]*40,[(0,0)]*40,[(0,0)]*40,[(0,0)]*40,.003125),(-1,1))
    def test_invalid(self):
        with self.assertRaises(ValueError):mean_interval([(2,2)],0,1,.05)
        with self.assertRaises(ValueError):mean_interval([],0,1,.05)

if __name__=='__main__':unittest.main()
