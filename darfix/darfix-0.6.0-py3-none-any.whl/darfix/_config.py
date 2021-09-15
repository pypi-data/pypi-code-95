# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017-2019 European Synchrotron Radiation Facility
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
"""This module contains library wide configuration.
"""

__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "19/11/2020"


class Config(object):
    """
    Class containing shared global configuration for the darfix project.

    .. versionadded:: 0.3
    """

    DEFAULT_COLORMAP_NAME = 'cividis'
    DEFAULT_COLORMAP_NORM = 'log'
    """Default LUT for the plot widgets.

    The available list of names are available in the module
    :module:`silx.gui.colors`.

    .. versionadded:: 0.3
    """

    FWHM_VAL = 2.35482

    """Magic value that returns FWHM when multiplied by the standard deviation.

    .. versionadded:: 0.5
    """
