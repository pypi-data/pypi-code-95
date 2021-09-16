# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
#
# Copyright (c) 2007-2010 by PloneGov
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

from Products.MeetingIDEA.tests.MeetingIDEATestCase import MeetingIDEATestCase
from Products.MeetingCommunes.tests.testWorkflows import testWorkflows as mctw


class testWorkflows(MeetingIDEATestCase, mctw):
    """Tests the default workflows implemented in MeetingIDEA.

       WARNING:
       The Plone test system seems to be bugged: it does not seem to take into
       account the write_permission and read_permission tags that are defined
       on some attributes of the Archetypes model. So when we need to check
       that a user is not authorized to set the value of a field protected
       in this way, we do not try to use the accessor to trigger an exception
       (self.assertRaise). Instead, we check that the user has the permission
       to do so (getSecurityManager().checkPermission)."""

    def test_pm_WholeDecisionProcess(self):
        """Bypass this test..."""
        pass

    def test_pm_WorkflowPermissions(self):
        """Bypass this test..."""
        pass

    def test_pm_RecurringItems(self):
        """Bypass this test..."""
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflows, prefix='test_pm_'))
    return suite