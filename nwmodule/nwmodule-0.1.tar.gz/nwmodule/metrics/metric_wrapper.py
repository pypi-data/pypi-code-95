import numpy as np
from overrides import overrides
from typing import Callable, Dict
from .metric import Metric
from ..utilities import isBaseOf

class MetricWrapper(Metric):
	def __init__(self, wrappedMetric:Callable[[np.ndarray, np.ndarray, Dict], float], direction:str="min"):
		assert not isBaseOf(wrappedMetric, Metric), "No need to wrap as it is already a metric/callback"
		self.wrappedMetric = wrappedMetric
		super().__init__(direction=direction)

	# @brief The main method that must be implemented by a metric
	@overrides
	def __call__(self, results, labels, **kwargs):
		res = self.wrappedMetric(results, labels, **kwargs)
		return res

	def __str__(self):
		return "Metric Wrapper (%s)" % str(self.wrappedMetric)

	def __repr__(self):
		return str(self)