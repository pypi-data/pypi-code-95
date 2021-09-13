# def makeGenerator(data, labels, batchSize:int):
# 	def mergeFn(x):
# 		Keys = x[0].keys()
# 		data = np.stack([y["data"]["data"] for y in x])
# 		labels = np.stack([y["labels"]["labels"] for y in x])
# 		return {"data":data, "labels":labels}

# 	reader = StaticBatchedReader(MergeBatchedReader(
# 		NWInplaceReader(data, labels), mergeFn=mergeFn), batchSize=batchSize)
# 	return reader.iterate()

import numpy as np
from nwdata.reader import MergeBatchedReader, StaticBatchedReader, NWInplaceReader

def mergeFn(x):
	Keys = x[0].keys()
	data = np.stack([y["data"]["data"] for y in x])
	labels = np.stack([y["labels"]["labels"] for y in x])
	return {"data":data, "labels":labels}

class TestNWInplaceReader:
	def test_constructor_1(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = NWInplaceReader(data, labels)
		assert not reader is None

	def test_getDataset_1(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = NWInplaceReader(data, labels)
		assert np.allclose(reader.getDataset()["data"], data)
		assert np.allclose(reader.getDataset()["labels"], labels)
	
	def test_len_1(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = NWInplaceReader(data, labels)
		assert len(reader) == 10

	def test_getter_1(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = NWInplaceReader(data, labels)
		for i in range(len(reader)):
			assert reader[i]["data"]["data"].shape == data[i].shape
			assert reader[i]["labels"]["labels"].shape == labels[i].shape

	def test_getter_2(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = MergeBatchedReader(NWInplaceReader(data, labels), mergeFn=mergeFn)
		for i in range(len(reader)):
			assert len(reader[i]["data"]) == 1
			assert reader[i]["data"][0].shape == data[i].shape
			assert len(reader[i]["labels"]) == 1
			assert reader[i]["labels"][0].shape == labels[i].shape

	def test_getter_3(self):
		data = np.float32(np.random.randn(10, 20))
		labels = np.float32(np.random.randn(10, 30))
		reader = StaticBatchedReader(MergeBatchedReader(NWInplaceReader(data, labels), mergeFn=mergeFn), 3)
		assert len(reader) == 4
		Lens = [3, 3, 3, 1]
		for i in range(len(reader)):
			assert len(reader[i]["data"]) == Lens[i]
			assert reader[i]["data"][0].shape == data[i].shape
			assert len(reader[i]["labels"]) == Lens[i]
			assert reader[i]["labels"][0].shape == labels[i].shape

def main():
	pass
	# TestNWInplaceReader().test_merge_1()

if __name__ == "__main__":
	main()
