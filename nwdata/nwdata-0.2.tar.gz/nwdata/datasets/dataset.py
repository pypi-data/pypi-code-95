from abc import abstractmethod
from ..reader import Reader

class Dataset(Reader):
	@staticmethod
	@abstractmethod
	def processRawData(**kwargs):
		pass
