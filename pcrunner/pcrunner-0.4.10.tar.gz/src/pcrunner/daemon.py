#!/usr/bin/env python
# pcrunner/daemon.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8

'''
pcrunner.daemon
---------------

Generic linux daemon base class for python 2.x/3.x.
'''
from __future__ import print_function, unicode_literals

import atexit
import io
import os
import signal
import sys
import time


class Daemon:
    '''
    A generic daemon class.
    Usage: subclass the daemon class and override the run() method.
    '''

    def __init__(self, pid_file):
        self.pid_file = pid_file

    def daemonize(self):
        '''
        Daemonize class. UNIX double fork mechanism.
        '''

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = io.open(os.devnull, 'r')
        so = io.open(os.devnull, 'a+')
        se = io.open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pid_file
        atexit.register(self.delpid)

        pid = os.getpid()
        with io.open(self.pid_file, 'w+', encoding='utf-8') as f:
            f.write('%d\n' % pid)

    def delpid(self):
        '''
        Remove pid file.
        '''
        os.remove(self.pid_file)

    def start(self):
        '''
        Start the daemon.
        '''

        # Check for a pid_file to see if the daemon already runs
        try:
            with io.open(self.pid_file, 'r', encoding='utf-8') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            mesg = "pid file {0} already exist. " + "Daemon already running?\n"
            sys.stderr.write(mesg.format(self.pid_file))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        '''
        Stop the daemon.
        '''

        # Get the pid from the pid file
        try:
            with io.open(self.pid_file, 'r', encoding='utf-8') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            mesg = "pid file {0} does not exist. " + "Daemon not running?\n"
            sys.stderr.write(mesg.format(self.pid_file))
            sys.exit(1)

        # Try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = '{0}'.format(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
            else:
                print('{0}'.format(err.args))
                sys.exit(1)

    def run(self):
        '''
        You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by start()
        '''
