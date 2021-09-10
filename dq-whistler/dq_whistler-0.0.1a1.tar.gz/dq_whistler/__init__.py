import logging

from pkg_resources import DistributionNotFound, get_distribution
from dq_whistler.analyzer import DataQualityAnalyzer

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

__all__ = [
    "DataQualityAnalyzer",
]
