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

from pypushflow.AbstractActor import AbstractActor

import logging

logger = logging.getLogger("pypushflow")


class RouterActor(AbstractActor):
    def __init__(
        self,
        parent=None,
        errorHandler=None,
        name="Router",
        itemName=None,
        listPort=None,
        **kw
    ):
        super().__init__(parent=parent, name=name, **kw)
        self.errorHandler = errorHandler
        self.name = name
        self.itemName = itemName
        if listPort is None:
            self.listPort = []
        else:
            self.listPort = listPort
        self.dictValues = {}

    def connect(self, actor, expectedValue="other"):
        if expectedValue != "other" and expectedValue not in self.listPort:
            raise RuntimeError(
                "Port {0} not defined for router actor {1}!".format(
                    expectedValue, self.name
                )
            )
        if expectedValue in self.dictValues:
            self.dictValues[expectedValue].append(actor)
        else:
            self.dictValues[expectedValue] = [actor]

    def trigger(self, inData):
        logger.debug('In router actor "{0}"'.format(self.name))
        self.setStarted()
        self.setFinished()
        listActor = None
        if self.itemName in inData:
            logger.debug(
                'In router actor "{0}", itemName {1} in inData'.format(
                    self.name, self.itemName
                )
            )
            value = inData[self.itemName]
            logger.debug('In router actor "{0}", value = {1}'.format(self.name, value))
            if value in [None, "None", "null"]:
                value = "null"
            elif type(value) == bool:
                if value:
                    value = "true"
                else:
                    value = "false"
            if not isinstance(value, dict) and value in self.dictValues:
                listActor = self.dictValues[value]
        if listActor is None:
            logger.debug('In router actor "{0}", actor is None')
            if "other" in self.dictValues:
                listActor = self.dictValues["other"]
            else:
                raise RuntimeError(
                    'No "other" port for router actor "{0}"'.format(self.name)
                )
        for actor in listActor:
            logger.debug(
                'In router actor "{0}", triggering actor "{1}"'.format(
                    self.name, actor.name
                )
            )
            actor.trigger(inData)
