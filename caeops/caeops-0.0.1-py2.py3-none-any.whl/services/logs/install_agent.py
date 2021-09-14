"""
## Description
---
This command helps you setup an `agent` that collects logs from any source (supported by CloudAEye) running on
a given cloud env  (supported by CloudAEye) and ships them to the provided logs service endpoint

Run `caeops logs install-agent --help` for more help.

## Synopsis
---

```shell
  install-agent
--service-name [value]
--cloud [value]
--source [value]
--app-name [value]
[--kubernetes-cluster-name [value]]
[--kubernetes-enable-system-logs [value]]
[--docker-network [value]]
```

## Options
---

**--service-name** (string)

> Name of the logs service

**--cloud** (string)

> The type of cloud service providers. Supported providers : aws

**--source** (string)

> The type of cloud source. Supported resources : kubernetes | docker

**--app-name** (string)

> A representative name for the current app sending the logs

**--kubernetes-cluster-name** (string)

> Name of the kubernetes cluster where the agent needs to run (for source='kubernetes')

**--kubernetes-enable-system-logs** (bool)

> Determines whether or not to collect system level logs for the cluster (for source='kubernetes')

**--docker-network** (string)

> Specifies the docker network on which the agent needs to run (for source='docker')


## Examples
---

### Example 1

- The following `logs install-agent` example generates commands to install an agent for a `kubernetes` source
  on `aws` cloud

```shell
caeops logs install-agent
        --service-name mylogs --cloud aws --source kubernetes --app-name "Test App"
        --kubernetes-cluster-name test-cluster --kubernetes-enable-system-logs true
```

#### Output
Instructions -> (string)

```shell
Step 1
------
Download the script to run the agent. (This script deploys a helm chart. Skip this step if the script is already downloaded)
    wget -O aws_kubernetes_agent.py https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/scripts/aws_kubernetes_agent.py

Do you want to execute the command ? (y/n)

Step 2
------
If no K8 agent is installed or active, run the below command to install a new K8 agent. (NOTE: If a K8 agent is already running for logs/metrics, skip this step and go to next step)
    python3 aws_kubernetes_agent.py --helm-repo "https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/helm/cae-k8-agent/charts" --enable-logs "yes" --k8-cluster-name "test-cluster" --k8-exclude-logs-from-namespace "cloudaeye" --k8-namespace "cloudaeye" --cloud-env "aws" --logs-destination "http" --destination-http-url "http://endpoint.com" --app-name "Test App" --app-key "TA" --user-key somekey --user-secret somesecret --agent-mode "create"

Do you want to execute the command ? (y/n)

If a K8 agent is already running, run the below command to update the existing K8 agent. (NOTE: Skip this step if a new agent was installed in previous step)
   python3 aws_kubernetes_agent.py --helm-repo "https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/helm/cae-k8-agent/charts" --enable-logs "yes" --k8-cluster-name "test-cluster" --k8-exclude-logs-from-namespace "cloudaeye" --k8-namespace "cloudaeye" --cloud-env "aws" --logs-destination "http" --destination-http-url "http://endpoint.com" --app-name "Test App" --app-key "TA" --user-key somekey --user-secret somesecret --agent-mode "update"
```

---

### Example 2

- The following `logs install-agent` example generates commands to install an agent for a `docker` source on `aws` cloud

```shell
caeops logs install-agent --service-name mylogs --cloud aws --source docker --app-name "Dev App" --docker-network test
```

#### Output

Instructions -> (string)

```shell
Step 1
------
Download the script to run the agent. (This script deploys a docker container. Skip this step if the script is already downloaded)
    wget -O aws_docker_agent.py https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/docker/scripts/aws_docker_agent.py

Do you want to execute the command ? (y/n)

Step 2
------
Run the below command to install the agent
   python3 aws_docker_agent.py --agent-mode create --agent-type logs --docker-network test --cloud-env aws --logs-destination http --destination-http-url http://endpoint.com --app-name "Dev App" --app-key DA --user-key somekey --user-secret somesecret

Do you want to execute the command ? (y/n)

Step 3
------
For Docker Containers: Restart your app containers with an additional argument --log-driver=fluentd to use fluentd as log driver and ship logs to destination. See example below
docker stop my-container
docker rm my-container
docker run --log-driver=fluentd --name my-container nginx --network test


Step 4
------
For Docker Compose: Update your docker-compose.yaml to set logging.driver=fluentd to use fluentd as log driver driver and ship logs to destination. See example below
docker-compose down

      version: "3"
      services:
      nginx:
        image: nginx
        container_name: nginx
        logging:
          driver: fluentd
        networks:
          - web
      networks:
        web:
          external: true
          name: --network test

docker-compose up

```

"""
import os

