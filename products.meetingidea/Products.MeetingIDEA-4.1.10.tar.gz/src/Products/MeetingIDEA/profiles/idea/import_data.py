# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data

data = deepcopy(mc_import_data.data)

# Remove persons -------------------------------------------------
data.persons = []

# No Users and groups -----------------------------------------------

# Meeting configurations -------------------------------------------------------
# CA
caMeeting = deepcopy(mc_import_data.collegeMeeting)
caMeeting.id = "meeting-config-ca"
caMeeting.title = "CA"
caMeeting.shortName = "CA"
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
caMeeting.id = "meeting-config-ag"
caMeeting.title = "AG"
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