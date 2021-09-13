"""Provides access to the API endpoints that are not game specific

.. moduleauthor: David "Gahd" Couples <gahdania@gahd.io>
"""
from exceptions import BNetClientError


def user_info(client, locale=None):
    """Returns the user info

    Args:
        locale (str): localization to use

    Returns:
        dict: the json decoded information for the user (user # and battle tag ID)

    Notes:
        this function requires the BattleNet Client to be use OAuth (Authentication Workflow)
    """
    if not client.auth_flow:
        raise BNetClientError("Requires Authorization Workflow")

    url = f"{client.auth_host}/oauth/userinfo"
    return client.api_get(url, locale, None)
