"""Adapter for Flywheel file objects."""
from __future__ import annotations

import json
import logging
import os
import tempfile
import typing as t

import backoff
from dotty_dict import Dotty

from .. import __version__
from .fw import META_EXCLUDE, FWAdapter
from .utils import FileInput

log = logging.getLogger(__name__)
try:
    from fw_core_client import ClientError, CoreClient, ServerError

    HAVE_CORE = True
except (ModuleNotFoundError, ImportError) as e:  # pragma: no cover
    HAVE_CORE = False
    log.warning("Could not find fw-core-client, skipping Flywheel API calls.")

try:
    from flywheel_gear_toolkit import GearToolkitContext

    HAVE_GTK = True  # pragma: no cover
except (ModuleNotFoundError, ImportError) as e:  # pragma: no cover
    HAVE_GTK = True

if t.TYPE_CHECKING:  # pragma: no cover
    from flywheel_gear_toolkit import GearToolkitContext
    from fw_core_client import ClientError, ServerError


def get_retry_time() -> int:
    """Helper function to return retry time from env."""
    return int(os.getenv("NIFTI_RETRY_TIME", "30"))


@backoff.on_exception(backoff.expo, (ClientError, ServerError), max_time=get_retry_time)
@backoff.on_exception(backoff.expo, ValueError, max_time=get_retry_time)
def get_sidecar(  # pylint: disable=too-many-locals
    fw: CoreClient, file: FileInput
) -> t.Tuple[str, t.Dict[str, t.Any]]:
    """Get hierarchy information."""
    parent_ref = file.hierarchy  # pylint: disable=unused-variable
    file_name = file.location.name
    log.info(f"Attempting to get sidecar for nifti {file_name}")
    candidates = fw.get(f"/{parent_ref.type}s/{parent_ref.id}").get("files", [])
    sidecar = None
    # Loop through files in the acquisition
    for file_ in candidates:
        # Get source code files
        if file_["type"] not in ["source code"]:
            continue
        try:
            # Get file root, continue if file doesn't end with `.json`
            name, _ = file_["name"].split(".json")
            # Split out root name, leaving only extension
            _, extension = file_name.split(name)
        except ValueError:
            continue
        # If extension is a nifti, this is our file.
        if extension in [".nii", ".nii.gz"]:
            sidecar = file_
            log.info("Found sidecar {file_.name}")
            break
    if sidecar is None:
        raise ValueError("Could not find NIfTI sidecar.")

    sidecar_json = {}
    fd, path = tempfile.mkstemp()
    os.close(fd)
    with open(path, "wb") as writer:
        resp = fw.get(f"/files/{sidecar['file_id']}/download", stream=True)
        writer.write(resp.content)
    with open(path, "r", encoding="utf-8") as reader:
        sidecar_json = json.load(reader)
    os.unlink(path)
    return sidecar["name"], sidecar_json


class NiftiFWAdapter(FWAdapter):
    """Special adapter for Flywheel Nifti objects.

    `preprocess`: Pull info from sidecar.
    `postprocess`: Generate .metadata.json for nifti and sidecar.
    """

    def __init__(
        self,
        file: t.Dict[str, t.Any],
        gear_context: GearToolkitContext,
        name: str = "",
        version: str = "",
    ) -> None:
        """Initialize nifti with sidecar empty."""
        super().__init__(file, gear_context, name=name, version=version)
        self.sidecar = ""

    def preprocess(self) -> t.Dict[str, t.Any]:
        """Populate hierarchy values."""
        i_dict = {"file": self.file.object.dict()}
        # Ensure file.info.header exists
        i_dict["file"].setdefault("info", {}).setdefault("header", {})
        if HAVE_CORE and self.fw:
            sidecar, sidecar_dict = get_sidecar(self.fw, self.file)
            i_dict["file"]["info"]["header"].update({"dicom": sidecar_dict})
            self.sidecar = sidecar
        return i_dict

    def postprocess(self, res: bool, out: Dotty) -> bool:
        """Populate sidecar meta."""
        if res:
            out.pop("file.info.header.dicom", None)
            metadata = out.to_dict()
            for key in META_EXCLUDE:
                metadata["file"].pop(key, None)
            self.gtk.update_file_metadata(self.file.location.name, **metadata["file"])
            file_ = metadata.get("file", {})
            self.gtk.update_file_metadata(
                self.sidecar,
                # NOTE: Leaving the following in case we decide to copy over
                #   more than just classification in the future
                **{
                    key: file_.get(key, {})
                    for key in ["classification"]
                    if key in file_
                },
            )
        return res
