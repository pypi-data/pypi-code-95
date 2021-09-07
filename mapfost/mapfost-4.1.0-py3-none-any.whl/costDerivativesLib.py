import numpy as np

def firstDerivAx(edge_len,z,ax):

    wngrd = np.array(
        np.meshgrid(range(int(-edge_len / 2), int(edge_len / 2)),
                    range(int(-edge_len / 2), int(edge_len / 2)))[::-1],
        dtype=np.float)

    wtd =  np.add(
            np.multiply(
                np.multiply(
                    wngrd[0], wngrd[0]),
                2 * ax + 2 * z),
            np.multiply(
                np.multiply(
                    wngrd[1], wngrd[1]),
                2 * ax - 2 * z))

    return wtd


def firstDerivAy(edge_len, z, ay):

    wngrd = np.array(
        np.meshgrid(range(int(-edge_len / 2), int(edge_len / 2)),
                    range(int(-edge_len / 2), int(edge_len / 2)))[::-1],
        dtype=np.float)

    wtd = np.add(
        np.add(
            np.multiply(
                np.multiply(
                    wngrd[0], wngrd[0]),
                2 * ay),
            np.multiply(
                np.multiply(
                    wngrd[1], wngrd[1]),
                2 * ay)),
        np.multiply(
            np.multiply(
                wngrd[0], wngrd[1]), -4 * z))

    return wtd


def firstDerivZ(edge_len, z, ax, ay):

    wngrd =np.array(
        np.meshgrid(range(int(-edge_len / 2), int(edge_len / 2)),
                    range(int(-edge_len / 2), int(edge_len / 2)))[::-1],
        dtype=np.float)

    wtd = np.add(
        np.add(
            np.multiply(
                np.multiply(
                    wngrd[0], wngrd[0]),
                    2 * ax + 2 * z),
            np.multiply(
                np.multiply(
                    wngrd[1], wngrd[1]),
                     -2 * ax + 2 * z)),
        np.multiply(
            np.multiply(
                wngrd[0], wngrd[1]), -4 * ay))

    return wtd


def secondDerivAxOrAyOrZ(w,pxsz):

    wngrd = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    wnc = 2*np.pi/int(w*pxsz)
    nn = 2*((wngrd[0] * wnc)**2 + (wngrd[1] * wnc)**2)
    return nn

def secondDerivAxZ(w,pxsz):

    wngrd = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    wnc = 2*np.pi/int(w*pxsz)
    nn = 2*((wngrd[0] * wnc)**2 - (wngrd[1] * wnc)**2)
    return nn


def secondDerivAyZ(w,pxsz):

    wngrd = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    wnc = 2*np.pi/int(w*pxsz)
    pp = -4*wngrd[0]*wngrd[1]*wnc**2
    return pp


def secondDerivAyAx(w,pxsz):

    wngrd = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    pp = wngrd[0]*wngrd[1]*0

    return pp


def getd1MTF(mtf, z, ax, ay, num_aperture, pxsz):

    edge_len = mtf.shape[0]
    wnCoeff = 2 * np.pi / (int(edge_len) * pxsz)
    mtfFirstDiv = [firstDerivZ(edge_len,z,ax,ay), firstDerivAx(edge_len,z,ax),  firstDerivAy(edge_len,z,ay)]
    d1mtf = [np.multiply(mtf,-(1/8)*wnCoeff*num_aperture**2*imtf) for imtf in mtfFirstDiv]

    return d1mtf


def getd2MTF(mtf, z, ax, ay, num_aperture, pxsz):
    edge_len = mtf.shape[1]
    mtfFirstDiv = getd1MTF(mtf, z, ax, ay, num_aperture, pxsz)
    mtfSecondDiv = [secondDerivAxOrAyOrZ(edge_len, pxsz), secondDerivAxZ(edge_len,pxsz),secondDerivAyZ(edge_len,pxsz),
                    secondDerivAxZ(edge_len,pxsz), secondDerivAxOrAyOrZ(edge_len, pxsz), secondDerivAyAx(edge_len,pxsz),
                    secondDerivAyZ(edge_len,pxsz),secondDerivAyAx(edge_len,pxsz),  secondDerivAxOrAyOrZ(edge_len, pxsz)]

    iv, jv = np.indices((3,3))

    iv = iv.reshape(-1)
    jv = jv.reshape(-1)

    res = [None]*9
    for inx in range(0,9):

        A = (-1/8)*num_aperture**2

        i = iv[inx]
        j = jv[inx]
        ij = 3*i +j
        fin1 = A**2*np.multiply(mtf, np.multiply(mtfFirstDiv[i], mtfFirstDiv[j]))
        fin2 = A*np.multiply(mtf, mtfSecondDiv[ij])

        fin = np.add(fin1,fin2)

        res[inx] = fin

    return res


def getMTF(edge_len, z, ax, ay, num_aperture, pxsz):

    wnc = 2 * np.pi/ (int(edge_len)*pxsz)
    wngrd = wnc * np.array(
                        np.meshgrid(range(int(-edge_len / 2), int(edge_len / 2)),
                                    range(int(-edge_len / 2), int(edge_len / 2)))[::-1],
                        dtype = np.float)

    wtd = np.add(
            np.add(
                np.multiply(
                        np.multiply(
                                wngrd[0], wngrd[0]),
                                z ** 2 + ax ** 2 +  ay ** 2 + 2 * ax * z),
                np.multiply(
                        np.multiply(
                                wngrd[1], wngrd[1]),
                                z ** 2 + ax ** 2 +  ay ** 2 - 2 * ax * z)),
                np.multiply(
                    np.multiply(
                        wngrd[0], wngrd[1]), -4 * ay * z))

    mtf = np.exp(np.multiply((-1 / 8) * (num_aperture ** 2), wtd))

    return mtf


