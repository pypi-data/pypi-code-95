"""
## Description
---
This command helps you delete labels from a Metrics Service.
Run `caeops metrics delete-labels --help` for more help.

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

> Name of Metrics Service

--labels (list)

> List of the labels that you want to delete


## Examples
---
To delete labels from a Metrics Service.

The following `metrics delete-labels` example deletes labels from Metrics Service.

```
caeops metrics delete-labels --name=name --labels=[{owner=example},{env=dev}]
``


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
from caeops.utilities import validate_mandatory_fields
from caeops.common.validators import validate_tenant_in_session
from caeops.common.labels_format import labels_format
from caeops.configurations import read
from caeops.utilities import (
    CentralizedMetricsUrl,
    generate_auth_headers,
)
from caeops.global_settings import ConfigKeys

import requests


def delete_labels(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/metrics/"
        + payload["name"]
        + "/labels"
    )
    del payload["name"]
    res = requests.delete(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_delete_labels(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name", "labels"],
    )
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