import requests

from caeops.global_settings import ConfigKeys
from caeops.common.api_helper import (
    parse_rest_api_response,
    generate_error_response_text,
)
from caeops.common.validators import validate_tenant_in_session
from caeops.configurations import read
from caeops.utilities import (
    CentralizedMetricsUrl,
    generate_auth_headers,
    validate_mandatory_fields,
    color_print_command,
    restructure_with_sub_object,
)
import subprocess


def install_agent(payload, tenant_id) -> dict:
    """
    Fetches the instructions to install agent for a given logs source
    :param payload: Payload to be passed to the REST API
    :param tenant_id: Id of the tenant in the current session
    :return: Parsed response from server
    """
    # Construct the Url
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/logs/agent/install"
    # Construct the query params
    query_params = {"cloud": payload["cloud"], "source": payload["source"]}
    # Construct the payload
    if "cloud" in payload:
        del payload["cloud"]
    if "source" in payload:
        del payload["source"]
    # Make a request to the REST API
    res = requests.put(
        url=url,
        json=payload,
        params=query_params,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def logs_install_agent(payload: dict):
    """
    Run the install agent command for logs
    :param payload: Payload from arguments
    :return: Response / None
    """
    # validate tenant in session
    tenant_id = read(ConfigKeys.TENANT_ID)
    if not validate_tenant_in_session(tenant_id):
        exit(1)
    auto_execute = False
    if "autoExecute" in payload:
        auto_execute = True
        del payload["autoExecute"]

    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        [
            "service-name",
            "cloud",
            "app-name",
            "source",
        ],
    )

    # If the cloud source is of type kubernetes => validate for k8 mandatory fields
    if payload.get("source", "") == "kubernetes":
        validate_mandatory_fields(payload, ["kubernetes-cluster-name"])
        payload = restructure_with_sub_object(
            actual_object=payload, sub_object_key="kubernetes"
        )
    elif payload.get("source", "") == "docker":
        validate_mandatory_fields(payload, ["docker-network"])
        payload = restructure_with_sub_object(
            actual_object=payload, sub_object_key="docker"
        )
    try:
        # Fetch agent installation instructions for logs from REST API
        import json

        response = install_agent(payload, tenant_id)
        # Parse through the steps
        all_steps = response.get("steps", {})
        print("\n")
        # For each step
        for step in all_steps.keys():
            # collect all instructions with in the step
            instructions = all_steps[step]
            print(f"Step {step}\n------")
            for cmd in instructions:
                # Fetch detail in the current instruction
                details = cmd.get("details", "").replace("'", '"')
                # If the instruction is a text simply display it and continue
                if cmd.get("type", "") == "text":
                    print(f"{details}")
                # If the instruction is a executable command => check for auto execute flag , if not present ask
                else:
                    color_print_command(f"\t {details}")
                    execute_cmd = ""
                    if auto_execute:
                        # subprocess.run(details.split(" "))
                        if os.system(details) != 0:
                            exit()
                        exit()
                    while not (execute_cmd == "y" or execute_cmd == "n"):
                        execute_cmd = input(
                            "\nDo you want to execute the command ? (y/n)"
                        )
                    if execute_cmd == "y":
                        if os.system(details) != 0:
                            exit()
            print("\n")
        return response
    except Exception as e:
        err_message = generate_error_response_text("install_agent")
        print(f"{err_message} : {str(e)}")
        return None
