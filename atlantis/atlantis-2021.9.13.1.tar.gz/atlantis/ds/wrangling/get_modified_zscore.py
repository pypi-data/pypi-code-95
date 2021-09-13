from pandas import DataFrame as PandasDF
from pyspark.sql import DataFrame as SparkDF
from pyspark.sql import functions as f
from pyspark.sql.types import FloatType, BooleanType

PERCENTILE75 = 0.6745


def get_modified_zscore(data, column, zscore_column=None, relative_error=1e-6):
	"""

	:type data: PandasDF or SparkDF
	:type column: str
	:type zscore_column: str or NoneType
	:type relative_error: float
	:rtype PandasDF or SparkDF
	"""
	if zscore_column is None:
		zscore_column = f'{column}_zscore'
	if isinstance(data, PandasDF):
		data = data.copy()
		median = data[column].median()
		deviation = data[column] - median
		mad = deviation.abs().median()
		data[zscore_column] = PERCENTILE75 * deviation / mad

	elif isinstance(data, SparkDF):
		median = data.approxQuantile(column, [0.5], relative_error)[0]
		data = data.withColumn(
			'_deviation_', f.col(column) - f.lit(median)
		).withColumn('_abs_deviation_', f.abs('_deviation_'))
		mad = data.approxQuantile('_abs_deviation_', [0.5], relative_error)[0]

		@f.udf(FloatType())
		def _get_modified_zscore(deviation):
			return PERCENTILE75 * deviation / mad

		data = data.withColumn(zscore_column, _get_modified_zscore('_deviation_')).drop(
			'_abs_deviation_', '_deviation_'
		)

	else:
		raise TypeError(f'data of type {type(data)} is not supported!')

	return data


def is_outlier(data, column, is_outlier_column=None, threshold=3.5, relative_error=1e-6):
	"""

	:type data: PandasDF or SparkDF
	:type column: str
	:type is_outlier_column: str or NoneType
	:type threshold: float
	:type relative_error: float
	:rtype PandasDF or SparkDF
	"""
	if is_outlier_column is None:
		is_outlier_column = f'{column}_is_outlier'

	data = get_modified_zscore(data=data, column=column, zscore_column='_zscore_', relative_error=relative_error)
	if isinstance(data, PandasDF):
		data[is_outlier_column] = data['_zscore_'].abs() > threshold
		data = data.drop(columns=['_zscore_'])

	elif isinstance(data, SparkDF):

		@f.udf(BooleanType())
		def _is_outlier(x):
			return abs(x) > threshold

		data = data.withColumn(is_outlier_column, _is_outlier('_zscore_')).drop('_zscore_')

	else:
		raise TypeError(f'data of type {type(data)} is not supported!')

	return data


def remove_outliers(data, column, threshold=3.5, relative_error=1e-6):
	"""
	:type data: PandasDF or SparkDF
	:type column: str
	:type threshold: float
	:type relative_error: float
	:rtype PandasDF or SparkDF
	"""
	data = is_outlier(
		data=data, column=column, is_outlier_column='_is_outlier_', threshold=threshold, relative_error=relative_error
	)

	if isinstance(data, PandasDF):
		return data[~data['_is_outlier_']].drop(columns=['_is_outlier_'])
	elif isinstance(data, SparkDF):
		return data.filter(~f.col('_is_outlier_')).drop('_is_outlier_')
	else:
		raise TypeError(f'data of type {type(data)} is not supported!')
