"""
## Description
---
This command helps to get metrics analyzer.
Run `caeops metrics-analyzers get --help` for more help.

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
To get details of a metrics analyzer.

The following `metrics-analyzers get` example gets details of a metrics analyzer.

```
caeops metrics-analyzers get --name=examplename
```


## Output
---
metrics analyzer details -> (structure)

- **serviceName** -> (string)  
Name of the metrics analyzer
- **serviceType** -> (string)  
Type of the resource (e.g metrics-analyzer)
- **groupName** -> (string)  
Name of the service group to which the Metrics analyzer is added
- **dataSources** -> (structure)  
List of the data sources and their type(e.g {"metrics":"example"})
- **createdAt** -> (long)  
Creation timestamp
- **updatedAt** -> (long)  
Last modified timestamp

"""

import json
from caeops.utilities import validate_mandatory_fields
from caeops.common.api_helper import generate_error_response_text

from caeops.common.api_helper import parse_rest_api_response
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def get(payload, tenant_id):
    """This function calls the rest API to get a metrics analyzer
    Parameters
    --------
    tenant_id : Id of tenant admin
    payload : it conatins details as entered by user

    Raises
    --------
    RuntimeError
        The response from server if the payload was incorrect
    """
    url = (
        KubernetesProvisioningUrl
        + "/v1/tenants/"
        + tenant_id
        + "/metrics-analyzers/"
        + payload["name"]
    )
    res = requests.get(
        url=url,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_analyzer_get(payload):
    """This function checks the validity of payload and invokes get function
    Parameters
    --------
    payload : it conatins details as entered by user
    """
    # validate tenant in session
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        ["name"],
    )
    try:
        response = get(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
