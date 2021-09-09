from pyspark.sql import DataFrame
from pyspark.sql import functions as f
from pyspark.ml.functions import vector_to_array
from pyspark.sql.types import FloatType


def disassemble(data, column, names=None, prefix=None, drop=True):
	"""
	disassembles a column of vectors into multiple columns
	:type data: DataFrame
	:type column: str
	:type names: NoneType or list[str]
	:param names: names of new columns, if not provided the prefix or column will be used
	:type prefix: NoneType or str
	:param prefix: a prefix to be used instead of names when names is not provided
	for example, if prefix='feature_' the new columns will be 'feature_1', 'feature_2', etc.
	if prefix is not provided either, the column name will be used with an underscore after
	:type drop: bool
	:param drop: if True, the original column of vectors will be dropped
	:rtype: DataFrame
	"""
	original_columns = data.columns
	if drop:
		original_columns = [col for col in original_columns if col != column]
	disassembled = data.withColumn('_array_', vector_to_array(column))
	length = len(disassembled.first()['_array_'])
	if names is None:
		if prefix is None:
			prefix = f'{column}_'
		names = [f'{prefix}{i}' for i in range(1, length + 1)]
	else:
		if len(names) != length:
			raise ValueError(f'names should be of size {length}')

	@f.udf(FloatType())
	def _get_item(array, i):
		return array[i]

	return disassembled.select(
		*original_columns,
		*[_get_item('_array_', f.lit(i)).alias(name) for i, name in enumerate(names)]
	)
