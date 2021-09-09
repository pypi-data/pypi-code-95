"""Core client."""
import copy
import json
import os
import re
import typing as t

from fw_http_client import HttpClient, errors
from fw_utils import AttrDict
from memoization import cached
from packaging import version

from .config import CoreConfig

__all__ = ["CoreClient"]

# cache time to live (duration to cache /api/config and /api/version response)
CACHE_TTL = 3600  # 1 hour
# global cache of drone keys (device api keys acquired via drone secret)
DRONE_DEVICE_KEYS = {}


class CoreClient(HttpClient):
    """Flywheel Core HTTP API Client."""

    def __init__(self, config: t.Optional[CoreConfig] = None, **kwargs) -> None:
        """Initialize Core client from the config."""
        config = config or CoreConfig(**kwargs)
        super().__init__(config)
        self.apis = {
            "/io-proxy": config.io_proxy_url,
            "/snapshot": config.snapshot_url,
            "/xfer": config.xfer_url,
        }
        if not config.api_key and config.drone_secret:
            config.api_key = self._get_device_key(config)
        if config.api_key:
            self.headers["Authorization"] = f"scitran-user {config.api_key}"

    def _get_device_key(self, config: CoreConfig) -> str:
        """Return device API key for the given drone_secret (cached)."""
        drone = (config.baseurl, config.device_type, config.device_label)
        if drone not in DRONE_DEVICE_KEYS:
            headers = {
                "X-Scitran-Auth": config.drone_secret,
                "X-Scitran-Method": config.device_type,
                "X-Scitran-Name": config.device_label,
            }
            device = self.get("/devices/self", headers=headers)
            DRONE_DEVICE_KEYS[drone] = device.key
        return DRONE_DEVICE_KEYS[drone]

    # pylint: disable=arguments-differ
    def request(self, method: str, url: str, **kwargs):  # type: ignore
        """Send request and return loaded JSON response."""
        if not url.startswith("http"):
            prefix = re.sub(r"^(/[^/]+)?.*$", r"\1", url)
            if prefix in self.apis:
                # route relative urls prefixed for known apis
                url = f"{self.apis[prefix] or ''}{url}"
            elif prefix != "/api":
                # assume core (/api) by default
                url = f"/api{url}"
        return super().request(method, url, **kwargs)

    @property
    def api_config(self) -> AttrDict:
        """Return Core's configuration."""
        return self.get_api_config()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_api_config(self) -> AttrDict:
        """Return Core's configuration (cached)."""
        return self.get("/config")

    @property
    def api_version(self) -> t.Optional[str]:
        """Return Core's release version."""
        return self.get_api_version()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_api_version(self) -> t.Optional[str]:
        """Return Core's release version (cached)."""
        return self.get("/version").get("release")

    @property
    def auth_status(self) -> AttrDict:
        """Return the client's auth status."""
        return self.get_auth_status()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_auth_status(self) -> AttrDict:
        """Return the client's auth status (cached)."""
        status = self.get("/auth/status")
        if status.is_device:
            status["info"] = self.get(f"/devices/{status.origin.id}")
        else:
            status["info"] = self.get("/users/self")
        return status

    def check_feature(self, feature: str) -> bool:
        """Return True if Core has the given feature and it's enabled."""
        return bool(self.api_config.features.get(feature))  # type: ignore

    def check_version(self, min_ver: str) -> bool:
        """Return True if Core's version is greater or equal to 'min_ver'."""
        if not self.api_version:
            # assume latest on dev deployments without a version
            return True
        return version.parse(self.api_version) >= version.parse(min_ver)  # type: ignore

    def upload(
        self,
        filepath: str,
        metadata: dict,
        method: str = "label",
        fill: bool = False,
    ) -> AttrDict:
        """Upload a file using the label or reaper /upload endpoint."""
        assert method in ("label", "reaper"), f"Invalid upload method {method!r}"
        endpoint = f"/upload/{method}"
        filename, metadata = get_upload_info(filepath, metadata, method, fill)
        with open(filepath, "rb") as file:
            signed_url = self.api_config.get("signed_url")  # type: ignore
            if signed_url:
                payload = {"filenames": [filename], "metadata": metadata}
                upload = self.post(endpoint, params={"ticket": ""}, json=payload)
                headers = {"Authorization": None, **upload.get("headers", {})}
                self.put(upload.urls[filename], headers=headers, data=file)
                response = self.post(endpoint, params={"ticket": upload.ticket})
            else:
                meta = json.dumps(metadata)
                response = self.post(endpoint, files={filename: file, "metadata": meta})
        return response

    def store_file(
        self, project_id: str, file: t.BinaryIO, origin: t.Optional[dict] = None
    ) -> str:
        """Store a single file using the /storage/files endpoint (device only)."""
        assert self.auth_status.is_device, "Device authentication required"
        endpoint = "/storage/files"
        origin = origin or self.auth_status.origin
        params = {
            "project_id": project_id,
            "origin_type": origin["type"],
            "origin_id": origin["id"],
            "signed_url": True,
        }
        response = self.post(endpoint, params=params, raw=True)
        if response.ok:
            response = response.json()
            upload_url = response["upload_url"]
            headers = {"Authorization": None, **response.get("upload_headers", {})}
            try:
                self.put(upload_url, headers=headers, data=file)
            except errors.RequestException:
                url = f"{endpoint}/{response['storage_file_id']}"
                self.delete(url, params={"ignore_storage_errors": True})
                raise
        elif response.status_code == 409:
            del params["signed_url"]
            response = self.post(endpoint, params=params, files={"file": file})
        else:
            response.raise_for_status()
        return response["storage_file_id"]


