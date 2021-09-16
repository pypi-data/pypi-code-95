import logging
import logging.handlers
import os

abspath = os.path.abspath(os.path.dirname(__file__))

format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')

def my_logger(module_name):

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    # stream handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(format)

    # debug handler
    f1_handler = logging.handlers.RotatingFileHandler(os.path.join(abspath, "logs/debug.log"))
    f1_handler.setLevel(logging.DEBUG)
    f1_handler.setFormatter(format)

    # info handler
    f2_handler = logging.handlers.RotatingFileHandler(os.path.join(abspath, "logs/info.log"))
    f2_handler.setLevel(logging.INFO)
    f2_handler.setFormatter(format)

    # warning handler
    f3_handler = logging.handlers.RotatingFileHandler(os.path.join(abspath, "logs/warning.log"))
    f3_handler.setLevel(logging.WARNING)
    f3_handler.setFormatter(format)

    # error handler
    f4_handler = logging.handlers.RotatingFileHandler(os.path.join(abspath, "logs/error.log"))
    f4_handler.setLevel(logging.ERROR)
    f4_handler.setFormatter(format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f1_handler)
    logger.addHandler(f2_handler)
    logger.addHandler(f3_handler)
    logger.addHandler(f4_handler)

    return logger
#
# logger = my_logger(__name__)
# logger.warning('This is a warning')
# logger.error('This is an error')
# logger.info('This is an info')
# logger.debug('This is an debug')