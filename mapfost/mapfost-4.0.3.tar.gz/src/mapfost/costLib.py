import numpy as np
from . import mtfLib as mtfl


def cost_mapfost(x, fftS, test_aberrs, numAper, stig_scale,useBessel, kSpaceXY):

    total_aberrs = [np.multiply(np.add(t, x), [1, stig_scale, stig_scale]) for t in test_aberrs]
    mtfS = [mtfl.getMTF(kSpaceXY, *qq, numAper, useBessel)
            for inx, qq in enumerate(total_aberrs)]
    m1 = np.array(mtfS[0])
    m2 = np.array(mtfS[1])
    f1 = fftS[0]
    f2 = fftS[1]
    log_lklhood = np.sum(np.abs(f1*m1 + f2*m2)** 2/(m1**2 + m2**2 + 0.000001))
    return -1 * log_lklhood

