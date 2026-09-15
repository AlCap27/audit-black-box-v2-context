"""Fixed-n bounded-cluster intervals proposed for the confirmatory protocol."""
import math

def mean_interval(intervals,lower,upper,alpha):
    if not intervals or not lower<upper or not 0<alpha<1:raise ValueError('Invalid specification')
    if any(not math.isfinite(x) or not math.isfinite(y) or not lower<=x<=y<=upper for x,y in intervals):raise ValueError('Invalid outcome interval')
    n=len(intervals);radius=(upper-lower)*math.sqrt(math.log(2/alpha)/(2*n))
    return max(lower,sum(x for x,y in intervals)/n-radius),min(upper,sum(y for x,y in intervals)/n+radius)

def conditional_difference(u1,v1,u0,v0,alpha):
    """Four means with union-bound coverage; numerator Y&Z, denominator Z.

    Inputs: assignment means per 16 vendors and 24 queries, or intervals for
    missing outcomes. Saturate at [0,1] if exposure lower bound is zero.
    """
    if len({len(v) for v in [u1,v1,u0,v0]})!=1:raise ValueError('Unequal cluster counts')
    def ratio(u,v):
        ul,uh=mean_interval(u,0,3/16,alpha/4)
        vl,vh=mean_interval(v,0,5/16,alpha/4)
        return (0 if vh<=0 else max(0,ul/vh),1 if vl<=0 else min(1,uh/vl))
    a,b=ratio(u1,v1),ratio(u0,v0)
    return max(-1,a[0]-b[1]),min(1,a[1]-b[0])
