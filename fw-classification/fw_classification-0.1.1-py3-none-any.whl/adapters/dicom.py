"""Basic dicom adapter."""
import typing as t
import warnings
import zipfile

from dotty_dict import Dotty
from fw_file.dicom import DICOM, DICOMCollection

try:  # pragma: no cover
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from flywheel_gear_toolkit.utils.dicom import get_dicom_header

        HAVE_GTK = True

except (ImportError, ModuleNotFoundError):  # pragma: no cover
    HAVE_GTK = False

from .base import Adapter


class DicomAdapter(Adapter):
    """Adapater for dicom files using fw_file."""

    def preprocess(self) -> t.Dict[str, t.Any]:
        """Extract dicom header."""
        if not HAVE_GTK:
            raise ValueError(
                "Cannot use this adapter without `flywheel-gear-toolkit`. "
                "Either install `flywheel-gear-toolkit` or install the "
                "extra `fw-classification[geartk]`"
            )
        if zipfile.is_zipfile(self.file):
            collection = DICOMCollection.from_zip(self.file, force=True)
            file_ = collection[0]
        else:
            collection = None
            file_ = DICOM(self.file, force=True, track=True)
        i_dict = {
            "file": {
                "info": {"header": {"dicom": get_dicom_header(file_)}},
                "type": "dicom",
            }
        }
        return i_dict

    def postprocess(self, res: bool, out: Dotty) -> t.Any:  # pragma: no cover
        """No post-processing needed, just return updated metadata."""
        return out.to_dict()
