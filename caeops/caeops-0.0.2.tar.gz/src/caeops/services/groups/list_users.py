"""
## Description
---
This command helps to list all users in a group.
Run `caeops groups list-users --help` for more help.

## Synopsis
---
```
  list-users
--group-name [value]
```

## Options
---

--group-name (string)

> A group name from which you want to list users

## Examples
---
To list users in a group.

The following `groups list-users` example list users in a group.

```
caeops groups list-users --group-name=example
```


## Output
---
User details -> List(structure)

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

import requests

from caeops.utilities import TenantRegistrationUrl


def list_users_in_group(tenant_id, payload):
    url = (
        TenantRegistrationUrl
        + "/v1/tenants/"
        + tenant_id
        + "/groups/"
        + payload["groupName"]
        + "/users"
    )
    res = requests.get(
        url=url, data={}, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def groups_list_users(payload):

    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["group-name"],
    )
    # Read tenantid from config.ini and check if it exista and its length is > 0
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list_users_in_group(tenant_id, payload)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list-users")
        print(f"{err_message} : {(str(e))}")
        return None
