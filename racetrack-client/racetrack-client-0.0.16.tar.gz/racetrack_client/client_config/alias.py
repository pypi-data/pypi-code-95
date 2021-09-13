from typing import Optional

from racetrack_client.client_config.client_config import ClientConfig


def resolve_lifecycle_url(client_config: ClientConfig, lifecycle_name: Optional[str]) -> str:
    """
    Get full URL of Lifecycle based on given short name.
    If aliased name is found, resolve it to full URL it's pointing to.
    If the name was not provided, return default URL.
    """
    if lifecycle_name is None:
        return client_config.lifecycle_url
    if lifecycle_name not in client_config.lifecycle_url_aliases:
        return lifecycle_name
    return client_config.lifecycle_url_aliases[lifecycle_name]
