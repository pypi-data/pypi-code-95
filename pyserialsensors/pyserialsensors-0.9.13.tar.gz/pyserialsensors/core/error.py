# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT


class Error:
    def __init__(self):
        """
        declaration of error types and error messages
        """
        # List of the errors
        self.error_list = ["crc", "read", "unsupported_sensor"]

    def error_dict(self, obj):
        """
        Compile error dict and provide sensor specifics
        """
        out = {
            "object": "ERROR",
            "FTDIserial": obj.ftdi_serial,
            "id": obj.sensor_id,
            "sensor_type": obj.__name__,
            "SENSORserial": obj.serial_number,
            "error_type": "",
            "message": "",
            "COMport": "",
        }
        if obj._serial_mode != "COM":
            out["MUXaddress"] = str(obj.mux.address)
            out["MUXport"] = str(obj.mux_port)
        else:
            out["COMport"] = obj.port

        return out

    def unsupported_sensor(self, obj):
        """
        Sensor type not supported
        :return: [DICT] Error dict object
        """
        val = self.error_dict(obj)
        val["error_type"] = "InvalidSensor"
        val["message"] = "[ERROR] Sensor not supported."
        return val

    def crc(self, obj):
        """
        CRC error declaration
        :return: [DICT] CRC-ERROR object
        """
        val = self.error_dict(obj)
        val["error_type"] = "CRC"
        val["message"] = "[ERROR] CRC check failed"
        return val

    def read(self, obj):
        """
        read error declaration
        :param ftdi: [STRING] serial number of the FTDI chip (USB interface)
        :param mux: [STRING] Hex address of the multiplexer
        :param mux_port: [STRING] address of the multiplexer port
        :param sensor_id: [STRING] identifier of the sensor
        :return: [DICT] read ERROR object
        """
        val = self.error_dict(obj)
        val["error_type"] = "read"
        val["message"] = "[ERROR] reading sensor failed"
        return val

    @staticmethod
    def msg(error):
        """
        makes error message
        :param error: [DICT] error object
        :return: [STRING] error message
        """
        if error["object"] == "ERROR":
            msg = f"{error['message']}!\
                    {error['id']}@{error['FTDIserial']} | \
                    {error['MUXaddress']}| {error['MUXport']}"
            return msg
        else:
            return None

    @staticmethod
    def checksum(byte_values, crc_value, crc_init=0xFF, crc_poly=0x131):
        """
        calculates the crc8 value based on LSB is default
        :param byte_values: [BYTE ARRAY]
        :param crc_value: [HEX] crc values of the byte_values
        :param crc_init: initialise crc (0xFF means LSB)
        :param crc_poly: crc generator polynomial
        :return: [LIST] = [crc [INT], [BOOLEAN] True=check Ok, False=check failed]
        """
        crc = crc_init
        for byte in byte_values:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc <<= 1
                    crc ^= crc_poly
                else:
                    crc <<= 1
                    crc ^= 0x00
        if crc == crc_value:
            return [crc, True]
        else:
            return [crc, False]


class TimeoutError(Exception):
    """
    Taken from
    https://stackoverflow.com/questions/35490555/python-timeout-decorator
    """

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)
