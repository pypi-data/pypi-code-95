# -*- coding:utf-8 -*-

from __future__ import division, print_function
import sys
from .keyevent import get_keyevent_obj


class PigitShell(object):
    def __init__(self, command_handle):
        super(PigitShell, self).__init__()
        self._buffer = []
        self._histories = []

        self._command_handle = command_handle
        self._key_handle = get_keyevent_obj()
        self._cursor_handle = None

        import pigit.tomato

        self._tomato = pigit.tomato

    def output(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def launch(self):
        print(
            "Welcome come PIGIT shell.\n"
            "You can use short commands directly. Input '?' to get help.\n"
        )
        while True:
            self.output("(pigit)> ")
            pass
