import dask.array as da

from . import richardsonLucy
from .psf import PSF
from ..adjustments.parallel import to_float


def deconvolve(input_img, H, Ht, num_iters):
    input_shape = input_img.shape
    dec = richardsonLucy.dec_conv()
    dec.psf_calc(H, Ht, input_shape)
    return dec.deconv(input_img, lamb=1, num_iters=num_iters, weights=1).reshape(dec.shape)


def deconvolve_single(input_img, img_resolution, psf_invert, psf_path, psf_res, iterations):
    input_shape = input_img.shape

    psf = PSF(psf_path, psf_res)
    if psf_invert:
        psf.flip()
    psf.visualize("PSF extracted")

    psf.adjust_resolution(img_resolution)
    psf.resize(input_shape, [0, 0, 0])

    H, Ht = psf.calculate_otf()
    print("OTF calculated")

    dec = richardsonLucy.dec_conv()
    dec.psf_calc(H, Ht, input_shape)
    return dec.deconv(input_img, lamb=1, num_iters=iterations, weights=1).reshape(dec.shape)


def deconvolve_parallel(dask_img, img_resolution, chunk_size, overlap, psf_invert, psf_path, psf_res, iterations):
    psf = PSF(psf_path, psf_res)
    if psf_invert:
        psf.flip()

    psf.adjust_resolution(img_resolution)
    psf.resize(chunk_size, overlap)

    H, Ht = psf.calculate_otf()
    print("\t\tOTF calculated")

    dask_img = to_float(dask_img)
    dask_img = da.overlap.overlap(dask_img, depth={0: overlap[0], 1: overlap[1], 2: overlap[2]},
                                  boundary='reflect')
    dask_img = da.map_blocks(deconvolve, dask_img, H, Ht, iterations, dtype='f4')
    return da.overlap.trim_internal(dask_img, {0: overlap[0], 1: overlap[1], 2: overlap[2]})
