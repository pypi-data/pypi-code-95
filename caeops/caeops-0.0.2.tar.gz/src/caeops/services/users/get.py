"""
## Description
---
This command helps you get details of a particular tenant user.
Run `caeops users get --help` for more help.

## Synopsis
---
```
  get
 --email [value]
```

## Options
---
--email (string)

> The account email for which you want to get details

## Examples
---
To get user details.

The following `users get` example gets details of a users.
```
caeops users get --email=example@example.com
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
)
from caeops.common.get_user import get_user
from caeops.configurations import read
from caeops.global_settings import ConfigKeys


def users_get(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["email"],
    )
    try:
        response = get_user(tenant_id, payload)
        del response[0]["key"]
        print(json.dumps(response[0], indent=2))
        return response[0]
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
