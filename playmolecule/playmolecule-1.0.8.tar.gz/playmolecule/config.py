from configparser import ConfigParser
import playmolecule
import inspect
import logging
import os


logger = logging.getLogger(__name__)


_config = ConfigParser()


def loadConfig():
    if os.getenv("PM_SDK_CONFIG"):
        path = os.environ["PM_SDK_CONFIG"]
    elif os.getenv("SDKCONFIG"):
        path = os.environ["SDKCONFIG"]
    else:
        homeDir = os.path.dirname(inspect.getfile(playmolecule))
        path = os.path.join(homeDir, "config.ini")

    logger.info(f"Reading PM API configuration from {path}")
    _config.read(path)
