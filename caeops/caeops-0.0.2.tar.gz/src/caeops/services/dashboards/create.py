"""
## Description
---
This command helps to create a Dashboards Service.
Run `caeops dashboards create --help` for more help.

## Synopsis
---
```
  create
--name [value]
--data-source [value]
[--labels [value]]
```

## Options
---
--name (string)

> Name of Dashboards Service

--labels (list)

> List of all the labels that you want to attach

--data-source (string)

> Name of service for which you want to create Dashboards Service

## Examples
---
To create a Dashboards Service.

The following `dashboards create` example creates a Dashboards Service.

```
caeops dashboards create --name=name --labels=[{owner=example},{env=dev}] --data-source=Dashboards-Service-Name
```


## Output
---
Dashboards Service details -> (structure)  

- **serviceName** -> (string)  
Name of the Dashboards Service
- **serviceRegion** -> (string)  
Region of Dashboards Service
- **serviceEndpoint** -> (string)  
Endpoint of the Grafana Instance
- **serviceType** -> (string)  
Type of the resource, `dashboards-service` for Dashboards Service
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
from caeops.common.labels_format import labels_format
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import validate_mandatory_fields
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def workspace_create(payload, tenant_id):
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/dashboards"
    res = requests.post(
        url=url,
        json=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def provisioning_create(tenant_id):
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/provisioning"
    res = requests.post(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def dashboards_create(payload):
    # Read tenantid from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)

    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name", "data-source"],
    )
    if "labels" in payload and payload["labels"] is not None:
        # Convert labels into json format
        new_labels = labels_format(payload["labels"])
        labels = json.loads(new_labels)
        payload["labels"] = labels
    try:
        provisioning_create(tenant_id)
    except Exception:
        pass

    try:
        response = workspace_create(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
