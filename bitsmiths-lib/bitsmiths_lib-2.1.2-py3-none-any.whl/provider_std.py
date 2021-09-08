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

import os
import os.path
import logging

import mettle

from . import IProvider
from . import Pod, PodAsync
from . import common


class ProviderStd(IProvider):
    """
    Standard provider object.
    """

    def new_config(self, options: dict = None) -> dict:
        """
        Overload.
        """
        if not options:
            raise Exception('Cannot create a new config with no options.')

        config_path = options.get('config-file')

        if not config_path:
            raise Exception('[config-file] key not found when initializing config.')

        return common.read_config_dict_from_file(config_path)


    def new_db_connector(self, cfg: dict = None, options: dict = None) -> "mettle.db.IConnect":
        """
        Overload.
        """
        dbcon = None

        if cfg and cfg.get('database'):
            dbType  = cfg['database'].get('type')
            connstr = cfg['database'].get('conn-string')
        elif options:
            dbType  = options.get('db-type')
            connstr = options.get('db-conn-string')

        if not dbType or not connstr:
            raise Exception('[db-type or db-conn-string] key not found when opening new db connector.')

        try:
            if dbType == 'sqlite3':
                import mettledb_sqlite3
                dbcon = mettledb_sqlite3.Connect()
            elif dbType == 'sqlite3_native':
                from mettle.db.sqlite.Connect import Connect as SqliteConnect
                dbcon = SqliteConnect()
            elif dbType == 'postgresql':
                import mettledb_postgresql9
                dbcon = mettledb_postgresql9.Connect()
            else:
                raise Exception('Unknown database type [%s]!' % str(dbType))

            dbcon.connect(connstr)
        except Exception:
            if dbcon:
                del dbcon
            raise

        return dbcon


    def new_logger(self, cfg: dict = None, options: dict = None) -> "logging.Logger":
        """
        Overload.
        """
        return common.getLogger(options)


    def init_std_logging(self,
                         cfg     : dict = None,
                         options : dict = None,
                         log_cfg : dict = None,
                         force   : bool = False):
        """
        Overload.
        """
        if logging.getLogger().hasHandlers() and not force:
            return

        import yaml

        log_dict = None

        if type(log_cfg) == str:
            if not os.path.exists(log_cfg):
                raise Exception('Log configuration file [%s] not found.' % log_cfg)

            with open(log_cfg, 'rt') as fh:
                cfg_dict = yaml.safe_load(fh.read())
                log_dict = cfg_dict.get('logging')

                if not log_dict:
                    raise Exception('Log configuration file [%s] does not appear to be a valid logging yaml file.' % log_cfg)

        elif type(log_cfg) == dict:
            log_dict = log_cfg
        else:
            raise Exception('Cannot initialize logging with log_cfg of type (%s).' % str(type(log_cfg)))

        logging.config.dictConfig(log_dict)


    def new_pod(self,
                cfg: dict = None,
                logger: "logging.Logger" = None,
                dbcon: "mettle.db.IConnect" = None,
                options: dict = None) -> "Pod|PodAsync":
        """
        Overload.
        """
        return Pod(cfg, logger, dbcon, options)
