# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
#
# Copyright (c) 2007-2012 by CommunesPlone.org
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
from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import View
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.MeetingIDEA.tests.MeetingIDEATestCase import MeetingIDEATestCase


class testCustomWorkflows(MeetingIDEATestCase):
    """Tests the default workflows implemented in MeetingIDEA."""

    def test_FreezeMeeting(self):
        """
           When we freeze a meeting, every presented items will be frozen
           too and their state will be set to 'itemfrozen'.  When the meeting
           come back to 'created', every items will be corrected and set in the
           'presented' state
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        # create 2 items and present them to the meeting
        item1 = self.create('MeetingItem', title='The first item')
        self.presentItem(item1)
        item2 = self.create('MeetingItem', title='The second item')
        self.presentItem(item2)
        wftool = self.portal.portal_workflow
        # every presented items are in the 'presented' state
        self.assertEquals('presented', item1.queryState())
        self.assertEquals('presented', item2.queryState())
        # every items must be in the 'itemfrozen' state if we freeze the meeting
        self.do(meeting, 'freeze')
        self.assertEquals('itemfrozen', item1.queryState())
        self.assertEquals('itemfrozen', item2.queryState())
        # when correcting the meeting back to created, the items must be corrected
        # when correcting the meeting back to created, the items must be corrected back to "presented"
        self.do(meeting, 'backToCreated')
        # when correcting the meeting back to created, the items must be corrected
        # back to "presented"
        self.assertEquals('presented', item1.queryState())
        self.assertEquals('presented', item2.queryState())

        self.freezeMeeting(meeting)
        # when an item is 'itemfrozen' it will stay itemfrozen if nothing
        # is defined in the meetingConfig.onMeetingTransitionItemActionToExecute
        self.meetingConfig.setOnMeetingTransitionItemActionToExecute([])
        self.backToState(meeting, 'created')
        self.assertEquals('itemfrozen', item1.queryState())
        self.assertEquals('itemfrozen', item2.queryState())

    def test_CloseMeeting(self):
        """
           When we close a meeting, every items are set to accepted if they are still
           not decided...
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting (with 7 items)
        meetingDate = DateTime().strftime('%y/%m/%d %H:%M:00')
        meeting = self.create('Meeting', date=meetingDate)
        item1 = self.create('MeetingItem')  # id=o2
        item1.setProposingGroup(self.vendors_uid)
        item1.setAssociatedGroups(self.developers_uid)
        item2 = self.create('MeetingItem')  # id=o3
        item2.setProposingGroup(self.developers_uid)
        item3 = self.create('MeetingItem')  # id=o4
        item3.setProposingGroup(self.vendors_uid)
        item4 = self.create('MeetingItem')  # id=o5
        item4.setProposingGroup(self.developers_uid)
        item5 = self.create('MeetingItem')  # id=o7
        item5.setProposingGroup(self.vendors_uid)
        item6 = self.create('MeetingItem', title='The sixth item')
        item6.setProposingGroup(self.vendors_uid)
        item7 = self.create('MeetingItem')  # id=o8
        item7.setProposingGroup(self.vendors_uid)
        for item in (item1, item2, item3, item4, item5, item6, item7):
            self.presentItem(item)
        # we freeze the meeting
        self.freezeMeeting(meeting)
        self.assertEquals('frozen', meeting.queryState())
        # a MeetingManager can put the item back to presented
        self.backToState(item7, 'presented')
        self.assertEquals('presented', item7.queryState())
        # we decide the meeting
        # while deciding the meeting, every items that where presented are frozen
        self.decideMeeting(meeting)
        self.assertEquals('decided', meeting.queryState())
        self.assertEquals('itemfrozen', item7.queryState())
        # change all items in all different state (except first who is in good state)
        self.backToState(item7, 'presented')
        self.assertEquals('presented', item7.queryState())
        self.do(item2, 'delay')
        self.do(item3, 'pre_accept')
        self.do(item4, 'accept_but_modify')
        self.do(item5, 'refuse')
        self.do(item6, 'accept')
        # we publish the meeting
        self.do(meeting, 'publish')
        self.backToState(meeting, 'decided')
        # we close the meeting
        self.do(meeting, 'publish')
        self.do(meeting, 'close')
        self.backToState(meeting, 'published')
        self.do(meeting, 'close')
        # every items must be in the 'decided' state if we close the meeting
        wftool = self.portal.portal_workflow
        # itemfrozen change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item1, 'review_state'))
        # delayed rest delayed (it's already a 'decide' state)
        self.assertEquals('delayed', wftool.getInfoFor(item2, 'review_state'))
        # pre_accepted change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item3, 'review_state'))
        # accepted_but_modified rest accepted_but_modified (it's already a 'decide' state)
        self.assertEquals('accepted_but_modified', wftool.getInfoFor(item4, 'review_state'))
        # refused rest refused (it's already a 'decide' state)
        self.assertEquals('refused', wftool.getInfoFor(item5, 'review_state'))
        # accepted rest accepted (it's already a 'decide' state)
        self.assertEquals('accepted', wftool.getInfoFor(item6, 'review_state'))
        # presented change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item7, 'review_state'))

    def test_ObserversMayViewInEveryStates(self):
        """A MeetingObserverLocal has every 'View' permissions."""

        def _checkObserverMayView(item):
            """Log as 'pmObserver1' and check if he has every 'View' like permissions."""
            original_user_id = self.member.getId()
            self.changeUser('pmObserver1')
            # compute permissions to check, it is View + ACI + every "PloneMeeting: Read ..." permissions
            itemWF = self.portal.portal_workflow.getWorkflowsFor(item)[0]
            read_permissions = [permission for permission in itemWF.permissions
                                if permission.startswith('PloneMeeting: Read')]
            read_permissions.append(View)
            read_permissions.append(AccessContentsInformation)
            for read_permission in read_permissions:
                self.assertTrue(self.hasPermission(read_permission, item))
            self.changeUser(original_user_id)

        # enable prevalidation
        cfg = self.meetingConfig
        self.changeUser('pmManager')
        if 'pre_validation' in cfg.listWorkflowAdaptations():
            cfg.setWorkflowAdaptations(('pre_validation',))
            performWorkflowAdaptations(cfg, logger=pm_logger)
            self._turnUserIntoPrereviewer(self.member)
        item = self.create('MeetingItem')
        item.setDecision(self.decisionText)
        meeting = self.create('Meeting', date=DateTime('2017/03/27'))
        for transition in self.TRANSITIONS_FOR_PRESENTING_ITEM_1:
            _checkObserverMayView(item)
            if transition in self.transitions(item):
                self.do(item, transition)
        _checkObserverMayView(item)
        for transition in self.TRANSITIONS_FOR_CLOSING_MEETING_1:
            _checkObserverMayView(item)
            if transition in self.transitions(meeting):
                self.do(meeting, transition)
        _checkObserverMayView(item)
        # we check that item and meeting did their complete workflow
        self.assertEqual(item.queryState(), 'accepted')
        self.assertEqual(meeting.queryState(), 'closed')

    def test_WholeDecisionProcess(self):
        """
            This test covers the whole decision workflow. It begins with the
            creation of some items, and ends by closing a meeting.
            test only CA
        """
        self._testWholeDecisionProcessCA()

    def _testWholeDecisionProcessCA(self):
        '''This test covers the whole decision workflow. It begins with the
           creation of some items, and ends by closing a meeting.'''
        # pmCreator1 creates an item with 1 annex and proposes it
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem', title='The first item')
        annex1 = self.addAnnex(item1)
        self.addAnnex(item1, relatedTo='item_decision')
        self.do(item1, 'proposeToDepartmentHead')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the DepartmentHead validation level
        self.changeUser('pmDepartmentHead1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.do(item1, 'proposeToDirector')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the reviwer (Director) can validate item
        self.changeUser('pmDirector1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.changeUser('pmReviewer1')
        self.do(item1, 'validate')
        # pmManager creates a meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        self.addAnnex(item1, relatedTo='item_decision')
        # pmCreator2 creates and proposes an item
        self.changeUser('pmCreator2')
        item2 = self.create('MeetingItem', title='The second item',
                            preferredMeeting=meeting.UID())
        self.do(item2, 'proposeToDepartmentHead')
        # pmReviewer1 can not validate the item has not in the same proposing group
        self.changeUser('pmReviewer1')
        self.failIf(self.hasPermission('Modify portal content', item2))
        # even pmManager can not see/validate an item in the validation queue
        self.changeUser('pmManager')
        self.failIf(self.hasPermission('Modify portal content', item2))
        # do the complete validation
        self.changeUser('admin')
        self.do(item2, 'proposeToDirector')
        # pmManager inserts item1 into the meeting and publishes it
        self.changeUser('pmManager')
        managerAnnex = self.addAnnex(item1)
        self.portal.restrictedTraverse('@@delete_givenuid')(managerAnnex.UID())
        self.do(item1, 'present')
        # Now reviewers can't add annexes anymore
        self.changeUser('pmReviewer1')
        self.assertRaises(Unauthorized, self.addAnnex, item2)
        # freeze the meeting
        self.changeUser('pmManager')
        self.freezeMeeting(meeting)

        # validate item2 after meeting freeze
        self.changeUser('pmReviewer2')
        self.do(item2, 'validate')
        self.changeUser('pmManager')
        self.do(item2, 'present')
        self.addAnnex(item2)
        # So now we should have 3 normal item (2 recurring items) and one late item in the meeting
        self.failUnless(len(meeting.getItems(listTypes=['normal'])) == 3)
        self.failUnless(len(meeting.getItems(listTypes=['late'])) == 1)
        self.do(meeting, 'decide')
        self.do(item1, 'refuse')
        self.assertEquals(item1.queryState(), 'refused')
        self.assertEquals(item2.queryState(), 'itemfrozen')
        self.do(meeting, 'publish')
        self.do(meeting, 'close')
        self.assertEquals(item1.queryState(), 'refused')
        # every items without a decision are automatically accepted
        self.assertEquals(item2.queryState(), 'accepted')

    def test_RecurringItems(self):
        """
            Tests the recurring items system.
        """
        self._testRecurringItemsAG()

    def _testRecurringItemsAG(self):
        '''Tests the recurring items system.
           Recurring items are added when the meeting is setInAG.'''
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        self.failUnless(len(meeting.getItems()) == 2)
        self.do(meeting, 'freeze')
        self.failUnless(len(meeting.getItems()) == 2)
        self.do(meeting, 'decide')
        self.failUnless(len(meeting.getItems()) == 2)
        self.do(meeting, 'publish')
        self.failUnless(len(meeting.getItems()) == 2)
        self.do(meeting, 'close')
        self.failUnless(len(meeting.getItems()) == 2)
