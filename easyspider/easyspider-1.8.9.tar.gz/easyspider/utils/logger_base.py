#coding=utf-8

import logging
from logging.config import dictConfig

DEFAULT_LOGGER_CONFIG = {
    "version":1,
    "handlers":{
        "console":{
            "class":"logging.StreamHandler",
            "formatter":"default_formatter",
        },
        "file":{
            "class":"logging.FileHandler",
            "formatter":"default_formatter",
            "filename":"./log_base.log"
        }
    },
    "formatters":{
        "default_formatter":{
            "format":"%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            "datefmt":"%Y-%m-%d %H:%M:%S"
        }
    },
    "root":{
        "level":"DEBUG",
        "handlers":["console","file"]

    }
}

def config_logger():
    dictConfig(DEFAULT_LOGGER_CONFIG)

config_logger()

logger = logging.getLogger(__name__)
logger.info("logger start")
