# -*- coding: utf8 -*-
from xlang import logger


def to_bool(o) -> bool:
    return True if o in [True, 'True', 'true', 'yes', 'on', '1'] else to_int(o) > 0


def to_int(o, default: int = 0) -> int:
    v: int = default

    try:
        v = int(o)
    except Exception as e:
        logger.error(e)

    return v


def to_float(o, default: float = 0) -> float:
    v = default

    try:
        v = float(o)
    except Exception as e:
        logger.error(e)

    return v
