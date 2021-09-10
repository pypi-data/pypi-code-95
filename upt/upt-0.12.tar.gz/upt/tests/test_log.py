# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from io import StringIO
import logging
import unittest
from unittest import mock

import upt


class TestLog(unittest.TestCase):
    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_quiet(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.CRITICAL+1)
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(), '')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_debug(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.DEBUG)
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(), 'debug\ninfo\nwarning\n')
        self.assertEqual(m_stderr.getvalue(), 'error\ncritical\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_formatter(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.DEBUG)
        upt.log.logger_set_formatter(logger, 'foo')
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(),
                         '[DEBUG   ] [foo] debug\n'
                         '[INFO    ] [foo] info\n'
                         '[WARNING ] [foo] warning\n')
        self.assertEqual(m_stderr.getvalue(),
                         '[ERROR   ] [foo] error\n'
                         '[CRITICAL] [foo] critical\n')

    @unittest.skipIf(upt.log.color_available is False,
                     reason='Colorlog not available')
    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_formatter_colored(self, m_stdout, m_stderr):
        logger = upt.log.create_logger(logging.DEBUG, colored=True)
        upt.log.logger_set_formatter(logger, 'foo')
        logger.debug('debug')
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        self.assertEqual(m_stdout.getvalue(),
                         '\x1b[37m [DEBUG   ] [foo] debug\x1b[0m\n'
                         '\x1b[32m [INFO    ] [foo] info\x1b[0m\n'
                         '\x1b[33m [WARNING ] [foo] warning\x1b[0m\n')
        self.assertEqual(m_stderr.getvalue(),
                         '\x1b[31m [ERROR   ] [foo] error\x1b[0m\n'
                         '\x1b[1;31m [CRITICAL] [foo] critical\x1b[0m\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_formatter_color_unavailable(self, m_stdout, m_stderr):
        try:
            # We want to pretend that colorlog is not installed.
            # Ideally we would not mess with upt.log.color_available and would
            # instead override the relevant methods from importlib, but I'm too
            # lazy to figure out how to do this.
            # This test should pass whether or not colorlog is actually
            # installed.
            color_available = upt.log.color_available
            upt.log.color_available = False
            logger = upt.log.create_logger(logging.DEBUG, colored=True)
            upt.log.logger_set_formatter(logger, 'foo')
            logger.debug('debug')
            logger.info('info')
            logger.warning('warning')
            logger.error('error')
            logger.critical('critical')
        finally:
            upt.log.color_available = color_available

        self.assertEqual(m_stdout.getvalue(),
                         '[WARNING ] [upt] You requested colored logs, but '
                         'the colorlog module could not be found. Switching '
                         'to black and white logs.\n'
                         '[DEBUG   ] [foo] debug\n'
                         '[INFO    ] [foo] info\n'
                         '[WARNING ] [foo] warning\n')
        self.assertEqual(m_stderr.getvalue(),
                         '[ERROR   ] [foo] error\n'
                         '[CRITICAL] [foo] critical\n')


if __name__ == '__main__':
    unittest.main()
