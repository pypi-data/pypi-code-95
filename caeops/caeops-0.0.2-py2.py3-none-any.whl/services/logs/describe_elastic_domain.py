"""
## Description
---
This command helps you get details of a Logs Service

## Synopsis
---
```
  get 
--name [value]
```

## Options
---

--name (string)

> The name of Logs Service

## Examples
---

The following `logs get` example gets details of a Logs Service

```
caeops logs get --name=my-test-domain
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

import requests

from caeops.configurations import read
from caeops.utilities import generate_auth_headers, CentralizedMetricsUrl
from caeops.global_settings import ConfigKeys


def get_logs(tenant_id, payload):
    domain_name = payload.get("name", "")
    url = f"{CentralizedMetricsUrl}/v1/tenants/{tenant_id}/logs/{domain_name}"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_get(payload):
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name"],
    )
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)

    try:
        response = get_logs(tenant_id, payload)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
