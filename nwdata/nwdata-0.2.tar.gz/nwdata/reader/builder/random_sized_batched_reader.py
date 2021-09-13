from __future__ import annotations
import numpy as np
from overrides import overrides
from typing import List, Tuple
from .builder_reader import BuilderReader
from ..batched_reader import BatchedReader
from ...utils import batchIndexFromBatchSizes, getBatchLens

class RandomSizedBatchedReader(BuilderReader):
	def __init__(self, baseReader:BatchedReader, seed:int=42):
		super().__init__(baseReader)
		assert baseReader.isBatched

		self.seed = seed
		self.batches = None
		self.setBatches(self.getShuffle())
		self.isCacheable = True
		self.isBatched = True

	def setBatches(self, batches:List[int]):
		self.batches = batches

	def getBatches(self) -> List[int]:
		return self.batches

	def unbatchedLen(self) -> int:
		return sum(getBatchLens(self.batches))

	def getShuffle(self):
		np.random.seed(self.seed)
		N = self.baseReader.unbatchedLen()
		S = 0
		batchLens = []
		while S < N:
			nLeft = N - S
			thisLen = np.random.randint(1, nLeft + 1)
			S += thisLen
			batchLens.append(thisLen)
		assert sum(batchLens) == N
		batches = batchIndexFromBatchSizes(batchLens)
		return batches

	def __len__(self):
		return len(self.batches)

	def __getitem__(self, ix):
		if isinstance(ix, (int, np.integer)):
			batchIndex = self.batches[ix]
			return super().__getitem__(batchIndex)
		else:
			return super().__getitem__(ix)

	@overrides
	def __str__(self) -> str:
		summaryStr = "[Random Sized Batched Reader]"
		summaryStr += "\n %s" % super().__str__()
		summaryStr += "\n Num batches: %d. Seed: %d" % (len(self.batches), self.seed)
		return summaryStr
