"""
## Description
---
This command helps to list logs analyzers.
Run `caeops logs-analyzers list --help` for more help.

## Examples
---
To list details of logs analyzer.

The following `logs-analyzers list` example lists details of logs analyzer.

```
caeops logs-analyzers list
```

## Output
---
Logs analyzer details -> List(structure)

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
Last modified timestamp)

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


def list_all_logs_analyzers(tenant_id):
    """
    List all the logs analyzer services created by the tenant
    :param tenant_id: Id of the tenant
    :return: Response from REST API
    """
    url = KubernetesProvisioningUrl + "/v1/tenants/" + tenant_id + "/logs-analyzers/"
    res = requests.get(
        url=url,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_analyzer_list():
    """
    Runs the list logs analyzers command for logs analyzer
    :return: Response / None
    """
    # validate tenant in session
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    try:
        response = list_all_logs_analyzers(tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("list")
        print(f"{err_message} : {(str(e))}")
        return None
