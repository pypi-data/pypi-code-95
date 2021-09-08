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

import os.path
import logging
import select
import signal
import subprocess
import sys

import mettle


class SentinelProcess():
    """
    The standard sub process class for the sentinel manager.
    This object is used ot manage sub processes, and there is not need to
    overload, consider it sealed class.
    """
    MAX_PIPE_OUT_LEN    = 4096

    def __init__(self,
                 name           : str,
                 proc_args      : list,
                 log            : "logging.Logger",
                 swallow_stdout : bool = False,
                 swallow_stderr : bool = False):
        """
        Constructor.

        :param name: The name of the process.
        :param proc_args: List of arguments to run the sub process.
        :param log: The logger object to use.
        :param swallow_stdout: If true, will not log any std output from the process
        :param swallow_stderr: If true, will not log any std error output from the process
        """
        if len(proc_args) < 1:
            raise mettle.lib.xMettle("Process arguements cannot be blank [name:%s]" % (name), __name__)

        self.name        = name
        self._proc_args  = proc_args
        self._rc         = None
        self._proc       = None
        self._log        = log
        self._stderr     = ''
        self._eat_stdout = swallow_stdout
        self._eat_stderr = swallow_stderr


    def shutdown(self):
        """
        Tells the process to terminate nicely, ie. sign interrupt/term.
        """
        if self._proc is None:
            return

        if sys.platform.startswith('win') and hasattr(signal, 'CTRL_C_EVENT'):
            self._proc.send_signal(getattr(signal, 'CTRL_C_EVENT'))
        else:
            self._proc.send_signal(signal.SIGINT)

        self._log.info("[pid:%s] Shutdown signal received [name:%s]" % (str(self._proc.pid), self.name))


    def kill(self):
        """
        Sends the kill command to the process, shutdown immediately.
        """
        if self._proc is None:
            return

        self._proc.kill()

        self._log.info("[pid:%s] Kill signal received [name:%s]" % (str(self._proc.pid), self.name))


    def pid(self) -> str:
        """
        Get the pid.

        :return: The process id, empty if the process has not started yet.
        """
        if self._proc is None:
            return ''

        return str(self._proc.pid)


    def proc_std_err(self) -> str:
        """
        Get the process std err if it failed.

        :return: The stanadard error from the process.
        """
        return self._stderr


    def is_alive(self) -> bool:
        """
        Checks if the process is running or not.

        :return: True if the process running else false.
        """
        if self._proc is None:
            return False

        if self._rc is not None:
            return False

        self._rc = self._proc.poll()

        if self._proc.stdout is not None:
            if select.select([self._proc.stdout], [], [], 0) == ([self._proc.stdout], [], []):
                while True:
                    stdout = os.read(self._proc.stdout.fileno(), self.MAX_PIPE_OUT_LEN)

                    if not self._eat_stdout and stdout:
                        self._log.info('[%s pid:%s] STDOUT: %s' % (
                            self.name, str(self._proc.pid), str(stdout, 'utf8').strip()))

                        if len(stdout) >= self.MAX_PIPE_OUT_LEN:
                            continue

                    break

        if self._proc.stderr is not None:
            if select.select([self._proc.stderr], [], [], 0) == ([self._proc.stderr], [], []):
                while True:
                    stderr = os.read(self._proc.stderr.fileno(), self.MAX_PIPE_OUT_LEN)
                    tmp    = str(stderr, 'utf8').strip()

                    self._stderr += tmp
                    self._stderr  = self._stderr[-1024:]

                    if not self._eat_stderr and tmp:
                        self._log.warning('[%s, pid:%s] stderr: %s' % (self.name, str(self._proc.pid), tmp))

                        if len(stderr) >= self.MAX_PIPE_OUT_LEN:
                            continue

                    break

        if self._rc is None:
            return True

        if self._proc.stdout:
            self._proc.stdout.close()
            self._proc.stdout = None

        if self._proc.stderr:
            self._proc.stderr.close()
            self._proc.stderr = None

        return False


    def completed_ok(self) -> bool:
        """
        Check if the process has completed ok.

        :return: If still running returns None, else returns True if exited without errors.
        """
        if self._rc is None:
            return None

        return self._rc == 0


    def start(self, pass_fds: list = []) -> None:
        """
        Sarts the processes.

        :param pass_fds: List of file descriptors to pass to the process.
        """
        if self._proc is not None:
            if self._proc.poll() is None:
                raise mettle.lib.xMettle("Cannot run process [name:%s] because it already has a running process [pid:%s]" % (
                    self.name, str(self._proc.pid)), __name__)

            self._proc = None

        self._rc = None

        try:
            self._log.debug(" - Starting process [fds:%s, args:%s]'" % (str(pass_fds), str(self._proc_args)))

            self._proc = subprocess.Popen(
                self._proc_args,
                close_fds=len(pass_fds) < 1,
                pass_fds=pass_fds,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            self._log.info("Running [pid:%s, name:%s]" % (str(self._proc.pid), self.name))

        except Exception as x:
            pid = ''

            if self._proc is not None:
                pid = str(self.pid)

            self._log.error('[pid:%s] Exception caught in run [name:%s, error:%s]' % (pid, self.name, str(x)))

            if self._proc is None:
                self._rc = 1
            else:
                self._rc = self._proc.poll()
        finally:
            if self._proc is not None:
                self._rc = self._proc.poll()
            else:
                self._rc = 1
