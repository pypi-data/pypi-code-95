import numpy as np
import math


def rotate_frame(mesh, alpha):

    # pdb.set_trace()
    meshRotated = [0,0]
    meshRotated[0] = np.add(mesh[0]*math.cos(math.radians(alpha)), mesh[1]*math.sin(-1*math.radians(alpha)))
    meshRotated[1] = np.add(mesh[0]*math.sin(math.radians(alpha)), mesh[1]*math.cos(math.radians(alpha)))

    mesh = [meshRotated[0], meshRotated[1]]
    return mesh


def firstDerivAx(w,z,ax,ps, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    na = 2*math.pi/int(w*4)


    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2*z) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), -2*z))
    kk = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2*ax) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), 2*ax))


    qq = np.add(nn,kk)


    return qq


def firstDerivAy(w, z, ay, ps, rot):
    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    na = 2 * math.pi / int(w*4)

    pp = np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[1]), -4*z*((na/ps)**2))

    kk = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), 2 * ay),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), 2 * ay))

    qq = np.add(pp, kk)

    return qq


def firstDerivZ(w, z, ax, ay, ps,rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    na = 2 * math.pi / int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), z*2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), z*2))

    mm = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2*ax) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), -2*ax))

    pp = np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[1]), -4*ay*((na/ps)**2))

    qq = np.add(nn, mm)
    qq = np.add(qq,pp)

    return qq


def secondDerivAxOrAyOrZ(w,ps, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)

    na = 2*math.pi/int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), 2))


    return nn

def secondDerivAxZ(w,ps, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)

    na = 2*math.pi/int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), -2))


    return nn



def secondDerivAyZ(w,ps, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])
    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)

    na = 2*math.pi/int(w*4)

    pp = np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[1]), -4*(na/ps)**2)

    return pp


def secondDerivAyAx(w,ps, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])

    pp = np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[1]), 0)

    return pp




def getFirstDerivGaussianMTF(w,z,ax,ay, na, ps, scale, rot):


    mtf_meshgrid = np.meshgrid(range(int(-w/2), int(w/2)), range(int(-w/2), int(w/2))[::-1])

    Ax = ax*scale[0]
    Ay = ay*scale[1]

    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    ona = na
    na = 2*math.pi/int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), z**2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), z**2))
    kk = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), Ax**2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), Ax**2))
    mm = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), 2*Ax*z) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), -2*Ax*z))
    oo = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[0]),(na/ps)**2), Ay**2) ,
               np.multiply(np.multiply(np.multiply(mtf_meshgrid[1],mtf_meshgrid[1]),(na/ps)**2), Ay**2))
    pp = np.multiply(np.multiply(mtf_meshgrid[0],mtf_meshgrid[1]), -4*Ay*z*((na/ps)**2))

    qq = np.add(nn, kk)
    qq = np.add(qq, mm)
    qq = np.add(qq, oo)
    qq = np.add(qq, pp)

    mtf = np.exp(np.multiply((-1 / 8) * (ona ** 2), qq))

    mtfFirstDiv = [firstDerivZ(w,z,Ax,Ay,ps,rot), firstDerivAx(w,z,Ax,ps,rot),  firstDerivAy(w,z,Ay,ps,rot)]

    res = [np.multiply(mtf,-(1/8)*ona**2*i) for i in mtfFirstDiv]

    return res


