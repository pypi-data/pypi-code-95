"""
## Description
---
This command deletes the given Logs Service

## Synopsis
---
```
  delete 
--name [value]
```

## Options
---
--name (string)

> Name of Logs Service that you want to delete

## Examples
---
The following `logs delete` example deletes the given Logs Service

```
caeops logs delete --name=name
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
- **labels** -> List (structure)
key -> (string)
Name  of the field
value -> (string)
Value of the field
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""

import json
from caeops.utilities import validate_mandatory_fields
from caeops.common.validators import validate_tenant_in_session
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.configurations import read
from caeops.utilities import generate_auth_headers, CentralizedMetricsUrl
from caeops.global_settings import ConfigKeys
import requests


def workspace_delete(payload, tenant_id):
    url = (
        CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/logs/" + payload["name"]
    )
    res = requests.delete(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_delete(payload):
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
        response = workspace_delete(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("delete")
        print(f"{err_message} : {(str(e))}")
        return None
