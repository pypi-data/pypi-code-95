# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.
# pylint: disable=unused-variable, unused-import, bad-indentation, no-self-use
import time
import unittest
import requests
from okera import (HAS_PANDAS, HAS_NUMPY, NO_PANDAS_RUNTIME_ERROR, NO_NUMPY_RUNTIME_ERROR)
from okera.tests import pycerebro_test_common as common

class DependencyTests(unittest.TestCase):

  def test_no_pandas_assert(self):
    ctx = common.get_test_context()
    with common.get_planner(ctx) as planner:
      HAS_NUMPY = True
      HAS_PANDAS = False
      try:
        planner.scan_as_pandas("okera_sample.sample")
      except (RuntimeError) as e:
        self.assertEqual(NO_PANDAS_RUNTIME_ERROR,
                         str(e),
                         msg='Expected NO_PANDAS_RUNTIME_ERROR but received other')
      planner.scan_as_json("okera_sample.sample")

  def test_no_numpy_assert(self):
    ctx = common.get_test_context()
    with common.get_planner(ctx) as planner:
      HAS_NUMPY = False
      HAS_PANDAS = False # Pandas requires numpy
      try:
        planner.scan_as_json("okera_sample.sample")
      except (RuntimeError) as e:
        self.assertEqual(NO_NUMPY_RUNTIME_ERROR,
                         str(e),
                         msg='Expected NO_NUMPY_RUNTIME_ERROR but received other')

      try:
        planner.scan_as_pandas("okera_sample.sample")
      except (RuntimeError) as e:
        self.assertEqual(NO_PANDAS_RUNTIME_ERROR,
                         str(e),
                         msg='Expected NO_PANDAS_RUNTIME_ERROR but received other')

  def test_no_numpy_presto(self):
    ctx = common.get_test_context()
    with common.get_planner(ctx, dialect='presto') as planner:
      HAS_NUMPY = False
      HAS_PANDAS = False
      planner.scan_as_json("select * from okera_sample.sample")

if __name__ == "__main__":
  unittest.main()