def getSecondDerivGaussianMTF(w, z, ax, ay, na, ps, scale, rot):
    mtf_meshgrid = np.meshgrid(range(int(-w / 2), int(w / 2)), range(int(-w / 2), int(w / 2))[::-1])

    Ax = ax * scale[0]
    Ay = ay * scale[1]

    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    ona = na
    na = 2 * math.pi / int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), z ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), z ** 2))
    kk = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), Ax ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), Ax ** 2))
    mm = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), 2 * Ax * z),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), -2 * Ax * z))
    oo = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), Ay ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), Ay ** 2))
    pp = np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[1]), -4 * Ay * z * ((na / ps) ** 2))

    qq = np.add(nn, kk)
    qq = np.add(qq, mm)
    qq = np.add(qq, oo)
    qq = np.add(qq, pp)

    mtf = np.exp(np.multiply((-1 / 8) * (ona ** 2), qq))

    # mtfFirstDiv = [firstDerivZ(w,z,Ax,Ay,ps,rot), firstDerivZ(w,z,Ax,Ay,ps,rot),firstDerivZ(w,z,Ax,Ay,ps,rot),
    #                firstDerivAx(w,z,Ax,ps,rot),firstDerivAx(w,z,Ax,ps,rot),firstDerivAx(w,z,Ax,ps,rot),
    #                firstDerivAy(w,z,Ay,ps,rot),firstDerivAy(w,z,Ay,ps,rot), firstDerivAy(w,z,Ay,ps,rot)]

    mtfFirstDiv = getFirstDerivGaussianMTF(w, z, ax, ay, ona, ps, scale, rot)
    mtfSecondDiv = [secondDerivAxOrAyOrZ(w, ps, rot), secondDerivAxZ(w,ps,rot),secondDerivAyZ(w,ps,rot),
                    secondDerivAxZ(w,ps,rot), secondDerivAxOrAyOrZ(w, ps, rot), secondDerivAyAx(w,ps,rot),
                    secondDerivAyZ(w,ps,rot),secondDerivAyAx(w,ps,rot),  secondDerivAxOrAyOrZ(w, ps, rot)]


    iv, jv = np.indices((3,3))

    iv = iv.reshape(-1)
    jv = jv.reshape(-1)

    res = [None]*9
    for inx in range(0,9):

        A = (-1/8)*ona**2

        i = iv[inx]
        j = jv[inx]
        ij = 3*i +j
        fin1 = A**2*np.multiply(mtf, np.multiply(mtfFirstDiv[i], mtfFirstDiv[j]))
        fin2 = A*np.multiply(mtf, mtfSecondDiv[ij])

        fin = np.add(fin1,fin2)

        res[inx] = fin
    # pdb.set_trace()
    # res = np.add([np.multiply(np.multiply(mtf, (1 / 64) * ona ** 4 * i),i) for i in mtfFirstDiv], [np.multiply(mtf,(-1/8)*ona**2)*i for i in mtfSecondDiv])

    return res

def get_gaussian_mtf(w, z, ax, ay, na, ps, scale, rot):

    mtf_meshgrid = np.meshgrid(range(int(-w / 2), int(w / 2)), range(int(-w / 2), int(w / 2))[::-1])

    Ax = ax * scale[0]
    Ay = ay * scale[1]

    mtf_meshgrid = rotate_frame(mtf_meshgrid, rot)
    ona = na
    na =  2 * math.pi / int(w*4)

    nn = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), z ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), z ** 2))
    kk = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), Ax ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), Ax ** 2))
    mm = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), 2 * Ax * z),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), -2 * Ax * z))
    oo = np.add(np.multiply(np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[0]), (na / ps) ** 2), Ay ** 2),
                np.multiply(np.multiply(np.multiply(mtf_meshgrid[1], mtf_meshgrid[1]), (na / ps) ** 2), Ay ** 2))
    pp = np.multiply(np.multiply(mtf_meshgrid[0], mtf_meshgrid[1]), -4 * Ay * z * ((na / ps) ** 2))

    qq = np.add(nn, kk)
    qq = np.add(qq, mm)
    qq = np.add(qq, oo)
    qq = np.add(qq, pp)

    mtf = np.exp(np.multiply((-1 / 8) * (ona ** 2), qq))


    return mtf

