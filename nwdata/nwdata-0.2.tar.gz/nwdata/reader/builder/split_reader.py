import numpy as np
from overrides import overrides
from collections.abc import Iterable
from typing import List, Dict, Union
from .builder_reader import BuilderReader
from ..reader import Reader

class SubDataset(BuilderReader):
	def __init__(self, baseReader:Reader, indexes:List[int]):
		super().__init__(baseReader)
		assert len(indexes) > 0
		self.indexes = indexes

	def __getitem__(self, ix):
		ix = self.indexes[ix]
		return self.baseReader.__getitem__(ix)

	def __len__(self):
		return len(self.indexes)

	# We can compute this bsased on the percentage of indexes compared to base reader's len / unbatched len
	def unbatchedLen(self):
		rapp = len(self.indexes) / len(self.baseReader)
		value = int(rapp * self.baseReader.unbatchedLen())
		return value

# Split one dataset into multiple (potentially overlapping) subdatasets
class SplitReader(BuilderReader):
	def __init__(self, baseReader:Reader, splits:Dict[str, Iterable]):
		super().__init__(baseReader)
		self.splits = splits
		indexes = self.getSplitIndexes(splits)
		self.datasets = {k : SubDataset(baseReader, indexes[k]) for k in splits}

	def __getitem__(self, ix:Union[str, List[str]]):
		if isinstance(ix, str):
			return self.datasets[ix]
		elif isinstance(ix, List):
			return [self.datasets[k] for k in ix]
		else:
			assert False, "Expected str or list of str. Got: %s" % ix

	# Gets the actual indexes of the original dataset so we can iterate properly
	def getSplitIndexes(self, splits:Dict[str, Iterable]) -> Dict[str, Iterable]:
		res = {}
		for split in splits:
			indexes = splits[split]
			if isinstance(indexes, (tuple, list, np.ndarray)):
				if len(indexes) == 2 and (isinstance(indexes[0], float) or isinstance(indexes[1], float)):
					start, end = indexes
					assert start < end and start >= 0 and end <= 1
					ixStart = int(start * len(self.baseReader))
					ixEnd = int(end * len(self.baseReader))
					res[split] = [x for x in range(ixStart, ixEnd)]
				else:
					for ix in indexes:
						assert isinstance(ix, int)
					res[split] = indexes
			elif isinstance(indexes, range):
				res[split] = [x for x in indexes]
			else:
				assert False, "Unknown type: %s" % type(indexes)
			
			for ix in res[split]:
				assert ix >= 0 and ix < len(self.baseReader), "%s: %d vs len==%d" % (split, ix, len(self.baseReader))
		return res

	def iterate(self):
		assert False

	def iterateOneEpoch(self):
		assert False