from battlenet_client.exceptions import BNetClientError


def get_user_info(client, locale=None):
    """Returns the user info

    Args:
        locale (str): localization to use

    Returns:
        dict: the json decoded information for the user (user # and battle tag ID)
    """
    if not client.auth_flow:
        raise BNetClientError("Requires Authorization Workflow")

    url = f"{client.auth_host}/oauth/userinfo"
    return client.post(url, locale, None)
