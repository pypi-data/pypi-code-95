"""Core client configuration."""
# pylint: disable=too-few-public-methods
import re
import typing as t

from fw_http_client import HttpConfig
from pydantic import root_validator, validator

__all__ = ["CoreConfig"]

# regex to match api keys with (to extract the host if it's embedded)
API_KEY_RE = r"(?P<scheme>https?://)?(?P<host>[^:]+)(?P<port>:\d+)?:(?P<key>)"


class CoreConfig(HttpConfig):
    """Flywheel Core API connection and authentication configuration."""

    api_key: t.Optional[str]
    url: t.Optional[str]
    io_proxy_url: t.Optional[str]
    snapshot_url: t.Optional[str]
    xfer_url: t.Optional[str]
    drone_secret: t.Optional[str]
    device_type: t.Optional[str]
    device_label: t.Optional[str]
    auth_proxy: bool = False

    @root_validator
    @classmethod
    def validate_config(cls, values: dict) -> dict:
        """Validate core client configuration or raise AssertionError.

        Authentication options:
         * api_key prefixed with the site URL (from the profile page)
         * url and api_key without the site URL (from the device page)
         * url and drone_secret with device_label (auto-creates device key)
         * auth_proxy set to True, deferring auth to request-time
        """
        api_key, url = values.get("api_key"), values.get("url")
        assert api_key or url, "api_key or url required"
        # strip flywheel api key prefix if present
        if api_key and api_key.lower().startswith("scitran-user "):
            api_key = values["api_key"] = api_key.split(maxsplit=1)[1]
        # extract url from api_key assuming format "[scheme://]host[:port]:key"
        if not url:
            match = re.match(API_KEY_RE, t.cast(str, api_key))
            assert match, f"api_key with url expected (got {api_key!r})"
            scheme = match.group("scheme") or "https://"
            host = match.group("host")
            port = match.group("port") or ""
            url = f"{scheme}{host}{port}"
        # prefix url with https:// if only a domain/host is passed
        if not url.startswith("http"):
            url = f"https://{url}"
        # strip url /api path suffix if present to accommodate other apis
        url = values["baseurl"] = re.sub(r"(/api)?/?$", "", url)
        # require auth (unless it's deferred via auth_proxy)
        drone_secret = values.get("drone_secret")
        if not values.get("auth_proxy"):
            assert api_key or drone_secret, "api_key or drone_secret required"
        # default device_type to client_name and require device_label
        if not api_key and drone_secret:
            if not values.get("device_type"):
                values["device_type"] = values.get("client_name")
            assert values.get("device_label"), "device_label required"
        headers = values.setdefault("headers", {})
        headers.setdefault("X-Accept-Feature", "Safe-Redirect")
        return values

    @validator("io_proxy_url", "snapshot_url", "xfer_url")
    @classmethod
    def validate_urls(cls, val: str) -> str:
        """Strip trailing slash from urls."""
        return val.rstrip("/") if val else val
