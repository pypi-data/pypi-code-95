import math
import struct
import sys
import sliplib
from crccheck.crc import Crc16X25 as _Crc16X25
from datetime import datetime as _datetime
from collections.abc import Callable as _Callable
from typing import Any as _Any


class HciMessage:
    DevMgmt = 1
    RadioLinkTest = 2
    RadioLink = 3
    RemoteCtrl = 4
    SensorApp = 5

    def __init__(self, endpoint_id: int, message_id: int):
        self.endpoint_id = endpoint_id
        self.message_id = message_id

    def __str__(self):
        endpoint = self.translate_endpoint(self.endpoint_id)
        message = self.translate_class(self.endpoint_id, self.message_id)
        return "HciMessage:\n Endpoint ID: {} ({})\n Message ID: {} ({})"\
            .format(self.endpoint_id, endpoint, self.message_id, message)

    def __bytes__(self):
        return struct.pack("BB", self.endpoint_id, self.message_id)

    def get_msg_class_name(self) -> str:
        return self.translate_class(self.endpoint_id, self.message_id)

    def get_msg_class(self) -> _Any:
        return globals()[self.get_msg_class_name()]

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(data[0], data[1])

    @staticmethod
    def translate_endpoint(endpoint: int):
        mapping = {
            1: "dev_mgmt",
            2: "radio_link_test",
            3: "radio_link",
            4: "remote_ctrl",
            5: "sensor_app",
        }
        return mapping.get(endpoint, "unknown")

    @staticmethod
    def translate_class(endpoint_id: int, message_id: int):
        mapping = {
            HciMessage.DevMgmt: {
                PingReq.ID: PingReq.__name__,
                PingRsp.ID: PingRsp.__name__,
                GetDeviceInfoReq.ID: GetDeviceInfoReq.__name__,
                GetDeviceInfoRsp.ID: GetDeviceInfoRsp.__name__,
                GetFWInfoReq.ID: GetFWInfoReq.__name__,
                GetFWInfoRsp.ID: GetFWInfoRsp.__name__,
                ResetReq.ID: ResetReq.__name__,
                ResetRsp.ID: ResetRsp.__name__,
                SetOpModeReq.ID: SetOpModeReq.__name__,
                SetOpModeRsp.ID: SetOpModeRsp.__name__,
                GetOpModeReq.ID: GetOpModeReq.__name__,
                GetOpModeRsp.ID: GetOpModeRsp.__name__,
                SetRTCReq.ID: SetRTCReq.__name__,
                SetRTCRsp.ID: SetRTCRsp.__name__,
                GetRTCReq.ID: GetRTCReq.__name__,
                GetRTCRsp.ID: GetRTCRsp.__name__,
                SetRadioConfigReq.ID: SetRadioConfigReq.__name__,
                SetRadioConfigRsp.ID: SetRadioConfigRsp.__name__,
                GetRadioConfigReq.ID: GetRadioConfigReq.__name__,
                GetRadioConfigRsp.ID: GetRadioConfigRsp.__name__,
                ResetRadioConfigReq.ID: ResetRadioConfigReq.__name__,
                ResetRadioConfigRsp.ID: ResetRadioConfigRsp.__name__,
                GetSystemStatusReq.ID: GetSystemStatusReq.__name__,
                GetSystemStatusRsp.ID: GetSystemStatusRsp.__name__,
                SetRadioModeReq.ID: SetRadioModeReq.__name__,
                SetRadioModeRsp.ID: SetRadioModeRsp.__name__,
                PowerUpInd.ID: PowerUpInd.__name__,
                SetAesKeyReq.ID: SetAesKeyReq.__name__,
                SetAesKeyRsp.ID: SetAesKeyRsp.__name__,
                GetAesKeyReq.ID: GetAesKeyReq.__name__,
                GetAesKeyRsp.ID: GetAesKeyRsp.__name__,
                SetRtcAlarmReq.ID: SetRtcAlarmReq.__name__,
                SetRtcAlarmRsp.ID: SetRtcAlarmRsp.__name__,
                ClearRtcAlarmReq.ID: ClearRtcAlarmReq.__name__,
                ClearRtcAlarmRsp.ID: ClearRtcAlarmRsp.__name__,
                GetRtcAlarmReq.ID: GetRtcAlarmReq.__name__,
                GetRtcAlarmRsp.ID: GetRtcAlarmRsp.__name__,
                RtcAlarmInd.ID: RtcAlarmInd.__name__,
                SetHciConfigReq.ID: SetHciConfigReq.__name__,
                SetHciConfigRsp.ID: SetHciConfigRsp.__name__,
                GetHciConfigReq.ID: GetHciConfigReq.__name__,
                GetHciConfigRsp.ID: GetHciConfigRsp.__name__,
                InitBootloaderReq.ID: InitBootloaderReq.__name__,
                InitBootloaderRsp.ID: InitBootloaderRsp.__name__,
            },
            HciMessage.RadioLinkTest: {
                StartRadioLinkTestReq.ID: StartRadioLinkTestReq.__name__,
                StartRadioLinkTestRsp.ID: StartRadioLinkTestRsp.__name__,
                StopRadioLinkTestReq.ID: StopRadioLinkTestReq.__name__,
                StopRadioLinkTestRsp.ID: StopRadioLinkTestRsp.__name__,
                RadioLinkTestStatusInd.ID: RadioLinkTestStatusInd.__name__,
            },
            HciMessage.RadioLink: {
                SendUnreliableDataReq.ID: SendUnreliableDataReq.__name__,
                SendUnreliableDataRsp.ID: SendUnreliableDataRsp.__name__,
                UnreliableDataRXInd.ID: UnreliableDataRXInd.__name__,
                UnreliableDataTXInd.ID: UnreliableDataTXInd.__name__,
                RawDataRXInd.ID: RawDataRXInd.__name__,
                SendConfirmedDataReq.ID: SendConfirmedDataReq.__name__,
                SendConfirmedDataRsp.ID: SendConfirmedDataRsp.__name__,
                ConfirmedDataRXInd.ID: ConfirmedDataRXInd.__name__,
                ConfirmedDataTXInd.ID: ConfirmedDataTXInd.__name__,
                AckRXInd.ID: AckRXInd.__name__,
                AckTimeoutInd.ID: AckTimeoutInd.__name__,
                AckTXInd.ID: AckTXInd.__name__,
                SetAckDataReq.ID: SetAckDataReq.__name__,
                SetAckDataRsp.ID: SetAckDataRsp.__name__,
            },
            HciMessage.RemoteCtrl: {
                ButtonPressedInd.ID: ButtonPressedInd.__name__,
            },
        }
        return mapping.get(endpoint_id, {}).get(message_id, "unknown")


class DevMgmtStatus:
    Status_OK = 0
    Status_Error = 1
    Status_CmdNotSupported = 2
    Status_WrongParameter = 3
    Status_WrongDeviceMode = 4
    Status_DeviceBusy = 6

    @staticmethod
    def translate_status(status: int):
        mapping = {
            0: "ok",
            1: "error",
            2: "cmd_not_supported",
            3: "wrong_parameter",
            4: "wrong_device_mode",
            6: "device_busy",
        }
        return mapping.get(status, "unknown")


class RadioLinkStatus:
    Status_OK = 0
    Status_Error = 1
    Status_CmdNotSupported = 2
    Status_WrongParameter = 3
    Status_WrongRadioMode = 4
    Status_MediaBusy = 5
    Status_BufferFull = 7
    Status_LengthError = 8

    @staticmethod
    def translate_status(status: int):
        mapping = {
            0: "ok",
            1: "error",
            2: "cmd_not_supported",
            3: "wrong_parameter",
            4: "wrong_radio_mode",
            5: "media_busy",
            7: "buffer_full",
            8: "length_error",
        }
        return mapping.get(status, "unknown")


class RTCTime:
    @staticmethod
    def time_to_bytes(time: _datetime) -> bytes:
        time = (time.year - 2000) << 26 | \
               time.day << 21 | \
               time.hour << 16 | \
               time.month << 12 | \
               time.minute << 6 | \
               time.second
        return time.to_bytes(4, "little")

    @staticmethod
    def bytes_to_time(data: bytes) -> _datetime:
        i = int.from_bytes(data, "little")
        time = _datetime(
            year=((i >> 26) & 0x3f) + 2000,
            day=(i >> 21) & 0x1f,
            hour=(i >> 16) & 0x1f,
            month=(i >> 12) & 0x0f,
            minute=(i >> 6) & 0x3f,
            second=i & 0x3f,
        )
        return time


class OpMode:
    OpMode_Default = 0

    @staticmethod
    def translate_op_mode(o: int) -> str:
        op_modes = {
            0: "default_mode",
        }
        return op_modes.get(o, "unknown")


