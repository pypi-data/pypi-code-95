"""
## Description
---
This command helps you list all notification templates.
Run `caeops notifications list-templates --help` for more help.
## Examples
---
To get notification templates.
The following `notifications list-templates` example displays notification templates.
```
caeops notifications list-templates --medium=email
```
## Output
---
List of all Notification templates
"""

import argparse
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.configurations import read
from caeops.utilities import CentralizedMetricsUrl, generate_auth_headers
from caeops.global_settings import ConfigKeys

import requests
import json


def list_templates(tenant_id, flags):
    medium = flags["medium"]
    url = (
        CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/notifications/templates"
    )
    if medium is not None:
        url += "?medium=" + medium
    else:
        print("Please also enter medium flag")
        return {"data": []}
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def templates_list(flags):

    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if tenant_id == "tenantid not found" or len(tenant_id) == 0:
        print("Tenant id not found. Please login to continue")
        exit(1)

    try:
        response = list_templates(tenant_id, flags)
        for i in response["data"]:

            del i["id"]
            del i["deletedAt"]
            del i["createdAt"]
            del i["updatedAt"]
            del i["tenant"]
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
