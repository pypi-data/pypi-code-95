from typing import Optional
from kenna.error import InvalidRegionError

GLOBAL = "global"
CA = "ca"
EU = "eu"
US = "us"

API_ENDPOINTS_BY_REGION = {
    GLOBAL: 'https://api.kennasecurity.com',
    US: 'https://api.us.kennasecurity.com',
    EU: 'https://api.eu.kennasecurity.com',
    CA: 'https://api.ca.kennasecurity.com',
}

ALL_REGIONS = list(API_ENDPOINTS_BY_REGION.keys())
ALL_ENDPOINTS = list(API_ENDPOINTS_BY_REGION.values())

DEFAULT_REGION = GLOBAL


def get_endpoint(region: Optional[str] = None) -> str:
    return API_ENDPOINTS_BY_REGION[region or DEFAULT_REGION]


def validate_name(region: str) -> str:
    if region not in ALL_REGIONS:
        raise InvalidRegionError("Unsupported region: {} (supported: {})".format(region, ALL_REGIONS))
    return region
