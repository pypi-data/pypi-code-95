import numpy as np
from scipy.stats import norm

def bpower(p1,p2,n1,n2,n=None,alpha=0.05)
    """
    a python version of the r command "bpower" from Hmsc https://github.com/harrelfe/Hmisc/blob/master/R/bpower.s
    
    """
    if n!=None:
        n1=n/2
        n2=n/2
    
    z=norm.ppf(1-alpha/2)
    q1=1-p1
    q2=1-p2
    pm = (n1*p1+n2*p2)/(n1+n2)
    ds = z*np.sqrt((1/n1 + 1/n2)*pm*(1-pm))
    ex = abs(p1-p2)
    sd= np.sqrt(p1*q1/n1+p2*q2/n2)

    power=1-norm.cdf((ds-ex)/sd) +norm.cdf((-ds-ex)/sd)
    
    return power