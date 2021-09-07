import logging
import numpy as np

logger = logging.getLogger(__name__)

class SubmAClass01:
    def describe(self):
        logger.info(__file__)
        logger.info("Hello from SubmAClass01")
        self.do_something()

    def do_something(self):
        np.random.randn()