def get_jacobian_vec(test_ims, total_aberrs, num_aperture, pix_size_um, fadeFac, mtfSqS=None, d1mtfSqS = None):

    edge_len = np.array(test_ims).shape[1]
    if mtfSqS is None:
        mtf1 = getMTF(edge_len, *total_aberrs[0], num_aperture, pix_size_um) * fadeFac[0]
        mtf2 = getMTF(edge_len, *total_aberrs[1], num_aperture, pix_size_um) * fadeFac[1]

    if d1mtfSqS is None:
        d1mtf1 = getd1MTF(mtf1, *total_aberrs[0], num_aperture, pix_size_um)
        d1mtf2 = getd1MTF(mtf2, *total_aberrs[1], num_aperture, pix_size_um)

    jacobian_vec = [None] * 3
    x1, x2 = test_ims
    for i in range(0, 3):

        aa = np.subtract(np.multiply(x1, mtf2**2), np.multiply(x2, mtf1**2))

        bb = np.subtract(np.multiply(x1, np.multiply(mtf2,d1mtf2[i])),
                         np.multiply(x2, np.multiply(mtf1,d1mtf1[i])))
        cc = np.add(mtf1**4, mtf2**4)
        dd = np.add(np.multiply(mtf1**3, d1mtf1[i]), np.multiply(mtf2**3, d1mtf2[i]))

        add1 = 4*np.divide(np.multiply(aa, bb), cc)
        add2 = -4*np.divide(np.multiply(aa**2, dd), cc**2)
        fin = np.add(add1,add2)
        jacobian_vec[i] = fin

    jacobian_vec = np.array(jacobian_vec).T.reshape(edge_len * edge_len, 3)

    return np.nansum(jacobian_vec, axis=0)

def get_hessian_matrix(test_ims, total_aberrs, num_aperture, pix_size_um):

    edge_len = np.array(test_ims).shape[1]
    mtf1= getMTF(edge_len, *total_aberrs[0], num_aperture, pix_size_um)
    mtf2 = getMTF(edge_len, *total_aberrs[1], num_aperture, pix_size_um)

    d1mtf1 = getd1MTF(mtf1, *total_aberrs[0], num_aperture, pix_size_um)
    d1mtf2 = getd1MTF(mtf1, *total_aberrs[1], num_aperture, pix_size_um)

    d2mtf1 = getd2MTF(mtf1, *total_aberrs[0], num_aperture, pix_size_um)
    d2mtf2 = getd2MTF(mtf1, *total_aberrs[1], num_aperture, pix_size_um)

    hessian_field = [[None]] * 9
    iv, jv = np.indices((3, 3))

    iv = iv.reshape(-1)
    jv = jv.reshape(-1)

    x1 = np.real(test_ims[0])
    y1 = np.imag(test_ims[0])

    x2 = np.real(test_ims[1])
    y2 = np.imag(test_ims[1])

    for inx in range(0, 9):

        i = iv[inx]
        j = jv[inx]

        ij = i * 3 + j
        aa = x1 * d1mtf2[j] - x2 * d1mtf1[j]
        bb = x1 * d1mtf2[i] - x2 * d1mtf1[i]
        cc = y1 * d1mtf2[j] - y2 * d1mtf1[j]
        dd = y1 * d1mtf2[i] - y2 * d1mtf1[i]

        oo = x1 * mtf2 - x2 * mtf1
        nn = x1 * d2mtf2[ij] - x2 * d2mtf1[ij]

        ll = y1 * mtf2 - y2 * mtf1
        mm = y1 * d2mtf2[ij] - y2 * d2mtf1[ij]

        ee = mtf1 * d1mtf1[i] + mtf2 * d1mtf2[i]
        kk = mtf1 * d1mtf1[j] + mtf2 * d1mtf2[j]
        ff = mtf1 * d2mtf1[ij] + mtf2 * d2mtf2[ij] + d1mtf1[i] * d1mtf1[j] + d1mtf2[i] * d1mtf2[j]
        gg = mtf1**2 + mtf2**2

        A = np.add(oo**2, ll**2)
        Aij = 2 *np.sum([np.multiply(aa,bb), np.multiply(cc,dd), np.multiply(oo,nn), np.multiply(ll,mm)], axis=0)
        Ai = 2 *np.sum([np.multiply(oo,bb), np.multiply(ll,dd)], axis=0)
        Aj = 2 *np.sum([np.multiply(oo,aa), np.multiply(ll,cc)], axis=0)

        Bi = 2 * ee
        Bj = 2 * kk
        Bij = 2 * ff

        B = gg
        fin1 = np.multiply(Aij, np.multiply(B, B))
        fin2 = -1 * np.multiply(Ai, np.multiply(Bj, B))
        fin3 = -1 * np.multiply(Aj, np.multiply(Bi, B))
        fin4 = 2 * np.multiply(A, np.multiply(Bi, Bj))
        fin5 = -1 * np.multiply(A, np.multiply(Bij, B))
        fin = np.divide(np.add(fin1, np.add(fin2, np.add(fin3, np.add(fin4, fin5)))), B ** 3)
        hessian_field[inx] = fin
    hessian = np.nansum(np.array(hessian_field).T.reshape(edge_len*edge_len, 3, 3), axis=0)

    return hessian

