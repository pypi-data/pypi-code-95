from overrides import overrides
from ..reader import Reader
from ..batched_reader import BatchedReader

class BuilderReader(Reader):
	def __init__(self, baseReader:Reader):
		assert isinstance(baseReader, Reader)
		super().__init__(dataBuckets=baseReader.datasetFormat.dataBuckets, \
			dimGetter=baseReader.datasetFormat.dimGetter, dimTransform=baseReader.datasetFormat.dimTransform)
		for k, v in baseReader.__dict__.items():
			setattr(self, k, v)
		# Important to put this here, as otherwise it'd cycle to the root baseReader when pipelining multiple readers
		self.baseReader = baseReader

	@overrides
	def __getitem__(self, ix):
		return self.baseReader.__getitem__(ix)

	@overrides
	def __len__(self):
		return len(self.baseReader)

	@overrides
	def getDataset(self):
		return self.baseReader.getDataset()

	@overrides
	def __cache__(self):
		return self.baseReader.__cache__()

	def unbatchedLen(self):
		if isinstance(self.baseReader, BatchedDataset):
			return self.baseReader.unbatchedLen()
		return len(self.baseReader)
