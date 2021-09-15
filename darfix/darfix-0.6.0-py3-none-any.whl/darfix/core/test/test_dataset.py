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
__date__ = "09/12/2020"

import copy
import unittest
import numpy
import tempfile
import shutil

from silx.io.url import DataUrl

from darfix.test import utils
from darfix.core.dataset import Data


class TestDataset(unittest.TestCase):

    """Tests for class Dataset in `dataset.py`"""

    def setUp(self):
        self._dir = tempfile.mkdtemp()
        self.dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=3,
                                                 header=True, _dir=self._dir)

    def test_data_load(self):
        """ Tests the correct load of the data"""
        self.assertEqual(len(self.dataset.get_data()), 3)
        self.assertEqual(self.dataset.nframes, 3)

    def test_nframes(self):
        """Tests the nframes method"""
        self.assertEqual(self.dataset.nframes, 3)

    def test_deepcopy(self):
        """Tests the correct deepcopy of the object"""
        dataset_copy = copy.deepcopy(self.dataset)
        self.assertEqual(self.dataset.nframes, dataset_copy.nframes)
        self.assertEqual(self.dataset.data.shape, dataset_copy.data.shape)

    def test_zsum_in_memory(self):

        zsum = self.dataset.zsum()
        self.assertEqual(zsum.shape, (100, 100))

        result = numpy.sum(self.dataset.get_data(), axis=0)
        numpy.testing.assert_array_equal(zsum, result)

        indices = [0, 1]
        zsum = self.dataset.zsum(indices)
        result = numpy.sum(self.dataset.get_data(indices), axis=0)
        numpy.testing.assert_array_equal(zsum, result)

    def test_zsum_in_disk(self):

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        zsum = dataset.zsum(indices)
        self.assertEqual(zsum.shape, (100, 100))
        data = []
        for i in indices:
            data += [dataset.get_data(i)]
        result = numpy.sum(data, axis=0)
        numpy.testing.assert_array_equal(zsum, result)

    def test_filter_data(self):
        """ Tests the correct separation of empty frames and data frames"""
        dims = (10, 100, 100)
        data = numpy.zeros(dims)
        background = numpy.random.random(dims)
        idxs = [0, 2, 4]
        data[idxs] += background[idxs]
        dataset = utils.createDataset(data=data, _dir=self._dir)
        hi_idx, li_idx = dataset.partition_by_intensity()
        self.assertEqual(hi_idx.shape[0], 3)
        self.assertEqual(li_idx.shape[0], 7)

    def test_bs_in_memory(self):
        """ Tests the background subtraction function with data in memory"""
        indices = [0, 1]
        bs_dataset = self.dataset.apply_background_subtraction(background=[2], indices=indices)

        self.assertEqual(bs_dataset.nframes, self.dataset.nframes)
        self.assertNotEqual(bs_dataset.data.urls[0], self.dataset.data.urls[0])
        numpy.testing.assert_equal(self.dataset.data.metadata, bs_dataset.data.metadata)
        numpy.testing.assert_equal(self.dataset.data[2], bs_dataset.data[2])

    def test_bs_in_disk(self):
        """ Tests the background subtraction function with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        bs_dataset = dataset.apply_background_subtraction(background=[5, 6, 7, 8, 9], indices=indices)

        self.assertEqual(bs_dataset.nframes, dataset.nframes)
        self.assertNotEqual(dataset.data.urls[0], bs_dataset.data.urls[0])
        numpy.testing.assert_equal(dataset.data[6], bs_dataset.data[6])

    def test_bs_mean_in_disk(self):
        """ Tests the correct subtraction of the background with data in disk and mean method"""
        data = numpy.array([[[1, 2, 3, 4, 5],
                             [2, 2, 3, 4, 5],
                             [3, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 3],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [8, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]]])

        dark = numpy.array([[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]])

        expected = numpy.array([[[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [2, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [7, 0, 0, 0, 0], [0, 0, 0, 0, 0]]])

        dataset = utils.createDataset(data, in_memory=False)

        # Background data in memory

        dark_dataset = utils.createDataset(dark, in_memory=True)

        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="mean")
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

        # Background data in disk

        dark_dataset = utils.createDataset(dark, in_memory=False)

        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="mean")
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

    def test_bs_median_in_disk(self):
        """ Tests the correct subtraction of the background with data in disk and median method"""
        data = numpy.array([[[1, 2, 3, 4, 5],
                             [2, 2, 3, 4, 5],
                             [3, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 3],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5],
                             [8, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5]]])

        dark = numpy.array([[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                            [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                             [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]])

        expected = numpy.array([[[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [2, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [7, 0, 0, 0, 0], [0, 0, 0, 0, 0]]])

        dataset = utils.createDataset(data, in_memory=False)

        # Background data in memory

        dark_dataset = utils.createDataset(dark, in_memory=True)

        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="median")
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

        # Background data in disk

        dark_dataset = utils.createDataset(dark, in_memory=False)

        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="median")
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

        # Compute background with chunks
        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="median",
                                                           chunk_shape=[2, 2])
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

        # Compute background with step
        new_dataset = dataset.apply_background_subtraction(background=dark_dataset, method="median",
                                                           step=2)
        new_dataset.in_memory = True
        numpy.testing.assert_array_equal(expected, new_dataset.data)

    def test_hp_in_memory(self):
        """ Tests the hot pixel removal function with data in memory"""
        indices = [0, 1]
        hp_dataset = self.dataset.apply_hot_pixel_removal(indices=indices)

        self.assertEqual(hp_dataset.nframes, self.dataset.nframes)
        self.assertNotEqual(hp_dataset.data.urls[0], self.dataset.data.urls[0])
        numpy.testing.assert_equal(self.dataset.data.metadata, hp_dataset.data.metadata)
        numpy.testing.assert_equal(self.dataset.data[2], hp_dataset.data[2])

    def test_hp_in_disk(self):
        """ Tests the hot pixel removal function with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        hp_dataset = dataset.apply_hot_pixel_removal(indices=indices)

        self.assertEqual(hp_dataset.nframes, dataset.nframes)
        self.assertNotEqual(hp_dataset.data.urls[0], dataset.data.urls[0])
        numpy.testing.assert_equal(dataset.data[5], hp_dataset.data[5])

    def test_threshold_in_memory(self):
        """ Tests the threshold removal function with data in memory"""
        indices = [0, 1]
        threshold_dataset = self.dataset.apply_threshold_removal(indices=indices)

        self.assertEqual(threshold_dataset.nframes, self.dataset.nframes)
        self.assertNotEqual(threshold_dataset.data.urls[0], self.dataset.data.urls[0])
        numpy.testing.assert_equal(self.dataset.data.metadata, threshold_dataset.data.metadata)
        numpy.testing.assert_equal(self.dataset.data[2], threshold_dataset.data[2])

    def test_threshold_in_disk(self):
        """ Tests the threshold removal function with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        threshold_dataset = dataset.apply_threshold_removal(indices=indices)

        self.assertEqual(threshold_dataset.nframes, dataset.nframes)
        self.assertNotEqual(threshold_dataset.data.urls[0], dataset.data.urls[0])
        numpy.testing.assert_equal(dataset.data[5], threshold_dataset.data[5])

    def test_roi_in_memory(self):
        """ Tests the roi function with data in memory"""
        new_dataset = self.dataset.apply_roi(origin=[0, 0], size=[20, 20])
        self.assertEqual(new_dataset.nframes, 3)
        numpy.testing.assert_equal(self.dataset.data[:, :20, :20], new_dataset.data)

    def test_roi_in_disk(self):
        """ Tests the roi function with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        new_dataset = dataset.apply_roi(origin=[0, 0], size=[20, 20], indices=indices)

        self.assertEqual(new_dataset.nframes, 5)
        numpy.testing.assert_equal(dataset.get_data(indices)[0][:20, :20], new_dataset.data[0])

    def test_find_shift(self):
        """ Tests the shift detection"""
        shift = self.dataset.find_shift()

        self.assertEqual(shift.shape, (2, 3))

        shift = self.dataset.find_shift(indices=[0, 1])

        self.assertEqual(shift.shape, (2, 2))

    def test_apply_shift(self):
        """ Tests the shift correction"""

        new_dataset = self.dataset.apply_shift(shift=numpy.array([[0, 0.5, 1], [0, 0.5, 1]]))

        self.assertEqual(new_dataset.nframes, self.dataset.nframes)
        self.assertNotEqual(new_dataset.data.urls[0], self.dataset.data.urls[0])

    def test_pca_in_memory(self):
        """ Tests PCA with data in memory"""

        H, W = self.dataset.pca()

        self.assertEqual(H.shape, (self.dataset.nframes, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (self.dataset.nframes, self.dataset.nframes))

        n_components = 1
        indices = [1, 2]
        H, W = self.dataset.pca(num_components=n_components, indices=indices)

        self.assertEqual(H.shape, (n_components, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (2, n_components))

    def test_pca_in_disk(self):
        """ Tests PCA with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)

        H, W = dataset.pca(chunk_size=1000)

        self.assertEqual(H.shape, (dataset.nframes, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (dataset.nframes, dataset.nframes))

        n_components = 3
        indices = [0, 1, 3, 4, 6]
        H, W = dataset.pca(chunk_size=1000, num_components=n_components, indices=indices)

        self.assertEqual(H.shape, (n_components, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (5, n_components))

    def test_nmf_in_memory(self):
        """ Tests NMF with data in memory"""

        num_components = 2
        H, W = self.dataset.nmf(num_components)

        self.assertEqual(H.shape, (num_components, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (self.dataset.nframes, num_components))

        num_components = 1
        indices = [1, 2]
        H, W = self.dataset.nmf(num_components=num_components, indices=indices)

        self.assertEqual(H.shape, (num_components, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (2, num_components))

    def test_nmf_in_disk(self):
        """ Tests NMF with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)

        num_components = 5
        H, W = dataset.nmf(num_components=num_components, num_iter=10, cascade=[100, 50, 25])

        self.assertEqual(H.shape, (num_components, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (dataset.nframes, num_components))

        n_components = 4
        indices = numpy.random.choice(10, size=8, replace=False)
        H, W = dataset.nmf(num_components=n_components, indices=indices)

        self.assertEqual(H.shape, (n_components, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (len(indices), n_components))

    def test_nica_in_memory(self):
        """ Tests NICA with data in memory"""

        num_components = 2
        H, W = self.dataset.nica(num_components)

        self.assertEqual(H.shape, (num_components, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (self.dataset.nframes, num_components))

        num_components = 1
        indices = [1, 2]
        H, W = self.dataset.nica(num_components=num_components, indices=indices)

        self.assertEqual(H.shape, (num_components, len(self.dataset.data[0].flatten())))
        self.assertEqual(W.shape, (2, num_components))

    def test_nica_in_disk(self):
        """ Tests NICA with data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=100, in_memory=False)

        num_components = 5
        H, W = dataset.nica(num_components=num_components, chunksize=1000)

        self.assertEqual(H.shape, (num_components, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (dataset.nframes, num_components))

        n_components = 10
        indices = numpy.random.choice(100, size=80, replace=False)
        H, W = dataset.nica(num_components=n_components, indices=indices, chunksize=1000)

        self.assertEqual(H.shape, (n_components, len(dataset.data[0].flatten())))
        self.assertEqual(W.shape, (len(indices), n_components))

    def test_apply_fit_in_memory(self):
        """ Tests fitting data in memory"""
        new_dataset = self.dataset.apply_fit()

        self.assertEqual(new_dataset.nframes, self.dataset.nframes)
        self.assertNotEqual(new_dataset.data.urls[0], self.dataset.data.urls[0])

    def test_apply_fit_in_disk(self):
        """Tests fitting data in disk"""

        dataset = utils.createRandomDataset(dims=(100, 100), nb_data_files=10, in_memory=False)
        indices = [0, 1, 2, 3, 4]
        fit_dataset = dataset.apply_fit(indices=indices)

        self.assertEqual(fit_dataset.nframes, dataset.nframes)
        self.assertNotEqual(fit_dataset.data.urls[0], dataset.data.urls[0])
        numpy.testing.assert_equal(fit_dataset.data[5], dataset.data[5])


class TestData(unittest.TestCase):

    """Tests for class Data in `dataset.py`"""

    def setUp(self):
        self._dir = tempfile.mkdtemp()
        self.urls = []
        self.metadata = []
        self.data = []
        for i in range(10):
            url = self._dir + str(i) + ".npy"
            data = numpy.random.rand(100, 100)
            self.data += [data]
            self.urls += [DataUrl(file_path=url, scheme='fabio')]
            self.metadata += ["No metadata"]
            numpy.save(url, data)

        self.data = numpy.array(self.data)

    def test_create_data_in_memory(self):
        """ Tests the correct creation of the data in memory"""
        data = Data(urls=self.urls, metadata=self.metadata)

        for i in range(10):
            self.assertEqual(data.urls[i], self.urls[i])
            self.assertEqual(data.metadata[i], self.metadata[i])

        numpy.testing.assert_array_equal(self.data, data)

    def test_create_data_in_disk(self):
        """ Tests the correct creation of the data in disk"""
        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)

        for i in range(10):
            self.assertEqual(data.urls[i], self.urls[i])
            self.assertEqual(data.metadata[i], self.metadata[i])

    def test_get_in_memory(self):
        """ Tests the correct get of the data in memory"""
        data = Data(urls=self.urls, metadata=self.metadata)

        for i in range(10):
            numpy.testing.assert_array_equal(data[i], self.data[i])

        indices = [0, 2, 6]
        numpy.testing.assert_array_equal(self.data[indices], data[indices])

    def test_get_in_disk(self):
        """ Tests the correct get of the data in disk"""
        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)

        for i in range(10):
            numpy.testing.assert_array_equal(data[i], self.data[i])

        indices = [0, 2, 6]
        for i in range(3):
            numpy.testing.assert_array_equal(self.data[indices][i], data[indices][i])

    def test_get_slices_in_memory(self):
        """ Tests getting slices of the data in memory"""
        data = Data(urls=self.urls, metadata=self.metadata)

        numpy.testing.assert_array_equal(data[2:3, 50:, 50:], self.data[2:3, 50:, 50:])

    def test_get_slices_in_disk(self):
        """ Tests getting slices of the data in disk"""
        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)

        for i in range(3):
            numpy.testing.assert_array_equal(data[2:5][i], self.data[2:5][i])

    def test_shape_in_memory(self):
        """ Tests the correct shape of the data in memory"""
        data = Data(urls=self.urls, metadata=self.metadata)
        self.assertEqual(data.shape, self.data.shape)

        urls = numpy.array(self.urls).reshape((5, 2))
        data = Data(urls=urls, metadata=self.metadata)
        self.assertEqual(data.shape, (5, 2, 100, 100))

    def test_shape_in_disk(self):
        """ Tests the correct shape of the data in disk"""
        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)
        self.assertEqual(data.shape, self.data.shape)

        urls = numpy.array(self.urls).reshape((5, 2))
        data = Data(urls=urls, metadata=self.metadata, in_memory=False)
        self.assertEqual(data.shape, (5, 2, 100, 100))

    def test_save(self):
        data = numpy.random.rand(10, 100, 100).view(Data)
        # data.in_memory = True
        data.save(self._dir + "/data.hdf5")

        numpy.testing.assert_array_equal(data.shape, (10, 100, 100))

    def test_convert_to_hdf5(self):
        """ Tests the reshape of the data"""
        data = Data(urls=self.urls, metadata=self.metadata)
        dataset = data.convert_to_hdf5(self._dir)
        self.assertEqual(dataset.shape, (10, 10000))
        data._file.close()

        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)
        dataset = data.convert_to_hdf5(self._dir)
        self.assertEqual(dataset.shape, (10, 10000))

    def test_reshape(self):
        """ Tests the reshape of the data"""
        data = Data(urls=self.urls, metadata=self.metadata)
        new_data = data.reshape((2, 5, 100, 100))
        self.assertEqual(new_data.shape, (2, 5, 100, 100))

        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)
        new_data = data.reshape((2, 5, 100, 100))
        self.assertEqual(new_data.shape, (2, 5, 100, 100))

    def test_take(self):
        """ Tests the take of the data"""
        data = Data(urls=self.urls, metadata=self.metadata)
        result = numpy.take(self.data, [0, 1, 2, 3], axis=0)
        new_data = data.take([0, 1, 2, 3])
        numpy.testing.assert_array_equal(new_data, result)

        data = Data(urls=self.urls, metadata=self.metadata, in_memory=False)
        new_data = data.take([0, 1, 2, 3])
        for i in range(4):
            numpy.testing.assert_array_equal(new_data[i], result[i])

    def test_flatten(self):
        """ Tests the flatten of the data"""
        urls = numpy.array(self.urls).reshape((2, 5))
        data = Data(urls=urls, metadata=self.metadata)
        numpy.testing.assert_array_equal(self.data, data.flatten())

        data = Data(urls=urls, metadata=self.metadata, in_memory=False)
        for i in range(4):
            numpy.testing.assert_array_equal(data.flatten()[i], self.data[i])

    def tearDown(self):
        shutil.rmtree(self._dir)


if __name__ == '__main__':
    unittest.main()
