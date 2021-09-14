"""
## Description
---
This command helps you update a tenant admin account with CloudAEye.
Run `caeops tenants update --help` for more help.

## Synopsis
---
```
  update
--email [value]
[--given-name [value]]
[--family-name [value]]
[--company [value]]
[--birthdate [value]]
[--address [value]]
[--gender [value]]
[--company-phone [value]]
[--company-logo [value]]
[--company-url [value]]
[--linkedin-url [value]]
[--phone-number [value]]
```
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
To update a tenant with CloudAEye.

The following `tenants update` example updates a user with CloudAEye.

```
caeops tenants update --company-url=company-website --linkedin-url=www.linkedin.com/example --company-phone=company-phone-number --company-logo=url-of-company-logo 
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
from caeops.common.validators import validate_tenant_in_session
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import TenantRegistrationUrl


def update_tenant(tenant_id, payload):
    url = TenantRegistrationUrl + "/v1/tenants/" + tenant_id + "/profile"
    res = requests.put(
        url=url,
        json=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def tenants_update(payload):

    # Read userid, tenantid from config.ini and add it to the request if the are not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)

    try:
        response = update_tenant(tenant_id, payload)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("update")
        print(f"{err_message} : {(str(e))}")
        return None
