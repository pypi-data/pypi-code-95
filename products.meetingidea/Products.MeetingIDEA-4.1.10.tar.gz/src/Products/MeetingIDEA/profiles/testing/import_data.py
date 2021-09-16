# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.PloneMeeting.config import MEETINGREVIEWERS
from Products.PloneMeeting.profiles import UserDescriptor

data = deepcopy(mc_import_data.data)

# Users and groups -------------------------------------------------------------
pmCreator1 = UserDescriptor(
    "pmCreator1", [], email="pmcreator1@plonemeeting.org", fullname="M. PMCreator One"
)
pmCreator1b = UserDescriptor(
    "pmCreator1b",
    [],
    email="pmcreator1b@plonemeeting.org",
    fullname="M. PMCreator One bee",
)
pmObserver1 = UserDescriptor(
    "pmObserver1",
    [],
    email="pmobserver1@plonemeeting.org",
    fullname="M. PMObserver One",
)
pmCreator2 = UserDescriptor("pmCreator2", [])
pmAdviser1 = UserDescriptor("pmAdviser1", [])
pmDepartmentHead1 = UserDescriptor("pmDepartmentHead1", [])
pmDirector1 = UserDescriptor("pmDirector1", [])
pmDirector2 = UserDescriptor("pmDirector2", [])
powerobserver1 = UserDescriptor(
    "powerobserver1",
    [],
    email="powerobserver1@plonemeeting.org",
    fullname="M. Power Observer1",
)

# Inherited users
pmReviewer1 = deepcopy(pm_import_data.pmReviewer1)
pmReviewer2 = deepcopy(pm_import_data.pmReviewer2)
pmReviewerLevel1 = deepcopy(pm_import_data.pmReviewerLevel1)
pmReviewerLevel2 = deepcopy(pm_import_data.pmReviewerLevel2)
pmManager = deepcopy(pm_import_data.pmManager)


developers = data.orgs[0]
developers.creators.append(pmCreator1)
developers.creators.append(pmCreator1b)
developers.creators.append(pmManager)
developers.observers.append(pmObserver1)
developers.observers.append(pmReviewer1)
developers.observers.append(pmManager)
developers.advisers.append(pmAdviser1)
developers.advisers.append(pmManager)
developers.departmentheads.append(pmDepartmentHead1)
developers.departmentheads.append(pmManager)
developers.reviewers.append(pmReviewer1)
developers.reviewers.append(pmDirector1)
developers.reviewers.append(pmManager)
# reviewers

setattr(developers, "signatures", "developers signatures")
setattr(developers, "echevinServices", "developers")
# put pmReviewerLevel1 in first level of reviewers from what is in MEETINGREVIEWERS
getattr(developers, MEETINGREVIEWERS["meetingitemcaidea_workflow"].keys()[-1]).append(
    pmReviewerLevel1
)
# put pmReviewerLevel2 in second level of reviewers from what is in MEETINGREVIEWERS
getattr(developers, MEETINGREVIEWERS["meetingitemcaidea_workflow"].keys()[0]).append(
    pmReviewerLevel2
)

vendors = data.orgs[1]
vendors.creators.append(pmCreator2)
vendors.reviewers.append(pmReviewer2)
vendors.observers.append(pmReviewer2)
vendors.advisers.append(pmReviewer2)
vendors.advisers.append(pmManager)
setattr(vendors, "signatures", "")

# Meeting configurations -------------------------------------------------------
# CA

caMeeting = deepcopy(mc_import_data.collegeMeeting)
caMeeting.id = "meeting-config-ca"
caMeeting.title = "CA"
caMeeting.itemWorkflow = "meetingitemcaidea_workflow"
caMeeting.meetingWorkflow = "meetingcaidea_workflow"
caMeeting.itemConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowConditions"
)
caMeeting.itemActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowActions"
)
caMeeting.meetingConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowConditions"
)
caMeeting.meetingActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowActions"
)
caMeeting.transitionsToConfirm = []
caMeeting.transitionsForPresentingAnItem = [
    "proposeToDepartmentHead",
    "proposeToDirector",
    "validate",
    "present",
]
caMeeting.workflowAdaptations = []
caMeeting.useAdvices = True
caMeeting.selectableAdvisers = ["developers", "vendors"]
caMeeting.itemAdviceStates = ["proposed_to_director"]
caMeeting.itemAdviceEditStates = ["proposed_to_director", "validated"]
caMeeting.itemAdviceViewStates = ["presented"]

# AG
agMeeting = deepcopy(mc_import_data.councilMeeting)
agMeeting.id = "meeting-config-ag"
agMeeting.title = "AG"
agMeeting.itemWorkflow = "meetingitemcaidea_workflow"
agMeeting.meetingWorkflow = "meetingcaidea_workflow"
agMeeting.itemConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowConditions"
)
agMeeting.itemActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowActions"
)
agMeeting.meetingConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowConditions"
)
agMeeting.meetingActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowActions"
)
agMeeting.transitionsToConfirm = []
agMeeting.transitionsForPresentingAnItem = [
    "proposeToDepartmentHead",
    "proposeToDirector",
    "validate",
    "present",
]
agMeeting.workflowAdaptations = []
agMeeting.useAdvices = False
agMeeting.selectableAdvisers = []
agMeeting.itemAdviceStates = ["proposed_to_director"]
agMeeting.itemAdviceEditStates = ["proposed_to_director", "validated"]
agMeeting.itemAdviceViewStates = ["presented"]
agMeeting.itemCopyGroupsStates = []

data.meetingConfigs = (caMeeting, agMeeting)
