"""
## Description
---
This command helps to list details of Dashboards Service.
Run `caeops dashboards list --help` for more help.

## Examples
---
To list details of Dashboards Service.

The following `dashboards list` example lists details of Dashboards Service.

```
caeops dashboards list
```

## Output
---
Dashboards Service details -> list(structure)  

- **serviceName** -> (string)  
Name of the Dashboards Service
- **serviceRegion** -> (string)  
Region of Dashboards Service
- **serviceEndpoint** -> (string)  
Endpoint of the Grafana Instance
- **serviceType** -> (string)  
Type of the resource, `dashboards-service` for Dashboards Service
- **labels** -> Structure
    * **key** -> (string)
      Name  of the label

    * **value** -> (string)
      Value of the label

- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""

import json
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def workspace_list(tenant_id):
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/dashboards"
    res = requests.get(
        url=url, json={}, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def dashboards_list():
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)

    try:
        response = workspace_list(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
