#!python
# scripts/run_check.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8

"""
A wrapper for running nagios checks within a limited time.
"""

from __future__ import print_function, unicode_literals

import shlex
import subprocess
import sys
import time
from argparse import ArgumentParser


class Check(object):
    def __init__(self, name, hostname, cmd_line, result_type):
        self.name = name
        self.hostname = hostname
        self.cmd_line = cmd_line
        self.result_type = result_type
        self.cmd = shlex.split(cmd_line, posix=True)
        self.returncode = 3
        self.time = 0
        self.stderr = ''
        self.stdout = ''

    def __unicode__(self):
        '''
        String representation in NSCA format
        '''
        return '[{0:.0f}] {1};{2};{3};{4};{5}'.format(
            self.time,
            self.result_type,
            self.hostname,
            self.name,
            self.returncode,
            ' '.join([self.stdout, self.stderr]).strip(),
        )


class RunCheck(object):
    def __init__(self, check, timeout):
        self.check = check
        self.timeout = timeout
        self.process_killed = False
        self.time_start = 0
        self.time_exec = 0
        self.pid = None

    def __unicode__(self):
        return (
            '{{"check_restult": "{0}", "pid": "{1}", "time_start": '
            '"{2:.0f}", "time_exec": "{3:.3f}"}}'.format(
                self.check,
                self.pid,
                self.time_start,
                self.time_exec,
            )
        )

    def start(self):
        self.time_start = time.time()
        try:
            self.process = subprocess.Popen(
                self.check.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError as error:
            self.stderr = str(error)
            self.check.returncode = 3
        else:
            self.pid = self.process.pid
            self.poll_process()
            if not self.process_killed:
                (
                    self.check.stderr,
                    self.check.stdout,
                ) = self.process.communicate()

    def poll_process(self):
        while self.process.poll() is None:
            self.time_exec = time.time() - self.time_start
            if self.time_exec > self.timeout:
                self.check.stderr = (
                    'Check timed out in {0:.0f} secs. No check results'.format(
                        self.time_exec
                    )
                )
                self.check.returncode = 3
                print(
                    '{0}[{1}]: {2}'.format(
                        self.check.name,
                        self.pid,
                        self.check.stderr,
                    )
                )
                print(
                    '{0}[{1}]: terminate process'.format(
                        self.check.name,
                        self.pid,
                    )
                )
                self.process.terminate()
                time.sleep(1)
                print(
                    '{0}[{1}]: kill process'.format(
                        self.check.name,
                        self.pid,
                    )
                )
                self.process.kill()
                self.process_killed = True
                break
            time.sleep(0.1)
        self.check.time = time.time()


def parse_args(args):
    '''
    Parse the command-line arguments
    '''

    parser = ArgumentParser(description='run_check.py')
    parser.add_argument(
        "name",
        type=str,
        help="name of the check",
    )
    parser.add_argument(
        "hostname",
        type=str,
        help="hostname",
    )
    parser.add_argument(
        "command",
        type=str,
        default='',
        help="command",
    )
    parser.add_argument(
        "result_type",
        type=str,
        default='',
        help="result_type",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="time to wait before terminating the process",
        default=60,
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    arg = parse_args(sys.argv[1:])
    check = Check(arg.name, arg.hostname, arg.command, arg.result_type)
    runcheck = RunCheck(check, arg.timeout)
    runcheck.start()
    print(runcheck)
    print(runcheck.check)
