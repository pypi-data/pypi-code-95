"""
## Description
---
This command helps to list all groups of the tenant.
Run `caeops groups list --help` for more help.

## Examples
---
To list groups of the tenant.

The following `groups list` example list groups of the tenant.

```
caeops groups list
```


## Output
--- 
User Details -> List(structure)

- **groupName** -> (string)   
Name of the group
- **createdAt** -> (string)  
Date at which the group was created
- **updatedAt** -> (string)  
Date at which the group was last modified

"""
import json
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session

from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def list_groups(tenant_id):
    url = TenantRegistrationUrl + "/v1/tenants/" + tenant_id + "/groups"
    res = requests.get(
        url=url, data={}, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def groups_list():
    # Read tenantid from config.ini and check if it exista and its length is > 0
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list_groups(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
