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
from pypushflow.ThreadCountingActor import ThreadCountingActor


logger = logging.getLogger("pypushflow")


class Port(ThreadCountingActor):
    def __init__(self, errorHandler, name, **kw):
        super().__init__(name=errorHandler.name + "." + name, **kw)
        self.errorHandler = errorHandler
        self.listActor = []
        self.inPortTrigger = None

    def connect(self, actor):
        logger.debug("Connect {0} -> actorName {1}".format(self.name, actor.name))
        self.listActor.append(actor)

    def setTrigger(self, trigger):
        self.inPortTrigger = trigger

    def trigger(self, *args, **kwargs):
        logger.debug("In {0} trigger".format(self.name))
        if len(self.listActor) > 0:
            for actor in self.listActor:
                logger.debug(
                    "In trigger {0} -> actorName {1}".format(
                        self.errorHandler.name, actor.name
                    )
                )
                actor.trigger(*args, **kwargs)
        if self.inPortTrigger is not None:
            logger.debug(
                "In {0} trigger, trigger = {1}".format(
                    self.errorHandler.name, self.inPortTrigger
                )
            )
            self.inPortTrigger(*args, **kwargs)


class Submodel:
    def __init__(
        self,
        parent=None,
        errorHandler=None,
        name=None,
        portNames=["In", "Out"],
        thread_counter=None,
    ):
        self.parent = parent
        self.mongoId = self.parent.mongoId
        self.name = name
        if errorHandler is None:
            self.errorHandler = parent
        else:
            self.errorHandler = errorHandler
        self.dictPort = {}
        self.listOnErrorActor = []
        for portName in portNames:
            self.dictPort[portName] = Port(
                self, portName, thread_counter=thread_counter
            )

    def getActorPath(self):
        return self.parent.getActorPath() + "/" + self.name.replace("%", " ")

    def getPort(self, portName):
        logger.debug("In {0} getPort, portName = {1}".format(self.name, portName))
        return self.dictPort[portName]

    def connect(self, actor, portName="Out"):
        logger.debug(
            "In {0} connect, portName = {2} -> actorName = {1}".format(
                self.name, actor.name, portName
            )
        )
        self.dictPort[portName].connect(actor)

    def connectOnError(self, actor):
        logger.debug(
            "In connectOnError in subModule {0}, actor name {1}".format(
                self.name, actor.name
            )
        )
        self.listOnErrorActor.append(actor)

    def triggerOnError(self, *args, **kwargs):
        for onErrorActor in self.listOnErrorActor:
            logger.debug(
                "In triggerOnError in subModule {0}, trigger actor {1}, inData = {2}".format(
                    self.name, onErrorActor.name, args[0]
                )
            )
            onErrorActor.trigger(*args, **kwargs)
        if self.errorHandler is not None:
            logger.error(
                'Trigger on error on errorHandler "{0}"'.format(self.errorHandler.name)
            )
            self.errorHandler.triggerOnError(*args, **kwargs)

    def addActorRef(self, actorRef):
        if self.parent is not None:
            self.parent.addActorRef(actorRef)
