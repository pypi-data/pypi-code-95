from pyspark.sql.functions import array, col, explode, lit
from pyspark.sql.functions import create_map
from pyspark.sql import DataFrame as SparkDF
from pandas import DataFrame as PandasDF
from typing import Iterable
from itertools import chain


def melt(data, id_columns, value_columns, variable_name='variable', value_name='value'):
	"""
	converts a DataFrame from wide to long format
	:type data: SparkDF or PandasDF
	:type id_columns: str or list[str]
	:type value_columns: str or list[str]
	:type variable_name: str
	:type value_name: str
	:rtype: SparkDF or PandasDF
	"""
