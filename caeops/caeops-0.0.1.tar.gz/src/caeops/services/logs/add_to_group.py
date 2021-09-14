"""
## Description
---
This command helps you add Logs Service to a group.
Run `caeops logs add-to-group --help` for more help.

## Synopsis
---
```
  add-to-group
--name [value]
--group-name [value]
```

## Options
---

--name (string)

> Name of Logs Service

--group-name (string)

> Name of group in which you want to add the Logs Service


## Examples
---
To add Logs Service to a group.

The following `logs add-to-group` example adds labels to a Logs Service.

```
caeops logs add-to-group --name=name --group-name=example
```


## Output
---
Logs Service Details -> (Structure)

- **serviceName** -> (string)  
Name of the Logs Service
- **serviceRegion** -> (string)  
Region of Logs Service
- **serviceEndpoint** -> (string)  
Endpoint of the Elasticsearch Instance
- **serviceType** -> (string)  
Type of the resource, `logs-service` for Logs Service
- **groupName** -> (string)  
Name of the service group to which the Logs Service is added
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
from caeops.utilities import validate_mandatory_fields
from caeops.common.validators import validate_tenant_in_session
from caeops.configurations import read
from caeops.utilities import (
    CentralizedMetricsUrl,
    generate_auth_headers,
)
from caeops.global_settings import ConfigKeys

import requests


def add_to_group(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/logs/"
        + payload["name"]
        + "/service-groups"
    )
    del payload["name"]
    res = requests.post(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_add_to_group(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name", "group-name"],
    )
    try:
        response = add_to_group(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("add-to-group")
        print(f"{err_message} : {(str(e))}")
        return None
