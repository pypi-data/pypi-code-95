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

import logging

from pypushflow import UtilsMongoDb
from pypushflow import Submodel
from pypushflow.ThreadCountingActor import ThreadCountingActor

logger = logging.getLogger("pypushflow")


class StopActor(ThreadCountingActor):
    def __init__(self, parent=None, errorHandler=None, name="Stop actor", **kw):
        super().__init__(name=name, parent=parent, **kw)
        self.errorHandler = errorHandler
        self.outData = None

    def trigger(self, inData):
        logger.debug(
            "In trigger {0}, errorHandler = {1}".format(self.name, self.errorHandler)
        )
        if self.parent is not None and not isinstance(self.parent, Submodel.Submodel):
            # Parent is a Workflow
            self.outData = inData
        elif self.errorHandler is not None:
            self.errorHandler.errorHandler.stopActor.trigger(inData)
        else:
            self.outData = inData

    def join(self, timeout=7200):
        if self.parent is not None:
            logger.debug(
                "In {0}, parent {1}, before wait_threads_finished".format(
                    self.name, self.parent.name
                )
            )
        success = self._wait_threads_finished(timeout=timeout)
        if self.parent is not None:
            logger.debug(
                "In {0}, parent {1}, after wait_threads_finished".format(
                    self.name, self.parent.name
                )
            )
        self._finalizeInMongo(success)
        return success

    def _finalizeInMongo(self, success):
        if self.parent is None:
            return
        if success:
            logger.debug(
                "In {0}, parent {1}, finished".format(self.name, self.parent.name)
            )
            UtilsMongoDb.closeMongo(self.parent.mongoId, status="finished")
        else:
            logger.error(
                "In {0}, parent {1}, timeout detected".format(
                    self.name, self.parent.name
                )
            )
            UtilsMongoDb.closeMongo(self.parent.mongoId, status="timeout")
