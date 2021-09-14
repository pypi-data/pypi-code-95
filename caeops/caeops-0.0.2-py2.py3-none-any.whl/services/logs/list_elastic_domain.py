"""
## Description
---
This command lists all the Logs Service

## Examples
---

The following `logs list` example lists all the Logs Service

```
caeops logs list
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
from caeops.common.validators import validate_tenant_in_session

import requests

from caeops.configurations import read
from caeops.utilities import generate_auth_headers, CentralizedMetricsUrl
from caeops.global_settings import ConfigKeys


def list_logs(tenant_id):
    url = f"{CentralizedMetricsUrl}/v1/tenants/{tenant_id}/logs"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_list():
    # Get list of ES
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list_logs(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
