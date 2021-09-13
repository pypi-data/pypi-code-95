from .reader import Reader

# Iterator that iterates one epoch over this dataset.
# @brief Epoch iterator that goes through the provided dataset reader for exactly one epoch as defined by len(reader)
# @param[in] reader The Reader we are iterating one epoch upon
class EpochIterator:
	def __init__(self, reader:Reader):
		self.reader = reader
		self.ix = -1

	def __len__(self):
		# assert not self.len is None, "Must be set before calling iterate()/iterateOneEpoch()"
		return len(self.reader)

	def __getitem__(self, ix):
		return self.reader[ix]

	# The logic of getting an item is. ix is a number going in range [0 : len(self) - 1]. Then, we call dataset's
	#  __getitem__ on this. So item = self[index], where __getitem__(ix) = self.reader[ix].
	# One-liner: items = self[ix] for ix in [0 : len(self) - 1]
	def __next__(self):
		self.ix += 1
		if self.ix < len(self):
			return self.__getitem__(self.ix)
		raise StopIteration

	def __iter__(self):
		return self
