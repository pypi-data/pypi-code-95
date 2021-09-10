from dq_whistler.profiler.column_profiler import ColumnProfiler
from dq_whistler.constraints.number_type import *
from pyspark.sql import DataFrame
import pyspark.sql.functions as f
from typing import Dict, Any
import json


class NumberProfiler(ColumnProfiler):
	"""
	Class for Numeric datatype profiler
	"""

	def __init__(self, column_data: DataFrame, config: Dict[str, str]):
		"""
		Creates an instance of :obj:`NumberProfiler`
		Args:
			column_data (pyspark.sql.DataFrame): Column data as a spark dataframe to execute constraints
			config (Dict[str, Any]): Config containing all the constraints of a column along with expected datatypes
			{
				"name": "col_name",
				"datatype": "col_data_type(number/string/date)",
				"constraints":[
				{
					"name": "gt_eq",
					"values": 5
				},
				{
					"name": "is_in",
					"values": [1, 2]
				}...
				]
			}
		"""
		super(NumberProfiler, self).__init__(column_data, config)

	def get_min_value(self) -> float:
		"""
		Returns:
			:obj:`float`: Min value of the column data
		"""
		min_value = json.loads(self._column_data.select(
			f.min(
				f.col(self._column_name)
					.cast("double")
			).alias("min")
		).toJSON().take(1)[0])["min"]
		return min_value

	def get_max_value(self) -> float:
		"""
		Returns:
			:obj:`float`: Max value of the column data
		"""
		max_value = json.loads(self._column_data.select(
			f.max(
				f.col(self._column_name)
					.cast("double")
			).alias("max")
		).toJSON().take(1)[0])["max"]
		return max_value

	def get_mean_value(self) -> float:
		"""
		Returns:
			:obj:`float`: Mean value of the column data
		"""
		mean_value = json.loads(self._column_data.select(
			f.mean(
				f.col(self._column_name)
					.cast("double")
			).alias("mean")
		).toJSON().take(1)[0])["mean"]
		return mean_value

	def get_stddev_value(self) -> float:
		"""
		Returns:
			:obj:`float`: Standard deviation value of the column value
		"""
		stddev_value = json.loads(self._column_data.select(
			f.stddev(
				f.col(self._column_name)
					.cast("double")
			).alias("stddev")
		).toJSON().take(1)[0])["stddev"]
		return stddev_value

	def run(self) -> Dict[str, Any]:
		"""
		Returns:
			:obj:`Dict[str, Any]`: The final dict with all the metrics of a numeric column
			Example Output::
				{
					"total_count": 100,
					"null_count": 50,
					"unique_count": 20,
					"topn_values": {"1": 24, "2": 25},
					"min": 2.0,
					"max": 30.0,
					"mean": 18.0,
					"stddev": 5.0,
					"quality_score": 0,
					"constraints": [
						{
							"name": "eq",
							"values", 5,
							"constraint_status": "failed/success",
							"invalid_count": 21,
							"invalid_values": [4, 6, 7, 1]
						}
					]
				}
		"""
		column_name = self._column_name
		for constraint in self._config.get("constraints"):
			name = constraint.get("name")
			if name == "eq":
				self.add_constraint(
					Equal(constraint=constraint, column_name=column_name)
				)
			elif name == "not_eq":
				self.add_constraint(
					NotEqual(constraint=constraint, column_name=column_name)
				)
			elif name == "lt":
				self.add_constraint(
					LessThan(constraint=constraint, column_name=column_name)
				)
			elif name == "gt":
				self.add_constraint(
					GreaterThan(constraint=constraint, column_name=column_name)
				)
			elif name == "lt_eq":
				self.add_constraint(
					LessThanEqualTo(constraint=constraint, column_name=column_name)
				)
			elif name == "gt_eq":
				self.add_constraint(
					GreaterThanEqualTo(constraint=constraint, column_name=column_name)
				)
			elif name == "between":
				self.add_constraint(
					Between(constraint=constraint, column_name=column_name)
				)
			elif name == "not_between":
				self.add_constraint(
					NotBetween(constraint=constraint, column_name=column_name)
				)
			elif name == "is_in":
				self.add_constraint(
					IsIn(constraint=constraint, column_name=column_name)
				)
			elif name == "not_in":
				self.add_constraint(
					NotIn(constraint=constraint, column_name=column_name)
				)
			else:
				raise NotImplementedError
		# Preparing data frame for constraints execution
		self.prepare_df_for_constraints()
		# Get final output of constraints
		output = self.get_custom_constraint_check()
		return {
			"total_count": self.get_total_count(),
			"null_count": self.get_null_count(),
			"unique_count": self.get_unique_count(),
			"topn_values": self.get_topn(),
			"min": self.get_min_value(),
			"max": self.get_max_value(),
			"mean": self.get_mean_value(),
			"stddev": self.get_stddev_value(),
			"quality_score": self.get_quality_score(),
			"constraints": output
		}
