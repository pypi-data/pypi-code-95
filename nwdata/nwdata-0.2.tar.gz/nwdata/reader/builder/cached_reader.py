from __future__ import annotations
import numpy as np
import os
from overrides import overrides
from typing import List, Tuple
from tqdm import trange
from simple_caching import Cache
from .builder_reader import BuilderReader
from ..reader import Reader
from ...utils import deepCheckEqual

class CachedReader(BuilderReader, Reader):
	# @param[in] baseReader The base dataset reader which is used as composite for caching
	# @param[in] cache The PyCache Cache object used for caching purposes
	# @param[in] buildCache Whether to do a pass through the entire dataset once before starting the iteration
	def __init__(self, baseReader:Reader, cache:Cache, buildCache:bool=True):
		super().__init__(baseReader)
		assert baseReader.isCacheable == True, "%s is not cacheable!" % type(baseReader)
		if isinstance(cache, type):
			envVar = "NWDATA_CACHED_DATASET_DIR"
			assert envVar in os.environ, "'%s' not in environment variables." % envVar
			cache = cache("%s/%s" % (os.environ[envVar], baseReader.__cache__()))
		self.cache = cache
		self.buildCache = buildCache

		if self.buildCache:
			self.doBuildCache()

	# They key is simply the index of the dataset. Only datasets that don't manipulate the indexes in a weird away are
	#  cachable. So, doing StaticBatchedDatast on top of a CachedReader will probably yield an error.
	def cacheKey(self, key):
		assert isinstance(key, (int, np.integer)), "Got type: %s" % type(key)
		return str(int(key))

	def buildRegular(self):
		for i in trange(len(self), desc="[CachedReader] Building regular"):
			_ = self.__getitem__(i)

	def buildDirty(self):
		for i in trange(len(self), desc="[CachedReader] Building dirty"):
			item = super().__getitem__(i)
			key = self.cacheKey(i)
			self.cache.set(key, item)

	def doBuildCache(self):
		# Try a random index to see if cache is built at all.
		randomIx = np.random.randint(0, len(self))
		key = self.cacheKey(randomIx)
		if not self.cache.check(key):
			self.buildRegular()
			return

		# Otherwise, check if cache is dirty. 5 iterations _should_ be enough.
		dirty = False
		for i in range(5):
			item = self.__getitem__(randomIx)
			itemGen = self.baseReader[randomIx]
			try:
				item = type(itemGen)(item)
				dirty = dirty or (not deepCheckEqual(item, itemGen))
			except Exception:
				dirty = True

			if dirty:
				break
			randomIx = np.random.randint(0, len(self))
			key = self.cacheKey(randomIx)

		if dirty:
			print("[CachedReader] Cache is dirty. Rebuilding...")
			self.buildDirty()

	@overrides
	def __getitem__(self, ix):
		key = self.cacheKey(ix)
		if self.cache.check(key):
			return self.cache.get(key)
		else:
			item = super().__getitem__(ix)
			self.cache.set(key, item)
			return item

	@overrides
	def __str__(self) -> str:
		summaryStr = "[Cached Dataset Reader]"
		summaryStr += "\n - Cache: %s. Build cache: %s" % (self.cache, self.buildCache)
		summaryStr += "\n %s" % str(self.baseReader)
		return summaryStr
