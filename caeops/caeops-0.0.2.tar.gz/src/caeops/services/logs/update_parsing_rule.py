"""
## Description
---
This command updates a parsing rule filter for the given logs source

## Synopsis
---
```
  update-parsing-rule
--name [value]
--service-name [value]
--filter [value]
```

## Options
---
**--name** (string)

> Name of parsing rule

**--service-name** (string)

> Name of the logs source to create this rule for

**--filter** (string)

> The format of parsing to be applied by the rule to extract relevant information from the log message

## Examples
---
The following `logs update-parsing-rule` example updates the parsing rule

```
caeops logs update-parsing-rule --name access-pattern --service-name dev-logs \

    --filter '{\"pattern\": \"(?<ip>\\d{1,3}.\\d{1,3}.\\d{1,3}.\\d{1,3}) - - \\[(?<date>\\d{2}\\\/\\w{3}\\\/\\d{4}:\\d{2}:\\d{2}:\\d{2} \\+\\d{4})\\] \\\"(?<method>\\b\\w+\\b) \\\/(?<service>\\b\\w+\\b?) (?<http>.*?)\\\" (?<code>\\d{3}) (?<bytes>\\d{3}) \"-\" \\\"(?<path>.*?)\\\" (?<count>\\d{3}) (?<message>.*)\",\"target\": \"parsed_log\"}'


```

## Output
---
Updated parsing Rule Details -> (Structure)

- **name** -> (string)
Name of the parsing rule created
- **serviceName** -> (string)
Name of the logs source that applies this rule
- **pluginName** -> (string)
Name of the plugin(logstash) used for parsing logs
- **rule** -> (structure)
    - **pattern** -> (string)
    Filter pattern updated for this rule
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


def _update(payload: dict, tenant_id: str):
    """
    Updates a parsing rule for the given log source
    :param payload: Payload to pass to the REST API
    :param tenant_id: Id of the current logged-in tenant
    :return: Response from the REST API
    """
    url = f"{KubernetesProvisioningUrl}/v1/tenants/{tenant_id}/logs/{payload.get('serviceName')}/logstash-rules/{payload.get('name')}"
    payload.pop("name")
    payload.pop("serviceName")
    if "filter" in payload:
        payload["rule"] = json.loads(payload["filter"])
        payload.pop("filter")
    res = requests.put(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def update_parsing_rule(payload):
    """
    Runs the update parsing rule command for logs
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
        ["name", "service-name", "filter"],
    )
    try:
        response = _update(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
