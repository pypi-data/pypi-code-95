#
# Copyright (c) European Synchrotron Radiation Facility (ESRF)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__authors__ = ["O. Svensson"]
__license__ = "MIT"
__date__ = "28/05/2019"


import os
import pprint
import logging
import pathlib
import logging.handlers

from pypushflow import UtilsMongoDb


class Workflow(object):
    def __init__(self, name):
        self.name = name
        self.listOnErrorActor = []
        self.mongoId = UtilsMongoDb.initMongo(name=name)
        self.listActorRef = []
        self.logger = self.initLogger(name)

    def connectOnError(self, actor):
        self.logger.debug(
            "In Workflow '{0}' connectOnError, actor name {1}".format(
                self.name, actor.name
            )
        )
        self.listOnErrorActor.append(actor)

    def triggerOnError(self, inData):
        self.logger.debug("In Workflow '{0}' triggerOnError, inData:".format(self.name))
        self.logger.debug(pprint.pformat(inData))
        for onErrorActor in self.listOnErrorActor:
            self.logger.debug(
                "In Workflow '{0}' triggerOnError, triggering actor name {1}".format(
                    self.name, onErrorActor.name
                )
            )
            onErrorActor.trigger(inData)

    def getActorPath(self):
        return "/" + self.name

    def addActorRef(self, actorRef):
        self.logger.debug("Adding actor ref: {0}".format(actorRef.name))
        self.listActorRef.append(actorRef)

    def getListActorRef(self):
        return self.listActorRef

    def initLogger(self, name):
        user = os.environ.get("USER", "unknown")
        initiator = os.environ.get("PYPUSHFLOW_INITIATOR", "pypushflow")
        log_file_dir = pathlib.Path("/tmp_14_days/{0}/{1}".format(user, initiator))
        if not log_file_dir.exists():
            log_file_dir.mkdir(mode=0o755, parents=True)
        log_file_path = log_file_dir / "{0}.log".format(name)
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("pypushflow")
        # with open(log_file_path, "w") as fd:
        #     fd.write("Test line\n")
        maxBytes = 1e7
        backupCount = 10
        fileHandler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=maxBytes, backupCount=backupCount
        )
        logFileFormat = "%(asctime)s %(levelname)-8s %(message)s"
        formatter = logging.Formatter(logFileFormat)
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(logging.DEBUG)
        logger.addHandler(fileHandler)
        logger.debug("")
        logger.debug("")
        logger.debug("Starting new workflow " + name)
        logger.debug("")
        return logger
