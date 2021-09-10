from pyspark.sql import DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import StringType
from memoria import smart_hash


class NullReplacer:
	def __init__(self):
		self._mappers = {}

	@staticmethod
	def _get_null_replaced_column_name(column_name):
		if column_name.startswith('_') and column_name.endswith('_null_replaced_'):
			raise ValueError(f'"{column_name}" matches the null replaced column name pattern!')
		return f'_{column_name}_null_replaced_'

	@staticmethod
	def _get_column_name(null_replaced_column_name):
		if null_replaced_column_name.startswith('_') and null_replaced_column_name.endswith('_null_replaced_'):
			return null_replaced_column_name[1:-len('_null_replaced_')]
		else:
			raise ValueError(f'"{null_replaced_column_name}" does not match the null replaced column name pattern!')

	def transform(self, X, columns=None):
		"""
		:param X: dataframe to be fixed
		:param columns: list of columns to be fixed by replacing nulls
		:type X: DataFrame
		:type columns: list[str]
		:rtype: DataFrame
		"""
		if columns is None:
			columns = X.columns

		@f.udf(StringType())
		def _hash(x):
			return smart_hash(x)

		result = X.select(
			*X.columns,
			*[_hash(column).alias(self._get_null_replaced_column_name(column)) for column in columns]
		)

		non_converted_columns = [col for col in X.columns if col not in columns]

		for col in columns:
			new_mapper = result.select(col, self._get_null_replaced_column_name(col)).distinct()
			if col not in self._mappers:
				self._mappers[col] = new_mapper
			else:
				self._mappers[col] = new_mapper.union(self._mappers[col]).distinct()

		return result.select(
			*non_converted_columns,
			*[f.col(self._get_null_replaced_column_name(col)).alias(col) for col in columns]
		)

	def revert(self, X):
		"""
		:type X: DataFrame
		:rtype: DataFrame
		"""
		result = X
		for col, mapper in self._mappers.items():
			if col in X.columns:
				null_replaced_column = self._get_null_replaced_column_name(col)
				result = result.withColumnRenamed(col, null_replaced_column).join(
					mapper, on=null_replaced_column, how='inner'
				).drop(null_replaced_column)
		return result
