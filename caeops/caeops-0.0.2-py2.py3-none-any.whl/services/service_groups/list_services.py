"""
## Description
---
This command helps you list all the services in a service group.
Run `caeops service-groups list-services --help` for more help.

## Synopsis
---
```
  list-services
--group-name [value]
```

## Options
---

--group-name (string)

> A group name for getting services.


## Examples
---
To list all the services in a service group

The following `service-groups list-services` example lists the services in a service group.

```
caeops service-groups list-services --group-name=example
```


## Output
--- 
Service group details -> List(structure)  

- **serviceName** -> (string)  
Name of the resource
- **serviceEndpoint** -> (string)  
URL of the resource instance
- **serviceType** -> (string)  
Type of the resource
- **groupName** -> (string)  
Name of the service group
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""

import json
from caeops.utilities import validate_mandatory_fields
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import CentralizedMetricsUrl, generate_auth_headers
from caeops.global_settings import ConfigKeys
from caeops.configurations import read

import requests


def list_services(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/service-groups/"
        + payload["groupName"]
        + "/services"
    )
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def service_groups_list_services(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["group-name"],
    )
    try:
        response = list_services(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list-services")
        print(f"{err_message} : {(str(e))}")
        return None
