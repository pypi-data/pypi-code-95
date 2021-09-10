#! /usr/bin/env python
import pkg_resources

__version__ = pkg_resources.get_distribution("pymt_era5").version


from .bmi import Era5

__all__ = [
    "Era5",
]
