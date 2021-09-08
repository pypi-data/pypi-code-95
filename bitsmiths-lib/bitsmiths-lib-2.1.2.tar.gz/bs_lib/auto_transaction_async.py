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


class AutoTransactionAsync:
    """
    A class to async manage auto rollbacks if exceptions are thrown.
    """

    def __init__(self, *tran_args):
        """
        Constructor.

        :param tran_args: The ATransactionable objects to auto transact on.
        """
        self._tran_args = tran_args
        self._handled   = False


    async def __aenter__(self):
        """
        On enter event.
        """
        for x in self._tran_args:
            if x:
                await x.begin()

        return self


    async def __aexit__(self, type, value, traceback):
        """
        On exit event.
        """
        if self._handled:
            return

        for x in self._tran_args:
            if x:
                await x.rollback()


    async def commit(self):
        """
        Commits the transactionable objects.
        """
        self._handled = True

        for x in self._tran_args:
            if x:
                await x.commit()


    async def rollback(self):
        """
        Rolls back the transactionable objects.
        """
        self._handled = True

        for x in self._tran_args:
            if x:
                await x.rollback()
