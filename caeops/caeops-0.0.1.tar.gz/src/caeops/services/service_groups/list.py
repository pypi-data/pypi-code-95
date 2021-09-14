"""
## Description
---
This command helps you list all the service groups.
Run `caeops service-groups list --help` for more help.


## Examples
---
To list all the service groups.

The following `service-groups list` example lists service groups.

```
caeops service-groups list
```


## Output
--- 
Service group details -> List(structure)  

- **createdAt** -> (number)  
Time at which the user was created
- **groupName** -> (string)  
Name of the service group
- **description** -> (string)
Description of the group

"""

import json
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


def list_group(tenant_id):
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/service-groups"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def service_groups_list():
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list_group(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
