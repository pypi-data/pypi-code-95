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
from pypushflow.ThreadCountingActor import ThreadCountingActor

logger = logging.getLogger("pypushflow")


class AbstractActor(ThreadCountingActor):
    def __init__(self, parent=None, name=None, **kw):
        super().__init__(name=name, parent=parent, **kw)
        self.listDownStreamActor = []
        self.actorId = None
        self.started = False
        self.finished = False

    def connect(self, actor):
        logger.debug(
            'Connecting actor "{0}" to actor "{1}"'.format(self.name, actor.name)
        )
        self.listDownStreamActor.append(actor)

    def trigger(self, inData):
        self.setStarted()
        self.setFinished()
        for actor in self.listDownStreamActor:
            logger.debug(
                'In actor "{0}", triggering actor "{1}"'.format(self.name, actor.name)
            )
            actor.trigger(inData)

    def uploadInDataToMongo(self, actorData={}, script=None):
        if self.parent is not None:
            if self.parent.mongoId is not None:
                actorPath = self.getActorPath() + "/" + self.name
                self.actorId = UtilsMongoDb.initActor(
                    workflowId=self.parent.mongoId,
                    name=actorPath,
                    actorData=actorData,
                    script=script,
                )

    def uploadOutDataToMongo(self, actorData={}, script=None):
        if self.parent is not None:
            if self.parent.mongoId is not None:
                UtilsMongoDb.addDataToActor(
                    workflowId=self.parent.mongoId,
                    actorId=self.actorId,
                    actorData=actorData,
                )

    def setMongoAttribute(self, attribute, value):
        if self.parent is not None:
            if self.parent.mongoId is not None:
                UtilsMongoDb.setMongoAttribute(self.parent.mongoId, attribute, value)

    def getActorPath(self):
        return self.parent.getActorPath()

    def hasStarted(self):
        return self.started

    def setStarted(self):
        logger.debug("Setting finished of {0} to True".format(self.name))
        self.started = True

    def hasFinished(self):
        return self.finished

    def setFinished(self):
        logger.debug("Setting finished of {0} to True".format(self.name))
        self.finished = True
