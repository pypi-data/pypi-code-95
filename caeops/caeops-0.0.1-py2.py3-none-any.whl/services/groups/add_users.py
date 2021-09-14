"""
## Description
---
This command helps to add an user to a group.
Run `caeops groups add-user --help` for more help.

## Synopsis
---
```
  add-user
--group-name [value]
--email [value]
```

## Options
---

--group-name (string)

> A group name to which you want to add the user 

--email (string)

> Email of the users that you want to add to the group


## Examples
---
To add users to a group.

The following `groups add-users` example add a user to a group.

```
caeops groups add-user --group-name=example --email=example@example.com
```


## Output
---
User details -> (structure)

- **email** -> (string)  
Email address of the user
- **givenName** -> (string)  
Name of the user
- **familyName** -> (string)  
Family name of the user
- **linkedinUrl** -> (string)  
LinkedIn url of the user
- **picture** -> (string)  
Url of the user's picture
- **phoneNumber** -> (number)  
Phone number of the user
- **roles** -> (list)  
Roles assigned to the user
- **gender** -> (list)  
Gender of the user
- **address** -> (list)  
Address of the user
- **birthdate** -> (list)  
Birthdate of the user
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
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys
from caeops.common.get_user import get_user

import requests

from caeops.utilities import TenantRegistrationUrl


def add_user_to_Group(tenant_id, payload, user_id):
    url = (
        TenantRegistrationUrl
        + "/v1/tenants/"
        + tenant_id
        + "/groups/"
        + payload["groupName"]
        + "/users/add"
    )
    # Change the input seperated by commas into an array
    users = []
    users.append(user_id)
    payload["users"] = users
    del payload["groupName"]
    res = requests.post(
        url=url,
        json=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def groups_add_users(payload):
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["group-name", "email"],
    )
    # Read tenantid from config.ini and check if it exists and its length is > 0
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    response_get_user = get_user(tenant_id, payload)
    if len(response_get_user) > 0:
        user_id = response_get_user[0]["key"]
        try:
            response = add_user_to_Group(tenant_id, payload, user_id)
            print(json.dumps(response, indent=2))
            return response
        except KeyboardInterrupt:
            print("")
            return None
        except Exception as e:
            err_message = generate_error_response_text("add-users")
            print(f"{err_message} : {(str(e))}")
            return None

    else:
        print("User not found")
        return None
