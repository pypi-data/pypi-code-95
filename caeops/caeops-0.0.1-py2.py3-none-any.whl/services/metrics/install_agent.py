"""
## Description
---
This command helps you setup an `agent` that collects metrics from any source (supported by CloudAEye) running on
a given cloud env  (supported by CloudAEye) and ships them to the provided metrics service endpoint

Run `caeops metrics install-agent --help` for more help.

## Synopsis
---

```shell
  install-agent
--service-name [value]
--cloud [value]
--source [value]
--app-name [value]
[--kubernetes-cluster-name [value]]
[--metrics-scrape-config [value]]
[--docker-network [value]]
[--metrics-scrape-config [value]]
[--generate-default-scrape-config [value]]
```

## Options
---

**--service-name** (string)

> Name of the metrics service

**--cloud** (string)

> The type of cloud service providers. Supported providers : aws

**--source** (string)

> The type of cloud source. Supported resources : kubernetes

**--app-name** (string)

> A representative name for the current app sending the metrics

**--kubernetes-cluster-name** (string)

> Name of the kubernetes cluster where the agent needs to run

**--docker-network** (string)

> Name of the docker network on which the docker agent needs to run

**--metrics-scrape-config** (string)

> Absolute path to the docker application metrics end points configuration file to scrape metrics

**--generate-default-scrape-config**

> Generates the default metrics end point configuration files based on the 'source' type

## Examples
---

- The following `metrics install-agent` example generates commands to install an agent for a `kubernetes` source
  on `aws` cloud

```shell
caeops metrics install-agent
        --service-name mymetrics --cloud aws --source kubernetes --app-name "Test App"
        --kubernetes-cluster-name test-cluster --metrics-scrape-config "/home/test/scrape_config.yaml"
```

#### Output
Instructions -> (string)
```shell
Step 1
------
Download the script to run the agent. (This script deploys a helm chart. Skip this step if the script is already downloaded)
←[36m    wget -O aws_kubernetes_agent.py https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/scripts/aws_kubernetes_agent.py

Do you want to execute the command ? (y/n)n


Step 2
------
If no K8 agent is installed or active, run the below command to install a new K8 agent. (NOTE: If a K8 agent is already running for logs/metrics, skip this step and go to next step)
←[36m  python3 aws_kubernetes_agent.py --helm-repo "https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/helm/cae-k8-agent/charts" --enable-metrics "yes" --k8-cluster-name "test-cluster" --k8-namespace "cloudaeye" --cloud-env "aws" --prometheus-endpoint "https://endpoint.com" --prometheus-region "someregion" --app-name "Test App" --app-key "TA" --user-key "somekey" --user-secret "somesecret" --agent-mode "create" --user-config-file "/home/test/scrape_config.yaml"

Do you want to execute the command ? (y/n)y

 .--. .-.                 .-. .--.  .--.
: .--': :                 : :: .; :: .--'
: :   : :   .--. .-..-. .-' ::    :: `;  .-..-. .--.
: :__ : :_ ' .; :: :; :' .; :: :: :: :__ : :; :' '_.'
`.__.'`.__;`.__.'`.__.'`.__.':_;:_;`.__.'`._. ;`.__.'
                                          .-. :
                                          `._.'


==================================================
Install Agent (via helm) => Log source: kubernetes
==================================================


----------------------
Helm command generated
----------------------

helm install cae-k8-agent cae-k8-agent --create-namespace --namespace cloudaeye --set namespace=cloudaeye --set client.cloud_env=aws --set client.app_name="Test App" --set client.app_key="TA" --repo https://cae-data-collection-agent.s3.us-east-2.amazonaws.com/kubernetes/helm/cae-k8-agent/charts --set user.key=somekey --set user.secret=somesecret --set client.cluster_name="test-cluster" --set metrics.enabled=true --set metrics.prometheusRegion=someregion  --set metrics.prometheusEndpoint=https://endpoint.com -f "/home/test/scrape_config.yaml"
Do you want to execute the helm command ?
(NOTE: Please make sure that you are connected to the right k8 cluster before running the helm command !) [y/n] :y
```

"""
import json
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


def install_agent(payload, tenant_id) -> dict:
    """
    Fetches the instructions to install agent for a given metrics source
    :param payload: Payload to be passed to the REST API
    :param tenant_id: Id of the tenant in the current session
    :return: Parsed response from server
    """
    # Construct the Url
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/metrics/agent/install"
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


def get_default_metrics_scrape_config(payload, tenant_id) -> dict:
    """
    Fetches the instructions to install agent for a given metrics source
    :param payload: Payload to be passed to the REST API
    :param tenant_id: Id of the tenant in the current session
    :return: Parsed response from server
    """
    # Construct the Url
    url = CentralizedMetricsUrl + "/v1/tenants/" + tenant_id + "/metrics/agent/default-config"
    # Construct the query params
    query_params = {"cloud": payload["cloud"], "source": payload["source"]}
    # Construct the payload
    if "cloud" in payload:
        del payload["cloud"]
    if "source" in payload:
        del payload["source"]
    # Make a request to the REST API
    res = requests.get(
        url=url,
        params=query_params,
        headers=generate_auth_headers(ConfigKeys.ID_TOKEN),
    )
    # Parse and return the response
    return parse_rest_api_response(res)


def metrics_install_agent(payload: dict):
    """
    Run the install agent command for metrics
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

    prefix = None

    if "generateDefaultScrapeConfig" in payload.keys():
        mandatory_fields = ["cloud", "source"]
    else:
        mandatory_fields = ["service-name", "cloud", "source", "app-name"]
        if payload.get("source", "") == "kubernetes":
            mandatory_fields.append("kubernetes-cluster-name")
            prefix = "kubernetes"
        elif payload.get("source", "") == "docker":
            mandatory_fields.append("docker-network")
            prefix = "docker"
        else:
            prefix = None

    # Validate for mandatory fields
    validate_mandatory_fields(
        payload,
        mandatory_fields=mandatory_fields,
    )

    if prefix:
        payload = restructure_with_sub_object(
            actual_object=payload, sub_object_key=prefix
        )
        if "metricsScrapeConfig" in payload.keys():
            payload[prefix]["metricsScrapeConfig"] = payload["metricsScrapeConfig"]
            payload.pop("metricsScrapeConfig")

    try:
        if "generateDefaultScrapeConfig" in payload:
            # Fetch default scrape template from REST API
            response = get_default_metrics_scrape_config(payload, tenant_id)
            print(response)
            print("\n")
        else:
            # Fetch agent installation instructions for metrics from REST API
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
