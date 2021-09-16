# -*- coding: utf-8 -*-
#
# File: testWFAdaptations.py
#
# Copyright (c) 2013 by Imio.be
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

from DateTime import DateTime

from Products.PloneMeeting.model.adaptations import RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS

from Products.MeetingIDEA.tests.MeetingIDEATestCase import MeetingIDEATestCase
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from zope.i18n import translate


class testWFAdaptations(MeetingIDEATestCase, mctwfa):
    '''Tests various aspects of votes management.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Most of wfAdaptations makes no sense, just make sure most are disabled.'''
        self.assertEquals(
            sorted(self.meetingConfig.listWorkflowAdaptations().keys()),
            ['no_publication', 'refused', 'return_to_proposing_group']
        )

    def _return_to_proposing_group_active_state_to_clone(self):
        '''Helper method to test 'return_to_proposing_group' wfAdaptation regarding the
           RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE defined value.
           In our usecase, this is Nonsense as we use RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS.'''
        return

    def _return_to_proposing_group_active_custom_permissions(self):
        '''Helper method to test 'return_to_proposing_group' wfAdaptation regarding the
           RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS defined value.
           In our use case, just test that permissions of 'returned_to_proposing_group' state
           are the one defined in RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS.'''
        itemWF = self.wfTool.getWorkflowsFor(self.meetingConfig.getItemTypeName())[0]
        returned_to_proposing_group_state_permissions = itemWF.states['returned_to_proposing_group'].permission_roles
        for permission in returned_to_proposing_group_state_permissions:
            self.assertEquals(returned_to_proposing_group_state_permissions[permission],
                              RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS['meetingitemcaidea_workflow'][permission])

    def _return_to_proposing_group_active_wf_functionality(self):
        '''Tests the workflow functionality of using the 'return_to_proposing_group' wfAdaptation.
           Same as default test until the XXX here under.'''
        # while it is active, the creators of the item can edit the item as well as the MeetingManagers
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.validateItem(item)
        # create a Meeting and add the item to it
        self.changeUser('pmManager')
        self.create('Meeting', date=DateTime())
        self.presentItem(item)
        # now that it is presented, some persons can not edit it anymore
        for userId in ('pmCreator1', 'pmDepartmentHead1'):
            self.changeUser(userId)
            self.failIf(self.hasPermission('Modify portal content', item))
        # the item can be send back to the proposing group by the MeetingManagers only
        for userId in ('pmCreator1', 'pmDepartmentHead1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.wfTool.getTransitionsFor(item))
        self.changeUser('pmManager')
        self.failUnless('return_to_proposing_group' in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)])
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')
        self.changeUser('pmCreator1')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # MeetingManagers can still edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # the creator can send the item back to the meeting managers, as the meeting managers
        for userId in ('pmCreator1', 'pmManager'):
            self.changeUser(userId)
            self.failUnless('backTo_presented_from_returned_to_proposing_group' in
                            [tr['name'] for tr in self.wfTool.getTransitionsFor(item)])
        # when the creator send the item back to the meeting, it is in the right state depending
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'backTo_presented_from_returned_to_proposing_group')
        self.assertEquals(item.queryState(), 'presented')
        # XXX changed by MeetingIDEA
        # send the item back to proposing group, set the meeting in_committee then send the item back to the meeting
        # the item should be now in the item state corresponding to the meeting frozen state, so 'itemfrozen'
        self.do(item, 'return_to_proposing_group')

    def _no_publication_inactive(self):
        '''
        Tests while 'no_publication' wfAdaptation is inactive.
        Override for MIDEA. In this WF, item doesn't have itempublished state
        '''
        meeting = self._createMeetingWithItems()
        self.publishMeeting(meeting)
        self.assertEqual(meeting.queryState(), 'published')

    def test_pm_Validate_workflowAdaptations_added_no_publication(self):
        """Test MeetingConfig.validate_workflowAdaptations that manage addition
           of wfAdaptations 'no_publication' that is not possible if some meeting
           or items are 'published'.
           Override for MIDEA. In this WF, item doesn't have itempublished state
           """
        # ease override by subproducts
        if 'no_publication' not in self.meetingConfig.listWorkflowAdaptations():
            return

        no_publication_added_error = translate('wa_added_no_publication_error',
                                               domain='PloneMeeting',
                                               context=self.request)
        cfg = self.meetingConfig
        # make sure we do not have recurring items
        self.changeUser('pmManager')
        # create a meeting with an item and publish it
        meeting = self.create('Meeting', date='2016/01/15')
        item = self.create('MeetingItem')
        self.presentItem(item)
        self.publishMeeting(meeting)
        self.assertEquals(meeting.queryState(), 'published')
        self.assertEquals(
            cfg.validate_workflowAdaptations(('no_publication', )),
            no_publication_added_error)

    def test_pm_WFA_refused(self):
        """Not needed in MeetingIdea WF"""
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
