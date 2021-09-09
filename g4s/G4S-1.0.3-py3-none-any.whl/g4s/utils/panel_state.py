from datetime import datetime
from typing import Any, Optional, Dict
from g4s.utils.time_zone import TimeZone
from g4s.utils.enums import ArmType


class PanelState:
    def __init__(self, input_dict: Dict[str, Any], time_zone: TimeZone) -> None:
        self.arm_type: ArmType = ArmType(input_dict["ArmType"])
        self.arm_type_changed_time: Optional[datetime] = time_zone.date_time_as_utc(input_dict["ArmTypeChangedTime"])
        self.arm_forced_state: int = input_dict["ArmForcedState"]
        self.arm_delayed_state: int = input_dict["ArmDelayedState"]
        self.alarm_state: int = input_dict["AlarmState"]
        self.alarm_state_time: Optional[datetime] = time_zone.date_time_as_utc(input_dict["AlarmStateTime"])
        self.partition: int = input_dict["Partition"]
        self.device_name: Any = input_dict["DeviceName"]
        self.exit_delay_arm_in_process: bool = input_dict["ExitDelayArmInProcess"]
        self.entry_delay_arm_in_process: bool = input_dict["EntryDelayArmInProcess"]
        self.reception_level: int = input_dict["ReceptionLevel"]
        self.reception_level_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["ReceptionLevelChangedTime"]
        )
        self.panel_battery_level: int = input_dict["PanelBatteryLevel"]
        self.is_panel_offline: bool = input_dict["IsPanelOffline"]
        self.is_panel_offline_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["IsPanelOfflineChangedTime"]
        )
        self.is_z_wave_enabled: bool = input_dict["IsZWaveEnabled"]
        self.is_z_wave_enabled_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["IsZWaveEnabledChangedTime"]
        )
        self.is_main_power_connected: bool = input_dict["IsMainPowerConnected"]
        self.is_main_power_connected_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["IsMainPowerConnectedChangedTime"]
        )
        self.is_sim_card_ready: bool = input_dict["IsSimCardReady"]
        self.communication_link: int = input_dict["CommunicationLink"]
        self.backup_channel_status: int = input_dict["BackupChannelStatus"]
        self.backup_channel_status_description: int = input_dict["BackupChannelStatusDescription"]

        self.has_low_battery: bool = input_dict["HasLowBattery"]
        self.has_low_battery_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["HasLowBatteryChangedTime"]
        )
        self.setup_mode: bool = input_dict["SetupMode"]
        self.sirens_volume_level: int = input_dict["SirensVolumeLevel"]
        self.sirens_duration: int = input_dict["SirensDuration"]
        self.sirens_volume_level_duration_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["SirensVolumeLevelDurationChangedTime"]
        )
        self.is_in_installation_mode: bool = input_dict["IsInInstallationMode"]
        self.is_in_installation_mode_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["IsInInstallationModeChangedTime"]
        )
        self.is_in_signal_strength_test: bool = input_dict["IsInSignalStrengthTest"]
        self.is_in_signal_strength_test_changed_time: Optional[datetime] = time_zone.date_time_as_utc(
            input_dict["IsInSignalStrengthTestChangedTime"]
        )
        self.panel_id: int = input_dict["PanelId"]
        self.is_synchronized: bool = input_dict["IsSynchronized"]
        self.sirens_entry_exit_duration: int = input_dict["SirensEntryExitDuration"]
        self.frt_state: int = input_dict["FrtState"]
        self.frt_state_changed_time: Optional[datetime] = time_zone.date_time_as_utc(input_dict["FrtStateChangedTime"])
