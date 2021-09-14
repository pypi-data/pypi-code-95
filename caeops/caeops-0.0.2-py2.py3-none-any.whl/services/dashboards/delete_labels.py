"""
## Description
---
This command helps you delete labels of a Dashboards Service.
Run `caeops dashboards delete-labels --help` for more help.

## Synopsis
---
```
  delete-labels
--name [value]
--labels [value]
```

## Options
---
--name (string)

> Dashboards Service name

--labels (list)

> List of all the labels that you want to attach


## Examples
---
To delete labels of a Dashboards Service .

The following `dashboards delete-labels` example deletes labels of a Dashboards Service .

```
caeops dashboards delete-labels --name=name --labels=[{owner=example},{env=dev}]
```


## Output
---
Label details -> (Structure)

- **key** -> (string)  
Name  of the field
- **value** -> (string)  
Value of the field

"""

import json
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import validate_mandatory_fields
from caeops.common.labels_format import labels_format
from caeops.configurations import read
from caeops.utilities import (
    KubernetesProvisioningUrl,
    generate_auth_headers,
)
from caeops.global_settings import ConfigKeys

import requests


def delete_labels(payload, tenant_id):
    url = (
        KubernetesProvisioningUrl
        + "/v1/tenants/"
        + tenant_id
        + "/dashboards/"
        + payload["name"]
        + "/labels"
    )
    res = requests.delete(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def dashboards_delete_labels(payload):
    # Read tenantid from config.ini and delete it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name", "labels"],
    )
    # Convert labels into json format
    try:
        new_labels = labels_format(payload["labels"])
        payload["labels"] = new_labels
        response = delete_labels(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("delete-labels")
        print(f"{err_message} : {(str(e))}")
        return None