def get_upload_info(
    filepath: str, meta: dict, method: str, fill: bool
) -> t.Tuple[str, dict]:
    """Return (filename, meta) tuple for given upload parameters.

    Core expects label- and reaper uploads as file forms with two files:
      * filename: with the actual file contents
      * metadata: json describing hierarchy placement and additional meta

    Core requires that the metadata has:
      * group._id set to a string ("" allowed)
      * project.label set to a string ("" allowed)
      * subject - if present - embedded under the session
      * uids in case of reaper uploads:
        * session.uid set to a string ("" allowed)
        * acquisition.uid set to a string if the acquisition is present ("" allowed)
      * the filename referenced on some hierarchy level (project or below)

    This function helps getting a correct (filename, metadata) pair where the
    filename is set appropriately if it was present in the metadata, or defaults
    to using the file's basename while making sure it is referenced in the meta.
    The subject - if present - is automatically embedded into the session.

    If fill=True then group._id and project.label, session.uid and acquisition.uid
    are auto-populated with empty strings as necessary to avoid rejected uploads.
    """
    meta = copy.deepcopy(meta)
    # populate group._id and project.label if not set
    if fill:
        if not meta.setdefault("group", {}).get("_id"):
            meta["group"]["_id"] = ""
        if not meta.setdefault("project", {}).get("label"):
            meta["project"]["label"] = ""
    # try to get filename from the meta (going bottom up, looking for files)
    filename = meta.get("file", {}).get("name")
    for level in ("acquisition", "session", "subject", "project"):
        if not meta.get(level):
            continue
        cont = meta[level]
        if filename:
            # using fw-meta file info
            cont["files"] = [meta.pop("file")]
            break
        if cont.get("files"):
            filename = cont["files"][0].get("name")
            break
    # use basename by default and set it in the meta at acquisition level
    if not filename:
        filename = os.path.basename(filepath)
        files = meta.setdefault("acquisition", {}).setdefault("files", [{}])
        files[0]["name"] = filename
    # embed subject meta under session
    if "subject" in meta:
        meta.setdefault("session", {})["subject"] = meta.pop("subject")
    # populate session.uid and acquisition.uid on reaper uploads
    if fill and method == "reaper":
        meta.setdefault("session", {}).setdefault("uid", "")
        if "acquisition" in meta:  # acquisition may be omitted
            meta.setdefault("acquisition", {}).setdefault("uid", "")
    return filename, meta
