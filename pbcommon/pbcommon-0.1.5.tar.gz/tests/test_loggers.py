import logging

from pbcommon.loggers import get_logger


def test_get_logger():
    logger = get_logger('test_get_logger', 'test.log', stream_level=logging.DEBUG, file_level=logging.ERROR)

    assert logger.name == 'test_get_logger'
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
    assert logger.handlers[0].level == logging.ERROR
    assert logger.handlers[1].level == logging.DEBUG
    assert logger.handlers[0].baseFilename.endswith('test.log')


def test_get_logger_with_defaults():
    logger = get_logger('test_get_logger_with_defaults', 'test.log')

    assert logger.name == 'test_get_logger_with_defaults'
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
    assert logger.handlers[0].level == logging.DEBUG
    assert logger.handlers[1].level == logging.ERROR
    assert logger.handlers[0].baseFilename.endswith('test.log')