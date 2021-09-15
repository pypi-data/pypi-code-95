#!/usr/bin/env python

# Copyright 2016 Earth Sciences Department, BSC-CNS

# This file is part of MapGenerator.

# MapGenerator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MapGenerator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MapGenerator. If not, see <http://www.gnu.org/licenses/>.

"""
Main module for MapGenerator. Only contains an interface class to all functionality implemented on MapGenerator.
"""

from __future__ import print_function

import logging
import matplotlib
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel('CRITICAL')

from mapgenerator.plotting.config import ArgumentParser
from mapgenerator.plotting import plotmap
import sys
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class MapGenerator:
    """
    Interface class for MapGenerator
    """
    def __init__(self, parser):
        self.parser = parser

    def main(self):
        """
        Main functionality of the tool
        """
        try:
            args = self.parser.parse_args()
            #log.info(args)
            req = vars(args)
            # print help if no args
            if req.values()==[None for i in range(len(req.values()))]:
                self.parser.parser.print_help()
                return False
#            srcfiles = req['srcfiles']
#            srcvars = req['srcvars']
#            req.pop('srcfiles')
#            req.pop('srcvars')
            # pass only valid values and cast boolean strings to boolean
            res = {k:eval(v) if v in ('True','False') else v for k,v in req.items() if v}

            loglevel = 'loglevel' in res and \
                getattr(logging, res['loglevel']) or \
                    getattr(logging, 'WARNING')

            mpl_logger.setLevel(loglevel)
            log.setLevel(loglevel)

            log.info(res)

            # various plot types
            if 'pltype' in res:
                if res['pltype'] == 'cross':
                    plotmap.PlotCross(loglevel).plot(**res)
                elif res['pltype'] == 'timeseries':
                    plotmap.PlotSeries(loglevel).plot(**res)
                elif res['pltype'] == 'map':
                    plotmap.PlotMap(loglevel).plot(**res)
            else:
                res['pltype'] = 'map'
                plotmap.PlotMap(loglevel).plot(**res)

        except Exception as e:
            log.error('Unhandled exception on MapGenerator: %s' % e, exc_info=True)
            return False


if __name__ == "__main__":
    if MapGenerator(ArgumentParser()).main() is False:
        sys.exit(1)
    sys.exit(0)

