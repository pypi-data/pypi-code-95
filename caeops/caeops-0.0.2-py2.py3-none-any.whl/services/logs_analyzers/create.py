"""
## Description
---
This command helps to create a logs analyzers service for the given data sources.
Run `caeops logs-analyzers create --help` for more help.

## Synopsis
---
```
  create
--name [value]
--data-sources [value]
```

## Options
---
--name (string)

> Name of the analyzer

--data-sources (string)

> Name of resource for which you want to deploy logs analyzer

## Examples
---
To deploy logs analyzer.

The following `logs-analyzers create` example deploys logs analyzer.

```
caeops logs-analyzers create --name=test-analyzer --data-sources=[{logs=some-logs-service}]
```


## Output
---
Logs analyzer details -> (structure)

- **serviceName** -> (string)  
Name of the logs analyzer
- **serviceType** -> (string)  
Type of the service (e.g logs-analyzer, metrics-analyzer)
- **groupName** -> (string)  
Name of the service group to which the logs-analyzer is added
- **dataSources** -> (structure)  
List of the data sources and their type(e.g {"logs":"some-logs-service"})
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp
"""

import json
from caeops.common.api_helper import generate_error_response_text
from caeops.utilities import validate_mandatory_fields

from caeops.common.api_helper import parse_rest_api_response
from caeops.common.labels_format import labels_format
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def create_logs_analyzer(payload, tenant_id):
    """
    Creates a logs analyzer service for the given data source
    :param payload: Payload for the request
    :param tenant_id: Id of the tenant
    :return: Response from REST API
    """
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/logs-analyzers"
    res = requests.post(
        url=url,
        json=payload or {},
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_analyzer_create(payload):
    """
    Run the create logs analyzer command for logs analyzer
    :param payload: Payload from arguments
    :return: Response / None
    """
    # validate tenant in session
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name", "data-sources"],
    )
    try:
        # Convert data-source into json format
        new_data_source = labels_format(payload["dataSources"])
        payload["dataSources"] = new_data_source
        response = create_logs_analyzer(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
