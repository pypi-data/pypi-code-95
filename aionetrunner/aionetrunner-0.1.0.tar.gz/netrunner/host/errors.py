from ipaddress import AddressValueError


class InvalidIPAddress(AddressValueError):
    pass


class InvalidPlatform(ValueError):
    pass
