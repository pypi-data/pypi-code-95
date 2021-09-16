# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.simple import import_data as simple_import_data
from Products.PloneMeeting.profiles import PloneMeetingConfiguration


config = deepcopy(simple_import_data.simpleMeeting)
config.id = 'meeting-config-executive'
config.title = 'Bureau exécutif'
config.folderTitle = 'Bureau exécutif'
config.shortName = 'Executive'

config.workflowAdaptations = ['return_to_proposing_group']


config.itemWorkflow = "meetingitemcaidea_workflow"
config.meetingWorkflow = "meetingcaidea_workflow"
config.itemConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowConditions"
)
config.itemActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingItemCAIDEAWorkflowActions"
)
config.meetingConditionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowConditions"
)
config.meetingActionsInterface = (
    "Products.MeetingIDEA.interfaces.IMeetingCAIDEAWorkflowActions"
)
config.transitionsToConfirm = []
config.transitionsForPresentingAnItem = [
    "proposeToDepartmentHead",
    "proposeToDirector",
    "validate",
    "present",
]

data = PloneMeetingConfiguration(
    meetingFolderTitle='Mes séances',
    meetingConfigs=(config, ),
    orgs=[])
