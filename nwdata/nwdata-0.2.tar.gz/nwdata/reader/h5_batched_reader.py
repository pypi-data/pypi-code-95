# H5 Batched Dataset Reader. By default H5 datasets are batched datasets, but we can make more asusmptions about it
#  based on the stored dataset. We can use a default dim getter (instead of providing one manually) that reads a batch
#  of data from the h5 file. We can also know ahead of time the number of data, so we don't need to provide this
#  information at all. Basically, all we need to do is to make a exporter file that will put the data in h5 form and
#  provide a good enough dataBuckets/dimTransform combination and this reader will take care of the rest.
# See mnist exporter/reader for this.
import h5py
from pathlib import Path
from overrides import overrides
from returns.curry import partial
from typing import Union
from .batched_reader import BatchedReader
from ..utils import defaultH5DimGetter, flattenList

class H5BatchedReader(BatchedReader):
	# @param[in] datasetPath can be a dataset or a h5py opened file/group etc. If it's str, we're opening it.
	def __init__(self, datasetPath:Union[str, Path, h5py._hl.files.File], dataBuckets, dimGetter={}, dimTransform={}):
		if isinstance(datasetPath, (Path, str)):
			self.datasetPath = datasetPath
			self.dataset = h5py.File(self.datasetPath, "r")
		elif isinstance(datasetPath, h5py._hl.files.File):
			# Assume h5 or h5 group or such. Either way, we can use the file attribute of h5py to get the h5py.File
			#  object, which has a filename attribute to get the original h5py file path.
			self.dataset = datasetPath
			self.datasetPath = self.dataset.file.filename
		else:
			assert False

		allDims = list(set(flattenList(dataBuckets.values())))
		# H5 assumption. If diGetter is not provided, assume the default getter. However, if provided, then perhaps
		#  that particular dimension is read somehow different (or is computed from another raw dimension).
		for key in allDims:
			# breakpoint()
			if not key in dimGetter:
				assert key in self.dataset, "Key %s vs %s" % (key, self.dataset.keys())
				dimGetter[key] = partial(defaultH5DimGetter, dim=key)
				print("[H5BatchedReader] Dim '%s' has no dim getter. Adding the default h5 dim getter." % key)

		# Some weird shit going on, error sometimes when we get some previous (?) dimGetters in pytest.
		dimGetter = {k : dimGetter[k] for k in filter(lambda x : x in allDims, dimGetter.keys())}
		super().__init__(dataBuckets, dimGetter, dimTransform)

	@overrides
	def getDataset(self):
		return self.dataset

	@overrides
	def __str__(self) -> str:
		summaryStr = "[H5 Batched Dataset Reader]"
		summaryStr += "\n - Path: %s" % self.datasetPath
		summaryStr += "\n %s" % super().__str__()
		return summaryStr
