"""
## Description
---
This command helps you Delete a notification template by name.
Run `caeops notifications delete-template --help` for more help.
## Examples
---
To delete a notification template.
The following `notifications delete-template` example deletes a notification template.
```
caeops notifications delete-template --template-name=sometemplate --medium=email
```
## Output
---
Delete a template
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


def delete_template(tenant_id, flags):
    templateName = flags["templateName"]
    medium = flags["medium"]
    url = (
        CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/notifications/templates/"
    )
    url += templateName
    if medium is not None:
        url += "?medium=" + medium
    res = requests.delete(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def templates_delete(flags):

    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if tenant_id == "tenantid not found" or len(tenant_id) == 0:
        print("Tenant id not found. Please login to continue")
        exit(1)

    try:
        response = delete_template(tenant_id, flags)
        i = response["data"]["deletedRecord"]

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
        err_message = generate_error_response_text("delete")
        print(f"{err_message} : {(str(e))}")
        return None
