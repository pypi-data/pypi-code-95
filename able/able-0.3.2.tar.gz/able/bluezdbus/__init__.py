"""
Globals defined for the bluezdbus backend
"""

from enum import Enum


class AdvertisementType(Enum):
    """Bluez defined advertising types"""

    BROADCAST = "broadcast"
    PERIPHERAL = "peripheral"


class DBusInterface(Enum):
    """Base class for interface types"""


class BluezServiceInterfaces(DBusInterface, Enum):
    """Bluez defined service interfaces"""

    BLUEZ_ORG = "org.bluez"
    ADAPTER_INTERFACE = "org.bluez.Adapter1"
    ADVERTISEMENT_INTERFACE = "org.bluez.LEAdvertisement1"
    GATT_CHARACTERISTIC_INTERFACE = "org.bluez.GattCharacteristic1"
    GATT_SERVICE_INTERFACE = "org.bluez.GattService1"
    GATT_MANAGER_INTERFACE = "org.bluez.GattManager1"
    ADVERTISING_MANAGER_INTERFACE = "org.bluez.LEAdvertisingManager1"
    DEVICE_INTERFACE = "org.bluez.Device1"


class DbusServiceInterfaces(DBusInterface, Enum):
    """Dbus defined service interfaces"""

    OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
    PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"


def get_service_path(name: str, index: int):
    """Fetches/generates the path of an service"""
    return f"/org/bluez/{name}/service{index}"


def get_advertisement_object_path(name: str, index: int):
    """Fetches the path of an advertisement"""
    return f"/org/bluez/{name}/advertisement{index}"


def get_characteristic_path(service_path: str, index: int):
    """Fetches the path of an characteristic"""
    return f"{service_path}/char{str(index).zfill(4)}"
