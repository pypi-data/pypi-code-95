from overrides import overrides
from ..reader import Reader
from .builder_reader import BuilderReader

# @brief A composite dataset reader that has a base reader attribute which it can partially use based on the percent
#  defined in the constructor
class PercentReader(BuilderReader):
	def __init__(self, baseReader:Reader, percent:float):
		super().__init__(baseReader)
		assert percent > 0 and percent <= 100
		self.percent = percent
		assert len(self.iterate()) > 0

	@overrides
	def __len__(self):
		N = self.baseReader.__len__()
		return int(N * self.percent / 100)

	@overrides
	def __str__(self) -> str:
		summaryStr = "[PercentReader]"
		summaryStr += "\n - Percent: %2.2f%%" % self.percent
		summaryStr += "\n %s" % super().__str__()
		return summaryStr