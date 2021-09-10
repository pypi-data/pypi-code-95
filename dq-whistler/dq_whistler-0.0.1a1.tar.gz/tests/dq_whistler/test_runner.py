import unittest
from pyspark.sql.session import SparkSession
from tests.dq_whistler.constraints.test_number_constraints import NumberConstraintTests
from tests.dq_whistler.constraints.test_string_constraints import StringConstraintTests


def get_spark_session():
	spark_session = (
		SparkSession
			.builder
			.master("local[*]")
			.appName("dq_whistler_test_cases")
			.getOrCreate()
	)
	return spark_session


def run_tests():
	"""
	Runs test cases for specific classes
	"""
	spark_session = get_spark_session()
	test_classes = [NumberConstraintTests, StringConstraintTests]

	loader = unittest.TestLoader()
	test_suites = []
	for test_class in test_classes:
		test_class.spark_session = spark_session
		suite = loader.loadTestsFromTestCase(test_class)
		test_suites.append(suite)

	big_suite = unittest.TestSuite(test_suites)
	runner = unittest.TextTestRunner()
	runner.run(big_suite)


if __name__ == "__main__":
	run_tests()
