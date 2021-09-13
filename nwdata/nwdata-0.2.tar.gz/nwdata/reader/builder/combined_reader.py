import numpy as np
from overrides import overrides
from typing import List
from .builder_reader import BuilderReader
from ..reader import Reader

class CombinedReader(BuilderReader):
	def __init__(self, baseReaders:List[Reader]):
		# super().__init__(baseReader)
		assert len(baseReaders) > 1, "Must provide a list of Readers!"
		firstReader = baseReaders[0]
		assert isinstance(firstReader, Reader)
		for reader in baseReaders[1 : ]:
			assert isinstance(reader, Reader)
			assert reader.datasetFormat == firstReader.datasetFormat, "All readers must provide same ReaderFormat!"

		Reader.__init__(self, dataBuckets=firstReader.datasetFormat.dataBuckets, \
			dimGetter=firstReader.datasetFormat.dimGetter, dimTransform=firstReader.datasetFormat.dimTransform)
		self.baseReaders = [reader for reader in baseReaders]
		self.baseReader = self.baseReaders
		self.Mappings = self.getMappings()

	def getMappings(self):
		Mappings = np.zeros((len(self), 2), dtype=np.uint32)
		ix = 0
		for i in range(len(self.baseReaders)):
			n = len(self.baseReaders[i])
			Range = np.arange(n)
			Mappings[ix : ix + n, 0] = np.repeat([i], n)
			Mappings[ix : ix + n, 1] = Range
			ix += n
		return Mappings

	@overrides
	def __getitem__(self, ix):
		# TODO: Slices are.. hard for now
		assert isinstance(ix, (int, np.integer))
		readerIx, readerInnerIx = self.Mappings[ix]
		return self.baseReaders[readerIx].__getitem__(readerInnerIx)

	def __getattr__(self, key):
		assert False
		# X = [getattr(baseIterator, key) for baseIterator in self.baseIterators]
		# return X

	@overrides
	def __len__(self):
		return sum([len(reader) for reader in self.baseReaders])

	@overrides
	def __str__(self) -> str:
		summaryStr = "[CombinedReader]"
		summaryStr += "\n - Num datasets: %d" % (len(self.baseReaders))
		for i, reader in enumerate(self.baseReaders):
			summaryStr += "\n----------- %d -----------" % (i + 1)
			summaryStr += "\n%s" % str(reader)
		return summaryStr