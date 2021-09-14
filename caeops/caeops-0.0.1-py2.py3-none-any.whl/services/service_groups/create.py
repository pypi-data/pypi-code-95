"""
## Description
---
This command helps you create a service group.
Run `caeops service-groups create --help` for more help.

## Synopsis
---
```
  create
--group-name [value]
[--description [value]]
```

## Options
---

--group-name (string)

> A group name for creating a new group

--description (string)

> A short description of the purpose of the group


## Examples
---
To create a service group.

The following `service-groups create` example creates a group.

```
caeops service-groups create --group-name=example
```


## Output
---
Service group details -> (structure)  

- **createdAt** -> (number)  
Time at which the user was created
- **groupName** -> (string)  
Name of the service group
- **description** -> (string)
Description of the group

"""

import json
from caeops.utilities import validate_mandatory_fields
from caeops.common.api_helper import (
    generate_error_response,
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import CentralizedMetricsUrl, generate_auth_headers
from caeops.global_settings import ConfigKeys
from caeops.configurations import read

import requests


def create_group(payload, tenant_id):
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/service-groups"
    res = requests.post(
        url=url, json=payload or {}, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def service_groups_create(payload):
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
        response = create_group(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
