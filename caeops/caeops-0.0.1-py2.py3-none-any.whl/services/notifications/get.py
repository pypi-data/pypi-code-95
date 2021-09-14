"""
## Description
---
This command helps you Get a notification template by name.
Run `caeops notifications get-template --help` for more help.
## Examples
---
To get a notification template.
The following `notifications get-template` example displays a notification template.
```
caeops notifications get-template --template-name=sometemplate --medium=email
```
## Output
---
Get a template
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


def get_template(tenant_id, flags):
    templateName = flags["templateName"]
    medium = flags["medium"]
    url = (
        CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/notifications/templates/"
    )
    if templateName is None:
        print("Please also enter template-name flag")
        return {"data": {}}
    else:
        url += templateName

    if medium is not None:
        url += "?medium=" + medium
    else:
        print("Please also enter medium flag")
        return {"data": {}}
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def templates_get(flags):

    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if tenant_id == "tenantid not found" or len(tenant_id) == 0:
        print("Tenant id not found. Please login to continue")
        exit(1)

    try:
        response = get_template(tenant_id, flags)
        i = response["data"]

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
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
