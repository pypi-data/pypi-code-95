import numpy as np
import numpy.ma as ma
from scipy import ndimage

def low_pass_filter(pow_spec, crop_factor=0.25):
    """
    low pass filtering of a regularly edged power spectrum.

    Args:
        pow_spec: 2D array, fftshifted power spectrum.
        crop_factor:  ratio of the filtered edge length to the inital edge length.

    Returns: 2D array, filtered power spectrum

    """

    powSpEdgeLen = pow_spec.shape[1]
    patchEdge = int(crop_factor * powSpEdgeLen)
    pow_spec_cropped = pow_spec[int((powSpEdgeLen - patchEdge)/2):-1 * int((powSpEdgeLen - patchEdge)/2),
              int((powSpEdgeLen - patchEdge)/2):-1 * int((powSpEdgeLen - patchEdge)/2)]
    return pow_spec_cropped

def get_shift_vec(img_ref, img_corr):

    """
    estimates the shift vector between the two images
    Args:
        img_ref: 2D array of reference image
        img_corr:2d array of the second image

    Returns:
        returns a list of length 2 which is the shift vector from img_ref to img_corr.

    """

    
    img_ref_arr = np.asarray(img_ref)
    img_corr_arr = np.asarray(img_corr)

    img_ref_smoothed = ndimage.gaussian_filter(img_ref_arr, sigma=5)
    img_corr_smoothed = ndimage.gaussian_filter(img_corr_arr, sigma=5)

    img_ref_enh = img_ref_smoothed - img_ref_arr
    img_corr_enh = img_corr_smoothed - img_corr

    ft1 = np.fft.fft2(img_ref_enh)
    ft2 = np.fft.fft2(img_corr_enh)

    cross_corr = np.fft.fftshift(np.abs(np.fft.ifft2(np.multiply(ft1, np.conj(ft2)))))
    shift_xy = np.subtract(np.unravel_index(cross_corr.argmax(), cross_corr.shape),
                            [len(img_ref_enh)/2, len(img_ref_enh)/2])[::-1]

    return shift_xy

def getMaskS(edgeLen,inOutCross=[1,1,1], reverse=False):

    radius = int(edgeLen/2)
    maskS = []
    if inOutCross[0]:

        if reverse:
            inCircleBinaryMask = np.sign(np.abs(np.add(np.sign(np.subtract(radius ** 2,
                                                                            np.add(*np.square(
                                                                                np.meshgrid(range(-1 * radius, radius),
                                                                                            range(-1 * radius, radius)
                                                                                            )
                                                                                )))), -1))).astype(float)
        else:


            inCircleBinaryMask = np.sign(np.add(np.sign(np.subtract(radius ** 2,
                                              np.add(*np.square(np.meshgrid(range(-1 * radius, radius),
                                                                            range(-1 * radius, radius)
                                                                            )
                                                                )))),1)).astype(float)
        maskS.append(inCircleBinaryMask)

    if inOutCross[1]:

        if reverse:
            outCircleBinaryMask = np.sign(np.add(np.sign(np.subtract(radius ** 2,
                                              np.add(*np.square(np.meshgrid(range(-1 * radius, radius),
                                                                            range(-1 * radius, radius)
                                                                            )
                                                                )))),1)).astype(float)
        else:

            outCircleBinaryMask = np.sign(np.abs(np.add(np.sign(np.subtract(radius ** 2,
                                              np.add(*np.square(np.meshgrid(range(-1 * radius, radius),
                                                                            range(-1 * radius, radius)
                                                                            )
                                                                )))),-1))).astype(float)
        maskS.append(outCircleBinaryMask)
    if inOutCross[2]:

        if reverse:
            crossMask = np.abs(np.sign(np.abs(np.multiply(*np.meshgrid(range(-1 * radius, radius),
                                                                       range(-1 * radius, radius)
                                                                       )
                                                          )))).astype(float)
        else:
            crossMask = np.abs(np.subtract(np.sign(np.abs(np.multiply(*np.meshgrid(range(-1 * radius, radius),
                                                                       range(-1 * radius, radius)
                                                                       )
                                                          ))), 1)).astype(float)


        maskS.append(crossMask)

    return maskS


def applyMask(powSpec, maskS=None, inOutCross=[0,1,1], debug = False):
    if maskS is None:
        maskS = getMaskS(len(powSpec), inOutCross)
    if debug:
        for im, mask in enumerate(maskS):
            print(mask)
    for ii,mask in enumerate(maskS):
        powSpec = ma.masked_array(powSpec, mask)

    return powSpec

def removeMeanAndMeanSlope(im):

    imarr = np.array(im)
    deMeaned = np.subtract(imarr, np.mean(imarr))
    imwidth, imheight = deMeaned.shape
    deSloped = np.subtract(deMeaned,
                           np.add(*np.meshgrid(np.linspace(np.mean(deMeaned[0]), np.mean(deMeaned[-1]), imwidth),
                                               np.linspace(np.mean(deMeaned[:, 0]), np.mean(deMeaned[:, -1]),
                                                           imheight))))

    return deSloped