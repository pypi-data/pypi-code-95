"""
## Description
---
This command helps to get details of a Dashboards Service.
Run `caeops dashboards get --help` for more help.

## Synopsis
---
```
  get
--name [value]
```

## Options
---
--name (string)

> Name of Dashboards Service you want to details

## Examples
---
To get details of a Dashboards Service.

The following `dashboards get` example get details of a Dashboards Service.

```
caeops dashboards get --name=example
```


## Output
---
Dashboards Service details -> (structure)  

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
from caeops.utilities import validate_mandatory_fields
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def get_dashboards(tenant_id, payload):
    url = (
        KubernetesProvisioningUrl
        + "/v1/tenants/"
        + tenant_id
        + "/dashboards/"
        + payload["name"]
    )
    res = requests.get(
        url=url, json={}, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def dashboards_get(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name"],
    )
    try:
        response = get_dashboards(tenant_id, payload)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
