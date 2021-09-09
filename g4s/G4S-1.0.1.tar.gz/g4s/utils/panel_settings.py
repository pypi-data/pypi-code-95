from typing import Any, Optional
from g4s.utils.time_zone import TimeZone
from g4s.utils.state_device import StateDevice


class PanelSettings:
    def __init__(self, input_dict: dict[str, Any]) -> None:
        self.time_zone: TimeZone = TimeZone(input_dict["TimeZone"])
        self.offset_from_utc_in_minutes: int = input_dict["OffsetFromUtcInMinutes"]
        self.temperature_unit: int = input_dict["OffsetFromUtcInMinutes"]
        self.default_temperature_device_id: int = input_dict["DefaultTemperatureDevice"]["Id"]
        self.default_temperature_device: Optional[StateDevice] = None
        self.installed_modules: int = input_dict["InstalledModules"]
        self.primary_link: int = input_dict["PrimaryLink"]
        self.available_delay_times: list[int] = input_dict["AvailableDelayTimes"]
        self.tag_access_code_min_length: int = input_dict["TagAccessCodeMinLength"]
        self.tag_access_code_max_length: int = input_dict["TagAccessCodeMaxLength"]
        self.tag_access_code_available_lengths: list[int] = input_dict["TagAccessCodeAvailableLengths"]
        self.tguard_access_code_length: int = input_dict["GuardAccessCodeLength"]
