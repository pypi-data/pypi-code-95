# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#
from Products.MeetingCommunes.browser.overrides import (
    MCItemDocumentGenerationHelperView,
    MCMeetingDocumentGenerationHelperView,
)
from collective.contact.plonegroup.utils import get_organizations


class MCBaseDocumentGenerationHelperView(object):

    def __init__(self, context, request):
        self.DptForItem_by_group_id = {}
        self.DptPos_by_group_id = {}
        self.CountDptItems_by_dpt_id = {}
        self.serviceIsEmpty_by_group_id = {}
        self.servicePos_by_group_id = {}
        self.Dpt_by_group_id = {}
        self.ItemPosInCategorie_by_item_uid = {}
        super(MCBaseDocumentGenerationHelperView, self).__init__(context, request)

    def getIdeaAssembly(self, filter):
        '''return formated assembly
           filer is 'present', 'excused', 'procuration', 'absent' or '*' for all
           This method is used on template
        '''
        if self.context.meta_type == 'Meeting':
            assembly = self.context.getAssembly().replace('<p>', '').replace('</p>', '')
        else:
            assembly = self.context.getItemAssembly().replace('<p>', '').replace('</p>', '')
        assembly = assembly.split('<br />')
        res = []
        status = 'present'
        for ass in assembly:
            # ass line "Excusé:" is used for define list of persons who are excused
            if ass.find('xcus') >= 0:
                status = 'excused'
                continue
            # ass line "Procurations:" is used for defined list of persons who recieve a procuration
            if ass.upper().find('PROCURATION') >= 0:
                status = 'procuration'
                continue
            # ass line "Absents:" is used for define list of persons who are excused
            if ass.upper().find('ABSENT') >= 0:
                status = 'absentee'
                continue
            if filter == '*' or status == filter:
                res.append(ass)
        return res

    # TODO Totally inefficient methods used in PODTemplates that need to be refactored... some day

    def getCountDptItems(self, meeting=None, dptid='', late=False):
        if dptid in self.CountDptItems_by_dpt_id.keys():
            return self.CountDptItems_by_dpt_id[dptid]
        long = 0
        listTypes = ['late'] if late else ['normal']
        for sublist in meeting.adapted().getPrintableItemsByCategory(listTypes=listTypes):
            if sublist[0].id == dptid:
                long = len(sublist) - 1  # remove categories
                break
        self.CountDptItems_by_dpt_id[dptid] = long
        return long

    def getDepartment(self, group):
        # return position, title and class for department
        if group.id in self.Dpt_by_group_id.keys():
            return self.Dpt_by_group_id[group.id]
        cpt_dpt = self.getDptPos(group.id)
        res = '%d. %s' % (cpt_dpt, group.Title())
        self.Dpt_by_group_id[group.id] = res
        return res

    def getDptForItem(self, groupid):
        # return department
        if groupid in self.DptForItem_by_group_id.keys():
            return self.DptForItem_by_group_id[groupid]
        res = ''
        groups = get_organizations()
        for group in groups:
            acronym = group.get_acronym()
            if acronym.find('-') < 0:
                res = group.id
            if group.id == groupid:
                break
        self.DptForItem_by_group_id[groupid] = res
        return res

    def getDptPos(self, groupid):
        # return department position in active groups list
        if groupid in self.DptPos_by_group_id.keys():
            return self.DptPos_by_group_id[groupid]
        groups = get_organizations()
        cpt_dpt = 0
        for group in groups:
            acronym = group.get_acronym()
            if acronym.find('-') < 0:
                cpt_dpt = cpt_dpt + 1
            if group.id == groupid:
                break
        res = cpt_dpt
        self.DptPos_by_group_id[groupid] = res
        return res

    def getItemPosInCategorie(self, item=None, late=False):
        if not item:
            return ''
        if item.UID() in self.ItemPosInCategorie_by_item_uid.keys():
            return self.ItemPosInCategorie_by_item_uid[item.UID()]
        meeting = item.getMeeting()
        pg = item.getProposingGroup()
        if late:
            cpt = self.getItemPosInCategorie(item, False)
        else:
            cpt = 1
        listTypes = ['late'] if late else ['normal']
        for sublist in meeting.adapted().getIDEAPrintableItemsByCategory(listTypes=listTypes):
            for elt in sublist[1:]:
                if elt.id == item.id:
                    break
                if elt.getProposingGroup() == pg:
                    cpt = cpt + 1

        self.ItemPosInCategorie_by_item_uid[item.UID()] = cpt
        return cpt

    def getServiceIsEmpty(self, groupid, meeting=None, late=False):
        if groupid in self.serviceIsEmpty_by_group_id.keys():
            return self.serviceIsEmpty_by_group_id[groupid]
        listTypes = ['late'] if late else ['normal']
        isEmpty = True
        for sublist in meeting.adapted().getIDEAPrintableItemsByCategory(listTypes=listTypes):
            if sublist[0].id == groupid:
                isEmpty = len(sublist) <= 1
                break
        self.serviceIsEmpty_by_group_id[groupid] = isEmpty
        return isEmpty

    def getServicePos(self, group, meeting=None, late=False):
        # return service position in active groups list incremented by item for department
        groupid = group.id
        if groupid in self.servicePos_by_group_id.keys():
            return self.servicePos_by_group_id[groupid]
        cpt_srv = 0
        groups = get_organizations()
        for gr in groups:
            acronym = gr.get_acronym()
            if acronym.find('-') >= 0:
                # only increment if no empty service and not current group
                if (gr.id != groupid) and (not self.getServiceIsEmpty(gr.id, meeting, late)):
                    cpt_srv = cpt_srv + 1
            else:  # new department, reset numbering
                cpt_srv = 1
            if gr.id == groupid:
                break
        dptid = self.getDptForItem(group.id)
        cpt_srv = cpt_srv + self.getCountDptItems(meeting, dptid, late)
        self.servicePos_by_group_id[groupid] = cpt_srv
        return cpt_srv


class MIDEAItemDocumentGenerationHelperView(
    MCBaseDocumentGenerationHelperView, MCItemDocumentGenerationHelperView
):
    """Specific printing methods used for item."""


class MIDEAMeetingDocumentGenerationHelperView(
    MCBaseDocumentGenerationHelperView, MCMeetingDocumentGenerationHelperView
):
    """Specific printing methods used for meeting."""
