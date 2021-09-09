from Utils.TimeZone import TimeZone
from Utils.StaticUtils import StaticUtils
from Utils.Enums import DeviceType


class StateDevice(object):
    def __init__(self, inputDict, timeZone: TimeZone):
        self.Key = inputDict["key"]
        self.IsTampered = inputDict["isTampered"]
        self.HasLowBattery = inputDict["hasLowBattery"]
        self.HasSupervisionFault = inputDict["hasSupervisionFault"]
        self.IsOpen = inputDict["isOpen"]
        self.IsLocked = inputDict["isLocked"]
        self.IsLockout = inputDict["isLockout"]
        self.IsTriggeredAlarm = inputDict["isTriggeredAlarm"]
        self.AlarmType = inputDict["alarmType"]
        self.UserName = inputDict["userName"]
        self.SerialNumber = inputDict["serialNumber"]
        self.DayPartition = inputDict["dayPartition"]
        self.NightPartition = inputDict["nightPartition"]
        self.RfLevel = inputDict["rfLevel"]
        self.BatteryLevel = inputDict["batteryLevel"]
        self.TemperatureLevel = inputDict["temperatureLevel"]
        self.SubType = inputDict["subType"]
        self.Attributes = inputDict["attributes"]
        self.HardwareDeviceType = inputDict["hardwareDeviceType"]
        self.RoleGroupId = inputDict["roleGroupId"]
        self.BypassState = inputDict["bypassState"]
        self.LockChangedByUser = inputDict["lockChangedByUser"]
        self.LockChangedByDeviceNumber = inputDict["lockChangedByDeviceNumber"]
        self.LockChangedByDeviceType = inputDict["lockChangedByDeviceType"]
        self.AssociatedOutputType = inputDict["associatedOutputType"]
        self.AssociatedOutputId = inputDict["associatedOutputId"]
        self.Owner = inputDict["owner"]
        self.PanelUpdateTime = timeZone.DateTimeAsUTC(inputDict["panelUpdateTime"])
        self.UpdateTime = timeZone.DateTimeAsUTC(inputDict["updateTime"])
        self.Chime = inputDict["chime"]
        self.SecurityMode = inputDict["securityMode"]
        self.IsOutdoorMode = inputDict["isOutdoorMode"]
        self.IsBeepEnable = inputDict["isBeepEnable"]
        self.FullExitBeepsEnabled = inputDict["fullExitBeepsEnabled"]
        self.DoorBellEnabled = inputDict["doorBellEnabled"]
        self.SubDeviceType = inputDict["subDeviceType"]
        self.PanelDeviceId = inputDict["panelDeviceId"]
        self.IsNormallyOpen = inputDict["isNormallyOpen"]
        self.IsPulseDevice = inputDict["isPulseDevice"]
        self.UtDeviceType = inputDict["utDeviceType"]
        self.AdditionalData = inputDict["additionalData"]
        self.AddedOrResetTime = timeZone.DateTimeAsUTC(inputDict["addedOrResetTime"])
        self.PkId = inputDict["PkId"]
        self.Id = inputDict["Id"]
        self.TypeId = inputDict["Type"]
        self.Type = DeviceType(inputDict["Type"])
        self.Name = inputDict["Name"]
        self.ParentDeviceId = inputDict["ParentDeviceId"]
        self.PanelId = inputDict["PanelId"]

    def __str__(self) -> str:
        return f"{self.Name} - {self.Type.name}"

    def __repr__(self) -> str:
        return str(self)
