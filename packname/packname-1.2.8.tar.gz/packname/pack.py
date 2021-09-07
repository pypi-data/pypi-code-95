import logging

from packname.subm_a import SubmAClass02, SubmAClass01
from packname.subm_b import SubmBClass01, SubmBClass02

logger = logging.getLogger(__name__)

class Pack():
    def describe(self):
        logger.info("Description of entire package")
        c = SubmAClass01()
        c.describe()
        c = SubmAClass02()
        c.describe()

        c = SubmBClass01()
        c.describe()
        c = SubmBClass02()
        c.describe()