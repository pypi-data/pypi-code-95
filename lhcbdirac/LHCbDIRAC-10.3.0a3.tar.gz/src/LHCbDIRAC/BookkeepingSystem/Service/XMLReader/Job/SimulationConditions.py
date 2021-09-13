###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""stores the simulation condition."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from DIRAC import gLogger

__RCSID__ = "$Id$"


class SimulationConditions(object):
  """SimulationConditions class."""

  def __init__(self):
    """initialize the class member."""
    self.parameters = {}

  def writeToXML(self):
    """creates the xml string."""
    gLogger.info("Write Simulation conditions to XML!!")
    result = '<SimulationCondition>\n'
    for name, value in self.parameters.items():
      result += '    <Parameter Name="' + name + '"   Value="' + value + '"/>\n'
    result += '</SimulationCondition>\n'

    return result
