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

import mettle.db

from bs_lib.transactionable import Transactionable


class Pod(Transactionable):
    """
    A containter object to store commonly used objects.
    """

    def __init__(self,
                 cfg    : dict = None,
                 dbcon  : "mettle.db.IConnect" = None,
                 log    : "logging.Logger" = None,
                 usr_id : str = None):
        """
        Constructor.
        """
        self.cfg    = cfg
        self.dbcon  = dbcon
        self.log    = log
        self.usr_id = usr_id


    def __del__(self):
        """
        Destructor.
        """
        pass


    def std_db_lock(self, mili_seconds: int = 500, retrys: int = 10):
        """
        Gets a lock that retries for 5 seconds before raising an exception.

        :param mili_seconds: Mili_seconds between retrys.
        :param retrys: Number of retrys.
        :return: The mettle.db.DBLock.
        """
        return mettle.db.DBLock(mili_seconds, retrys)


    def nowait_db_lock(self):
        """
        Gets a lock that does not wait and fails instantly.

        :return: mettle.db.DBLock
        """
        return mettle.db.DBLock(0, 0)


    def commit(self):
        """
        Implemented Transactionable method.
        """
        if self.dbcon:
            self.dbcon.commit()


    def rollback(self):
        """
        Implemented Transactionable method.
        """
        if self.dbcon:
            self.dbcon.rollback()
