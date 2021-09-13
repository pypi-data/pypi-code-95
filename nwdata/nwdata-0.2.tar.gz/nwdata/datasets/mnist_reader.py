import os
import numpy as np
import h5py
from functools import partial
from overrides import overrides
from pathlib import Path
from typing import Iterator, Tuple, List
from .dataset import Dataset
from ..reader.h5_batched_reader import H5BatchedReader
from ..utils import batchIndexFromBatchSizes, toCategorical, Debug

import gzip
from urllib.error import URLError
from urllib.request import urlretrieve

class MNISTReader(H5BatchedReader, Dataset):
	def __init__(self, datasetPath:str, normalization:str = "min_max_0_1"):
		assert normalization in ("none", "min_max_0_1")

		rgbTransform = {
			"min_max_0_1" : (lambda x : np.float32(x) / 255),
			"none" : (lambda x : x)
		}[normalization]

		super().__init__(datasetPath,
			dataBuckets = {"data" : ["images"], "labels" : ["labels"]},
			dimTransform = {
				"data" : {"images" : rgbTransform},
				"labels" : {"labels" : lambda x : toCategorical(x, numClasses=10)}
			}
		)
		self.isCacheable = True

	@staticmethod
	@overrides
	def processRawData(**kwargs):
		baseDir = Path(os.environ["MNIST_DATASET_PATH"]).absolute()
		baseDir.mkdir(exist_ok=True)
		assert baseDir.is_dir()
		trainH5Path = baseDir / "train.h5"
		testH5Path = baseDir / "test.h5"
		if trainH5Path.exists():
			Debug.log(1, "[MNISTReader::processRawData] Dataset already exists at '%s'" % baseDir)
		baseUrl = "http://yann.lecun.com/exdb/mnist/"
		Debug.log(1, "[MNISTReader::processRawData] Downloading and creating dataset at '%s' from '%s'" % \
			(baseDir, baseUrl))
		files = [
			"train-images-idx3-ubyte.gz",
			"train-labels-idx1-ubyte.gz",
			"t10k-images-idx3-ubyte.gz",
			"t10k-labels-idx1-ubyte.gz",
		]

		for file in files:
			url = "%s/%s" % (baseUrl, file)
			destination = baseDir / file
			if destination.exists():
				Debug.log(1, "[MNISTReader::processRawData] Raw file '%s' exists. Skipping download." % file)
				continue
			Debug.log(1, "[MNISTReader::processRawData] Downloading '%s'." % file)
			urlretrieve(url, str(destination), reporthook=None)
			assert destination.exists(), "%s error" % url

		def processImages(path):
			Debug.log(1, "[MNISTReader::processRawData] Processing '%s'." % path)
			zippedFile = gzip.open(path, "rb")
			magic_number = int.from_bytes(zippedFile.read(4), "big")
			image_count = int.from_bytes(zippedFile.read(4), "big")
			row_count = int.from_bytes(zippedFile.read(4), "big")
			column_count = int.from_bytes(zippedFile.read(4), "big")
			image_data = zippedFile.read()
			images = np.frombuffer(image_data, dtype=np.uint8).reshape((image_count, row_count, column_count))
			zippedFile.close()
			return images

		def processLabels(path):
			Debug.log(1, "[MNISTReader::processRawData] Processing '%s'." % path)
			zippedFile = gzip.open(path, "rb")
			magic_number = int.from_bytes(zippedFile.read(4), "big")
			label_count = int.from_bytes(zippedFile.read(4), "big")
			label_data = zippedFile.read()
			labels = np.frombuffer(label_data, dtype=np.uint8)
			zippedFile.close()
			return labels

		trainImages = processImages(baseDir / files[0])
		trainLabels = processLabels(baseDir / files[1])
		testImages = processImages(baseDir / files[2])
		testLabels = processLabels(baseDir / files[3])

		trainH5File = h5py.File(trainH5Path, "w")
		trainH5File["images"] = trainImages
		trainH5File["labels"] = trainLabels
		testH5File = h5py.File(testH5Path, "w")
		testH5File["images"] = testImages
		testH5File["labels"] = testLabels
		Debug.log(1, "[MNISTReader::processRawData] Done. Train & test set were stored at '%s'" % baseDir)

	@overrides
	def getBatches(self) -> List[int]:
		if self.batches is None:
			nData = len(self.getDataset()["images"])
			batches = np.arange(nData).reshape(-1, 1)
			self.setBatches(batches)
		return self.batches

	@overrides
	def __getitem__(self, index):
		item = super().__getitem__(index)
		return {"data" : item["data"], "labels" : item["labels"]["labels"]}
