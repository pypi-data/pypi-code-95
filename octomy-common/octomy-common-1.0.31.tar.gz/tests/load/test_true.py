import pprint
import logging
import os

logger = logging.getLogger(__name__)


def test_true():
    logger.info("Dummy load test")
    return True
