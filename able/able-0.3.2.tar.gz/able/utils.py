#    Copyright (c)  2021  Allthenticate
"""
Home to any utility classes and functions in ABle
"""


class DeviceCallbackData:
    """
    Akin to the AdvertisementData class that Bleak implements, this call will be used for the standardizing
    of all callback data between the bless interface and anything that utilizes it.
    """

    def __init__(self, devices_identifier: str, **kwargs):
        """
        Initializes the DeviceCallbackData object
        :param devices_identifier: required param with the unique identifier of the ble device. It could be
        an MAC address (eg. 52:B8:E9:9E:F5:E5), UUID and etc. as long as it's unique.
        :type devices_identifier: `str`
        :param args: Extra arguments
        :type args:
        :param kwargs: Extra arguments
        :type kwargs:
        """
        # Update the identifier in the correct format
        self.identifier = devices_identifier.replace("_", ":")

        # Characteristic uuid in case of subscription/unsubscription
        self.char_uuid = kwargs.get("char_uuid", None)

        # Extra data TODO
        self.device_data = kwargs.get("device_data", {})

    def __str__(self):
        return f"DeviceCallbackData for: {self.identifier}"

    def __repr__(self):
        return str(self)
