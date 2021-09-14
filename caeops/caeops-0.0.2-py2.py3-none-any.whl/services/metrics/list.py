"""
## Description
---
This command helps you list all Metrics Service.
Run `caeops metrics list --help` for more help.


## Examples
---
To get Metrics Service.

The following `metrics list` example displays Metrics Service.

```
caeops metrics list
```


## Output
---
Metrics Service Details -> List(structure)

- **serviceName** -> (string)  
Name of the Metrics Service
- **serviceRegion** -> (string)  
Region of Metrics Service
- **serviceEndpoint** -> (string)  
Endpoint of the Prometheus Instance
- **serviceType** -> (string)  
Type of the resource, `metrics-service` for Metrics Service
- **groupName** -> (string)  
Name of the service group to which the Metrics Service is added
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
    generate_error_response,
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session

from caeops.configurations import read
from caeops.utilities import CentralizedMetricsUrl, generate_auth_headers
from caeops.global_settings import ConfigKeys

import requests


def list_workspace(tenant_id):
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/metrics"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_list():
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)

    try:
        response = list_workspace(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("delete")
        print(f"{err_message} : {(str(e))}")
        return None
