from g4s.utils.panel_state import PanelState
from g4s.utils.panel_settings import PanelSettings
from g4s.utils.state_device import StateDevice
from g4s.utils.user import User


class AlarmStatus:
    def __init__(self, input_dict, api):
        self.panel_id = input_dict["panelInfo"]["PanelId"]
        self.name = input_dict["panelInfo"]["Name"]
        self.panel_settings = PanelSettings(input_dict["panelSettings"])
        self.panel_state = PanelState(
            input_dict["panelState"], self.panel_settings.time_zone
        )
        self.state_devices = [
            StateDevice(device, self.panel_settings.time_zone)
            for device in input_dict["stateDevices"]
        ]
        self.system_state = PanelState(
            input_dict["systemState"], self.panel_settings.time_zone
        )
        self.users = [User(user, api) for user in input_dict["users"]]
