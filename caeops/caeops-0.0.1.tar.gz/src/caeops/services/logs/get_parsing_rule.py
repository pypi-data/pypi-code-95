"""
## Description
---
This command fetches a parsing rule filter for the given logs source

## Synopsis
---
```
  get-parsing-rule
--name [value]
--service-name [value]
```

## Options
---
**--name** (string)

> Name of parsing rule

**--service-name** (string)

> Name of the logs source to create this rule for

## Examples
---
The following `logs get-parsing-rule` example fetches the parsing rule for the given logs source

```
caeops logs get-parsing-rule --name access-pattern --service-name dev-logs
```

## Output
---

Parsing Rule Details -> (Structure)

- **name** -> (string)
Name of the parsing rule created
- **serviceName** -> (string)
Name of the logs source that applies this rule
- **pluginName** -> (string)
Name of the plugin(logstash) used for parsing logs
- **rule** -> (structure)
    - **pattern** -> (string)
    Filter pattern defined for this rule
    - **target** -> (string)
    Name of the target field, that should contain the parsed information

"""

import json

import requests
from caeops.common.api_helper import (
    generate_error_response_text,
    parse_rest_api_response,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.configurations import read
from caeops.global_settings import ConfigKeys
from caeops.utilities import generate_auth_headers, KubernetesProvisioningUrl
from caeops.utilities import validate_mandatory_fields


def _get(payload: dict, tenant_id: str):
    """
    Fetches a parsing rule with the given name for the given log source
    :param payload: Payload to pass to the REST API
    :param tenant_id: Id of the current logged-in tenant
    :return: Response from the REST API
    """
    url = f"{KubernetesProvisioningUrl}/v1/tenants/{tenant_id}/logs/{payload.get('serviceName')}/logstash-rules/{payload.get('name')}"
    res = requests.get(url=url, headers=generate_auth_headers(ConfigKeys.ID_TOKEN))
    # Parse and return the response
    return parse_rest_api_response(res)


def get_parsing_rule(payload):
    """
    Runs the get parsing rules command for logs
    :param payload: Payload from arguments
    :return: Response / None
    """
    # Read tenant id from config.ini and add it to the request if it is not null
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        [
            "service-name",
            "name",
        ],
    )
    try:
        response = _get(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("get")
        print(f"{err_message} : {(str(e))}")
        return None
