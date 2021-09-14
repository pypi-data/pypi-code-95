"""
## Description
---
This command helps you remove Metrics Service from a group.
Run `caeops metrics remove-from-group --help` for more help.

## Synopsis
---
```
  remove-to-group
--name [value]
--group-name [value]
```

## Options
---

--name (string)

> Name of Metrics Service

--group-name (string)

> Name of group from which you want to remove the Metrics Service


## Examples
---
To remove Metrics Service from a group.

The following `metrics remove-from-group` example removes Metrics Service from the group.

```
caeops metrics remove-from-group --name=name --group-name=example
```


## Output
---
Metrics Service Details -> (Structure)

- **serviceName** -> (string)  
Name of the Metrics Service
- **serviceRegion** -> (string)  
Region of Metrics Service
- **serviceEndpoint** -> (string)  
Endpoint of the Prometheus Instance
- **serviceType** -> (string)  
Type of the resource, `metrics-service` for Metrics Service
- **groupName** -> (string)  
Name of the service group (Here it will be - "")
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


def remove_from_group(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/metrics/"
        + payload["name"]
        + "/service-groups/"
        + payload["groupName"]
    )
    res = requests.delete(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_remove_from_group(payload):
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
        response = remove_from_group(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("remove-from-group")
        print(f"{err_message} : {(str(e))}")
        return None
