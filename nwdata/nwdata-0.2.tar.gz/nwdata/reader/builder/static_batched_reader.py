import numpy as np
from overrides import overrides
from typing import List, Tuple
from .builder_reader import BuilderReader
from ..batched_reader import BatchedReader
from ...utils import batchIndexFromBatchSizes, getBatchLens

class StaticBatchedReader(BuilderReader, BatchedReader):
	def __init__(self, baseReader:BatchedReader, batchSize:int):
		super().__init__(baseReader)
		assert batchSize == -1 or batchSize > 0
		assert baseReader.isBatched
		self.batchSize = batchSize
		self.staticBatches = None
		self.batches = None

		self.setBatches(self.staticBatchFn())
		self.isCacheable = True
		self.isBatched = True

	def setBatches(self, batches:List[int]):
		self.batches = batches

	def getBatches(self) -> List[int]:
		return self.batches

	def unbatchedLen(self) -> int:
		return sum(getBatchLens(self.batches))

	# @param[in] batchSize The static batch size required to iterate one epoch. If the batch size is not divisible by
	#  the number of items, the last batch will trimmed accordingly. If the provided value is -1, it is set to the
	#  default value of the entire dataset, based on self.getNumData()
	def staticBatchFn(self):
		N = self.baseReader.unbatchedLen()
		B = self.batchSize
		n = N // B + (N % B != 0)
		batchLens = n * [B]
		batchLens[-1] -= n * B - N
		return batchIndexFromBatchSizes(batchLens)

	def __getitem__(self, ix):
		if isinstance(ix, (int, np.integer)):
			batchIndex = self.batches[ix]
			return super().__getitem__(batchIndex)
		else:
			return super().__getitem__(ix)

	@overrides
	def __len__(self):
		if self.staticBatches is None:
			self.staticBatches = self.staticBatchFn()
		return len(self.staticBatches)

	@overrides
	def __str__(self) -> str:
		summaryStr = "[Static Batched Dataset]"
		summaryStr += "\n %s" % super().__str__()
		summaryStr += "\n - Static batch size: %d" % self.batchSize
		return summaryStr
