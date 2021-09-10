"""Translate objects to and from dicts produced/consumed by classify.run()."""
from typing import Dict, Type

# pylint: disable=cyclic-import
from .base import Adapter
from .dicom import DicomAdapter
from .fw import FWAdapter
from .nifti import NiftiFWAdapter

__all__ = ["available_adapters"]

available_adapters: Dict[str, Type[Adapter]] = {
    "base": Adapter,
    "dicom": DicomAdapter,
    "flywheel": FWAdapter,
    "nifti": NiftiFWAdapter,
}
