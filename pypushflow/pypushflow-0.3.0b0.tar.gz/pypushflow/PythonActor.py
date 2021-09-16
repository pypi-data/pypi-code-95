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
import time
import pprint
import logging
import datetime
import traceback
import functools
import importlib
import multiprocessing
import multiprocessing.pool

from pypushflow.AbstractActor import AbstractActor


logger = logging.getLogger("pypushflow")


class ActorWrapperException(Exception):
    def __init__(self, errorMessage="", traceBack="", data={}, msg=None):
        super(ActorWrapperException, self).__init__(msg)
        self.errorMessage = errorMessage
        self.data = data
        self.traceBack = traceBack


def trace_unhandled_exceptions(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            outData = func(*args, **kwargs)
        except Exception as e:
            errorMessage = "{0}".format(e)
            logger.exception(errorMessage)
            traceBack = traceback.format_exc()
            return ActorWrapperException(
                errorMessage=errorMessage, traceBack=traceBack, data=args[1]
            )
        return outData

    return wrapped_func


#############################################################################
# Create no daemon processes
# See : https://stackoverflow.com/a/53180921
#


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess


# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class Edna2Pool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs["context"] = NoDaemonContext()
        super().__init__(*args, **kwargs)


#
#
#############################################################################


class AsyncFactory:
    def __init__(self, func, callback=None, errorCallback=None):
        self.func = func
        self.callback = callback
        self.errorCallback = errorCallback
        self.pool = Edna2Pool(1)
        self.hasFinished = False

    def call(self, *args, **kwargs):
        logger.debug(
            "Before apply_async, func={0}, callback={1}, errorCallback={2}".format(
                self.func, self.callback, self.errorCallback
            )
        )
        logger.debug("args={0}, kwargs={1}".format(args, kwargs))
        self.pool.apply_async(
            self.func,
            args=args,
            kwds=kwargs,
            callback=self.callback,
            error_callback=self.errorCallback,
        )
        self.pool.close()
        logger.debug("After apply_async")


class ActorWrapper:
    def __init__(self, name, method):
        self.name = name
        self.method = method

    @trace_unhandled_exceptions
    def run(self, *args, **kwargs):
        logger.debug("In actor wrapper for {0}".format(self.name))
        logger.debug(
            "args={0}, kwargs={1}, method={2}".format(args, kwargs, self.method)
        )
        inData = args[0]
        outData = self.method(**inData)
        return outData


class PythonActor(AbstractActor):
    def __init__(
        self, parent=None, name="Python Actor", errorHandler=None, script=None, **kw
    ):
        super().__init__(parent=parent, name=name, **kw)
        self.parentErrorHandler = errorHandler
        self.listErrorHandler = []
        self.script = script
        self.actorWrapper = None
        self.inData = None
        self.outData = None
        self.af = None

    def connectOnError(self, errorHandler):
        self.listErrorHandler.append(errorHandler)

    def trigger(self, inData):
        self.setStarted()
        self.inData = dict(inData)
        self.uploadInDataToMongo(actorData={"inData": inData}, script=self.script)
        logger.debug(
            "In trigger {0}, inData = {1}".format(self.name, pprint.pformat(inData))
        )
        if isinstance(inData, ActorWrapperException):
            logger.error(
                "Error from previous actor! Not running actor {0}".format(self.name)
            )
            if self.parentErrorHandler is not None:
                workflowException = inData
                oldInData = workflowException.data
                exceptionDict = {
                    "errorMessage": workflowException.errorMessage,
                    "traceBack": workflowException.traceBack.split("\n"),
                }
                oldInData["WorkflowException"] = exceptionDict
                self.parentErrorHandler.triggerOnError(oldInData)
        try:
            module = importlib.import_module(os.path.splitext(self.script)[0])
        except Exception as e:
            logger.error("Error when trying to import script {0}".format(self.script))
            time.sleep(1)
            self.errorHandler(inData, e)
        else:

            def errorHandler(e):
                self.errorHandler(inData, e)

            with self._postpone_end_thread(
                self.triggerDownStreamActor, errorHandler
            ) as (callback, errorCallback):
                actorWrapper = ActorWrapper(self.name, module.run)
                self.af = AsyncFactory(
                    actorWrapper.run, callback=callback, errorCallback=errorCallback
                )
                self.af.call(self.inData)

    def errorHandler(self, inData, exception):
        logger.error("Error when running actor {0}!".format(self.name))
        self.setFinished()
        errorMessage = "{0}".format(exception)
        logger.exception(errorMessage)
        traceBack = traceback.format_exc().split("\n")
        # workflowException = WorkflowException(
        #     errorMessage=errorMessage,
        #     traceBack=traceBack
        # )
        outData = dict(inData)
        outData["WorkflowException"] = {
            "errorMessage": errorMessage,
            "traceBack": traceBack,
        }
        logger.error(exception)
        for errorHandler in self.listErrorHandler:
            errorHandler.trigger(outData)
        if self.parentErrorHandler is not None:
            self.parentErrorHandler.triggerOnError(outData)

    def triggerDownStreamActor(self, inData={}):
        logger.debug("In triggerDownStreamActor for {0}".format(self.name))
        self.setFinished()
        if isinstance(inData, ActorWrapperException):
            logger.error(
                "Error from previous actor! Not running down stream actors {0}".format(
                    [actor.name for actor in self.listDownStreamActor]
                )
            )
            workflowException = inData
            oldInData = workflowException.data
            exceptionDict = {
                "errorMessage": workflowException.errorMessage,
                "traceBack": workflowException.traceBack.split("\n"),
            }
            oldInData["WorkflowException"] = exceptionDict
            self.uploadOutDataToMongo(
                actorData={
                    "stopTime": datetime.datetime.now(),
                    "status": "error",
                    "outData": exceptionDict,
                }
            )
            for errorHandler in self.listErrorHandler:
                errorHandler.trigger(oldInData)
            if self.parentErrorHandler is not None:
                logger.error(
                    'Trigger on error on errorHandler "{0}"'.format(
                        self.parentErrorHandler.name
                    )
                )
                self.parentErrorHandler.triggerOnError(inData=oldInData)
        else:
            outData = dict(inData)
            self.uploadOutDataToMongo(
                actorData={
                    "stopTime": datetime.datetime.now(),
                    "status": "finished",
                    "outData": outData,
                }
            )
            if "workflowLogFile" in outData:
                self.setMongoAttribute("logFile", outData["workflowLogFile"])
            if "workflowDebugLogFile" in outData:
                self.setMongoAttribute("debugLogFile", outData["workflowDebugLogFile"])
            downstreamData = dict(self.inData)
            downstreamData.update(outData)
            for downStreamActor in self.listDownStreamActor:
                logger.debug(
                    "In trigger {0}, triggering actor {1}, inData={2}".format(
                        self.name, downStreamActor.name, downstreamData
                    )
                )
                downStreamActor.trigger(downstreamData)
