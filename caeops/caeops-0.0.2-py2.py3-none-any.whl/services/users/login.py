"""
## Description
---
This command helps you login an account.
Run `caeops users login --help` for more help.

## Synopsis
---
```
  login
--password [value]
[--email [value]]
```

## Options
---
--email (string)

> Registered email-id of the user

--password (string)

> Valid password of the user



## Examples
---
To login a user with CloudAEye.

The following `login` example logs in a user.

```
caeops users login --email=user@example.com --password=enter the password
```


## Output
---
Message -> (string)  

User successfully Logged In  
It will write the user details in a config file (Please do not manually change it. File location is C:\\Users\\username\\\.cloudaeye)

"""

from caeops.utilities import generate_auth_headers
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.utilities import success
from caeops.configurations import write
from caeops.global_settings import ConfigKeys, ResponseAuthTokens

import requests

from caeops.utilities import TenantRegistrationUrl


def login(payload):
    url = TenantRegistrationUrl + "/v1/login"
    res = requests.post(url=url, json=payload or {})
    # Parse and return the response
    return parse_rest_api_response(res)


def get_profile(payload):
    url = TenantRegistrationUrl + "/v1/me"
    headers = {"Authorization": "Bearer " + str(payload)}
    res = requests.get(url=url, headers=headers)
    # # Parse and return the response
    return parse_rest_api_response(res)


def users_login(payload):
    # Check if email exists
    if payload["email"] == "email not found" or len(payload["email"]) == 0:
        print("please enter the email id")
        exit(1)
    else:
        write(ConfigKeys.EMAIL, payload["email"])

    try:
        response = login(payload)
        # if temporary password change is required
        if "requiredPasswordChange" in response:
            newPassword = input("New Password: ")
            payload["newPassword"] = newPassword
            try:
                login(payload)
            except KeyboardInterrupt:
                print("")
                return None
            except Exception as e:
                err_message = generate_error_response_text("login")
                print(f"{err_message} : {(str(e))}")
                exit(1)
            del payload["password"]
            del payload["newPassword"]
            payload["password"] = newPassword
            try:
                response = login(payload)
            except KeyboardInterrupt:
                print("")
                return None
            except Exception as e:
                err_message = generate_error_response_text("login")
                print(f"{err_message} : {(str(e))}")
                exit(1)
        details = get_profile(response[ResponseAuthTokens.ID_TOKEN])
        write(
            ResponseAuthTokens.ACCESS_TOKEN,
            str(response[ResponseAuthTokens.ACCESS_TOKEN]),
        )
        write(ResponseAuthTokens.ID_TOKEN, str(response[ResponseAuthTokens.ID_TOKEN]))
        # Get user details such as userid tenantid
        write(ConfigKeys.TENANT_ID, str(details["tenant"]["key"]))
        write(ConfigKeys.USER_ID, str(details["key"]))
        success("User successfully Logged In")
        return True
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("login")
        print(f"{err_message} : {str(e)}")
        return None
