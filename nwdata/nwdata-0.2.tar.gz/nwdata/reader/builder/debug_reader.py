from overrides import overrides
from .builder_reader import BuilderReader
from ..reader import Reader

class DebugReader(BuilderReader):
	def __init__(self, reader:Reader, N:int):
		assert N <= len(reader)
		self.N = N
		super().__init__(reader)

	def __len__(self):
		return self.N

	@overrides
	def __cache__(self):
		Key = super().__cache__()
		return "%s-DebugLen%d" % (Key, self.N)

	def __str__(self):
		Str = "[DebugReader]"
		Str += "\n %s" % super().__str__()
		Str += "\n - N: %d" % self.N
		return Str
