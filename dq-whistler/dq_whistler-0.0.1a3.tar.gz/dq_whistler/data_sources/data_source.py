import enum
from typing import Any, Callable, Dict, Iterable, Optional, Tuple
from abc import ABC, abstractmethod


class SourceType(enum.Enum):
	"""
	DataSource type. Used to define source type
	"""
	FILE_BASED = 0
	BIGQUERY = 1


class DataSourceOptions(ABC):
	"""
	Base abstract class for defining options for a data source
	Args:
		source_options: Dict resources for all source related options
	"""

	_source_options: Dict[str, str]

	def __init__(
			self,
			source_options: Dict[str, str],
	):
		self._source_options = source_options

	@property
	def get_source_details(self):
		return self._source_options


class DataSource(ABC):
	"""
	Base abstract class for defining DataSource
	Args:
		quality_config (optional): Dict resources map for column level checks
	"""

	_quality_config: Dict[str, str]

	def __init__(
			self,
			quality_config: Optional[str] = None,
	):
		"""Create a datasource object"""
		self._quality_config = quality_config if quality_config else dict()

	def __eq__(self, other):
		if not isinstance(other, DataSource):
			raise TypeError("Comparison possible only for DataSource objects")

		if (
			self._quality_config != other._quality_config
		):
			return False
		return True

	@property
	def quality_config(self) -> Dict[str, str]:
		"""Returns the quality resources for this datasource"""
		return self._quality_config

	@quality_config.setter
	def quality_config(self, quality_config):
		"""Setting up the quality resources for this datasource"""
		self._quality_config = quality_config

	@abstractmethod
	def read(self):
		pass

	@abstractmethod
	def run_quality_checks(self):
		pass

