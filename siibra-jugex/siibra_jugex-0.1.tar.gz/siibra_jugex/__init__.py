__version__="0.1"

import logging
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s:%(levelname)s]  %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# convenience function, will be easier to discover
def set_log_level(level):
    logger.setLevel(level)

set_log_level("INFO")
logger.info(f"Version: {__version__}")

from .jugex import DifferentialGeneExpression
