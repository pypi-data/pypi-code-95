import numpy as np
from scipy import special

def spaceRotate(meshx, meshy, rot):
    """
    rotates the spatial mesh for x and spatial mesh for y by the angle rot.
    Args:
        meshx: 2D array spatial mesh for x
        meshy: 2D array spatial mesh for y
        rot: rotation angle in degrees

    Returns:
        rotated spatial mesh
    """
    meshxtr = np.subtract(meshx * np.cos(np.radians(rot)), meshy * np.sin(np.radians(rot)))
    meshytr = np.add(meshx * np.sin(np.radians(rot)), meshy * np.cos(np.radians(rot)))
    return [meshxtr, meshytr]

def get_kspace_xy(edgeLen, pixSzUM, astigRot=0, pow_spec_crop_factor=0.5):
    """
    Returns the wave vectors kx and ky of size edgeLen and rotated by the angle astigRot
    Args:
        edgeLen: the edge length of the wave vector grid
        pixSzUM: pixel size in um
        astigRot: the rotation in degrees between the image plane and the stigmation plane
        pow_spec_crop_factor: ratio of the filtered edge length to the inital edge length
         of the test images power spectrum. Refer mapfost.imageLib.lowpass_pow_spec()

    Returns:
        2D array of kx and ky wave vectors in a list of length 2 [kx, ky]. rotated by astigRot
    """

    kNyquist = 2*np.pi*pow_spec_crop_factor/pixSzUM

    kXarr = np.linspace(-kNyquist, kNyquist, edgeLen, endpoint=False)
    kYarr = np.linspace(-kNyquist, kNyquist, edgeLen, endpoint=False)[::-1]
    kXY = np.meshgrid(kXarr, kYarr)

    kXYrotated = spaceRotate(kXY[0], kXY[1],astigRot)

    return kXYrotated

def getMTF(kspaceXY, z, ax, ay, num_aperture=0.004, useBessel=False):

    """
    Generates the MTF for the aberration state [z, ax, ay] with the given numerical aperture.
    Args:
        kspaceXY: 2D array of kx and ky wave vectors in a list of length 2 [kx, ky]
        z: defocus in um
        ax: amount of ax in um
        ay: amount of ay in um
        num_aperture: numerical aperture of the optical system
        useBessel: if yes, a bessel mtf will be returned, if no the gaussian approximation will be returned

    Returns:
        a 2D array of mtf with the zero frequency in the center.

    """

    kX, kY = kspaceXY

    qq = np.add(
        np.add(
            np.multiply(
                np.multiply(
                    kX, kX),
                z ** 2 + ax ** 2 + ay ** 2 + 2 * ax * z),
            np.multiply(
                np.multiply(
                    kY, kY),
                z ** 2 + ax ** 2 + ay ** 2 - 2 * ax * z)),
        np.multiply(
            np.multiply(
                kX, kY), - 4 * ay * z))

    if not useBessel:
        return np.exp(np.multiply
                      ((-1 / 8) * (num_aperture ** 2)
                       , qq)).astype(np.float64)
    else:
        ll = num_aperture * np.sqrt(np.add(qq, 10**-18))
        return np.divide(2 * special.jv(1, ll), ll).astype(np.float64)
