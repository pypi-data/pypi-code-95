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
import logging
import unittest


from pypushflow import UtilsMongoDb

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("testPythonActor")


class TestUtilsMongoDb(unittest.TestCase):
    def setUp(self):
        os.environ[
            "PYPUSHFLOW_MONGOURL"
        ] = "mongodb://pybes:pybes@linsvensson.esrf.fr:27017/pybes"
        os.environ["PYPUSHFLOW_CREATOR"] = "TestUtilsMongoDb"

    def tes_initMongo(self):
        name = "test_initMongo"
        workflowId = UtilsMongoDb.initMongo(name=name)
        self.assertIsNotNone(workflowId)

    def tes_initActor(self):
        name = "test_initMongo"
        workflowId = UtilsMongoDb.initMongo(name=name)
        self.assertIsNotNone(workflowId)
        actorName = "TestActor"
        actorId = UtilsMongoDb.initActor(name=actorName, workflowId=workflowId)
        self.assertIsNotNone(actorId)

    def tes_addDataToActor(self):
        name = "test_initMongo"
        workflowId = UtilsMongoDb.initMongo(name=name)
        self.assertIsNotNone(workflowId)
        actorName1 = "TestActor1"
        actorId1 = UtilsMongoDb.initActor(name=actorName1, workflowId=workflowId)
        self.assertIsNotNone(actorId1)
        actorName2 = "TestActor2"
        UtilsMongoDb.initActor(name=actorName2, workflowId=workflowId)
        inData = {"a": 1}
        UtilsMongoDb.addDataToActor(
            workflowId=workflowId, actorId=actorId1, actorData={"inData": inData}
        )
