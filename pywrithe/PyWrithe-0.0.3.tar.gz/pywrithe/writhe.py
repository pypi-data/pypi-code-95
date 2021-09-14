import numpy as np
import math as ma

def _normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0.0:
       return v
    return v / norm

def writhe(curve):
    '''
    Returns writhe of given closed parametric curve.

    Parameters
    ----------
    curve: np.array
        An ``N`` by 3 array describing locations of endpoints of ``N`` linear segments approximating the curve. All locations should be distinct.

    Returns
    -------
    float
        Value of writhe for closed curve comprised of linear segments given.

    Example
    -------
    >>> import numpy as np
    >>> curve = np.array([[-1,0,-1],[1,0,1],[0,-1,1],[0,1,1]])
    >>> pywrithe.writhe(curve)
    0.366

    '''
    segments = np.transpose(np.array([np.roll(curve,1,axis=0),curve]),(1,0,2)) # (segment,begin/end,coordinate) order
    n = len(segments)
    omegas = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            if i-j == 0 or i-j == 1 or i-j == -1 or i-j == n-1 or i-j == -n+1:
                omegas[i][j] = 0
            else:
                segment_a = segments[i]
                segment_b = segments[j]
                r13 = segment_a[0] - segment_b[0]
                r14 = segment_a[0] - segment_b[1]
                r23 = segment_a[1] - segment_b[0]
                r24 = segment_a[1] - segment_b[1]

                r34 = segment_b[0] - segment_b[1]
                r12 = segment_a[0] - segment_a[1]

                n1 = _normalize(np.cross(r13,r14))
                n2 = _normalize(np.cross(r14,r24))
                n3 = _normalize(np.cross(r24,r23))
                n4 = _normalize(np.cross(r23,r13))

                d1 = np.clip(np.dot(n1,n2),-1,1)
                d2 = np.clip(np.dot(n2,n3),-1,1)
                d3 = np.clip(np.dot(n3,n4),-1,1)
                d4 = np.clip(np.dot(n4,n1),-1,1)

                a1 = ma.asin(d1)
                a2 = ma.asin(d2)
                a3 = ma.asin(d3)
                a4 = ma.asin(d4)

                omega_star = (a1+a2+a3+a4)

                omega = omega_star * ma.copysign(1.0, np.dot( np.cross( r34, r12) , r13) )

                omegas[i][j] = omega

    #print(omegas)

    return (1.0 / (4.0 * ma.pi)) * np.sum(omegas)



