import unittest
import datetime
from bmlx_components.xdl_base.interval import Interval


class IntervalTest(unittest.TestCase):
    def testStepInterval(self):
        interval = Interval.create_interval(step=10)
        self.assertFalse(interval.reached_threshold(current_step=5))
        self.assertTrue(interval.reached_threshold(current_step=10))
        self.assertFalse(interval.reached_threshold(current_step=11))

    def testHourInterval(self):
        interval = Interval.create_interval(time=3)
        current_ts = datetime.datetime.now().timestamp()

        self.assertTrue(interval.reached_threshold(current_ts=current_ts))
        self.assertTrue(interval.reached_threshold(current_ts=current_ts + 3))
        self.assertFalse(interval.reached_threshold(current_ts=4 + current_ts))
        self.assertTrue(interval.reached_threshold(current_ts=current_ts + 6))