class RadioConfig:
    RadioConfigMode_Standard = 0
    RadioConfigMode_Sniffer = 2

    RadioConfigModulation_Lora = 0
    RadioConfigModulation_Flrc = 1
    RadioConfigModulation_Fsk = 2

    RadioConfigBWLora_200khz = 2
    RadioConfigBWLora_400khz = 3
    RadioConfigBWLora_800khz = 4
    RadioConfigBWLora_1600khz = 5

    RadioConfigBWFlrc_260_300 = 1
    RadioConfigBWFlrc_325_300 = 1
    RadioConfigBWFlrc_520_600 = 2
    RadioConfigBWFlrc_650_600 = 3
    RadioConfigBWFlrc_1040_1200 = 4
    RadioConfigBWFlrc_1300_1200 = 5

    RadioConfigErrorCodingLora_4_5 = 1
    RadioConfigErrorCodingLora_4_6 = 2
    RadioConfigErrorCodingLora_4_7 = 3
    RadioConfigErrorCodingLora_4_8 = 4
    RadioConfigErrorCodingLora_LI4_5 = 5
    RadioConfigErrorCodingLora_LI4_6 = 6
    RadioConfigErrorCodingLora_LI4_8 = 7

    RadioConfigErrorCodingFlrc_1_2 = 1
    RadioConfigErrorCodingFlrc_3_4 = 2
    RadioConfigErrorCodingFlrc_1 = 3

    RadioConfigTXControl_LbtOnBit = 1

    RadioConfigRXControl_RXOff = 0
    RadioConfigRXControl_RXAlwaysOn = 1
    RadioConfigRXControl_RXWindow = 2

    RadioConfigLedControl_RXIndicatorOnBit = 1
    RadioConfigLedControl_TXIndicatorOnBit = 2
    RadioConfigLedControl_AliveIndicatorOnBit = 4
    RadioConfigLedControl_ButtonPressedBit = 8

    RadioConfigMiscOptions_ExtendedRFPacketBit = 0
    RadioConfigMiscOptions_RtcEnabledBit = 1
    RadioConfigMiscOptions_HciTXIndicationBit = 2
    RadioConfigMiscOptions_HciPowerUpIndicationBit = 3
    RadioConfigMiscOptions_HciButtonPressedIndicationBit = 4
    RadioConfigMiscOptions_AesOnBit = 5
    RadioConfigMiscOptions_RemoteControlOnBit = 6

    RadioControlPowerSavingMode_Off = 0
    RadioControlPowerSavingMode_On = 1

    RadioControlNvmFlag_Ram = 0
    RadioControlNvmFlag_Nvm = 1

    @staticmethod
    def translate_radio_mode(value: int) -> str:
        mapping = {
            0: "standard_mode",
            2: "sniffer_mode",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_modulation(value: int) -> str:
        mapping = {
            0: "lora",
            1: "flrc",
            2: "fsk",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_bandwidth(modulation: int, value: int) -> str:
        mapping = {
            0: {
                2: "200_khz",
                3: "400_khz",
                4: "800_khz",
                5: "1600_khz",
            },
            1: {
                1: "260_kbs_300_khz",
                2: "325_kbs_300_khz",
                3: "520_kbs_600_khz",
                4: "650_kbs_600_khz",
                5: "1040_kbs_1200_khz",
                6: "1300_kbs_1200_khz",
            },
            2: {
                0: "2000_kbs_2400_khz",
                3: "1000_kbs_1200_khz",
                11: "250_kbs_300_khz",
                12: "125_kbs_300_khz",
            },
        }
        return mapping.get(modulation, {}).get(value, "unknown")

    @staticmethod
    def translate_error_coding(modulation: int, value: int) -> str:
        mapping = {
            0: {
                1: "4/5",
                2: "4/6",
                3: "4/7",
                4: "4/8",
                5: "li_4/5",
                6: "li_4/6",
                7: "li_4/8",
            },
            1: {
                1: "1/2",
                2: "3/4",
                3: "1",
            },
        }
        return mapping.get(modulation, {}).get(value, "unknown")

    @staticmethod
    def translate_rx_control(value: int) -> str:
        mapping = {
            0: "rx_off",
            1: "rx_always_on",
            2: "rx_window",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_off_on(value: int) -> str:
        mapping = {
            0: "off",
            1: "on",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_power_saving(value: int) -> str:
        mapping = {
            0: "off",
            1: "automatic",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def frequency_mhz_from_bytes_to_value(data: bytes) -> float:
        return round(52 / 2**18 * int.from_bytes(data, "little"), 6)

    @staticmethod
    def frequency_mhz_from_value_to_bytes(value: float) -> bytes:
        return math.floor(value / 52 * 2**18).to_bytes(3, "little")

    @staticmethod
    def translate_nvm_flag(value: int) -> str:
        mapping = {
            0: "ram",
            1: "nvm",
        }
        return mapping.get(value, "unknown")


class RadioConfigValidation:
    RadioConfigValidation_ModulationBit = 0
    RadioConfigValidation_FrequencyBit = 1
    RadioConfigValidation_BandwidthBit = 2
    RadioConfigValidation_SpreadingFactorBit = 3
    RadioConfigValidation_ErrorCodingBit = 4
    RadioConfigValidation_PowerLevelBit = 5

    RadioConfigValidation_RadioModeBit = 0
    RadioConfigValidation_RXOptionsBit = 1
    RadioConfigValidation_LbtThresholdBit = 2
    RadioConfigValidation_GroupAddressBit = 3
    RadioConfigValidation_DeviceAddressBit = 4
    RadioConfigValidation_PowerSavingModeBit = 5

    @staticmethod
    def translate_valid_invalid(value: int) -> str:
        mapping = {
            0: "valid",
            1: "invalid",
        }
        return mapping.get(value, "unknown")


class SystemStatus:
    SystemStatusNvmState_SystemBlockBit = 0
    SystemStatusNvmState_RadioBlockBit = 1

    @staticmethod
    def translate_ok_error(value: int) -> str:
        mapping = {
            0: "ok",
            1: "error",
        }
        return mapping.get(value, "unknown")


class RtcAlarm:
    RtcAlarmOptions_SingleAlarm = 0
    RtcAlarmOptions_DailyAlarm = 1

    RtcAlarmStatus_NoAlarmSet = 0
    RtcAlarmStatus_AlarmSet = 1

    @staticmethod
    def translate_rtc_alarm_options(value: int) -> str:
        mapping = {
            0: "single_alarm",
            1: "daily_alarm",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_rtc_alarm_status(value: int) -> str:
        mapping = {
            0: "no_alarm_set",
            1: "alarm_set",
        }
        return mapping.get(value, "unknown")


class HciConfig:
    HciConfigNvmFlag_Ram = 0
    HciConfigNvmFlag_Nvm = 1

    HciConfigBaudrate_57600_bps = 0x03
    HciConfigBaudrate_115200_bps = 0x04

    @staticmethod
    def translate_nvm_flag(value: int) -> str:
        mapping = {
            0: "ram",
            1: "nvm",
        }
        return mapping.get(value, "unknown")

    @staticmethod
    def translate_hci_baudrate(value: int) -> str:
        mapping = {
            0x03: "57600_bps",
            0x04: "115200_bps",
        }
        return mapping.get(value, "unknown")


class DataFormat:
    DataFormat_ExtendedBit = 0
    DataFormat_DecryptedBit = 5
    DataFormat_DecryptionErrorBit = 6
    DataFormat_EncryptedBit = 7


class RadioControl:
    RadioControl_AckRequestBit = 0
    RadioControl_AckBit = 1
    RadioControl_EncryptedBit = 2


class PingReq(HciMessage):
    ID = 1

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n PingReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class PingRsp(HciMessage, DevMgmtStatus):
    ID = 2

    def __init__(self, status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status

    def __str__(self):
        return super().__str__() + "\n PingRsp:\n  Status: {} ({})".format(self.status,
                                                                           self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(data[0])


class GetDeviceInfoReq(HciMessage):
    ID = 3

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetDeviceInfoReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetDeviceInfoRsp(HciMessage, DevMgmtStatus):
    ID = 4

    ModuleType_IM282A = 0xb0

    def __init__(self,
                 status: int,
                 module_type: int,
                 device_address: int,
                 group_address: int,
                 reserved: int,
                 device_id: int,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.module_type = module_type
        self.device_address = device_address
        self.group_address = group_address
        self.reserved = reserved
        self.device_id = device_id

    def __str__(self):
        return super().__str__() + "\n GetDeviceInfoRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  ModuleType: 0x{:X} ({})\n" \
                                   "  DeviceAddress: 0x{:X}\n" \
                                   "  GroupAddress: 0x{:X}\n" \
                                   "  Reserved: {}\n" \
                                   "  DeviceID: {}"\
            .format(self.status,
                    self.translate_status(self.status),
                    self.module_type,
                    self.translate_module_type(self.module_type),
                    self.device_address,
                    self.group_address,
                    self.reserved,
                    self.device_id)

    def __bytes__(self):
        return super().__bytes__() +\
               self.status.to_bytes(1, "little") +\
               self.module_type.to_bytes(1, "little") +\
               self.device_address.to_bytes(2, "little") +\
               self.group_address.to_bytes(1, "little") +\
               self.reserved.to_bytes(1, "little") +\
               self.device_id.to_bytes(4, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = data[0]
        module_type = data[1]
        device_address = int.from_bytes(data[2:4], "little")
        group_address = data[4]
        reserved = data[5]
        device_id = int.from_bytes(data[6:10], "little")
        return cls(status, module_type, device_address, group_address, reserved, device_id)

    @staticmethod
    def translate_module_type(t: int) -> str:
        types = {
            0xb0: "iM282A",
        }
        return types.get(t, "unknown")


class GetFWInfoReq(HciMessage):
    ID = 5

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetFWInfoReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetFWInfoRsp(HciMessage, DevMgmtStatus):
    ID = 6

    def __init__(self,
                 status: int,
                 fw_version_minor: int,
                 fw_version_major: int,
                 build: int,
                 date: str,
                 name: str,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.fw_version_minor = fw_version_minor
        self.fw_version_major = fw_version_major
        self.build = build
        self.date = date
        self.name = name

    def __str__(self):
        return super().__str__() + "\n GetFWInfoRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  FWVersionMinor: {}\n" \
                                   "  FWVersionMajor: {}\n" \
                                   "  Build: {}\n" \
                                   "  Date: {}\n" \
                                   "  Name: {}" \
            .format(self.status,
                    self.translate_status(self.status),
                    self.fw_version_minor,
                    self.fw_version_major,
                    self.build,
                    self.date,
                    self.name)

    def __bytes__(self):
        return super().__bytes__() + \
               self.status.to_bytes(1, "little") + \
               self.fw_version_minor.to_bytes(1, "little") + \
               self.fw_version_major.to_bytes(1, "little") + \
               self.build.to_bytes(2, "little") + \
               self.date[:10].encode("utf-8") + \
               self.name.encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = data[0]
        fw_version_minor = data[1]
        fw_version_major = data[2]
        build = int.from_bytes(data[3:5], "little")
        date = data[5:15].decode("utf-8")
        name = data[15:].decode("utf-8")
        return cls(status, fw_version_minor, fw_version_major, build, date, name)


class ResetReq(HciMessage):
    ID = 7

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n ResetReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class ResetRsp(HciMessage, DevMgmtStatus):
    ID = 8

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n ResetRsp:\n  Status: {} ({})".format(self.status,
                                                                            self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class SetOpModeReq(HciMessage, OpMode):
    ID = 9

    def __init__(self, op_mode: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.op_mode = op_mode

    def __str__(self):
        return super().__str__() + "\n SetOpModeReq:\n  OpMode: {} ({})".format(self.op_mode,
                                                                                self.translate_op_mode(self.op_mode))

    def __bytes__(self):
        return super().__bytes__() + self.op_mode.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        op_mode = data[0]
        return cls(op_mode)


class SetOpModeRsp(HciMessage, DevMgmtStatus):
    ID = 10

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetOpModeRsp:\n  Status: {} ({})".format(self.status,
                                                                                self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetOpModeReq(HciMessage):
    ID = 11

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetOpModeReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetOpModeRsp(HciMessage, DevMgmtStatus, OpMode):
    ID = 12

    def __init__(self, dev_mgmt_status: int, op_mode: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status
        self.op_mode = op_mode

    def __str__(self):
        return super().__str__() + "\n GetOpModeRsp:\n  Status: {} ({})\n  OpMode: {} ({})"\
            .format(self.status, self.translate_status(self.status), self.op_mode, self.translate_op_mode(self.op_mode))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little") + self.op_mode.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = data[0]
        op_mode = data[1]
        return cls(status, op_mode)


class SetRTCReq(HciMessage, RTCTime):
    ID = 13

    def __init__(self, time: _datetime):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.time = time

    def __str__(self):
        return super().__str__() + "\n SetRTCReq:\n  DateTime: {}"\
            .format(self.time)

    def __bytes__(self):
        data = self.time_to_bytes(self.time)
        return super().__bytes__() + data

    @classmethod
    def from_bytes(cls, data: bytes):
        time = cls.bytes_to_time(data)
        return cls(time)


class SetRTCRsp(HciMessage, DevMgmtStatus):
    ID = 14

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetRTCRsp:\n  Status: {} ({})".format(self.status,
                                                                             self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetRTCReq(HciMessage):
    ID = 15

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetRTCReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetRTCRsp(HciMessage, DevMgmtStatus, RTCTime):
    ID = 16

    def __init__(self, status: int, time: _datetime):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.time = time

    def __str__(self):
        return super().__str__() + "\n GetRTCRsp:\n" \
                                   "  Status: {} ({})\n  DateTime: {}" \
            .format(self.status, self.translate_status(self.status), self.time)

    def __bytes__(self):
        data = self.time_to_bytes(self.time)
        return super().__bytes__() + self.status.to_bytes(1, "little") + data

    @classmethod
    def from_bytes(cls, data: bytes):
        status = data[0]
        time = cls.bytes_to_time(data[1:])
        return cls(status, time)


class SetRadioConfigReq(HciMessage, DevMgmtStatus, RadioConfig):
    ID = 17

    def __init__(self,
                 nvm_flag: int,
                 radio_mode: int = RadioConfig.RadioConfigMode_Standard,
                 group_address: int = 0x10,
                 group_address_dst: int = 0x10,
                 device_address: int = 0x1234,
                 device_address_dst: int = 0x1234,
                 modulation: int = RadioConfig.RadioConfigModulation_Lora,
                 frequency_mhz: float = 2449.999924,
                 bandwidth: int = RadioConfig.RadioConfigBWLora_200khz,
                 spreading_factor: int = 11,
                 error_coding: int = RadioConfig.RadioConfigErrorCodingLora_4_5,
                 power_level: int = 8,
                 tx_control_lbt: bool = False,
                 rx_control: int = RadioConfig.RadioConfigRXControl_RXAlwaysOn,
                 rx_window_time: int = 4000,
                 led_control_rx_indicator: bool = True,
                 led_control_tx_indicator: bool = True,
                 led_control_alive_indicator: bool = True,
                 led_control_button_pressed_indicator: bool = False,
                 misc_options_extended_format: bool = True,
                 misc_options_rtc: bool = True,
                 misc_options_hci_tx_indication: bool = True,
                 misc_options_hci_power_up_indication: bool = False,
                 misc_options_hci_button_pressed_indication: bool = False,
                 misc_options_aes: bool = False,
                 misc_options_remote_control: bool = False,
                 reserved: int = 0,
                 power_saving_mode: int = RadioConfig.RadioControlPowerSavingMode_Off,
                 lbt_threshold: int = -70,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.nvm_flag = nvm_flag
        self.radio_mode = radio_mode
        self.group_address = group_address
        self.group_address_dst = group_address_dst
        self.device_address = device_address
        self.device_address_dst = device_address_dst
        self.modulation = modulation
        self.frequency_mhz = frequency_mhz
        self.bandwidth = bandwidth
        self.spreading_factor = spreading_factor
        self.error_coding = error_coding
        self.power_level = power_level
        self.tx_control_lbt = tx_control_lbt
        self.rx_control = rx_control
        self.rx_window_time = rx_window_time
        self.led_control_rx_indicator = led_control_rx_indicator
        self.led_control_tx_indicator = led_control_tx_indicator
        self.led_control_alive_indicator = led_control_alive_indicator
        self.led_control_button_pressed_indicator = led_control_button_pressed_indicator
        self.misc_options_extended_format = misc_options_extended_format
        self.misc_options_rtc = misc_options_rtc
        self.misc_options_hci_tx_indication = misc_options_hci_tx_indication
        self.misc_options_hci_power_up_indication = misc_options_hci_power_up_indication
        self.misc_options_hci_button_pressed_indication = misc_options_hci_button_pressed_indication
        self.misc_options_aes = misc_options_aes
        self.misc_options_remote_control = misc_options_remote_control
        self.reserved = reserved
        self.power_saving_mode = power_saving_mode
        self.lbt_threshold = lbt_threshold

    def __str__(self):
        return super().__str__() + "\n GetRadioConfigRsp:\n" \
                                   "  NvmFlag: {} ({})\n" \
                                   "  RadioMode {} ({})\n" \
                                   "  GroupAddress: 0x{:X}\n" \
                                   "  GroupAddressDst: 0x{:X}\n" \
                                   "  DeviceAddress: 0x{:X}\n" \
                                   "  DeviceAddressDst: 0x{:X}\n" \
                                   "  Modulation: {} ({})\n" \
                                   "  Frequency: {} MHz\n" \
                                   "  Bandwidth: {} ({})\n" \
                                   "  SpreadingFactor: {}\n" \
                                   "  ErrorCoding: {} ({})\n" \
                                   "  PowerLevel: {} dBm\n" \
                                   "  TXControl:\n" \
                                   "    LBT: {} ({})\n" \
                                   "  RXControl: {} ({})\n" \
                                   "  RXWindowTime: {} ms\n" \
                                   "  LedControl:\n" \
                                   "   RXIndicatorD3: {} ({})\n" \
                                   "   TXIndicatorD2: {} ({})\n" \
                                   "   AliveIndicatorD4: {} ({})\n" \
                                   "   ButtonPressedIndicatorD1: {} ({})\n" \
                                   "  MiscOptions:\n" \
                                   "   PacketFormatExtended: {} ({})\n" \
                                   "   RTC: {} ({})\n" \
                                   "   HciTXIndication: {} ({})\n" \
                                   "   HciPowerUpIndication: {} ({})\n" \
                                   "   HciButtonPressedIndication: {} ({})\n" \
                                   "   AES: {} ({})\n" \
                                   "   RemoteControl: {} ({})\n" \
                                   "  Reserved: {}\n" \
                                   "  PowerSavingMode: {} ({})\n" \
                                   "  LbtThreshold: {} dBm".format(
            self.nvm_flag, self.translate_nvm_flag(self.nvm_flag),
            self.radio_mode, self.translate_radio_mode(self.radio_mode),
            self.group_address,
            self.group_address_dst,
            self.device_address,
            self.device_address_dst,
            self.modulation, self.translate_modulation(self.modulation),
            self.frequency_mhz,
            self.bandwidth, self.translate_bandwidth(self.modulation, self.bandwidth),
            self.spreading_factor,
            self.error_coding, self.translate_error_coding(self.modulation, self.error_coding),
            self.power_level,
            self.tx_control_lbt, self.translate_off_on(self.tx_control_lbt),
            self.rx_control, self.translate_rx_control(self.rx_control),
            self.rx_window_time,
            self.led_control_rx_indicator, self.translate_off_on(self.led_control_rx_indicator),
            self.led_control_tx_indicator, self.translate_off_on(self.led_control_tx_indicator),
            self.led_control_alive_indicator, self.translate_off_on(self.led_control_alive_indicator),
            self.led_control_button_pressed_indicator, self.translate_off_on(self.led_control_button_pressed_indicator),
            self.misc_options_extended_format, self.translate_off_on(self.misc_options_extended_format),
            self.misc_options_rtc, self.translate_off_on(self.misc_options_rtc),
            self.misc_options_hci_tx_indication, self.translate_off_on(self.misc_options_hci_tx_indication),
            self.misc_options_hci_power_up_indication, self.translate_off_on(self.misc_options_hci_power_up_indication),
            self.misc_options_hci_button_pressed_indication,
            self.translate_off_on(self.misc_options_hci_button_pressed_indication),
            self.misc_options_aes, self.translate_off_on(self.misc_options_aes),
            self.misc_options_remote_control, self.translate_off_on(self.misc_options_remote_control),
            self.reserved,
            self.power_saving_mode, self.translate_power_saving(self.power_saving_mode),
            self.lbt_threshold
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.nvm_flag.to_bytes(1, "little") + \
               self.radio_mode.to_bytes(1, "little") + \
               self.group_address.to_bytes(1, "little") + \
               self.group_address_dst.to_bytes(1, "little") + \
               self.device_address.to_bytes(2, "little") + \
               self.device_address_dst.to_bytes(2, "little") + \
               self.modulation.to_bytes(1, "little") + \
               self.frequency_mhz_from_value_to_bytes(self.frequency_mhz) + \
               self.bandwidth.to_bytes(1, "little") + \
               self.spreading_factor.to_bytes(1, "little") + \
               self.error_coding.to_bytes(1, "little") + \
               self.power_level.to_bytes(1, "little", signed=True) + \
               (int(self.tx_control_lbt) << self.RadioConfigTXControl_LbtOnBit).to_bytes(1, "little") + \
               self.rx_control.to_bytes(1, "little") + \
               self.rx_window_time.to_bytes(2, "little") + \
               ((int(self.led_control_rx_indicator) << self.RadioConfigLedControl_RXIndicatorOnBit) |
                (int(self.led_control_tx_indicator) << self.RadioConfigLedControl_TXIndicatorOnBit) |
                (int(self.led_control_alive_indicator) << self.RadioConfigLedControl_AliveIndicatorOnBit) |
                (int(self.led_control_button_pressed_indicator) <<
                 self.RadioConfigLedControl_ButtonPressedBit)).to_bytes(1, "little") + \
               ((int(self.misc_options_extended_format) << self.RadioConfigMiscOptions_ExtendedRFPacketBit) |
                (int(self.misc_options_rtc) << self.RadioConfigMiscOptions_RtcEnabledBit) |
                (int(self.misc_options_hci_tx_indication) << self.RadioConfigMiscOptions_HciTXIndicationBit) |
                (int(self.misc_options_hci_power_up_indication) <<
                 self.RadioConfigMiscOptions_HciPowerUpIndicationBit) |
                (int(self.misc_options_hci_button_pressed_indication) <<
                 self.RadioConfigMiscOptions_HciButtonPressedIndicationBit) |
                (int(self.misc_options_aes) << self.RadioConfigMiscOptions_AesOnBit) |
                (int(self.misc_options_remote_control) <<
                 self.RadioConfigMiscOptions_RemoteControlOnBit)).to_bytes(1, "little") + \
               self.reserved.to_bytes(1, "little") + \
               self.power_saving_mode.to_bytes(1, "little") + \
               self.lbt_threshold.to_bytes(2, "little", signed=True)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            nvm_flag=data[0],
            radio_mode=data[1],
            group_address=data[2],
            group_address_dst=data[3],
            device_address=int.from_bytes(data[4:6], "little"),
            device_address_dst=int.from_bytes(data[6:8], "little"),
            modulation=data[8],
            frequency_mhz=cls.frequency_mhz_from_bytes_to_value(data[9:12]),
            bandwidth=data[12],
            spreading_factor=data[13],
            error_coding=data[14],
            power_level=data[15],
            tx_control_lbt=bool((data[16] >> cls.RadioConfigTXControl_LbtOnBit) & 0x1),
            rx_control=data[17],
            rx_window_time=int.from_bytes(data[18:20], "little"),
            led_control_rx_indicator=bool((data[20] >> cls.RadioConfigLedControl_RXIndicatorOnBit) & 0x1),
            led_control_tx_indicator=bool((data[20] >> cls.RadioConfigLedControl_TXIndicatorOnBit) & 0x1),
            led_control_alive_indicator=bool((data[20] >> cls.RadioConfigLedControl_AliveIndicatorOnBit) & 0x1),
            led_control_button_pressed_indicator=bool((data[20] >> cls.RadioConfigLedControl_ButtonPressedBit) & 0x1),
            misc_options_extended_format=bool((data[21] >> cls.RadioConfigMiscOptions_ExtendedRFPacketBit) & 0x1),
            misc_options_rtc=bool((data[21] >> cls.RadioConfigMiscOptions_RtcEnabledBit) & 0x1),
            misc_options_hci_tx_indication=bool((data[21] >> cls.RadioConfigMiscOptions_HciTXIndicationBit) & 0x1),
            misc_options_hci_power_up_indication=bool(
                (data[21] >> cls.RadioConfigMiscOptions_HciPowerUpIndicationBit) & 0x1),
            misc_options_hci_button_pressed_indication=bool(
                (data[21] >> cls.RadioConfigMiscOptions_HciButtonPressedIndicationBit) & 0x1),
            misc_options_aes=bool((data[21] >> cls.RadioConfigMiscOptions_AesOnBit) & 0x1),
            misc_options_remote_control=bool((data[21] >> cls.RadioConfigMiscOptions_RemoteControlOnBit) & 0x1),
            reserved=data[22],
            power_saving_mode=data[23],
            lbt_threshold=int.from_bytes(data[24:26], "little", signed=True),
        )


class SetRadioConfigRsp(HciMessage, DevMgmtStatus, RadioConfigValidation):
    ID = 18

    def __init__(self,
                 status: int,
                 invalid_modulation: bool = False,
                 invalid_frequency: bool = False,
                 invalid_bandwidth: bool = False,
                 invalid_spreading_factor: bool = False,
                 invalid_error_coding: bool = False,
                 invalid_power_level: bool = False,
                 invalid_radio_mode: bool = False,
                 invalid_rx_options: bool = False,
                 invalid_lbt_threshold: bool = False,
                 invalid_group_address: bool = False,
                 invalid_device_address: bool = False,
                 invalid_power_saving_mode: bool = False,
                 reserved1: int = 0,
                 reserved2: int = 0,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.invalid_modulation = invalid_modulation
        self.invalid_frequency = invalid_frequency
        self.invalid_bandwidth = invalid_bandwidth
        self.invalid_spreading_factor = invalid_spreading_factor
        self.invalid_error_coding = invalid_error_coding
        self.invalid_power_level = invalid_power_level
        self.invalid_radio_mode = invalid_radio_mode
        self.invalid_rx_options = invalid_rx_options
        self.invalid_lbt_threshold = invalid_lbt_threshold
        self.invalid_group_address = invalid_group_address
        self.invalid_device_address = invalid_device_address
        self.invalid_power_saving_mode = invalid_power_saving_mode
        self.reserved1 = reserved1
        self.reserved2 = reserved2

    def __str__(self):
        return super().__str__() + "\n SetRadioConfigRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  InvalidModulation: {} ({})\n" \
                                   "  InvalidFrequency: {} ({})\n" \
                                   "  InvalidBandwidth: {} ({})\n" \
                                   "  InvalidSpreadingFactor: {} ({})\n" \
                                   "  InvalidErrorCoding: {} ({})\n" \
                                   "  InvalidPowerLevel: {} ({})\n" \
                                   "  InvalidRadioMode: {} ({})\n" \
                                   "  InvalidRXOptions: {} ({})\n" \
                                   "  InvalidLbtThreshold: {} ({})\n" \
                                   "  InvalidGroupAddress: {} ({})\n" \
                                   "  InvalidDeviceAddress: {} ({})\n" \
                                   "  InvalidPowerSavingMode: {} ({})\n" \
                                   "  Reserved1: {}\n" \
                                   "  Reserved2: {}".format(
            self.status, self.translate_status(self.status),
            self.invalid_modulation, self.translate_valid_invalid(self.invalid_modulation),
            self.invalid_frequency, self.translate_valid_invalid(self.invalid_frequency),
            self.invalid_bandwidth, self.translate_valid_invalid(self.invalid_bandwidth),
            self.invalid_spreading_factor, self.translate_valid_invalid(self.invalid_spreading_factor),
            self.invalid_error_coding, self.translate_valid_invalid(self.invalid_error_coding),
            self.invalid_power_level, self.translate_valid_invalid(self.invalid_power_level),
            self.invalid_radio_mode, self.translate_valid_invalid(self.invalid_radio_mode),
            self.invalid_rx_options, self.translate_valid_invalid(self.invalid_rx_options),
            self.invalid_lbt_threshold, self.translate_valid_invalid(self.invalid_lbt_threshold),
            self.invalid_group_address, self.translate_valid_invalid(self.invalid_group_address),
            self.invalid_device_address, self.translate_valid_invalid(self.invalid_device_address),
            self.invalid_power_saving_mode, self.translate_valid_invalid(self.invalid_power_saving_mode),
            self.reserved1,
            self.reserved2,
        )

    def __bytes__(self):
        data = super().__bytes__()
        if self.status == self.Status_WrongParameter:
            data += ((int(self.invalid_modulation) << self.RadioConfigValidation_ModulationBit) |
                     (int(self.invalid_frequency) << self.RadioConfigValidation_FrequencyBit) |
                     (int(self.invalid_bandwidth) << self.RadioConfigValidation_BandwidthBit) |
                     (int(self.invalid_spreading_factor) << self.RadioConfigValidation_SpreadingFactorBit) |
                     (int(self.invalid_error_coding) << self.RadioConfigValidation_ErrorCodingBit) |
                     (int(self.invalid_power_level) << self.RadioConfigValidation_PowerLevelBit)).to_bytes(
                        1, "little") +\
                    ((int(self.invalid_radio_mode) << self.RadioConfigValidation_RadioModeBit) |
                     (int(self.invalid_rx_options) << self.RadioConfigValidation_RXOptionsBit) |
                     (int(self.invalid_lbt_threshold) << self.RadioConfigValidation_LbtThresholdBit) |
                     (int(self.invalid_group_address) << self.RadioConfigValidation_GroupAddressBit) |
                     (int(self.invalid_device_address) << self.RadioConfigValidation_DeviceAddressBit) |
                     (int(self.invalid_power_saving_mode) << self.RadioConfigValidation_PowerSavingModeBit)).to_bytes(
                        1, "little")
        return data

    @classmethod
    def from_bytes(cls, data: bytes):
        status = data[0]
        if status == cls.Status_WrongParameter:
            return cls(
                status=data[0],
                invalid_modulation=bool((data[1] >> cls.RadioConfigValidation_ModulationBit) & 0x1),
                invalid_frequency=bool((data[1] >> cls.RadioConfigValidation_FrequencyBit) & 0x1),
                invalid_bandwidth=bool((data[1] >> cls.RadioConfigValidation_BandwidthBit) & 0x1),
                invalid_spreading_factor=bool((data[1] >> cls.RadioConfigValidation_SpreadingFactorBit) & 0x1),
                invalid_error_coding=bool((data[1] >> cls.RadioConfigValidation_ErrorCodingBit) & 0x1),
                invalid_power_level=bool((data[1] >> cls.RadioConfigValidation_PowerLevelBit) & 0x1),
                invalid_radio_mode=bool((data[3] >> cls.RadioConfigValidation_RadioModeBit) & 0x1),
                invalid_rx_options=bool((data[3] >> cls.RadioConfigValidation_RXOptionsBit) & 0x1),
                invalid_lbt_threshold=bool((data[3] >> cls.RadioConfigValidation_LbtThresholdBit) & 0x1),
                invalid_group_address=bool((data[3] >> cls.RadioConfigValidation_GroupAddressBit) & 0x1),
                invalid_device_address=bool((data[3] >> cls.RadioConfigValidation_DeviceAddressBit) & 0x1),
                invalid_power_saving_mode=bool((data[3] >> cls.RadioConfigValidation_PowerSavingModeBit) & 0x1),
                reserved1=data[2],
                reserved2=data[4],
            )
        else:
            return cls(status)


class GetRadioConfigReq(HciMessage):
    ID = 19

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetRadioConfigReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetRadioConfigRsp(HciMessage, DevMgmtStatus, RadioConfig):
    ID = 20

    def __init__(self,
                 status: int,
                 radio_mode: int,
                 group_address: int,
                 group_address_dst: int,
                 device_address: int,
                 device_address_dst: int,
                 modulation: int,
                 frequency_mhz: float,
                 bandwidth: int,
                 spreading_factor: int,
                 error_coding: int,
                 power_level: int,
                 tx_control_lbt: bool,
                 rx_control: int,
                 rx_window_time: int,
                 led_control_rx_indicator: bool,
                 led_control_tx_indicator: bool,
                 led_control_alive_indicator: bool,
                 led_control_button_pressed_indicator: bool,
                 misc_options_extended_format: bool,
                 misc_options_rtc: bool,
                 misc_options_hci_tx_indication: bool,
                 misc_options_hci_power_up_indication: bool,
                 misc_options_hci_button_pressed_indication: bool,
                 misc_options_aes: bool,
                 misc_options_remote_control: bool,
                 reserved: int,
                 power_saving_mode: int,
                 lbt_threshold: int,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.radio_mode = radio_mode
        self.group_address = group_address
        self.group_address_dst = group_address_dst
        self.device_address = device_address
        self.device_address_dst = device_address_dst
        self.modulation = modulation
        self.frequency_mhz = frequency_mhz
        self.bandwidth = bandwidth
        self.spreading_factor = spreading_factor
        self.error_coding = error_coding
        self.power_level = power_level
        self.tx_control_lbt = tx_control_lbt
        self.rx_control = rx_control
        self.rx_window_time = rx_window_time
        self.led_control_rx_indicator = led_control_rx_indicator
        self.led_control_tx_indicator = led_control_tx_indicator
        self.led_control_alive_indicator = led_control_alive_indicator
        self.led_control_button_pressed_indicator = led_control_button_pressed_indicator
        self.misc_options_extended_format = misc_options_extended_format
        self.misc_options_rtc = misc_options_rtc
        self.misc_options_hci_tx_indication = misc_options_hci_tx_indication
        self.misc_options_hci_power_up_indication = misc_options_hci_power_up_indication
        self.misc_options_hci_button_pressed_indication = misc_options_hci_button_pressed_indication
        self.misc_options_aes = misc_options_aes
        self.misc_options_remote_control = misc_options_remote_control
        self.reserved = reserved
        self.power_saving_mode = power_saving_mode
        self.lbt_threshold = lbt_threshold

    def __str__(self):
        return super().__str__() + "\n GetRadioConfigRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  RadioMode {} ({})\n" \
                                   "  GroupAddress: 0x{:X}\n" \
                                   "  GroupAddressDst: 0x{:X}\n" \
                                   "  DeviceAddress: 0x{:X}\n" \
                                   "  DeviceAddressDst: 0x{:X}\n" \
                                   "  Modulation: {} ({})\n" \
                                   "  Frequency: {} MHz\n" \
                                   "  Bandwidth: {} ({})\n" \
                                   "  SpreadingFactor: {}\n" \
                                   "  ErrorCoding: {} ({})\n" \
                                   "  PowerLevel: {} dBm\n" \
                                   "  TXControl:\n" \
                                   "    LBT: {} ({})\n" \
                                   "  RXControl: {} ({})\n" \
                                   "  RXWindowTime: {} ms\n" \
                                   "  LedControl:\n" \
                                   "   RXIndicatorD3: {} ({})\n" \
                                   "   TXIndicatorD2: {} ({})\n" \
                                   "   AliveIndicatorD4: {} ({})\n" \
                                   "   ButtonPressedIndicatorD1: {} ({})\n" \
                                   "  MiscOptions:\n" \
                                   "   PacketFormatExtended: {} ({})\n" \
                                   "   RTC: {} ({})\n" \
                                   "   HciTXIndication: {} ({})\n" \
                                   "   HciPowerUpIndication: {} ({})\n" \
                                   "   HciButtonPressedIndication: {} ({})\n" \
                                   "   AES: {} ({})\n" \
                                   "   RemoteControl: {} ({})\n" \
                                   "  Reserved: {}\n" \
                                   "  PowerSavingMode: {} ({})\n" \
                                   "  LbtThreshold: {} dBm".format(
            self.status, self.translate_status(self.status),
            self.radio_mode, self.translate_radio_mode(self.radio_mode),
            self.group_address,
            self.group_address_dst,
            self.device_address,
            self.device_address_dst,
            self.modulation, self.translate_modulation(self.modulation),
            self.frequency_mhz,
            self.bandwidth, self.translate_bandwidth(self.modulation, self.bandwidth),
            self.spreading_factor,
            self.error_coding, self.translate_error_coding(self.modulation, self.error_coding),
            self.power_level,
            self.tx_control_lbt, self.translate_off_on(self.tx_control_lbt),
            self.rx_control, self.translate_rx_control(self.rx_control),
            self.rx_window_time,
            self.led_control_rx_indicator, self.translate_off_on(self.led_control_rx_indicator),
            self.led_control_tx_indicator, self.translate_off_on(self.led_control_tx_indicator),
            self.led_control_alive_indicator, self.translate_off_on(self.led_control_alive_indicator),
            self.led_control_button_pressed_indicator, self.translate_off_on(self.led_control_button_pressed_indicator),
            self.misc_options_extended_format, self.translate_off_on(self.misc_options_extended_format),
            self.misc_options_rtc, self.translate_off_on(self.misc_options_rtc),
            self.misc_options_hci_tx_indication, self.translate_off_on(self.misc_options_hci_tx_indication),
            self.misc_options_hci_power_up_indication, self.translate_off_on(self.misc_options_hci_power_up_indication),
            self.misc_options_hci_button_pressed_indication,
            self.translate_off_on(self.misc_options_hci_button_pressed_indication),
            self.misc_options_aes, self.translate_off_on(self.misc_options_aes),
            self.misc_options_remote_control, self.translate_off_on(self.misc_options_remote_control),
            self.reserved,
            self.power_saving_mode, self.translate_power_saving(self.power_saving_mode),
            self.lbt_threshold
        )

    def __bytes__(self):
        return super().__bytes__() +\
               self.status.to_bytes(1, "little") +\
               self.radio_mode.to_bytes(1, "little") +\
               self.group_address.to_bytes(1, "little") +\
               self.group_address_dst.to_bytes(1, "little") +\
               self.device_address.to_bytes(2, "little") +\
               self.device_address_dst.to_bytes(2, "little") +\
               self.modulation.to_bytes(1, "little") +\
               self.frequency_mhz_from_value_to_bytes(self.frequency_mhz) +\
               self.bandwidth.to_bytes(1, "little") +\
               self.spreading_factor.to_bytes(1, "little") +\
               self.error_coding.to_bytes(1, "little") +\
               self.power_level.to_bytes(1, "little", signed=True) + \
               (int(self.tx_control_lbt) << self.RadioConfigTXControl_LbtOnBit).to_bytes(1, "little") +\
               self.rx_control.to_bytes(1, "little") +\
               self.rx_window_time.to_bytes(2, "little") + \
               ((int(self.led_control_rx_indicator) << self.RadioConfigLedControl_RXIndicatorOnBit) |
                (int(self.led_control_tx_indicator) << self.RadioConfigLedControl_TXIndicatorOnBit) |
                (int(self.led_control_alive_indicator) << self.RadioConfigLedControl_AliveIndicatorOnBit) |
                (int(self.led_control_button_pressed_indicator) <<
                 self.RadioConfigLedControl_ButtonPressedBit)).to_bytes(1, "little") +\
               ((int(self.misc_options_extended_format) << self.RadioConfigMiscOptions_ExtendedRFPacketBit) |
                (int(self.misc_options_rtc) << self.RadioConfigMiscOptions_RtcEnabledBit) |
                (int(self.misc_options_hci_tx_indication) << self.RadioConfigMiscOptions_HciTXIndicationBit) |
                (int(self.misc_options_hci_power_up_indication) <<
                 self.RadioConfigMiscOptions_HciPowerUpIndicationBit) |
                (int(self.misc_options_hci_button_pressed_indication) <<
                 self.RadioConfigMiscOptions_HciButtonPressedIndicationBit) |
                (int(self.misc_options_aes) << self.RadioConfigMiscOptions_AesOnBit) |
                (int(self.misc_options_remote_control) <<
                 self.RadioConfigMiscOptions_RemoteControlOnBit)).to_bytes(1, "little") +\
               self.reserved.to_bytes(1, "little") +\
               self.power_saving_mode.to_bytes(1, "little") +\
               self.lbt_threshold.to_bytes(2, "little", signed=True)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            status=data[0],
            radio_mode=data[1],
            group_address=data[2],
            group_address_dst=data[3],
            device_address=int.from_bytes(data[4:6], "little"),
            device_address_dst=int.from_bytes(data[6:8], "little"),
            modulation=data[8],
            frequency_mhz=cls.frequency_mhz_from_bytes_to_value(data[9:12]),
            bandwidth=data[12],
            spreading_factor=data[13],
            error_coding=data[14],
            power_level=data[15],
            tx_control_lbt=bool((data[16] >> cls.RadioConfigTXControl_LbtOnBit) & 0x1),
            rx_control=data[17],
            rx_window_time=int.from_bytes(data[18:20], "little"),
            led_control_rx_indicator=bool((data[20] >> cls.RadioConfigLedControl_RXIndicatorOnBit) & 0x1),
            led_control_tx_indicator=bool((data[20] >> cls.RadioConfigLedControl_TXIndicatorOnBit) & 0x1),
            led_control_alive_indicator=bool((data[20] >> cls.RadioConfigLedControl_AliveIndicatorOnBit) & 0x1),
            led_control_button_pressed_indicator=bool((data[20] >> cls.RadioConfigLedControl_ButtonPressedBit) & 0x1),
            misc_options_extended_format=bool((data[21] >> cls.RadioConfigMiscOptions_ExtendedRFPacketBit) & 0x1),
            misc_options_rtc=bool((data[21] >> cls.RadioConfigMiscOptions_RtcEnabledBit) & 0x1),
            misc_options_hci_tx_indication=bool((data[21] >> cls.RadioConfigMiscOptions_HciTXIndicationBit) & 0x1),
            misc_options_hci_power_up_indication=bool(
                (data[21] >> cls.RadioConfigMiscOptions_HciPowerUpIndicationBit) & 0x1),
            misc_options_hci_button_pressed_indication=bool(
                (data[21] >> cls.RadioConfigMiscOptions_HciButtonPressedIndicationBit) & 0x1),
            misc_options_aes=bool((data[21] >> cls.RadioConfigMiscOptions_AesOnBit) & 0x1),
            misc_options_remote_control=bool((data[21] >> cls.RadioConfigMiscOptions_RemoteControlOnBit) & 0x1),
            reserved=data[22],
            power_saving_mode=data[23],
            lbt_threshold=int.from_bytes(data[24:26], "little", signed=True),
        )


class ResetRadioConfigReq(HciMessage):
    ID = 21

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n ResetRadioConfigReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class ResetRadioConfigRsp(HciMessage, DevMgmtStatus):
    ID = 22

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n ResetRadioConfigRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetSystemStatusReq(HciMessage):
    ID = 23

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetSystemStatusReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetSystemStatusRsp(HciMessage, DevMgmtStatus, SystemStatus, RTCTime):
    ID = 24

    def __init__(self,
                 status: int,
                 system_tick_resolution_ms: int,
                 system_ticks: int,
                 rtc_time: _datetime,
                 corrupt_nvm_system_block: bool,
                 corrupt_nvm_radio_block: bool,
                 supply_voltage_mv: int,
                 reserved_extra_status: int,
                 rx_packets_crc_ok: int,
                 rx_packets_crc_ok_and_matched: int,
                 rx_packets_crc_error: int,
                 tx_packets: int,
                 tx_packets_error: int,
                 tx_packets_lbt_busy: int,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.system_tick_resolution_ms = system_tick_resolution_ms
        self.system_ticks = system_ticks
        self.rtc_time = rtc_time
        self.corrupt_nvm_system_block = corrupt_nvm_system_block
        self.corrupt_nvm_radio_block = corrupt_nvm_radio_block
        self.supply_voltage_mv = supply_voltage_mv
        self.reserved_extra_status = reserved_extra_status
        self.rx_packets_crc_ok = rx_packets_crc_ok
        self.rx_packets_crc_ok_and_matched = rx_packets_crc_ok_and_matched
        self.rx_packets_crc_error = rx_packets_crc_error
        self.tx_packets = tx_packets
        self.tx_packets_error = tx_packets_error
        self.tx_packets_lbt_busy = tx_packets_lbt_busy

    def __str__(self):
        return super().__str__() + "\n GetSystemStatusRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  SystemTickResolution: {} ms\n" \
                                   "  SystemTicks: {}\n" \
                                   "  RtcTime: {}\n" \
                                   "  NvmState:\n" \
                                   "   CorruptSystemBlock: {} ({})\n" \
                                   "   CorruptRadioBlock: {} ({})\n" \
                                   "  SupplyVoltage: {} mV\n" \
                                   "  ReservedExtraStatus: {}\n" \
                                   "  RXPacketsCrcOK: {}\n" \
                                   "  RXPacketsCrcOKAndMatched: {}\n" \
                                   "  RXPacketsCrcError: {}\n" \
                                   "  TXPackets: {}\n" \
                                   "  TXPacketsError: {}\n" \
                                   "  TXPacketsLbtBusy: {}\n".format(
            self.status, self.translate_status(self.status),
            self.system_tick_resolution_ms,
            self.system_ticks,
            self.rtc_time,
            self.corrupt_nvm_system_block, self.translate_ok_error(self.corrupt_nvm_system_block),
            self.corrupt_nvm_radio_block, self.translate_ok_error(self.corrupt_nvm_radio_block),
            self.supply_voltage_mv,
            self.reserved_extra_status,
            self.rx_packets_crc_ok,
            self.rx_packets_crc_ok_and_matched,
            self.rx_packets_crc_error,
            self.tx_packets,
            self.tx_packets_error,
            self.tx_packets_lbt_busy,
        )

    def __bytes__(self):
        return super().__bytes__() +\
               self.status.to_bytes(1, "little") +\
               self.system_tick_resolution_ms.to_bytes(4, "little") +\
               self.system_ticks.to_bytes(4, "little") +\
               self.time_to_bytes(self.rtc_time) + \
               ((int(self.corrupt_nvm_system_block) << self.SystemStatusNvmState_SystemBlockBit) |
                (int(self.corrupt_nvm_radio_block) << self.SystemStatusNvmState_RadioBlockBit)).to_bytes(2, "little") +\
               self.supply_voltage_mv.to_bytes(2, "little") +\
               self.reserved_extra_status.to_bytes(2, "little") +\
               self.rx_packets_crc_ok.to_bytes(4, "little") +\
               self.rx_packets_crc_ok_and_matched.to_bytes(4, "little") +\
               self.rx_packets_crc_error.to_bytes(4, "little") +\
               self.tx_packets.to_bytes(4, "little") +\
               self.tx_packets_error.to_bytes(4, "little") +\
               self.tx_packets_lbt_busy.to_bytes(4, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            status=data[0],
            system_tick_resolution_ms=data[1],
            system_ticks=int.from_bytes(data[2:6], "little"),
            rtc_time=cls.bytes_to_time(data[6:10]),
            corrupt_nvm_system_block=bool(
                (int.from_bytes(data[10:12], "little") >> cls.SystemStatusNvmState_SystemBlockBit) & 0x1),
            corrupt_nvm_radio_block=bool(
                (int.from_bytes(data[10:12], "little") >> cls.SystemStatusNvmState_RadioBlockBit) & 0x1),
            supply_voltage_mv=int.from_bytes(data[12:14], "little"),
            reserved_extra_status=int.from_bytes(data[14:16], "little"),
            rx_packets_crc_ok=int.from_bytes(data[16:20], "little"),
            rx_packets_crc_ok_and_matched=int.from_bytes(data[20:24], "little"),
            rx_packets_crc_error=int.from_bytes(data[24:28], "little"),
            tx_packets=int.from_bytes(data[28:32], "little"),
            tx_packets_error=int.from_bytes(data[32:36], "little"),
            tx_packets_lbt_busy=int.from_bytes(data[36:40], "little"),
        )


class SetRadioModeReq(HciMessage, RadioConfig):
    ID = 25

    def __init__(self, radio_mode: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.radio_mode = radio_mode

    def __str__(self):
        return super().__str__() + "\n SetRadioModeReq\n  RadioMode: {} ({})".format(
            self.radio_mode, self.translate_radio_mode(self.radio_mode)
        )

    def __bytes__(self):
        return super().__bytes__() + self.radio_mode.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            radio_mode=data[0]
        )


class SetRadioModeRsp(HciMessage, DevMgmtStatus):
    ID = 26

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetRadioModeRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class PowerUpInd(HciMessage):
    ID = 32

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n PowerUpInd"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class SetAesKeyReq(HciMessage):
    ID = 33

    def __init__(self, aes_key: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.aes_key = aes_key

    def __str__(self):
        return super().__str__() + "\n SetRadioModeRsp:\n  AesKey: {:X}".format(self.aes_key)

    def __bytes__(self):
        return super().__bytes__() + self.aes_key.to_bytes(16, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            aes_key=int.from_bytes(data[:16], "little")
        )


class SetAesKeyRsp(HciMessage, DevMgmtStatus):
    ID = 34

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetAesKeyRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetAesKeyReq(HciMessage):
    ID = 35

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetAesKeyReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetAesKeyRsp(HciMessage, DevMgmtStatus):
    ID = 36

    def __init__(self, status: int, aes_key: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.aes_key = aes_key

    def __str__(self):
        return super().__str__() + "\n SetRadioModeRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  AesKey: {:032X}".format(
            self.status, self.translate_status(self.status),
            self.aes_key,
        )

    def __bytes__(self):
        return super().__bytes__() +\
               self.status.to_bytes(1, "little") +\
               self.aes_key.to_bytes(16, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            status=data[0],
            aes_key=int.from_bytes(data[1:17], "little")
        )


class SetRtcAlarmReq(HciMessage, RtcAlarm):
    ID = 49

    def __init__(self,
                 options: int,
                 hours: int,
                 minutes: int,
                 seconds: int,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.options = options
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self):
        return super().__str__() + "\n SetRtcAlarmReq:\n" \
                                   "  Options: {} ({})\n" \
                                   "  Hours: {}\n" \
                                   "  Minutes: {}\n" \
                                   "  Seconds: {}\n".format(
            self.options, self.translate_rtc_alarm_options(self.options),
            self.hours,
            self.minutes,
            self.seconds,
        )

    def __bytes__(self):
        return super().__bytes__() +\
               self.options.to_bytes(1, "little") +\
               self.hours.to_bytes(1, "little") +\
               self.minutes.to_bytes(1, "little") +\
               self.seconds.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            options=data[0],
            hours=data[1],
            minutes=data[2],
            seconds=data[3],
        )


class SetRtcAlarmRsp(HciMessage, DevMgmtStatus):
    ID = 50

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetRtcAlarmRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class ClearRtcAlarmReq(HciMessage):
    ID = 51

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n ClearRtcAlarmReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class ClearRtcAlarmRsp(HciMessage, DevMgmtStatus):
    ID = 52

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n ClearRtcAlarmRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetRtcAlarmReq(HciMessage):
    ID = 53

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetRtcAlarmReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetRtcAlarmRsp(HciMessage, DevMgmtStatus, RtcAlarm):
    ID = 54

    def __init__(self,
                 status: int,
                 alarm_status: int,
                 options: int,
                 hours: int,
                 minutes: int,
                 seconds: int,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.alarm_status = alarm_status
        self.options = options
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self):
        return super().__str__() + "\n GetRtcAlarmRsp:\n" \
                                   "  Status: {} ({})\n" \
                                   "  AlarmStatus: {} ({})\n" \
                                   "  Options: {} ({})\n" \
                                   "  Hours: {}\n" \
                                   "  Minutes: {}\n" \
                                   "  Seconds: {}\n".format(
            self.status, self.translate_status(self.status),
            self.alarm_status, self.translate_rtc_alarm_status(self.alarm_status),
            self.options, self.translate_rtc_alarm_options(self.options),
            self.hours,
            self.minutes,
            self.seconds,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.status.to_bytes(1, "little") + \
               self.alarm_status.to_bytes(1, "little") + \
               self.options.to_bytes(1, "little") + \
               self.hours.to_bytes(1, "little") + \
               self.minutes.to_bytes(1, "little") + \
               self.seconds.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            status=data[0],
            alarm_status=data[1],
            options=data[2],
            hours=data[3],
            minutes=data[4],
            seconds=data[5],
        )


class RtcAlarmInd(HciMessage, DevMgmtStatus):
    ID = 56

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n RtcAlarmInd:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class SetHciConfigReq(HciMessage, HciConfig):
    ID = 65

    def __init__(self,
                 nvm_flag: int,
                 baudrate: int = HciConfig.HciConfigBaudrate_115200_bps,
                 wakeup_chars_n: int = 0,
                 tx_hold_time_ms: int = 0,
                 rx_hold_time_ms: int = 0,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.nvm_flag = nvm_flag
        self.baudrate = baudrate
        self.wakeup_chars_n = wakeup_chars_n
        self.tx_hold_time_ms = tx_hold_time_ms
        self.rx_hold_time_ms = rx_hold_time_ms

    def __str__(self):
        return super().__str__() + "\n SetHciConfigReq:\n" \
                                   "  NvmFlag: {} ({})\n" \
                                   "  Baudrate: {} ({})\n" \
                                   "  WakeupChars: {}\n" \
                                   "  TXHoldTime: {} ms\n" \
                                   "  RXHoldTime: {} ms\n".format(
            self.nvm_flag, self.translate_nvm_flag(self.nvm_flag),
            self.baudrate, self.translate_hci_baudrate(self.baudrate),
            self.wakeup_chars_n,
            self.tx_hold_time_ms,
            self.rx_hold_time_ms,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.nvm_flag.to_bytes(1, "little") + \
               self.baudrate.to_bytes(1, "little") + \
               self.wakeup_chars_n.to_bytes(2, "little") + \
               self.tx_hold_time_ms.to_bytes(1, "little") + \
               self.rx_hold_time_ms.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            nvm_flag=data[0],
            baudrate=data[1],
            wakeup_chars_n=int.from_bytes(data[2:4], "little"),
            tx_hold_time_ms=data[4],
            rx_hold_time_ms=data[5],
        )


class SetHciConfigRsp(HciMessage, DevMgmtStatus):
    ID = 66

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetHciConfigRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class GetHciConfigReq(HciMessage):
    ID = 67

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n GetHciConfigReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class GetHciConfigRsp(HciMessage, DevMgmtStatus, HciConfig):
    ID = 68

    def __init__(self,
                 status: int,
                 baudrate: int = HciConfig.HciConfigBaudrate_115200_bps,
                 wakeup_chars_n: int = 0,
                 tx_hold_time_ms: int = 0,
                 rx_hold_time_ms: int = 0,
                 ):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = status
        self.baudrate = baudrate
        self.wakeup_chars_n = wakeup_chars_n
        self.tx_hold_time_ms = tx_hold_time_ms
        self.rx_hold_time_ms = rx_hold_time_ms

    def __str__(self):
        return super().__str__() + "\n SetHciConfigReq:\n" \
                                   "  Status: {} ({})\n" \
                                   "  Baudrate: {} ({})\n" \
                                   "  WakeupChars: {}\n" \
                                   "  TXHoldTime: {} ms\n" \
                                   "  RXHoldTime: {} ms\n".format(
            self.status, self.translate_status(self.status),
            self.baudrate, self.translate_hci_baudrate(self.baudrate),
            self.wakeup_chars_n,
            self.tx_hold_time_ms,
            self.rx_hold_time_ms,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.status.to_bytes(1, "little") + \
               self.baudrate.to_bytes(1, "little") + \
               self.wakeup_chars_n.to_bytes(2, "little") + \
               self.tx_hold_time_ms.to_bytes(1, "little") + \
               self.rx_hold_time_ms.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            status=data[0],
            baudrate=data[1],
            wakeup_chars_n=int.from_bytes(data[2:4], "little"),
            tx_hold_time_ms=data[4],
            rx_hold_time_ms=data[5],
        )


class InitBootloaderReq(HciMessage):
    ID = 246

    def __init__(self):
        super().__init__(HciMessage.DevMgmt, self.ID)

    def __str__(self):
        return super().__str__() + "\n InitBootloaderReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class InitBootloaderRsp(HciMessage, DevMgmtStatus):
    ID = 247

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.DevMgmt, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n InitBootloaderRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class StartRadioLinkTestReq(HciMessage):
    ID = 1

    TestMode_SingleRun = 0
    TestMode_RepeatedRun = 1

    def __init__(self,
                 dst_group_address: int,
                 dst_device_address: int,
                 packet_size: int,
                 number_packets: int,
                 test_mode: int,
                 ):
        super().__init__(HciMessage.RadioLinkTest, self.ID)
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.packet_size = packet_size
        self.number_packets = number_packets
        self.test_mode = test_mode

    def __str__(self):
        return super().__str__() + "\n StartRadioLinkTestReq:\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  PacketSize: {}\n" \
                                   "  NumberPackets: {}\n" \
                                   "  TestMode: {} ({})\n".format(
            self.dst_group_address,
            self.dst_device_address,
            self.packet_size,
            self.number_packets,
            self.test_mode, self.translate_test_mode(self.test_mode),
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.packet_size.to_bytes(1, "little") + \
               self.number_packets.to_bytes(2, "little") + \
               self.test_mode.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dst_group_address=data[0],
            dst_device_address=int.from_bytes(data[1:3], "little"),
            packet_size=data[3],
            number_packets=int.from_bytes(data[4:6], "little"),
            test_mode=data[6],
        )

    @staticmethod
    def translate_test_mode(value: int) -> str:
        mapping = {
            0: "single_run",
            1: "repeated_run",
        }
        return mapping.get(value, "unknown")


class StartRadioLinkTestRsp(HciMessage, DevMgmtStatus):
    ID = 2

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.RadioLinkTest, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetHciConfigRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class StopRadioLinkTestReq(HciMessage):
    ID = 3

    def __init__(self):
        super().__init__(HciMessage.RadioLinkTest, self.ID)

    def __str__(self):
        return super().__str__() + "\n StopRadioLinkTestReq"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class StopRadioLinkTestRsp(HciMessage, DevMgmtStatus):
    ID = 4

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.RadioLinkTest, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n StopRadioLinkTestRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class RadioLinkTestStatusInd(HciMessage):
    ID = 6

    TestStatus_OK = 0
    TestStatus_StartNewRun = 1

    def __init__(self,
                 test_status: int,
                 local_tx_counter: int,
                 local_rx_counter: int,
                 peer_tx_counter: int,
                 peer_rx_counter: int,
                 local_rssi_dbm: int,
                 peer_rssi_dbm: int,
                 local_snr_db: int,
                 peer_snr_db: int,
                 ):
        super().__init__(HciMessage.RadioLinkTest, self.ID)
        self.test_status = test_status
        self.local_tx_counter = local_tx_counter
        self.local_rx_counter = local_rx_counter
        self.peer_tx_counter = peer_tx_counter
        self.peer_rx_counter = peer_rx_counter
        self.local_rssi_dbm = local_rssi_dbm
        self.peer_rssi_dbm = peer_rssi_dbm
        self.local_snr_db = local_snr_db
        self.peer_snr_db = peer_snr_db

    def __str__(self):
        return super().__str__() + "\n RadioLinkTestStatusInd:\n" \
                                   "  TestStatus: {} ({})\n" \
                                   "  LocalTXCounter: {}\n" \
                                   "  LocalRXCounter: {}\n" \
                                   "  PeerTXCounter: {}\n" \
                                   "  PeerRXCounter: {}\n" \
                                   "  LocalRssi: {} dBm\n" \
                                   "  PeerRssi: {} dBm\n" \
                                   "  LocalSnr: {} dB\n" \
                                   "  PeerSnr: {} dB\n".format(
            self.test_status, self.translate_test_status(self.test_status),
            self.local_tx_counter,
            self.local_rx_counter,
            self.peer_tx_counter,
            self.peer_rx_counter,
            self.local_rssi_dbm,
            self.peer_rssi_dbm,
            self.local_snr_db,
            self.peer_snr_db,
        )

    def __bytes__(self):
        return super().__bytes__() + \
                self.test_status.to_bytes(1, "little") + \
                self.local_tx_counter.to_bytes(2, "little") + \
                self.local_rx_counter.to_bytes(2, "little") + \
                self.peer_tx_counter.to_bytes(2, "little") + \
                self.peer_rx_counter.to_bytes(2, "little") + \
                self.local_rssi_dbm.to_bytes(2, "little", signed=True) + \
                self.peer_rssi_dbm.to_bytes(2, "little", signed=True) + \
                self.local_snr_db.to_bytes(1, "little", signed=True) + \
                self.peer_snr_db.to_bytes(1, "little", signed=True)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            test_status=data[0],
            local_tx_counter=int.from_bytes(data[1:3], "little"),
            local_rx_counter=int.from_bytes(data[3:5], "little"),
            peer_tx_counter=int.from_bytes(data[5:7], "little"),
            peer_rx_counter=int.from_bytes(data[7:9], "little"),
            local_rssi_dbm=int.from_bytes(data[9:11], "little", signed=True),
            peer_rssi_dbm=int.from_bytes(data[11:13], "little", signed=True),
            local_snr_db=int.from_bytes(data[13:14], "little", signed=True),
            peer_snr_db=int.from_bytes(data[14:15], "little", signed=True),
        )

    @staticmethod
    def translate_test_status(value: int) -> str:
        mapping = {
            0: "ok",
            1: "start_new_run",
        }
        return mapping.get(value, "unknown")


class SendUnreliableDataReq(HciMessage):
    ID = 1

    def __init__(self,
                 dst_group_address: int,
                 dst_device_address: int,
                 payload: bytes,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.payload = payload

    def __str__(self):
        return super().__str__() + "\n SendUnreliableDataReq:\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}".format(
            self.dst_group_address,
            self.dst_device_address,
            self.payload.hex(),
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.payload

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dst_group_address=data[0],
            dst_device_address=int.from_bytes(data[1:3], "little"),
            payload=data[3:],
        )


class SendUnreliableDataRsp(HciMessage, RadioLinkStatus):
    ID = 2

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SendUnreliableDataRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class UnreliableDataRXInd(HciMessage, DataFormat, RTCTime):
    ID = 4

    def __init__(self,
                 status_extended: bool,
                 status_decrypted: bool,
                 status_decryption_error: bool,
                 status_encrypted: bool,
                 dst_group_address: int,
                 dst_device_address: int,
                 src_group_address: int,
                 src_device_address: int,
                 payload: bytes,
                 rssi_dbm: int = 0,
                 snr_db: int = 0,
                 rx_time: _datetime = None,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status_extended = status_extended
        self.status_decrypted = status_decrypted
        self.status_decryption_error = status_decryption_error
        self.status_encrypted = status_encrypted
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.src_group_address = src_group_address
        self.src_device_address = src_device_address
        self.payload = payload
        self.rssi_dbm = rssi_dbm
        self.snr_db = snr_db
        self.rx_time = rx_time

    def __str__(self):
        return super().__str__() + "\n UnreliableDataRXInd:\n" \
                                   "  Status:\n" \
                                   "   Extended: {}\n" \
                                   "   Decrypted: {}\n" \
                                   "   DecryptionError: {}\n" \
                                   "   Encrypted: {}\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  SrcGroupAddress: 0x{:x}\n" \
                                   "  SrcDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}\n" \
                                   "  Rssi: {} dBm\n" \
                                   "  Snr: {} dB\n" \
                                   "  RXTime: {}".format(
            self.status_extended,
            self.status_decrypted,
            self.status_decryption_error,
            self.status_encrypted,
            self.dst_group_address,
            self.dst_device_address,
            self.src_group_address,
            self.src_device_address,
            self.payload.hex(),
            self.rssi_dbm,
            self.snr_db,
            self.rx_time,
        )

    def __bytes__(self):
        data = super().__bytes__() + \
               ((int(self.status_extended) << self.DataFormat_ExtendedBit) |
                (int(self.status_decrypted) << self.DataFormat_DecryptedBit) |
                (int(self.status_decryption_error) << self.DataFormat_DecryptionErrorBit) |
                (int(self.status_encrypted) <<
                 self.DataFormat_EncryptedBit)).to_bytes(1, "little") + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.src_group_address.to_bytes(1, "little") + \
               self.src_device_address.to_bytes(2, "little") + \
               self.payload
        if self.status_extended:
            data += self.rssi_dbm.to_bytes(2, "little") +\
                    self.snr_db.to_bytes(1, "little") +\
                    self.time_to_bytes(self.rx_time)
        return data

    @classmethod
    def from_bytes(cls, data: bytes):
        rssi_dbm = 0
        snr_db = 0
        rx_time = None
        payload = data[7:]

        status_extended = bool((data[0] >> cls.DataFormat_ExtendedBit) & 0x1)
        if status_extended:
            rssi_dbm = int.from_bytes(data[-7:-5], "little", signed=True)
            snr_db = int.from_bytes(data[-5:-4], "little", signed=True)
            rx_time = cls.bytes_to_time(data[-4:])
            payload = data[7:-7]

        return cls(
            status_extended=status_extended,
            status_decrypted=bool((data[0] >> cls.DataFormat_DecryptedBit) & 0x1),
            status_decryption_error=bool((data[0] >> cls.DataFormat_DecryptionErrorBit) & 0x1),
            status_encrypted=bool((data[0] >> cls.DataFormat_EncryptedBit) & 0x1),
            dst_group_address=data[1],
            dst_device_address=int.from_bytes(data[2:4], "little"),
            src_group_address=data[4],
            src_device_address=int.from_bytes(data[5:7], "little"),
            payload=payload,
            rssi_dbm=rssi_dbm,
            snr_db=snr_db,
            rx_time=rx_time,
        )


class UnreliableDataTXInd(HciMessage, RadioLinkStatus):
    ID = 6

    def __init__(self,
                 dev_mgmt_status: int,
                 tx_event_counter: int,
                 rf_message_airtime_ms: int,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status
        self.tx_event_counter = tx_event_counter
        self.rf_message_airtime_ms = rf_message_airtime_ms

    def __str__(self):
        return super().__str__() + "\n UnreliableDataTXInd:\n" \
                                   "  Status: {} ({})\n" \
                                   "  TXEventCounter: {}\n" \
                                   "  RFMessageAirtime: {} ms".format(
            self.status, self.translate_status(self.status),
            self.tx_event_counter,
            self.rf_message_airtime_ms,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.status.to_bytes(1, "little") + \
               self.tx_event_counter.to_bytes(2, "little") + \
               self.rf_message_airtime_ms.to_bytes(4, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dev_mgmt_status=data[0],
            tx_event_counter=int.from_bytes(data[1:3], "little"),
            rf_message_airtime_ms=int.from_bytes(data[3:7], "little"),
        )


class RawDataRXInd(HciMessage, DataFormat, RTCTime, RadioControl):
    ID = 8

    def __init__(self,
                 status_extended: bool,
                 status_decrypted: bool,
                 status_decryption_error: bool,
                 status_encrypted: bool,
                 ctrl_ack_request: bool,
                 ctrl_ack: bool,
                 ctrl_encrypted: bool,
                 dst_group_address: int,
                 dst_device_address: int,
                 src_group_address: int,
                 src_device_address: int,
                 radio_stack_fields_reserved: int,
                 payload: bytes,
                 rssi_dbm: int = 0,
                 snr_db: int = 0,
                 rx_time: _datetime = None,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status_extended = status_extended
        self.status_decrypted = status_decrypted
        self.status_decryption_error = status_decryption_error
        self.status_encrypted = status_encrypted
        self.ctrl_ack_request = ctrl_ack_request
        self.ctrl_ack = ctrl_ack
        self.ctrl_encrypted = ctrl_encrypted
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.src_group_address = src_group_address
        self.src_device_address = src_device_address
        self.radio_stack_fields_reserved = radio_stack_fields_reserved
        self.payload = payload
        self.rssi_dbm = rssi_dbm
        self.snr_db = snr_db
        self.rx_time = rx_time

    def __str__(self):
        return super().__str__() + "\n RawDataRXInd:\n" \
                                   "  Status:\n" \
                                   "   Extended: {}\n" \
                                   "   Decrypted: {}\n" \
                                   "   DecryptionError: {}\n" \
                                   "   Encrypted: {}\n" \
                                   "  RadioControl:\n" \
                                   "   AckRequested: {}\n" \
                                   "   Ack: {}\n" \
                                   "   Encrypted: {}\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  SrcGroupAddress: 0x{:x}\n" \
                                   "  SrcDeviceAddress: 0x{:x}\n" \
                                   "  RadioStackFieldsReserved: 0x{:x}\n" \
                                   "  Payload: {}\n" \
                                   "  Rssi: {} dBm\n" \
                                   "  Snr: {} dB\n" \
                                   "  RXTime: {}".format(
            self.status_extended,
            self.status_decrypted,
            self.status_decryption_error,
            self.status_encrypted,
            self.ctrl_ack_request,
            self.ctrl_ack,
            self.ctrl_encrypted,
            self.dst_group_address,
            self.dst_device_address,
            self.src_group_address,
            self.src_device_address,
            self.radio_stack_fields_reserved,
            self.payload.hex(),
            self.rssi_dbm,
            self.snr_db,
            self.rx_time,
        )

    def __bytes__(self):
        data = super().__bytes__() + \
               ((int(self.status_extended) << self.DataFormat_ExtendedBit) |
                (int(self.status_decrypted) << self.DataFormat_DecryptedBit) |
                (int(self.status_decryption_error) << self.DataFormat_DecryptionErrorBit) |
                (int(self.status_encrypted) <<
                 self.DataFormat_EncryptedBit)).to_bytes(1, "little") + \
               ((int(self.ctrl_ack_request) << self.RadioControl_AckRequestBit) |
                (int(self.ctrl_ack) << self.RadioControl_AckBit) |
                (int(self.ctrl_encrypted) <<
                 self.RadioControl_EncryptedBit)).to_bytes(1, "little") + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.src_group_address.to_bytes(1, "little") + \
               self.src_device_address.to_bytes(2, "little") + \
               self.radio_stack_fields_reserved.to_bytes(1, "little") + \
               self.payload
        if self.status_extended:
            data += self.rssi_dbm.to_bytes(2, "little") + \
                    self.snr_db.to_bytes(1, "little") + \
                    self.time_to_bytes(self.rx_time)
        return data

    @classmethod
    def from_bytes(cls, data: bytes):
        rssi_dbm = 0
        snr_db = 0
        rx_time = None
        payload = data[9:]

        status_extended = bool((data[0] >> cls.DataFormat_ExtendedBit) & 0x1)
        if status_extended:
            rssi_dbm = int.from_bytes(data[-7:-5], "little", signed=True)
            snr_db = int.from_bytes(data[-5:-4], "little", signed=True)
            rx_time = cls.bytes_to_time(data[-4:])
            payload = data[9:-7]

        return cls(
            status_extended=status_extended,
            status_decrypted=bool((data[0] >> cls.DataFormat_DecryptedBit) & 0x1),
            status_decryption_error=bool((data[0] >> cls.DataFormat_DecryptionErrorBit) & 0x1),
            status_encrypted=bool((data[0] >> cls.DataFormat_EncryptedBit) & 0x1),
            ctrl_ack_request=bool((data[1] >> cls.RadioControl_AckRequestBit) & 0x1),
            ctrl_ack=bool((data[1] >> cls.RadioControl_AckBit) & 0x1),
            ctrl_encrypted=bool((data[1] >> cls.RadioControl_EncryptedBit) & 0x1),
            dst_group_address=data[2],
            dst_device_address=int.from_bytes(data[3:5], "little"),
            src_group_address=data[5],
            src_device_address=int.from_bytes(data[6:8], "little"),
            radio_stack_fields_reserved=data[8],
            payload=payload,
            rssi_dbm=rssi_dbm,
            snr_db=snr_db,
            rx_time=rx_time,
        )


class SendConfirmedDataReq(HciMessage):
    ID = 9

    def __init__(self,
                 dst_group_address: int,
                 dst_device_address: int,
                 payload: bytes,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.payload = payload

    def __str__(self):
        return super().__str__() + "\n SendConfirmedDataReq:\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}".format(
            self.dst_group_address,
            self.dst_device_address,
            self.payload.hex(),
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.payload

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dst_group_address=data[0],
            dst_device_address=int.from_bytes(data[1:3], "little"),
            payload=data[3:],
        )


class SendConfirmedDataRsp(HciMessage, RadioLinkStatus):
    ID = 10

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SendConfirmedDataRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class ConfirmedDataRXInd(HciMessage, DataFormat, RTCTime):
    ID = 12

    def __init__(self,
                 status_extended: bool,
                 status_decrypted: bool,
                 status_decryption_error: bool,
                 status_encrypted: bool,
                 dst_group_address: int,
                 dst_device_address: int,
                 src_group_address: int,
                 src_device_address: int,
                 payload: bytes,
                 rssi_dbm: int = 0,
                 snr_db: int = 0,
                 rx_time: _datetime = None,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status_extended = status_extended
        self.status_decrypted = status_decrypted
        self.status_decryption_error = status_decryption_error
        self.status_encrypted = status_encrypted
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.src_group_address = src_group_address
        self.src_device_address = src_device_address
        self.payload = payload
        self.rssi_dbm = rssi_dbm
        self.snr_db = snr_db
        self.rx_time = rx_time

    def __str__(self):
        return super().__str__() + "\n ConfirmedDataRXInd:\n" \
                                   "  Status:\n" \
                                   "   Extended: {}\n" \
                                   "   Decrypted: {}\n" \
                                   "   DecryptionError: {}\n" \
                                   "   Encrypted: {}\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  SrcGroupAddress: 0x{:x}\n" \
                                   "  SrcDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}\n" \
                                   "  Rssi: {} dBm\n" \
                                   "  Snr: {} dB\n" \
                                   "  RXTime: {}".format(
            self.status_extended,
            self.status_decrypted,
            self.status_decryption_error,
            self.status_encrypted,
            self.dst_group_address,
            self.dst_device_address,
            self.src_group_address,
            self.src_device_address,
            self.payload.hex(),
            self.rssi_dbm,
            self.snr_db,
            self.rx_time,
        )

    def __bytes__(self):
        data = super().__bytes__() + \
               ((int(self.status_extended) << self.DataFormat_ExtendedBit) |
                (int(self.status_decrypted) << self.DataFormat_DecryptedBit) |
                (int(self.status_decryption_error) << self.DataFormat_DecryptionErrorBit) |
                (int(self.status_encrypted) <<
                 self.DataFormat_EncryptedBit)).to_bytes(1, "little") + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.src_group_address.to_bytes(1, "little") + \
               self.src_device_address.to_bytes(2, "little") + \
               self.payload
        if self.status_extended:
            data += self.rssi_dbm.to_bytes(2, "little") + \
                    self.snr_db.to_bytes(1, "little") + \
                    self.time_to_bytes(self.rx_time)
        return data

    @classmethod
    def from_bytes(cls, data: bytes):
        rssi_dbm = 0
        snr_db = 0
        rx_time = None
        payload = data[7:]

        status_extended = bool((data[0] >> cls.DataFormat_ExtendedBit) & 0x1)
        if status_extended:
            rssi_dbm = int.from_bytes(data[-7:-5], "little", signed=True)
            snr_db = int.from_bytes(data[-5:-4], "little", signed=True)
            rx_time = cls.bytes_to_time(data[-4:])
            payload = data[7:-7]

        return cls(
            status_extended=status_extended,
            status_decrypted=bool((data[0] >> cls.DataFormat_DecryptedBit) & 0x1),
            status_decryption_error=bool((data[0] >> cls.DataFormat_DecryptionErrorBit) & 0x1),
            status_encrypted=bool((data[0] >> cls.DataFormat_EncryptedBit) & 0x1),
            dst_group_address=data[1],
            dst_device_address=int.from_bytes(data[2:4], "little"),
            src_group_address=data[4],
            src_device_address=int.from_bytes(data[5:7], "little"),
            payload=payload,
            rssi_dbm=rssi_dbm,
            snr_db=snr_db,
            rx_time=rx_time,
        )


class ConfirmedDataTXInd(HciMessage, RadioLinkStatus):
    ID = 14

    def __init__(self,
                 dev_mgmt_status: int,
                 tx_event_counter: int,
                 rf_message_airtime_ms: int,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status
        self.tx_event_counter = tx_event_counter
        self.rf_message_airtime_ms = rf_message_airtime_ms

    def __str__(self):
        return super().__str__() + "\n ConfirmedDataTXInd:\n" \
                                   "  Status: {} ({})\n" \
                                   "  TXEventCounter: {}\n" \
                                   "  RFMessageAirtime: {} ms".format(
            self.status, self.translate_status(self.status),
            self.tx_event_counter,
            self.rf_message_airtime_ms,
        )

    def __bytes__(self):
        return super().__bytes__() +\
               self.status.to_bytes(1, "little") +\
               self.tx_event_counter.to_bytes(2, "little") +\
               self.rf_message_airtime_ms.to_bytes(4, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dev_mgmt_status=data[0],
            tx_event_counter=int.from_bytes(data[1:3], "little"),
            rf_message_airtime_ms=int.from_bytes(data[3:7], "little"),
        )


class AckRXInd(HciMessage, DataFormat, RTCTime):
    ID = 16

    def __init__(self,
                 status_extended: bool,
                 status_decrypted: bool,
                 status_decryption_error: bool,
                 status_encrypted: bool,
                 dst_group_address: int,
                 dst_device_address: int,
                 src_group_address: int,
                 src_device_address: int,
                 payload: bytes,
                 rssi_dbm: int = 0,
                 snr_db: int = 0,
                 rx_time: _datetime = None,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status_extended = status_extended
        self.status_decrypted = status_decrypted
        self.status_decryption_error = status_decryption_error
        self.status_encrypted = status_encrypted
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.src_group_address = src_group_address
        self.src_device_address = src_device_address
        self.payload = payload
        self.rssi_dbm = rssi_dbm
        self.snr_db = snr_db
        self.rx_time = rx_time

    def __str__(self):
        return super().__str__() + "\n AckRXInd:\n" \
                                   "  Status:\n" \
                                   "   Extended: {}\n" \
                                   "   Decrypted: {}\n" \
                                   "   DecryptionError: {}\n" \
                                   "   Encrypted: {}\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  SrcGroupAddress: 0x{:x}\n" \
                                   "  SrcDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}\n" \
                                   "  Rssi: {} dBm\n" \
                                   "  Snr: {} dB\n" \
                                   "  RXTime: {}".format(
            self.status_extended,
            self.status_decrypted,
            self.status_decryption_error,
            self.status_encrypted,
            self.dst_group_address,
            self.dst_device_address,
            self.src_group_address,
            self.src_device_address,
            self.payload.hex(),
            self.rssi_dbm,
            self.snr_db,
            self.rx_time,
        )

    def __bytes__(self):
        data = super().__bytes__() + \
               ((int(self.status_extended) << self.DataFormat_ExtendedBit) |
                (int(self.status_decrypted) << self.DataFormat_DecryptedBit) |
                (int(self.status_decryption_error) << self.DataFormat_DecryptionErrorBit) |
                (int(self.status_encrypted) <<
                 self.DataFormat_EncryptedBit)).to_bytes(1, "little") + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.src_group_address.to_bytes(1, "little") + \
               self.src_device_address.to_bytes(2, "little") + \
               self.payload
        if self.status_extended:
            data += self.rssi_dbm.to_bytes(2, "little") + \
                    self.snr_db.to_bytes(1, "little") + \
                    self.time_to_bytes(self.rx_time)
        return data

    @classmethod
    def from_bytes(cls, data: bytes):
        rssi_dbm = 0
        snr_db = 0
        rx_time = None
        payload = data[7:]

        status_extended = bool((data[0] >> cls.DataFormat_ExtendedBit) & 0x1)
        if status_extended:
            rssi_dbm = int.from_bytes(data[-7:-5], "little", signed=True)
            snr_db = int.from_bytes(data[-5:-4], "little", signed=True)
            rx_time = cls.bytes_to_time(data[-4:])
            payload = data[7:-7]

        return cls(
            status_extended=status_extended,
            status_decrypted=bool((data[0] >> cls.DataFormat_DecryptedBit) & 0x1),
            status_decryption_error=bool((data[0] >> cls.DataFormat_DecryptionErrorBit) & 0x1),
            status_encrypted=bool((data[0] >> cls.DataFormat_EncryptedBit) & 0x1),
            dst_group_address=data[1],
            dst_device_address=int.from_bytes(data[2:4], "little"),
            src_group_address=data[4],
            src_device_address=int.from_bytes(data[5:7], "little"),
            payload=payload,
            rssi_dbm=rssi_dbm,
            snr_db=snr_db,
            rx_time=rx_time,
        )


class AckTimeoutInd(HciMessage):
    ID = 18

    def __init__(self):
        super().__init__(HciMessage.RadioLinkTest, self.ID)

    def __str__(self):
        return super().__str__() + "\n AckTimeoutInd"

    def __bytes__(self):
        return super().__bytes__()

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class AckTXInd(HciMessage, RadioLinkStatus):
    ID = 20

    def __init__(self,
                 dev_mgmt_status: int,
                 tx_event_counter: int,
                 rf_message_airtime_ms: int,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status
        self.tx_event_counter = tx_event_counter
        self.rf_message_airtime_ms = rf_message_airtime_ms

    def __str__(self):
        return super().__str__() + "\n AckTXInd:\n" \
                                   "  Status: {} ({})\n" \
                                   "  TXEventCounter: {}\n" \
                                   "  RFMessageAirtime: {} ms".format(
            self.status, self.translate_status(self.status),
            self.tx_event_counter,
            self.rf_message_airtime_ms,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.status.to_bytes(1, "little") + \
               self.tx_event_counter.to_bytes(2, "little") + \
               self.rf_message_airtime_ms.to_bytes(4, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dev_mgmt_status=data[0],
            tx_event_counter=int.from_bytes(data[1:3], "little"),
            rf_message_airtime_ms=int.from_bytes(data[3:7], "little"),
        )


class SetAckDataReq(HciMessage):
    ID = 21

    def __init__(self,
                 dst_group_address: int,
                 dst_device_address: int,
                 payload: bytes,
                 ):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.payload = payload

    def __str__(self):
        return super().__str__() + "\n SetAckDataReq:\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  Payload: {}".format(
            self.dst_group_address,
            self.dst_device_address,
            self.payload.hex(),
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.payload

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dst_group_address=data[0],
            dst_device_address=int.from_bytes(data[1:3], "little"),
            payload=data[3:],
        )


class SetAckDataRsp(HciMessage, RadioLinkStatus):
    ID = 22

    def __init__(self, dev_mgmt_status: int):
        super().__init__(HciMessage.RadioLink, self.ID)
        self.status = dev_mgmt_status

    def __str__(self):
        return super().__str__() + "\n SetAckDataRsp:\n  Status: {} ({})".format(
            self.status, self.translate_status(self.status))

    def __bytes__(self):
        return super().__bytes__() + self.status.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        status = int.from_bytes(data, "little")
        return cls(status)


class ButtonPressedInd(HciMessage):
    ID = 2

    def __init__(self,
                 dst_group_address: int,
                 dst_device_address: int,
                 src_group_address: int,
                 src_device_address: int,
                 button_bitmap: int,
                 ):
        super().__init__(HciMessage.RemoteCtrl, self.ID)
        self.dst_group_address = dst_group_address
        self.dst_device_address = dst_device_address
        self.src_group_address = src_group_address
        self.src_device_address = src_device_address
        self.button_bitmap = button_bitmap

    def __str__(self):
        return super().__str__() + "\n ButtonPressedInd:\n" \
                                   "  DstGroupAddress: 0x{:x}\n" \
                                   "  DstDeviceAddress: 0x{:x}\n" \
                                   "  SrcGroupAddress: 0x{:x}\n" \
                                   "  SrcDeviceAddress: 0x{:x}\n" \
                                   "  ButtonBitmap: 0x{:x}".format(
            self.dst_group_address,
            self.dst_device_address,
            self.src_group_address,
            self.src_device_address,
            self.button_bitmap,
        )

    def __bytes__(self):
        return super().__bytes__() + \
               self.dst_group_address.to_bytes(1, "little") + \
               self.dst_device_address.to_bytes(2, "little") + \
               self.src_group_address.to_bytes(1, "little") + \
               self.src_device_address.to_bytes(2, "little") + \
               self.button_bitmap.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dst_group_address=data[0],
            dst_device_address=int.from_bytes(data[1:3], "little"),
            src_group_address=data[3],
            src_device_address=int.from_bytes(data[4:6], "little"),
            button_bitmap=data[6],
        )


class IM282A:
    def __init__(self, address: str, port: int, timeout: float = None):
        self._sock = sliplib.SlipSocket.create_connection((address, port), timeout)
        self._handlers = {}
        self.default_handler = self.default_handler_function

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sock.close()

    def close(self):
        self._sock.close()

    def send(self, msg: HciMessage):
        data = bytes(msg)
        crc = _Crc16X25.calcbytes(data, byteorder="little")
        self._sock.send_msg(data+crc)

    def register_handler(self, endpoint_id: int, message_id: int, handler: _Callable[[bytes]]):
        h = self._handlers.get((endpoint_id, message_id))
        if h is None:
            self._handlers[(endpoint_id, message_id)] = [handler]
        else:
            h.append(handler)

    def receive(self):
        data = self._sock.recv_msg()

        # Check CRC
        crc = _Crc16X25.calc(data)
        if crc != 0xf47:
            # Just log CRC errors
            print("CRC check failed on receive: {}".format(data.hex()), file=sys.stderr)
            return

        # Handle message
        handlers = self._handlers.get((data[0], data[1]))
        if handlers is not None:
            for h in handlers:
                h(data[2:-2])
        else:
            self.default_handler(data[:2], data[2:-2])

    @staticmethod
    def default_handler_function(header: bytes, data: bytes):
        hci_message = HciMessage.from_bytes(header)
        msg_class = hci_message.get_msg_class()
        msg = msg_class.from_bytes(data)
        print(msg)
