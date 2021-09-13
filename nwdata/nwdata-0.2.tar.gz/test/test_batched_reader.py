import numpy as np
from overrides import overrides
from typing import Tuple, List, Any
from nwdata import BatchedReader
from nwdata.utils import batchIndexFromBatchSizes, getBatchIndexLen

class DummyBatchedDataset(BatchedReader):
	def __init__(self, N=10, seed=42):
		super().__init__(
			dataBuckets = {"data" : ["rgb"], "labels" : ["class"]},
			dimGetter = {
				"rgb" : (lambda dataset, index : dataset[index]),
				"class" : (lambda dataset, index : getBatchIndexLen(index) * [0])
			},
			dimTransform = {}
		)
		self.N = N
		self.isCacheable = True
		np.random.seed(42)
		self.dataset = np.random.randn(N, 3)
		self.setBatches(self.batchFn())

	@overrides
	def getDataset(self) -> Any:
		return self.dataset

	@overrides
	def getBatches(self) -> List[int]:
		return self.batches

	def batchFn(self) -> List[int]:
		batchSizes = np.array({
			10 : [4, 1, 2, 3],
			20 : [10, 10],
			100 : [40, 10, 20, 30]
		}[self.N], dtype=np.int32)
		batches = batchIndexFromBatchSizes(batchSizes)
		return batches

class TestBatchedDataset:
	def test_constructor_1(self):
		reader = DummyBatchedDataset()
		assert not reader is None

	def test_getBatchItem_1(self):
		reader = DummyBatchedDataset()
		batches = reader.getBatches()
		item = reader.iterate()[0]
		rgb = item["data"]["rgb"]
		assert rgb.shape[0] == 4
		assert np.abs(rgb - reader.dataset[0:4]).sum() < 1e-5

	def test_getBatchItem_2(self):
		reader = DummyBatchedDataset()
		batches = reader.getBatches()
		g = reader.iterate()
		n = len(g)
		for j in range(100):
			index = batches[j % n]
			batchItem = g[j % n]
			rgb = batchItem["data"]["rgb"]
			assert np.abs(rgb - reader.dataset[index.start : index.stop]).sum() < 1e-5

	def test_iterateForever_1(self):
		reader = DummyBatchedDataset()
		batches = reader.getBatches()
		batchSizes = [(x.stop - x.start) for x in batches]
		n = len(batches)
		for j, batchItem in enumerate(reader.iterateForever()):
			rgb = batchItem["data"]["rgb"]
			try:
				assert len(rgb) == batchSizes[j % n]
			except Exception as e:
				print(str(e))
				breakpoint()
			index = batches[j % n]
			assert np.abs(rgb - reader.dataset[index.start : index.stop]).sum() < 1e-5

			if j == 100:
				break

def main():
	TestBatchedDataset().test_getBatchItem_1()

if __name__ == "__main__":
	main()