"""
## Description
---
This command helps you get a service group.
Run `caeops service-groups get --help` for more help.

## Synopsis
---
```
  get
--group-name [value]
```

## Options
---

--group-name (string)

> Name of the group


## Examples
---
To get a service group.

The following `service-groups get` example gets a group.

```
caeops service-groups get --group-name=example
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


def get_group(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/service-groups/"
        + payload["groupName"]
    )
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def service_groups_get(payload):
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
        response = get_group(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
