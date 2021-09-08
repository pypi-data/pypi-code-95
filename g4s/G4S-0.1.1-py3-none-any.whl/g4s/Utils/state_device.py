from g4s.utils.time_zone import TimeZone
from g4s.utils.enums import DeviceType


class StateDevice:
    def __init__(self, inputDict, timeZone: TimeZone):
        self.key = inputDict["key"]
        self.is_tampered = inputDict["isTampered"]
        self.has_low_battery = inputDict["hasLowBattery"]
        self.has_supervision_fault = inputDict["hasSupervisionFault"]
        self.is_open = inputDict["isOpen"]
        self.is_locked = inputDict["isLocked"]
        self.is_lockout = inputDict["isLockout"]
        self.is_triggered_alarm = inputDict["isTriggeredAlarm"]
        self.alarm_type = inputDict["alarmType"]
        self.user_name = inputDict["userName"]
        self.serial_number = inputDict["serialNumber"]
        self.day_partition = inputDict["dayPartition"]
        self.night_partition = inputDict["nightPartition"]
        self.rf_level = inputDict["rfLevel"]
        self.battery_level = inputDict["batteryLevel"]
        self.temperature_level = inputDict["temperatureLevel"]
        self.sub_type = inputDict["subType"]
        self.attributes = inputDict["attributes"]
        self.hardware_device_type = inputDict["hardwareDeviceType"]
        self.role_group_id = inputDict["roleGroupId"]
        self.bypass_state = inputDict["bypassState"]
        self.lock_changed_by_user = inputDict["lockChangedByUser"]
        self.lock_changed_by_device_number = inputDict["lockChangedByDeviceNumber"]
        self.lock_changed_by_device_type = inputDict["lockChangedByDeviceType"]
        self.associated_output_type = inputDict["associatedOutputType"]
        self.associated_output_id = inputDict["associatedOutputId"]
        self.owner = inputDict["owner"]
        self.panel_update_time = timeZone.date_time_as_utc(inputDict["panelUpdateTime"])
        self.update_time = timeZone.date_time_as_utc(inputDict["updateTime"])
        self.chime = inputDict["chime"]
        self.security_mode = inputDict["securityMode"]
        self.is_outdoor_mode = inputDict["isOutdoorMode"]
        self.is_beep_enable = inputDict["isBeepEnable"]
        self.full_exit_beeps_enabled = inputDict["fullExitBeepsEnabled"]
        self.door_bell_enabled = inputDict["doorBellEnabled"]
        self.sub_device_type = inputDict["subDeviceType"]
        self.panel_device_id = inputDict["panelDeviceId"]
        self.is_normally_open = inputDict["isNormallyOpen"]
        self.is_pulse_device = inputDict["isPulseDevice"]
        self.ut_device_type = inputDict["utDeviceType"]
        self.additional_data = inputDict["additionalData"]
        self.added_or_reset_time = timeZone.date_time_as_utc(inputDict["addedOrResetTime"])
        self.pk_id = inputDict["PkId"]
        self.id = inputDict["Id"]
        self.type_id = inputDict["Type"]
        self.type = DeviceType(inputDict["Type"])
        self.name = inputDict["Name"]
        self.parent_device_id = inputDict["ParentDeviceId"]
        self.panel_id = inputDict["PanelId"]

    def __str__(self) -> str:
        return f"{self.name} - {self.type.name}"

    def __repr__(self) -> str:
        return str(self)
