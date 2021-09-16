# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2017 by Imio.be
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
# ------------------------------------------------------------------------------

import re
from collections import OrderedDict

from Products.MeetingIDEA import logger
from Products.MeetingIDEA.interfaces import IMeetingCAIDEAWorkflowActions
from Products.MeetingIDEA.interfaces import IMeetingCAIDEAWorkflowConditions
from Products.MeetingIDEA.interfaces import IMeetingItemCAIDEAWorkflowActions
from Products.MeetingIDEA.interfaces import IMeetingItemCAIDEAWorkflowConditions

from Products.MeetingCommunes.adapters import CustomMeeting as MCMeeting
from Products.MeetingCommunes.adapters import CustomMeetingItem as MCMeetingItem
from Products.MeetingCommunes.adapters import CustomMeetingConfig as MCMeetingConfig
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting as MCToolPloneMeeting
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowConditions

from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE
from Products.PloneMeeting.interfaces import IMeetingConfigCustom
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_APPLIED
from Products.PloneMeeting.config import PMMessageFactory as _

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.class_init import InitializeClass
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from collective.contact.plonegroup.utils import get_organizations
from plone import api
from zope.i18n import translate
from zope.interface import implements


MeetingConfig.wfAdaptations = ['return_to_proposing_group', 'no_publication', 'refused']
# configure parameters for the returned_to_proposing_group wfAdaptation
adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = ('presented', 'itemfrozen',)

RETURN_TO_PROPOSING_GROUP_MAPPINGS = {'backTo_presented_from_returned_to_proposing_group':
                                          ['created'],
                                      'backTo_itemfrozen_from_returned_to_proposing_group':
                                          ['frozen', 'decided', 'published',
                                           'decisions_published', ],
                                      'NO_MORE_RETURNABLE_STATES': ['closed', 'archived', ]
                                      }

adaptations.RETURN_TO_PROPOSING_GROUP_MAPPINGS.update(RETURN_TO_PROPOSING_GROUP_MAPPINGS)

RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = {
    'meetingitemcaidea_workflow': 'meetingitemcaidea_workflow.proposed_to_director',
    'meetingitemcommunes_workflow': 'meetingitemcommunes_workflow.itemcreated',
}

adaptations.RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE

RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = {
    'meetingitemcaidea_workflow': {
        # view permissions
        'Access contents information':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'View':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'PloneMeeting: Read decision':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'PloneMeeting: Read optional advisers':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'PloneMeeting: Read decision annex':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'PloneMeeting: Read item observations':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        'PloneMeeting: Read budget infos':
            ('Manager', 'MeetingManager',
             'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingObserverLocal',
             'Reader',),
        # edit permissions
        'Modify portal content':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write decision':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'Review portal content':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'Add portal content':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add annex':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add annexDecision':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add MeetingFile':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write optional advisers':
            ('Manager', 'MeetingMember',
             'MeetingDepartmentHead',
             'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write budget infos':
            ('Manager', 'MeetingMember',
             'MeetingOfficeManager',
             'MeetingManager',
             'MeetingBudgetImpactEditor',),
        'PloneMeeting: Write marginal notes':
            ('Manager', 'MeetingManager',),
        # MeetingManagers edit permissions
        'Delete objects':
            ('Manager', 'MeetingManager',),
        'PloneMeeting: Write item observations':
            ('Manager', 'MeetingManager',),
        'PloneMeeting: Write item MeetingManager reserved fields':
            ('Manager', 'MeetingManager',),
    }
}

adaptations.RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS


class CustomMeeting(MCMeeting):
    """Adapter that adapts a meeting implementing IMeeting to the
       interface IMeetingCustom."""

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting

    # Implements here methods that will be used by templates

    security.declarePublic('getIDEAPrintableItemsByCategory')

    def getIDEAPrintableItemsByCategory(self, itemUids=[], listTypes=['normal'],
                                        ignore_review_states=[], by_proposing_group=False,
                                        group_prefixes={},
                                        oralQuestion='both', toDiscuss='both', excludeCategories=[],
                                        includeEmptyCategories=False, includeEmptyDepartment=False,
                                        includeEmptyGroups=False):
        '''Returns a list of (late-)items (depending on p_late) ordered by
           category. Items being in a state whose name is in
           p_ignore_review_state will not be included in the result.
           If p_by_proposing_group is True, items are grouped by proposing group
           within every category. In this case, specifying p_group_prefixes will
           allow to consider all groups whose acronym starts with a prefix from
           this param prefix as a unique group. p_group_prefixes is a dict whose
           keys are prefixes and whose values are names of the logical big
           groups. A toDiscuss and oralQuestion can also be given, the item is a
           toDiscuss (oralQuestion) or not (or both) item.
           If p_includeEmptyCategories is True, categories for which no
           item is defined are included nevertheless. If p_includeEmptyGroups
           is True, proposing groups for which no item is defined are included
           nevertheless.'''
        # The result is a list of lists, where every inner list contains:
        # - at position 0: the category object (MeetingCategory or MeetingGroup)
        # - at position 1 to n: the items in this category
        # If by_proposing_group is True, the structure is more complex.
        # oralQuestion can be 'both' or False or True
        # toDiscuss can be 'both' or 'False' or 'True'
        # Every inner list contains:
        # - at position 0: the category object
        # - at positions 1 to n: inner lists that contain:
        #   * at position 0: the proposing group object
        #   * at positions 1 to n: the items belonging to this group.
        res = []
        tool = getToolByName(self.context, 'portal_plonemeeting')
        # Retrieve the list of items
        for elt in itemUids:
            if elt == '':
                itemUids.remove(elt)

        items = self.context.getItems(uids=itemUids, listTypes=listTypes, ordered=True)

        if by_proposing_group:
            groups = get_organizations()
        else:
            groups = None

        previousCatId = None
        if items:
            for item in items:
                # Check if the review_state has to be taken into account
                if item.queryState() in ignore_review_states:
                    continue
                elif excludeCategories != [] and item.getProposingGroup() in excludeCategories:
                    continue
                elif not (oralQuestion == 'both' or item.getOralQuestion() == oralQuestion):
                    continue
                elif not (toDiscuss == 'both' or item.getToDiscuss() == toDiscuss):
                    continue
                currentCat = item.getCategory(theObject=True)
                currentCatId = currentCat.getId()
                if currentCatId != previousCatId:
                    # Add the item to a new category, excepted if the
                    # category already exists.
                    catExists = False
                    for catList in res:
                        if catList[0] == currentCat:
                            catExists = True
                            break
                    if catExists:
                        self._insertItemInCategory(catList, item, by_proposing_group,
                                                   group_prefixes, groups)
                    else:
                        res.append([currentCat])
                        self._insertItemInCategory(res[-1], item, by_proposing_group,
                                                   group_prefixes, groups)
                    previousCatId = currentCatId
                else:
                    # Append the item to the same category
                    self._insertItemInCategory(res[-1], item, by_proposing_group, group_prefixes,
                                               groups)
        if includeEmptyCategories:
            meetingConfig = self.context.portal_plonemeeting.getMeetingConfig(
                self.context)
            allCategories = meetingConfig.getCategories()
            usedCategories = [elem[0] for elem in res]
            for cat in allCategories:
                if cat not in usedCategories:
                    # no empty service, we want only show department
                    if cat.get_acronym().find('-') > 0:
                        continue
                    elif not includeEmptyDepartment:
                        dpt_empty = True
                        for uc in usedCategories:
                            if uc.get_acronym().startswith(cat.get_acronym()):
                                dpt_empty = False
                                break
                        if dpt_empty:
                            continue
                            # Insert the category among used categories at the right place.
                    categoryInserted = False
                    for i in range(len(usedCategories)):
                        try:
                            if allCategories.index(cat) < \
                                    allCategories.index(usedCategories[i]):
                                usedCategories.insert(i, cat)
                                res.insert(i, [cat])
                                categoryInserted = True
                                break
                        except:
                            continue
                    if not categoryInserted:
                        usedCategories.append(cat)
                        res.append([cat])
        if by_proposing_group and includeEmptyGroups:
            # Include, in every category list, not already used groups.
            # But first, compute "macro-groups": we will put one group for
            # every existing macro-group.
            macroGroups = []  # Contains only 1 group of every "macro-group"
            consumedPrefixes = []
            for group in groups:
                prefix = self._getAcronymPrefix(group, group_prefixes)
                if not prefix:
                    group._v_printableName = group.Title()
                    macroGroups.append(group)
                else:
                    if prefix not in consumedPrefixes:
                        consumedPrefixes.append(prefix)
                        group._v_printableName = group_prefixes[prefix]
                        macroGroups.append(group)
            # Every category must have one group from every macro-group
            for catInfo in res:
                for group in macroGroups:
                    self._insertGroupInCategory(catInfo, group, group_prefixes,
                                                groups)
                    # The method does nothing if the group (or another from the
                    # same macro-group) is already there.
        return res


    security.declarePublic('getAvailableItems')

    def getAvailableItems(self):
        '''Items are available to the meeting no matter the meeting state (except 'closed').
           In the 'created' state, every validated items are availble, in other states, only items
           for wich the specific meeting is selected as preferred will appear.'''
        meeting = self.getSelf()
        if meeting.queryState() not in ('created', 'frozen', 'decided'):
            return []
        meetingConfig = meeting.portal_plonemeeting.getMeetingConfig(meeting)
        # First, get meetings accepting items for which the date is lower or
        # equal to the date of this meeting (self)
        meetings = meeting.portal_catalog(
            portal_type=meetingConfig.getMeetingTypeName(),
            getDate={'query': meeting.getDate(), 'range': 'max'}, )
        meetingUids = [b.getObject().UID() for b in meetings]
        meetingUids.append(ITEM_NO_PREFERRED_MEETING_VALUE)
        # Then, get the items whose preferred meeting is None or is among
        # those meetings.
        itemsUids = meeting.portal_catalog(
            portal_type=meetingConfig.getItemTypeName(),
            review_state='validated',
            getPreferredMeeting=meetingUids,
            sort_on="modified")
        if meeting.queryState() in ('frozen', 'decided'):
            # Oups. I can only take items which are "late" items.
            res = []
            for uid in itemsUids:
                if uid.getObject().wfConditions().isLateFor(meeting):
                    res.append(uid)
        else:
            res = itemsUids
        return res

    security.declarePublic('getPresenceList')

    def getPresenceList(self, filter):
        '''return list of presence in the form of dictionnary
           keys are fullname, status [0=present;1:excused;2=procuration]
           filer on status : 0,1,2 or 3 or * for all
           This method is used on template
        '''
        # suppress paragraph
        assembly = self.context.getAssembly().replace('<p>', '').replace('</p>', '')
        # supress M., MM.
        assembly = re.sub(r"M{1,2}[.]", "", assembly)
        # suppress Mmes, Mme
        assembly = re.sub(r"Mmes*.?", "", assembly)
        assembly = assembly.split('<br />')
        res = []
        status = 0
        for ass in assembly:
            ass = ass.split(',')
            for a in ass:
                # retrieve blank and pass empty lines
                a = a.strip()
                if not a:
                    continue
                # a line "ExcusÃ©:" is used for define list of persons who are excused
                if a.find('xcus') >= 0:
                    status = 1
                    continue
                # a line "Absents:" is used for define list of persons who are absentee
                if a.upper().find('ABSENT') >= 0:
                    status = 2
                    continue
                # a line "Procurations:" is used for defined list of persons who recieve a procuration
                if a.upper().find('PROCURATION') >= 0:
                    status = 3
                    continue
                if filter == '*' or status in filter:
                    res.append({'fullname': a, 'status': status})
        return res


class CustomMeetingItem(MCMeetingItem):
    """Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom."""

    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    security.declarePublic('getObservations')

    def getObservations(self, **kwargs):
        """Overridden version of 'observations' field accessor.
           Hides the observations for non-managers if meeting state is 'decided'."""
        item = self.getSelf()
        res = item.getField('observations').get(item, **kwargs)
        tool = getToolByName(item, 'portal_plonemeeting')
        if item.hasMeeting() and item.getMeeting().queryState() == 'decided' and not tool.isManager(
                item):
            return translate('intervention_under_edit',
                             domain='PloneMeeting',
                             context=item.REQUEST,
                             default='<p>The intervention is currently under '
                                     'edit by managers, you can not access it.</p>')
        return res

    MCMeetingItem.getObservations = getObservations
    MCMeetingItem.getRawObservations = getObservations

    security.declarePublic('getStrategicAxis')

    def getStrategicAxisView(self, **kwargs):
        """View Strategic Axis Title in page template."""
        item = self.getSelf()
        res = []
        for sa in item.getStrategicAxis():
            res.append(sa.Title())
        res.sort()
        return '<br />'.join(res)

    security.declarePublic('mustShowItemReference')

    def mustShowItemReference(self):
        """See doc in interfaces.py"""
        item = self.getSelf()
        if item.hasMeeting():
            return True


class CustomMeetingConfig(MCMeetingConfig):
    """Adapter that adapts a meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom."""

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def _extraSearchesInfo(self, infos):
        """Add some specific searches."""
        cfg = self.getSelf()
        itemType = cfg.getItemTypeName()
        extra_infos = OrderedDict(
            [
                # Items in state 'proposed'
                ('searchproposeditems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': "python: not tool.userIsAmong(['reviewers'])",
                     'roles_bypassing_talcondition': ['Manager', ]
                 }
                 ),
                # Items in state 'validated'
                ('searchvalidateditems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['validated']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': "",
                     'roles_bypassing_talcondition': ['Manager', ]
                 }
                 ),
            ]
        )
        infos.update(extra_infos)

        return infos

    def getMeetingsAcceptingItemsAdditionalManagerStates(self):
        """See doc in interfaces.py."""
        return 'created', 'frozen', 'decided'


