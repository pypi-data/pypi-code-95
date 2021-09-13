# Helper class that takes a non-batched dataset reader and makes it batched, by merging multiple items via a merging
#  function that is provided by the user.
from __future__ import annotations
import numpy as np
from overrides import overrides
from abc import abstractmethod
from collections.abc import Iterable
from typing import Tuple, List, Callable, Any
from .builder_reader import BuilderReader
from ..reader import Reader
from ..batched_reader import BatchedReader
from ...utils import getBatchLens, getBatchesAsIndices, Debug

MergeFnType = Callable[[List[Any]], Any]
BatchesFnType = Callable[[List[Any]], Any]

def defaultMergeFn(x:List[Dict]) -> Dict:
	Keys = list(x[0].keys())
	N = len(x)

	res = {k : {j:[x[0][k][j]] for j in x[0][k]} for k in Keys}
	for i in range(1, N):
		for k in res:
			for k2 in res[k]:
				a = res[k][k2]
				b = [x[i][k][k2]]
				res[k][k2] = np.concatenate([a, b], axis=0)
	return res

# Converts a non-batched dataset into a batched dataset by providing a merging function for the unbatched elements.
class MergeBatchedReader(BuilderReader, BatchedReader):
	def __init__(self, baseReader:Reader, mergeFn:MergeFnType=None, batchesFn:BatchesFnType=None):
		assert not baseReader.isBatched, "[MergeBatchedReader] Already a batched dataset, sir!"
		super().__init__(baseReader)

		if batchesFn is None:
			Debug.log(1, "[MergeBatchedDataset] No batchesFn provided. Setting default (one by one item).")
			batchesFn = lambda : np.arange(len(baseReader)).reshape(-1, 1)

		if mergeFn is None:
			Debug.log(1, "[MergeBatchedDataset] No mergeFn provided. Setting to default (merging list of dicts)")
			mergeFn = defaultMergeFn

		self.mergeFn = mergeFn
		self.batchesFn = batchesFn
		
		assert sum(getBatchLens(self.getBatches())) == len(self.baseReader)
		X = getBatchesAsIndices(self.getBatches()).flatten()
		try:
			assert (np.sort(X) != np.arange(len(self.baseReader))).sum() == 0, \
				"The provided batch indices must iterate through the entire dataset!"
		except Exception:
			breakpoint()
		self.isBatched = True

	def setBatches(self, batches:List[int]):
		self.batches = batches

	@overrides
	def getBatches(self) -> List[int]:
		if self.batches is None:
			self.setBatches(self.batchesFn())
		return self.batches

	def unbatchedLen(self) -> int:
		return len(self.baseReader)

	def __len__(self):
		return len(self.getBatches())

	@overrides
	# Similarily to how BatcheDataset works, if we get an index n as integer, we'll receive the nth batch. However, if
	#  we get an iterable (slice, range, list etc.), we'll call the base unbatched dataset on this special index and
	#  apply the merging function on top of it.
	def __getitem__(self, ix):
		if isinstance(ix, (int, np.integer)):
			ix = self.getBatches()[ix]
		if isinstance(ix, slice):
			ix = np.arange(ix.start, ix.stop)
		
		assert not isinstance(ix, (int, np.integer))
		assert isinstance(ix, Iterable), "Got type: %s" % type(ix)

		listItems = [self.baseReader.__getitem__(j) for j in ix]
		items = self.mergeFn(listItems)
		return items

	def __str__(self) -> str:
		summaryStr = "[MergeBatchedReader]"
		summaryStr += "\n %s" % str(self.baseReader)
		return summaryStr

