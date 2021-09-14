"""

## Description
---
This command creates a parsing rule filter for the given logs source

## Synopsis
---
```
  create-parsing-rule
--name [value]
--service-name [value]
--plugin-name [value]
--filter [value]
```

## Options
---
**--name** (string)

> Name of parsing rule

**--service-name** (string)

> Name of the logs source to create this rule for

**--plugin-name** (string)

> Name of the plugin (logstash plugin) to use for parsing log message. Supported values : ``grok``

**--filter** (string)

> The format of parsing to be applied by the rule to extract relevant information from the log message

## Examples
---
The following `logs create-parsing-rule` example creates a parsing rule

```
caeops logs create-parsing-rule \

    --name access-pattern --service-name dev-logs --plugin-name grok \

    --filter '{\"pattern\": \"(?<date>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{3})  (?<method>\\b\\w+\\b) \\[(?<service>.*?)\\] (?<count>[0-9]+) --- \\[(?<hook>.*?)\\] (?<action>.*) : (?<log_message>.*)\",\"target\": \"parsed_data\"}'
```

``--filter :``

  * The ``pattern`` can take any inbuilt or custom pattern supported by the logstash's [Grok filter plugin](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html).
    See the complete list of [inbuilt patterns](https://github.com/logstash-plugins/logstash-patterns-core).

  * The ``target`` determines the meta-data field name that should contain the parsed log object

In the above example for the given ``pattern``, if the **log** message looks like below
```
2021-08-10 12:08:50.384  INFO [api-gateway,,,] 1 --- [extShutdownHook] o.s.b.w.embedded.netty.GracefulShutdown  : Commencing graceful shutdown. Waiting for active requests to complete
```

then the **parsed log message** structure would be
```
{
    'date': '2021-08-10 12:08:50.384',
    'method': 'INFO',
    'service': 'api-gateway,,,'
    'count': 1
    'hook': 'extShutdownHook'
    'action': 'o.s.b.w.embedded.netty.GracefulShutdown',
    'log_message': 'Commencing graceful shutdown. Waiting for active requests to complete'
}
```

> Logstash's Grok filter uses [`Oniguruma`](https://github.com/kkos/oniguruma/blob/master/doc/RE) regex library.
In case you want to build custom regex like in the above example, use the [rubular](https://rubular.com/) to create and validate your regex patterns.


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


def _create(payload: dict, tenant_id: str):
    """
    Creates a parsing rule for the given log source
    :param payload: Payload to pass to the REST API
    :param tenant_id: Id of the current logged-in tenant
    :return: Response from the REST API
    """
    url = f"{KubernetesProvisioningUrl}/v1/tenants/{tenant_id}/logs/{payload.get('serviceName')}/logstash-rules"
    payload.pop("serviceName")
    if "filter" in payload:
        payload["rule"] = json.loads(payload["filter"])
        payload.pop("filter")
    res = requests.post(
        url=url, json=payload, headers=generate_auth_headers(ConfigKeys.ID_TOKEN)
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def create_parsing_rule(payload):
    """
    Runs the create parsing rule command for logs
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
        ["name", "service-name", "plugin-name", "filter"],
    )
    try:
        response = _create(payload, tenant_id)
        print(json.dumps(response, indent=2))
        return response
    except KeyboardInterrupt:
        print("")
        return None
    except Exception as e:
        err_message = generate_error_response_text("create")
        print(f"{err_message} : {(str(e))}")
        return None
