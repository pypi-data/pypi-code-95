from dq_whistler.constraints.constraint import Constraint
from typing import Dict
from pyspark.sql import DataFrame
import pyspark.sql.functions as f


class Equal(Constraint):
	"""
	Equal constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"eq",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``eq`` to ``"abc"``, then the dataframe will have rows where
			values are ``!= "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) != self._values
		)


class NotEqual(Constraint):
	"""
	NotEqual constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"nt_eq",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``nt_eq`` to ``"abc"``, then the dataframe will have rows where
			values are ``== "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) == self._values
		)


class Contains(Constraint):
	"""
	Contains constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"contains",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``contains`` ``"abc"``, then the dataframe will have rows where
			values ``does not contains "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).contains(self._values)
		)


class NotContains(Constraint):
	"""
	NotContains constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"not_contains",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``not_contains`` ``abc``, then the dataframe will have rows where
			values ``contains "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).contains(self._values)
		)


class StartsWith(Constraint):
	"""
	StartsWith constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"starts_with",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``starts_with`` ``"abc"``, then the dataframe will have rows where
			values ``does not starts with "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).startswith(self._values)
		)


class NotStartsWith(Constraint):
	"""
	NotStartsWith constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"not_starts_with",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``not_starts_with`` ``"abc"``, then the dataframe will have rows where
			values ``starts with "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).startswith(self._values)
		)


class EndsWith(Constraint):
	"""
	EndsWith constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"ends_with",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``ends_with`` ``"abc"``, then the dataframe will have rows where
			values ``does not ends with "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).endswith(self._values)
		)


class NotEndsWith(Constraint):
	"""
	NotEndsWith constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"not_ends_with",
					"values": "abc"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``not_ends_with`` ``"abc"``, then the dataframe will have rows where
			values ``ends with "abc"`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).endswith(self._values)
		)


class IsIn(Constraint):
	"""
	IsIn constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"is_in",
					"values": ["abc", "xyz"]
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``is_in`` ``["abc", "xyz"]``, then the dataframe will have rows where
			values ``are not in ["abc", "xyz"]`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).isin(*self._values)
		)


class NotIn(Constraint):
	"""
	NotIn constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"not_in",
					"values": ["abc", "xyz"]
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``not_in`` ``["abc", "xyz"]``, then the dataframe will have rows where
			values ``are in ["abc", "xyz"]`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).isin(self._values)
		)


class Regex(Constraint):
	"""
	Regex constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"regex",
					"values": "^[A-Za-z]$"
				}
		column_name (:obj:`str`): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``regex`` ``^[A-Za-z]$``, then the dataframe will have rows where
			values ``does not`` satisfies the regex ``^[A-Za-z]$`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).rlike(self._values)
		)
