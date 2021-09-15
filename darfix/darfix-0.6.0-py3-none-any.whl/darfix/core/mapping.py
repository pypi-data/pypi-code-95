# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "04/06/2021"

import numpy
try:
    import tqdm
except ImportError:
    tqdm = None
from functools import partial
import multiprocessing
from multiprocessing import Pool
from scipy.optimize import curve_fit
from scipy.stats import skew, kurtosis
from silx.math.medianfilter import medfilt2d


def gaussian(x, a, b, c, d):
    """
    Function to calculate the Gaussian with constants a, b, and c

    :param float x: Value to evaluate
    :param float a: height of the curve's peak
    :param float b: position of the center of the peak
    :param float c: standard deviation
    :param float d: lowest value of the curve (value of the limits)

    :returns: result of the function on x
    :rtype: float
    """
    return d + a * numpy.exp(-numpy.power(x - b, 2) / (2 * numpy.power(c, 2)))


def generator(data, moments=None):
    """
    Generator that returns the rocking curve for every pixel

    :param ndarray data: data to analyse
    :param moments: array of same shape as data with the moments values per pixel and image, optional
    :type moments: Union[None, ndarray]
    """
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if moments is not None:
                yield data[:, i, j], moments[:, i, j]
            yield data[:, i, j], None


def fit_rocking_curve(y_values, values=None, num_points=None, int_thresh=None):
    """
    Fit rocking curve.

    :param tuple y_values: the first element is the dependent data and the second element are
        the moments to use as starting values for the fit
    :param values: The independent variable where the data is measured, optional
    :type values: Union[None, list]
    :param int num_points: Number of points to evaluate the data on, optional
    :param float int_thresh: Intensity threshold. If not None, only the rocking curves with
        higher ptp (range of values) are fitted, others are assumed to be noise and not important
        data. This parameter is used to accelerate the fit. Optional.

    :returns: If curve was fitted, the fitted curve, else item[0]
    :rtype: list
    """
    y, moments = y_values
    y = numpy.asanyarray(y)
    if int_thresh is not None and y.ptp() < int_thresh:
        return y
    x = values if values is not None else numpy.arange(len(y))
    if moments is not None:
        p0 = [y.ptp(), moments[0], moments[1], min(y)]
    else:
        mean = sum(x * y) / sum(y)
        sigma = numpy.sqrt(sum(y * (x - mean)**2) / sum(y))
        p0 = [y.ptp(), mean, sigma, min(y)]
    if numpy.isclose(p0[2], 0):
        return y
    if num_points is None:
        num_points = len(y)
    try:
        pars, cov = curve_fit(f=gaussian, xdata=x, ydata=y, p0=p0)
        y_gauss = gaussian(numpy.linspace(x[0], x[-1], num_points), *pars)
        y_gauss[numpy.isnan(y_gauss)] = 0
        return y_gauss
    except RuntimeError:
        return y


def fit_data(data, moments=None, values=None, int_thresh=15, _tqdm=False):
    """
    Fit data in axis 0 of data

    :param bool _tqdm: If True, execut fitting under tqdm library.
    :returns: fitted data
    """
    g = generator(data, moments)
    cpus = multiprocessing.cpu_count()
    with Pool(cpus - 1) as p:
        if _tqdm and tqdm is not None:
            new_data = list(tqdm.tqdm(p.imap(partial(fit_rocking_curve, values=values, int_thresh=15), g), total=data.shape[1] * data.shape[2]))
        else:
            new_data = p.map(partial(fit_rocking_curve, values=values, int_thresh=15), g)
    return numpy.array(new_data).T.reshape(data.shape)


def compute_moments(values, data):
    """
    Compute first, second, third and fourth moment of data on values.

    :returns: The four moments
    """
    stack = [values[i] * data[i] for i in range(len(data))]
    zsum = numpy.sum(data, axis=0)
    com = numpy.sum(stack, axis=0) / zsum
    com = medfilt2d(com.astype(numpy.float64))
    com[numpy.isnan(com)] = numpy.min(com[~numpy.isnan(com)])
    repeat_values = numpy.repeat(values, com.shape[0] * com.shape[1]).reshape(len(values), com.shape[0], com.shape[1])
    std = numpy.sqrt(numpy.sum((data[i] * ((repeat_values[i] - com)**2) for i in range(len(data))), axis=0)) / zsum
    std = medfilt2d(std.astype(numpy.float64))
    std[numpy.isnan(std)] = numpy.min(std[~numpy.isnan(std)])
    skews = skew(stack, axis=0)
    kurt = kurtosis(stack, axis=0)

    return com, std, skews, kurt


def compute_rsm(H, W, d, ffz, mainx):

    pix_arr = numpy.meshgrid(numpy.arange(H), numpy.arange(W))
    pix_arr[0] = (pix_arr[0] - W / 2) * d
    pix_arr[1] = (H / 2 - pix_arr[1]) * d
    pix_arr[0] = numpy.arctan2((ffz - W / 2) * pix_arr[0], mainx)
    pix_arr[1] = numpy.arctan2(pix_arr[1], numpy.sqrt(ffz * ffz + mainx * mainx))
    return pix_arr


def compute_magnification(H, W, d, obx, obpitch, mainx):

    pix_arr = numpy.meshgrid(numpy.arange(H), numpy.arange(W))
    d1 = obx / numpy.cos(obpitch)
    d2 = mainx / numpy.cos(obpitch) - d1
    M = d2 / d1
    d /= M
    pix_arr[0] = (pix_arr[0] - W / 2) * d
    pix_arr[1] = (H / 2 - pix_arr[1]) * d
    return pix_arr
