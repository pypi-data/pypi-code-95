from dq_whistler.profiler.column_profiler import ColumnProfiler
from dq_whistler.constraints.string_type import *
from pyspark.sql import DataFrame
from typing import Dict, Any


class StringProfiler(ColumnProfiler):
	"""
	Class for String datatype profiler
	"""

	def __init__(self, column_data: DataFrame, config: Dict[str, str]):
		"""
		Creates an instance of Column Profiler
		Args:
			column_data (pyspark.sql.DataFrame): Column data as a spark dataframe to execute constraints
			config (Dict[str, Any]): Config containing all the constraints of a column along with expected datatypes
			{
				"name": "col_name",
				"datatype": "col_data_type(number/string/date)",
				"constraints":[
				{
					"name": "contains",
					"values": "abc"
				},
				{
					"name": "is_in",
					"values": ["abc", "xyz"]
				}...
				]
			}
		"""
		super(StringProfiler, self).__init__(column_data, config)

	def run(self) -> Dict[str, Any]:
		"""
		Returns:
			:obj:`Dict[str, Any]`: The final dict with all the metrics of a string column
			Example Output::
				{
					"total_count": 100,
					"null_count": 50,
					"unique_count": 20,
					"topn_values": {"abc": 24, "xyz": 25},
					"quality_score": 0,
					"constraints": [
						{
							"name": "eq",
							"values", "abc",
							"constraint_status": "failed/success",
							"invalid_count": 21,
							"invalid_values": ["xy", "ab", "abcd"]
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
			elif name == "contains":
				self.add_constraint(
					Contains(constraint=constraint, column_name=column_name)
				)
			elif name == "not_contains":
				self.add_constraint(
					NotContains(constraint=constraint, column_name=column_name)
				)
			elif name == "starts_with":
				self.add_constraint(
					StartsWith(constraint=constraint, column_name=column_name)
				)
			elif name == "not_starts_with":
				self.add_constraint(
					NotStartsWith(constraint=constraint, column_name=column_name)
				)
			elif name == "ends_with":
				self.add_constraint(
					EndsWith(constraint=constraint, column_name=column_name)
				)
			elif name == "not_ends_with":
				self.add_constraint(
					NotEndsWith(constraint=constraint, column_name=column_name)
				)
			elif name == "is_in":
				self.add_constraint(
					IsIn(constraint=constraint, column_name=column_name)
				)
			elif name == "not_in":
				self.add_constraint(
					NotIn(constraint=constraint, column_name=column_name)
				)
			elif name == "regex":
				self.add_constraint(
					Regex(constraint=constraint, column_name=column_name)
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
			"quality_score": self.get_quality_score(),
			"constraints": output
		}
