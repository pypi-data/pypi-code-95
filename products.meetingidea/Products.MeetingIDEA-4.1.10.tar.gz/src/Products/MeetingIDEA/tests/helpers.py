# -*- coding: utf-8 -*-
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

from Products.MeetingCommunes.tests.helpers import MeetingCommunesTestingHelpers

from DateTime import DateTime


class MeetingIDEATestingHelpers(MeetingCommunesTestingHelpers):
    """Stub class that provides some helper methods about testing."""

    TRANSITIONS_FOR_PROPOSING_ITEM_1 = ('proposeToDepartmentHead', 'proposeToDirector',)
    TRANSITIONS_FOR_PROPOSING_ITEM_2 = ('validate', 'backToProposedToDirector',)
    TRANSITIONS_FOR_VALIDATING_ITEM_1 = ('proposeToDepartmentHead', 'proposeToDirector', 'validate',)
    TRANSITIONS_FOR_VALIDATING_ITEM_2 = ('validate',)
    TRANSITIONS_FOR_PRESENTING_ITEM_1 = ('proposeToDepartmentHead', 'proposeToDirector', 'validate', 'present',)
    TRANSITIONS_FOR_PRESENTING_ITEM_2 = ('validate', 'present',)
    TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_1 = ('freeze', 'decide',)
    TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_2 = ('freeze', 'decide',)
    TRANSITIONS_FOR_ACCEPTING_ITEMS_1 = ('freeze', 'decide',)
    TRANSITIONS_FOR_ACCEPTING_ITEMS_2 = ('freeze', 'decide',)

    TRANSITIONS_FOR_FREEZING_MEETING_1 = TRANSITIONS_FOR_FREEZING_MEETING_2 = ('freeze',)
    TRANSITIONS_FOR_PUBLISHING_MEETING_1 = TRANSITIONS_FOR_PUBLISHING_MEETING_2 = ('freeze', 'decide', 'publish',)
    TRANSITIONS_FOR_DECIDING_MEETING_1 = ('freeze', 'decide',)
    TRANSITIONS_FOR_DECIDING_MEETING_2 = ('freeze', 'decide',)
    TRANSITIONS_FOR_CLOSING_MEETING_1 = ('freeze', 'decide', 'publish', 'close',)
    TRANSITIONS_FOR_CLOSING_MEETING_2 = ('freeze', 'decide', 'publish', 'close',)
    BACK_TO_WF_PATH_1 = {
        # Meeting
        'created': ('backToPublished',
                    'backToDecided',
                    'backToFrozen',
                    'backToCreated',),
        # MeetingItem
        'itemcreated': ('backToItemFrozen',
                        'backToPresented',
                        'backToValidated',
                        'backToProposedToDirector',
                        'backToProposedToDepartmentHead',
                        'backToItemCreated'),
        'proposed_to_director': ('backToItemFrozen',
                                 'backToPresented',
                                 'backToValidated',
                                 'backToProposedToDirector',),
        'validated': ('backToItemFrozen',
                      'backToPresented',
                      'backToValidated'),

        'presented': ('backToItemFrozen',
                      'backToPresented',)}
    BACK_TO_WF_PATH_2 = {
        # MeetingItem
        'itemcreated': ('backToItemFrozen',
                        'backToPresented',
                        'backToValidated',
                        'backToProposedToDirector',
                        'backToProposedToDepartmentHead',
                        'backToItemCreated'),
        'proposed_to_director': ('backToItemFrozen',
                                 'backToPresented',
                                 'backToValidated',
                                 'backToProposedToDirector',),
        'validated': ('backToItemFrozen',
                      'backToPresented',
                      'backToValidated',),

        'presented': ('backToItemFrozen',
                      'backToPresented',)}

    WF_ITEM_STATE_NAME_MAPPINGS_1 = WF_ITEM_STATE_NAME_MAPPINGS_2 = {'itemcreated': 'itemcreated',
                                                                     'proposed': 'proposed_to_director',
                                                                     'proposed_to_director': 'proposed_to_director',
                                                                     'validated': 'validated',
                                                                     'presented': 'presented'}

    # in which state an item must be after an particular meeting transition?
    ITEM_WF_STATE_AFTER_MEETING_TRANSITION = {'publish_decisions': 'accepted',
                                              'close': 'accepted'}
