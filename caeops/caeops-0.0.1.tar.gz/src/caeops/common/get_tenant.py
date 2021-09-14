from caeops.common.api_helper import parse_rest_api_response
from caeops.utilities import generate_auth_headers
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def get_tenant():
    url = TenantRegistrationUrl + "/v1/" + "me"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    if not res.ok:
        raise Exception("Getting failed: " + str(res.text))
    # Parse and return the response
    return parse_rest_api_response(res)
