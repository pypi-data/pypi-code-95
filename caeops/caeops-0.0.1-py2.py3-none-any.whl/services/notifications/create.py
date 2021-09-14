"""
## Description
---
This command helps you Create a notification template.
Run `caeops notifications create-template --help` for more help.
## Examples
---
To create a notification template.
The following `notifications create-template` example creates a notification template.
```
caeops notifications create-template --template-name=sometemplate --medium=email --template-file=template.json
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


def create_template(tenant_id, flags):
    try:
        templateFile = flags["templateFile"]
        f = open(
            templateFile,
        )
        payload = json.load(f)
    except Exception as e:
        return e
    url = (
        CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/notifications/templates"
    )
    res = requests.post(
        url=url,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
        json=payload or {},
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def templates_create(flags):

    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if tenant_id == "tenantid not found" or len(tenant_id) == 0:
        print("Tenant id not found. Please login to continue")
        exit(1)

    try:
        response = create_template(tenant_id, flags)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
