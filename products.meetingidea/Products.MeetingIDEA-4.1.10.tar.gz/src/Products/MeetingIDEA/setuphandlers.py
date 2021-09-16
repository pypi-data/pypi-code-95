# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre Nuyens <andre.nuyens@imio.be>"""
__docformat__ = 'plaintext'


import logging
import os

logger = logging.getLogger('MeetingIDEA: setuphandlers')
from plone import api
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.MeetingIDEA.config import PROJECTNAME


def isNotMeetingIDEAProfile(context):
    return context.readDataFile("MeetingIDEA_marker.txt") is None


def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingIDEAProfile(context):
        return
    wft = api.portal.get_tool('portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingIDEAProfile(context):
        return
    logStep("postInstall", context)
    site = context.getSite()
    # need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    showHomeTab(context, site)
    reorderSkinsLayers(context, site)


def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isMeetingIDEAConfigureProfile(context):
    return context.readDataFile("MeetingIDEA_idea_marker.txt") or \
        context.readDataFile("MeetingIDEA_idea_executive_office_marker.txt") or \
        context.readDataFile("MeetingIDEA_idea_ag_marker.txt") or \
        context.readDataFile("MeetingIDEA_testing_marker.txt")


def isNotMeetingIDEADemoProfile(context):
    return context.readDataFile("MeetingIDEA_demo_marker.txt") is None


def isMeetingIDEATestingProfile(context):
    return context.readDataFile("MeetingIDEA_testing_marker.txt")


def isMeetingIDEAMigrationProfile(context):
    return context.readDataFile("MeetingIDEA_migrations_marker.txt")


def installMeetingIDEA(context):
    """ Run the default profile"""
    if not isMeetingIDEAConfigureProfile(context):
        return
    logStep("installMeetingIDEA", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingIDEA:default')


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if not isMeetingIDEAConfigureProfile(context):
        return

    logStep("initializeTool", context)
    # PloneMeeting is no more a dependency to avoid
    # magic between quickinstaller and portal_setup
    # so install it manually
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example.'''

    if isNotMeetingIDEAProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingIDEAProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reorderSkinsLayers(context, site):
    """
       Re-apply MeetingIDEA skins.xml step as the reinstallation of
       MeetingIDEA and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingIDEAProfile(context) and not isMeetingIDEAConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingIDEA:default', 'skins')


def finalizeExampleInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here
    """
    if not isMeetingIDEAConfigureProfile(context):
        return

    # finalizeExampleInstance will behave differently if on
    # a Commune instance or CPAS instance
    specialUserId = 'president'
    meetingConfig1Id = 'meeting-config-ca'
    meetingConfig2Id = 'meeting-config-ag'

    site = context.getSite()

    logStep("finalizeExampleInstance", context)
    # add the test user 'president' to every '_powerobservers' groups
    mTool = api.portal.get_tool('portal_membership')
    groupsTool = api.portal.get_tool('portal_groups')
    member = mTool.getMemberById(specialUserId)

    if member:
        groupsTool.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig1Id)
        groupsTool.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig2Id)

    # add some topics to the portlet_todo
    mc_ca = getattr(site.portal_plonemeeting, meetingConfig1Id)
    mc_ca.setToDoListSearches(
        [getattr(mc_ca.searches.searches_items, 'searchdecideditems'),
         getattr(mc_ca.searches.searches_items, 'searchitemstovalidate'),
         getattr(mc_ca.searches.searches_items, 'searchallitemsincopy'),
         getattr(mc_ca.searches.searches_items, 'searchallitemstoadvice'),
         ])

    # add some topics to the portlet_todo
    mc_ag = getattr(site.portal_plonemeeting, meetingConfig2Id)
    mc_ag.setToDoListSearches(
        [getattr(mc_ag.searches.searches_items, 'searchdecideditems'),
         getattr(mc_ag.searches.searches_items, 'searchitemstovalidate'),
         getattr(mc_ag.searches.searches_items, 'searchallitemsincopy'),
         getattr(mc_ag.searches.searches_items, 'searchallitemstoadvice'),
         ])

    # finally, re-launch plonemeetingskin and MeetingIDEA skins step
    # because PM has been installed before the import_data profile and messed up skins layers
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingIDEA:default', 'skins')

def addMeetingCDGroup(context):
    """
      Add a Plone group configured to receive Direction Council
      These users can modify the items in prsented state
      This group recieved the MeetingPowerObserverRôle
    """
    if isNotMeetingIDEAProfile(context):
        return
    logStep("addCDGroup", context)
    portal = context.getSite()
    groupId = "meetingCD"
    if not groupId in portal.portal_groups.listGroupIds():
        portal.portal_groups.addGroup(groupId, title=portal.utranslate("meetingCDGroupTitle", domain='PloneMeeting'))
        portal.portal_groups.setRolesForGroup(groupId, ('MeetingObserverGlobal', 'MeetingCD'))
