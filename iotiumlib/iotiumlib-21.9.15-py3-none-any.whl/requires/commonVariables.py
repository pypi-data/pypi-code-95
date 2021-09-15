"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""


__author__ = "ioTium QA"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."

from iotiumlib import orch

class commonVariables:

    def __init__(self):
        self.__orchip__ = orch.ip
        self.__token__ = orch.token
        self.__apikey__=orch.apikey

    def __getattr__(self, item):
        return item
