from pyspark.sql import DataFrame
from pyspark.ml.feature import VectorAssembler, PCA as SparkPCA
from ..testing import assert_has_columns
from .Scaler import Scaler
from .disassemble import disassemble


_PCA_STATE = [
	'_columns', '_scale', '_assembler', '_k', '_scaler', '_scale_with_means', '_scale_with_sd', '_fitted',
	'_pca_columns'
]


class PCA:
	def __init__(self, k=None, columns=None, scale=False, scale_with_means=True, scale_with_sd=True):
		"""

		:type k: int or NoneType
		:type columns: NoneType or list[str]
		:type scale: bool
		:type scale_with_means: bool
		:type scale_with_sd: bool
		"""
		self._columns = columns
		self._scale = scale
		self._assembler = None
		self._k = k

		self._scaler = None
		self._scale_with_means = scale_with_means
		self._scale_with_sd = scale_with_sd

		self._pca = None
		self._fitted = False
		self._pca_columns = None

	def __getstate__(self):
		return {
			name: getattr(self, name)
			for name in _PCA_STATE
		}

	def __setstate__(self, state):
		for name, value in state.items():
			setattr(self, name, value)

	def fit(self, X):
		"""
		:type X: DataFrame
		:rtype: PCA
		"""
		if self._columns is None:
			self._columns = X.columns
		else:
			assert_has_columns(X, columns=self._columns)

		if self._scale:
			self._scaler = Scaler(columns=self._columns, with_mean=self._scale_with_means, with_sd=self._scale_with_sd)
			scaled = self._scaler.fit_transform(X=X, return_vector=True)
			self._pca = SparkPCA(k=self._k, inputCol='scaled_features', outputCol='pca_features').fit(scaled)

		else:
			self._assembler = VectorAssembler(inputCols=self._columns, outputCol='features')
			assembled = self._assembler.transform(X).select('features')
			self._pca = SparkPCA(k=self._k, inputCol='features', outputCol='pca_features').fit(assembled)

		self._fitted = True
		return self

	def transform(self, X, return_vector=False):
		"""
		:type X: DataFrame
		:type return_vector: bool
		:param return_vector: True: the vector column will be returned. False: the vector column will be disassembled.
		:rtype: DataFrame
		"""
		if not self._fitted:
			self.fit(X=X)

		assert_has_columns(X, self._columns)

		if self._scale:
			scaled = self._scaler.transform(X=X, return_vector=True)
		else:
			scaled = self._assembler.transform(X).select(
				'features', *[col for col in X.columns if col not in self._columns]
			)

		transformed = self._pca.transform(scaled).drop('features', 'scaled_features')
		if return_vector:
			return transformed

		else:
			self._pca_columns = [f'pca_{i}' for i in range(1, self._k + 1)]
			return disassemble(transformed, column='pca_features', names=self._pca_columns, drop=True)

	fit_transform = transform

	@property
	def variance_ratios(self):
		"""
		:rtype: list[float]
		"""
		return list(self._pca.explainedVariance.toArray())

	@property
	def pca_columns(self):
		"""
		:rtype: list[str]
		"""
		return self._pca_columns

	@property
	def variance_ratio_by_column(self):
		"""
		:rtype: dict[str, float]
		"""
		variance_ratios = self.variance_ratios
		pca_columns = self.pca_columns
		if len(variance_ratios) != len(pca_columns):
			raise RuntimeError(f'There are {len(variance_ratios)} variance ratios for {len(pca_columns)} columns!')

		return {column: variance_ratio for column, variance_ratio in zip(pca_columns, variance_ratios)}
