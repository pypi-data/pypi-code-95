"""
## Description
---
This command helps to list metrics analyzers.
Run `caeops metrics-analyzers list --help` for more help.

## Examples
---
To list details of metrics analyzer.

The following `metrics-analyzers list` example lists details of metrics analyzer.

```
caeops metrics-analyzers list
```

## Output
---
metrics analyzer details -> List(structure)

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
from caeops.common.api_helper import generate_error_response_text

from caeops.common.api_helper import parse_rest_api_response
from caeops.common.validators import validate_tenant_in_session
from caeops.utilities import generate_auth_headers
from caeops.configurations import read
from caeops.global_settings import ConfigKeys

import requests

from caeops.utilities import KubernetesProvisioningUrl


def list(tenant_id):
    """This function calls the rest API to list metrics analyzer
    Parameters
    --------
    tenant_id : Id of tenant admin
    payload : it conatins details as entered by user

    Raises
    --------
    RuntimeError
        The response from server if the payload was incorrect
    """
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/metrics-analyzers/"
    res = requests.get(
        url=url,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_analyzer_list():
    """This function checks the validity of payload and invokes list function
    Parameters
    --------
    payload : it conatins details as entered by user
    """
    # validate tenant in session
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
