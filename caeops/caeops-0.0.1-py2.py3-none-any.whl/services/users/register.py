"""
## Description
---
This command helps you register an user with CloudAEye.
Run `caeops users register --help` for more help.

## Synopsis
---
```
  register
 --email [value]
 --given-name [value]
 --family-name [value]
 --phone-number [value]
 [--linkedin-url [value]]
 [--picture [value]]
 [--birthdate [value]]
 [--gender [value]]
 [--address [value]]
```

## Options
---
--email (string)

> A valid email-id for account registration

--given-name (string)

> A name for account registration

--family-name (string)

> Family name of the user

--phone-number (number)

> Valid phone number of the user(format -> +[country code][phone number])

--linkedin-url (string)

> LinkedIn url of the user

--picture (string)

> URL of the picture 

--birthdate (date)

> Birthday of the user

--gender (string)

> Gender of the user

--address (string)

> Valid address of the user


## Examples
---
To register a user with CloudAEye.

The following `register` example registers a user with CloudAEye.

```
caeops users register --email=user@example.com --given-name=example --family-name=user-example --phone-number=123456789
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
from caeops.configurations import read
from caeops.global_settings import ConfigKeys
from caeops.utilities import generate_auth_headers

import requests

from caeops.utilities import TenantRegistrationUrl


def tenant_user_register(tenant_id, payload):
    url = TenantRegistrationUrl + "/v1/tenants/" + tenant_id + "/users"
    res = requests.post(
        url=url,
        data=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def users_register(payload):

    # Read tenantid from config.ini and add it to the payload
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = tenant_user_register(tenant_id, payload)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("register")
        print(f"{err_message} : {(str(e))}")
        return None
