# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2013 by IMIO
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Andre Nuyens <andre@imio.be>"""
__docformat__ = 'plaintext'

# ------------------------------------------------------------------------------
from Products.PloneMeeting.interfaces import \
    IMeetingItemWorkflowConditions, IMeetingItemWorkflowActions, \
    IMeetingWorkflowActions, IMeetingWorkflowConditions

# ------------------------------------------------------------------------------
class IMeetingItemCAIDEAWorkflowActions(IMeetingItemWorkflowActions):
    """This interface represents a meeting item as viewed by the specific
       item workflow that is defined in this MeetingIDEA product."""
    def doPresent(self, stateChange):
        """
          Triggered while doing the 'present' transition
        """
    def doAcceptButModify(self, stateChange):
        """
          Triggered while doing the 'accept_but_modify' transition
        """
    def doPreAccept(self, stateChange):
        """
          Triggered while doing the 'pre_accept' transition
        """
class IMeetingItemCAIDEAWorkflowConditions(IMeetingItemWorkflowConditions):
    """This interface represents a meeting item as viewed by the specific
       item workflow that is defined in this MeetingIDEA product."""
    def mayDecide(self, stateChange):
        """
          Guard for the 'decide' transition
        """
    def isLateFor(self, stateChange):
        """
          is the MeetingItem considered as late
        """
    def mayFreeze(self, stateChange):
        """
          Guard for the 'freeze' transition
        """
    def mayCorrect(self, stateChange):
        """
          Guard for the 'backToXXX' transitions
        """
class IMeetingCAIDEAWorkflowActions(IMeetingWorkflowActions):
    """This interface represents a meeting as viewed by the specific meeting
       workflow that is defined in this MeetingIDEA product."""
    def doClose(self, stateChange):
        """
          Triggered while doing the 'close' transition
        """
    def doDecide(self, stateChange):
        """
          Triggered while doing the 'decide' transition
        """
    def doFreeze(self, stateChange):
        """
          Triggered while doing the 'freeze' transition
        """
    def doBackToCreated(self, stateChange):
        """
          Triggered while doing the 'doBackToCreated' transition
        """
class IMeetingCAIDEAWorkflowConditions(IMeetingWorkflowConditions):
    """This interface represents a meeting as viewed by the specific meeting
       workflow that is defined in this MeetingIDEA product."""
    def mayFreeze(self, stateChange):
        """
          Guard for the 'freeze' transition
        """
    def mayClose(self, stateChange):
        """
          Guard for the 'close' transitions
        """
    def mayDecide(self, stateChange):
        """
          Guard for the 'decide' transition
        """
    def mayChangeItemsOrder(self, stateChange):
        """
          Check if the user may or not changes the order of the items on the meeting
        """
    def mayCorrect(self, stateChange):
        """
          Guard for the 'backToXXX' transitions
        """
# ------------------------------------------------------------------------------