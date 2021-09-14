"""
## Description
---
This command helps to get logs analyzer.
Run `caeops logs-analyzers get --help` for more help.

## Synopsis
---
```
  get
--name [value]
```

## Options
---
--name (string)

> Name of the analyzer

## Examples
---
To get details of a logs analyzer.

The following `logs-analyzers get` example gets details of a logs analyzer.

```
caeops logs-analyzers get --name=examplename
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

from caeops.common.api_helper import parse_rest_api_response, generate_error_response
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def get_logs_analyzer(payload, tenant_id):
    """
    Fetches logs analyzer with the given name
    :param payload: Payload for the request
    :param tenant_id: Id of the tenant
    :return: Response from REST API
    """
    url = (
        KubernetesProvisioningUrl
        + "/v1/tenants/"
        + tenant_id
        + "/logs-analyzers/"
        + payload["name"]
    )
    res = requests.get(
        url=url,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_analyzer_get(payload):
    """
    Runs the get command for logs analyzer
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
        [
            "name",
        ],
    )
    try:
        response = get_logs_analyzer(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
