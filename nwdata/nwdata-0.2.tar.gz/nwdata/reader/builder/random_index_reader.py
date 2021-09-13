import numpy as np
from overrides import overrides
from .builder_reader import BuilderReader
from ..reader import Reader

# @brief A composite dataset reader that provides an interface to iterate through a dataset in a randomized way.
class RandomIndexReader(BuilderReader):
	def __init__(self, baseReader:Reader, seed:int=None):
		super().__init__(baseReader)
		np.random.seed(seed)
		self.seed = seed
		self.isCacheable = False
		self.permutation = np.random.permutation(len(baseReader))

	@overrides
	def __getitem__(self, ix):
		ix = self.permutation[ix]
		item = super().__getitem__(ix)
		return item

	@overrides
	def __str__(self) -> str:
		summaryStr = "[RandomIndexReader]"
		summaryStr += "\n - Seed: %s" % self.seed
		summaryStr += "\n %s" % super().__str__()
		return summaryStr