from typing import Any, Dict, List
from g4s.utils.panel_state import PanelState
from g4s.utils.panel_settings import PanelSettings
from g4s.utils.state_device import StateDevice
from g4s.utils.user import User
from g4s.utils.api import API


class AlarmStatus:
    def __init__(self, input_dict: Dict[str, Any], api: API) -> None:
        self.panel_id: int = input_dict["panelInfo"]["PanelId"]
        self.name: str = input_dict["panelInfo"]["Name"]
        self.panel_settings: PanelSettings = PanelSettings(input_dict["panelSettings"])
        self.panel_state: PanelState = PanelState(input_dict["panelState"], self.panel_settings.time_zone)
        self.state_devices: List[StateDevice] = [
            StateDevice(device, self.panel_settings.time_zone) for device in input_dict["stateDevices"]
        ]
        self.system_state: PanelState = PanelState(input_dict["systemState"], self.panel_settings.time_zone)
        self.users: List[User] = [User(user, api, self.panel_settings.time_zone) for user in input_dict["users"]]
