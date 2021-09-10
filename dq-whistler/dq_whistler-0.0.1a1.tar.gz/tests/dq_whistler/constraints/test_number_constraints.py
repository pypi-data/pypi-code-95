import unittest
import logging
from typing import Any
from pyspark.sql.session import SparkSession
from dq_whistler.constraints.number_type import *
from tests.dq_whistler.resources.configuration import number_constraints

log = logging.getLogger("SomeTest.testSomething")


class NumberConstraintTests(unittest.TestCase):
	"""
		Test suite for number type column constraints
	"""
	spark_session: SparkSession
	_column_data: DataFrame
	_column_name: str = "number_col"

	def setUp(self):
		"""
		"""
		pass

	def tearDown(self):
		"""
		"""
		pass

	def test_equal_pass(self):
		self._column_data = self.spark_session.createDataFrame([(5, ), (5, )]).toDF(self._column_name)
		constraint = number_constraints["eq"]
		output = Equal(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(output, constraint=constraint)

	def test_equal_fail(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["eq"]
		output = Equal(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=1, test_result=output, constraint=constraint)

	def test_not_equal_pass(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["not_eq"]
		output = NotEqual(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_not_equal_fail(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["not_eq"]
		output = NotEqual(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=5, test_result=output, constraint=constraint)

	def test_less_than_pass(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["lt"]
		output = LessThan(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_less_than_fail(self):
		self._column_data = self.spark_session.createDataFrame([(6,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["lt"]
		output = LessThan(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=6, test_result=output, constraint=constraint)

	def test_greater_than_pass(self):
		self._column_data = self.spark_session.createDataFrame([(6,), (7,)]).toDF(self._column_name)
		constraint = number_constraints["gt"]
		output = GreaterThan(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_greater_than_fail(self):
		self._column_data = self.spark_session.createDataFrame([(6,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["gt"]
		output = GreaterThan(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=1, test_result=output, constraint=constraint)

	def test_less_than_equal_to_pass(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (1,)]).toDF(self._column_name)
		constraint = number_constraints["lt_eq"]
		output = LessThanEqualTo(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_less_than_equal_to_fail(self):
		self._column_data = self.spark_session.createDataFrame([(6,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["lt_eq"]
		output = LessThanEqualTo(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=6, test_result=output, constraint=constraint)

	def test_greater_than_equal_to_pass(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (6,)]).toDF(self._column_name)
		constraint = number_constraints["gt_eq"]
		output = GreaterThanEqualTo(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_greater_than_equal_to_fail(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["gt_eq"]
		output = GreaterThanEqualTo(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=1, test_result=output, constraint=constraint)

	def test_between_pass(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (7,), (9,)]).toDF(self._column_name)
		constraint = number_constraints["between"]
		output = Between(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_between_fail(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["between"]
		output = Between(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=1, test_result=output, constraint=constraint)

	def test_not_between_pass(self):
		self._column_data = self.spark_session.createDataFrame([(4,), (10,)]).toDF(self._column_name)
		constraint = number_constraints["not_between"]
		output = NotBetween(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_not_between_fail(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["not_between"]
		output = NotBetween(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=5, test_result=output, constraint=constraint)

	def test_is_in_pass(self):
		self._column_data = self.spark_session.createDataFrame([(5,), (7,)]).toDF(self._column_name)
		constraint = number_constraints["is_in"]
		output = IsIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_is_in_fail(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["is_in"]
		output = IsIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=1, test_result=output, constraint=constraint)

	def test_not_in_pass(self):
		self._column_data = self.spark_session.createDataFrame([(4,), (10,)]).toDF(self._column_name)
		constraint = number_constraints["not_in"]
		output = NotIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintPass(test_result=output, constraint=constraint)

	def test_not_in_fail(self):
		self._column_data = self.spark_session.createDataFrame([(1,), (5,)]).toDF(self._column_name)
		constraint = number_constraints["not_in"]
		output = NotIn(constraint=constraint, column_name=self._column_name).execute_check(self._column_data)
		self.assertConstraintFail(invalid_count=1, invalid_value=5, test_result=output, constraint=constraint)

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
			invalid_value: int,
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
