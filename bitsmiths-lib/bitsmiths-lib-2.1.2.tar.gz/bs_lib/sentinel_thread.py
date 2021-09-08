# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

import logging
import time
import traceback

from threading import Thread

import mettle

from bs_lib import common


class SentinelThread(Thread):
    """
    Any thread that are to be managed by the Sentinel must inherit from this class.
    """

    PROC_INTERVAL_SLEEP = 0.2
    PROC_INTERVAL       = 1.0

    def __init__(self, name: str, proc_interval: float = 5.0):
        """
        Constructor.

        :param name: Name of thread.
        :param proc_interval: The interval in seconds to perform processing, cannot be less than 0.2.
        """
        super().__init__(name=name)

        self._usr_id     = "[%s]" % self.name
        self._pod        = None
        self._shutdown   = False
        self._err_code   = None
        self._err_msg    = None
        self._err_except = None
        self._log        = common.get_logger([name, 'sentinel.pluggin', 'pluggin'])

        if self._log is None:
            self._log = logging.getLogger()

        self.set_process_interver(proc_interval)


    def __del__(self):
        """
        Destructor.
        """
        self._destroy()


    def pod_required(self) -> bool:
        """
        Indicate if this thread requires its own pod. If this method returns
        true then the Sentinel will allocte the thread a pod for entire time
        it is running.

        :return: True if a pod is required, else False
        """
        return False


    def set_pod(self, pod):
        """
        Sets the pod for sentinel, this will only be called right after the
        object is initialized, and before _initialize() is called.

        :param pod: The pod object to use.
        """
        self._pod = pod


    def set_process_interver(self, proc_interval: float):
        """
        Sets the process interval, this can be done at any time and it will reflect.

        :param proc_interval: The new proc_interval (float) in seconds, cannot be less than 0.2
        """
        if proc_interval < 0.2:
            self._proc_interval = self.PROC_INTERVAL
        else:
            self._proc_interval = proc_interval


    def _initialize(self):
        """
        Initialize the service.  Called when thread starts.
        """
        self._err_code   = None
        self._err_msg    = None
        self._err_except = None

        self._log.info("%s Initializing Sentinel Thread [name:%s]" % (self._usr_id, self.name))

        if self.pod_required() and self._pod is None:
            raise mettle.lib.xMettle('SentinelThread [%s] requires a pod, but notpod has been provided!' % (
                self.name))

        if self._pod is not None:
            self._pod.log = self._log


    def _destroy(self):
        """
        Destroys the service, freeing all resource.
        Note the pod is not destroyed, as it would be managed by the parent porocess.
        !Note this method could be called twice, make sure your code is safe.
        """
        pass


    def shutdown(self):
        """
        Tells the thread/service to shutdown.
        """
        self._shutdown = True
        self._log.info("[tid:%s] Shutdown signal received [name:%s]" % (str(self.ident), self.name))


    def kill(self):
        """
        Attempt to kill the thread.  Not implemented properly yet.
        """
        self._shutdown = True
        self._log.info("[tid:%s] Kill signal received [name:%s]" % (str(self.ident), self.name))


    def tid(self):
        """
        Get the tid, thread id.

        :returns: The id string.
        """
        return str(self.ident)


    def process(self):
        """
        Pure virtual method, write your thread processing code here.
        """
        pass


    def completed_ok(self) -> bool:
        """
        Returns if the thread exited without error.

        :return: If still running returns None, else returns True if exited without errors.
        """
        if self._err_code is None:
            return None

        return self._err_code == 0


    def get_errors(self) -> dict:
        """
        Returns errors if the thread crashed.

        :return: A dictionary of errors, or None if there were not errors or the proc is still running.
        """
        if self._err_code is None or self._err_code == 0:
            return None

        return {'errorCode' : self._err_code, 'exception' : self._err_except, 'message' : self._err_msg}


    def run(self):
        """
        The Thread overload, called by parent process to run this thread.
        """
        self._shutdown = False

        try:
            self._initialize()

            self._log.info("[tid:%s] Run starting [name:%s, proc_interval:%s]" % (
                str(self.ident), self.name, str(self._proc_interval)))

            while not self._shutdown:
                self.process()

                if self._shutdown:
                    break

                pi = self._proc_interval

                while pi > 0.0:
                    if self._shutdown:
                        break

                    pi -= self.PROC_INTERVAL_SLEEP
                    time.sleep(self.PROC_INTERVAL_SLEEP)


            self._err_code = 0
            self._log.info("[tid:%s] Run stopping [name:%s, proc_interval:%s]" % (
                str(self.ident), self.name, str(self._proc_interval)))

        except Exception as x:
            self._err_code   = 1
            self._err_except = x
            self._err_msg    = str(x)
            self._log.error('[tid:%s] Exception caught in run [name:%s, error:%s, trace:%s]' % (
                str(self.ident), self.name, self._err_msg, traceback.format_exc()))
        finally:
            self._destroy()
