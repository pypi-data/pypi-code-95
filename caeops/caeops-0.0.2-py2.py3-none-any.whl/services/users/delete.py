"""
## Description
---
This command helps you delete an user with CloudAEye.
Run `caeops users delete --help` for more help.

## Synopsis
---
```
  delete
--email [value]
```

## Options
---
--email (string)

> Email of the account you want to delete


## Examples
---
To delete a user account.

The following `users delete` example deletes an user.

```
caeops users delete --email=example@example.com
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
from caeops.common.validators import validate_tenant_in_session
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.utilities import validate_mandatory_fields
from caeops.common.get_user import get_user
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def tenant_user_delete(tenant_id, user_id):
    url = TenantRegistrationUrl + "/v1/tenants/" + tenant_id + "/users/" + str(user_id)
    res = requests.delete(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def users_delete(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["email"],
    )
    # Get user id from email
    response_get_user = get_user(tenant_id, payload)
    if len(response_get_user) > 0:
        user_id = response_get_user[0]["key"]
        try:
            response = tenant_user_delete(tenant_id, user_id)
            print(json.dumps(response, indent=2))
            return response
        except KeyboardInterrupt:
            print("")
            return None
        except Exception as e:
            err_message = generate_error_response_text("delete")
            print(f"{err_message} : {(str(e))}")
            return None
    else:
        print("User not found")
        return None
