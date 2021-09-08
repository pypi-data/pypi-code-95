from Utils.PanelState import PanelState
from Utils.PanelSettings import PanelSettings
from Utils.StateDevice import StateDevice
from Utils.User import User


class AlarmStatus(object):
    def __init__(self, inputDict, api):
        self.PanelId = inputDict["panelInfo"]["PanelId"]
        self.Name = inputDict["panelInfo"]["Name"]
        self.PanelSettings = PanelSettings(inputDict["panelSettings"])
        self.PanelState = PanelState(inputDict["panelState"], self.PanelSettings.TimeZone)
        self.StateDevices = [
            StateDevice(device, self.PanelSettings.TimeZone) for device in inputDict["stateDevices"]
        ]
        self.SystemState = PanelState(inputDict["systemState"], self.PanelSettings.TimeZone)
        self.Users = [User(user, api) for user in inputDict["users"]]
        
