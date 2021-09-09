import os
import requests
import numpy as np
from PIL import Image
from scipy.optimize import minimize
# from skimage.feature import register_translation

from skimage.registration import  phase_cross_correlation
from scipy.ndimage import shift


from . import costLib as ctl
from . import mtfLib as mtl
from . import imageLib as iml
from . import costDerivativesLib as cdl
# import costLib as ctl
# import mtfLib as mtl
# import imageLib as iml
# import costDerivativesLib as cdl


from matplotlib import pyplot as plt

def get_mapfost_path():
    return os.path.dirname(__file__)

def cropping_sanity_check(all_crop_refS):
    croppin_valid = True
    for im_crop_ref in all_crop_refS:
        if im_crop_ref[0] < 0 or im_crop_ref[1] < 0 :
            croppin_valid = False
        if im_crop_ref[2] - im_crop_ref[0] != im_crop_ref[3] - im_crop_ref[1]:
            croppin_valid = False
        if im_crop_ref[2] < im_crop_ref[0]:
            croppin_valid = False
        if im_crop_ref[2] - im_crop_ref[0] < 64:
            croppin_valid = False
    return croppin_valid


def est_aberr(test_ims, test_aberrs, pix_size_um=0.08, num_aperture=0.004, stig_rot_deg=0,
              stig_scale=1, use_bessel=False, crop_ref=(0,0), crop_size=(512,512),
              test_ims_aligned=0, get_hessian=False, get_uncertainty=False, do_subpixel_shift=False):

    im_width, im_height = test_ims[0].shape[::-1]
    test_ims_cropped = [
        np.array(Image.fromarray(m).crop((crop_ref[0], crop_ref[1], crop_ref[0] + crop_size[0], crop_ref[1] + crop_size[1]))) for m
        in test_ims]

    if not test_ims_aligned:
        shift_in_meas = [iml.get_shift_vec(test_ims_cropped[0], test_ims_cropped[1]), [0, 0]]
    else:
        shift_in_meas = [[0, 0], [0, 0]]
    # print("crop shift", crop_ref, shift_in_meas)



    # print("before", crop_ref, shift_in_meas)

    for ish in [0,1]:
        if shift_in_meas[0][ish] + crop_ref[ish] < 0:
            shift_in_meas[1][ish] = shift_in_meas[0][ish]*-1
            shift_in_meas[0][ish] = 0
            if shift_in_meas[1][ish] + crop_ref[ish] > [im_width, im_height][ish] - crop_size[ish]:
                crop_size  = np.subtract(crop_size, shift_in_meas[1][ish] + crop_ref[ish]-[im_width, im_height][ish] - crop_size[ish] )
        if shift_in_meas[0][ish] + crop_ref[ish] > [im_width, im_height][ish] - crop_size[ish]:
            shift_in_meas[1][ish] = shift_in_meas[0][ish]*-1
            shift_in_meas[0][ish] = 0
            if shift_in_meas[1][ish] + crop_ref[ish] < 0:
                crop_size  = np.add(crop_size, shift_in_meas[1][ish] + crop_ref[ish] )
                crop_ref[ish] = crop_ref[ish] + -1*(shift_in_meas[1][ish] + crop_ref[ish])

    all_crop_refS = [[crop_ref[0] + shift_in_meas[k][0],
                      crop_ref[1] + shift_in_meas[k][1],
                      crop_ref[0] + crop_size[0] + shift_in_meas[k][0],
                      crop_ref[1] + crop_size[1] + shift_in_meas[k][1]] for k in [0, 1]]

    cropping_valid = cropping_sanity_check(all_crop_refS)
    print("CROP VALID", cropping_valid)
    if cropping_valid:
        test_ims_cr_al = [np.array(Image.fromarray(m).crop((crop_ref[0] + shift_in_meas[k][0], crop_ref[1] + shift_in_meas[k][1],
                                                            crop_ref[0] + crop_size[0] + shift_in_meas[k][0],
                                                            crop_ref[1] + crop_size[1]
                                                            + shift_in_meas[k][1]))) for k, m in enumerate(test_ims)]
        if do_subpixel_shift:
            shifted, error, diffphase = phase_cross_correlation(test_ims_cr_al[0], test_ims_cr_al[1], upsample_factor=100)
            test_ims_cr_al[1] = shift(test_ims_cr_al[1], shift=(shifted[0], shifted[1]), mode='constant')


        test_ims_cr_al_pr = [iml.removeMeanAndMeanSlope(im) for im in test_ims_cr_al]
        test_ims_cr_al_pr_fft = [np.fft.fftshift(np.fft.fft2(im)) for im in test_ims_cr_al_pr]
        test_ims_cr_al_pr_fft_lp = [iml.low_pass_filter(m) for m in test_ims_cr_al_pr_fft]

        ps_width, ps_height = test_ims_cr_al_pr_fft_lp[0].shape
        kspace_xy = mtl.get_kspace_xy(ps_width, pix_size_um, stig_rot_deg)

        res = minimize(ctl.cost_mapfost, [0, 0, 0],
                       args=(test_ims_cr_al_pr_fft_lp, test_aberrs, num_aperture,stig_scale, use_bessel, kspace_xy),
                       method="L-BFGS-B")
        res.x = np.round(res.x,2)

        # Image.fromarray(test_ims_cr_al[0]).save("E:/autofocus/hessian_evolution/" + str(crop_ref) + ".tif")
        resx = res.x
        if get_hessian:
            hess_field = cdl.get_hessian_matrix(test_ims_cr_al_pr_fft_lp, np.add(test_aberrs, res.x), num_aperture, pix_size_um)
            from .import mapfost_hess_lib as mhl
            hess_field_old = mhl.get_hess_field(test_ims_cr_al_pr_fft_lp[0],test_ims_cr_al_pr_fft_lp[1],
                                                len(test_ims_cr_al_pr_fft_lp[0]),np.add(test_aberrs[0], resx),
                                                np.add(test_aberrs[1], resx),[1,1], num_aperture, pix_size_um, 0 )
            # uncertainty = cdl.get_uncertainty(test_ims_cr_al_pr_fft_lp, resx, test_aberrs, num_aperture, pix_size_um)

            # hess_curve = [cdl.get_hessian_matrix(test_ims_cr_al_pr_fft_lp, np.add(test_aberrs, [res.x[0]+ ii, 0, 0]),
            #                                      num_aperture, pix_size_um)[0,0] for ii in range(-20,20)]
            # plt.title(str(res.x))
            # plt.plot(hess_curve)
            # plt.savefig("E:/autofocus/hessian_evolution/" + str(crop_ref) + ".png")
            # plt.show()
            res.hess_field = hess_field
            res.hess_field_old = hess_field_old


    else:
        res = None
    return cropping_valid, res

def test_installation():

    im1 = np.array(Image.open(requests.get('https://gitlab.com/rangolisaxena90/mapfost/-/raw/main/src/mapfost/example/test_im1.png', stream=True).raw))
    im2 = np.array(Image.open(requests.get('https://gitlab.com/rangolisaxena90/mapfost/-/raw/main/src/mapfost/example/test_im2.png', stream=True).raw))
    res = est_aberr([im1, im2], [[-4,0,0],[4,0,0]], get_hessian=True)
    if res.x[0] == -1.11 and res.x[1] == -1.31 and res.x[2] == 0.59:
        print("...Installation Test Successful...")
        print(res)
    else:
        print(".. check if the result is close to the one given in the docs...")
        print(res)

