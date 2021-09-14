from caeops.common.api_helper import parse_rest_api_response
from caeops.utilities import generate_auth_headers
from caeops.global_settings import ConfigKeys
import urllib

import requests

from caeops.utilities import TenantRegistrationUrl


def get_user(tenant_id, payload):
    email = urllib.parse.quote_plus(payload["email"])
    url = (
        TenantRegistrationUrl
        + "/v1/tenants/"
        + tenant_id
        + "/users/find?email="
        + email
    )
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)
