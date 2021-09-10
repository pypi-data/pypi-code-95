"""
Preset Logger

Config:
    LOGGER:
        filename:
        filemode:
        format:
        datefmt:
        style:
        level:
"""

import logging

logger = logging.getLogger()


def setup_logger(config: dict):
    logging.basicConfig(**config)
    logger = logging.getLogger()
