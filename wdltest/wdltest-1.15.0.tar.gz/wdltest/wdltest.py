from wdltest.cromwell_handler import CromwellHandler
from wdltest.test_configuration import TestConfiguration
from wdltest.test_runner import TestRunner

import logging
import os
import configparser

class Wdltest(object):

    def __init__(self, testConfigFile = os.path.dirname(__file__) + "/test_config.json", configFile = os.path.dirname(__file__) + "/wdltest.cfg", index = -1):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Reading config')
        config = self.getConfig(configFile)
        testConfig = TestConfiguration(testConfigFile).getConfiguration()

        # Preparing cromwell
        self.logger.info('Preparing cromwell handler')
        self.cromwell = CromwellHandler(config)
        self.testRunner = TestRunner(testConfig, self.cromwell, index = index)

    def getConfig(self, configFile = os.path.dirname(__file__) + "/wdltest.cfg"):
        config = configparser.ConfigParser()
        config.read(configFile)
        return config

    def run(self):
        exitCode = self.testRunner.run()
        self.cromwell.stop()
        return exitCode

    def localrun(self):
        exitCode = self.testRunner.run()
        self.cromwell.stop()
        return exitCode

    def stop(self):
        self.cromwell.stop()