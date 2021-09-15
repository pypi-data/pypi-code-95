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
__date__ = "05/10/2020"

import numpy


def convertDictToDim(_dict):

    from darfix.core.dataset import Dimension
    """
    Convert dictionary of dimensions from Settings to Dimension.
    """
    if len(_dict) > 0:
        _dims = {}
        for _axis, _dim in _dict.items():
            assert type(_dim) is dict
            _dims[_axis] = Dimension.from_dict(_dim)
        return _dims

    else:
        return {}


def wrapTo2pi(x):
    """
    Python implementation of Matlab method `wrapTo2pi`.
    Wraps angles in x, in radians, to the interval [0, 2*pi] such that 0 maps
    to 0 and 2*pi maps to 2*pi. In general, positive multiples of 2*pi map to
    2*pi and negative multiples of 2*pi map to 0.
    """
    xwrap = numpy.remainder(x - numpy.pi, 2 * numpy.pi)
    mask = numpy.abs(xwrap) > numpy.pi
    xwrap[mask] -= 2 * numpy.pi * numpy.sign(xwrap[mask])
    return xwrap + numpy.pi
