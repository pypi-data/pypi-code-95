"""
## Description
---
This command helps you update an user account with CloudAEye.
Run `caeops users update --help` for more help.

## Synopsis
---
```
    update
--email [value]
[--given-name [value]]
[--family-name [value]]
[--role [value]]
[--linkedin-url [value]]
[--birthdate [value]]
[--gender [value]]
[--phone-number [value]]
[--picture [value]]
```

## Options
---
--email (string)

> Email of the user you want to edit

--given-name (string)

> New name for the account 

--family-name (string)

> New family name for the account

--role (string)

> Role assigned to the user. e.g TenantUser

--linkedin-url (string)

> LinkedIn url of the user

--birthdate (date)

> Birthday of the user

--gender (string)

> Gender of the user

--address (string)

> Valid address of the user

--phone-number (number)

> Valid phone number of the user

--picture (string)

> URL of the picture 


## Examples
---
To update a user with CloudAEye.

The following `users update` example updates a user with CloudAEye.

```
caeops users update --email=example@example.com --given-name=example --family-name=user-example --role=developer --linkedin-url=www.linkedin.com/example --birthdate=dd/mm/yyyy --gender=gender --address=valid address
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
from caeops.utilities import validate_mandatory_fields
from caeops.common.validators import validate_tenant_in_session
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common import get_user
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def tenant_user_update(tenant_id, user_id, payload):
    url = TenantRegistrationUrl + "/v1/tenants/" + tenant_id + "/users/" + str(user_id)
    res = requests.put(
        url=url,
        json=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def users_update(payload):
    # Read userid, tenantid from config.ini and add it to the request if the are not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["email-id"],
    )
    response_get_user = get_user(tenant_id, payload)
    if len(response_get_user["data"]["users"]) > 0:
        user_id = response_get_user["data"]["users"][0]["key"]
        try:
            response = tenant_user_update(tenant_id, user_id, payload)
            print(json.dumps(response, indent=2))
            return response
        except KeyboardInterrupt:
            print("")
            return None
        except Exception as e:
            err_message = generate_error_response_text("update")
            print(f"{err_message} : {(str(e))}")
            return None
    else:
        print("User not found")
        return None
