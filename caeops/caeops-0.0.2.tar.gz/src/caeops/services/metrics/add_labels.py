"""
## Description
---
This command helps you add labels to a Metrics Service.
Run `caeops metrics add-labels --help` for more help.

## Synopsis
---
```
  add-labels
--name [value]
--labels [value]
```

## Options
---

--name (string)

> Name of Metrics Service

--labels (list)

> List of all the labels that you want to attach


## Examples
---
To add labels to a Metrics Service.

The following `metrics add-labels` example adds labels to a Metrics Service.

```
caeops metrics add-labels --name=name --labels=[{owner=example},{env=dev}]
```


## Output
---
Metrics Service Details -> (Structure)

- **serviceName** -> (string)  
Name of the Metrics Service
- **serviceRegion** -> (string)  
Region of Metrics Service
- **serviceEndpoint** -> (string)  
Endpoint of the Prometheus Instance
- **serviceType** -> (string)  
Type of the resource, `metrics-service` for Metrics Service
- **groupName** -> (string)  
Name of the service group to which the Metrics Service is added
- **labels** -> Structure
    * **key** -> (string)
      Name  of the label

    * **value** -> (string)
      Value of the label

- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""

import json
from caeops.common.api_helper import (
    generate_error_response,
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


def add_labels(payload, tenant_id):
    url = (
        CentralizedMetricsUrl
        + "/v1/tenants/"
        + tenant_id
        + "/metrics/"
        + payload["name"]
        + "/labels"
    )
    res = requests.post(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_add_labels(payload):
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
        response = add_labels(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("add-labels")
        print(f"{err_message} : {(str(e))}")
        return None