def get_hess_field(I1, I2, w, T1, T2, scale, na, ps, rot):
    # ForZ

    MTF1 = get_gaussian_mtf(w, T1[0], T1[1], T1[2], na, ps, scale, rot)
    MTfFirstDeriv1 = getFirstDerivGaussianMTF(w, T1[0], T1[1], T1[2], na, ps, scale, rot)
    MTFSecondDeriv1 = getSecondDerivGaussianMTF(w, T1[0], T1[1], T1[2], na, ps, scale, rot)

    MTF2 = get_gaussian_mtf(w, T2[0], T2[1], T2[2], na, ps, scale, rot)
    MTfFirstDeriv2 = getFirstDerivGaussianMTF(w, T2[0], T2[1], T2[2], na, ps, scale, rot)
    MTFSecondDeriv2 = getSecondDerivGaussianMTF(w, T2[0], T2[1], T2[2], na, ps, scale, rot)

    hessianField = [[None]] * 9
    iv, jv = np.indices((3, 3))

    iv = iv.reshape(-1)
    jv = jv.reshape(-1)

    x1 = np.real(I1)
    y1 = np.imag(I1)

    x2 = np.real(I2)
    y2 = np.imag(I2)


    for inx in range(0, 9):

        i = iv[inx]
        j = jv[inx]

        ij = i * 3 + j
        # pdb.set_trace()
        aa = np.subtract(np.multiply(x1, MTfFirstDeriv2[j]), np.multiply(x2, MTfFirstDeriv1[j]))
        bb = np.subtract(np.multiply(x1, MTfFirstDeriv2[i]), np.multiply(x2, MTfFirstDeriv1[i]))
        cc = np.subtract(np.multiply(y1, MTfFirstDeriv2[j]), np.multiply(y2, MTfFirstDeriv1[j]))
        dd = np.subtract(np.multiply(y1, MTfFirstDeriv2[i]), np.multiply(y2, MTfFirstDeriv1[i]))

        oo = np.subtract(np.multiply(x1, MTF2), np.multiply(x2, MTF1))
        nn = np.subtract(np.multiply(x1, MTFSecondDeriv2[ij]), np.multiply(x2, MTFSecondDeriv1[ij]))
        ll = np.subtract(np.multiply(y1, MTF2), np.multiply(y2, MTF1))
        mm = np.subtract(np.multiply(y1, MTFSecondDeriv2[ij]), np.multiply(y2, MTFSecondDeriv1[ij]))

        ee = np.add(np.multiply(MTF1, MTfFirstDeriv1[i]), np.multiply(MTF2, MTfFirstDeriv2[i]))
        kk = np.add(np.multiply(MTF1, MTfFirstDeriv1[j]), np.multiply(MTF2, MTfFirstDeriv2[j]))
        ff = np.add(np.add(np.multiply(MTF1, MTFSecondDeriv1[ij]), np.multiply(MTF2, MTFSecondDeriv2[ij])),
                    np.add(np.multiply(MTfFirstDeriv1[i], MTfFirstDeriv1[j]),
                           np.multiply(MTfFirstDeriv2[i], MTfFirstDeriv2[j])))
        gg = np.add(np.multiply(MTF1, MTF1), np.multiply(MTF2, MTF2))

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
        hessianField[inx] = fin

    hessianField = np.nansum(np.array(hessianField).T.reshape(w*w, 3, 3), axis=0)

    return hessianField

def getJacobianSplitMeasIntoRealImag(I1, I2, w, T1, T2, scale, na, ps, rot):
    # ForZ

    MTF1 = get_gaussian_mtf(w, T1[0], T1[1], T1[2], na, ps, scale, rot)
    MTfFirstDeriv1 = getFirstDerivGaussianMTF(w, T1[0], T1[1], T1[2], na, ps, scale, rot)

    MTF2 = get_gaussian_mtf(w, T2[0], T2[1], T2[2], na, ps, scale, rot)
    MTfFirstDeriv2 = getFirstDerivGaussianMTF(w, T2[0], T2[1], T2[2], na, ps, scale, rot)

    jacobianVector = [None] * 3

    x1 = np.real(I1)
    y1 = np.imag(I1)

    x2 = np.real(I2)
    y2 = np.real(I2)


    for i in range(0, 3):

        bb = np.subtract(np.multiply(x1, MTfFirstDeriv2[i]), np.multiply(x2, MTfFirstDeriv1[i]))
        dd = np.subtract(np.multiply(y1, MTfFirstDeriv2[i]), np.multiply(y2, MTfFirstDeriv1[i]))

        oo = np.subtract(np.multiply(x1, MTF2), np.multiply(x2, MTF1))
        ll = np.subtract(np.multiply(y1, MTF2), np.multiply(y2, MTF1))


        ee = np.add(np.multiply(MTF1, MTfFirstDeriv1[i]), np.multiply(MTF2, MTfFirstDeriv2[i]))
        gg = np.add(np.multiply(MTF1, MTF1), np.multiply(MTF2, MTF2))


        A = np.add(oo**2, ll**2)
        Ai = 2 *np.sum([np.multiply(oo,bb), np.multiply(ll,dd)], axis=0)


        Bi = 2 * ee

        B = gg
        fin1 = np.multiply(A, Bi)
        fin2 = -1 * np.multiply(Ai,B)

        fin = np.divide(np.add(fin1, fin2), B **2)
        jacobianVector[i] = fin

    jacobianVector = np.array(jacobianVector).T.reshape(w, w, 3)

    return jacobianVector
