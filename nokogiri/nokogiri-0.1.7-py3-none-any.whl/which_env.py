#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class WhichEnv:
    JUPYTER = 'ZMQInteractiveShell'
    IPYTHON = 'TerminalInteractiveShell'
    NOIPYTHON = 'NOIPYTHON'
    UNKNOWN = 'UNKNOWN'
    def __call__(self):
        try:
            name = get_ipython().__class__.__name__
            for attr in dir(self):
                if not attr.isupper():
                    continue
                if name == getattr(self, attr):
                    return getattr(self, attr)
            return self.UNKNOWN
        except:
            return self.NOIPYTHON

which_env = WhichEnv()
