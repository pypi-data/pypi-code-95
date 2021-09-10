from __future__ import absolute_import

import pkg_resources

from bmi_era5 import BmiEra5 as Era5

Era5.__name__ = "Era5"
Era5.METADATA = pkg_resources.resource_filename(__name__, "data/Era5")

__all__ = [
    "Era5",
]
