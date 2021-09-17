#    Copyright (c)  2021  Allthenticate
"""
This __init__.py handles all the magic imports such that the same
"""

import sys

# Platform specific
if sys.platform == "linux":
    from able.bluezdbus.advertisement import BluezLEAdvertisement as LEAdvertisement
    from able.bluezdbus.application import BluezApplication as ABleApplication
    from able.bluezdbus.characteristic import BluezCharacteristic as ABleCharacteristic
    from able.bluezdbus.characteristic import (
        BlueZCharacteristicFlags as CharacteristicFlags,
    )
    from able.bluezdbus.service import BluezService as ABleService
elif sys.platform == "darwin":
    from able.corebluetooth.advertisement import CBLEAdvertisement as LEAdvertisement
    from able.corebluetooth.application import CBApplication as ABleApplication
    from able.corebluetooth.characteristic import CBCharacteristic as ABleCharacteristic
    from able.corebluetooth.characteristic import (
        CBCharacteristicFlags as CharacteristicFlags,
    )
    from able.corebluetooth.service import ABleCBService as ABleService
else:
    print(f"{sys.platform} is not yet supported on able!")
