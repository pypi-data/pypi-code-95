from __future__ import annotations
import numpy as np
from overrides import overrides
from abc import abstractmethod
from typing import List
from .reader import Reader
from ..utils import getBatchLens

class BatchedReader(Reader):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.isBatched = True
		self.batches = None

	def setBatches(self, batches:List[int]):
		self.batches = batches

	@abstractmethod
	def getBatches(self) -> List[int]:
		pass

	def unbatchedLen(self) -> int:
		return sum(getBatchLens(self.getBatches()))

	# @brief This can receive either an iterable or an integer. If it's an integer (i.e. reader[2]) then we'll get the
	#  3rd batch. If it's an iterable (i.e. slice, range, tuple, array), then we'll call the dataset's __getitem__.
	# If you really want the 0th element... don't create a batched dataset (or use slice(0, 1), I guess).
	def __getitem__(self, ix):
		if isinstance(ix, (int, np.integer)):
			batchIndex = self.getBatches()[ix]
			return super().__getitem__(batchIndex)
		else:
			return super().__getitem__(ix)

	@overrides
	def __len__(self) -> int:
		batches = self.getBatches()
		return len(batches)

	@overrides
	def __str__(self) -> str:
		summaryStr = "[Batched Reader]"
		summaryStr += "\n - Type: %s" % type(self)
		summaryStr += "\n - Data buckets:"
		for dataBucket in self.datasetFormat.dataBuckets:
			summaryStr += "\n   - %s => %s" % (dataBucket, self.datasetFormat.dataBuckets[dataBucket])
		try:
			batches = self.getBatches()
			numBatches = len(batches)
		except Exception:
			numBatches = "Not implemented"
		numData = self.unbatchedLen()
		summaryStr += "\n - Num data: %s. Num batches: %s." % (numData, numBatches)
		return summaryStr
