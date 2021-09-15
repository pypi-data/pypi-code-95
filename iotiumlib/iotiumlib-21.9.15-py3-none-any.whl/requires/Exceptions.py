"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

class ApiPayloadError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'ioTiumApiPayloadError: ({})'.format(self.msg)

    def __repr__(self):
        return self.__str__()

class ApiMethodError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'ioTiumApiMethodError: ({})'.format(self.msg)

    def __repr__(self):
        return self.__str__()

class ArgMissingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'ioTiumArgMissingError: ({})'.format(self.msg)

    def __repr__(self):
        return self.__str__()

class ArgValueError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'ioTiumArgValueError: ({})'.format(self.msg)

    def __repr__(self):
        return self.__str__()