class MeetingCAIDEAWorkflowActions(MeetingCommunesWorkflowActions):
    """Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCAIDEAWorkflowActions"""

    implements(IMeetingCAIDEAWorkflowActions)


class MeetingCAIDEAWorkflowConditions(MeetingCommunesWorkflowConditions):
    """Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCAIDEAWorkflowConditions"""

    implements(IMeetingCAIDEAWorkflowConditions)

    def __init__(self, meeting):
        self.context = meeting

        customAcceptItemsStates = ('created', 'frozen', 'decided')
        self.acceptItemsStates = customAcceptItemsStates


class MeetingItemCAIDEAWorkflowActions(MeetingItemCommunesWorkflowActions):
    """Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCAIDEAWorkflowActions"""

    implements(IMeetingItemCAIDEAWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doProposeToDepartmentHead')

    def doProposeToDepartmentHead(self, stateChange):
        pass

    security.declarePrivate('doProposeToDirector')

    def doProposeToDirector(self, stateChange):
        pass


class MeetingItemCAIDEAWorkflowConditions(MeetingItemCommunesWorkflowConditions):
    """Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCAIDEAWorkflowConditions"""

    implements(IMeetingItemCAIDEAWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem
        self.sm = getSecurityManager()
        self.useHardcodedTransitionsForPresentingAnItem = True
        self.transitionsForPresentingAnItem = (
            'proposeToDepartmentHead', 'proposeToDirector', 'validate', 'present')

    security.declarePublic('mayDecide')

    def mayValidate(self):
        """
          The MeetingManager can bypass the validation process and validate an item
          that is in the state 'itemcreated'
        """

        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        # User must have the 'Review portal content permission'
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
            # if the current item state is 'itemcreated', only the MeetingManager can validate
            if self.context.queryState() in ('itemcreated',) and \
                    not self.context.portal_plonemeeting.isManager(self.context):
                res = False
        return res

    security.declarePublic('mayProposeToDepartmentHead')

    def mayProposeToDepartmentHead(self):
        '''We may propose an item if the workflow permits it and if the
           necessary fields are filled.  In the case an item is transferred from
           another meetingConfig, the category could not be defined.'''

        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg
        if _checkPermission(ReviewPortalContent, self.context):
            return True

    security.declarePublic('mayProposeToDirector')

    def mayProposeToDirector(self):
        """
          Check that the user has the 'Review portal content'
        """

        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg
        if _checkPermission(ReviewPortalContent, self.context):
            return True

    security.declarePublic('mayRemove')

    def mayRemove(self):
        """
          We may remove an item if the linked meeting is in the 'decided'
          state.  For now, this is the same behaviour as 'mayDecide'
        """
        res = False
        meeting = self.context.getMeeting()
        if _checkPermission(ReviewPortalContent, self.context) and \
                meeting and (meeting.queryState() in ['decided', 'published', 'closed',
                                                      'decisions_published', ]):
            res = True
        return res


class CustomToolPloneMeeting(MCToolPloneMeeting):
    '''Adapter that adapts a tool implementing ToolPloneMeeting to the
       interface IToolPloneMeetingCustom'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def isFinancialUser_cachekey(method, self, brain=False):
        '''cachekey method for self.isFinancialUser.'''
        return str(self.context.REQUEST._debug), self.context.REQUEST['AUTHENTICATED_USER']

    def performCustomWFAdaptations(self, meetingConfig, wfAdaptation, logger, itemWorkflow,
                                   meetingWorkflow):
        """ """
        if wfAdaptation == 'refused' and 'refused' in itemWorkflow.states:
            return True

        if wfAdaptation == 'no_publication':
            # we override the PloneMeeting's 'no_publication' wfAdaptation
            # First, update the meeting workflow
            wf = meetingWorkflow
            # Delete transitions 'publish' and 'backToPublished'
            for tr in ('publish', 'backToPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['frozen'].setProperties(
                title='frozen', description='',
                transitions=['backToCreated', 'decide'])
            wf.states['decided'].setProperties(
                title='decided', description='', transitions=['backToFrozen', 'close'])
            # Delete state 'published'
            if 'published' in wf.states:
                wf.states.deleteStates(['published'])
            # Then, update the item workflow.
            wf = itemWorkflow
            # Delete transitions 'itempublish' and 'backToItemPublished'
            for tr in ('itempublish', 'backToItemPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['itemfrozen'].setProperties(
                title='itemfrozen', description='',
                transitions=['accept', 'accept_but_modify', 'refuse', 'delay', 'pre_accept',
                             'backToPresented'])
            for decidedState in ['accepted', 'refused', 'delayed', 'accepted_but_modified']:
                wf.states[decidedState].setProperties(
                    title=decidedState, description='',
                    transitions=['backToItemFrozen', ])
            wf.states['pre_accepted'].setProperties(
                title='pre_accepted', description='',
                transitions=['accept', 'accept_but_modify', 'backToItemFrozen'])
            # Delete state 'published'
            if 'itempublished' in wf.states:
                wf.states.deleteStates(['itempublished'])
            logger.info(WF_APPLIED % ("no_publication", meetingConfig.getId()))
            return True
        return False

    security.declarePublic('getSpecificAssemblyFor')

    def getSpecificAssemblyFor(self, assembly, startTxt=''):
        ''' Return the Assembly between two tag.
            This method is used in templates.
        '''
        # Pierre Dupont - Bourgmestre,
        # Charles Exemple - 1er Echevin,
        # Echevin Un, Echevin Deux excusé, Echevin Trois - Echevins,
        # Jacqueline Exemple, Responsable du CPAS
        # Absentes:
        # Mademoiselle x
        # Excusés:
        # Monsieur Y, Madame Z
        res = []
        tmp = ['<p class="mltAssembly">']
        splitted_assembly = assembly.replace('<p>', '').replace('</p>', '').split('<br />')
        start_text = startTxt == ''
        for assembly_line in splitted_assembly:
            assembly_line = assembly_line.strip()
            # check if this line correspond to startTxt (in this cas, we can begin treatment)
            if not start_text:
                start_text = assembly_line.startswith(startTxt)
                if start_text:
                    # when starting treatment, add tag (not use if startTxt=='')
                    res.append(assembly_line)
                continue
            # check if we must stop treatment...
            if assembly_line.endswith(':'):
                break
            lines = assembly_line.split(',')
            cpt = 1
            my_line = ''
            for line in lines:
                if cpt == len(lines):
                    my_line = "%s%s<br />" % (my_line, line)
                    tmp.append(my_line)
                else:
                    my_line = "%s%s," % (my_line, line)
                cpt = cpt + 1
        if len(tmp) > 1:
            tmp[-1] = tmp[-1].replace('<br />', '')
            tmp.append('</p>')
        else:
            return ''
        res.append(''.join(tmp))
        return res

    def initializeProposingGroupWithGroupInCharge(self):
        """Initialize every items of MeetingConfig for which
           'proposingGroupWithGroupInCharge' is in usedItemAttributes."""
        tool = self.getSelf()
        catalog = api.portal.get_tool('portal_catalog')
        logger.info('Initializing proposingGroupWithGroupInCharge...')
        for cfg in tool.objectValues('MeetingConfig'):
            if 'proposingGroupWithGroupInCharge' in cfg.getUsedItemAttributes():
                brains = catalog(portal_type=cfg.getItemTypeName())
                logger.info('Updating MeetingConfig {0}'.format(cfg.getId()))
                len_brains = len(brains)
                i = 1
                for brain in brains:
                    logger.info('Updating item {0}/{1}'.format(i, len_brains))
                    i = i + 1
                    item = brain.getObject()
                    proposingGroup = item.getProposingGroup(theObject=True)
                    groupsInCharge = proposingGroup.getGroupsInCharge()
                    groupInCharge = groupsInCharge and groupsInCharge[0] or ''
                    value = '{0}__groupincharge__{1}'.format(proposingGroup.getId(),
                                                             groupInCharge)
                    item.setProposingGroupWithGroupInCharge(value)
                    if cfg.getItemGroupInChargeStates():
                        item._updateGroupInChargeLocalRoles()
                        item.reindexObjectSecurity()
                    item.reindexObject(idxs=['getGroupInCharge'])
        logger.info('Done.')


# ------------------------------------------------------------------------------

InitializeClass(CustomMeeting)
InitializeClass(CustomMeetingItem)
InitializeClass(CustomMeetingConfig)
InitializeClass(MeetingCAIDEAWorkflowActions)
InitializeClass(MeetingCAIDEAWorkflowConditions)
InitializeClass(MeetingItemCAIDEAWorkflowActions)
InitializeClass(MeetingItemCAIDEAWorkflowConditions)
InitializeClass(CustomToolPloneMeeting)

# -----------------------------------------------------------------------------


class MeetingIDEAItemPrettyLinkAdapter(ItemPrettyLinkAdapter):
    """
      Override to take into account MeetingIDEA use cases...
    """

    def _leadingIcons(self):
        """
          Manage icons to display before the icons managed by PrettyLink._icons.
        """
        # Default PM item icons
        icons = super(MeetingIDEAItemPrettyLinkAdapter, self)._leadingIcons()

        if self.context.isDefinedInTool():
            return icons

        itemState = self.context.queryState()
        # Add our icons for some review states
        if itemState == 'proposed':
            icons.append(('proposeToDepartmentHead.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_director':
            icons.append(('proposeToDirector.png',
                          translate('icon_help_proposed_to_director',
                                    domain="PloneMeeting",
                                    context=self.request)))
        return icons
