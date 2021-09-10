import unittest
from typing import Any
import logging
from pyspark.sql.session import SparkSession
from dq_whistler.constraints.string_type import *
from tests.dq_whistler.resources.configuration import string_constraints

log = logging.getLogger("SomeTest.testSomething")


class StringConstraintTests(unittest.TestCase):
	"""
	Test suite for numeric data type constraints
	"""
	spark_session: SparkSession
	_column_data: DataFrame
	_column_name: str = "string_col"

	def setUp(self):
		"""
		"""
		pass

	def tearDown(self):
		"""
		"""
		pass

	def test_equal_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("abc",)]).toDF(self._column_name)
		constraint = string_constraints["eq"]
		output = Equal(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_equal_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["eq"]
		output = Equal(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="xyz", test_result=output, constraint=constraint)

	def test_not_equal_pass(self):
		self._column_data = self.spark_session.createDataFrame([("xy",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_eq"]
		output = NotEqual(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_not_equal_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_eq"]
		output = NotEqual(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="abc", test_result=output, constraint=constraint)

	def test_contains_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("abc",)]).toDF(self._column_name)
		constraint = string_constraints["contains"]
		output = Contains(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_contains_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abcd",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["contains"]
		output = Contains(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="xyz", test_result=output, constraint=constraint)

	def test_not_contains_pass(self):
		self._column_data = self.spark_session.createDataFrame([("xy",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_contains"]
		output = NotContains(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_not_contains_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abcd",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_contains"]
		output = NotContains(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="abcd", test_result=output, constraint=constraint)

	def test_starts_with_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abcd",), ("abce",)]).toDF(self._column_name)
		constraint = string_constraints["starts_with"]
		output = StartsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_starts_with_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abcef",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["starts_with"]
		output = StartsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="xyz", test_result=output, constraint=constraint)

	def test_not_starts_with_pass(self):
		self._column_data = self.spark_session.createDataFrame([("aabc",), ("aaabc",)]).toDF(self._column_name)
		constraint = string_constraints["not_starts_with"]
		output = NotStartsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_not_starts_with_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abcef",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_starts_with"]
		output = NotStartsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="abcef", test_result=output, constraint=constraint)

	def test_ends_with_pass(self):
		self._column_data = self.spark_session.createDataFrame([("afgabc",), ("bghabc",)]).toDF(self._column_name)
		constraint = string_constraints["ends_with"]
		output = EndsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_ends_with_fail(self):
		self._column_data = self.spark_session.createDataFrame([("bghabc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["ends_with"]
		output = EndsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="xyz", test_result=output, constraint=constraint)

	def test_not_ends_with_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abcef",), ("abcefg",)]).toDF(self._column_name)
		constraint = string_constraints["not_ends_with"]
		output = NotEndsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_not_ends_with_fail(self):
		self._column_data = self.spark_session.createDataFrame([("bghabc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_ends_with"]
		output = NotEndsWith(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="bghabc", test_result=output, constraint=constraint)

	def test_is_in_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("abcd",)]).toDF(self._column_name)
		constraint = string_constraints["is_in"]
		output = IsIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_is_in_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["is_in"]
		output = IsIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="xyz", test_result=output, constraint=constraint)

	def test_not_in_pass(self):
		self._column_data = self.spark_session.createDataFrame([("xy",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_in"]
		output = NotIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_not_in_fail(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["not_in"]
		output = NotIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="abc", test_result=output, constraint=constraint)

	def test_regex_pass(self):
		self._column_data = self.spark_session.createDataFrame([("abc",), ("abcdef",)]).toDF(self._column_name)
		constraint = string_constraints["regex"]
		output = Regex(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_regex_fail(self):
		self._column_data = self.spark_session.createDataFrame([("1abc2",), ("xyz",)]).toDF(self._column_name)
		constraint = string_constraints["regex"]
		output = Regex(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value="1abc2", test_result=output, constraint=constraint)

	def assertConstraintPass(self, test_result: Dict[str, Any], constraint: Dict[str, Any]) -> None:
		return self.assertEqual(
			test_result, {
				**constraint,
				"constraint_status": "success",
				"invalid_count": 0,
				"invalid_values": []
			}
		)

	def assertConstraintFail(
			self,
			invalid_count: int,
			invalid_value: str,
			test_result: Dict[str, Any],
			constraint: Dict[str, Any]
	) -> None:
		return self.assertEqual(
			test_result, {
				**constraint,
				"constraint_status": "failed",
				"invalid_count": invalid_count,
				"invalid_values": [invalid_value]
			}
		)
