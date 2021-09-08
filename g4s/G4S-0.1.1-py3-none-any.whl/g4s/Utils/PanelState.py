from Utils.TimeZone import TimeZone
from Utils.Enums import ArmType
from Utils.StaticUtils import StaticUtils


class PanelState(object):
    def __init__(self, inputDict: dict, timeZone: TimeZone):
        self.ArmType = ArmType(inputDict.get("ArmType"))
        self.ArmTypeChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("ArmTypeChangedTime")
        )
        self.ArmForcedState = inputDict.get("ArmForcedState")
        self.ArmDelayedState = inputDict.get("ArmDelayedState")
        self.AlarmState = inputDict.get("AlarmState")
        self.AlarmStateTime = timeZone.DateTimeAsUTC(inputDict.get("AlarmStateTime"))
        self.Partition = inputDict.get("Partition")
        self.DeviceName = inputDict.get("DeviceName")
        self.ExitDelayArmInProcess = inputDict.get("ExitDelayArmInProcess")
        self.EntryDelayArmInProcess = inputDict.get("EntryDelayArmInProcess")
        self.ReceptionLevel = inputDict.get("ReceptionLevel")
        self.ReceptionLevelChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("ReceptionLevelChangedTime")
        )
        self.PanelBatteryLevel = inputDict.get("PanelBatteryLevel")
        self.IsPanelOffline = inputDict.get("IsPanelOffline")
        self.IsPanelOfflineChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("IsPanelOfflineChangedTime")
        )
        self.IsZWaveEnabled = inputDict.get("IsZWaveEnabled")
        self.IsZWaveEnabledChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("IsZWaveEnabledChangedTime")
        )
        self.IsMainPowerConnected = inputDict.get("IsMainPowerConnected")
        self.IsMainPowerConnectedChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("IsMainPowerConnectedChangedTime")
        )
        self.IsSimCardReady = inputDict.get("IsSimCardReady")
        self.CommunicationLink = inputDict.get("CommunicationLink")
        self.BackupChannelStatus = inputDict.get("BackupChannelStatus")
        self.BackupChannelStatusDescription = inputDict.get(
            "BackupChannelStatusDescription"
        )
        self.HasLowBattery = inputDict.get("HasLowBattery")
        self.HasLowBatteryChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("HasLowBatteryChangedTime")
        )
        self.SetupMode = inputDict.get("SetupMode")
        self.SirensVolumeLevel = inputDict.get("SirensVolumeLevel")
        self.SirensDuration = inputDict.get("SirensDuration")
        self.SirensVolumeLevelDurationChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("SirensVolumeLevelDurationChangedTime")
        )
        self.IsInInstallationMode = inputDict.get("IsInInstallationMode")
        self.IsInInstallationModeChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("IsInInstallationModeChangedTime")
        )
        self.IsInSignalStrengthTest = inputDict.get("IsInSignalStrengthTest")
        self.IsInSignalStrengthTestChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("IsInSignalStrengthTestChangedTime")
        )
        self.PanelId = inputDict.get("PanelId")
        self.IsSynchronized = inputDict.get("IsSynchronized")
        self.SirensEntryExitDuration = inputDict.get("SirensEntryExitDuration")
        self.FrtState = inputDict.get("FrtState")
        self.FrtStateChangedTime = timeZone.DateTimeAsUTC(
            inputDict.get("FrtStateChangedTime")
        )
