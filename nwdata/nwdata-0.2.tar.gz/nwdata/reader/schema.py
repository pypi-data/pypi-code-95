from __future__ import annotations
import numpy as np
from typing import Union, Sequence, Dict, List, Callable
from .random_index import RandomIndex
from ..utils import Debug

# Types for Schema
DatasetIndex = Union[int, Sequence[int], np.ndarray, range, RandomIndex]
DimGetterCallable = Callable[[str, DatasetIndex], np.ndarray]
DimTransformCallable = Callable[[str, np.ndarray], np.ndarray]
DataBucketsType = Dict[str, List[str]]
DimGetterType = Dict[str, DimGetterCallable]
DimTransformType = Dict[str, Dict[str, DimTransformCallable]]

# @param[in] dataBuckets A dictionary with all available data bucket names (data, label etc.) and, for each bucket,
#  a list of dimensions (rgb, depth, etc.).
#  Example: {"data":["rgb", "depth"], "labels":["depth", "semantic"]}
# @param[in] dimGetter For each possible dimension defined above, we need to receive a method that tells us how
#  to retrieve a batch of items. Some dimensions may be overlapped in multiple data bucket names, however, they are
#  logically the same information before transforms, so we only read it once and copy in memory if needed.
# @param[in] dimTransform The transformations for each dimension of each topdata bucket name. Some dimensions may
#  overlap and if this happens we duplicate the data to ensure consistency. This may be needed for cases where
#  the same dimension may be required in 2 formats (i.e. position as quaternions as well as unnormalized 6DoF).
class Schema:
	def __init__(self, dataBuckets:DataBucketsType, dimGetter:DimGetterType, dimTransform:DimTransformType):
		from ..utils import flattenList
		self.allDims = list(set(flattenList(dataBuckets.values())))
		self.dataBuckets = dataBuckets
		self.dimGetter = self.sanitizeDimGetter(dimGetter)
		self.dimTransform = self.sanitizeDimTransform(dimTransform)
		# Used for CachedDatasetReader. Update this if the dataset is cachable (thus immutable). This means that, we
		#  enforce the condition that self.getItem(X) will return the same Item(X) from now until the end of the
		#  universe. If this assumption is ever broken, the cache and the _actual_ Item(X) will be different. And we
		#  don't want that.
		self.isCacheable = False

		# Make a reverse mapping D => [dataBucket]. Eg: "rgb" => ["data", "labels"]. Used by reader's __getitem__.
		self.dimToDataBuckets:DataBucketsType = {dim : [] for dim in self.allDims}
		for dim in self.allDims:
			for bucket in self.dataBuckets:
				if dim in self.dataBuckets[bucket]:
					self.dimToDataBuckets[dim].append(bucket)

	def sanitizeDimGetter(self, dimGetter:DimGetterType) -> DimGetterType:
		for key in self.allDims:
			if not key in dimGetter:
				Debug.log(1, "[Schema::sanitizeDimGetter] Key '%s' not provided. Adding default: d[i]." % key)
				dimGetter[key] = lambda d, i:d[i]
		return dimGetter

	def sanitizeDimTransform(self, dimTransform:DimTransformType) -> DimTransformType:
		for key in dimTransform:
			assert key in self.dataBuckets, "Key '%s' not in data buckets: %s" % (key, self.dataBuckets)
			for dim in dimTransform[key]:
				assert dim in self.allDims, "Dim '%s' is not in allDims: %s" % (dim, self.allDims)

		for dataBucket in self.dataBuckets:
			if not dataBucket in dimTransform:
				Debug.log(1, "[Schema::sanitizeDimTransform] Data bucket '%s' not present in dimTransforms." % \
					dataBucket)
				dimTransform[dataBucket] = {}

			for dim in self.dataBuckets[dataBucket]:
				if not dim in dimTransform[dataBucket]:
					Debug.log(1, ("[Schema::sanitizeDimTransform] Dim '%s'=>'%s' not present in " + \
						"dimTransforms. Adding identity.") % (dataBucket, dim))
					dimTransform[dataBucket][dim] = lambda x : x
		return dimTransform

	def __eq__(self, other:Schema) -> bool:
		return self.allDims == other.allDims and self.dataBuckets == other.dataBuckets

	def __str__(self) -> str:
		Str = "[Reader::Schema]"
		Str += "\n - Data buckets: %s"
		Str += "\n - Dim transforms:"
		for bucket in self.dataBuckets:
			X = list(self.dimTransform[bucket].keys())
			Str += "\n    - Bucket: %s" % ",".join(X)
		return Str