from pandas import DataFrame as PandasDF
from pyspark.sql import DataFrame as SparkDF
from pyspark.sql.types import StringType


def get_string_columns(data):
	"""
	:type data: PandasDF or SparkDF
	:rtype: list[str]
	"""
	if isinstance(data, SparkDF):
		return [
			f.name
			for f in data.schema.fields if isinstance(f.dataType, StringType)
		]
	elif isinstance(data, PandasDF):
		return list(data.select_dtypes(exclude=['bool', 'number', 'datetime64', 'datetime']).columns)

	else:
		raise TypeError(f'data of type {type(data)} is not supported!')
