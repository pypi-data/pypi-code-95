import unittest
import pytest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pytz import timezone
from bmlx.utils import io_utils
from pathlib import Path
from bmlx_components.sample_selector.driver import SampleSelectorDriver


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.driver = SampleSelectorDriver(None)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def testSearchLastModelHourSucc(self):
        cst_tz = timezone("Asia/Chongqing")
        current_time = datetime.now(cst_tz)
        model_hour = current_time - timedelta(hours=3)

        dir_path = os.path.join(self.test_dir, model_hour.strftime("%Y%m%d/%H"))
        os.makedirs(dir_path)
        # create _SUCCESS file
        Path(os.path.join(dir_path, "_SUCCESS")).touch()

        ret = self.driver.search_last_model_hour(
            self.test_dir,
            (current_time - timedelta(hours=4)).strftime("%Y%m%d/%H"),
        )
        self.assertEqual(ret, model_hour.strftime("%Y%m%d/%H"))

    def testSearchLastModelHourFail_1(self):
        cst_tz = timezone("Asia/Chongqing")
        current_time = datetime.now(cst_tz)
        model_hour = current_time - timedelta(hours=3)

        dir_path = os.path.join(self.test_dir, model_hour.strftime("%Y%m%d/%H"))
        os.makedirs(dir_path)
        # no _SUCCESS file

        ret = self.driver.search_last_model_hour(
            self.test_dir,
            (current_time - timedelta(hours=4)).strftime("%Y%m%d/%H"),
        )
        self.assertEqual(ret, None)

    def testSearchLastModelHourFail_2(self):
        cst_tz = timezone("Asia/Chongqing")
        current_time = datetime.now(cst_tz)
        model_hour = current_time - timedelta(hours=3)

        dir_path = os.path.join(self.test_dir, model_hour.strftime("%Y%m%d/%H"))
        os.makedirs(dir_path)
        # create _SUCCESS file
        Path(os.path.join(dir_path, "_SUCCESS")).touch()

        ret = self.driver.search_last_model_hour(
            self.test_dir,
            (current_time - timedelta(hours=2)).strftime("%Y%m%d/%H"),
        )
        self.assertEqual(ret, model_hour.strftime("%Y%m%d/%H"))

    def testGenCandidateSamples_1(self):
        ret = self.driver.gen_candidate_samples(
            self.test_dir,
            last_model_hour="20200520/01",
            start_sample_hour="20200520/03",
            end_sample_hour="20200520/03",
        )
        self.assertEqual(len(ret), 1)

    def testGenCandidateSamples_2(self):
        ret = self.driver.gen_candidate_samples(
            self.test_dir,
            last_model_hour="20200520/01",
            start_sample_hour="20200520/03",
            end_sample_hour="20200520/04",
        )
        self.assertEqual(len(ret), 2)

    def testGenCandidateSamplesEmpty(self):
        ret = self.driver.gen_candidate_samples(
            self.test_dir,
            last_model_hour="20200520/01",
            start_sample_hour="20200520/03",
            end_sample_hour="20200520/02",
        )

        self.assertEqual(len(ret), 0)
