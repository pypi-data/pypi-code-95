"""
## Description
---
This command helps you list all the groups that the user is part of.
Run `caeops users list-groups --help` for more help.

## Synopsis
---
```
  list-groups
--email [value]
```

## Options
---
--email (string)

> Email of the user for which you want to list groups.


## Examples
---
To list all the groups that the user is part of.

The following `users list-groups` example list all the groups that the user is part of.
```
caeops users list-groups --email=example@example.com
```

## Output
---
Description of the groups -> List(structure)

- **groupName** -> (string)   
Name of the group
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp
"""

import json
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import validate_mandatory_fields
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.get_user import get_user
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def list_groups_for_users(tenant_id, user_id):
    url = (
        TenantRegistrationUrl
        + "/v1/tenants/"
        + tenant_id
        + "/users/"
        + str(user_id)
        + "/groups"
    )
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def users_list_groups(payload):

    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["email"],
    )
    response_get_user = get_user(tenant_id, payload)
    if len(response_get_user) > 0:
        user_id = response_get_user[0]["key"]
        try:
            response = list_groups_for_users(tenant_id, user_id)
            print(json.dumps(response, indent=2))
            return response
        except KeyboardInterrupt:
            print("")
            return None
        except Exception as e:
            err_message = generate_error_response_text("list-groups")
            print(f"{err_message} : {(str(e))}")
            return None
    else:
        print("User not found")
        return None
