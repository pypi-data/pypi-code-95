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

from .pod       import Pod
from .pod_async import PodAsync


class IProvider:
    """
    Provider interface object.
    """

    def new_config(self, options: dict = None) -> dict:
        """
        Load a new configuration instance.

        :param options: Optional dict object.
        :return: The loaded dictionary config
        """
        pass


    def new_db_connector(self, cfg: dict = None, options: dict = None) -> "mettle.db.IConnect":
        """
        Create a new database connection object.

        :param cfg: Optional config object.
        :param options: Optional options object
        :return: The connect database connection.
        """
        pass


    def new_logger(self, cfg: dict = None, options: dict = None) -> "logging.Logger":
        """
        Return a logger object from the standard python logging.

        :param cfg: Optional config object.
        :param options: Optional options object
        :return: The logging object.
        """
        pass


    def new_pod(self,
                cfg: dict = None,
                logger: "logging.Logger" = None,
                dbcon: "mettle.db.IConnect" = None,
                options: dict = None) -> "Pod|PodAsync":
        """
        Creates a new pod.

        :param cfg: Config dictionary.
        :param logger: Logger to use
        :param dbcon: Database connection
        :param options: Optional options object
        :return: The new pod object.
        """
        pass


    def init_std_logging(self,
                         cfg     : dict = None,
                         options : dict = None,
                         log_cfg : dict = None,
                         force   : bool = False):
        """
        Initializes the standard logging.

        :param cfg: Optional config object.
        :param options: Optional options object
        :param log_cfg: (str/dict) If string, path to logging config yaml, else is logging config dictionary.
        :param force: If set to True, forces reload.
        """
        pass
