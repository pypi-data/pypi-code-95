from datetime import datetime
from g4s.utils.time_zone import TimeZone
from g4s.utils.enums import DeviceType
from typing import Any, Optional, Dict


class StateDevice:
    def __init__(self, input_dict: Dict[str, Any], timeZone: TimeZone) -> None:
        self.key: Optional[int] = input_dict["key"]
        self.is_tampered: Optional[bool] = input_dict["isTampered"]
        self.has_low_battery: Optional[bool] = input_dict["hasLowBattery"]
        self.has_supervision_fault: Optional[bool] = input_dict["hasSupervisionFault"]
        self.is_open: Optional[bool] = input_dict["isOpen"]
        self.is_locked: bool = input_dict["isLocked"]
        self.is_lockout: Optional[bool] = input_dict["isLockout"]
        self.is_triggered_alarm: bool = input_dict["isTriggeredAlarm"]
        self.alarm_type: int = input_dict["alarmType"]
        self.user_name: Optional[str] = input_dict["userName"]
        self.serial_number: str = input_dict["serialNumber"]
        self.day_partition: bool = input_dict["dayPartition"]
        self.night_partition: bool = input_dict["nightPartition"]
        self.rf_level: Optional[int] = input_dict["rfLevel"]
        self.battery_level: Optional[int] = input_dict["batteryLevel"]
        self.temperature_level: Optional[int] = input_dict["temperatureLevel"]
        self.sub_type: Optional[int] = input_dict["subType"]
        self.attributes: Dict[str, Any] = input_dict["attributes"]
        self.hardware_device_type: Optional[int] = input_dict["hardwareDeviceType"]
        self.role_group_id: int = input_dict["roleGroupId"]
        self.bypass_state: int = input_dict["bypassState"]
        self.lock_changed_by_user: Any = input_dict["lockChangedByUser"]
        self.lock_changed_by_device_number: Any = input_dict["lockChangedByDeviceNumber"]
        self.lock_changed_by_device_type: Any = input_dict["lockChangedByDeviceType"]
        self.associated_output_type: Optional[int] = input_dict["associatedOutputType"]
        self.associated_output_id: Any = input_dict["associatedOutputId"]
        self.owner: Optional[int] = input_dict["owner"]
        self.panel_update_time: Optional[datetime] = timeZone.date_time_as_utc(input_dict["panelUpdateTime"])
        self.update_time: Optional[datetime] = timeZone.date_time_as_utc(input_dict["updateTime"])
        self.chime: bool = input_dict["chime"]
        self.security_mode: Optional[int] = input_dict["securityMode"]
        self.is_outdoor_mode: Optional[bool] = input_dict["isOutdoorMode"]
        self.is_beep_enable: Optional[bool] = input_dict["isBeepEnable"]
        self.full_exit_beeps_enabled: Optional[bool] = input_dict["fullExitBeepsEnabled"]
        self.door_bell_enabled: Optional[bool] = input_dict["doorBellEnabled"]
        self.sub_device_type: Any = input_dict["subDeviceType"]
        self.panel_device_id: Any = input_dict["panelDeviceId"]
        self.is_normally_open: Any = input_dict["isNormallyOpen"]
        self.is_pulse_device: Any = input_dict["isPulseDevice"]
        self.ut_device_type: Any = input_dict["utDeviceType"]
        self.additional_data: Any = input_dict["additionalData"]
        self.added_or_reset_time: Optional[datetime] = timeZone.date_time_as_utc(input_dict["addedOrResetTime"])
        self.pk_id: int = input_dict["PkId"]
        self.id: int = input_dict["Id"]
        self.type_id: int = input_dict["Type"]
        self.type: DeviceType = DeviceType(input_dict["Type"])
        self.name: str = input_dict["Name"]
        self.parent_device_id: Any = input_dict["ParentDeviceId"]
        self.panel_id: int = input_dict["PanelId"]
        self.access_code: Optional[str] = input_dict.get("AccessCode")
        self.pet_immune: Optional[bool] = input_dict.get("petImmune")

    def __str__(self) -> str:
        return f"{self.name} - {self.type.name}"

    def __repr__(self) -> str:
        return str(self)
