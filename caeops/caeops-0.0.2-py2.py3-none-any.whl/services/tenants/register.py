"""
## Description
---
This command helps you register a tenant admin with CloudAEye.
Run `caeops tenants register --help` for more help.

## Synopsis
---
```
  register
--email [value]
--given-name [value]
--family-name [value]
--company [value]
[--birthdate [value]]
[--address [value]]
[--gender [value]]
[--company-phone [value]]
[--company-logo [value]]
[--company-url [value]]
[--linkedin-url [value]]
[--phone-number [value]]
```

## Options
---
--email (string)

> A valid email-id for account registration

--given-name (string)

> Name of the tenant admin

--family-name (string)

> Family name of the tenant admin

--company (string)

> Name of tenant admin's comapny

--birthdate (string)

> Birthdate of the tenant

--gender (string)

> Gender of the tenant

--address (string)

> Address of the company

--comapny-phone (string)

> Phone number of tenant admin's company

--company-logo (string)

> Logo of tenant admin's company

--company-url (string)

> Url of tenant admin's company

--linkedin-url (string)

> LinkedIn url of the tenant admin

--phone-number (string)

> Phone number of the tenant admin 

## Examples
---
To register a tenant admin with CloudAEye.
The following `tenants register` example registers a tenant admin with CloudAEye.
```
caeops tenants register --email=user@example.com --given-name=user-name --family-name=user-family name --company=company-name --company-phone=company-phone-number --company-logo=url-of-company-logo --company-url=company-website --linkedin-url=linkedin-url-of-tenant--phone-number=tenant-phone-number
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
- **company** -> (list)  
Name of the company
- **companyUrl** -> (list)  
Website of the company
- **companyPhone** -> (list)  
Phone number of the company
- **companyLogo** -> (list)  
URL of the company's logo
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""
import json

from caeops.global_settings import ConfigKeys
from caeops.configurations import write

import requests

from caeops.utilities import TenantRegistrationUrl, success
from caeops.utilities import validate_mandatory_fields


def signup(payload):
    url = TenantRegistrationUrl + "/v1/register"
    res = requests.post(url=url, json=payload or {})
    if not res.ok:
        raise Exception("Signup failed : " + str(res.text))
    res_json = res.json()
    return res_json


def tenants_register(payload: dict):
    try:
        # Validate for mandatory fields
        validate_mandatory_fields(
            payload,
            ["email", "given-name", "family-name", "company"],
        )
        response = signup(payload)
        if response.get("success", False) is True:
            success("Tenant registration successful")
            # Write the user details to the config.ini file
            write(ConfigKeys.EMAIL, payload["email"])
            write(ConfigKeys.TENANT_ID, str(response["tenant"]["key"]))
            write(ConfigKeys.USER_ID, str(response["user"]["key"]))
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(e)
