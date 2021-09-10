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
					"values": 5
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
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint,
			for ex: if constraint is ``eq`` to ``5``, then the dataframe will have rows where
			values are ``!= 5`` (i.e only invalid cases)
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
					"values": 5
				}
		column_name (str): The name of the column for constraint check
	"""

	def __init__(self, constraint: Dict[str, str], column_name: str):
		super().__init__(constraint, column_name)

	def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
		"""
		Args:
			data_frame (:obj:`pyspark.sql.DataFrame`): The column data as spark dataframe

		Returns:
			:obj:`pyspark.sql.DataFrame`: The dataframe with ``invalid cases`` as per the constraint
			for ex: if constraint is ``nt_eq`` to ``5``, then the dataframe will have rows where
			values are ``= 5`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) == self._values
		)


class LessThan(Constraint):
	"""
	LessThan constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"lt",
					"values": 5
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
			for ex: if constraint is ``lt`` ``5``, then the dataframe will have rows where values
			are ``>= 5`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) >= self._values
		)


class GreaterThan(Constraint):
	"""
	GreaterThan constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"gt",
					"values": 5
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
			for ex: if constraint is ``gt`` ``5``, then the dataframe will have rows where values
			are ``<= 5`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) <= self._values
		)


class LessThanEqualTo(Constraint):
	"""
	LessThanEqualTo constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"lt_eq",
					"values": 5
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
			for ex: if constraint is ``lt_eq`` to ``5``, then the dataframe will have rows where
			the values are ``> 5`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) > self._values
		)


class GreaterThanEqualTo(Constraint):
	"""
	GreaterThanEqualTo constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"gt_eq",
					"values": 5
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
			for ex: if constraint is ``gt_eq`` to ``5``, then the dataframe will have rows where
			values are ``< 5`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name) < self._values
		)


class Between(Constraint):
	"""
	Between constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"between",
					"values": [3, 4]
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
			for ex: if constraint is ``between`` ``[2, 8]``, then the dataframe will have rows
			where values are ``not in between [2, 8]`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			~f.col(self._column_name).between(*self._values)
		)


class NotBetween(Constraint):
	"""
	NotBetween constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"not_between",
					"values": [3, 5]
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
			for ex: if constraint is ``not_between`` ``[2,8]``, then the dataframe will have rows
			where values ``are in between [2, 8]`` (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).between(*self._values)
		)


class IsIn(Constraint):
	"""
	IsIn constraint class that extends the base Constraint class

	Args:
		constraint (:obj:`Dict[str, str]`): The dict representing a constraint config
			::
				{
					"name":"is_in",
					"values": [1, 2, 3]
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
			for ex: if constraint is ``is_in`` ``[1, 2, 3]``, then the dataframe will have rows where
			values ``are in [1, 2, 3]`` (i.e only invalid cases)
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
					"values": [1, 2, 3]
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
			:obj:`pyspark.sql.DataFrame`: The dataframe with invalid cases as per the constraint
			for ex: if constraint is "not_in" [1, 2, 3], then the dataframe will have rows where
			values are in [1, 2, 3] (i.e only invalid cases)
		"""
		return data_frame.filter(
			f.col(self._column_name).isin(self._values)
		)
