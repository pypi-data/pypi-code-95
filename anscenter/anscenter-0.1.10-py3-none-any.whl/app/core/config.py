import logging
import sys
from typing import List

from anscenter.app.core.logging import InterceptHandler
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


config = Config("anscenter/.env")

API_PREFIX = "/api"
VERSION = config("VERSION")
DEBUG : bool = config("DEBUG", cast=bool, default=False)
MAX_CONNECTIONS_COUNT : int = config("MAX_CONNECTIONS_COUNT", cast= int, default=100)
MIN_CONNECTIONS_ACOUNT : int = config("MIN_CONNECTIONS_COUNT", cast=int, default=0)
SECRET_KEY : Secret = config("SECRET_KEY", cast=Secret, default="")

PROJECT_NAME : str = config("PROJECT_NAME")

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

MODEL_PATH = config("MODEL_PATH")
MODEL_NAME = config("MODEL_NAME")
MODEL_ID = config("MODEL_ID")