from wdltest.wdltest import Wdltest
import os
import sys
import logging
import logging.config
import signal
import time
import subprocess

# Create the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create the Handler for logging data to a file
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
logger.addHandler(logger_handler)
logger.info('Configured logger handler')

def sigterm_handler(_signo, _stack_frame):
    cromwell.stop()
    sys.exit(0)
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

def hello():
    return "wdltest hello"

#def server_testrun():
#    return Wdltest().run()

def local_testrun():
    return Wdltest().localrun()
