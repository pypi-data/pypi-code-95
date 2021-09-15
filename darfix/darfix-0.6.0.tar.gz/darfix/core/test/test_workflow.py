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
__date__ = "08/12/2020"


import unittest
import shutil
import tempfile

import numpy
try:
    import scipy
except ImportError:
    scipy = None

from darfix.test import utils
from darfix.core import imageOperations, imageRegistration, roi


@unittest.skipUnless(scipy, "scipy is missing")
class TestWorkflow(unittest.TestCase):

    """Tests different workflows"""

    def setUp(self):
        self._dir = tempfile.mkdtemp()
        first_frame = numpy.zeros((100, 100))
        # Simulating a series of frame with information in the middle.
        first_frame[25:75, 25:75] = numpy.random.randint(50, 300, size=(50, 50))
        background = [numpy.random.randint(-5, 5, size=(100, 100), dtype='int16') for i in range(5)]
        data = [first_frame]
        shift = [1.0, 0]
        for i in range(9):
            data += [numpy.fft.ifftn(scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)).real]
        data = numpy.asanyarray(data, dtype=numpy.int16)
        self.dataset = utils.createDataset(data=data, _dir=self._dir)
        self.dark_dataset = utils.createDataset(data=background, _dir=self._dir)

    def test_workflow0(self):
        """ Tests a possible workflow"""

        expected = numpy.subtract(self.dataset.data[:, 49:52, 50:51],
                                  numpy.median(self.dark_dataset.data[:, 49:52, 50:51],
                                  axis=0).astype(numpy.int16), dtype=numpy.int64).astype(numpy.int16)
        expected[expected > 20] = 0
        expected[expected < 1] = 0
        # ROI of the data
        data = roi.apply_3D_ROI(self.dataset.data, size=[3, 3], center=(numpy.array(self.dataset.data[0].shape) / 2).astype(numpy.int))

        # ROI of the dark frames
        dark_frames = roi.apply_3D_ROI(numpy.array(self.dark_dataset.data), size=[3, 3],
                                       center=(numpy.array(self.dark_dataset.data[0].shape) / 2).astype(numpy.int))

        # Background substraction of the data
        data = imageOperations.background_subtraction(data, dark_frames, method="median")
        # ROI of the data
        data = roi.apply_3D_ROI(data, size=[3, 1], center=(numpy.array(data[0].shape) / 2).astype(numpy.int))
        # Threshold removal of the data
        data = imageOperations.threshold_removal(data, 1, 20)
        numpy.testing.assert_array_equal(data, expected)

    def test_workflow1(self):
        """ Tests a possible workflow"""

        first_frame = numpy.asarray(self.dataset.data[0])
        expected = numpy.tile(first_frame, (10, 1)).reshape(10, 100, 100)[:, 25:75, 25:75].astype(numpy.float32)
        # Detect the shift
        optimal_shift = imageRegistration.shift_detection(self.dataset.data, 2)
        data = imageRegistration.shift_correction(self.dataset.data, optimal_shift)

        # ROI of the data
        data = roi.apply_3D_ROI(data, size=[50, 50], center=(numpy.array(self.dataset.data[0].shape) / 2).astype(numpy.int))

        numpy.testing.assert_allclose(data[0, 0:10, 0:10], expected[0, 0:10, 0:10], rtol=0.1)

    def tearDown(self):
        shutil.rmtree(self._dir)


if __name__ == '__main__':
    unittest.main()
