from typing import Sequence

# @brief Internal class used for indexing with random "iterators" that preserve shapes:
#  [[1, 10], [2], [1, 2, [3, 5]]] shall return the values at those indices for this shape
class RandomIndex:
	def __init__(self, sequence:Sequence):
		self.sequence = sequence

	def __str__(self):
		return "DatasetRandomIndex: %s" % (str(self.sequence))
